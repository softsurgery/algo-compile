# 4. Procédures et Fonctions sur les Fichiers

Répertoire officiel des instructions de manipulation de fichiers selon les conventions algorithmiques.

---

## Tableau Récapitulatif

| Instruction | Forme | Description |
|---|---|---|
| **Ouvrir** | `Ouvrir("chemin", F, "mode")` | Ouvre le fichier désigné et l'associe à `F`. Si `"chemin"` est relatif, il est résolu dans le dossier de l'algorithme en cours d'exécution. |
| **Fermer** | `Fermer(F)` | Ferme le descripteur de fichier `F`. |
| **Lire** | `Lire(F, objet)` | Lit la totalité d'un fichier texte ou le prochain enregistrement d'un fichier de données. |
| **Lire_ligne** | `Lire_ligne(F, ligne)` | Lit la prochaine ligne d'un fichier texte. |
| **Ecrire** | `Ecrire(F, contenu)` | Écrit du contenu ou enregistre un objet sans saut de ligne. |
| **Ecrire_nl** | `Ecrire_nl(F, contenu)` | Écrit une ligne terminée par un retour à la ligne dans un fichier texte. |
| **Fin_fichier** | `Fin_fichier(F)` | Fonction booléenne retournant `Vrai` si la fin du fichier est atteinte, sinon `Faux`. |

---

## Modes d'Ouverture Supportés

* **Fichiers Texte** :
  - `"r"` : Lecture
  - `"w"` : Écriture (écrase le fichier)
  - `"a"` : Ajout en fin de fichier
* **Fichiers de Données** :
  - `"rb"` : Lecture binaire
  - `"wb"` : Écriture binaire
  - `"ab"` : Ajout binaire

---

## Exemple Minimal

```algo
ALGORITHME EcritureSimple
DEBUT
  Ouvrir("resultat.txt", F, "w")
  Ecrire_nl(F, "Première ligne de résultat")
  Ecrire_nl(F, "Fin du traitement")
  Fermer(F)
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
F              Fichier Texte
```
