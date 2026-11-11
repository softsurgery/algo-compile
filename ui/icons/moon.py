"""
Moon vector icon for Dark Mode.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QRectF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    m = s * 0.12
    r_outer = QRectF(m, m, s - 2 * m, s - 2 * m)
    r_inner = QRectF(m + s * 0.20, m - s * 0.05, (s - 2 * m) * 0.88, (s - 2 * m) * 0.88)

    path_outer = QPainterPath()
    path_outer.addEllipse(r_outer)

    path_inner = QPainterPath()
    path_inner.addEllipse(r_inner)

    crescent = path_outer.subtracted(path_inner)

    painter.setPen(Qt.NoPen)
    painter.setBrush(color)
    painter.drawPath(crescent)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
