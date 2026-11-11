"""
Font / Typography vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.8, s * 0.09)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    # Capital A
    # Left diagonal
    painter.drawLine(QPointF(s * 0.22, s * 0.82), QPointF(s * 0.50, s * 0.18))
    # Right diagonal
    painter.drawLine(QPointF(s * 0.50, s * 0.18), QPointF(s * 0.78, s * 0.82))
    # Crossbar
    painter.drawLine(QPointF(s * 0.33, s * 0.58), QPointF(s * 0.67, s * 0.58))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
