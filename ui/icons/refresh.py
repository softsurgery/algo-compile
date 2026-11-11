"""
Refresh / Reload icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    r = s - 2 * margin - 2.0
    rect = QRectF(margin + 1.0, margin + 1.0, r, r)

    path = QPainterPath()
    path.arcMoveTo(rect, 45)
    path.arcTo(rect, 45, 275)
    painter.drawPath(path)

    end_pt = path.currentPosition()
    painter.drawLine(end_pt, end_pt + QPointF(3.0, 0))
    painter.drawLine(end_pt, end_pt + QPointF(0, -3.0))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
