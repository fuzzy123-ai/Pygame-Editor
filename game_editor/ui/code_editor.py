"""
Code Editor - Python Editor mit QTextEdit, LSP und Auto-Completion
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
                               QDialog, QScrollArea, QToolButton, QTextEdit, QMenu, QCompleter,
                               QListWidgetItem)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPoint, QStringListModel
from typing import Optional
from PySide6.QtGui import (QIcon, QPainter, QColor, QPolygon, QFont, QContextMenuEvent, QAction,
                          QTextCharFormat, QTextCursor, QTextDocument)
from pathlib import Path
import sys
import urllib.parse

# LSP-Module importieren
from .lsp_client import LSPClient
from .syntax_highlighter import LSPSyntaxHighlighter

# Editor-Import: Nur QTextEdit (kein QScintilla mehr)
# WICHTIG: Nur eine Binding-Ebene (PySide6) - keine PyQt5/PyQt6
QSCINTILLA_AVAILABLE = False  # QScintilla wird nicht mehr verwendet
EDITOR_TYPE = "qtextedit"

# Hilfsfunktionen werden nicht mehr benötigt (nur noch QTextEdit)

class CustomTextEdit(QTextEdit):
    """Custom QTextEdit mit LSP-Unterstützung, Syntax-Highlighting und Auto-Completion"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_code_editor = None  # Referenz zum CodeEditor-Widget
        self.lsp_completer = None  # Wird später von CodeEditor gesetzt
        self._setup_basic_autocompletion()
        self._setup_syntax_highlighting()
    
    def _setup_basic_autocompletion(self):
        """Richtet grundlegende Auto-Vervollständigung ein (Fallback wenn LSP nicht verfügbar)"""
        # API-Funktionen für Auto-Vervollständigung
        api_keywords = [
            "get_object", "get_all_objects",
            "key_pressed", "key_down", "mouse_position",
            "print_debug", "spawn_object",
            "move_with_collision", "push_objects",
            "lock_y_position", "unlock_y_position",
        ]
        
        # GameObject-Attribute
        gameobject_attrs = [
            "x", "y", "width", "height",
            "visible", "sprite", "id",
            "collides_with", "is_ground", "is_camera", "layer",
        ]
        
        # Python-Keywords
        python_keywords = [
            "def", "class", "if", "else", "elif", "for", "while",
            "return", "True", "False", "None", "and", "or", "not",
            "import", "from", "as", "pass", "break", "continue",
            "try", "except", "finally", "raise", "with", "lambda",
        ]
        
        # Alle Keywords zusammenfassen
        all_keywords = api_keywords + gameobject_attrs + python_keywords
        
        # QCompleter erstellen (Fallback)
        self.fallback_completer = QCompleter(all_keywords, self)
        self.fallback_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.fallback_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.fallback_completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
    
    def _setup_syntax_highlighting(self):
        """Richtet Syntax-Highlighting ein"""
        self.syntax_highlighter = LSPSyntaxHighlighter(self.document(), self)
    
    def keyPressEvent(self, event):
        """Überschreibt KeyPressEvent für LSP-Auto-Completion"""
        # Wenn LSP-Completer verfügbar ist, verwende diesen
        if self.lsp_completer and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
            # LSP-Completer behandelt diese Tasten
            if hasattr(self.lsp_completer, 'popup') and self.lsp_completer.popup().isVisible():
                self.lsp_completer.popup().hide()
                return
        
        super().keyPressEvent(event)
        
        # Trigger LSP-Completion nach Tastendruck
        if self.parent_code_editor and self.parent_code_editor.lsp_client:
            cursor = self.textCursor()
            char = event.text()
            if char and (char.isalnum() or char in ['.', '_']):
                # Trigger LSP-Completion
                QTimer.singleShot(100, lambda: self.parent_code_editor._trigger_lsp_completion())
    
    def apply_syntax_highlighting(self, text: str):
        """Wendet Syntax-Highlighting an"""
        if self.syntax_highlighter:
            self.syntax_highlighter.apply_syntax_highlighting(text)
    
    def apply_diagnostics(self, diagnostics: list):
        """Wendet Diagnostics (Fehler-Unterstreichungen) an
        
        WICHTIG: Diese Funktion setzt nur Unterstreichungen, keine Syntax-Highlighting-Farben!
        Syntax-Highlighting wird NUR durch self.syntax_highlighter.apply_syntax_highlighting() angewendet.
        """
        # WICHTIG: Verwende mergeCharFormat statt setCharFormat, um bestehende Formatierungen zu erhalten!
        # Lösche alte Unterstreichungen (nur Unterstreichungen, keine Farben!)
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.SelectionType.Document)
        format_clear = QTextCharFormat()
        format_clear.setUnderlineStyle(QTextCharFormat.UnderlineStyle.NoUnderline)
        # mergeCharFormat behält bestehende Formatierungen (Farben) und ändert nur Unterstreichungen
        cursor.mergeCharFormat(format_clear)
        
        # Wende neue Diagnostics an
        for diagnostic in diagnostics:
            severity = diagnostic.get("severity", 1)
            range_info = diagnostic.get("range", {})
            start = range_info.get("start", {})
            end = range_info.get("end", {})
            
            start_line = start.get("line", 0)
            start_char = start.get("character", 0)
            end_line = end.get("line", 0)
            end_char = end.get("character", 0)
            
            # Finde Positionen im Dokument
            start_block = self.document().findBlockByNumber(start_line)
            end_block = self.document().findBlockByNumber(end_line)
            
            if start_block.isValid() and end_block.isValid():
                start_pos = start_block.position() + start_char
                end_pos = end_block.position() + end_char
                
                cursor.setPosition(start_pos)
                cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
                
                # Format basierend auf Severity - NUR Unterstreichungen, keine Farben!
                format_error = QTextCharFormat()
                if severity == 1:  # Error
                    format_error.setUnderlineColor(QColor(244, 67, 54))  # Rot
                    format_error.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
                elif severity == 2:  # Warning
                    format_error.setUnderlineColor(QColor(255, 152, 0))  # Orange
                    format_error.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
                else:
                    format_error.setUnderlineColor(QColor(156, 220, 254))  # Blau
                    format_error.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
                
                # mergeCharFormat behält bestehende Formatierungen (Syntax-Highlighting-Farben) und fügt nur Unterstreichungen hinzu
                cursor.mergeCharFormat(format_error)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Überschreibt das Standard-Kontextmenü und erweitert es"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
            }
            QMenu::item {
                padding: 5px 20px 5px 30px;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3d3d3d;
                margin: 5px 0px;
            }
        """)
        
        # Standard-Aktionen
        undo_action = menu.addAction("↶ Rückgängig")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        undo_action.setEnabled(self.document().isUndoAvailable())
        
        redo_action = menu.addAction("↷ Wiederherstellen")
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        redo_action.setEnabled(self.document().isRedoAvailable())
        
        menu.addSeparator()
        
        cut_action = menu.addAction("✂ Ausschneiden")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(self.textCursor().hasSelection())
        
        copy_action = menu.addAction("📋 Kopieren")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.textCursor().hasSelection())
        
        paste_action = menu.addAction("📄 Einfügen")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        
        menu.addSeparator()
        
        select_all_action = menu.addAction("✓ Alle auswählen")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.selectAll)
        
        menu.addSeparator()
        
        # Einstellungen
        if self.parent_code_editor:
            settings_action = menu.addAction("⚙ Einstellungen...")
            settings_action.triggered.connect(self.parent_code_editor._open_settings)
        
        menu.exec(event.globalPos())


class CodeEditor(QWidget):
    """Code Editor mit Syntax-Highlighting für Python"""
    
    code_changed = Signal()  # Wird emittiert wenn Code geändert wird
    run_requested = Signal()  # Wird emittiert wenn Start-Button gedrückt wird
    stop_requested = Signal()  # Wird emittiert wenn Stop-Button gedrückt wird
    undo_redo_changed = Signal()  # Wird emittiert wenn Undo/Redo-Status sich ändert
    
    def __init__(self):
        super().__init__()
        self.project_path: Path | None = None
        self.current_object_id: str | None = None  # ID des aktuell ausgewählten Objekts
        self.undo_redo_manager = None  # Wird vom main_window gesetzt
        self.scene_canvas = None  # Wird vom main_window gesetzt (für Objekt-Updates)
        self.last_text = ""  # Letzter Text für Undo/Redo
        self.last_syntax_text = ""  # Letzter Text für Syntax-Highlighting-Check
        self.text_change_timer = QTimer()
        self.text_change_timer.setSingleShot(True)
        self.text_change_timer.timeout.connect(self._on_text_changed_delayed)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(5000)  # Alle 5 Sekunden
        
        # LSP-Client
        self.lsp_client: Optional[LSPClient] = None
        self.lsp_document_version = 0
        self.lsp_document_uri: Optional[str] = None
        self.lsp_update_timer = QTimer()
        self.lsp_update_timer.setSingleShot(True)
        self.lsp_update_timer.timeout.connect(self._update_lsp_document)
        
        # Flag um rekursive Aufrufe zu verhindern
        self._updating_syntax = False
        self._updating_lsp = False
        
        # Timer für Syntax-Highlighting Debouncing (sehr kurz für bessere Reaktionszeit)
        self.syntax_update_timer = QTimer()
        self.syntax_update_timer.setSingleShot(True)
        self.syntax_update_timer.timeout.connect(self._apply_syntax_highlighting)
        
        # Lexer für späteren Zugriff (für Einstellungen)
        self.lexer = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        # Dark-Mode für das gesamte Widget
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar mit Start/Stop Buttons
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setContentsMargins(5, 5, 5, 5)
        self.toolbar_layout.setSpacing(5)
        
        # Start-Button mit grünem Dreieck (Dark-Mode)
        self.run_button = QPushButton()
        self.run_button.setFixedSize(40, 40)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: 2px solid #3d8b40;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #66bb6a;
                border-color: #4CAF50;
            }
            QPushButton:pressed {
                background-color: #388e3c;
                border-color: #2e7d32;
            }
            QPushButton:disabled {
                background-color: #424242;
                border-color: #616161;
            }
        """)
        # Grünes Dreieck-Icon erstellen
        self._create_play_icon()
        self.run_button.setToolTip("Spiel starten (F5)")
        self.run_button.clicked.connect(self.run_requested.emit)
        self.run_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.run_button)
        
        # Stop-Button (Dark-Mode)
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: 2px solid #c62828;
                border-radius: 20px;
                font-size: 18pt;
                color: white;
            }
            QPushButton:hover {
                background-color: #ef5350;
                border-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #d32f2f;
                border-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #424242;
                border-color: #616161;
                color: #757575;
            }
        """)
        self.stop_button.setToolTip("Spiel stoppen (F6)")
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.stop_button.setEnabled(False)
        self.toolbar_layout.addWidget(self.stop_button)
        
        # Undo/Redo Buttons (werden vom main_window gesetzt)
        self.undo_button = None  # Wird vom main_window gesetzt
        self.redo_button = None  # Wird vom main_window gesetzt
        
        self.toolbar_layout.addStretch()
        
        # Label (wird dynamisch aktualisiert) - Dark-Mode
        self.label = QLabel("Code Editor (game.py)")
        self.label.setStyleSheet("""
            font-weight: bold; 
            padding: 5px; 
            background-color: #1e1e1e; 
            color: #d4d4d4;
            border-radius: 3px;
        """)
        self.toolbar_layout.addWidget(self.label)
        
        # Fragezeichen-Button für Hilfe (Dark-Mode)
        from PySide6.QtWidgets import QToolButton
        self.help_button = QToolButton()
        self.help_button.setText("?")
        self.help_button.setToolTip("Hilfe: Verfügbare Pygame-Befehle")
        self.help_button.setFixedSize(30, 30)
        self.help_button.setStyleSheet("""
            QToolButton {
                background-color: #4a9eff;
                color: white;
                border: 2px solid #3a8eef;
                border-radius: 15px;
                font-size: 14pt;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #5aaeff;
                border-color: #4a9eff;
            }
            QToolButton:pressed {
                background-color: #3a8eef;
                border-color: #2a7eef;
            }
        """)
        self.help_button.clicked.connect(self._toggle_help_overlay)
        self.toolbar_layout.addWidget(self.help_button)
        
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(self.toolbar_layout)
        toolbar_widget.setStyleSheet("""
            background-color: #1e1e1e;
            border-bottom: 1px solid #3d3d3d;
        """)
        layout.addWidget(toolbar_widget)
        
        # Hilfe-Overlay (wird später erstellt wenn benötigt)
        self.help_overlay = None
        
        # Code Editor: QTextEdit mit LSP-Unterstützung
        self.editor = CustomTextEdit()
        self.editor.parent_code_editor = self  # Referenz für Einstellungen
        
        # Word Wrap aktivieren (Zeilenumbrüche wenn Fenster zu schmal wird)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Monospace-Font für bessere Lesbarkeit
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor.setFont(font)
        
        # Dark-Mode Styling
        # WICHTIG: Textfarbe NICHT über Stylesheet setzen, da das die Syntax-Highlighting-Formatierungen überschreibt
        # Die Textfarbe wird stattdessen über die Syntax-Highlighter-Formate gesetzt
        self.editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
        
        # Text geändert (mit Debouncing für Undo/Redo)
        self.editor.textChanged.connect(self._on_text_changed_with_undo)
        self.editor.textChanged.connect(self._on_text_changed_for_lsp)
        
        # Syntax-Highlighting bei Textänderung
        self.editor.textChanged.connect(self._on_text_changed_for_syntax)
        
        # Lexer auf None setzen (wird nicht mehr verwendet)
        self.lexer = None
        
        # Editor direkt zum Layout hinzufügen (nutzt gesamten verfügbaren Platz)
        layout.addWidget(self.editor)
        self.setLayout(layout)
        
        # LSP-Client wird später initialisiert (wenn Projekt geladen wird)
    
    def _create_play_icon(self):
        """Erstellt ein grünes Dreieck-Icon für den Start-Button"""
        from PySide6.QtGui import QPixmap, QPainter
        
        pixmap = QPixmap(24, 24)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255))  # Weißes Dreieck
        painter.setPen(Qt.NoPen)
        
        # Dreieck zeichnen (nach rechts zeigend)
        triangle = QPolygon([
            QPoint(8, 6),
            QPoint(8, 18),
            QPoint(18, 12)
        ])
        painter.drawPolygon(triangle)
        painter.end()
        
        self.run_button.setIcon(QIcon(pixmap))
        self.run_button.setIconSize(pixmap.size())
    
    def load_project(self, project_path: Path):
        """Lädt Projekt und öffnet game.py"""
        self.project_path = project_path
        self.current_object_id = None
        
        # LSP-Client starten
        self._init_lsp_client()
        
        self._load_code()
        self._load_editor_settings()
    
    def _init_lsp_client(self):
        """Initialisiert den LSP-Client"""
        if not self.project_path:
            return
        
        try:
            self.lsp_client = LSPClient(self.project_path, self)
            
            # Signals verbinden
            self.lsp_client.diagnostics_received.connect(self._on_lsp_diagnostics)
            self.lsp_client.completion_received.connect(self._on_lsp_completion)
            self.lsp_client.hover_received.connect(self._on_lsp_hover)
            
            # Server starten
            if self.lsp_client.start_server():
                print("LSP-Server gestartet")
            else:
                print("WARNUNG: LSP-Server konnte nicht gestartet werden")
                self.lsp_client = None
        except Exception as e:
            print(f"Fehler beim Initialisieren des LSP-Clients: {e}")
            self.lsp_client = None
    
    def set_object(self, object_id: str | None, object_data: dict | None = None):
        """Setzt das aktuell ausgewählte Objekt und lädt dessen Code
        
        WICHTIG: Code ist immer an die ID gebunden, nicht an den Namen!
        Der Name ist nur für die Anzeige (QOL-Feature).
        """
        # Code des vorherigen Objekts speichern (immer mit ID!)
        if self.current_object_id and self.project_path:
            self._save_object_code(self.current_object_id)
        
        # ID setzen (immer ID verwenden, nie Name!)
        self.current_object_id = object_id
        
        if object_id and object_data:
            # Code für dieses Objekt laden (immer mit ID!)
            self._load_object_code(object_id, object_data)
            
            # Label anzeigen: Name falls vorhanden, sonst ID
            display_name = object_data.get("name") or object_id
            self.label.setText(f"Code Editor ({display_name})")
        else:
            # Globale game.py laden
            self._load_code()
            self.label.setText("Code Editor (game.py)")
    
    def _load_code(self):
        """Lädt game.py aus dem Projekt (globale Datei)"""
        if not self.project_path:
            return
        
        code_file = self.project_path / "code" / "game.py"
        
        if code_file.exists():
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Signal temporär blockieren, damit beim Laden kein textChanged ausgelöst wird
                if hasattr(self.editor, 'blockSignals'):
                    self.editor.blockSignals(True)
                
                if hasattr(self.editor, 'setText'):
                    self.editor.setText(code)
                else:
                    self.editor.setPlainText(code)
                
                # Signal wieder aktivieren
                if hasattr(self.editor, 'blockSignals'):
                    self.editor.blockSignals(False)
                
                # Letzten Text für Undo/Redo speichern
                self.last_text = code
                
                # LSP-Document öffnen
                self._open_lsp_document(code_file, code)
                
                # Cache zurücksetzen, damit Highlighting beim Laden ausgeführt wird
                if hasattr(self.editor, 'syntax_highlighter') and self.editor.syntax_highlighter:
                    self.editor.syntax_highlighter.reset_cache()
                
                # Syntax-Highlighting sofort anwenden (nach dem Laden)
                QTimer.singleShot(100, lambda: self._apply_syntax_highlighting())
                
            except Exception as e:
                print(f"Fehler beim Laden von game.py: {e}")
        else:
            # Standard-Code
            default_code = """# game.py - Dein Spiel-Code
# Hier schreibst du die Logik für dein Spiel

player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT"):
        player.x += 4
    
    if key_pressed("LEFT"):
        player.x -= 4
"""
            if hasattr(self.editor, 'setText'):
                self.editor.setText(default_code)
            else:
                self.editor.setPlainText(default_code)
            
            # Letzten Text für Undo/Redo speichern
            self.last_text = default_code
            
            # LSP-Document öffnen (auch für neue Datei)
            self._open_lsp_document(code_file, default_code)
            
            # Cache zurücksetzen, damit Highlighting beim Laden ausgeführt wird
            if hasattr(self.editor, 'syntax_highlighter') and self.editor.syntax_highlighter:
                self.editor.syntax_highlighter.reset_cache()
            
            # Syntax-Highlighting sofort anwenden (nach dem Laden)
            QTimer.singleShot(100, lambda: self._apply_syntax_highlighting())
    
    def _load_object_code(self, object_id: str, object_data: dict):
        """Lädt Code für ein spezifisches Objekt
        
        WICHTIG: Code ist immer an die ID gebunden, nicht an den Namen!
        Der Name ist nur für die Anzeige (QOL-Feature).
        """
        # WICHTIG: Code immer direkt aus JSON-Datei laden, nicht aus object_data!
        # Das stellt sicher, dass der neueste Code geladen wird, auch wenn self.objects
        # noch nicht aktualisiert wurde.
        code = ""
        
        if self.project_path:
            try:
                import json
                project_file = self.project_path / "project.json"
                if project_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    start_scene = config.get("start_scene", "level1")
                    scene_file = self.project_path / "scenes" / f"{start_scene}.json"
                    
                    if scene_file.exists():
                        with open(scene_file, 'r', encoding='utf-8') as f:
                            scene_data = json.load(f)
                        
                        # Objekt in Szene finden und Code laden
                        objects = scene_data.get("objects", [])
                        for obj in objects:
                            if obj.get("id") == object_id:
                                code = obj.get("code", "")
                                break
            except Exception:
                # Bei Fehler Fallback auf object_data
                pass
        
        # Fallback: Code aus Objekt-Daten laden (falls nicht in JSON gefunden)
        if not code:
            code = object_data.get("code", "")
        
        if not code:
            # Standard-Code für Objekt - IMMER mit ID!
            code = f"""# Code für {object_id}
# Hier schreibst du die Logik für dieses Objekt

obj = get_object("{object_id}")

def update():
    # Deine Logik hier
    pass
"""
        
        # Signal temporär blockieren, damit beim Laden kein textChanged ausgelöst wird
        if hasattr(self.editor, 'blockSignals'):
            self.editor.blockSignals(True)
        
        if hasattr(self.editor, 'setText'):
            self.editor.setText(code)
        else:
            self.editor.setPlainText(code)
        
        # Signal wieder aktivieren
        if hasattr(self.editor, 'blockSignals'):
            self.editor.blockSignals(False)
        
        # Letzten Text für Undo/Redo speichern
        self.last_text = code
        
        # Cache zurücksetzen, damit Highlighting beim Laden ausgeführt wird
        if hasattr(self.editor, 'syntax_highlighter') and self.editor.syntax_highlighter:
            self.editor.syntax_highlighter.reset_cache()
        
        # Syntax-Highlighting sofort anwenden (nach dem Laden)
        QTimer.singleShot(100, lambda: self._apply_syntax_highlighting())
    
    def _save_object_code(self, object_id: str):
        """Speichert Code für ein spezifisches Objekt in die Szene"""
        if not self.project_path or not object_id:
            return
        
        # Code aus Editor holen
        if hasattr(self.editor, 'text'):
            code = self.editor.text()
        else:
            code = self.editor.toPlainText()
        
        # Szene laden und Code im Objekt speichern
        try:
            import json
            project_file = self.project_path / "project.json"
            if not project_file.exists():
                return
            
            with open(project_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            start_scene = config.get("start_scene", "level1")
            scene_file = self.project_path / "scenes" / f"{start_scene}.json"
            
            if not scene_file.exists():
                return
            
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            
            # Objekt finden und Code aktualisieren - IMMER mit ID suchen!
            objects = scene_data.get("objects", [])
            found = False
            for obj in objects:
                # WICHTIG: Immer ID verwenden, nie Name!
                if obj.get("id") == object_id:
                    obj["code"] = code
                    found = True
                    break
            
            if not found:
                return
            
            # Szene speichern
            with open(scene_file, 'w', encoding='utf-8') as f:
                json.dump(scene_data, f, indent=2, ensure_ascii=False)
            
            # WICHTIG: Auch self.objects in scene_canvas aktualisieren, damit die Daten synchron bleiben
            if self.scene_canvas:
                for obj in self.scene_canvas.objects:
                    if obj.get("id") == object_id:
                        obj["code"] = code
                        break
            
        except Exception as e:
            # Fehler stillschweigend ignorieren (kann bei gleichzeitigen Zugriffen passieren)
            pass
    
    def set_undo_redo_manager(self, manager):
        """Setzt den Undo/Redo-Manager"""
        self.undo_redo_manager = manager
    
    def set_undo_redo_buttons(self, undo_button, redo_button):
        """Setzt die Undo/Redo Buttons vom main_window"""
        self.undo_button = undo_button
        self.redo_button = redo_button
        
        # Buttons zur Toolbar hinzufügen (nach Stop-Button)
        if undo_button and redo_button and hasattr(self, 'toolbar_layout'):
            # Finde die Position nach dem Stop-Button
            stop_index = self.toolbar_layout.indexOf(self.stop_button)
            if stop_index >= 0:
                self.toolbar_layout.insertWidget(stop_index + 1, undo_button)
                self.toolbar_layout.insertWidget(stop_index + 2, redo_button)
                undo_button.setVisible(True)
                redo_button.setVisible(True)
    
    def _on_text_changed_with_undo(self):
        """Wird aufgerufen wenn Text geändert wird - mit Undo/Redo-Tracking"""
        # Code SOFORT speichern bei jeder Änderung
        if self.project_path:
            if self.current_object_id:
                # Code für aktuelles Objekt sofort speichern
                self._save_object_code(self.current_object_id)
            else:
                # Globale game.py sofort speichern
                self.save_code()
        
        # Debouncing: Warte 500ms bevor Text-Änderung als Undo-Punkt gespeichert wird
        self.text_change_timer.stop()
        self.text_change_timer.start(500)
        self.code_changed.emit()
    
    def _on_text_changed_delayed(self):
        """Wird nach Debouncing aufgerufen - speichert Text-Änderung für Undo/Redo"""
        if not self.undo_redo_manager:
            return
        
        # Aktuellen Text holen
        if hasattr(self.editor, 'text'):
            current_text = self.editor.text()
        else:
            current_text = self.editor.toPlainText()
        
        # Nur speichern wenn Text sich wirklich geändert hat
        if current_text != self.last_text:
            from ..utils.commands import TextChangeCommand
            
            old_text = self.last_text
            new_text = current_text
            
            # Command erstellen
            command = TextChangeCommand(
                self.editor,
                old_text,
                new_text,
                f"Text geändert ({'Objekt: ' + self.current_object_id if self.current_object_id else 'game.py'})"
            )
            
            # Command zur Historie hinzufügen (ohne execute, da Text bereits geändert ist)
            # Verwende die execute_command-Methode, aber ohne execute() aufzurufen
            # da der Text bereits geändert wurde
            self.undo_redo_manager.undo_stack.append(command)
            self.undo_redo_manager.redo_stack.clear()
            
            # Historie begrenzen
            if len(self.undo_redo_manager.undo_stack) > self.undo_redo_manager.max_history:
                self.undo_redo_manager.undo_stack.pop(0)
            
            self.last_text = new_text
            self.undo_redo_changed.emit()  # Signal für Button-Update
    
    def _on_modification_changed(self, modified: bool):
        """Wird aufgerufen wenn Dokument geändert wird - aktualisiert Syntax-Highlighting"""
        # QScintilla aktualisiert Syntax-Highlighting automatisch, aber wir können es explizit triggern
    
    def _toggle_help_overlay(self):
        """Zeigt/versteckt das Hilfe-Fenster"""
        if self.help_overlay is None:
            self._create_help_overlay()
        
        if self.help_overlay.isVisible():
            self.help_overlay.hide()
        else:
            self.help_overlay.show()
            self.help_overlay.raise_()  # Fenster nach vorne bringen
            self.help_overlay.activateWindow()  # Fokus setzen
    
    def _create_help_overlay(self):
        """Erstellt das Hilfe-Fenster mit allen Pygame-Befehlen"""
        # Separates Fenster (QDialog)
        self.help_overlay = QDialog(self)
        self.help_overlay.setWindowTitle("Pygame-Befehle - Hilfe")
        self.help_overlay.setModal(False)  # Nicht-modal, damit Editor weiterhin benutzbar ist
        self.help_overlay.setMinimumSize(600, 700)
        self.help_overlay.resize(700, 800)
        self.help_overlay.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(15, 15, 15, 15)
        dialog_layout.setSpacing(10)
        
        # Header mit Titel und Schließen-Button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Pygame-Befehle")
        title_label.setStyleSheet("font-weight: bold; font-size: 16pt; color: #4a9eff;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        close_button = QPushButton("✕")
        close_button.setToolTip("Schließen")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        close_button.clicked.connect(self.help_overlay.close)
        header_layout.addWidget(close_button)
        
        dialog_layout.addLayout(header_layout)
        
        # ScrollArea für den Inhalt
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #4a9eff;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5aaeff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Content-Widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(0)  # Kein Spacing, damit TextEdit den gesamten Platz nutzt
        
        # Hilfe-Text mit allen Befehlen
        help_text = self._generate_help_text()
        
        # QTextEdit statt QLabel für Textauswahl
        help_text_edit = QTextEdit()
        help_text_edit.setReadOnly(True)  # Read-only, aber Text auswählbar
        help_text_edit.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        help_text_edit.setHtml(help_text)
        help_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                border: none;
                selection-background-color: #4a9eff;
                selection-color: white;
            }
        """)
        
        # TextEdit soll den gesamten verfügbaren Platz nutzen
        content_layout.addWidget(help_text_edit, stretch=1)  # stretch=1 für gesamten Platz
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        dialog_layout.addWidget(scroll_area)
        
        self.help_overlay.setLayout(dialog_layout)
    
    def _generate_help_text(self) -> str:
        """Generiert den Hilfe-Text mit allen verfügbaren Befehlen"""
        help_html = """
        <h2 style="color: #4a9eff; margin-top: 0;">Objekt-Funktionen</h2>
        
        <h3 style="color: #90caf9;">get_object(id)</h3>
        <p>Gibt ein Objekt anhand seiner ID zurück.</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
player = get_object("player")</pre>
        
        <h3 style="color: #90caf9;">get_all_objects()</h3>
        <p>Gibt alle sichtbaren Objekte zurück.</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
all_objects = get_all_objects()</pre>
        
        <h2 style="color: #4a9eff;">Input-Funktionen</h2>
        
        <h3 style="color: #90caf9;">key_pressed(key)</h3>
        <p>Prüft ob eine Taste gedrückt gehalten wird.</p>
        <p><b>Verfügbare Tasten:</b> "LEFT", "RIGHT", "UP", "DOWN", "SPACE", "ENTER", "W", "A", "S", "D", "F1"</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
if key_pressed("RIGHT") or key_pressed("D"):
    player.x += 4</pre>
        
        <h3 style="color: #90caf9;">key_down(key)</h3>
        <p>Prüft ob eine Taste gerade gedrückt wurde (nur einmal beim Drücken).</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
if key_down("SPACE"):
    print_debug("Springen!")</pre>
        
        <h3 style="color: #90caf9;">mouse_position()</h3>
        <p>Gibt die aktuelle Mausposition zurück (x, y).</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
mx, my = mouse_position()</pre>
        
        <h2 style="color: #4a9eff;">GameObject-Eigenschaften</h2>
        
        <p>Jedes Objekt hat folgende Eigenschaften:</p>
        <ul style="color: #d4d4d4;">
            <li><b>id</b> - Eindeutige ID des Objekts</li>
            <li><b>x, y</b> - Position (float)</li>
            <li><b>width, height</b> - Größe (float)</li>
            <li><b>visible</b> - Sichtbarkeit (bool)</li>
            <li><b>sprite</b> - Sprite-Pfad (string)</li>
            <li><b>is_ground</b> - Boden-Tile (bool) - True wenn Objekt als Boden markiert ist</li>
        </ul>
        
        <h2 style="color: #4a9eff;">GameObject-Methoden</h2>
        
        <h3 style="color: #90caf9;">collides_with(other_id)</h3>
        <p>Prüft ob dieses Objekt mit einem anderen kollidiert.</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
if player.collides_with("enemy1"):
    print_debug("Kollision!")</pre>
        
        <h3 style="color: #90caf9;">destroy()</h3>
        <p>Entfernt das Objekt aus dem Spiel.</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
enemy.destroy()</pre>
        
        <h2 style="color: #4a9eff;">Debug-Funktionen</h2>
        
        <h3 style="color: #90caf9;">print_debug(text)</h3>
        <p>Gibt Debug-Text aus (erscheint in Editor-Console).</p>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
print_debug("Spieler-Position: " + str(player.x))</pre>
        
        <h2 style="color: #4a9eff;">Beispiel-Code</h2>
        
        <h3 style="color: #90caf9;">Einfache Bewegung</h3>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
player = get_object("player")

def update():
    # Bewegung mit Pfeiltasten
    if key_pressed("RIGHT") or key_pressed("D"):
        player.x += 4
    
    if key_pressed("LEFT") or key_pressed("A"):
        player.x -= 4
    
    # Kollision prüfen
    if player.collides_with("enemy1"):
        print_debug("Kollision!")
        player.destroy()</pre>
        
        <h3 style="color: #90caf9;">Bewegung mit Schwerkraft und Boden-Kollision</h3>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
bear = get_object("object_15")

# Geschwindigkeit
speed = 3
gravity = 0.5
velocity_y = 0
on_ground = False

def update():
    global velocity_y, on_ground
    
    # Horizontal-Bewegung
    dx = 0
    if key_pressed("LEFT"):
        dx = -speed
    if key_pressed("RIGHT"):
        dx = speed
    
    # Schwerkraft
    if not on_ground:
        velocity_y += gravity
    
    # Bewegung mit automatischer Kollisionsbehandlung
    on_ground, collision_x, collision_y = move_with_collision(bear, dx, velocity_y)
    
    # Wenn auf Boden, Geschwindigkeit zurücksetzen
    if on_ground:
        velocity_y = 0
    
    # Sprung
    if key_down("SPACE") and on_ground:
        velocity_y = -10
        on_ground = False</pre>
        
        <h3 style="color: #90caf9;">Bewegliche Plattform</h3>
        <pre style="background-color: #1e1e1e; padding: 10px; border-radius: 3px; color: #d4d4d4;">
platform = get_object("object_13")

platform_speed = 2
platform_direction = 1
platform_start_x = 672
platform_end_x = 800

def update():
    global platform_direction
    
    # Bewegung hin und her
    platform.x += platform_speed * platform_direction
    
    # Umkehren wenn am Ende
    if platform.x >= platform_end_x:
        platform_direction = -1
    elif platform.x <= platform_start_x:
        platform_direction = 1</pre>
        """
        return help_html
    
    def _on_text_changed(self):
        """Wird aufgerufen wenn Text geändert wird (für Kompatibilität)"""
        self.code_changed.emit()
    
    @Slot()
    def _auto_save(self):
        """Auto-Save alle 5 Sekunden"""
        if self.project_path:
            if self.current_object_id:
                # Code für aktuelles Objekt speichern
                self._save_object_code(self.current_object_id)
            else:
                # Globale game.py speichern
                self.save_code()
    
    def save_code(self):
        """Speichert game.py (globale Datei)"""
        if not self.project_path:
            return
        
        code_file = self.project_path / "code" / "game.py"
        code_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if hasattr(self.editor, 'text'):
                code = self.editor.text()
            else:
                code = self.editor.toPlainText()
            
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
        except Exception as e:
            print(f"Fehler beim Speichern von game.py: {e}")
    
    def get_code(self) -> str:
        """Gibt den aktuellen Code zurück"""
        if hasattr(self.editor, 'text'):
            return self.editor.text()
        else:
            return self.editor.toPlainText()
    
    def set_run_enabled(self, enabled: bool):
        """Aktiviert/deaktiviert den Start-Button"""
        self.run_button.setEnabled(enabled)
    
    def set_stop_enabled(self, enabled: bool):
        """Aktiviert/deaktiviert den Stop-Button"""
        self.stop_button.setEnabled(enabled)
    
    
    def _open_settings(self):
        """Öffnet Einstellungs-Dialog"""
        from .code_editor_settings import CodeEditorSettingsDialog
        
        if not self.project_path:
            return
        
        dialog = CodeEditorSettingsDialog(self.project_path, self)
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()
    
    def _apply_settings(self, settings: dict):
        """Wendet Einstellungen an"""
        # Font-Größe
        font_size = settings.get("font_size", 11)
        font = QFont("Consolas", font_size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        
        # QTextEdit: Font setzen
        if hasattr(self.editor, 'setFont'):
            self.editor.setFont(font)
        
        # Farben über Stylesheet
        def hex_to_color_str(hex_str: str) -> str:
            """Konvertiert Hex-String zu CSS-Farbstring"""
            hex_str = hex_str.lstrip('#')
            if len(hex_str) == 6:
                return f"#{hex_str}"
            return "#d4d4d4"  # Fallback
        
        bg_color = hex_to_color_str(settings.get("background", "#1e1e1e"))
        # WICHTIG: Textfarbe NICHT über Stylesheet setzen, da das die Syntax-Highlighting-Formatierungen überschreibt
        # Die Textfarbe wird stattdessen über die Syntax-Highlighter-Formate gesetzt
        
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)
        
        # Syntax-Highlighter-Farben aktualisieren (inkl. Standard-Textfarbe)
        if hasattr(self.editor, 'syntax_highlighter') and self.editor.syntax_highlighter:
            syntax_colors = {
                "default": settings.get("default", "#d4d4d4"),  # Standard-Textfarbe
                "comment": settings.get("comment", "#646464"),
                "number": settings.get("number", "#b5cea8"),
                "string": settings.get("string", "#ec7600"),
                "keyword": settings.get("keyword", "#4faff0"),
                "class": settings.get("class", "#4ec9b0"),
                "function": settings.get("function", "#dcdc64"),
                "variable": settings.get("variable", "#9cdcfe"),
                "operator": settings.get("operator", "#b4b4ff"),
            }
            self.editor.syntax_highlighter.update_formats(syntax_colors)
            
            # Syntax-Highlighting neu anwenden
            if hasattr(self.editor, 'text'):
                text = self.editor.text()
            else:
                text = self.editor.toPlainText()
            self.editor.apply_syntax_highlighting(text)
    
    def _load_editor_settings(self):
        """Lädt Editor-Einstellungen beim Start"""
        if not self.project_path:
            return
        
        settings_file = self.project_path / "code_editor_settings.json"
        if settings_file.exists():
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # Aktuelles Preset laden
                current_preset = settings_data.get("current_preset", "default")
                custom_presets = settings_data.get("custom_presets", {})
                
                # Preset-Daten holen
                if current_preset in custom_presets:
                    preset = custom_presets[current_preset]
                elif current_preset == "light_mode":
                    from .code_editor_settings import CodeEditorSettingsDialog
                    dialog = CodeEditorSettingsDialog(self.project_path, self)
                    preset = dialog._get_light_mode_preset()
                elif current_preset == "high_contrast":
                    from .code_editor_settings import CodeEditorSettingsDialog
                    dialog = CodeEditorSettingsDialog(self.project_path, self)
                    preset = dialog._get_high_contrast_preset()
                elif current_preset == "matrix_mode":
                    from .code_editor_settings import CodeEditorSettingsDialog
                    dialog = CodeEditorSettingsDialog(self.project_path, self)
                    preset = dialog._get_matrix_mode_preset()
                else:
                    # Default
                    from .code_editor_settings import CodeEditorSettingsDialog
                    dialog = CodeEditorSettingsDialog(self.project_path, self)
                    preset = dialog._get_default_preset()
                
                # Einstellungen anwenden
                self._apply_settings(preset)
            except Exception as e:
                print(f"Fehler beim Laden der Editor-Einstellungen: {e}")
    
    # ========== LSP-Methoden ==========
    
    def _open_lsp_document(self, file_path: Path, text: str):
        """Öffnet ein Dokument im LSP-Server"""
        if not self.lsp_client:
            return
        
        # URI erstellen (file:///path/to/file)
        uri = f"file://{file_path.absolute().as_posix()}"
        self.lsp_document_uri = uri
        self.lsp_document_version = 1
        
        # Document im Server öffnen
        self.lsp_client.open_document(uri, text, "python")
    
    def _update_lsp_document(self):
        """Aktualisiert das Dokument im LSP-Server (mit Debouncing)"""
        if not self.lsp_client or not self.lsp_document_uri or self._updating_lsp:
            return
        
        self._updating_lsp = True
        try:
            # Text aus Editor holen
            if hasattr(self.editor, 'text'):
                text = self.editor.text()
            else:
                text = self.editor.toPlainText()
            
            # Version erhöhen
            self.lsp_document_version += 1
            
            # Document aktualisieren
            self.lsp_client.update_document(self.lsp_document_uri, text, self.lsp_document_version)
        finally:
            self._updating_lsp = False
    
    def _on_text_changed_for_lsp(self):
        """Wird aufgerufen wenn Text geändert wird (für LSP)"""
        if not self.lsp_client or self._updating_lsp:
            return
        
        # Debouncing: Warte 300ms bevor LSP-Update gesendet wird
        self.lsp_update_timer.stop()
        self.lsp_update_timer.start(300)
    
    def _on_text_changed_for_syntax(self):
        """Wird aufgerufen wenn Text geändert wird (für Syntax-Highlighting)"""
        # WICHTIG: Verhindere Endlosschleife - wenn Highlighting bereits läuft, nicht erneut starten
        if self._updating_syntax:
            return
        
        # Prüfe ob Text sich tatsächlich geändert hat (textChanged wird auch bei Format-Änderungen getriggert!)
        current_text = self.editor.toPlainText() if hasattr(self.editor, 'toPlainText') else ""
        if current_text == self.last_syntax_text:
            # Text hat sich nicht geändert - überspringen (verhindert Flackern)
            return
        
        # Text als "letzten" Text speichern
        self.last_syntax_text = current_text
        
        # Debouncing: Timer zurücksetzen (wird nach 30ms ausgeführt)
        self.syntax_update_timer.stop()
        self.syntax_update_timer.start(30)  # Sehr kurze Verzögerung für bessere Reaktionszeit
    
    def _apply_syntax_highlighting(self):
        """Wendet Syntax-Highlighting an (wird nach Debouncing aufgerufen)"""
        if self._updating_syntax:
            return
        
        self._updating_syntax = True
        
        # WICHTIG: Blockiere textChanged Signale des Editors während des Highlightings
        # Das verhindert, dass das Formatieren eine Endlosschleife auslöst
        editor_signals_blocked = False
        if hasattr(self.editor, 'blockSignals'):
            editor_signals_blocked = self.editor.blockSignals(True)
        
        try:
            if hasattr(self.editor, 'text'):
                text = self.editor.text()
            else:
                text = self.editor.toPlainText()
            
            # Syntax-Highlighting anwenden (einfache Regex-Version)
            if hasattr(self.editor, 'apply_syntax_highlighting'):
                self.editor.apply_syntax_highlighting(text)
            
            # WICHTIG: last_syntax_text nach dem Highlighting aktualisieren, damit textChanged nicht erneut getriggert wird
            self.last_syntax_text = text
        finally:
            # Signale wieder aktivieren
            if hasattr(self.editor, 'blockSignals'):
                self.editor.blockSignals(editor_signals_blocked)
            
            self._updating_syntax = False
    
    def _trigger_lsp_completion(self):
        """Triggert LSP-Auto-Vervollständigung"""
        if not self.lsp_client or not self.lsp_document_uri:
            return
        
        cursor = self.editor.textCursor()
        line = cursor.blockNumber()
        character = cursor.positionInBlock()
        
        def on_completion(result, error):
            if error:
                return
            
            # Completion-Items verarbeiten
            items = result.get("items", []) if result else []
            if items:
                # QCompleter mit LSP-Items aktualisieren
                completions = []
                for item in items:
                    label = item.get("label", "")
                    detail = item.get("detail", "")
                    if detail:
                        completions.append(f"{label} - {detail}")
                    else:
                        completions.append(label)
                
                # Completer aktualisieren (QTextEdit hat keine setCompleter-Methode)
                # Wir speichern die Completions und zeigen sie manuell an
                if not hasattr(self, 'lsp_completer') or not self.lsp_completer:
                    from PySide6.QtWidgets import QCompleter
                    from PySide6.QtCore import QStringListModel
                    model = QStringListModel(completions, self)
                    self.lsp_completer = QCompleter(model, self)
                    self.lsp_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                    self.lsp_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
                    self.lsp_completer.setWidget(self.editor)  # Widget setzen, aber nicht setCompleter verwenden
                    self.editor.lsp_completer = self.lsp_completer
                else:
                    model = QStringListModel(completions, self)
                    self.lsp_completer.setModel(model)
                
                # Completion manuell anzeigen (QTextEdit hat keine setCompleter)
                # Wir zeigen die Completion über ein Popup an
                cursor = self.editor.textCursor()
                rect = self.editor.cursorRect(cursor)
                self.lsp_completer.complete(rect)  # Popup an Cursor-Position anzeigen
        
        self.lsp_client.request_completion(self.lsp_document_uri, line, character, on_completion)
    
    def _on_lsp_diagnostics(self, params: dict):
        """Wird aufgerufen wenn LSP Diagnostics empfangen werden"""
        uri = params.get("uri", "")
        diagnostics = params.get("diagnostics", [])
        
        # Nur Diagnostics für aktuelles Document anzeigen
        if uri == self.lsp_document_uri:
            # Unterstreichungen im Editor anwenden
            if hasattr(self.editor, 'apply_diagnostics'):
                self.editor.apply_diagnostics(diagnostics)
    
    def _on_lsp_completion(self, items: list):
        """Wird aufgerufen wenn LSP Completion empfangen wird"""
        # Wird bereits in _trigger_lsp_completion behandelt
        pass
    
    def _on_lsp_hover(self, result: dict):
        """Wird aufgerufen wenn LSP Hover-Informationen empfangen werden"""
        # Kann später für Tooltips verwendet werden
        pass
    