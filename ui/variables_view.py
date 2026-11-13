"""
Variables Inspector Panel (Thonny style).
Displays variable names, algorithmic types, scopes (Global and Subprograms), and runtime values.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from ui.components import AppSelect


class VariablesView(QWidget):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._all_variables = []
        self._current_values = {}
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

        # Scope filter dropdown
        self.scope_filter = AppSelect(
            items=["Toutes les portées"],
            fixed_height=24,
            min_width=150,
            compact=True,
            is_dark=self.is_dark,
            on_changed=self._on_scope_filter_changed,
        )
        header.addWidget(self.scope_filter)

        self.btn_clear = QPushButton("Réinitialiser")
        self.btn_clear.setFixedHeight(24)
        self.btn_clear.clicked.connect(self.clear_variables)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # Table: 4 columns: Nom | Type Algorithmique | Portée | Valeur
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nom", "Type Algorithmique", "Portée", "Valeur"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
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
            self.btn_clear.setStyleSheet(
                "QPushButton { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 2px 8px; }"
                "QPushButton:hover { background-color: #313244; }"
            )
        else:
            self.table.setStyleSheet(
                "QTableWidget { background-color: #ffffff; alternate-background-color: #f8fafc; color: #1e293b; border: 1px solid #e2e8f0; }"
                "QHeaderView::section { background-color: #f1f5f9; color: #0f172a; padding: 4px; border: 1px solid #e2e8f0; }"
            )
            self.btn_clear.setStyleSheet(
                "QPushButton { background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 8px; }"
                "QPushButton:hover { background-color: #e2e8f0; }"
            )
        self.scope_filter.set_dark_mode(is_dark)

        self._render_table()

    def update_declared_variables(self, declared_objects):
        """
        Populates initial list from declared objects/variables.
        declared_objects can be:
        - a list of dicts: [{'name': ..., 'type': ..., 'scope': ..., 'scope_display': ..., 'value': ...}, ...]
        - a dict: {name: type} (legacy fallback)
        """
        self._all_variables = []
        if isinstance(declared_objects, list):
            self._all_variables = list(declared_objects)
        elif isinstance(declared_objects, dict):
            for name, typ in declared_objects.items():
                val_str = self._default_val_for_type(typ)
                self._all_variables.append({
                    'name': name,
                    'type': typ,
                    'scope': 'Globale',
                    'scope_display': 'Globale',
                    'value': val_str
                })

        # Update scope filter dropdown
        cur_filter = self.scope_filter.currentText()
        scopes = []
        seen = set()
        for item in self._all_variables:
            sc = item.get('scope', 'Globale')
            if sc and sc not in seen:
                seen.add(sc)
                scopes.append(sc)

        self.scope_filter.blockSignals(True)
        self.scope_filter.clear()
        self.scope_filter.addItem("Toutes les portées")
        if "Globale" in scopes:
            self.scope_filter.addItem("Globale")
        for sc in scopes:
            if sc != "Globale":
                self.scope_filter.addItem(sc)

        idx = self.scope_filter.findText(cur_filter)
        if idx >= 0:
            self.scope_filter.setCurrentIndex(idx)
        else:
            self.scope_filter.setCurrentIndex(0)
        self.scope_filter.blockSignals(False)

        self._render_table()

    def _on_scope_filter_changed(self):
        self._render_table()

    def _render_table(self):
        self.table.setRowCount(0)
        selected_scope = self.scope_filter.currentText()
        if selected_scope == "Toutes les portées":
            selected_scope = None

        row = 0
        for var in self._all_variables:
            scope = var.get('scope', 'Globale')
            if selected_scope and scope.lower() != selected_scope.lower():
                continue

            name = var.get('name', '')
            typ = var.get('type', '')
            scope_disp = var.get('scope_display') or scope
            
            # Use current runtime value if set, else initial value
            val_str = self._current_values.get(name.lstrip('@'), var.get('value', '-'))

            self.table.insertRow(row)

            # 1. Nom
            item_name = QTableWidgetItem(name)
            item_name.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            item_name.setForeground(QColor("#3182ce" if not self.is_dark else "#89b4fa"))

            # 2. Type Algorithmique
            item_type = QTableWidgetItem(typ)
            item_type.setForeground(QColor("#b45309" if not self.is_dark else "#fab387"))

            # 3. Portée
            item_scope = QTableWidgetItem(scope_disp)
            if scope.lower() == 'globale':
                item_scope.setForeground(QColor("#475569" if not self.is_dark else "#9399b2"))
            else:
                item_scope.setForeground(QColor("#0891b2" if not self.is_dark else "#74c7ec"))

            # 4. Valeur
            item_val = QTableWidgetItem(str(val_str))
            item_val.setForeground(QColor("#047857" if not self.is_dark else "#a6e3a1"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_type)
            self.table.setItem(row, 2, item_scope)
            self.table.setItem(row, 3, item_val)
            row += 1

    def update_variable_values(self, values_dict: dict):
        """Updates values of variables based on runtime state."""
        self._current_values.update(values_dict)
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if name_item:
                clean_name = name_item.text().lstrip('@')
                if clean_name in values_dict:
                    val = values_dict[clean_name]
                    val_item = self.table.item(row, 3)
                    if val_item:
                        val_item.setText(str(val))

    def clear_variables(self):
        """Resets values to initial defaults."""
        self._current_values.clear()
        self._render_table()

    def _default_val_for_type(self, typ: str) -> str:
        from compiler.symbol_extractor import get_default_val
        return get_default_val(typ)
