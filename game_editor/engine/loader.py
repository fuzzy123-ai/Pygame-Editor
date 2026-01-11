"""
Loader - Lädt Projekt- und Szenen-Daten aus JSON
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from .gameobject import GameObject


def load_project(project_dir: Path) -> Dict[str, Any]:
    """
    Lädt project.json
    
    Args:
        project_dir: Projektverzeichnis
        
    Returns:
        Projekt-Konfiguration als Dict
    """
    project_file = project_dir / "project.json"
    if not project_file.exists():
        raise FileNotFoundError(f"project.json nicht gefunden in {project_dir}")
    
    with open(project_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_scene(project_dir: Path, scene_name: str) -> Dict[str, Any]:
    """
    Lädt eine Szene aus scenes/{scene_name}.json
    
    Args:
        project_dir: Projektverzeichnis
        scene_name: Name der Szene (ohne .json)
        
    Returns:
        Szenen-Daten als Dict
    """
    scene_file = project_dir / "scenes" / f"{scene_name}.json"
    if not scene_file.exists():
        raise FileNotFoundError(f"Szene {scene_name}.json nicht gefunden")
    
    with open(scene_file, 'r', encoding='utf-8') as f:
        scene_data = json.load(f)
    
    return scene_data


def create_objects_from_scene(scene_data: Dict[str, Any], project_dir: Path) -> List[GameObject]:
    """
    Erstellt GameObject-Liste aus Szenen-Daten
    
    Args:
        scene_data: Geladene Szenen-Daten
        project_dir: Projektverzeichnis
        
    Returns:
        Liste von GameObject-Instanzen
    """
    objects = []
    
    if "objects" not in scene_data:
        return objects
    
    # Sprite-Größe aus Projekteinstellungen laden
    sprite_size = None
    try:
        project_file = project_dir / "project.json"
        if project_file.exists():
            with open(project_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            sprite_size_config = config.get("sprite_size", 64)
            if isinstance(sprite_size_config, dict):
                sprite_size = sprite_size_config.get("width", sprite_size_config.get("size", 64))
            else:
                sprite_size = sprite_size_config if isinstance(sprite_size_config, int) else 64
    except Exception:
        sprite_size = 64  # Standard bei Fehler
    
    for obj_data in scene_data["objects"]:
        obj = GameObject(obj_data, project_dir, sprite_size)
        objects.append(obj)
    
    # Alle Objekte kennen die komplette Liste (für collides_with)
    for obj in objects:
        obj.set_all_objects(objects)
    
    return objects


def save_scene(scene_data: Dict[str, Any], project_dir: Path, scene_name: str):
    """
    Speichert eine Szene in scenes/{scene_name}.json
    
    Args:
        scene_data: Szenen-Daten als Dict
        project_dir: Projektverzeichnis
        scene_name: Name der Szene (ohne .json)
    """
    scene_file = project_dir / "scenes" / f"{scene_name}.json"
    scene_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(scene_file, 'w', encoding='utf-8') as f:
        json.dump(scene_data, f, indent=2, ensure_ascii=False)
