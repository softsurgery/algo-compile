# 1. Les Fonctions

Une **Fonction** est un sous-programme qui effectue un traitement et **retourne obligatoirement un résultat scalaire unique**.

---

## Syntaxe Générale

```algo
Fonction NomFonction(param1: Type1, param2: Type2) : TypeRetour
DEBUT
  // Traitement
  Retourner resultat
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
resultat       TypeRetour
```

---

## Exemple Complet : Factorielle

```algo
Fonction Factorielle(n: Entier) : Entier
DEBUT
  f <- 1
  Pour i de 2 à n Faire
    f <- f * i
  Fin Pour
  Retourner f
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
f, i           Entier

ALGORITHME TestFact
DEBUT
  Ecrire("5! = ", Factorielle(5))
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
Factorielle    Fonction
```

---

## Caractéristiques Essentielles

1. **Type de retour obligatoire** : Précisé après les paramètres avec `: TypeRetour`.
2. **Instruction `Retourner`** : Chaque chemin d'exécution doit renvoyer une valeur.
3. **Appel** : Une fonction s'appelle toujours au sein d'une **expression**, d'une affectation ou d'un affichage :
   ```algo
   y <- 2 * Factorielle(k) + 1
   ```
