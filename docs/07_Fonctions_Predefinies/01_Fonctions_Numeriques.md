# 1. Fonctions Numériques et Aléatoires

Le compilateur fournit des fonctions mathématiques prédéfinies prêtes à l'emploi.

---

## Répertoire des Fonctions

| Fonction Algo | Équivalent Python | Rôle | Exemple | Résultat |
|---|---|---|---|---|
| `Arrondi(x)` | `round(x)` | Retourne l'entier le plus proche du réel `x`. | `Arrondi(3.7)` | `4` |
| `RacineCarré(x)` | `math.sqrt(x)` | Retourne la racine carrée positive de `x`. | `RacineCarré(25)` | `5.0` |
| `Aléa(vi, vf)` | `random.randint(vi, vf)` | Retourne un entier aléatoire dans $[vi, vf]$ (inclus). | `Aléa(1, 6)` | Entier de 1 à 6 |
| `Ent(x)` | `int(x)` | Retourne la partie entière de `x`. | `Ent(7.89)` | `7` |
| `Abs(x)` | `abs(x)` | Retourne la valeur absolue de `x`. | `Abs(-15)` | `15` |

---

## Remarques Importantes

* L'argument de `RacineCarré` doit être supérieur ou égal à zéro sous peine d'erreur de domaine mathématique.
* Pour `Aléa(vi, vf)`, on doit toujours avoir `vi <= vf`.
* Ces fonctions ne nécessitent aucun import manuel dans le code algorithmique.
