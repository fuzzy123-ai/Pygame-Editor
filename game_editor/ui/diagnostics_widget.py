"""
Diagnostics Widget - Zeigt LSP-Fehler und Warnungen an
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from typing import List, Dict, Any


class DiagnosticsWidget(QWidget):
    """Widget zur Anzeige von LSP-Diagnostics (Fehler/Warnungen)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Probleme")
        header.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 5px;
                font-weight: bold;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        layout.addWidget(header)
        
        # Liste für Fehler/Warnungen
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
    
    def update_diagnostics(self, diagnostics: List[Dict[str, Any]], uri: str):
        """Aktualisiert die angezeigten Diagnostics"""
        self.list_widget.clear()
        
        for diagnostic in diagnostics:
            severity = diagnostic.get("severity", 1)  # 1=Error, 2=Warning, 3=Info, 4=Hint
            message = diagnostic.get("message", "")
            range_info = diagnostic.get("range", {})
            start = range_info.get("start", {})
            line = start.get("line", 0) + 1  # LSP verwendet 0-basiert
            character = start.get("character", 0) + 1
            
            # Severity-Text
            severity_text = {
                1: "Fehler",
                2: "Warnung",
                3: "Info",
                4: "Hinweis"
            }.get(severity, "Unbekannt")
            
            # Item erstellen
            item_text = f"[Zeile {line}:{character}] {severity_text}: {message}"
            item = QListWidgetItem(item_text)
            
            # Farbe basierend auf Severity
            if severity == 1:  # Error
                item.setForeground(QColor(244, 67, 54))  # Rot
            elif severity == 2:  # Warning
                item.setForeground(QColor(255, 152, 0))  # Orange
            else:
                item.setForeground(QColor(156, 220, 254))  # Blau
            
            # Zusätzliche Daten speichern
            item.setData(Qt.ItemDataRole.UserRole, {
                "line": line - 1,  # Zurück zu 0-basiert
                "character": character - 1,
                "message": message,
                "severity": severity
            })
            
            self.list_widget.addItem(item)
    
    def clear_diagnostics(self):
        """Löscht alle Diagnostics"""
        self.list_widget.clear()
