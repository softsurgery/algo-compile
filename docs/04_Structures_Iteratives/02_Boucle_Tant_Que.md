# 2. Boucle à Condition Préalable (Tant que)

La boucle `Tant que` répète un bloc d'instructions **tant qu'une condition reste vraie**. La condition est évaluée **avant** chaque exécution du corps de la boucle.

---

## Syntaxe Générale

```algo
Tant que <Condition> Faire
  # Instructions à répéter
  # Mise à jour de la condition pour éviter une boucle infinie
Fin Tant que
```

---

## Exemple : Recherche de l'élément d'arrêt

```algo
Ecrire("Entrez un nombre positif (0 pour stopper) : ")
Lire(n)

somme <- 0
Tant que n > 0 Faire
  somme <- somme + n
  Ecrire("Nombre suivant : ")
  Lire(n)
Fin Tant que

Ecrire_nl("Total cumulé = ", somme)
```

---

## Particularités Fondamentales

1. **Nombre d'exécutions possible : de 0 à l'infini**. Si la condition est fausse dès le départ, le corps n'est jamais exécuté.
2. **Initialisation** : Les variables composant la condition doivent être initialisées **avant** l'entrée dans la boucle.
3. **Évolution** : Le corps de la boucle doit obligatoirement modifier au moins une variable de la condition sous peine d'engendrer une boucle infinie.

---

## Correspondance Python

```python
while condition:
    # Instructions
```
