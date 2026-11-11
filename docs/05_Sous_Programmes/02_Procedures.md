# 2. Les Procédures

Une **Procédure** est un sous-programme autonome qui réalise une tâche précise sans renvoyer directement une valeur de retour scalaire. Elle peut modifier ses arguments passés par référence.

---

## Syntaxe Générale

```algo
Procédure NomProcedure(param1: Type1, @param2: Type2)
DEBUT
  // Traitement
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
/              /
```

---

## Exemple : Affichage d'une ligne d'étoiles

```algo
Procédure AfficherLigne(longueur: Entier, c: Caractère)
DEBUT
  Pour i de 1 à longueur Faire
    Ecrire(c)
  Fin Pour
  Ecrire_nl("")
FIN

Tableau de déclaration des objets locaux
Objet          Type / Nature
i              Entier
```

---

## Mode d'Appel

Une procédure s'appelle comme une **instruction indépendante** (jamais à l'intérieur d'une expression mathématique) :

```algo
ALGORITHME TestMenu
DEBUT
  AfficherLigne(30, "*")
  Ecrire_nl("          MENU PRINCIPAL")
  AfficherLigne(30, "*")
FIN

Tableau de déclaration des objets globaux
Objet          Type / Nature
AfficherLigne  Procédure
```
