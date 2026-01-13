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
                # Text-Daten lesen (bereits dekodiert durch subprocess)
                # readline() blockiert, bis eine Zeile verfügbar ist oder EOF erreicht wird
                line = self.process.stdout.readline()
                if line:
                    # Zeile ist bereits ein String (durch text=True)
                    decoded_line = line.rstrip('\n\r')
                    if decoded_line:  # Nur nicht-leere Zeilen senden
                        self.output_received.emit(decoded_line)
                elif self.process.poll() is not None:
                    # Prozess beendet, keine weiteren Daten
                    break
            except (UnicodeDecodeError, ValueError) as e:
                # Unicode-Fehler ignorieren (sollten nicht auftreten mit text=True)
                # Aber falls doch, ignorieren wir sie
                if self.process.poll() is not None:
                    break
                continue
            except Exception as e:
                # Alle anderen Fehler ignorieren (z.B. wenn Prozess beendet wird)
                if self.process.poll() is not None:
                    break
                continue
    
    def _read_stderr(self):
        """Liest stderr in einem separaten Thread (Fehler werden sofort angezeigt)"""
        if not self.process.stderr:
            return
        
        while self._running and self.process.poll() is None:
            try:
                # Text-Daten lesen (bereits dekodiert durch subprocess)
                # readline() blockiert, bis eine Zeile verfügbar ist oder EOF erreicht wird
                line = self.process.stderr.readline()
                if line:
                    # Zeile ist bereits ein String (durch text=True)
                    decoded_line = line.rstrip('\n\r')
                    if decoded_line:  # Nur nicht-leere Zeilen senden
                        self.error_received.emit(decoded_line)
                elif self.process.poll() is not None:
                    # Prozess beendet, keine weiteren Daten
                    break
            except (UnicodeDecodeError, ValueError) as e:
                # Unicode-Fehler ignorieren (sollten nicht auftreten mit text=True)
                # Aber falls doch, ignorieren wir sie
                if self.process.poll() is not None:
                    break
                continue
            except Exception as e:
                # Alle anderen Fehler ignorieren (z.B. wenn Prozess beendet wird)
                if self.process.poll() is not None:
                    break
                continue
    
    def run(self):
        """Startet Threads zum Lesen von stdout und stderr"""
        import sys
        import select
        import time
        
        # Starte separate Threads für stdout und stderr SOFORT
        # Das verhindert, dass Python's interne subprocess Threads die Daten lesen
        # WICHTIG: Threads müssen sofort starten, bevor Python's interne Threads die Streams lesen
        
        # Sofort einen ersten read() Aufruf machen, um die Streams zu "reservieren"
        # Das verhindert, dass Python's interne Threads die Streams lesen
        # WICHTIG: Dies muss VOR dem Starten der Threads passieren
        if self.process.stdout:
            try:
                # Sofort einen ersten read() Aufruf machen (non-blocking)
                # Das "reserviert" den Stream für unseren Thread
                # read(0) ist non-blocking und "reserviert" den Stream
                _ = self.process.stdout.read(0)  # Non-blocking read
            except (AttributeError, ValueError, OSError):
                # Stream könnte bereits geschlossen sein oder nicht unterstützen
                pass
            
            self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self.stdout_thread.start()
        
        if self.process.stderr:
            try:
                # Sofort einen ersten read() Aufruf machen (non-blocking)
                # Das "reserviert" den Stream für unseren Thread
                _ = self.process.stderr.read(0)  # Non-blocking read
            except (AttributeError, ValueError, OSError):
                # Stream könnte bereits geschlossen sein oder nicht unterstützen
                pass
            
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
                    # stdout ist bereits ein String (durch text=True)
                    for line in stdout.splitlines():
                        if line.strip():
                            self.output_received.emit(line.strip())
                if stderr:
                    # stderr ist bereits ein String (durch text=True)
                    for line in stderr.splitlines():
                        if line.strip():
                            self.error_received.emit(line.strip())
            except Exception:
                pass
        
        self.finished.emit()
    
    def stop(self):
        """Stoppt den Thread"""
        self._running = False
