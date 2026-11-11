# 3. Passage de Paramètres et Portée des Variables

Le mode de passage détermine si les modifications apportées à un paramètre formel dans un sous-programme se répercutent sur la variable d'origine (argument effectif) transmise lors de l'appel.

---

## 1. Passage par Valeur (Par défaut)

* **Principe** : Le sous-programme reçoit une **copie** de la valeur de l'argument.
* **Effet** : Toute modification du paramètre n'affecte en rien la variable originale.
* **Syntaxe** : `param: Type` (sans symbole particulier).

```algo
Procédure Modifier(x: Entier)
DEBUT
  x <- x + 10 // Ne modifie que la copie locale
FIN
```

---

## 2. Passage par Référence / Adresse (Symbole `@`)

* **Principe** : Le sous-programme reçoit l'**adresse mémoire** de la variable d'origine.
* **Effet** : Toute modification effectuée sur le paramètre modifie directement la variable de l'appelant.
* **Syntaxe** : `@param: Type`.

### Exemple Classique : Échange de deux variables (`Permuter`)

```algo
Procédure Echanger(@a: Entier, @b: Entier)
DEBUT
  aux <- a
  a <- b
  b <- aux
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
aux            Entier
```

---

## Tableau Récapitulatif

| Mode | Symbole | Rôle | Impact sur la variable appelante |
|---|---|---|---|
| **Par Valeur** | Aucun (`x: Entier`) | Donnée d'entrée (consultation) | Aucun impact |
| **Par Référence** | `@` (`@x: Entier`) | Donnée de sortie ou entrée/sortie | Modifiée directement |

---

## Portée : Globale vs Locale

* **Variables Globales** (déclarées dans le **TDOG**) : Accessibles partout dans l'algorithme principal.
* **Variables Locales** (déclarées dans le **TDOL**) : Strictement isolées à l'intérieur du sous-programme où elles sont déclarées.
