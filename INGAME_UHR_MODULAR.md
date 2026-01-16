# Modularer und Effizienter Aufbau: Ingame-Uhr System

## 🎯 Design-Prinzipien

### 1. Separation of Concerns
- **Zeit-Verwaltung:** Separates Modul (`time.py`)
- **Zeit-API:** Teil von `api.py` (für Schüler-Code)
- **Zeit-Anzeige:** Teil von `runtime.py` (Debug-Overlay)

### 2. Single Responsibility
- Jedes Modul hat eine klare Aufgabe
- Keine Vermischung von Verantwortlichkeiten

### 3. Dependency Injection
- Zeit-Manager wird von Runtime initialisiert
- API greift auf Zeit-Manager zu (nicht umgekehrt)

### 4. Performance
- Minimale Berechnungen pro Frame
- Caching wo sinnvoll
- Keine unnötigen Objekt-Erstellungen

---

## 📁 Modulare Struktur

### Neue Datei: `game_editor/engine/time.py`

**Zweck:** Zentrale Zeit-Verwaltung (Kern-Logik)

**Verantwortlichkeiten:**
- Zeit-Berechnung (Delta-Zeit, Gesamt-Zeit)
- FPS-Berechnung
- Validierung und Begrenzung
- Zeit-Reset beim Neustart

**Vorteile:**
- ✅ Klare Trennung von Runtime-Logik
- ✅ Wiederverwendbar für andere Features
- ✅ Einfach zu testen
- ✅ Einfach zu erweitern

---

## 🏗️ Implementierung

### Option A: Klasse-basiert (Empfohlen)

**Vorteile:**
- ✅ Kapselung (keine globalen Variablen)
- ✅ Einfach zu testen
- ✅ Einfach zu erweitern
- ✅ Klare API

**Nachteile:**
- ⚠️ Minimaler Overhead (Methoden-Aufrufe)

**Implementierung:**

```python
# game_editor/engine/time.py
"""
Zeit-Manager - Zentrale Zeit-Verwaltung für das Spiel
"""
import pygame
from typing import Optional


class TimeManager:
    """Verwaltet Zeit-Berechnung, Delta-Zeit und FPS"""
    
    def __init__(self, target_fps: int = 60):
        """
        Initialisiert den Zeit-Manager
        
        Args:
            target_fps: Ziel-FPS (Standard: 60)
        """
        self.target_fps = target_fps
        self.game_start_time: float = 0.0
        self.last_frame_time: float = 0.0
        self.delta_time: float = 0.0
        self.total_time: float = 0.0
        self.fps: int = 0
        self.frame_count: int = 0
        
        # FPS-Berechnung (gleitender Durchschnitt)
        self.fps_samples: list[float] = []
        self.fps_sample_size: int = 10
        
        # Validierung
        self.max_delta_time: float = 0.1  # Maximal 100ms (10 FPS Minimum)
        self.min_delta_time: float = 0.0001  # Minimal 0.1ms (verhindert Division durch 0)
        
        # Flags
        self.first_frame: bool = True
        self.initialized: bool = False
    
    def start(self):
        """Startet die Zeit-Messung (beim Spielstart)"""
        current_time = pygame.time.get_ticks() / 1000.0
        self.game_start_time = current_time
        self.last_frame_time = current_time
        self.total_time = 0.0
        self.delta_time = 1.0 / self.target_fps  # Standard-Delta-Zeit
        self.frame_count = 0
        self.first_frame = True
        self.initialized = True
    
    def update(self, clock: pygame.time.Clock) -> float:
        """
        Aktualisiert Zeit-Werte (wird bei jedem Frame aufgerufen)
        
        Args:
            clock: Pygame Clock-Objekt für FPS-Berechnung
            
        Returns:
            Delta-Zeit in Sekunden
        """
        if not self.initialized:
            self.start()
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Erster Frame: Standard-Delta-Zeit verwenden
        if self.first_frame:
            self.first_frame = False
            self.last_frame_time = current_time
            self.delta_time = 1.0 / self.target_fps
            return self.delta_time
        
        # Delta-Zeit berechnen
        raw_delta = current_time - self.last_frame_time
        
        # Validierung: Negatives Delta-Zeit verhindern
        if raw_delta < 0:
            # System-Uhr wurde zurückgestellt
            self.last_frame_time = current_time
            self.delta_time = 1.0 / self.target_fps
            return self.delta_time
        
        # Validierung: Delta-Zeit begrenzen (verhindert Sprünge bei niedriger FPS)
        self.delta_time = min(raw_delta, self.max_delta_time)
        
        # Validierung: Minimum-Delta-Zeit (verhindert Division durch 0)
        if self.delta_time <= 0:
            self.delta_time = self.min_delta_time
        
        # Gesamt-Zeit aktualisieren
        self.total_time = current_time - self.game_start_time
        
        # FPS berechnen (nach Rendering, wenn clock.get_fps() verfügbar ist)
        raw_fps = clock.get_fps()
        if raw_fps > 0:
            # Gleitender Durchschnitt für stabilere FPS-Anzeige
            self.fps_samples.append(raw_fps)
            if len(self.fps_samples) > self.fps_sample_size:
                self.fps_samples.pop(0)
            
            if len(self.fps_samples) > 0:
                self.fps = int(sum(self.fps_samples) / len(self.fps_samples))
        
        # Frame-Zähler
        self.frame_count += 1
        
        # Für nächsten Frame
        self.last_frame_time = current_time
        
        return self.delta_time
    
    def get_delta_time(self) -> float:
        """Gibt Delta-Zeit zurück (Sekunden seit letztem Frame)"""
        return self.delta_time
    
    def get_total_time(self) -> float:
        """Gibt Gesamt-Spielzeit zurück (Sekunden seit Start)"""
        return self.total_time
    
    def get_fps(self) -> int:
        """Gibt aktuelle FPS zurück"""
        return self.fps
    
    def get_frame_count(self) -> int:
        """Gibt Anzahl der Frames seit Start zurück"""
        return self.frame_count
    
    def reset(self):
        """Setzt Zeit-Manager zurück (beim Neustart)"""
        self.start()
    
    def set_target_fps(self, target_fps: int):
        """Setzt Ziel-FPS (kann während des Spiels geändert werden)"""
        self.target_fps = max(1, target_fps)  # Minimum: 1 FPS
```

---

### Option B: Funktions-basiert (Einfacher, aber weniger modular)

**Vorteile:**
- ✅ Einfacher (keine Klasse)
- ✅ Minimaler Overhead (direkte Funktionsaufrufe)

**Nachteile:**
- ⚠️ Globale Variablen (weniger sauber)
- ⚠️ Schwerer zu testen
- ⚠️ Schwerer zu erweitern

**Implementierung:**

```python
# game_editor/engine/time.py
"""
Zeit-Funktionen - Zentrale Zeit-Verwaltung
"""
import pygame
from typing import Optional

# Globale Variablen
_game_start_time: float = 0.0
_last_frame_time: float = 0.0
_delta_time: float = 0.0
_total_time: float = 0.0
_fps: int = 60
_frame_count: int = 0
_first_frame: bool = True
_initialized: bool = False
_target_fps: int = 60

# FPS-Berechnung
_fps_samples: list[float] = []
_fps_sample_size: int = 10

# Validierung
_max_delta_time: float = 0.1
_min_delta_time: float = 0.0001


def start_time(target_fps: int = 60):
    """Startet Zeit-Messung"""
    global _game_start_time, _last_frame_time, _total_time, _delta_time
    global _frame_count, _first_frame, _initialized, _target_fps
    
    current_time = pygame.time.get_ticks() / 1000.0
    _game_start_time = current_time
    _last_frame_time = current_time
    _total_time = 0.0
    _delta_time = 1.0 / target_fps
    _frame_count = 0
    _first_frame = True
    _initialized = True
    _target_fps = target_fps


def update_time(clock: pygame.time.Clock) -> float:
    """Aktualisiert Zeit-Werte (bei jedem Frame)"""
    # ... (ähnlich wie Klasse-Version)
    return _delta_time


def get_delta_time() -> float:
    """Gibt Delta-Zeit zurück"""
    return _delta_time


def get_total_time() -> float:
    """Gibt Gesamt-Zeit zurück"""
    return _total_time


def get_fps() -> int:
    """Gibt FPS zurück"""
    return _fps
```

**Empfehlung:** Option A (Klasse-basiert) für bessere Modularität

---

## 🔗 Integration in bestehende Module

### 1. `runtime.py` - Zeit-Manager verwenden

```python
# game_editor/engine/runtime.py
from .time import TimeManager

def main(project_path: str):
    # ... bestehender Code ...
    
    clock = pygame.time.Clock()
    target_fps = config.get("target_fps", 60)
    
    # Zeit-Manager initialisieren
    time_manager = TimeManager(target_fps=target_fps)
    time_manager.start()
    
    # Game Loop
    while running:
        # Zeit aktualisieren (VOR allen Updates!)
        delta_time = time_manager.update(clock)
        
        # API aktualisieren (inkl. Zeit)
        _init_api(game_objects)
        _update_time_api(time_manager)  # Neue Funktion
        
        # ... Rest des Game Loops ...
        
        # Debug-Overlay
        if debug_mode:
            fps = time_manager.get_fps()
            delta = time_manager.get_delta_time()
            total = time_manager.get_total_time()
            # ... Anzeige ...
        
        pygame.display.flip()
        clock.tick(target_fps)
```

---

### 2. `api.py` - Zeit-API für Schüler-Code

```python
# game_editor/engine/api.py
from .time import TimeManager
from typing import Optional

# Zeit-Manager-Referenz (wird von Runtime gesetzt)
_time_manager: Optional[TimeManager] = None


def _set_time_manager(time_manager: TimeManager):
    """Setzt Zeit-Manager (wird von runtime.py aufgerufen)"""
    global _time_manager
    _time_manager = time_manager


def get_delta_time() -> float:
    """
    Gibt Delta-Zeit zurück (Sekunden seit letztem Frame)
    
    Returns:
        Delta-Zeit in Sekunden (z.B. 0.016 bei 60 FPS)
    """
    if _time_manager is None:
        # Fallback wenn nicht initialisiert
        return 1.0 / 60.0
    return _time_manager.get_delta_time()


def get_total_time() -> float:
    """
    Gibt Gesamt-Spielzeit zurück (Sekunden seit Start)
    
    Returns:
        Gesamt-Zeit in Sekunden
    """
    if _time_manager is None:
        return 0.0
    return _time_manager.get_total_time()


def get_fps() -> int:
    """
    Gibt aktuelle FPS zurück
    
    Returns:
        FPS als Integer
    """
    if _time_manager is None:
        return 60
    return _time_manager.get_fps()
```

**Vorteile:**
- ✅ Keine globalen Zeit-Variablen in `api.py`
- ✅ Klare Trennung: Zeit-Manager vs. Zeit-API
- ✅ Einfach zu testen (Mock-Objekt möglich)

---

### 3. `runtime.py` - Zeit-Manager an API übergeben

```python
# game_editor/engine/runtime.py
from .api import _set_time_manager

def main(project_path: str):
    # ... bestehender Code ...
    
    time_manager = TimeManager(target_fps=target_fps)
    time_manager.start()
    
    # Zeit-Manager an API übergeben
    _set_time_manager(time_manager)
    
    # ... Rest des Codes ...
```

---

## 📊 Effizienz-Optimierungen

### 1. Minimale Berechnungen pro Frame

**Aktuell:**
- `pygame.time.get_ticks()` → 1 Aufruf
- Delta-Zeit-Berechnung → 1 Subtraktion
- Validierung → 2 Vergleiche + 1 min()
- Gesamt: ~5 Operationen pro Frame

**Optimiert:**
- Gleiche Operationen, aber strukturiert
- Keine unnötigen Berechnungen

---

### 2. FPS-Berechnung (Gleitender Durchschnitt)

**Problem:** `clock.get_fps()` ist bei ersten Frames ungenau

**Lösung:**
```python
# In TimeManager.update()
raw_fps = clock.get_fps()
if raw_fps > 0:
    self.fps_samples.append(raw_fps)
    if len(self.fps_samples) > self.fps_sample_size:
        self.fps_samples.pop(0)
    
    if len(self.fps_samples) > 0:
        self.fps = int(sum(self.fps_samples) / len(self.fps_samples))
```

**Vorteile:**
- ✅ Stabilere FPS-Anzeige
- ✅ Weniger Sprünge
- ✅ Minimaler Overhead (nur bei FPS-Berechnung)

---

### 3. Caching von Berechnungen

**Nicht nötig:**
- Delta-Zeit wird bei jedem Frame neu berechnet (korrekt)
- Gesamt-Zeit wird bei jedem Frame neu berechnet (korrekt)
- FPS wird bei jedem Frame aktualisiert (korrekt)

**Caching wäre kontraproduktiv:**
- Zeit-Werte müssen aktuell sein
- Caching würde nur Overhead hinzufügen

---

### 4. Methoden-Aufrufe optimieren

**Problem:** Methoden-Aufrufe haben Overhead

**Lösung:**
- Direkte Zugriffe auf Attribute (wenn nötig)
- Aber: Kapselung ist wichtiger als minimaler Overhead
- Overhead ist vernachlässigbar (< 1% der Frame-Zeit)

**Optional (wenn Performance kritisch):**
```python
# Direkter Zugriff (weniger sauber, aber schneller)
delta_time = time_manager.delta_time  # Statt: time_manager.get_delta_time()
```

**Empfehlung:** Methoden verwenden (sauberer, Overhead ist minimal)

---

## 🔄 Erweiterbarkeit

### 1. Zeit-Skalierung (Slow-Motion, Fast-Forward)

**Einfach erweiterbar:**
```python
class TimeManager:
    def __init__(self, target_fps: int = 60):
        # ... bestehender Code ...
        self.time_scale: float = 1.0  # 1.0 = normal, 0.5 = slow-motion, 2.0 = fast-forward
    
    def get_delta_time(self) -> float:
        """Gibt skalierte Delta-Zeit zurück"""
        return self.delta_time * self.time_scale
    
    def set_time_scale(self, scale: float):
        """Setzt Zeit-Skalierung"""
        self.time_scale = max(0.0, scale)  # Minimum: 0 (pausiert)
```

---

### 2. Pause-System

**Einfach erweiterbar:**
```python
class TimeManager:
    def __init__(self, target_fps: int = 60):
        # ... bestehender Code ...
        self.paused: bool = False
    
    def pause(self):
        """Pausiert Zeit"""
        self.paused = True
    
    def resume(self):
        """Setzt Zeit fort"""
        self.paused = False
    
    def get_delta_time(self) -> float:
        """Gibt Delta-Zeit zurück (0 wenn pausiert)"""
        if self.paused:
            return 0.0
        return self.delta_time
```

---

### 3. Mehrere Zeit-Spuren (für Animationen, etc.)

**Einfach erweiterbar:**
```python
class TimeManager:
    def __init__(self, target_fps: int = 60):
        # ... bestehender Code ...
        self.time_tracks: dict[str, float] = {}  # Zusätzliche Zeit-Spuren
    
    def get_track_time(self, track_name: str) -> float:
        """Gibt Zeit für spezifische Spur zurück"""
        if track_name not in self.time_tracks:
            self.time_tracks[track_name] = 0.0
        return self.time_tracks[track_name]
    
    def update_track(self, track_name: str, delta: float):
        """Aktualisiert Zeit-Spur"""
        if track_name not in self.time_tracks:
            self.time_tracks[track_name] = 0.0
        self.time_tracks[track_name] += delta
```

---

## 🧪 Testbarkeit

### 1. Unit-Tests für TimeManager

```python
# tests/test_time.py
import unittest
from unittest.mock import Mock
from game_editor.engine.time import TimeManager
import pygame

class TestTimeManager(unittest.TestCase):
    def setUp(self):
        self.time_manager = TimeManager(target_fps=60)
        self.clock = Mock()
        self.clock.get_fps.return_value = 60.0
    
    def test_start(self):
        self.time_manager.start()
        self.assertTrue(self.time_manager.initialized)
        self.assertEqual(self.time_manager.delta_time, 1.0 / 60.0)
    
    def test_update(self):
        self.time_manager.start()
        delta = self.time_manager.update(self.clock)
        self.assertGreater(delta, 0)
        self.assertLessEqual(delta, 0.1)
    
    def test_negative_delta(self):
        # Simuliere System-Uhr-Sprung
        self.time_manager.start()
        # ... Test negativer Delta-Zeit ...
```

---

### 2. Mock-Objekt für API-Tests

```python
# tests/test_api.py
from unittest.mock import Mock
from game_editor.engine.api import get_delta_time, _set_time_manager
from game_editor.engine.time import TimeManager

def test_get_delta_time():
    time_manager = Mock(spec=TimeManager)
    time_manager.get_delta_time.return_value = 0.016
    
    _set_time_manager(time_manager)
    assert get_delta_time() == 0.016
```

---

## 📋 Zusammenfassung: Modulare Struktur

### Datei-Struktur:
```
game_editor/engine/
├── __init__.py
├── time.py          # NEU: Zeit-Manager (Kern-Logik)
├── api.py           # ERWEITERT: Zeit-API für Schüler-Code
├── runtime.py       # ERWEITERT: Verwendet TimeManager
├── gameobject.py
├── collision.py
└── loader.py
```

### Abhängigkeiten:
```
runtime.py
  └──> time.py (TimeManager)
  └──> api.py (_set_time_manager)

api.py
  └──> time.py (TimeManager-Referenz)

time.py
  └──> pygame (nur für get_ticks())
```

### Vorteile:
- ✅ **Modular:** Klare Trennung der Verantwortlichkeiten
- ✅ **Effizient:** Minimale Berechnungen, keine unnötigen Objekte
- ✅ **Erweiterbar:** Einfach neue Features hinzufügen (Pause, Slow-Motion, etc.)
- ✅ **Testbar:** Einfach zu testen (Mock-Objekte möglich)
- ✅ **Wartbar:** Klare Struktur, einfach zu verstehen

---

## 🚀 Implementierungs-Reihenfolge

1. **`time.py` erstellen** (TimeManager-Klasse)
   - Kern-Logik isoliert
   - Einfach zu testen

2. **`runtime.py` erweitern** (TimeManager verwenden)
   - Zeit-Manager initialisieren
   - Bei jedem Frame aktualisieren

3. **`api.py` erweitern** (Zeit-API für Schüler-Code)
   - Zeit-Manager-Referenz
   - API-Funktionen

4. **Integration testen**
   - Unit-Tests für TimeManager
   - Integration-Tests für Runtime

5. **Debug-Overlay erweitern**
   - Zeit-Werte anzeigen

---

## ⚡ Performance-Vergleich

### Option A (Klasse-basiert):
- **Overhead:** ~0.001ms pro Frame (Methoden-Aufrufe)
- **Speicher:** ~200 Bytes (TimeManager-Objekt)
- **Vorteile:** Modular, erweiterbar, testbar

### Option B (Funktions-basiert):
- **Overhead:** ~0.0005ms pro Frame (direkte Zugriffe)
- **Speicher:** ~150 Bytes (globale Variablen)
- **Vorteile:** Minimaler Overhead

**Fazit:** Overhead-Unterschied ist vernachlässigbar (< 0.1% der Frame-Zeit). Option A ist besser für Modularität und Wartbarkeit.

---

## 🎯 Empfehlung

**Verwende Option A (Klasse-basiert):**
- ✅ Besser für langfristige Wartbarkeit
- ✅ Einfacher zu erweitern (Pause, Slow-Motion, etc.)
- ✅ Einfacher zu testen
- ✅ Klare API
- ✅ Overhead ist vernachlässigbar

**Struktur:**
```
time.py          → TimeManager (Kern-Logik)
api.py           → Zeit-API (für Schüler-Code)
runtime.py       → Verwendet TimeManager
```
