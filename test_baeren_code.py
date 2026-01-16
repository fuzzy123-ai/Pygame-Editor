#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test ob deutscher Bären-Code funktioniert"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from game_editor.engine.german_code_translator import translate_code

print("=" * 60)
print("TEST: Deutscher Bären-Code")
print("=" * 60)

# Bären-Code (deutsch)
baeren_code = """bär = hole_objekt("object_15")

# Geschwindigkeit
geschwindigkeit = 3
schwerkraft = 0.5
geschwindigkeit_y = 0
auf_boden = falsch

funktion aktualisiere():
    global geschwindigkeit_y, auf_boden
    
    # Horizontal-Bewegung
    dx = 0
    wenn taste_gedrückt("LINKS"):
        dx = -geschwindigkeit
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit
    
    # Schwerkraft
    wenn nicht auf_boden:
        geschwindigkeit_y += schwerkraft
    
    # Bewegung mit automatischer Kollisionsbehandlung
    auf_boden, kollision_x, kollision_y = bewege_mit_kollision(bär, dx, geschwindigkeit_y)
    
    # Wenn auf Boden, Geschwindigkeit zurücksetzen
    wenn auf_boden:
        geschwindigkeit_y = 0
    
    # Sprung
    wenn taste_gedrückt("SPACE") und auf_boden:
        geschwindigkeit_y = -10
        auf_boden = falsch
"""

print("INPUT (Deutsch):")
print(baeren_code)

# Übersetzen
python_code, line_mapping = translate_code(baeren_code)

print("\n" + "=" * 60)
print("OUTPUT (Python):")
print("=" * 60)
print(python_code)

# Prüfe Übersetzung
checks = {
    "def aktualisiere" in python_code: "funktion → def",
    "if taste_gedrückt" in python_code: "wenn → if",
    "False" in python_code: "falsch → False",
    "if not auf_boden" in python_code: "wenn nicht → if not",
    "and auf_boden" in python_code: "und → and",
}

print("\n" + "=" * 60)
print("UEBERSETZUNGS-CHECKS:")
print("=" * 60)
all_passed = True
for check, description in checks.items():
    status = "[OK]" if check else "[FEHLER]"
    desc = description.replace("→", "->")
    print(f"{status} {desc}")
    if not check:
        all_passed = False

# Prüfe dass deutsche Funktionen NICHT übersetzt wurden
print("\n" + "=" * 60)
print("FUNKTIONS-CHECKS:")
print("=" * 60)
func_checks = {
    "hole_objekt" in python_code: "hole_objekt bleibt (Funktion)",
    "taste_gedrückt" in python_code: "taste_gedrückt bleibt (Funktion)",
    "bewege_mit_kollision" in python_code: "bewege_mit_kollision bleibt (Funktion)",
}
for check, description in func_checks.items():
    status = "[OK]" if check else "[FEHLER]"
    print(f"{status} {description}")
    if not check:
        all_passed = False

# Prüfe Syntax (kann Code kompiliert werden?)
print("\n" + "=" * 60)
print("SYNTAX-CHECK:")
print("=" * 60)
try:
    compile(python_code, "<test>", "exec")
    print("[OK] Code kann kompiliert werden!")
except SyntaxError as e:
    print(f"[FEHLER] Syntax-Fehler: {e}")
    all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("ALLE TESTS BESTANDEN!")
else:
    print("EINIGE TESTS FEHLGESCHLAGEN!")
print("=" * 60)

if not all_passed:
    sys.exit(1)
