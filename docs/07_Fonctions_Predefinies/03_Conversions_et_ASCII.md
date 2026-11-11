# 3. Conversions de Types et Code ASCII

Ces fonctions permettent de passer d'un type textuel à numérique et d'exploiter les codes ASCII.

---

## 1. Fonctions de Conversion

| Fonction Algo | Équivalent Python | Rôle | Exemple | Résultat |
|---|---|---|---|---|
| `Convch(x)` | `str(x)` | Convertit un nombre en chaîne | `Convch(123)` | `"123"` |
| `Valeur(ch)` | `int(ch)` ou `float(ch)` | Convertit une chaîne en valeur numérique | `Valeur("45.6")` | `45.6` |
| `Estnum(ch)` | `ch.isdecimal()` | Teste si la chaîne représente un nombre valide | `Estnum("124")` | `Vrai` |

---

## 2. Fonctions ASCII

| Fonction Algo | Équivalent Python | Rôle | Exemple | Résultat |
|---|---|---|---|---|
| `Ord(c)` | `ord(c)` | Retourne le code ASCII (entier) du caractère `c`. | `Ord('A')` | `65` |
| `Chr(d)` | `chr(d)` | Retourne le caractère correspondant au code ASCII `d`. | `Chr(65)` | `'A'` |

---

## Exemple d'application : Décalage César (Chiffrement)

```algo
Fonction ChiffrerCaractere(c: Caractère, decalage: Entier) : Caractère
DEBUT
  code <- Ord(c) + decalage
  Retourner Chr(code)
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
code           Entier
```
