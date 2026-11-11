"""
Checkmark vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(2.0, s * 0.11)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # Checkmark
    painter.drawLine(QPointF(s * 0.22, s * 0.52), QPointF(s * 0.42, s * 0.76))
    painter.drawLine(QPointF(s * 0.42, s * 0.76), QPointF(s * 0.82, s * 0.26))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
