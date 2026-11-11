# Vérification de Palindrome

## Description
Un algorithme classique qui teste si un mot est identique qu'il soit lu de gauche à droite ou de droite à gauche (ex: *radar*, *kayak*, *non*).

## Principe de l'Algorithme
1. Saisie d'une chaîne non vide avec une boucle `Répéter...Jusqu'à`.
2. Initialisation de deux pointeurs : `i` au début (0) et `j` à la fin (`Long(ch) - 1`).
3. Parcours avec `Tant que (i < j Et valide)` :
   - Comparaison de `ch[i]` et `ch[j]`.
   - Si différents, `valide <- Faux`.
   - Sinon incrémenter `i` et décrémenter `j`.
4. Affichage du résultat conditionnel `Si...Alors...Sinon`.

## Complexité
- **Temporelle** : O(N/2) => O(N)
- **Spatiale** : O(1) (en place)
