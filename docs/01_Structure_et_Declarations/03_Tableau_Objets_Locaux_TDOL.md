# 3. Tableau des Objets Locaux (TDOL)

Le **Tableau de déclaration des objets locaux** (TDOL) est associé à **chaque sous-programme** (fonction ou procédure). Il est positionné **immédiatement après le `FIN`** de ce sous-programme.

---

## Exemple d'utilisation

```algo
Fonction Puissance(x: Réel, n: Entier) : Réel
DEBUT
  res <- 1.0
  Pour i de 1 à n Faire
    res <- res * x
  Fin Pour
  Retourner res
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
res            Réel
i              Entier
```

---

## Règles Clés

1. **Portée locale** :
   - Les objets figurant dans le TDOL ne sont accessibles **que** dans le sous-programme concerné.
   - Ils sont détruits à la sortie du sous-programme.
2. **Paramètres formels** :
   - Les paramètres définis dans l'en-tête (ex: `x` et `n`) n'ont pas besoin d'être redéclarés dans le TDOL.
3. **Absence d'objets locaux** :
   - Si un sous-programme n'utilise aucune variable locale, on place une barre oblique `/` dans chaque colonne :
```algo
Tableau de déclaration des objets locaux
Objet          Type / Nature
/              /
```
