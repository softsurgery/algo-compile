"""
Shared theme resolution and toggle-control layout/painting helpers for ui/components.
"""

from typing import Optional, Tuple, Union
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWidgets import QAbstractButton, QApplication, QWidget


INDICATOR_SIZE = 18
INDICATOR_GAP = 8
ICON_GAP = 6
H_PADDING = 2
V_PADDING = 4


def resolve_is_dark(widget: QWidget, explicit_is_dark: Optional[bool]) -> bool:
    """Determines whether dark mode is active for a component."""
    if explicit_is_dark is not None:
        return explicit_is_dark

    parent = widget.parentWidget()
    while parent is not None:
        if hasattr(parent, "is_dark"):
            return bool(getattr(parent, "is_dark"))
        if hasattr(parent, "is_dark_mode"):
            return bool(getattr(parent, "is_dark_mode"))
        parent = parent.parentWidget()

    app = QApplication.instance()
    if app is not None:
        return app.palette().window().color().lightness() < 128
    return widget.palette().window().color().lightness() < 128


def normalize_icon_size(
    icon_size: Optional[Union[QSize, Tuple[int, int], int]]
) -> Optional[QSize]:
    """Converts int, (w, h) tuple, or QSize into QSize."""
    if icon_size is None:
        return None
    if isinstance(icon_size, int):
        return QSize(icon_size, icon_size)
    if isinstance(icon_size, tuple):
        return QSize(icon_size[0], icon_size[1])
    return icon_size


def toggle_size_hint(button: QAbstractButton) -> QSize:
    """Computes sizeHint for a fused [indicator + optional icon + label] control."""
    fm = button.fontMetrics()
    text = button.text()
    has_icon = not button.icon().isNull()
    icon_sz = button.iconSize() if has_icon else QSize(0, 0)

    width = H_PADDING + INDICATOR_SIZE
    if has_icon:
        width += INDICATOR_GAP + icon_sz.width()
        if text:
            width += ICON_GAP + fm.horizontalAdvance(text)
    elif text:
        width += INDICATOR_GAP + fm.horizontalAdvance(text)
    width += H_PADDING + 4

    height = max(
        INDICATOR_SIZE + V_PADDING * 2,
        icon_sz.height() + V_PADDING * 2 if has_icon else 0,
        fm.height() + V_PADDING * 2,
    )
    return QSize(width, height)


def draw_toggle_contents(
    button: QAbstractButton,
    painter: QPainter,
    is_dark: bool,
) -> Tuple[float, float]:
    """
    Draws optional icon and label text to the right of the indicator.
    Returns (indicator_x, indicator_y) for the 18x18 indicator box.
    """
    h = button.height()
    ind_x = float(H_PADDING)
    ind_y = (h - INDICATOR_SIZE) / 2.0

    x = H_PADDING + INDICATOR_SIZE + INDICATOR_GAP
    has_icon = not button.icon().isNull()
    if has_icon:
        icon_sz = button.iconSize()
        icon_y = int((h - icon_sz.height()) / 2)
        mode = QIcon.Normal if button.isEnabled() else QIcon.Disabled
        button.icon().paint(
            painter,
            QRect(x, icon_y, icon_sz.width(), icon_sz.height()),
            Qt.AlignCenter,
            mode,
        )
        x += icon_sz.width() + ICON_GAP

    text = button.text()
    if text:
        fg = QColor("#cdd6f4" if is_dark else "#1e293b")
        painter.setPen(fg)
        painter.setFont(button.font())
        text_rect = QRect(x, 0, max(0, button.width() - x - H_PADDING), h)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

    return ind_x, ind_y
