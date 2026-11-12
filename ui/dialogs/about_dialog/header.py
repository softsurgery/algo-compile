"""
Header element for AboutDialog: App Logo, Title, and Version.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.icons import get_logo_pixmap


class AboutHeaderWidget(QWidget):
    """Header widget displaying the Algoo logo, app title, and version info."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        # Logo
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = get_logo_pixmap(96)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap)
        layout.addWidget(self.logo_label)

        # Title
        self.title_label = QLabel("Algoo", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("SansSerif", 18, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("about_title")
        layout.addWidget(self.title_label)

        # Version & tag
        self.version_label = QLabel("Version 1.0 — IDE Algorithmique", self)
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setObjectName("about_version")
        layout.addWidget(self.version_label)
