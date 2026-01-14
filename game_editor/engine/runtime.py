"""
Runtime Engine - Pygame Game Loop und Schüler-Code Ausführung
"""
import pygame
import sys
import json
import warnings
from pathlib import Path
from typing import Optional, Dict, Any
from .loader import load_project, load_scene, create_objects_from_scene
from .gameobject import GameObject
from .api import (_init_api, _update_key_states, get_debug_output, 
                  clear_debug_output, print_debug, get_object, get_all_objects,
                  key_pressed, key_down, mouse_position, spawn_object,
                  move_with_collision, push_objects, lock_y_position,
                  unlock_y_position, apply_locked_y_positions)

# libpng Warnungen werden direkt auf stderr geschrieben, nicht als Python warnings
# Sie werden in gameobject.py beim Laden der Bilder unterdrückt

# Fehler-Übersetzungen (Deutsch)
ERROR_TRANSLATIONS: Dict[str, str] = {
    "invalid syntax": "Ungültige Syntax - fehlt ein Doppelpunkt oder Klammer?",
    "unexpected EOF": "Code ist unvollständig - fehlt eine schließende Klammer?",
    "name '.*' is not defined": "Variable existiert nicht",
    "IndentationError": "Einrückungsfehler - achte auf Leerzeichen oder Tabs",
}


def translate_error(error_msg: str) -> str:
    """Übersetzt Python-Fehlermeldungen ins Deutsche"""
    error_lower = error_msg.lower()
    for key, translation in ERROR_TRANSLATIONS.items():
        if key in error_lower:
            return translation
    return error_msg


def load_student_code(game_code_path: Path, game_objects: list[GameObject]) -> Dict[str, Any]:
    """
    Lädt und kompiliert Schüler-Code
    
    Args:
        game_code_path: Pfad zu game.py
        game_objects: Liste aller GameObjects
        
    Returns:
        Namespace-Dict mit Funktionen und Variablen
    """
    if not game_code_path.exists():
        raise FileNotFoundError(f"game.py nicht gefunden: {game_code_path}")
    
    # API initialisieren
    _init_api(game_objects)
    clear_debug_output()
    
    # Namespace für Schüler-Code vorbereiten
    game_namespace = {
        # Objekte
        "get_object": get_object,
        "get_all_objects": get_all_objects,
        
        # Input
        "key_pressed": key_pressed,
        "key_down": key_down,
        "mouse_position": mouse_position,
        
        # Utility
        "print_debug": print_debug,
        "spawn_object": spawn_object,
        "move_with_collision": move_with_collision,
        "push_objects": push_objects,
        "lock_y_position": lock_y_position,
        "unlock_y_position": unlock_y_position,
        
        # Standard-Python (für Schüler nützlich)
        "print": print,
        "len": len,
        "range": range,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
    }
    
    # Code laden und kompilieren
    try:
        with open(game_code_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Test-Compile
        compile(code, str(game_code_path), 'exec')
        
        # Code ausführen
        exec(code, game_namespace)
        
    except SyntaxError as e:
        error_msg = translate_error(str(e))
        print(f"SYNTAXFEHLER in Zeile {e.lineno}: {error_msg}")
        print(f"Details: {e.msg}")
        raise
    
    except Exception as e:
        error_msg = translate_error(str(e))
        print(f"FEHLER: {error_msg}")
        print(f"Typ: {type(e).__name__}")
        raise
    
    return game_namespace


def main(project_path: str):
    """
    Hauptfunktion - Startet das Spiel
    
    Args:
        project_path: Pfad zum Projektordner
    """
    project_dir = Path(project_path)
    if not project_dir.exists():
        print(f"FEHLER: Projektordner nicht gefunden: {project_path}")
        sys.exit(1)
    
    # Projekt laden
    try:
        config = load_project(project_dir)
    except Exception as e:
        print(f"FEHLER beim Laden von project.json: {e}")
        sys.exit(1)
    
    # Pygame initialisieren
    pygame.init()
    
    window_width = config.get("window", {}).get("width", 800)
    window_height = config.get("window", {}).get("height", 600)
    window_title = config.get("window", {}).get("title", "GameDev-Edu")
    
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption(window_title)
    clock = pygame.time.Clock()
    
    # Szene laden
    start_scene = config.get("start_scene", "level1")
    try:
        scene_data = load_scene(project_dir, start_scene)
    except Exception as e:
        print(f"FEHLER beim Laden der Szene {start_scene}: {e}")
        pygame.quit()
        sys.exit(1)
    
    # Objekte erstellen
    game_objects = create_objects_from_scene(scene_data, project_dir)
    
    # Schüler-Code laden (code/game.py)
    game_code_path = project_dir / "code" / "game.py"
    game_namespace = None
    try:
        game_namespace = load_student_code(game_code_path, game_objects)
    except Exception as e:
        print(f"FEHLER beim Laden von game.py: {e}")
        # Spiel trotzdem starten, aber ohne update()
        game_namespace = {}
    
    # Code aus allen Objekten laden und ausführen
    # WICHTIG: Jedes Objekt kann eigenen Code haben, der in jedem Frame ausgeführt wird
    object_namespaces = {}  # Dict: obj_id -> namespace
    for obj in game_objects:
        obj_code = scene_data.get("objects", [])
        # Finde das Objekt in der Szene
        obj_data = None
        for o in obj_code:
            if o.get("id") == obj.id:
                obj_data = o
                break
        
        if obj_data and obj_data.get("code"):
            try:
                # Code für dieses Objekt ausführen
                obj_namespace = {
                    # Objekte
                    "get_object": get_object,
                    "get_all_objects": get_all_objects,
                    # Input
                    "key_pressed": key_pressed,
                    "key_down": key_down,
                    "mouse_position": mouse_position,
                    # Utility
                    "print_debug": print_debug,
                    "spawn_object": spawn_object,
                    "move_with_collision": move_with_collision,
                    "push_objects": push_objects,
                    "lock_y_position": lock_y_position,
                    "unlock_y_position": unlock_y_position,
                    # Standard-Python
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                }
                # Code ausführen
                exec(obj_data["code"], obj_namespace)
                object_namespaces[obj.id] = obj_namespace
            except Exception as e:
                error_msg = translate_error(str(e))
                print(f"FEHLER beim Laden von Code für Objekt {obj.id}: {error_msg}")
                # Objekt-Code wird übersprungen, aber Spiel läuft weiter
    
    # Background-Farbe
    bg_color = scene_data.get("background_color", [135, 206, 235])
    if isinstance(bg_color, list) and len(bg_color) >= 3:
        background_color = tuple(bg_color[:3])
    else:
        background_color = (135, 206, 235)
    
    # Debug-Modus
    debug_mode = False
    
    # Game Loop
    running = True
    fps = 0
    fps_font = pygame.font.Font(None, 24)
    
    while running:
        # Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    debug_mode = not debug_mode
        
        # Tastatur-Status aktualisieren (für key_down)
        _update_key_states()
        
        # API aktualisieren (falls Objekte-Liste sich geändert hat)
        # WICHTIG: Muss vor jedem Update aufgerufen werden, damit get_object() die aktuelle Liste verwendet
        _init_api(game_objects)
        
        # Positionen vor Updates speichern (für Mitbewegung)
        # WICHTIG: Speichere Positionen BEVOR Updates ausgeführt werden
        frame_start_positions = {}
        for obj in game_objects:
            frame_start_positions[obj.id] = (obj.x, obj.y)
        
        # Update-Funktionen aus allen Objekten aufrufen
        # WICHTIG: Code für alle Objekte wird ausgeführt, nicht nur für das aktuell ausgewählte
        for obj_id, obj_namespace in object_namespaces.items():
            if "update" in obj_namespace:
                try:
                    obj_namespace["update"]()
                except Exception as e:
                    error_msg = translate_error(str(e))
                    print(f"FEHLER in update() für Objekt {obj_id}: {error_msg}")
                    print(f"Typ: {type(e).__name__}")
                    # Spiel pausiert nicht, läuft weiter
        
        # Schüler-Update aufrufen (code/game.py)
        # WICHTIG: Nur ausführen wenn keine Objekte eigenen Code haben, um Doppelausführung zu vermeiden
        # Wenn Objekte Code haben, wird nur deren Code ausgeführt
        if not object_namespaces and game_namespace and "update" in game_namespace:
            try:
                game_namespace["update"]()
            except Exception as e:
                error_msg = translate_error(str(e))
                print(f"FEHLER in update() (game.py): {error_msg}")
                print(f"Typ: {type(e).__name__}")
                # Spiel pausiert nicht, läuft weiter
        
        # Unsichtbare Objekte entfernen (destroy())
        game_objects[:] = [obj for obj in game_objects if obj.visible]
        
        # Fixierte Y-Positionen anwenden (NACH Updates, VOR Mitbewegung)
        apply_locked_y_positions()
        
        # Mitbewegung: Objekte, die auf anderen Objekten stehen, mitbewegen
        # Prüfe für jedes Objekt, ob es sich bewegt hat (vergleiche mit Position vor Updates)
        for moved_obj in game_objects:
            if moved_obj.id not in frame_start_positions:
                continue
            
            start_x, start_y = frame_start_positions[moved_obj.id]
            curr_x, curr_y = moved_obj.x, moved_obj.y
            dx = curr_x - start_x
            dy = curr_y - start_y
            
            # Wenn sich das Objekt bewegt hat
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                # Prüfe alle anderen Objekte, ob sie auf diesem Objekt stehen
                for other_obj in game_objects:
                    if other_obj.id == moved_obj.id or not other_obj._collider_enabled:
                        continue
                    
                    # Prüfe ob other_obj auf moved_obj steht (verwende Positionen VOR Updates)
                    # WICHTIG: Prüfe mit den Positionen, die vor den Updates gespeichert wurden
                    other_start_x, other_start_y = frame_start_positions.get(other_obj.id, (other_obj.x, other_obj.y))
                    other_collider_bottom = other_start_y + other_obj._collider_offset_y + other_obj._collider_height
                    moved_collider_top = start_y + moved_obj._collider_offset_y
                    
                    # Prüfe auch horizontale Überlappung (Objekte müssen sich überlappen)
                    other_collider_left = other_start_x + other_obj._collider_offset_x
                    other_collider_right = other_collider_left + other_obj._collider_width
                    moved_collider_left = start_x + moved_obj._collider_offset_x
                    moved_collider_right = moved_collider_left + moved_obj._collider_width
                    
                    horizontal_overlap = (other_collider_left < moved_collider_right and 
                                         other_collider_right > moved_collider_left)
                    
                    # Toleranz von 3 Pixeln für "darauf stehen"
                    is_standing_on = (horizontal_overlap and
                                     other_collider_bottom >= moved_collider_top - 3.0 and 
                                     other_collider_bottom <= moved_collider_top + 3.0)
                    
                    if is_standing_on:
                        # Objekt steht darauf - mitbewegen
                        other_obj.x += dx
                        other_obj.y += dy
        
        # Fixierte Y-Positionen erneut anwenden (NACH Mitbewegung)
        apply_locked_y_positions()
        
        # Kamera finden und Offset berechnen
        camera_offset_x = 0
        camera_offset_y = 0
        camera_obj = None
        for obj in game_objects:
            if obj.is_camera:
                camera_obj = obj
                # Kamera in Bildschirmmitte zentrieren
                camera_offset_x = int(obj.x + obj.width / 2 - window_width / 2)
                camera_offset_y = int(obj.y + obj.height / 2 - window_height / 2)
                break
        
        # Rendering
        screen.fill(background_color)
        
        # Alle Objekte zeichnen (mit Kamera-Offset)
        for obj in game_objects:
            obj.draw(screen, debug=debug_mode, offset_x=-camera_offset_x, offset_y=-camera_offset_y)
        
        # Debug-Overlay
        if debug_mode:
            # FPS-Counter
            fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, 10))
            
            # Objekt-Zähler
            obj_text = fps_font.render(f"Objekte: {len(game_objects)}", True, (255, 255, 255))
            screen.blit(obj_text, (10, 35))
        
        pygame.display.flip()
        fps = int(clock.get_fps())
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: python -m game_editor.engine.runtime <projekt_pfad>")
        sys.exit(1)
    
    main(sys.argv[1])
