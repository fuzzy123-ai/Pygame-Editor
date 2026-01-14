# 🚀 Quick Start Guide

## Editor starten

### Windows (einfachste Methode)
1. Doppelklick auf `start_editor_direct.bat` (startet direkt)
2. Fertig! ✅

**Alternative:** `start_editor.bat` (prüft Requirements vor dem Start)

### Kommandozeile (alle Plattformen)
```bash
python -m game_editor.editor
```

## Erste Schritte

1. **Beim Start**: Dialog erscheint
   - **"Ja"** → Neues Projekt erstellen
   - **"Nein"** → Vorhandenes Projekt öffnen
   - **"Abbrechen"** → Später laden

2. **Neues Projekt erstellen**:
   - Wähle einen Ordner (z.B. `C:\MeineSpiele\MeinErstesSpiel`)
   - Template wird automatisch kopiert

3. **Bilder importieren**:
   - Asset Browser → "Bild importieren..."
   - Wähle PNG-Dateien (empfohlen: 32x32 oder 32x48 Pixel)

4. **Objekt platzieren**:
   - Sprite aus Asset Browser in Canvas ziehen
   - Oder: Sprite doppelklicken → Objekt wird erstellt

5. **Objekt verschieben**:
   - Im Canvas auf Objekt klicken und ziehen

6. **Eigenschaften ändern**:
   - Objekt im Canvas auswählen
   - Inspector rechts → X, Y, Breite, Höhe, Sprite ändern

7. **Code schreiben**:
   - Code Editor (unten) → `game.py` bearbeiten
   - Auto-Save alle 5 Sekunden

8. **Spiel testen**:
   - ▶ **Starten** Button klicken
   - Spiel läuft in separatem Fenster
   - ⏹ **Stop** Button zum Beenden

## Beispiel-Code

```python
# code/game.py

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten oder WASD
    if key_pressed("RIGHT") or key_pressed("D"):
        player.x += 4
    
    if key_pressed("LEFT") or key_pressed("A"):
        player.x -= 4
    
    if key_pressed("UP") or key_pressed("W"):
        player.y -= 4
    
    if key_pressed("DOWN") or key_pressed("S"):
        player.y += 4
    
    # Kollision prüfen
    if player.collides_with("enemy1"):
        print_debug("Kollision!")
    
    # Bewegung mit Kollisionsbehandlung
    # on_ground, collision_x, collision_y = move_with_collision(player, dx, dy)
    
    # Andere Objekte wegdrücken
    # pushed_count = push_objects(player, dx, dy)
```

## Tastatur-Shortcuts

- **F1** (im Spiel): Debug-Overlay ein/aus
- **Ctrl+S**: Projekt speichern
- **Ctrl+O**: Projekt öffnen
- **Ctrl+N**: Neues Projekt

## Hilfe

- Fehler erscheinen im Terminal/Console (unten)
- Debug-Ausgaben mit `print_debug()` erscheinen auch dort
- Projekt wird automatisch gespeichert beim Starten des Spiels
