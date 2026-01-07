# 🔄 Stratégies de Réessai - Workflow assurance

## 📋 Problème à résoudre

Les fichiers CSV ne sont pas toujours disponibles sur le serveur FTP à 04h00 précises. Il faut donc :

1. ✅ Réessayer plusieurs fois (04h, 05h, 06h, 07h, 08h)
2. ✅ S'arrêter dès qu'au moins un fichier a été traité
3. ✅ Ne pas retraiter les mêmes fichiers plusieurs fois

---

## 🎯 Solutions proposées

J'ai créé **2 solutions différentes** selon vos préférences :

### Solution 1 : Script intelligent avec réessais intégrés ⭐ (Recommandée)

**Fichiers :**
- `workflow_assurance_retry.py` - Script avec logique de réessai intégrée
- `install_workflow_retry.bat` - Installation (1 seule tâche Windows)

**Comment ça fonctionne :**
```
04h00 → Lance le script
   ↓
   Tentative 1 : Téléchargement FTP
   ├─ Fichiers trouvés ? → OUI → Import PMI → FIN ✓
   └─ Fichiers trouvés ? → NON → Attendre 1 heure
   ↓
05h00 (automatique)
   Tentative 2 : Téléchargement FTP
   ├─ Fichiers trouvés ? → OUI → Import PMI → FIN ✓
   └─ Fichiers trouvés ? → NON → Attendre 1 heure
   ↓
... (jusqu'à 08h00)
```

**Avantages :**
- ✅ Une seule tâche Windows à gérer
- ✅ Le script reste actif et réessaye automatiquement
- ✅ Logs centralisés dans un seul fichier
- ✅ Facile à suivre et déboguer

**Inconvénients :**
- ⚠️ Le processus Python reste actif pendant 5 heures max
- ⚠️ Si le processus plante, il ne réessaiera pas

### Solution 2 : Plusieurs tâches Windows planifiées

**Fichiers :**
- `workflow_assurance_complet.py` - Script standard (sans réessai)
- `install_workflow_multi_tasks.bat` - Installation (5 tâches Windows)

**Comment ça fonctionne :**
```
04h00 → Tâche 1 : Workflow complet
   ├─ Fichiers trouvés ? → OUI → Import PMI → FIN ✓
   └─ Fichiers trouvés ? → NON → Fin du script

05h00 → Tâche 2 : Workflow complet (nouveau processus)
   ├─ Fichiers trouvés ? → OUI → Import PMI → FIN ✓
   └─ Fichiers trouvés ? → NON → Fin du script

... (5 tâches indépendantes)
```

**Avantages :**
- ✅ Chaque tentative est indépendante
- ✅ Si un processus plante, les autres continuent
- ✅ Plus robuste en cas de problème système

**Inconvénients :**
- ⚠️ 5 tâches Windows à gérer
- ⚠️ 5 fichiers de logs différents
- ⚠️ Peut traiter le même fichier plusieurs fois si mal configuré

---

## 🚀 Installation

### Solution 1 (Recommandée) : Script avec réessais intégrés

1. **Installer la tâche planifiée :**
   ```cmd
   Clic droit sur install_workflow_retry.bat → Exécuter en tant qu'administrateur
   ```

2. **Tester manuellement :**
   ```cmd
   python workflow_assurance_retry.py
   ```

### Solution 2 : Plusieurs tâches Windows

1. **Installer les 5 tâches :**
   ```cmd
   Clic droit sur install_workflow_multi_tasks.bat → Exécuter en tant qu'administrateur
   ```

2. **Vérifier les tâches :**
   ```cmd
   schtasks /query /tn "Workflow assurance*"
   ```

---

## 📊 Comportement détaillé - Solution 1

### Scénario 1 : Fichiers disponibles à 04h00

```
04:00:00 - Tentative 1/5
04:00:05 - Connexion FTP...
04:00:10 - 3 fichiers trouvés et téléchargés ✓
04:00:15 - Import PMI...
04:00:30 - Import PMI terminé ✓
04:00:30 - WORKFLOW TERMINÉ AVEC SUCCÈS
         - Tentative réussie : 1/5
```

**Durée totale : 30 secondes**

### Scénario 2 : Fichiers disponibles à 06h00

```
04:00:00 - Tentative 1/5
04:00:05 - Aucun fichier trouvé sur le FTP
04:00:05 - Prochaine tentative dans 60 minutes (05:00)

05:00:05 - Tentative 2/5
05:00:10 - Aucun fichier trouvé sur le FTP
05:00:10 - Prochaine tentative dans 60 minutes (06:00)

06:00:10 - Tentative 3/5
06:00:15 - 3 fichiers trouvés et téléchargés ✓
06:00:20 - Import PMI...
06:00:35 - Import PMI terminé ✓
06:00:35 - WORKFLOW TERMINÉ AVEC SUCCÈS
         - Tentative réussie : 3/5
```

**Durée totale : 2 heures 35 secondes**

### Scénario 3 : Aucun fichier trouvé

```
04:00:00 - Tentative 1/5 - Aucun fichier
05:00:00 - Tentative 2/5 - Aucun fichier
06:00:00 - Tentative 3/5 - Aucun fichier
07:00:00 - Tentative 4/5 - Aucun fichier
08:00:00 - Tentative 5/5 - Aucun fichier
08:00:05 - WORKFLOW TERMINÉ - AUCUN FICHIER TROUVÉ
         - Tentatives effectuées : 5
```

**Durée totale : 4 heures**

---

## 🔧 Configuration

### Modifier le nombre de tentatives

Éditez `workflow_assurance_retry.py` :

```python
MAX_RETRIES = 5  # Nombre de tentatives (actuellement 5)
RETRY_INTERVAL = 3600  # Intervalle en secondes (3600 = 1 heure)
```

**Exemples :**

- **3 tentatives (04h, 05h, 06h)** :
  ```python
  MAX_RETRIES = 3
  ```

- **Tentatives toutes les 30 minutes** :
  ```python
  RETRY_INTERVAL = 1800  # 30 minutes
  ```

- **10 tentatives espacées de 15 minutes** :
  ```python
  MAX_RETRIES = 10
  RETRY_INTERVAL = 900  # 15 minutes
  ```

### Modifier les heures de démarrage

Pour démarrer à une autre heure (ex: 03h00 au lieu de 04h00) :

```cmd
schtasks /create /tn "Workflow assurance Tentative" /tr "python workflow_assurance_retry.py" /sc daily /st 03:00 /f /rl highest
```

---

## 📝 Logs et monitoring

### Fichiers de logs

**Solution 1 (Script avec réessais) :**
```
E:\cegid\logs\workflow\workflow_retry_20251222.log
```

Un seul fichier contenant toutes les tentatives.

**Solution 2 (Multi-tâches) :**
```
E:\cegid\logs\workflow\workflow_20251222.log
```

Un fichier par exécution (peut avoir plusieurs fichiers le même jour).

### Exemple de log - Solution 1

```
2025-12-22 04:00:00 - INFO - ======================================
2025-12-22 04:00:00 - INFO - TENTATIVE 1/5
2025-12-22 04:00:00 - INFO - ======================================
2025-12-22 04:00:01 - INFO - 📥 ÉTAPE 1 : Téléchargement FTP
2025-12-22 04:00:05 - WARNING - Aucun fichier trouvé sur le serveur FTP
2025-12-22 04:00:05 - INFO - 📅 Prochaine tentative dans 60 minutes (05:00)

2025-12-22 05:00:05 - INFO - ======================================
2025-12-22 05:00:05 - INFO - TENTATIVE 2/5
2025-12-22 05:00:05 - INFO - ======================================
2025-12-22 05:00:06 - INFO - 📥 ÉTAPE 1 : Téléchargement FTP
2025-12-22 05:00:10 - INFO - 3 fichier(s) CSV trouvé(s)
2025-12-22 05:00:15 - INFO - ✓ Fichiers trouvés et téléchargés à la tentative 2
2025-12-22 05:00:16 - INFO - 🔄 ÉTAPE 2 : Import Cegid PMI
2025-12-22 05:00:30 - INFO - ✓ Import terminé avec succès
2025-12-22 05:00:30 - INFO - 🎉 WORKFLOW TERMINÉ AVEC SUCCÈS
```

---

## 🔍 Dépannage

### Le script ne réessaye pas

**Problème :** Le script s'arrête après la première tentative même si aucun fichier n'est trouvé.

**Solution :** Vérifier les logs pour voir si une erreur a été levée. Le script ne réessaye que si :
- Aucune erreur fatale n'est survenue
- Aucun fichier n'a été trouvé (pas d'erreur de connexion)

### Le script traite les mêmes fichiers plusieurs fois

**Problème :** Les fichiers sont traités à 04h puis à nouveau à 05h.

**Cause :** Les fichiers ne sont pas supprimés du serveur FTP ou pas archivés localement.

**Solution :** Vérifier que :
1. Le script FTP supprime bien les fichiers du serveur après téléchargement
2. Le script PMI archive bien les fichiers dans le dossier `done/`

### Les tentatives sont trop rapides

**Problème :** Les tentatives se suivent toutes les 5 minutes au lieu d'1 heure.

**Solution :** Vérifier `RETRY_INTERVAL` dans `workflow_assurance_retry.py` :
```python
RETRY_INTERVAL = 3600  # Doit être 3600 (1 heure)
```

---

## 📊 Comparaison des solutions

| Critère | Solution 1 (Réessais intégrés) | Solution 2 (Multi-tâches) |
|---------|--------------------------------|---------------------------|
| **Tâches Windows** | 1 | 5 |
| **Fichiers de logs** | 1 par jour | 5 par jour |
| **Robustesse** | Moyenne (1 processus actif) | Haute (5 processus indépendants) |
| **Simplicité** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐⭐ Moyen |
| **Monitoring** | ⭐⭐⭐⭐⭐ Facile | ⭐⭐⭐ Plus complexe |
| **Maintenance** | ⭐⭐⭐⭐⭐ Facile | ⭐⭐⭐ Plus lourde |

---

## ✅ Recommandation

**Je recommande la Solution 1** (script avec réessais intégrés) pour :
- ✅ Simplicité de gestion
- ✅ Logs centralisés
- ✅ Facile à déboguer
- ✅ Une seule tâche Windows

**Utilisez la Solution 2** uniquement si :
- Vous avez des contraintes de sécurité (pas de processus longue durée)
- Vous voulez une redondance maximale
- Vous préférez les tâches Windows indépendantes

---

**Document créé le** : 23 décembre 2025  
**Version** : 1.0