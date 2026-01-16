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
_locked_y_positions: Dict[str, float] = {}  # Für lock_y_position - speichert fixierte Y-Positionen

# Key-Mapping: String -> Pygame Key Code (einmalig erstellt, für bessere Performance)
_KEY_MAP = {
    # Englische Tasten-Namen
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
    # Deutsche Tasten-Namen (Aliase)
    "LINKS": pygame.K_LEFT,
    "RECHTS": pygame.K_RIGHT,
    "HOCH": pygame.K_UP,
    "RUNTER": pygame.K_DOWN,
    "LEERTASTE": pygame.K_SPACE,
    "EINGABE": pygame.K_RETURN,
}


def _init_api(objects: List[GameObject]):
    """Initialisiert die API (wird von runtime.py aufgerufen)"""
    global _game_objects, _key_pressed_last_frame
    _game_objects = objects
    _key_pressed_last_frame = {}


def _update_key_states():
    """Aktualisiert Tastatur-Status (wird von runtime.py aufgerufen)"""
    global _key_states, _key_pressed_last_frame
    # WICHTIG: Hole Tastatur-Status sofort und direkt (keine Verzögerung)
    keys = pygame.key.get_pressed()
    
    # Aktueller Frame - alle Tasten gleichzeitig und unabhängig prüfen
    current_states = {}
    for key_name, key_code in _KEY_MAP.items():
        # Direkter Zugriff auf Tastatur-Status (sofort, keine Verzögerung)
        current_states[key_name] = bool(keys[key_code])
    
    # key_down: True nur beim ersten Drücken (alle Tasten unabhängig voneinander)
    # WICHTIG: Jede Taste wird unabhängig geprüft - keine Blockierung zwischen Tasten
    _key_states = {}
    for key_name in _KEY_MAP.keys():
        was_pressed = _key_pressed_last_frame.get(key_name, False)
        is_pressed = current_states.get(key_name, False)
        # Taste wurde gerade gedrückt (war vorher nicht gedrückt, jetzt gedrückt)
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
        key: Tastenname ("LEFT"/"LINKS", "RIGHT"/"RECHTS", "UP"/"HOCH", "DOWN"/"RUNTER", 
                         "SPACE"/"LEERTASTE", "W", "A", "S", "D", "ENTER"/"EINGABE")
        
    Returns:
        True wenn Taste gedrückt, sonst False
        
    WICHTIG: Diese Funktion prüft sofort den aktuellen Tastatur-Status.
    Alle Tasten können gleichzeitig und unabhängig voneinander erkannt werden.
    """
    try:
        # Hole sofort den aktuellen Tastatur-Status (keine Verzögerung)
        keys = pygame.key.get_pressed()
        key_code = _KEY_MAP.get(key.upper())
        if key_code is None:
            return False
        # Direkte Rückgabe - keine zusätzliche Verarbeitung
        return bool(keys[key_code])
    except:
        return False


def key_down(key: str) -> bool:
    """
    Prüft ob eine Taste gerade gedrückt wurde (einmalig beim Drücken)
    
    Args:
        key: Tastenname ("LEFT"/"LINKS", "RIGHT"/"RECHTS", "UP"/"HOCH", "DOWN"/"RUNTER", 
                         "SPACE"/"LEERTASTE", "W", "A", "S", "D", "ENTER"/"EINGABE")
        
    Returns:
        True nur beim ersten Frame nach Drücken, sonst False
        
    WICHTIG: Diese Funktion prüft sowohl den gecachten Status als auch direkt
    den Tastatur-Status, um sicherzustellen, dass keine Tastendrücke verpasst werden.
    """
    key_upper = key.upper()
    
    # Zuerst prüfe den gecachten Status (schnell)
    if _key_states.get(key_upper, False):
        return True
    
    # Falls nicht im Cache, prüfe direkt den Tastatur-Status
    # Das stellt sicher, dass auch sehr schnelle Tastendrücke erkannt werden
    try:
        keys = pygame.key.get_pressed()
        key_code = _KEY_MAP.get(key_upper)
        if key_code is None:
            return False
        
        # Prüfe ob Taste gerade gedrückt ist, aber im letzten Frame nicht
        is_pressed = bool(keys[key_code])
        was_pressed = _key_pressed_last_frame.get(key_upper, False)
        
        # Wenn Taste gerade gedrückt wurde (war vorher nicht gedrückt)
        if is_pressed and not was_pressed:
            return True
    except:
        pass
    
    return False


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
            if other.id != obj.id and other._collider_enabled:
                # Kollisionen mit ALLEN Objekten mit aktivierter Kollisionsbox (Boden, Plattformen, etc.)
                # TODO: Später könnte hier geprüft werden ob other.is_enemy für spezielle Behandlung
                if obj.collides_with(other.id):
                    # WICHTIG: Prüfe ob Objekt auf dem anderen Objekt steht
                    # Verwende Position NACH Bewegung für Kollisionsprüfung
                    obj_collider_bottom = obj._collider_y + obj._collider_height
                    obj_collider_top = obj._collider_y
                    other_collider_bottom = other._collider_y + other._collider_height
                    other_collider_top = other._collider_y
                    
                    # Prüfe ob Objekt auf dem anderen Objekt steht (von oben)
                    # Wenn Unterseite des Objekts nahe an Oberseite des anderen Objekts = Objekt steht darauf
                    # Toleranz von 3 Pixeln für Rundungsfehler und kleine Bewegungen
                    is_standing_on = (obj_collider_bottom >= other_collider_top - 3.0 and 
                                     obj_collider_bottom <= other_collider_top + 3.0)
                    
                    # WICHTIG: Wenn Objekt auf Plattform/Boden steht, KEINE horizontale Blockierung!
                    if is_standing_on:
                        # Objekt steht darauf - horizontale Bewegung erlauben
                        continue
                    
                    # Nur blockieren wenn es KEINE "darauf stehen" Situation ist
                    # Prüfe ob es eine echte seitliche Kollision ist (nicht nur vertikale Überlappung)
                    obj_fully_above = obj_collider_bottom < other_collider_top
                    obj_fully_below = obj_collider_top > other_collider_bottom
                    
                    if not (obj_fully_above or obj_fully_below):
                        # Echte seitliche Kollision - Position zurücksetzen
                        obj.x = old_x
                        collision_x = True
                        break
    
    # Prüfe vertikale Kollisionen (Y-Achse)
    on_ground = False
    collision_y = False
    
    # Prüfe Kollisionen mit allen Objekten (Boden und andere mit Kollisionsbox)
    for other in _game_objects:
        if other.id != obj.id and other._collider_enabled:
            # Kollisionen mit allen Objekten mit aktivierter Kollisionsbox
            if obj.collides_with(other.id):
                collision_y = True
                
                if other.is_ground:
                    # Berechne Positionen für Boden-Kollision
                    # WICHTIG: Verwende Kollisionsbox-Positionen, nicht Objekt-Positionen!
                    obj_collider_bottom = obj._collider_y + obj._collider_height  # Unterseite der Kollisionsbox des Objekts
                    ground_top = other._collider_y  # Oberseite der Kollisionsbox des Bodens
                    penetration = obj_collider_bottom - ground_top  # Wie weit die Kollisionsbox in den Boden eindringt
                    
                    if dy > 0:  # Objekt fällt nach unten
                        # Prüfe ob Kollisionsbox wirklich in den Boden eindringt
                        # Nur korrigieren wenn Kollisionsbox wirklich unter dem Boden ist (mehr als 0.1 Pixel)
                        if penetration > 0.1:
                            # Kollisionsbox war über dem Boden - jetzt darauf setzen
                            # Setze Unterseite der Kollisionsbox auf Oberseite des Bodens
                            # obj._collider_y + obj._collider_height = ground_top
                            # obj.y + obj._collider_offset_y + obj._collider_height = ground_top
                            # obj.y = ground_top - obj._collider_height - obj._collider_offset_y
                            on_ground = True
                            obj.y = ground_top - obj._collider_height - obj._collider_offset_y
                        elif penetration >= -1.0:  # Toleranz: bereits korrekt oder maximal 1 Pixel darüber
                            # Kollisionsbox steht bereits korrekt auf dem Boden - keine Position-Änderung!
                            on_ground = True
                            # Position NICHT ändern, um Wackeln zu vermeiden
                    elif dy < 0:  # Objekt springt nach oben
                        # Position zurücksetzen wenn gegen Decke
                        obj.y = old_y
                    elif dy == 0:  # Objekt bewegt sich nicht vertikal
                        # WICHTIG: Keine Position-Korrektur bei dy == 0!
                        # Nur prüfen, ob Kollisionsbox auf Boden steht (ohne Position zu ändern)
                        # Toleranz von 1 Pixel für Rundungsfehler
                        if ground_top - 1.0 <= obj_collider_bottom <= ground_top + 1.0:
                            on_ground = True
                else:
                    # Kollision mit anderem Objekt (nicht Boden) - z.B. Plattformen
                    # Berechne Kollisionsbox-Positionen für präzise Kollisionsbehandlung
                    obj_collider_bottom = obj._collider_y + obj._collider_height
                    obj_collider_top = obj._collider_y
                    other_collider_bottom = other._collider_y + other._collider_height
                    other_collider_top = other._collider_y
                    
                    # Prüfe von welcher Richtung die Kollision kommt
                    # WICHTIG: Für Plattformen - nur von oben blockieren (durchfallen erlauben)
                    # Später kann hier auch "enemy" Logik hinzugefügt werden
                    
                    if dy > 0:  # Objekt fällt nach unten
                        # Prüfe ob Objekt wirklich von oben kommt (Unterseite über Oberseite der Plattform)
                        # Nur wenn Objekt von oben kommt, auf Plattform landen
                        penetration = obj_collider_bottom - other_collider_top
                        if penetration > 0.1:  # Objekt dringt wirklich in Plattform ein
                            # Objekt kollidiert von oben mit Plattform/Objekt
                            # Setze Unterseite der Kollisionsbox auf Oberseite des anderen Objekts
                            # TODO: Später hier prüfen ob other.is_enemy und dann töten statt landen
                            obj.y = other_collider_top - obj._collider_height - obj._collider_offset_y
                            # WICHTIG: Objekt steht jetzt auf der Plattform - on_ground setzen!
                            on_ground = True
                        elif penetration >= -2.0:  # Toleranz: bereits korrekt oder maximal 2 Pixel darüber
                            # Objekt steht bereits korrekt auf Plattform - keine Position-Änderung!
                            # WICHTIG: on_ground setzen, damit Schwerkraft nicht weiter angewendet wird!
                            on_ground = True
                            # Position NICHT ändern, um Wackeln zu vermeiden
                    elif dy < 0:  # Objekt springt nach oben
                        # Objekt kommt von unten - durch Plattform durchgehen (keine Blockierung)
                        # Position NICHT zurücksetzen, damit Objekt durch Plattform springen kann
                        # Nur wenn Objekt wirklich von unten kommt (Oberseite unter Unterseite der Plattform)
                        if obj_collider_top < other_collider_bottom:
                            # Objekt kollidiert von unten - durchgehen lassen (keine Position-Änderung)
                            pass
                        else:
                            # Objekt ist bereits in der Plattform - Position zurücksetzen
                            obj.y = old_y
                    elif dy == 0:  # Objekt bewegt sich nicht vertikal
                        # WICHTIG: Keine Position-Korrektur bei dy == 0!
                        # Nur prüfen, ob Objekt auf Plattform steht (ohne Position zu ändern)
                        # Toleranz von 2 Pixeln für Rundungsfehler
                        if other_collider_top - 2.0 <= obj_collider_bottom <= other_collider_top + 2.0:
                            # Objekt steht auf Plattform - on_ground setzen!
                            on_ground = True
                        else:
                            # Objekt ist seitlich oder in Plattform - keine Position-Korrektur bei dy == 0
                            pass
                break
    
    return (on_ground, collision_x, collision_y)


def push_objects(obj: GameObject, dx: float, dy: float, push_strength: float = 1.0) -> int:
    """
    Drückt andere Objekte weg, wenn dieses Objekt mit ihnen kollidiert
    
    Args:
        obj: Das Objekt, das andere wegdrücken soll
        dx: Bewegungsrichtung in X (wird verwendet um Push-Richtung zu bestimmen)
        dy: Bewegungsrichtung in Y (wird verwendet um Push-Richtung zu bestimmen)
        push_strength: Stärke des Pushs (Standard: 1.0 = vollständige Bewegung)
        
    Returns:
        Anzahl der Objekte, die weggedrückt wurden
        
    WICHTIG: Diese Funktion sollte NACH move_with_collision() aufgerufen werden,
    wenn das Objekt sich bewegt hat und andere Objekte wegdrücken soll.
    """
    if not obj or not obj._collider_enabled:
        return 0
    
    pushed_count = 0
    
    # Prüfe alle anderen Objekte
    for other in _game_objects:
        if other.id == obj.id or not other._collider_enabled:
            continue
        
        # Ignoriere Boden-Objekte (werden nicht weggedrückt)
        if other.is_ground:
            continue
        
        # Prüfe ob Objekte kollidieren (basierend auf aktueller Position)
        collides_now = obj.collides_with(other.id)
        
        # Wenn keine Kollision jetzt, prüfe ob Objekte sich überlappen würden
        # basierend auf der Bewegungsrichtung (für horizontale Bewegung)
        collides = collides_now
        if not collides_now and abs(dx) > 0.1:
            # Prüfe ob Objekte sich überlappen würden, wenn wir die Position
            # um -dx zurücksetzen würden (Position vor der Bewegung)
            from .collision import CollisionSystem
            # Temporär Position zurücksetzen für Kollisionsprüfung
            old_x = obj.x
            old_y = obj.y
            obj.x = old_x - dx
            obj.y = old_y - dy
            collides = CollisionSystem.check_collision(obj, other)
            obj.x = old_x  # Position wiederherstellen
            obj.y = old_y
        
        # Zusätzlich: Prüfe ob Objekte sich in der Bewegungsrichtung befinden
        # und sich überlappen würden (für den Fall, dass die Plattform sich bereits bewegt hat)
        if not collides and abs(dx) > 0.1:
            from .collision import CollisionSystem
            # Prüfe ob Objekte sich in der Bewegungsrichtung befinden
            # und sich überlappen würden, wenn die Plattform sich weiter bewegt
            old_x = obj.x
            old_y = obj.y
            # Prüfe Position in Bewegungsrichtung
            obj.x = old_x + dx
            obj.y = old_y + dy
            if CollisionSystem.check_collision(obj, other):
                collides = True
            obj.x = old_x  # Position wiederherstellen
            obj.y = old_y
        
        if collides:
            # Berechne Push-Richtung basierend auf Bewegungsrichtung
            push_dx = 0
            push_dy = 0
            
            if abs(dx) > abs(dy):
                # Hauptsächlich horizontale Bewegung
                if dx > 0:
                    push_dx = push_strength * abs(dx)  # Nach rechts drücken
                elif dx < 0:
                    push_dx = -push_strength * abs(dx)  # Nach links drücken
            else:
                # Hauptsächlich vertikale Bewegung
                if dy > 0:
                    push_dy = push_strength * abs(dy)  # Nach unten drücken
                elif dy < 0:
                    push_dy = -push_strength * abs(dy)  # Nach oben drücken
            
            # Prüfe ob Objekt wirklich in die Push-Richtung bewegt werden kann
            # (nur wenn es nicht auf dem drückenden Objekt steht)
            obj_collider_bottom = obj._collider_y + obj._collider_height
            other_collider_top = other._collider_y
            other_collider_bottom = other._collider_y + other._collider_height
            
            # Wenn anderes Objekt auf diesem Objekt steht, nicht nach oben drücken
            if push_dy < 0 and other_collider_bottom <= obj_collider_bottom + 3.0:
                push_dy = 0
            
            # Objekt wegdrücken (mit Kollisionsprüfung)
            if push_dx != 0 or push_dy != 0:
                # Verwende move_with_collision für das andere Objekt, um Kollisionen zu berücksichtigen
                # Das stellt sicher, dass weggedrückte Objekte auch an Hindernissen hängen bleiben
                other_old_x = other.x
                other_old_y = other.y
                on_ground, collision_x, collision_y = move_with_collision(other, push_dx, push_dy)
                
                # Prüfe ob Objekt wirklich bewegt wurde (nicht durch Kollision blockiert)
                if abs(other.x - other_old_x) > 0.01 or abs(other.y - other_old_y) > 0.01:
                    pushed_count += 1
    
    return pushed_count


def lock_y_position(obj: GameObject, y: float):
    """
    Fixiert die Y-Position eines Objekts.
    Die Y-Position wird nach jedem Update automatisch auf diesen Wert zurückgesetzt.
    
    Args:
        obj: Das Objekt, dessen Y-Position fixiert werden soll
        y: Die Y-Position, die beibehalten werden soll
    """
    if obj:
        _locked_y_positions[obj.id] = y


def unlock_y_position(obj: GameObject):
    """
    Entfernt die Y-Position-Fixierung eines Objekts.
    
    Args:
        obj: Das Objekt, dessen Y-Position-Fixierung entfernt werden soll
    """
    if obj and obj.id in _locked_y_positions:
        del _locked_y_positions[obj.id]


def apply_locked_y_positions():
    """
    Wird von runtime.py nach jedem Update aufgerufen, um fixierte Y-Positionen anzuwenden.
    """
    global _locked_y_positions
    for obj_id, locked_y in _locked_y_positions.items():
        obj = get_object(obj_id)
        if obj:
            obj.y = locked_y


# ============================================================================
# Deutsche Funktions-Aliase (Phase 1)
# ============================================================================

def hole_objekt(obj_id: str) -> Optional[GameObject]:
    """
    Deutsche Version von get_object()
    
    Gibt ein Objekt anhand seiner ID zurück
    
    Args:
        obj_id: ID des Objekts
        
    Returns:
        GameObject oder None wenn nicht gefunden
    """
    return get_object(obj_id)


def hole_alle_objekte() -> List[GameObject]:
    """
    Deutsche Version von get_all_objects()
    
    Gibt alle sichtbaren Objekte zurück
    
    Returns:
        Liste aller sichtbaren GameObjects
    """
    return get_all_objects()


def taste_gedrückt(taste: str) -> bool:
    """
    Deutsche Version von key_pressed()
    
    Prüft ob eine Taste gedrückt gehalten wird
    
    Args:
        taste: Tastenname ("LEFT", "RIGHT", "UP", "DOWN", "SPACE", "W", "A", "S", "D", "ENTER")
        
    Returns:
        True wenn Taste gedrückt, sonst False
    """
    return key_pressed(taste)


def taste_runter(taste: str) -> bool:
    """
    Deutsche Version von key_down()
    
    Prüft ob eine Taste gerade gedrückt wurde (einmalig beim Drücken)
    
    Args:
        taste: Tastenname ("LEFT", "RIGHT", "UP", "DOWN", "SPACE", "W", "A", "S", "D", "ENTER")
        
    Returns:
        True nur beim ersten Frame nach Drücken, sonst False
    """
    return key_down(taste)


def maus_position() -> Tuple[int, int]:
    """
    Deutsche Version von mouse_position()
    
    Gibt die aktuelle Mausposition zurück
    
    Returns:
        Tuple (x, y) der Mausposition
    """
    return mouse_position()


def drucke_debug(text: str):
    """
    Deutsche Version von print_debug()
    
    Gibt Debug-Text aus (erscheint in Editor-Console)
    
    Args:
        text: Debug-Text
    """
    print_debug(text)


def erstelle_objekt(vorlage: Dict[str, Any]) -> Optional[GameObject]:
    """
    Deutsche Version von spawn_object()
    
    Erstellt ein neues Objekt aus einer Template-Vorlage
    
    Args:
        vorlage: Dict mit Objekt-Eigenschaften (id, type, x, y, width, height, sprite, etc.)
        
    Returns:
        Neues GameObject oder None bei Fehler
    """
    return spawn_object(vorlage)


def bewege_mit_kollision(obj: GameObject, dx: float, dy: float) -> Tuple[bool, bool, bool]:
    """
    Deutsche Version von move_with_collision()
    
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
    return move_with_collision(obj, dx, dy)


def drücke_objekte(obj: GameObject, dx: float, dy: float, drück_stärke: float = 1.0) -> int:
    """
    Deutsche Version von push_objects()
    
    Drückt andere Objekte weg, wenn dieses Objekt mit ihnen kollidiert
    
    Args:
        obj: Das Objekt, das andere wegdrücken soll
        dx: Bewegungsrichtung in X (wird verwendet um Push-Richtung zu bestimmen)
        dy: Bewegungsrichtung in Y (wird verwendet um Push-Richtung zu bestimmen)
        drück_stärke: Stärke des Pushs (Standard: 1.0 = vollständige Bewegung)
        
    Returns:
        Anzahl der Objekte, die weggedrückt wurden
    """
    return push_objects(obj, dx, dy, drück_stärke)


def fixiere_y_position(obj: GameObject, y: float):
    """
    Deutsche Version von lock_y_position()
    
    Fixiert die Y-Position eines Objekts.
    Die Y-Position wird nach jedem Update automatisch auf diesen Wert zurückgesetzt.
    
    Args:
        obj: Das Objekt, dessen Y-Position fixiert werden soll
        y: Die Y-Position, die beibehalten werden soll
    """
    lock_y_position(obj, y)


def entferne_y_fixierung(obj: GameObject):
    """
    Deutsche Version von unlock_y_position()
    
    Entfernt die Y-Position-Fixierung eines Objekts.
    
    Args:
        obj: Das Objekt, dessen Y-Position-Fixierung entfernt werden soll
    """
    unlock_y_position(obj)