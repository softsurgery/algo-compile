"""
Python logo / translation icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(QColor("#3498db"), 2))
    painter.drawArc(QRectF(margin + 1, margin + 1, s / 2 + 1, s / 2 + 1), 0, 270 * 16)
    painter.setPen(QPen(QColor("#f1c40f"), 2))
    painter.drawArc(QRectF(s / 2 - 2, s / 2 - 2, s / 2 + 1, s / 2 + 1), 180 * 16, 270 * 16)

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
