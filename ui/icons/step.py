"""
Step / Debug icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawEllipse(QPointF(s / 2, s - margin - 4), 2, 2)
    # Curved arrow
    painter.drawArc(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 30 * 16, 120 * 16)
    painter.drawLine(QPointF(s - margin - 2, s / 2 - 2), QPointF(s - margin - 2, s / 2 + 3))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
