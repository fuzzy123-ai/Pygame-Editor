"""
Runtime Engine - Pygame Game Loop und Schüler-Code Ausführung
"""
import pygame
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from .loader import load_project, load_scene, create_objects_from_scene
from .gameobject import GameObject
from .api import (_init_api, _update_key_states, get_debug_output, 
                  clear_debug_output, print_debug, get_object, get_all_objects,
                  key_pressed, key_down, mouse_position, spawn_object)

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
    
    # Schüler-Code laden
    game_code_path = project_dir / "code" / "game.py"
    game_namespace = None
    try:
        game_namespace = load_student_code(game_code_path, game_objects)
    except Exception as e:
        print(f"FEHLER beim Laden von game.py: {e}")
        # Spiel trotzdem starten, aber ohne update()
        game_namespace = {}
    
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
        
        # Schüler-Update aufrufen (mit Fehlerbehandlung)
        if game_namespace and "update" in game_namespace:
            try:
                game_namespace["update"]()
            except Exception as e:
                error_msg = translate_error(str(e))
                print(f"FEHLER in update(): {error_msg}")
                print(f"Typ: {type(e).__name__}")
                # Spiel pausiert nicht, läuft weiter
        
        # Unsichtbare Objekte entfernen (destroy())
        game_objects[:] = [obj for obj in game_objects if obj.visible]
        
        # Rendering
        screen.fill(background_color)
        
        # Alle Objekte zeichnen
        for obj in game_objects:
            obj.draw(screen, debug=debug_mode)
        
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
