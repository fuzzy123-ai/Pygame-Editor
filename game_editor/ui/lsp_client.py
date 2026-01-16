"""
LSP Client - Wrapper für Language Server Protocol Kommunikation
"""
import subprocess
import json
import threading
import queue
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from PySide6.QtCore import QObject, Signal, QTimer


class LSPClient(QObject):
    """LSP-Client für Kommunikation mit Language Server"""
    
    # Signals für LSP-Events
    diagnostics_received = Signal(dict)  # Fehler/Warnungen
    completion_received = Signal(list)   # Auto-Vervollständigung
    hover_received = Signal(dict)        # Hover-Informationen
    
    def __init__(self, project_path: Path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.server_process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.pending_requests: Dict[int, Callable] = {}
        self.server_capabilities: Dict[str, Any] = {}
        self.initialized = False
        
        # Queues für Kommunikation
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Thread für Server-Kommunikation
        self.communication_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start_server(self) -> bool:
        """Startet den LSP-Server (pylsp)"""
        try:
            # Prüfe ob pylsp verfügbar ist
            import shutil
            pylsp_path = shutil.which("pylsp")
            if not pylsp_path:
                # Versuche python -m pylsp
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pylsp", "--version"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        print("WARNUNG: pylsp nicht gefunden. LSP-Features nicht verfügbar.")
                        return False
                except Exception:
                    print("WARNUNG: pylsp nicht gefunden. LSP-Features nicht verfügbar.")
                    return False
            
            # Server starten (binary mode für JSON-RPC)
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "pylsp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            # Kommunikations-Thread starten
            self.running = True
            self.communication_thread = threading.Thread(
                target=self._communication_loop,
                daemon=True
            )
            self.communication_thread.start()
            
            # Initialize Request senden
            self._initialize()
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Starten des LSP-Servers: {e}")
            return False
    
    def _communication_loop(self):
        """Haupt-Loop für Server-Kommunikation"""
        buffer = ""
        while self.running and self.server_process:
            try:
                # Lese vom Server (JSON-RPC verwendet Content-Length Header)
                chunk = self.server_process.stdout.read(1024)
                if not chunk:
                    break
                
                buffer += chunk.decode('utf-8', errors='ignore')
                
                # Parse Messages (Content-Length: XXX\r\n\r\n{json})
                while True:
                    # Suche nach Content-Length Header
                    if "\r\n\r\n" not in buffer:
                        break
                    
                    header_end = buffer.find("\r\n\r\n")
                    headers = buffer[:header_end]
                    body_start = header_end + 4
                    
                    # Content-Length extrahieren
                    content_length = None
                    for line in headers.split("\r\n"):
                        if line.startswith("Content-Length:"):
                            content_length = int(line.split(":")[1].strip())
                            break
                    
                    if content_length is None:
                        # Kein gültiger Header, Buffer zurücksetzen
                        buffer = buffer[body_start:]
                        continue
                    
                    # Prüfe ob vollständige Message vorhanden
                    if len(buffer) < body_start + content_length:
                        break
                    
                    # Message extrahieren
                    message_json = buffer[body_start:body_start + content_length]
                    buffer = buffer[body_start + content_length:]
                    
                    # Parse JSON
                    try:
                        message = json.loads(message_json)
                        self._handle_message(message)
                    except json.JSONDecodeError:
                        continue
                    
            except Exception as e:
                if self.running:
                    print(f"Fehler in Kommunikations-Loop: {e}")
                break
    
    def _handle_message(self, message: Dict[str, Any]):
        """Verarbeitet eingehende LSP-Messages"""
        if "method" in message:
            # Notification (keine Response erwartet)
            method = message.get("method")
            params = message.get("params", {})
            
            if method == "textDocument/publishDiagnostics":
                # Fehler/Warnungen
                self.diagnostics_received.emit(params)
            elif method == "window/logMessage":
                # Log-Nachricht (können wir ignorieren)
                pass
                
        elif "id" in message:
            # Response auf Request
            request_id = message.get("id")
            if request_id in self.pending_requests:
                callback = self.pending_requests.pop(request_id)
                if callback:
                    # Callback im Hauptthread ausführen (über QTimer)
                    result = message.get("result")
                    error = message.get("error")
                    QTimer.singleShot(0, lambda: callback(result, error))
    
    def _send_request(self, method: str, params: Dict[str, Any], callback: Optional[Callable] = None):
        """Sendet einen Request an den Server"""
        if not self.server_process:
            return
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        if callback:
            self.pending_requests[self.request_id] = callback
        
        # Sende Request (JSON-RPC Format: Content-Length Header)
        try:
            message = json.dumps(request)
            message_bytes = message.encode('utf-8')
            content_length = len(message_bytes)
            header = f"Content-Length: {content_length}\r\n\r\n"
            self.server_process.stdin.write(header.encode('utf-8') + message_bytes)
            self.server_process.stdin.flush()
        except Exception as e:
            print(f"Fehler beim Senden von Request: {e}")
            if self.request_id in self.pending_requests:
                del self.pending_requests[self.request_id]
    
    def _initialize(self):
        """Initialisiert die Verbindung zum Server"""
        params = {
            "processId": None,
            "rootPath": str(self.project_path),
            "rootUri": f"file://{self.project_path.absolute()}",
            "capabilities": {
                "textDocument": {
                    "completion": {
                        "completionItem": {
                            "snippetSupport": True
                        }
                    },
                    "hover": {
                        "contentFormat": ["plaintext", "markdown"]
                    },
                    "publishDiagnostics": {
                        "relatedInformation": True
                    }
                },
                "workspace": {}
            }
        }
        
        def on_initialized(result, error):
            # Callback wird im Hintergrund-Thread aufgerufen
            # Verwende QTimer.singleShot um im Hauptthread auszuführen
            if error:
                print(f"LSP Initialisierung fehlgeschlagen: {error}")
                return
            
            # Qt-Operationen müssen im Hauptthread ausgeführt werden
            def do_initialized():
                self.server_capabilities = result.get("capabilities", {})
                self.initialized = True
                
                # Initialized Notification senden
                self._send_notification("initialized", {})
                
                print("LSP-Server initialisiert")
            
            # Im Hauptthread ausführen
            QTimer.singleShot(0, do_initialized)
        
        self._send_request("initialize", params, on_initialized)
    
    def _send_notification(self, method: str, params: Dict[str, Any]):
        """Sendet eine Notification an den Server"""
        if not self.server_process:
            return
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        try:
            message = json.dumps(notification)
            message_bytes = message.encode('utf-8')
            content_length = len(message_bytes)
            header = f"Content-Length: {content_length}\r\n\r\n"
            self.server_process.stdin.write(header.encode('utf-8') + message_bytes)
            self.server_process.stdin.flush()
        except Exception as e:
            print(f"Fehler beim Senden von Notification: {e}")
    
    def open_document(self, uri: str, text: str, language_id: str = "python"):
        """Öffnet ein Dokument im Server"""
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": 1,
                "text": text
            }
        })
    
    def update_document(self, uri: str, text: str, version: int):
        """Aktualisiert ein Dokument im Server"""
        self._send_notification("textDocument/didChange", {
            "textDocument": {
                "uri": uri,
                "version": version
            },
            "contentChanges": [{
                "text": text
            }]
        })
    
    def close_document(self, uri: str):
        """Schließt ein Dokument im Server"""
        self._send_notification("textDocument/didClose", {
            "textDocument": {
                "uri": uri
            }
        })
    
    def request_completion(self, uri: str, line: int, character: int, callback: Callable):
        """Fordert Auto-Vervollständigung an"""
        self._send_request("textDocument/completion", {
            "textDocument": {
                "uri": uri
            },
            "position": {
                "line": line,
                "character": character
            }
        }, callback)
    
    def request_hover(self, uri: str, line: int, character: int, callback: Callable):
        """Fordert Hover-Informationen an"""
        self._send_request("textDocument/hover", {
            "textDocument": {
                "uri": uri
            },
            "position": {
                "line": line,
                "character": character
            }
        }, callback)
    
    def stop_server(self):
        """Stoppt den LSP-Server"""
        self.running = False
        
        if self.server_process:
            try:
                # Shutdown Request senden
                self._send_request("shutdown", {}, None)
                # Exit Notification
                self._send_notification("exit", {})
                
                # Process beenden
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                
            except Exception as e:
                print(f"Fehler beim Stoppen des LSP-Servers: {e}")
            
            self.server_process = None
        
        if self.communication_thread:
            self.communication_thread.join(timeout=2)
