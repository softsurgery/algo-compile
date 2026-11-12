"""
Bottom action bar for InsertCodeDialog (Copy, Fullscreen, Cancel, New tab, Insert).
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from ui.icons import create_icon
from ui.dialogs.insert_code_dialog.styles import (
    get_secondary_button_style,
    get_primary_insert_button_style,
)


class InsertCodeActionBar(QWidget):
    """Bottom action toolbar for InsertCodeDialog."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(
            "color: #6c7086; font-size: 11px;" if self.is_dark else "color: #94a3b8; font-size: 11px;"
        )
        layout.addWidget(self.lbl_status)

        icon_color = "#cdd6f4" if self.is_dark else "#475569"
        btn_sec_style = get_secondary_button_style(self.is_dark)

        self.btn_copy = QPushButton("Copier")
        self.btn_copy.setStyleSheet(btn_sec_style)
        self.btn_copy.setIcon(create_icon("copy", icon_color, 14))
        layout.addWidget(self.btn_copy)

        self.btn_fullscreen = QPushButton("Plein écran")
        self.btn_fullscreen.setStyleSheet(btn_sec_style)
        self.btn_fullscreen.setIcon(create_icon("fullscreen", icon_color, 14))
        self.btn_fullscreen.setToolTip("Basculer la boîte de dialogue en plein écran (F11)")
        layout.addWidget(self.btn_fullscreen)

        layout.addStretch()

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.setStyleSheet(btn_sec_style)
        self.btn_cancel.setIcon(create_icon("close", icon_color, 14))
        layout.addWidget(self.btn_cancel)

        self.btn_new_tab = QPushButton("Ouvrir dans un nouvel onglet")
        self.btn_new_tab.setStyleSheet(btn_sec_style)
        self.btn_new_tab.setIcon(create_icon("new", icon_color, 14))
        layout.addWidget(self.btn_new_tab)

        self.btn_insert = QPushButton("Insérer dans l'éditeur")
        self.btn_insert.setDefault(True)
        self.btn_insert.setStyleSheet(get_primary_insert_button_style())
        self.btn_insert.setIcon(create_icon("step", "#ffffff", 14))
        layout.addWidget(self.btn_insert)

    def update_icons(self, is_dark: bool):
        self.is_dark = is_dark
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.btn_copy.setIcon(create_icon("copy", icon_color, 14))
        self.btn_fullscreen.setIcon(create_icon("fullscreen", icon_color, 14))
        self.btn_cancel.setIcon(create_icon("close", icon_color, 14))
        self.btn_new_tab.setIcon(create_icon("new", icon_color, 14))
        self.btn_insert.setIcon(create_icon("step", "#ffffff", 14))
