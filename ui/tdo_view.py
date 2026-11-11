"""
Tableau de Déclaration des Objets (T.D.O.) Inspector.
Displays separate declaration tables for TDOG (Global Objects) and each subprogram's
TDOL (Local Objects and Parameters).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QComboBox,
    QScrollArea, QFrame, QAbstractScrollArea
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class TDOTableCard(QWidget):
    """A distinct card widget representing one single TDOG or TDOL table."""

    def __init__(self, table_info: dict, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self.table_info = table_info
        self.is_dark = is_dark
        self._setup_ui()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 0, 8)
        layout.setSpacing(4)

        # Header banner
        self.banner = QFrame()
        self.banner.setFixedHeight(30)
        b_layout = QHBoxLayout(self.banner)
        b_layout.setContentsMargins(8, 2, 8, 2)

        kind = self.table_info.get('kind', 'tdog')
        icon_symbol = "🌐" if kind == 'tdog' else "📦"
        title_text = f"{icon_symbol} {self.table_info.get('title', 'Tableau de déclaration')}"

        self.lbl_title = QLabel(title_text)
        self.lbl_title.setFont(QFont("SansSerif", 9, QFont.Bold))
        b_layout.addWidget(self.lbl_title)
        b_layout.addStretch()

        objs = self.table_info.get('objects', [])
        count_text = f"{len(objs)} objet{'s' if len(objs) > 1 else ''}"
        self.lbl_count = QLabel(count_text)
        self.lbl_count.setFont(QFont("SansSerif", 8))
        b_layout.addWidget(self.lbl_count)

        layout.addWidget(self.banner)

        # Table: 2 columns: Objet | Type / Nature
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Objet", "Type / Nature"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        font = QFont("JetBrains Mono", 10)
        font.setStyleHint(QFont.Monospace)
        self.table.setFont(font)

        layout.addWidget(self.table)
        self._populate_rows()

    def _populate_rows(self):
        objs = self.table_info.get('objects', [])
        self.table.setRowCount(0)

        if not objs:
            self.table.insertRow(0)
            empty_item = QTableWidgetItem("(Aucun objet déclaré)")
            empty_item.setForeground(QColor("#94a3b8" if not self.is_dark else "#6c7086"))
            empty_item.setFont(QFont("SansSerif", 9, QFont.StyleItalic))
            self.table.setItem(0, 0, empty_item)
            self.table.setItem(0, 1, QTableWidgetItem("-"))
            self._fit_height()
            return

        for row, obj in enumerate(objs):
            self.table.insertRow(row)

            # 1. Objet
            name = obj.get('name', '')
            item_name = QTableWidgetItem(name)
            item_name.setFont(QFont("JetBrains Mono", 10, QFont.Bold))
            item_name.setForeground(QColor("#2563eb" if not self.is_dark else "#89b4fa"))

            # 2. Type / Nature
            typ = obj.get('type', '')
            item_type = QTableWidgetItem(typ)
            t_low = typ.lower()
            if 'procédure' in t_low or 'procedure' in t_low or 'fonction' in t_low:
                item_type.setForeground(QColor("#7c3aed" if not self.is_dark else "#cba6f7"))
            else:
                item_type.setForeground(QColor("#d97706" if not self.is_dark else "#fab387"))

            self.table.setItem(row, 0, item_name)
            self.table.setItem(row, 1, item_type)

        self._fit_height()

    def _fit_height(self):
        row_count = max(self.table.rowCount(), 1)
        header_h = self.table.horizontalHeader().height() or 26
        row_h = self.table.rowHeight(0) if self.table.rowCount() > 0 else 24
        total_h = header_h + (row_h * row_count) + 6
        self.table.setFixedHeight(max(total_h, 55))

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark

        if is_dark:
            banner_bg = "#181825"
            title_color = "#cdd6f4"
            self.banner.setStyleSheet(
                f"QFrame {{ background-color: {banner_bg}; border: none; border-radius: 4px; }}"
            )
            self.lbl_title.setStyleSheet(f"color: {title_color}; font-weight: bold;")
            self.lbl_count.setStyleSheet("color: #a6adc8;")
            self.table.setStyleSheet(
                "QTableWidget { background-color: #11111b; alternate-background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-right: none; border-top-left-radius: 4px; border-bottom-left-radius: 4px; }"
                "QHeaderView::section { background-color: #181825; color: #89b4fa; padding: 4px; border-top: 1px solid #313244; border-bottom: 1px solid #313244; border-left: none; border-right: 1px solid #313244; font-weight: bold; }"
                "QHeaderView::section:last { border-right: none; }"
            )
        else:
            banner_bg = "#f1f5f9"
            title_color = "#1e293b"
            self.banner.setStyleSheet(
                f"QFrame {{ background-color: {banner_bg}; border: none; border-radius: 4px; }}"
            )
            self.lbl_title.setStyleSheet(f"color: {title_color}; font-weight: bold;")
            self.lbl_count.setStyleSheet("color: #64748b;")
            self.table.setStyleSheet(
                "QTableWidget { background-color: #ffffff; alternate-background-color: #f8fafc; color: #1e293b; border: 1px solid #e2e8f0; border-right: none; border-top-left-radius: 4px; border-bottom-left-radius: 4px; }"
                "QHeaderView::section { background-color: #f1f5f9; color: #0f172a; padding: 4px; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; border-left: none; border-right: 1px solid #e2e8f0; font-weight: bold; }"
                "QHeaderView::section:last { border-right: none; }"
            )

        self._populate_rows()


class TDOView(QWidget):
    """
    Tableau T.D.O. Inspector that cleanly displays TDOG and each TDOL
    in separate tables rather than lumped together.
    """

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._raw_tables = []
        self._table_cards = []
        self._setup_ui()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Header bar
        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)
        title = QLabel("Tableaux de Déclaration (T.D.O.)")
        title.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        # Selector dropdown to focus on a specific table or view all
        self.table_selector = QComboBox()
        self.table_selector.setFixedHeight(24)
        self.table_selector.setMinimumWidth(180)
        self.table_selector.addItem("Tous les tableaux")
        self.table_selector.currentIndexChanged.connect(self._on_selector_changed)
        header.addWidget(self.table_selector)

        main_layout.addLayout(header)

        # Scroll area for separate tables
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area, 1)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        if is_dark:
            self.scroll_area.setStyleSheet(
                "QScrollArea { background-color: #11111b; border: none; }"
                "QWidget { background-color: #11111b; }"
            )
            self.table_selector.setStyleSheet(
                "QComboBox { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 2px 6px; font-size: 11px; }"
                "QComboBox QAbstractItemView { background-color: #181825; color: #cdd6f4; selection-background-color: #313244; border: 1px solid #313244; }"
            )
        else:
            self.scroll_area.setStyleSheet(
                "QScrollArea { background-color: #f7f9fa; border: none; }"
                "QWidget { background-color: #f7f9fa; }"
            )
            self.table_selector.setStyleSheet(
                "QComboBox { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 6px; font-size: 11px; }"
                "QComboBox QAbstractItemView { background-color: #ffffff; color: #1e293b; selection-background-color: #edf2f7; border: 1px solid #cbd5e1; }"
            )

        for card in self._table_cards:
            card.set_dark_mode(is_dark)

    def update_tdo(self, tdo_data):
        """
        Populates separate TDOG and TDOL tables.
        tdo_data can be:
        - a list of table dicts: [{'id': ..., 'title': ..., 'kind': ..., 'objects': [...]}, ...]
        - a list of object dicts: [{'name': ..., 'type': ..., 'scope': ..., ...}, ...]
        - a dict: {name: type} (legacy)
        """
        tables = []
        if isinstance(tdo_data, list):
            # Check if it's already a list of table dicts
            if tdo_data and isinstance(tdo_data[0], dict) and 'objects' in tdo_data[0] and 'kind' in tdo_data[0]:
                tables = list(tdo_data)
            else:
                # Group list of flat objects by scope into separate tables
                tdog_objs = []
                subprog_map = {}
                for obj in tdo_data:
                    scope = obj.get('scope', 'Globale')
                    if scope.lower() == 'globale':
                        tdog_objs.append(obj)
                    else:
                        subprog_map.setdefault(scope, []).append(obj)

                tables.append({
                    'id': 'tdog',
                    'title': 'Tableau de Déclaration des Objets Globaux (T.D.O.G.)',
                    'short_name': 'T.D.O.G. (Objets Globaux)',
                    'kind': 'tdog',
                    'objects': tdog_objs
                })

                for sub_name, objs in subprog_map.items():
                    tables.append({
                        'id': f"tdol_{sub_name}",
                        'title': f"T.D.O.L. — {sub_name}",
                        'short_name': f"T.D.O.L. ({sub_name})",
                        'kind': 'tdol',
                        'subprogram_name': sub_name,
                        'objects': objs
                    })

        elif isinstance(tdo_data, dict):
            # Legacy dict -> single TDOG table
            from compiler.symbol_extractor import get_python_equivalent
            objs = []
            for name, typ in tdo_data.items():
                objs.append({
                    'name': name,
                    'type': typ,
                    'py_equiv': get_python_equivalent(typ, name=name)
                })
            tables.append({
                'id': 'tdog',
                'title': 'Tableau de Déclaration des Objets Globaux (T.D.O.G.)',
                'short_name': 'T.D.O.G. (Objets Globaux)',
                'kind': 'tdog',
                'objects': objs
            })

        self._raw_tables = tables

        # Update selector dropdown options
        cur_text = self.table_selector.currentText()
        self.table_selector.blockSignals(True)
        self.table_selector.clear()

        if len(tables) > 1:
            self.table_selector.addItem("Tous les tableaux (T.D.O.G. & T.D.O.L.)")
        for tbl in tables:
            self.table_selector.addItem(tbl.get('short_name', tbl.get('title', 'Table')))

        idx = self.table_selector.findText(cur_text)
        if idx >= 0:
            self.table_selector.setCurrentIndex(idx)
        else:
            self.table_selector.setCurrentIndex(0)
        self.table_selector.blockSignals(False)

        self._render_cards()

    def _on_selector_changed(self):
        self._render_cards()

    def _render_cards(self):
        # Clear existing card widgets
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._table_cards.clear()

        if not self._raw_tables:
            lbl_empty = QLabel("Aucun tableau de déclaration (T.D.O.G. ou T.D.O.L.) détecté.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("color: #94a3b8; font-style: italic; padding: 20px;")
            self.cards_layout.addWidget(lbl_empty)
            self.cards_layout.addStretch()
            return

        selected_text = self.table_selector.currentText()
        show_all = selected_text.startswith("Tous les tableaux") or not selected_text

        for tbl in self._raw_tables:
            short_name = tbl.get('short_name', tbl.get('title', ''))
            if not show_all and short_name != selected_text and tbl.get('title') != selected_text:
                continue

            card = TDOTableCard(tbl, is_dark=self.is_dark, parent=self.container)
            self._table_cards.append(card)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def clear_tdo(self):
        self._raw_tables = []
        self._render_cards()
