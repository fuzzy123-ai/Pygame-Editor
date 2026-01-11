"""
GameDev-Edu Editor - Hauptprogramm
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from .ui.main_window import EditorMainWindow
from .utils.single_instance import is_instance_running, create_lock_file, remove_lock_file


def main():
    """Hauptfunktion - Startet den Editor"""
    # Single-Instance-Check
    if is_instance_running():
        QMessageBox.warning(
            None, "Editor bereits geöffnet",
            "Der Editor läuft bereits!\n\nBitte schließen Sie die vorhandene Instanz, "
            "bevor Sie eine neue starten."
        )
        sys.exit(1)
    
    # Lock-Datei erstellen
    if not create_lock_file():
        QMessageBox.warning(
            None, "Fehler",
            "Konnte Lock-Datei nicht erstellen.\n\nDer Editor wird trotzdem gestartet, "
            "aber es können mehrere Instanzen laufen."
        )
    
    app = QApplication(sys.argv)
    
    # High DPI Support
    # High DPI Scaling ist in neueren Qt-Versionen (6.5+) standardmäßig aktiviert
    # Die Attribute AA_EnableHighDpiScaling und AA_UseHighDpiPixmaps sind deprecated
    # und werden nicht mehr benötigt
    
    # Main Window
    window = EditorMainWindow()
    window.show()
    
    # Fenster in den Vordergrund bringen (mehrfach für Sicherheit)
    window.raise_()
    window.activateWindow()
    
    # Windows-spezifisch: Fenster fokussieren
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = int(window.winId())
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.BringWindowToTop(hwnd)
        except:
            pass
    
    # Cleanup beim Beenden
    app.aboutToQuit.connect(remove_lock_file)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
