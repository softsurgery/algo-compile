"""
Attachment / Paperclip vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    painter.setRenderHint(QPainter.Antialiasing, True)
    pen = QPen(color, max(1.5, s * 0.08), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    cx = s / 2.0
    cy = s / 2.0
    w = s * 0.28
    h = s * 0.55

    path = QPainterPath()
    path.moveTo(cx - w * 0.3, cy + h * 0.2)
    path.lineTo(cx - w * 0.3, cy - h * 0.2)
    path.arcTo(cx - w * 0.3, cy - h * 0.45, w * 0.6, h * 0.35, 180, -180)
    path.lineTo(cx + w * 0.3, cy + h * 0.3)
    path.arcTo(cx - w * 0.6, cy + h * 0.15, w * 0.9, h * 0.35, 0, -180)
    path.lineTo(cx - w * 0.6, cy - h * 0.25)
    path.arcTo(cx - w * 0.6, cy - h * 0.5, w * 1.2, h * 0.38, 180, -180)
    path.lineTo(cx + w * 0.6, cy + h * 0.4)

    painter.drawPath(path)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
