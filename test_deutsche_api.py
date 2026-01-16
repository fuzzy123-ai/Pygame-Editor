#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test-Skript für deutsche API"""
import sys
from pathlib import Path

# Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

from game_editor.engine.german_code_translator import translate_code
from game_editor.engine.api import hole_objekt, taste_gedrückt, bewege_mit_kollision

print("=" * 60)
print("TEST 1: Translator - Einfache Übersetzung")
print("=" * 60)
code1 = """funktion test():
    wenn wahr:
        gib_zurueck 5"""
result1, _ = translate_code(code1)
print("INPUT:")
print(code1)
print("\nOUTPUT:")
print(result1)
print("\nERWARTET:")
print("def test():\n    if True:\n        return 5")
test1_passed = "def test" in result1 and "if True" in result1 and "return 5" in result1
print("\nTEST 1 PASSED" if test1_passed else "TEST 1 FAILED")

print("\n" + "=" * 60)
print("TEST 2: Translator - Strings bleiben unverändert")
print("=" * 60)
code2 = 'text = "wenn das wahr ist"\nfunktion test(): pass'
result2, _ = translate_code(code2)
print("INPUT:")
print(code2)
print("\nOUTPUT:")
print(result2)
expected2 = 'text = "wenn das wahr ist"'
print("\nERWARTET: String sollte 'wenn' enthalten")
test2_passed = expected2 in result2
print("TEST 2 PASSED" if test2_passed else f"TEST 2 FAILED - String wurde uebersetzt!")

print("\n" + "=" * 60)
print("TEST 3: Deutsche Funktionen importieren")
print("=" * 60)
print(f"hole_objekt: {hole_objekt}")
print(f"taste_gedrückt: {taste_gedrückt}")
print(f"bewege_mit_kollision: {bewege_mit_kollision}")
print("TEST 3 PASSED - Alle deutschen Funktionen importierbar")

print("\n" + "=" * 60)
print("TEST 4: Komplexeres Beispiel")
print("=" * 60)
code4 = """spieler = hole_objekt("player")
geschwindigkeit = 3

funktion aktualisiere():
    global geschwindigkeit
    dx = 0
    wenn taste_gedrückt("LINKS"):
        dx = -geschwindigkeit
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit
    auf_boden, kollision_x, kollision_y = bewege_mit_kollision(spieler, dx, 0)
    wenn auf_boden:
        drucke_debug("Auf Boden!")
"""
result4, _ = translate_code(code4)
print("INPUT (erste Zeilen):")
print(code4[:100] + "...")
print("\nOUTPUT (erste Zeilen):")
print(result4[:150] + "...")
test4_passed = "def aktualisiere" in result4 and "if taste_gedrückt" in result4
print("\nTEST 4 PASSED" if test4_passed else "TEST 4 FAILED")

print("\n" + "=" * 60)
print("ALLE TESTS ABGESCHLOSSEN")
print("=" * 60)
