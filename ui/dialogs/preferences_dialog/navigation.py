"""
Navigation tree view and item delegate for PreferencesDialog.
"""

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from ui.components import AppTreeView, NoFocusDelegate
from ui.icons import create_icon


class PreferencesNavigationTree(AppTreeView):
    """Left-hand sidebar tree for navigating Preferences sections."""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            header_hidden=True,
            animated=True,
            indentation=12,
            root_is_decorated=False,
            icon_size=22,
            no_focus_rect=True,
            focus_policy=Qt.NoFocus,
            horizontal_scrollbar=Qt.ScrollBarAlwaysOff,
            min_width=200,
            max_width=320,
            border_radius=8,
            item_padding="6px 6px",
            item_radius=6,
        )

        self._setup_items()

    def _setup_items(self):
        # Category 1: Thème
        self.item_theme = QTreeWidgetItem(self, ["Thème"])
        self.item_theme.setData(0, Qt.UserRole, 0)
        self.item_theme.setSizeHint(0, QSize(0, 38))

        # Category 2: Éditeur de code
        self.cat_ed = QTreeWidgetItem(self, ["Éditeur de code"])
        self.cat_ed.setFont(0, QFont("SansSerif", 10, QFont.Bold))
        self.cat_ed.setSizeHint(0, QSize(0, 38))

        self.item_font = QTreeWidgetItem(self.cat_ed, ["Police & Affichage"])
        self.item_font.setData(0, Qt.UserRole, 1)
        self.item_font.setSizeHint(0, QSize(0, 36))

        self.item_colors = QTreeWidgetItem(self.cat_ed, ["Couleurs de syntaxe"])
        self.item_colors.setData(0, Qt.UserRole, 2)
        self.item_colors.setSizeHint(0, QSize(0, 36))

        self.expandAll()

    def update_icons(self, is_dark: bool):
        icon_color = "#cdd6f4" if is_dark else "#475569"
        sub_icon_color = "#89b4fa" if is_dark else "#2563eb"
        self.item_theme.setIcon(0, create_icon("theme", icon_color, size=24))
        self.cat_ed.setIcon(0, create_icon("settings", icon_color, size=24))
        self.item_font.setIcon(0, create_icon("font", sub_icon_color, size=22))
        self.item_colors.setIcon(0, create_icon("syntax", sub_icon_color, size=22))
