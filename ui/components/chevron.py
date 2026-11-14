"""
Reusable rotating chevron component, vector painter helper, and branch animation controller.
"""

from typing import Callable, Dict, Optional
from PyQt5.QtCore import (
    QEasingCurve,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QPointF,
    QRect,
    QSize,
    Qt,
    QVariantAnimation,
    pyqtProperty,
    pyqtSignal,
)
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QWidget

from ui.components._theme import resolve_is_dark


def chevron_color(
    is_dark: bool,
    *,
    active: bool = False,
    enabled: bool = True,
) -> QColor:
    """Returns the theme-appropriate chevron color for normal/active/disabled states."""
    if is_dark:
        color = QColor("#cdd6f4" if active else "#a6adc8")
    else:
        color = QColor("#1e293b" if active else "#64748b")
    if not enabled:
        color.setAlphaF(0.45)
    return color


def draw_chevron(
    painter: QPainter,
    rect: QRect,
    *,
    angle: float = 0.0,
    color: Optional[QColor] = None,
    is_dark: bool = False,
    active: bool = False,
    enabled: bool = True,
    half_arm: float = 3.8,
    depth: float = 2.2,
    stroke_width: float = 1.6,
) -> None:
    """Paints an anti-aliased chevron centered in `rect` rotated by `angle` degrees.

    At 0 degrees the chevron points right (`>`). At 90 degrees it points down (`v`).
    """
    if not rect.isValid() or rect.width() <= 0 or rect.height() <= 0:
        return

    resolved_color = color if color is not None else chevron_color(
        is_dark, active=active, enabled=enabled
    )

    cx = rect.left() + rect.width() / 2.0
    cy = rect.top() + rect.height() / 2.0

    path = QPainterPath()
    path.moveTo(QPointF(-depth * 0.6, -half_arm))
    path.lineTo(QPointF(depth, 0.0))
    path.lineTo(QPointF(-depth * 0.6, half_arm))

    painter.save()
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.translate(cx, cy)
    painter.rotate(angle)
    pen = QPen(resolved_color, stroke_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)
    painter.restore()


class ChevronRotationAnimator(QObject):
    """Manages per-index chevron rotation animations for tree/item views."""

    angle_changed = pyqtSignal(QPersistentModelIndex)

    def __init__(
        self,
        parent: Optional[QObject] = None,
        *,
        closed_angle: float = 0.0,
        open_angle: float = 90.0,
        duration_ms: int = 150,
    ):
        super().__init__(parent)
        self._closed_angle = float(closed_angle)
        self._open_angle = float(open_angle)
        self._duration_ms = int(duration_ms)
        self._angles: Dict[QPersistentModelIndex, float] = {}
        self._animations: Dict[QPersistentModelIndex, QVariantAnimation] = {}

    def animate_to(self, index: QModelIndex, expanded: bool) -> None:
        """Animates the chevron for `index` toward its expanded or collapsed angle."""
        if not index.isValid():
            return

        target_angle = self._open_angle if expanded else self._closed_angle
        key = QPersistentModelIndex(index)
        prev_anim = self._animations.pop(key, None)
        if prev_anim is not None:
            prev_anim.stop()
            prev_anim.deleteLater()

        default_start = self._closed_angle if expanded else self._open_angle
        start_angle = self._angles.get(key, default_start)
        self._angles[key] = start_angle

        anim = QVariantAnimation(self)
        anim.setDuration(self._duration_ms)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(start_angle)
        anim.setEndValue(target_angle)

        def _on_value(value, p_idx=key) -> None:
            if not p_idx.isValid():
                return
            self._angles[p_idx] = float(value)
            self.angle_changed.emit(p_idx)

        def _on_finished(p_idx=key, current_anim=anim) -> None:
            if self._animations.get(p_idx) is current_anim:
                self._animations.pop(p_idx, None)
                self._angles.pop(p_idx, None)
            current_anim.deleteLater()
            self.angle_changed.emit(p_idx)

        anim.valueChanged.connect(_on_value)
        anim.finished.connect(_on_finished)
        self._animations[key] = anim
        anim.start()

    def angle_for(self, index: QModelIndex, is_expanded: bool) -> float:
        """Returns the current rotation angle for `index`."""
        key = QPersistentModelIndex(index)
        if key in self._angles:
            return self._angles[key]
        return self._open_angle if is_expanded else self._closed_angle

    def active_count(self) -> int:
        """Returns the number of currently running chevron animations."""
        return len(self._animations)

    def clear(self) -> None:
        """Stops and discards all active animations and cached angles."""
        for anim in list(self._animations.values()):
            anim.stop()
            anim.deleteLater()
        self._animations.clear()
        self._angles.clear()


class AppRotatingChevron(QWidget):
    """Standalone, prop-driven rotating chevron indicator widget."""

    toggled = pyqtSignal(bool)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        expanded: bool = False,
        closed_angle: float = 0.0,
        open_angle: float = 90.0,
        duration_ms: int = 150,
        size: int = 16,
        half_arm: float = 3.8,
        depth: float = 2.2,
        stroke_width: float = 1.6,
        clickable: bool = False,
        is_dark: Optional[bool] = None,
        on_toggled: Optional[Callable[[bool], None]] = None,
        object_name: Optional[str] = None,
    ):
        super().__init__(parent)
        self._expanded = bool(expanded)
        self._closed_angle = float(closed_angle)
        self._open_angle = float(open_angle)
        self._duration_ms = int(duration_ms)
        self._size = int(size)
        self._half_arm = float(half_arm)
        self._depth = float(depth)
        self._stroke_width = float(stroke_width)
        self._clickable = bool(clickable)
        self._is_dark = is_dark
        self._hovered = False
        self._angle = self._open_angle if self._expanded else self._closed_angle

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._duration_ms)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_value)

        self.setFixedSize(self._size, self._size)
        if self._clickable:
            self.setCursor(Qt.PointingHandCursor)
        if object_name is not None:
            self.setObjectName(object_name)
        if on_toggled is not None:
            self.toggled.connect(on_toggled)

    def sizeHint(self) -> QSize:
        return QSize(self._size, self._size)

    def minimumSizeHint(self) -> QSize:
        return QSize(self._size, self._size)

    @pyqtProperty(float)
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = float(value)
        self.update()

    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool, animated: bool = True) -> None:
        """Sets the expanded state and rotates the chevron to its target angle."""
        expanded = bool(expanded)
        if expanded == self._expanded and self._anim.state() != QVariantAnimation.Running:
            return
        self._expanded = expanded
        target = self._open_angle if expanded else self._closed_angle

        self._anim.stop()
        if animated and self._duration_ms > 0:
            self._anim.setStartValue(self._angle)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._angle = target
            self.update()

    def toggle(self, animated: bool = True) -> None:
        """Toggles the expanded state and emits `toggled`."""
        self.set_expanded(not self._expanded, animated=animated)
        self.toggled.emit(self._expanded)

    def set_dark_mode(self, is_dark: bool) -> None:
        """Sets explicit light or dark mode and triggers a repaint."""
        self._is_dark = is_dark
        self.update()

    def _on_anim_value(self, value) -> None:
        self._angle = float(value)
        self.update()

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if self._clickable and event.button() == Qt.LeftButton and self.isEnabled():
            self.toggle(animated=True)
            event.accept()
            return
        super().mousePressEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        is_dark = resolve_is_dark(self, self._is_dark)
        draw_chevron(
            painter,
            self.rect(),
            angle=self._angle,
            is_dark=is_dark,
            active=self._hovered or self.underMouse(),
            enabled=self.isEnabled(),
            half_arm=self._half_arm,
            depth=self._depth,
            stroke_width=self._stroke_width,
        )
        painter.end()
