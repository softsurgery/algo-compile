# 4. Tableau des Nouveaux Types (TDNT)

Le **Tableau de déclaration des nouveaux types** (TDNT) permet de définir des structures de données complexes composées de champs hétérogènes (les **enregistrements**), ainsi que des types personnalisés.

---

## Syntaxe d'un Enregistrement

```algo
Tableau de déclaration des nouveaux types
Eleve = Enregistrement
    nom : Chaîne
    age : Entier
    moyenne : Réel
Fin Enregistrement

Point = Enregistrement
    x, y : Réel
Fin Enregistrement
```

---

## Déclaration et Utilisation dans l'Algorithme

Après avoir déclaré un type dans le TDNT, on peut déclarer des variables ou tableaux de ce type dans le TDOG ou TDOL :

```algo
ALGORITHME GestionPoints
DEBUT
  P.x <- 12.5
  P.y <- -3.0
  Ecrire_nl("Coordonnées : (", P.x, ", ", P.y, ")")
FIN

Tableau de déclaration des nouveaux types
Point = Enregistrement
    x, y : Réel
Fin Enregistrement

Tableau de déclaration des objets globaux
Objet          Type / Nature
P              Point
```

---

## Correspondance Python

En Python, ces structures sont modélisées dynamiquement via des dictionnaires enrichis (`dict` ou `Enregistrement`), permettant à la fois l'accès direct par attribut (`P.x`) et par clé (`P['x']`).
