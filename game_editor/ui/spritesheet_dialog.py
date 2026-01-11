"""
Spritesheet Extraction Dialog - Dialog zum Extrahieren von Spritesheets
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QSpinBox, QLineEdit, QFormLayout,
                                QGroupBox, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from pathlib import Path


class SpritesheetDialog(QDialog):
    """Dialog zum Extrahieren von Spritesheets"""
    
    def __init__(self, parent=None, spritesheet_path: Path = None):
        super().__init__(parent)
        self.spritesheet_path = spritesheet_path
        self.extracted_count = 0
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        self.setWindowTitle("Spritesheet extrahieren")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Info
        if self.spritesheet_path:
            info_label = QLabel(f"Spritesheet: {self.spritesheet_path.name}")
            info_label.setStyleSheet("font-weight: bold; padding: 5px;")
            layout.addWidget(info_label)
        
        # Grid-Parameter
        grid_group = QGroupBox("Grid-Parameter")
        grid_layout = QFormLayout()
        
        # Sprite-Größe
        size_layout = QHBoxLayout()
        self.sprite_width = QSpinBox()
        self.sprite_width.setRange(1, 2000)
        self.sprite_width.setValue(32)
        size_layout.addWidget(self.sprite_width)
        
        size_label = QLabel("x")
        size_layout.addWidget(size_label)
        
        self.sprite_height = QSpinBox()
        self.sprite_height.setRange(1, 2000)
        self.sprite_height.setValue(32)
        size_layout.addWidget(self.sprite_height)
        
        grid_layout.addRow("Sprite-Größe:", size_layout)
        
        # Spacing
        self.spacing = QSpinBox()
        self.spacing.setRange(0, 100)
        self.spacing.setValue(0)
        grid_layout.addRow("Abstand:", self.spacing)
        
        # Margin
        self.margin = QSpinBox()
        self.margin.setRange(0, 100)
        self.margin.setValue(0)
        grid_layout.addRow("Rand:", self.margin)
        
        # Output-Ordner
        self.output_folder = QLineEdit()
        self.output_folder.setPlaceholderText("(optional - wird aus Dateinamen abgeleitet)")
        grid_layout.addRow("Output-Ordner:", self.output_folder)
        
        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        extract_button = QPushButton("Extrahieren")
        extract_button.clicked.connect(self.accept)
        button_layout.addWidget(extract_button)
        
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_parameters(self):
        """Gibt die Extraktions-Parameter zurück"""
        return {
            "sprite_width": self.sprite_width.value(),
            "sprite_height": self.sprite_height.value(),
            "spacing": self.spacing.value(),
            "margin": self.margin.value(),
            "output_folder": self.output_folder.text().strip() or None
        }
