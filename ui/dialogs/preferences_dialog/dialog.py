"""
Preferences and Settings Dialog for Algoo IDE.
Features:
- Tree View navigation on the left (Thème, Éditeur de code).
- Theme Mode: Dark, Light, or System mode with dedicated crisp vector icons.
- Code Editor settings: Font family, size, tab width, line numbers, highlight current line.
- Syntax Highlighting Presets: Curated color palettes applying to both Dark and Light modes.
- Interactive live code preview for both dark and light modes.
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QStackedWidget, QSplitter,
    QFrame, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

from database import get_database, DatabaseManager
from ui.editor_themes import SYNTAX_PRESETS
from ui.theme_utils import detect_system_dark_mode, get_system_theme_watcher
from ui.dialogs.preferences_dialog.navigation import (
    NoFocusDelegate, PreferencesNavigationTree
)
from ui.dialogs.preferences_dialog.action_bar import PreferencesActionBar
from ui.dialogs.preferences_dialog.pages import (
    ThemePage, EditorPage, ColorsPage
)
from ui.dialogs.preferences_dialog.styles import apply_preferences_styles


class PreferencesDialog(QDialog):
    """Modern Preferences dialog with TreeView navigation, theme modes, and syntax presets."""

    settings_applied = pyqtSignal()

    def __init__(self, parent=None, is_dark: bool = False, db: Optional[DatabaseManager] = None):
        super().__init__(parent)
        self.db = db or get_database()
        self.is_dark = is_dark

        self.setWindowTitle("Préférences — Algoo")

        # Remove default icon in window header
        empty_pm = QPixmap(1, 1)
        empty_pm.fill(Qt.transparent)
        self.setWindowIcon(QIcon(empty_pm))

        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.resize(1080, 720)
        self.setMinimumSize(900, 600)

        # Load current preferences from DB
        self.current_theme_mode = self.db.get_theme_mode(default="system")
        self.current_syntax_preset = self.db.get_syntax_preset(default="Algoo")
        self.editor_settings = self.db.get_editor_settings()

        self._setup_ui()
        self._load_values()
        self.set_dark_mode(self.is_dark)

        # Connect live system theme watcher for immediate detection in dialog
        self.theme_watcher = get_system_theme_watcher()
        self.theme_watcher.theme_changed.connect(self._on_system_theme_changed)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Main splitter (Tree view on left, Pages on right)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(6)

        # -------------------------------------------------------------
        # Left Panel: Tree View
        # -------------------------------------------------------------
        self.tree = PreferencesNavigationTree(self)
        self.item_theme = self.tree.item_theme
        self.cat_ed = self.tree.cat_ed
        self.item_font = self.tree.item_font
        self.item_colors = self.tree.item_colors

        self.tree.currentItemChanged.connect(self._on_tree_item_changed)
        self.splitter.addWidget(self.tree)

        # -------------------------------------------------------------
        # Right Panel: Stacked Pages
        # -------------------------------------------------------------
        self.pages = QStackedWidget()
        self.pages.setMinimumWidth(560)

        self.page_theme = ThemePage(self)
        self.page_editor = EditorPage(self)
        self.page_colors = ColorsPage(self, is_dark=self.is_dark)

        # Expose subcomponent aliases for tests & backward-compatibility
        self.btn_group_mode = self.page_theme.btn_group_mode
        self.rb_system = self.page_theme.rb_system
        self.rb_light = self.page_theme.rb_light
        self.rb_dark = self.page_theme.rb_dark
        self.lbl_sys_info = self.page_theme.lbl_sys_info

        self.combo_font_family = self.page_editor.combo_font_family
        self.spin_font_size = self.page_editor.spin_font_size
        self.spin_tab_size = self.page_editor.spin_tab_size
        self.chk_line_numbers = self.page_editor.chk_line_numbers
        self.chk_highlight_line = self.page_editor.chk_highlight_line
        self.chk_auto_indent = self.page_editor.chk_auto_indent

        self.combo_syntax_preset = self.page_colors.combo_syntax_preset
        self.lbl_preset_desc = self.page_colors.lbl_preset_desc
        self.chips_layout = self.page_colors.chips_layout
        self.chip_labels = self.page_colors.chip_labels
        self.btn_preview_group = self.page_colors.btn_preview_group
        self.rb_preview_dark = self.page_colors.rb_preview_dark
        self.rb_preview_light = self.page_colors.rb_preview_light
        self.preview_editor = self.page_colors.preview_editor

        self.pages.addWidget(self.page_theme)   # Index 0
        self.pages.addWidget(self.page_editor)  # Index 1
        self.pages.addWidget(self.page_colors)  # Index 2

        self.splitter.addWidget(self.pages)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([240, 840])
        main_layout.addWidget(self.splitter, 1)

        # -------------------------------------------------------------
        # Bottom Buttons
        # -------------------------------------------------------------
        btn_sep = QFrame()
        btn_sep.setFrameShape(QFrame.HLine)
        btn_sep.setObjectName("pref_separator")
        main_layout.addWidget(btn_sep)

        self.action_bar = PreferencesActionBar(self)
        self.btn_defaults = self.action_bar.btn_defaults
        self.btn_apply = self.action_bar.btn_apply
        self.btn_cancel = self.action_bar.btn_cancel
        self.btn_ok = self.action_bar.btn_ok

        self.btn_defaults.clicked.connect(self._on_reset_defaults)
        self.btn_apply.clicked.connect(self.apply_preferences)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._on_ok_clicked)

        main_layout.addWidget(self.action_bar)

        # Wire color page preview signals
        self.combo_syntax_preset.currentIndexChanged.connect(self._on_syntax_preset_changed)
        self.rb_preview_dark.toggled.connect(self._update_chips_and_preview)
        self.rb_preview_light.toggled.connect(self._update_chips_and_preview)

        # Wire live theme mode selection
        self.btn_group_mode.buttonClicked.connect(self._on_theme_mode_radio_clicked)

        # Select first page by default
        self.tree.setCurrentItem(self.item_theme)

    def _on_tree_item_changed(self, current, _):
        if not current:
            return
        page_idx = current.data(0, Qt.UserRole)
        if page_idx is not None:
            self.pages.setCurrentIndex(page_idx)
        elif current.childCount() > 0:
            self.tree.setCurrentItem(current.child(0))

    def _load_values(self):
        # 1. Mode
        self.page_theme.set_selected_mode(self.current_theme_mode)

        # 2. Editor settings
        self.page_editor.set_editor_settings(self.editor_settings)

        # 3. Syntax preset
        saved_preset = self.current_syntax_preset
        idx = self.combo_syntax_preset.findText(saved_preset)
        if idx >= 0:
            self.combo_syntax_preset.setCurrentIndex(idx)
        else:
            self.combo_syntax_preset.setCurrentIndex(0)

        # Set preview mode initial state matching current effective mode
        is_dark_active = (self.current_theme_mode == "dark") or (
            self.current_theme_mode == "system" and detect_system_dark_mode()
        )
        if is_dark_active:
            self.rb_preview_dark.setChecked(True)
        else:
            self.rb_preview_light.setChecked(True)

        self._on_syntax_preset_changed()

    def _on_theme_mode_radio_clicked(self, _=None):
        """Immediately applies selected theme mode live across the dialog components and window bar."""
        chosen_mode = self.page_theme.get_selected_mode()
        self.db.set_theme_mode(chosen_mode)
        if chosen_mode == "system":
            effective_dark = detect_system_dark_mode()
        elif chosen_mode == "dark":
            effective_dark = True
        else:
            effective_dark = False

        self.set_dark_mode(effective_dark)
        if hasattr(self, "rb_preview_dark") and hasattr(self, "rb_preview_light"):
            if effective_dark:
                self.rb_preview_dark.setChecked(True)
            else:
                self.rb_preview_light.setChecked(True)
        self.settings_applied.emit()

    def _on_syntax_preset_changed(self, _=None):
        preset_name = self.combo_syntax_preset.currentText()
        preset = SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])
        self.lbl_preset_desc.setText(preset.get("description", ""))
        self._update_chips_and_preview()

    def _update_chips_and_preview(self, _=None):
        ed_settings = self._collect_editor_settings()
        self.page_colors.update_chips_and_preview(ed_settings)

    def _collect_editor_settings(self) -> Dict[str, Any]:
        return self.page_editor.get_editor_settings()

    def _on_reset_defaults(self):
        res = QMessageBox.question(
            self,
            "Rétablir par défaut",
            "Voulez-vous réinitialiser toutes les préférences (mode système, police et preset Algoo) ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            self.rb_system.setChecked(True)
            self.combo_font_family.setCurrentIndex(0)
            self.spin_font_size.setValue(11)
            self.spin_tab_size.setValue(4)
            self.chk_line_numbers.setChecked(True)
            self.chk_highlight_line.setChecked(True)
            self.chk_auto_indent.setChecked(True)
            idx = self.combo_syntax_preset.findText("Algoo")
            if idx >= 0:
                self.combo_syntax_preset.setCurrentIndex(idx)
            self._on_syntax_preset_changed()

    def apply_preferences(self):
        """Saves settings to database and notifies parent to apply them immediately."""
        # 1. Mode
        chosen_mode = self.page_theme.get_selected_mode()
        self.db.set_theme_mode(chosen_mode)

        # 2. Editor settings
        ed = self._collect_editor_settings()
        self.db.set_editor_settings(ed)

        # 3. Syntax preset & colors (applies to both dark and light modes)
        preset_name = self.combo_syntax_preset.currentText()
        preset = SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])
        self.db.set_syntax_preset(preset_name)
        self.db.set_syntax_colors(preset["dark"], is_dark=True)
        self.db.set_syntax_colors(preset["light"], is_dark=False)

        # Calculate effective dark mode
        if chosen_mode == "system":
            effective_dark = detect_system_dark_mode()
        else:
            effective_dark = (chosen_mode == "dark")

        self.set_dark_mode(effective_dark)

        # Notify parent MainWindow
        self.settings_applied.emit()

    def _on_ok_clicked(self):
        self.apply_preferences()
        self.accept()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        apply_preferences_styles(self, is_dark)

    def _on_system_theme_changed(self, is_dark: bool):
        """Reflects system theme transition live in the Preferences dialog and window manager."""
        from ui.theme_utils import apply_os_window_theme
        apply_os_window_theme(self, is_dark)
        if hasattr(self, "page_theme"):
            self.page_theme.update_system_info(is_dark)
            if self.page_theme.get_selected_mode() == "system":
                self.set_dark_mode(is_dark)
                if hasattr(self, "rb_preview_dark") and hasattr(self, "rb_preview_light"):
                    if is_dark:
                        self.rb_preview_dark.setChecked(True)
                    else:
                        self.rb_preview_light.setChecked(True)
