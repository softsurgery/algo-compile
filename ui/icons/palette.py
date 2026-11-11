"""
Palette icon for theme colors and palettes.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.5, s * 0.08)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)

    # Palette main circular body
    m = s * 0.12
    r = QRectF(m, m, s - 2 * m, s - 2 * m)
    painter.drawEllipse(r)

    # Thumb hole
    painter.drawEllipse(QPointF(s * 0.65, s * 0.65), s * 0.10, s * 0.10)

    # 3 paint spots
    painter.setBrush(QBrush(color))
    painter.drawEllipse(QPointF(s * 0.35, s * 0.35), s * 0.08, s * 0.08)
    painter.drawEllipse(QPointF(s * 0.58, s * 0.32), s * 0.08, s * 0.08)
    painter.drawEllipse(QPointF(s * 0.32, s * 0.58), s * 0.08, s * 0.08)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
