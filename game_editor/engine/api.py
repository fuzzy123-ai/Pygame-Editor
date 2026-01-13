"""
Schüler-API - Vereinfachte Funktionen für Schüler-Code
"""
import pygame
from typing import Optional, List, Tuple, Dict, Any
from .gameobject import GameObject


# Globale Variablen, die von der Runtime gesetzt werden
_game_objects: List[GameObject] = []
_key_states: Dict[str, bool] = {}  # Für key_down (einmalig beim Drücken)
_key_pressed_last_frame: Dict[str, bool] = {}
_debug_output: List[str] = []
_spawn_templates: List[Dict[str, Any]] = []  # Für spawn_object


def _init_api(objects: List[GameObject]):
    """Initialisiert die API (wird von runtime.py aufgerufen)"""
    global _game_objects, _key_pressed_last_frame
    _game_objects = objects
    _key_pressed_last_frame = {}


def _update_key_states():
    """Aktualisiert Tastatur-Status (wird von runtime.py aufgerufen)"""
    global _key_states, _key_pressed_last_frame
    keys = pygame.key.get_pressed()
    
    # Key-Mapping: String -> Pygame Key Code
    KEY_MAP = {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        "SPACE": pygame.K_SPACE,
        "ENTER": pygame.K_RETURN,
        "W": pygame.K_w,
        "A": pygame.K_a,
        "S": pygame.K_s,
        "D": pygame.K_d,
        "F1": pygame.K_F1,
    }
    
    # Aktueller Frame
    current_states = {}
    for key_name, key_code in KEY_MAP.items():
        current_states[key_name] = keys[key_code]
    
    # key_down: True nur beim ersten Drücken
    _key_states = {}
    for key_name in KEY_MAP.keys():
        was_pressed = _key_pressed_last_frame.get(key_name, False)
        is_pressed = current_states.get(key_name, False)
        _key_states[key_name] = is_pressed and not was_pressed
    
    _key_pressed_last_frame = current_states


def get_object(obj_id: str) -> Optional[GameObject]:
    """
    Gibt ein Objekt anhand seiner ID zurück
    
    Args:
        obj_id: ID des Objekts
        
    Returns:
        GameObject oder None wenn nicht gefunden
    """
    for obj in _game_objects:
        if obj.id == obj_id and obj.visible:
            return obj
    return None


def get_all_objects() -> List[GameObject]:
    """
    Gibt alle sichtbaren Objekte zurück
    
    Returns:
        Liste aller sichtbaren GameObjects
    """
    return [obj for obj in _game_objects if obj.visible]


def key_pressed(key: str) -> bool:
    """
    Prüft ob eine Taste gedrückt gehalten wird
    
    Args:
        key: Tastenname ("LEFT", "RIGHT", "UP", "DOWN", "SPACE", "W", "A", "S", "D", "ENTER")
        
    Returns:
        True wenn Taste gedrückt, sonst False
    """
    try:
        keys = pygame.key.get_pressed()
        KEY_MAP = {
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "SPACE": pygame.K_SPACE,
            "ENTER": pygame.K_RETURN,
            "W": pygame.K_w,
            "A": pygame.K_a,
            "S": pygame.K_s,
            "D": pygame.K_d,
            "F1": pygame.K_F1,
        }
        key_code = KEY_MAP.get(key.upper())
        if key_code is None:
            return False
        return keys[key_code]
    except:
        return False


def key_down(key: str) -> bool:
    """
    Prüft ob eine Taste gerade gedrückt wurde (einmalig beim Drücken)
    
    Args:
        key: Tastenname ("LEFT", "RIGHT", "UP", "DOWN", "SPACE", "W", "A", "S", "D", "ENTER")
        
    Returns:
        True nur beim ersten Frame nach Drücken, sonst False
    """
    return _key_states.get(key.upper(), False)


def mouse_position() -> Tuple[int, int]:
    """
    Gibt die aktuelle Mausposition zurück
    
    Returns:
        Tuple (x, y) der Mausposition
    """
    try:
        return pygame.mouse.get_pos()
    except:
        return (0, 0)


def print_debug(text: str):
    """
    Gibt Debug-Text aus (erscheint in Editor-Console)
    
    Args:
        text: Debug-Text
    """
    _debug_output.append(str(text))
    print(f"[DEBUG] {text}")


def spawn_object(template: Dict[str, Any]) -> Optional[GameObject]:
    """
    Erstellt ein neues Objekt aus einer Template-Vorlage (MVP: später)
    
    Args:
        template: Dict mit Objekt-Eigenschaften (id, type, x, y, width, height, sprite, etc.)
        
    Returns:
        Neues GameObject oder None bei Fehler
    """
    # MVP: Wird später implementiert, wenn Projekt-Verwaltung fertig ist
    # Für jetzt: Template wird gespeichert und bei nächstem Reload erstellt
    _spawn_templates.append(template)
    print_debug(f"spawn_object: Wird in zukünftiger Version unterstützt")
    return None


def get_debug_output() -> List[str]:
    """Gibt alle Debug-Ausgaben zurück (wird von Editor verwendet)"""
    return _debug_output.copy()


def clear_debug_output():
    """Löscht alle Debug-Ausgaben (wird von Editor verwendet)"""
    global _debug_output
    _debug_output = []


def move_with_collision(obj: GameObject, dx: float, dy: float) -> Tuple[bool, bool, bool]:
    """
    Bewegt ein Objekt mit automatischer Kollisionsbehandlung
    
    Args:
        obj: Das zu bewegende Objekt
        dx: Bewegung in X-Richtung
        dy: Bewegung in Y-Richtung
        
    Returns:
        Tuple (on_ground, collision_x, collision_y)
        - on_ground: True wenn Objekt auf Boden steht
        - collision_x: True wenn Kollision in X-Richtung
        - collision_y: True wenn Kollision in Y-Richtung
    """
    if not obj:
        return (False, False, False)
    
    # Position vor der Bewegung speichern
    old_x = obj.x
    old_y = obj.y
    
    # Bewegung anwenden (immer, auch ohne Kollisionsbox)
    obj.x += dx
    obj.y += dy
    
    # Kollisionsprüfung nur wenn Objekt eine Kollisionsbox hat
    if not obj._collider_enabled:
        return (False, False, False)
    
    # Prüfe horizontale Kollisionen (X-Achse) - NUR wenn sich bewegt
    collision_x = False
    if dx != 0:
        for other in _game_objects:
            if other.id != obj.id and other.is_ground and other._collider_enabled:
                if obj.collides_with(other.id):
                    # Kollision in X-Richtung - Position zurücksetzen
                    obj.x = old_x
                    collision_x = True
                    break
    
    # Prüfe vertikale Kollisionen (Y-Achse)
    on_ground = False
    collision_y = False
    
    # Prüfe ob Objekt mit Boden kollidiert
    for other in _game_objects:
        if other.id != obj.id and other.is_ground and other._collider_enabled:
            if obj.collides_with(other.id):
                collision_y = True
                if dy > 0:  # Objekt fällt nach unten
                    # Objekt war über dem Boden - jetzt auf Boden setzen
                    # Verwende die Y-Position der Kollisionsbox des Bodens (other._collider_y)
                    # minus Objekt-Höhe, um die Unterseite des Objekts auf die Oberseite des Bodens zu setzen
                    on_ground = True
                    obj.y = other._collider_y - obj.height
                elif dy < 0:  # Objekt springt nach oben
                    # Position zurücksetzen wenn gegen Decke
                    obj.y = old_y
                elif dy == 0:  # Objekt bewegt sich nicht vertikal
                    # Prüfe ob Objekt wirklich auf dem Boden steht
                    # Wenn Unterseite des Objekts nahe an Oberseite des Bodens
                    # Toleranz von 2 Pixeln
                    if obj.y + obj.height <= other._collider_y + 2:
                        on_ground = True
                break
    
    return (on_ground, collision_x, collision_y)