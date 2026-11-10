"""
Quick Algorithmic Symbols & Snippets Insertion Bar.
Allows one-click insertion of official algorithmic symbols:
LT, LTE, GT, GTE, NEQ, MOD, DIV, IN, ASSIGN, control structures, and declaration tables (TDNT, TDOG, TDOL).
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
        layout.setContentsMargins(6, 4, 6, 20)
        layout.setSpacing(4)

        self.lbl_sym = QLabel("Symboles :")
        layout.addWidget(self.lbl_sym)

        # Essential mathematical & algorithmic symbols: LT, LTE, GT, GTE, NEQ, MOD, DIV, IN, ASSIGN
        symbols = [
            ("LT", "<", "Strictement inférieur (<)"),
            ("LTE", "≤", "Inférieur ou égal (≤)"),
            ("GT", ">", "Strictement supérieur (>)"),
            ("GTE", "≥", "Supérieur ou égal (≥)"),
            ("NEQ", "≠", "Différent (≠ ou <>)"),
            ("MOD", " Mod ", "Reste division entière (Mod)"),
            ("DIV", " Div ", "Division entière (Div)"),
            ("IN", " ∈ ", "Appartient à un intervalle ou ensemble (∈)"),
            ("ASSIGN", "←", "Affectation (← ou <-)"),
        ]

        for label, text_to_insert, tooltip in symbols:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(26)
            btn.setMinimumWidth(32)
            btn.setStyleSheet(
                "QPushButton { font-weight: bold; font-size: 11px; padding: 2px 6px; border-radius: 4px; }"
            )
            btn.clicked.connect(lambda _, t=text_to_insert: self.insert_requested.emit(t))
            layout.addWidget(btn)

        # Snippet separator
        self.sep = QLabel("|")
        layout.addWidget(self.sep)

        self.lbl_snip = QLabel("Structures :")
        layout.addWidget(self.lbl_snip)

        snippets = [
            ("SI", "Si condition Alors\n    \nFinSi", "Insérer Si ... FinSi"),
            ("POUR", "Pour i de 0 à n - 1 Faire\n    \nFin Pour", "Insérer boucle Pour"),
            ("TANTQUE", "Tant que condition Faire\n    \nFin Tant que", "Insérer boucle Tant que"),
            ("REPETER", "Répéter\n    \nJusqu'à condition", "Insérer boucle Répéter"),
            ("SELON", "Selon sélecteur\n    1 : \n    Sinon \nFin Selon", "Insérer Selon"),
        ]

        for label, text_to_insert, tooltip in snippets:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "QPushButton { font-weight: bold; font-size: 11px; padding: 2px 6px; border-radius: 4px; }"
            )
            btn.clicked.connect(lambda _, t=text_to_insert: self.insert_requested.emit(t))
            layout.addWidget(btn)

        # Tables separator
        self.sep2 = QLabel("|")
        layout.addWidget(self.sep2)

        self.lbl_tables = QLabel("Tableaux :")
        layout.addWidget(self.lbl_tables)

        table_shortcuts = [
            ("TDNT", "Tableau de déclaration des nouveaux types\nType\nNomEnreg = Enregistrement\n    champ1 : Type1\n    champ2 : Type2\nFin Enregistrement\nTab = Tableau de 100 Entier\n", "Insérer TDNT (Nouveaux types / typedef : Enregistrement, Tableau)"),
            ("TDOG", "Tableau de déclaration des objets globaux\nObjet          Type / Nature\n", "Insérer TDOG (Objets globaux sous l'algorithme)"),
            ("TDOL", "Tableau de déclaration des objets locaux\nObjet          Type / Nature\n", "Insérer TDOL (Objets locaux après le sous-programme)"),
        ]

        for label, text_to_insert, tooltip in table_shortcuts:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setFixedHeight(26)
            btn.setStyleSheet(
                "QPushButton { font-weight: bold; font-size: 11px; padding: 2px 6px; border-radius: 4px; }"
            )
            btn.clicked.connect(lambda _, t=text_to_insert: self.insert_requested.emit(t))
            layout.addWidget(btn)

        layout.addStretch()
        self.set_dark_mode(self.is_dark)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        if is_dark:
            self.lbl_sym.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 11px;")
            self.sep.setStyleSheet("color: #45475a; margin: 0 4px;")
            self.lbl_snip.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 11px;")
            self.sep2.setStyleSheet("color: #45475a; margin: 0 4px;")
            self.lbl_tables.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 11px;")
        else:
            self.lbl_sym.setStyleSheet("font-weight: bold; color: #64748b; font-size: 11px;")
            self.sep.setStyleSheet("color: #cbd5e1; margin: 0 4px;")
            self.lbl_snip.setStyleSheet("font-weight: bold; color: #64748b; font-size: 11px;")
            self.sep2.setStyleSheet("color: #cbd5e1; margin: 0 4px;")
            self.lbl_tables.setStyleSheet("font-weight: bold; color: #64748b; font-size: 11px;")
