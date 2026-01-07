#!/usr/bin/env python3
"""
Script d'importation des données Assurance dans Cegid PMI - Version Multi-Sociétés
Traite automatiquement les CSV de plusieurs sociétés

Fonctionnalités :
- Support de plusieurs sociétés (100, 200, etc.)
- Parse et valide les données pour chaque société
- Génère et exécute les requêtes SQL UPDATE par société
- Archive les fichiers traités par société
- Logs séparés par société
"""

import csv
import re
import sys
import pyodbc
import shutil
import configparser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging

# Chemins
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config_multi_societes.ini"

# Configuration base de données (peut être dans le config.ini)
DB_SERVER = "med-srv-pmi-19"
DB_NAME = "PMI"
DB_USER = "sa"
DB_PASSWORD = "cegid.2016"  # À sécuriser en production

# Code client à exclure
EXCLUDED_CODE = "151500"


class AssuranceRecord:
    """Représente un enregistrement Assurance à importer."""
    
    def __init__(self, code: str, date_debut: str, date_fin: str, montant: str, societe: str):
        self.code_raw = code
        self.code = self._clean_code(code)
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.montant = montant
        self.societe = societe
        self.is_valid = False
        self.validation_errors = []
        
        self._validate()
    
    def _clean_code(self, code: str) -> str:
        """Nettoie le code client (supprime les zéros de début)."""
        return code.lstrip('0')
    
    def _validate(self):
        """Valide l'enregistrement selon les règles métier."""
        # Validation du code : doit être numérique et après nettoyage être 6 chiffres max
        if not self.code_raw.isdigit():
            self.validation_errors.append(f"Code invalide (non numérique) : {self.code_raw}")
            return
        
        # Vérifier que le code nettoyé n'est pas vide et fait max 6 chiffres
        if not self.code or len(self.code) > 6:
            self.validation_errors.append(f"Code invalide (longueur) : {self.code_raw}")
            return
        
        # Vérifier si le code est exclu
        if self.code == EXCLUDED_CODE:
            self.validation_errors.append(f"Code exclu : {self.code}")
            return
        
        self.is_valid = True
    
    def format_date(self, date_str: str) -> str:
        """Convertit une date du format DD/MM/YYYY vers YYYYMMDD."""
        if not date_str or date_str.strip() == '':
            return ''
        
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                jour, mois, annee = parts
                return f"{annee}{mois.zfill(2)}{jour.zfill(2)}"
        except Exception:
            pass
        
        return ''
    
    def get_dates_and_amount(self) -> Tuple[str, str, str]:
        """Calcule les dates et montant selon les règles métier."""
        date_debut_fmt = self.format_date(self.date_debut)
        date_fin_fmt = self.format_date(self.date_fin)
        montant_val = self.montant.strip()
        
        # Règle : Si montant est vide ou 0, mettre 1
        if not montant_val or montant_val == '0':
            montant_val = '1'
        
        # Règle : Si date_fin est vide, alors date_fin = 20991231 et montant = montant_val
        if not date_fin_fmt:
            return date_debut_fmt, '20991231', montant_val
        else:
            # Si date_fin n'est pas vide, alors date_debut = date_fin et montant = 1
            return date_fin_fmt, '20991231', '1'
    
    def generate_sql(self) -> str:
        """Génère la requête SQL UPDATE pour cet enregistrement."""
        date_d, date_f, montant = self.get_dates_and_amount()
        date_maj = datetime.now().strftime('%d/%m/%Y')  # Format DD/MM/YYYY
        
        sql = (
            f"UPDATE CLIENT SET "
            f"CLCJEBCOU1 = '{date_d}', "
            f"CLCJEBCOU2 = '{date_d}', "
            f"CLCJINCOU1 = '{date_f}', "
            f"CLCJINCOU2 = '{date_f}', "
            f"CLCNDECOU1 = {montant}, "
            f"CLCNDECOU2 = {montant}, "
            f"CLCTLIBRE4 = 'Mise à jour Assurance le {date_maj}' "
            f"WHERE CLKTSOC = '{self.societe}' AND CLKTCODE = '{self.code}'"
        )
        
        return sql


class CegidPMIImporter:
    """Classe pour gérer l'importation dans Cegid PMI pour une société."""
    
    def __init__(self, society_name: str, society_config: Dict[str, str]):
        self.society_name = society_name
        self.society_id = society_name.replace('SOCIETE_', '')
        
        # Configuration
        self.local_folder = Path(society_config['local_folder'])
        self.csv_folder = self.local_folder
        self.done_folder = self.local_folder / "done"
        self.sql_file = self.local_folder / "sql.txt"
        
        # Configuration du logging
        self.setup_logging()
    
    def setup_logging(self):
        """Configure le système de logging pour cette société."""
        log_folder = self.local_folder / "logs"
        log_folder.mkdir(parents=True, exist_ok=True)
        
        log_file = log_folder / f"import_pmi_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Créer un logger spécifique
        self.logger = logging.getLogger(f"{self.society_name}_PMI")
        self.logger.setLevel(logging.INFO)
        
        # Éviter les doublons
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            console_handler = logging.StreamHandler(sys.stdout)
            
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def parse_csv_file(self, filepath: Path) -> List[AssuranceRecord]:
        """Parse un fichier CSV et retourne les enregistrements."""
        records = []
        
        try:
            with open(filepath, 'r', encoding='iso-8859-1') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    # Remplacer les virgules par des espaces
                    line = line.replace(',', ' ')
                    
                    # Split par point-virgule
                    parts = line.split(';')
                    
                    if len(parts) < 4:
                        self.logger.warning(f"Ligne {line_num} ignorée (format invalide)")
                        continue
                    
                    code = parts[0].strip()
                    date_debut = parts[1].strip() if len(parts) > 1 else ''
                    date_fin = parts[2].strip() if len(parts) > 2 else ''
                    montant = parts[3].strip() if len(parts) > 3 else ''
                    
                    record = AssuranceRecord(code, date_debut, date_fin, montant, self.society_id)
                    records.append(record)
                    
                    if not record.is_valid:
                        self.logger.debug(f"Ligne {line_num} invalide : {', '.join(record.validation_errors)}")
            
        except Exception as e:
            self.logger.error(f"Erreur lecture fichier {filepath} : {e}")
        
        return records
    
    def generate_sql_file(self, records: List[AssuranceRecord]) -> int:
        """Génère le fichier SQL avec toutes les requêtes UPDATE."""
        valid_records = [r for r in records if r.is_valid]
        
        if not valid_records:
            return 0
        
        try:
            with open(self.sql_file, 'w', encoding='utf-8') as f:
                for record in valid_records:
                    sql = record.generate_sql()
                    f.write(sql + '\n')
            
            self.logger.info(f"{len(valid_records)} requête(s) SQL générée(s)")
            return len(valid_records)
            
        except Exception as e:
            self.logger.error(f"Erreur génération SQL : {e}")
            return 0
    
    def execute_sql_file(self) -> Tuple[int, int]:
        """Exécute toutes les requêtes SQL du fichier."""
        if not self.sql_file.exists():
            return 0, 0
        
        if self.sql_file.stat().st_size == 0:
            self.logger.info("Fichier SQL vide")
            self.sql_file.unlink()
            return 0, 0
        
        success_count = 0
        error_count = 0
        
        try:
            connection_string = (
                f"DRIVER={{SQL Server}};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_NAME};"
                f"UID={DB_USER};"
                f"PWD={DB_PASSWORD};"
            )
            
            self.logger.info(f"Connexion à la base {DB_NAME}...")
            conn = pyodbc.connect(connection_string, timeout=30)
            cursor = conn.cursor()
            
            with open(self.sql_file, 'r', encoding='utf-8') as f:
                for line_num, sql in enumerate(f, 1):
                    sql = sql.strip()
                    
                    if not sql:
                        continue
                    
                    try:
                        cursor.execute(sql)
                        conn.commit()
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        self.logger.error(f"Erreur requête {line_num} : {e}")
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"Exécution : {success_count} succès, {error_count} erreur(s)")
            
            # Archiver le fichier SQL
            self.archive_sql_file()
            
        except Exception as e:
            self.logger.error(f"Erreur connexion/exécution SQL : {e}")
            error_count += 1
        
        return success_count, error_count
    
    def archive_sql_file(self):
        """Archive le fichier SQL."""
        if not self.sql_file.exists():
            return
        
        try:
            self.done_folder.mkdir(parents=True, exist_ok=True)
            
            date_str = datetime.now().strftime('%Y%m%d')
            archived_name = f"sql MA {date_str}.txt"
            archived_path = self.done_folder / archived_name
            
            if archived_path.exists():
                timestamp = datetime.now().strftime('%H%M%S')
                archived_name = f"sql MA {date_str}_{timestamp}.txt"
                archived_path = self.done_folder / archived_name
            
            shutil.move(str(self.sql_file), str(archived_path))
            self.logger.info(f"SQL archivé : {archived_path.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur archivage SQL : {e}")
    
    def archive_csv_file(self, filepath: Path):
        """Archive un fichier CSV traité."""
        try:
            self.done_folder.mkdir(parents=True, exist_ok=True)
            
            archived_name = filepath.stem + filepath.suffix + '.bak'
            archived_path = self.done_folder / archived_name
            
            if archived_path.exists():
                archived_path.unlink()
            
            shutil.move(str(filepath), str(archived_path))
            self.logger.info(f"CSV archivé : {archived_path.name}")
            
        except Exception as e:
            self.logger.error(f"Erreur archivage CSV : {e}")
    
    def process_csv_file(self, filepath: Path) -> bool:
        """Traite un fichier CSV complet."""
        self.logger.info("=" * 70)
        self.logger.info(f"TRAITEMENT : {filepath.name}")
        self.logger.info("=" * 70)
        
        try:
            # Parser
            records = self.parse_csv_file(filepath)
            valid_count = sum(1 for r in records if r.is_valid)
            
            self.logger.info(f"Enregistrements : {len(records)} (valides : {valid_count})")
            
            if valid_count == 0:
                self.logger.warning("Aucun enregistrement valide")
                self.archive_csv_file(filepath)
                return False
            
            # Générer SQL
            sql_count = self.generate_sql_file(records)
            
            if sql_count == 0:
                self.logger.warning("Aucune requête SQL générée")
                self.archive_csv_file(filepath)
                return False
            
            # Exécuter SQL
            success_count, error_count = self.execute_sql_file()
            
            # Archiver CSV
            self.archive_csv_file(filepath)
            
            self.logger.info(f"RÉSUMÉ : {success_count} succès, {error_count} erreur(s)")
            self.logger.info("=" * 70)
            
            return error_count == 0
            
        except Exception as e:
            self.logger.error(f"Erreur traitement {filepath} : {e}")
            return False
    
    def process_all_csv_files(self) -> Tuple[int, int]:
        """Traite tous les fichiers CSV de cette société."""
        csv_files = list(self.csv_folder.glob('*.csv'))
        
        if not csv_files:
            self.logger.info("Aucun fichier CSV trouvé")
            return 0, 0
        
        self.logger.info(f"{len(csv_files)} fichier(s) CSV trouvé(s)")
        
        success = 0
        errors = 0
        
        for csv_file in csv_files:
            if self.process_csv_file(csv_file):
                success += 1
            else:
                errors += 1
        
        return success, errors


def load_config():
    """Charge la configuration."""
    if not CONFIG_FILE.exists():
        print(f"ERREUR : Fichier de configuration introuvable : {CONFIG_FILE}")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config


def main():
    """Point d'entrée principal."""
    print("\n" + "=" * 70)
    print("IMPORTATION CEGID PMI - MULTI-SOCIÉTÉS")
    print("=" * 70 + "\n")
    
    config = load_config()
    
    societies = [s for s in config.sections() if s.startswith('SOCIETE_')]
    
    if not societies:
        print("ERREUR : Aucune société configurée")
        sys.exit(1)
    
    print(f"Sociétés : {', '.join(societies)}\n")
    
    results = {}
    
    for society_name in sorted(societies):
        try:
            society_config = dict(config[society_name])
            
            importer = CegidPMIImporter(society_name, society_config)
            success, errors = importer.process_all_csv_files()
            
            results[society_name] = (success, errors)
            print()
            
        except Exception as e:
            print(f"ERREUR {society_name} : {e}\n")
            results[society_name] = (0, 1)
    
    # Résumé global
    print("=" * 70)
    print("RÉSUMÉ GLOBAL")
    print("=" * 70)
    
    total_success = sum(s for s, e in results.values())
    total_errors = sum(e for s, e in results.values())
    
    print(f"Total fichiers traités avec succès : {total_success}")
    print(f"Total fichiers en erreur : {total_errors}")
    print("=" * 70)
    
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()