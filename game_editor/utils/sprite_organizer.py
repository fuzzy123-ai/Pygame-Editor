"""
Sprite Organizer - Sortiert Sprites aus dem sprites/ Ordner automatisch
"""
from pathlib import Path
import shutil
from typing import List, Tuple, Optional

# PIL/Pillow optional - falls nicht verfügbar, verwende QPixmap
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    try:
        from PySide6.QtGui import QPixmap
        HAS_QT = True
    except ImportError:
        HAS_QT = False


class SpriteOrganizer:
    """Organisiert Sprites automatisch nach verschiedenen Kriterien"""
    
    def __init__(self, project_path: Path):
        """
        Args:
            project_path: Pfad zum Projektordner
        """
        self.project_path = project_path
        self.sprites_folder = project_path / "sprites"
        self.assets_images = project_path / "assets" / "images"
    
    def organize_sprites(self, strategy: str = "size") -> Tuple[int, List[str]]:
        """
        Organisiert alle Sprites aus dem sprites/ Ordner
        
        Args:
            strategy: Sortier-Strategie ("size", "name", "flat")
                - "size": Nach Größe (klein, mittel, groß)
                - "name": Nach Dateinamen-Präfixen
                - "flat": Alle in assets/images/
        
        Returns:
            Tuple (anzahl_verschoben, liste_der_fehler)
        """
        if not self.sprites_folder.exists():
            return (0, ["sprites/ Ordner existiert nicht"])
        
        moved_count = 0
        errors = []
        
        # assets/images erstellen falls nicht existiert
        self.assets_images.mkdir(parents=True, exist_ok=True)
        
        # Alle Bilddateien finden
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
        sprite_files = [
            f for f in self.sprites_folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not sprite_files:
            return (0, ["Keine Sprites gefunden im sprites/ Ordner"])
        
        for sprite_file in sprite_files:
            try:
                target_path = self._determine_target_path(sprite_file, strategy)
                
                # Datei verschieben (nicht kopieren, damit sprites/ leer wird)
                if target_path.exists():
                    # Datei existiert bereits - umbenennen
                    base_name = sprite_file.stem
                    counter = 1
                    while target_path.exists():
                        new_name = f"{base_name}_{counter}{sprite_file.suffix}"
                        target_path = target_path.parent / new_name
                        counter += 1
                
                shutil.move(str(sprite_file), str(target_path))
                moved_count += 1
                
            except Exception as e:
                errors.append(f"Fehler bei {sprite_file.name}: {e}")
        
        return (moved_count, errors)
    
    def _determine_target_path(self, sprite_file: Path, strategy: str) -> Path:
        """Bestimmt den Zielpfad basierend auf der Strategie"""
        
        if strategy == "flat":
            # Alle direkt in assets/images/
            return self.assets_images / sprite_file.name
        
        elif strategy == "size":
            # Nach Größe sortieren
            try:
                if HAS_PIL:
                    with Image.open(sprite_file) as img:
                        width, height = img.size
                        max_dimension = max(width, height)
                elif HAS_QT:
                    pixmap = QPixmap(str(sprite_file))
                    if not pixmap.isNull():
                        width = pixmap.width()
                        height = pixmap.height()
                        max_dimension = max(width, height)
                    else:
                        raise Exception("Bild konnte nicht geladen werden")
                else:
                    # Fallback: Nach Dateinamen raten
                    raise Exception("Keine Bild-Bibliothek verfügbar")
                
                if max_dimension <= 32:
                    folder = "small"
                elif max_dimension <= 64:
                    folder = "medium"
                else:
                    folder = "large"
                
                target_dir = self.assets_images / folder
                target_dir.mkdir(parents=True, exist_ok=True)
                return target_dir / sprite_file.name
                
            except Exception:
                # Falls Bild nicht geladen werden kann, in "other"
                target_dir = self.assets_images / "other"
                target_dir.mkdir(parents=True, exist_ok=True)
                return target_dir / sprite_file.name
        
        elif strategy == "name":
            # Nach Dateinamen-Präfixen sortieren
            # z.B. "player_idle.png" -> assets/images/player/
            #      "enemy_walk.png" -> assets/images/enemy/
            
            name_parts = sprite_file.stem.split('_')
            if len(name_parts) > 1:
                category = name_parts[0]  # Erster Teil als Kategorie
            else:
                category = "misc"
            
            target_dir = self.assets_images / category
            target_dir.mkdir(parents=True, exist_ok=True)
            return target_dir / sprite_file.name
        
        else:
            # Default: flat
            return self.assets_images / sprite_file.name
    
    def create_sprites_folder(self):
        """Erstellt den sprites/ Ordner falls er nicht existiert"""
        self.sprites_folder.mkdir(parents=True, exist_ok=True)
        
        # README im sprites/ Ordner erstellen
        readme_path = self.sprites_folder / "README.txt"
        if not readme_path.exists():
            readme_content = """SPRITES ORDNER
===============

Legen Sie hier alle Ihre Sprites/Bilder ab.
Der Asset Browser kann diese dann automatisch sortieren.

Sortier-Strategien:
- "size": Nach Größe (small, medium, large)
- "name": Nach Dateinamen-Präfix (z.B. "player_*.png" -> player/)
- "flat": Alle in assets/images/

Im Asset Browser: "Sprites organisieren" Button
"""
            readme_path.write_text(readme_content, encoding='utf-8')
