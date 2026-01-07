@echo off
REM Wrapper pour executer le workflow Assurance complet
REM Ce fichier trouve automatiquement Python et execute le script

REM Obtenir le repertoire du script
set SCRIPT_DIR=%~dp0

REM Definir le chemin du script Python
set PYTHON_SCRIPT=%SCRIPT_DIR%workflow_Assurance_complet.py

REM Verifier que le script existe
if not exist "%PYTHON_SCRIPT%" (
    echo ERREUR : Script Python introuvable : %PYTHON_SCRIPT%
    echo Veuillez verifier que le fichier existe.
    exit /b 1
)

REM Trouver Python dans le PATH
where python >nul 2>&1
if %errorLevel% equ 0 (
    python "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

REM Si Python n'est pas dans le PATH, essayer les emplacements courants
if exist "C:\Python312\python.exe" (
    "C:\Python312\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "C:\Python311\python.exe" (
    "C:\Python311\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "C:\Python310\python.exe" (
    "C:\Python310\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "C:\Python39\python.exe" (
    "C:\Python39\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" "%PYTHON_SCRIPT%"
    exit /b %errorLevel%
)

REM Si Python n'est toujours pas trouve
echo ERREUR : Python est introuvable
echo.
echo Veuillez installer Python depuis https://www.python.org/
echo OU ajouter Python au PATH systeme
echo.
echo Emplacements verifies :
echo   - PATH systeme
echo   - C:\Python3xx\
echo   - %LOCALAPPDATA%\Programs\Python\
echo.
exit /b 1