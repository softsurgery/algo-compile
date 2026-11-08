"""
Variables Inspector Panel (Thonny style).
Displays variable names, algorithmic types, and values.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class VariablesView(QWidget):
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
        title = QLabel("Variables & État")
        title.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.btn_clear = QPushButton("Réinitialiser")
        self.btn_clear.setFixedHeight(24)
        self.btn_clear.clicked.connect(self.clear_variables)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # Table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom", "Type Algorithmique", "Valeur"])
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

    def update_declared_variables(self, declared_objects: dict):
        """Populates initial list from declared objects."""
        self.table.setRowCount(0)
        row = 0
        for name, typ in declared_objects.items():
            self.table.insertRow(row)

            item_name = QTableWidgetItem(name)
            item_name.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            item_name.setForeground(QColor("#3182ce" if not self.is_dark else "#89b4fa"))

            item_type = QTableWidgetItem(typ)
            item_type.setForeground(QColor("#b45309" if not self.is_dark else "#fab387"))

            # Determine placeholder initial value
            val_str = "-"
            t_lower = typ.lower()
            if 'entier' in t_lower:
                val_str = "0"
            elif 'réel' in t_lower or 'reel' in t_lower:
                val_str = "0.0"
            elif 'bool' in t_lower:
                val_str = "Faux"
            elif 'caractere' in t_lower or 'chaine' in t_lower:
                val_str = "''"
            elif 'tableau' in t_lower:
                val_str = "[...]"
            elif 'enregistrement' in t_lower:
                val_str = "{...}"

            item_val = QTableWidgetItem(val_str)
            item_val.setForeground(QColor("#047857" if not self.is_dark else "#a6e3a1"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_type)
            self.table.setItem(row, 2, item_val)
            row += 1

    def update_variable_values(self, values_dict: dict):
        """Updates values of variables based on runtime state."""
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if name_item and name_item.text() in values_dict:
                val = values_dict[name_item.text()]
                val_item = self.table.item(row, 2)
                if val_item:
                    val_item.setText(str(val))

    def clear_variables(self):
        self.table.setRowCount(0)
