"""
Sun vector icon for Light Mode.
"""

import math
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    cx = s / 2.0
    cy = s / 2.0
    r_core = s * 0.20
    ray_inner = s * 0.30
    ray_outer = s * 0.43

    # Central sun disk
    pen_w = max(1.5, s * 0.08)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(QBrush(color))
    painter.drawEllipse(QPointF(cx, cy), r_core, r_core)

    # 8 radiating rays
    painter.setBrush(Qt.NoBrush)
    for i in range(8):
        angle = i * (math.pi / 4.0)
        x1 = cx + ray_inner * math.cos(angle)
        y1 = cy + ray_inner * math.sin(angle)
        x2 = cx + ray_outer * math.cos(angle)
        y2 = cy + ray_outer * math.sin(angle)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
