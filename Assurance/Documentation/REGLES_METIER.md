# Règles Métier - Traitement des données assurance

## 📋 Format du fichier CSV

```
CODE;DATE_DEBUT;DATE_FIN;MONTANT
123456;01/01/2025;;100
234567;15/03/2025;31/12/2025;
345678;01/06/2025;;50
```

**Format :**
- **Séparateur** : `;` (point-virgule)
- **CODE** : 6 chiffres (ex: `123456`)
- **DATE_DEBUT** : Format `DD/MM/YYYY` (ex: `01/01/2025`)
- **DATE_FIN** : Format `DD/MM/YYYY` ou vide (ex: `31/12/2025` ou vide)
- **MONTANT** : Nombre entier ou vide (ex: `100` ou vide)

---

## ✅ Règles de validation

### 1. Validation du code client

- ✅ **Le code doit contenir exactement 6 chiffres**
  - Exemple valide : `123456`, `000001`, `999999`
  - Exemple invalide : `12345` (5 chiffres), `1234567` (7 chiffres), `12A456` (contient une lettre)

- ✅ **Le code `151500` est exclu**
  - Si un enregistrement a le code `151500`, il est ignoré
  - Les zéros de début sont supprimés pour la comparaison (ex: `000151500` → `151500`)

### 2. Nettoyage du code

- Les **zéros de début sont supprimés** pour la base de données
  - Exemple : `000123` → `123`
  - Exemple : `012345` → `12345`
  - Exemple : `123456` → `123456` (inchangé)

---

## 🔄 Règles de transformation

### Règle 1 : Traitement du montant

```
SI montant est vide OU montant = 0
  ALORS montant = 1
SINON
  ALORS montant = valeur du CSV
```

**Exemples :**
- CSV : `123456;01/01/2025;;` (montant vide) → Montant final = `1`
- CSV : `123456;01/01/2025;;0` → Montant final = `1`
- CSV : `123456;01/01/2025;;100` → Montant final = `100`

### Règle 2 : Traitement des dates

#### ✅ **CAS 1 : Date de fin est VIDE**

```
SI date_fin est vide
  ALORS 
    date_debut (dans SQL) = date_debut (du CSV)
    date_fin (dans SQL) = 20991231
    montant = montant_val (voir Règle 1)
```

**Exemple :**
```
CSV : 123456;15/03/2025;;100

Résultat SQL :
  CLCJEBCOU1 = '20250315'  ← date_debut du CSV
  CLCJEBCOU2 = '20250315'  ← date_debut du CSV
  CLCJINCOU1 = '20991231'  ← date fixe (2099-12-31)
  CLCJINCOU2 = '20991231'  ← date fixe (2099-12-31)
  CLCNDECOU1 = 100         ← montant du CSV
  CLCNDECOU2 = 100         ← montant du CSV
```

#### ✅ **CAS 2 : Date de fin est RENSEIGNÉE**

```
SI date_fin n'est pas vide
  ALORS 
    date_debut (dans SQL) = date_fin (du CSV)  ← IMPORTANT !
    date_fin (dans SQL) = 20991231
    montant = 1  ← Toujours 1 dans ce cas
```

**Exemple :**
```
CSV : 234567;15/03/2025;31/12/2025;

Résultat SQL :
  CLCJEBCOU1 = '20251231'  ← date_fin du CSV (pas date_debut !)
  CLCJEBCOU2 = '20251231'  ← date_fin du CSV (pas date_debut !)
  CLCJINCOU1 = '20991231'  ← date fixe (2099-12-31)
  CLCJINCOU2 = '20991231'  ← date fixe (2099-12-31)
  CLCNDECOU1 = 1           ← Toujours 1
  CLCNDECOU2 = 1           ← Toujours 1
```

---

## 📊 Exemples complets

### Exemple 1 : Date fin vide, montant présent
```
CSV : 123456;01/01/2025;;50

Transformation :
  Code : 123456 (valide ✓)
  Date début : 01/01/2025 → 20250101
  Date fin : vide → 20991231
  Montant : 50

SQL généré :
UPDATE CLIENT SET 
  CLCJEBCOU1 = '20250101', 
  CLCJEBCOU2 = '20250101', 
  CLCJINCOU1 = '20991231', 
  CLCJINCOU2 = '20991231', 
  CLCNDECOU1 = 50,  
  CLCNDECOU2 = 50, 
  CLCTLIBRE4 = 'Mise à jour assurance le 20251209' 
WHERE CLKTSOC = '100' AND CLKTCODE = '123456'
```

### Exemple 2 : Date fin vide, montant vide
```
CSV : 234567;15/03/2025;;

Transformation :
  Code : 234567 (valide ✓)
  Date début : 15/03/2025 → 20250315
  Date fin : vide → 20991231
  Montant : vide → 1 (règle du montant)

SQL généré :
UPDATE CLIENT SET 
  CLCJEBCOU1 = '20250315', 
  CLCJEBCOU2 = '20250315', 
  CLCJINCOU1 = '20991231', 
  CLCJINCOU2 = '20991231', 
  CLCNDECOU1 = 1,  
  CLCNDECOU2 = 1, 
  CLCTLIBRE4 = 'Mise à jour assurance le 20251209' 
WHERE CLKTSOC = '100' AND CLKTCODE = '234567'
```

### Exemple 3 : Date fin présente
```
CSV : 345678;01/06/2025;31/12/2025;999

Transformation :
  Code : 345678 (valide ✓)
  Date début : 01/06/2025 (ignorée car date_fin présente)
  Date fin : 31/12/2025 → devient la date_debut dans SQL !
  Montant : 999 (ignoré car date_fin présente) → 1

SQL généré :
UPDATE CLIENT SET 
  CLCJEBCOU1 = '20251231',  ← date_fin du CSV !
  CLCJEBCOU2 = '20251231',  ← date_fin du CSV !
  CLCJINCOU1 = '20991231', 
  CLCJINCOU2 = '20991231', 
  CLCNDECOU1 = 1,  ← Toujours 1 quand date_fin présente
  CLCNDECOU2 = 1,  ← Toujours 1 quand date_fin présente
  CLCTLIBRE4 = 'Mise à jour assurance le 20251209' 
WHERE CLKTSOC = '100' AND CLKTCODE = '345678'
```

### Exemple 4 : Code invalide (exclu)
```
CSV : 151500;01/01/2025;;100

Résultat : ❌ Enregistrement ignoré (code exclu)
Aucune requête SQL générée
```

### Exemple 5 : Code invalide (pas 6 chiffres)
```
CSV : 12345;01/01/2025;;100

Résultat : ❌ Enregistrement ignoré (code pas 6 chiffres)
Aucune requête SQL générée
```

---

## 🗄️ Champs SQL mis à jour

La requête SQL met à jour ces champs dans la table `CLIENT` :

| Champ SQL | Description | Valeur |
|-----------|-------------|--------|
| `CLCJEBCOU1` | Date début couverture 1 | Date calculée selon règles |
| `CLCJEBCOU2` | Date début couverture 2 | Date calculée selon règles |
| `CLCJINCOU1` | Date fin couverture 1 | Toujours `20991231` |
| `CLCJINCOU2` | Date fin couverture 2 | Toujours `20991231` |
| `CLCNDECOU1` | Montant couverture 1 | Montant calculé selon règles |
| `CLCNDECOU2` | Montant couverture 2 | Montant calculé selon règles |
| `CLCTLIBRE4` | Champ libre 4 | `'Mise à jour assurance le YYYYMMDD'` |

**Condition WHERE :**
```sql
WHERE CLKTSOC = '100' AND CLKTCODE = '123456'
```

- `CLKTSOC` : Code société (100, 200, etc.)
- `CLKTCODE` : Code client (sans les zéros de début)

---

## 🔍 Résumé des règles (tableau de décision)

| Date fin | Montant CSV | Date début SQL | Date fin SQL | Montant SQL |
|----------|-------------|----------------|--------------|-------------|
| Vide     | Vide ou 0   | date_debut     | 20991231     | 1           |
| Vide     | > 0         | date_debut     | 20991231     | montant     |
| Renseignée | N'importe  | date_fin       | 20991231     | 1           |

**Note importante** : Quand date_fin est renseignée dans le CSV, c'est cette date_fin qui devient la date_debut dans SQL (et non la date_debut du CSV).

---

## ⚙️ Implémentation dans le code

Cette logique est implémentée dans la méthode `get_dates_and_amount()` de la classe `assuranceRecord` :

```python
def get_dates_and_amount(self) -> Tuple[str, str, str]:
    date_debut_fmt = self.format_date(self.date_debut)
    date_fin_fmt = self.format_date(self.date_fin)
    montant_val = self.montant.strip()
    
    # Règle : Si montant est vide ou 0, mettre 1
    if not montant_val or montant_val == '0':
        montant_val = '1'
    
    # Règle : Si date_fin est vide
    if not date_fin_fmt:
        return date_debut_fmt, '20991231', montant_val
    else:
        # Si date_fin n'est pas vide
        return date_fin_fmt, '20991231', '1'
```

---

**Document créé le** : 23 décembre 2025  
**Version** : 1.1 (corrigée)