"""
Inspector - Zeigt und bearbeitet Eigenschaften des selektierten Objekts
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                                QSpinBox, QFormLayout, QGroupBox, QComboBox, QHBoxLayout, QGridLayout, QScrollArea, QToolBar, QToolButton, QCheckBox)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from pathlib import Path
from typing import Optional, Dict, Any


class Inspector(QWidget):
    """Inspector-Panel für Objekt-Eigenschaften"""
    
    sprite_changed = Signal()  # Signal wenn Sprite geändert wurde
    object_changed = Signal()  # Signal wenn Objekt-Eigenschaften geändert wurden
    object_deleted = Signal(str)  # Signal wenn Objekt gelöscht wurde (mit Objekt-ID)
    object_created = Signal()  # Signal wenn ein neues leeres Objekt erstellt werden soll
    
    def __init__(self):
        super().__init__()
        self.current_object: Optional[Dict[str, Any]] = None
        self.current_object_id: Optional[str] = None  # ID des aktuellen Objekts
        self.project_path: Optional[Path] = None
        self.grid_size: int = 16  # Standard-Grid-Größe
        self.scene_canvas = None  # Wird vom main_window gesetzt
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        # Dark-Mode für Inspector
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 5)  # Weniger Abstand oben (2 statt 5)
        layout.setSpacing(3)  # Weniger Spacing
        
        # Titel mit Status-Anzeige
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("Inspector")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 3px; color: #d4d4d4;")
        title_layout.addWidget(self.title_label)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #d4d4d4; font-size: 9pt; padding: 3px;")
        title_layout.addStretch()
        title_layout.addWidget(self.status_label)
        
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        layout.addWidget(title_widget)
        
        # Werkzeugleiste mit Add- und Lösch-Button
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        
        # Plus-Button zum Hinzufügen einer leeren Entität (Dark-Mode)
        self.add_button = QToolButton()
        self.add_button.setText("+")
        self.add_button.setToolTip("Neue leere Entität hinzufügen")
        self.add_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #3d3d3d;
                padding: 3px;
                font-size: 16pt;
                font-weight: bold;
                color: #4CAF50;
                background-color: #2d2d2d;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #3d3d3d;
                border-color: #4CAF50;
            }
        """)
        self.add_button.clicked.connect(self._create_new_object)
        toolbar.addWidget(self.add_button)
        
        # Papierkorb-Button zum Löschen (Dark-Mode)
        self.delete_button = QToolButton()
        self.delete_button.setText("🗑")
        self.delete_button.setToolTip("Objekt löschen")
        self.delete_button.setEnabled(False)  # Standardmäßig deaktiviert
        self.delete_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #3d3d3d;
                padding: 3px;
                font-size: 14pt;
                background-color: #2d2d2d;
                border-radius: 3px;
            }
            QToolButton:enabled {
                color: #f44336;
            }
            QToolButton:disabled {
                color: #757575;
                border-color: #2d2d2d;
            }
            QToolButton:enabled:hover {
                background-color: #3d3d3d;
                border-color: #f44336;
            }
        """)
        self.delete_button.clicked.connect(self._delete_object)
        toolbar.addWidget(self.delete_button)
        
        layout.addWidget(toolbar)
        
        # ScrollArea für Formular-Inhalt
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Formular-Gruppe (kompakt) - Dark-Mode
        form_group = QGroupBox("Objekt-Eigenschaften")
        form_group.setObjectName("Objekt-Eigenschaften")  # Für Styling
        form_group.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #d4d4d4;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 3px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
            QSpinBox {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 3px;
            }
            QSpinBox:focus {
                border-color: #4a9eff;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 3px;
            }
            QComboBox:focus {
                border-color: #4a9eff;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #2d2d2d;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #d4d4d4;
            }
        """)
        form_layout = QGridLayout()
        form_layout.setSpacing(3)  # Weniger Spacing
        form_layout.setContentsMargins(5, 5, 5, 5)  # Weniger Abstand oben
        
        row = 0
        
        # ID (nur anzeigen)
        form_layout.addWidget(QLabel("ID:"), row, 0)
        self.id_label = QLabel("-")
        form_layout.addWidget(self.id_label, row, 1, 1, 2)
        row += 1
        
        # Name (editierbar)
        form_layout.addWidget(QLabel("Name:"), row, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("(ID wird verwendet)")
        self.name_edit.textChanged.connect(self._on_name_changed)
        form_layout.addWidget(self.name_edit, row, 1, 1, 2)
        row += 1
        
        # Position X und Y nebeneinander
        form_layout.addWidget(QLabel("Grid X:"), row, 0)
        self.x_spinbox = QSpinBox()
        self.x_spinbox.setRange(-1000, 1000)
        self.x_spinbox.valueChanged.connect(self._on_x_changed)
        form_layout.addWidget(self.x_spinbox, row, 1)
        
        form_layout.addWidget(QLabel("Grid Y:"), row, 2)
        self.y_spinbox = QSpinBox()
        self.y_spinbox.setRange(-1000, 1000)
        self.y_spinbox.valueChanged.connect(self._on_y_changed)
        form_layout.addWidget(self.y_spinbox, row, 3)
        row += 1
        
        # Breite und Höhe nebeneinander
        form_layout.addWidget(QLabel("Breite:"), row, 0)
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 2000)
        self.width_spinbox.valueChanged.connect(self._on_width_changed)
        form_layout.addWidget(self.width_spinbox, row, 1)
        
        form_layout.addWidget(QLabel("Höhe:"), row, 2)
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 2000)
        self.height_spinbox.valueChanged.connect(self._on_height_changed)
        form_layout.addWidget(self.height_spinbox, row, 3)
        row += 1
        
        # Sprite (Dropdown + Drag & Drop)
        form_layout.addWidget(QLabel("Sprite:"), row, 0)
        sprite_layout = QHBoxLayout()
        sprite_layout.setSpacing(3)
        self.sprite_combo = QComboBox()
        self.sprite_combo.currentIndexChanged.connect(self._on_sprite_changed)
        self.sprite_combo.setAcceptDrops(True)  # Drag & Drop aktivieren
        # Drag & Drop Events für ComboBox
        self.sprite_combo.dragEnterEvent = self._drag_enter_event
        self.sprite_combo.dropEvent = self._drop_event
        self._updating_sprite = False  # Flag um Rekursion zu vermeiden
        sprite_layout.addWidget(self.sprite_combo)
        
        # Drag & Drop Label (Icon)
        drop_label = QLabel("📥")
        drop_label.setToolTip("Ziehen Sie ein Sprite aus dem Asset Browser hierher")
        drop_label.setAcceptDrops(True)
        drop_label.setStyleSheet("font-size: 14pt; padding: 3px; border: 2px dashed #ccc;")
        drop_label.dragEnterEvent = self._drag_enter_event
        drop_label.dropEvent = self._drop_event
        sprite_layout.addWidget(drop_label)
        
        sprite_widget = QWidget()
        sprite_widget.setLayout(sprite_layout)
        form_layout.addWidget(sprite_widget, row, 1, 1, 3)
        
        form_group.setLayout(form_layout)
        
        # Formular-Gruppe in ScrollArea setzen
        scroll_area.setWidget(form_group)
        layout.addWidget(scroll_area)
        
        # Kollisionsbox-Gruppe (nur sichtbar wenn Kollision aktiviert)
        collider_group = QGroupBox("Kollisionsbox")
        collider_group.setObjectName("Kollisionsbox")
        collider_group.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QCheckBox {
                color: #d4d4d4;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border-color: #3a8eef;
            }
        """)
        collider_layout = QGridLayout()
        collider_layout.setSpacing(3)
        collider_layout.setContentsMargins(5, 5, 5, 5)
        
        collider_row = 0
        
        # Kollision aktivieren Checkbox
        self.collider_enabled_checkbox = QCheckBox("Kollision aktivieren")
        self.collider_enabled_checkbox.stateChanged.connect(self._on_collider_enabled_changed)
        collider_layout.addWidget(self.collider_enabled_checkbox, collider_row, 0, 1, 2)
        collider_row += 1
        
        # Kollisionsbox X und Y Offset (relativ zum Objektmittelpunkt)
        self.collider_x_label = QLabel("Kollisionsbox X Offset (px):")
        self.collider_x_label.setVisible(False)
        collider_layout.addWidget(self.collider_x_label, collider_row, 0)
        self.collider_x_spinbox = QSpinBox()
        self.collider_x_spinbox.setRange(-10000, 10000)  # Größerer Bereich für Pixel-Offsets
        self.collider_x_spinbox.setSingleStep(1)  # 1 Pixel pro Schritt (Pfeiltasten)
        self.collider_x_spinbox.setVisible(False)
        self.collider_x_spinbox.valueChanged.connect(self._on_collider_x_changed)
        collider_layout.addWidget(self.collider_x_spinbox, collider_row, 1)
        
        self.collider_y_label = QLabel("Kollisionsbox Y Offset (px):")
        self.collider_y_label.setVisible(False)
        collider_layout.addWidget(self.collider_y_label, collider_row, 2)
        self.collider_y_spinbox = QSpinBox()
        self.collider_y_spinbox.setRange(-10000, 10000)  # Größerer Bereich für Pixel-Offsets
        self.collider_y_spinbox.setSingleStep(1)  # 1 Pixel pro Schritt (Pfeiltasten)
        self.collider_y_spinbox.setVisible(False)
        self.collider_y_spinbox.valueChanged.connect(self._on_collider_y_changed)
        collider_layout.addWidget(self.collider_y_spinbox, collider_row, 3)
        collider_row += 1
        
        # Kollisionsbox Breite und Höhe (nur sichtbar wenn aktiviert)
        self.collider_width_label = QLabel("Kollisionsbox Breite:")
        self.collider_width_label.setVisible(False)
        collider_layout.addWidget(self.collider_width_label, collider_row, 0)
        self.collider_width_spinbox = QSpinBox()
        self.collider_width_spinbox.setRange(1, 2000)
        self.collider_width_spinbox.setVisible(False)
        self.collider_width_spinbox.valueChanged.connect(self._on_collider_width_changed)
        collider_layout.addWidget(self.collider_width_spinbox, collider_row, 1)
        
        self.collider_height_label = QLabel("Kollisionsbox Höhe:")
        self.collider_height_label.setVisible(False)
        collider_layout.addWidget(self.collider_height_label, collider_row, 2)
        self.collider_height_spinbox = QSpinBox()
        self.collider_height_spinbox.setRange(1, 2000)
        self.collider_height_spinbox.setVisible(False)
        self.collider_height_spinbox.valueChanged.connect(self._on_collider_height_changed)
        collider_layout.addWidget(self.collider_height_spinbox, collider_row, 3)
        
        collider_group.setLayout(collider_layout)
        self.collider_group = collider_group
        layout.addWidget(collider_group)
        
        # Ground-Checkbox (einfach, unter der Kollisionsbox)
        self.ground_checkbox = QCheckBox("Ground (Boden-Tile)")
        self.ground_checkbox.setStyleSheet("""
            QCheckBox {
                color: #d4d4d4;
                padding: 5px;
                margin-top: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border-color: #3a8eef;
            }
        """)
        self.ground_checkbox.stateChanged.connect(self._on_ground_changed)
        layout.addWidget(self.ground_checkbox)
        
        self.setLayout(layout)
        
        # Standard: Kein Objekt ausgewählt
        self._clear_fields()
    
    def load_project(self, project_path: Path):
        """Lädt Projekt (für Sprite-Liste)"""
        self.project_path = project_path
        
        # Grid-Größe aus project.json laden
        self._load_grid_size()
        
        # Sprite-Liste laden
        self._load_sprites()
    
    def _load_grid_size(self):
        """Lädt Grid-Größe aus project.json"""
        if not self.project_path:
            return
        
        project_file = self.project_path / "project.json"
        if project_file.exists():
            try:
                import json
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
                
                # Debug: Grid-Größe prüfen
                print(f"[Inspector] Grid-Größe geladen: {self.grid_size}")
            except Exception as e:
                print(f"[Inspector] Fehler beim Laden der Grid-Größe: {e}")
                pass  # Standard-Wert beibehalten
    
    def _load_sprites(self):
        """Lädt verfügbare Sprites aus assets/images (rekursiv)"""
        if not self.project_path:
            return
        
        self.sprite_combo.clear()
        self.sprite_combo.addItem("- Kein Sprite -", "")
        
        images_dir = self.project_path / "assets" / "images"
        if images_dir.exists():
            # Rekursiv alle Bilddateien finden
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            for img_file in sorted(images_dir.rglob("*")):
                if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                    # Relativen Pfad erzeugen (für Data)
                    relative_path = img_file.relative_to(self.project_path)
                    relative_path_str = str(relative_path).replace("\\", "/")
                    # Nur Dateiname für Anzeige
                    display_name = img_file.name
                    self.sprite_combo.addItem(display_name, relative_path_str)
    
    def set_scene_canvas(self, scene_canvas):
        """Setzt die Referenz zum SceneCanvas"""
        self.scene_canvas = scene_canvas
    
    def on_object_selected(self, obj_data: Dict[str, Any]):
        """Wird aufgerufen wenn ein Objekt im Canvas ausgewählt wird"""
        if obj_data and obj_data.get("id"):
            # Objekt ausgewählt - obj_data sollte bereits eine Referenz sein
            # Aber zur Sicherheit: Wenn wir ein scene_canvas haben, können wir das Objekt
            # aus dem objects Array holen, um sicherzustellen, dass es eine Referenz ist
            obj_id = obj_data.get("id")
            self.current_object_id = obj_id
            
            # Objekt aus Canvas-Array holen, um sicherzustellen, dass es eine Referenz ist
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == obj_id:
                        self.current_object = obj
                        break
                else:
                    # Objekt nicht gefunden - verwende obj_data als Fallback
                    self.current_object = obj_data
            else:
                self.current_object = obj_data
            
            self._update_fields()
            self._show_selected()
            # Lösch-Button aktivieren
            if hasattr(self, 'delete_button'):
                self.delete_button.setEnabled(True)
        else:
            # Kein Objekt ausgewählt
            self.current_object = None
            self.current_object_id = None
            self._clear_fields()
            self._show_no_selection()
            # Lösch-Button deaktivieren
            if hasattr(self, 'delete_button'):
                self.delete_button.setEnabled(False)
    
    def _update_fields(self):
        """Aktualisiert die Felder mit aktuellen Objekt-Daten"""
        if not self.current_object:
            self._clear_fields()
            return
        
        # ID
        self.id_label.setText(self.current_object.get("id", "-"))
        
        # Name (Signale temporär blockieren)
        self.name_edit.blockSignals(True)
        self.name_edit.setText(self.current_object.get("name", ""))
        self.name_edit.blockSignals(False)
        
        # Kollisionsbox (Signale temporär blockieren)
        collider_data = self.current_object.get("collider", {})
        collider_enabled = collider_data.get("enabled", False)
        self.collider_enabled_checkbox.blockSignals(True)
        self.collider_enabled_checkbox.setChecked(collider_enabled)
        self.collider_enabled_checkbox.blockSignals(False)
        self._update_collider_visibility(collider_enabled)
        
        if collider_enabled:
            # Kollisionsbox-Daten laden
            # Position als Offset vom Objektmittelpunkt berechnen
            obj_x = self.current_object.get("x", 0)
            obj_y = self.current_object.get("y", 0)
            obj_width = self.current_object.get("width", 32)
            obj_height = self.current_object.get("height", 32)
            obj_center_x = obj_x + obj_width / 2
            obj_center_y = obj_y + obj_height / 2
            
            # Absolute Position der Kollisionsbox (falls vorhanden)
            collider_abs_x = collider_data.get("x", obj_center_x)
            collider_abs_y = collider_data.get("y", obj_center_y)
            
            # Offset berechnen (relativ zum Objektmittelpunkt)
            collider_offset_x = collider_abs_x - obj_center_x
            collider_offset_y = collider_abs_y - obj_center_y
            
            collider_width = collider_data.get("width", self.current_object.get("width", 32))
            collider_height = collider_data.get("height", self.current_object.get("height", 32))
            
            # Offset-Werte in SpinBoxen setzen
            self.collider_x_spinbox.blockSignals(True)
            self.collider_x_spinbox.setValue(int(collider_offset_x))
            self.collider_x_spinbox.blockSignals(False)
            
            self.collider_y_spinbox.blockSignals(True)
            self.collider_y_spinbox.setValue(int(collider_offset_y))
            self.collider_y_spinbox.blockSignals(False)
            
            self.collider_width_spinbox.blockSignals(True)
            self.collider_width_spinbox.setValue(int(collider_width))
            self.collider_width_spinbox.blockSignals(False)
            
            self.collider_height_spinbox.blockSignals(True)
            self.collider_height_spinbox.setValue(int(collider_height))
            self.collider_height_spinbox.blockSignals(False)
        
        # Ground (Signale temporär blockieren)
        self.ground_checkbox.blockSignals(True)
        self.ground_checkbox.setChecked(self.current_object.get("ground", False))
        self.ground_checkbox.blockSignals(False)
        
        # Position (Signale temporär blockieren)
        self.x_spinbox.blockSignals(True)
        self.y_spinbox.blockSignals(True)
        self.width_spinbox.blockSignals(True)
        self.height_spinbox.blockSignals(True)
        
        # Pixel-Koordinaten in Grid-Koordinaten umrechnen
        pixel_x = int(self.current_object.get("x", 0))
        pixel_y = int(self.current_object.get("y", 0))
        grid_x = pixel_x // self.grid_size if self.grid_size > 0 else 0
        grid_y = pixel_y // self.grid_size if self.grid_size > 0 else 0
        
        self.x_spinbox.setValue(grid_x)
        self.y_spinbox.setValue(grid_y)
        self.width_spinbox.setValue(int(self.current_object.get("width", 32)))
        self.height_spinbox.setValue(int(self.current_object.get("height", 32)))
        
        self.x_spinbox.blockSignals(False)
        self.y_spinbox.blockSignals(False)
        self.width_spinbox.blockSignals(False)
        self.height_spinbox.blockSignals(False)
        
        # Sprite (mit Flag um Signal zu blockieren)
        self._updating_sprite = True
        sprite_path = self.current_object.get("sprite", "")
        if sprite_path:
            # Pfad normalisieren (Backslashes zu Forward slashes)
            sprite_path_normalized = str(sprite_path).replace("\\", "/")
            
            # Wenn absoluter Pfad, in relativen Pfad umwandeln
            if self.project_path:
                try:
                    sprite_path_obj = Path(sprite_path_normalized)
                    if sprite_path_obj.is_absolute():
                        # Versuche relativ zum Projekt-Pfad zu machen
                        try:
                            relative_path = sprite_path_obj.relative_to(self.project_path)
                            sprite_path_normalized = str(relative_path).replace("\\", "/")
                        except ValueError:
                            # Pfad liegt außerhalb des Projekts - versuche trotzdem zu finden
                            pass
                except Exception:
                    pass  # Falls Path-Konstruktion fehlschlägt
            
            # Versuchen den Sprite in der ComboBox zu finden
            index = -1
            # Zuerst exakte Suche
            for i in range(self.sprite_combo.count()):
                combo_data = self.sprite_combo.itemData(i)
                if combo_data:
                    combo_data_normalized = str(combo_data).replace("\\", "/")
                    if combo_data_normalized == sprite_path_normalized:
                        index = i
                        break
            
            if index >= 0:
                self.sprite_combo.setCurrentIndex(index)
            else:
                # Sprite nicht gefunden - auf "Kein Sprite" setzen
                # (Debug-Ausgabe entfernt, da sie zu häufig erscheint)
                self.sprite_combo.setCurrentIndex(0)
                # Sprite-Pfad im Objekt auf relativen Pfad korrigieren (falls möglich)
                if self.project_path and sprite_path_normalized:
                    # Versuche den Pfad zu korrigieren, wenn er absolut war
                    try:
                        sprite_path_obj = Path(sprite_path_normalized)
                        if sprite_path_obj.is_absolute():
                            try:
                                relative_path = sprite_path_obj.relative_to(self.project_path)
                                self.current_object["sprite"] = str(relative_path).replace("\\", "/")
                            except ValueError:
                                pass  # Kann nicht relativ gemacht werden
                    except Exception:
                        pass
        else:
            self.sprite_combo.setCurrentIndex(0)
        self._updating_sprite = False
        
        # Visuelle Hervorhebung
        self._show_selected()
    
    def _clear_fields(self):
        """Leert alle Felder"""
        self.id_label.setText("-")
        self.name_edit.setText("")
        self.x_spinbox.setValue(0)
        self.y_spinbox.setValue(0)
        self.width_spinbox.setValue(32)
        self.height_spinbox.setValue(32)
        self.sprite_combo.setCurrentIndex(0)
        
        # Kollisionsbox-Felder
        self.collider_enabled_checkbox.setChecked(False)
        self._update_collider_visibility(False)
        self.collider_x_spinbox.setValue(0)
        self.collider_y_spinbox.setValue(0)
        self.collider_width_spinbox.setValue(32)
        self.collider_height_spinbox.setValue(32)
        
        # Ground
        self.ground_checkbox.setChecked(False)
    
    def _create_new_object(self):
        """Erstellt ein neues leeres Objekt"""
        # Signal emittieren, damit ein neues Objekt im Canvas erstellt wird
        self.object_created.emit()
    
    def _delete_object(self):
        """Löscht das aktuell ausgewählte Objekt"""
        if self.current_object:
            obj_id = self.current_object.get("id")
            if obj_id:
                # Signal emittieren, damit das Objekt aus der Szene gelöscht wird
                self.object_deleted.emit(obj_id)
                # Felder leeren
                self.current_object = None
                self._clear_fields()
                self._show_no_selection()
                self.delete_button.setEnabled(False)
    
    def _show_selected(self):
        """Zeigt visuell an, dass ein Objekt ausgewählt ist"""
        if self.current_object:
            obj_id = self.current_object.get("id", "Unbekannt")
            self.status_label.setText(f"✓ {obj_id}")
            self.status_label.setStyleSheet("color: #4a9eff; font-weight: bold; font-size: 10pt; padding: 10px;")
            # Formular-Gruppe hervorheben
            form_group = self.findChild(QGroupBox, "Objekt-Eigenschaften")
            if form_group:
                form_group.setStyleSheet("QGroupBox { border: 2px solid #4a9eff; border-radius: 5px; padding-top: 10px; }")
    
    def _show_no_selection(self):
        """Zeigt an, dass kein Objekt ausgewählt ist"""
        self.status_label.setText("Kein Objekt ausgewählt")
        self.status_label.setStyleSheet("color: #999; font-size: 10pt; padding: 10px; font-style: italic;")
        # Formular-Gruppe zurücksetzen
        form_group = self.findChild(QGroupBox, "Objekt-Eigenschaften")
        if form_group:
            form_group.setStyleSheet("")
    
    def _on_x_changed(self, value: int):
        """Wird aufgerufen wenn Grid X geändert wird"""
        if self.current_object and self.current_object_id:
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        # Grid-Koordinaten in Pixel-Koordinaten umrechnen
                        old_x = obj.get("x", 0)
                        pixel_x = value * self.grid_size
                        obj["x"] = pixel_x
                        
                        # Kollisionsbox mitbewegen (Offset beibehalten)
                        collider_data = obj.get("collider", {})
                        if collider_data.get("enabled", False):
                            delta_x = pixel_x - old_x
                            if "x" in collider_data:
                                collider_data["x"] = collider_data.get("x", old_x) + delta_x
                        
                        self.current_object = obj  # Referenz aktualisieren
                        break
            
            # Auch current_object aktualisieren (falls kein scene_canvas)
            if self.current_object:
                pixel_x = value * self.grid_size
                self.current_object["x"] = pixel_x
                
                # Kollisionsbox immer im gleichen Grid-Feld wie das Objekt
                collider_data = self.current_object.get("collider", {})
                if collider_data.get("enabled", False):
                    collider_data["x"] = pixel_x
            
            # Direkt Canvas aktualisieren
            self._notify_change()
    
    def _on_y_changed(self, value: int):
        """Wird aufgerufen wenn Grid Y geändert wird"""
        if self.current_object and self.current_object_id:
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        # Grid-Koordinaten in Pixel-Koordinaten umrechnen
                        old_y = obj.get("y", 0)
                        pixel_y = value * self.grid_size
                        obj["y"] = pixel_y
                        
                        # Kollisionsbox mitbewegen (Offset beibehalten)
                        collider_data = obj.get("collider", {})
                        if collider_data.get("enabled", False):
                            delta_y = pixel_y - old_y
                            if "y" in collider_data:
                                collider_data["y"] = collider_data.get("y", old_y) + delta_y
                        
                        self.current_object = obj  # Referenz aktualisieren
                        break
            
            # Auch current_object aktualisieren (falls kein scene_canvas)
            if self.current_object:
                pixel_y = value * self.grid_size
                self.current_object["y"] = pixel_y
                
                # Kollisionsbox immer im gleichen Grid-Feld wie das Objekt
                collider_data = self.current_object.get("collider", {})
                if collider_data.get("enabled", False):
                    collider_data["y"] = pixel_y
            
            # Direkt Canvas aktualisieren
            self._notify_change()
    
    def _on_name_changed(self, text: str):
        """Wird aufgerufen wenn Name geändert wird"""
        if self.current_object and self.current_object_id:
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        # Name setzen (leeren String = None, damit ID verwendet wird)
                        if text.strip():
                            new_name = text.strip()
                            # Prüfen ob Name bereits verwendet wird (von anderem Objekt)
                            name_exists = False
                            for other_obj in self.scene_canvas.objects:
                                if other_obj.get("id") != self.current_object_id:
                                    other_name = other_obj.get("name", "")
                                    if other_name and other_name == new_name:
                                        name_exists = True
                                        break
                            
                            if name_exists:
                                # Name existiert bereits - nicht setzen, Warnung anzeigen
                                from PySide6.QtWidgets import QMessageBox
                                QMessageBox.warning(self, "Doppelter Name", 
                                                   f"Der Name '{new_name}' wird bereits von einem anderen Objekt verwendet.\n"
                                                   "Bitte wählen Sie einen anderen Namen.")
                                # Ursprünglichen Namen wiederherstellen
                                self.name_edit.blockSignals(True)
                                self.name_edit.setText(obj.get("name", ""))
                                self.name_edit.blockSignals(False)
                                return
                            
                            obj["name"] = new_name
                        else:
                            obj.pop("name", None)  # Entfernen wenn leer
                        self.current_object = obj  # Referenz aktualisieren
                        break
            
            # Auch current_object aktualisieren (falls kein scene_canvas)
            if self.current_object:
                if text.strip():
                    self.current_object["name"] = text.strip()
                else:
                    self.current_object.pop("name", None)
            
            # Direkt Canvas aktualisieren
            self._notify_change()
    
    def _on_ground_changed(self, state: int):
        """Wird aufgerufen wenn Ground Checkbox geändert wird"""
        is_ground = (state == Qt.CheckState.Checked.value)
        
        if self.current_object and self.current_object_id:
            # Ground-Eigenschaft im Objekt setzen
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        obj["ground"] = is_ground
                        self.current_object = obj
                        break
            
            # Auch current_object aktualisieren
            if self.current_object:
                self.current_object["ground"] = is_ground
            
            # Direkt Canvas aktualisieren
            self._notify_change()
    
    def _on_collider_enabled_changed(self, state: int):
        """Wird aufgerufen wenn Kollision Checkbox geändert wird"""
        enabled = (state == Qt.CheckState.Checked.value)
        self._update_collider_visibility(enabled)
        
        if self.current_object and self.current_object_id:
            # Collider-Daten im Objekt setzen
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        if "collider" not in obj:
                            obj["collider"] = {}
                        obj["collider"]["enabled"] = enabled
                        
                        # Wenn aktiviert, Standard-Werte setzen (falls nicht vorhanden)
                        if enabled:
                            if "x" not in obj["collider"]:
                                obj["collider"]["x"] = obj.get("x", 0)
                            if "y" not in obj["collider"]:
                                obj["collider"]["y"] = obj.get("y", 0)
                            if "width" not in obj["collider"]:
                                obj["collider"]["width"] = obj.get("width", 32)
                            if "height" not in obj["collider"]:
                                obj["collider"]["height"] = obj.get("height", 32)
                        else:
                            # Wenn deaktiviert, Collider-Daten entfernen
                            obj["collider"] = {"enabled": False}
                        
                        self.current_object = obj
                        break
            
            # Auch current_object aktualisieren
            if self.current_object:
                if "collider" not in self.current_object:
                    self.current_object["collider"] = {}
                self.current_object["collider"]["enabled"] = enabled
                
                if enabled:
                    if "x" not in self.current_object["collider"]:
                        self.current_object["collider"]["x"] = self.current_object.get("x", 0)
                    if "y" not in self.current_object["collider"]:
                        self.current_object["collider"]["y"] = self.current_object.get("y", 0)
                    if "width" not in self.current_object["collider"]:
                        self.current_object["collider"]["width"] = self.current_object.get("width", 32)
                    if "height" not in self.current_object["collider"]:
                        self.current_object["collider"]["height"] = self.current_object.get("height", 32)
                else:
                    self.current_object["collider"] = {"enabled": False}
            
            # Felder aktualisieren wenn aktiviert
            if enabled:
                self._update_collider_fields()
            
            # Direkt Canvas aktualisieren
            self._notify_change()
    
    def _update_collider_visibility(self, enabled: bool):
        """Aktualisiert die Sichtbarkeit der Kollisionsbox-Felder"""
        self.collider_x_label.setVisible(enabled)
        self.collider_x_spinbox.setVisible(enabled)
        self.collider_y_label.setVisible(enabled)
        self.collider_y_spinbox.setVisible(enabled)
        self.collider_width_label.setVisible(enabled)
        self.collider_width_spinbox.setVisible(enabled)
        self.collider_height_label.setVisible(enabled)
        self.collider_height_spinbox.setVisible(enabled)
    
    def _update_collider_fields(self):
        """Aktualisiert die Kollisionsbox-Felder mit aktuellen Werten"""
        if not self.current_object:
            return
        
        collider_data = self.current_object.get("collider", {})
        if collider_data.get("enabled", False):
            collider_x = collider_data.get("x", self.current_object.get("x", 0))
            collider_y = collider_data.get("y", self.current_object.get("y", 0))
            collider_width = collider_data.get("width", self.current_object.get("width", 32))
            collider_height = collider_data.get("height", self.current_object.get("height", 32))
            
            # X und Y direkt in Pixeln (nicht Grid-Koordinaten)
            self.collider_x_spinbox.blockSignals(True)
            self.collider_x_spinbox.setValue(int(collider_x))
            self.collider_x_spinbox.blockSignals(False)
            
            self.collider_y_spinbox.blockSignals(True)
            self.collider_y_spinbox.setValue(int(collider_y))
            self.collider_y_spinbox.blockSignals(False)
            
            self.collider_width_spinbox.blockSignals(True)
            self.collider_width_spinbox.setValue(int(collider_width))
            self.collider_width_spinbox.blockSignals(False)
            
            self.collider_height_spinbox.blockSignals(True)
            self.collider_height_spinbox.setValue(int(collider_height))
            self.collider_height_spinbox.blockSignals(False)
    
    def _on_collider_x_changed(self, value: int):
        """Wird aufgerufen wenn Kollisionsbox X Offset geändert wird"""
        if self.current_object and self.current_object_id:
            # Offset-Wert speichern und absolute Position berechnen
            obj_x = self.current_object.get("x", 0)
            obj_width = self.current_object.get("width", 32)
            obj_center_x = obj_x + obj_width / 2
            
            # Absolute Position = Objektmittelpunkt + Offset
            collider_abs_x = obj_center_x + value
            
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        if "collider" not in obj:
                            obj["collider"] = {"enabled": True}
                        obj["collider"]["x"] = collider_abs_x
                        self.current_object = obj
                        break
            
            if self.current_object:
                if "collider" not in self.current_object:
                    self.current_object["collider"] = {"enabled": True}
                self.current_object["collider"]["x"] = collider_abs_x
            
            self._notify_change()
    
    def _on_collider_y_changed(self, value: int):
        """Wird aufgerufen wenn Kollisionsbox Y Offset geändert wird"""
        if self.current_object and self.current_object_id:
            # Offset-Wert speichern und absolute Position berechnen
            obj_y = self.current_object.get("y", 0)
            obj_height = self.current_object.get("height", 32)
            obj_center_y = obj_y + obj_height / 2
            
            # Absolute Position = Objektmittelpunkt + Offset
            collider_abs_y = obj_center_y + value
            
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        if "collider" not in obj:
                            obj["collider"] = {"enabled": True}
                        obj["collider"]["y"] = collider_abs_y
                        self.current_object = obj
                        break
            
            if self.current_object:
                if "collider" not in self.current_object:
                    self.current_object["collider"] = {"enabled": True}
                self.current_object["collider"]["y"] = collider_abs_y
            
            self._notify_change()
    
    def _on_collider_width_changed(self, value: int):
        """Wird aufgerufen wenn Kollisionsbox Breite geändert wird"""
        if self.current_object and self.current_object_id:
            # Offset beibehalten, nur Breite ändern
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        if "collider" not in obj:
                            obj["collider"] = {"enabled": True}
                        obj["collider"]["width"] = value
                        self.current_object = obj
                        break
            
            if self.current_object:
                if "collider" not in self.current_object:
                    self.current_object["collider"] = {"enabled": True}
                self.current_object["collider"]["width"] = value
            
            self._notify_change()
    
    def _on_collider_height_changed(self, value: int):
        """Wird aufgerufen wenn Kollisionsbox Höhe geändert wird"""
        if self.current_object and self.current_object_id:
            # Offset beibehalten, nur Höhe ändern
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        if "collider" not in obj:
                            obj["collider"] = {"enabled": True}
                        obj["collider"]["height"] = value
                        self.current_object = obj
                        break
            
            if self.current_object:
                if "collider" not in self.current_object:
                    self.current_object["collider"] = {"enabled": True}
                self.current_object["collider"]["height"] = value
            
            self._notify_change()
    
    def _on_width_changed(self, value: int):
        """Wird aufgerufen wenn Breite geändert wird"""
        if self.current_object and self.current_object_id:
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        old_width = obj.get("width", value)
                        obj["width"] = value
                        self.current_object = obj
                        
                        # Kollisionsbox-Breite mit aktualisieren (wenn nicht explizit gesetzt)
                        collider_data = obj.get("collider", {})
                        if collider_data.get("enabled", False) and "width" not in collider_data:
                            collider_data["width"] = value
                        break
            
            # Auch current_object aktualisieren
            if self.current_object:
                self.current_object["width"] = value
            
            self._notify_change()
    
    def _on_height_changed(self, value: int):
        """Wird aufgerufen wenn Höhe geändert wird"""
        if self.current_object and self.current_object_id:
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        old_height = obj.get("height", value)
                        obj["height"] = value
                        self.current_object = obj
                        
                        # Kollisionsbox-Höhe mit aktualisieren (wenn nicht explizit gesetzt)
                        collider_data = obj.get("collider", {})
                        if collider_data.get("enabled", False) and "height" not in collider_data:
                            collider_data["height"] = value
                        break
            
            # Auch current_object aktualisieren
            if self.current_object:
                self.current_object["height"] = value
            
            self._notify_change()
    
    def _on_sprite_changed(self, index: int):
        """Wird aufgerufen wenn Sprite geändert wird"""
        # Verhindere Rekursion wenn Felder aktualisiert werden
        if self._updating_sprite:
            return
        
        if self.current_object and self.current_object_id:
            sprite_path = self.sprite_combo.currentData()
            # Leeren String in None umwandeln
            if sprite_path == "":
                sprite_path = None
            
            # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == self.current_object_id:
                        obj["sprite"] = sprite_path
                        self.current_object = obj  # Referenz aktualisieren
                        break
            
            # Auch current_object aktualisieren (falls kein scene_canvas)
            if self.current_object:
                self.current_object["sprite"] = sprite_path
            
            # Beide Signale emittieren
            self._notify_change()
            self.sprite_changed.emit()  # Signal für Canvas-Update (Sprite-Cache leeren)
    
    def _notify_change(self):
        """Benachrichtigt Canvas über Änderung"""
        # Canvas aktualisieren und Szene speichern
        if self.current_object:
            # Signal für Canvas-Update und Szene-Speichern
            self.object_changed.emit()
    
    def _drag_enter_event(self, event: QDragEnterEvent):
        """Wird aufgerufen wenn etwas über das Drop-Label gezogen wird"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def _drop_event(self, event: QDropEvent):
        """Wird aufgerufen wenn ein Sprite auf das Drop-Label oder ComboBox gezogen wird"""
        if event.mimeData().hasText():
            sprite_path = event.mimeData().text()
            # Sprite-Pfad setzen
            if self.current_object and self.project_path:
                try:
                    # Prüfen ob Pfad relativ oder absolut
                    sprite_path_obj = Path(sprite_path)
                    if sprite_path_obj.is_absolute():
                        # Prüfen ob es im Projekt-Ordner liegt
                        try:
                            rel_path = sprite_path_obj.relative_to(self.project_path)
                        except ValueError:
                            # Pfad liegt außerhalb des Projekts - nicht verwenden
                            from PySide6.QtWidgets import QMessageBox
                            QMessageBox.warning(self, "Fehler", 
                                              "Das Sprite muss sich im Projekt-Ordner befinden!")
                            event.ignore()
                            return
                    else:
                        rel_path = sprite_path_obj
                    
                    sprite_rel = str(rel_path).replace("\\", "/")
                    
                    # Sicherstellen, dass wir das richtige Objekt im Canvas-Array aktualisieren
                    if self.scene_canvas and self.current_object_id:
                        for obj in self.scene_canvas.objects:
                            if obj.get("id") == self.current_object_id:
                                obj["sprite"] = sprite_rel
                                self.current_object = obj  # Referenz aktualisieren
                                break
                    
                    # Auch current_object aktualisieren (falls kein scene_canvas)
                    if self.current_object:
                        self.current_object["sprite"] = sprite_rel
                    
                    # ComboBox aktualisieren (mit Flag um Signal zu blockieren)
                    self._updating_sprite = True
                    index = self.sprite_combo.findData(sprite_rel)
                    if index >= 0:
                        self.sprite_combo.setCurrentIndex(index)
                    else:
                        # Neues Item hinzufügen
                        self.sprite_combo.addItem(Path(rel_path).name, sprite_rel)
                        self.sprite_combo.setCurrentIndex(self.sprite_combo.count() - 1)
                    self._updating_sprite = False
                    
                    # Felder aktualisieren um Sprite anzuzeigen
                    self._update_fields()
                    
                    self._notify_change()
                    self.sprite_changed.emit()  # Signal für Canvas-Update
                    event.acceptProposedAction()
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Fehler", f"Fehler beim Setzen des Sprites:\n{e}")
                    import traceback
                    traceback.print_exc()
            else:
                event.ignore()
        else:
            event.ignore()