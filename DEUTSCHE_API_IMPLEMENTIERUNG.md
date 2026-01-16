# Implementierungs-Plan: Deutsche Code API (Phase 1 + 2)

## 🎯 Übersicht

**Phase 1:** Deutsche Funktions-Aliase
- Alle API-Funktionen bekommen deutsche Aliase
- Beide Varianten (deutsch + englisch) funktionieren

**Phase 2:** Pre-Processor für deutsche Schlüsselwörter
- Übersetzt `funktion` → `def`, `wenn` → `if`, etc.
- Code kann komplett auf Deutsch sein

---

## 📋 Phase 1: Deutsche Funktions-Aliase

### 1.1. Dateien die geändert werden müssen

#### `game_editor/engine/api.py`
**Änderungen:**
- Deutsche Wrapper-Funktionen hinzufügen (für jede englische Funktion)
- Alle Funktionen bleiben unverändert (nur Aliase hinzufügen)

**Betroffene Funktionen:**
```python
# Englisch → Deutsch
get_object → hole_objekt
get_all_objects → hole_alle_objekte
key_pressed → taste_gedrückt
key_down → taste_runter
mouse_position → maus_position
print_debug → drucke_debug
spawn_object → erstelle_objekt
move_with_collision → bewege_mit_kollision
push_objects → drücke_objekte
lock_y_position → fixiere_y_position
unlock_y_position → entferne_y_fixierung
```

**Implementierung:**
```python
# Deutsche Aliase als Wrapper (einfach, keine Logik-Duplikation)
def hole_objekt(obj_id: str) -> Optional[GameObject]:
    """Deutsche Version von get_object()"""
    return get_object(obj_id)

def hole_alle_objekte() -> List[GameObject]:
    """Deutsche Version von get_all_objects()"""
    return get_all_objects()

# ... etc. für alle Funktionen
```

---

#### `game_editor/engine/gameobject.py`
**Änderungen:**
- Deutsche Methoden-Aliase für GameObject hinzufügen

**Betroffene Methoden:**
```python
collides_with → kollidiert_mit
destroy → zerstöre
```

**Implementierung:**
```python
def kollidiert_mit(self, other_id: str) -> bool:
    """Deutsche Version von collides_with()"""
    return self.collides_with(other_id)

def zerstöre(self):
    """Deutsche Version von destroy()"""
    self.destroy()
```

---

#### `game_editor/engine/runtime.py`
**Änderungen:**
- Deutsche Aliase zu beiden Namespaces hinzufügen (game_namespace und obj_namespace)
- 2 Stellen: `load_student_code()` (Zeile 58-86) und Objekt-Code-Namespace (Zeile 181-206)

**Betroffene Stellen:**
1. **game_namespace** (Zeile 58-86):
   ```python
   game_namespace = {
       # Englisch (bestehend)
       "get_object": get_object,
       "get_all_objects": get_all_objects,
       # ... etc.
       
       # Deutsch (neu)
       "hole_objekt": hole_objekt,
       "hole_alle_objekte": hole_alle_objekte,
       # ... etc.
   }
   ```

2. **obj_namespace** (Zeile 181-206):
   ```python
   obj_namespace = {
       # Englisch (bestehend)
       "get_object": get_object,
       # ... etc.
       
       # Deutsch (neu)
       "hole_objekt": hole_objekt,
       # ... etc.
   }
   ```

---

### 1.2. Potenzielle Bugs - Phase 1

#### Bug 1: Import-Fehler in runtime.py
**Problem:**
- Deutsche Funktionen werden nicht importiert
- `NameError: name 'hole_objekt' is not defined`

**Lösung:**
```python
# In runtime.py, Zeile 12-16:
from .api import (..., hole_objekt, hole_alle_objekte, taste_gedrückt, ...)
```

**Test:**
- Import-Statement prüfen
- Alle deutschen Funktionen müssen importiert werden

---

#### Bug 2: Zirkuläre Abhängigkeiten
**Problem:**
- `api.py` importiert `gameobject.py`
- `gameobject.py` könnte `api.py` importieren (zirkulär)

**Prüfung:**
- `gameobject.py` importiert NUR `pygame` und `image_fixer`
- KEINE zirkuläre Abhängigkeit ✅

**Test:**
- Import-Statements prüfen
- Keine zirkulären Abhängigkeiten

---

#### Bug 3: Alte Code funktioniert nicht mehr
**Problem:**
- Wenn nur deutsche Varianten hinzugefügt werden
- Alte Code (englisch) funktioniert nicht mehr

**Lösung:**
- Beide Varianten (deutsch + englisch) hinzufügen ✅
- Alte Code funktioniert weiterhin

**Test:**
- Bestehende Projekte mit englischem Code testen
- Sollte weiterhin funktionieren

---

#### Bug 4: GameObject-Methoden werden doppelt aufgerufen
**Problem:**
```python
def kollidiert_mit(self, other_id: str) -> bool:
    return self.collides_with(other_id)  # Ruft sich selbst auf?
```

**Prüfung:**
- `collides_with()` ist eine INSTANZ-Methode
- `kollidiert_mit()` ist eine NEUE Instanz-Methode
- KEIN Problem: `self.collides_with()` ruft die englische Version auf ✅

**Test:**
- Beide Methoden testen: `obj.collides_with("x")` und `obj.kollidiert_mit("x")`
- Sollten identisches Ergebnis haben

---

#### Bug 5: Typ-Hints fehlen
**Problem:**
- Deutsche Funktionen haben keine Typ-Hints
- IDE-Auto-Completion funktioniert nicht

**Lösung:**
- Typ-Hints von englischer Funktion kopieren
```python
def hole_objekt(obj_id: str) -> Optional[GameObject]:
    """Deutsche Version von get_object()"""
    return get_object(obj_id)
```

**Test:**
- Typ-Hints prüfen
- IDE-Auto-Completion testen

---

### 1.3. Test-Strategie - Phase 1

#### Test 1: Import-Test
```python
# test_api_deutsch.py
from game_editor.engine.api import (
    hole_objekt, hole_alle_objekte, taste_gedrückt, taste_runter,
    maus_position, drucke_debug, bewege_mit_kollision, etc.
)
# Sollte ohne Fehler funktionieren
```

#### Test 2: Funktionstest
```python
# Test dass deutsche Funktionen identisch mit englischen funktionieren
player = hole_objekt("player")
assert player == get_object("player")

alle = hole_alle_objekte()
assert alle == get_all_objects()
```

#### Test 3: Namespace-Test
```python
# Test dass beide Varianten im Namespace sind
# In runtime.py testen:
assert "hole_objekt" in game_namespace
assert "get_object" in game_namespace
assert game_namespace["hole_objekt"] == game_namespace["get_object"]
```

#### Test 4: GameObject-Methoden-Test
```python
# Test dass deutsche Methoden funktionieren
obj = GameObject(...)
result1 = obj.collides_with("enemy")
result2 = obj.kollidiert_mit("enemy")
assert result1 == result2

obj.destroy()
# Objekt sollte zerstört sein

obj2 = GameObject(...)
obj2.zerstöre()
# Objekt sollte zerstört sein
```

#### Test 5: Rückwärtskompatibilität
```python
# Bestehender Code (englisch) sollte funktionieren
player = get_object("player")
if key_pressed("RIGHT"):
    player.x += 4
# Sollte funktionieren
```

#### Test 6: Gemischter Code
```python
# Gemischter Code (deutsch + englisch) sollte funktionieren
spieler = get_object("player")  # Englisch
if taste_gedrückt("RECHTS"):    # Deutsch
    spieler.x += 4
# Sollte funktionieren
```

---

## 📋 Phase 2: Pre-Processor für deutsche Schlüsselwörter

### 2.1. Neue Datei: `game_editor/engine/german_code_translator.py`

**Zweck:**
- Übersetzt deutschen Code in Python-Code
- Wird vor `exec()` aufgerufen

**Struktur:**
```python
# game_editor/engine/german_code_translator.py
"""
Deutscher Code-Translator - Übersetzt deutschen Code in Python
"""
import re
from typing import Tuple, Dict, List

# Mapping: Deutsch → Python
GERMAN_TO_PYTHON = {
    # Schlüsselwörter
    "funktion": "def",
    "wenn": "if",
    "sonst": "else",
    "sonst_wenn": "elif",
    "für": "for",
    "während": "while",
    "gib_zurück": "return",
    "überspringen": "pass",
    "breche": "break",
    "mache_weiter": "continue",
    "versuche": "try",
    "außer": "except",
    "schließlich": "finally",
    "importiere": "import",
    "von": "from",
    "als": "as",
    "global": "global",
    "wahr": "True",
    "falsch": "False",
    "keine": "None",
    "und": "and",
    "oder": "or",
    "nicht": "not",
    "ist": "is",
    "in": "in",
    "mit": "with",
    
    # Ohne Umlaute (Alternative)
    "fuer": "for",
    "waehrend": "while",
    "gib_zurueck": "return",
    "ueberspringen": "pass",
    "ausser": "except",
    "schliesslich": "finally",
}

def translate_code(german_code: str) -> Tuple[str, Dict[int, int]]:
    """
    Übersetzt deutschen Code in Python-Code
    
    Args:
        german_code: Code mit deutschen Schlüsselwörtern
        
    Returns:
        Tuple (python_code, line_mapping)
        - python_code: Übersetzter Python-Code
        - line_mapping: Mapping von Zeile (deutsch) → Zeile (python)
                        für Fehlermeldungen
    """
    # ... Implementierung ...
```

---

### 2.2. Übersetzungs-Strategie

#### Problem: Wort-Grenzen
**Problem:**
- `wenn` sollte zu `if` werden
- Aber `wennspieler` sollte NICHT zu `ifspieler` werden

**Lösung:**
- Regex mit Wort-Grenzen (`\b`)
```python
# Nur ganze Wörter ersetzen
pattern = r'\bfunktion\b'
replacement = 'def'
code = re.sub(pattern, replacement, code)
```

---

#### Problem: In Strings
**Problem:**
```python
text = "wenn das wahr ist"  # Sollte NICHT übersetzt werden
```

**Lösung:**
- Nur außerhalb von Strings ersetzen
- Oder: Strings maskieren, ersetzen, dann demaskieren

**Einfachere Lösung (für MVP):**
- Nur Schlüsselwörter am Zeilenanfang oder nach bestimmten Zeichen ersetzen
- Für Anfang: Einfache Lösung ist ausreichend

**Bessere Lösung (für später):**
- Tokenisierung: Code in Tokens zerlegen
- Nur Schlüsselwort-Tokens ersetzen
- Strings bleiben unverändert

**Empfehlung für MVP:**
- Einfache Regex mit Wort-Grenzen (sollte in 99% der Fälle funktionieren)
- Dokumentation: "Strings mit deutschen Schlüsselwörtern werden möglicherweise übersetzt"
- Später: Bessere Tokenisierung

---

#### Problem: Kommentare
**Problem:**
```python
# wenn das wahr ist  # Sollte NICHT übersetzt werden
```

**Lösung:**
- Kommentare vor Übersetzung entfernen (maskieren)
- Übersetzen
- Kommentare wieder einfügen

**Einfachere Lösung:**
- Kommentare werden NICHT übersetzt (ist OK)
- Regex mit Wort-Grenzen ignoriert Kommentare meist

---

#### Problem: Mehrzeilige Strings
**Problem:**
```python
text = """wenn
das
wahr ist"""
```

**Lösung:**
- Strings maskieren (ersetzen durch Platzhalter)
- Übersetzen
- Strings wieder einfügen

**Implementierung:**
```python
# Strings finden und maskieren
string_pattern = r'("""[\s\S]*?"""|"""[\s\S]*?""")|'  # Triple quotes
                 r'(".*?")|'                            # Double quotes
                 r"('.*?')"                             # Single quotes

strings = []
def mask_string(match):
    strings.append(match.group(0))
    return f"__STRING_{len(strings)-1}__"

code = re.sub(string_pattern, mask_string, code, flags=re.MULTILINE)

# Übersetzen
# ...

# Strings wieder einfügen
for i, string in enumerate(strings):
    code = code.replace(f"__STRING_{i}__", string)
```

---

### 2.3. Integration in runtime.py

**Stelle 1:** `load_student_code()` (Zeile 88-97)
```python
# Code laden
with open(game_code_path, 'r', encoding='utf-8') as f:
    german_code = f.read()

# DEUTSCH: Übersetzen
from .german_code_translator import translate_code
python_code, line_mapping = translate_code(german_code)

# Test-Compile (mit Python-Code)
compile(python_code, str(game_code_path), 'exec')

# Code ausführen (mit Python-Code)
exec(python_code, game_namespace)
```

**Stelle 2:** Objekt-Code (Zeile 207-208)
```python
if obj_data and obj_data.get("code"):
    german_code = obj_data["code"]
    
    # DEUTSCH: Übersetzen
    python_code, line_mapping = translate_code(german_code)
    
    # Code ausführen
    exec(python_code, obj_namespace)
```

---

### 2.4. Fehlerbehandlung

#### Problem: Fehlermeldungen zeigen Python-Code
**Problem:**
- Schüler schreibt: `wenn x > 0:`
- Übersetzt zu: `if x > 0:`
- Fehlermeldung zeigt: `if x > 0:` (Python-Code)

**Lösung:**
- Fehlermeldungen zurückübersetzen (Zeile-Nummern müssen stimmen!)
- `line_mapping` verwenden: Zeile (Python) → Zeile (Deutsch)

**Implementierung:**
```python
except SyntaxError as e:
    # Zeile-Nummer zurückübersetzen
    if e.lineno and e.lineno in line_mapping:
        german_line = line_mapping[e.lineno]
        error_msg = f"SYNTAXFEHLER in Zeile {german_line}: {error_msg}"
    else:
        error_msg = translate_error(str(e))
```

---

### 2.5. Potenzielle Bugs - Phase 2

#### Bug 1: Regex ersetzt zu viel
**Problem:**
```python
variable_wenn = 5  # "wenn" wird zu "if" → variable_if = 5
```

**Lösung:**
- Wort-Grenzen verwenden (`\b`)
- Test: Variablen-Namen mit deutschen Schlüsselwörtern

---

#### Bug 2: Strings werden übersetzt
**Problem:**
```python
text = "wenn das wahr ist"  # Wird zu: text = "if das wahr ist"
```

**Lösung:**
- Strings maskieren (siehe oben)
- Test: Strings mit deutschen Schlüsselwörtern

---

#### Bug 3: Kommentare werden übersetzt
**Problem:**
```python
# wenn das wahr ist  # Wird zu: # if das wahr ist
```

**Lösung:**
- Kommentare maskieren oder ignorieren
- Test: Kommentare mit deutschen Schlüsselwörtern

---

#### Bug 4: Mehrzeilige Strings werden übersetzt
**Problem:**
```python
text = """wenn
das
wahr ist"""
```

**Lösung:**
- Strings maskieren (siehe oben)
- Test: Mehrzeilige Strings

---

#### Bug 5: Encoding-Probleme (Umlaute)
**Problem:**
- `für` enthält Umlaut
- Datei muss UTF-8 sein

**Lösung:**
- Sicherstellen dass alle Dateien UTF-8 sind
- Beim Laden: `encoding='utf-8'` (bereits vorhanden ✅)
- Test: Code mit Umlauten laden

---

#### Bug 6: Zeile-Nummern stimmen nicht
**Problem:**
- Fehlermeldung zeigt Zeile 5
- Aber Schüler-Code hat Fehler in Zeile 3

**Lösung:**
- `line_mapping` korrekt erstellen
- Test: Code mit Syntax-Fehler, prüfe Zeile-Nummer

---

#### Bug 7: Performance bei großen Dateien
**Problem:**
- Große Code-Dateien werden langsam übersetzt

**Lösung:**
- Regex ist schnell (auch bei 1000 Zeilen)
- Test: Große Datei (1000+ Zeilen)

---

#### Bug 8: Leere Dateien
**Problem:**
- Leere Datei führt zu Fehler

**Lösung:**
- Prüfen: `if not code or not code.strip():`
- Test: Leere Datei laden

---

### 2.6. Test-Strategie - Phase 2

#### Test 1: Einfache Übersetzung
```python
# Input:
german_code = """
funktion aktualisiere():
    wenn taste_gedrückt("RECHTS"):
        spieler.x += 4
"""

# Erwartet:
python_code = """
def aktualisiere():
    if taste_gedrückt("RECHTS"):
        spieler.x += 4
"""
```

#### Test 2: Strings bleiben unverändert
```python
# Input:
german_code = 'text = "wenn das wahr ist"'

# Erwartet:
python_code = 'text = "wenn das wahr ist"'  # KEINE Übersetzung
```

#### Test 3: Kommentare bleiben unverändert
```python
# Input:
german_code = '# wenn das wahr ist'

# Erwartet:
python_code = '# wenn das wahr ist'  # KEINE Übersetzung (oder OK wenn übersetzt)
```

#### Test 4: Variablen-Namen bleiben unverändert
```python
# Input:
german_code = 'variable_wenn = 5'

# Erwartet:
python_code = 'variable_wenn = 5'  # KEINE Übersetzung
```

#### Test 5: Gemischter Code (deutsch + englisch)
```python
# Input:
german_code = """
def update():  # Englisch
    wenn taste_gedrückt("RECHTS"):  # Deutsch
        player.x += 4
"""

# Erwartet:
python_code = """
def update():  # Englisch
    if taste_gedrückt("RECHTS"):  # Deutsch übersetzt
        player.x += 4
"""
```

#### Test 6: Fehlermeldungen zeigen richtige Zeile
```python
# Input (Zeile 3 hat Fehler):
german_code = """
funktion aktualisiere():
    wenn taste_gedrückt("RECHTS"):  # Zeile 3
        spieler.x +=  # Syntax-Fehler
"""

# Fehlermeldung sollte Zeile 3 zeigen (nicht übersetzte Zeile)
```

#### Test 7: Umlaute funktionieren
```python
# Input:
german_code = """
funktion aktualisiere():
    für objekt in alle_objekte:  # Mit Umlaut
        wenn objekt.sichtbar:
            objekt.aktualisiere()
"""

# Sollte korrekt übersetzt werden
```

#### Test 8: Komplexe Beispiele
```python
# Input:
german_code = """
spieler = hole_objekt("player")
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

# Sollte korrekt übersetzt werden und funktionieren
```

---

## 🔧 Implementierungs-Reihenfolge

### Schritt 1: Phase 1 implementieren
1. Deutsche Funktionen in `api.py` hinzufügen
2. Deutsche Methoden in `gameobject.py` hinzufügen
3. Import-Statements in `runtime.py` erweitern
4. Deutsche Aliase zu Namespaces hinzufügen
5. **Testen:** Einfache Tests ausführen
6. **Testen:** Bestehendes Projekt öffnen (sollte funktionieren)

### Schritt 2: Phase 2 implementieren
1. `german_code_translator.py` erstellen
2. Grundlegende Übersetzung implementieren (einfache Fälle)
3. Integration in `runtime.py`
4. **Testen:** Einfache Übersetzungen testen
5. Strings-Maskierung implementieren
6. **Testen:** Strings bleiben unverändert
7. Fehlerbehandlung mit Zeile-Mapping
8. **Testen:** Fehlermeldungen zeigen richtige Zeile
9. Edge Cases behandeln (leere Dateien, etc.)

### Schritt 3: Umfassende Tests
1. Alle Tests aus Test-Strategie ausführen
2. Bestehende Projekte testen (Rückwärtskompatibilität)
3. Neue Projekte mit deutschem Code testen
4. Gemischter Code testen
5. Edge Cases testen

---

## 🐛 Debugging-Strategie

### 1. Schrittweise Implementierung
- Nicht alles auf einmal implementieren
- Nach jedem Schritt testen
- Fehler sofort beheben

### 2. Logging hinzufügen
```python
# In german_code_translator.py
import logging
logger = logging.getLogger(__name__)

def translate_code(german_code: str) -> Tuple[str, Dict[int, int]]:
    logger.debug(f"Übersetze Code ({len(german_code)} Zeichen)")
    # ... Übersetzung ...
    logger.debug(f"Übersetzt zu {len(python_code)} Zeichen")
    return python_code, line_mapping
```

### 3. Test-Code schreiben
```python
# test_german_api.py
def test_hole_objekt():
    # Test dass hole_objekt funktioniert
    # ...

def test_translate_code():
    # Test dass Übersetzung funktioniert
    # ...
```

### 4. Editor starten und manuell testen
- Editor starten
- Projekt öffnen
- Code auf Deutsch schreiben
- Spiel starten
- Prüfen ob Fehler auftreten
- Console-Ausgaben prüfen

---

## ✅ Checkliste vor Implementierung

- [ ] Alle Dateien identifiziert, die geändert werden müssen
- [ ] Alle Funktionen identifiziert, die Aliase brauchen
- [ ] Übersetzungs-Mapping vollständig
- [ ] Edge Cases identifiziert
- [ ] Test-Strategie entwickelt
- [ ] Debugging-Strategie entwickelt

---

## ✅ Checkliste nach Implementierung

### Phase 1:
- [ ] Alle deutschen Funktionen in `api.py` hinzugefügt
- [ ] Alle deutschen Methoden in `gameobject.py` hinzugefügt
- [ ] Import-Statements erweitert
- [ ] Deutsche Aliase zu Namespaces hinzugefügt
- [ ] Bestehende Projekte funktionieren weiterhin
- [ ] Neue Projekte können deutsche Funktionen verwenden

### Phase 2:
- [ ] `german_code_translator.py` erstellt
- [ ] Grundlegende Übersetzung funktioniert
- [ ] Strings bleiben unverändert
- [ ] Kommentare bleiben unverändert (oder werden korrekt behandelt)
- [ ] Fehlermeldungen zeigen richtige Zeile-Nummern
- [ ] Edge Cases behandelt (leere Dateien, etc.)
- [ ] Integration in `runtime.py` funktioniert
- [ ] Code mit deutschen Schlüsselwörtern funktioniert

### Tests:
- [ ] Alle Tests aus Test-Strategie ausgeführt
- [ ] Bestehende Projekte getestet
- [ ] Neue Projekte mit deutschem Code getestet
- [ ] Gemischter Code getestet
- [ ] Edge Cases getestet
- [ ] Editor startet ohne Fehler
- [ ] Spiel startet ohne Fehler
- [ ] Code wird korrekt ausgeführt
