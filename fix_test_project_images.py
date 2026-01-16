"""
Skript zum Beheben von iCCP-Profil-Problemen in allen Bildern des Test-Projekts
"""
from pathlib import Path
from game_editor.utils.image_fixer import fix_images_in_directory
import sys

# Test-Projekt-Pfad
script_dir = Path(__file__).parent
test_project_path = script_dir / "Test_Project"

if not test_project_path.exists():
    print(f"[FEHLER] Test-Projekt nicht gefunden: {test_project_path}")
    sys.exit(1)

print("=" * 60)
print("iCCP-Profil-Korrektur für Test-Projekt")
print("=" * 60)
print()

# Sprites-Ordner
sprites_folder = test_project_path / "sprites"
if sprites_folder.exists():
    print(f"[1/2] Verarbeite sprites/ Ordner...")
    fixed_count, errors = fix_images_in_directory(sprites_folder, recursive=True)
    print(f"   [OK] {fixed_count} Bild(er) korrigiert")
    if errors:
        print(f"   [FEHLER] {len(errors)} Fehler:")
        for error in errors[:10]:  # Maximal 10 Fehler anzeigen
            print(f"      - {error}")
else:
    print(f"[WARN] sprites/ Ordner nicht gefunden: {sprites_folder}")

# Assets-Ordner
assets_images_folder = test_project_path / "assets" / "images"
if assets_images_folder.exists():
    print(f"[2/2] Verarbeite assets/images/ Ordner...")
    fixed_count, errors = fix_images_in_directory(assets_images_folder, recursive=True)
    print(f"   [OK] {fixed_count} Bild(er) korrigiert")
    if errors:
        print(f"   [FEHLER] {len(errors)} Fehler:")
        for error in errors[:10]:  # Maximal 10 Fehler anzeigen
            print(f"      - {error}")
else:
    print(f"[WARN] assets/images/ Ordner nicht gefunden: {assets_images_folder}")

print()
print("Fertig!")
