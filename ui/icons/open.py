"""
Open folder icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    fx1 = margin + 0.5
    fy1 = margin + 1.5
    fw = s - 2 * margin - 1.0
    fh = s - 2 * margin - 1.5
    fx2 = fx1 + fw
    fy2 = fy1 + fh
    tab_w = fw * 0.42
    tab_h = fh * 0.22

    back_folder = QPolygonF([
        QPointF(fx1, fy1),
        QPointF(fx1 + tab_w, fy1),
        QPointF(fx1 + tab_w + 2.5, fy1 + tab_h),
        QPointF(fx2, fy1 + tab_h),
        QPointF(fx2, fy2),
        QPointF(fx1, fy2),
    ])
    painter.setBrush(QBrush(QColor("#d97706")))
    painter.setPen(QPen(QColor("#b45309"), 1.2))
    painter.drawPolygon(back_folder)

    # Paper sheet inside folder
    px1 = fx1 + 2.5
    py1 = fy1 + tab_h * 0.5
    pw = fw - 5.0
    ph = fh * 0.65
    painter.setBrush(QBrush(QColor("#ffffff")))
    painter.setPen(QPen(QColor("#cbd5e1"), 1.0))
    painter.drawRoundedRect(QRectF(px1, py1, pw, ph), 1.5, 1.5)
    # Line on sheet
    painter.setPen(QPen(QColor("#94a3b8"), 1.2, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(px1 + 2.5, py1 + 3.0), QPointF(px1 + pw - 2.5, py1 + 3.0))

    # Front pocket
    front_poly = QPolygonF([
        QPointF(fx1, fy1 + fh * 0.38),
        QPointF(fx2, fy1 + fh * 0.38),
        QPointF(fx2 - 1.5, fy2),
        QPointF(fx1 + 1.5, fy2),
    ])
    painter.setBrush(QBrush(QColor("#f59e0b")))
    painter.setPen(QPen(QColor("#b45309"), 1.2))
    painter.drawPolygon(front_poly)

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
