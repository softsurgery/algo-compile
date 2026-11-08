"""
Tableau de Déclaration des Objets (T.D.O.) Inspector.
Complies with 'Convention Algorithmique 2024' section A & B.4.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor


class TDOView(QWidget):
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
        title = QLabel("Tableau de Déclaration des Objets (T.D.O.)")
        title.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Objet", "Type / Nature", "Équivalent Python (2024/2025)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        font = QFont("JetBrains Mono", 10)
        font.setStyleHint(QFont.Monospace)
        self.table.setFont(font)

        layout.addWidget(self.table, 1)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        if is_dark:
            self.table.setStyleSheet(
                "QTableWidget { background-color: #11111b; alternate-background-color: #181825; color: #cdd6f4; border: 1px solid #313244; }"
                "QHeaderView::section { background-color: #181825; color: #89b4fa; padding: 4px; border: 1px solid #313244; }"
            )
        else:
            self.table.setStyleSheet(
                "QTableWidget { background-color: #ffffff; alternate-background-color: #f8fafc; color: #1e293b; border: 1px solid #e2e8f0; }"
                "QHeaderView::section { background-color: #f1f5f9; color: #0f172a; padding: 4px; border: 1px solid #e2e8f0; }"
            )

    def update_tdo(self, declared_objects: dict):
        self.table.setRowCount(0)
        row = 0
        for name, typ in declared_objects.items():
            self.table.insertRow(row)

            item_obj = QTableWidgetItem(name)
            item_obj.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            item_obj.setForeground(QColor("#2563eb" if not self.is_dark else "#89b4fa"))

            item_type = QTableWidgetItem(typ)
            item_type.setForeground(QColor("#d97706" if not self.is_dark else "#fab387"))

            # Explanation of python implementation
            py_equiv = self._get_python_equivalent(typ)
            item_py = QTableWidgetItem(py_equiv)
            item_py.setForeground(QColor("#059669" if not self.is_dark else "#a6e3a1"))

            self.table.setItem(row, 0, item_obj)
            self.table.setItem(row, 1, item_type)
            self.table.setItem(row, 2, item_py)
            row += 1

    def _get_python_equivalent(self, typ: str) -> str:
        t = typ.lower()
        if 'tableau' in t:
            if '*' in t or 'lignes' in t:
                return "from numpy import array; array([[...]*C]*L)"
            return "from numpy import array; array([...]*N)"
        elif 'enregistrement' in t:
            return "dict(champ1=..., champ2=...)"
        elif 'fichier' in t:
            if 'texte' in t:
                return "open(..., 'r'/'w'/'a')"
            return "open(..., 'rb'/'wb'/'ab') + pickle load/dump"
        elif 'entier' in t:
            return "int"
        elif 'réel' in t or 'reel' in t:
            return "float"
        elif 'bool' in t:
            return "bool (True / False)"
        elif 'caractère' in t or 'caractere' in t or 'chaîne' in t or 'chaine' in t:
            return "str"
        return "Objet Python dynamique"
