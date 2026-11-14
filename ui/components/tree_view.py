"""
Reusable TreeView (QTreeWidget) component with declarative props, no-focus delegate,
theme support, and recursive item filtering.
"""

from typing import Any, Callable, Optional, Sequence, Tuple, Union
from PyQt5.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QRect,
    QSize,
    Qt,
)
from PyQt5.QtGui import QCursor, QPainter
from PyQt5.QtWidgets import (
    QHeaderView,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from ui.components._theme import normalize_icon_size, resolve_is_dark
from ui.components.chevron import ChevronRotationAnimator, draw_chevron


class NoFocusDelegate(QStyledItemDelegate):
    """Prevents Qt from drawing dotted or rectangular focus artifacts on tree items."""

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)


class AppTreeView(QTreeWidget):
    """Themed, prop-driven QTreeWidget with clean focus handling and filtering."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        headers: Optional[Sequence[str]] = None,
        header_hidden: Optional[bool] = None,
        animated: bool = True,
        indentation: int = 14,
        root_is_decorated: bool = True,
        icon_size: Optional[Union[QSize, Tuple[int, int], int]] = None,
        no_focus_rect: bool = True,
        focus_policy: Optional[Qt.FocusPolicy] = Qt.NoFocus,
        horizontal_scrollbar: Optional[Qt.ScrollBarPolicy] = None,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None,
        border_radius: int = 6,
        item_padding: str = "4px 6px",
        item_margin: str = "1px 2px",
        item_radius: int = 4,
        is_dark: Optional[bool] = None,
        on_selection_changed: Optional[Callable[[], None]] = None,
        on_current_item_changed: Optional[Callable[[Any, Any], None]] = None,
        on_item_clicked: Optional[Callable[[Any, int], None]] = None,
        on_item_double_clicked: Optional[Callable[[Any, int], None]] = None,
        object_name: Optional[str] = None,
    ):
        super().__init__(parent)
        self._is_dark = is_dark
        self._border_radius = border_radius
        self._item_padding = item_padding
        self._item_margin = item_margin
        self._item_radius = item_radius
        self._chevron_animator = ChevronRotationAnimator(self)
        self._chevron_animator.angle_changed.connect(self._on_chevron_angle_changed)

        if headers is not None:
            header_list = list(headers)
            self.setColumnCount(len(header_list))
            self.setHeaderLabels(header_list)
            if len(header_list) > 0:
                self.header().setSectionResizeMode(0, QHeaderView.Stretch)
            if header_hidden is None:
                header_hidden = False
        elif header_hidden is None:
            header_hidden = True

        self.setHeaderHidden(header_hidden)
        self.setAnimated(animated)
        self.setIndentation(indentation)
        self.setRootIsDecorated(root_is_decorated)

        norm_size = normalize_icon_size(icon_size)
        if norm_size is not None:
            self.setIconSize(norm_size)

        if no_focus_rect:
            self.setItemDelegate(NoFocusDelegate(self))
        if focus_policy is not None:
            self.setFocusPolicy(focus_policy)
        if horizontal_scrollbar is not None:
            self.setHorizontalScrollBarPolicy(horizontal_scrollbar)
        if min_width is not None:
            self.setMinimumWidth(min_width)
        if max_width is not None:
            self.setMaximumWidth(max_width)
        if object_name is not None:
            self.setObjectName(object_name)

        if on_selection_changed is not None:
            self.itemSelectionChanged.connect(on_selection_changed)
        if on_current_item_changed is not None:
            self.currentItemChanged.connect(on_current_item_changed)
        if on_item_clicked is not None:
            self.itemClicked.connect(on_item_clicked)
        if on_item_double_clicked is not None:
            self.itemDoubleClicked.connect(on_item_double_clicked)

        self.expanded.connect(self._on_branch_expanded)
        self.collapsed.connect(self._on_branch_collapsed)

        self._apply_style()

    def set_dark_mode(self, is_dark: bool) -> None:
        """Sets explicit light or dark mode and reapplies the stylesheet."""
        self._is_dark = is_dark
        self._apply_style()

    def _apply_style(self) -> None:
        is_dark = resolve_is_dark(self, self._is_dark)
        if is_dark:
            bg = "#181825"
            fg = "#cdd6f4"
            border = "#313244"
            hover = "#313244"
            sel_bg = "#45475a"
            sel_fg = "#ffffff"
        else:
            bg = "#ffffff"
            fg = "#1e293b"
            border = "#cbd5e1"
            hover = "#f1f5f9"
            sel_bg = "#e2e8f0"
            sel_fg = "#0f172a"

        self.setStyleSheet(
            f"QTreeWidget {{"
            f"  background-color: {bg};"
            f"  color: {fg};"
            f"  border: 1px solid {border};"
            f"  border-radius: {self._border_radius}px;"
            f"  padding: 4px 2px;"
            f"  outline: none;"
            f"  show-decoration-selected: 0;"
            f"}}"
            f"QTreeWidget::item {{"
            f"  padding: {self._item_padding};"
            f"  margin: {self._item_margin};"
            f"  border-radius: {self._item_radius}px;"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:hover {{"
            f"  background-color: {hover};"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:selected {{"
            f"  background-color: {sel_bg};"
            f"  color: {sel_fg};"
            f"  font-weight: bold;"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:selected:active {{"
            f"  background-color: {sel_bg};"
            f"  color: {sel_fg};"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:selected:!active {{"
            f"  background-color: {sel_bg};"
            f"  color: {sel_fg};"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:focus {{"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::branch {{"
            f"  background: transparent;"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::branch:selected {{"
            f"  background: transparent;"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QHeaderView::section {{"
            f"  background-color: {bg};"
            f"  color: {fg};"
            f"  border: none;"
            f"  border-bottom: 1px solid {border};"
            f"  padding: 4px;"
            f"  font-weight: bold;"
            f"}}"
        )

    def filter_items(
        self,
        query: str,
        matcher: Optional[Callable[[QTreeWidgetItem, str], bool]] = None,
        expand_matches: bool = True,
        show_children_on_parent_match: bool = False,
    ) -> None:
        """Recursively filters tree items by query, expanding branches with matches."""
        q = query.strip().lower()

        def _check(item: QTreeWidgetItem, parent_matched: bool = False) -> bool:
            if not q:
                item.setHidden(False)
                for i in range(item.childCount()):
                    _check(item.child(i), False)
                return True

            if matcher is not None:
                matches_self = bool(matcher(item, q))
            else:
                matches_self = q in item.text(0).lower()

            child_inherit = show_children_on_parent_match and (parent_matched or matches_self)
            any_child_matches = False
            for i in range(item.childCount()):
                if _check(item.child(i), child_inherit):
                    any_child_matches = True

            visible = parent_matched or matches_self or any_child_matches
            item.setHidden(not visible)
            if expand_matches and (any_child_matches or (show_children_on_parent_match and matches_self and item.childCount() > 0)):
                item.setExpanded(True)

            return visible

        for i in range(self.topLevelItemCount()):
            _check(self.topLevelItem(i), False)

    def clear(self) -> None:
        """Stops active branch animations and clears all tree items."""
        self._chevron_animator.clear()
        super().clear()

    def _on_branch_expanded(self, index: QModelIndex) -> None:
        self._chevron_animator.animate_to(index, expanded=True)

    def _on_branch_collapsed(self, index: QModelIndex) -> None:
        self._chevron_animator.animate_to(index, expanded=False)

    def _on_chevron_angle_changed(self, p_idx: QPersistentModelIndex) -> None:
        if p_idx.isValid():
            row_rect = self.visualRect(QModelIndex(p_idx))
            if row_rect.isValid():
                self.viewport().update(QRect(0, row_rect.top(), self.viewport().width(), row_rect.height()))
                return
        self.viewport().update()

    def _branch_angle(self, index: QModelIndex) -> float:
        """Returns the current chevron rotation angle in degrees (0=closed, 90=open)."""
        return self._chevron_animator.angle_for(index, self.isExpanded(index))

    def drawBranches(self, painter: QPainter, rect: QRect, index: QModelIndex) -> None:
        """Draws a rotating anti-aliased chevron for expandable items."""
        super().drawBranches(painter, rect, index)

        if not index.isValid() or rect.width() <= 0 or rect.height() <= 0:
            return
        if not self.rootIsDecorated() and not index.parent().isValid():
            return

        model = self.model()
        if model is None or not model.hasChildren(index):
            return

        ind = self.indentation()
        if ind <= 0:
            return

        indicator_width = min(ind, rect.width())
        indicator_rect = QRect(
            rect.right() - indicator_width + 1,
            rect.top(),
            indicator_width,
            rect.height(),
        )

        is_dark = resolve_is_dark(self, self._is_dark)
        sel_model = self.selectionModel()
        is_selected = sel_model is not None and sel_model.isSelected(index)
        hovered_idx = (
            self.indexAt(self.viewport().mapFromGlobal(QCursor.pos()))
            if self.viewport().underMouse()
            else QModelIndex()
        )
        is_hovered = hovered_idx.isValid() and hovered_idx == index

        draw_chevron(
            painter,
            indicator_rect,
            angle=self._branch_angle(index),
            is_dark=is_dark,
            active=is_selected or is_hovered,
            enabled=self.isEnabled(),
        )
