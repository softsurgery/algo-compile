# 3. Boucle à Condition d'Arrêt (Répéter ... Jusqu'à)

La structure `Répéter ... Jusqu'à` exécute le corps de la boucle **au moins une fois**, puis vérifie la condition d'arrêt à la fin.

---

## Syntaxe Générale

```algo
Répéter
  // Instructions (exécutées au moins une fois)
Jusqu'à <Condition_d_arret>
```

---

## Règle de Sortie

* La répétition **continue tant que la condition est FAUSSE**.
* La répétition **s'arrête dès que la condition devient VRAIE**.

---

## Exemple : Contrôle de Saisie (Validation d'entrée)

```algo
Répéter
  Ecrire("Donner une note comprise entre 0 et 20 : ")
  Lire(note)
Jusqu'à (note >= 0) Et (note <= 20)

Ecrire_nl("Note validée : ", note)
```

---

## Correspondance Python

Python ne disposant pas d'instruction native `do ... until`, le compilateur génère une boucle infinie `while True:` avec une clause de rupture conditionnelle inversée :

```python
while True:
    # Instructions
    if condition_d_arret:
        break
```
