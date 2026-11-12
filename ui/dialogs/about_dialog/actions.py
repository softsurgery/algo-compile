"""
Bottom action buttons (GitHub link, Close) for AboutDialog.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QUrl


class AboutActionsWidget(QWidget):
    """Bottom action button row for AboutDialog."""

    def __init__(self, parent=None, on_close=None):
        super().__init__(parent)
        self.on_close = on_close
        self._setup_ui()

    def _setup_ui(self):
        btn_layout = QHBoxLayout(self)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)

        self.btn_github = QPushButton("Dépôt GitHub", self)
        self.btn_github.setObjectName("about_btn_github")
        self.btn_github.setCursor(Qt.PointingHandCursor)
        self.btn_github.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/softsurgery/algoo"))
        )
        btn_layout.addWidget(self.btn_github)

        self.btn_close = QPushButton("Fermer", self)
        self.btn_close.setObjectName("about_btn_close")
        self.btn_close.setDefault(True)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        if self.on_close:
            self.btn_close.clicked.connect(self.on_close)
        btn_layout.addWidget(self.btn_close)
