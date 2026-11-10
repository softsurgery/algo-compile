"""
Stop execution icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    # Red stop square
    painter.setBrush(QBrush(QColor("#e74c3c")))
    painter.setPen(QPen(QColor("#c0392b"), 1.5))
    painter.drawRoundedRect(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 3, 3)

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
