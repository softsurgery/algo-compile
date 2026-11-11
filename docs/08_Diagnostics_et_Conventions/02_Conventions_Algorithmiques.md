# 2. Conventions Algorithmiques Officielles

Synthèse des conventions adoptées pour l'enseignement de l'informatique et de l'algorithmique (Sections Sciences de l'Informatique, Mathématiques et Sciences Expérimentales).

---

## 1. Principes Majeurs

1. **Indice 0** :
   - Tout tableau, matrice ou chaîne de caractères a son premier élément à l'indice **0**.
2. **Typage Explicite** :
   - Tout objet manipulé possède un type déclaré. Pas de typage implicite.
3. **Modularité** :
   - Tout programme complexe est subdivisé en fonctions et procédures dotées de leurs TDOL respectifs.
4. **Tableaux Statiques et Homogènes** :
   - Les tableaux ont une taille maximale prédéfinie lors de la déclaration (`Tableau de N Type`).

---

## 2. Correspondance des Notations

| Algorithmique Officielle  | Transpilation Python                   |
| ------------------------- | -------------------------------------- |
| `x <- expr` ou `x ← expr` | `x = expr`                             |
| `Lire(x)`                 | Saisie selon type (ex: `int(input())`) |
| `Ecrire(expr)`            | `print(expr, end='')`                  |
| `Ecrire_nl(expr)`         | `print(expr)`                          |
| `a Div b`                 | `a // b`                               |
| `a Mod b`                 | `a % b`                                |
| `a ≠ b` ou `a <> b`       | `a != b`                               |
| `Non (A Et B)`            | `not (A and B)`                        |
| `x ∈ [a .. b]`            | `a <= x <= b`                          |
| `Tableau de N Type`       | `numpy.array([defaut] * N)`            |
