"""
Code Editor Settings Dialog - Einstellungen für Syntax-Highlighting und Editor
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QComboBox, QSpinBox, QColorDialog,
                                QGroupBox, QFormLayout, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from pathlib import Path
import json
from typing import Dict, Any, Optional


class CodeEditorSettingsDialog(QDialog):
    """Einstellungs-Dialog für Code-Editor"""
    
    settings_changed = Signal(dict)  # Signal wenn Einstellungen geändert wurden
    
    def __init__(self, project_path: Path, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.current_preset = "default"
        self.custom_presets: Dict[str, Dict[str, Any]] = {}
        
        # Syntax-Highlighting ist verfügbar (QTextEdit mit Regex)
        self.has_syntax_highlighting = True
        
        self.setWindowTitle("Code Editor Einstellungen")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        # Dark-Mode
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #d4d4d4;
            }
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: 2px solid #3a8eef;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5aaeff;
                border-color: #4a9eff;
            }
            QPushButton:pressed {
                background-color: #3a8eef;
            }
            QComboBox, QSpinBox, QLineEdit {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:hover, QSpinBox:hover, QLineEdit:hover {
                border-color: #4a9eff;
            }
        """)
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Preset-Auswahl
        preset_group = QGroupBox("Preset")
        preset_layout = QFormLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["default", "light_mode", "high_contrast", "matrix_mode"])
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addRow("Preset:", self.preset_combo)
        
        # Preset-Verwaltung
        preset_buttons_layout = QHBoxLayout()
        self.add_preset_button = QPushButton("Preset hinzufügen...")
        self.add_preset_button.clicked.connect(self._add_custom_preset)
        self.delete_preset_button = QPushButton("Preset löschen")
        self.delete_preset_button.clicked.connect(self._delete_preset)
        self.delete_preset_button.setEnabled(False)  # Nur für Custom-Presets
        preset_buttons_layout.addWidget(self.add_preset_button)
        preset_buttons_layout.addWidget(self.delete_preset_button)
        preset_buttons_layout.addStretch()
        preset_layout.addRow("", preset_buttons_layout)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Warnung wenn kein Syntax-Highlighting verfügbar
        if not self.has_syntax_highlighting:
            warning_label = QLabel(
                "⚠️ Syntax-Highlighting nicht verfügbar. Nur Standard-Text und Hintergrund können angepasst werden.\n"
                "Hinweis: PySide6-QScintilla existiert nicht als offizielles Paket. "
                "Das GitLab-Projekt ist archiviert und nicht verfügbar."
            )
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet("""
                QLabel {
                    background-color: #3d3d3d;
                    color: #ffaa00;
                    padding: 10px;
                    border: 2px solid #ffaa00;
                    border-radius: 5px;
                }
            """)
            layout.addWidget(warning_label)
        
        # Text-Einstellungen
        text_group = QGroupBox("Text")
        text_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(11)
        self.font_size_spin.valueChanged.connect(self._on_setting_changed)
        text_layout.addRow("Text-Größe:", self.font_size_spin)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # Farb-Einstellungen
        colors_group = QGroupBox("Farben")
        colors_layout = QFormLayout()
        
        # Default Text
        self.default_color_button = QPushButton("Farbe wählen...")
        self.default_color_button.clicked.connect(lambda: self._choose_color("default"))
        self.default_color_label = QLabel("#d4d4d4")
        default_layout = QHBoxLayout()
        default_layout.addWidget(self.default_color_button)
        default_layout.addWidget(self.default_color_label)
        default_layout.addStretch()
        colors_layout.addRow("Standard-Text:", default_layout)
        
        # Syntax-Highlighting-Farben (jetzt mit QTextEdit unterstützt)
        syntax_colors = [
            ("comment", "Kommentare"),
            ("number", "Zahlen"),
            ("string", "Strings"),
            ("keyword", "Keywords"),
            ("class", "Klassen"),
            ("function", "Funktionen"),
            ("variable", "Variablen"),
            ("operator", "Operatoren & Zeichen"),
        ]
        
        for color_type, label_text in syntax_colors:
            color_button = QPushButton("Farbe wählen...")
            color_button.clicked.connect(lambda checked, ct=color_type: self._choose_color(ct))
            color_label = QLabel("#000000")
            color_label.setMinimumWidth(80)
            color_layout = QHBoxLayout()
            color_layout.addWidget(color_button)
            color_layout.addWidget(color_label)
            color_layout.addStretch()
            colors_layout.addRow(f"{label_text}:", color_layout)
            setattr(self, f"{color_type}_color_button", color_button)
            setattr(self, f"{color_type}_color_label", color_label)
        
        # Hintergrund
        self.background_color_button = QPushButton("Farbe wählen...")
        self.background_color_button.clicked.connect(lambda: self._choose_color("background"))
        self.background_color_label = QLabel("#1e1e1e")
        background_layout = QHBoxLayout()
        background_layout.addWidget(self.background_color_button)
        background_layout.addWidget(self.background_color_label)
        background_layout.addStretch()
        colors_layout.addRow("Hintergrund:", background_layout)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Übernehmen")
        self.apply_button.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._ok_clicked)
        buttons_layout.addWidget(self.ok_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def _choose_color(self, color_type: str):
        """Öffnet Farb-Dialog für einen Farb-Typ"""
        # Aktuelle Farbe holen
        label = getattr(self, f"{color_type}_color_label")
        current_color = QColor(label.text())
        
        # Farb-Dialog öffnen
        color = QColorDialog.getColor(current_color, self, f"{color_type} Farbe wählen")
        if color.isValid():
            label.setText(color.name())
            label.setStyleSheet(f"background-color: {color.name()}; padding: 3px; border-radius: 3px;")
            self._on_setting_changed()
    
    def _on_preset_changed(self, preset_name: str):
        """Wird aufgerufen wenn Preset geändert wird"""
        self.current_preset = preset_name
        self._load_preset(preset_name)
        self.delete_preset_button.setEnabled(preset_name not in ["default", "light_mode", "high_contrast", "matrix_mode"])
    
    def _load_preset(self, preset_name: str):
        """Lädt ein Preset"""
        if preset_name in self.custom_presets:
            preset = self.custom_presets[preset_name]
        elif preset_name == "default":
            preset = self._get_default_preset()
        elif preset_name == "light_mode":
            preset = self._get_light_mode_preset()
        elif preset_name == "high_contrast":
            preset = self._get_high_contrast_preset()
        elif preset_name == "matrix_mode":
            preset = self._get_matrix_mode_preset()
        else:
            preset = self._get_default_preset()
        
        # Preset anwenden
        self.font_size_spin.setValue(preset.get("font_size", 11))
        self._set_color("default", preset.get("default", "#d4d4d4"))
        self._set_color("comment", preset.get("comment", "#646464"))
        self._set_color("number", preset.get("number", "#b5cea8"))
        self._set_color("string", preset.get("string", "#ec7600"))
        self._set_color("keyword", preset.get("keyword", "#4faff0"))
        self._set_color("class", preset.get("class", "#4ec9b0"))
        self._set_color("function", preset.get("function", "#dcdc64"))
        self._set_color("variable", preset.get("variable", "#9cdcfe"))
        self._set_color("operator", preset.get("operator", "#b4b4ff"))
        self._set_color("background", preset.get("background", "#1e1e1e"))
    
    def _set_color(self, color_type: str, color_hex: str):
        """Setzt eine Farbe"""
        label = getattr(self, f"{color_type}_color_label")
        label.setText(color_hex)
        label.setStyleSheet(f"background-color: {color_hex}; padding: 3px; border-radius: 3px;")
    
    def _get_default_preset(self) -> Dict[str, Any]:
        """Gibt das Default-Preset zurück (stärkere Farben, keine Pastelltöne)"""
        return {
            "font_size": 11,
            "default": "#d4d4d4",
            "comment": "#646464",
            "number": "#b5cea8",
            "string": "#ec7600",  # Kräftiges Orange
            "keyword": "#4faff0",  # Kräftiges Blau
            "class": "#4ec9b0",  # Türkis
            "function": "#dcdc64",  # Kräftiges Gelb
            "variable": "#9cdcfe",  # Hellblau
            "operator": "#b4b4ff",  # Kräftiges Cyan/Lila für Operatoren
            "background": "#1e1e1e"
        }
    
    def _get_light_mode_preset(self) -> Dict[str, Any]:
        """Gibt das Light Mode Preset zurück"""
        return {
            "font_size": 11,
            "default": "#1e1e1e",
            "comment": "#6a9955",
            "number": "#098658",
            "string": "#a31515",
            "keyword": "#0000ff",
            "class": "#267f99",
            "function": "#795e26",
            "variable": "#001080",
            "operator": "#0000ff",
            "background": "#ffffff"
        }
    
    def _get_high_contrast_preset(self) -> Dict[str, Any]:
        """Gibt das High Contrast Preset zurück"""
        return {
            "font_size": 14,
            "default": "#ffffff",
            "comment": "#ffff00",
            "number": "#00ffff",
            "string": "#ff00ff",
            "keyword": "#00ff00",
            "class": "#ff0000",
            "function": "#0000ff",
            "variable": "#ffffff",
            "operator": "#00ffff",
            "background": "#000000"
        }
    
    def _get_matrix_mode_preset(self) -> Dict[str, Any]:
        """Gibt das Matrix Mode Preset zurück"""
        return {
            "font_size": 11,
            "default": "#90ee90",  # Pastell-Grün (lightgreen)
            "comment": "#00aa00",
            "number": "#00ff88",
            "string": "#88ff00",
            "keyword": "#00ff00",
            "class": "#00ff88",
            "function": "#88ff00",
            "variable": "#00ff00",
            "operator": "#00ffff",
            "background": "#000000"
        }
    
    def _add_custom_preset(self):
        """Fügt ein Custom-Preset hinzu"""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Preset hinzufügen", "Preset-Name:")
        if ok and name:
            if name in ["default", "light_mode", "high_contrast", "matrix_mode"]:
                QMessageBox.warning(self, "Fehler", "Dieser Preset-Name ist reserviert!")
                return
            
            # Aktuelle Einstellungen als Preset speichern
            preset = {
                "font_size": self.font_size_spin.value(),
                "default": self.default_color_label.text(),
                "comment": self.comment_color_label.text(),
                "number": self.number_color_label.text(),
                "string": self.string_color_label.text(),
                "keyword": self.keyword_color_label.text(),
                "class": self.class_color_label.text(),
                "function": self.function_color_label.text(),
                "variable": self.variable_color_label.text(),
                "operator": self.operator_color_label.text(),
                "background": self.background_color_label.text()
            }
            
            self.custom_presets[name] = preset
            self.preset_combo.addItem(name)
            self.preset_combo.setCurrentText(name)
            self._save_custom_presets()
    
    def _delete_preset(self):
        """Löscht ein Custom-Preset"""
        preset_name = self.preset_combo.currentText()
        if preset_name in self.custom_presets:
            reply = QMessageBox.question(self, "Preset löschen", 
                                        f"Möchten Sie das Preset '{preset_name}' wirklich löschen?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                index = self.preset_combo.findText(preset_name)
                if index >= 0:
                    self.preset_combo.removeItem(index)
                del self.custom_presets[preset_name]
                self.preset_combo.setCurrentText("default")
                self._save_custom_presets()
    
    def _on_setting_changed(self):
        """Wird aufgerufen wenn eine Einstellung geändert wird"""
        # Preset auf "custom" setzen wenn vorhanden, sonst nichts
        pass
    
    def _load_settings(self):
        """Lädt Einstellungen aus project.json"""
        if not self.project_path:
            self._load_preset("default")
            return
        
        settings_file = self.project_path / "code_editor_settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Custom Presets laden
                self.custom_presets = settings.get("custom_presets", {})
                for preset_name in self.custom_presets.keys():
                    if preset_name not in ["default", "light_mode", "high_contrast", "matrix_mode"]:
                        self.preset_combo.addItem(preset_name)
                
                # Aktuelles Preset laden
                current_preset = settings.get("current_preset", "default")
                if current_preset in self.custom_presets or current_preset in ["default", "light_mode", "high_contrast", "matrix_mode"]:
                    self.preset_combo.setCurrentText(current_preset)
                    self.current_preset = current_preset
                else:
                    self._load_preset("default")
                    return
                
                # Gespeicherte Einstellungen laden (falls vorhanden)
                saved_settings = settings.get("current_settings")
                if saved_settings:
                    # Gespeicherte Einstellungen anwenden (überschreibt Preset)
                    self.font_size_spin.setValue(saved_settings.get("font_size", 11))
                    self._set_color("default", saved_settings.get("default", "#d4d4d4"))
                    self._set_color("comment", saved_settings.get("comment", "#646464"))
                    self._set_color("number", saved_settings.get("number", "#b5cea8"))
                    self._set_color("string", saved_settings.get("string", "#ec7600"))
                    self._set_color("keyword", saved_settings.get("keyword", "#4faff0"))
                    self._set_color("class", saved_settings.get("class", "#4ec9b0"))
                    self._set_color("function", saved_settings.get("function", "#dcdc64"))
                    self._set_color("variable", saved_settings.get("variable", "#9cdcfe"))
                    self._set_color("operator", saved_settings.get("operator", "#b4b4ff"))
                    self._set_color("background", saved_settings.get("background", "#1e1e1e"))
                else:
                    # Keine gespeicherten Einstellungen - Preset laden
                    self._load_preset(current_preset)
            except Exception as e:
                print(f"Fehler beim Laden der Einstellungen: {e}")
                self._load_preset("default")
        else:
            self._load_preset("default")
    
    def _save_custom_presets(self):
        """Speichert Custom-Presets"""
        if not self.project_path:
            return
        
        settings_file = self.project_path / "code_editor_settings.json"
        try:
            settings = {
                "current_preset": self.current_preset,
                "custom_presets": self.custom_presets
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    def _apply_settings(self):
        """Wendet Einstellungen an"""
        settings = self._get_current_settings()
        self.settings_changed.emit(settings)
        self._save_custom_presets()
    
    def _ok_clicked(self):
        """OK-Button wurde geklickt"""
        self._apply_settings()
        self.accept()
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Gibt aktuelle Einstellungen zurück"""
        return {
            "font_size": self.font_size_spin.value(),
            "default": self.default_color_label.text(),
            "comment": self.comment_color_label.text(),
            "number": self.number_color_label.text(),
            "string": self.string_color_label.text(),
            "keyword": self.keyword_color_label.text(),
            "class": self.class_color_label.text(),
            "function": self.function_color_label.text(),
            "variable": self.variable_color_label.text(),
            "operator": self.operator_color_label.text(),
            "background": self.background_color_label.text()
        }
