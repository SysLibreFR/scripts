# Migration RoboTask vers Python - FTP assurance Import Multi-Sociétés

## 📋 Description

Cette version avancée permet de gérer **plusieurs sociétés** avec des identifiants FTP différents et des dossiers de destination distincts.

**Fonctionnalités :**
- ✅ Support de plusieurs sociétés (100, 200, 300, etc.)
- ✅ Identifiants FTP différents par société
- ✅ Dossiers de destination différents (*/100/*, */200/*, etc.)
- ✅ Connexion au serveur FTP ftp.assurance.pro
- ✅ Téléchargement de tous les fichiers .csv
- ✅ Suppression des fichiers CSV du serveur après téléchargement
- ✅ Logs séparés par société
- ✅ Traitement séquentiel de toutes les sociétés
- ✅ Planification quotidienne à 04h00

---

## 📁 Fichiers fournis

### Version Multi-Sociétés (recommandée pour votre cas)
1. **`ftp_assurance_multi_societes.py`** - Script principal multi-sociétés
2. **`config_multi_societes.ini`** - Configuration des sociétés
3. **`ftp_assurance_scheduler_multi.py`** - Planificateur
4. **`install_service_multi.bat`** - Installation automatique
5. **`README_MULTI_SOCIETES.md`** - Ce fichier

### Version Simple (une seule société)
- `ftp_assurance_import.py` - Script simple
- `ftp_assurance_import_v2.py` - Script simple avec config
- `ftp_assurance_scheduler.py` - Planificateur simple
- `install_service.bat` - Installation simple

---

## 🔧 Prérequis

### 1. Python 3.7 ou supérieur

```cmd
python --version
```

Si Python n'est pas installé : https://www.python.org/downloads/

### 2. Installer les dépendances

```cmd
pip install schedule
```

---

## 🚀 Installation et Configuration

### Étape 1 : Configurer les sociétés

Éditez le fichier **`config_multi_societes.ini`** :

```ini
# Configuration globale
[DEFAULT]
ftp_host = ftp.assurance.pro
ftp_port = 21
passive = True
file_pattern = *.csv
base_folder = E:\cegid

# Société 100
[SOCIETE_100]
username = assurance-MED
password = MOT_DE_PASSE_SOCIETE_100
local_folder = %(base_folder)s\100\assurance
remote_folder = 

# Société 200
[SOCIETE_200]
username = assurance-SOC200
password = MOT_DE_PASSE_SOCIETE_200
local_folder = %(base_folder)s\200\assurance
remote_folder = 
```

**Points importants :**
- Chaque section `[SOCIETE_XXX]` représente une société
- `username` et `password` : identifiants FTP spécifiques à chaque société
- `local_folder` : dossier de destination local (utilise `%(base_folder)s` pour le chemin de base)
- `remote_folder` : dossier distant sur le FTP (laisser vide pour la racine)
- Vous pouvez ajouter autant de sociétés que nécessaire

### Étape 2 : Récupérer les mots de passe FTP

Pour chaque société, récupérez le mot de passe depuis RoboTask :

1. Ouvrez RoboTask
2. Ouvrez la tâche correspondante à la société
3. Double-cliquez sur l'action "FTP Log On"
4. Notez le mot de passe
5. Mettez-le dans le fichier `config_multi_societes.ini`

### Étape 3 : Tester le script

Testez le script manuellement avant de planifier l'exécution automatique :

```cmd
cd C:\chemin\vers\vos\scripts
python ftp_assurance_multi_societes.py
```

**Ce que vous devriez voir :**
```
======================================================================
SCRIPT D'IMPORTATION FTP assurance - MULTI-SOCIÉTÉS
======================================================================

Sociétés configurées : SOCIETE_100, SOCIETE_200

======================================================================
DÉBUT IMPORTATION - SOCIETE_100
======================================================================
Connexion au serveur FTP : ftp.assurance.pro:21
Connecté avec succès en tant que : assurance-MED
Recherche des fichiers *.csv sur le serveur...
3 fichier(s) trouvé(s) : file1.csv, file2.csv, file3.csv
Téléchargement de 'file1.csv'...
✓ Téléchargé : file1.csv (1,234 octets)
✓ Supprimé du serveur : file1.csv
...
======================================================================
FIN IMPORTATION - SOCIETE_100
Durée : 5.23 secondes
Fichiers téléchargés : 3
✓ Aucune erreur

======================================================================
DÉBUT IMPORTATION - SOCIETE_200
======================================================================
...
```

### Étape 4 : Installer la planification automatique

**Option A : Planificateur Windows (Recommandé)**

1. Faites un clic droit sur **`install_service_multi.bat`**
2. Choisissez **"Exécuter en tant qu'administrateur"**
3. La tâche sera créée pour s'exécuter à 04h00

**Option B : Service Python continu**

```cmd
python ftp_assurance_scheduler_multi.py
```

---

## 📊 Structure des dossiers et logs

```
E:\cegid\
├── 100\
│   └── assurance\
│       ├── logs\
│       │   └── ftp_import_20251209.log
│       ├── file1.csv
│       ├── file2.csv
│       └── file3.csv
├── 200\
│   └── assurance\
│       ├── logs\
│       │   └── ftp_import_20251209.log
│       ├── file1.csv
│       └── file2.csv
└── logs\
    └── scheduler\
        └── scheduler_multi_societes.log
```

**Logs par société :**
- `E:\cegid\100\assurance\logs\ftp_import_YYYYMMDD.log` - Logs société 100
- `E:\cegid\200\assurance\logs\ftp_import_YYYYMMDD.log` - Logs société 200

**Log du planificateur :**
- `E:\cegid\logs\scheduler\scheduler_multi_societes.log`

---

## 🔍 Vérification et gestion

### Vérifier la tâche planifiée

```cmd
schtasks /query /tn "FTP assurance Import Multi-Societes" /v
```

### Exécuter manuellement

```cmd
schtasks /run /tn "FTP assurance Import Multi-Societes"
```

### Désactiver / Réactiver

```cmd
schtasks /change /tn "FTP assurance Import Multi-Societes" /disable
schtasks /change /tn "FTP assurance Import Multi-Societes" /enable
```

### Supprimer

```cmd
schtasks /delete /tn "FTP assurance Import Multi-Societes" /f
```

---

## 🛠️ Personnalisation

### Ajouter une nouvelle société

Éditez `config_multi_societes.ini` et ajoutez :

```ini
[SOCIETE_300]
username = assurance-SOC300
password = MOT_DE_PASSE_SOCIETE_300
local_folder = %(base_folder)s\300\assurance
remote_folder = 
```

Le script détectera automatiquement la nouvelle société !

### Changer l'heure d'exécution

Dans `ftp_assurance_scheduler_multi.py`, ligne 56 :
```python
schedule.every().day.at("04:00").do(run_ftp_import)
```

### Télécharger d'autres types de fichiers

Dans `config_multi_societes.ini`, section `[DEFAULT]` :
```ini
file_pattern = *.xlsx
```

### Utiliser des dossiers distants différents

Si vos sociétés ont des dossiers différents sur le serveur FTP :

```ini
[SOCIETE_100]
username = assurance-MED
password = xxxxxxxx
local_folder = E:\cegid\100\assurance
remote_folder = /societe100/data

[SOCIETE_200]
username = assurance-SOC200
password = yyyyyyyy
local_folder = E:\cegid\200\assurance
remote_folder = /societe200/data
```

### Ne pas supprimer les fichiers du serveur

Éditez `ftp_assurance_multi_societes.py` et commentez les lignes 149-157 :

```python
# Supprimer le fichier du serveur FTP
# try:
#     ftp.delete(filename)
#     self.logger.info(f"✓ Supprimé du serveur : {filename}")
#     downloaded_files.append(filename)
# except Exception as e:
#     ...
```

---

## 🔧 Dépannage

### Erreur : "Aucune société configurée"

Vérifiez que vos sections commencent bien par `SOCIETE_` :
- ✅ Correct : `[SOCIETE_100]`
- ❌ Incorrect : `[Societe100]` ou `[SOC_100]`

### Une société échoue mais pas les autres

Le script continue le traitement des autres sociétés même si une échoue. Consultez les logs de la société en erreur :

```
E:\cegid\XXX\assurance\logs\ftp_import_YYYYMMDD.log
```

### Erreur de connexion FTP pour une société

Vérifiez :
- Le nom d'utilisateur est correct
- Le mot de passe est correct
- Le compte a bien accès au serveur FTP

### Les fichiers ne vont pas dans le bon dossier

Vérifiez le paramètre `local_folder` dans `config_multi_societes.ini` :
```ini
local_folder = E:\cegid\100\assurance  # Attention au numéro !
```

---

## 📋 Exemple de résumé d'exécution

```
======================================================================
RÉSUMÉ GLOBAL
======================================================================
Durée totale : 12.45 secondes
Sociétés traitées : 2
Succès : 2
Échecs : 0
======================================================================
```

Si une société échoue :
```
======================================================================
RÉSUMÉ GLOBAL
======================================================================
Durée totale : 15.23 secondes
Sociétés traitées : 2
Succès : 1
Échecs : 1

Détails des échecs :
  ✗ SOCIETE_200
======================================================================
```

---

## 🔄 Migration depuis RoboTask

### Si vous avez deux tâches RoboTask séparées

Vous pouvez :
1. **Option A** : Utiliser le script multi-sociétés (recommandé)
   - Plus facile à maintenir
   - Un seul point de configuration
   - Logs centralisés

2. **Option B** : Créer deux scripts simples séparés
   - Plus simple si les configurations sont très différentes
   - Deux tâches planifiées Windows distinctes

### Désactiver les anciennes tâches RoboTask

Une fois que vous avez validé que le script Python fonctionne :
1. Ouvrez RoboTask
2. Désactivez ou supprimez les anciennes tâches
3. Gardez RoboTask installé pendant quelques semaines "au cas où"

---

## ✅ Checklist de migration multi-sociétés

- [ ] Python 3.7+ installé
- [ ] Dépendance `schedule` installée
- [ ] Fichier `config_multi_societes.ini` créé
- [ ] Mots de passe FTP configurés pour toutes les sociétés
- [ ] Chemins `local_folder` vérifiés pour chaque société
- [ ] Test manuel réussi pour toutes les sociétés
- [ ] Logs vérifiés pour chaque société
- [ ] Tâche planifiée créée
- [ ] Premier run automatique vérifié
- [ ] RoboTask désactivé (après validation)

---

## 🎯 Avantages de la version multi-sociétés

| Fonctionnalité | Avant (RoboTask) | Maintenant (Python) |
|----------------|------------------|---------------------|
| Nombre de scripts | 2 (un par société) | 1 (toutes les sociétés) |
| Configuration | 2 fichiers .tsk | 1 fichier .ini |
| Maintenance | Modifier 2 scripts | Modifier 1 fichier |
| Ajout d'une société | Créer un nouveau script | Ajouter 4 lignes dans le .ini |
| Logs | Séparés et basiques | Séparés et détaillés |
| Résumé global | Non disponible | Oui (succès/échecs) |
| Coût | Licence RoboTask | Gratuit |

---

**Dernière mise à jour :** Décembre 2025
**Version :** 2.0 Multi-Sociétés