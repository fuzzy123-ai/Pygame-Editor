@echo off
REM GameDev-Edu Editor Starter (Windows)
REM Prüft Requirements und startet den Editor

echo ========================================
echo GameDev-Edu Editor Starter
echo ========================================
echo.

REM Python prüfen
echo [1/4] Pruefe Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python 3.10 oder hoeher.
    pause
    exit /b 1
)
python --version
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNUNG] Python 3.10 oder hoeher wird empfohlen!
    echo.
    echo Moechten Sie trotzdem fortfahren? (J/N)
    set /p CONTINUE=
    if /i not "%CONTINUE%"=="J" (
        exit /b 1
    )
) else (
    echo [OK] Python Version OK ^(3.10+^)
)
echo.

REM Pygame prüfen
echo [2/4] Pruefe Pygame...
python -c "import pygame; print('pygame-ce' if hasattr(pygame, 'version') else 'pygame')" >nul 2>&1
if errorlevel 1 (
    echo [WARNUNG] Pygame nicht gefunden!
    pip --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] pip ist nicht verfuegbar! Bitte installieren Sie Pygame manuell:
        echo   pip install pygame-ce
        pause
        exit /b 1
    )
    echo Installiere Pygame...
    pip install pygame-ce
    if errorlevel 1 (
        echo [FEHLER] Pygame konnte nicht installiert werden!
        echo Versuche pygame statt pygame-ce...
        pip install pygame
        if errorlevel 1 (
            echo [FEHLER] Installation fehlgeschlagen!
            pause
            exit /b 1
        )
    )
    echo [OK] Pygame installiert
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
    pip --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] pip ist nicht verfuegbar! Bitte installieren Sie PySide6 manuell:
        echo   pip install PySide6
        pause
        exit /b 1
    )
    echo Installiere PySide6...
    pip install PySide6
    if errorlevel 1 (
        echo [FEHLER] PySide6 konnte nicht installiert werden!
        pause
        exit /b 1
    )
    echo [OK] PySide6 installiert
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
    echo Bitte stellen Sie sicher, dass Sie im richtigen Verzeichnis sind.
    echo Aktuelles Verzeichnis: %CD%
    pause
    exit /b 1
)
echo [OK] game_editor Modul gefunden
echo.

REM Alles OK - Editor starten
echo ========================================
echo Alle Requirements erfuellt!
echo Starte Editor...
echo ========================================
echo.

python -m game_editor.editor

if errorlevel 1 (
    echo.
    echo [FEHLER] Editor konnte nicht gestartet werden!
    pause
    exit /b 1
)

pause
