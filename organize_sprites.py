"""
Skript zum Organisieren der Sprites
"""
from pathlib import Path
from game_editor.utils.sprite_organizer import SpriteOrganizer
from game_editor.utils.spritesheet_extractor import SpritesheetExtractor
import sys

print("=" * 60)
print("Sprite-Organisation")
print("=" * 60)
print()

# Projekt-Pfad abfragen
if len(sys.argv) > 1:
    project_path = Path(sys.argv[1])
else:
    project_input = input("Projekt-Ordner Pfad (oder Enter für Template): ").strip()
    if project_input:
        project_path = Path(project_input)
    else:
        project_path = Path(__file__).parent / "game_editor" / "templates" / "empty_project"

if not project_path.exists():
    print(f"[FEHLER] Projekt-Ordner nicht gefunden: {project_path}")
    sys.exit(1)

print(f"Projekt: {project_path}")
print()

# Prüfen ob sprites/ Ordner existiert
sprites_folder = project_path / "sprites"
if not sprites_folder.exists():
    print("[WARN] sprites/ Ordner existiert nicht!")
    print(f"Erstelle: {sprites_folder}")
    sprites_folder.mkdir(parents=True, exist_ok=True)
    print("Bitte legen Sie Ihre Sprites dort ab und starten Sie das Skript erneut.")
    sys.exit(0)

# Sprites auflisten
image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
sprite_files = [f for f in sprites_folder.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]

if not sprite_files:
    print("[WARN] Keine Sprites gefunden im sprites/ Ordner!")
    sys.exit(0)

print(f"Gefundene Sprites ({len(sprite_files)}):")
for sprite_file in sprite_files:
    print(f"  - {sprite_file.name}")
print()

# 1. Character-Sheets organisieren (nach Name)
print("[1/2] Organisiere Character-Sheets...")
organizer = SpriteOrganizer(project_path)
moved_count, errors = organizer.organize_sprites(strategy="name")

if moved_count > 0:
    print(f"   [OK] {moved_count} Sprite(s) organisiert")
    if errors:
        print(f"   [WARN] Warnungen: {len(errors)}")
        for error in errors[:3]:
            print(f"      - {error}")
else:
    if errors:
        print(f"   [WARN] Fehler:")
        for error in errors:
            print(f"      - {error}")

print()

# 2. Spritesheet extrahieren (falls vorhanden)
print("[2/2] Pruefe Spritesheet...")
spritesheet_path = project_path / "sprites" / "spritesheet.png"

if spritesheet_path.exists():
    print(f"   Spritesheet gefunden: {spritesheet_path.name}")
    
    # Sprite-Größe abfragen
    print("   Sprite-Größe eingeben:")
    try:
        width = int(input("   Breite (Standard: 32): ") or "32")
        height = int(input("   Hoehe (Standard: 32): ") or "32")
        spacing = int(input("   Abstand zwischen Sprites (Standard: 0): ") or "0")
        margin = int(input("   Rand um Sheet (Standard: 0): ") or "0")
    except ValueError:
        print("   [WARN] Ungueltige Eingabe, verwende Standard-Werte")
        width, height, spacing, margin = 32, 32, 0, 0
    
    print(f"   Extrahiere Sprites ({width}x{height}, Abstand: {spacing}, Rand: {margin})...")
    
    extractor = SpritesheetExtractor(project_path)
    extracted_count, errors = extractor.extract_from_grid(
        spritesheet_path,
        sprite_width=width,
        sprite_height=height,
        output_folder="environment",
        spacing=spacing,
        margin=margin
    )
    
    if extracted_count > 0:
        print(f"   [OK] {extracted_count} Sprite(s) extrahiert")
        if errors:
            print(f"   [WARN] Warnungen: {len(errors)}")
            for error in errors[:3]:
                print(f"      - {error}")
    else:
        print(f"   [WARN] Keine Sprites extrahiert")
        if errors:
            for error in errors:
                print(f"      - {error}")
else:
    print("   [INFO] Kein Spritesheet gefunden (spritesheet.png)")

print()
print("=" * 60)
print("Fertig!")
print("=" * 60)
print()
print("Organisierte Sprites finden Sie in:")
print(f"  {project_path / 'assets' / 'images'}")
