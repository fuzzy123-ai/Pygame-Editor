"""
Test-Skript um Editor zu testen ohne GUI zu öffnen
"""
import sys
from pathlib import Path

print("Testing Editor Components...")
print("=" * 50)

# Test 1: Imports
print("\n1. Testing imports...")
try:
    from game_editor.engine import runtime, loader, collision, api, gameobject
    print("   [OK] Engine imports OK")
except Exception as e:
    print(f"   [FAIL] Engine import failed: {e}")
    sys.exit(1)

try:
    from game_editor.ui import main_window, scene_canvas, asset_browser, code_editor, inspector, console
    print("   [OK] UI imports OK")
except Exception as e:
    print(f"   [FAIL] UI import failed: {e}")
    sys.exit(1)

# Test 2: QScintilla
print("\n2. Testing QScintilla...")
try:
    from PySide6.Qsci import QsciScintilla
    print("   [OK] QScintilla available")
except ImportError:
    print("   [WARN] QScintilla not available (using fallback)")

# Test 3: Pygame
print("\n3. Testing Pygame...")
try:
    import pygame
    pygame.init()
    print(f"   [OK] Pygame OK ({pygame.version.ver})")
    pygame.quit()
except Exception as e:
    print(f"   [FAIL] Pygame failed: {e}")
    sys.exit(1)

# Test 4: PySide6
print("\n4. Testing PySide6...")
try:
    from PySide6.QtWidgets import QApplication
    print("   [OK] PySide6 OK")
except Exception as e:
    print(f"   [FAIL] PySide6 failed: {e}")
    sys.exit(1)

# Test 5: Template
print("\n5. Testing template...")
template_path = Path(__file__).parent / "game_editor" / "templates" / "empty_project"
if template_path.exists():
    print(f"   [OK] Template found at {template_path}")
    if (template_path / "project.json").exists():
        print("   [OK] project.json exists")
    if (template_path / "scenes" / "level1.json").exists():
        print("   [OK] level1.json exists")
    if (template_path / "code" / "game.py").exists():
        print("   [OK] game.py exists")
else:
    print(f"   [WARN] Template not found at {template_path}")

print("\n" + "=" * 50)
print("All tests passed! Editor should work.")
print("\nTo start the editor, run:")
print("  python -m game_editor.editor")
print("  or")
print("  start_editor.bat")
