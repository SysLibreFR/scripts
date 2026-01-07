# 🔧 Résolution de l'erreur du Planificateur de tâches

## ❌ Erreur rencontrée

```
Le Planificateur de tâches n'a pas pu lancer l'action « python » 
dans l'instance « {eaf77cfa-db37-4b6d-bcd5-6dead3708f86} » 
de la tâche « \FTP Assurance Import Multi-Societes ». 
Données supplémentaires : Valeur de l'erreur : 2147942402.
```

**Code d'erreur :** `2147942402` (0x80070002)  
**Signification :** "Le fichier spécifié est introuvable"

---

## 🎯 Cause du problème

Le Planificateur de tâches Windows ne trouve pas la commande `python` car :

1. **Python n'est pas dans le PATH système** (le PATH utilisateur ne suffit pas)
2. **La commande `python` n'est pas reconnue** en tant que programme

---

## ✅ Solutions (par ordre de préférence)

### Solution 1 : Utiliser les fichiers batch wrapper ⭐ (Recommandée)

J'ai créé des fichiers `.bat` qui trouvent automatiquement Python et lancent les scripts.

**Fichiers fournis :**
- `run_workflow.bat` - Pour le workflow complet
- `run_workflow_retry.bat` - Pour le workflow avec réessais
- `run_ftp.bat` - Pour le FTP uniquement

**Installation :**

1. **Supprimez l'ancienne tâche :**
   ```cmd
   schtasks /delete /tn "FTP Assurance Import Multi-Societes" /f
   ```

2. **Réinstallez avec le fichier batch d'installation :**
   ```cmd
   Clic droit sur install_workflow_complet.bat → Exécuter en tant qu'administrateur
   ```
   
   OU pour la version avec réessais :
   ```cmd
   Clic droit sur install_workflow_retry.bat → Exécuter en tant qu'administrateur
   ```

Les nouveaux scripts d'installation ont été mis à jour pour utiliser les wrappers `.bat` au lieu d'appeler `python` directement.

---

### Solution 2 : Ajouter Python au PATH système

Si vous préférez utiliser directement les scripts Python :

1. **Trouver le chemin de Python :**
   ```cmd
   where python
   ```
   
   Exemple de résultat : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python312\python.exe`

2. **Ajouter au PATH système :**
   - Appuyez sur `Win + Pause` (ou cherchez "Variables d'environnement")
   - Cliquez sur "Variables d'environnement"
   - Dans "Variables système" (pas "Variables utilisateur"), sélectionnez `Path`
   - Cliquez sur "Modifier"
   - Cliquez sur "Nouveau"
   - Ajoutez le chemin Python (ex: `C:\Users\VotreNom\AppData\Local\Programs\Python\Python312`)
   - Cliquez OK sur toutes les fenêtres
   - **Redémarrez l'ordinateur**

3. **Recréer la tâche planifiée**

---

### Solution 3 : Utiliser le chemin complet de Python

Si vous ne pouvez pas modifier le PATH système :

1. **Trouver le chemin de Python :**
   ```cmd
   where python
   ```

2. **Modifier manuellement la tâche planifiée :**
   - Ouvrir le Planificateur de tâches (`Win + R` → `taskschd.msc`)
   - Trouver votre tâche
   - Clic droit → Propriétés
   - Onglet "Actions"
   - Modifier l'action existante
   - Dans "Programme/script", remplacer `python` par le chemin complet
   - Exemple : `C:\Users\VotreNom\AppData\Local\Programs\Python\Python312\python.exe`
   - Dans "Ajouter des arguments", mettre le chemin complet du script Python
   - Exemple : `"C:\Scripts\workflow_Assurance_complet.py"`

---

## 🧪 Test de la solution

### Tester le wrapper batch manuellement

1. **Ouvrir une invite de commande**

2. **Naviguer vers le dossier des scripts :**
   ```cmd
   cd C:\chemin\vers\vos\scripts
   ```

3. **Exécuter le wrapper :**
   ```cmd
   run_workflow.bat
   ```

Si ça fonctionne, le wrapper trouvera Python et lancera le script.

### Tester la tâche planifiée

1. **Ouvrir le Planificateur de tâches :**
   ```cmd
   taskschd.msc
   ```

2. **Trouver votre tâche** dans la liste

3. **Clic droit → Exécuter**

4. **Vérifier les résultats :**
   - Onglet "Historique" de la tâche
   - Ou consulter les logs : `E:\cegid\logs\workflow\`

---

## 📊 Comment savoir si ça fonctionne ?

### ✅ Signes de succès

Dans le Planificateur de tâches, onglet "Historique" :
- **Code de sortie : 0x0** (succès)
- Aucune erreur dans les événements

Dans les logs (`E:\cegid\logs\workflow\`) :
- Fichiers de log créés avec la date du jour
- Messages de succès dans les logs

### ❌ Signes d'échec

Dans le Planificateur de tâches :
- **Code de sortie : 0x1** ou autre (échec)
- Erreur 2147942402 toujours présente

Dans les logs :
- Aucun fichier de log créé
- Ou logs montrant des erreurs

---

## 🔍 Dépannage avancé

### Vérifier que Python fonctionne

```cmd
python --version
```

Si cette commande fonctionne en ligne de commande mais pas dans le Planificateur de tâches, c'est que Python n'est pas dans le PATH **système**.

### Vérifier les emplacements de Python

Les wrappers batch cherchent Python dans ces emplacements :

```
1. PATH système (where python)
2. C:\Python312\python.exe
3. C:\Python311\python.exe
4. C:\Python310\python.exe
5. C:\Python39\python.exe
6. %LOCALAPPDATA%\Programs\Python\Python312\python.exe
7. %LOCALAPPDATA%\Programs\Python\Python311\python.exe
8. %LOCALAPPDATA%\Programs\Python\Python310\python.exe
```

Si votre Python est installé ailleurs, modifiez `run_workflow.bat` pour ajouter votre chemin.

### Tester avec le chemin complet

Créer une tâche de test avec le chemin complet :

```cmd
schtasks /create /tn "Test Python" /tr "C:\Python312\python.exe C:\Scripts\workflow_Assurance_complet.py" /sc once /st 15:00 /f
```

(Remplacez les chemins par les vôtres)

---

## 📝 Checklist de résolution

- [ ] Supprimer l'ancienne tâche planifiée
- [ ] Vérifier que les fichiers `.bat` sont présents
- [ ] Exécuter manuellement `run_workflow.bat` pour tester
- [ ] Réinstaller avec `install_workflow_complet.bat` (en admin)
- [ ] Vérifier que la nouvelle tâche utilise le `.bat` et non `python`
- [ ] Tester manuellement la tâche dans le Planificateur
- [ ] Vérifier les logs après exécution

---

## 💡 Pourquoi les wrappers batch ?

Les fichiers `.bat` résolvent le problème car :

1. ✅ Windows trouve toujours les fichiers `.bat` (pas besoin de PATH)
2. ✅ Le wrapper cherche Python à plusieurs endroits automatiquement
3. ✅ Fonctionne même si Python n'est pas dans le PATH système
4. ✅ Plus robuste et portable

---

## 🎓 Explication technique de l'erreur

**Code erreur 2147942402 = 0x80070002 = ERROR_FILE_NOT_FOUND**

Le Planificateur de tâches Windows utilise le **PATH système** (pas le PATH utilisateur).

Quand vous lancez une commande manuellement dans cmd.exe, Windows utilise :
- PATH système
- **+ PATH utilisateur** (celui de votre compte)

Quand le Planificateur lance une tâche, il utilise :
- PATH système uniquement (pas de PATH utilisateur)
- Compte SYSTEM ou votre compte sans session interactive

Si Python est installé "pour l'utilisateur actuel uniquement", il n'est que dans le PATH utilisateur, donc le Planificateur ne le trouve pas.

**Solution :** Utiliser un wrapper `.bat` qui trouve Python explicitement, ou ajouter Python au PATH système.

---

**Document créé le** : 23 décembre 2025  
**Dernière mise à jour** : 23 décembre 2025