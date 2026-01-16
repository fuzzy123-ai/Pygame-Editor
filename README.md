# GameDev-Edu: Python 2D Game Editor für Schulen

Ein Python-basierter 2D-Game-Editor für Schüler der Klassen 7-10 mit visueller Szenen-Editierung und vereinfachter Python-API.

## 🎯 Features

- **Visueller Editor**: Drag & Drop für Objekte, Scene Canvas mit Zoom
- **Asset Browser**: Bilder importieren und verwalten
- **Code Editor**: Python-Editor mit Syntax-Highlighting (QScintilla)
- **Inspector**: Objekt-Eigenschaften bearbeiten (X, Y, Größe, Sprite)
- **Terminal/Console**: Debug-Ausgaben und Fehleranzeige
- **Vereinfachte API**: Kein Boilerplate - Schüler schreiben nur Logik
- **Run/Stop System**: Spiel läuft in separatem Prozess

## 📋 Anforderungen

- **Python**: 3.10 oder höher
- **Windows**: Zielplattform (portabel, USB-Stick kompatibel)
- **Dependencies**: Siehe `requirements.txt`

## 🚀 Installation & Start

### Schritt 1: Dependencies installieren
```bash
pip install -r requirements.txt
```

### Schritt 2: Editor starten

**Windows:**
- **Empfohlen:** Doppelklick auf `start_editor_direct.bat` (startet direkt ohne Dialog)
- **Mit Prüfung:** Doppelklick auf `start_editor.bat` (prüft Requirements)
- **Oder in der Kommandozeile:**
  ```bash
  python -m game_editor.editor
  ```

**Linux/Mac:**
```bash
python3 -m game_editor.editor
```

**Oder direkt:**
```bash
python -m game_editor.editor
```

### Schritt 3: Projekt erstellen/öffnen
Beim Start erscheint ein Dialog:
- **"Ja"** = Neues Projekt erstellen
- **"Nein"** = Vorhandenes Projekt öffnen
- **"Abbrechen"** = Editor öffnet ohne Projekt (kann später geladen werden)

## 📁 Projektstruktur

### Editor-Code (nicht für Schüler sichtbar)
```
game_editor/
├── editor.py              # Hauptprogramm
├── engine/                # Runtime Engine
│   ├── runtime.py        # Pygame Game Loop
│   ├── loader.py         # JSON Loader
│   ├── collision.py      # Kollisionssystem
│   ├── api.py            # Schüler-API
│   └── gameobject.py     # GameObject-Klasse
├── ui/                    # Editor UI
│   ├── main_window.py    # Hauptfenster
│   ├── scene_canvas.py   # 2D Canvas
│   ├── asset_browser.py  # Asset Browser
│   ├── code_editor.py    # Code Editor
│   ├── inspector.py      # Inspector Panel
│   └── console.py        # Terminal/Console
└── templates/             # Projekt-Templates
    └── empty_project/     # Leeres Starter-Projekt
```

### Schüler-Projekt
```
mein_spiel/
├── project.json          # Projekt-Konfiguration
├── scenes/
│   └── level1.json       # Szenen-Definition
├── assets/
│   └── images/           # Bilder (PNG)
│       ├── player.png
│       └── enemy.png
└── code/
    └── game.py           # Schüler-Code
```

## 🎮 Schüler-API

**WICHTIG:** Alle Code kann auf Deutsch geschrieben werden! Beide Varianten (Deutsch + Englisch) funktionieren.

### Objekte

**Deutsch:**
```python
spieler = hole_objekt("player")           # Objekt nach ID holen
alle_objekte = hole_alle_objekte()        # Alle Objekte
```

**Englisch (funktioniert weiterhin):**
```python
player = get_object("player")        # Objekt nach ID holen
all_objects = get_all_objects()      # Alle Objekte
```

### Input

**Deutsch:**
```python
wenn taste_gedrückt("RECHTS"):       # Taste gedrückt halten
    spieler.x += 4

wenn taste_runter("LEERTASTE"):      # Taste einmalig drücken
    springe()

maus_x, maus_y = maus_position()     # Mausposition
```

**Englisch:**
```python
if key_pressed("RIGHT"):             # Taste gedrückt halten
    player.x += 4

if key_down("SPACE"):                # Taste einmalig drücken
    jump()

mouse_x, mouse_y = mouse_position()  # Mausposition
```

### GameObject-Eigenschaften

**Deutsch:**
```python
spieler.x = 100                       # Position X
spieler.y = 200                       # Position Y
spieler.width = 32                    # Breite
spieler.height = 48                   # Höhe
spieler.visible = wahr                # Sichtbarkeit
spieler.sprite = "path"               # Sprite-Pfad

wenn spieler.kollidiert_mit("enemy1"):  # Kollision prüfen
    drucke_debug("Kollision!")

spieler.zerstöre()                    # Objekt entfernen
```

**Englisch:**
```python
player.x = 100           # Position X
player.y = 200           # Position Y
player.width = 32        # Breite
player.height = 48       # Höhe
player.visible = True    # Sichtbarkeit
player.sprite = "path"   # Sprite-Pfad

if player.collides_with("enemy1"):  # Kollision prüfen
    print_debug("Kollision!")

player.destroy()         # Objekt entfernen
```

### Bewegung & Kollision

**Deutsch:**
```python
# Bewegung mit automatischer Kollisionsbehandlung
auf_boden, kollision_x, kollision_y = bewege_mit_kollision(obj, dx, dy)
# auf_boden: wahr wenn Objekt auf Boden/Plattform steht
# kollision_x: wahr wenn Kollision in X-Richtung
# kollision_y: wahr wenn Kollision in Y-Richtung

# Andere Objekte wegdrücken
gedrückt = drücke_objekte(obj, dx, dy, drück_stärke=1.0)
# drückt andere Objekte in Bewegungsrichtung weg
```

**Englisch:**
```python
# Bewegung mit automatischer Kollisionsbehandlung
on_ground, collision_x, collision_y = move_with_collision(obj, dx, dy)
# on_ground: True wenn Objekt auf Boden/Plattform steht
# collision_x: True wenn Kollision in X-Richtung
# collision_y: True wenn Kollision in Y-Richtung

# Andere Objekte wegdrücken
pushed_count = push_objects(obj, dx, dy, push_strength=1.0)
# drückt andere Objekte in Bewegungsrichtung weg
```

### Code auf Deutsch schreiben

**Alle Schlüsselwörter können auf Deutsch sein:**
```python
# Deutsch → Python
funktion → def
wenn → if
sonst → else
für → for
während → while
gib_zurück → return
überspringen → pass
wahr → True
falsch → False
keine → None
und → and
oder → or
nicht → not
# ... und mehr!
```

**Beispiel:**
```python
spieler = hole_objekt("player")
geschwindigkeit = 3

funktion aktualisiere():
    global geschwindigkeit
    
    dx = 0
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit
    
    auf_boden, kollision_x, kollision_y = bewege_mit_kollision(spieler, dx, 0)
    
    wenn auf_boden:
        drucke_debug("Auf Boden!")
```
# push_strength: Stärke des Pushs (Standard: 1.0)
# gibt Anzahl der weggedrückten Objekte zurück
```

### Utility
```python
print_debug("Text")      # Debug-Ausgabe (erscheint in Console)
```

## 🎨 Verwendung

1. **Projekt erstellen/öffnen**: Datei → Neues Projekt / Projekt öffnen
2. **Assets importieren**: Asset Browser → "Bild importieren..."
3. **Objekte platzieren**: Sprite aus Asset Browser in Canvas ziehen
4. **Eigenschaften bearbeiten**: Objekt im Canvas auswählen → Inspector
5. **Code schreiben**: Code Editor → `game.py`
6. **Spiel starten**: ▶ Starten Button
7. **Spiel stoppen**: ⏹ Stop Button

## 🛡️ Fehlerbehandlung

- **Syntaxfehler**: Werden mit deutschen Übersetzungen angezeigt
- **Runtime-Fehler**: Erscheinen in Terminal/Console
- **Editor bleibt stabil**: Schüler-Code kann Editor nicht crashen

## 📚 Weitere Informationen

Siehe `project.md` für detaillierte Spezifikation.

## 📄 Lizenz

Dieses Projekt ist für den Bildungsbereich gedacht.

## 🎯 Erfolgs-Kriterien (MVP)

- ✅ Projekt öffnen/erstellen
- ✅ Objekte im Canvas verschieben
- ✅ Code in `game.py` schreiben
- ✅ Spiel starten/stoppen
- ✅ Syntax-Fehler verständlich anzeigen
- ✅ USB-Stick kompatibel (relative Pfade)
