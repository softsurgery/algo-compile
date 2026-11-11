"""
Next / Right Arrow vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen = QPen(color, max(2.0, s * 0.1), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    cx = s / 2.0
    cy = s / 2.0
    dx = s * 0.22
    dy = s * 0.28

    # Right chevron
    p1 = QPointF(cx - dx * 0.6, cy - dy)
    p2 = QPointF(cx + dx * 0.8, cy)
    p3 = QPointF(cx - dx * 0.6, cy + dy)
    painter.drawLine(p1, p2)
    painter.drawLine(p2, p3)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
