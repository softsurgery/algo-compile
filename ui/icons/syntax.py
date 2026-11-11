"""
Syntax / Code colors vector icon (< / >).
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.8, s * 0.09)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # Left bracket <
    painter.drawLine(QPointF(s * 0.32, s * 0.28), QPointF(s * 0.15, s * 0.50))
    painter.drawLine(QPointF(s * 0.15, s * 0.50), QPointF(s * 0.32, s * 0.72))

    # Middle slash /
    painter.drawLine(QPointF(s * 0.58, s * 0.22), QPointF(s * 0.42, s * 0.78))

    # Right bracket >
    painter.drawLine(QPointF(s * 0.68, s * 0.28), QPointF(s * 0.85, s * 0.50))
    painter.drawLine(QPointF(s * 0.85, s * 0.50), QPointF(s * 0.68, s * 0.72))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
