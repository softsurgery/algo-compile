"""
Reusable CheckBox component with declarative props, optional icon, and crisp vector painting.
"""

from typing import Callable, Optional, Tuple, Union
from PyQt5.QtCore import Qt, QPointF, QRectF, QSize
from PyQt5.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QCheckBox, QWidget

from ui.components._theme import (
    INDICATOR_SIZE,
    draw_toggle_contents,
    normalize_icon_size,
    resolve_is_dark,
    toggle_size_hint,
)


class AppCheckBox(QCheckBox):
    """Themed, prop-driven QCheckBox with fused indicator, optional icon, and label."""

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
        on_changed: Optional[Callable[[int], None]] = None,
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
        if on_changed is not None:
            self.stateChanged.connect(on_changed)

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
            bg_unchecked = QColor("#181825")
            border_unchecked = QColor("#89b4fa" if is_hover else "#585b70")
            accent = QColor("#a6c8ff" if is_hover else "#89b4fa")
            check_color = QColor("#11111b")
        else:
            bg_unchecked = QColor("#ffffff")
            border_unchecked = QColor("#2563eb" if is_hover else "#94a3b8")
            accent = QColor("#1d4ed8" if is_hover else "#2563eb")
            check_color = QColor("#ffffff")

        box_size = float(INDICATOR_SIZE - 1)
        box_rect = QRectF(ind_x + 0.5, ind_y + 0.5, box_size, box_size)

        if is_checked:
            painter.setPen(QPen(accent, 1.5))
            painter.setBrush(accent)
            painter.drawRoundedRect(box_rect, 4.5, 4.5)

            path = QPainterPath()
            path.moveTo(QPointF(box_rect.x() + box_size * 0.24, box_rect.y() + box_size * 0.52))
            path.lineTo(QPointF(box_rect.x() + box_size * 0.43, box_rect.y() + box_size * 0.71))
            path.lineTo(QPointF(box_rect.x() + box_size * 0.77, box_rect.y() + box_size * 0.30))
            painter.setPen(QPen(check_color, 2.1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        else:
            painter.setPen(QPen(border_unchecked, 1.6))
            painter.setBrush(bg_unchecked)
            painter.drawRoundedRect(box_rect, 4.5, 4.5)

        painter.end()
