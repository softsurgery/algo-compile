"""
Runtime library for the Algorithmic Language.
Provides standard predefined functions and helpers.
"""

import math
import random
import pickle
import sys

# Numpy array
try:
    from numpy import array
except ImportError:
    array = list

# Math and Random helpers
sqrt = math.sqrt
randint = random.randint

# Boolean aliases
Vrai = True
Faux = False
vrai = True
faux = False

def Arrondi(x):
    """Retourne l'entier le plus proche de x."""
    return round(float(x))

def RacineCarré(x):
    """Retourne la racine carrée d'un nombre positif x."""
    return math.sqrt(float(x))

RacineCarre = RacineCarré

def Aléa(vi, vf):
    """Retourne un entier aléatoire de l'intervalle [vi, vf]."""
    return random.randint(int(vi), int(vf))

Alea = Aléa

def Ent(x):
    """Retourne la partie entière de x."""
    return int(x)

def Abs(x):
    """Retourne la valeur absolue de x."""
    return abs(x)

def Ord(c):
    """Retourne le code ASCII du caractère c."""
    return ord(str(c)[0]) if len(str(c)) > 0 else 0

def Chr(d):
    """Retourne le caractère dont le code ASCII est d."""
    return chr(int(d))

def Long(ch):
    """Retourne le nombre de caractères de la chaîne ch."""
    return len(str(ch))

def Pos(ch1, ch2):
    """Retourne la première position de ch1 dans ch2, sinon -1."""
    return str(ch2).find(str(ch1))

def Convch(x):
    """Retourne la conversion d'un nombre en chaîne de caractères."""
    return str(x)

def Estnum(ch):
    """Retourne Vrai si la chaîne est convertible en numérique, sinon Faux."""
    s = str(ch).strip()
    if not s:
        return False
    if s.isdigit():
        return True
    try:
        float(s)
        return True
    except ValueError:
        return False

def Valeur(ch):
    """Retourne la conversion d'une chaîne en valeur numérique."""
    s = str(ch).strip()
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return 0

def Sous_chaine(ch, d, f):
    """Retourne une sous-chaîne de d à f (f exclue)."""
    return str(ch)[int(d):int(f)]

def Effacer(ch, d, f):
    """Retourne la chaîne après suppression des caractères de d à f (f exclue)."""
    s = str(ch)
    return s[:int(d)] + s[int(f):]

def Majus(ch):
    """Retourne l'équivalent de la chaîne en majuscule."""
    return str(ch).upper()

# Record helper (allows both dot access E.nom and dict access E['nom'])
class Enregistrement(dict):
    """Dictionnaire compatible enregistrement (accès E.champ ou E['champ'])."""
    def __getattr__(self, key):
        if key in self:
            return self[key]
        if key.startswith('_'):
            raise AttributeError(key)
        return self.get(key, 0)
    
    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        val = super().get(key, None)
        return val if val is not None else 0

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.items())
        return f"dict({fields})"

# Smart input helper
def _lire_valeur(prompt="", var_type=None):
    """Reads input from user and converts it according to type or smart heuristic."""
    val = input(prompt)
    if var_type is not None:
        t = var_type.lower()
        if 'chaine' in t or 'chaîne' in t or 'str' in t:
            return val
        elif 'caractere' in t or 'caractère' in t or 'char' in t:
            return val[0] if len(val) > 0 else ''
        elif 'entier' in t or 'int' in t:
            try:
                return int(val.strip())
            except ValueError:
                return 0
        elif 'reel' in t or 'réel' in t or 'float' in t:
            try:
                return float(val.strip())
            except ValueError:
                return 0.0
        elif 'bool' in t:
            v = val.strip().lower()
            return v in ('vrai', 'true', '1', 't', 'o', 'oui')
        else:
            return val
    # Smart auto-detection if no explicit type
    val_trimmed = val.strip()
    if val_trimmed.isdigit() or (val_trimmed.startswith(('-', '+')) and val_trimmed[1:].isdigit()):
        return int(val_trimmed)
    try:
        f = float(val_trimmed)
        return f
    except ValueError:
        pass
    if val_trimmed.lower() in ('vrai', 'true'):
        return True
    if val_trimmed.lower() in ('faux', 'false'):
        return False
    return val

# File helpers
def _fin_fichier(f):
    """Vérifie si le fichier est à la fin."""
    try:
        pos = f.tell()
        line = f.readline()
        f.seek(pos)
        return len(line) == 0
    except Exception:
        return True
