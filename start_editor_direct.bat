@echo off
REM GameDev-Edu Editor Starter (Direkt, ohne Dialog)
echo Starte Editor...
python -m game_editor.editor
if errorlevel 1 (
    echo.
    echo [FEHLER] Editor konnte nicht gestartet werden!
    pause
)
