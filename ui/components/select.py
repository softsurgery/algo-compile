"""
Reusable Select (QComboBox) component with declarative props and crisp chevron icon.
"""

from typing import Any, Callable, Optional, Sequence, Tuple, Union
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox, QWidget

from ui.components._theme import resolve_is_dark


SelectItem = Union[str, Tuple[str, Any]]


class AppSelect(QComboBox):
    """Themed, prop-driven QComboBox (select) with anti-aliased chevron indicator."""

    def __init__(
        self,
        items: Optional[Sequence[SelectItem]] = None,
        parent: Optional[QWidget] = None,
        *,
        current: Optional[Union[str, int]] = None,
        tooltip: Optional[str] = None,
        fixed_height: Optional[int] = None,
        min_width: Optional[int] = None,
        enabled: bool = True,
        compact: bool = False,
        is_dark: Optional[bool] = None,
        on_changed: Optional[Callable[[int], None]] = None,
        on_text_changed: Optional[Callable[[str], None]] = None,
        object_name: Optional[str] = None,
    ):
        super().__init__(parent)
        self._compact = compact
        self._is_dark = is_dark
        self.setCursor(Qt.PointingHandCursor)

        if items:
            self.set_items(items)
        if current is not None:
            if isinstance(current, int):
                if 0 <= current < self.count():
                    self.setCurrentIndex(current)
            else:
                idx = self.findText(current)
                if idx >= 0:
                    self.setCurrentIndex(idx)

        self.setEnabled(enabled)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if fixed_height is not None:
            self.setFixedHeight(fixed_height)
        if min_width is not None:
            self.setMinimumWidth(min_width)
        if object_name is not None:
            self.setObjectName(object_name)
        if on_changed is not None:
            self.currentIndexChanged.connect(on_changed)
        if on_text_changed is not None:
            self.currentTextChanged.connect(on_text_changed)
        if is_dark is not None:
            self.set_dark_mode(is_dark)

    def set_items(self, items: Sequence[SelectItem], keep_selection: bool = False) -> None:
        """Replaces items from strings or (label, userData) tuples."""
        prev_text = self.currentText() if keep_selection else None
        self.clear()
        for item in items:
            if isinstance(item, tuple):
                label, data = item
                self.addItem(label, data)
            else:
                self.addItem(item)
        if prev_text is not None:
            idx = self.findText(prev_text)
            if idx >= 0:
                self.setCurrentIndex(idx)

    def set_dark_mode(self, is_dark: bool) -> None:
        """Applies explicit light or dark styling when used outside global stylesheets."""
        self._is_dark = is_dark
        if is_dark:
            bg = "#181825"
            fg = "#cdd6f4"
            border = "#313244"
            hover_border = "#45475a"
            sel_bg = "#313244"
        else:
            bg = "#ffffff"
            fg = "#1e293b"
            border = "#cbd5e1"
            hover_border = "#94a3b8"
            sel_bg = "#edf2f7"

        padding = "2px 24px 2px 6px" if self._compact else "4px 28px 4px 10px"
        font_rule = "font-size: 11px;" if self._compact else ""
        self.setStyleSheet(
            f"QComboBox {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: 5px; padding: {padding}; {font_rule} }}"
            f"QComboBox:hover {{ border-color: {hover_border}; }}"
            f"QComboBox::drop-down {{ subcontrol-origin: padding; subcontrol-position: top right; width: 22px; border: none; background: transparent; }}"
            f"QComboBox::down-arrow {{ image: none; border: none; width: 0px; height: 0px; }}"
            f"QComboBox QAbstractItemView {{ background-color: {bg}; color: {fg}; "
            f"selection-background-color: {sel_bg}; border: 1px solid {border}; }}"
        )
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        is_dark = resolve_is_dark(self, self._is_dark)
        is_hover = bool(opt.state & QStyle.State_MouseOver)
        if is_dark:
            chevron_color = QColor("#cdd6f4" if is_hover else "#a6adc8")
        else:
            chevron_color = QColor("#1e293b" if is_hover else "#64748b")

        if not self.isEnabled():
            painter.setOpacity(0.45)

        arrow_rect = self.style().subControlRect(QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, self)
        if not arrow_rect.isValid() or arrow_rect.width() <= 0:
            cx = float(self.width()) - 13.0
            cy = float(self.height()) / 2.0
        else:
            cx = float(arrow_rect.center().x())
            cy = float(arrow_rect.center().y())

        w = 4.2
        h = 2.4
        path = QPainterPath()
        path.moveTo(QPointF(cx - w, cy - h * 0.6))
        path.lineTo(QPointF(cx, cy + h))
        path.lineTo(QPointF(cx + w, cy - h * 0.6))

        pen = QPen(chevron_color, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        painter.end()
