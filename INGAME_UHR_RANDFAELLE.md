# Randfälle und Probleme: Ingame-Uhr System

## ⚠️ Kritische Probleme

### 1. Erster Frame: Delta-Zeit = 0 oder sehr groß

**Problem:**
- Beim ersten Frame ist `last_frame_time = game_start_time`
- Delta-Zeit könnte 0 sein (wenn sofort berechnet) oder sehr groß (wenn System-Uhr springt)
- Bewegung würde beim ersten Frame nicht funktionieren oder Objekte würden springen

**Lösung:**
```python
# Beim ersten Frame: Delta-Zeit auf Standard-Wert setzen
if last_frame_time == game_start_time:
    delta_time = 1.0 / target_fps  # Standard-Delta-Zeit (z.B. 1/60 = 0.0167s)
else:
    delta_time = current_time - last_frame_time
    delta_time = min(delta_time, 0.1)  # Begrenzung
```

**Oder:**
```python
# Erstes Frame überspringen
first_frame = True
while running:
    if first_frame:
        first_frame = False
        last_frame_time = pygame.time.get_ticks() / 1000.0
        continue  # Erstes Frame überspringen
```

---

### 2. System-Uhr springt (negatives Delta-Zeit)

**Problem:**
- System-Uhr wird zurückgestellt (z.B. durch NTP-Sync, Zeitzone-Änderung)
- `delta_time` wird negativ
- Bewegung würde rückwärts laufen

**Lösung:**
```python
delta_time = current_time - last_frame_time

# Negatives Delta-Zeit verhindern
if delta_time < 0:
    delta_time = 1.0 / target_fps  # Fallback auf Standard-Wert
    last_frame_time = current_time  # Reset
```

---

### 3. Sehr niedrige FPS (< 10 FPS)

**Problem:**
- Bei sehr niedriger FPS wird `delta_time` sehr groß (z.B. 0.5 Sekunden)
- Objekte würden in großen Sprüngen bewegt werden
- Kollisionserkennung könnte Objekte überspringen

**Lösung:**
```python
# Delta-Zeit begrenzen (bereits in Planung erwähnt)
delta_time = min(delta_time, 0.1)  # Maximal 100ms (10 FPS Minimum)
```

**Zusätzlich:**
- Warnung im Debug-Overlay wenn FPS < 30
- Optional: Frame-Skipping bei sehr niedriger FPS

---

### 4. Sehr hohe FPS (> 120 FPS)

**Problem:**
- Bei sehr hoher FPS wird `delta_time` sehr klein (z.B. 0.008 Sekunden)
- Rundungsfehler könnten sich summieren
- Performance könnte leiden

**Lösung:**
- `clock.tick(target_fps)` begrenzt bereits auf 60 FPS (Standard)
- `target_fps` kann aus `project.json` geladen werden
- Optional: VSync aktivieren für stabile FPS

---

### 5. Delta-Zeit = 0 (Frame-Skipping)

**Problem:**
- Wenn zwei Frames zur exakt gleichen Zeit berechnet werden
- `delta_time = 0` → Bewegung = 0
- Objekte würden einfrieren

**Lösung:**
```python
# Minimum-Delta-Zeit sicherstellen
if delta_time <= 0:
    delta_time = 0.0001  # Sehr kleiner Wert (verhindert Division durch 0)
```

---

## 🔄 Rückwärtskompatibilität

### 6. Bestehende Projekte mit Frame-basierter Bewegung

**Problem:**
- Alte Projekte verwenden `player.x += 4` (Frame-basiert)
- Nach Update würde Bewegung plötzlich viel schneller sein (4 Pixel/Sekunde statt 4 Pixel/Frame)
- Projekte würden "kaputt" gehen

**Lösung:**
- Standard: `use_delta_time=True` (zeit-basiert)
- Alte Code kann `use_delta_time=False` verwenden
- **ODER:** Migration-Tool das alte Code automatisch anpasst
- **ODER:** Config-Flag in `project.json`: `"use_frame_based_movement": true`

**Empfehlung:**
```python
# In project.json:
{
  "legacy_mode": {
    "frame_based_movement": false  # Standard: false (zeit-basiert)
  }
}
```

---

### 7. Code verwendet `get_delta_time()` aber Funktion existiert noch nicht

**Problem:**
- Schüler schreiben Code mit `get_delta_time()` in altem Projekt
- Projekt wird auf altem System ausgeführt → Fehler: `NameError: name 'get_delta_time' is not defined`

**Lösung:**
- Funktionen sind immer im Namespace (auch wenn Uhr-System nicht aktiv ist)
- Fallback-Wert: `get_delta_time()` gibt `1.0 / 60.0` zurück wenn nicht initialisiert
- **ODER:** Version-Check in `project.json`: `"requires_time_system": true`

---

## 🎮 Spiel-Logik Probleme

### 8. Timer akkumuliert Fehler bei niedriger FPS

**Problem:**
```python
timer += get_delta_time()
if timer >= 2.0:
    # Nach 2 Sekunden
    timer = 0.0
```

Bei niedriger FPS (z.B. 10 FPS):
- `delta_time = 0.1` (100ms)
- Nach 20 Frames: `timer = 2.0` (korrekt)
- Aber: Timer könnte bei 2.1 sein wenn Delta-Zeit-Begrenzung greift

**Lösung:**
- Timer sollte immer korrekt sein (Delta-Zeit-Begrenzung hilft)
- Optional: Timer mit `total_time` statt Akkumulation:
```python
start_time = get_total_time()
if get_total_time() - start_time >= 2.0:
    # Nach 2 Sekunden
    start_time = get_total_time()
```

---

### 9. Bewegung mit `use_delta_time=False` und `get_delta_time()` gemischt

**Problem:**
```python
# Inkonsistente Verwendung
dx = speed * get_delta_time()  # Zeit-basiert
move_with_collision(player, dx, 0, use_delta_time=False)  # Wird nicht nochmal multipliziert
```

**Lösung:**
- Klare Dokumentation: Wenn `use_delta_time=False`, dann KEINE Multiplikation mit `get_delta_time()`
- Warnung im Code-Editor (optional): "Vermischung von Zeit-basierter und Frame-basierter Bewegung"

---

### 10. Negative Geschwindigkeiten mit Delta-Zeit

**Problem:**
```python
speed = -100  # Rückwärts
dx = speed * get_delta_time()  # Wird negativ
```

**Lösung:**
- Funktioniert korrekt (negativ * positiv = negativ)
- Kein Problem, aber sollte dokumentiert sein

---

## 🔧 Technische Probleme

### 11. `_update_time()` wird nicht aufgerufen

**Problem:**
- Wenn `_update_time()` vergessen wird aufzurufen
- `get_delta_time()` gibt 0 zurück (Initialwert)
- Bewegung funktioniert nicht

**Lösung:**
- Assertion oder Warnung:
```python
def get_delta_time() -> float:
    if _delta_time == 0.0 and _total_time == 0.0:
        # Warnung: Zeit-System nicht initialisiert
        print("WARNUNG: Zeit-System nicht initialisiert!")
    return _delta_time
```

---

### 12. Zeit-Variablen werden während des Spiels zurückgesetzt

**Problem:**
- Wenn `_update_time(0, 0, 60)` während des Spiels aufgerufen wird
- `total_time` springt zurück auf 0
- Timer würden falsch funktionieren

**Lösung:**
- `_update_time()` sollte nur von Runtime aufgerufen werden
- Keine direkten Aufrufe von außen erlauben
- **ODER:** Validierung:
```python
def _update_time(delta: float, total: float, fps: int):
    global _delta_time, _total_time, _fps
    
    # Validierung: total_time sollte immer steigen
    if total < _total_time:
        print("WARNUNG: total_time wurde zurückgesetzt!")
        # Ignorieren oder korrigieren
        return
    
    _delta_time = delta
    _total_time = total
    _fps = fps
```

---

### 13. FPS-Berechnung ist ungenau bei ersten Frames

**Problem:**
- `clock.get_fps()` braucht mehrere Frames um stabil zu werden
- Erste Frames zeigen falsche FPS (z.B. 0 oder sehr hoch)

**Lösung:**
- FPS erst nach 10-20 Frames anzeigen
- **ODER:** Eigene FPS-Berechnung:
```python
fps_samples = []  # Letzte 10 Delta-Zeiten
fps_samples.append(1.0 / delta_time if delta_time > 0 else 60)
if len(fps_samples) > 10:
    fps_samples.pop(0)
fps = int(sum(fps_samples) / len(fps_samples))
```

---

## 🎯 Spiel-Neustart Probleme

### 14. Zeit wird nicht zurückgesetzt beim Neustart

**Problem:**
- Spiel wird neu gestartet (Code geändert)
- `total_time` startet nicht bei 0
- Timer würden falsch funktionieren

**Lösung:**
- `game_start_time` wird beim Neustart neu gesetzt
- `total_time` wird automatisch korrekt berechnet
- **ABER:** Wenn Spiel während des Laufens neu gestartet wird (Hot-Reload), muss Zeit zurückgesetzt werden

**Aktuell:** Spiel wird komplett neu gestartet → Zeit wird automatisch zurückgesetzt ✅

---

### 15. Objekte behalten Position beim Neustart

**Problem:**
- Objekte werden beim Neustart neu erstellt
- Positionen werden aus JSON geladen
- **KEIN Problem mit Uhr-System**, aber sollte beachtet werden

**Lösung:**
- Objekte werden immer neu erstellt → Positionen werden zurückgesetzt ✅

---

## 📊 Performance-Probleme

### 16. Delta-Zeit-Berechnung bei jedem Frame

**Problem:**
- `pygame.time.get_ticks()` wird bei jedem Frame aufgerufen
- Minimaler Overhead, aber könnte bei sehr hoher FPS summiert werden

**Lösung:**
- Overhead ist minimal (nur 1 Funktionsaufruf pro Frame)
- Kein Problem bei 60 FPS
- Optional: Caching wenn nötig (aber nicht nötig)

---

### 17. Viele Objekte mit Zeit-basierter Bewegung

**Problem:**
- 100+ Objekte mit `move_with_collision()` und Delta-Zeit
- Jedes Objekt multipliziert mit `_delta_time`
- Minimaler Overhead, aber könnte summiert werden

**Lösung:**
- Overhead ist minimal (nur 2 Multiplikationen pro Objekt)
- Bei 100 Objekten: 200 Multiplikationen pro Frame (vernachlässigbar)
- Kein Problem

---

## 🐛 Edge Cases

### 18. `get_delta_time()` wird außerhalb von `update()` aufgerufen

**Problem:**
```python
# Code außerhalb von update()
initial_delta = get_delta_time()  # Wird beim Laden aufgerufen
# Delta-Zeit ist 0 oder falsch
```

**Lösung:**
- Dokumentation: `get_delta_time()` sollte nur in `update()` verwendet werden
- Warnung wenn außerhalb aufgerufen (optional)
- **ODER:** Fallback-Wert zurückgeben

---

### 19. `get_total_time()` für Timer statt Akkumulation

**Problem:**
```python
# Falsch:
timer = 0.0
def update():
    timer += get_delta_time()  # Akkumuliert Fehler

# Richtig:
start_time = get_total_time()
def update():
    if get_total_time() - start_time >= 2.0:
        # Nach 2 Sekunden
```

**Lösung:**
- Dokumentation und Beispiele zeigen beide Methoden
- Empfehlung: `get_total_time()` für Timer

---

### 20. Division durch 0 bei `get_delta_time() == 0`

**Problem:**
```python
speed_per_second = 100
frames_per_second = speed_per_second / get_delta_time()  # Division durch 0!
```

**Lösung:**
- `get_delta_time()` gibt nie 0 zurück (Minimum: 0.0001)
- **ODER:** Validierung:
```python
dt = get_delta_time()
if dt > 0:
    frames_per_second = speed_per_second / dt
else:
    frames_per_second = 0
```

---

## 🔄 Multi-Szene Probleme

### 21. Zeit wird bei Szene-Wechsel zurückgesetzt?

**Problem:**
- Wenn Spiel zwischen Szenen wechselt
- Sollte `total_time` zurückgesetzt werden oder weiterlaufen?

**Lösung:**
- **Weiterlaufen:** Zeit läuft über Szenen hinweg (konsistent)
- **ODER:** Szene-spezifische Zeit (komplexer)
- Empfehlung: Weiterlaufen (einfacher, konsistenter)

---

### 22. Objekte aus vorheriger Szene behalten Timer

**Problem:**
- Objekte werden beim Szene-Wechsel neu erstellt
- Timer-Variablen werden zurückgesetzt
- **KEIN Problem**, aber sollte dokumentiert sein

**Lösung:**
- Objekte werden neu erstellt → Timer werden zurückgesetzt ✅

---

## 🎓 Schüler-spezifische Probleme

### 23. Schüler verwenden `get_delta_time()` falsch

**Problem:**
```python
# Falsch:
speed = 100
dx = speed / get_delta_time()  # Sollte multipliziert werden, nicht dividiert!

# Richtig:
dx = speed * get_delta_time()
```

**Lösung:**
- Klare Dokumentation mit Beispielen
- Fehlermeldung wenn Division verwendet wird (optional, aber kompliziert)
- Beispiele in Templates

---

### 24. Schüler verwenden Frame-basierte und Zeit-basierte Bewegung gemischt

**Problem:**
```python
# Inkonsistent:
if key_pressed("RIGHT"):
    player.x += 4  # Frame-basiert
if key_pressed("LEFT"):
    player.x -= 100 * get_delta_time()  # Zeit-basiert
```

**Lösung:**
- Dokumentation: Eine Methode konsistent verwenden
- Warnung im Code-Editor (optional, aber kompliziert)
- Beispiele zeigen nur eine Methode

---

### 25. Schüler verwenden `get_delta_time()` für Animationen

**Problem:**
```python
# Falsch für Animationen:
frame_index = int(get_total_time() * 10)  # 10 FPS
# Problem: Frame springt bei niedriger FPS

# Richtig:
animation_timer += get_delta_time()
if animation_timer >= 0.1:
    frame_index += 1
    animation_timer = 0.0
```

**Lösung:**
- Dokumentation mit Animation-Beispielen
- Klare Erklärung: Timer vs. direkte Berechnung

---

## 🔧 Debug-Overlay Probleme

### 26. Debug-Overlay zeigt falsche Werte

**Problem:**
- FPS wird NACH `clock.tick()` berechnet
- Delta-Zeit wird VOR `clock.tick()` berechnet
- Werte könnten nicht synchron sein

**Lösung:**
- FPS wird NACH Rendering berechnet (korrekt)
- Delta-Zeit wird VOR Updates berechnet (korrekt)
- Werte sind für den aktuellen Frame korrekt ✅

---

### 27. Debug-Overlay Text überlappt bei langen Werten

**Problem:**
- `total_time` könnte sehr groß werden (z.B. 999.99s)
- Text könnte überlappen

**Lösung:**
- Formatierung: `f"Zeit: {total_time:.1f}s"` (1 Dezimalstelle)
- **ODER:** Minuten/Sekunden Format: `f"Zeit: {int(total_time//60)}m {int(total_time%60)}s"`

---

## 📋 Zusammenfassung: Kritische Probleme

### Muss gelöst werden:
1. ✅ **Erster Frame:** Delta-Zeit auf Standard-Wert setzen
2. ✅ **Negatives Delta-Zeit:** Verhindern (System-Uhr springt)
3. ✅ **Delta-Zeit = 0:** Minimum-Wert sicherstellen
4. ✅ **Sehr niedrige FPS:** Delta-Zeit begrenzen (max 0.1s)
5. ✅ **Rückwärtskompatibilität:** `use_delta_time=False` für alte Code

### Sollte dokumentiert werden:
6. ⚠️ **Timer-Methoden:** Akkumulation vs. `get_total_time()`
7. ⚠️ **Schüler-Fehler:** Falsche Verwendung von `get_delta_time()`
8. ⚠️ **Gemischte Bewegung:** Frame-basiert + Zeit-basiert vermeiden

### Optional (Nice-to-Have):
9. 💡 **FPS-Warnung:** Warnung wenn FPS < 30
10. 💡 **Version-Check:** `project.json` Flag für Zeit-System
11. 💡 **Code-Editor-Warnung:** Warnung bei gemischter Bewegung (kompliziert)

---

## 🛡️ Empfohlene Validierungen

### In `_update_time()`:
```python
def _update_time(delta: float, total: float, fps: int):
    global _delta_time, _total_time, _fps
    
    # Validierungen
    if delta < 0:
        print("WARNUNG: Negatives Delta-Zeit erkannt!")
        delta = 1.0 / 60.0  # Fallback
    
    if delta > 0.1:
        print("WARNUNG: Sehr große Delta-Zeit (>100ms)!")
        delta = 0.1  # Begrenzung
    
    if total < _total_time:
        print("WARNUNG: total_time wurde zurückgesetzt!")
        # Ignorieren (behält alten Wert)
        return
    
    _delta_time = delta
    _total_time = total
    _fps = fps
```

### In `get_delta_time()`:
```python
def get_delta_time() -> float:
    if _delta_time == 0.0:
        # Fallback wenn nicht initialisiert
        return 1.0 / 60.0
    return _delta_time
```

---

## 📝 Testing-Checkliste

- [ ] Erster Frame: Delta-Zeit ist korrekt
- [ ] Negatives Delta-Zeit: Wird verhindert
- [ ] Delta-Zeit = 0: Wird verhindert
- [ ] Sehr niedrige FPS (< 10): Delta-Zeit wird begrenzt
- [ ] Sehr hohe FPS (> 120): Funktioniert korrekt
- [ ] Rückwärtskompatibilität: Alte Code funktioniert mit `use_delta_time=False`
- [ ] Timer: Beide Methoden funktionieren (Akkumulation + `get_total_time()`)
- [ ] Bewegung: Zeit-basiert funktioniert konsistent bei verschiedenen FPS
- [ ] Debug-Overlay: Zeigt korrekte Werte
- [ ] Spiel-Neustart: Zeit wird zurückgesetzt
- [ ] Szene-Wechsel: Zeit läuft weiter (oder wird zurückgesetzt, je nach Design)
- [ ] Performance: Keine Verzögerung bei vielen Objekten
