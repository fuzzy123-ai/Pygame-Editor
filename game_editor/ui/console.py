"""
Console/Terminal - Zeigt Debug-Ausgaben und Fehler
"""
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor


class Console(QWidget):
    """Terminal-ähnliche Konsole für Debug-Ausgaben und Fehler"""
    
    # Signal wenn neuer Text hinzugefügt wird
    text_added = Signal()
    
    def __init__(self):
        super().__init__()
        self.is_expanded = True  # Terminal ist standardmäßig aufgeklappt
        self.expanded_height = 200  # Standard-Höhe (immer sichtbar)
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        # Dark-Mode für Console
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 10)  # Mehr Abstand unten (10 statt 5)
        layout.setSpacing(0)
        
        # Header mit Label und Toggle-Button (Dark-Mode)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toggle-Button (Pfeil) - Dark-Mode
        self.toggle_button = QPushButton("▼")
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 10pt;
                padding: 0px;
                color: #d4d4d4;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-radius: 3px;
            }
        """)
        self.toggle_button.clicked.connect(self._toggle_expanded)
        header_layout.addWidget(self.toggle_button)
        
        # Label (Dark-Mode)
        label = QLabel("Terminal")
        label.setStyleSheet("font-weight: bold; padding: 5px; color: #d4d4d4;")
        header_layout.addWidget(label)
        header_layout.addStretch()
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        layout.addWidget(header_widget)
        
        # Text-Editor für Ausgaben
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
        
        # Standardmäßig AUFGEKLAPPT starten, damit Debug-Ausgaben sichtbar sind
        # Fixe Höhe setzen, damit Konsole immer sichtbar ist
        self.setMinimumHeight(self.expanded_height)  # Mindesthöhe = expanded_height
        self.setMaximumHeight(self.expanded_height)  # Maximale Höhe = expanded_height
        self.setFixedHeight(self.expanded_height)  # Fixe Höhe
        self.text_edit.setVisible(True)
        self.toggle_button.setText("▼")
    
    def ensure_visible(self):
        """Stellt sicher, dass die Konsole sichtbar ist und aufklappt"""
        if not self.is_expanded:
            self.expand()
        # Scroll zum Ende, damit neue Ausgaben sichtbar sind
        self.text_edit.moveCursor(QTextCursor.End)
    
    def _toggle_expanded(self):
        """Klappt das Terminal auf/zu"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            # Aufgeklappt: Fixe Höhe setzen
            self.setMinimumHeight(self.expanded_height)
            self.setMaximumHeight(self.expanded_height)
            self.setFixedHeight(self.expanded_height)
            self.toggle_button.setText("▼")
            self.text_edit.setVisible(True)
        else:
            # Minimiert: Nur Header sichtbar
            self.setMinimumHeight(25)  # Mindesthöhe für Header (sichtbar bleiben)
            self.setMaximumHeight(25)  # Nur Header sichtbar
            self.setFixedHeight(25)  # Fixe Höhe für minimierten Zustand
            self.toggle_button.setText("▶")
            self.text_edit.setVisible(False)
    
    def expand(self):
        """Klappt das Terminal auf"""
        if not self.is_expanded:
            self._toggle_expanded()
        # Sicherstellen dass Konsole sichtbar ist
        self.ensure_visible()
    
    def append_output(self, text: str):
        """Fügt normale Ausgabe hinzu (weiß)"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format_normal = QTextCharFormat()
        format_normal.setForeground(QColor("#d4d4d4"))
        
        cursor.setCharFormat(format_normal)
        cursor.insertText(text + "\n")
        
        # Scroll nach unten
        self.text_edit.moveCursor(QTextCursor.End)
        
        # Signal emittieren und Terminal aufklappen
        self.text_added.emit()
        self.expand()
    
    def append_error(self, text: str):
        """Fügt Fehler-Ausgabe hinzu (rot)"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format_error = QTextCharFormat()
        format_error.setForeground(QColor("#f48771"))
        
        cursor.setCharFormat(format_error)
        cursor.insertText(text + "\n")
        
        # Scroll nach unten
        self.text_edit.moveCursor(QTextCursor.End)
        
        # Signal emittieren und Terminal aufklappen
        self.text_added.emit()
        self.expand()
    
    def append_debug(self, text: str):
        """Fügt Debug-Ausgabe hinzu (gelb)"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format_debug = QTextCharFormat()
        format_debug.setForeground(QColor("#dcdcaa"))
        
        cursor.setCharFormat(format_debug)
        cursor.insertText(f"[DEBUG] {text}\n")
        
        # Scroll nach unten
        self.text_edit.moveCursor(QTextCursor.End)
        
        # Signal emittieren und Terminal aufklappen
        self.text_added.emit()
        self.expand()
    
    def clear(self):
        """Löscht alle Ausgaben"""
        self.text_edit.clear()
