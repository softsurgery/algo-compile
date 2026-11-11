"""
Help / Question mark icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(color)
    font = QFont("SansSerif", int(s * 0.55), QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "?")

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
