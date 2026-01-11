"""
Sprite Viewer Tab - Zeigt ein einzelnes Sprite groß an
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPaintEvent
from pathlib import Path


class SpriteViewerTab(QWidget):
    """Tab zum Anzeigen eines einzelnen Sprites"""
    
    def __init__(self, sprite_path: Path, project_path: Path):
        super().__init__()
        self.sprite_path = sprite_path
        self.project_path = project_path
        self._init_ui()
    
    def _init_ui(self):
        """Initialisiert die UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Titel
        title = QLabel(f"Sprite: {self.sprite_path.name}")
        title.setStyleSheet("font-weight: bold; font-size: 14pt; padding: 10px;")
        layout.addWidget(title)
        
        # ScrollArea für großes Bild
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        
        # Sprite-Widget
        self.sprite_widget = SpriteDisplayWidget(self.sprite_path)
        scroll.setWidget(self.sprite_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def get_tab_name(self) -> str:
        """Gibt den Namen für den Tab zurück"""
        return self.sprite_path.name


class SpriteDisplayWidget(QWidget):
    """Widget zum Anzeigen eines Sprites"""
    
    def __init__(self, sprite_path: Path):
        super().__init__()
        self.sprite_path = sprite_path
        self.pixmap = QPixmap(str(sprite_path))
        if not self.pixmap.isNull():
            self.setMinimumSize(self.pixmap.size())
    
    def paintEvent(self, event: QPaintEvent):
        """Zeichnet das Sprite"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.pixmap.isNull():
            # Sprite zentriert zeichnen
            x = (self.width() - self.pixmap.width()) // 2
            y = (self.height() - self.pixmap.height()) // 2
            painter.drawPixmap(x, y, self.pixmap)
