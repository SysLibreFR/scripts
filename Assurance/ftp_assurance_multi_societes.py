#!/usr/bin/env python3
"""
Script de téléchargement automatique depuis FTP Assurance - Version Multi-Sociétés
Remplace le script RoboTask pour gérer plusieurs sociétés avec des identifiants différents

Fonctionnalités :
- Support de plusieurs sociétés (100, 200, etc.)
- Identifiants FTP différents par société
- Dossiers de destination différents par société
- Logs séparés par société
- Traitement séquentiel de toutes les sociétés configurées
"""

import ftplib
import os
import sys
import configparser
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Tuple

# Chemins
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config_multi_societes.ini"


class FTPImporter:
    """Classe pour gérer l'importation FTP pour une société."""
    
    def __init__(self, society_name: str, config: Dict[str, str]):
        """
        Initialise l'importateur FTP pour une société.
        
        Args:
            society_name: Nom de la société (ex: "SOCIETE_100")
            config: Configuration de la société
        """
        self.society_name = society_name
        self.config = config
        
        # Configuration FTP
        self.ftp_host = config['ftp_host']
        self.ftp_port = int(config['ftp_port'])
        self.ftp_user = config['username']
        self.ftp_password = config['password']
        self.ftp_passive = config['passive'].lower() == 'true'
        
        # Configuration locale
        self.local_folder = Path(config['local_folder'])
        self.remote_folder = config.get('remote_folder', '').strip()
        self.file_pattern = config['file_pattern']
        
        # Configuration du logging spécifique à cette société
        self.setup_logging()
    
    def setup_logging(self):
        """Configure le système de logging pour cette société."""
        log_folder = self.local_folder / "logs"
        log_folder.mkdir(parents=True, exist_ok=True)
        
        log_file = log_folder / f"ftp_import_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Créer un logger spécifique pour cette société
        self.logger = logging.getLogger(self.society_name)
        self.logger.setLevel(logging.INFO)
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            # Handler pour le fichier
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Handler pour la console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def download_and_delete_files(self) -> Tuple[int, List[str]]:
        """
        Télécharge tous les fichiers depuis le serveur FTP et les supprime après téléchargement.
        
        Returns:
            tuple: (nombre de fichiers téléchargés, liste des erreurs)
        """
        downloaded_files = []
        errors = []
        ftp = None
        
        try:
            # Vérifier que le mot de passe a été configuré
            if 'VOTRE_MOT_DE_PASSE' in self.ftp_password.upper():
                error_msg = f"Mot de passe FTP non configuré pour {self.society_name}"
                self.logger.error(error_msg)
                return 0, [error_msg]
            
            # Créer le dossier local s'il n'existe pas
            self.local_folder.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Dossier local : {self.local_folder}")
            
            # Connexion au serveur FTP
            self.logger.info(f"Connexion au serveur FTP : {self.ftp_host}:{self.ftp_port}")
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
            ftp.login(self.ftp_user, self.ftp_password)
            
            # Mode passif si nécessaire
            if self.ftp_passive:
                ftp.set_pasv(True)
                self.logger.info("Mode passif activé")
            
            self.logger.info(f"Connecté avec succès en tant que : {self.ftp_user}")
            
            # Se déplacer vers le dossier distant si spécifié
            if self.remote_folder:
                try:
                    ftp.cwd(self.remote_folder)
                    self.logger.info(f"Dossier distant : {self.remote_folder}")
                except Exception as e:
                    self.logger.warning(f"Impossible d'accéder au dossier distant '{self.remote_folder}' : {e}")
                    self.logger.info("Utilisation du dossier racine")
            
            # Lister les fichiers sur le serveur
            self.logger.info(f"Recherche des fichiers {self.file_pattern} sur le serveur...")
            all_files = ftp.nlst()
            
            # Filtrer selon le pattern
            if self.file_pattern == "*":
                filtered_files = all_files
            else:
                extension = self.file_pattern.replace('*', '').lower()
                filtered_files = [f for f in all_files if f.lower().endswith(extension)]
            
            if not filtered_files:
                self.logger.info(f"Aucun fichier {self.file_pattern} trouvé sur le serveur")
                return 0, []
            
            self.logger.info(f"{len(filtered_files)} fichier(s) trouvé(s) : {', '.join(filtered_files)}")
            
            # Télécharger et supprimer chaque fichier
            for filename in filtered_files:
                local_filepath = self.local_folder / filename
                
                try:
                    self.logger.info(f"Téléchargement de '{filename}'...")
                    
                    # Télécharger le fichier
                    with open(local_filepath, 'wb') as local_file:
                        ftp.retrbinary(f'RETR {filename}', local_file.write)
                    
                    file_size = local_filepath.stat().st_size
                    self.logger.info(f"✓ Téléchargé : {filename} ({file_size:,} octets)")
                    
                    # Supprimer le fichier du serveur FTP
                    try:
                        ftp.delete(filename)
                        self.logger.info(f"✓ Supprimé du serveur : {filename}")
                        downloaded_files.append(filename)
                        
                    except Exception as e:
                        error_msg = f"Erreur lors de la suppression de '{filename}' : {e}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        
                except Exception as e:
                    error_msg = f"Erreur lors du téléchargement de '{filename}' : {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
            
            return len(downloaded_files), errors
            
        except ftplib.error_perm as e:
            error_msg = f"Erreur d'authentification FTP : {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            return 0, errors
            
        except Exception as e:
            error_msg = f"Erreur inattendue : {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            return 0, errors
            
        finally:
            # Déconnexion
            if ftp:
                try:
                    ftp.quit()
                    self.logger.info("Déconnecté du serveur FTP")
                except:
                    try:
                        ftp.close()
                    except:
                        pass
    
    def run(self) -> bool:
        """
        Lance l'importation pour cette société.
        
        Returns:
            bool: True si succès, False si erreur
        """
        self.logger.info("=" * 70)
        self.logger.info(f"DÉBUT IMPORTATION - {self.society_name}")
        self.logger.info("=" * 70)
        
        start_time = datetime.now()
        
        downloaded_count, errors = self.download_and_delete_files()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info("=" * 70)
        self.logger.info(f"FIN IMPORTATION - {self.society_name}")
        self.logger.info(f"Durée : {duration:.2f} secondes")
        self.logger.info(f"Fichiers téléchargés : {downloaded_count}")
        
        if errors:
            self.logger.warning(f"Erreurs rencontrées : {len(errors)}")
            for error in errors:
                self.logger.warning(f"  - {error}")
            return False
        else:
            self.logger.info("✓ Aucune erreur")
            return True


def load_config() -> configparser.ConfigParser:
    """
    Charge la configuration depuis le fichier config_multi_societes.ini
    
    Returns:
        configparser.ConfigParser: Configuration chargée
    """
    if not CONFIG_FILE.exists():
        print(f"ERREUR : Fichier de configuration introuvable : {CONFIG_FILE}")
        print("Veuillez créer le fichier config_multi_societes.ini")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
        print(f"Configuration chargée depuis : {CONFIG_FILE}")
        return config
    except Exception as e:
        print(f"ERREUR : Impossible de lire {CONFIG_FILE} : {e}")
        sys.exit(1)


def get_societies(config: configparser.ConfigParser) -> List[str]:
    """
    Récupère la liste des sociétés configurées.
    
    Args:
        config: Configuration chargée
        
    Returns:
        List[str]: Liste des noms de sociétés (sections commençant par SOCIETE_)
    """
    societies = [section for section in config.sections() 
                 if section.startswith('SOCIETE_')]
    
    if not societies:
        print("ERREUR : Aucune société configurée dans le fichier de configuration")
        print("Les sections doivent commencer par 'SOCIETE_' (ex: SOCIETE_100)")
        sys.exit(1)
    
    return sorted(societies)


def main():
    """Point d'entrée principal du script."""
    print("\n" + "=" * 70)
    print("SCRIPT D'IMPORTATION FTP Assurance - MULTI-SOCIÉTÉS")
    print("=" * 70 + "\n")
    
    # Charger la configuration
    config = load_config()
    
    # Récupérer les sociétés configurées
    societies = get_societies(config)
    print(f"Sociétés configurées : {', '.join(societies)}\n")
    
    # Traiter chaque société
    results = {}
    start_time = datetime.now()
    
    for society_name in societies:
        try:
            society_config = dict(config[society_name])
            
            # Ajouter les valeurs par défaut si nécessaire
            if 'ftp_host' not in society_config:
                society_config['ftp_host'] = config['DEFAULT']['ftp_host']
            if 'ftp_port' not in society_config:
                society_config['ftp_port'] = config['DEFAULT']['ftp_port']
            if 'passive' not in society_config:
                society_config['passive'] = config['DEFAULT']['passive']
            if 'file_pattern' not in society_config:
                society_config['file_pattern'] = config['DEFAULT']['file_pattern']
            
            # Créer l'importateur et lancer le traitement
            importer = FTPImporter(society_name, society_config)
            success = importer.run()
            results[society_name] = success
            
            print()  # Ligne vide entre les sociétés
            
        except Exception as e:
            print(f"ERREUR lors du traitement de {society_name} : {e}\n")
            results[society_name] = False
    
    # Résumé global
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    
    print("=" * 70)
    print("RÉSUMÉ GLOBAL")
    print("=" * 70)
    print(f"Durée totale : {total_duration:.2f} secondes")
    print(f"Sociétés traitées : {len(results)}")
    
    success_count = sum(1 for success in results.values() if success)
    print(f"Succès : {success_count}")
    print(f"Échecs : {len(results) - success_count}")
    
    if success_count < len(results):
        print("\nDétails des échecs :")
        for society, success in results.items():
            if not success:
                print(f"  ✗ {society}")
    
    print("=" * 70)
    
    # Code de sortie
    if success_count == len(results):
        sys.exit(0)  # Tout s'est bien passé
    else:
        sys.exit(1)  # Au moins une erreur


if __name__ == "__main__":
    main()
