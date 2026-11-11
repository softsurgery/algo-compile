"""
Picture / Image vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    x = margin + 1.0
    y = margin + 1.5
    w = s - 2 * margin - 2.0
    h = s - 2 * margin - 3.0

    # Picture outer frame
    painter.setPen(QPen(color, 1.4))
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(int(x), int(y), int(w), int(h), 2.0, 2.0)

    # Sun / Circle
    sun_r = s * 0.09
    sun_cx = x + w * 0.72
    sun_cy = y + h * 0.32
    painter.setBrush(QBrush(QColor("#f59e0b")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(sun_cx, sun_cy), sun_r, sun_r)

    # Mountain landscape
    mountain = QPolygonF([
        QPointF(x + 1.0, y + h - 1.0),
        QPointF(x + w * 0.35, y + h * 0.45),
        QPointF(x + w * 0.6, y + h * 0.7),
        QPointF(x + w * 0.8, y + h * 0.52),
        QPointF(x + w - 1.0, y + h - 1.0),
    ])
    painter.setBrush(QBrush(QColor("#10b981") if color.value() > 100 else QColor("#059669")))
    painter.setPen(QPen(color, 1.0))
    painter.drawPolygon(mountain)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
