# 2. Tableau des Objets Globaux (TDOG)

Le **Tableau de déclaration des objets globaux** (TDOG) est placé **immédiatement sous le `FIN` de l'algorithme principal**. Il recense tous les objets visibles par l'algorithme entier.

---

## Syntaxe et Format

```algo
ALGORITHME CalculMoyenne
DEBUT
  Ecrire("Donner la note : ")
  Lire(note)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
note, somme    Réel
n, i           Entier
T              Tableau de 20 Réel
Calcul         Fonction
```

---

## Règles Spécifiques

| Règle | Détail |
|---|---|
| **Position** | Placé après le `FIN` de l'algorithme principal. |
| **Colonnes** | Deux colonnes obligatoires : `Objet` (à gauche) et `Type / Nature` (à droite). |
| **Regroupement** | Les objets de même type peuvent être déclarés sur une même ligne séparés par des virgules (ex: `n, i : Entier`). |
| **Fonctions** | Les fonctions ou procédures définies doivent être déclarées avec la nature `Fonction` ou `Procédure`. |
| **Tableaux** | Un tableau est typé sous la forme : `Tableau de <Taille> <Type>` (ex: `Tableau de 50 Entier`). |

---

## Erreurs Fréquentes

* **Oubli du TDOG** : Tout algorithme principal requiert son TDOG. L'oubli génère une alerte de validation.
* **Variable non déclarée** : Utiliser un nom de variable dans le corps sans le déclarer dans le TDOG provoque une erreur de compilation.
