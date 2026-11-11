"""
Close / Cross icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    cx, cy = s / 2, s / 2
    d = s * 0.22
    painter.drawLine(QPointF(cx - d, cy - d), QPointF(cx + d, cy + d))
    painter.drawLine(QPointF(cx + d, cy - d), QPointF(cx - d, cy + d))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
