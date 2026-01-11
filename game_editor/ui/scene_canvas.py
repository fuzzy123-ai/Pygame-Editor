"""
Scene Canvas - 2D Canvas für Objekte mit Drag & Drop, Zoom, Game Preview
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                                QPushButton, QSlider, QComboBox, QMenu)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QTimer, QMimeData
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QPen, QBrush, QPixmap, QImage, QWheelEvent, QContextMenuEvent, QDrag
from pathlib import Path
import json
from typing import Optional, Dict, Any, List


class SceneCanvas(QWidget):
    """2D Canvas für Szenen-Editierung"""
    
    object_selected = Signal(dict)  # Signal wenn Objekt ausgewählt wird
    undo_redo_changed = Signal()  # Signal wenn Undo/Redo-Status sich ändert
    
    def __init__(self):
        super().__init__()
        self.project_path: Optional[Path] = None
        self.scene_data: Dict[str, Any] = {}
        self.objects: List[Dict[str, Any]] = []
        self.selected_object_id: Optional[str] = None  # Für Rückwärtskompatibilität
        self.selected_object_ids: List[str] = []  # Mehrfachauswahl
        self.undo_redo_manager = None  # Wird vom main_window gesetzt
        self.console = None  # Wird vom main_window gesetzt
        self._last_move_positions = {}  # Speichert letzte Positionen für Move-Commands
        self._copied_collider = None  # Zwischenablage für kopierte Kollisionsbox
        self._duplicating = False  # Flag für Alt+Drag Duplizieren
        self._duplicate_preview_mode = False  # Flag für Duplizieren mit Vorschau
        self._duplicate_preview_objects = []  # Liste der Vorschau-Objekte (Dicts)
        self._duplicate_preview_offset = QPoint(0, 0)  # Offset für Vorschau-Position
        
        # Zoom
        self.zoom_factor = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
        # Grid (wird aus Projekt-Einstellungen geladen)
        self.grid_size = 16  # Standard-Grid-Größe
        self.grid_color = QColor(200, 200, 200, 120)  # Standard-Grid-Farbe
        
        # Panning (mit mittlerer Maustaste)
        self.panning = False
        self.pan_start_pos = QPoint()
        self.view_offset = QPoint(0, 0)  # Offset für Panning
        
        # Drag & Drop
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.drag_object_id: Optional[str] = None
        
        # Game Preview
        self.preview_mode = False
        # self.preview_surface: Optional[pygame.Surface] = None  # Wird später implementiert
        
        # Layer-System
        self.current_layer = "default"  # Aktuell gewählter Layer
        self.available_layers = ["background", "default", "foreground"]  # Verfügbare Layer
        
        # Anzeige-Optionen
        self.show_labels = True  # Namen/IDs anzeigen
        self.show_highlights = True  # Hervorhebungen anzeigen
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        # Dark-Mode für Scene Canvas
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Werkzeugleiste (für spätere Map-Editier-Funktionen) - Dark-Mode
        tool_toolbar = QHBoxLayout()
        tool_toolbar.setContentsMargins(5, 5, 5, 5)
        
        title = QLabel("Scene Canvas")
        title.setStyleSheet("font-weight: bold; padding: 5px; color: #d4d4d4;")
        tool_toolbar.addWidget(title)
        
        tool_toolbar.addStretch()
        
        # Layer-Auswahl (Dark-Mode)
        layer_label = QLabel("Layer:")
        layer_label.setStyleSheet("font-size: 10pt; padding: 5px; color: #d4d4d4;")
        tool_toolbar.addWidget(layer_label)
        
        self.layer_combo = QComboBox()
        self.layer_combo.addItems(self.available_layers)
        self.layer_combo.setCurrentText(self.current_layer)
        self.layer_combo.currentTextChanged.connect(self._on_layer_changed)
        self.layer_combo.setStyleSheet("""
            QComboBox {
                padding: 3px;
                font-weight: bold;
                background-color: #4a9eff;
                color: white;
                border: 2px solid #3a8eef;
                border-radius: 3px;
            }
            QComboBox:hover {
                background-color: #5aaeff;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #3a8eef;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #d4d4d4;
                selection-background-color: #4a9eff;
            }
        """)
        tool_toolbar.addWidget(self.layer_combo)
        
        tool_toolbar.addStretch()
        
        # Platzhalter für zukünftige Tools
        # TODO: Hier kommen später Map-Editier-Tools rein
        
        layout.addLayout(tool_toolbar)
        
        # Canvas mit Zoom-Controls oben rechts
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        
        # Zoom-Controls oben rechts (klein, in der Ecke)
        zoom_container = QWidget()
        zoom_container.setFixedSize(220, 30)  # Breiter für größeren Slider
        zoom_layout = QHBoxLayout()
        zoom_layout.setContentsMargins(5, 0, 5, 0)
        zoom_layout.setSpacing(5)
        
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("font-size: 10pt; color: #d4d4d4;")
        zoom_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)  # 0.5
        self.zoom_slider.setMaximum(200)  # 2.0
        self.zoom_slider.setValue(100)  # 1.0
        self.zoom_slider.setFixedWidth(120)  # Breiter gemacht
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #2d2d2d;
                height: 6px;
                border-radius: 3px;
                border: 1px solid #3d3d3d;
            }
            QSlider::sub-page:horizontal {
                background-color: #4a9eff;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background-color: #4a9eff;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
                border: 2px solid #3a8eef;
            }
            QSlider::handle:horizontal:hover {
                background-color: #5aaeff;
                border-color: #4a9eff;
            }
            QSlider::handle:horizontal:pressed {
                background-color: #3a8eef;
                border-color: #2a7eef;
            }
        """)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        zoom_value_label = QLabel("100%")
        zoom_value_label.setMinimumWidth(40)
        zoom_value_label.setStyleSheet("font-size: 10pt; color: #d4d4d4;")
        self.zoom_value_label = zoom_value_label
        zoom_layout.addWidget(zoom_value_label)
        
        # Augen-Symbol Button für Labels/Highlights Toggle
        from PySide6.QtWidgets import QToolButton
        self.toggle_labels_button = QToolButton()
        self.toggle_labels_button.setText("👁")  # Augen-Symbol
        self.toggle_labels_button.setToolTip("Namen und Hervorhebungen ein/aus")
        self.toggle_labels_button.setCheckable(True)
        self.toggle_labels_button.setChecked(True)  # Standard: an
        self.toggle_labels_button.setStyleSheet("""
            QToolButton {
                font-size: 14pt;
                padding: 3px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QToolButton:checked {
                background-color: #4a9eff;
                color: white;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolButton:checked:hover {
                background-color: #5aaeff;
            }
        """)
        self.toggle_labels_button.toggled.connect(self._on_toggle_labels)
        zoom_layout.addWidget(self.toggle_labels_button)
        
        zoom_container.setLayout(zoom_layout)
        
        # Canvas-Widget
        self.canvas = CanvasWidget(self)
        
        # Overlay-Layout für Zoom-Controls oben rechts
        overlay_layout = QVBoxLayout()
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.addWidget(self.canvas, 1)
        
        # Zoom-Controls oben rechts positionieren
        canvas_wrapper = QWidget()
        canvas_wrapper.setLayout(overlay_layout)
        
        # Zoom-Container oben rechts
        zoom_wrapper = QWidget(canvas_wrapper)
        zoom_wrapper.setLayout(QVBoxLayout())
        zoom_wrapper.layout().setContentsMargins(0, 0, 0, 0)
        zoom_wrapper.layout().addWidget(zoom_container)
        zoom_wrapper.layout().addStretch()
        zoom_wrapper.setGeometry(0, 0, 220, 30)  # Breiter für größeren Slider
        zoom_wrapper.setStyleSheet("background-color: rgba(30, 30, 30, 220); border-radius: 5px; border: 1px solid #3d3d3d;")  # Dark-Mode Hintergrund
        
        canvas_layout.addWidget(canvas_wrapper, 1)
        canvas_container.setLayout(canvas_layout)
        
        layout.addWidget(canvas_container, 1)  # Mehr Platz für Canvas
        
        self.setLayout(layout)
        
        # Canvas-Events verbinden
        self.canvas.mouse_pressed.connect(self._on_mouse_pressed)
        self.canvas.mouse_moved.connect(self._on_mouse_moved)
        self.canvas.mouse_released.connect(self._on_mouse_released)
    
    def load_project(self, project_path: Path):
        """Lädt Projekt und Szene"""
        self.project_path = project_path
        self._load_grid_settings()
        self._load_scene()
    
    def _load_grid_settings(self):
        """Lädt Grid-Einstellungen aus project.json"""
        if not self.project_path:
            return
        
        project_file = self.project_path / "project.json"
        if project_file.exists():
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Grid-Größe = Sprite-Größe (quadratisch)
                sprite_size = config.get("sprite_size", 64)
                # Alte Format-Unterstützung (width/height)
                if isinstance(sprite_size, dict):
                    self.grid_size = sprite_size.get("width", sprite_size.get("size", 64))
                else:
                    # Neues Format (nur eine Zahl)
                    self.grid_size = sprite_size if isinstance(sprite_size, int) else 64
                
                # Grid-Farbe laden
                grid_settings = config.get("grid", {})
                grid_color = grid_settings.get("color", [200, 200, 200, 120])
                if isinstance(grid_color, list) and len(grid_color) >= 3:
                    alpha = grid_color[3] if len(grid_color) >= 4 else 120
                    self.grid_color = QColor(grid_color[0], grid_color[1], grid_color[2], alpha)
                else:
                    self.grid_color = QColor(200, 200, 200, 120)
            except Exception:
                pass  # Standard-Werte beibehalten
    
    def _cleanup_duplicate_ids_and_names(self):
        """Bereinigt doppelte IDs und Namen in der Objekt-Liste"""
        seen_ids = set()
        seen_names = set()
        duplicate_fixed = False
        
        # Erster Durchlauf: Alle IDs sammeln und doppelte finden
        for obj in self.objects:
            obj_id = obj.get("id")
            
            # Doppelte oder fehlende ID reparieren
            if not obj_id or obj_id in seen_ids:
                # Neue eindeutige ID generieren
                base_id = obj_id if obj_id and obj_id.startswith("object_") else None
                if not base_id:
                    base_id = f"object_{len(self.objects)}"
                
                counter = 1
                new_id = base_id
                while new_id in seen_ids:
                    new_id = f"object_{len(self.objects) + counter}"
                    counter += 1
                
                old_id = obj_id or "fehlend"
                obj["id"] = new_id
                seen_ids.add(new_id)
                duplicate_fixed = True
                print(f"[Canvas] Doppelte ID repariert: {old_id} -> {new_id}")
            else:
                seen_ids.add(obj_id)
        
        # Zweiter Durchlauf: Namen bereinigen
        for obj in self.objects:
            obj_name = obj.get("name", "")
            
            # Doppelte Namen reparieren (nur wenn Name gesetzt ist)
            if obj_name and obj_name.strip():
                if obj_name in seen_names:
                    # Namen mit Nummer versehen
                    base_name = obj_name
                    counter = 1
                    unique_name = obj_name
                    while unique_name in seen_names:
                        unique_name = f"{base_name}_{counter}"
                        counter += 1
                    obj["name"] = unique_name
                    seen_names.add(unique_name)
                    duplicate_fixed = True
                    print(f"[Canvas] Doppelter Name repariert: {base_name} -> {unique_name}")
                else:
                    seen_names.add(obj_name)
        
        if duplicate_fixed:
            print(f"[Canvas] Duplikate bereinigt - {len(self.objects)} Objekte, {len(seen_ids)} eindeutige IDs")
    
    def _load_scene(self):
        """Lädt die aktuelle Szene"""
        if not self.project_path:
            return
        
        # Projekt-Konfiguration laden
        project_file = self.project_path / "project.json"
        if not project_file.exists():
            return
        
        with open(project_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        start_scene = config.get("start_scene", "level1")
        
        # Szene laden
        scene_file = self.project_path / "scenes" / f"{start_scene}.json"
        if not scene_file.exists():
            # Leere Szene erstellen
            self.scene_data = {
                "name": "Level 1",
                "background_color": [135, 206, 235],
                "objects": []
            }
        else:
            with open(scene_file, 'r', encoding='utf-8') as f:
                self.scene_data = json.load(f)
        
        self.objects = self.scene_data.get("objects", [])
        
        # Doppelte IDs und Namen bereinigen
        self._cleanup_duplicate_ids_and_names()
        
        # Objekte auf Grid-Größe anpassen (wenn nicht bereits korrekt)
        for obj in self.objects:
            # Objekt-Größe = Grid-Größe setzen
            obj["width"] = self.grid_size
            obj["height"] = self.grid_size
            
            # Position an Grid ausrichten
            obj["x"] = (obj.get("x", 0) // self.grid_size) * self.grid_size
            obj["y"] = (obj.get("y", 0) // self.grid_size) * self.grid_size
            
            # Layer-Information hinzufügen falls nicht vorhanden (für Rückwärtskompatibilität)
            if "layer" not in obj:
                obj["layer"] = "default"
        
        # Szene speichern mit aktualisierten Größen und bereinigten Duplikaten
        self.save_scene()
        
        # Sprite-Cache leeren beim Laden
        if self.canvas:
            self.canvas.sprite_cache.clear()
        self.canvas.update()
        # Selektion zurücksetzen
        self.selected_object_id = None
    
    def save_scene(self):
        """Speichert die aktuelle Szene"""
        if not self.project_path:
            return
        
        # Projekt-Konfiguration laden
        project_file = self.project_path / "project.json"
        if not project_file.exists():
            return
        
        with open(project_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        start_scene = config.get("start_scene", "level1")
        
        # Alle Sprite-Pfade zu relativen Pfaden konvertieren
        objects_to_save = []
        for obj in self.objects:
            obj_copy = obj.copy()
            sprite_path = obj_copy.get("sprite")
            if sprite_path:
                try:
                    sprite_path_obj = Path(sprite_path)
                    if sprite_path_obj.is_absolute():
                        # Versuchen relativ zum Projekt-Ordner zu machen
                        try:
                            rel_path = sprite_path_obj.relative_to(self.project_path)
                            obj_copy["sprite"] = str(rel_path).replace("\\", "/")
                        except ValueError:
                            # Pfad liegt außerhalb des Projekts - behalten wie es ist
                            pass
                    else:
                        # Bereits relativ - sicherstellen dass Pfad-Separatoren korrekt sind
                        obj_copy["sprite"] = sprite_path.replace("\\", "/")
                except Exception:
                    # Bei Fehler Pfad behalten wie er ist
                    pass
            objects_to_save.append(obj_copy)
        
        # Szene speichern
        scene_file = self.project_path / "scenes" / f"{start_scene}.json"
        scene_file.parent.mkdir(parents=True, exist_ok=True)
        
        scene_data_to_save = self.scene_data.copy()
        scene_data_to_save["objects"] = objects_to_save
        
        with open(scene_file, 'w', encoding='utf-8') as f:
            json.dump(scene_data_to_save, f, indent=2, ensure_ascii=False)
    
    def _on_zoom_changed(self, value: int):
        """Wird aufgerufen wenn Zoom geändert wird"""
        self.zoom_factor = value / 100.0
        self.zoom_value_label.setText(f"{value}%")
        self.canvas.update()
    
    def _on_layer_changed(self, layer_name: str):
        """Wird aufgerufen wenn Layer geändert wird"""
        self.current_layer = layer_name
        # Selektion zurücksetzen wenn Objekt nicht im aktiven Layer ist
        if self.selected_object_id:
            selected_obj = next((obj for obj in self.objects if obj.get("id") == self.selected_object_id), None)
            if selected_obj and selected_obj.get("layer", "default") != self.current_layer:
                self.selected_object_id = None
                self.object_selected.emit({})
        # Canvas aktualisieren
        self.canvas.update()
    
    def _on_toggle_labels(self, checked: bool):
        """Wird aufgerufen wenn Labels/Highlights Toggle geändert wird"""
        self.show_labels = checked
        self.show_highlights = checked
        self.canvas.update()
    
    
    def _on_mouse_pressed(self, pos: QPoint):
        """Wird aufgerufen wenn Maus gedrückt wird"""
        # Canvas-Koordinaten in World-Koordinaten umrechnen
        # Panning-Offset berücksichtigen
        adjusted_pos = pos - self.view_offset
        # Zoom-Faktor anwenden
        world_x = int(adjusted_pos.x() / self.zoom_factor)
        world_y = int(adjusted_pos.y() / self.zoom_factor)
        
        # Objekt finden das angeklickt wurde
        # Zuerst Objekte des aktiven Layers prüfen, dann andere Layer
        clicked_obj = None
        
        # Phase 1: Objekte des aktiven Layers (prioritär)
        for obj in reversed(self.objects):  # Von hinten nach vorne
            obj_layer = obj.get("layer", "default")
            if obj_layer != self.current_layer:
                continue
                
            # Prüfen ob Klick innerhalb der Objekt-Grenzen liegt
            obj_x = int(obj.get("x", 0))
            obj_y = int(obj.get("y", 0))
            obj_width = int(obj.get("width", 32))
            obj_height = int(obj.get("height", 32))
            
            # Toleranz für Klickerkennung (ein paar Pixel) - macht Klicken einfacher
            tolerance = 2
            if (obj_x - tolerance <= world_x < obj_x + obj_width + tolerance and
                obj_y - tolerance <= world_y < obj_y + obj_height + tolerance):
                clicked_obj = obj
                break
        
        # Phase 2: Falls kein Objekt im aktiven Layer gefunden, andere Layer prüfen
        if clicked_obj is None:
            for obj in reversed(self.objects):  # Von hinten nach vorne
                obj_layer = obj.get("layer", "default")
                if obj_layer == self.current_layer:
                    continue  # Bereits geprüft
                    
                # Prüfen ob Klick innerhalb der Objekt-Grenzen liegt
                obj_x = int(obj.get("x", 0))
                obj_y = int(obj.get("y", 0))
                obj_width = int(obj.get("width", 32))
                obj_height = int(obj.get("height", 32))
                
                # Toleranz für Klickerkennung
                tolerance = 2
                if (obj_x - tolerance <= world_x < obj_x + obj_width + tolerance and
                    obj_y - tolerance <= world_y < obj_y + obj_height + tolerance):
                    clicked_obj = obj
                    # Layer wechseln zum gefundenen Objekt
                    if obj_layer in self.available_layers:
                        self.current_layer = obj_layer
                        self.layer_combo.setCurrentText(obj_layer)
                    break
        
        if clicked_obj:
            clicked_obj_id = clicked_obj.get("id")
            
            # Shift-Taste: Mehrfachauswahl
            modifiers = getattr(self, '_mouse_modifiers', Qt.NoModifier)
            if modifiers & Qt.ShiftModifier:
                # Objekt zur Auswahl hinzufügen oder entfernen
                if clicked_obj_id in self.selected_object_ids:
                    self.selected_object_ids.remove(clicked_obj_id)
                else:
                    self.selected_object_ids.append(clicked_obj_id)
            else:
                # Prüfen ob angeklicktes Objekt bereits ausgewählt ist
                if clicked_obj_id in self.selected_object_ids:
                    # Objekt ist bereits ausgewählt - alle ausgewählten Objekte bewegen
                    # Auswahl bleibt bestehen, keine Änderung
                    pass
                else:
                    # Normale Auswahl: Nur dieses Objekt
                    self.selected_object_ids = [clicked_obj_id]
            
            # Für Rückwärtskompatibilität
            self.selected_object_id = self.selected_object_ids[0] if self.selected_object_ids else None
            
            # Alt-Taste: Duplizieren statt Bewegen
            if modifiers & Qt.AltModifier:
                self._duplicating = True
            else:
                self._duplicating = False
                self.dragging = True
                self.drag_start_pos = pos
                self.drag_object_id = clicked_obj_id
                # Drag-Start-Positionen für alle ausgewählten Objekte speichern
                self._drag_start_positions = {}  # Dict: obj_id -> (x, y)
                self._drag_start_canvas_pos = pos  # Rohe Canvas-Position für Delta-Berechnung
                
                # Start-Positionen aller ausgewählten Objekte speichern
                for obj_id in self.selected_object_ids:
                    obj = next((o for o in self.objects if o.get("id") == obj_id), None)
                    if obj:
                        obj_layer = obj.get("layer", "default")
                        if obj_layer == self.current_layer:  # Nur Objekte im aktiven Layer
                            self._drag_start_positions[obj_id] = QPoint(obj.get("x", 0), obj.get("y", 0))
            
            self.object_selected.emit(clicked_obj)
        else:
            # Kein Objekt angeklickt - Auswahl zurücksetzen (außer bei Shift)
            modifiers = getattr(self, '_mouse_modifiers', Qt.NoModifier)
            if not (modifiers & Qt.ShiftModifier):
                self.selected_object_ids = []
                self.selected_object_id = None
                self.dragging = False
                self.drag_object_id = None
                self.object_selected.emit({})  # Leeres Dictionary = keine Auswahl
                # Drag-Start-Positionen löschen
                if hasattr(self, '_drag_start_positions'):
                    delattr(self, '_drag_start_positions')
                if hasattr(self, '_drag_start_canvas_pos'):
                    delattr(self, '_drag_start_canvas_pos')
        
        self.canvas.update()
    
    def _on_mouse_moved(self, pos: QPoint):
        """Wird aufgerufen wenn Maus bewegt wird"""
        # Alt+Drag: Duplizieren
        if self._duplicating and self.drag_object_id:
            # Delta berechnen
            if not hasattr(self, '_drag_start_canvas_pos'):
                return
            
            canvas_dx = pos.x() - self._drag_start_canvas_pos.x()
            canvas_dy = pos.y() - self._drag_start_canvas_pos.y()
            
            # Nur duplizieren wenn genug bewegt wurde (mindestens 5 Pixel)
            if abs(canvas_dx) < 5 and abs(canvas_dy) < 5:
                return
            
            # Original-Objekt finden
            original_obj = None
            for obj in self.objects:
                if obj.get("id") == self.drag_object_id:
                    original_obj = obj
                    break
            
            if original_obj:
                # Neues Objekt duplizieren
                new_obj = original_obj.copy()
                
                # Neue eindeutige ID generieren
                new_obj["id"] = self._generate_unique_id()
                
                # Neuen eindeutigen Namen generieren
                base_name = new_obj.get("name", "")
                if not base_name or not base_name.strip():
                    # Wenn kein Name vorhanden, verwende die ID als Basis
                    base_name = new_obj.get("id", "object")
                new_obj["name"] = self._generate_unique_name(base_name)
                
                # Delta in World-Koordinaten umrechnen
                dx = int(canvas_dx / self.zoom_factor)
                dy = int(canvas_dy / self.zoom_factor)
                
                # Neue Position berechnen
                new_x = original_obj.get("x", 0) + dx
                new_y = original_obj.get("y", 0) + dy
                
                # An Grid ausrichten
                grid_x = (new_x // self.grid_size) * self.grid_size
                grid_y = (new_y // self.grid_size) * self.grid_size
                grid_x = int(grid_x)
                grid_y = int(grid_y)
                
                # Prüfen ob Position frei ist
                grid_cell_x = grid_x // self.grid_size
                grid_cell_y = grid_y // self.grid_size
                position_free = True
                for other_obj in self.objects:
                    other_x = other_obj.get("x", 0)
                    other_y = other_obj.get("y", 0)
                    other_grid_x = other_x // self.grid_size
                    other_grid_y = other_y // self.grid_size
                    if other_grid_x == grid_cell_x and other_grid_y == grid_cell_y:
                        position_free = False
                        break
                
                if position_free:
                    new_obj["x"] = grid_x
                    new_obj["y"] = grid_y
                    
                    # Objekt hinzufügen
                    self.objects.append(new_obj)
                    
                    # Undo/Redo-Command erstellen
                    if self.undo_redo_manager:
                        from ..utils.commands import ObjectAddCommand
                        command = ObjectAddCommand(
                            new_obj,
                            self.objects,
                            lambda: (self.canvas.update(), self.save_scene())
                        )
                        self.undo_redo_manager.execute_command(command)
                        self.undo_redo_changed.emit()
                    
                    # Auswahl auf neues Objekt setzen
                    self.selected_object_ids = [new_obj.get("id")]
                    self.selected_object_id = new_obj.get("id")
                    self.drag_object_id = new_obj.get("id")
                    
                    # Duplizieren beenden
                    self._duplicating = False
                    self.dragging = True
                    # Start-Positionen für das neue Objekt speichern
                    self._drag_start_positions = {new_obj.get("id"): QPoint(grid_x, grid_y)}
                    self._drag_start_canvas_pos = pos
                    
                    self.save_scene()
                    self.canvas.update()
                    self.object_selected.emit(new_obj)
            return
        
        if self.dragging and hasattr(self, '_drag_start_positions') and self._drag_start_positions:
            # Sicherstellen dass Start-Positionen gesetzt sind
            if not hasattr(self, '_drag_start_canvas_pos'):
                self._drag_start_canvas_pos = pos
            
            # Delta in Canvas-Koordinaten berechnen (rohe Pixel-Differenz)
            canvas_dx = pos.x() - self._drag_start_canvas_pos.x()
            canvas_dy = pos.y() - self._drag_start_canvas_pos.y()
            
            # Delta in World-Koordinaten umrechnen (Zoom berücksichtigen)
            dx = int(canvas_dx / self.zoom_factor)
            dy = int(canvas_dy / self.zoom_factor)
            
            # Alle ausgewählten Objekte zusammen bewegen
            for obj_id, start_pos in self._drag_start_positions.items():
                obj = next((o for o in self.objects if o.get("id") == obj_id), None)
                if not obj:
                    continue
                
                # Nur Objekte des aktiven Layers können bewegt werden
                obj_layer = obj.get("layer", "default")
                if obj_layer != self.current_layer:
                    continue
                
                # Neue Position berechnen (basierend auf ursprünglicher World-Position)
                new_x = start_pos.x() + dx
                new_y = start_pos.y() + dy
                
                # An Grid ausrichten (Grid-Position)
                grid_x = (new_x // self.grid_size) * self.grid_size
                grid_y = (new_y // self.grid_size) * self.grid_size
                grid_x = int(grid_x)
                grid_y = int(grid_y)
                
                # Prüfen ob bereits ein anderes Objekt an dieser Grid-Position existiert
                grid_cell_x = grid_x // self.grid_size
                grid_cell_y = grid_y // self.grid_size
                position_free = True
                for other_obj in self.objects:
                    other_id = other_obj.get("id")
                    # Ignoriere alle ausgewählten Objekte (werden gerade bewegt)
                    if other_id in self._drag_start_positions:
                        continue
                    other_layer = other_obj.get("layer", "default")
                    if other_layer != self.current_layer:
                        continue  # Nur Objekte im selben Layer prüfen
                    other_x = other_obj.get("x", 0)
                    other_y = other_obj.get("y", 0)
                    other_grid_x = other_x // self.grid_size
                    other_grid_y = other_y // self.grid_size
                    if other_grid_x == grid_cell_x and other_grid_y == grid_cell_y:
                        position_free = False
                        break
                
                # Nur bewegen wenn Position frei ist
                if position_free:
                    obj["x"] = grid_x
                    obj["y"] = grid_y
                
                # Objekt-Größe = Grid-Größe sicherstellen
                obj["width"] = self.grid_size
                obj["height"] = self.grid_size
            
            # Signal für Inspector (vom angeklickten Objekt)
            if self.drag_object_id:
                clicked_obj = next((o for o in self.objects if o.get("id") == self.drag_object_id), None)
                if clicked_obj:
                    self.object_selected.emit(clicked_obj)
            
            self.canvas.update()
    
    def set_undo_redo_manager(self, manager):
        """Setzt den Undo/Redo-Manager"""
        self.undo_redo_manager = manager
    
    def _on_mouse_released(self, pos: QPoint):
        """Wird aufgerufen wenn Maus losgelassen wird"""
        if self.dragging and hasattr(self, '_drag_start_positions') and self._drag_start_positions and self.undo_redo_manager:
            # Move-Commands für alle ausgewählten Objekte erstellen
            from ..utils.commands import ObjectMoveCommand
            
            for obj_id, start_pos in self._drag_start_positions.items():
                obj = next((o for o in self.objects if o.get("id") == obj_id), None)
                if not obj:
                    continue
                
                # Nur Objekte des aktiven Layers
                obj_layer = obj.get("layer", "default")
                if obj_layer != self.current_layer:
                    continue
                
                old_x = start_pos.x()
                old_y = start_pos.y()
                new_x = obj.get("x", 0)
                new_y = obj.get("y", 0)
                
                # Nur Command erstellen wenn Position sich geändert hat
                if old_x != new_x or old_y != new_y:
                    command = ObjectMoveCommand(
                        obj,
                        old_x,
                        old_y,
                        new_x,
                        new_y,
                        lambda: (self.canvas.update(), self.save_scene())
                    )
                    self.undo_redo_manager.execute_command(command)
                    
                    # Letzte Position speichern
                    self._last_move_positions[obj_id] = (new_x, new_y)
            
            if self._drag_start_positions:
                self.undo_redo_changed.emit()  # Signal für Button-Update
                self.save_scene()  # Auto-Save nach Drag
        
        self.dragging = False
        self.drag_object_id = None
        # Drag-Start-Positionen löschen
        if hasattr(self, '_drag_start_positions'):
            delattr(self, '_drag_start_positions')
        if hasattr(self, '_drag_start_canvas_pos'):
            delattr(self, '_drag_start_canvas_pos')
    
    def _generate_unique_id(self) -> str:
        """Generiert eine eindeutige Objekt-ID"""
        existing_ids = {obj.get("id") for obj in self.objects if obj.get("id")}
        base_id = f"object_{len(self.objects) + 1}"
        obj_id = base_id
        counter = 1
        while obj_id in existing_ids:
            obj_id = f"object_{len(self.objects) + 1 + counter}"
            counter += 1
        return obj_id
    
    def _generate_unique_name(self, desired_name: str = "") -> str:
        """Generiert einen eindeutigen Namen (falls Name gewünscht)"""
        if not desired_name or not desired_name.strip():
            return ""  # Kein Name gewünscht
        
        existing_names = {obj.get("name", "") for obj in self.objects if obj.get("name")}
        base_name = desired_name.strip()
        unique_name = base_name
        counter = 1
        while unique_name in existing_names:
            unique_name = f"{base_name}_{counter}"
            counter += 1
        return unique_name
    
    def add_object_from_sprite(self, sprite_path: str, x: int, y: int):
        """Fügt ein neues Objekt aus einem Sprite hinzu"""
        # Neue eindeutige ID generieren
        obj_id = self._generate_unique_id()
        
        # Objekt-Größe = Grid-Größe (quadratisch)
        obj_size = self.grid_size
        
        # Sprite-Pfad normalisieren (absolut → relativ)
        normalized_sprite_path = sprite_path
        if self.project_path:
            try:
                sprite_path_obj = Path(sprite_path)
                if sprite_path_obj.is_absolute():
                    # Versuchen relativ zum Projekt-Ordner zu machen
                    try:
                        rel_path = sprite_path_obj.relative_to(self.project_path)
                        normalized_sprite_path = str(rel_path).replace("\\", "/")
                    except ValueError:
                        # Pfad liegt außerhalb des Projekts - behalten wie es ist
                        normalized_sprite_path = sprite_path
                else:
                    # Bereits relativ - sicherstellen dass Pfad-Separatoren korrekt sind
                    normalized_sprite_path = sprite_path.replace("\\", "/")
            except Exception:
                # Bei Fehler Pfad behalten wie er ist
                normalized_sprite_path = sprite_path
        
        new_obj = {
            "id": obj_id,
            "type": "sprite",
            "sprite": normalized_sprite_path,
            "x": x,
            "y": y,
            "width": obj_size,
            "height": obj_size,
            "layer": self.current_layer,  # Layer-Information hinzufügen
            "collider": {
                "enabled": False,  # Nicht per default aktiv
                "type": "rect"
            },
            "ground": False  # Standard: kein Ground
        }
        
        # Prüfen ob bereits ein Objekt an dieser Grid-Position existiert
        # Nur wenn es im selben Layer ist, verhindern wir doppelte Platzierung
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        for existing_obj in self.objects:
            existing_grid_x = existing_obj.get("x", 0) // self.grid_size
            existing_grid_y = existing_obj.get("y", 0) // self.grid_size
            existing_layer = existing_obj.get("layer", "default")
            if (existing_grid_x == grid_x and existing_grid_y == grid_y and 
                existing_layer == self.current_layer):
                # Objekt existiert bereits an dieser Position im selben Layer
                # Erlaube aber Objekte in anderen Layern an derselben Position
                print(f"[Canvas] Objekt bereits vorhanden an Grid ({grid_x}, {grid_y}) im Layer {self.current_layer}")
                return
        
        self.objects.append(new_obj)
        
        # Undo/Redo-Command erstellen
        if self.undo_redo_manager:
            from ..utils.commands import ObjectAddCommand
            command = ObjectAddCommand(
                self.objects,
                new_obj,
                lambda: self.canvas.update()
            )
            self.undo_redo_manager.execute_command(command)
            self.undo_redo_changed.emit()  # Signal für Button-Update
        
        # Canvas sofort aktualisieren
        self.canvas.update()
        
        self.save_scene()
        
        # Neues Objekt auswählen, damit es sofort bewegt werden kann
        self.selected_object_id = obj_id
        # Signal sofort senden - Canvas ist bereits aktualisiert
        self.object_selected.emit(new_obj)
        # Canvas nochmal aktualisieren um Selektion anzuzeigen
        self.canvas.update()
    
    def add_empty_object(self):
        """Fügt ein neues leeres Objekt hinzu (ohne Sprite)"""
        # Neue eindeutige ID generieren
        obj_id = self._generate_unique_id()
        
        # Objekt-Größe = Grid-Größe (quadratisch)
        obj_size = self.grid_size
        
        # Standard-Position (0, 0) - kann später verschoben werden
        grid_x = 0
        grid_y = 0
        
        new_obj = {
            "id": obj_id,
            "type": "empty",
            "sprite": None,  # Kein Sprite
            "x": grid_x,
            "y": grid_y,
            "width": obj_size,
            "height": obj_size,
            "layer": self.current_layer,
            "collider": {
                "enabled": False,  # Nicht per default aktiv
                "type": "rect"
            },
            "ground": False,  # Standard: kein Ground
            "code": ""  # Leerer Code für neues Objekt
        }
        
        self.objects.append(new_obj)
        
        # Undo/Redo-Command erstellen
        if self.undo_redo_manager:
            from ..utils.commands import ObjectAddCommand
            command = ObjectAddCommand(
                self.objects,
                new_obj,
                lambda: self.canvas.update()
            )
            self.undo_redo_manager.execute_command(command)
            self.undo_redo_changed.emit()  # Signal für Button-Update
        else:
            self.canvas.update()
        
        self.save_scene()
        
        # Neues Objekt auswählen
        self.selected_object_id = obj_id
        self.object_selected.emit(new_obj)
    
    def _calculate_sprite_bounds(self, sprite_path: str) -> tuple[int, int, int, int]:
        """
        Berechnet die Bounding Box um die sichtbaren Pixel eines Sprites
        Gibt zurück: (min_x, min_y, width, height) relativ zum Sprite (in Grid-Größe)
        """
        if not self.project_path or not sprite_path:
            return (0, 0, self.grid_size, self.grid_size)
        
        try:
            # Pfad normalisieren
            sprite_path_obj = Path(sprite_path)
            if sprite_path_obj.is_absolute():
                full_path = sprite_path_obj
            else:
                full_path = self.project_path / sprite_path
            
            if not full_path.exists():
                msg = f"[Canvas] Sprite nicht gefunden: {full_path}"
                print(msg)
                if self.console:
                    self.console.append_debug(msg)
                return (0, 0, self.grid_size, self.grid_size)
            
            # Sprite als QImage laden (direkt, um Alpha-Kanal zu erhalten)
            image = QImage(str(full_path))
            if image.isNull():
                msg = f"[Canvas] Sprite konnte nicht geladen werden: {full_path}"
                print(msg)
                if self.console:
                    self.console.append_debug(msg)
                return (0, 0, self.grid_size, self.grid_size)
            
            # Bild-Format prüfen
            original_format = image.format()
            has_alpha = image.hasAlphaChannel()
            msg_format = f"[Canvas] Bild-Format: {original_format}, Hat Alpha: {has_alpha}, Größe: {image.width()}x{image.height()}"
            print(msg_format)
            if self.console:
                self.console.append_debug(msg_format)
            
            # Sicherstellen dass Alpha-Kanal vorhanden ist
            if image.format() != QImage.Format.Format_ARGB32:
                image = image.convertToFormat(QImage.Format.Format_ARGB32)
                msg_convert = f"[Canvas] Bild konvertiert zu ARGB32"
                print(msg_convert)
                if self.console:
                    self.console.append_debug(msg_convert)
            
            # Original-Größe
            original_width = image.width()
            original_height = image.height()
            
            # Bounding Box im Original-Bild finden
            orig_min_x = original_width
            orig_min_y = original_height
            orig_max_x = -1
            orig_max_y = -1
            has_visible_pixels = False
            
            # Durch alle Pixel des Original-Bildes iterieren
            visible_pixel_count = 0
            transparent_pixel_count = 0
            alpha_values = {}  # Debug: Zähle verschiedene Alpha-Werte
            
            for y in range(original_height):
                for x in range(original_width):
                    pixel = image.pixel(x, y)
                    # Alpha-Kanal extrahieren - mehrere Methoden versuchen
                    color = QColor(pixel)
                    alpha_qcolor = color.alpha()
                    
                    # Direkt aus Pixel extrahieren (ARGB32 Format: Alpha ist die oberen 8 Bits)
                    alpha_direct = (pixel >> 24) & 0xFF
                    
                    # Verwende den direkten Wert, da QColor.alpha() manchmal nicht korrekt ist
                    alpha = alpha_direct
                    
                    # Debug: Alpha-Werte zählen (nur erste 100 Pixel, um Performance zu sparen)
                    if visible_pixel_count + transparent_pixel_count < 100:
                        alpha_rounded = (alpha // 10) * 10  # Auf 10er-Schritte runden
                        alpha_values[alpha_rounded] = alpha_values.get(alpha_rounded, 0) + 1
                    
                    # Nur Pixel mit Alpha > 10 als sichtbar betrachten (Schwellenwert für Anti-Aliasing)
                    # Alpha 0-10 = transparent, Alpha 11-255 = sichtbar
                    if alpha > 10:
                        has_visible_pixels = True
                        visible_pixel_count += 1
                        orig_min_x = min(orig_min_x, x)
                        orig_min_y = min(orig_min_y, y)
                        orig_max_x = max(orig_max_x, x)
                        orig_max_y = max(orig_max_y, y)
                    else:
                        transparent_pixel_count += 1
            
            if not has_visible_pixels:
                # Keine sichtbaren Pixel - volle Größe verwenden
                msg = f"[Canvas] Keine sichtbaren Pixel gefunden in {sprite_path}"
                print(msg)
                if self.console:
                    self.console.append_debug(msg)
                return (0, 0, self.grid_size, self.grid_size)
            
            # Bounds im Original-Bild
            orig_width = orig_max_x - orig_min_x + 1
            orig_height = orig_max_y - orig_min_y + 1
            
            # Auf Grid-Größe skalieren (falls nötig)
            if original_width != self.grid_size or original_height != self.grid_size:
                # Skalierungsfaktoren
                scale_x = self.grid_size / original_width
                scale_y = self.grid_size / original_height
                
                # Bounds skalieren
                min_x = int(orig_min_x * scale_x)
                min_y = int(orig_min_y * scale_y)
                width = int(orig_width * scale_x)
                height = int(orig_height * scale_y)
            else:
                # Keine Skalierung nötig
                min_x = orig_min_x
                min_y = orig_min_y
                width = orig_width
                height = orig_height
            
            # Debug: Alpha-Werte-Statistik
            alpha_stats = ", ".join([f"Alpha {k}: {v}" for k, v in sorted(alpha_values.items())[:5]])  # Top 5
            msg = f"[Canvas] Sprite-Bounds für {sprite_path}: Original({orig_min_x},{orig_min_y},{orig_width},{orig_height}) -> Grid({min_x},{min_y},{width},{height}) | Sichtbar: {visible_pixel_count}, Transparent: {transparent_pixel_count} | {alpha_stats}"
            print(msg)
            if self.console:
                self.console.append_debug(msg)
            
            return (min_x, min_y, width, height)
        except Exception as e:
            import traceback
            print(f"[Canvas] Fehler beim Berechnen der Sprite-Bounds: {e}")
            traceback.print_exc()
            return (0, 0, self.grid_size, self.grid_size)
    
    def _add_collider(self, obj_id: str):
        """Fügt eine Kollisionsbox zu einem Objekt hinzu"""
        for obj in self.objects:
            if obj.get("id") == obj_id:
                collider_data = obj.get("collider", {})
                collider_data["enabled"] = True
                collider_data["type"] = "rect"
                
                # Kollisionsbox um sichtbare Pixel berechnen
                sprite_path = obj.get("sprite")
                if sprite_path:
                    min_x, min_y, width, height = self._calculate_sprite_bounds(sprite_path)
                    
                    # RELATIVE Position der Kollisionsbox (Offset vom Objekt)
                    # Sicherstellen dass Kollisionsbox innerhalb des Grid-Feldes bleibt
                    # min_x und min_y sind bereits relativ zum Sprite (0-96)
                    # Aber wir müssen sicherstellen, dass die Kollisionsbox innerhalb des Grid-Feldes (0-grid_size) bleibt
                    offset_x = max(0, min(min_x, self.grid_size - width))  # Innerhalb Grid-Feld
                    offset_y = max(0, min(min_y, self.grid_size - height))  # Innerhalb Grid-Feld
                    
                    # Breite und Höhe anpassen, falls nötig
                    width = min(width, self.grid_size - offset_x)
                    height = min(height, self.grid_size - offset_y)
                    
                    collider_data["offset_x"] = offset_x  # RELATIV zum Objekt
                    collider_data["offset_y"] = offset_y  # RELATIV zum Objekt
                    collider_data["width"] = width
                    collider_data["height"] = height
                else:
                    # Kein Sprite - volle Objekt-Größe verwenden (kein Offset)
                    collider_data["offset_x"] = 0  # RELATIV zum Objekt
                    collider_data["offset_y"] = 0  # RELATIV zum Objekt
                    collider_data["width"] = obj.get("width", self.grid_size)
                    collider_data["height"] = obj.get("height", self.grid_size)
                
                obj["collider"] = collider_data
                self.save_scene()
                self.canvas.update()
                break
    
    def _copy_collider(self, obj_id: str):
        """Kopiert die Kollisionsbox eines Objekts in die Zwischenablage"""
        for obj in self.objects:
            if obj.get("id") == obj_id:
                collider_data = obj.get("collider", {})
                if collider_data.get("enabled", False):
                    # Kollisionsbox-Daten kopieren (relative Position und Größe)
                    # Falls alte absolute Position vorhanden, in relative umrechnen
                    offset_x = collider_data.get("offset_x")
                    offset_y = collider_data.get("offset_y")
                    
                    if offset_x is None or offset_y is None:
                        # Alte absolute Position vorhanden - in relative umrechnen
                        obj_x = obj.get("x", 0)
                        obj_y = obj.get("y", 0)
                        collider_x = collider_data.get("x", obj_x)
                        collider_y = collider_data.get("y", obj_y)
                        offset_x = collider_x - obj_x
                        offset_y = collider_y - obj_y
                    
                    # Sicherstellen dass Offset innerhalb des Grid-Feldes ist
                    width = collider_data.get("width", self.grid_size)
                    height = collider_data.get("height", self.grid_size)
                    max_offset_x = self.grid_size - width
                    max_offset_y = self.grid_size - height
                    offset_x = max(0, min(offset_x, max_offset_x))
                    offset_y = max(0, min(offset_y, max_offset_y))
                    
                    self._copied_collider = {
                        "offset_x": offset_x,
                        "offset_y": offset_y,
                        "width": width,
                        "height": height,
                        "type": collider_data.get("type", "rect")
                    }
                    msg = f"[Canvas] Kollisionsbox kopiert: offset=({self._copied_collider['offset_x']},{self._copied_collider['offset_y']}), size=({self._copied_collider['width']},{self._copied_collider['height']})"
                    print(msg)
                    if self.console:
                        self.console.append_debug(msg)
                break
    
    def _paste_collider(self, obj_id: str):
        """Fügt die kopierte Kollisionsbox in ein Objekt ein"""
        if self._copied_collider is None:
            return
        
        for obj in self.objects:
            if obj.get("id") == obj_id:
                collider_data = obj.get("collider", {})
                collider_data["enabled"] = True
                collider_data["type"] = self._copied_collider.get("type", "rect")
                
                # Kopierte Werte übernehmen (relative Position und Größe)
                collider_data["offset_x"] = self._copied_collider["offset_x"]
                collider_data["offset_y"] = self._copied_collider["offset_y"]
                collider_data["width"] = self._copied_collider["width"]
                collider_data["height"] = self._copied_collider["height"]
                
                # Sicherstellen dass Kollisionsbox innerhalb des Grid-Feldes bleibt
                max_offset_x = self.grid_size - collider_data["width"]
                max_offset_y = self.grid_size - collider_data["height"]
                collider_data["offset_x"] = max(0, min(collider_data["offset_x"], max_offset_x))
                collider_data["offset_y"] = max(0, min(collider_data["offset_y"], max_offset_y))
                
                # Alte absolute Positionen entfernen (falls vorhanden)
                if "x" in collider_data:
                    del collider_data["x"]
                if "y" in collider_data:
                    del collider_data["y"]
                
                obj["collider"] = collider_data
                self.save_scene()
                self.canvas.update()
                
                msg = f"[Canvas] Kollisionsbox eingefügt: offset=({collider_data['offset_x']},{collider_data['offset_y']}), size=({collider_data['width']},{collider_data['height']})"
                print(msg)
                if self.console:
                    self.console.append_debug(msg)
                break
    
    def _remove_collider(self, obj_id: str):
        """Entfernt die Kollisionsbox von einem Objekt"""
        self._remove_collider_multiple([obj_id])
    
    def _remove_collider_multiple(self, obj_ids: List[str]):
        """Entfernt die Kollisionsbox von mehreren Objekten"""
        for obj in self.objects:
            if obj.get("id") in obj_ids:
                collider_data = obj.get("collider", {})
                collider_data["enabled"] = False
                obj["collider"] = collider_data
        self.save_scene()
        self.canvas.update()
    
    def _add_collider_multiple(self, obj_ids: List[str]):
        """Fügt Kollisionsbox zu mehreren Objekten hinzu"""
        for obj_id in obj_ids:
            self._add_collider(obj_id)
        self.save_scene()
        self.canvas.update()
    
    def _paste_collider_multiple(self, obj_ids: List[str]):
        """Fügt kopierte Kollisionsbox in mehrere Objekte ein"""
        for obj_id in obj_ids:
            self._paste_collider(obj_id)
        self.save_scene()
        self.canvas.update()
    
    def _add_ground(self, obj_id: str):
        """Fügt Boden-Eigenschaft zu einem Objekt hinzu"""
        self._add_ground_multiple([obj_id])
    
    def _add_ground_multiple(self, obj_ids: List[str]):
        """Fügt Boden-Eigenschaft zu mehreren Objekten hinzu"""
        for obj in self.objects:
            if obj.get("id") in obj_ids:
                obj["ground"] = True
        self.save_scene()
        self.canvas.update()
    
    def _remove_ground(self, obj_id: str):
        """Entfernt Boden-Eigenschaft von einem Objekt"""
        self._remove_ground_multiple([obj_id])
    
    def _remove_ground_multiple(self, obj_ids: List[str]):
        """Entfernt Boden-Eigenschaft von mehreren Objekten"""
        for obj in self.objects:
            if obj.get("id") in obj_ids:
                obj["ground"] = False
        self.save_scene()
        self.canvas.update()
    
    def _delete_object_by_id(self, obj_id: str):
        """Löscht ein Objekt anhand seiner ID"""
        self._delete_objects_multiple([obj_id])
    
    def _delete_objects_multiple(self, obj_ids: List[str]):
        """Löscht mehrere Objekte anhand ihrer IDs"""
        if not obj_ids or not self.undo_redo_manager:
            return
        
        # Objekte finden und löschen
        deleted_objects = []
        for obj_id in obj_ids:
            obj_to_delete = next((obj for obj in self.objects if obj.get("id") == obj_id), None)
            if obj_to_delete:
                deleted_objects.append(obj_to_delete)
        
        if not deleted_objects:
            return
        
        # Alle Objekte löschen (mit Undo/Redo)
        from ..utils.commands import ObjectDeleteCommand
        for obj_to_delete in deleted_objects:
            # ObjectDeleteCommand erwartet: (objects_list, deleted_object, canvas_update_callback)
            command = ObjectDeleteCommand(
                self.objects,
                obj_to_delete,
                lambda: (self.canvas.update(), self.save_scene())
            )
            self.undo_redo_manager.execute_command(command)
        
        self.undo_redo_changed.emit()
        
        # Auswahl zurücksetzen wenn gelöschte Objekte ausgewählt waren
        for obj_id in obj_ids:
            if obj_id in self.selected_object_ids:
                self.selected_object_ids.remove(obj_id)
            if self.selected_object_id == obj_id:
                self.selected_object_id = None
        
        # Neue Auswahl setzen falls noch Objekte ausgewählt sind
        if self.selected_object_ids:
            self.selected_object_id = self.selected_object_ids[0]
        else:
            self.selected_object_ids = []
            self.selected_object_id = None
            self.object_selected.emit({})
        
        self.save_scene()
        self.canvas.update()
    
    def _start_duplicate_preview(self, obj_ids: List[str]):
        """Startet den Duplizieren-Vorschau-Modus"""
        if not obj_ids:
            return
        
        # Original-Objekte finden und kopieren
        self._duplicate_preview_objects = []
        self._duplicate_preview_offset = QPoint(0, 0)
        
        for obj_id in obj_ids:
            obj = next((o for o in self.objects if o.get("id") == obj_id), None)
            if obj:
                obj_layer = obj.get("layer", "default")
                if obj_layer == self.current_layer:  # Nur Objekte im aktiven Layer
                    # Objekt kopieren (ohne ID, wird später generiert)
                    obj_copy = obj.copy()
                    self._duplicate_preview_objects.append({
                        "original": obj,
                        "copy": obj_copy,
                        "start_pos": QPoint(obj.get("x", 0), obj.get("y", 0))
                    })
        
        if self._duplicate_preview_objects:
            self._duplicate_preview_mode = True
            self.canvas.setCursor(Qt.CursorShape.CrossCursor)  # Kreuz-Cursor für Platzierung
            self.canvas.update()
    
    def _place_duplicate_preview(self):
        """Platziert die Vorschau-Objekte tatsächlich in der Szene"""
        if not self._duplicate_preview_mode or not self._duplicate_preview_objects:
            return
        
        new_objects = []
        
        for preview_data in self._duplicate_preview_objects:
            obj_copy = preview_data["copy"]
            start_pos = preview_data["start_pos"]
            offset = self._duplicate_preview_offset
            
            # Neue Position berechnen
            new_x = start_pos.x() + offset.x()
            new_y = start_pos.y() + offset.y()
            
            # An Grid ausrichten
            grid_x = (new_x // self.grid_size) * self.grid_size
            grid_y = (new_y // self.grid_size) * self.grid_size
            grid_x = int(grid_x)
            grid_y = int(grid_y)
            
            # Prüfen ob Position frei ist (gegen bestehende Objekte UND bereits hinzugefügte neue Objekte)
            # WICHTIG: Original-Objekte, die gerade dupliziert werden, ausschließen
            original_obj_ids = {preview_data["original"].get("id") for preview_data in self._duplicate_preview_objects}
            
            grid_cell_x = grid_x // self.grid_size
            grid_cell_y = grid_y // self.grid_size
            position_free = True
            
            # Prüfe gegen bestehende Objekte (aber ignoriere Original-Objekte, die gerade dupliziert werden)
            for other_obj in self.objects:
                other_id = other_obj.get("id")
                # Ignoriere Original-Objekte, die gerade dupliziert werden
                if other_id in original_obj_ids:
                    continue
                    
                other_x = other_obj.get("x", 0)
                other_y = other_obj.get("y", 0)
                other_grid_x = other_x // self.grid_size
                other_grid_y = other_y // self.grid_size
                if other_grid_x == grid_cell_x and other_grid_y == grid_cell_y:
                    position_free = False
                    break
            
            # Prüfe auch gegen bereits in dieser Runde hinzugefügte Objekte
            if position_free:
                for already_added in new_objects:
                    other_x = already_added.get("x", 0)
                    other_y = already_added.get("y", 0)
                    other_grid_x = other_x // self.grid_size
                    other_grid_y = other_y // self.grid_size
                    if other_grid_x == grid_cell_x and other_grid_y == grid_cell_y:
                        position_free = False
                        break
            
            if not position_free:
                continue  # Überspringe dieses Objekt wenn Position belegt
            
            # Neues Objekt erstellen
            new_obj = obj_copy.copy()
            new_obj["id"] = self._generate_unique_id()
            # Namen aktualisieren - wenn kein Name vorhanden, ID als Basis verwenden
            base_name = new_obj.get("name", "")
            if not base_name or not base_name.strip():
                # Wenn kein Name vorhanden, versuche einen Namen aus der ID zu generieren
                base_name = new_obj.get("id", "object")
            new_obj["name"] = self._generate_unique_name(base_name)
            new_obj["x"] = grid_x
            new_obj["y"] = grid_y
            new_obj["width"] = self.grid_size
            new_obj["height"] = self.grid_size
            
            new_objects.append(new_obj)
        
        # Objekte hinzufügen mit Undo/Redo (alle auf einmal)
        if new_objects and self.undo_redo_manager:
            from ..utils.commands import ObjectAddMultipleCommand
            command = ObjectAddMultipleCommand(
                self.objects,
                new_objects,
                lambda: (self.canvas.update(), self.save_scene())
            )
            self.undo_redo_manager.execute_command(command)
            
            self.undo_redo_changed.emit()
            
            # Auswahl auf neue Objekte setzen
            new_ids = [obj.get("id") for obj in new_objects]
            self.selected_object_ids = new_ids
            self.selected_object_id = new_ids[0] if new_ids else None
            if new_objects:
                self.object_selected.emit(new_objects[0])
        
        # Vorschau-Modus beenden
        self._duplicate_preview_mode = False
        self._duplicate_preview_objects = []
        self._duplicate_preview_offset = QPoint(0, 0)
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
        self.save_scene()
        self.canvas.update()


class CanvasWidget(QWidget):
    """Eigentliches Canvas-Widget für Zeichnen"""
    
    mouse_pressed = Signal(QPoint)
    mouse_moved = Signal(QPoint)
    mouse_released = Signal(QPoint)
    
    def __init__(self, parent: SceneCanvas):
        super().__init__()
        self.parent_canvas = parent
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)  # Drag & Drop aktivieren
        
        # Sprites cache
        self.sprite_cache: Dict[str, QPixmap] = {}
    
    def mousePressEvent(self, event):
        """Maus-Druck Event"""
        # Mittlere Maustaste für Panning
        if event.button() == Qt.MiddleButton:
            self.parent_canvas.panning = True
            self.parent_canvas.pan_start_pos = event.position().toPoint()
            return
        
        # Linke Maustaste
        if event.button() == Qt.LeftButton:
            # Wenn Duplizieren-Vorschau aktiv ist, Objekte platzieren
            if self.parent_canvas._duplicate_preview_mode:
                self.parent_canvas._place_duplicate_preview()
                return
            
            # Modifier-Tasten prüfen
            modifiers = event.modifiers()
            self.parent_canvas._mouse_modifiers = modifiers  # Für später speichern
            self.mouse_pressed.emit(event.position().toPoint())
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Rechtsklick-Menü Event"""
        # Canvas-Koordinaten in World-Koordinaten umrechnen
        # QContextMenuEvent verwendet pos() statt position()
        pos = event.pos()
        adjusted_pos = pos - self.parent_canvas.view_offset
        zoom = self.parent_canvas.zoom_factor
        world_x = int(adjusted_pos.x() / zoom)
        world_y = int(adjusted_pos.y() / zoom)
        
        # Objekt finden das angeklickt wurde
        clicked_obj = None
        tolerance = 2
        
        # Zuerst aktiven Layer prüfen
        for obj in reversed(self.parent_canvas.objects):
            obj_layer = obj.get("layer", "default")
            if obj_layer != self.parent_canvas.current_layer:
                continue
                
            obj_x = int(obj.get("x", 0))
            obj_y = int(obj.get("y", 0))
            obj_width = int(obj.get("width", 32))
            obj_height = int(obj.get("height", 32))
            
            if (obj_x - tolerance <= world_x < obj_x + obj_width + tolerance and
                obj_y - tolerance <= world_y < obj_y + obj_height + tolerance):
                clicked_obj = obj
                break
        
        # Falls nicht gefunden, andere Layer prüfen
        if clicked_obj is None:
            for obj in reversed(self.parent_canvas.objects):
                obj_layer = obj.get("layer", "default")
                if obj_layer == self.parent_canvas.current_layer:
                    continue
                    
                obj_x = int(obj.get("x", 0))
                obj_y = int(obj.get("y", 0))
                obj_width = int(obj.get("width", 32))
                obj_height = int(obj.get("height", 32))
                
                if (obj_x - tolerance <= world_x < obj_x + obj_width + tolerance and
                    obj_y - tolerance <= world_y < obj_y + obj_height + tolerance):
                    clicked_obj = obj
                    break
        
        if clicked_obj:
            # Objekt zur Auswahl hinzufügen (falls nicht bereits ausgewählt)
            clicked_obj_id = clicked_obj.get("id")
            if clicked_obj_id not in self.parent_canvas.selected_object_ids:
                self.parent_canvas.selected_object_ids = [clicked_obj_id]
                self.parent_canvas.selected_object_id = clicked_obj_id
            self.parent_canvas.object_selected.emit(clicked_obj)
            self.update()
            
            # Menü erstellen
            menu = QMenu(self)
            
            # Anzahl der ausgewählten Objekte anzeigen
            selected_count = len(self.parent_canvas.selected_object_ids)
            if selected_count > 1:
                menu.addAction(f"{selected_count} Objekte ausgewählt").setEnabled(False)
                menu.addSeparator()
            
            # Duplizieren-Option (direkt nach Separator, nahe an Maus)
            duplicate_action = menu.addAction("Duplizieren")
            duplicate_action.triggered.connect(
                lambda: self.parent_canvas._start_duplicate_preview(self.parent_canvas.selected_object_ids)
            )
            
            # Löschen-Option (direkt nach Duplizieren, nahe an Maus)
            delete_action = menu.addAction("Löschen")
            delete_action.triggered.connect(
                lambda: self.parent_canvas._delete_objects_multiple(self.parent_canvas.selected_object_ids)
            )
            
            menu.addSeparator()
            
            # Kollision-Untermenü
            # Prüfen ob alle ausgewählten Objekte Kollision haben
            all_have_collision = True
            any_has_collision = False
            for obj_id in self.parent_canvas.selected_object_ids:
                obj = next((o for o in self.parent_canvas.objects if o.get("id") == obj_id), None)
                if obj:
                    collider_data = obj.get("collider", {})
                    if collider_data.get("enabled", False):
                        any_has_collision = True
                    else:
                        all_have_collision = False
            
            collision_menu = menu.addMenu("Kollision")
            
            # Kollision hinzufügen - immer sichtbar, enabled wenn keine Kollision vorhanden
            add_collision_action = collision_menu.addAction("Kollision hinzufügen")
            if not (all_have_collision and any_has_collision):
                add_collision_action.triggered.connect(
                    lambda: self.parent_canvas._add_collider_multiple(self.parent_canvas.selected_object_ids)
                )
            else:
                add_collision_action.setEnabled(False)  # Ausgegraut wenn bereits Kollision vorhanden
            
            # Kollision entfernen - immer sichtbar, enabled wenn Kollision vorhanden
            remove_collision_action = collision_menu.addAction("Kollision entfernen")
            if all_have_collision and any_has_collision:
                remove_collision_action.triggered.connect(
                    lambda: self.parent_canvas._remove_collider_multiple(self.parent_canvas.selected_object_ids)
                )
            else:
                remove_collision_action.setEnabled(False)  # Ausgegraut wenn keine Kollision vorhanden
            
            # Separator zwischen hinzufügen/entfernen und kopieren/einfügen
            collision_menu.addSeparator()
            
            # Kollision kopieren - immer sichtbar, enabled wenn Kollision vorhanden
            copy_collision_action = collision_menu.addAction("Kollision kopieren")
            if all_have_collision and any_has_collision:
                copy_collision_action.triggered.connect(
                    lambda: self.parent_canvas._copy_collider(clicked_obj_id)
                )
            else:
                copy_collision_action.setEnabled(False)  # Ausgegraut wenn keine Kollision vorhanden
            
            # Kollision einfügen - immer sichtbar, enabled wenn etwas kopiert wurde
            paste_collision_action = collision_menu.addAction("Kollision einfügen")
            if self.parent_canvas._copied_collider is not None:
                paste_collision_action.triggered.connect(
                    lambda: self.parent_canvas._paste_collider_multiple(self.parent_canvas.selected_object_ids)
                )
            else:
                paste_collision_action.setEnabled(False)  # Ausgegraut wenn nichts kopiert wurde
            
            # Boden-Untermenü
            # Prüfen ob alle ausgewählten Objekte Boden haben
            all_have_ground = True
            any_has_ground = False
            for obj_id in self.parent_canvas.selected_object_ids:
                obj = next((o for o in self.parent_canvas.objects if o.get("id") == obj_id), None)
                if obj:
                    if obj.get("ground", False):
                        any_has_ground = True
                    else:
                        all_have_ground = False
            
            ground_menu = menu.addMenu("Boden")
            
            # Boden hinzufügen - immer sichtbar, enabled wenn kein Boden vorhanden
            add_ground_action = ground_menu.addAction("Boden hinzufügen")
            if not (all_have_ground and any_has_ground):
                add_ground_action.triggered.connect(
                    lambda: self.parent_canvas._add_ground_multiple(self.parent_canvas.selected_object_ids)
                )
            else:
                add_ground_action.setEnabled(False)  # Ausgegraut wenn bereits Boden vorhanden
            
            # Boden entfernen - immer sichtbar, enabled wenn Boden vorhanden
            remove_ground_action = ground_menu.addAction("Boden entfernen")
            if all_have_ground and any_has_ground:
                remove_ground_action.triggered.connect(
                    lambda: self.parent_canvas._remove_ground_multiple(self.parent_canvas.selected_object_ids)
                )
            else:
                remove_ground_action.setEnabled(False)  # Ausgegraut wenn kein Boden vorhanden
            
            # Menü anzeigen
            menu.exec(event.globalPos())
    
    def mouseMoveEvent(self, event):
        """Maus-Bewegung Event"""
        # Duplizieren-Vorschau aktualisieren
        if self.parent_canvas._duplicate_preview_mode:
            pos = event.position().toPoint()
            adjusted_pos = pos - self.parent_canvas.view_offset
            zoom = self.parent_canvas.zoom_factor
            world_x = int(adjusted_pos.x() / zoom)
            world_y = int(adjusted_pos.y() / zoom)
            
            # Offset berechnen (relativ zum ersten Objekt)
            if self.parent_canvas._duplicate_preview_objects:
                first_obj = self.parent_canvas._duplicate_preview_objects[0]
                start_pos = first_obj["start_pos"]
                
                # Delta berechnen
                dx = world_x - start_pos.x()
                dy = world_y - start_pos.y()
                
                # An Grid ausrichten
                grid_size = self.parent_canvas.grid_size
                grid_dx = ((dx // grid_size) * grid_size) - (dx % grid_size)
                grid_dy = ((dy // grid_size) * grid_size) - (dy % grid_size)
                
                self.parent_canvas._duplicate_preview_offset = QPoint(grid_dx, grid_dy)
                self.update()
            return
        
        # Panning mit mittlerer Maustaste
        if self.parent_canvas.panning:
            current_pos = event.position().toPoint()
            dx = current_pos.x() - self.parent_canvas.pan_start_pos.x()
            dy = current_pos.y() - self.parent_canvas.pan_start_pos.y()
            self.parent_canvas.view_offset += QPoint(dx, dy)
            self.parent_canvas.pan_start_pos = current_pos
            self.update()
            return
        
        self.mouse_moved.emit(event.position().toPoint())
    
    def mouseReleaseEvent(self, event):
        """Maus-Losgelassen Event"""
        # Panning beenden
        if event.button() == Qt.MiddleButton:
            self.parent_canvas.panning = False
            return
        
        self.mouse_released.emit(event.position().toPoint())
    
    def wheelEvent(self, event: QWheelEvent):
        """Mausrad-Event für Zoom mit Strg"""
        # Prüfen ob Strg gedrückt ist
        if event.modifiers() & Qt.ControlModifier:
            # Zoom ändern
            delta = event.angleDelta().y()
            if delta > 0:
                # Reinzoomen
                new_value = min(200, self.parent_canvas.zoom_slider.value() + 5)
            else:
                # Rauszoomen
                new_value = max(50, self.parent_canvas.zoom_slider.value() - 5)
            
            self.parent_canvas.zoom_slider.setValue(new_value)
            event.accept()
        else:
            # Standard-Verhalten (Scrollen)
            event.ignore()
    
    def dragEnterEvent(self, event):
        """Wird aufgerufen wenn etwas über das Canvas gezogen wird"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Wird aufgerufen wenn etwas auf das Canvas fallen gelassen wird"""
        if event.mimeData().hasText():
            sprite_path = event.mimeData().text()
            # Position relativ zum Canvas (mit Zoom und Panning)
            pos = event.position().toPoint()
            adjusted_pos = pos - self.parent_canvas.view_offset
            zoom = self.parent_canvas.zoom_factor
            world_x = int(adjusted_pos.x() / zoom)
            world_y = int(adjusted_pos.y() / zoom)
            
            # An Grid ausrichten (Grid-Position) - sicherstellen dass Position eindeutig ist
            grid_size = self.parent_canvas.grid_size
            grid_x = (world_x // grid_size) * grid_size
            grid_y = (world_y // grid_size) * grid_size
            
            # Sicherstellen dass Position genau auf Grid ist (keine Rundungsfehler)
            grid_x = int(grid_x)
            grid_y = int(grid_y)
            
            # Objekt im Grid zentrieren (Position = Grid-Position, Objekt ist grid_size x grid_size)
            # Die Position ist bereits die obere linke Ecke des Grid-Felds
            obj_x = grid_x
            obj_y = grid_y
            
            # Objekt hinzufügen (prüft automatisch auf Duplikate)
            self.parent_canvas.add_object_from_sprite(sprite_path, obj_x, obj_y)
            
            # Canvas sofort aktualisieren und Objekt auswählen
            self.update()
            event.acceptProposedAction()
    
    def paintEvent(self, event: QPaintEvent):
        """Zeichnet den Canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Hintergrund
        bg_color = self.parent_canvas.scene_data.get("background_color", [135, 206, 235])
        if isinstance(bg_color, list) and len(bg_color) >= 3:
            color = QColor(bg_color[0], bg_color[1], bg_color[2])
        else:
            color = QColor(135, 206, 235)
        painter.fillRect(self.rect(), color)
        
        # Panning-Offset anwenden
        offset = self.parent_canvas.view_offset
        painter.translate(offset.x(), offset.y())
        
        # Raster ZUERST zeichnen (vor Zoom)
        self._draw_grid(painter)
        
        # Zoom-Transform
        zoom = self.parent_canvas.zoom_factor
        painter.scale(zoom, zoom)
        
        # Zuerst Objekte aus anderen Layern grau-transparent zeichnen (Ghost-Ansicht)
        current_layer = self.parent_canvas.current_layer
        for obj in self.parent_canvas.objects:
            obj_layer = obj.get("layer", "default")  # Rückwärtskompatibilität
            if obj_layer != current_layer:
                self._draw_object_ghost(painter, obj)
        
        # Dann Objekte des aktiven Layers normal zeichnen
        for obj in self.parent_canvas.objects:
            obj_layer = obj.get("layer", "default")  # Rückwärtskompatibilität
            if obj_layer == current_layer:
                self._draw_object(painter, obj)
        
        # Kollisionsboxen für alle Objekte im aktiven Layer zeichnen
        for obj in self.parent_canvas.objects:
            obj_layer = obj.get("layer", "default")
            if obj_layer == current_layer:
                collider_data = obj.get("collider", {})
                if collider_data.get("enabled", False):
                    self._draw_collider(painter, obj)
                # Ground-Markierung zeichnen
                if obj.get("ground", False):
                    self._draw_ground_marker(painter, obj)
        
        # Selektion hervorheben (Mehrfachauswahl)
        for obj_id in self.parent_canvas.selected_object_ids:
            for obj in self.parent_canvas.objects:
                if obj.get("id") == obj_id:
                    obj_layer = obj.get("layer", "default")
                    if obj_layer == current_layer:
                        self._draw_selection(painter, obj)
                    break
        
        # Duplizieren-Vorschau zeichnen
        if self.parent_canvas._duplicate_preview_mode and self.parent_canvas._duplicate_preview_objects:
            for preview_data in self.parent_canvas._duplicate_preview_objects:
                obj_copy = preview_data["copy"]
                start_pos = preview_data["start_pos"]
                offset = self.parent_canvas._duplicate_preview_offset
                
                # Neue Position berechnen
                new_x = start_pos.x() + offset.x()
                new_y = start_pos.y() + offset.y()
                
                # An Grid ausrichten
                grid_size = self.parent_canvas.grid_size
                grid_x = (new_x // grid_size) * grid_size
                grid_y = (new_y // grid_size) * grid_size
                grid_x = int(grid_x)
                grid_y = int(grid_y)
                
                # Vorschau-Objekt zeichnen (halbtransparent)
                obj_copy["x"] = grid_x
                obj_copy["y"] = grid_y
                self._draw_object_preview(painter, obj_copy)
                
                # Grid-Feld hervorheben
                self._draw_grid_highlight(painter, grid_x, grid_y, grid_size)
        
        # Duplizieren-Vorschau zeichnen
        if self.parent_canvas._duplicate_preview_mode and self.parent_canvas._duplicate_preview_objects:
            for preview_data in self.parent_canvas._duplicate_preview_objects:
                obj_copy = preview_data["copy"]
                start_pos = preview_data["start_pos"]
                offset = self.parent_canvas._duplicate_preview_offset
                
                # Neue Position berechnen
                new_x = start_pos.x() + offset.x()
                new_y = start_pos.y() + offset.y()
                
                # An Grid ausrichten
                grid_size = self.parent_canvas.grid_size
                grid_x = (new_x // grid_size) * grid_size
                grid_y = (new_y // grid_size) * grid_size
                grid_x = int(grid_x)
                grid_y = int(grid_y)
                
                # Vorschau-Objekt zeichnen (halbtransparent)
                obj_copy["x"] = grid_x
                obj_copy["y"] = grid_y
                self._draw_object_preview(painter, obj_copy)
                
                # Grid-Feld hervorheben
                self._draw_grid_highlight(painter, grid_x, grid_y, grid_size)
    
    def _draw_object(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet ein Objekt"""
        x = int(obj.get("x", 0))
        y = int(obj.get("y", 0))
        width = int(obj.get("width", 32))
        height = int(obj.get("height", 32))
        
        # Dezente Hervorhebung (wenn aktiviert)
        if self.parent_canvas.show_highlights:
            # Leicht transparentes hellblaues Rechteck
            highlight_color = QColor(192, 224, 240, 80)  # Dezentes Hellblau, 80 Alpha
            painter.setPen(QPen(QColor(192, 224, 240, 120), 1))
            painter.setBrush(QBrush(highlight_color))
            painter.drawRect(x, y, width, height)
        
        # Sprite laden
        sprite_path = obj.get("sprite")
        if sprite_path and self.parent_canvas.project_path:
            try:
                # Pfad normalisieren (kann absolut oder relativ sein)
                sprite_path_obj = Path(sprite_path)
                if sprite_path_obj.is_absolute():
                    full_path = sprite_path_obj
                else:
                    full_path = self.parent_canvas.project_path / sprite_path
                
                # Pfad-Separatoren normalisieren für Cache-Key
                cache_key = str(sprite_path).replace("\\", "/")
                
                if full_path.exists() and full_path.is_file():
                    if cache_key not in self.sprite_cache:
                        pixmap = QPixmap(str(full_path))
                        if not pixmap.isNull():
                            # Immer auf die Projekteinstellungs-Größe skalieren
                            target_size = self.parent_canvas.grid_size
                            pixmap = pixmap.scaled(target_size, target_size, 
                                                 Qt.AspectRatioMode.IgnoreAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
                            self.sprite_cache[cache_key] = pixmap
                    
                    if cache_key in self.sprite_cache:
                        painter.drawPixmap(x, y, width, height, self.sprite_cache[cache_key])
                        # Label zeichnen (wenn aktiviert)
                        if self.parent_canvas.show_labels:
                            self._draw_label(painter, obj, x, y, width, height)
                        return
            except Exception as e:
                # Fehler beim Laden des Sprites - Fallback verwenden
                pass
        
        # Fallback: Rechteck
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
        painter.drawRect(x, y, width, height)
        
        # Label zeichnen (wenn aktiviert)
        if self.parent_canvas.show_labels:
            self._draw_label(painter, obj, x, y, width, height)
    
    def _draw_collider(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet die Kollisionsbox als rote Box"""
        collider_data = obj.get("collider", {})
        if not collider_data.get("enabled", False):
            return
        
        # Objekt-Position
        obj_x = int(obj.get("x", 0))
        obj_y = int(obj.get("y", 0))
        
        # Kollisionsbox-Position RELATIV zum Objekt (Offset)
        # Falls alte absolute Position vorhanden (für Rückwärtskompatibilität), umrechnen
        if "x" in collider_data and "y" in collider_data:
            # Alte absolute Position - in relative umrechnen
            old_collider_x = int(collider_data.get("x", obj_x))
            old_collider_y = int(collider_data.get("y", obj_y))
            offset_x = old_collider_x - obj_x
            offset_y = old_collider_y - obj_y
            # Alte absolute Werte entfernen
            if "x" in collider_data:
                del collider_data["x"]
            if "y" in collider_data:
                del collider_data["y"]
            # Relative Werte setzen
            collider_data["offset_x"] = max(0, min(offset_x, self.parent_canvas.grid_size - 1))
            collider_data["offset_y"] = max(0, min(offset_y, self.parent_canvas.grid_size - 1))
        
        # Relative Position (Offset) vom Objekt
        offset_x = int(collider_data.get("offset_x", 0))
        offset_y = int(collider_data.get("offset_y", 0))
        collider_width = int(collider_data.get("width", obj.get("width", 32)))
        collider_height = int(collider_data.get("height", obj.get("height", 32)))
        
        # Absolute Position berechnen (Objekt-Position + Offset)
        collider_x = obj_x + offset_x
        collider_y = obj_y + offset_y
        
        # Sicherstellen dass Kollisionsbox innerhalb des Grid-Feldes bleibt
        # (sollte bereits durch offset_x/offset_y sichergestellt sein, aber zur Sicherheit)
        max_offset_x = self.parent_canvas.grid_size - collider_width
        max_offset_y = self.parent_canvas.grid_size - collider_height
        offset_x = max(0, min(offset_x, max_offset_x))
        offset_y = max(0, min(offset_y, max_offset_y))
        collider_x = obj_x + offset_x
        collider_y = obj_y + offset_y
        
        # Rote Box für Kollisionsbox zeichnen
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 30)))  # Leicht transparentes Rot
        painter.drawRect(collider_x, collider_y, collider_width, collider_height)
    
    def _draw_ground_marker(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet eine grüne Markierung am unteren Rand für Ground-Tiles"""
        x = int(obj.get("x", 0))
        y = int(obj.get("y", 0))
        width = int(obj.get("width", 32))
        height = int(obj.get("height", 32))
        
        # Grüne Linie am unteren Rand des Objekts
        bottom_y = y + height
        painter.setPen(QPen(QColor(0, 255, 0), 3))  # Grüne Linie, 3px dick
        painter.drawLine(x, bottom_y, x + width, bottom_y)
        
        # Optional: Grüne Markierung in der oberen linken Ecke
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))  # Leicht transparentes Grün
        marker_size = 8
        painter.drawEllipse(x + 2, y + 2, marker_size, marker_size)
    
    def _draw_label(self, painter: QPainter, obj: Dict[str, Any], x: int, y: int, width: int, height: int):
        """Zeichnet das Label (Name oder ID) über dem Objekt"""
        # Name oder ID bestimmen
        display_name = obj.get("name") or obj.get("id", "unknown")
        
        # Text mit Hintergrund für bessere Lesbarkeit
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # Text-Metriken
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(display_name)
        text_height = metrics.height()
        
        # Hintergrund für Text (halbtransparentes Weiß)
        bg_rect = QRect(x + 2, y + 2, min(text_width + 4, width - 4), text_height + 2)
        painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
        painter.drawRect(bg_rect)
        
        # Text zeichnen
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(x + 4, y + text_height + 2, display_name)
    
    def _draw_object_ghost(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet ein Objekt aus einem anderen Layer grau-transparent (Ghost-Ansicht)"""
        x = int(obj.get("x", 0))
        y = int(obj.get("y", 0))
        width = int(obj.get("width", 32))
        height = int(obj.get("height", 32))
        
        # Sprite laden und grau-transparent machen
        sprite_path = obj.get("sprite")
        if sprite_path and self.parent_canvas.project_path:
            try:
                # Pfad normalisieren (kann absolut oder relativ sein)
                sprite_path_obj = Path(sprite_path)
                if sprite_path_obj.is_absolute():
                    full_path = sprite_path_obj
                else:
                    full_path = self.parent_canvas.project_path / sprite_path
                
                # Pfad-Separatoren normalisieren für Cache-Key
                cache_key = str(sprite_path).replace("\\", "/")
                
                if full_path.exists() and full_path.is_file():
                    # Sprite laden (aus Cache oder neu)
                    if cache_key not in self.sprite_cache:
                        pixmap = QPixmap(str(full_path))
                        if not pixmap.isNull():
                            # Immer auf die Projekteinstellungs-Größe skalieren
                            target_size = self.parent_canvas.grid_size
                            pixmap = pixmap.scaled(target_size, target_size, 
                                                 Qt.AspectRatioMode.IgnoreAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
                            self.sprite_cache[cache_key] = pixmap
                    
                    if cache_key in self.sprite_cache:
                        # Grau-transparente Version zeichnen
                        painter.setOpacity(0.35)  # 35% Opazität
                        # Sprite zeichnen
                        painter.drawPixmap(x, y, width, height, self.sprite_cache[cache_key])
                        # Graues Overlay für Graustufen-Effekt
                        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
                        gray_overlay = QPixmap(width, height)
                        gray_overlay.fill(QColor(128, 128, 128, 200))
                        painter.drawPixmap(x, y, gray_overlay)
                        painter.setOpacity(1.0)  # Zurücksetzen
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        return
            except Exception:
                # Fehler beim Laden - Fallback verwenden
                # Opacity und CompositionMode zurücksetzen falls gesetzt
                painter.setOpacity(1.0)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                pass
        
        # Fallback: Grau-transparentes Rechteck
        painter.setOpacity(0.3)
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        painter.setBrush(QBrush(QColor(128, 128, 128, 50)))
        painter.drawRect(x, y, width, height)
        painter.setOpacity(1.0)
    
    def _draw_selection(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet Selektion-Highlight"""
        x = int(obj.get("x", 0))
        y = int(obj.get("y", 0))
        width = int(obj.get("width", 32))
        height = int(obj.get("height", 32))
        
        painter.setPen(QPen(QColor(255, 255, 0), 3))
        painter.setBrush(QBrush(QColor(255, 255, 0, 50)))
        painter.drawRect(x - 2, y - 2, width + 4, height + 4)
    
    def _draw_object_preview(self, painter: QPainter, obj: Dict[str, Any]):
        """Zeichnet ein Objekt als Vorschau (halbtransparent)"""
        x = int(obj.get("x", 0))
        y = int(obj.get("y", 0))
        width = int(obj.get("width", 32))
        height = int(obj.get("height", 32))
        
        sprite_path = obj.get("sprite")
        if sprite_path and self.parent_canvas.project_path:
            try:
                sprite_path_obj = Path(sprite_path)
                if sprite_path_obj.is_absolute():
                    full_path = sprite_path_obj
                else:
                    full_path = self.parent_canvas.project_path / sprite_path
                
                cache_key = str(sprite_path).replace("\\", "/")
                
                if full_path.exists() and full_path.is_file():
                    if cache_key not in self.sprite_cache:
                        pixmap = QPixmap(str(full_path))
                        if not pixmap.isNull():
                            target_size = self.parent_canvas.grid_size
                            pixmap = pixmap.scaled(target_size, target_size, 
                                                 Qt.AspectRatioMode.IgnoreAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
                            self.sprite_cache[cache_key] = pixmap
                    
                    if cache_key in self.sprite_cache:
                        # Halbtransparentes Pixmap zeichnen
                        pixmap = self.sprite_cache[cache_key]
                        painter.setOpacity(0.5)  # 50% Transparenz
                        painter.drawPixmap(x, y, width, height, pixmap)
                        painter.setOpacity(1.0)  # Zurücksetzen
                        return
            except Exception:
                pass
        
        # Fallback: Halbtransparentes Rechteck
        painter.setOpacity(0.5)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
        painter.drawRect(x, y, width, height)
        painter.setOpacity(1.0)
    
    def _draw_grid_highlight(self, painter: QPainter, grid_x: int, grid_y: int, grid_size: int):
        """Zeichnet eine Hervorhebung für ein Grid-Feld"""
        # Grüne Umrandung für Grid-Feld
        painter.setPen(QPen(QColor(0, 255, 0), 2))  # Grün
        painter.setBrush(QBrush(QColor(0, 255, 0, 30)))  # Leicht transparentes Grün
        painter.drawRect(grid_x, grid_y, grid_size, grid_size)
    
    def _draw_grid(self, painter: QPainter):
        """Zeichnet ein Raster (einstellbare Größe)"""
        grid_size = self.parent_canvas.grid_size
        zoom = self.parent_canvas.zoom_factor
        effective_grid = grid_size * zoom
        
        # Nur zeichnen wenn Grid groß genug ist
        if effective_grid < 2:
            return
        
        # Grid-Farbe verwenden
        grid_color = self.parent_canvas.grid_color
        painter.setPen(QPen(grid_color, 1))
        
        # Viewport-Bereich berechnen (mit Panning-Offset)
        offset = self.parent_canvas.view_offset
        view_x = -offset.x() / zoom
        view_y = -offset.y() / zoom
        view_width = self.width() / zoom
        view_height = self.height() / zoom
        
        # Start-Position für Grid (an Grid ausrichten)
        start_x = (int(view_x) // grid_size) * grid_size
        start_y = (int(view_y) // grid_size) * grid_size
        
        # Vertikale Linien
        x = start_x
        while x < view_x + view_width:
            painter.drawLine(int(x * zoom), int(view_y * zoom), 
                           int(x * zoom), int((view_y + view_height) * zoom))
            x += grid_size
        
        # Horizontale Linien
        y = start_y
        while y < view_y + view_height:
            painter.drawLine(int(view_x * zoom), int(y * zoom), 
                           int((view_x + view_width) * zoom), int(y * zoom))
            y += grid_size