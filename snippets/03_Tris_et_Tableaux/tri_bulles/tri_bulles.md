# Algorithme du Tri à Bulles (Bubble Sort)

## Description
Le tri à bulles parcourt répétitivement un tableau d'éléments en comparant chaque paire d'éléments adjacents et en les permutant s'ils sont dans le mauvais ordre.

## Caractéristiques
- **Stabilité** : Oui (conserve l'ordre relatif des éléments égaux)
- **Complexité dans le pire cas** : O(n^2)
- **Complexité dans le meilleur cas (déjà trié)** : O(n) grâce au booléen `permute`

## Trace d'exécution
À chaque passe complète, le plus grand élément restant « remonte » comme une bulle vers sa position finale à droite.
Consultez le fichier joint `trace_execution.txt` pour observer chaque étape.
