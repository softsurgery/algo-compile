# 5. Ensembles et Intervalles (Opérateur ∈)

L'opérateur d'appartenance `∈` (ou `dans` / `in`) permet de tester si une valeur fait partie d'un ensemble discret de valeurs ou d'un intervalle continu/discret.

---

## 1. Appartenance à un Intervalle

### Syntaxe Algo :
```algo
x ∈ [borne_inf .. borne_sup]
```

### Équivalent logique :
```algo
(x >= borne_inf) Et (x <= borne_sup)
```

### Équivalent Python généré :
```python
borne_inf <= x <= borne_sup
```

### Exemple :
```algo
Si note ∈ [10 .. 20] Alors
  Ecrire_nl("Note valide et admise")
FinSi
```

---

## 2. Appartenance à un Ensemble Discret

### Syntaxe Algo :
```algo
caractère ∈ {'a', 'e', 'i', 'o', 'u', 'y'}
```

### Équivalent Python généré :
```python
caractère in {'a', 'e', 'i', 'o', 'u', 'y'}
```

### Exemple complet :
```algo
Si c ∈ {'A' .. 'Z'} Alors
  Ecrire_nl(c, " est une lettre majuscule")
Sinon Si c ∈ {'0' .. '9'} Alors
  Ecrire_nl(c, " est un chiffre")
FinSi
```
