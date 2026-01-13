"""
Asset Browser - Zeigt verfügbare Bilder und Assets
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QLabel,
                                QPushButton, QHBoxLayout, QFileDialog, QMessageBox,
                                QComboBox, QDialog, QScrollArea, QMenu, QSlider, QFrame,
                                QInputDialog, QLineEdit)
from PySide6.QtCore import Signal, Qt, QPoint, QMimeData, QFileSystemWatcher, QTimer
from PySide6.QtGui import QPixmap, QIcon, QDrag, QDragEnterEvent, QDropEvent
from pathlib import Path
import shutil
from typing import Dict
from ..utils.sprite_organizer import SpriteOrganizer
from ..utils.spritesheet_extractor import SpritesheetExtractor
from .spritesheet_dialog import SpritesheetDialog
from .asset_grid_widget import AssetGridWidget
from .project_settings_dialog import ProjectSettingsDialog


class AssetBrowser(QWidget):
    """Asset Browser für Bilder und Assets"""
    
    sprite_selected = Signal(str)  # Signal mit Sprite-Pfad
    sprite_dragged = Signal(str, int, int)  # Signal für Drag & Drop
    asset_double_clicked = Signal(str)  # Signal für Doppelklick auf Asset
    assets_updated = Signal()  # Signal wenn Assets aktualisiert wurden
    settings_changed = Signal()  # Signal wenn Projekt-Einstellungen geändert wurden
    
    def __init__(self):
        super().__init__()
        self.project_path: Path | None = None
        # Drag & Drop aktivieren
        self.setAcceptDrops(True)
        # Asset-Frames speichern für Highlighting
        self.asset_frames: Dict[str, QFrame] = {}
        # File-Watcher für sprites/ und assets/images/ Ordner
        self.file_watcher = QFileSystemWatcher()
        # Timer für verzögertes Neuladen (verhindert zu häufige Updates)
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        # Timer für Asset-Browser-Aktualisierung (bei Datei-Löschung)
        self.assets_reload_timer = QTimer()
        self.assets_reload_timer.setSingleShot(True)
        self._init_ui()
        
        # Verbindungen nach _init_ui herstellen (Methoden müssen existieren)
        # Die Verbindung wird in load_project() hergestellt, wenn der Pfad bekannt ist
        self.reload_timer.timeout.connect(self._process_sprites_folder)
        self.assets_reload_timer.timeout.connect(self._load_assets)
    
    def _init_ui(self):
        """Initialisiert die UI"""
        # Dark-Mode für Asset Browser
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label (Dark-Mode)
        label = QLabel("Asset Browser")
        label.setStyleSheet("font-weight: bold; padding: 5px; color: #d4d4d4;")
        layout.addWidget(label)
        
        # Button-Layout
        button_layout = QVBoxLayout()
        
        # Import-Button (Dark-Mode)
        import_button = QPushButton("Bild importieren...")
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
            }
        """)
        import_button.clicked.connect(self._import_image)
        button_layout.addWidget(import_button)
        
        # Projekt-Einstellungen (Dark-Mode)
        settings_button = QPushButton("Projekt-Einstellungen...")
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
            }
        """)
        settings_button.clicked.connect(self._open_settings)
        button_layout.addWidget(settings_button)
        
        # Spritesheet extrahieren (Dark-Mode)
        extract_button = QPushButton("Spritesheet extrahieren...")
        extract_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
            }
        """)
        extract_button.clicked.connect(self._extract_spritesheet)
        button_layout.addWidget(extract_button)
        
        # Aktualisieren-Button (grüner Pfeil)
        refresh_button = QPushButton("↻")
        refresh_button.setToolTip("Asset Browser aktualisieren")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #4caf50;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
                font-size: 16pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #4a9eff;
                color: #66bb6a;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        """)
        refresh_button.clicked.connect(self._refresh_assets)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
        # Liste für Assets (einfach untereinander)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container für Asset-Items
        self.asset_container = QWidget()
        self.asset_layout = QVBoxLayout()
        self.asset_layout.setContentsMargins(5, 5, 5, 5)
        self.asset_layout.setSpacing(5)
        self.asset_container.setLayout(self.asset_layout)
        
        self.scroll_area.setWidget(self.asset_container)
        layout.addWidget(self.scroll_area)
        
        # Alte Liste für Drag & Drop (versteckt)
        self.asset_list = QListWidget()
        self.asset_list.setVisible(False)
        self.asset_list.setDragEnabled(True)
        self.asset_list.setDragDropMode(QListWidget.DragOnly)
        
        self.setLayout(layout)
    
    def load_project(self, project_path: Path):
        """Lädt Projekt und zeigt Assets"""
        # Alten Watcher stoppen
        if self.file_watcher.directories():
            self.file_watcher.removePaths(self.file_watcher.directories())
        
        self.project_path = project_path
        
        # sprites/ Ordner erstellen
        sprites_folder = project_path / "sprites"
        if not sprites_folder.exists():
            organizer = SpriteOrganizer(project_path)
            organizer.create_sprites_folder()
        
        # File-Watcher für sprites/ Ordner aktivieren
        if sprites_folder.exists():
            self.file_watcher.addPath(str(sprites_folder))
            print(f"[Asset Browser] Überwache sprites/ Ordner: {sprites_folder}")
            # Beim Laden einmal prüfen ob Bilder im sprites/ Ordner sind
            QTimer.singleShot(1000, self._process_sprites_folder)
        
        # File-Watcher für assets/images/ Ordner aktivieren (für automatisches Löschen)
        images_dir = project_path / "assets" / "images"
        if images_dir.exists():
            self.file_watcher.addPath(str(images_dir))
            print(f"[Asset Browser] Überwache assets/images/ Ordner: {images_dir}")
        
        # Verbindung herstellen (trennen falls bereits verbunden, dann neu verbinden)
        # Alle Verbindungen trennen (ohne Argument = alle), um RuntimeWarning zu vermeiden
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            try:
                # Alle Verbindungen zum directoryChanged Signal trennen
                self.file_watcher.directoryChanged.disconnect()
            except (TypeError, RuntimeError):
                pass  # War noch nicht verbunden - das ist OK
        
        # Signal verbinden (für beide Ordner)
        self.file_watcher.directoryChanged.connect(self._on_folder_changed)
        
        self._load_assets()
    
    def _refresh_assets(self):
        """Aktualisiert den Asset Browser manuell"""
        self._load_assets()
        print("[Asset Browser] Asset Browser manuell aktualisiert")
    
    def _load_assets(self):
        """Lädt verfügbare Assets aus assets/images (rekursiv)"""
        if not self.project_path:
            return
        
        # Alte Items löschen
        while self.asset_layout.count():
            item = self.asset_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.asset_list.clear()
        
        images_dir = self.project_path / "assets" / "images"
        if not images_dir.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
            return
        
        # Sprite-Größe aus Einstellungen laden (quadratisch)
        sprite_size = self._get_sprite_size()
        
        # Prüfen ob sprite_size in project.json definiert ist
        has_sprite_size_setting = False
        if self.project_path:
            settings_file = self.project_path / "project.json"
            if settings_file.exists():
                try:
                    import json
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    has_sprite_size_setting = "sprite_size" in config
                except:
                    pass
        
        # Alle Bilddateien rekursiv finden
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        found_count = 0
        
        for img_file in sorted(images_dir.rglob("*")):
            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                found_count += 1
                pixmap = QPixmap(str(img_file))
                if not pixmap.isNull():
                    # Alle Bilder anzeigen (Skalierung erfolgt automatisch beim Laden)
                    self._add_asset_item_simple(str(img_file))
                    # Auch für Drag & Drop
                    self._add_asset_item(str(img_file))
    
    def _add_asset_item_simple(self, file_path: str):
        """Fügt ein Asset als einfaches Item untereinander hinzu"""
        from PySide6.QtWidgets import QFrame, QMenu
        from PySide6.QtCore import QPoint
        
        img_path = Path(file_path)
        
        # Item-Frame
        item_frame = QFrame()
        item_frame.setFrameShape(QFrame.Shape.Box)
        item_frame.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Thumbnail (128x128)
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            thumb_label = QLabel()
            thumb_label.setPixmap(scaled)
            thumb_label.setFixedSize(128, 128)
            thumb_label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(thumb_label)
        else:
            thumb_label = None
        
        # Name (ohne Pfad, nur Dateiname)
        name_label = QLabel(img_path.name)
        name_label.setWordWrap(True)
        item_layout.addWidget(name_label, 1)
        
        item_frame.setLayout(item_layout)
        
        # Frame in Dictionary speichern für Highlighting
        self.asset_frames[str(img_path)] = item_frame
        
        # Events
        def on_click():
            # Alle Frames zurücksetzen
            self._clear_selection()
            # Dieses Frame highlighten (dunkelgrau)
            item_frame.setStyleSheet("border: 2px solid #4a9eff; background-color: #808080; padding: 5px;")
            if self.project_path:
                try:
                    rel_path = img_path.relative_to(self.project_path)
                    self.sprite_selected.emit(str(rel_path))
                except ValueError:
                    pass
        
        def on_double_click():
            self.asset_double_clicked.emit(str(img_path))
        
        def on_right_click(event):
            menu = QMenu(self)
            
            # Vollständigen Pfad anzeigen
            full_path_str = str(img_path)
            path_action = menu.addAction(f"Pfad: {full_path_str}")
            path_action.setEnabled(False)
            
            menu.addSeparator()
            
            # Im Windows Explorer öffnen
            open_explorer_action = menu.addAction("Im Explorer öffnen")
            def open_in_explorer():
                import subprocess
                import os
                # Windows Explorer mit dem Ordner öffnen und Datei auswählen
                try:
                    # Windows: explorer /select,"pfad"
                    subprocess.Popen(f'explorer /select,"{full_path_str}"', shell=True)
                except Exception as e:
                    # Fallback: Nur Ordner öffnen
                    folder_path = os.path.dirname(full_path_str)
                    subprocess.Popen(f'explorer "{folder_path}"', shell=True)
            open_explorer_action.triggered.connect(open_in_explorer)
            
            # Umbenennen-Option
            rename_action = menu.addAction("Umbenennen")
            def rename_asset():
                # Dialog mit nur Dateiname ohne Endung markiert
                dialog = QDialog(self)
                dialog.setWindowTitle("Asset umbenennen")
                dialog.setModal(True)
                
                layout = QVBoxLayout()
                
                label = QLabel(f"Neuer Name für {img_path.name}:")
                layout.addWidget(label)
                
                # Dateiname ohne Endung
                file_stem = img_path.stem
                file_suffix = img_path.suffix
                
                line_edit = QLineEdit()
                line_edit.setText(file_stem)
                # Nur den Namen ohne Endung markieren
                line_edit.selectAll()
                layout.addWidget(line_edit)
                
                button_layout = QHBoxLayout()
                ok_button = QPushButton("OK")
                cancel_button = QPushButton("Abbrechen")
                button_layout.addWidget(ok_button)
                button_layout.addWidget(cancel_button)
                layout.addLayout(button_layout)
                
                dialog.setLayout(layout)
                
                ok_button.clicked.connect(dialog.accept)
                cancel_button.clicked.connect(dialog.reject)
                
                # Fokus auf LineEdit setzen und Text markieren
                line_edit.setFocus()
                line_edit.selectAll()
                
                if dialog.exec() == QDialog.Accepted:
                    new_name = line_edit.text().strip()
                    if new_name and new_name != file_stem:
                        # Neuer Dateiname mit Endung
                        new_file_name = new_name + file_suffix
                        new_path = img_path.parent / new_file_name
                        
                        # Prüfen ob Datei bereits existiert
                        if new_path.exists() and new_path != img_path:
                            QMessageBox.warning(self, "Fehler", f"Eine Datei mit dem Namen '{new_file_name}' existiert bereits!")
                            return
                        
                        try:
                            # Datei umbenennen
                            old_path_str = str(img_path)
                            img_path.rename(new_path)
                            # Frame aus asset_frames entfernen (wird beim Neuladen neu erstellt)
                            if old_path_str in self.asset_frames:
                                del self.asset_frames[old_path_str]
                            # Asset Browser neu laden
                            self._load_assets()
                            self.assets_updated.emit()
                            print(f"[Asset Browser] Asset umbenannt: {img_path.name} -> {new_file_name}")
                        except Exception as e:
                            QMessageBox.critical(self, "Fehler", f"Fehler beim Umbenennen:\n{e}")
            
            rename_action.triggered.connect(rename_asset)
            
            menu.addSeparator()
            
            # Details-Menü entfernt (erzeugte Ping-Sound)
            
            # Menü anzeigen (ohne Sound)
            menu.exec(event.globalPos())
            
            # Nach Rechtsklick-Menü: Highlight wiederherstellen (nur wenn Frame noch existiert)
            try:
                # Prüfen ob Frame noch existiert (wurde möglicherweise durch _load_assets() gelöscht)
                if item_frame and str(img_path) in self.asset_frames:
                    self._clear_selection()
                    item_frame.setStyleSheet("border: 2px solid #4a9eff; background-color: #808080; padding: 5px;")
                else:
                    # Frame wurde gelöscht (z.B. nach Umbenennen) - nur Selection clearen
                    self._clear_selection()
            except RuntimeError:
                # Frame wurde bereits gelöscht - ignorieren
                pass
        
        # Linksklick: Auswahl (überall im Frame)
        def on_frame_click(event):
            if event.button() == Qt.LeftButton:
                on_click()
        
        def on_frame_double_click(event):
            if event.button() == Qt.LeftButton:
                on_double_click()
        
        # Rechtsklick: Menü (überall im Frame)
        def on_frame_right_click(event):
            on_right_click(event)
        
        # Event-Handler auf item_frame setzen (funktioniert überall im Kasten)
        item_frame.mousePressEvent = on_frame_click
        item_frame.mouseDoubleClickEvent = on_frame_double_click
        item_frame.contextMenuEvent = on_frame_right_click
        
        # Drag & Drop: Maus-Druck auf Thumbnail (nur Linksklick)
        if thumb_label:
            def thumb_mouse_press(event):
                if event.button() == Qt.LeftButton:
                    # Drag starten
                    drag = QDrag(item_frame)
                    mime_data = QMimeData()
                    mime_data.setText(str(img_path))
                    drag.setMimeData(mime_data)
                    if not pixmap.isNull():
                        drag.setPixmap(scaled)
                        # Hotspot zentrieren (Mitte des Pixmaps)
                        hotspot_x = scaled.width() // 2
                        hotspot_y = scaled.height() // 2
                        drag.setHotSpot(QPoint(hotspot_x, hotspot_y))
                    drag.exec(Qt.CopyAction)
            
            thumb_label.mousePressEvent = thumb_mouse_press
        
        self.asset_layout.addWidget(item_frame)
    
    def _clear_selection(self):
        """Setzt alle Asset-Frames auf Standard-Style zurück"""
        # Liste der Frames kopieren, da sich asset_frames während der Iteration ändern kann
        frames_to_clear = list(self.asset_frames.items())
        for path_str, frame in frames_to_clear:
            try:
                # Prüfen ob Frame noch existiert (nicht gelöscht wurde)
                # Versuche auf das Widget zuzugreifen - wenn es gelöscht wurde, gibt es RuntimeError
                _ = frame.objectName()  # Einfacher Zugriff um zu prüfen ob Widget noch existiert
                frame.setStyleSheet("border: 1px solid #ccc; padding: 5px; background-color: transparent;")
            except (RuntimeError, AttributeError):
                # Frame wurde bereits gelöscht - aus Dictionary entfernen
                if path_str in self.asset_frames:
                    del self.asset_frames[path_str]
    
    def _select_asset(self, file_path: str):
        """Selektiert/Highlightet ein Asset anhand des Dateipfads"""
        # Alle Selektierungen zurücksetzen
        self._clear_selection()
        
        # Asset-Pfad finden (kann absolut oder relativ sein)
        target_path = Path(file_path)
        
        # Prüfen ob es ein absoluter Pfad ist
        if target_path.is_absolute():
            # Direkt suchen
            if str(target_path) in self.asset_frames:
                frame = self.asset_frames[str(target_path)]
                frame.setStyleSheet("border: 2px solid #4a9eff; background-color: #808080; padding: 5px;")
                # Scrollen zum Frame
                self._scroll_to_frame(frame)
                return
        
        # Relativen Pfad suchen
        if self.project_path:
            try:
                # Versuchen relativen Pfad zu erstellen
                if not target_path.is_absolute():
                    full_path = self.project_path / target_path
                else:
                    full_path = target_path
                
                # Alle Frames durchsuchen
                for asset_path_str, frame in self.asset_frames.items():
                    asset_path = Path(asset_path_str)
                    # Prüfen ob Pfade übereinstimmen
                    if asset_path == full_path or asset_path.name == target_path.name:
                        frame.setStyleSheet("border: 2px solid #4a9eff; background-color: #808080; padding: 5px;")
                        # Scrollen zum Frame
                        self._scroll_to_frame(frame)
                        return
            except Exception:
                pass
    
    def _scroll_to_frame(self, frame: QFrame):
        """Scrollt zum angegebenen Frame"""
        if hasattr(self, 'scroll_area') and self.scroll_area:
            self.scroll_area.ensureWidgetVisible(frame)
    
    def _add_asset_item(self, file_path: str):
        """Fügt ein Asset zur Liste hinzu"""
        img_path = Path(file_path)
        
        # Thumbnail erstellen
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Thumbnail skalieren
            scaled = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            icon = QIcon(scaled)
        else:
            icon = QIcon()
        
        # Anzeigename mit relativem Pfad
        if self.project_path:
            try:
                rel_path = img_path.relative_to(self.project_path)
                display_name = str(rel_path).replace("\\", "/")
            except ValueError:
                display_name = img_path.name
        else:
            display_name = img_path.name
        
        # Item erstellen
        from PySide6.QtWidgets import QListWidgetItem
        item = QListWidgetItem(icon, display_name)
        item.setData(Qt.ItemDataRole.UserRole, str(img_path))
        self.asset_list.addItem(item)
    
    def _import_image(self):
        """Importiert ein oder mehrere Bilder ins Projekt"""
        if not self.project_path:
            print("[Asset Browser] FEHLER: Kein Projekt geöffnet!")
            return
        
        # Mehrfachauswahl aktivieren
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Bilder importieren", "",
            "Bilder (*.png *.jpg *.jpeg *.bmp);;Alle Dateien (*.*)"
        )
        
        if not file_paths:
            return
        
        # Alle Dateien importieren
        imported_count = 0
        failed_count = 0
        
        for file_path in file_paths:
            source_path = Path(file_path)
            if self._import_single_image(source_path):
                imported_count += 1
            else:
                failed_count += 1
        
        if imported_count > 0:
            self._load_assets()
            self.assets_updated.emit()
            print(f"[Asset Browser] {imported_count} Bild(er) erfolgreich importiert")
        
        if failed_count > 0:
            print(f"[Asset Browser] {failed_count} Bild(er) konnten nicht importiert werden")
    
    def _import_single_image(self, source_path: Path) -> bool:
        """Importiert ein einzelnes Bild - gibt True zurück bei Erfolg"""
        
        # Prüfen ob es ein Spritesheet ist (größer als eingestellte Sprite-Größe)
        pixmap = QPixmap(str(source_path))
        if pixmap.isNull():
            print(f"[Asset Browser] FEHLER: Bild konnte nicht geladen werden: {source_path.name}")
            return False
        
        sprite_size = self._get_sprite_size()
        
        # Wenn Bild größer ist, könnte es ein Spritesheet sein
        if pixmap.width() > sprite_size * 2 or pixmap.height() > sprite_size * 2:
            # Spritesheet-Dialog anbieten (nur bei manuellem Import)
            reply = QMessageBox.question(
                self, "Spritesheet erkannt",
                f"Das Bild ({pixmap.width()}×{pixmap.height()}) ist größer als die eingestellte Sprite-Größe ({sprite_size}×{sprite_size}).\n\n"
                "Möchten Sie es als Spritesheet extrahieren?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Spritesheet extrahieren
                dialog = SpritesheetDialog(self, source_path)
                if dialog.exec() == QDialog.Accepted:
                    params = dialog.get_parameters()
                    extractor = SpritesheetExtractor(self.project_path)
                    try:
                        extracted_count, errors = extractor.extract_from_grid(
                            source_path,
                            params["sprite_width"],
                            params["sprite_height"],
                            params["output_folder"],
                            params["spacing"],
                            params["margin"]
                        )
                        if extracted_count > 0:
                            print(f"[Asset Browser] {extracted_count} Sprite(s) wurden extrahiert!")
                            self._load_assets()
                            # Inspector auch aktualisieren
                            self.assets_updated.emit()
                        else:
                            print(f"[Asset Browser] FEHLER: Keine Sprites konnten extrahiert werden.")
                    except Exception as e:
                        print(f"[Asset Browser] FEHLER beim Extrahieren: {e}")
                return True
            # Wenn "Nein" -> nicht importieren (Spritesheet zu groß)
            return False
        
        # Normales Bild importieren
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
            # Importiertes Asset highlighten
            self._select_asset(str(dest_path))
            return True
        except Exception as e:
            print(f"[Asset Browser] FEHLER: Bild konnte nicht importiert werden: {source_path.name} - {e}")
            return False
    
    def _get_sprite_size(self) -> int:
        """Lädt Sprite-Größe aus project.json (quadratisch)"""
        if not self.project_path:
            return 64  # Standard
        
        settings_file = self.project_path / "project.json"
        if settings_file.exists():
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                sprite_size = config.get("sprite_size", 64)
                # Alte Format-Unterstützung (width/height)
                if isinstance(sprite_size, dict):
                    return sprite_size.get("width", sprite_size.get("size", 64))
                else:
                    # Neues Format (nur eine Zahl)
                    return sprite_size if isinstance(sprite_size, int) else 64
            except:
                pass
        return 64  # Standard
    
    def _open_settings(self):
        """Öffnet Projekt-Einstellungen"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Kein Projekt geöffnet!")
            return
        
        dialog = ProjectSettingsDialog(self.project_path, self)
        if dialog.exec() == QDialog.Accepted:
            # Assets neu laden mit neuer Größe
            self._load_assets()
            # Signal für Main Window senden, damit Grid-Einstellungen aktualisiert werden
            self.assets_updated.emit()
            # Signal für Settings-Änderungen senden
            self.settings_changed.emit()
            # Signal für Settings-Änderungen senden
            self.settings_changed.emit()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Wird aufgerufen wenn etwas über den Asset Browser gezogen wird"""
        # Prüfen ob es Objekte vom Canvas sind (Text mit "object_id:" Präfix)
        if event.mimeData().hasText():
            text = event.mimeData().text()
            # Objekt-ID Format: "object_id:xxx"
            if text.startswith("object_id:"):
                event.acceptProposedAction()
                return
        
        # Prüfen ob es Bilddateien sind (für Import)
        if event.mimeData().hasUrls():
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
    
    def _on_folder_changed(self, path: str):
        """Wird aufgerufen wenn sich ein überwachter Ordner ändert"""
        if not self.project_path:
            return
        
        path_obj = Path(path)
        sprites_folder = self.project_path / "sprites"
        images_dir = self.project_path / "assets" / "images"
        
        # Prüfen welcher Ordner sich geändert hat
        if path_obj == sprites_folder or str(path_obj) == str(sprites_folder):
            # sprites/ Ordner geändert - verarbeite neue Sprites
            self.reload_timer.stop()
            self.reload_timer.timeout.disconnect()
            self.reload_timer.timeout.connect(self._process_sprites_folder)
            self.reload_timer.start(500)  # 500ms Verzögerung
        elif path_obj == images_dir or str(path_obj) == str(images_dir):
            # assets/images/ Ordner geändert - aktualisiere Asset Browser
            # Verzögertes Neuladen (verhindert zu häufige Updates)
            self.assets_reload_timer.stop()
            self.assets_reload_timer.start(500)  # 500ms Verzögerung
    
    def _process_sprites_folder(self):
        """Verarbeitet neue Bilder im sprites/ Ordner"""
        if not self.project_path:
            return
        
        sprites_folder = self.project_path / "sprites"
        if not sprites_folder.exists():
            return
        
        sprite_size = self._get_sprite_size()
        images_dir = self.project_path / "assets" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        processed_count = 0
        error_count = 0
        
        # Alle Bilder im sprites/ Ordner prüfen
        for img_file in sprites_folder.rglob("*"):
            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                # Größe prüfen
                pixmap = QPixmap(str(img_file))
                if pixmap.isNull():
                    print(f"[Asset Browser] FEHLER: Bild konnte nicht geladen werden: {img_file.name}")
                    error_count += 1
                    continue
                
                if pixmap.width() != sprite_size or pixmap.height() != sprite_size:
                    print(f"[Asset Browser] FEHLER: {img_file.name} hat falsche Größe: {pixmap.width()}×{pixmap.height()} (erwartet: {sprite_size}×{sprite_size})")
                    error_count += 1
                    continue
                
                # Prüfen ob Datei bereits in assets/images/ existiert (rekursiv)
                # Vergleiche Dateiname UND Dateigröße um sicherzustellen dass es die gleiche Datei ist
                already_exists = False
                source_size = img_file.stat().st_size
                
                for existing_file in images_dir.rglob(img_file.name):
                    if existing_file.is_file():
                        try:
                            # Dateigröße vergleichen (schneller als Hash-Vergleich)
                            if existing_file.stat().st_size == source_size:
                                # Gleiche Größe - wahrscheinlich die gleiche Datei
                                # Optional: Hash-Vergleich für absolute Sicherheit (könnte langsam sein)
                                already_exists = True
                                break
                        except:
                            # Bei Fehler trotzdem als existierend betrachten
                            already_exists = True
                            break
                
                if already_exists:
                    # Datei wurde bereits importiert - überspringen (keine Meldung, ist normal)
                    continue
                
                # Bild nach assets/images/ kopieren
                dest_path = images_dir / img_file.name
                counter = 1
                while dest_path.exists():
                    stem = img_file.stem
                    dest_path = images_dir / f"{stem}_{counter}{img_file.suffix}"
                    counter += 1
                
                try:
                    shutil.copy2(img_file, dest_path)
                    processed_count += 1
                    print(f"[Asset Browser] Bild automatisch importiert: {img_file.name}")
                except Exception as e:
                    print(f"[Asset Browser] FEHLER beim Kopieren: {img_file.name} - {e}")
                    error_count += 1
        
        if processed_count > 0:
            self._load_assets()
            self.assets_updated.emit()
        
        if error_count > 0:
            print(f"[Asset Browser] {error_count} Bild(er) konnten nicht verarbeitet werden")
    
    def dropEvent(self, event: QDropEvent):
        """Wird aufgerufen wenn etwas in den Asset Browser gedroppt wird"""
        if not self.project_path:
            print("[Asset Browser] FEHLER: Kein Projekt geöffnet!")
            event.ignore()
            return
        
        # Prüfen ob es ein Objekt vom Canvas ist (zum Löschen)
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text.startswith("object_id:"):
                obj_id = text.replace("object_id:", "")
                # Objekt löschen über SceneCanvas
                # Signal an Main Window senden, damit es das Objekt löschen kann
                from ..ui.main_window import EditorMainWindow
                # Finde das Main Window
                widget = self
                while widget:
                    if isinstance(widget, EditorMainWindow):
                        # SceneCanvas finden und Objekt löschen
                        if hasattr(widget, 'scene_canvas') and widget.scene_canvas:
                            widget.scene_canvas._delete_object_by_id(obj_id)
                        break
                    widget = widget.parent()
                event.accept()
                return
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            imported_count = 0
            
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
                # Assets neu laden
                self._load_assets()
                
                # Letztes importiertes Asset highlighten
                if last_imported_path:
                    self._select_asset(str(last_imported_path))
                
                self.assets_updated.emit()
                
                # Erfolgsmeldung
                QMessageBox.information(self, "Erfolg", 
                                       f"{imported_count} Datei(en) erfolgreich importiert!")
            
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _organize_sprites(self):
        """Organisiert Sprites aus dem sprites/ Ordner"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Kein Projekt geöffnet!")
            return
        
        organizer = SpriteOrganizer(self.project_path)
        strategy = self.strategy_combo.currentData()
        
        # Prüfen ob sprites/ Ordner existiert und Dateien enthält
        sprites_folder = self.project_path / "sprites"
        if not sprites_folder.exists():
            QMessageBox.information(self, "Info", 
                                   "Der sprites/ Ordner existiert noch nicht.\n"
                                   "Er wird jetzt erstellt.\n\n"
                                   "Legen Sie Ihre Sprites dort ab und klicken Sie erneut auf 'Sprites organisieren'.")
            organizer.create_sprites_folder()
            return
        
        # Sprites organisieren
        try:
            moved_count, errors = organizer.organize_sprites(strategy)
            
            if moved_count > 0:
                message = f"{moved_count} Sprite(s) wurden organisiert!"
                if errors:
                    message += f"\n\nWarnungen:\n" + "\n".join(errors[:5])
                QMessageBox.information(self, "Erfolg", message)
                
                # Assets neu laden
                self._load_assets()
            else:
                if errors:
                    QMessageBox.warning(self, "Warnung", "\n".join(errors))
                else:
                    QMessageBox.information(self, "Info", 
                                           "Keine Sprites gefunden im sprites/ Ordner.\n\n"
                                           "Legen Sie Ihre Sprites dort ab und versuchen Sie es erneut.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", 
                               f"Fehler beim Organisieren der Sprites:\n{e}")
    
    def _extract_spritesheet(self):
        """Extrahiert ein Spritesheet"""
        if not self.project_path:
            QMessageBox.warning(self, "Warnung", "Kein Projekt geöffnet!")
            return
        
        # Spritesheet auswählen
        sprites_folder = self.project_path / "sprites"
        if not sprites_folder.exists():
            QMessageBox.information(self, "Info", 
                                   "Der sprites/ Ordner existiert nicht.\n"
                                   "Bitte legen Sie zuerst Spritesheets dort ab.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Spritesheet auswählen", str(sprites_folder),
            "Bilder (*.png *.jpg *.jpeg *.bmp);;Alle Dateien (*.*)"
        )
        
        if not file_path:
            return
        
        spritesheet_path = Path(file_path)
        
        # Dialog öffnen
        dialog = SpritesheetDialog(self, spritesheet_path)
        if dialog.exec() != QDialog.Accepted:
            return
        
        # Parameter holen
        params = dialog.get_parameters()
        
        # Extrahieren
        try:
            extractor = SpritesheetExtractor(self.project_path)
            extracted_count, errors = extractor.extract_from_grid(
                spritesheet_path,
                params["sprite_width"],
                params["sprite_height"],
                params["output_folder"],
                params["spacing"],
                params["margin"]
            )
            
            # Output-Ordner anzeigen
            if params["output_folder"]:
                output_dir = self.project_path / "assets" / "images" / params["output_folder"]
            else:
                output_dir = self.project_path / "assets" / "images" / spritesheet_path.stem
            
            if extracted_count > 0:
                message = f"{extracted_count} Sprite(s) wurden extrahiert!\n\n"
                message += f"Gespeichert in:\n{output_dir.relative_to(self.project_path)}"
                if errors:
                    message += f"\n\nWarnungen ({len(errors)}):\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... und {len(errors) - 5} weitere"
                QMessageBox.information(self, "Erfolg", message)
                
                # Assets neu laden
                self._load_assets()
            else:
                error_msg = "Keine Sprites konnten extrahiert werden."
                if errors:
                    error_msg += f"\n\nFehler:\n" + "\n".join(errors[:10])
                QMessageBox.warning(self, "Warnung", error_msg)
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(self, "Fehler", 
                               f"Fehler beim Extrahieren des Spritesheets:\n\n{str(e)}\n\n"
                               f"Details:\n{error_details[:500]}")
            
            # Auch in Console ausgeben
            if hasattr(self, 'parent') and hasattr(self.parent(), 'console'):
                self.parent().console.append_error(f"Spritesheet-Extraktion fehlgeschlagen: {e}")
    
    def _on_zoom_changed(self, value: int):
        """Wird aufgerufen wenn Zoom geändert wird"""
        zoom = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.asset_grid.set_zoom(zoom)
    
    def _on_asset_selected(self, sprite_path: str):
        """Wird aufgerufen wenn ein Asset ausgewählt wird"""
        if self.project_path:
            try:
                rel_path = Path(sprite_path).relative_to(self.project_path)
                self.sprite_selected.emit(str(rel_path))
            except ValueError:
                pass
    
    def _on_asset_double_clicked(self, sprite_path: str):
        """Wird aufgerufen wenn ein Asset doppelgeklickt wird"""
        # Signal für Tab-Öffnung
        if self.project_path:
            try:
                rel_path = Path(sprite_path).relative_to(self.project_path)
                # Wird vom Main Window behandelt
                self.sprite_selected.emit(str(rel_path))
            except ValueError:
                pass
    
    def _on_asset_right_clicked(self, sprite_path: str, global_pos: QPoint):
        """Wird aufgerufen bei Rechtsklick - zeigt Details"""
        menu = QMenu(self)
        
        # Pfad anzeigen
        if self.project_path:
            try:
                rel_path = Path(sprite_path).relative_to(self.project_path)
                path_action = menu.addAction(f"Pfad: {rel_path}")
                path_action.setEnabled(False)
            except ValueError:
                pass
        
        menu.addSeparator()
        
        # Details-Action
        details_action = menu.addAction("Details anzeigen...")
        details_action.triggered.connect(lambda: self._show_asset_details(sprite_path))
        
        menu.exec(global_pos)
    
    def _show_asset_details(self, sprite_path: str):
        """Zeigt Details eines Assets"""
        path = Path(sprite_path)
        if not path.exists():
            return
        
        # Größe ermitteln
        pixmap = QPixmap(str(path))
        size_info = f"{pixmap.width()}x{pixmap.height()}" if not pixmap.isNull() else "Unbekannt"
        
        # Relativen Pfad
        if self.project_path:
            try:
                rel_path = path.relative_to(self.project_path)
            except ValueError:
                rel_path = path
        else:
            rel_path = path
        
        message = f"Asset-Details:\n\n"
        message += f"Dateiname: {path.name}\n"
        message += f"Pfad: {rel_path}\n"
        message += f"Größe: {size_info} Pixel\n"
        message += f"Dateigröße: {path.stat().st_size / 1024:.1f} KB"
        
        QMessageBox.information(self, "Asset-Details", message)
    
    def _on_item_double_clicked(self, item):
        """Wird aufgerufen wenn ein Asset doppelgeklickt wird (für Drag & Drop)"""
        sprite_path = item.data(Qt.ItemDataRole.UserRole)
        if sprite_path:
            # Relativen Pfad erzeugen
            if self.project_path:
                rel_path = Path(sprite_path).relative_to(self.project_path)
                self.sprite_selected.emit(str(rel_path))
