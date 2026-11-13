"""
Theme selection page for PreferencesDialog (System, Light, Dark).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QButtonGroup, QLabel
from PyQt5.QtCore import QSize
from ui.components import AppRadioButton
from ui.dialogs.preferences_dialog.header import create_section_header
from ui.theme_utils import detect_system_dark_mode
from ui.icons import create_icon


class ThemePage(QWidget):
    """Page for configuring IDE visual theme mode (System / Light / Dark)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        layout.addWidget(create_section_header(
            "Thème de l'interface",
            "Choisissez le mode d'affichage de l'environnement de développement. "
            "Le mode Système s'adapte automatiquement aux réglages de votre système d'exploitation."
        ))

        box = QGroupBox("Mode d'affichage :")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 18, 16, 16)
        box_layout.setSpacing(14)

        self.btn_group_mode = QButtonGroup(self)

        self.rb_system = AppRadioButton(
            "Système (Automatique)",
            tooltip="Suit automatiquement le thème clair/sombre de votre système d'exploitation",
            icon_size=24,
        )
        self.btn_group_mode.addButton(self.rb_system, 0)
        box_layout.addWidget(self.rb_system)

        self.rb_light = AppRadioButton(
            "Mode Clair (Light)",
            tooltip="Active en permanence le thème clair épuré",
            icon_size=24,
        )
        self.btn_group_mode.addButton(self.rb_light, 1)
        box_layout.addWidget(self.rb_light)

        self.rb_dark = AppRadioButton(
            "Mode Sombre (Dark)",
            tooltip="Active en permanence le thème sombre moderne",
            icon_size=24,
        )
        self.btn_group_mode.addButton(self.rb_dark, 2)
        box_layout.addWidget(self.rb_dark)

        layout.addWidget(box)

        # System detection info card
        sys_detected = "Sombre (Dark)" if detect_system_dark_mode() else "Clair (Light)"
        self.lbl_sys_info = QLabel(f"ℹ️  Thème système actuellement détecté : <b>{sys_detected}</b>")
        self.lbl_sys_info.setObjectName("pref_sys_info")
        layout.addWidget(self.lbl_sys_info)

        layout.addStretch()

    def update_system_info(self, is_dark: bool):
        sys_detected = "Sombre (Dark)" if is_dark else "Clair (Light)"
        self.lbl_sys_info.setText(f"ℹ️  Thème système actuellement détecté : <b>{sys_detected}</b>")

    def update_icons(self, is_dark: bool):
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.rb_system.setIcon(create_icon("system", icon_color, size=24))
        self.rb_light.setIcon(create_icon("sun", "#f59e0b", size=24))
        self.rb_dark.setIcon(create_icon("moon", "#89b4fa" if is_dark else "#2563eb", size=24))

    def get_selected_mode(self) -> str:
        if self.rb_light.isChecked():
            return "light"
        elif self.rb_dark.isChecked():
            return "dark"
        return "system"

    def set_selected_mode(self, mode: str):
        if mode == "light":
            self.rb_light.setChecked(True)
        elif mode == "dark":
            self.rb_dark.setChecked(True)
        else:
            self.rb_system.setChecked(True)
