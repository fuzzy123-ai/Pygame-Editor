# Template-Vereinfachung: Brauche ich alle 3?

## Aktuelle Situation

### Template 1: Template-Datei
- **NÖTIG:** ✅ Ja
- **Grund:** Wird beim Erstellen neuer Projekte kopiert
- **Kann nicht entfernt werden:** Wird von `main_window.py` verwendet

### Template 2: Fallback game.py
- **NÖTIG?** ⚠️ Könnte vereinfacht werden
- **Aktuell:** Hardcoded in `code_editor.py` (Zeile 559-571)
- **Problem:** Duplikation - ähnlich wie Template 1, aber kürzer
- **Lösung:** Könnte Template 1 laden oder gemeinsame Funktion verwenden

### Template 3: Standard Objekt-Code
- **NÖTIG?** ⚠️ Teilweise nötig
- **Aktuell:** Hardcoded in `code_editor.py` (Zeile 632-640)
- **Problem:** Verwendet `obj` statt `player` und `object_id` (dynamisch)
- **Lösung:** Könnte Template-Funktion mit Parametern verwenden

---

## Empfehlung: Vereinfachung

### Option 1: Template-Funktion (Empfohlen)

**Eine zentrale Funktion, die alle Templates generiert:**

```python
# In code_editor.py oder neue Datei: code_templates.py

def get_default_code(code_type: str = "game", object_id: str = None) -> str:
    """
    Gibt Standard-Code zurück
    
    Args:
        code_type: "game" oder "object"
        object_id: ID des Objekts (nur für code_type="object")
    """
    if code_type == "game":
        return """# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT"):
        player.x += 4
    
    if key_pressed("LEFT"):
        player.x -= 4
"""
    elif code_type == "object":
        if not object_id:
            object_id = "object_1"
        return f"""# Code für {object_id}
# Hier schreibst du die Logik für dieses Objekt

obj = get_object("{object_id}")

def update():
    # Deine Logik hier
    pass
"""
    return ""
```

**Vorteile:**
- ✅ Keine Duplikation
- ✅ Einfach zu warten (nur eine Stelle)
- ✅ Einfach auf Deutsch umzustellen (nur eine Funktion)
- ✅ Template 1 kann diese Funktion auch verwenden

**Nachteile:**
- ⚠️ Template 1 ist eine Datei, nicht Code - muss trotzdem existieren

---

### Option 2: Template 1 für alles verwenden

**Template 2 könnte einfach Template 1 laden:**

```python
# In code_editor.py, _load_code():

else:
    # Template-Datei laden
    template_path = Path(__file__).parent.parent / "templates" / "empty_project" / "code" / "game.py"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            default_code = f.read()
    else:
        # Fallback wenn Template nicht existiert
        default_code = get_default_code("game")
```

**Vorteile:**
- ✅ Template 1 wird wiederverwendet
- ✅ Keine Duplikation zwischen Template 1 und 2

**Nachteile:**
- ⚠️ Template 1 ist länger (alle Richtungen) - vielleicht zu viel für Fallback?
- ⚠️ Template 3 ist anders (obj statt player) - kann nicht wiederverwendet werden

---

### Option 3: Alle behalten (Aktuell)

**Alle drei Templates behalten wie sie sind:**

**Vorteile:**
- ✅ Jedes Template ist für seinen Zweck optimiert
- ✅ Template 2 ist kürzer (nur LEFT/RIGHT) - weniger überwältigend
- ✅ Template 3 ist spezifisch für Objekte

**Nachteile:**
- ❌ Duplikation (Template 1 und 2 sind ähnlich)
- ❌ Mehr Wartung (3 Stellen müssen aktualisiert werden)
- ❌ Für deutsche API: 3 Stellen müssen übersetzt werden

---

## Empfehlung: Option 1 (Template-Funktion)

### Implementierung

**1. Neue Datei:** `game_editor/utils/code_templates.py`

```python
"""
Code-Templates für Standard-Code
"""
from pathlib import Path
from typing import Optional


def get_default_game_code() -> str:
    """Gibt Standard-Code für game.py zurück"""
    return """# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT"):
        player.x += 4
    
    if key_pressed("LEFT"):
        player.x -= 4
"""


def get_default_object_code(object_id: str) -> str:
    """Gibt Standard-Code für Objekt zurück"""
    return f"""# Code für {object_id}
# Hier schreibst du die Logik für dieses Objekt

obj = get_object("{object_id}")

def update():
    # Deine Logik hier
    pass
"""


def get_template_game_code() -> Optional[str]:
    """
    Lädt Template-Code aus templates/empty_project/code/game.py
    Falls nicht vorhanden, gibt None zurück
    """
    template_path = Path(__file__).parent.parent / "templates" / "empty_project" / "code" / "game.py"
    if template_path.exists():
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    return None
```

**2. In `code_editor.py` verwenden:**

```python
# Zeile 559-571 ersetzen:
from ..utils.code_templates import get_default_game_code

# ...
else:
    default_code = get_default_game_code()
    # ... rest bleibt gleich

# Zeile 632-640 ersetzen:
from ..utils.code_templates import get_default_object_code

# ...
if not code:
    code = get_default_object_code(object_id)
```

**3. Template 1 kann auch die Funktion verwenden:**

- Option A: Template-Datei bleibt wie sie ist (wird kopiert)
- Option B: Template-Datei wird beim Kopieren generiert (aus Funktion)

---

## Vergleich: Vorher vs. Nachher

### Vorher (3 Templates):
- ❌ 3 verschiedene Stellen mit Code
- ❌ Duplikation zwischen Template 1 und 2
- ❌ 3 Stellen müssen auf Deutsch umgestellt werden

### Nachher (Template-Funktion):
- ✅ 1 zentrale Funktion für Template 2 & 3
- ✅ Template 1 bleibt Datei (wird kopiert)
- ✅ Nur 2 Stellen müssen auf Deutsch umgestellt werden (Funktion + Template-Datei)
- ✅ Oder: Template 1 wird auch aus Funktion generiert → nur 1 Stelle!

---

## Finale Empfehlung

**Option 1 mit Erweiterung:**

1. **Template-Funktion** für Template 2 & 3
2. **Template 1** kann auch aus Funktion generiert werden (beim Kopieren)
3. **Ergebnis:** Nur 1 Stelle für alle Templates!

**Vorteile:**
- ✅ Keine Duplikation
- ✅ Einfach zu warten
- ✅ Für deutsche API: Nur 1 Funktion muss übersetzt werden
- ✅ Template 1 wird beim Kopieren aus Funktion generiert (konsistent)

**Nachteile:**
- ⚠️ Kleine Refactoring-Arbeit nötig

---

## Fazit

**Du brauchst NICHT alle 3 Templates separat!**

**Empfehlung:** 
- ✅ **Template-Funktion** für alle (1 zentrale Stelle)
- ✅ Template 1 wird beim Kopieren aus Funktion generiert
- ✅ Template 2 & 3 verwenden die Funktion direkt

**Ergebnis:** Nur 1 Stelle für alle Templates = viel einfacher zu warten!
