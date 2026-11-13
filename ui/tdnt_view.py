"""
Tableau de Déclaration des Nouveaux Types (T.D.N.T.) Inspector.
Displays user-defined algorithmic types (Enregistrements, Tableaux 1D/2D, Alias).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class TDNTView(QWidget):
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
        title = QLabel("Tableau de Déclaration des Nouveaux Types (T.D.N.T.)")
        title.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.lbl_count = QLabel("0 types")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 10px;")
        header.addWidget(self.lbl_count)

        self.btn_clear = QPushButton("Effacer")
        self.btn_clear.setFixedHeight(24)
        self.btn_clear.clicked.connect(self.clear_tdnt)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nouveau Type", "Nature", "Définition / Structure"])
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
            self.lbl_count.setStyleSheet("color: #a6adc8; font-size: 10px;")
            self.btn_clear.setStyleSheet(
                "QPushButton { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 2px 8px; }"
                "QPushButton:hover { background-color: #313244; }"
            )
        else:
            self.table.setStyleSheet(
                "QTableWidget { background-color: #ffffff; alternate-background-color: #f8fafc; color: #1e293b; border: 1px solid #e2e8f0; }"
                "QHeaderView::section { background-color: #f1f5f9; color: #0f172a; padding: 4px; border: 1px solid #e2e8f0; }"
            )
            self.lbl_count.setStyleSheet("color: #64748b; font-size: 10px;")
            self.btn_clear.setStyleSheet(
                "QPushButton { background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 8px; }"
                "QPushButton:hover { background-color: #e2e8f0; }"
            )

    def update_tdnt(self, custom_types_data: dict):
        """
        Populates the TDNT table from custom_types dict:
        custom_types_data: { type_name: {'kind': ..., ...} }
        """
        self.table.setRowCount(0)
        if not custom_types_data:
            self.lbl_count.setText("0 types")
            return

        row = 0
        for name, t_def in custom_types_data.items():
            self.table.insertRow(row)

            # 1. Type Name
            item_name = QTableWidgetItem(str(name))
            item_name.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            item_name.setForeground(QColor("#2563eb" if not self.is_dark else "#89b4fa"))

            # 2. Nature & 3. Definition
            kind = t_def.get('kind', '').lower()
            if kind == 'enregistrement':
                nature_str = "Enregistrement"
                fields = t_def.get('fields', {})
                if fields:
                    fields_repr = " ; ".join(f"{f} : {t}" for f, t in fields.items())
                    def_str = f"Enregistrement ({fields_repr})"
                else:
                    def_str = "Enregistrement (aucun champ)"

            elif kind == 'tableau_1d':
                nature_str = "Tableau (1D)"
                size = t_def.get('size', '?')
                elem_t = t_def.get('elem_type', 'Entier')
                def_str = f"Tableau de {size} {elem_t}"

            elif kind == 'tableau_2d':
                nature_str = "Tableau (2D / Matrice)"
                rows = t_def.get('rows', '?')
                cols = t_def.get('cols', '?')
                elem_t = t_def.get('elem_type', 'Entier')
                def_str = f"Tableau de {rows} lig * {cols} col {elem_t}"

            elif kind == 'alias':
                nature_str = "Alias (Synonyme)"
                target = t_def.get('target_type', '')
                def_str = f"{target}"
            else:
                nature_str = kind.capitalize() or "Type personnalisé"
                def_str = str(t_def)

            item_nature = QTableWidgetItem(nature_str)
            item_nature.setForeground(QColor("#7c3aed" if not self.is_dark else "#cba6f7"))

            item_def = QTableWidgetItem(def_str)
            item_def.setForeground(QColor("#d97706" if not self.is_dark else "#fab387"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_nature)
            self.table.setItem(row, 2, item_def)
            row += 1

        count = len(custom_types_data)
        self.lbl_count.setText(f"{count} type{'s' if count > 1 else ''}")

    def clear_tdnt(self):
        self.table.setRowCount(0)
        self.lbl_count.setText("0 types")
