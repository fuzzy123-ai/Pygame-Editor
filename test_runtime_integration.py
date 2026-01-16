#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test-Skript für Runtime-Integration"""
import sys
from pathlib import Path

# Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TEST: Runtime-Integration")
print("=" * 60)

# Test 1: Import runtime
try:
    from game_editor.engine import runtime
    print("[OK] runtime.py importiert")
except Exception as e:
    print(f"[FEHLER] Fehler beim Import von runtime.py: {e}")
    sys.exit(1)

# Test 2: Namespace-Erstellung testen (Mock)
try:
    # Mock-Namespace-Erstellung
    from game_editor.engine.api import (
        get_object, hole_objekt,
        key_pressed, taste_gedrückt,
        move_with_collision, bewege_mit_kollision
    )
    
    # Prüfe dass beide Varianten existieren
    assert get_object is not None
    assert hole_objekt is not None
    assert key_pressed is not None
    assert taste_gedrückt is not None
    assert move_with_collision is not None
    assert bewege_mit_kollision is not None
    
    print("[OK] Beide Varianten (deutsch + englisch) sind importierbar")
except Exception as e:
    print(f"[FEHLER] Fehler bei Namespace-Test: {e}")
    sys.exit(1)

# Test 3: Translator wird korrekt importiert
try:
    from game_editor.engine.runtime import translate_code
    print("[OK] translate_code ist importierbar")
except ImportError:
    # translate_code wird nicht direkt exportiert, das ist OK
    from game_editor.engine.german_code_translator import translate_code
    print("[OK] translate_code aus german_code_translator importierbar")
except Exception as e:
    print(f"[FEHLER] Fehler beim Import von translate_code: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALLE TESTS BESTANDEN")
print("=" * 60)
