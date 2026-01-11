# Bekannte Bugs

## Bug #1: Duplizieren mehrerer Objekte platziert nur ein Objekt

**Status:** Offen  
**Priorität:** Hoch  
**Datum:** 2024

### Beschreibung
Wenn mehrere Objekte ausgewählt und per Rechtsklick → "Duplizieren" dupliziert werden, werden zwar alle Objekte in der Vorschau angezeigt, aber beim Platzieren (Klick) wird nur ein Objekt tatsächlich in die Szene eingefügt.

### Schritte zur Reproduktion
1. Mehrere Objekte im Canvas auswählen (Shift+Klick)
2. Rechtsklick auf eines der ausgewählten Objekte
3. "Duplizieren" auswählen
4. Vorschau zeigt alle Objekte korrekt an
5. Auf Canvas klicken, um Objekte zu platzieren
6. **Erwartet:** Alle Objekte werden platziert
7. **Tatsächlich:** Nur ein Objekt wird platziert

### Technische Details
- Datei: `game_editor/ui/scene_canvas.py`
- Methode: `_place_duplicate_preview()`
- Problem: Position-Prüfung überspringt Objekte, die an bereits belegten Positionen platziert werden sollen
- Versuchte Fixes:
  - Original-Objekte von Position-Prüfung ausgeschlossen
  - Prüfung gegen bereits hinzugefügte Objekte hinzugefügt
  - `ObjectAddMultipleCommand` erstellt für Batch-Operationen

### Workaround
Einzelne Objekte nacheinander duplizieren.

### Zugehörige Commits
- Versuche zur Behebung wurden unternommen, aber Bug besteht weiterhin

---

## Bug #2: Asset Browser bleibt zu schmal trotz mehrfacher Änderungen

**Status:** Offen  
**Priorität:** Mittel  
**Datum:** 2024

### Beschreibung
Der Asset Browser bleibt trotz mehrfacher Versuche, die Breite zu erhöhen (z.B. `setMaximumWidth(360)`), sehr schmal und bietet nicht genug Platz für die Anzeige von Assets.

### Schritte zur Reproduktion
1. Editor starten
2. Asset Browser öffnen (links)
3. **Erwartet:** Breiterer Asset Browser mit mehr Platz
4. **Tatsächlich:** Asset Browser bleibt schmal

### Technische Details
- Datei: `game_editor/ui/main_window.py`
- Methode: `_create_central_widget()`
- Problem: `setMaximumWidth()` wird möglicherweise durch Layout-Constraints überschrieben
- Versuchte Fixes:
  - `setMaximumWidth(300)` → `setMaximumWidth(360)` erhöht
  - Verschiedene Layout-Anpassungen

### Workaround
Manuell die Splitter-Größe anpassen, um den Asset Browser zu verbreitern.

### Zugehörige Commits
- Mehrfache Versuche, die Breite zu erhöhen, aber Problem besteht weiterhin
