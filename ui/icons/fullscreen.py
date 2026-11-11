"""
Fullscreen vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen = QPen(color, 1.8, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    x1 = margin + 2.0
    y1 = margin + 2.0
    x2 = s - margin - 2.0
    y2 = s - margin - 2.0
    arm = min((x2 - x1) * 0.32, 5.0)

    # Top-Left corner
    painter.drawLine(int(x1), int(y1), int(x1 + arm), int(y1))
    painter.drawLine(int(x1), int(y1), int(x1), int(y1 + arm))

    # Top-Right corner
    painter.drawLine(int(x2), int(y1), int(x2 - arm), int(y1))
    painter.drawLine(int(x2), int(y1), int(x2), int(y1 + arm))

    # Bottom-Left corner
    painter.drawLine(int(x1), int(y2), int(x1 + arm), int(y2))
    painter.drawLine(int(x1), int(y2), int(x1), int(y2 - arm))

    # Bottom-Right corner
    painter.drawLine(int(x2), int(y2), int(x2 - arm), int(y2))
    painter.drawLine(int(x2), int(y2), int(x2), int(y2 - arm))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
