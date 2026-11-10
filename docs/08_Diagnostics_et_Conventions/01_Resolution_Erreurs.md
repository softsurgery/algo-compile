# 1. Guide de Résolution des Erreurs Courantes

Ce guide récapitule les erreurs de compilation et d'exécution les plus courantes et la façon de les corriger rapidement.

---

## 1. Erreur d'Indentation (`IndentationError`)

* **Cause** : Les lignes situées à l'intérieur d'un bloc (`DEBUT`, `Alors`, `Faire`) ne sont pas alignées de manière cohérente.
* **Solution** : Utilisez 2 ou 4 espaces pour décaler le contenu des blocs. Ne mélangez pas tabulations et espaces.

---

## 2. Tableau de Déclaration Manquant (`TDOG` ou `TDOL`)

* **Cause** : L'algorithme principal n'a pas de TDOG sous son `FIN`, ou un sous-programme n'a pas son TDOL.
* **Solution** : Ajoutez le tableau adéquat avec son en-tête complet :
```algo
Tableau de déclaration des objets globaux
Objet          Type / Nature
n              Entier
```

---

## 3. Variable Non Déclarée (`NameError` ou non déclaré)

* **Cause** : Une variable est utilisée dans le code mais n'a pas été déclarée dans la table d'objets correspondante.
* **Solution** : Ajoutez la variable dans le TDOG (pour le corps principal) ou dans le TDOL (pour le sous-programme).

---

## 4. Mot-clé `FIN` Manquant

* **Cause** : L'algorithme ou un sous-programme n'a pas de `FIN` de clôture, ou une structure (`Si`, `Pour`, `Tant que`, `Selon`) n'est pas refermée (`FinSi`, `Fin Pour`, `Fin Tant que`, `Fin Selon`).
* **Solution** : Assurez-vous que chaque ouverture de structure possède sa fermeture explicite.

---

## 5. Mauvais Symbole d'Affectation

* **Cause** : Utilisation du signe `=` pour affecter une valeur au lieu de `<-` ou `←`.
* **Solution** : En algorithmique, `=` teste l'égalité. L'affectation s'écrit `x <- 10` ou `x ← 10`.
