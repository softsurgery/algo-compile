"""
Refresh / Reload icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.5, s * 0.08)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    m = s * 0.14
    rect = QRectF(m, m, s - 2 * m, s - 2 * m)

    path = QPainterPath()
    path.arcMoveTo(rect, 45)
    path.arcTo(rect, 45, 275)
    painter.drawPath(path)

    end_pt = path.currentPosition()
    arrow_len = s * 0.18
    painter.drawLine(end_pt, end_pt + QPointF(arrow_len, 0))
    painter.drawLine(end_pt, end_pt + QPointF(0, -arrow_len))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
