"""
Quick Algorithmic Symbols & Snippets Insertion Bar.
Allows one-click insertion of official algorithmic symbols:
←, ≠, ≤, ≥, , [vi .. vf], {..}, Div, Mod, Si..Alors, etc.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal


class SymbolsBar(QWidget):
    insert_requested = pyqtSignal(str)

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        lbl = QLabel("Symboles :")
        lbl.setStyleSheet("font-weight: bold; color: #64748b; font-size: 11px;")
        layout.addWidget(lbl)

        # Essential mathematical & algorithmic symbols
        symbols = [
            ("←", "←", "Affectation (ou <-)"),
            ("≠", "≠", "Différent (ou <>)"),
            ("≤", "≤", "Inférieur ou égal"),
            ("≥", "≥", "Supérieur ou égal"),
            ("∈", " ∈ ", "Appartient à un intervalle ou ensemble ()"),
            ("[ .. ]", "[vi .. vf]", "Intervalle de valeurs [vi .. vf]"),
            ("{ .. }", "{v1, v2, v3}", "Ensemble de valeurs {v1, v2, v3}"),
            ("Div", " Div ", "Division entière (//)"),
            ("Mod", " Mod ", "Reste division entière (%)"),
        ]

        for label, text_to_insert, tooltip in symbols:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(26)
            btn.setMinimumWidth(32)
            btn.setStyleSheet(
                "QPushButton { font-weight: bold; padding: 2px 6px; border-radius: 4px; }"
            )
            btn.clicked.connect(lambda _, t=text_to_insert: self.insert_requested.emit(t))
            layout.addWidget(btn)

        # Snippet separator
        sep = QLabel("|")
        sep.setStyleSheet("color: #cbd5e1; margin: 0 4px;")
        layout.addWidget(sep)

        lbl_snip = QLabel("Structures :")
        lbl_snip.setStyleSheet("font-weight: bold; color: #64748b; font-size: 11px;")
        layout.addWidget(lbl_snip)

        snippets = [
            ("Si..Alors", "Si condition Alors\n    \nFinSi", "Insérer Si ... FinSi"),
            ("Pour..Faire", "Pour i de 0 à n - 1 Faire\n    \nFin Pour", "Insérer boucle Pour"),
            ("Tant que", "Tant que condition Faire\n    \nFin Tant que", "Insérer boucle Tant que"),
            ("Répéter", "Répéter\n    \nJusqu'à condition", "Insérer boucle Répéter"),
            ("Selon", "Selon sélecteur\n    1 : \n    Sinon \nFin Selon", "Insérer Selon"),
            ("TDO", "Déclaration des objets\nObjet          Type / Nature\n", "Insérer section TDO"),
        ]

        for label, text_to_insert, tooltip in snippets:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "QPushButton { font-size: 11px; padding: 2px 6px; border-radius: 4px; }"
            )
            btn.clicked.connect(lambda _, t=text_to_insert: self.insert_requested.emit(t))
            layout.addWidget(btn)

        layout.addStretch()
