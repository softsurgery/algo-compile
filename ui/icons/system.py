"""
System / Desktop monitor vector icon for System Mode.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRectF, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    pen_w = max(1.5, s * 0.08)
    painter.setPen(QPen(color, pen_w, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.setBrush(Qt.NoBrush)

    # Monitor screen rectangle
    m_x = s * 0.12
    m_y = s * 0.16
    w = s - 2 * m_x
    h = s * 0.52
    painter.drawRoundedRect(QRectF(m_x, m_y, w, h), s * 0.06, s * 0.06)

    # Monitor stand neck
    neck_top_y = m_y + h
    neck_bot_y = s * 0.78
    painter.drawLine(QPointF(s * 0.5, neck_top_y), QPointF(s * 0.5, neck_bot_y))

    # Monitor stand base
    base_w = s * 0.40
    painter.drawLine(QPointF(s * 0.5 - base_w / 2, neck_bot_y), QPointF(s * 0.5 + base_w / 2, neck_bot_y))


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
