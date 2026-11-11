"""
Base utilities for vector icons generation.
"""

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

def make_icon(draw_fn, color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    """Helper to create a QIcon by executing draw_fn on a transparent QPixmap."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    color = QColor(color_hex)
    margin = 2.5 if size <= 24 else 3.5
    s = float(size)

    draw_fn(painter, s, margin, color)

    painter.end()
    return QIcon(pixmap)
