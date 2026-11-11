"""
Folder icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    x = margin
    y = margin + s * 0.08
    w = s - 2 * margin
    h = s - 2 * margin - s * 0.08
    
    tab_w = w * 0.44
    tab_h = h * 0.30
    
    # Back folder shape
    back_folder = QPolygonF([
        QPointF(x, y + tab_h),
        QPointF(x, y),
        QPointF(x + tab_w, y),
        QPointF(x + tab_w + tab_h * 0.5, y + tab_h),
        QPointF(x + w, y + tab_h),
        QPointF(x + w, y + h),
        QPointF(x, y + h),
    ])
    painter.setBrush(QBrush(QColor("#f59e0b")))
    painter.setPen(QPen(QColor("#d97706"), 1.2))
    painter.drawPolygon(back_folder)
    
    # Front flap
    front_flap = QPolygonF([
        QPointF(x, y + tab_h + 1.5),
        QPointF(x + w, y + tab_h + 1.5),
        QPointF(x + w, y + h),
        QPointF(x, y + h),
    ])
    painter.setBrush(QBrush(QColor("#fbbf24")))
    painter.setPen(QPen(QColor("#d97706"), 1.2))
    painter.drawPolygon(front_flap)


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
