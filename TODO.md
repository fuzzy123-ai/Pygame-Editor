# TODO-Liste: Zukünftige Systeme

Sortiert nach Aufwand (einfach → komplex) mit Randfällen und Testing-Bedarf.

---

## 🔴 Einfach (1-2 Tage)

### 0. Template-Vereinfachung: Code-Templates zentralisieren
**Aufwand:** Niedrig  
**Priorität:** Mittel  
**Datum:** 2025

#### Beschreibung
Die 3 Code-Templates (Template-Datei, Fallback game.py, Standard Objekt-Code) sollen in eine zentrale Template-Funktion zusammengeführt werden, um Duplikation zu vermeiden und Wartung zu vereinfachen.

**Aktuelle Situation:**
- Template 1: `templates/empty_project/code/game.py` (wird beim Erstellen neuer Projekte kopiert)
- Template 2: Hardcoded in `code_editor.py` Zeile 559-571 (Fallback wenn game.py fehlt)
- Template 3: Hardcoded in `code_editor.py` Zeile 632-640 (Standard Objekt-Code)

**Problem:**
- ❌ Duplikation zwischen Template 1 und 2
- ❌ 3 Stellen müssen aktualisiert werden
- ❌ Für deutsche API: 3 Stellen müssen übersetzt werden

#### Technische Details
- **Dateien:** 
  - `game_editor/utils/code_templates.py` (neu) - Zentrale Template-Funktionen
  - `game_editor/ui/code_editor.py` - Verwendet Template-Funktionen
  - `game_editor/ui/main_window.py` - Kann Template-Funktion beim Kopieren verwenden
- **Änderungen:**
  - **Neue Datei:** `code_templates.py` mit Funktionen:
    - `get_default_game_code() -> str` - Standard-Code für game.py
    - `get_default_object_code(object_id: str) -> str` - Standard-Code für Objekte
    - `get_template_game_code() -> Optional[str]` - Lädt Template-Datei (optional)
  - **In code_editor.py:**
    - Zeile 559-571: `default_code = get_default_game_code()` verwenden
    - Zeile 632-640: `code = get_default_object_code(object_id)` verwenden
  - **Optional:** Template 1 wird beim Kopieren aus Funktion generiert (konsistent)

#### Randfälle
- ✅ Template-Datei existiert nicht → Fallback auf Funktion
- ✅ Objekt-ID ist None → Standard-ID verwenden
- ✅ Encoding-Probleme → UTF-8 sicherstellen
- ✅ Template 1 kann weiterhin als Datei existieren (wird kopiert)

#### Testing
- [ ] Template-Funktion gibt korrekten Code zurück
- [ ] Fallback game.py verwendet Template-Funktion
- [ ] Standard Objekt-Code verwendet Template-Funktion
- [ ] Template 1 wird korrekt kopiert (oder generiert)
- [ ] Alle 3 Templates sind konsistent
- [ ] UTF-8 Encoding funktioniert

#### Referenzen
- 📄 Siehe: `TEMPLATE_ERKLAERUNG.md` - Detaillierte Erklärung aller 3 Templates
- 📄 Siehe: `TEMPLATE_VEREINFACHUNG.md` - Vollständige Analyse und Implementierungs-Plan

---

### 1. Hotkey-System und Tooltips
**Aufwand:** Niedrig  
**Priorität:** Hoch  
**Datum:** 2024

#### Beschreibung
Vollständiges Hotkey-System für alle Editor-Funktionen mit Tooltips die auf Hotkeys verweisen.

**Neue Hotkeys:**
- **Strg+C**: Objekte kopieren (auch mehrere)
- **Strg+V**: Objekte einfügen mit Vorschau (auch mehrere)
- **Strg+S**: Spiel starten (⚠️ Konflikt: Aktuell für "Speichern" belegt - muss geändert werden)
- **Strg+X**: Objekte ausschneiden (auch mehrere)
- **Entf/Delete**: Objekte löschen (auch mehrere)
- **Strg+A**: Alle Objekte auswählen
- **Strg+D**: Objekte duplizieren (auch mehrere)
- **Esc**: Auswahl aufheben / Vorschau abbrechen
- **F5**: Spiel starten (Alternative zu Strg+S)
- **F6**: Spiel stoppen
- **Alt+Enter**: Fullscreen-Modus umschalten (im laufenden Spiel)

**Tooltips:**
- Alle Buttons und Menü-Items die einen Hotkey haben, sollen den Hotkey im Tooltip anzeigen
- Format: `"Funktion (Strg+C)"` oder `"Funktion (F5)"`
- Start-Button: `"Spiel starten (Strg+S)"` oder `"Spiel starten (F5)"`
- Stop-Button: `"Spiel stoppen (F6)"`
- Alle anderen Buttons entsprechend

#### Aktuelle Hotkeys (bereits implementiert)
- **Strg+N**: Neues Projekt
- **Strg+O**: Projekt öffnen
- **Strg+S**: Projekt speichern (⚠️ Konflikt mit gewünschtem "Spiel starten")
- **Strg+Q**: Beenden
- **Strg+Z**: Rückgängig
- **Strg+Y**: Wiederherstellen

#### Technische Details
- **Dateien:** `game_editor/ui/main_window.py`, `game_editor/ui/scene_canvas.py`, `game_editor/ui/code_editor.py`
- **Änderungen:**
  - **Kopieren/Einfügen:**
    - `QShortcut("Ctrl+C", self)` für Kopieren
    - `QShortcut("Ctrl+V", self)` für Einfügen
    - Clipboard-System: Objekte als JSON serialisieren
    - Vorschau beim Einfügen: Geister-Objekte anzeigen (wie bei Duplizieren)
    - Mehrere Objekte: Liste von Objekten im Clipboard
  - **Ausschneiden:**
    - `QShortcut("Ctrl+X", self)` für Ausschneiden
    - Kombiniert Kopieren + Löschen
  - **Löschen:**
    - `QShortcut("Delete", self)` für Löschen
    - `QShortcut("Backspace", self)` als Alternative
  - **Auswählen:**
    - `QShortcut("Ctrl+A", self)` für Alle auswählen
  - **Duplizieren:**
    - `QShortcut("Ctrl+D", self)` für Duplizieren
  - **Spiel starten/stoppen:**
    - `QShortcut("Ctrl+S", self)` für Starten (⚠️ **KONFLIKT:** Aktuell für "Speichern" belegt!)
    - `QShortcut("F5", self)` als Alternative für Starten (empfohlen)
    - `QShortcut("F6", self)` für Stoppen
    - **Lösung für Strg+S Konflikt (empfohlen: Option 1):**
      - **Option 1 (empfohlen):** Strg+S bleibt für Speichern, F5 für Starten
        - Vorteil: Standard-Konvention (F5 = Starten in vielen IDEs)
        - Keine Breaking Changes
      - **Option 2:** Strg+S für Starten, Strg+Shift+S für Speichern
        - Vorteil: Strg+S für Starten wie gewünscht
        - Nachteil: Ungewöhnlich, Breaking Change
      - **Option 3:** Kontextabhängig (wenn Spiel läuft → Stoppen, sonst Starten)
        - Vorteil: Ein Hotkey für beide Aktionen
        - Nachteil: Verwirrend, Speichern braucht neuen Hotkey
  - **Tooltips:**
    - `button.setToolTip("Funktion (Strg+C)")` für alle Buttons
    - Menü-Items zeigen Hotkeys automatisch (Qt-Feature)
    - Konsistente Formatierung: `"Funktion (Hotkey)"`
    - **Buttons die Tooltips brauchen:**
      - Start-Button: `"Spiel starten (F5)"` oder `"Spiel starten (Strg+S)"`
      - Stop-Button: `"Spiel stoppen (F6)"`
      - Undo-Button: ✅ Bereits vorhanden `"Rückgängig (Ctrl+Z)"`
      - Redo-Button: ✅ Bereits vorhanden `"Wiederherstellen (Ctrl+Y)"`
      - Alle anderen Buttons entsprechend

#### Randfälle
- ✅ Mehrere Objekte kopieren/einfügen → Alle Objekte werden korrekt kopiert
- ✅ Vorschau beim Einfügen → Geister-Objekte wie bei Duplizieren
- ✅ Clipboard zwischen Szenen → Objekte können in andere Szenen eingefügt werden
- ✅ Strg+S Konflikt → Muss gelöst werden (siehe oben)
- ✅ Hotkey-Konflikte → Warnung wenn Hotkey bereits belegt
- ✅ Tooltips aktualisieren → Wenn Hotkey geändert wird
- ✅ Esc-Taste → Vorschau abbrechen, Auswahl aufheben
- ✅ Kontextabhängige Hotkeys → Nur aktiv wenn relevant (z.B. Strg+V nur wenn Clipboard nicht leer)

#### Testing
- [ ] Strg+C kopiert Objekte (einzeln und mehrere)
- [ ] Strg+V fügt Objekte ein mit Vorschau
- [ ] Strg+X schneidet Objekte aus
- [ ] Entf/Delete löscht Objekte
- [ ] Strg+A wählt alle Objekte aus
- [ ] Strg+D dupliziert Objekte
- [ ] Esc hebt Auswahl auf / bricht Vorschau ab
- [ ] F5 startet Spiel
- [ ] F6 stoppt Spiel
- [ ] Strg+S Konflikt ist gelöst
- [ ] Alle Tooltips zeigen Hotkeys korrekt an
- [ ] Hotkeys funktionieren in allen Kontexten (Canvas, Code Editor, etc.)
- [ ] Mehrere Objekte werden korrekt kopiert/eingefügt
- [ ] Vorschau funktioniert beim Einfügen

---

### 2. Debug-Ansicht ergänzen: Auge-Button
**Aufwand:** Niedrig  
**Priorität:** Hoch  
**Datum:** 2024

#### Beschreibung
Wenn der Auge-Button (Debug-Toggle) gedrückt wird, sollen alle Debug-Elemente ausgeblendet werden:
- Alle Kollisionsbox-Rahmen (rote Boxen)
- Objekt-Markierungen und Beschriftungen (ID-Texte)
- Grid/Line-Grid
- Alle anderen Debug-Overlays

**Nur die Sprites sollen sichtbar bleiben**, solange Debug-Mode deaktiviert ist.

**WICHTIG:** Debug-Ansicht wird **NUR** aktiviert/deaktiviert wenn der Button explizit gedrückt wird. Keine automatische Aktivierung/Deaktivierung (z.B. beim Layer-Wechsel).

#### Technische Details
- **Dateien:** `game_editor/engine/runtime.py`, `game_editor/ui/scene_canvas.py`
- **Änderungen:**
  - `debug_mode` Flag in Runtime prüfen
  - `obj.draw()` Parameter `debug=False` wenn Debug-Mode aus
  - Grid-Zeichnung nur bei `debug_mode=True`
  - Debug-Overlays (ID-Texte, Kollisionsboxen) nur bei `debug_mode=True`
  - **Button-Handler:** Nur bei explizitem Button-Klick wird `debug_mode` umgeschaltet
  - **Keine automatische Aktivierung:** Debug-Mode bleibt unverändert bei anderen Aktionen (Layer-Wechsel, etc.)

#### Randfälle
- ✅ Debug-Mode während laufendem Spiel umschalten
- ✅ Debug-Mode beim Start des Spiels (sollte aus sein)
- ✅ F1-Toggle funktioniert weiterhin
- ✅ Performance: Keine Debug-Zeichnungen wenn aus
- ✅ Debug-Mode bleibt unverändert bei Layer-Wechsel
- ✅ Debug-Mode bleibt unverändert bei anderen Aktionen

#### Testing
- [ ] Auge-Button funktioniert (nur per Button-Klick)
- [ ] F1-Toggle funktioniert weiterhin
- [ ] Alle Debug-Elemente verschwinden/erscheinen korrekt
- [ ] Performance-Test: Keine Verzögerung wenn Debug aus
- [ ] Debug-Mode bleibt unverändert bei Layer-Wechsel
- [ ] Debug-Mode bleibt unverändert bei anderen Aktionen

---

### 2.5. Fullscreen-Modus für Spiel
**Aufwand:** Mittel  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Fullscreen-Modus für das Spiel mit Alt+Enter zum Umschalten zwischen Fullscreen und Fenster-Modus.

**Anforderungen:**
- **Alt+Enter**: Umschalten zwischen Fullscreen und Fenster-Modus
- **Desktop-Auflösung**: Im Fullscreen wird die native Desktop-Auflösung verwendet
- **Korrektes Scaling**: Spielwelt und Funktionen bleiben erhalten, keine Verzerrung
- **Zurück zum Fenster**: Alt+Enter schaltet zurück zum Fenster-Modus mit ursprünglicher Größe

#### Technische Details
- **Dateien:** `game_editor/engine/runtime.py`, `game_editor/engine/api.py`
- **Änderungen:**
  - **Fullscreen-Flag:** `fullscreen_mode: bool = False` in Runtime
  - **Alt+Enter Erkennung:**
    - In Game-Loop: `pygame.key.get_pressed()` prüfen auf `K_LALT` oder `K_RALT` + `K_RETURN`
    - Oder: `pygame.event.get()` für `KEYDOWN` Events mit `event.key == K_RETURN` und `event.mod & KMOD_ALT`
  - **Display-Modus wechseln:**
    - `pygame.display.set_mode((width, height), pygame.FULLSCREEN)` für Fullscreen
    - `pygame.display.set_mode((width, height))` für Fenster-Modus
    - Desktop-Auflösung: `pygame.display.Info()` → `current_w, current_h`
  - **Scaling-System:**
    - **Option 1 (empfohlen):** Viewport-Scaling
      - Spielwelt bleibt in Original-Größe (z.B. 800x600)
      - Viewport wird auf Desktop-Auflösung skaliert
      - `pygame.transform.scale()` für alle Zeichnungen
      - Oder: Separate Surface für Spielwelt, dann auf Screen skalieren
    - **Option 2:** Letterboxing (schwarze Balken)
      - Spielwelt bleibt in Original-Größe
      - Schwarze Balken oben/unten oder links/rechts
      - Zentrierte Anzeige
    - **Option 3:** Stretch (nicht empfohlen - verzerrt)
  - **Camera-Offset anpassen:**
    - Camera-System muss mit neuer Auflösung arbeiten
    - Offset-Berechnung anpassen für Fullscreen
  - **Input-Skalierung:**
    - Maus-Position muss auf Spielwelt-Koordinaten umgerechnet werden
    - `mouse_position()` API muss korrekt skalieren

#### Randfälle
- ✅ Alt+Enter während laufendem Spiel → Sofortiger Wechsel
- ✅ Desktop-Auflösung ändert sich → Fullscreen passt sich an
- ✅ Verschiedene Bildschirm-Auflösungen → Korrektes Scaling auf allen
- ✅ Spielwelt-Größe vs. Desktop-Auflösung → Keine Verzerrung
- ✅ Camera-System → Funktioniert in Fullscreen korrekt
- ✅ Maus-Input → Korrekte Koordinaten in Fullscreen
- ✅ Mehrere Monitore → Fullscreen auf aktivem Monitor
- ✅ Alt+Tab während Fullscreen → Fenster bleibt im Fullscreen
- ✅ Performance: Scaling sollte nicht zu Verzögerungen führen

#### Testing
- [ ] Alt+Enter schaltet zwischen Fullscreen und Fenster um
- [ ] Desktop-Auflösung wird korrekt verwendet
- [ ] Spielwelt wird nicht verzerrt (korrektes Aspect Ratio)
- [ ] Camera-System funktioniert in Fullscreen
- [ ] Maus-Input funktioniert korrekt (Koordinaten stimmen)
- [ ] Alle Objekte werden korrekt angezeigt
- [ ] Performance ist akzeptabel (keine Verzögerung durch Scaling)
- [ ] Zurück zum Fenster-Modus funktioniert
- [ ] Verschiedene Bildschirm-Auflösungen getestet
- [ ] Mehrere Monitore getestet

---

### 2.6. Editor-Einstellungen Persistenz
**Aufwand:** Niedrig  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Editor-Einstellungen sollen über Neustart hinweg gespeichert werden, damit die Arbeitsumgebung erhalten bleibt.

**Zu speichernde Einstellungen:**
- **Fenstergrößen:** Größe der Editor-Fenster (Main Window, Asset Browser, Code Editor, etc.)
- **Splitter-Positionen:** Position der Splitter zwischen Panels
- **Debug-Ansicht Status:** Ob Debug-Ansicht aktiviert ist (`show_labels`, `show_highlights`)
- **Zoom-Level:** Aktueller Zoom-Faktor im Scene Canvas
- **Layer-Auswahl:** Aktuell ausgewählter Layer
- **Grid-Einstellungen:** Grid-Sichtbarkeit (falls vorhanden)

**Speicherort:** `project.json` unter `"editor_settings"` Sektion

#### Technische Details
- **Dateien:** `game_editor/ui/main_window.py`, `game_editor/ui/scene_canvas.py`, `game_editor/ui/asset_browser.py`, `game_editor/ui/code_editor.py`, `game_editor/engine/loader.py`
- **Änderungen:**
  - **Neue Sektion in project.json:**
    ```json
    {
      "editor_settings": {
        "main_window": {
          "width": 1920,
          "height": 1080,
          "splitter_sizes": [300, 800, 300]
        },
        "scene_canvas": {
          "zoom_factor": 1.0,
          "current_layer": "default",
          "show_labels": true,
          "show_highlights": true
        },
        "asset_browser": {
          "width": 300
        }
      }
    }
    ```
  - **Beim Laden:**
    - `_load_editor_settings()` in `main_window.py`
    - Fenstergrößen wiederherstellen: `self.resize(width, height)`
    - Splitter-Positionen wiederherstellen: `splitter.setSizes(sizes)`
    - Debug-Ansicht Status wiederherstellen: `show_labels`, `show_highlights`
    - Zoom-Level wiederherstellen: `zoom_factor`
    - Layer-Auswahl wiederherstellen: `current_layer`
  - **Beim Speichern:**
    - `_save_editor_settings()` in `main_window.py`
    - Wird aufgerufen bei: Fenster-Resize, Splitter-Bewegung, Debug-Toggle, Zoom-Änderung, Layer-Wechsel
    - Auto-Save: Alle 5 Sekunden oder bei expliziten Änderungen
  - **Signal-System:**
    - `editor_settings_changed` Signal wenn Einstellungen geändert werden
    - Alle UI-Komponenten können ihre Einstellungen speichern

#### Randfälle
- ✅ Projekt wird geschlossen → Einstellungen werden gespeichert
- ✅ Projekt wird geöffnet → Einstellungen werden geladen
- ✅ Fenster außerhalb Bildschirm → Validierung und Korrektur
- ✅ Ungültige Einstellungen → Fallback auf Standard-Werte
- ✅ Erstes Öffnen → Standard-Einstellungen verwenden
- ✅ Mehrere Projekte → Jedes Projekt hat eigene Einstellungen

#### Testing
- [ ] Fenstergrößen werden gespeichert und geladen
- [ ] Splitter-Positionen werden gespeichert und geladen
- [ ] Debug-Ansicht Status wird gespeichert und geladen
- [ ] Zoom-Level wird gespeichert und geladen
- [ ] Layer-Auswahl wird gespeichert und geladen
- [ ] Einstellungen werden beim Projekt-Wechsel korrekt getrennt
- [ ] Ungültige Einstellungen werden korrekt behandelt
- [ ] Erstes Öffnen verwendet Standard-Werte

---

### 2.7. Ingame-Uhr System (Zeit-basierte Bewegung)
**Aufwand:** Mittel  
**Priorität:** Hoch  
**Datum:** 2025

#### Beschreibung
Zentrale Zeit-Verwaltung als Standard-Richtwert für alle Systeme:
- **Bewegung:** Zeit-basiert statt Frame-basiert (Pixel/Sekunde statt Pixel/Frame)
- **Pausen/Timer:** Zeit-basierte Wartezeiten
- **Animationen:** Zeit-basierte Frame-Rate (später)
- **Physik:** Zeit-basierte Geschwindigkeiten
- **Anzeige:** FPS, Delta-Zeit, absolute Zeit im Debug-Overlay

**Problem aktuell:**
- ❌ Bewegung ist Frame-basiert (hängt von FPS ab)
- ❌ Bei niedriger FPS läuft Spiel langsamer
- ❌ Bei hoher FPS läuft Spiel schneller
- ❌ Nicht konsistent auf verschiedenen Systemen

**Lösung:**
- ✅ Delta-Zeit berechnen (Zeit seit letztem Frame)
- ✅ Zeit-basierte Bewegung (Pixel/Sekunde statt Pixel/Frame)
- ✅ Zeit-API für Schüler-Code (`get_delta_time()`, `get_total_time()`, `get_fps()`)
- ✅ Debug-Overlay erweitern (FPS, Delta-Zeit, Gesamt-Zeit)

#### Technische Details
- **Dateien:** 
  - `game_editor/engine/runtime.py` - Zeit-Berechnung im Game Loop
  - `game_editor/engine/api.py` - Zeit-Funktionen für Schüler-Code
  - `game_editor/engine/collision.py` - Zeit-basierte Bewegung (optional)
- **Änderungen:**
  - **Runtime:** Zeit-Variablen (`delta_time`, `total_time`, `fps`) berechnen
  - **API:** Zeit-Funktionen (`get_delta_time()`, `get_total_time()`, `get_fps()`) hinzufügen
  - **Bewegung:** `move_with_collision()` erweitern mit Delta-Zeit-Support
  - **Debug-Overlay:** Delta-Zeit und Gesamt-Zeit anzeigen
  - **Namespace:** Zeit-Funktionen in `game_namespace` und `obj_namespace` einfügen

#### Randfälle
- ✅ Delta-Zeit-Begrenzung: Maximal 0.1 Sekunden (verhindert Sprünge bei niedriger FPS)
- ✅ Rückwärtskompatibilität: Alte Code funktioniert weiterhin (`use_delta_time=False`)
- ✅ Performance: Minimaler Overhead (nur 3 Berechnungen pro Frame)
- ✅ FPS-Variation: Bewegung bleibt konsistent bei verschiedenen FPS

#### Testing
- [ ] Delta-Zeit wird korrekt berechnet
- [ ] Zeit-basierte Bewegung funktioniert (konsistent bei verschiedenen FPS)
- [ ] Zeit-Funktionen sind im Schüler-Code verfügbar
- [ ] Debug-Overlay zeigt FPS, Delta-Zeit, Gesamt-Zeit
- [ ] Rückwärtskompatibilität: Alte Code funktioniert weiterhin
- [ ] Performance-Test: Keine Verzögerung durch Zeit-Berechnung
- [ ] Delta-Zeit-Begrenzung funktioniert (verhindert Sprünge)

#### Referenzen
- 📄 Siehe: `INGAME_UHR_PLAN.md` - Vollständige Planung mit allen Systemen, Integrationen und Beispielen

---

## 🟡 Mittel (2-3 Tage)

### 2. Asset Browser: Mehrspalten-Layout
**Aufwand:** Mittel  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Asset Browser soll mehrere Spalten nebeneinander anzeigen können:
- **1-4 Spalten** je nach Fensterbreite
- Sprites werden in einem Grid-Layout angezeigt
- **Dateinamen werden NICHT angezeigt** (nur Sprites)
- Responsive: Automatische Anpassung der Spaltenanzahl

#### Technische Details
- **Dateien:** `game_editor/ui/asset_browser.py`
- **Änderungen:**
  - QGridLayout oder Custom Layout für Spalten
  - Berechnung: `columns = max(1, min(4, floor(window_width / sprite_width)))`
  - Sprite-Größe anpassen (z.B. 64x64 oder 96x96)
  - Scrollbar für vertikales Scrollen

#### Randfälle
- ✅ Fenster-Resize: Spaltenanzahl aktualisiert sich automatisch
- ✅ Wenige Sprites: Layout funktioniert auch mit 1-3 Sprites
- ✅ Viele Sprites: Scrollbar erscheint korrekt
- ✅ Sprite-Größe: Konsistente Größe über alle Sprites
- ✅ Performance: Lazy Loading für viele Sprites

#### Testing
- [ ] 1-4 Spalten werden korrekt angezeigt
- [ ] Fenster-Resize aktualisiert Spaltenanzahl
- [ ] Scrollbar funktioniert bei vielen Sprites
- [ ] Sprite-Auswahl funktioniert in allen Spalten
- [ ] Performance-Test mit 100+ Sprites

---

### 4. Asset Browser: Ordner-System
**Aufwand:** Mittel  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Asset Browser soll Ordner unterstützen:
- Ordner erstellen/löschen
- Sprites in Ordner verschieben
- **Umbenennen:** Ordner und Sprites umbenennen
- **Kopieren:** Sprites kopieren (z.B. für Varianten)

#### Technische Details
- **Dateien:** `game_editor/ui/asset_browser.py`
- **Änderungen:**
  - Tree-Widget oder List-Widget mit Ordner-Icons
  - Context-Menü: Rechtsklick → "Umbenennen", "Kopieren", "Löschen"
  - Dateisystem-Operationen: `os.rename()`, `shutil.copy()`
  - Projektstruktur: `assets/images/` mit Unterordnern

#### Randfälle
- ✅ Ordner-Name bereits vorhanden → Fehlermeldung
- ✅ Sprite-Name bereits vorhanden → Fehlermeldung oder Auto-Increment
- ✅ Ungültige Zeichen in Namen (/, \, :, etc.) → Validierung
- ✅ Referenzen: Objekte die Sprite verwenden müssen aktualisiert werden
- ✅ Löschen: Warnung wenn Sprite noch verwendet wird

#### Testing
- [ ] Ordner erstellen/löschen funktioniert
- [ ] Sprites umbenennen funktioniert
- [ ] Sprites kopieren funktioniert
- [ ] Referenzen werden aktualisiert
- [ ] Fehlerbehandlung bei ungültigen Namen
- [ ] Warnung bei Löschen von verwendeten Sprites

---

## 🟠 Mittel-Hoch (3-5 Tage)

### 4. Editor: Multi-Platzierung mit Vorschau
**Aufwand:** Mittel-Hoch  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Beim Platzieren von Objekten soll durch **Drücken und Ziehen** mehrere Objekte platziert werden können:
- **Grüne Vorschau-Markierung** zeigt wo Objekte platziert werden würden
- Grid-basiert: Objekte werden an Grid-Punkten platziert
- Beim Loslassen werden alle Objekte erstellt

#### Technische Details
- **Dateien:** `game_editor/ui/scene_canvas.py`
- **Änderungen:**
  - Mouse-Drag-Event: `mousePressEvent`, `mouseMoveEvent`, `mouseReleaseEvent`
  - Vorschau-Zeichnung: Grüne Rechtecke/Boxen während Drag
  - Grid-Berechnung: `grid_x = floor(mouse_x / grid_size) * grid_size`
  - Objekt-Erstellung: Liste von Positionen beim Loslassen
  - Undo/Redo: Alle Objekte als eine Operation

#### Randfälle
- ✅ Drag außerhalb Canvas → Vorschau verschwindet
- ✅ Drag über existierende Objekte → Vorschau zeigt Kollision
- ✅ Grid-Snap: Objekte werden an Grid ausgerichtet
- ✅ Performance: Viele Vorschau-Objekte (100+) → Limit setzen
- ✅ Undo/Redo: Alle Objekte werden zusammen rückgängig gemacht

#### Testing
- [ ] Drag erstellt mehrere Objekte
- [ ] Grüne Vorschau erscheint korrekt
- [ ] Grid-Snap funktioniert
- [ ] Undo/Redo funktioniert für Multi-Platzierung
- [ ] Performance-Test mit vielen Objekten
- [ ] Drag außerhalb Canvas funktioniert korrekt

---

### 6. Layer-System erweitern
**Aufwand:** Mittel-Hoch  
**Priorität:** Hoch  
**Datum:** 2024

#### Beschreibung
Layer-System mit mehreren Ebenen erweitern (basiert auf aktuellem System).

**Aktuelles System (zu erweitern):**
- **Verfügbare Layer:** `["background", "default", "foreground"]` (siehe `game_editor/ui/scene_canvas.py`)
- **Aktueller Layer:** `current_layer = "default"` (wird in ComboBox ausgewählt)
- **Layer-Auswahl:** Dropdown-ComboBox in der Toolbar
- **Ghost-Ansicht:** Objekte aus anderen Layern werden bereits grau-transparent angezeigt

**Erweiterungen:**
- **Neue Layer hinzufügen:**
  - **Level Layer:** Für Level-Elemente (Plattformen, Blöcke)
  - **Level Backdrop:** Hintergrund-Elemente (hinter allem) - kann `"background"` ersetzen
  - **Level Front:** Vordergrund-Elemente (vor allem) - kann `"foreground"` ersetzen
- **Layer umbenennen/umbenennen:**
  - `"background"` → `"backdrop"` (konsistenter)
  - `"foreground"` → `"front"` (konsistenter)
  - `"default"` bleibt für Charaktere/Spieler

**Debug-Ansicht:**
- Nur Objekte im **ausgewählten Layer** werden vollständig angezeigt (bereits implementiert)
- Objekte in anderen Layern werden **leicht transparent** dargestellt (bereits implementiert als Ghost-Ansicht)
- **WICHTIG:** Debug-Ansicht wird **NICHT** automatisch aktiviert/deaktiviert beim Layer-Wechsel (siehe Aufgabe #1)

#### Technische Details
- **Dateien:** `game_editor/ui/scene_canvas.py`, `game_editor/engine/gameobject.py`, `game_editor/engine/runtime.py`
- **Aktuelle Implementierung:**
  - `self.available_layers = ["background", "default", "foreground"]` (Zeile 61)
  - `self.current_layer = "default"` (Zeile 60)
  - `self.layer_combo` für Layer-Auswahl (Zeile 97-100)
  - Ghost-Ansicht bereits implementiert (Zeile 2237-2247)
- **Änderungen:**
  - `available_layers` erweitern: `["backdrop", "default", "level", "front"]`
  - Zeichnungs-Reihenfolge: Backdrop → Level → Default → Front
  - Migration: Bestehende Objekte mit `"background"` → `"backdrop"`, `"foreground"` → `"front"`
  - Ghost-Ansicht bleibt unverändert (bereits implementiert)
  - **Keine automatische Debug-Ansicht-Aktivierung** beim Layer-Wechsel

#### Randfälle
- ✅ Objekte ohne Layer → Default Layer (bereits implementiert)
- ✅ Layer-Wechsel → Ghost-Ansicht aktualisiert sich (bereits implementiert)
- ✅ Objekte zwischen Layern verschieben → Ghost-Ansicht aktualisiert sich
- ✅ Performance: Viele Objekte in mehreren Layern
- ✅ Zeichnungs-Reihenfolge: Korrekte Überlappung
- ✅ Migration: Bestehende Projekte mit alten Layer-Namen
- ✅ Debug-Ansicht bleibt unverändert beim Layer-Wechsel

#### Testing
- [ ] Neue Layer werden korrekt hinzugefügt
- [ ] Layer-Migration funktioniert (background → backdrop, foreground → front)
- [ ] Ghost-Ansicht funktioniert weiterhin
- [ ] Zeichnungs-Reihenfolge ist korrekt
- [ ] Objekte können zwischen Layern verschoben werden
- [ ] Performance-Test mit vielen Objekten in mehreren Layern
- [ ] Debug-Ansicht bleibt unverändert beim Layer-Wechsel

---

## 🔴 Hoch (5-7 Tage)

### 7. Interaktive Blöcke (Super Mario Style)
**Aufwand:** Hoch  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Blöcke die von unten getroffen werden können:
- **Von unten gegen Block springen** → Block reagiert (z.B. nach oben bewegt sich)
- **Oben kommt etwas raus** (Münze, Power-Up, etc.)
- Block kann nach dem Treffen deaktiviert werden (leer) oder wieder aktiviert werden

#### Technische Details
- **Dateien:** `game_editor/engine/api.py`, `game_editor/engine/gameobject.py`, `game_editor/ui/scene_canvas.py`
- **Änderungen:**
  - Neues GameObject-Attribut: `is_interactive_block: bool`
  - Kollisionserkennung: Prüfen ob Objekt von unten gegen Block springt
  - Block-Reaktion: Animation nach oben (z.B. 10 Pixel), dann zurück
  - Spawn-System: Objekt oben aus Block spawnen (Münze, etc.)
  - Block-Status: `block_hit: bool` (verhindert mehrfaches Treffen)

#### Randfälle
- ✅ Block bereits getroffen → Keine Reaktion mehr
- ✅ Block wird von der Seite getroffen → Keine Reaktion
- ✅ Block wird von oben getroffen → Keine Reaktion
- ✅ Spawn-Objekt kollidiert mit Block → Korrekte Positionierung
- ✅ Mehrere Blöcke gleichzeitig → Alle reagieren korrekt
- ✅ Block-Animation: Smooth Movement nach oben und zurück

#### Testing
- [ ] Block reagiert nur von unten
- [ ] Block reagiert nicht von Seiten/Oben
- [ ] Block reagiert nur einmal
- [ ] Spawn-Objekt erscheint korrekt
- [ ] Block-Animation ist smooth
- [ ] Mehrere Blöcke funktionieren gleichzeitig
- [ ] Performance-Test mit vielen Blöcken

---

### 8. Sound-System über Editor
**Aufwand:** Hoch  
**Priorität:** Mittel  
**Datum:** 2024

#### Beschreibung
Sound-System vollständig über Editor integrieren:
- **Asset Browser:** Sound-Dateien (MP3, WAV, OGG) anzeigen und verwalten
- **Sound-Playback:** Sounds im Editor abspielen (Vorschau)
- **Objekt-Sounds:** Sounds Objekten zuweisen (z.B. Sprung-Sound, Kollisions-Sound)
- **Code-API:** `play_sound(sound_id)` Funktion für Schüler-Code

#### Technische Details
- **Dateien:** `game_editor/ui/asset_browser.py`, `game_editor/engine/api.py`, `game_editor/engine/runtime.py`
- **Änderungen:**
  - Asset Browser: Sound-Tab oder Filter für Sound-Dateien
  - Pygame Mixer: `pygame.mixer` für Sound-Playback
  - Sound-Assets: `assets/sounds/` Ordner
  - GameObject: `sounds: Dict[str, str]` (z.B. `{"jump": "jump.wav", "hit": "hit.wav"}`)
  - API: `play_sound(sound_id: str)` Funktion
  - Editor: Sound-Vorschau-Button

#### Randfälle
- ✅ Sound-Datei nicht gefunden → Fehlermeldung, Spiel läuft weiter
- ✅ Mehrere Sounds gleichzeitig → Mixer unterstützt mehrere Channels
- ✅ Sound-Volume: Einstellungen für Master-Volume
- ✅ Sound-Loop: Option für Looping-Sounds (Hintergrundmusik)
- ✅ Performance: Viele Sounds gleichzeitig → Channel-Limit

#### Testing
- [ ] Sound-Dateien werden im Asset Browser angezeigt
- [ ] Sound-Vorschau funktioniert
- [ ] Sounds können Objekten zugewiesen werden
- [ ] `play_sound()` funktioniert im Code
- [ ] Mehrere Sounds gleichzeitig funktionieren
- [ ] Sound-Volume-Einstellungen funktionieren
- [ ] Fehlerbehandlung bei fehlenden Sounds
- [ ] Performance-Test mit vielen Sounds

---

## 🔴 Sehr Hoch (7-10 Tage)

### 9. Animation-System
**Aufwand:** Sehr Hoch  
**Priorität:** Hoch  
**Datum:** 2024

#### Beschreibung
Vollständiges Animation-System:
- **Asset Browser:** Animationen erstellen/verwalten (Sprite-Sheets oder Einzelbilder)
- **Animation Player:** Animationen im Editor abspielen (Vorschau)
- **Einstellungen:** Frame-Rate, Loop, Start-Frame, etc.
- **Ingame-Systeme:** Animationen werden automatisch abgespielt
- **Code-API:** Nur für Animation bei Bewegung (z.B. `play_animation("walk")`), Rest Backend

#### Technische Details
- **Dateien:** `game_editor/ui/asset_browser.py`, `game_editor/engine/animation.py` (neu), `game_editor/engine/gameobject.py`, `game_editor/engine/runtime.py`
- **Änderungen:**
  - **Animation-Klasse:** `Animation` mit Frames, Frame-Rate, Loop-Flag
  - **Animation-Player:** Verwaltet aktuelle Animation, Frame-Index, Timer
  - **Asset Browser:**
    - Animation-Editor: Sprite-Sheet hochladen oder Einzelbilder auswählen
    - Frame-Auswahl: Manuell Frames auswählen oder automatisch aus Sprite-Sheet
    - Vorschau: Animation abspielen im Editor
  - **GameObject:**
    - `animations: Dict[str, Animation]` (z.B. `{"idle": Animation(...), "walk": Animation(...)}`)
    - `current_animation: str` (aktuelle Animation)
    - `animation_player: AnimationPlayer` (verwaltet Frame-Wechsel)
  - **Runtime:**
    - Automatische Frame-Updates basierend auf Frame-Rate
    - Sprite-Wechsel basierend auf aktueller Animation
  - **API:**
    - `play_animation(obj: GameObject, animation_name: str)` - Nur für manuelle Steuerung (z.B. bei Bewegung)
    - Backend: Automatische Animation-Updates

#### Randfälle
- ✅ Animation nicht gefunden → Fallback auf Standard-Sprite
- ✅ Frame-Rate = 0 → Animation pausiert
- ✅ Loop = False → Animation stoppt am Ende
- ✅ Animation-Wechsel: Smooth Transition oder sofort?
- ✅ Viele Animationen gleichzeitig → Performance-Optimierung
- ✅ Sprite-Sheet-Parsing: Automatische Frame-Erkennung (gleichmäßige Größe)
- ✅ Einzelbilder: Manuelle Frame-Auswahl

#### Testing
- [ ] Animationen können im Asset Browser erstellt werden
- [ ] Sprite-Sheet-Parsing funktioniert
- [ ] Einzelbilder können zu Animation zusammengefügt werden
- [ ] Animation-Vorschau funktioniert im Editor
- [ ] Animationen werden im Spiel abgespielt
- [ ] `play_animation()` funktioniert im Code
- [ ] Frame-Rate-Einstellungen funktionieren
- [ ] Loop-Flag funktioniert
- [ ] Performance-Test mit vielen animierten Objekten
- [ ] Animation-Wechsel ist smooth
- [ ] Fehlerbehandlung bei fehlenden Animationen

---

## 📊 Zusammenfassung

| Aufgabe | Aufwand | Priorität | Status |
|---------|---------|-----------|--------|
| 0. Template-Vereinfachung | 🔴 Einfach | Mittel | Pending |
| 1. Hotkey-System und Tooltips | 🔴 Einfach | Hoch | Pending |
| 2. Debug-Ansicht ergänzen | 🔴 Einfach | Hoch | Pending |
| 2.7. Ingame-Uhr System | 🟡 Mittel | Hoch | Pending |
| 3. Asset Browser: Mehrspalten | 🟡 Mittel | Mittel | Pending |
| 4. Asset Browser: Ordner | 🟡 Mittel | Mittel | Pending |
| 5. Editor: Multi-Platzierung | 🟠 Mittel-Hoch | Mittel | Pending |
| 6. Layer-System erweitern | 🟠 Mittel-Hoch | Hoch | Pending |
| 7. Interaktive Blöcke | 🔴 Hoch | Mittel | Pending |
| 8. Sound-System | 🔴 Hoch | Mittel | Pending |
| 9. Animation-System | 🔴 Sehr Hoch | Hoch | Pending |
| 10. Level-Editor mit pytmx | 🔴 Sehr Hoch | Niedrig | Pending |

**Empfohlene Reihenfolge:**
1. **Template-Vereinfachung** (schnell, vereinfacht Wartung, Vorbereitung für deutsche API)
2. **Hotkey-System** (schnell, hoher Impact, verbessert Workflow erheblich)
3. Debug-Ansicht (schnell, hoher Impact)
4. **Ingame-Uhr System** (wichtig als Basis für Bewegung, Animationen, Physik - hohe Priorität)
5. **Editor-Einstellungen Persistenz** (gute UX, relativ einfach, sollte früh kommen)
6. **Fullscreen-Modus** (gute UX, relativ einfach)
7. Asset Browser Verbesserungen (3+4 zusammen)
8. Layer-System (wichtig für Level-Design)
9. Multi-Platzierung (QOL-Feature)
10. Interaktive Blöcke (Gameplay-Feature)
11. Sound-System (Immersion)
12. Animation-System (komplex, aber wichtig - profitiert von Uhr-System)

---

## 🔵 Niedrige Priorität / Zukünftige Optionen

### 9. Level-Editor mit pytmx (Tiled Map Editor Integration)
**Aufwand:** Sehr Hoch (7-10+ Tage)  
**Priorität:** Niedrig  
**Datum:** 2024

#### Beschreibung
Optionaler Level-Editor mit pytmx für Tiled Map Editor TMX-Dateien:
- **Tiled Map Editor Integration:** Level können in Tiled erstellt und im Editor geladen werden
- **TMX-Format:** Unterstützung für Tile-Layers, Object-Layers, Properties
- **Dual-Mode:** Editor kann sowohl JSON (aktuell) als auch TMX (optional) verwenden
- **Konvertierung:** Möglichkeit JSON ↔ TMX zu konvertieren

#### Technische Details
- **Dependencies:** `pytmx` (Python 3.9+, pygame-CE kompatibel)
- **Dateien:** 
  - `game_editor/engine/tmx_loader.py` (neu) - TMX-Loader
  - `game_editor/ui/level_editor.py` (neu) - Level-Editor UI
  - `game_editor/engine/loader.py` - Erweitern für TMX-Support
- **Änderungen:**
  - **Format-Konvertierung:** JSON → TMX und TMX → JSON
  - **Loader-Erweiterung:** Automatische Format-Erkennung (.json vs .tmx)
  - **Tiled-Integration:** Export/Import von Tiled-Maps
  - **Tile-Layer-Support:** Tile-Layers werden zu GameObject-Arrays konvertiert
  - **Object-Layer-Support:** Tiled-Objects werden zu GameObjects konvertiert
  - **Properties-Mapping:** Tiled-Properties → GameObject-Attribute

#### Vorteile
- ✅ Professionelle Tilemap-Erstellung mit Tiled
- ✅ Große Level effizienter erstellen
- ✅ Tileset-Management in Tiled
- ✅ Automatische Kollisionsboxen aus Tiled

#### Nachteile / Herausforderungen
- ⚠️ **Format-Inkompatibilität:** Aktuelles System nutzt JSON, nicht TMX
- ⚠️ **Doppelte Workflows:** Schüler müssen Tiled lernen (zusätzlich zum Editor)
- ⚠️ **Großer Refactoring-Aufwand:** Loader, Scene Canvas, Inspector müssen erweitert werden
- ⚠️ **Editor-Integration:** Visueller Editor arbeitet mit JSON, nicht mit Tiled
- ⚠️ **Zielgruppe:** Für Klassen 7-10 möglicherweise zu komplex

#### Empfehlung
**Nur implementieren wenn:**
- Tiled Map Editor Teil des Lehrplans ist
- Große, komplexe Level benötigt werden
- Professionelle Tilemap-Features gewünscht sind
- Zeit für umfangreiches Refactoring vorhanden ist

**Alternative:** Eigenes Tilemap-System im Editor entwickeln (weniger Features, aber besser integriert)

#### Randfälle
- ✅ JSON ↔ TMX Konvertierung → Datenverlust vermeiden
- ✅ Tiled-Properties → GameObject-Attribute Mapping
- ✅ Tile-Layers → GameObject-Arrays
- ✅ Object-Layers → GameObjects
- ✅ Tileset-Management → Asset Browser Integration
- ✅ Kollisionsboxen aus Tiled → GameObject Colliders
- ✅ Bestehende JSON-Projekte → Migration zu TMX (optional)

#### Testing
- [ ] TMX-Dateien werden korrekt geladen
- [ ] JSON ↔ TMX Konvertierung funktioniert ohne Datenverlust
- [ ] Tile-Layers werden zu GameObjects konvertiert
- [ ] Object-Layers werden zu GameObjects konvertiert
- [ ] Properties werden korrekt gemappt
- [ ] Bestehende JSON-Projekte funktionieren weiterhin
- [ ] Editor kann beide Formate verarbeiten
- [ ] Tiled-Export/Import funktioniert

---

## 🔧 Technische Notizen

### Gemeinsame Abhängigkeiten
- **Asset Browser:** Wird für Animationen, Sounds und Sprites verwendet
- **Runtime:** Muss für alle ingame-Features erweitert werden
- **GameObject:** Wird für alle neuen Objekt-Features erweitert
- **API:** Wird für alle Code-APIs erweitert

### Performance-Bedenken
- Viele Objekte mit Animationen → Frame-Updates optimieren
- Viele Sounds gleichzeitig → Channel-Management
- Viele Layer → Zeichnungs-Optimierung
- Multi-Platzierung → Vorschau-Performance

### Testing-Strategie
- Jede Aufgabe sollte isoliert getestet werden
- Integration-Tests für kombinierte Features
- Performance-Tests mit vielen Objekten
- Edge-Cases für alle Features dokumentieren
