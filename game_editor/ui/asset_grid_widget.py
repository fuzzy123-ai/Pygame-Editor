"""
Asset Grid Widget - Raster-Ansicht für Assets mit Zoom
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QMenu, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QPixmap, QIcon, QMouseEvent, QWheelEvent
from pathlib import Path
from typing import List, Tuple, Optional, Dict


class AssetGridWidget(QWidget):
    """Raster-Widget für Asset-Anzeige mit Zoom"""
    
    asset_selected = Signal(str)  # Signal mit Sprite-Pfad
    asset_double_clicked = Signal(str)  # Signal für Doppelklick
    asset_right_clicked = Signal(str, QPoint)  # Signal für Rechtsklick
    
    def __init__(self):
        super().__init__()
        self.assets: List[Tuple[str, Path]] = []  # (display_name, full_path)
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.columns = 2  # Standard: 2 Spalten
        self.thumbnail_size = 128  # Basis-Thumbnail-Größe
        self.selected_index = -1
        
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)
        
        # Thumbnail-Cache
        self.thumbnail_cache: Dict[str, QPixmap] = {}
    
    def set_assets(self, assets: List[Tuple[str, Path]]):
        """Setzt die anzuzeigenden Assets"""
        self.assets = assets
        self.thumbnail_cache.clear()
        self.update()
    
    def set_zoom(self, zoom: float):
        """Setzt den Zoom-Level"""
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, zoom))
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Mausrad für Zoom"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_level = min(self.max_zoom, self.zoom_level + 0.1)
        else:
            self.zoom_level = max(self.min_zoom, self.zoom_level - 0.1)
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Maus-Druck Event"""
        if event.button() == Qt.LeftButton:
            index = self._get_asset_at_position(event.position().toPoint())
            if index >= 0:
                self.selected_index = index
                _, path = self.assets[index]
                self.asset_selected.emit(str(path))
                self.update()
                
                # Drag & Drop starten
                self._start_drag(event.position().toPoint(), str(path))
        elif event.button() == Qt.RightButton:
            index = self._get_asset_at_position(event.position().toPoint())
            if index >= 0:
                _, path = self.assets[index]
                self.asset_right_clicked.emit(str(path), event.globalPosition().toPoint())
    
    def _start_drag(self, pos: QPoint, sprite_path: str):
        """Startet Drag & Drop"""
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(sprite_path)
        drag.setMimeData(mime_data)
        
        # Thumbnail als Drag-Bild
        if sprite_path in self.thumbnail_cache:
            thumb = self.thumbnail_cache[sprite_path]
            drag.setPixmap(thumb)
            drag.setHotSpot(pos)
        
        drag.exec(Qt.CopyAction)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Doppelklick Event"""
        if event.button() == Qt.LeftButton:
            index = self._get_asset_at_position(event.position().toPoint())
            if index >= 0:
                _, path = self.assets[index]
                self.asset_double_clicked.emit(str(path))
    
    def _get_asset_at_position(self, pos: QPoint) -> int:
        """Gibt den Index des Assets an der Position zurück"""
        current_size = int(self.thumbnail_size * self.zoom_level)
        spacing = 10
        item_width = current_size + spacing
        item_height = current_size + 30 + spacing  # +30 für Text
        
        col = pos.x() // item_width
        row = pos.y() // item_height
        
        index = row * self.columns + col
        if 0 <= index < len(self.assets):
            # Prüfe ob wirklich im Thumbnail-Bereich
            item_x = col * item_width + spacing // 2
            item_y = row * item_height + spacing // 2
            if (item_x <= pos.x() <= item_x + current_size and
                item_y <= pos.y() <= item_y + current_size):
                return index
        return -1
    
    def paintEvent(self, event: QPaintEvent):
        """Zeichnet das Raster"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        current_size = int(self.thumbnail_size * self.zoom_level)
        spacing = 10
        item_width = current_size + spacing
        item_height = current_size + 30 + spacing
        
        x = spacing // 2
        y = spacing // 2
        
        for i, (display_name, path) in enumerate(self.assets):
            col = i % self.columns
            row = i // self.columns
            
            item_x = col * item_width + spacing // 2
            item_y = row * item_height + spacing // 2
            
            # Thumbnail laden/cachen
            if str(path) not in self.thumbnail_cache:
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        current_size, current_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.thumbnail_cache[str(path)] = scaled
            
            # Hintergrund für selektiertes Item
            if i == self.selected_index:
                painter.fillRect(
                    item_x - 2, item_y - 2,
                    current_size + 4, current_size + 4,
                    QColor(100, 150, 255, 100)
                )
            
            # Thumbnail zeichnen
            if str(path) in self.thumbnail_cache:
                thumb = self.thumbnail_cache[str(path)]
                thumb_x = item_x + (current_size - thumb.width()) // 2
                thumb_y = item_y + (current_size - thumb.height()) // 2
                painter.drawPixmap(thumb_x, thumb_y, thumb)
            
            # Dateiname (nur wenn Zoom groß genug)
            if self.zoom_level >= 0.7:
                painter.setPen(QColor(0, 0, 0))
                text_rect = QRect(item_x, item_y + current_size + 5, current_size, 25)
                painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, 
                               Path(display_name).name)
        
        # Gesamtgröße setzen
        total_rows = (len(self.assets) + self.columns - 1) // self.columns
        total_height = total_rows * item_height + spacing
        self.setMinimumHeight(total_height)
    
    def sizeHint(self) -> QSize:
        """Gibt die bevorzugte Größe zurück"""
        current_size = int(self.thumbnail_size * self.zoom_level)
        spacing = 10
        item_width = current_size + spacing
        item_height = current_size + 30 + spacing
        
        total_rows = (len(self.assets) + self.columns - 1) // self.columns
        total_height = total_rows * item_height + spacing
        
        return QSize(self.columns * item_width, total_height)
