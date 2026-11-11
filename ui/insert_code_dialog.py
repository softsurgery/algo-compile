"""
Dialog for browsing, managing, and inserting algorithmic code snippets and collections.
Features:
- Tree view following folder structure on disk.
- Multi-tab preview for Code, Markdown documentation, Pictures, and Companion files.
- Capability to attach/join files (MD, Pictures, data files) to snippets.
- Preserves full backward-compatibility with tests expecting list_widget and preview_editor styles and methods.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QWidget, QShortcut
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt

from ui.editor import AlgoCodeEditor
from ui.icons import create_icon
from ui.styles import LIGHT_THEME, DARK_THEME
from ui.snippets_view import SnippetsWidget
from ui.snippets_manager import scan_snippets_tree, get_all_snippets_flat, SnippetItem, KNOWN_EXAMPLES_META


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
        header_lbl = QLabel("Parcourez vos collections d'algorithmes, consultez les documents Markdown joints et insérez le code :")
        header_lbl.setFont(QFont("SansSerif", 10, QFont.Bold))
        header_lbl.setStyleSheet("color: #a6adc8;" if self.is_dark else "color: #475569;")
        main_layout.addWidget(header_lbl)

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
        self.list_widget = QListWidget()
        self.list_widget.setVisible(False)
        self.list_widget.currentRowChanged.connect(self._on_compat_list_row_changed)
        main_layout.addWidget(self.list_widget)

        # Connect search input to also filter compatibility list
        self.search_input.textChanged.connect(self._sync_compatibility_list)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #6c7086; font-size: 11px;" if self.is_dark else "color: #94a3b8; font-size: 11px;")
        bottom_layout.addWidget(self.lbl_status)

        icon_color = "#cdd6f4" if self.is_dark else "#475569"

        if self.is_dark:
            btn_sec_style = (
                "QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
                "QPushButton:hover { background-color: #45475a; border-color: #585b70; }"
                "QPushButton:pressed { background-color: #585b70; }"
            )
        else:
            btn_sec_style = (
                "QPushButton { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
                "QPushButton:hover { background-color: #f1f5f9; border-color: #94a3b8; }"
                "QPushButton:pressed { background-color: #e2e8f0; }"
            )

        self.btn_copy = QPushButton("Copier")
        self.btn_copy.setStyleSheet(btn_sec_style)
        self.btn_copy.setIcon(create_icon("copy", icon_color, 14))
        self.btn_copy.clicked.connect(self.snippets_widget._copy_code)
        bottom_layout.addWidget(self.btn_copy)

        self.btn_fullscreen = QPushButton("Plein écran")
        self.btn_fullscreen.setStyleSheet(btn_sec_style)
        self.btn_fullscreen.setIcon(create_icon("fullscreen", icon_color, 14))
        self.btn_fullscreen.setToolTip("Basculer la boîte de dialogue en plein écran (F11)")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        bottom_layout.addWidget(self.btn_fullscreen)

        bottom_layout.addStretch()

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.setStyleSheet(btn_sec_style)
        self.btn_cancel.setIcon(create_icon("close", icon_color, 14))
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_new_tab = QPushButton("Ouvrir dans un nouvel onglet")
        self.btn_new_tab.setStyleSheet(btn_sec_style)
        self.btn_new_tab.setIcon(create_icon("new", icon_color, 14))
        self.btn_new_tab.clicked.connect(self._on_open_new_tab)
        bottom_layout.addWidget(self.btn_new_tab)

        self.btn_insert = QPushButton("Insérer dans l'éditeur")
        self.btn_insert.setDefault(True)
        self.btn_insert.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: #ffffff; font-weight: bold; border: none; padding: 6px 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:pressed { background-color: #1e40af; }"
        )
        self.btn_insert.setIcon(create_icon("step", "#ffffff", 14))
        self.btn_insert.clicked.connect(self._on_insert_clicked)
        bottom_layout.addWidget(self.btn_insert)

        main_layout.addLayout(bottom_layout)

    def _apply_compat_styles(self):
        icon_color = "#cdd6f4" if self.is_dark else "#475569"
        if hasattr(self, "btn_copy"):
            self.btn_copy.setIcon(create_icon("copy", icon_color, 14))
        if hasattr(self, "btn_fullscreen"):
            self.btn_fullscreen.setIcon(create_icon("fullscreen", icon_color, 14))
        if hasattr(self, "btn_cancel"):
            self.btn_cancel.setIcon(create_icon("close", icon_color, 14))
        if hasattr(self, "btn_new_tab"):
            self.btn_new_tab.setIcon(create_icon("new", icon_color, 14))
        if hasattr(self, "btn_insert"):
            self.btn_insert.setIcon(create_icon("step", "#ffffff", 14))

        if self.is_dark:
            self.search_input.setStyleSheet(
                "QLineEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #89b4fa; }"
            )
            self.list_widget.setStyleSheet(
                "QListWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #cdd6f4; }"
                "QListWidget::item:hover { background-color: #313244; }"
                "QListWidget::item:selected { background-color: #45475a; color: #ffffff; font-weight: bold; }"
            )
            self.preview_editor.setStyleSheet(
                "QPlainTextEdit { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }"
            )
        else:
            self.search_input.setStyleSheet(
                "QLineEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #3b82f6; }"
            )
            self.list_widget.setStyleSheet(
                "QListWidget { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #1e293b; }"
                "QListWidget::item:hover { background-color: #f1f5f9; }"
                "QListWidget::item:selected { background-color: #e2e8f0; color: #0f172a; font-weight: bold; }"
            )
            self.preview_editor.setStyleSheet(
                "QPlainTextEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; }"
            )

    def _sync_compatibility_list(self):
        """Populates and filters self.list_widget for backward compatibility."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        query = self.search_input.text().strip().lower()
        all_snippets = get_all_snippets_flat()

        matched = []
        for s in all_snippets:
            if query:
                searchable = f"{s.title} {s.category} {s.desc} {s.filename} {s.code}".lower()
                if query not in searchable:
                    continue
            item = QListWidgetItem()
            item.setText(f"{s.title}\n  • {s.category}")
            item.setData(Qt.UserRole, {
                "title": s.title,
                "category": s.category,
                "filename": s.filename,
                "filepath": s.code_file,
                "code": s.code,
                "desc": s.desc,
                "lines_count": s.lines_count,
                "snippet_obj": s
            })
            self.list_widget.addItem(item)
            matched.append(s)

        self.list_widget.blockSignals(False)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            first = matched[0]
            self.selected_code = first.code
            self.selected_title = first.title
            self.preview_editor.setPlainText(first.code)
            self.snippets_widget._on_snippet_selected(first)
        else:
            self.selected_code = ""
            self.selected_title = ""

    def _on_compat_list_row_changed(self, row: int):
        if row < 0 or row >= self.list_widget.count():
            return
        item = self.list_widget.item(row)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if data:
            self.selected_code = data["code"]
            self.selected_title = data["title"]
            self.preview_editor.setPlainText(self.selected_code)
            if "snippet_obj" in data:
                self.snippets_widget._on_snippet_selected(data["snippet_obj"])

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
