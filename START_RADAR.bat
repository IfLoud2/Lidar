@echo off
echo ===================================================
echo   Lancement du RADAR (LD19) - SONAR VIEW
echo ===================================================
echo.

:: Vérification de Python 3.11
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python 3.11 requis.
    pause
    exit /b
)

:: Installation dépendances (pygame)
py -3.11 -m pip install pygame pyserial numpy >nul 2>&1

:: Lancement
echo Radar active...
echo [Cerceaux verts : 5cm, 10cm, 15cm]
echo.

py -3.11 python/radar_viz.py

echo.
echo Radar termine.
pause
