"""
Projekt-Einstellungen Dialog
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QSpinBox, QPushButton, QFormLayout, QGroupBox,
                                QMessageBox, QColorDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from pathlib import Path
import json
from typing import Optional


class ProjectSettingsDialog(QDialog):
    """Dialog für Projekt-Einstellungen"""
    
    def __init__(self, project_path: Path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.setWindowTitle("Projekt-Einstellungen")
        self.setMinimumWidth(400)
        
        # Grid-Farbe (Standard)
        self.grid_color = QColor(200, 200, 200, 120)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        layout = QVBoxLayout()
        
        # Sprite-Einstellungen
        sprite_group = QGroupBox("Sprite-Einstellungen")
        sprite_layout = QFormLayout()
        
        # Sprite-Größe (quadratisch, eine Zahl)
        self.sprite_size_spin = QSpinBox()
        self.sprite_size_spin.setMinimum(8)
        self.sprite_size_spin.setMaximum(512)
        self.sprite_size_spin.setValue(64)
        self.sprite_size_spin.setSuffix(" px")
        sprite_layout.addRow("Sprite-Größe (quadratisch):", self.sprite_size_spin)
        sprite_group.setLayout(sprite_layout)
        layout.addWidget(sprite_group)
        
        # Grid-Einstellungen (nur Farbe, Größe = Sprite-Größe)
        grid_group = QGroupBox("Grid-Einstellungen")
        grid_layout = QFormLayout()
        
        # Info-Label
        info_label = QLabel("Hinweis: Grid-Größe entspricht der Sprite-Größe")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        grid_layout.addRow("", info_label)
        
        # Grid-Farbe
        grid_color_layout = QHBoxLayout()
        self.grid_color_button = QPushButton()
        self.grid_color_button.setFixedSize(50, 30)
        self.grid_color_button.setStyleSheet("border: 1px solid #666;")
        self.grid_color_button.clicked.connect(self._on_grid_color_clicked)
        grid_color_layout.addWidget(self.grid_color_button)
        grid_color_layout.addStretch()
        grid_layout.addRow("Grid-Farbe:", grid_color_layout)
        
        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _load_settings(self):
        """Lädt Einstellungen aus project.json"""
        settings_file = self.project_path / "project.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Sprite-Größe laden (quadratisch)
                sprite_size = config.get("sprite_size", {})
                # Alte Format-Unterstützung (width/height)
                if isinstance(sprite_size, dict):
                    size = sprite_size.get("width", sprite_size.get("size", 64))
                else:
                    # Neues Format (nur eine Zahl)
                    size = sprite_size if isinstance(sprite_size, int) else 64
                self.sprite_size_spin.setValue(size)
                
                # Grid-Farbe laden (Grid-Größe = Sprite-Größe)
                grid_settings = config.get("grid", {})
                grid_color = grid_settings.get("color", [200, 200, 200, 120])
                if isinstance(grid_color, list) and len(grid_color) >= 3:
                    alpha = grid_color[3] if len(grid_color) >= 4 else 120
                    self.grid_color = QColor(grid_color[0], grid_color[1], grid_color[2], alpha)
                    self._update_grid_color_button()
            except Exception as e:
                QMessageBox.warning(self, "Warnung", 
                                  f"Fehler beim Laden der Einstellungen:\n{e}")
    
    def get_sprite_size(self) -> int:
        """Gibt die eingestellte Sprite-Größe zurück (quadratisch)"""
        return self.sprite_size_spin.value()
    
    def get_grid_color(self) -> QColor:
        """Gibt die eingestellte Grid-Farbe zurück"""
        return self.grid_color
    
    def _on_grid_color_clicked(self):
        """Wird aufgerufen wenn Grid-Farbe-Button geklickt wird"""
        color = QColorDialog.getColor(self.grid_color, self, "Grid-Farbe wählen")
        if color.isValid():
            self.grid_color = color
            self._update_grid_color_button()
    
    def _update_grid_color_button(self):
        """Aktualisiert die Farbe des Grid-Farbe-Buttons"""
        self.grid_color_button.setStyleSheet(
            f"background-color: rgb({self.grid_color.red()}, {self.grid_color.green()}, {self.grid_color.blue()}); "
            f"border: 1px solid #666;"
        )
    
    def save_settings(self):
        """Speichert Einstellungen in project.json"""
        settings_file = self.project_path / "project.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                config = {}
        else:
            config = {}
        
        # Sprite-Größe speichern (quadratisch, eine Zahl)
        config["sprite_size"] = self.sprite_size_spin.value()
        
        # Grid-Einstellungen speichern (nur Farbe, Größe = Sprite-Größe)
        config["grid"] = {
            "color": [
                self.grid_color.red(),
                self.grid_color.green(),
                self.grid_color.blue(),
                self.grid_color.alpha()
            ]
        }
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                               f"Fehler beim Speichern der Einstellungen:\n{e}")
            return False
    
    def accept(self):
        """Wird aufgerufen wenn OK geklickt wird"""
        if self.save_settings():
            super().accept()
