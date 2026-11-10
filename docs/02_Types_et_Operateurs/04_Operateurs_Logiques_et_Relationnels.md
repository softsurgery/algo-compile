# 4. Opérateurs Logiques et Relationnels

Ces opérateurs permettent de construire des conditions et des prédicats booléens.

---

## 1. Opérateurs Relationnels (Comparaison)

| Opérateur Algo | Python | Signification |
|---|---|---|
| `=` | `==` | Égal à |
| `≠` ou `<>` | `!=` | Différent de |
| `<` | `<` | Strictement inférieur |
| `<=` ou `≤` | `<=` | Inférieur ou égal |
| `>` | `>` | Strictement supérieur |
| `>=` ou `≥` | `>=` | Supérieur ou égal |

---

## 2. Opérateurs Logiques (Booléens)

| Opérateur Algo | Python | Signification |
|---|---|---|
| `Non` | `not` | Négation logique (inverse la valeur) |
| `Et` | `and` | Conjonction logique (Vrai si les deux opérandes sont Vrais) |
| `Ou` | `or` | Disjonction logique (Vrai si au moins un opérande est Vrai) |

---

## Table de Vérité

| A | B | Non A | A Et B | A Ou B |
|---|---|---|---|---|
| `Vrai` | `Vrai` | `Faux` | `Vrai` | `Vrai` |
| `Vrai` | `Faux` | `Faux` | `Faux` | `Vrai` |
| `Faux` | `Vrai` | `Vrai` | `Faux` | `Vrai` |
| `Faux` | `Faux` | `Vrai` | `Faux` | `Faux` |

---

## Exemple d'utilisation

```algo
Si (note >= 10) Et (absences <= 3) Alors
  Ecrire_nl("Admis sans réserve")
Sinon
  Ecrire_nl("Revue nécessaire")
FinSi
```
