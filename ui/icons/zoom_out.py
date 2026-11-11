"""
Zoom Out icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    zr = s * 0.28
    zcx = margin + zr + 0.5
    zcy = margin + zr + 0.5

    # Handle
    hx1 = zcx + zr * 0.707
    hy1 = zcy + zr * 0.707
    hx2 = s - margin - 0.5
    hy2 = s - margin - 0.5
    painter.setPen(QPen(QColor("#64748b"), s * 0.16, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(hx1, hy1), QPointF(hx2, hy2))
    painter.setPen(QPen(QColor("#334155"), s * 0.10, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(hx1 + 1.0, hy1 + 1.0), QPointF(hx2, hy2))

    # Glass lens fill & ocean blue rim
    painter.setBrush(QBrush(QColor(56, 189, 248, 60)))
    painter.setPen(QPen(QColor("#0284c7"), 2.0))
    painter.drawEllipse(QPointF(zcx, zcy), zr, zr)

    # Subtle reflection arc
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(QColor(255, 255, 255, 160), 1.2, Qt.SolidLine, Qt.RoundCap))
    painter.drawArc(QRectF(zcx - zr + 2, zcy - zr + 2, (zr - 2) * 2, (zr - 2) * 2), 100 * 16, 80 * 16)

    # Crimson red - sign
    painter.setPen(QPen(QColor("#ef4444"), 2.2, Qt.SolidLine, Qt.RoundCap))
    p_len = zr * 0.52
    painter.drawLine(QPointF(zcx - p_len, zcy), QPointF(zcx + p_len, zcy))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
