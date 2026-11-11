# 3. Les Enregistrements (Structures Composées)

Un **Enregistrement** est un type de données personnalisé regroupant plusieurs champs pouvant être de types différents (hétérogènes).

---

## 1. Définition du Type dans le TDNT

La définition se fait obligatoirement dans le **Tableau de déclaration des nouveaux types (TDNT)** :

```algo
Tableau de déclaration des nouveaux types
Etudiant = Enregistrement
    matricule : Entier
    nom       : Chaîne
    moyenne   : Réel
Fin Enregistrement
```

---

## 2. Déclaration d'Objets Enregistrements

Dans le **TDOG** ou **TDOL** :
```algo
Tableau de déclaration des objets globaux
Objet          Type / Nature
E              Etudiant
Classe         Tableau de 30 Etudiant
```

---

## 3. Accès aux Champs (Opérateur Point `.`)

On accède aux données internes d'un enregistrement à l'aide du point `.` :

```algo
E.matricule <- 1042
E.nom <- "Nadia"
E.moyenne <- 16.75

Ecrire_nl("Élève : ", E.nom, " - Moyenne : ", E.moyenne)
```

### Accès dans un Tableau d'Enregistrements :
```algo
Classe[0].nom <- "Amine"
Classe[0].moyenne <- 14.5
```

---

## Correspondance Python

Géré élégamment par la classe d'exécution `Enregistrement` (dérivée de `dict`) acceptant à la fois la syntaxe pointée et par crochet :
```python
E = Enregistrement(matricule=1042, nom="Nadia", moyenne=16.75)
print(E.nom)
```
