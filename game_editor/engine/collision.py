"""
Kollisionssystem - AABB (Axis-Aligned Bounding Box) Kollisionserkennung
"""
from typing import List
from .gameobject import GameObject


class CollisionSystem:
    """Verwaltet Kollisionserkennung zwischen Objekten"""
    
    @staticmethod
    def check_collision(obj1: GameObject, obj2: GameObject) -> bool:
        """
        Prüft ob zwei Objekte kollidieren (AABB)
        
        Args:
            obj1: Erstes Objekt
            obj2: Zweites Objekt
            
        Returns:
            True wenn Kollision, sonst False
        """
        if not obj1._collider_enabled or not obj2._collider_enabled:
            return False
        
        # Verwende Kollisionsbox-Positionen und -Größen
        return (obj1._collider_x < obj2._collider_x + obj2._collider_width and
                obj1._collider_x + obj1._collider_width > obj2._collider_x and
                obj1._collider_y < obj2._collider_y + obj2._collider_height and
                obj1._collider_y + obj1._collider_height > obj2._collider_y)
    
    @staticmethod
    def get_colliding_objects(obj: GameObject, all_objects: List[GameObject]) -> List[GameObject]:
        """
        Gibt alle Objekte zurück, mit denen das gegebene Objekt kollidiert
        
        Args:
            obj: Das zu prüfende Objekt
            all_objects: Liste aller Objekte
            
        Returns:
            Liste aller kollidierenden Objekte
        """
        colliding = []
        for other in all_objects:
            if other.id != obj.id and CollisionSystem.check_collision(obj, other):
                colliding.append(other)
        return colliding
