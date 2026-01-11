"""
Umfassender Test des Game Editors
Testet alle Funktionen systematisch
"""
import json
import sys
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).parent
TEST_PROJECT = PROJECT_ROOT / "Test_Project"

def test_project_structure():
    """Test 1: Projekt-Struktur prüfen"""
    print("=" * 60)
    print("TEST 1: Projekt-Struktur")
    print("=" * 60)
    
    required_files = [
        "project.json",
        "code/game.py",
        "scenes/level1.json"
    ]
    
    required_dirs = [
        "assets/images",
        "assets/sounds",
        "sprites"
    ]
    
    errors = []
    warnings = []
    
    # Dateien prüfen
    for file_path in required_files:
        full_path = TEST_PROJECT / file_path
        if full_path.exists():
            print(f"[OK] {file_path} existiert")
        else:
            errors.append(f"[FEHLER] {file_path} fehlt")
            print(f"[FEHLER] {file_path} fehlt")
    
    # Verzeichnisse prüfen
    for dir_path in required_dirs:
        full_path = TEST_PROJECT / dir_path
        if full_path.exists():
            print(f"[OK] {dir_path}/ existiert")
        else:
            warnings.append(f"[WARN] {dir_path}/ fehlt (wird automatisch erstellt)")
            print(f"[WARN] {dir_path}/ fehlt (wird automatisch erstellt)")
    
    # Sprites prüfen
    sprites_dir = TEST_PROJECT / "sprites"
    if sprites_dir.exists():
        sprite_files = list(sprites_dir.glob("*.png")) + list(sprites_dir.glob("*.jpg"))
        print(f"[OK] {len(sprite_files)} Sprite-Dateien im sprites/ Ordner gefunden")
        for sprite in sprite_files:
            print(f"  - {sprite.name}")
    
    # Assets prüfen
    assets_dir = TEST_PROJECT / "assets" / "images"
    if assets_dir.exists():
        asset_files = list(assets_dir.rglob("*.png")) + list(assets_dir.rglob("*.jpg"))
        print(f"[OK] {len(asset_files)} Asset-Dateien im assets/images/ Ordner gefunden")
        for asset in asset_files[:10]:  # Nur erste 10 anzeigen
            rel_path = asset.relative_to(TEST_PROJECT)
            print(f"  - {rel_path}")
        if len(asset_files) > 10:
            print(f"  ... und {len(asset_files) - 10} weitere")
    
    print()
    return len(errors) == 0

def test_project_json():
    """Test 2: project.json prüfen"""
    print("=" * 60)
    print("TEST 2: project.json Validierung")
    print("=" * 60)
    
    project_file = TEST_PROJECT / "project.json"
    if not project_file.exists():
        print("[FEHLER] project.json nicht gefunden")
        return False
    
    try:
        with open(project_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Pflichtfelder prüfen
        required_fields = ["name", "version", "start_scene", "window"]
        for field in required_fields:
            if field in config:
                print(f"[OK] {field}: {config[field]}")
            else:
                print(f"[FEHLER] {field} fehlt")
                return False
        
        # Window-Einstellungen
        window = config.get("window", {})
        if "width" in window and "height" in window:
            print(f"[OK] Fenstergroesse: {window['width']}x{window['height']}")
        else:
            print("[WARN] Fenstergroesse nicht vollstaendig definiert")
        
        # Sprite-Größe prüfen
        if "sprite_size" in config:
            sprite_size = config["sprite_size"]
            print(f"[OK] Sprite-Groesse: {sprite_size}x{sprite_size}")
        else:
            print("[WARN] sprite_size nicht definiert (alle Bilder werden angezeigt)")
        
        # Grid-Einstellungen
        if "grid" in config:
            grid = config["grid"]
            if "color" in grid:
                color = grid["color"]
                print(f"[OK] Grid-Farbe: RGB({color[0]}, {color[1]}, {color[2]})")
        else:
            print("[WARN] Grid-Einstellungen nicht definiert")
        
        print()
        return True
        
    except json.JSONDecodeError as e:
        print(f"[FEHLER] JSON-Fehler: {e}")
        return False
    except Exception as e:
        print(f"[FEHLER] Fehler beim Laden: {e}")
        return False

def test_scene_json():
    """Test 3: level1.json prüfen"""
    print("=" * 60)
    print("TEST 3: level1.json Validierung")
    print("=" * 60)
    
    scene_file = TEST_PROJECT / "scenes" / "level1.json"
    if not scene_file.exists():
        print("[FEHLER] level1.json nicht gefunden")
        return False
    
    try:
        with open(scene_file, 'r', encoding='utf-8') as f:
            scene = json.load(f)
        
        # Pflichtfelder
        if "objects" in scene:
            objects = scene["objects"]
            print(f"[OK] {len(objects)} Objekte in der Szene")
            
            # Objekte prüfen
            for i, obj in enumerate(objects):
                obj_id = obj.get("id", f"object_{i}")
                obj_type = obj.get("type", "unknown")
                x = obj.get("x", 0)
                y = obj.get("y", 0)
                width = obj.get("width", 0)
                height = obj.get("height", 0)
                sprite = obj.get("sprite", None)
                
                print(f"  Objekt {i+1}: {obj_id} ({obj_type})")
                print(f"    Position: ({x}, {y})")
                print(f"    Groesse: {width}x{height}")
                if sprite:
                    # Prüfen ob Pfad relativ ist
                    if Path(sprite).is_absolute():
                        print(f"    [WARN] Sprite-Pfad ist absolut: {sprite}")
                    else:
                        print(f"    [OK] Sprite: {sprite}")
                else:
                    print(f"    [WARN] Kein Sprite zugewiesen")
                
                # Kollisionsprüfung
                if "collider" in obj:
                    collider = obj["collider"]
                    if collider.get("enabled", False):
                        print(f"    [OK] Kollision aktiviert")
        else:
            print("[WARN] Keine Objekte in der Szene")
        
        # Hintergrundfarbe
        if "background_color" in scene:
            bg = scene["background_color"]
            print(f"[OK] Hintergrundfarbe: RGB({bg[0]}, {bg[1]}, {bg[2]})")
        
        print()
        return True
        
    except json.JSONDecodeError as e:
        print(f"[FEHLER] JSON-Fehler: {e}")
        return False
    except Exception as e:
        print(f"[FEHLER] Fehler beim Laden: {e}")
        return False

def test_sprite_sizes():
    """Test 4: Sprite-Größen prüfen"""
    print("=" * 60)
    print("TEST 4: Sprite-Größen Validierung")
    print("=" * 60)
    
    # Sprite-Größe aus project.json laden
    project_file = TEST_PROJECT / "project.json"
    sprite_size = None
    
    if project_file.exists():
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            sprite_size = config.get("sprite_size")
        except:
            pass
    
    if not sprite_size:
        print("[WARN] sprite_size nicht in project.json definiert - alle Bilder werden angezeigt")
        print()
        return True
    
    print(f"Erwartete Sprite-Groesse: {sprite_size}x{sprite_size}")
    print()
    
    # Assets prüfen
    assets_dir = TEST_PROJECT / "assets" / "images"
    if not assets_dir.exists():
        print("[WARN] assets/images/ Ordner existiert nicht")
        print()
        return True
    
    errors = []
    correct = []
    
    for img_file in assets_dir.rglob("*.png"):
        try:
            from PySide6.QtGui import QPixmap
            pixmap = QPixmap(str(img_file))
            if not pixmap.isNull():
                width = pixmap.width()
                height = pixmap.height()
                rel_path = img_file.relative_to(TEST_PROJECT)
                
                if width == sprite_size and height == sprite_size:
                    correct.append(rel_path)
                    print(f"[OK] {rel_path}: {width}x{height}")
                else:
                    errors.append((rel_path, width, height))
                    print(f"[FEHLER] {rel_path}: {width}x{height} (erwartet: {sprite_size}x{sprite_size})")
        except Exception as e:
            print(f"[FEHLER] Fehler beim Laden von {img_file.name}: {e}")
    
    print()
    if errors:
        print(f"[WARN] {len(errors)} Bilder haben falsche Groesse")
    if correct:
        print(f"[OK] {len(correct)} Bilder haben korrekte Groesse")
    print()
    
    return len(errors) == 0

def test_relative_paths():
    """Test 5: Relative Pfade in JSON prüfen"""
    print("=" * 60)
    print("TEST 5: Relative Pfade Validierung")
    print("=" * 60)
    
    scene_file = TEST_PROJECT / "scenes" / "level1.json"
    if not scene_file.exists():
        print("[FEHLER] level1.json nicht gefunden")
        return False
    
    try:
        with open(scene_file, 'r', encoding='utf-8') as f:
            scene = json.load(f)
        
        absolute_paths = []
        relative_paths = []
        
        for obj in scene.get("objects", []):
            sprite = obj.get("sprite")
            if sprite:
                if Path(sprite).is_absolute():
                    absolute_paths.append((obj.get("id", "unknown"), sprite))
                else:
                    relative_paths.append((obj.get("id", "unknown"), sprite))
        
        if absolute_paths:
            print("[WARN] Absolute Pfade gefunden (sollten relativ sein):")
            for obj_id, path in absolute_paths:
                print(f"  - {obj_id}: {path}")
        
        if relative_paths:
            print("[OK] Relative Pfade:")
            for obj_id, path in relative_paths:
                print(f"  - {obj_id}: {path}")
                # Prüfen ob Datei existiert
                full_path = TEST_PROJECT / path
                if full_path.exists():
                    print(f"    [OK] Datei existiert")
                else:
                    print(f"    [FEHLER] Datei nicht gefunden: {full_path}")
        
        print()
        return len(absolute_paths) == 0
        
    except Exception as e:
        print(f"[FEHLER] Fehler: {e}")
        return False

def main():
    """Hauptfunktion - führt alle Tests aus"""
    print("\n" + "=" * 60)
    print("UMFASSENDER TEST DES GAME EDITORS")
    print("=" * 60)
    print()
    
    if not TEST_PROJECT.exists():
        print(f"[FEHLER] Test-Projekt nicht gefunden: {TEST_PROJECT}")
        print("  Bitte erstellen Sie ein Test-Projekt oder passen Sie den Pfad an.")
        return
    
    results = []
    
    # Alle Tests ausführen
    results.append(("Projekt-Struktur", test_project_structure()))
    results.append(("project.json", test_project_json()))
    results.append(("level1.json", test_scene_json()))
    results.append(("Sprite-Größen", test_sprite_sizes()))
    results.append(("Relative Pfade", test_relative_paths()))
    
    # Zusammenfassung
    print("=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] BESTANDEN" if result else "[FEHLER] FEHLGESCHLAGEN"
        print(f"{test_name}: {status}")
    
    print()
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    print()
    
    if passed == total:
        print("[OK] Alle Tests bestanden!")
    else:
        print("[WARN] Einige Tests sind fehlgeschlagen. Bitte ueberpruefen Sie die Ausgabe oben.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
