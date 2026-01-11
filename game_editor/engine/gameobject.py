"""
GameObject - Repräsentiert ein Objekt im Spiel
"""
from pathlib import Path
from typing import Optional, Dict, Any
import pygame


class GameObject:
    """Ein Spielobjekt mit Position, Größe, Sprite und Collider"""
    
    def __init__(self, data: Dict[str, Any], project_dir: Path, sprite_size: Optional[int] = None):
        """
        Erstellt ein GameObject aus JSON-Daten
        
        Args:
            data: Objekt-Daten aus JSON (id, type, x, y, width, height, sprite, collider)
            project_dir: Projektverzeichnis für relative Pfade
            sprite_size: Sprite-Größe aus Projekteinstellungen (wird automatisch geladen wenn None)
        """
        self.id: str = data.get("id", "unknown")
        self.type: str = data.get("type", "sprite")
        
        # Position und Größe
        self.x: float = float(data.get("x", 0))
        self.y: float = float(data.get("y", 0))
        self.width: float = float(data.get("width", 32))
        self.height: float = float(data.get("height", 32))
        
        # Sichtbarkeit
        self.visible: bool = data.get("visible", True)
        
        # Sprite-Größe aus Projekteinstellungen laden (falls nicht übergeben)
        if sprite_size is None:
            try:
                import json
                project_file = project_dir / "project.json"
                if project_file.exists():
                    with open(project_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    sprite_size_config = config.get("sprite_size", 64)
                    if isinstance(sprite_size_config, dict):
                        sprite_size = sprite_size_config.get("width", sprite_size_config.get("size", 64))
                    else:
                        sprite_size = sprite_size_config if isinstance(sprite_size_config, int) else 64
                else:
                    sprite_size = 64  # Standard
            except Exception:
                sprite_size = 64  # Standard bei Fehler
        
        # Sprite laden
        self._sprite_path: Optional[str] = data.get("sprite")
        self._sprite_surface: Optional[pygame.Surface] = None
        if self._sprite_path:
            sprite_full_path = project_dir / self._sprite_path
            if sprite_full_path.exists():
                try:
                    self._sprite_surface = pygame.image.load(str(sprite_full_path)).convert_alpha()
                    # Immer auf die Projekteinstellungs-Größe skalieren
                    target_size = int(sprite_size)
                    if self._sprite_surface.get_width() != target_size or \
                       self._sprite_surface.get_height() != target_size:
                        self._sprite_surface = pygame.transform.scale(
                            self._sprite_surface, 
                            (target_size, target_size)
                        )
                except Exception as e:
                    print(f"Warnung: Sprite {self._sprite_path} konnte nicht geladen werden: {e}")
        
        # Collider
        self._collider_enabled: bool = False
        self._collider_type: str = "rect"
        self._collider_x: float = 0.0
        self._collider_y: float = 0.0
        self._collider_width: float = 0.0
        self._collider_height: float = 0.0
        
        if "collider" in data and data["collider"].get("enabled", False):
            self._collider_enabled = True
            self._collider_type = data["collider"].get("type", "rect")
            # Kollisionsbox-Position und -Größe (falls explizit gesetzt, sonst Objekt-Werte)
            self._collider_x = float(data["collider"].get("x", self.x))
            self._collider_y = float(data["collider"].get("y", self.y))
            self._collider_width = float(data["collider"].get("width", self.width))
            self._collider_height = float(data["collider"].get("height", self.height))
        
        # Ground (Boden-Tile)
        self.is_ground: bool = data.get("ground", False)
        
        # Referenz zu allen Objekten (für collides_with)
        self._all_objects: list['GameObject'] = []
    
    def set_all_objects(self, objects: list['GameObject']):
        """Setzt die Liste aller Objekte (für Kollisionserkennung)"""
        self._all_objects = objects
    
    @property
    def sprite(self) -> Optional[str]:
        """Gibt den Sprite-Pfad zurück"""
        return self._sprite_path
    
    @sprite.setter
    def sprite(self, path: str):
        """Setzt einen neuen Sprite (relativer Pfad)"""
        self._sprite_path = path
    
    def collides_with(self, other_id: str) -> bool:
        """
        Prüft ob dieses Objekt mit einem anderen kollidiert
        
        Args:
            other_id: ID des anderen Objekts
            
        Returns:
            True wenn Kollision, sonst False
        """
        if not self._collider_enabled:
            return False
        
        # Anderes Objekt finden
        other = None
        for obj in self._all_objects:
            if obj.id == other_id and obj._collider_enabled:
                other = obj
                break
        
        if other is None:
            return False
        
        # AABB Collision Detection mit Kollisionsboxen
        # Verwende Kollisionsbox-Positionen und -Größen
        return (self._collider_x < other._collider_x + other._collider_width and
                self._collider_x + self._collider_width > other._collider_x and
                self._collider_y < other._collider_y + other._collider_height and
                self._collider_y + self._collider_height > other._collider_y)
    
    def destroy(self):
        """Markiert das Objekt zum Entfernen"""
        self.visible = False
        # Objekt wird in der nächsten Update-Phase aus der Liste entfernt
    
    def draw(self, screen: pygame.Surface, debug: bool = False):
        """Zeichnet das Objekt auf den Screen"""
        if not self.visible:
            return
        
        # Sprite zeichnen
        if self._sprite_surface:
            screen.blit(self._sprite_surface, (int(self.x), int(self.y)))
        else:
            # Fallback: Rechteck wenn kein Sprite
            color = (200, 200, 200) if self.type == "sprite" else (100, 100, 100)
            pygame.draw.rect(screen, color, 
                           (int(self.x), int(self.y), int(self.width), int(self.height)))
        
        # Debug: Collider-Box (rote Box für Kollisionsbox)
        if debug and self._collider_enabled:
            pygame.draw.rect(screen, (255, 0, 0), 
                           (int(self._collider_x), int(self._collider_y), 
                            int(self._collider_width), int(self._collider_height)), 
                           2)
            # Objekt-ID anzeigen
            font = pygame.font.Font(None, 24)
            text = font.render(self.id, True, (255, 255, 255))
            screen.blit(text, (int(self.x), int(self.y) - 20))
