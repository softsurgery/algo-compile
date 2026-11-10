"""
Theme toggle icon (Sun / Moon).
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(QBrush(color))
    painter.drawPie(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 90 * 16, 180 * 16)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
