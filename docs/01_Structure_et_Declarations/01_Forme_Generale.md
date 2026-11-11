# 1. Forme Générale d'un Algorithme

Un algorithme complet respecte une structure modulaire stricte, composée d'éventuels sous-programmes (fonctions ou procédures), du programme principal, et des tableaux de déclarations.

---

## Structure d'un Programme Complet

```algo
// 1. Sous-programmes (Procédures et Fonctions)
Procedure Exemple(@x: Entier)
DEBUT
  // Instructions locales
FIN
Tableau de déclaration des objets locaux
Objet          Type / Nature
/              /

// 2. Algorithme Principal
ALGORITHME NomAlgorithme
DEBUT
  // Instructions principales
  Ecrire("Bienvenue dans le programme")
FIN

// 3. Déclaration des types personnalisés (optionnel)
Tableau de déclaration des nouveaux types
// Définitions de types (ex: enregistrements)

// 4. Déclaration des objets globaux (obligatoire)
Tableau de déclaration des objets globaux
Objet          Type / Nature
x              Entier
```

---

## Règles Fondamentales

1. **Mot-clé de début et de fin** :
   - Tout algorithme débute par `ALGORITHME <Nom>` et son bloc d'instructions est délimité par `DEBUT` et `FIN`.
   - Chaque sous-programme se termine obligatoirement par `FIN`.
2. **Indentation** :
   - Les blocs d'instructions situés entre `DEBUT` et `FIN`, ainsi que l'intérieur des structures de contrôle (`Si`, `Pour`, `Tant que`...) doivent être indentés pour une clarté optimale.
3. **Indices des tableaux et chaînes** :
   - Selon la convention officielle, le premier élément d'une chaîne ou d'un tableau a l'indice **0**.
4. **Typage strict** :
   - Tout identificateur (variable, constante, tableau, fonction) utilisé dans l'algorithme doit être expressément déclaré dans son tableau correspondant (**TDOG** ou **TDOL**).
