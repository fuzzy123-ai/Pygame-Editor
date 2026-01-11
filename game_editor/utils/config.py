"""
Editor-Konfiguration - Speichert Einstellungen wie zuletzt geöffnetes Projekt
"""
import json
import sys
import os
from pathlib import Path
from typing import Optional


def get_config_file() -> Path:
    """Gibt den Pfad zur Konfigurationsdatei zurück"""
    if sys.platform == "win32":
        # Windows: AppData/Local
        appdata = Path(os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ".")))
        config_dir = appdata / "PygameEditor"
    else:
        # Linux/Mac: ~/.config
        config_dir = Path.home() / ".config" / "pygame-editor"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> dict:
    """Lädt Konfiguration aus Datei"""
    config_file = get_config_file()
    
    if not config_file.exists():
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: dict):
    """Speichert Konfiguration in Datei"""
    config_file = get_config_file()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")


def get_last_project() -> Optional[Path]:
    """Gibt den Pfad zum zuletzt geöffneten Projekt zurück"""
    config = load_config()
    project_path = config.get("last_project")
    
    if project_path:
        path = Path(project_path)
        # Prüfen ob Projekt noch existiert
        if path.exists() and (path / "project.json").exists():
            return path
    
    return None


def set_last_project(project_path: Path):
    """Speichert den Pfad zum zuletzt geöffneten Projekt"""
    config = load_config()
    config["last_project"] = str(project_path.absolute())
    save_config(config)
