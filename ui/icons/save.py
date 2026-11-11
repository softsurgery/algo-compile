"""
Save floppy disk icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    sx1 = margin + 1.0
    sy1 = margin
    sw = s - 2 * margin - 2.0
    sh = s - 2 * margin
    sx2 = sx1 + sw
    sy2 = sy1 + sh
    sc = s * 0.16

    # Disk body
    disk_poly = QPolygonF([
        QPointF(sx1, sy1),
        QPointF(sx2 - sc, sy1),
        QPointF(sx2, sy1 + sc),
        QPointF(sx2, sy2),
        QPointF(sx1, sy2),
    ])
    painter.setBrush(QBrush(QColor("#2563eb")))
    painter.setPen(QPen(QColor("#1d4ed8"), 1.2))
    painter.drawPolygon(disk_poly)

    # Metal shutter at top
    shutter_w = sw * 0.58
    shutter_h = sh * 0.34
    shutter_x = sx1 + (sw - shutter_w) / 2
    painter.setBrush(QBrush(QColor("#e2e8f0")))
    painter.setPen(QPen(QColor("#94a3b8"), 1.0))
    painter.drawRoundedRect(QRectF(shutter_x, sy1, shutter_w, shutter_h), 1.0, 1.0)
    # Shutter window
    painter.setBrush(QBrush(QColor("#1e293b")))
    painter.setPen(Qt.NoPen)
    painter.drawRect(QRectF(shutter_x + shutter_w * 0.22, sy1 + 2.0, shutter_w * 0.25, shutter_h - 3.5))

    # White label at bottom
    label_w = sw * 0.76
    label_h = sh * 0.42
    label_x = sx1 + (sw - label_w) / 2
    label_y = sy2 - label_h
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.setPen(QPen(QColor("#93c5fd"), 1.0))
    painter.drawRoundedRect(QRectF(label_x, label_y, label_w, label_h), 1.5, 1.5)
    # Label colored accent lines
    painter.setPen(QPen(QColor("#ef4444"), 1.5, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(label_x + 2.5, label_y + 3.0), QPointF(label_x + label_w - 2.5, label_y + 3.0))
    painter.setPen(QPen(QColor("#3b82f6"), 1.2, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(label_x + 2.5, label_y + label_h * 0.55), QPointF(label_x + label_w - 2.5, label_y + label_h * 0.55))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
