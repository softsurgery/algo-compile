"""
Dialog for browsing, managing, and inserting algorithmic code snippets and collections.
Features:
- Tree view following folder structure on disk.
- Multi-tab preview for Code, Markdown documentation, Pictures, and Companion files.
- Capability to attach/join files (MD, Pictures, data files) to snippets.
- Preserves full backward-compatibility with tests expecting list_widget and preview_editor styles and methods.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QShortcut
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt

from ui.snippets_view import SnippetsWidget
from ui.styles import LIGHT_THEME, DARK_THEME
from ui.dialogs.insert_code_dialog.header import create_header_label
from ui.dialogs.insert_code_dialog.action_bar import InsertCodeActionBar
from ui.dialogs.insert_code_dialog.compat_list import CompatibilityListManager
from ui.dialogs.insert_code_dialog.styles import apply_compat_widget_styles


class InsertCodeDialog(QDialog):
    """Modern modal dialog with Tree View for code snippets, collections, and attachments."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setWindowTitle("Outils — Bibliothèque de Snippets & Collections (Insert Code)")

        # Remove app icon in the top left
        transparent_pixmap = QPixmap(1, 1)
        transparent_pixmap.fill(Qt.transparent)
        self.setWindowIcon(QIcon(transparent_pixmap))

        # Enable maximize, minimize and fullscreen buttons
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)

        self.resize(1180, 750)
        self.setMinimumSize(950, 580)
        self._is_fullscreen = False

        # Apply global theme to dialog window
        self.setStyleSheet(DARK_THEME if self.is_dark else LIGHT_THEME)

        self.selected_code = ""
        self.selected_title = ""
        self.action_mode = None  # 'insert' or 'new_tab'

        self._setup_ui()
        self._apply_compat_styles()
        self._sync_compatibility_list()

        # Keyboard shortcut for full screen
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Header description
        self.header_lbl = create_header_label(self.is_dark)
        main_layout.addWidget(self.header_lbl)

        # Main Snippets Tree Widget
        self.snippets_widget = SnippetsWidget(self, is_dark=self.is_dark)
        self.snippets_widget.set_bottom_actions_visible(False)
        self.snippets_widget.insert_requested.connect(self._on_snippet_insert_requested)
        self.snippets_widget.new_tab_requested.connect(self._on_snippet_new_tab_requested)
        main_layout.addWidget(self.snippets_widget, 1)

        # Direct references for backward-compatibility
        self.tree_widget = self.snippets_widget.tree_widget
        self.search_input = self.snippets_widget.search_input
        self.preview_editor = self.snippets_widget.preview_editor
        self.lbl_count = self.snippets_widget.lbl_count

        # Synchronized list_widget for tests and compatibility
        self._compat_mgr = CompatibilityListManager(self)
        self.list_widget = self._compat_mgr.list_widget
        main_layout.addWidget(self.list_widget)

        # Connect search input to also filter compatibility list
        self.search_input.textChanged.connect(self._sync_compatibility_list)

        # Bottom Action Bar
        self.action_bar = InsertCodeActionBar(self, is_dark=self.is_dark)
        self.lbl_status = self.action_bar.lbl_status
        self.btn_copy = self.action_bar.btn_copy
        self.btn_fullscreen = self.action_bar.btn_fullscreen
        self.btn_cancel = self.action_bar.btn_cancel
        self.btn_new_tab = self.action_bar.btn_new_tab
        self.btn_insert = self.action_bar.btn_insert

        self.btn_copy.clicked.connect(self.snippets_widget._copy_code)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_new_tab.clicked.connect(self._on_open_new_tab)
        self.btn_insert.clicked.connect(self._on_insert_clicked)

        main_layout.addWidget(self.action_bar)

    def _apply_compat_styles(self):
        self.action_bar.update_icons(self.is_dark)
        apply_compat_widget_styles(self, self.is_dark)

    def _sync_compatibility_list(self):
        self._compat_mgr.sync()

    def _on_compat_list_row_changed(self, row: int):
        self._compat_mgr._on_compat_list_row_changed(row)

    def _on_snippet_insert_requested(self, code: str, title: str):
        self.selected_code = code
        self.selected_title = title
        self.action_mode = 'insert'
        self.accept()

    def _on_snippet_new_tab_requested(self, code: str, title: str):
        self.selected_code = code
        self.selected_title = title
        self.action_mode = 'new_tab'
        self.accept()

    def _on_insert_clicked(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            data = item.data(Qt.UserRole)
            self.selected_code = data["code"]
            self.selected_title = data["title"]
        elif self.snippets_widget.current_snippet:
            self.selected_code = self.snippets_widget.current_snippet.code
            self.selected_title = self.snippets_widget.current_snippet.title
        elif self.list_widget.count() > 0:
            item = self.list_widget.item(0)
            data = item.data(Qt.UserRole)
            self.selected_code = data["code"]
            self.selected_title = data["title"]

        self.action_mode = 'insert'
        self.accept()

    def _on_open_new_tab(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            data = item.data(Qt.UserRole)
            self.selected_code = data["code"]
            self.selected_title = data["filename"]
        elif self.snippets_widget.current_snippet:
            self.selected_code = self.snippets_widget.current_snippet.code
            self.selected_title = self.snippets_widget.current_snippet.filename
        elif self.list_widget.count() > 0:
            item = self.list_widget.item(0)
            data = item.data(Qt.UserRole)
            self.selected_code = data["code"]
            self.selected_title = data["filename"]

        self.action_mode = 'new_tab'
        self.accept()

    def toggle_fullscreen(self):
        """Toggles dialog between full screen and normal window."""
        if self.isFullScreen():
            self.showNormal()
            self._is_fullscreen = False
            if hasattr(self, "btn_fullscreen"):
                self.btn_fullscreen.setText("Plein écran")
        else:
            self.showFullScreen()
            self._is_fullscreen = True
            if hasattr(self, "btn_fullscreen"):
                self.btn_fullscreen.setText("Quitter plein écran")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.toggle_fullscreen()
            return
        super().keyPressEvent(event)
