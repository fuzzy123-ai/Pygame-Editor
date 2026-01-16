# Plan: Ingame-Uhr System

## 🎯 Ziel
Eine zentrale Zeit-Verwaltung, die als Standard-Richtwert für ALLES verwendet wird:
- **Bewegung:** Zeit-basiert statt Frame-basiert (Pixel/Sekunde statt Pixel/Frame)
- **Pausen/Timer:** Zeit-basierte Wartezeiten
- **Animationen:** Zeit-basierte Frame-Rate
- **Physik:** Zeit-basierte Geschwindigkeiten
- **Anzeige:** FPS, Delta-Zeit, absolute Zeit im Debug-Overlay

---

## 📊 Aktuelle Situation

### Was existiert bereits:
- ✅ `pygame.time.Clock()` - existiert (Zeile 142 in runtime.py)
- ✅ `clock.tick(60)` - Frame-Limit auf 60 FPS (Zeile 359)
- ✅ `clock.get_fps()` - FPS-Berechnung (Zeile 358)
- ✅ FPS-Anzeige im Debug-Overlay (Zeile 350-351)
- ❌ **KEINE Delta-Zeit** - wird nicht berechnet
- ❌ **KEINE absolute Zeit** - wird nicht getrackt
- ❌ **KEINE Zeit-API** - Schüler können keine Zeit abfragen

### Aktuelle Bewegung (Frame-basiert):
```python
# Aktuell: Frame-basiert (Pixel pro Frame)
platform_speed = 2  # 2 Pixel pro Frame
dx = platform_speed * platform_direction  # Bei 60 FPS = 120 Pixel/Sekunde
move_with_collision(platform, dx, dy)
```

**Problem:**
- ❌ Geschwindigkeit hängt von FPS ab
- ❌ Bei niedriger FPS läuft Spiel langsamer
- ❌ Bei hoher FPS läuft Spiel schneller
- ❌ Nicht konsistent auf verschiedenen Systemen

---

## 🔧 Technische Umsetzung

### 1. Zeit-Verwaltung in Runtime

**Datei:** `game_editor/engine/runtime.py`

**Neue Variablen:**
```python
# Zeit-Verwaltung
game_start_time = 0.0  # Zeitpunkt des Spielstarts (in Sekunden)
delta_time = 0.0       # Zeit seit letztem Frame (in Sekunden)
total_time = 0.0       # Gesamt-Spielzeit seit Start (in Sekunden)
target_fps = 60        # Ziel-FPS (aus config oder Standard)
```

**Berechnung im Game Loop:**
```python
# Vor dem Game Loop:
game_start_time = pygame.time.get_ticks() / 1000.0  # Startzeit in Sekunden
last_frame_time = game_start_time

# Im Game Loop (vor Updates):
current_time = pygame.time.get_ticks() / 1000.0
delta_time = current_time - last_frame_time
total_time = current_time - game_start_time
last_frame_time = current_time

# Nach Updates (vor Rendering):
fps = int(clock.get_fps())
clock.tick(target_fps)
```

**WICHTIG:** Delta-Zeit wird VOR allen Updates berechnet, damit alle Systeme sie verwenden können!

---

### 2. Zeit-API für Schüler-Code

**Datei:** `game_editor/engine/api.py`

**Neue globale Variablen:**
```python
# Zeit-Variablen (werden von runtime.py gesetzt)
_delta_time: float = 0.0      # Zeit seit letztem Frame (Sekunden)
_total_time: float = 0.0      # Gesamt-Spielzeit seit Start (Sekunden)
_fps: int = 60                # Aktuelle FPS
```

**Neue Funktionen:**
```python
def get_delta_time() -> float:
    """
    Gibt die Zeit seit dem letzten Frame zurück (in Sekunden)
    
    Returns:
        Delta-Zeit in Sekunden (z.B. 0.016 bei 60 FPS)
    """
    return _delta_time


def get_total_time() -> float:
    """
    Gibt die Gesamt-Spielzeit seit Start zurück (in Sekunden)
    
    Returns:
        Gesamt-Zeit in Sekunden
    """
    return _total_time


def get_fps() -> int:
    """
    Gibt die aktuelle FPS zurück
    
    Returns:
        FPS als Integer
    """
    return _fps


def wait(seconds: float):
    """
    Wartet X Sekunden (blockierend - NICHT für Schüler-Code!)
    
    WICHTIG: Diese Funktion sollte NICHT verwendet werden, da sie blockiert!
    Stattdessen: Zeit-basierte Timer verwenden (siehe Beispiele)
    """
    import time
    time.sleep(seconds)
```

**Update-Funktion:**
```python
def _update_time(delta: float, total: float, fps: int):
    """Aktualisiert Zeit-Variablen (wird von runtime.py aufgerufen)"""
    global _delta_time, _total_time, _fps
    _delta_time = delta
    _total_time = total
    _fps = fps
```

**Integration in Namespace:**
```python
# In load_student_code() und Objekt-Code-Namespace:
game_namespace = {
    # ... bestehende Funktionen ...
    
    # Zeit-Funktionen
    "get_delta_time": get_delta_time,
    "get_total_time": get_total_time,
    "get_fps": get_fps,
    "wait": wait,  # Optional, aber nicht empfohlen
}
```

---

### 3. Zeit-basierte Bewegung

**Problem:** Aktuell ist Bewegung Frame-basiert

**Lösung:** `move_with_collision()` erweitern ODER neue Funktion

**Option A: move_with_collision() erweitern (Empfohlen)**
```python
def move_with_collision(obj: GameObject, dx: float, dy: float, 
                       use_delta_time: bool = True) -> Tuple[bool, bool, bool]:
    """
    Bewegt ein Objekt mit automatischer Kollisionsbehandlung
    
    Args:
        obj: Das zu bewegende Objekt
        dx: Bewegung in X-Richtung (Pixel/Sekunde wenn use_delta_time=True)
        dy: Bewegung in Y-Richtung (Pixel/Sekunde wenn use_delta_time=True)
        use_delta_time: Wenn True, wird dx/dy mit Delta-Zeit multipliziert
    
    Returns:
        Tuple (on_ground, collision_x, collision_y)
    """
    if use_delta_time:
        # Zeit-basierte Bewegung: Pixel/Sekunde → Pixel/Frame
        dx = dx * _delta_time
        dy = dy * _delta_time
    
    # Rest bleibt gleich...
```

**Option B: Neue Funktion (einfacher für Migration)**
```python
def move_with_collision_timed(obj: GameObject, speed_x: float, speed_y: float) -> Tuple[bool, bool, bool]:
    """
    Bewegt ein Objekt zeit-basiert (Pixel/Sekunde)
    
    Args:
        obj: Das zu bewegende Objekt
        speed_x: Geschwindigkeit in X-Richtung (Pixel/Sekunde)
        speed_y: Geschwindigkeit in Y-Richtung (Pixel/Sekunde)
    """
    dx = speed_x * _delta_time
    dy = speed_y * _delta_time
    return move_with_collision(obj, dx, dy, use_delta_time=False)
```

**Empfehlung:** Option A mit `use_delta_time=True` als Standard (rückwärtskompatibel)

---

### 4. Zeit-Anzeige im Debug-Overlay

**Datei:** `game_editor/engine/runtime.py`, Zeile 347-355

**Aktuell:**
```python
if debug_mode:
    # FPS-Counter
    fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
    
    # Objekt-Zähler
    obj_text = fps_font.render(f"Objekte: {len(game_objects)}", True, (255, 255, 255))
    screen.blit(obj_text, (10, 35))
```

**Erweitert:**
```python
if debug_mode:
    y_offset = 10
    
    # FPS-Counter
    fps_text = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, y_offset))
    y_offset += 25
    
    # Delta-Zeit
    delta_text = fps_font.render(f"Delta: {delta_time*1000:.2f}ms", True, (255, 255, 255))
    screen.blit(delta_text, (10, y_offset))
    y_offset += 25
    
    # Gesamt-Zeit
    total_text = fps_font.render(f"Zeit: {total_time:.2f}s", True, (255, 255, 255))
    screen.blit(total_text, (10, y_offset))
    y_offset += 25
    
    # Objekt-Zähler
    obj_text = fps_font.render(f"Objekte: {len(game_objects)}", True, (255, 255, 255))
    screen.blit(obj_text, (10, y_offset))
```

---

### 5. Integration in alle Systeme

#### 5.1. Runtime-System

**Datei:** `game_editor/engine/runtime.py`

**Änderungen:**
1. **Zeit-Variablen initialisieren** (vor Game Loop, Zeile 142-143):
   ```python
   clock = pygame.time.Clock()
   game_start_time = pygame.time.get_ticks() / 1000.0
   last_frame_time = game_start_time
   delta_time = 0.0
   total_time = 0.0
   target_fps = config.get("target_fps", 60)  # Aus project.json oder Standard
   ```

2. **Zeit berechnen** (im Game Loop, VOR Updates, Zeile 230):
   ```python
   # Zeit berechnen (VOR allen Updates!)
   current_time = pygame.time.get_ticks() / 1000.0
   delta_time = current_time - last_frame_time
   total_time = current_time - game_start_time
   last_frame_time = current_time
   
   # Zeit-API aktualisieren
   _update_time(delta_time, total_time, int(clock.get_fps()))
   ```

3. **FPS berechnen** (NACH Rendering, Zeile 357-359):
   ```python
   pygame.display.flip()
   fps = int(clock.get_fps())
   clock.tick(target_fps)
   ```

#### 5.2. API-System

**Datei:** `game_editor/engine/api.py`

**Änderungen:**
1. **Zeit-Variablen hinzufügen** (Zeile 9-15):
   ```python
   _delta_time: float = 0.0
   _total_time: float = 0.0
   _fps: int = 60
   ```

2. **Update-Funktion hinzufügen** (nach _update_key_states):
   ```python
   def _update_time(delta: float, total: float, fps: int):
       """Aktualisiert Zeit-Variablen (wird von runtime.py aufgerufen)"""
       global _delta_time, _total_time, _fps
       _delta_time = delta
       _total_time = total
       _fps = fps
   ```

3. **Zeit-Funktionen hinzufügen** (nach mouse_position):
   ```python
   def get_delta_time() -> float:
       """Gibt Delta-Zeit zurück (Sekunden seit letztem Frame)"""
       return _delta_time
   
   def get_total_time() -> float:
       """Gibt Gesamt-Spielzeit zurück (Sekunden seit Start)"""
       return _total_time
   
   def get_fps() -> int:
       """Gibt aktuelle FPS zurück"""
       return _fps
   ```

4. **In Namespace einfügen** (Zeile 58-86 und 181-206):
   ```python
   game_namespace = {
       # ... bestehende Funktionen ...
       "get_delta_time": get_delta_time,
       "get_total_time": get_total_time,
       "get_fps": get_fps,
   }
   ```

5. **Import in runtime.py** (Zeile 12-16):
   ```python
   from .api import (..., _update_time, get_delta_time, get_total_time, get_fps)
   ```

#### 5.3. Bewegung-System

**Datei:** `game_editor/engine/api.py`, `move_with_collision()`

**Änderungen:**
1. **Delta-Zeit-Support hinzufügen** (Zeile 207):
   ```python
   def move_with_collision(obj: GameObject, dx: float, dy: float, 
                          use_delta_time: bool = True) -> Tuple[bool, bool, bool]:
       """
       Bewegt ein Objekt mit automatischer Kollisionsbehandlung
       
       Args:
           obj: Das zu bewegende Objekt
           dx: Bewegung in X-Richtung (Pixel/Sekunde wenn use_delta_time=True)
           dy: Bewegung in Y-Richtung (Pixel/Sekunde wenn use_delta_time=True)
           use_delta_time: Wenn True, wird dx/dy mit Delta-Zeit multipliziert (Standard: True)
       """
       if use_delta_time:
           # Zeit-basierte Bewegung: Pixel/Sekunde → Pixel/Frame
           dx = dx * _delta_time
           dy = dy * _delta_time
       
       # Rest bleibt gleich...
   ```

2. **Rückwärtskompatibilität:**
   - Standard: `use_delta_time=True` (neue Zeit-basierte Bewegung)
   - Alte Code: Kann `use_delta_time=False` verwenden (Frame-basiert)

#### 5.4. Debug-Overlay

**Datei:** `game_editor/engine/runtime.py`, Zeile 347-355

**Erweitern:**
- FPS (bereits vorhanden)
- Delta-Zeit (neu)
- Gesamt-Zeit (neu)
- Objekt-Zähler (bereits vorhanden)

#### 5.5. Editor-Integration (optional)

**Datei:** `game_editor/ui/code_editor.py` oder `game_editor/ui/console.py`

**Optional:** Zeit-Anzeige im Editor (wenn Spiel läuft):
- FPS im Console-Widget
- Delta-Zeit im Console-Widget
- Gesamt-Zeit im Console-Widget

**WICHTIG:** Nur wenn Spiel läuft, nicht im Editor selbst!

---

## 📍 Wo muss Zeit überall eingebunden werden?

### ✅ Runtime-System (`runtime.py`)

1. **Zeit initialisieren** (vor Game Loop):
   - `game_start_time` setzen
   - `last_frame_time` setzen
   - `target_fps` aus config laden

2. **Zeit berechnen** (im Game Loop, VOR Updates):
   - `current_time` berechnen
   - `delta_time` berechnen
   - `total_time` berechnen
   - `_update_time()` aufrufen

3. **FPS berechnen** (im Game Loop, NACH Rendering):
   - `fps = clock.get_fps()`
   - `clock.tick(target_fps)`

4. **Debug-Overlay erweitern** (im Game Loop, beim Rendering):
   - FPS anzeigen (bereits vorhanden)
   - Delta-Zeit anzeigen (neu)
   - Gesamt-Zeit anzeigen (neu)

### ✅ API-System (`api.py`)

1. **Zeit-Variablen** (globale Variablen):
   - `_delta_time`
   - `_total_time`
   - `_fps`

2. **Update-Funktion** (`_update_time()`):
   - Wird von runtime.py aufgerufen

3. **Zeit-Funktionen** (für Schüler-Code):
   - `get_delta_time()`
   - `get_total_time()`
   - `get_fps()`

4. **Namespace-Integration** (in `load_student_code()` und Objekt-Code):
   - Zeit-Funktionen zum Namespace hinzufügen

### ✅ Bewegung-System (`api.py`, `move_with_collision()`)

1. **Delta-Zeit-Support**:
   - Parameter `use_delta_time` hinzufügen
   - Standard: `True` (zeit-basiert)
   - Multiplikation: `dx * delta_time`, `dy * delta_time`

2. **Rückwärtskompatibilität**:
   - Alte Code kann `use_delta_time=False` verwenden

### ✅ Debug-Overlay (`runtime.py`)

1. **Zeit-Anzeige erweitern**:
   - FPS (bereits vorhanden)
   - Delta-Zeit (neu)
   - Gesamt-Zeit (neu)

### ⚠️ Editor-Integration (optional)

1. **Console-Widget** (`game_editor/ui/console.py`):
   - Zeit-Anzeige wenn Spiel läuft (optional)

2. **Code-Editor** (`game_editor/ui/code_editor.py`):
   - Zeit-Anzeige im Debug-Overlay (optional)

---

## 🎮 Beispiel: Vorher vs. Nachher

### Vorher (Frame-basiert):
```python
platform_speed = 2  # Pixel pro Frame
dx = platform_speed * platform_direction  # Bei 60 FPS = 120 Pixel/Sekunde
move_with_collision(platform, dx, dy)
```

**Problem:**
- Bei 30 FPS: 60 Pixel/Sekunde (zu langsam)
- Bei 60 FPS: 120 Pixel/Sekunde (korrekt)
- Bei 120 FPS: 240 Pixel/Sekunde (zu schnell)

### Nachher (Zeit-basiert):
```python
platform_speed = 120  # Pixel pro Sekunde
dx = platform_speed * platform_direction  # Wird automatisch mit Delta-Zeit multipliziert
move_with_collision(platform, dx, dy)  # use_delta_time=True (Standard)
```

**Oder explizit:**
```python
platform_speed = 120  # Pixel pro Sekunde
dx = platform_speed * get_delta_time() * platform_direction
move_with_collision(platform, dx, dy, use_delta_time=False)
```

**Vorteil:**
- Bei 30 FPS: 120 Pixel/Sekunde (korrekt!)
- Bei 60 FPS: 120 Pixel/Sekunde (korrekt!)
- Bei 120 FPS: 120 Pixel/Sekunde (korrekt!)
- **Konsistent auf allen Systemen!**

---

## 🔄 Migration: Frame-basiert → Zeit-basiert

### Alte Code (Frame-basiert):
```python
speed = 3  # Pixel pro Frame
dx = speed  # Bei 60 FPS = 180 Pixel/Sekunde
```

### Neue Code (Zeit-basiert):
```python
speed = 180  # Pixel pro Sekunde
dx = speed  # Wird automatisch mit Delta-Zeit multipliziert
move_with_collision(player, dx, dy)  # use_delta_time=True (Standard)
```

### Rückwärtskompatibilität:
```python
# Alte Code funktioniert weiterhin:
speed = 3  # Pixel pro Frame
dx = speed
move_with_collision(player, dx, dy, use_delta_time=False)  # Explizit Frame-basiert
```

---

## 📊 Zeit-Anzeige: Wo und wie?

### 1. Debug-Overlay (im Spiel)

**Datei:** `game_editor/engine/runtime.py`, Zeile 347-355

**Position:** Oben links auf dem Bildschirm

**Anzeige:**
```
FPS: 60
Delta: 16.67ms
Zeit: 45.23s
Objekte: 12
```

**Sichtbarkeit:** Nur wenn `debug_mode = True` (F1-Taste)

### 2. Console-Widget (im Editor, optional)

**Datei:** `game_editor/ui/console.py`

**Position:** Im Console-Widget, wenn Spiel läuft

**Anzeige:**
```
[FPS: 60] [Delta: 16.67ms] [Zeit: 45.23s]
```

**Sichtbarkeit:** Nur wenn Spiel läuft

### 3. Code-Editor (optional)

**Datei:** `game_editor/ui/code_editor.py`

**Position:** Im Debug-Overlay des Code-Editors (optional)

**Anzeige:** FPS, Delta-Zeit, Gesamt-Zeit

---

## 🎯 Zeit als Standard-Richtwert

### Bewegung

**Aktuell:**
```python
dx = speed  # Frame-basiert
```

**Neu:**
```python
dx = speed  # Zeit-basiert (automatisch mit Delta-Zeit multipliziert)
# speed ist jetzt in Pixel/Sekunde, nicht Pixel/Frame!
```

### Pausen/Timer

**Aktuell:** Nicht vorhanden

**Neu:**
```python
# Timer-Variable
timer = 0.0

def update():
    global timer
    
    # Timer erhöhen
    timer += get_delta_time()
    
    # Nach 2 Sekunden etwas tun
    if timer >= 2.0:
        print_debug("2 Sekunden vergangen!")
        timer = 0.0  # Zurücksetzen
```

### Animationen (später)

**Aktuell:** Nicht vorhanden

**Neu:**
```python
# Animation mit Zeit-basierter Frame-Rate
animation_timer = 0.0
frame_duration = 0.1  # 0.1 Sekunden pro Frame

def update():
    global animation_timer
    
    animation_timer += get_delta_time()
    
    if animation_timer >= frame_duration:
        # Nächstes Frame
        current_frame += 1
        animation_timer = 0.0
```

### Physik (Schwerkraft, etc.)

**Aktuell:**
```python
gravity = 0.5  # Pixel pro Frame
velocity_y += gravity  # Bei 60 FPS = 30 Pixel/Sekunde
```

**Neu:**
```python
gravity = 500  # Pixel pro Sekunde² (Beschleunigung)
velocity_y += gravity * get_delta_time()  # Zeit-basierte Beschleunigung
```

---

## 🔍 Integration in bestehende Systeme

### 1. Game Loop (`runtime.py`)

**Aktueller Ablauf:**
```
1. Events verarbeiten
2. Tastatur-Status aktualisieren
3. API aktualisieren
4. Updates ausführen
5. Rendering
6. clock.tick(60)
```

**Neuer Ablauf:**
```
1. Zeit berechnen (VOR allem anderen!)
2. Events verarbeiten
3. Tastatur-Status aktualisieren
4. API aktualisieren (inkl. Zeit)
5. Updates ausführen (können Delta-Zeit verwenden)
6. Rendering
7. Debug-Overlay (zeigt Zeit)
8. clock.tick(60)
```

### 2. API-Initialisierung

**Aktuell:**
```python
_init_api(game_objects)  # Zeile 244
```

**Neu:**
```python
_init_api(game_objects)
_update_time(delta_time, total_time, fps)  # Zeit-API aktualisieren
```

### 3. Namespace-Erstellung

**Aktuell:**
```python
game_namespace = {
    "get_object": get_object,
    # ...
}
```

**Neu:**
```python
game_namespace = {
    "get_object": get_object,
    # ...
    "get_delta_time": get_delta_time,
    "get_total_time": get_total_time,
    "get_fps": get_fps,
}
```

### 4. Bewegung-Funktionen

**Aktuell:**
```python
def move_with_collision(obj, dx, dy):
    obj.x += dx  # Frame-basiert
    obj.y += dy
```

**Neu:**
```python
def move_with_collision(obj, dx, dy, use_delta_time=True):
    if use_delta_time:
        dx = dx * _delta_time  # Zeit-basiert
        dy = dy * _delta_time
    obj.x += dx
    obj.y += dy
```

---

## 📋 Checkliste: Alle Systeme

### ✅ Runtime-System
- [ ] Zeit-Variablen initialisieren (vor Game Loop)
- [ ] Zeit berechnen (im Game Loop, VOR Updates)
- [ ] FPS berechnen (im Game Loop, NACH Rendering)
- [ ] Debug-Overlay erweitern (FPS, Delta-Zeit, Gesamt-Zeit)
- [ ] `target_fps` aus config laden (optional)

### ✅ API-System
- [ ] Zeit-Variablen hinzufügen (`_delta_time`, `_total_time`, `_fps`)
- [ ] `_update_time()` Funktion erstellen
- [ ] `get_delta_time()` Funktion erstellen
- [ ] `get_total_time()` Funktion erstellen
- [ ] `get_fps()` Funktion erstellen
- [ ] Zeit-Funktionen in Namespace einfügen (game.py)
- [ ] Zeit-Funktionen in Namespace einfügen (Objekt-Code)

### ✅ Bewegung-System
- [ ] `move_with_collision()` erweitern (Delta-Zeit-Support)
- [ ] `push_objects()` erweitern (Delta-Zeit-Support, optional)
- [ ] Rückwärtskompatibilität sicherstellen

### ✅ Debug-Overlay
- [ ] FPS anzeigen (bereits vorhanden)
- [ ] Delta-Zeit anzeigen (neu)
- [ ] Gesamt-Zeit anzeigen (neu)
- [ ] Formatierung optimieren

### ⚠️ Editor-Integration (optional)
- [ ] Console-Widget: Zeit-Anzeige wenn Spiel läuft
- [ ] Code-Editor: Zeit-Anzeige im Debug-Overlay

### ⚠️ Templates (später, für deutsche API)
- [ ] Template-Code: Zeit-basierte Bewegung-Beispiele
- [ ] Template-Code: Timer-Beispiele

---

## 🎓 Für Schüler (Klasse 7-10)

### Einfache Zeit-basierte Bewegung:
```python
spieler = hole_objekt("player")
geschwindigkeit = 120  # Pixel pro Sekunde

funktion aktualisiere():
    dx = 0
    wenn taste_gedrückt("RECHTS"):
        dx = geschwindigkeit  # Wird automatisch mit Delta-Zeit multipliziert
    
    bewege_mit_kollision(spieler, dx, 0)
```

### Timer-Beispiel:
```python
timer = 0.0

funktion aktualisiere():
    global timer
    
    timer += hole_delta_zeit()
    
    wenn timer >= 2.0:
        drucke_debug("2 Sekunden vergangen!")
        timer = 0.0
```

### Zeit-basierte Schwerkraft:
```python
schwerkraft = 500  # Pixel pro Sekunde²
geschwindigkeit_y = 0.0

funktion aktualisiere():
    global geschwindigkeit_y
    
    geschwindigkeit_y += schwerkraft * hole_delta_zeit()
    
    bewege_mit_kollision(spieler, 0, geschwindigkeit_y)
```

---

## ⚠️ Wichtige Überlegungen

### Delta-Zeit-Begrenzung
**Problem:** Bei sehr niedriger FPS kann Delta-Zeit sehr groß werden (z.B. 1 Sekunde)

**Lösung:** Delta-Zeit begrenzen:
```python
delta_time = min(delta_time, 0.1)  # Maximal 100ms (10 FPS Minimum)
```

### Rückwärtskompatibilität
**WICHTIG:** Alte Code muss weiterhin funktionieren!

**Lösung:**
- Standard: `use_delta_time=True` (zeit-basiert)
- Alte Code: Kann `use_delta_time=False` verwenden
- Oder: Alte Code multipliziert manuell mit `get_delta_time()`

### Performance
**Delta-Zeit-Berechnung:** Minimaler Overhead (nur 3 Berechnungen pro Frame)

**Zeit-basierte Bewegung:** Minimaler Overhead (2 Multiplikationen pro Bewegung)

---

## 🐛 Randfälle und Probleme

**WICHTIG:** Eine vollständige Analyse aller potenziellen Randfälle und Probleme findet sich in:
📄 **`INGAME_UHR_RANDFAELLE.md`** - Detaillierte Liste mit 27+ identifizierten Problemen und Lösungen

**Kritische Probleme (müssen gelöst werden):**
1. **Erster Frame:** Delta-Zeit könnte 0 oder sehr groß sein
2. **Negatives Delta-Zeit:** System-Uhr springt zurück
3. **Delta-Zeit = 0:** Frame-Skipping verhindert Bewegung
4. **Sehr niedrige FPS:** Delta-Zeit wird sehr groß → Objekte springen
5. **Rückwärtskompatibilität:** Alte Code muss weiterhin funktionieren

**Sollte dokumentiert werden:**
- Timer-Methoden (Akkumulation vs. `get_total_time()`)
- Schüler-Fehler (falsche Verwendung von `get_delta_time()`)
- Gemischte Bewegung (Frame-basiert + Zeit-basiert vermeiden)

Siehe `INGAME_UHR_RANDFAELLE.md` für vollständige Details und Lösungsvorschläge.

---

## 🚀 Implementierungs-Reihenfolge

1. **Zeit-Manager Modul erstellen** (`time.py`) - KERN
   - `TimeManager` Klasse (modular, erweiterbar)
   - Zeit-Berechnung (Delta-Zeit, Gesamt-Zeit)
   - FPS-Berechnung (gleitender Durchschnitt)
   - Validierung und Begrenzung

2. **Runtime erweitern** (TimeManager verwenden)
   - TimeManager initialisieren
   - Bei jedem Frame aktualisieren
   - An API übergeben

3. **Zeit-API erweitern** (für Schüler-Code)
   - Zeit-Manager-Referenz
   - API-Funktionen (`get_delta_time()`, etc.)
   - Namespace-Integration

4. **Zeit-basierte Bewegung** (Migration)
   - `move_with_collision()` erweitern
   - Rückwärtskompatibilität

5. **Debug-Overlay erweitern** (Anzeige)
   - Delta-Zeit anzeigen
   - Gesamt-Zeit anzeigen

6. **Templates aktualisieren** (Beispiele)
   - Zeit-basierte Bewegung-Beispiele
   - Timer-Beispiele

---

## 🏗️ Modulare Architektur

**WICHTIG:** Für einen modularen und effizienten Aufbau siehe:
📄 **`INGAME_UHR_MODULAR.md`** - Detaillierte modulare Struktur mit:
- `TimeManager` Klasse (separates Modul)
- Klare Trennung der Verantwortlichkeiten
- Effizienz-Optimierungen
- Erweiterbarkeit (Pause, Slow-Motion, etc.)
- Testbarkeit

**Empfohlene Struktur:**
```
time.py          → TimeManager (Kern-Logik, isoliert)
api.py           → Zeit-API (für Schüler-Code)
runtime.py       → Verwendet TimeManager
```

**Vorteile:**
- ✅ Modular: Klare Trennung der Verantwortlichkeiten
- ✅ Effizient: Minimale Berechnungen, kein unnötiger Overhead
- ✅ Erweiterbar: Einfach neue Features hinzufügen
- ✅ Testbar: Einfach zu testen (Mock-Objekte möglich)

---

## 📝 Notizen

- **target_fps:** Sollte aus `project.json` geladen werden können (optional)
- **Delta-Zeit-Begrenzung:** Maximal 0.1 Sekunden (verhindert Sprünge bei niedriger FPS)
- **Zeit-Format:** Alle Zeiten in Sekunden (float)
- **FPS-Format:** Integer (ganze Zahl)
- **Rückwärtskompatibilität:** Alte Code muss weiterhin funktionieren!
