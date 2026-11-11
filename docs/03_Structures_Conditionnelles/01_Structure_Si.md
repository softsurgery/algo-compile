# 1. Structure Conditionnelle Si

La structure conditionnelle permet d'exécuter un bloc d'instructions uniquement lorsqu'une condition booléenne est satisfaite.

---

## 1. Forme Simple (Si Réduit)

```algo
Si Condition Alors
  // Traitement exécuté si Condition est Vrai
FinSi
```

### Exemple :
```algo
Si x < 0 Alors
  x <- -x
FinSi
```

---

## 2. Forme Complète (Si ... Alors ... Sinon)

```algo
Si Condition Alors
  // Traitement 1
Sinon
  // Traitement 2
FinSi
```

### Exemple :
```algo
Si moyenne >= 10 Alors
  Ecrire_nl("Félicitations, vous êtes Admis")
Sinon
  Ecrire_nl("Ajourné, session de rattrapage")
FinSi
```

---

## 3. Conditions Imbriquées / Enchaînées

```algo
Si note >= 16 Alors
  mention <- "Très Bien"
Sinon Si note >= 14 Alors
  mention <- "Bien"
Sinon Si note >= 12 Alors
  mention <- "Assez Bien"
Sinon Si note >= 10 Alors
  mention <- "Passable"
Sinon
  mention <- "Non admis"
FinSi
```

---

## Bonnes Pratiques
* Toujours fermer chaque `Si` par son mot-clé obligatoire `FinSi`.
* Éviter les imbrications trop profondes en préférant la structure `Selon` quand cela est possible.
