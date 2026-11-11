# 4. Les Fichiers (Texte et Données)

Un **Fichier** est une structure de données stockée de façon permanente sur un support de mémoire de masse (disque). Il permet de conserver les données après l'arrêt du programme.

---

## 1. Types de Fichiers selon les Conventions

La convention distingue deux grandes catégories de fichiers :

| Catégorie              | Type Algorithmique  | Description                                                                  | Implémentation Python                         |
| ---------------------- | ------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| **Fichier texte**      | `Fichier Texte`     | Fichier composé de lignes de caractères lisibles.                            | Mode texte standard (`r`, `w`, `a`)           |
| **Fichier de données** | `Fichier de <Type>` | Fichier binaire stockant des objets typés (entiers, réels, enregistrements). | Mode binaire (`rb`, `wb`, `ab`) avec `pickle` |

---

## 2. Déclaration dans les Tableaux d'Objets (TDOG / TDOL)

Dans le **Tableau de déclaration des objets globaux (TDOG)** ou **TDOL** :

```algo
Objet          Type / Nature
F_txt          Fichier Texte
F_notes        Fichier de Réel
F_eleves       Fichier de Eleve
```

---

## 3. Ouverture d'un Fichier : Procédure `Ouvrir`

Conformément aux conventions officielles, l'ouverture d'un fichier associe son chemin physique à un nom logique avec un mode d'accès :

```algo
Ouvrir ("Chemin\\Nom_physique", Nom_logique, "Mode")
```

### Règle d'Emplacement des Fichiers Manipulés :

> **Important** : Le fichier qui sera ouvert et manipulé est **localisé dans le même dossier que l'algorithme en cours d'exécution**, à moins qu'un chemin absolu (ex: `"/home/user/..."` ou `"C:\\..."`) ne soit expressément spécifié.
> Ainsi, `Ouvrir("notes.txt", F, "r")` cherchera ou créera toujours le fichier `notes.txt` directement à côté du fichier `.algo`.

### Modes d'Ouverture :

| Mode   | Type de Fichier    | Rôle                                                 |
| ------ | ------------------ | ---------------------------------------------------- |
| `"r"`  | Fichier Texte      | Lecture (le fichier doit déjà exister).              |
| `"w"`  | Fichier Texte      | Écriture / Création (écrase le contenu s'il existe). |
| `"a"`  | Fichier Texte      | Ajout (écrit à la fin du fichier sans effacer).      |
| `"rb"` | Fichier de Données | Lecture binaire (pointeur positionné au début).      |
| `"wb"` | Fichier de Données | Écriture binaire / Création.                         |
| `"ab"` | Fichier de Données | Ajout binaire en fin de fichier.                     |

### Transpilation Python :

```python
Nom_logique = Ouvrir("Chemin\\Nom_physique", "Mode")
```

---

## 4. Opérations sur les Fichiers Textes

| Opération Algo                 | Équivalent Python                  | Rôle                                                       |
| ------------------------------ | ---------------------------------- | ---------------------------------------------------------- |
| `Ouvrir("source.txt", F, "r")` | `F = open("source.txt", "r")`      | Ouverture en lecture                                       |
| `Lire(F, ch)`                  | `ch = F.read()`                    | Lecture de **tout** le fichier dans une chaîne             |
| `Lire_ligne(F, ch)`            | `ch = F.readline().rstrip('\r\n')` | Lecture d'**une seule ligne** (sans le saut de ligne `\n`) |
| `Ecrire(F, ch)`                | `F.write(ch)`                      | Écriture sans saut de ligne                                |
| `Ecrire_nl(F, ch)`             | `F.write(ch + "\n")`               | Écriture **avec saut de ligne**                            |
| `Fin_fichier(F)`               | Condition de fin                   | `Vrai` si la fin du fichier est atteinte                   |
| `Fermer(F)`                    | `F.close()`                        | Fermeture obligatoire du fichier                           |

### Exemple : Parcours ligne par ligne d'un fichier texte

```algo
ALGORITHME LectureTexte
DEBUT
  Ouvrir("donnees.txt", F, "r")
  Tant que Non Fin_fichier(F) Faire
    Lire_ligne(F, ligne)
    Ecrire_nl(ligne)
  Fin Tant que
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier Texte
ligne          Chaîne
```

---

## 5. Opérations sur les Fichiers de Données (Typés)

Pour les fichiers de données d'éléments (`Entier`, `Réel`, ou `Enregistrement`), la lecture et l'écriture s'effectuent par objet complet (sérialisation via `pickle`) :

| Opération Algo                 | Équivalent Python             | Rôle                                  |
| ------------------------------ | ----------------------------- | ------------------------------------- |
| `Ouvrir("notes.dat", F, "wb")` | `F = open("notes.dat", "wb")` | Ouverture binaire en création         |
| `Ecrire(F, note)`              | `dump(note, F)`               | Sauvegarde de l'objet dans le fichier |
| `Ouvrir("notes.dat", F, "rb")` | `F = open("notes.dat", "rb")` | Ouverture binaire en lecture          |
| `Lire(F, note)`                | `note = load(F)`              | Lecture de l'objet depuis le fichier  |
| `Fin_fichier(F)`               | `_fin_fichier(F)`             | Détection de fin de fichier           |
| `Fermer(F)`                    | `F.close()`                   | Fermeture du fichier                  |

---

## 6. Bonnes Pratiques

1. **Toujours fermer un fichier** ouvert avec `Fermer(Nom_logique)`.
2. Pour les fichiers texte, la fin de fichier correspond à la chaîne vide `""`.
3. Vérifier le mode d'ouverture : utiliser `"r"` ou `"rb"` pour lire, `"w"` ou `"wb"` pour écrire.
