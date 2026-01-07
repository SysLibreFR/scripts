@echo off
REM Installation du workflow Assurance avec 5 taches planifiees distinctes
REM Alternative : 5 taches a 04h, 05h, 06h, 07h, 08h
REM Chaque tache verifie si le travail n'a pas deja ete fait

echo ============================================================
echo Installation Workflow Assurance - Methode Multi-Taches
echo ============================================================
echo.

REM Verifier les privileges administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR : Ce script doit etre execute en tant qu'administrateur
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
set WORKFLOW_SCRIPT=%SCRIPT_DIR%run_workflow.bat

echo Script : %WORKFLOW_SCRIPT%
echo.

REM Verifier Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERREUR : Python n'est pas installe
    pause
    exit /b 1
)

REM Supprimer les anciennes taches
echo Suppression des anciennes taches...
schtasks /delete /tn "Workflow Assurance 04h" /f >nul 2>&1
schtasks /delete /tn "Workflow Assurance 05h" /f >nul 2>&1
schtasks /delete /tn "Workflow Assurance 06h" /f >nul 2>&1
schtasks /delete /tn "Workflow Assurance 07h" /f >nul 2>&1
schtasks /delete /tn "Workflow Assurance 08h" /f >nul 2>&1

echo.
echo Creation de 5 taches planifiees...
echo.

REM Creer les 5 taches
schtasks /create /tn "Workflow Assurance 04h" /tr "\"%WORKFLOW_SCRIPT%\"" /sc daily /st 04:00 /f /rl highest
schtasks /create /tn "Workflow Assurance 05h" /tr "\"%WORKFLOW_SCRIPT%\"" /sc daily /st 05:00 /f /rl highest
schtasks /create /tn "Workflow Assurance 06h" /tr "\"%WORKFLOW_SCRIPT%\"" /sc daily /st 06:00 /f /rl highest
schtasks /create /tn "Workflow Assurance 07h" /tr "\"%WORKFLOW_SCRIPT%\"" /sc daily /st 07:00 /f /rl highest
schtasks /create /tn "Workflow Assurance 08h" /tr "\"%WORKFLOW_SCRIPT%\"" /sc daily /st 08:00 /f /rl highest

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo Installation terminee avec succes !
    echo ============================================================
    echo.
    echo 5 taches planifiees creees :
    echo   - Workflow Assurance 04h (04h00)
    echo   - Workflow Assurance 05h (05h00)
    echo   - Workflow Assurance 06h (06h00)
    echo   - Workflow Assurance 07h (07h00)
    echo   - Workflow Assurance 08h (08h00)
    echo.
    echo Si aucun fichier n'est trouve a 04h00, le script s'arrete.
    echo La tache de 05h00 relancera automatiquement le workflow.
    echo Et ainsi de suite jusqu'a 08h00.
    echo.
    echo Commandes utiles :
    echo   - Lister toutes les taches : schtasks /query /tn "Workflow Assurance*"
    echo   - Supprimer toutes les taches : 
    echo       schtasks /delete /tn "Workflow Assurance 04h" /f
    echo       schtasks /delete /tn "Workflow Assurance 05h" /f
    echo       (etc.)
    echo.
    echo Logs : E:\cegid\logs\workflow\workflow_YYYYMMDD.log
    echo.
) else (
    echo ERREUR : Impossible de creer les taches
    pause
    exit /b 1
)

pause