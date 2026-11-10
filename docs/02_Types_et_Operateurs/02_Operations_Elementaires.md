# 2. Opérations Élémentaires (Entrées, Sorties et Affectation)

Les opérations élémentaires forment la base de toute interaction avec l'utilisateur et de manipulation de données.

---

## 1. L'Affectation (`<-` ou `←`)

L'affectation permet de stocker le résultat d'une expression dans une variable.

```algo
x <- 10
somme <- somme + note
message <- "Bienvenue"
T[0] <- 42
```

* Le symbole peut être saisi sous la forme `<-` ou directement avec la flèche Unicode `←`.
* En Python, cela correspond à l'opérateur d'assignation `=`.

---

## 2. La Lecture Clavier (`Lire`)

Permet de saisir une valeur depuis le clavier et de la stocker dans une variable.

```algo
Ecrire("Entrez votre âge : ")
Lire(age)
Lire(nom, prenom)
```

* En Python : `age = int(input())` ou `nom = input()`. Le compilateur transpile intelligemment selon le type de la variable.

---

## 3. L'Écriture à l'Écran (`Ecrire` et `Ecrire_nl`)

| Instruction | Équivalent Python | Effet |
|---|---|---|
| `Ecrire(expr1, expr2, ...)` | `print(expr1, expr2, end='')` | Affiche les arguments **sans saut de ligne**. |
| `Ecrire_nl(expr1, expr2, ...)` | `print(expr1, expr2)` | Affiche les arguments **avec saut de ligne final**. |

### Exemple :

```algo
Ecrire("La note est : ", note)
Ecrire_nl(" / 20")
```
Affichage :
```text
La note est : 15 / 20
```
