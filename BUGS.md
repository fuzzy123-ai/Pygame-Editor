# Bekannte Bugs

## Bug #1: Duplizieren mehrerer Objekte platziert nur ein Objekt

**Status:** Behoben  
**Priorität:** Hoch  
**Datum:** 2024  
**Behoben:** 2024

### Beschreibung
Wenn mehrere Objekte ausgewählt und per Rechtsklick → "Duplizieren" dupliziert werden, werden zwar alle Objekte in der Vorschau angezeigt, aber beim Platzieren (Klick) wird nur ein Objekt tatsächlich in die Szene eingefügt.

### Lösung
Die Position-Prüfung wurde verbessert: Wenn eine Position belegt ist, wird automatisch in einem 5x5 Grid um die ursprüngliche Position herum nach einer freien Position gesucht. Dies stellt sicher, dass alle Objekte platziert werden, auch wenn einige Positionen belegt sind.

### Technische Details
- Datei: `game_editor/ui/scene_canvas.py`
- Methode: `_place_duplicate_preview()`
- Fix: Suche nach alternativen Positionen in einem 5x5 Grid, wenn die ursprüngliche Position belegt ist

---

## Bug #2: Asset Browser bleibt zu schmal trotz mehrfacher Änderungen

**Status:** Behoben  
**Priorität:** Mittel  
**Datum:** 2024  
**Behoben:** 2024

### Beschreibung
Der Asset Browser bleibt trotz mehrfacher Versuche, die Breite zu erhöhen (z.B. `setMaximumWidth(360)`), sehr schmal und bietet nicht genug Platz für die Anzeige von Assets.

### Lösung
Die Breiten-Einstellungen wurden angepasst:
- `setMinimumWidth(250)` (vorher 150)
- `setMaximumWidth(400)` (vorher 360)
- Splitter-Größen werden explizit auf 300px für Asset Browser gesetzt

### Technische Details
- Datei: `game_editor/ui/main_window.py`
- Methode: `_create_central_widget()`
- Fix: Erhöhte Mindest- und Maximalbreite, explizite Splitter-Größen-Setzung


## Bug #3: Aktualisieren-Button und automatisches Löschen im Asset Browser

**Status:** Behoben  
**Priorität:** Mittel  
**Datum:** 2024  
**Behoben:** 2024

### Beschreibung
Ein kleiner Aktualisieren-Pfeil im Asset Browser fehlt. Wenn eine Datei über Windows gelöscht wird, sollte das automatisch passieren, sonst über den grünen Pfeil.

### Lösung
- Aktualisieren-Button (↻) wurde hinzugefügt mit grüner Farbe
- File-Watcher wurde erweitert, um auch den `assets/images/` Ordner zu überwachen
- Bei Datei-Löschung wird der Asset Browser automatisch aktualisiert (nach 500ms Verzögerung)
- Manuelle Aktualisierung über den grünen Pfeil-Button möglich

### Technische Details
- Datei: `game_editor/ui/asset_browser.py`
- Methoden: `_refresh_assets()`, `_on_folder_changed()`
- Fix: File-Watcher überwacht jetzt `assets/images/` Ordner, automatische Aktualisierung bei Änderungen

## Bug #4: Kollisionsbehandlung: Wackeln bei Boden-Kollision

**Status:** Behoben  
**Priorität:** Hoch  
**Datum:** 2024  
**Behoben:** 2024

### Beschreibung
Die `move_with_collision()` Funktion führte zu einem Wackeln (hoch und runter springen), wenn ein Objekt auf dem Boden stand. Die Kollisionsbehandlung korrigierte die Position zu aggressiv, was zu einem Bounce-Effekt führte.

### Lösung
Die Position-Korrektur wurde verbessert:
- **Keine Position-Korrektur bei `dy == 0`**: Wenn sich das Objekt nicht vertikal bewegt, wird nur geprüft, ob es auf dem Boden steht, aber die Position wird nicht korrigiert. Dies verhindert das Wackeln.
- **Bessere Unterscheidung**: Bei `dy == 0` wird nur geprüft, ob die Unterseite des Objekts nahe an der Oberseite des Bodens ist (Toleranz: 1 Pixel für Rundungsfehler), ohne die Position zu ändern.
- **Erweiterte Kollisionsprüfung**: Kollisionen funktionieren jetzt zwischen ALLEN Objekten mit aktivierter Kollisionsbox, nicht nur mit Boden-Objekten. Dies ermöglicht Kollisionen zwischen normalen Objekten untereinander.
- **Einfache API beibehalten**: Die Funktion bleibt einfach zu verwenden - keine Änderungen an der API-Signatur oder den Parametern.

### Technische Details
- Datei: `game_editor/engine/api.py`
- Methode: `move_with_collision()`
- Fix: 
  - Position wird nur korrigiert, wenn sich das Objekt tatsächlich bewegt (`dy != 0`)
  - Bei `dy == 0` wird nur der `on_ground` Status geprüft, ohne Position zu ändern
  - Kollisionsprüfung erweitert auf alle Objekte mit `_collider_enabled`, nicht nur `is_ground`
  - Horizontale Kollisionen funktionieren jetzt auch mit allen Objekten mit aktivierter Kollisionsbox