"""
Assistant & Convention Guide View (Thonny style).
Provides contextual error diagnostics and reference cards directly from
'Convention Algorithmique 2024.pdf' and 'Implémention 2024-2025.pdf'.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QComboBox, QLabel
)
from PyQt5.QtGui import QFont


REFERENCE_TOPICS = {
    "1. Structure Générale & TDO": """
<h3>Forme générale d'un algorithme (2024/2025)</h3>
<pre>
ALGORITHME Nom
DEBUT
  Traitements...
FIN
Déclaration des objets
Objet          Type / Nature
n, s, i        Entier
T              Tableau de 20 Entier
</pre>
<b>Règles d'or :</b>
<ul>
  <li>L'écriture de l'algorithme doit respecter l'indentation.</li>
  <li>La nomenclature des objets doit être significative.</li>
  <li>L'indice du premier élément d'une chaîne ou d'un tableau est <b>0</b>.</li>
</ul>
""",

    "2. Opérations Élémentaires (I/O & Affectation)": """
<h3>Opérations Élémentaires</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <tr style="background-color: #f1f5f9;"><th>Algorithmique</th><th>Python (2024/2025)</th><th>Description</th></tr>
  <tr><td><b>Lire(x)</b></td><td><code>x = input()</code> ou <code>int(input())</code></td><td>Saisie clavier</td></tr>
  <tr><td><b>Écrire("msg", x)</b></td><td><code>print("msg", x, end='')</code></td><td>Affichage sans saut de ligne</td></tr>
  <tr><td><b>Écrire_nl("msg", x)</b></td><td><code>print("msg", x)</code></td><td>Affichage avec saut de ligne</td></tr>
  <tr><td><b>x &larr; expr</b> ou <b>x &lt;- expr</b></td><td><code>x = expr</code></td><td>Affectation</td></tr>
</table>
""",

    "3. Structures Conditionnelles (Si & Selon)": """
<h3>Structures Conditionnelles</h3>
<h4>1. Si Simple et Complet</h4>
<pre>
Si Condition Alors
  Traitement1
Sinon
  Traitement2
FinSi
</pre>
<h4>2. Selon (Choix multiples & Intervalles)</h4>
<pre>
Selon &lt;Sélecteur&gt;
  1, 2, 3 : Traitement1
  10 .. 20 : Traitement2
  Sinon TraitementParDefaut
Fin Selon
</pre>
<i>En Python 3.10+, le Selon est implémenté via <code>match / case</code>.</i>
""",

    "4. Structures Itératives (Pour, Tant que, Répéter)": """
<h3>Structures Itératives (Boucles)</h3>
<h4>1. Pour (Itération complète)</h4>
<pre>
Pour i de Début à Fin [Pas = valeur_pas] Faire
  Traitement
Fin Pour
</pre>
<i>Python : <code>for i in range(Début, Fin + 1, Pas):</code></i>

<h4>2. Tant que (Condition d'entrée)</h4>
<pre>
Tant que Condition Faire
  Traitement
Fin Tant que
</pre>

<h4>3. Répéter (Condition de sortie)</h4>
<pre>
Répéter
  Traitement
Jusqu'à Condition
</pre>
""",

    "5. Modules (Fonctions & Procédures)": """
<h3>Modules et Sous-programmes</h3>
<h4>1. Fonction (retourne une valeur simple)</h4>
<pre>
Fonction Somme(a: Entier, b: Entier) : Entier
DEBUT
  Retourner a + b
FIN
</pre>

<h4>2. Procédure & Passage par référence (@)</h4>
<pre>
Procédure Echanger(@x: Entier, @y: Entier)
DEBUT
  aux &larr; x
  x &larr; y
  y &larr; aux
FIN
</pre>
<i>Le symbole <b>@</b> devant un paramètre indique le mode de passage par référence (adresse).</i>
""",

    "6. Tableaux & Enregistrements": """
<h3>Tableaux & Enregistrements</h3>
<h4>1. Tableaux Numpy (1D & 2D)</h4>
<p>Les tableaux sont implémentés avec <code>numpy.array</code> statiques et homogènes :</p>
<pre>
T = array([0] * N)                # 1D Entiers
T = array([0.0] * N)              # 1D Réels
T = array([''] * N, dtype='U20')  # 1D Chaînes
M = array([[0] * C] * L)          # 2D Matrice
</pre>
<p>Accès 1D : <code>T[i]</code> | Accès 2D : <code>M[i, j]</code></p>

<h4>2. Enregistrements (Dictionnaires)</h4>
<pre>
E = dict(nom="", age=0)
E['nom'] = "Karim"
</pre>
""",

    "7. Fonctions Prédéfinies": """
<h3>Tableau des Fonctions Prédéfinies</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
  <tr style="background-color: #f1f5f9;"><th>Fonction Algo</th><th>Python</th><th>Rôle</th></tr>
  <tr><td><b>Arrondi(x)</b></td><td><code>round(x)</code></td><td>Entier le plus proche</td></tr>
  <tr><td><b>RacineCarré(x)</b></td><td><code>sqrt(x)</code></td><td>Racine carrée (math.sqrt)</td></tr>
  <tr><td><b>Aléa(vi, vf)</b></td><td><code>randint(vi, vf)</code></td><td>Entier aléatoire [vi, vf]</td></tr>
  <tr><td><b>Ent(x)</b></td><td><code>int(x)</code></td><td>Partie entière</td></tr>
  <tr><td><b>Abs(x)</b></td><td><code>abs(x)</code></td><td>Valeur absolue</td></tr>
  <tr><td><b>Ord(c)</b></td><td><code>ord(c)</code></td><td>Code ASCII</td></tr>
  <tr><td><b>Chr(d)</b></td><td><code>chr(d)</code></td><td>Caractère depuis code ASCII</td></tr>
  <tr><td><b>Long(ch)</b></td><td><code>len(ch)</code></td><td>Longueur chaîne</td></tr>
  <tr><td><b>Pos(ch1, ch2)</b></td><td><code>ch2.find(ch1)</code></td><td>Position (-1 si absente)</td></tr>
  <tr><td><b>Convch(x)</b></td><td><code>str(x)</code></td><td>Nombre vers chaîne</td></tr>
  <tr><td><b>Estnum(ch)</b></td><td><code>ch.isdecimal()</code></td><td>Vrai si chaîne numérique</td></tr>
  <tr><td><b>Valeur(ch)</b></td><td><code>int(ch) / float(ch)</code></td><td>Chaîne vers nombre</td></tr>
  <tr><td><b>Sous_chaine(ch, d, f)</b></td><td><code>ch[d:f]</code></td><td>Sous-chaîne (f exclue)</td></tr>
  <tr><td><b>Effacer(ch, d, f)</b></td><td><code>ch[:d] + ch[f:]</code></td><td>Suppression de d à f</td></tr>
  <tr><td><b>Majus(ch)</b></td><td><code>ch.upper()</code></td><td>Conversion en majuscules</td></tr>
</table>
""",

    "8. Opérateurs & Ensembles": """
<h3>Opérateurs et Notations Spéciales</h3>
<ul>
  <li><b>Arithmétique :</b> <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>, <code>Div</code> (//), <code>Mod</code> (%)</li>
  <li><b>Logique :</b> <code>Non</code> (not), <code>Et</code> (and), <code>Ou</code> (or)</li>
  <li><b>Comparaison :</b> <code>=</code> (==), <code>≠</code> ou <code>&lt;&gt;</code> (!=), <code>&le;</code> (&lt;=), <code>&ge;</code> (&gt;=)</li>
  <li><b>Appartenance Intervalle :</b> <code>x &isin; [vi .. vf]</code> &rarr; <code>vi &le; x &le; vf</code></li>
  <li><b>Appartenance Ensemble :</b> <code>x &isin; {v1, v2, v3}</code> &rarr; <code>x in {v1, v2, v3}</code></li>
</ul>
"""
}


class AssistantView(QWidget):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._setup_ui()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)
        lbl = QLabel("Sujet de référence :")
        lbl.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(lbl)

        self.topic_combo = QComboBox()
        self.topic_combo.addItems(list(REFERENCE_TOPICS.keys()))
        self.topic_combo.currentIndexChanged.connect(self._on_topic_changed)
        header.addWidget(self.topic_combo, 1)

        layout.addLayout(header)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser, 1)

        self._show_topic(self.topic_combo.currentText())

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        bg = "#11111b" if is_dark else "#ffffff"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        border = "#313244" if is_dark else "#e2e8f0"
        self.browser.setStyleSheet(f"QTextBrowser {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 4px; padding: 8px; }}")
        self._show_topic(self.topic_combo.currentText())

    def _on_topic_changed(self, idx):
        self._show_topic(self.topic_combo.itemText(idx))

    def _show_topic(self, topic_title):
        content = REFERENCE_TOPICS.get(topic_title, "")
        header_color = "#3b82f6" if not self.is_dark else "#89b4fa"
        bg_pre = "#f1f5f9" if not self.is_dark else "#181825"
        text_color = "#0f172a" if not self.is_dark else "#cdd6f4"

        html = f"""
        <style>
          body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: {text_color}; }}
          h3 {{ color: {header_color}; margin-top: 4px; }}
          h4 {{ color: {header_color}; margin-bottom: 4px; }}
          pre {{ background-color: {bg_pre}; padding: 8px; border-radius: 4px; font-family: "JetBrains Mono", Consolas, monospace; }}
          code {{ font-family: "JetBrains Mono", Consolas, monospace; background-color: {bg_pre}; padding: 2px 4px; border-radius: 3px; }}
        </style>
        {content}
        """
        self.browser.setHtml(html)

    def show_error_advice(self, error_message: str, line_no: int = None):
        """Displays helpful advice when an error occurs."""
        title = "Diagnostic & Aide"
        err_color = "#dc2626" if not self.is_dark else "#f38ba8"
        bg_pre = "#f1f5f9" if not self.is_dark else "#181825"

        tips = []
        low = error_message.lower()
        if "indent" in low:
            tips.append("Vérifiez l'indentation de vos blocs (après Alors, Faire, DEBUT).")
        if "nameerror" in low or "not defined" in low:
            tips.append("Assurez-vous que l'objet est bien déclaré dans la section <b>Déclaration des objets (TDO)</b>.")
        if "syntaxerror" in low:
            tips.append("Vérifiez la concordance des mots clés (ex: <code>Si ... FinSi</code>, <code>Pour ... Fin Pour</code>).")
            tips.append("Vérifiez que le symbole d'affectation est bien <code>&larr;</code> ou <code>&lt;-</code>.")
        if not tips:
            tips.append("Consultez les fiches de référence ci-dessus pour la syntaxe exacte selon la Convention 2024.")

        tips_html = "".join(f"<li>{t}</li>" for t in tips)
        html = f"""
        <h3 style="color: {err_color};">Erreur détectée {"à la ligne " + str(line_no) if line_no else ""}</h3>
        <pre style="background: {bg_pre}; color: {err_color};">{error_message}</pre>
        <h4>Conseils de l'assistant :</h4>
        <ul>{tips_html}</ul>
        """
        self.browser.setHtml(html)
