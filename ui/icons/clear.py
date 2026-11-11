"""
Clear / Eraser icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawLine(QPointF(margin + 3, margin + 3), QPointF(s - margin - 3, s - margin - 3))
    painter.drawLine(QPointF(s - margin - 3, margin + 3), QPointF(margin + 3, s - margin - 3))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
