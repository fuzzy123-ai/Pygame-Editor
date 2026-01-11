"""
Code Editor - Python Editor mit QScintilla Syntax-Highlighting
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
                               QDialog, QScrollArea, QToolButton)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QPoint
from PySide6.QtGui import QIcon, QPainter, QColor, QPolygon, QFont
from pathlib import Path
import sys

# QScintilla Import
try:
    from PySide6.Qsci import QsciScintilla, QsciLexerPython
except ImportError:
    # Fallback falls QScintilla nicht verfügbar
    QsciScintilla = None
    QsciLexerPython = None


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
        self.last_text = ""  # Letzter Text für Undo/Redo
        self.text_change_timer = QTimer()
        self.text_change_timer.setSingleShot(True)
        self.text_change_timer.timeout.connect(self._on_text_changed_delayed)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(5000)  # Alle 5 Sekunden
        
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
        
        # QScintilla Editor
        if QsciScintilla:
            self.editor = QsciScintilla()
            
            # Python Lexer mit verbessertem Syntax-Highlighting
            lexer = QsciLexerPython()
            
            # Monospace-Font für bessere Lesbarkeit
            from PySide6.QtGui import QFont
            font = QFont("Consolas", 11)
            font.setStyleHint(QFont.StyleHint.Monospace)
            lexer.setFont(font, 0)  # Standard-Font für alle Styles
            
            # Syntax-Highlighting-Farben (dunkles Theme) - Alle Styles konfigurieren
            # QsciLexerPython Style-Indizes:
            # 0 = Default, 1 = Comment, 2 = Number, 3 = String, 4 = Keyword, 
            # 5 = Triple quotes, 6 = Triple double quotes, 7 = Class name,
            # 8 = Function/method name, 9 = Operator, 10 = Identifier, 11 = Comment block,
            # 12 = Unclosed string, 13 = Highlighted identifier, 14 = Decorator
            
            # Default Text
            lexer.setColor(QColor(212, 212, 212), 0)  # #d4d4d4 - Helles Grau
            lexer.setPaper(QColor(30, 30, 30), 0)  # #1e1e1e - Dunkler Hintergrund
            
            # Kommentare
            lexer.setColor(QColor(106, 153, 85), 1)  # #6a9955 - Grün für Kommentare
            lexer.setPaper(QColor(30, 30, 30), 1)
            
            # Zahlen
            lexer.setColor(QColor(181, 206, 168), 2)  # #b5cea8 - Hellgrün für Zahlen
            lexer.setPaper(QColor(30, 30, 30), 2)
            
            # Strings
            lexer.setColor(QColor(206, 145, 120), 3)  # #ce9178 - Orange für Strings
            lexer.setPaper(QColor(30, 30, 30), 3)
            
            # Keywords (if, def, for, etc.)
            lexer.setColor(QColor(86, 156, 214), 4)  # #569cd6 - Blau für Keywords
            lexer.setPaper(QColor(30, 30, 30), 4)
            
            # Triple quotes
            lexer.setColor(QColor(206, 145, 120), 5)  # Orange wie Strings
            lexer.setPaper(QColor(30, 30, 30), 5)
            lexer.setColor(QColor(206, 145, 120), 6)  # Triple double quotes
            lexer.setPaper(QColor(30, 30, 30), 6)
            
            # Class names
            lexer.setColor(QColor(78, 201, 176), 7)  # #4ec9b0 - Türkis für Klassen
            lexer.setPaper(QColor(30, 30, 30), 7)
            
            # Function/method names
            lexer.setColor(QColor(220, 220, 170), 8)  # #dcdcaa - Gelb für Funktionen
            lexer.setPaper(QColor(30, 30, 30), 8)
            
            # Operators
            lexer.setColor(QColor(212, 212, 212), 9)  # #d4d4d4 - Weiß für Operatoren
            lexer.setPaper(QColor(30, 30, 30), 9)
            
            # Identifiers (Variablen)
            lexer.setColor(QColor(156, 220, 254), 10)  # #9cdcfe - Hellblau für Variablen
            lexer.setPaper(QColor(30, 30, 30), 10)
            
            # Comment blocks
            lexer.setColor(QColor(106, 153, 85), 11)  # Grün wie Kommentare
            lexer.setPaper(QColor(30, 30, 30), 11)
            
            # Unclosed strings
            lexer.setColor(QColor(206, 145, 120), 12)  # Orange
            lexer.setPaper(QColor(30, 30, 30), 12)
            
            # Highlighted identifier
            lexer.setColor(QColor(156, 220, 254), 13)  # Hellblau
            lexer.setPaper(QColor(30, 30, 30), 13)
            
            # Decorator
            lexer.setColor(QColor(220, 220, 170), 14)  # Gelb
            lexer.setPaper(QColor(30, 30, 30), 14)
            
            # Standard-Hintergrund für alle Styles
            lexer.setDefaultPaper(QColor(30, 30, 30))  # #1e1e1e
            lexer.setDefaultColor(QColor(212, 212, 212))  # #d4d4d4
            
            self.editor.setLexer(lexer)
            
            # Einstellungen für bessere Formatierung
            self.editor.setUtf8(True)
            self.editor.setAutoIndent(True)
            self.editor.setIndentationGuides(True)
            self.editor.setTabWidth(4)
            self.editor.setIndentationsUseTabs(False)
            
            # Auto-Formatierung aktivieren (Dark-Mode)
            self.editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
            self.editor.setMatchedBraceBackgroundColor(QColor(60, 60, 60))  # Heller für bessere Sichtbarkeit
            self.editor.setMatchedBraceForegroundColor(QColor(255, 255, 0))  # Gelb für Klammern
            
            # Auto-Completion
            self.editor.setAutoCompletionThreshold(2)  # Früher aktivieren
            self.editor.setAutoCompletionSource(QsciScintilla.AcsAll)
            self.editor.setAutoCompletionCaseSensitivity(False)
            self.editor.setAutoCompletionReplaceWord(True)
            
            # Zeilennummern (Dark-Mode)
            self.editor.setMarginsBackgroundColor(QColor(30, 30, 30))  # #1e1e1e
            self.editor.setMarginsForegroundColor(QColor(128, 128, 128))  # Grau für Zeilennummern
            self.editor.setMarginLineNumbers(0, True)
            # Margin-Breite dynamisch basierend auf Zeilenanzahl (mindestens 4 Ziffern)
            self.editor.setMarginWidth(0, "00000")  # 5 Ziffern für bis zu 99999 Zeilen
            
            # Farbschema (Dark-Mode)
            self.editor.setPaper(QColor(30, 30, 30))  # #1e1e1e - Dunkler Hintergrund
            self.editor.setColor(QColor(212, 212, 212))  # #d4d4d4 - Helles Text
            
            # Caret (Cursor) sichtbarer machen (Dark-Mode)
            self.editor.setCaretForegroundColor(QColor(255, 255, 255))
            self.editor.setCaretLineVisible(True)
            self.editor.setCaretLineBackgroundColor(QColor(42, 42, 42))  # Etwas heller als Hintergrund
            
            # Selection (Auswahl) - Dark-Mode
            self.editor.setSelectionBackgroundColor(QColor(38, 79, 120))  # Blau für Auswahl
            self.editor.setSelectionForegroundColor(QColor(255, 255, 255))
            
            # Text geändert (mit Debouncing für Undo/Redo)
            self.editor.textChanged.connect(self._on_text_changed_with_undo)
            
            # Event-Handler für Einfügen (Auto-Formatierung)
            self.editor.modificationChanged.connect(self._on_modification_changed)
            
            # EOL (End of Line) Mode
            self.editor.setEolMode(QsciScintilla.EolMode.EolUnix)  # Unix-Style (\n)
            
            # Syntax-Highlighting ist bereits aktiv durch setLexer() oben
            # QScintilla aktualisiert Syntax-Highlighting automatisch bei Textänderungen
            # Der Lexer ist bereits konfiguriert und arbeitet live während des Schreibens
            
        else:
            # Fallback: Einfacher QTextEdit wenn QScintilla nicht verfügbar (Dark-Mode)
            from PySide6.QtWidgets import QTextEdit
            from PySide6.QtGui import QFont
            
            self.editor = QTextEdit()
            self.editor.setFont(QFont("Consolas", 10))
            self.editor.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3d3d3d;
                }
            """)
            self.editor.textChanged.connect(self._on_text_changed_with_undo)
            # QScintilla ist optional - keine Warnung ausgeben
            pass
        
        layout.addWidget(self.editor)
        self.setLayout(layout)
    
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
        self._load_code()
    
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
                
                if hasattr(self.editor, 'setText'):
                    self.editor.setText(code)
                else:
                    self.editor.setPlainText(code)
                
                # Letzten Text für Undo/Redo speichern
                self.last_text = code
                
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
    
    def _load_object_code(self, object_id: str, object_data: dict):
        """Lädt Code für ein spezifisches Objekt
        
        WICHTIG: Code ist immer an die ID gebunden, nicht an den Namen!
        Der Name ist nur für die Anzeige (QOL-Feature).
        """
        # Code aus Objekt-Daten laden (falls vorhanden)
        # WICHTIG: Immer mit ID suchen, nie mit Name!
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
        
        if hasattr(self.editor, 'setText'):
            self.editor.setText(code)
        else:
            self.editor.setPlainText(code)
        
        # Letzten Text für Undo/Redo speichern
        self.last_text = code
        
        # Syntax-Highlighting aktualisieren nach dem Laden
        if QsciScintilla and hasattr(self.editor, 'colourise'):
            try:
                self.editor.colourise(0, -1)
            except:
                pass
    
    def _save_object_code(self, object_id: str):
        """Speichert Code für ein spezifisches Objekt in die Szene"""
        if not self.project_path:
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
            
            if scene_file.exists():
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
                    print(f"Warnung: Objekt mit ID '{object_id}' nicht in Szene gefunden!")
                
                # Szene speichern
                with open(scene_file, 'w', encoding='utf-8') as f:
                    json.dump(scene_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern des Objekt-Codes: {e}")
    
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
        if hasattr(self, 'editor') and self.editor and QsciScintilla:
            try:
                # Aktualisiere Syntax-Highlighting für den gesamten Text
                # Dies stellt sicher, dass alle Änderungen sofort farbig werden
                self.editor.colourise(0, -1)
            except:
                pass  # Falls Fehler, ignorieren (QScintilla macht es automatisch)
    
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
        content_layout.setSpacing(15)
        
        # Hilfe-Text mit allen Befehlen
        help_text = self._generate_help_text()
        
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
                line-height: 1.6;
            }
        """)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        
        content_layout.addWidget(help_label)
        content_layout.addStretch()
        
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