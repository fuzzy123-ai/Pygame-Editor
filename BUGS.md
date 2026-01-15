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

  #bug5
  implementiere abprallen, wenn eine ein anderes berühr that, soll sie die richtung wechseln

  #bug6
  wenn ein objekt dupliziert wird, dann wird der name auch dupliziert, obwohl eine andere obcect_id vergeben wurde.
  bsp obect_2 wird dupliziert zu object_2_1 obwohl es eigenntlich die id object_4 hat

## Bug #7: Syntax-Highlighting: Strings und Kommentare flackern

**Status:** Offen  
**Priorität:** Mittel  
**Datum:** 2024

### Beschreibung
Strings (Text in Anführungszeichen) und Kommentare flackern im Code-Editor. Sie wechseln regelmäßig (~500ms) zwischen ihrer gesetzten Farbe und weiß (Standard-Textfarbe).

### Symptome
- Strings und Kommentare flackern sichtbar zwischen gesetzter Farbe und weiß
- Das Flackern tritt regelmäßig auf (ca. alle 500ms)
- Andere Syntax-Elemente (Keywords, Operatoren, etc.) funktionieren korrekt

### Technische Details
- Datei: `game_editor/ui/syntax_highlighter.py`
- Methode: `apply_syntax_highlighting()`
- Datei: `game_editor/ui/code_editor.py`
- Methoden: `_on_text_changed_for_syntax()`, `_apply_syntax_highlighting()`

### Versuchte Lösungen (bisher erfolglos)
1. Debouncing mit QTimer (30ms Verzögerung) - verringert, aber beseitigt das Problem nicht
2. Cache-Mechanismus (`_last_formatted_text`) - verhindert Re-Highlighting bei unverändertem Text, aber Flackern bleibt
3. Dokument-Formatierungs-Check - prüft ob Dokument bereits formatiert ist, aber Flackern bleibt
4. Signal-Blockierung (`blockSignals`) - verhindert rekursive Aufrufe, aber Flackern bleibt
5. `_updating_syntax` Flag - verhindert parallele Highlighting-Aufrufe, aber Flackern bleibt

### Mögliche Ursachen
- Konflikt zwischen Syntax-Highlighting und LSP-Diagnostics
- QTextDocument wird möglicherweise mehrmals formatiert
- Race Condition zwischen Text-Änderungen und Highlighting
- `apply_diagnostics()` könnte Syntax-Highlighting überschreiben

### Nächste Schritte
- Debug-Logging implementieren, um den genauen Ablauf zu verstehen
- Prüfen, ob LSP-Updates das Highlighting überschreiben
- Prüfen, ob `apply_diagnostics()` die Formatierung zurücksetzt

---

## Bug #8: Block-Vorschau beim Sprite-Platzieren ist verschoben

**Status:** Offen  
**Priorität:** Mittel  
**Datum:** 2024

### Beschreibung
Bei der Block-Vorschau (z.B. beim Sprite-Platzieren) ist die Vorschau verschoben. Nach dem Klicken soll die Vorschau auf die Maus zentriert werden.

### Symptome
- Die Vorschau-Box erscheint nicht an der Maus-Position
- Die Vorschau ist versetzt zur tatsächlichen Maus-Position
- Nach dem Klick wird das Objekt nicht an der erwarteten Position platziert

### Technische Details
- Datei: `game_editor/ui/scene_canvas.py`
- Betroffene Funktionen: Sprite-Platzierung, Duplicate-Preview, Paste-Preview
- Problem: Vorschau-Offset-Berechnung ist nicht korrekt auf Maus-Position zentriert

### Lösung
Die Vorschau sollte nach dem Klicken auf die Maus zentriert werden. Die Offset-Berechnung muss angepasst werden, damit die Vorschau-Box genau an der Maus-Position erscheint.

---

## Bug #9: Strg+V (Paste) - Vorschau erscheint, aber Objekte werden beim Klicken nicht platziert

**Status:** Offen  
**Priorität:** Hoch  
**Datum:** 2024

### Beschreibung
Beim Drücken von Strg+V (Paste) erscheint die Vorschau der kopierten Objekte korrekt, aber beim Klicken auf den Canvas werden die Objekte nicht tatsächlich in die Szene platziert. Die Vorschau verschwindet, aber die Objekte werden nicht hinzugefügt.

### Symptome
- Strg+V zeigt die Vorschau der kopierten Objekte korrekt an
- Die Vorschau folgt der Maus-Bewegung
- Beim Klicken auf den Canvas passiert nichts - Objekte werden nicht platziert
- Die Vorschau verschwindet möglicherweise, aber Objekte erscheinen nicht in der Szene

### Vergleich mit Duplizieren-Funktion
Die Paste-Funktion sollte ähnlich wie die Duplizieren-Funktion funktionieren:
- Beide zeigen eine Vorschau der Objekte
- Beide sollten beim Klicken die Objekte tatsächlich platzieren
- Die Duplizieren-Funktion funktioniert korrekt, Paste-Funktion nicht

### Technische Details
- Datei: `game_editor/ui/scene_canvas.py`
- Methoden: 
  - `_start_paste_preview()` - Startet Paste-Vorschau (funktioniert)
  - `_place_paste_preview()` - Sollte Objekte platzieren (funktioniert möglicherweise nicht)
  - `mousePressEvent()` im Canvas - Ruft `_place_paste_preview()` auf
- Vergleich: `_place_duplicate_preview()` funktioniert korrekt

### Mögliche Ursachen
- `_place_paste_preview()` wird möglicherweise nicht korrekt aufgerufen
- Objekte werden erstellt, aber nicht zur `self.objects` Liste hinzugefügt
- Undo/Redo-Command wird möglicherweise nicht korrekt erstellt
- Fehler in der Position-Berechnung verhindert Platzierung
- Objekte werden erstellt, aber Canvas wird nicht aktualisiert

### Nächste Schritte
- Debug-Logging in `_place_paste_preview()` hinzufügen
- Prüfen ob Methode überhaupt aufgerufen wird
- Vergleich mit `_place_duplicate_preview()` - was ist anders?
- Prüfen ob Objekte zur Liste hinzugefügt werden
- Prüfen ob `save_scene()` aufgerufen wird
  