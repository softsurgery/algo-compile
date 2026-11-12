"""
Card container displaying technical metadata, engine, and developer links for AboutDialog.
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel


class AboutDetailsCard(QFrame):
    """Card container displaying version and developer details in a styled table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("about_card")
        self._setup_ui()

    def _setup_ui(self):
        card_layout = QVBoxLayout(self)
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
        self.details_label = QLabel(details_html, self)
        self.details_label.setOpenExternalLinks(True)
        self.details_label.setObjectName("about_details")
        card_layout.addWidget(self.details_label)
