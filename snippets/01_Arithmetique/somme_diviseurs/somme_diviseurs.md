# Somme des Diviseurs & Sous-Programmes

## Description
Cet algorithme permet de vérifier la validité d'un identifiant numérique et de saisir une série d'enregistrements identifiants et dates.
Il illustre la **décomposition modulaire** avec passage de paramètres par variable (`@n`, `@IDENT`, `@DATE`).

## Concepts Abordés
- **Procédures** avec passage par adresse / référence (`@`)
- **Fonctions** avec retour d'un booléen (`Fonction verifIdent(id: chaine) : Booléen`)
- **Boucle Répéter...Jusqu'à** pour le contrôle de saisie
- Tableaux de chaînes de caractères de dimension fixe (50 éléments)

## Spécification des modules
| Module | Type | Paramètres | Rôle |
|---|---|---|---|
| `saisir` | Procédure | `@n: entier` | Saisie sécurisée de n dans [3, 50] |
| `verifIdent` | Fonction | `id: chaine` | Vérifie que l'identifiant est numérique |
| `remplir` | Procédure | `@IDENT, @DATE, n` | Remplit les tableaux jusqu'à validation |
