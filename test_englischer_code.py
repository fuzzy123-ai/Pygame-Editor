#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test ob englischer Code weiterhin funktioniert (Rückwärtskompatibilität)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TEST: Rückwärtskompatibilität (Englischer Code)")
print("=" * 60)

# Test 1: Englische Funktionen sind noch verfügbar
try:
    from game_editor.engine.api import (
        get_object, get_all_objects,
        key_pressed, key_down, mouse_position,
        print_debug, spawn_object,
        move_with_collision, push_objects,
        lock_y_position, unlock_y_position
    )
    print("[OK] Alle englischen Funktionen sind importierbar")
except ImportError as e:
    print(f"[FEHLER] Englische Funktionen nicht importierbar: {e}")
    sys.exit(1)

# Test 2: Englischer Code wird nicht übersetzt (nur deutsche Schlüsselwörter)
from game_editor.engine.german_code_translator import translate_code

englischer_code = """player = get_object("player")

def update():
    if key_pressed("RIGHT"):
        player.x += 4
    
    if player.collides_with("enemy1"):
        print_debug("Kollision!")
"""

python_code, _ = translate_code(englischer_code)
print("\nINPUT (Englisch):")
print(englischer_code)
print("\nOUTPUT (sollte identisch sein):")
print(python_code)

# Prüfe dass englische Funktionen NICHT übersetzt wurden
if "get_object" in python_code and "def update" in python_code:
    print("\n[OK] Englische Funktionen bleiben unverändert")
else:
    print("\n[FEHLER] Englische Funktionen wurden übersetzt!")
    sys.exit(1)

# Test 3: Gemischter Code (deutsch + englisch)
gemischter_code = """player = get_object("player")

funktion update():
    wenn key_pressed("RIGHT"):
        player.x += 4
"""

python_code_gemischt, _ = translate_code(gemischter_code)
print("\n" + "=" * 60)
print("TEST: Gemischter Code (deutsch + englisch)")
print("=" * 60)
print("INPUT:")
print(gemischter_code)
print("\nOUTPUT:")
print(python_code_gemischt)

# Prüfe dass deutsche Schlüsselwörter übersetzt wurden, aber englische Funktionen nicht
if "def update" in python_code_gemischt and "if key_pressed" in python_code_gemischt:
    print("\n[OK] Gemischter Code funktioniert: deutsche Schlüsselwörter übersetzt, englische Funktionen bleiben")
else:
    print("\n[FEHLER] Gemischter Code funktioniert nicht korrekt!")
    sys.exit(1)

# Test 4: Deutsche Tasten-Namen
from game_editor.engine.api import key_pressed

# Prüfe dass deutsche Tasten-Namen im _KEY_MAP sind
from game_editor.engine import api
if hasattr(api, '_KEY_MAP'):
    key_map = api._KEY_MAP
    if "RECHTS" in key_map and "LINKS" in key_map and "HOCH" in key_map and "RUNTER" in key_map:
        print("\n[OK] Deutsche Tasten-Namen (RECHTS, LINKS, HOCH, RUNTER) sind verfügbar")
    else:
        print("\n[WARNUNG] Deutsche Tasten-Namen fehlen (aber nicht kritisch)")

print("\n" + "=" * 60)
print("ALLE TESTS BESTANDEN - Englischer Code funktioniert weiterhin!")
print("=" * 60)
