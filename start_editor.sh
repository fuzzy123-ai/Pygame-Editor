#!/bin/bash
# GameDev-Edu Editor Starter (Linux/Mac)
# Prüft Requirements und startet den Editor

echo "========================================"
echo "GameDev-Edu Editor Starter"
echo "========================================"
echo ""

# Python prüfen
echo "[1/4] Prüfe Python..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[FEHLER] Python ist nicht installiert oder nicht im PATH!"
    echo "Bitte installieren Sie Python 3.10 oder höher."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD --version
echo "[OK] Python gefunden"
echo ""

# Pygame prüfen
echo "[2/4] Prüfe Pygame..."
if ! $PYTHON_CMD -c "import pygame" 2>/dev/null; then
    echo "[WARNUNG] Pygame nicht gefunden!"
    echo "Installiere Pygame..."
    pip3 install pygame-ce 2>/dev/null || pip install pygame-ce
    if [ $? -ne 0 ]; then
        echo "[FEHLER] Pygame konnte nicht installiert werden!"
        exit 1
    fi
else
    $PYTHON_CMD -c "import pygame; print('Pygame Version:', pygame.version.ver if hasattr(pygame, 'version') else 'unbekannt')"
    echo "[OK] Pygame gefunden"
fi
echo ""

# PySide6 prüfen
echo "[3/4] Prüfe PySide6..."
if ! $PYTHON_CMD -c "import PySide6" 2>/dev/null; then
    echo "[WARNUNG] PySide6 nicht gefunden!"
    echo "Installiere PySide6..."
    pip3 install PySide6 2>/dev/null || pip install PySide6
    if [ $? -ne 0 ]; then
        echo "[FEHLER] PySide6 konnte nicht installiert werden!"
        exit 1
    fi
else
    $PYTHON_CMD -c "import PySide6; print('PySide6 Version:', PySide6.__version__)"
    echo "[OK] PySide6 gefunden"
fi
echo ""

# game_editor Modul prüfen
echo "[4/4] Prüfe game_editor Modul..."
if ! $PYTHON_CMD -c "from game_editor import editor" 2>/dev/null; then
    echo "[FEHLER] game_editor Modul nicht gefunden!"
    echo "Bitte stellen Sie sicher, dass Sie im richtigen Verzeichnis sind."
    echo "Aktuelles Verzeichnis: $(pwd)"
    exit 1
fi
echo "[OK] game_editor Modul gefunden"
echo ""

# Alles OK - Editor starten
echo "========================================"
echo "Alle Requirements erfüllt!"
echo "Starte Editor..."
echo "========================================"
echo ""

$PYTHON_CMD -m game_editor.editor

if [ $? -ne 0 ]; then
    echo ""
    echo "[FEHLER] Editor konnte nicht gestartet werden!"
    exit 1
fi
