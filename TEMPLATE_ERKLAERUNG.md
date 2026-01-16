# Erklärung: Die 3 Code-Templates

## Übersicht

Es gibt **3 verschiedene Stellen**, wo Code-Templates verwendet werden. Jede hat einen anderen Zweck:

---

## 1. Template-Datei (für neue Projekte)

**Datei:** `game_editor/templates/empty_project/code/game.py`

**Wann wird es verwendet?**
- Beim Erstellen eines **neuen Projekts** über "Datei → Neues Projekt"
- Wird vom Editor **kopiert** in das neue Projekt

**Wo wird es kopiert?**
- `main_window.py`, Zeile 467-481
- `shutil.copytree()` kopiert den gesamten `empty_project` Ordner

**Aktueller Inhalt:**
```python
# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT") or key_pressed("D"):
        player.x += 4
    
    if key_pressed("LEFT") or key_pressed("A"):
        player.x -= 4
    
    if key_pressed("UP") or key_pressed("W"):
        player.y -= 4
    
    if key_pressed("DOWN") or key_pressed("S"):
        player.y += 4
    
    # Kollisionserkennung
    if player.collides_with("enemy1"):
        print_debug("Achtung! Kollision mit Enemy!")
```

**Zweck:** Starter-Code für komplett neue Projekte

---

## 2. Fallback-Code im Code-Editor (wenn game.py fehlt)

**Datei:** `game_editor/ui/code_editor.py`, Zeile 559-571

**Wann wird es verwendet?**
- Wenn ein **bestehendes Projekt** geöffnet wird
- Aber die Datei `code/game.py` **nicht existiert**
- Wird im Code-Editor **angezeigt** (nicht gespeichert, bis Schüler speichert)

**Code-Stelle:**
```python
def _load_code(self):
    """Lädt game.py aus dem Projekt (globale Datei)"""
    code_file = self.project_path / "code" / "game.py"
    
    if code_file.exists():
        # Datei laden...
    else:
        # Standard-Code (Zeile 559-571)
        default_code = """# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT"):
        player.x += 4
    
    if key_pressed("LEFT"):
        player.x -= 4
"""
        self.editor.setText(default_code)
```

**Zweck:** Fallback wenn `game.py` gelöscht wurde oder fehlt

**Unterschied zu Template 1:**
- Kürzer (nur LEFT/RIGHT, nicht alle Richtungen)
- Wird nicht gespeichert, nur angezeigt
- Wird verwendet wenn Projekt bereits existiert

---

## 3. Standard-Code für Objekte (wenn Objekt keinen Code hat)

**Datei:** `game_editor/ui/code_editor.py`, Zeile 632-640

**Wann wird es verwendet?**
- Wenn ein **Objekt** im Canvas ausgewählt wird
- Aber das Objekt hat **keinen Code** in der JSON-Datei
- Wird im Code-Editor **angezeigt** (nicht gespeichert, bis Schüler speichert)

**Code-Stelle:**
```python
def _load_object_code(self, object_id: str, object_data: dict):
    """Lädt Code für ein spezifisches Objekt"""
    code = ""  # Wird aus JSON geladen...
    
    if not code:
        # Standard-Code für Objekt (Zeile 632-640)
        code = f"""# Code für {object_id}
# Hier schreibst du die Logik für dieses Objekt

obj = get_object("{object_id}")

def update():
    # Deine Logik hier
    pass
"""
        self.editor.setText(code)
```

**Zweck:** Starter-Code für Objekt-spezifischen Code

**Unterschied zu Template 1 & 2:**
- Verwendet `obj` statt `player`
- Verwendet `object_id` (dynamisch)
- Für Objekt-Code, nicht globale `game.py`

---

## Zusammenfassung

| Template | Datei | Wann verwendet? | Gespeichert? | Zweck |
|----------|-------|-----------------|--------------|-------|
| **1. Template-Datei** | `templates/empty_project/code/game.py` | Neues Projekt erstellen | ✅ Ja (wird kopiert) | Starter-Projekt |
| **2. Fallback game.py** | `code_editor.py` Zeile 559-571 | `game.py` fehlt in bestehendem Projekt | ❌ Nein (nur Anzeige) | Fallback |
| **3. Standard Objekt-Code** | `code_editor.py` Zeile 632-640 | Objekt hat keinen Code | ❌ Nein (nur Anzeige) | Objekt-Starter |

---

## Für deutsche Code-API

**Alle drei müssen deutsche Versionen bekommen:**

1. ✅ **Template-Datei:** Deutsche Version erstellen
   - `templates/empty_project/code/game.py` → deutsche Version
   - Oder: Template wird übersetzt beim Kopieren

2. ✅ **Fallback game.py:** Deutsche Version im Code
   - `code_editor.py` Zeile 559-571 → deutschen Code verwenden

3. ✅ **Standard Objekt-Code:** Deutsche Version im Code
   - `code_editor.py` Zeile 632-640 → deutschen Code verwenden

**WICHTIG:** Alle drei verwenden aktuell englischen Code und müssen auf Deutsch umgestellt werden!
