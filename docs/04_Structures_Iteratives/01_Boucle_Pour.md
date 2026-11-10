# 1. Structure Itérative Complète (Pour)

La boucle `Pour` est utilisée lorsque le nombre d'itérations est **connu à l'avance** avant d'entrer dans la boucle.

---

## Syntaxe Générale

```algo
Pour compteur de Début à Fin [Pas = valeur_du_pas] Faire
  // Instructions à répéter
Fin Pour
```

---

## 1. Pas Par Défaut (+1)

Lorsque le pas n'est pas spécifié, il vaut implicitement **+1** :

```algo
somme <- 0
Pour i de 1 à 10 Faire
  somme <- somme + i
Fin Pour
Ecrire_nl("Somme = ", somme)
```

Équivalent Python généré :
```python
somme = 0
for i in range(1, 10 + 1, 1):
    somme += i
```

---

## 2. Pas Spécifié (Positif ou Négatif)

### Pas Positif :
```algo
Pour i de 0 à 100 Pas = 10 Faire
  Ecrire(i, " ")
Fin Pour
```

### Décompte (Pas Négatif) :
```algo
Pour i de 10 à 1 Pas = -1 Faire
  Ecrire(i, " ")
Fin Pour
Ecrire_nl("Décollage !")
```

---

## Points Importants
* Le compteur de boucle doit être déclaré dans le TDOG ou TDOL (généralement de type `Entier`).
* Ne jamais modifier manuellement la valeur de la variable de contrôle (`i <- i + 1`) à l'intérieur du corps d'une boucle `Pour`.
