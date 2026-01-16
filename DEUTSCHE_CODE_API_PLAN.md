# Plan: Deutsche Code-API für Schüler

## 🎯 Ziel
Alle Code, der über den Editor geschrieben wird, soll komplett auf Deutsch sein:
- **Funktionen:** `def` → `funktion`
- **Schleifen:** `for` → `für`, `while` → `während`
- **Bedingungen:** `if` → `wenn`, `else` → `sonst`, `elif` → `sonst_wenn`
- **Befehle:** `return` → `gib_zurück`, `pass` → `überspringen`
- **Variablen:** Können auf Deutsch sein
- **API-Funktionen:** Bereits auf Deutsch (z.B. `get_object`, `key_pressed`)

---

## 🔧 Technische Umsetzung

### Option 1: Pre-Processor (Empfohlen)
**Wie es funktioniert:**
1. Schüler schreibt Code auf Deutsch
2. Pre-Processor übersetzt deutschen Code in Python
3. Python-Code wird normal ausgeführt

**Vorteile:**
- ✅ Keine Änderungen an Python-Interpreter nötig
- ✅ Funktioniert mit bestehender `exec()` Struktur
- ✅ Fehlerbehandlung bleibt erhalten
- ✅ Syntax-Highlighting kann angepasst werden

**Nachteile:**
- ⚠️ Pre-Processing-Schritt nötig
- ⚠️ Fehlermeldungen zeigen Python-Code (können aber übersetzt werden)

**Implementierung:**
- Neue Datei: `game_editor/engine/german_code_translator.py`
- Übersetzt deutschen Code vor `exec()`
- Fehlermeldungen werden zurückübersetzt (Zeile-Nummern bleiben korrekt)

### Option 2: Namespace-Aliase (Einfacher, aber limitiert)
**Wie es funktioniert:**
- Deutsche Funktionen als Aliase im Namespace
- Python-Schlüsselwörter bleiben englisch

**Nachteile:**
- ❌ Python-Schlüsselwörter (`if`, `for`, `def`) können nicht übersetzt werden
- ❌ Nur Funktionen können übersetzt werden

**Fazit:** Nicht ausreichend für vollständig deutschen Code

---

## 📋 Mapping: Deutsch → Python

### Schlüsselwörter

| Deutsch | Python | Beispiel |
|---------|--------|----------|
| Deutsch (mit Umlaut) | Deutsch (ohne Umlaut) | Python | Beispiel |
|---------------------|----------------------|--------|----------|
| `funktion` | `funktion` | `def` | `funktion aktualisieren():` |
| `wenn` | `wenn` | `if` | `wenn taste_gedrückt("LINKS"):` |
| `sonst` | `sonst` | `else` | `sonst:` |
| `sonst_wenn` | `sonst_wenn` | `elif` | `sonst_wenn x > 10:` |
| `für` | `fuer` | `for` | `für objekt in alle_objekte:` oder `fuer objekt in alle_objekte:` |
| `während` | `waehrend` | `while` | `während laufen:` oder `waehrend laufen:` |
| `gib_zurück` | `gib_zurueck` | `return` | `gib_zurück ergebnis` oder `gib_zurueck ergebnis` |
| `überspringen` | `ueberspringen` | `pass` | `überspringen` oder `ueberspringen` |
| `breche` | `breche` | `break` | `breche` |
| `mache_weiter` | `mache_weiter` | `continue` | `mache_weiter` |
| `versuche` | `versuche` | `try` | `versuche:` |
| `außer` | `ausser` | `except` | `außer Fehler:` oder `ausser Fehler:` |
| `schließlich` | `schliesslich` | `finally` | `schließlich:` oder `schliesslich:` |
| `importiere` | `importiere` | `import` | `importiere pygame` |
| `von` | `von` | `from` | `von pygame importiere` |
| `als` | `als` | `as` | `importiere pygame als pg` |
| `global` | `global` | `global` | `global geschwindigkeit` |
| `wahr` | `wahr` | `True` | `laufen = wahr` |
| `falsch` | `falsch` | `False` | `laufen = falsch` |
| `keine` | `keine` | `None` | `objekt = keine` |
| `und` | `und` | `and` | `wenn x > 0 und y > 0:` |
| `oder` | `oder` | `or` | `wenn x > 0 oder y > 0:` |
| `nicht` | `nicht` | `not` | `wenn nicht sichtbar:` |
| `ist` | `ist` | `is` | `wenn objekt ist keine:` |
| `in` | `in` | `in` | `wenn "LINKS" in gedrückte_tasten:` |
| `mit` | `mit` | `with` | `mit datei öffnen("test.txt"):` |

**Hinweis:** Beide Varianten (mit und ohne Umlaute) funktionieren. Schüler können wählen, was für ihre Tastatur einfacher ist.

### Operatoren (bleiben gleich)
- `+`, `-`, `*`, `/`, `%`, `**`, `//`
- `==`, `!=`, `<`, `>`, `<=`, `>=`
- `=`, `+=`, `-=`, `*=`, `/=`

### Kommentare
- `#` bleibt (kann auch `//` sein, aber `#` ist Python-Standard)

---

## ✅ Bereits vorhandene deutsche Funktionen

### Objekt-Funktionen
- ✅ `get_object(id)` → `hole_objekt(id)` (neu)
- ✅ `get_all_objects()` → `hole_alle_objekte()` (neu)

### Input-Funktionen
- ✅ `key_pressed(key)` → `taste_gedrückt(taste)` (neu)
- ✅ `key_down(key)` → `taste_runter(taste)` (neu)
- ✅ `mouse_position()` → `maus_position()` (neu)

### Bewegung & Kollision
- ✅ `move_with_collision(obj, dx, dy)` → `bewege_mit_kollision(obj, dx, dy)` (neu)
- ✅ `push_objects(obj, dx, dy)` → `drücke_objekte(obj, dx, dy)` (neu)
- ✅ `lock_y_position(obj, y)` → `fixiere_y_position(obj, y)` (neu)
- ✅ `unlock_y_position(obj)` → `entferne_y_fixierung(obj)` (neu)

### Debug & Utility
- ✅ `print_debug(text)` → `drucke_debug(text)` (neu)
- ✅ `spawn_object(template)` → `erstelle_objekt(vorlage)` (neu)

### GameObject-Attribute (bereits vorhanden)
- ✅ `obj.x`, `obj.y`, `obj.width`, `obj.height`
- ✅ `obj.visible`, `obj.sprite`, `obj.id`
- ✅ `obj.collides_with(other_id)` → `obj.kollidiert_mit(andere_id)` (neu)
- ✅ `obj.destroy()` → `obj.zerstöre()` (neu)
- ✅ `obj.is_ground`, `obj.is_camera`

---

## 🆕 Noch zu implementierende Funktionen (für vollständiges Spiel)

### Zeit & Timer
- ❌ `warte(sekunden)` - Wartet X Sekunden
- ❌ `hole_zeit()` - Gibt aktuelle Zeit zurück (seit Spielstart)
- ❌ `hole_delta_zeit()` - Gibt Zeit seit letztem Frame zurück

### Zufall
- ❌ `zufallszahl(min, max)` - Gibt zufällige Zahl zwischen min und max zurück
- ❌ `zufällige_wahl(liste)` - Wählt zufälliges Element aus Liste

### Mathematik
- ❌ `abstand(x1, y1, x2, y2)` - Berechnet Abstand zwischen zwei Punkten
- ❌ `winkel(x1, y1, x2, y2)` - Berechnet Winkel zwischen zwei Punkten
- ❌ `normalisiere_wert(wert, min_alt, max_alt, min_neu, max_neu)` - Mappt Wert von einem Bereich in anderen

### Listen & Sammlungen
- ❌ `finde_objekte_mit_typ(typ)` - Findet alle Objekte mit bestimmten Typ
- ❌ `finde_objekte_in_bereich(x, y, breite, höhe)` - Findet Objekte in Bereich
- ❌ `sortiere_nach_entfernung(liste, x, y)` - Sortiert Liste nach Entfernung zu Punkt

### Szenen & Level
- ❌ `lade_szene(szene_name)` - Lädt neue Szene
- ❌ `aktuelle_szene()` - Gibt Namen der aktuellen Szene zurück
- ❌ `spiel_neustarten()` - Startet Spiel neu

### Objekt-Management
- ❌ `erstelle_objekt_bei_position(typ, x, y)` - Erstellt Objekt an Position
- ❌ `finde_objekt_mit_name(name)` - Findet Objekt anhand Name (nicht ID)
- ❌ `zähle_objekte_mit_typ(typ)` - Zählt Objekte mit bestimmten Typ

### Text & UI (optional, für einfache Spiele)
- ❌ `zeige_text(text, x, y, farbe)` - Zeigt Text auf Bildschirm
- ❌ `zeige_zahl(zahl, x, y, farbe)` - Zeigt Zahl auf Bildschirm
- ❌ `hole_text_breite(text)` - Gibt Breite von Text zurück

### Sound (später, wenn Sound-System implementiert)
- ❌ `spiele_sound(sound_id)` - Spielt Sound ab
- ❌ `stoppe_sound(sound_id)` - Stoppt Sound
- ❌ `setze_lautstärke(lautstärke)` - Setzt Lautstärke (0.0 - 1.0)

### Animation (später, wenn Animation-System implementiert)
- ❌ `spiele_animation(obj, animation_name)` - Spielt Animation ab
- ❌ `setze_animation(obj, animation_name)` - Setzt Animation (ohne zu spielen)

### Kollision (erweitert)
- ❌ `prüfe_kollision_mit_typ(obj, typ)` - Prüft Kollision mit Objekten bestimmten Typs
- ❌ `hole_kollidierende_objekte(obj)` - Gibt Liste aller kollidierenden Objekte zurück
- ❌ `prüfe_kollision_mit_maus(x, y)` - Prüft ob Maus auf Objekt klickt

### Physik (einfach, für Schüler)
- ❌ `setze_schwerkraft(obj, schwerkraft)` - Setzt Schwerkraft für Objekt
- ❌ `setze_geschwindigkeit(obj, vx, vy)` - Setzt Geschwindigkeit
- ❌ `hole_geschwindigkeit(obj)` - Gibt Geschwindigkeit zurück (vx, vy)

---

## 📝 Beispiel: Vorher vs. Nachher

### Vorher (Englisch):
```python
player = get_object("player")
speed = 3
gravity = 0.5
velocity_y = 0
on_ground = False

def update():
    global velocity_y, on_ground
    
    dx = 0
    if key_pressed("LEFT"):
        dx = -speed
    if key_pressed("RIGHT"):
        dx = speed
    
    if not on_ground:
        velocity_y += gravity
    
    on_ground, collision_x, collision_y = move_with_collision(player, dx, velocity_y)
    
    if on_ground:
        velocity_y = 0
    
    if key_down("SPACE") and on_ground:
        velocity_y = -10
        on_ground = False
```

### Nachher (Deutsch):
```python
spieler = hole_objekt("player")
geschwindigkeit = 3
schwerkraft = 0.5
geschwindigkeit_y = 0
auf_boden = falsch

funktion aktualisiere():
    global geschwindigkeit_y, auf_boden
    
    dx = 0
    wenn taste_gedrückt("LINKS"):
        dx = -geschwindigkeit
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit
    
    wenn nicht auf_boden:
        geschwindigkeit_y += schwerkraft
    
    auf_boden, kollision_x, kollision_y = bewege_mit_kollision(spieler, dx, geschwindigkeit_y)
    
    wenn auf_boden:
        geschwindigkeit_y = 0
    
    wenn taste_runter("LEERTASTE") und auf_boden:
        geschwindigkeit_y = -10
        auf_boden = falsch
```

---

## 🏗️ Implementierungs-Plan

### Phase 1: Pre-Processor (Kern)
1. **Datei erstellen:** `game_editor/engine/german_code_translator.py`
2. **Funktionen:**
   - `translate_german_to_python(code: str) -> str` - Übersetzt deutschen Code
   - `translate_error_to_german(error: str, line_number: int) -> str` - Übersetzt Fehlermeldungen
3. **Integration:** In `runtime.py` vor **beiden** `exec()` Aufrufen:
   - ✅ `load_student_code()` - für `game.py` (Zeile 97)
   - ✅ Objekt-Code-Ausführung - für Objekt-Code (Zeile 208)
4. **WICHTIG:** Beide Code-Quellen müssen übersetzt werden!

### Phase 2: Deutsche API-Funktionen
1. **Aliase hinzufügen:** In `api.py` deutsche Funktionen als Aliase
2. **Namespace erweitern:** In `runtime.py` deutsche Namen hinzufügen
   - ✅ `game_namespace` (für `game.py`, Zeile 58-86)
   - ✅ `obj_namespace` (für Objekt-Code, Zeile 181-206)
   - **WICHTIG:** Beide Namespaces müssen identische deutsche Aliase haben!
3. **Beide Namen unterstützen:** Englisch UND Deutsch (für Migration)

### Phase 3: Fehlermeldungen
1. **Fehler-Übersetzung:** Zeile-Nummern korrekt mappen
   - ✅ `translate_error()` existiert bereits (Zeile 30-36 in runtime.py)
   - ⚠️ Muss erweitert werden für deutsche Schlüsselwörter
2. **Syntax-Fehler:** Deutsche Übersetzungen für Python-Fehler
   - ✅ `ERROR_TRANSLATIONS` existiert bereits (Zeile 22-27)
   - ⚠️ Muss erweitert werden
3. **Runtime-Fehler:** Deutsche Übersetzungen für Laufzeit-Fehler
4. **Fehler-Quellen:** Beide Code-Quellen müssen unterstützt werden:
   - ✅ `game.py` Fehler (Zeile 99-109)
   - ✅ Objekt-Code Fehler (Zeile 210-213)

### Phase 4: Syntax-Highlighting
1. **Highlighter erweitern:** Deutsche Schlüsselwörter erkennen
2. **Farben:** Deutsche Schlüsselwörter wie Python-Keywords behandeln

### Phase 5: Dokumentation & Beispiele
1. **Hilfe-Overlay:** Deutsche Befehle dokumentieren
2. **Beispiele:** Deutsche Code-Beispiele
3. **Templates:** Deutsche Starter-Templates
   - ✅ **Template 1:** `game_editor/templates/empty_project/code/game.py` - deutsche Version erstellen
     - Wird beim Erstellen neuer Projekte kopiert
   - ✅ **Template 2:** Standard-Code in `code_editor.py` (Zeile 559-571) - deutsche Version
     - Fallback wenn `game.py` fehlt in bestehendem Projekt
   - ✅ **Template 3:** Standard-Code in `code_editor.py` (Zeile 632-640) - deutsche Version
     - Fallback wenn Objekt keinen Code hat
   - 📄 **Siehe:** `TEMPLATE_ERKLAERUNG.md` für detaillierte Erklärung aller 3 Templates

---

## 🔍 Technische Details

### Pre-Processor Implementation

```python
# game_editor/engine/german_code_translator.py

GERMAN_TO_PYTHON = {
    # Schlüsselwörter (mit Umlauten)
    'funktion': 'def',
    'wenn': 'if',
    'sonst': 'else',
    'sonst_wenn': 'elif',
    'für': 'for',
    'während': 'while',
    'gib_zurück': 'return',
    'überspringen': 'pass',
    'breche': 'break',
    'mache_weiter': 'continue',
    'versuche': 'try',
    'außer': 'except',
    'schließlich': 'finally',
    'importiere': 'import',
    'von': 'from',
    'als': 'as',
    'wahr': 'True',
    'falsch': 'False',
    'keine': 'None',
    'und': 'and',
    'oder': 'or',
    'nicht': 'not',
    'ist': 'is',
    'in': 'in',  # Bleibt gleich, aber wird erkannt
    'mit': 'with',
    
    # Schlüsselwörter (ohne Umlaute - Alternative)
    'fuer': 'for',           # Alternative zu 'für'
    'waehrend': 'while',     # Alternative zu 'während'
    'gib_zurueck': 'return', # Alternative zu 'gib_zurück'
    'ueberspringen': 'pass', # Alternative zu 'überspringen'
    'ausser': 'except',      # Alternative zu 'außer'
    'schliesslich': 'finally', # Alternative zu 'schließlich'
    
    # API-Funktionen (werden im Namespace gemappt)
    # Diese werden NICHT hier übersetzt, sondern im Namespace
}

def translate_german_to_python(code: str) -> str:
    """
    Übersetzt deutschen Code in Python-Code.
    
    WICHTIG: Übersetzt nur Schlüsselwörter, nicht Funktionen!
    Funktionen werden im Namespace gemappt.
    """
    lines = code.split('\n')
    translated_lines = []
    
    for line in lines:
        # Kommentare beibehalten
        if line.strip().startswith('#'):
            translated_lines.append(line)
            continue
        
        # Schlüsselwörter ersetzen (nur ganze Wörter)
        translated_line = line
        for german, python in GERMAN_TO_PYTHON.items():
            # Regex: Nur ganze Wörter ersetzen
            pattern = r'\b' + re.escape(german) + r'\b'
            translated_line = re.sub(pattern, python, translated_line)
        
        translated_lines.append(translated_line)
    
    return '\n'.join(translated_lines)
```

### Namespace-Erweiterung

**WICHTIG:** Es gibt ZWEI Namespaces, die beide erweitert werden müssen!

```python
# In runtime.py, load_student_code() - für game.py:

def _create_game_namespace():
    """Erstellt Namespace für game.py UND Objekt-Code (beide identisch!)"""
    return {
        # Englische Namen (für Kompatibilität)
        "get_object": get_object,
        "get_all_objects": get_all_objects,
        "key_pressed": key_pressed,
        "key_down": key_down,
        "mouse_position": mouse_position,
        "print_debug": print_debug,
        "spawn_object": spawn_object,
        "move_with_collision": move_with_collision,
        "push_objects": push_objects,
        "lock_y_position": lock_y_position,
        "unlock_y_position": unlock_y_position,
        
        # Deutsche Namen (neue API)
        "hole_objekt": get_object,
        "hole_alle_objekte": get_all_objects,
        "taste_gedrückt": key_pressed,
        "taste_runter": key_down,
        "maus_position": mouse_position,
        "bewege_mit_kollision": move_with_collision,
        "drücke_objekte": push_objects,
        "fixiere_y_position": lock_y_position,
        "entferne_y_fixierung": unlock_y_position,
        "drucke_debug": print_debug,
        "erstelle_objekt": spawn_object,
        
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
        
        # GameObject-Methoden (werden dynamisch hinzugefügt)
        # obj.kollidiert_mit() → obj.collides_with()
        # obj.zerstöre() → obj.destroy()
    }

# In load_student_code() (Zeile 58):
game_namespace = _create_game_namespace()

# In Objekt-Code-Ausführung (Zeile 181):
obj_namespace = _create_game_namespace()  # Gleicher Namespace!
```

**WICHTIG:** Beide Namespaces müssen identisch sein, damit Code in `game.py` und Objekt-Code die gleichen Funktionen haben!

### GameObject-Methoden (dynamisch)

```python
# In gameobject.py, GameObject.__init__():

# Deutsche Methoden als Wrapper
def kollidiert_mit(self, andere_id: str) -> bool:
    return self.collides_with(andere_id)

def zerstöre(self):
    return self.destroy()

# Methoden hinzufügen
GameObject.kollidiert_mit = kollidiert_mit
GameObject.zerstöre = zerstöre
```

---

## 📊 Zusammenfassung: Funktionen-Status

### ✅ Bereits vorhanden (nur Alias nötig)
- Objekt-Funktionen: `hole_objekt`, `hole_alle_objekte`
- Input: `taste_gedrückt`, `taste_runter`, `maus_position`
- Bewegung: `bewege_mit_kollision`, `drücke_objekte`
- Debug: `drucke_debug`
- GameObject-Methoden: `kollidiert_mit`, `zerstöre`

### 🆕 Noch zu implementieren (für vollständiges Spiel)
- Zeit: `warte`, `hole_zeit`, `hole_delta_zeit`
- Zufall: `zufallszahl`, `zufällige_wahl`
- Mathematik: `abstand`, `winkel`, `normalisiere_wert`
- Listen: `finde_objekte_mit_typ`, `finde_objekte_in_bereich`
- Szenen: `lade_szene`, `aktuelle_szene`, `spiel_neustarten`
- Objekt-Management: `erstelle_objekt_bei_position`, `finde_objekt_mit_name`
- Text/UI: `zeige_text`, `zeige_zahl` (optional)
- Sound: `spiele_sound`, `stoppe_sound` (später)
- Animation: `spiele_animation` (später)
- Kollision (erweitert): `prüfe_kollision_mit_typ`, `hole_kollidierende_objekte`
- Physik: `setze_schwerkraft`, `setze_geschwindigkeit` (einfach)

---

## 🎓 Für Schüler (Klasse 7-10)

### Minimale Funktionen für einfaches Spiel:
1. ✅ Objekte holen/bewegen
2. ✅ Input (Tastatur, Maus)
3. ✅ Kollision
4. ✅ Debug-Ausgabe
5. 🆕 Zufall (für Spawn-Punkte, etc.)
6. 🆕 Zeit (für Timer, Cooldowns)
7. 🆕 Abstand (für AI, Verfolgung)

### Erweiterte Funktionen (für komplexere Spiele):
8. 🆕 Szenen wechseln
9. 🆕 Objekte erstellen/löschen
10. 🆕 Text anzeigen (Score, UI)
11. 🆕 Sound (später)
12. 🆕 Animation (später)

---

## ⚠️ Wichtige Überlegungen

### Kompatibilität
- **Beide Sprachen unterstützen:** Englisch UND Deutsch
- **Migration:** Bestehende Projekte funktionieren weiterhin
- **Schrittweise:** Schüler können gemischt programmieren (z.B. `wenn key_pressed()`)

### Fehlerbehandlung
- **Zeile-Nummern:** Müssen korrekt gemappt werden
- **Fehlermeldungen:** Sollen auf Deutsch sein
- **Syntax-Fehler:** Deutsche Übersetzungen

### Performance
- **Pre-Processing:** Minimaler Overhead (nur einmal beim Laden)
- **Namespace:** Keine Performance-Einbußen (nur Aliase)

### Syntax-Highlighting
- **Deutsche Schlüsselwörter:** Müssen erkannt werden
- **Farben:** Gleiche Farben wie Python-Keywords

---

## 🚀 Nächste Schritte

1. **Pre-Processor implementieren** (Phase 1)
2. **Deutsche API-Aliase hinzufügen** (Phase 2)
3. **Fehlermeldungen übersetzen** (Phase 3)
4. **Syntax-Highlighting erweitern** (Phase 4)
5. **Dokumentation & Beispiele** (Phase 5)
6. **Neue Funktionen implementieren** (nach Bedarf)

---

## 🔤 Umgang mit Umlauten (ö, ü, ä)

### Technische Unterstützung
Python 3 unterstützt Umlaute in:
- ✅ Variablennamen: `geschwindigkeit`, `höhe`, `größe`
- ✅ Funktionsnamen: `hole_objekt()`, `prüfe_kollision()`
- ✅ Schlüsselwörter: `für`, `während`, `überspringen`

**ABER:** Es gibt praktische Probleme:
- ⚠️ **Tastatur-Layouts:** Nicht alle Schüler haben deutsche Tastatur
- ⚠️ **Encoding-Probleme:** Bei falschem Encoding können Umlaute kaputt gehen
- ⚠️ **Kompatibilität:** Manche Systeme/Tools haben Probleme mit Umlauten

### Lösung: Beide Varianten unterstützen

**Strategie:** Umlaute werden im Pre-Processor normalisiert, aber beide Varianten funktionieren:

| Mit Umlaut | Ohne Umlaut | Python |
|------------|-------------|--------|
| `für` | `fuer` | `for` |
| `während` | `waehrend` | `while` |
| `überspringen` | `ueberspringen` | `pass` |
| `mache_weiter` | `mache_weiter` | `continue` (kein Umlaut) |
| `prüfe` | `pruefe` | (Funktion) |
| `höhe` | `hoehe` | (Variable) |

### Implementierung

```python
# game_editor/engine/german_code_translator.py

# Mapping mit beiden Varianten
GERMAN_TO_PYTHON = {
    # Mit Umlaut (bevorzugt)
    'für': 'for',
    'während': 'while',
    'überspringen': 'pass',
    'prüfe': 'check',  # Beispiel-Funktion
    'höhe': 'height',  # Beispiel-Variable
    
    # Ohne Umlaut (Alternative)
    'fuer': 'for',
    'waehrend': 'while',
    'ueberspringen': 'pass',
    'pruefe': 'check',
    'hoehe': 'height',
}

def normalize_umlauts(code: str) -> str:
    """
    Normalisiert Umlaute zu ASCII-Äquivalenten für interne Verarbeitung.
    WICHTIG: Nur für Schlüsselwörter, nicht für Variablennamen!
    """
    # Umlaut-Mapping für Schlüsselwörter
    umlaut_map = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
    }
    
    # Nur Schlüsselwörter normalisieren, nicht Variablennamen
    # z.B. "für" → "for", aber "höhe" bleibt "höhe" (wird als Variable behandelt)
    normalized = code
    for umlaut, replacement in umlaut_map.items():
        # Nur in Schlüsselwörtern ersetzen
        normalized = normalized.replace(f'f{umlaut}r', 'fuer')  # für → fuer
        normalized = normalized.replace(f'w{umlaut}hrend', 'waehrend')  # während → waehrend
        # etc.
    
    return normalized
```

### Empfehlung für Schüler

**Option 1: Mit Umlauten (bevorzugt, wenn Tastatur vorhanden)**
```python
für objekt in alle_objekte:
    wenn objekt.höhe > 100:
        überspringen
```

**Option 2: Ohne Umlaute (Alternative, wenn keine deutsche Tastatur)**
```python
fuer objekt in alle_objekte:
    wenn objekt.hoehe > 100:
        ueberspringen
```

**Option 3: Gemischt (flexibel)**
```python
fuer objekt in alle_objekte:  # "fuer" ohne Umlaut
    wenn objekt.höhe > 100:    # "höhe" mit Umlaut (aus Variablenname)
        ueberspringen          # "ueberspringen" ohne Umlaut
```

### Encoding-Sicherheit

**WICHTIG:** Alle Dateien müssen UTF-8 sein!

```python
# In runtime.py, beim Laden von Code:
with open(game_code_path, 'r', encoding='utf-8') as f:
    code = f.read()
```

**Editor-Einstellungen:**
- Code-Editor speichert automatisch als UTF-8
- Syntax-Highlighter unterstützt Umlaute
- Fehlermeldungen zeigen Umlaute korrekt an

### Pre-Processor-Strategie

**Schritt 1: Umlaute normalisieren (optional)**
- Schüler kann mit oder ohne Umlaute schreiben
- Pre-Processor erkennt beide Varianten

**Schritt 2: Zu Python übersetzen**
- `für` → `for`
- `fuer` → `for` (auch unterstützt)
- `während` → `while`
- `waehrend` → `while` (auch unterstützt)

**Schritt 3: Variablennamen beibehalten**
- `höhe` bleibt `höhe` (wird nicht übersetzt, ist Variable)
- `geschwindigkeit` bleibt `geschwindigkeit`
- Nur Schlüsselwörter werden übersetzt!

### Beispiel-Implementierung

```python
def translate_german_to_python(code: str) -> str:
    """
    Übersetzt deutschen Code in Python-Code.
    Unterstützt sowohl Umlaute als auch ASCII-Äquivalente.
    """
    lines = code.split('\n')
    translated_lines = []
    
    # Erweiterte Mapping-Tabelle (mit und ohne Umlaute)
    GERMAN_KEYWORDS = {
        # Mit Umlaut
        'für': 'for',
        'während': 'while',
        'überspringen': 'pass',
        # Ohne Umlaut (Alternative)
        'fuer': 'for',
        'waehrend': 'while',
        'ueberspringen': 'pass',
        # Weitere Schlüsselwörter...
    }
    
    for line in lines:
        # Kommentare beibehalten
        if line.strip().startswith('#'):
            translated_lines.append(line)
            continue
        
        # Schlüsselwörter ersetzen (nur ganze Wörter)
        translated_line = line
        for german, python in GERMAN_KEYWORDS.items():
            pattern = r'\b' + re.escape(german) + r'\b'
            translated_line = re.sub(pattern, python, translated_line)
        
        translated_lines.append(translated_line)
    
    return '\n'.join(translated_lines)
```

### Best Practices für Schüler

1. **Schlüsselwörter:** Beide Varianten funktionieren (`für` oder `fuer`)
2. **Variablennamen:** Können Umlaute haben (`höhe`, `größe`)
3. **Funktionsnamen:** Können Umlaute haben (`prüfe_kollision()`)
4. **Strings:** Können Umlaute haben (`"Höhe: " + str(höhe)`)
5. **Kommentare:** Können Umlaute haben (`# Prüfe Höhe`)

### Fehlerbehandlung

Wenn Encoding-Probleme auftreten:
- **Fehlermeldung:** "Encoding-Fehler: Bitte UTF-8 verwenden"
- **Auto-Korrektur:** Versuche automatisch zu korrigieren
- **Fallback:** ASCII-Äquivalente verwenden

---

## ⚠️ WICHTIG: Zwei Code-Quellen!

### Code wird an ZWEI Stellen ausgeführt:

1. **`game.py`** (globale Datei)
   - Pfad: `code/game.py`
   - Wird geladen in: `load_student_code()` (Zeile 39-111)
   - Namespace: `game_namespace` (Zeile 58-86)
   - Ausführung: `exec(code, game_namespace)` (Zeile 97)
   - Update-Funktion: `game_namespace["update"]()` (Zeile 269)

2. **Objekt-Code** (in JSON gespeichert)
   - Pfad: `scenes/level1.json` → `objects[].code`
   - Wird geladen in: `main()` (Zeile 166-213)
   - Namespace: `obj_namespace` (Zeile 181-206)
   - Ausführung: `exec(obj_data["code"], obj_namespace)` (Zeile 208)
   - Update-Funktion: `obj_namespace["update"]()` (Zeile 257)

### Beide müssen unterstützt werden:

- ✅ **Pre-Processor:** Muss beide Code-Quellen übersetzen
- ✅ **Namespace:** Beide müssen identische deutsche Aliase haben
- ✅ **Fehlerbehandlung:** Beide müssen deutsche Fehlermeldungen bekommen
- ✅ **Syntax-Highlighting:** Editor zeigt beide Code-Typen an
- ✅ **Templates:** Beide müssen deutsche Starter-Templates bekommen

### Code-Editor unterstützt beide:

- ✅ `_load_code()` - lädt `game.py` (Zeile 517-588)
- ✅ `_load_object_code()` - lädt Objekt-Code (Zeile 590-663)
- ✅ `_save_object_code()` - speichert Objekt-Code (Zeile 665-721)
- ✅ Beide verwenden den gleichen Editor, müssen also beide übersetzt werden

---

## 📝 Notizen

- **Tastatur-Namen:** Sollen auch auf Deutsch sein? (`"LINKS"` statt `"LEFT"`)
- **Variablennamen:** Schüler können deutsche Namen verwenden (keine Übersetzung nötig)
- **Kommentare:** Können auf Deutsch sein (keine Übersetzung nötig)
- **Strings:** Können auf Deutsch sein (keine Übersetzung nötig)
- **Umlaute:** Beide Varianten unterstützen (mit und ohne Umlaute)
- **Zwei Code-Quellen:** `game.py` UND Objekt-Code müssen beide unterstützt werden!
- **Standard-Python:** Sollen `print`, `len`, etc. auch deutsche Aliase bekommen? (z.B. `drucke` statt `print`?)

---

## ✅ Vollständigkeits-Checkliste

### Code-Ausführung
- [x] `game.py` wird geladen und ausgeführt (`load_student_code()`, Zeile 39-111)
- [x] Objekt-Code wird geladen und ausgeführt (`main()`, Zeile 166-213)
- [x] Beide verwenden `exec()` - müssen Pre-Processing bekommen
- [x] Beide haben separate Namespaces - müssen beide erweitert werden

### Namespace
- [x] `game_namespace` existiert (Zeile 58-86)
- [x] `obj_namespace` existiert (Zeile 181-206)
- [x] Beide haben identische Funktionen - müssen beide deutsche Aliase bekommen
- [x] Standard-Python-Funktionen sind in beiden (Zeile 77-85, 197-205)

### Fehlerbehandlung
- [x] `translate_error()` existiert (Zeile 30-36)
- [x] `ERROR_TRANSLATIONS` existiert (Zeile 22-27)
- [x] Fehler werden für `game.py` übersetzt (Zeile 99-109)
- [x] Fehler werden für Objekt-Code übersetzt (Zeile 210-213)
- [ ] Muss erweitert werden für deutsche Schlüsselwörter

### Code-Editor
- [x] `_load_code()` lädt `game.py` (Zeile 517-588)
- [x] `_load_object_code()` lädt Objekt-Code (Zeile 590-663)
- [x] `_save_object_code()` speichert Objekt-Code (Zeile 665-721)
- [x] Beide verwenden UTF-8 Encoding (Zeile 526, 606, 692)
- [x] Syntax-Highlighting wird für beide angewendet (Zeile 553, 663)

### Templates
- [x] `game_editor/templates/empty_project/code/game.py` existiert
- [x] Standard-Code in `code_editor.py` für `game.py` (Zeile 559-571)
- [x] Standard-Code in `code_editor.py` für Objekt-Code (Zeile 632-640)
- [ ] Alle müssen deutsche Versionen bekommen

### Syntax-Highlighting
- [x] `LSPSyntaxHighlighter` existiert (`syntax_highlighter.py`)
- [x] Erkennt Python-Keywords (Zeile 119-135)
- [ ] Muss erweitert werden für deutsche Schlüsselwörter

### GameObject-Methoden
- [x] `collides_with()` existiert (`gameobject.py`, Zeile 154-182)
- [x] `destroy()` existiert (`gameobject.py`, Zeile 184-187)
- [ ] Deutsche Methoden müssen hinzugefügt werden (`kollidiert_mit()`, `zerstöre()`)

### API-Funktionen
- [x] Alle Funktionen existieren in `api.py`
- [x] Werden in Namespace eingefügt
- [ ] Deutsche Aliase müssen hinzugefügt werden

### Pre-Processor
- [ ] `german_code_translator.py` muss erstellt werden
- [ ] Muss vor beiden `exec()` Aufrufen verwendet werden
- [ ] Muss Umlaute unterstützen (mit und ohne)

---

## 🔍 Gefundene Lücken (wurden ergänzt)

1. ✅ **Zwei Code-Quellen:** Plan erwähnte nur `game.py`, aber Objekt-Code wurde übersehen
2. ✅ **Zwei Namespaces:** Beide müssen identische deutsche Aliase bekommen
3. ✅ **Templates:** Alle drei Templates müssen deutsche Versionen bekommen
4. ✅ **Standard-Code:** Code-Editor generiert Standard-Code - muss auch deutsch sein
5. ✅ **Fehlerbehandlung:** Existiert bereits, muss aber erweitert werden
