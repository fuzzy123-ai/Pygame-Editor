"""
Thread zum Lesen von Game-Output in Echtzeit
"""
import subprocess
import threading
from PySide6.QtCore import QThread, Signal
from typing import Optional


class GameOutputReader(QThread):
    """Thread der stdout/stderr eines Subprocess in Echtzeit liest"""
    
    output_received = Signal(str)  # Normale Ausgabe
    error_received = Signal(str)   # Fehler-Ausgabe
    finished = Signal()            # Thread beendet
    
    def __init__(self, process: subprocess.Popen):
        super().__init__()
        self.process = process
        self._running = True
        self.stdout_thread = None
        self.stderr_thread = None
    
    def _read_stdout(self):
        """Liest stdout in einem separaten Thread"""
        if not self.process.stdout:
            return
        
        while self._running and self.process.poll() is None:
            try:
                # Text lesen (dank PYTHONIOENCODING=utf-8 sollte UTF-8 verwendet werden)
                line = self.process.stdout.readline()
                if line:
                    # Bereits dekodiert, nur rstrip
                    decoded_line = line.rstrip('\n\r')
                    self.output_received.emit(decoded_line)
                elif self.process.poll() is not None:
                    # Prozess beendet, keine weiteren Daten
                    break
            except (UnicodeDecodeError, UnicodeError) as e:
                # Fallback: Fehlerhafte Zeichen ersetzen
                try:
                    # Versuche nochmal mit Fehlerbehandlung
                    if hasattr(line, 'encode'):
                        # Falls es bereits ein String ist, ist alles OK
                        decoded_line = line.rstrip('\n\r')
                        self.output_received.emit(decoded_line)
                except Exception:
                    pass  # Ignoriere fehlerhafte Zeilen
            except Exception:
                break
    
    def _read_stderr(self):
        """Liest stderr in einem separaten Thread (Fehler werden sofort angezeigt)"""
        if not self.process.stderr:
            return
        
        while self._running and self.process.poll() is None:
            try:
                # Text lesen (dank PYTHONIOENCODING=utf-8 sollte UTF-8 verwendet werden)
                line = self.process.stderr.readline()
                if line:
                    # Bereits dekodiert, nur rstrip
                    decoded_line = line.rstrip('\n\r')
                    self.error_received.emit(decoded_line)
                elif self.process.poll() is not None:
                    # Prozess beendet, keine weiteren Daten
                    break
            except (UnicodeDecodeError, UnicodeError) as e:
                # Fallback: Fehlerhafte Zeichen ersetzen
                try:
                    # Versuche nochmal mit Fehlerbehandlung
                    if hasattr(line, 'encode'):
                        # Falls es bereits ein String ist, ist alles OK
                        decoded_line = line.rstrip('\n\r')
                        self.error_received.emit(decoded_line)
                except Exception:
                    pass  # Ignoriere fehlerhafte Zeilen
            except Exception:
                break
    
    def run(self):
        """Startet Threads zum Lesen von stdout und stderr"""
        import sys
        
        # Starte separate Threads für stdout und stderr
        # Das ermöglicht sofortige Ausgabe beider Streams ohne Blockierung
        if self.process.stdout:
            self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self.stdout_thread.start()
        
        if self.process.stderr:
            self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self.stderr_thread.start()
        
        # Warte bis Prozess beendet ist
        while self._running and self.process.poll() is None:
            self.msleep(100)  # Alle 100ms prüfen
        
        # Warte auf Threads (mit Timeout)
        if self.stdout_thread:
            self.stdout_thread.join(timeout=1.0)
        if self.stderr_thread:
            self.stderr_thread.join(timeout=1.0)
        
        # Restliche Ausgaben lesen (falls noch Daten im Buffer)
        if self.process.poll() is not None:
            try:
                stdout, stderr = self.process.communicate(timeout=0.5)
                if stdout:
                    # Bereits Text (dank PYTHONIOENCODING=utf-8)
                    try:
                        for line in stdout.splitlines():
                            if line.strip():
                                self.output_received.emit(line.strip())
                    except Exception:
                        pass
                if stderr:
                    # Bereits Text (dank PYTHONIOENCODING=utf-8)
                    try:
                        for line in stderr.splitlines():
                            if line.strip():
                                self.error_received.emit(line.strip())
                    except Exception:
                        pass
            except Exception:
                pass
        
        self.finished.emit()
    
    def stop(self):
        """Stoppt den Thread"""
        self._running = False
