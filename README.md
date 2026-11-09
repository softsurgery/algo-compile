# Algoo

Environnement de Développement Intégré (IDE) moderne développé par **[softsurgery](https://github.com/softsurgery)** avec **PyQt 5**, inspiré de l'ergonomie pédagogique de **Thonny**, spécialement conçu pour compiler et exécuter les algorithmes éducatifs.

🔗 **Dépôt GitHub :** [https://github.com/softsurgery/algoo](https://github.com/softsurgery/algoo)

---

## Fonctionnalités Clés

### 1. Interface Moderne et Ergonomique (Inspirée de Thonny)
- **Barre d'outils ergonomique :** Boutons iconographiques larges et modernes pour `Nouveau`, `Ouvrir`, `Enregistrer`, `Exécuter` (Vert F5), `Traduire en Python` (Bleu/Or F6), `Arrêter` (Rouge Échap), menu déroulant `Exemples Bac` et bascule `Thème Clair / Sombre`.
- **Barre d'insertion rapide de symboles algorithmiques :** Insertion en un clic des symboles algorithmiques usuels (`←`, `≠`, `≤`, `≥`, `∈`, `[vi .. vf]`, `{..}`, `Div`, `Mod`) ainsi que des blocs de structures conditionnelles et itératives.
- **Éditeur d'algorithmes multi-onglets :**
  - Numérotation des lignes avec surbrillance de la ligne active.
  - Coloration syntaxique complète pour les algorithmes (mots-clés, types simples et structurés, fonctions prédéfinies, opérateurs, chaînes et commentaires).
  - Indentation automatique intelligente après `DEBUT`, `Alors`, `Sinon`, `Faire`, `Selon`, `Répéter`.
  - Signalement visuel des erreurs à la ligne exacte.
- **Console / Shell Interactive (Bas de page) :**
  - Exécution asynchrone non bloquante via `QProcess` (l'interface ne gèle jamais).
  - Gestion interactive native de l'opération d'entrée `Lire(x)` via la zone de commande `>>>`.
  - Affichage en couleurs (Sorties standards, invites en bleu, saisies en violet, erreurs en rouge).
  - Arrêt forcé instantané en cas de boucle infinie.

### 2. Panneau Latéral Multifonctionnel
- **Code Python généré :** Affichage en temps réel du code Python 3 traduit selon les règles d'implémentation (utilisation de `numpy.array`, dictionnaires pour les enregistrements, `match/case` pour les Selon, imports modulaires, conversions automatiques). Possibilité de copier le code ou de l'exporter en `.py`.
- **Inspecteur de Variables :** Affichage tabulaire des variables actives, leurs types algorithmiques et leurs valeurs.
- **Tableau T.D.O. :** Visualisation et analyse automatique du Tableau de Déclaration des Objets (Objets, Types/Natures, et équivalences Python).
- **Assistant & Guide :** Fiches de synthèse et aide-mémoire avec conseils pédagogiques automatiques lors d'erreurs de syntaxe ou d'exécution.

---

## Équivalences Algorithme et Python

| Syntaxe Algorithmique | Implémentation Python |
|-----------------------------|---------------------------------|
| `Lire(x)` | `x = input()` / conversion selon le type TDO |
| `Écrire(...)` | `print(..., end='')` |
| `Écrire_nl(...)` | `print(...)` |
| `x ← expr` ou `x <- expr` | `x = expr` |
| `Tableau de N Entier` | `array([0] * N)` (`from numpy import array`) |
| `Tableau de N lignes * M colonnes` | `array([[0] * M] * N)` |
| `Enregistrement` | `dict(champ1=..., champ2=...)` et accès `E['champ']` |
| `Selon <Sélecteur>` | `match Sélecteur : case ...` (Python 3.10+) |
| `Pour i de début à fin [Pas=p]` | `for i in range(début, fin + 1, pas):` |
| `Tant que <cond> Faire` | `while <cond>:` |
| `Répéter ... Jusqu'à <cond>` | `while True: ... if <cond>: break` |
| `Fonction Nom(...) : Type` | `def Nom(...): ... return résultat` |
| `Procédure Nom(@p1, ...)` | `def Nom(p1, ...):` (gestion passage par adresse) |
| `Div`, `Mod`, `Et`, `Ou`, `Non` | `//`, `%`, `and`, `or`, `not` |
| `≠`, `≤`, `≥`, `∈ [a .. b]` | `!=`, `<=`, `>=`, `a <= x <= b` |
| `Arrondi`, `RacineCarré`, `Aléa` | `round()`, `sqrt()`, `randint()` |
| `Long`, `Pos`, `Sous_chaine` | `len()`, `ch.find()`, `ch[d:f]` |
| `Effacer`, `Majus`, `Valeur` | `ch[:d] + ch[f:]`, `ch.upper()`, `int(ch)/float(ch)` |

---

## Lancement de l'Application

Assurez-vous que PyQt5 et NumPy sont installés :

```bash
python3 main.py
```

### Exécuter les tests unitaires du compilateur :

```bash
python3 -m unittest discover tests
```

---

## Exemples Inclus

Les exemples suivants sont intégrés dans le menu **Exemples Bac** :
1. `somme_diviseurs.algo` : Recherche d'un nombre parfait (boucle Pour, Div, Mod).
2. `tri_bulles.algo` : Tri à bulles avec tableaux NumPy 1D et nombres aléatoires (`Aléa`).
3. `palindrome.algo` : Sous-programme (Fonction), manipulation de chaînes (`Long`, `Majus`) et boucle `Tant que`.
4. `matrice_alea.algo` : Tableaux NumPy 2D (lignes * colonnes) et parcours imbriqué.
5. `gestion_eleves.algo` : Enregistrement (`dict`) et structure à choix multiples (`Selon`).

---

## Auteur & Contribution

- **Développeur :** [softsurgery](https://github.com/softsurgery)
- **Dépôt du projet :** [https://github.com/softsurgery/algoo](https://github.com/softsurgery/algoo)
