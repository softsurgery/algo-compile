# 2. Tableaux à Deux Dimensions (Matrices)

Une matrice est un tableau organisé en lignes et colonnes, chaque case contenant un élément de même type.

---

## Déclaration

Dans le **TDOG** ou **TDOL** :
```algo
Objet          Type / Nature
M              Tableau de 10 x 20 Entier
Mat            Tableau de 5 x 5 Réel
```

* Le premier nombre correspond au nombre de **Lignes** ($L$).
* Le second nombre correspond au nombre de **Colonnes** ($C$).

---

## Accès aux Éléments

* L'élément situé à la ligne `i` et la colonne `j` est noté : `M[i, j]` (ou `M[i][j]`).
* Les indices de lignes varient de `0` à `L - 1`.
* Les indices de colonnes varient de `0` à `C - 1`.

---

## Exemple : Remplissage et Affichage d'une Matrice

```algo
ALGORITHME MatriceExemple
DEBUT
  // Remplissage avec des nombres aléatoires
  Pour i de 0 à 2 Faire
    Pour j de 0 à 3 Faire
      M[i, j] <- Aléa(1, 50)
    Fin Pour
  Fin Pour

  // Affichage sous forme de grille
  Pour i de 0 à 2 Faire
    Pour j de 0 à 3 Faire
      Ecrire(M[i, j], "\t")
    Fin Pour
    Ecrire_nl("")
  Fin Pour
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
M              Tableau de 3 x 4 Entier
i, j           Entier
```

---

## Correspondance Python

```python
from numpy import array
M = array([[0] * 4 for _ in range(3)])
# Accès : M[i, j]
```
