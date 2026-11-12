"""
Reusable section header component for PreferencesDialog pages.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QFont


def create_section_header(title: str, description: str) -> QWidget:
    """Helper to create a unified, elegant header block for each settings page."""
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 8)
    lay.setSpacing(6)

    lbl_title = QLabel(title)
    lbl_title.setFont(QFont("SansSerif", 13, QFont.Bold))
    lay.addWidget(lbl_title)

    lbl_desc = QLabel(description)
    lbl_desc.setWordWrap(True)
    lbl_desc.setObjectName("pref_desc")
    lbl_desc.setFont(QFont("SansSerif", 9))
    lay.addWidget(lbl_desc)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setObjectName("pref_separator")
    lay.addWidget(sep)

    return w
