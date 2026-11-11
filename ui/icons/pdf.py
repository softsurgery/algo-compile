"""
PDF vector icon.
"""

from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF
from .base import make_icon


def draw(painter: QPainter, s: float, margin: float, color: QColor):
    x = margin + 2.0
    y = margin + 1.0
    w = s - 2 * margin - 4.0
    h = s - 2 * margin - 2.0

    fold = min(w * 0.35, 6.0)

    # Document outline with folded top-right corner
    doc_poly = QPolygonF([
        QPointF(x, y),
        QPointF(x + w - fold, y),
        QPointF(x + w, y + fold),
        QPointF(x + w, y + h),
        QPointF(x, y + h),
    ])

    painter.setPen(QPen(color, 1.4))
    painter.setBrush(Qt.NoBrush)
    painter.drawPolygon(doc_poly)

    # Folded flap
    flap_poly = QPolygonF([
        QPointF(x + w - fold, y),
        QPointF(x + w - fold, y + fold),
        QPointF(x + w, y + fold),
    ])
    painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 40)))
    painter.drawPolygon(flap_poly)

    # Red badge for "PDF"
    badge_h = h * 0.35
    badge_y = y + h * 0.5
    badge_rect = QRectF(x + 1.5, badge_y, w - 3.0, badge_h)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor("#ef4444")))
    painter.drawRoundedRect(badge_rect, 1.5, 1.5)

    # "PDF" text inside badge
    painter.setPen(QColor("#ffffff"))
    font = QFont("SansSerif", max(5, int(s * 0.18)), QFont.Bold)
    painter.setFont(font)
    painter.drawText(badge_rect, Qt.AlignCenter, "PDF")


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    return make_icon(draw, color_hex, size)
