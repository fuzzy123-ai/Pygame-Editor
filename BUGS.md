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