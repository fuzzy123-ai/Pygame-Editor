"""
Konkrete Command-Implementierungen für Undo/Redo
"""
from typing import Any, Dict, List, Optional, Callable
from .undo_redo import Command
from pathlib import Path
import json


class TextChangeCommand(Command):
    """Befehl für Text-Änderungen im Code-Editor"""
    
    def __init__(self, editor_widget, old_text: str, new_text: str, description: str = "Text geändert"):
        """
        Args:
            editor_widget: Das Editor-Widget (QScintilla oder QTextEdit)
            old_text: Alter Text
            new_text: Neuer Text
            description: Beschreibung der Änderung
        """
        self.editor_widget = editor_widget
        self.old_text = old_text
        self.new_text = new_text
        self.description = description
    
    def execute(self) -> None:
        """Setzt den neuen Text"""
        if hasattr(self.editor_widget, 'setText'):
            self.editor_widget.setText(self.new_text)
        else:
            self.editor_widget.setPlainText(self.new_text)
    
    def undo(self) -> None:
        """Setzt den alten Text zurück"""
        if hasattr(self.editor_widget, 'setText'):
            self.editor_widget.setText(self.old_text)
        else:
            self.editor_widget.setPlainText(self.old_text)
    
    def get_description(self) -> str:
        return self.description


class ObjectAddCommand(Command):
    """Befehl für das Hinzufügen eines Objekts"""
    
    def __init__(self, objects_list: List[Dict], new_object: Dict, canvas_update_callback: Callable):
        """
        Args:
            objects_list: Liste aller Objekte
            new_object: Das hinzuzufügende Objekt
            canvas_update_callback: Callback zum Aktualisieren des Canvas
        """
        self.objects_list = objects_list
        self.new_object = new_object.copy()
        self.object_id = new_object.get("id")
        self.canvas_update = canvas_update_callback
    
    def execute(self) -> None:
        """Fügt das Objekt hinzu"""
        # Prüfen ob Objekt bereits existiert (anhand ID)
        existing = any(obj.get("id") == self.object_id for obj in self.objects_list)
        if not existing:
            self.objects_list.append(self.new_object.copy())
        self.canvas_update()
    
    def undo(self) -> None:
        """Entfernt das Objekt"""
        self.objects_list[:] = [obj for obj in self.objects_list if obj.get("id") != self.object_id]
        self.canvas_update()
    
    def get_description(self) -> str:
        return f"Objekt '{self.object_id}' hinzugefügt"


class ObjectDeleteCommand(Command):
    """Befehl für das Löschen eines Objekts"""
    
    def __init__(self, objects_list: List[Dict], deleted_object: Dict, canvas_update_callback: Callable):
        """
        Args:
            objects_list: Liste aller Objekte
            deleted_object: Das gelöschte Objekt
            canvas_update_callback: Callback zum Aktualisieren des Canvas
        """
        self.objects_list = objects_list
        self.deleted_object = deleted_object.copy()
        self.object_id = deleted_object.get("id")
        self.canvas_update = canvas_update_callback
    
    def execute(self) -> None:
        """Entfernt das Objekt"""
        self.objects_list[:] = [obj for obj in self.objects_list if obj.get("id") != self.object_id]
        self.canvas_update()
    
    def undo(self) -> None:
        """Stellt das Objekt wieder her"""
        # Prüfen ob Objekt bereits existiert (anhand ID)
        existing = any(obj.get("id") == self.object_id for obj in self.objects_list)
        if not existing:
            self.objects_list.append(self.deleted_object.copy())
        self.canvas_update()
    
    def get_description(self) -> str:
        return f"Objekt '{self.object_id}' gelöscht"


class ObjectMoveCommand(Command):
    """Befehl für das Verschieben eines Objekts"""
    
    def __init__(self, object_dict: Dict, old_x: int, old_y: int, new_x: int, new_y: int, canvas_update_callback: Callable):
        """
        Args:
            object_dict: Das zu bewegende Objekt
            old_x: Alte X-Position
            old_y: Alte Y-Position
            new_x: Neue X-Position
            new_y: Neue Y-Position
            canvas_update_callback: Callback zum Aktualisieren des Canvas
        """
        self.object_dict = object_dict
        self.old_x = old_x
        self.old_y = old_y
        self.new_x = new_x
        self.new_y = new_y
        self.canvas_update = canvas_update_callback
        
        # Kollisionsbox-Positionen speichern (falls vorhanden)
        collider_data = object_dict.get("collider", {})
        if collider_data.get("enabled", False):
            self.old_collider_x = collider_data.get("x", old_x)
            self.old_collider_y = collider_data.get("y", old_y)
            self.has_collider = True
        else:
            self.has_collider = False
    
    def execute(self) -> None:
        """Bewegt das Objekt zur neuen Position"""
        # Delta berechnen
        delta_x = self.new_x - self.old_x
        delta_y = self.new_y - self.old_y
        
        self.object_dict["x"] = self.new_x
        self.object_dict["y"] = self.new_y
        
        # Kollisionsbox mitbewegen (Offset beibehalten)
        if self.has_collider:
            collider_data = self.object_dict.get("collider", {})
            if collider_data.get("enabled", False):
                if "x" in collider_data:
                    collider_data["x"] = collider_data.get("x", self.old_x) + delta_x
                if "y" in collider_data:
                    collider_data["y"] = collider_data.get("y", self.old_y) + delta_y
        
        self.canvas_update()
    
    def undo(self) -> None:
        """Bewegt das Objekt zurück zur alten Position"""
        # Delta berechnen (rückwärts)
        delta_x = self.old_x - self.new_x
        delta_y = self.old_y - self.new_y
        
        self.object_dict["x"] = self.old_x
        self.object_dict["y"] = self.old_y
        
        # Kollisionsbox mitbewegen (Offset beibehalten)
        if self.has_collider:
            collider_data = self.object_dict.get("collider", {})
            if collider_data.get("enabled", False):
                if "x" in collider_data:
                    collider_data["x"] = collider_data.get("x", self.new_x) + delta_x
                if "y" in collider_data:
                    collider_data["y"] = collider_data.get("y", self.new_y) + delta_y
        
        self.canvas_update()
    
    def get_description(self) -> str:
        return f"Objekt '{self.object_dict.get('id', 'unknown')}' verschoben"


class ObjectPropertyChangeCommand(Command):
    """Befehl für Änderungen von Objekt-Eigenschaften"""
    
    def __init__(self, object_dict: Dict, property_name: str, old_value: Any, new_value: Any, canvas_update_callback: Callable):
        """
        Args:
            object_dict: Das zu ändernde Objekt
            property_name: Name der Eigenschaft (z.B. "width", "height", "sprite")
            old_value: Alter Wert
            new_value: Neuer Wert
            canvas_update_callback: Callback zum Aktualisieren des Canvas
        """
        self.object_dict = object_dict
        self.property_name = property_name
        self.old_value = old_value
        self.new_value = new_value
        self.canvas_update = canvas_update_callback
    
    def execute(self) -> None:
        """Setzt die neue Eigenschaft"""
        self.object_dict[self.property_name] = self.new_value
        self.canvas_update()
    
    def undo(self) -> None:
        """Setzt die alte Eigenschaft zurück"""
        self.object_dict[self.property_name] = self.old_value
        self.canvas_update()
    
    def get_description(self) -> str:
        return f"Eigenschaft '{self.property_name}' von '{self.object_dict.get('id', 'unknown')}' geändert"
