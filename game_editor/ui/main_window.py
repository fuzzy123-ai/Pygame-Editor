"""
Editor Hauptfenster - Godot-ähnliches Dock-Layout
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QSplitter, QMenuBar, QStatusBar, QToolBar,
                                QPushButton, QLabel, QFileDialog, QMessageBox,
                                QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
import sys
import os
import shutil
from .game_output_reader import GameOutputReader
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from pathlib import Path
from typing import Dict, Optional

from .scene_canvas import SceneCanvas
from .asset_browser import AssetBrowser
from .code_editor import CodeEditor
# Inspector entfernt - wird durch Rechtsklick-Menü ersetzt
from .console import Console
from .sprite_viewer_tab import SpriteViewerTab
from ..utils.undo_redo import UndoRedoManager


class EditorMainWindow(QMainWindow):
    """Hauptfenster des Editors mit Godot-ähnlichem Layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameDev-Edu Editor")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Dark-Mode für das gesamte Hauptfenster
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border-bottom: 1px solid #3d3d3d;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border-top: 1px solid #3d3d3d;
            }
            QToolBar {
                background-color: #1e1e1e;
                border: none;
                spacing: 2px;
                padding: 2px;
            }
            QSplitter::handle {
                background-color: #3d3d3d;
            }
            QSplitter::handle:hover {
                background-color: #4a9eff;
            }
        """)
        
        # Fenster-Eigenschaften - sicherstellen dass Close-Button aktiv ist
        flags = self.windowFlags()
        flags = flags & ~Qt.WindowStaysOnTopHint  # WindowStaysOnTop entfernen
        flags = flags | Qt.WindowCloseButtonHint  # Close-Button sicherstellen
        self.setWindowFlags(flags)
        
        # Projekt-Verwaltung
        self.project_path: Path | None = None
        
        # UI-Komponenten
        self.scene_canvas: SceneCanvas | None = None
        self.asset_browser: AssetBrowser | None = None
        self.code_editor: CodeEditor | None = None
        # Inspector entfernt
        self.console: Console | None = None
        
        # Run/Stop System
        self.game_process = None
        self.output_reader: Optional[GameOutputReader] = None
        self.run_timer = QTimer()
        self.run_timer.timeout.connect(self._check_game_process)
        
        # Undo/Redo System
        self.undo_redo_manager = UndoRedoManager(max_history=50)
        
        # Drag & Drop aktivieren
        self.setAcceptDrops(True)
        
        # Setup UI
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_central_widget()
        
        # Zuletzt geöffnetes Projekt laden
        QTimer.singleShot(100, self._load_last_project)
        
        # Fenster in den Vordergrund bringen
        QTimer.singleShot(200, self._bring_to_front)
    
    def _bring_to_front(self):
        """Bringt das Fenster in den Vordergrund"""
        self.raise_()
        self.activateWindow()
        
        # Windows-spezifisch
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = int(self.winId())
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.BringWindowToTop(hwnd)
            except:
                pass
    
    def _create_menu_bar(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        new_action = QAction("&Neues Projekt...", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Projekt öffnen...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Speichern", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Bearbeiten-Menü
        edit_menu = menubar.addMenu("&Bearbeiten")
        
        # Undo-Aktion
        undo_action = QAction("&Rückgängig", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        self.undo_action = undo_action
        
        # Redo-Aktion
        redo_action = QAction("&Wiederherstellen", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        self.redo_action = redo_action
        
        # Ansicht-Menü
        view_menu = menubar.addMenu("&Ansicht")
    
    def _create_toolbar(self):
        """Erstellt die Toolbar mit Undo/Redo Buttons rechtsbündig"""
        toolbar = self.addToolBar("Main")
        toolbar.setIconSize(QSize(24, 24))  # Größere Icons
        toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Nur Icons, kein Text
        toolbar.setFixedHeight(36)  # Höhere Toolbar für größere Buttons
        toolbar.setMovable(False)  # Nicht verschiebbar
        
        # Toolbar-Stylesheet für minimale Höhe
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1e1e1e;
                border: none;
                spacing: 3px;
                padding: 3px;
            }
        """)
        
        # Spacer links, damit Buttons rechts sind - expandierend
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        # Undo-Button (50% größer = 30x30)
        self.undo_button = QPushButton("↶")
        self.undo_button.setToolTip("Rückgängig (Ctrl+Z)")
        self.undo_button.setFixedSize(30, 30)
        # Stylesheet mit Farben: weiß wenn enabled, anthrazit wenn disabled
        self.undo_button.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                padding: 0px;
                margin: 0px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #404040;
            }
            QPushButton:enabled {
                color: #ffffff;
            }
            QPushButton:enabled:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
            }
            QPushButton:enabled:pressed {
                background-color: #4d4d4d;
            }
        """)
        self.undo_button.clicked.connect(self._undo)
        self.undo_button.setEnabled(False)
        toolbar.addWidget(self.undo_button)
        
        # Redo-Button (50% größer = 30x30)
        self.redo_button = QPushButton("↷")
        self.redo_button.setToolTip("Wiederherstellen (Ctrl+Y)")
        self.redo_button.setFixedSize(30, 30)
        # Stylesheet mit Farben: weiß wenn enabled, anthrazit wenn disabled
        self.redo_button.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                padding: 0px;
                margin: 0px;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #404040;
            }
            QPushButton:enabled {
                color: #ffffff;
            }
            QPushButton:enabled:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
            }
            QPushButton:enabled:pressed {
                background-color: #4d4d4d;
            }
        """)
        self.redo_button.clicked.connect(self._redo)
        self.redo_button.setEnabled(False)
        toolbar.addWidget(self.redo_button)
        
        # Run-Button und Stop-Button (werden nicht mehr in der Toolbar angezeigt)
        # Sie werden im Code-Editor verwendet
        self.run_button = QPushButton("▶")
        self.run_button.setToolTip("Spiel starten")
        self.run_button.setFixedSize(30, 30)
        self.run_button.setVisible(False)  # Nicht sichtbar in Toolbar
        self.run_button.clicked.connect(self._run_game)
        self.run_button.setEnabled(False)
        
        self.stop_button = QPushButton("■")
        self.stop_button.setToolTip("Spiel stoppen")
        self.stop_button.setFixedSize(30, 30)
        self.stop_button.setVisible(False)  # Nicht sichtbar in Toolbar
        self.stop_button.clicked.connect(self._stop_game)
        self.stop_button.setEnabled(False)
    
    def _create_status_bar(self):
        """Erstellt die Statusleiste"""
        # Projekt-Label in Statusleiste
        self.project_label = QLabel("Kein Projekt geöffnet")
        self.statusBar().addPermanentWidget(self.project_label)
        self.statusBar().showMessage("Bereit")
    
    def _create_central_widget(self):
        """Erstellt das zentrale Widget mit Godot-ähnlichem Layout"""
        # Haupt-Splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)  # Panels können nicht komplett geschlossen werden
        
        # Linker Bereich: Asset Browser
        self.asset_browser = AssetBrowser()
        self.asset_browser.setMaximumWidth(300)
        self.asset_browser.setMinimumWidth(150)  # Mindestbreite damit es sichtbar bleibt
        main_splitter.addWidget(self.asset_browser)
        
        # Mittlerer Bereich: Scene Canvas (komplett, kein Inspector mehr)
        self.scene_canvas = SceneCanvas()
        main_splitter.addWidget(self.scene_canvas)
        
        # Rechter Bereich: Code Editor (breiter, mehr Y-Platz)
        self.code_editor = CodeEditor()
        self.code_editor.setMinimumWidth(300)
        # Buttons im Code Editor mit Funktionen verbinden
        self.code_editor.run_requested.connect(self._run_game)
        self.code_editor.stop_requested.connect(self._stop_game)
        main_splitter.addWidget(self.code_editor)
        # Verhältnisse setzen
        main_splitter.setStretchFactor(0, 0)  # Asset Browser fix
        main_splitter.setStretchFactor(1, 1)  # Canvas nimmt restlichen Platz
        main_splitter.setStretchFactor(2, 0)  # Code Editor fix
        
        # Splitter-Änderungen überwachen für visuelle Indikatoren
        self.main_splitter = main_splitter
        main_splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Terminal/Console am unteren Rand
        self.console = Console()
        # Höhe wird von der Console selbst verwaltet
        
        # Stacked Widget für Projekt-View und Sprite-Views
        self.view_stack = QStackedWidget()
        
        # Tab-Buttons für Sprites (nur intern, nicht mehr sichtbar)
        self.sprite_tabs = {}  # Dictionary: sprite_key -> button
        
        # Projekt-View (Standard) - ohne Tab-Leiste
        project_widget = QWidget()
        project_layout = QVBoxLayout()
        project_layout.setContentsMargins(0, 0, 0, 0)
        
        # Keine Tab-Buttons mehr - direkt main_splitter und console
        project_layout.addWidget(main_splitter)
        project_layout.addWidget(self.console)
        project_widget.setLayout(project_layout)
        
        self.view_stack.addWidget(project_widget)  # Index 0 = Projekt
        
        self.setCentralWidget(self.view_stack)
        
        # Initial: Projekt-View anzeigen
        self.current_sprite_tab = None
        
        # Signals verbinden
        if self.scene_canvas:
            self.scene_canvas.object_selected.connect(self._on_object_selected_for_code)
        
        # Undo/Redo-Manager an Komponenten weitergeben
        if self.scene_canvas:
            self.scene_canvas.set_undo_redo_manager(self.undo_redo_manager)
            self.scene_canvas.undo_redo_changed.connect(self._update_undo_redo_buttons)
        if self.code_editor:
            self.code_editor.set_undo_redo_manager(self.undo_redo_manager)
            self.code_editor.undo_redo_changed.connect(self._update_undo_redo_buttons)
        
        # Initial Buttons-Status setzen
        self._update_undo_redo_buttons()
        
        if self.asset_browser:
            self.asset_browser.sprite_selected.connect(self._on_sprite_selected)
            self.asset_browser.asset_double_clicked.connect(self._on_sprite_double_clicked)
            self.asset_browser.assets_updated.connect(self._on_assets_updated)
            self.asset_browser.settings_changed.connect(self._on_project_settings_changed)
    
    def _load_last_project(self):
        """Lädt das zuletzt geöffnete Projekt automatisch"""
        from ..utils.config import get_last_project
        
        last_project = get_last_project()
        if last_project:
            # Projekt automatisch laden
            self._load_project(last_project)
        else:
            # Kein zuletzt geöffnetes Projekt - Dialog anzeigen
            self._show_project_dialog()
    
    def _show_project_dialog(self):
        """Zeigt Dialog zur Projekt-Auswahl beim Start"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Projekt öffnen")
        msg_box.setText("Was möchten Sie tun?")
        msg_box.setInformativeText("Wählen Sie eine Option:")
        
        # Buttons mit klaren Beschriftungen
        new_btn = msg_box.addButton("Neues Projekt erstellen", QMessageBox.ActionRole)
        open_btn = msg_box.addButton("Projekt öffnen", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Später laden", QMessageBox.RejectRole)
        
        # Standard-Button
        msg_box.setDefaultButton(new_btn)
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        if clicked_button == new_btn:
            self._new_project()
        elif clicked_button == open_btn:
            self._open_project()
        else:
            # Trotzdem Editor öffnen (Projekt kann später geladen werden)
            self.statusBar().showMessage("Kein Projekt geöffnet - Datei → Projekt öffnen")
    
    def _new_project(self):
        """Erstellt ein neues Projekt"""
        project_dir = QFileDialog.getExistingDirectory(
            self, "Projektordner wählen", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not project_dir:
            return
        
        project_path = Path(project_dir)
        
        # Template kopieren
        template_path = Path(__file__).parent.parent / "templates" / "empty_project"
        if not template_path.exists():
            QMessageBox.critical(self, "Fehler", "Template nicht gefunden!")
            return
        
        # Projektordner erstellen falls nicht existiert
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Template-Dateien kopieren
        try:
            for item in template_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, project_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, project_path / item.name)
            
            QMessageBox.information(self, "Erfolg", 
                                   f"Neues Projekt erstellt in:\n{project_path}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                               f"Fehler beim Erstellen des Projekts:\n{e}")
            return
        
        # Projekt öffnen
        self._load_project(project_path)
    
    def _open_project(self):
        """Öffnet ein vorhandenes Projekt"""
        project_dir = QFileDialog.getExistingDirectory(
            self, "Projektordner öffnen", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not project_dir:
            return
        
        project_path = Path(project_dir)
        
        # Prüfen ob project.json existiert
        if not (project_path / "project.json").exists():
            QMessageBox.critical(self, "Fehler", 
                               "Kein gültiges Projekt!\nproject.json nicht gefunden.")
            return
        
        self._load_project(project_path)
    
    def _load_project(self, project_path: Path):
        """Lädt ein Projekt in den Editor"""
        self.project_path = project_path
        
        # Projektname aus project.json laden, falls vorhanden
        project_name = project_path.name  # Fallback: Ordnername
        project_file = project_path / "project.json"
        if project_file.exists():
            try:
                import json
                with open(project_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                project_name = config.get("name", project_path.name)
            except:
                pass  # Fallback auf Ordnername
        
        # Projekt-Label aktualisieren
        self.project_label.setText(f"Projekt: {project_name}")
        
        # Fenstertitel aktualisieren
        self.setWindowTitle(f"GameDev-Edu Editor - {project_name}")
        
        # Zuletzt geöffnetes Projekt speichern
        from ..utils.config import set_last_project
        set_last_project(project_path)
        
        # Projekt laden
        try:
            if self.scene_canvas:
                self.scene_canvas.load_project(project_path)
            if self.asset_browser:
                self.asset_browser.load_project(project_path)
            if self.code_editor:
                self.code_editor.load_project(project_path)
                # Code-Editor initial auf globale game.py setzen (kein Objekt ausgewählt)
                self.code_editor.set_object(None, None)
            # Inspector entfernt
            
            # Undo/Redo-Historie beim Laden eines neuen Projekts löschen
            self.undo_redo_manager.clear()
            self._update_undo_redo_buttons()
            
            self.run_button.setEnabled(True)
            if self.code_editor:
                self.code_editor.set_run_enabled(True)
            self.statusBar().showMessage(f"Projekt geladen: {project_path}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                               f"Fehler beim Laden des Projekts:\n{e}")
            import traceback
            traceback.print_exc()
    
    def _save_project(self):
        """Speichert das aktuelle Projekt"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Kein Projekt geöffnet!")
            return
        
        # Alle Komponenten speichern
        if self.scene_canvas:
            self.scene_canvas.save_scene()
        if self.code_editor:
            self.code_editor.save_code()
        
        self.statusBar().showMessage("Projekt gespeichert", 2000)
    
    def _on_sprite_selected(self, sprite_path: str):
        """Wird aufgerufen wenn ein Sprite im Asset Browser ausgewählt wird"""
        # Für Drag & Drop vorbereiten
        pass
    
    # Inspector-Methoden entfernt - wird durch Rechtsklick-Menü ersetzt
    
    def _on_object_selected_for_code(self, obj_data: dict):
        """Wird aufgerufen wenn ein Objekt ausgewählt wird - aktualisiert Code-Editor"""
        if self.code_editor:
            # Prüfen ob obj_data leer ist oder keine ID hat
            if not obj_data or not obj_data.get("id"):
                # Kein Objekt ausgewählt - globale game.py anzeigen
                self.code_editor.set_object(None, None)
            else:
                # Objekt ausgewählt - Code für dieses Objekt anzeigen
                self.code_editor.set_object(obj_data.get("id"), obj_data)
    
    def _on_assets_updated(self):
        """Wird aufgerufen wenn Assets im Asset Browser aktualisiert wurden"""
        # Assets wurden aktualisiert - Canvas kann neu geladen werden falls nötig
        pass
    
    def _on_project_settings_changed(self):
        """Wird aufgerufen wenn Projekt-Einstellungen geändert wurden"""
        # Scene Canvas Grid-Einstellungen neu laden
        if self.scene_canvas and self.project_path:
            self.scene_canvas._load_grid_settings()
            self.scene_canvas.canvas.update()
    
    def _on_splitter_moved(self, pos: int, index: int):
        """Wird aufgerufen wenn Splitter bewegt wird"""
        # Diese Funktion kann für zukünftige Features verwendet werden
        pass
    
    def _toggle_asset_browser(self, checked: bool):
        """Zeigt/versteckt den Asset Browser"""
        if not self.main_splitter:
            return
        
        if checked:
            # Asset Browser anzeigen (auf 200px setzen)
            sizes = self.main_splitter.sizes()
            if sizes[0] < 50:
                sizes[0] = 200
                self.main_splitter.setSizes(sizes)
        else:
            # Asset Browser verstecken (auf 0 setzen)
            sizes = self.main_splitter.sizes()
            sizes[0] = 0
            self.main_splitter.setSizes(sizes)
    
    # Inspector-Toggle entfernt
    
    def _on_sprite_double_clicked(self, sprite_path: str):
        """Wird aufgerufen wenn ein Sprite doppelgeklickt wird - öffnet Tab"""
        if not self.project_path:
            return
        
        sprite_full_path = Path(sprite_path)
        if not sprite_full_path.is_absolute():
            sprite_full_path = self.project_path / sprite_path
        
        if not sprite_full_path.exists():
            return
        
        # Prüfen ob Tab bereits existiert
        sprite_key = str(sprite_full_path)
        if sprite_key in self.sprite_tabs:
            # Tab bereits vorhanden - aktivieren
            self._show_sprite_tab(sprite_key)
            return
        
        # Neuen Tab erstellen
        sprite_tab = SpriteViewerTab(sprite_full_path, self.project_path)
        tab_index = self.view_stack.addWidget(sprite_tab)
        
        # Tab-Button erstellen (nur für interne Verwaltung, nicht mehr sichtbar)
        tab_button = QPushButton(sprite_tab.get_tab_name())
        tab_button.setCheckable(True)
        tab_button.clicked.connect(lambda: self._show_sprite_tab(sprite_key))
        tab_button.setVisible(False)  # Nicht mehr sichtbar
        
        self.sprite_tabs[sprite_key] = tab_button
        self.view_stack.widget(tab_index).sprite_key = sprite_key  # Für später
        
        # Tab aktivieren
        self._show_sprite_tab(sprite_key)
    
    def _show_sprite_tab(self, sprite_key: str):
        """Zeigt einen Sprite-Tab"""
        if sprite_key not in self.sprite_tabs:
            return
        
        # Alle Tabs deaktivieren
        for btn in self.sprite_tabs.values():
            btn.setChecked(False)
        
        # Gewählten Tab aktivieren
        self.sprite_tabs[sprite_key].setChecked(True)
        self.current_sprite_tab = sprite_key
        
        # View wechseln
        for i in range(self.view_stack.count()):
            widget = self.view_stack.widget(i)
            if hasattr(widget, 'sprite_key') and widget.sprite_key == sprite_key:
                self.view_stack.setCurrentIndex(i)
                break
    
    def _show_project_view(self):
        """Zeigt die Projekt-View"""
        # Alle Tabs deaktivieren
        for btn in self.sprite_tabs.values():
            btn.setChecked(False)
        
        self.current_sprite_tab = None
        self.view_stack.setCurrentIndex(0)  # Projekt-View
    
    def _run_game(self):
        """Startet das Spiel in einem separaten Prozess"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Kein Projekt geöffnet!")
            return
        
        # Projekt speichern
        self._save_project()
        
        # TODO: Subprocess starten
        import subprocess
        import sys
        
        runtime_path = Path(__file__).parent.parent / "engine" / "runtime.py"
        
        try:
            # Umgebungsvariablen für unbuffered Output und UTF-8 Encoding
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'  # Erzwingt UTF-8 für alle I/O-Operationen
            
            self.game_process = subprocess.Popen(
                [sys.executable, "-u", "-m", "game_editor.engine.runtime", str(self.project_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Beide Streams getrennt für sofortige Fehlererkennung
                text=True,  # Text-Modus mit UTF-8 (dank PYTHONIOENCODING)
                encoding='utf-8',
                errors='replace',  # Fehlerhafte Zeichen durch Ersatzzeichen ersetzen
                bufsize=1,  # Line-buffered für sofortige Ausgabe
                env=env
            )
            
            # Output-Reader starten
            self.output_reader = GameOutputReader(self.game_process)
            self.output_reader.output_received.connect(self.console.append_output)
            self.output_reader.error_received.connect(self.console.append_error)
            self.output_reader.finished.connect(self._on_game_finished)
            self.output_reader.start()
            
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            if self.code_editor:
                self.code_editor.set_run_enabled(False)
                self.code_editor.set_stop_enabled(True)
            self.run_timer.start(100)  # Alle 100ms prüfen ob Prozess noch läuft
            
            self.statusBar().showMessage("Spiel läuft...")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Spiel konnte nicht gestartet werden:\n{e}")
    
    def _undo(self):
        """Macht die letzte Aktion rückgängig"""
        if not self.undo_redo_manager:
            return
        
        success = self.undo_redo_manager.undo()
        if success:
            # Canvas aktualisieren und Szene speichern
            if self.scene_canvas:
                self.scene_canvas.canvas.update()
                self.scene_canvas.save_scene()
            # Canvas aktualisiert sich automatisch
        self._update_undo_redo_buttons()
    
    def _redo(self):
        """Stellt die letzte rückgängig gemachte Aktion wieder her"""
        if not self.undo_redo_manager:
            return
        
        success = self.undo_redo_manager.redo()
        if success:
            # Canvas aktualisieren und Szene speichern
            if self.scene_canvas:
                self.scene_canvas.canvas.update()
                self.scene_canvas.save_scene()
            # Canvas aktualisiert sich automatisch
        self._update_undo_redo_buttons()
    
    def _update_undo_redo_buttons(self):
        """Aktualisiert den Status der Undo/Redo-Buttons"""
        if not self.undo_redo_manager:
            return
        
        can_undo = self.undo_redo_manager.can_undo()
        can_redo = self.undo_redo_manager.can_redo()
        
        if hasattr(self, 'undo_button'):
            self.undo_button.setEnabled(can_undo)
        if hasattr(self, 'redo_button'):
            self.redo_button.setEnabled(can_redo)
        if hasattr(self, 'undo_action'):
            self.undo_action.setEnabled(can_undo)
        if hasattr(self, 'redo_action'):
            self.redo_action.setEnabled(can_redo)
    
    def _stop_game(self):
        """Stoppt das laufende Spiel"""
        # Output-Reader stoppen
        if self.output_reader:
            self.output_reader.stop()
            self.output_reader.wait(1000)  # Max 1 Sekunde warten
            self.output_reader = None
        
        if self.game_process:
            self.game_process.terminate()
            self.game_process.wait(timeout=2)
            self.game_process = None
        
        self.run_timer.stop()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.code_editor:
            self.code_editor.set_run_enabled(True)
            self.code_editor.set_stop_enabled(False)
        self.statusBar().showMessage("Spiel gestoppt")
    
    def _on_game_finished(self):
        """Wird aufgerufen wenn der Output-Reader fertig ist"""
        if self.game_process and self.game_process.poll() is not None:
            # Spiel ist beendet
            self.run_timer.stop()
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            if self.code_editor:
                self.code_editor.set_run_enabled(True)
                self.code_editor.set_stop_enabled(False)
            self.statusBar().showMessage("Spiel beendet")
            self.game_process = None
            self.output_reader = None
    
    def _check_game_process(self):
        """Prüft ob der Spiel-Prozess noch läuft"""
        if self.game_process:
            if self.game_process.poll() is not None:
                # Prozess ist beendet - Output-Reader wird den Rest lesen
                # UI wird in _on_game_finished zurückgesetzt
                pass
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Wird aufgerufen wenn eine Datei über das Fenster gezogen wird"""
        if event.mimeData().hasUrls():
            # Prüfen ob es Bilddateien sind
            urls = event.mimeData().urls()
            has_images = False
            for url in urls:
                file_path = url.toLocalFile()
                if file_path:
                    ext = Path(file_path).suffix.lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                        has_images = True
                        break
            
            if has_images and self.project_path:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Wird aufgerufen wenn eine Datei in das Fenster gedroppt wird"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Bitte öffnen Sie zuerst ein Projekt!")
            event.ignore()
            return
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            imported_count = 0
            last_imported_path = None
            
            for url in urls:
                file_path = url.toLocalFile()
                if not file_path:
                    continue
                
                source_path = Path(file_path)
                if not source_path.exists():
                    continue
                
                # Dateiformat prüfen
                ext = source_path.suffix.lower()
                if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                    continue
                
                # Zielordner: assets/images/
                images_dir = self.project_path / "assets" / "images"
                images_dir.mkdir(parents=True, exist_ok=True)
                
                # Datei kopieren
                dest_path = images_dir / source_path.name
                
                # Wenn Datei bereits existiert, Nummer anhängen
                counter = 1
                while dest_path.exists():
                    stem = source_path.stem
                    dest_path = images_dir / f"{stem}_{counter}{source_path.suffix}"
                    counter += 1
                
                try:
                    shutil.copy2(source_path, dest_path)
                    imported_count += 1
                    last_imported_path = dest_path
                except Exception as e:
                    QMessageBox.warning(self, "Fehler", 
                                      f"Datei konnte nicht importiert werden:\n{source_path.name}\n{e}")
            
            if imported_count > 0:
                # Asset Browser aktualisieren
                if self.asset_browser:
                    self.asset_browser._load_assets()
                    # Letztes importiertes Asset highlighten
                    if last_imported_path:
                        self.asset_browser._select_asset(str(last_imported_path))
                    self.asset_browser.assets_updated.emit()
                
                self.statusBar().showMessage(f"{imported_count} Datei(en) importiert", 3000)
            
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def closeEvent(self, event):
        """Wird aufgerufen wenn das Fenster geschlossen wird"""
        if self.game_process:
            self._stop_game()
        event.accept()
