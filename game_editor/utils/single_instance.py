"""
Single Instance Check - Verhindert mehrere Editor-Instanzen
"""
import sys
import os
from pathlib import Path
import atexit


def get_lock_file_path() -> Path:
    """Gibt den Pfad zur Lock-Datei zurück"""
    if sys.platform == "win32":
        # Windows: Temp-Verzeichnis
        temp_dir = Path(os.environ.get("TEMP", os.environ.get("TMP", ".")))
    else:
        # Linux/Mac: /tmp
        temp_dir = Path("/tmp")
    
    return temp_dir / "pygame_editor.lock"


def is_instance_running() -> bool:
    """Prüft ob bereits eine Editor-Instanz läuft"""
    lock_file = get_lock_file_path()
    
    if not lock_file.exists():
        return False
    
    # Prüfen ob Prozess noch läuft (Windows)
    if sys.platform == "win32":
        try:
            # PID aus Lock-Datei lesen
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Prüfen ob Prozess existiert (ohne psutil)
            try:
                # Windows: tasklist verwenden
                import subprocess
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if str(pid) in result.stdout:
                    # Prozess existiert - prüfen ob es Python ist
                    result2 = subprocess.run(
                        ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if "game_editor.editor" in result2.stdout:
                        return True
            except Exception:
                pass
        except (ValueError, FileNotFoundError):
            # Lock-Datei löschen
            try:
                lock_file.unlink()
            except:
                pass
    
    # Fallback: Lock-Datei existiert, aber Prozess-Check fehlgeschlagen
    # Lock-Datei löschen und neu erstellen
    try:
        lock_file.unlink()
    except:
        pass
    
    return False


def create_lock_file() -> bool:
    """Erstellt Lock-Datei mit aktueller PID"""
    lock_file = get_lock_file_path()
    
    try:
        # PID schreiben
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Cleanup beim Beenden registrieren
        atexit.register(remove_lock_file)
        
        return True
    except Exception:
        return False


def remove_lock_file():
    """Entfernt Lock-Datei"""
    lock_file = get_lock_file_path()
    try:
        if lock_file.exists():
            lock_file.unlink()
    except Exception:
        pass
