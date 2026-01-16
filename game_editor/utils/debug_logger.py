"""
Debug Logger - Schreibt Debug-Ausgaben in eine Log-Datei
"""
from pathlib import Path
from datetime import datetime
import threading

class DebugLogger:
    """Thread-sicherer Logger für Debug-Ausgaben"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.log_file = None
        self.log_path = None
        self._init_log()
    
    def _init_log(self):
        """Initialisiert die Log-Datei"""
        # Log-Datei im Projekt-Root oder im Temp-Verzeichnis
        try:
            # Versuche Projekt-Root zu finden
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
            log_dir.mkdir(exist_ok=True)
            self.log_path = log_dir / "syntax_highlighting_debug.log"
        except:
            # Fallback: Temp-Verzeichnis
            import tempfile
            self.log_path = Path(tempfile.gettempdir()) / "syntax_highlighting_debug.log"
        
        # Log-Datei öffnen (append mode)
        try:
            self.log_file = open(self.log_path, 'a', encoding='utf-8')
            self.log("=" * 80)
            self.log(f"Debug-Log gestartet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log("=" * 80)
        except Exception as e:
            print(f"FEHLER: Konnte Log-Datei nicht öffnen: {e}")
            self.log_file = None
    
    @classmethod
    def get_instance(cls):
        """Gibt die Singleton-Instanz zurück"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def log(self, message: str, category: str = "INFO"):
        """Schreibt eine Nachricht ins Log"""
        if self.log_file is None:
            return
        
        try:
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]  # Millisekunden
            log_entry = f"[{timestamp}] [{category}] {message}\n"
            
            with self._lock:
                self.log_file.write(log_entry)
                self.log_file.flush()  # Sofort schreiben
        except Exception as e:
            # Falls Logging fehlschlägt, ignorieren (verhindert Endlosschleifen)
            pass
    
    def close(self):
        """Schließt die Log-Datei"""
        if self.log_file:
            try:
                self.log("=" * 80)
                self.log(f"Debug-Log beendet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.log("=" * 80)
                self.log_file.close()
            except:
                pass
    
    def get_log_path(self):
        """Gibt den Pfad zur Log-Datei zurück"""
        return self.log_path
