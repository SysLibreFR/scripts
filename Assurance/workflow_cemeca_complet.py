#!/usr/bin/env python3
"""
Workflow complet Assurance : FTP Download + Import Cegid PMI
Ce script orchestre les deux etapes :
1. Telechargement des CSV depuis le FTP
2. Importation des donnees dans Cegid PMI

A planifier tous les jours a 04h00
"""

import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Chemins des scripts
SCRIPT_DIR = Path(__file__).parent
FTP_SCRIPT = SCRIPT_DIR / "ftp_Assurance_multi_societes.py"
PMI_SCRIPT = SCRIPT_DIR / "import_cegid_pmi_multi.py"

# Configuration du logging
LOG_FOLDER = Path("E:/cegid/logs/workflow")
LOG_FOLDER.mkdir(parents=True, exist_ok=True)
log_file = LOG_FOLDER / f"workflow_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)


def run_script(script_path: Path, script_name: str) -> bool:
    """
    Execute un script Python et retourne le resultat.
    
    Args:
        script_path: Chemin du script a executer
        script_name: Nom du script (pour les logs)
        
    Returns:
        True si succes, False si erreur
    """
    if not script_path.exists():
        logging.error(f"Script introuvable : {script_path}")
        return False
    
    logging.info("=" * 70)
    logging.info(f"EXECUTION : {script_name}")
    logging.info("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='cp1252',  # Encodage Windows Latin-1
            errors='replace',
            timeout=3600  # Timeout de 1 heure
        )
        
        # Afficher la sortie
        if result.stdout:
            for line in result.stdout.splitlines():
                logging.info(f"  {line}")
        
        if result.stderr:
            for line in result.stderr.splitlines():
                logging.warning(f"  STDERR: {line}")
        
        if result.returncode == 0:
            logging.info(f"OK - {script_name} termine avec succes")
            return True
        else:
            logging.error(f"ERREUR - {script_name} a echoue (code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error(f"ERREUR - {script_name} a depasse le timeout")
        return False
    except Exception as e:
        logging.error(f"ERREUR - Lors de l'execution de {script_name} : {e}")
        return False


def main():
    """Point d'entree principal du workflow."""
    logging.info("\n" + "=" * 70)
    logging.info("WORKFLOW COMPLET Assurance")
    logging.info(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 70 + "\n")
    
    start_time = datetime.now()
    
    # Etape 1 : Telechargement FTP
    logging.info("ETAPE 1 : TELECHARGEMENT FTP")
    ftp_success = run_script(FTP_SCRIPT, "Telechargement FTP")
    
    if not ftp_success:
        logging.error("Le telechargement FTP a echoue, arret du workflow")
        sys.exit(1)
    
    print()
    
    # Etape 2 : Import dans Cegid PMI
    logging.info("ETAPE 2 : IMPORTATION CEGID PMI")
    pmi_success = run_script(PMI_SCRIPT, "Import Cegid PMI")
    
    if not pmi_success:
        logging.warning("L'import Cegid PMI a rencontre des erreurs")
    
    # Resume final
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print()
    logging.info("=" * 70)
    logging.info("RESUME DU WORKFLOW")
    logging.info("=" * 70)
    logging.info(f"Duree totale : {duration:.2f} secondes")
    logging.info(f"Etape 1 (FTP) : {'OK SUCCES' if ftp_success else 'ERREUR ECHEC'}")
    logging.info(f"Etape 2 (PMI) : {'OK SUCCES' if pmi_success else 'ERREUR ECHEC'}")
    
    if ftp_success and pmi_success:
        logging.info("WORKFLOW TERMINE AVEC SUCCES")
        logging.info("=" * 70)
        sys.exit(0)
    else:
        logging.error("WORKFLOW TERMINE AVEC DES ERREURS")
        logging.info("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
