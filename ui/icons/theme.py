"""
Theme toggle icon (Sun / Moon).
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.5, s * 0.08)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    m = s * 0.12
    r = QRectF(m, m, s - 2 * m, s - 2 * m)

    # Left half filled (moon), right half empty (sun)
    painter.setBrush(QBrush(color))
    painter.drawPie(r, 90 * 16, 180 * 16)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(r)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
