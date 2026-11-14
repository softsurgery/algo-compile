# Somme des Diviseurs

## Description
Cet algorithme lit un entier strictement positif `n` à l'aide d'une procédure avec passage par variable (`@n`), affiche tous ses diviseurs et calcule leur somme via la fonction `SommeDiviseurs(n)`.

## Concepts Abordés
- **Procédure** avec passage par variable (`@n`) et boucle `Répéter ... Jusqu'à`
- **Fonction** retournant un entier (`Fonction SommeDiviseurs(n: Entier) : Entier`)
- **Boucle `Pour`** et test de divisibilité avec `Mod`

## Spécification des modules
| Module | Type | Paramètres | Rôle |
|---|---|---|---|
| `Saisir` | Procédure | `@n: Entier` | Saisie contrôlée d'un entier `n > 0` |
| `SommeDiviseurs` | Fonction | `n: Entier` | Affiche les diviseurs de `n` et retourne leur somme |
