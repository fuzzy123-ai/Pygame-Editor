"""
Spritesheet Extractor - Extrahiert einzelne Sprites aus Spritesheets
"""
from pathlib import Path
from typing import List, Tuple, Optional
import json

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    try:
        from PySide6.QtGui import QPixmap, QImage
        HAS_QT = True
    except ImportError:
        HAS_QT = False


class SpritesheetExtractor:
    """Extrahiert einzelne Sprites aus Spritesheets"""
    
    def __init__(self, project_path: Path):
        """
        Args:
            project_path: Pfad zum Projektordner
        """
        self.project_path = project_path
        self.assets_images = project_path / "assets" / "images"
    
    def extract_from_grid(self, spritesheet_path: Path, 
                         sprite_width: int, sprite_height: int,
                         output_folder: str = None,
                         spacing: int = 0,
                         margin: int = 0) -> Tuple[int, List[str]]:
        """
        Extrahiert Sprites aus einem Grid-basierten Spritesheet
        
        Args:
            spritesheet_path: Pfad zum Spritesheet
            sprite_width: Breite eines einzelnen Sprites
            sprite_height: Höhe eines einzelnen Sprites
            output_folder: Unterordner in assets/images/ (optional)
            spacing: Abstand zwischen Sprites (optional)
            margin: Rand um das gesamte Sheet (optional)
        
        Returns:
            Tuple (anzahl_extrahiert, liste_der_fehler)
        """
        if not spritesheet_path.exists():
            return (0, [f"Spritesheet nicht gefunden: {spritesheet_path}"])
        
        extracted_count = 0
        errors = []
        
        # Output-Ordner
        if output_folder:
            output_dir = self.assets_images / output_folder
        else:
            # Aus Dateinamen ableiten
            output_dir = self.assets_images / spritesheet_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if HAS_PIL:
                # Mit PIL
                img = Image.open(spritesheet_path)
                sheet_width, sheet_height = img.size
            elif HAS_QT:
                # Mit Qt
                pixmap = QPixmap(str(spritesheet_path))
                if pixmap.isNull():
                    return (0, ["Spritesheet konnte nicht geladen werden"])
                sheet_width = pixmap.width()
                sheet_height = pixmap.height()
                # pixmap wird später für copy() verwendet
            else:
                return (0, ["Keine Bild-Bibliothek verfügbar (PIL oder Qt)"])
            
            # Berechne wie viele Sprites pro Zeile/Spalte
            # Formel: (Gesamtbreite - 2*Rand + Abstand) / (Spritebreite + Abstand)
            if sprite_width + spacing == 0 or sprite_height + spacing == 0:
                return (0, ["Ungültige Sprite-Größe oder Abstand"])
            
            cols = (sheet_width - margin * 2 + spacing) // (sprite_width + spacing)
            rows = (sheet_height - margin * 2 + spacing) // (sprite_height + spacing)
            
            if cols <= 0 or rows <= 0:
                return (0, [f"Keine Sprites gefunden! Sheet: {sheet_width}x{sheet_height}, "
                           f"Sprite: {sprite_width}x{sprite_height}, "
                           f"Berechnet: {cols} Spalten x {rows} Zeilen"])
            
            sprite_index = 0
            
            for row in range(rows):
                for col in range(cols):
                    # Position berechnen
                    x = margin + col * (sprite_width + spacing)
                    y = margin + row * (sprite_height + spacing)
                    
                    # Prüfen ob noch im Bild
                    if x + sprite_width > sheet_width or y + sprite_height > sheet_height:
                        continue
                    
                    try:
                        if HAS_PIL:
                            # Sprite extrahieren
                            sprite = img.crop((x, y, x + sprite_width, y + sprite_height))
                            
                            # Speichern
                            output_name = f"{spritesheet_path.stem}_{sprite_index:03d}.png"
                            output_path = output_dir / output_name
                            sprite.save(output_path, "PNG")
                            
                        elif HAS_QT:
                            # Sprite extrahieren
                            sprite_pixmap = pixmap.copy(x, y, sprite_width, sprite_height)
                            
                            if sprite_pixmap.isNull():
                                errors.append(f"Sprite ({row}, {col}) konnte nicht extrahiert werden")
                                continue
                            
                            # Speichern
                            output_name = f"{spritesheet_path.stem}_{sprite_index:03d}.png"
                            output_path = output_dir / output_name
                            
                            if not sprite_pixmap.save(str(output_path), "PNG"):
                                errors.append(f"Konnte Sprite nicht speichern: {output_name}")
                                continue
                        
                        extracted_count += 1
                        sprite_index += 1
                        
                    except Exception as e:
                        errors.append(f"Fehler bei Sprite ({row}, {col}): {e}")
            
            return (extracted_count, errors)
            
        except Exception as e:
            return (0, [f"Fehler beim Extrahieren: {e}"])
    
    def extract_from_json_config(self, spritesheet_path: Path, 
                                 config_path: Path) -> Tuple[int, List[str]]:
        """
        Extrahiert Sprites basierend auf einer JSON-Konfiguration
        
        JSON-Format:
        {
            "sprites": [
                {"name": "idle_0", "x": 0, "y": 0, "width": 32, "height": 48},
                {"name": "idle_1", "x": 32, "y": 0, "width": 32, "height": 48}
            ]
        }
        """
        if not spritesheet_path.exists():
            return (0, [f"Spritesheet nicht gefunden: {spritesheet_path}"])
        
        if not config_path.exists():
            return (0, [f"Konfiguration nicht gefunden: {config_path}"])
        
        extracted_count = 0
        errors = []
        
        try:
            # JSON laden
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Output-Ordner
            output_dir = self.assets_images / spritesheet_path.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if HAS_PIL:
                img = Image.open(spritesheet_path)
            elif HAS_QT:
                pixmap = QPixmap(str(spritesheet_path))
                if pixmap.isNull():
                    return (0, ["Spritesheet konnte nicht geladen werden"])
            else:
                return (0, ["Keine Bild-Bibliothek verfügbar"])
            
            # Sprites extrahieren
            for sprite_def in config.get("sprites", []):
                name = sprite_def.get("name", f"sprite_{extracted_count}")
                x = sprite_def.get("x", 0)
                y = sprite_def.get("y", 0)
                width = sprite_def.get("width", 32)
                height = sprite_def.get("height", 32)
                
                try:
                    if HAS_PIL:
                        sprite = img.crop((x, y, x + width, y + height))
                        output_path = output_dir / f"{name}.png"
                        sprite.save(output_path, "PNG")
                    elif HAS_QT:
                        sprite_pixmap = pixmap.copy(x, y, width, height)
                        output_path = output_dir / f"{name}.png"
                        sprite_pixmap.save(str(output_path), "PNG")
                    
                    extracted_count += 1
                    
                except Exception as e:
                    errors.append(f"Fehler bei Sprite '{name}': {e}")
            
            return (extracted_count, errors)
            
        except Exception as e:
            return (0, [f"Fehler beim Extrahieren: {e}"])
