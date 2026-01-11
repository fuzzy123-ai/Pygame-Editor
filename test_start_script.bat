@echo off
REM Test-Skript für Requirements-Prüfung (ohne Editor zu starten)

echo ========================================
echo Test: Requirements-Pruefung
echo ========================================
echo.

REM Python prüfen
echo [1/4] Pruefe Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    exit /b 1
)
python --version
echo [OK] Python gefunden
echo.

REM Pygame prüfen
echo [2/4] Pruefe Pygame...
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [WARNUNG] Pygame nicht gefunden!
) else (
    python -c "import pygame; print('Pygame Version:', pygame.version.ver if hasattr(pygame, 'version') else 'unbekannt')"
    echo [OK] Pygame gefunden
)
echo.

REM PySide6 prüfen
echo [3/4] Pruefe PySide6...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo [WARNUNG] PySide6 nicht gefunden!
) else (
    python -c "import PySide6; print('PySide6 Version:', PySide6.__version__)"
    echo [OK] PySide6 gefunden
)
echo.

REM game_editor Modul prüfen
echo [4/4] Pruefe game_editor Modul...
python -c "from game_editor import editor" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] game_editor Modul nicht gefunden!
    exit /b 1
)
echo [OK] game_editor Modul gefunden
echo.

echo ========================================
echo Alle Tests bestanden!
echo ========================================
pause
