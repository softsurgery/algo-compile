"""
New file icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF
from .base import make_icon

def draw(painter: QPainter, s: float, margin: float, color: QColor):
    x1 = margin + 1.0
    y1 = margin
    w = s - 2 * margin - 2.5
    h = s - 2 * margin
    x2 = x1 + w
    y2 = y1 + h
    fold = s * 0.24

    # Document body
    sheet = QPolygonF([
        QPointF(x1, y1),
        QPointF(x2 - fold, y1),
        QPointF(x2, y1 + fold),
        QPointF(x2, y2),
        QPointF(x1, y2),
    ])
    painter.setBrush(QBrush(QColor("#3b82f6")))
    painter.setPen(QPen(QColor("#1d4ed8"), 1.2))
    painter.drawPolygon(sheet)

    # Folded dog-ear corner
    fold_poly = QPolygonF([
        QPointF(x2 - fold, y1),
        QPointF(x2 - fold, y1 + fold),
        QPointF(x2, y1 + fold),
    ])
    painter.setBrush(QBrush(QColor("#93c5fd")))
    painter.setPen(QPen(QColor("#1d4ed8"), 1.0))
    painter.drawPolygon(fold_poly)

    # Document preview lines
    painter.setPen(QPen(QColor("#ffffff"), 1.4, Qt.SolidLine, Qt.RoundCap))
    line1_y = y1 + fold * 0.95
    painter.drawLine(QPointF(x1 + 3.0, line1_y), QPointF(x2 - fold - 1.5, line1_y))
    line2_y = line1_y + s * 0.16
    painter.drawLine(QPointF(x1 + 3.0, line2_y), QPointF(x2 - 3.5, line2_y))

    # Plus badge at bottom-right
    badge_r = s * 0.22
    bcx = x2 - badge_r + 1.0
    bcy = y2 - badge_r + 1.0
    painter.setBrush(QBrush(QColor("#10b981")))
    painter.setPen(QPen(QColor("#059669"), 1.2))
    painter.drawEllipse(QPointF(bcx, bcy), badge_r, badge_r)

    painter.setPen(QPen(QColor("#ffffff"), 1.8, Qt.SolidLine, Qt.RoundCap))
    pw = badge_r * 0.55
    painter.drawLine(QPointF(bcx - pw, bcy), QPointF(bcx + pw, bcy))
    painter.drawLine(QPointF(bcx, bcy - pw), QPointF(bcx, bcy + pw))

def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
