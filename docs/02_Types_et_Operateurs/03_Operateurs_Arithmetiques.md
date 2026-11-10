# 3. Opérateurs Arithmétiques

Les opérateurs arithmétiques permettent d'effectuer des calculs mathématiques sur les nombres entiers et réels.

---

## Liste des Opérateurs

| Opérateur Algo | Python | Rôle | Exemple Algo | Résultat |
|---|---|---|---|---|
| `+` | `+` | Addition | `7 + 3` | `10` |
| `-` | `-` | Soustraction | `10 - 4` | `6` |
| `*` | `*` | Multiplication | `6 * 7` | `42` |
| `/` | `/` | Division réelle | `7 / 2` | `3.5` |
| `Div` | `//` | Division entière (quotient) | `7 Div 2` | `3` |
| `Mod` | `%` | Reste de la division entière (modulo) | `7 Mod 2` | `1` |

---

## Règles de Priorité

1. Parenthèses `( ... )`
2. Fonctions arithmétiques (`RacineCarré`, `Abs`, etc.)
3. `*`, `/`, `Div`, `Mod`
4. `+`, `-`

---

## Exemples Typiques

```algo
// Tester si un entier n est pair
Si (n Mod 2 = 0) Alors
  Ecrire_nl(n, " est PAIR")
FinSi

// Extraction des chiffres d'un nombre à deux chiffres
dizaine <- n Div 10
unite <- n Mod 10
```
