"""
Header label component for InsertCodeDialog.
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont


def create_header_label(is_dark: bool) -> QLabel:
    """Creates top descriptive label with styled typography."""
    header_lbl = QLabel(
        "Parcourez vos collections d'algorithmes, consultez les documents Markdown joints et insérez le code :"
    )
    header_lbl.setFont(QFont("SansSerif", 10, QFont.Bold))
    header_lbl.setStyleSheet("color: #a6adc8;" if is_dark else "color: #475569;")
    return header_lbl
