# Structure Enregistrement et Structure Selon

## Description
Cet exemple démontre l'utilisation des types structurés (`Enregistrement`) en algorithmique et le branchement conditionnel à choix multiple (`Selon`).

## Concepts
- Définition d'un nouveau type dans le tableau TDNT :
```algo
Type
  Eleve = Enregistrement
    nom : Chaine
    moyenne : Reel
  Fin Enregistrement
```
- Accès aux champs par le point : `e.nom`, `e.moyenne`
- Aiguillage `Selon e.moyenne Faire` avec tranches de notes (intervalles).
