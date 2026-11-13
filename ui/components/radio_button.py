"""
Reusable RadioButton component with declarative props, optional icon, and crisp vector painting.
"""

from typing import Callable, Optional, Tuple, Union
from PyQt5.QtCore import Qt, QRectF, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QRadioButton, QWidget

from ui.components._theme import (
    INDICATOR_SIZE,
    draw_toggle_contents,
    normalize_icon_size,
    resolve_is_dark,
    toggle_size_hint,
)


class AppRadioButton(QRadioButton):
    """Themed, prop-driven QRadioButton with fused circular indicator, optional icon, and label."""

    def __init__(
        self,
        text: str = "",
        parent: Optional[QWidget] = None,
        *,
        checked: bool = False,
        tooltip: Optional[str] = None,
        icon: Optional[QIcon] = None,
        icon_size: Optional[Union[QSize, Tuple[int, int], int]] = None,
        enabled: bool = True,
        is_dark: Optional[bool] = None,
        on_toggled: Optional[Callable[[bool], None]] = None,
        object_name: Optional[str] = None,
    ):
        super().__init__(text, parent)
        self._is_dark = is_dark
        self._hovered = False
        self.setChecked(checked)
        self.setEnabled(enabled)
        self.setCursor(Qt.PointingHandCursor)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if icon is not None:
            self.setIcon(icon)
        norm_size = normalize_icon_size(icon_size)
        if norm_size is not None:
            self.setIconSize(norm_size)
        if object_name is not None:
            self.setObjectName(object_name)
        if on_toggled is not None:
            self.toggled.connect(on_toggled)

    def set_dark_mode(self, is_dark: bool) -> None:
        """Sets explicit light or dark mode and triggers a repaint."""
        self._is_dark = is_dark
        self.update()

    def sizeHint(self) -> QSize:
        return toggle_size_hint(self)

    def minimumSizeHint(self) -> QSize:
        return toggle_size_hint(self)

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        is_dark = resolve_is_dark(self, self._is_dark)
        is_checked = self.isChecked()
        is_hover = self._hovered or self.underMouse()

        if not self.isEnabled():
            painter.setOpacity(0.5)

        ind_x, ind_y = draw_toggle_contents(self, painter, is_dark)

        if is_dark:
            bg = QColor("#181825")
            border_unchecked = QColor("#89b4fa" if is_hover else "#585b70")
            accent = QColor("#a6c8ff" if is_hover else "#89b4fa")
        else:
            bg = QColor("#ffffff")
            border_unchecked = QColor("#2563eb" if is_hover else "#94a3b8")
            accent = QColor("#1d4ed8" if is_hover else "#2563eb")

        diameter = float(INDICATOR_SIZE - 1)
        cx = ind_x + INDICATOR_SIZE / 2.0
        cy = ind_y + INDICATOR_SIZE / 2.0
        outer_rect = QRectF(cx - diameter / 2.0, cy - diameter / 2.0, diameter, diameter)

        if is_checked:
            painter.setPen(QPen(accent, 1.8))
            painter.setBrush(bg)
            painter.drawEllipse(outer_rect)

            dot_d = 8.5
            dot_rect = QRectF(cx - dot_d / 2.0, cy - dot_d / 2.0, dot_d, dot_d)
            painter.setPen(Qt.NoPen)
            painter.setBrush(accent)
            painter.drawEllipse(dot_rect)
        else:
            painter.setPen(QPen(border_unchecked, 1.6))
            painter.setBrush(bg)
            painter.drawEllipse(outer_rect)

        painter.end()
