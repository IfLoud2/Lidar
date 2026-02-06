@echo off
echo ===================================================
echo   Lancement du Visualiseur LiDAR (LD19) - HELHA
echo ===================================================
echo.

:: Vérification de Python 3.11 (Requis pour Open3D)
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python 3.11 n'est pas detecte.
    echo Veuillez l'installer ou verifier le lanceur 'py'.
    echo Actuellement detecte : 
    py --list
    pause
    exit /b
)

:: Installation automatique des dépendances sur Python 3.11
echo Verification des modules Python...
py -3.11 -m pip install open3d pyserial numpy >nul 2>&1

:: Lancement du script
echo.
echo Demarrage de la visualisation (Python 3.11)...
echo Appuyez sur 'Q' dans la fenetre 3D pour quitter.
echo.

py -3.11 python/lidar_viz.py

echo.
echo Application terminee.
pause
