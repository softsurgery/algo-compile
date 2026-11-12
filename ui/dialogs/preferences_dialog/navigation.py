"""
Navigation tree view and item delegate for PreferencesDialog.
"""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from ui.icons import create_icon


class NoFocusDelegate(QStyledItemDelegate):
    """Prevents Qt from drawing dotted or rectangular focus artifacts on tree items."""

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)


class PreferencesNavigationTree(QTreeWidget):
    """Left-hand sidebar tree for navigating Preferences sections."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(NoFocusDelegate(self))
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(12)
        self.setRootIsDecorated(False)
        self.setIconSize(QSize(22, 22))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMinimumWidth(200)
        self.setMaximumWidth(320)

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
