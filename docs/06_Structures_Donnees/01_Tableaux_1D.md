# 1. Tableaux à Une Dimension (Vecteurs)

Un tableau à une dimension est une collection ordonnée, de taille fixe, d'éléments de même type (homogène).

---

## Déclaration

Dans le **TDOG** ou **TDOL** :

```algo
Objet          Type / Nature
T              Tableau de 20 Entier
Mots           Tableau de 50 Chaîne
```

---

## Indice de Départ : 0 (Convention)

> **Important** : Conformément à la norme officielle, le premier élément se trouve à l'indice **0**.
> Pour un tableau de taille `N`, les indices valides vont de `0` à `N - 1`.

---

## Opérations Fondamentales

### 1. Accès et Modification :

```algo
T[0] <- 15
T[i] <- T[i] + 1
```

### 2. Saisie d'un Tableau :

```algo
Pour i de 0 à n - 1 Faire
  Ecrire("T[", i, "] = ")
  Lire(T[i])
Fin Pour
```

### 3. Affichage d'un Tableau :

```algo
Pour i de 0 à n - 1 Faire
  Ecrire(T[i], "  ")
Fin Pour
Ecrire_nl("")
```

---

## Correspondance Python

Le compilateur génère des tableaux statiques et typés via `numpy.array` :

```python
from numpy import array
T = array([0] * 20)
Mots = array([''] * 50, dtype='U20')
```
