# 2. Structure de Choix Multiple (Selon)

La structure `Selon` permet d'aiguiller l'exécution vers différentes branches selon la valeur prise par une variable sélectrice (entier, caractère ou chaîne).

---

## Syntaxe Générale

```algo
Selon <Sélecteur>
  valeur_1 : Traitement_1
  valeur_2, valeur_3 : Traitement_2
  borne_inf .. borne_sup : Traitement_3
  Sinon Traitement_Par_Defaut
Fin Selon
```

---

## Exemple avec Valeurs Discrètes

```algo
Selon jour
  1 : Ecrire_nl("Lundi")
  2 : Ecrire_nl("Mardi")
  3 : Ecrire_nl("Mercredi")
  4 : Ecrire_nl("Jeudi")
  5 : Ecrire_nl("Vendredi")
  6, 7 : Ecrire_nl("Week-end")
  Sinon Ecrire_nl("Jour invalide")
Fin Selon
```

---

## Exemple avec Intervalles

```algo
Selon note
  16 .. 20 : mention <- "Très Bien"
  14 .. 15.99 : mention <- "Bien"
  12 .. 13.99 : mention <- "Assez Bien"
  10 .. 11.99 : mention <- "Passable"
  Sinon mention <- "Échec"
Fin Selon
```

---

## Correspondance Python

Pour Python 3.10+, le compilateur transpile cette structure vers l'instruction native `match / case` :

```python
match note:
    case _ if 16 <= note <= 20:
        mention = "Très Bien"
    case _ if 14 <= note <= 15.99:
        mention = "Bien"
    case _:
        mention = "Échec"
```

Pour les versions antérieures, elle est convertie en chaîne `if / elif / else`.
