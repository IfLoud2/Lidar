@echo off
echo ===================================================
echo   Lancement du Visualiseur LiDAR (LD19) - HELHA
echo ===================================================
echo.

:: Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b
)

:: Installation automatique des dépendances si nécessaire (rapide si déjà fait)
echo Verification des modules Python...
pip install open3d pyserial numpy >nul 2>&1

:: Lancement du script
echo.
echo Demarrage de la visualisation...
echo Appuyez sur 'Q' dans la fenetre 3D pour quitter.
echo.

python python/lidar_viz.py

if %errorlevel% neq 0 (
    echo.
    echo Une erreur est survenue lors de l'execution.
    pause
)
