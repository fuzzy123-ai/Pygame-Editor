"""
Undo/Redo System - Command Pattern für Rückgängig/Wiederherstellen
"""
from typing import Any, Callable, Optional
from abc import ABC, abstractmethod


class Command(ABC):
    """Basis-Klasse für alle Undo/Redo-Befehle"""
    
    @abstractmethod
    def execute(self) -> None:
        """Führt den Befehl aus"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Macht den Befehl rückgängig"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Gibt eine Beschreibung des Befehls zurück"""
        pass


class UndoRedoManager:
    """Verwaltet Undo/Redo-Historie"""
    
    def __init__(self, max_history: int = 50):
        """
        Args:
            max_history: Maximale Anzahl von Befehlen in der Historie
        """
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self.max_history = max_history
    
    def execute_command(self, command: Command) -> None:
        """Führt einen Befehl aus und fügt ihn zur Undo-Historie hinzu"""
        command.execute()
        self.undo_stack.append(command)
        
        # Redo-Stack leeren (neue Aktion macht Redo-Historie ungültig)
        self.redo_stack.clear()
        
        # Historie begrenzen
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
    
    def undo(self) -> bool:
        """
        Macht die letzte Aktion rückgängig
        
        Returns:
            True wenn erfolgreich, False wenn keine Aktion zum Rückgängigmachen vorhanden
        """
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """
        Stellt die letzte rückgängig gemachte Aktion wieder her
        
        Returns:
            True wenn erfolgreich, False wenn keine Aktion zum Wiederherstellen vorhanden
        """
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True
    
    def can_undo(self) -> bool:
        """Prüft ob eine Undo-Aktion möglich ist"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Prüft ob eine Redo-Aktion möglich ist"""
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """Löscht die gesamte Historie"""
        self.undo_stack.clear()
        self.redo_stack.clear()
    
    def get_undo_description(self) -> Optional[str]:
        """Gibt die Beschreibung der nächsten Undo-Aktion zurück"""
        if self.undo_stack:
            return self.undo_stack[-1].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Gibt die Beschreibung der nächsten Redo-Aktion zurück"""
        if self.redo_stack:
            return self.redo_stack[-1].get_description()
        return None
