"""
Bottom action bar for PreferencesDialog (Reset defaults, Apply, Cancel, OK).
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize
from ui.icons import create_icon


class PreferencesActionBar(QWidget):
    """Bottom action button row for PreferencesDialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        bottom_layout = QHBoxLayout(self)
        bottom_layout.setContentsMargins(4, 2, 4, 2)
        bottom_layout.setSpacing(10)

        self.btn_defaults = QPushButton("Rétablir par défaut")
        self.btn_defaults.setCursor(Qt.PointingHandCursor)
        self.btn_defaults.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_defaults)

        bottom_layout.addStretch()

        self.btn_apply = QPushButton("Appliquer")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setIconSize(QSize(18, 18))
        self.btn_ok.setStyleSheet("font-weight: bold; min-width: 75px;")
        bottom_layout.addWidget(self.btn_ok)

    def update_icons(self, is_dark: bool):
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.btn_apply.setIcon(create_icon("check", icon_color, size=20))
        self.btn_cancel.setIcon(create_icon("close", icon_color, size=20))
        self.btn_defaults.setIcon(create_icon("refresh", icon_color, size=20))
        self.btn_ok.setIcon(create_icon("check", "#ffffff", size=20))
