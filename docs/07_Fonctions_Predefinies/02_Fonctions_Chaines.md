# 2. Fonctions sur les Chaînes de Caractères

Ces fonctions permettent de mesurer, découper, rechercher et modifier les chaînes de caractères.

---

## Répertoire des Fonctions

| Fonction Algo | Équivalent Python | Rôle | Exemple | Résultat |
|---|---|---|---|---|
| `Long(ch)` | `len(ch)` | Longueur (nombre de caractères) | `Long("Tunisie")` | `7` |
| `Pos(ch1, ch2)` | `ch2.find(ch1)` | Première position de `ch1` dans `ch2` (`-1` si absente) | `Pos("info", "algorithme info")` | `11` |
| `Sous_chaine(ch, d, f)` | `ch[d:f]` | Sous-chaîne de l'indice `d` jusqu'à `f` exclu | `Sous_chaine("ABCDEF", 1, 4)` | `"BCD"` |
| `Effacer(ch, d, f)` | `ch[:d] + ch[f:]` | Chaîne privée de la tranche d'indices `[d, f[` | `Effacer("ABCDEF", 1, 4)` | `"AEF"` |
| `Majus(ch)` | `ch.upper()` | Convertit la chaîne en majuscules | `Majus("bonjour")` | `"BONJOUR"` |

---

## Rappels sur l'Indiçage

* Les indices commencent à **0**.
* Pour la fonction `Pos`, si la sous-chaîne recherchée n'est pas présente, la fonction renvoie `-1`.
* Pour `Sous_chaine(ch, d, f)` et `Effacer(ch, d, f)`, l'indice de fin `f` est **exclu**.
