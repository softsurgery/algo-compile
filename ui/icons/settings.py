"""
Settings / Preferences gear vector icon.
"""

import math
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    cx = s / 2.0
    cy = s / 2.0
    r_out = s * 0.40
    r_in = s * 0.28
    r_hole = s * 0.14
    num_teeth = 8

    path = QPainterPath()
    for i in range(num_teeth):
        a1 = (i * 2 * math.pi) / num_teeth
        a2 = a1 + (math.pi / num_teeth) * 0.35
        a3 = a1 + (math.pi / num_teeth) * 0.65
        a4 = (i + 1) * 2 * math.pi / num_teeth

        p1 = QPointF(cx + r_in * math.cos(a1), cy + r_in * math.sin(a1))
        p2 = QPointF(cx + r_out * math.cos(a2), cy + r_out * math.sin(a2))
        p3 = QPointF(cx + r_out * math.cos(a3), cy + r_out * math.sin(a3))
        p4 = QPointF(cx + r_in * math.cos(a4), cy + r_in * math.sin(a4))

        if i == 0:
            path.moveTo(p1)
        else:
            path.lineTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p4)

    path.closeSubpath()
    path.addEllipse(QPointF(cx, cy), r_hole, r_hole)

    pen = QPen(color, max(1.2, s * 0.06), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(color)
    painter.drawPath(path)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
