"""
Vector icons generator using QPainter and QPixmap.
Ensures crisp, resolution-independent modern icons without external asset dependencies.
"""

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF

def create_icon(name: str, color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    """Generates a QIcon with the specified name and color."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    color = QColor(color_hex)
    pen = QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)

    margin = 3
    s = float(size)

    if name == "new":
        # Blank page with folded corner
        path_poly = QPolygonF([
            QPointF(margin + 2, margin),
            QPointF(s - margin - 5, margin),
            QPointF(s - margin, margin + 5),
            QPointF(s - margin, s - margin),
            QPointF(margin + 2, s - margin),
        ])
        painter.drawPolygon(path_poly)
        painter.drawLine(QPointF(s - margin - 5, margin), QPointF(s - margin - 5, margin + 5))
        painter.drawLine(QPointF(s - margin - 5, margin + 5), QPointF(s - margin, margin + 5))
        # Plus inside
        cx, cy = s / 2 - 1, s / 2 + 2
        painter.drawLine(QPointF(cx - 3, cy), QPointF(cx + 3, cy))
        painter.drawLine(QPointF(cx, cy - 3), QPointF(cx, cy + 3))

    elif name == "open":
        # Folder icon
        folder_poly = QPolygonF([
            QPointF(margin, margin + 5),
            QPointF(margin + 6, margin + 5),
            QPointF(margin + 9, margin + 8),
            QPointF(s - margin, margin + 8),
            QPointF(s - margin, s - margin),
            QPointF(margin, s - margin),
        ])
        painter.drawPolygon(folder_poly)

    elif name == "save":
        # Floppy disk icon
        disk_poly = QPolygonF([
            QPointF(margin, margin),
            QPointF(s - margin - 4, margin),
            QPointF(s - margin, margin + 4),
            QPointF(s - margin, s - margin),
            QPointF(margin, s - margin),
        ])
        painter.drawPolygon(disk_poly)
        painter.drawRect(QRectF(margin + 4, margin, s - 2 * margin - 8, 5))
        painter.drawRect(QRectF(margin + 3, s - margin - 6, s - 2 * margin - 6, 6))

    elif name == "run":
        # Green play triangle with circle
        painter.setBrush(QBrush(QColor("#2ecc71")))
        painter.setPen(QPen(QColor("#27ae60"), 1.5))
        triangle = QPolygonF([
            QPointF(margin + 4, margin + 2),
            QPointF(s - margin - 2, s / 2),
            QPointF(margin + 4, s - margin - 2),
        ])
        painter.drawPolygon(triangle)

    elif name == "stop":
        # Red stop square
        painter.setBrush(QBrush(QColor("#e74c3c")))
        painter.setPen(QPen(QColor("#c0392b"), 1.5))
        painter.drawRoundedRect(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 3, 3)

    elif name == "step":
        # Step / Debug icon (arrow over dot)
        painter.drawEllipse(QPointF(s / 2, s - margin - 4), 2, 2)
        # Curved arrow
        painter.drawArc(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 30 * 16, 120 * 16)
        painter.drawLine(QPointF(s - margin - 2, s / 2 - 2), QPointF(s - margin - 2, s / 2 + 3))

    elif name == "python":
        # Python representation (two interlaced snakes/curves)
        painter.setPen(QPen(QColor("#3498db"), 2))
        painter.drawArc(QRectF(margin + 1, margin + 1, s / 2 + 1, s / 2 + 1), 0, 270 * 16)
        painter.setPen(QPen(QColor("#f1c40f"), 2))
        painter.drawArc(QRectF(s / 2 - 2, s / 2 - 2, s / 2 + 1, s / 2 + 1), 180 * 16, 270 * 16)

    elif name == "copy":
        painter.drawRect(QRectF(margin, margin + 4, s - 2 * margin - 4, s - 2 * margin - 4))
        painter.drawPolyline(QPolygonF([
            QPointF(margin + 4, margin + 4),
            QPointF(margin + 4, margin),
            QPointF(s - margin, margin),
            QPointF(s - margin, s - margin - 4),
            QPointF(s - 2 * margin, s - margin - 4),
        ]))

    elif name == "clear":
        # Eraser / Broom
        painter.drawLine(QPointF(margin + 3, margin + 3), QPointF(s - margin - 3, s - margin - 3))
        painter.drawLine(QPointF(s - margin - 3, margin + 3), QPointF(margin + 3, s - margin - 3))

    elif name == "theme":
        # Sun / Moon half
        painter.setBrush(QBrush(color))
        painter.drawPie(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4), 90 * 16, 180 * 16)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(margin + 2, margin + 2, s - 2 * margin - 4, s - 2 * margin - 4))

    elif name == "help":
        font = QFont("SansSerif", int(s * 0.55), QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "?")

    else:
        # Default dot
        painter.drawEllipse(QPointF(s / 2, s / 2), 3, 3)

    painter.end()
    return QIcon(pixmap)
