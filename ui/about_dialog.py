"""
About Dialog for Algoo IDE.
Displays app branding, logo, version, developer info, and repository links.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget
)
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import Qt, QUrl

from ui.icons import get_app_icon, get_logo_pixmap


class AboutDialog(QDialog):
    """Modern modal dialog displaying information about Algoo IDE."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setWindowTitle("À propos d'Algoo")
        # self.setWindowIcon(get_app_icon())
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setMaximumWidth(520)

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 20)
        main_layout.setSpacing(16)

        # Header section: Logo + Title + Subtitle
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(8)

        # Logo
        self.logo_label = QLabel(self)
        self.logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = get_logo_pixmap(96)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(self.logo_label)

        # Title
        title_label = QLabel("Algoo", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("SansSerif", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setObjectName("about_title")
        header_layout.addWidget(title_label)

        # Version & tag
        version_label = QLabel("Version 1.0 — IDE Algorithmique", self)
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setObjectName("about_version")
        header_layout.addWidget(version_label)

        main_layout.addLayout(header_layout)

        # Description text
        desc_label = QLabel(
            "Environnement de développement moderne et pédagogique "
            "pour l'Algorithmique scolaire et universitaire.",
            self
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("about_desc")
        main_layout.addWidget(desc_label)

        # Card container with details
        card = QFrame(self)
        card.setObjectName("about_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        details_html = (
            "<table style='width: 100%; border-collapse: collapse; font-size: 13px;'>"
            "<tr><td style='padding: 3px 0; font-weight: bold;'>Développeur :</td>"
            "<td style='padding: 3px 0; text-align: right;'>softsurgery</td></tr>"
            "<tr><td style='padding: 3px 0; font-weight: bold;'>Code source :</td>"
            "<td style='padding: 3px 0; text-align: right;'>"
            "<a href='https://github.com/softsurgery/algoo'>github.com/softsurgery/algoo</a></td></tr>"
            "<tr><td style='padding: 3px 0; font-weight: bold;'>Moteur :</td>"
            "<td style='padding: 3px 0; text-align: right;'>Python 3 + NumPy</td></tr>"
            "<tr><td style='padding: 3px 0; font-weight: bold;'>Interface :</td>"
            "<td style='padding: 3px 0; text-align: right;'>PyQt5</td></tr>"
            "</table>"
        )
        self.details_label = QLabel(details_html, card)
        self.details_label.setOpenExternalLinks(True)
        self.details_label.setObjectName("about_details")
        card_layout.addWidget(self.details_label)

        main_layout.addWidget(card)

        # Bottom buttons
        btn_layout = QHBoxLayout()
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
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        main_layout.addLayout(btn_layout)

    def _apply_styling(self):
        if self.is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                }
                QLabel#about_title {
                    color: #cdd6f4;
                }
                QLabel#about_version {
                    color: #a6adc8;
                    font-size: 12px;
                }
                QLabel#about_desc {
                    color: #bac2de;
                    font-size: 13px;
                }
                QFrame#about_card {
                    background-color: #181825;
                    border: 1px solid #313244;
                    border-radius: 8px;
                }
                QLabel#about_details {
                    color: #cdd6f4;
                }
                QLabel#about_details a {
                    color: #89b4fa;
                    text-decoration: none;
                }
                QLabel#about_details a:hover {
                    text-decoration: underline;
                }
                QPushButton#about_btn_github {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 1px solid #45475a;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton#about_btn_github:hover {
                    background-color: #45475a;
                }
                QPushButton#about_btn_close {
                    background-color: #89b4fa;
                    color: #11111b;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton#about_btn_close:hover {
                    background-color: #b4befe;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #1e293b;
                }
                QLabel#about_title {
                    color: #0f172a;
                }
                QLabel#about_version {
                    color: #64748b;
                    font-size: 12px;
                }
                QLabel#about_desc {
                    color: #475569;
                    font-size: 13px;
                }
                QFrame#about_card {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                }
                QLabel#about_details {
                    color: #334155;
                }
                QLabel#about_details a {
                    color: #2563eb;
                    text-decoration: none;
                }
                QLabel#about_details a:hover {
                    text-decoration: underline;
                }
                QPushButton#about_btn_github {
                    background-color: #f1f5f9;
                    color: #334155;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton#about_btn_github:hover {
                    background-color: #e2e8f0;
                }
                QPushButton#about_btn_close {
                    background-color: #2563eb;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QPushButton#about_btn_close:hover {
                    background-color: #1d4ed8;
                }
            """)
