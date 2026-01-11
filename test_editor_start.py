"""
Test: Editor-Start mit Fehlerausgabe
"""
import sys
import traceback

try:
    print("Importiere Module...")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    print("  [OK] PySide6 importiert")
    
    print("Erstelle QApplication...")
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    print("  [OK] QApplication erstellt")
    
    print("Importiere EditorMainWindow...")
    from game_editor.ui.main_window import EditorMainWindow
    print("  [OK] EditorMainWindow importiert")
    
    print("Erstelle Hauptfenster...")
    window = EditorMainWindow()
    print("  [OK] Fenster erstellt")
    
    print("Zeige Fenster...")
    window.show()
    print("  [OK] Fenster sollte jetzt sichtbar sein!")
    print()
    print("=" * 60)
    print("Editor sollte jetzt geoeffnet sein!")
    print("Falls nicht, pruefe ob ein anderes Fenster im Hintergrund ist.")
    print("=" * 60)
    print()
    
    print("Starte Event-Loop...")
    sys.exit(app.exec())
    
except Exception as e:
    print()
    print("=" * 60)
    print("FEHLER beim Start:")
    print("=" * 60)
    print(f"Fehler: {e}")
    print()
    print("Traceback:")
    traceback.print_exc()
    input("\nDruecken Sie Enter zum Beenden...")
    sys.exit(1)
