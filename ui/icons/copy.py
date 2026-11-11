"""
Copy to clipboard icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawRect(QRectF(margin, margin + 4, s - 2 * margin - 4, s - 2 * margin - 4))
    painter.drawPolyline(QPolygonF([
        QPointF(margin + 4, margin + 4),
        QPointF(margin + 4, margin),
        QPointF(s - margin, margin),
        QPointF(s - margin, s - margin - 4),
        QPointF(s - 2 * margin, s - margin - 4),
    ]))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
