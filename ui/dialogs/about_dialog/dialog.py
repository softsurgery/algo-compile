"""
Modern modal dialog displaying information about Algoo IDE.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

from ui.dialogs.about_dialog.header import AboutHeaderWidget
from ui.dialogs.about_dialog.details_card import AboutDetailsCard
from ui.dialogs.about_dialog.actions import AboutActionsWidget
from ui.dialogs.about_dialog.styles import get_about_dialog_stylesheet


class AboutDialog(QDialog):
    """Modern modal dialog displaying information about Algoo IDE."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setWindowTitle("À propos d'Algoo")
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setMaximumWidth(520)

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 20)
        main_layout.setSpacing(16)

        # Header component
        self.header_widget = AboutHeaderWidget(self)
        self.logo_label = self.header_widget.logo_label
        main_layout.addWidget(self.header_widget)

        # Description text
        self.desc_label = QLabel(
            "Environnement de développement moderne et pédagogique "
            "pour l'Algorithmique scolaire et universitaire.",
            self
        )
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        self.desc_label.setObjectName("about_desc")
        main_layout.addWidget(self.desc_label)

        # Card container with details
        self.card = AboutDetailsCard(self)
        self.details_label = self.card.details_label
        main_layout.addWidget(self.card)

        # Bottom buttons
        self.actions_widget = AboutActionsWidget(self, on_close=self.accept)
        self.btn_github = self.actions_widget.btn_github
        self.btn_close = self.actions_widget.btn_close
        main_layout.addWidget(self.actions_widget)

    def _apply_styling(self):
        self.setStyleSheet(get_about_dialog_stylesheet(self.is_dark))
