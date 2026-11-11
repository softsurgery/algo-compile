"""
Preferences and Settings Dialog for Algoo IDE.
Features:
- Tree View navigation on the left.
- Theme Mode: Dark, Light, or System mode (auto-detect OS).
- Global theme palette options and accents.
- Code Editor settings: Font family, size, tab width, line numbers, highlight current line.
- Full syntax highlighting color customizer with interactive live code preview.
"""

import os
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QRadioButton, QButtonGroup,
    QComboBox, QSpinBox, QCheckBox, QColorDialog, QFrame, QSplitter,
    QScrollArea, QGridLayout, QMessageBox, QGroupBox
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from database import get_database, DatabaseManager
from ui.editor import (
    AlgoCodeEditor, DEFAULT_SYNTAX_COLORS_DARK, DEFAULT_SYNTAX_COLORS_LIGHT
)
from ui.icons import create_icon
from ui.styles import DARK_THEME, LIGHT_THEME
from ui.theme_utils import detect_system_dark_mode


SAMPLE_ALGO_CODE = """ALGORITHME ExemplePreferences
// Aperçu en temps réel de vos polices et couleurs
DEBUT
    Pour i de 1 à 5 Faire
        Si i Mod 2 = 0 Alors
            Ecrire("Nombre pair : ", i)
        Sinon
            Ecrire("Nombre impair : ", i)
        FinSi
    FinPour
FIN
Tableau de déclaration des objets globaux
Objet   Type
i       Entier
"""


class ColorButton(QPushButton):
    """Button showing a color swatch and hex code, opening QColorDialog on click."""
    color_changed = pyqtSignal(str)

    def __init__(self, color_hex: str, parent=None):
        super().__init__(parent)
        self._color_hex = color_hex
        self.setFixedHeight(28)
        self.setMinimumWidth(110)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._pick_color)
        self._update_appearance()

    def color(self) -> str:
        return self._color_hex

    def set_color(self, hex_val: str):
        self._color_hex = hex_val
        self._update_appearance()

    def _update_appearance(self):
        c = QColor(self._color_hex)
        # Determine contrast text color
        brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
        text_color = "#000000" if brightness > 140 else "#ffffff"

        self.setText(self._color_hex.upper())
        self.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {self._color_hex};"
            f"  color: {text_color};"
            f"  font-family: monospace;"
            f"  font-weight: bold;"
            f"  border: 1px solid rgba(0,0,0,0.25);"
            f"  border-radius: 4px;"
            f"  padding: 2px 8px;"
            f"}}"
            f"QPushButton:hover {{"
            f"  border: 2px solid #89b4fa;"
            f"}}"
        )

    def _pick_color(self):
        initial = QColor(self._color_hex)
        chosen = QColorDialog.getColor(initial, self, "Choisir une couleur")
        if chosen.isValid():
            self.set_color(chosen.name())
            self.color_changed.emit(chosen.name())


class PreferencesDialog(QDialog):
    """Modern Preferences dialog with TreeView navigation and live code preview."""

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
        self.resize(920, 640)
        self.setMinimumSize(780, 520)

        # Load current preferences from DB
        self.current_theme_mode = self.db.get_theme_mode(default="system")
        self.current_global_theme = self.db.get_global_theme(default="catppuccin")
        self.editor_settings = self.db.get_editor_settings()
        self.colors_dark = dict(DEFAULT_SYNTAX_COLORS_DARK)
        self.colors_dark.update(self.db.get_syntax_colors(is_dark=True))
        self.colors_light = dict(DEFAULT_SYNTAX_COLORS_LIGHT)
        self.colors_light.update(self.db.get_syntax_colors(is_dark=False))

        self._setup_ui()
        self._load_values()
        self.set_dark_mode(self.is_dark)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Main splitter (Tree view on left, Pages on right)
        self.splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Panel: Tree View
        # -------------------------------------------------------------
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(230)
        self.tree.setAnimated(True)

        # Category 1: Apparence & Thème
        cat_app = QTreeWidgetItem(self.tree, ["Apparence & Thème"])
        cat_app.setFont(0, QFont("SansSerif", 10, QFont.Bold))
        cat_app.setIcon(0, create_icon("theme", size=18))

        self.item_theme = QTreeWidgetItem(cat_app, ["Mode de thème"])
        self.item_theme.setData(0, Qt.UserRole, 0)
        self.item_palette = QTreeWidgetItem(cat_app, ["Thème global & Palette"])
        self.item_palette.setData(0, Qt.UserRole, 1)

        # Category 2: Éditeur de code
        cat_ed = QTreeWidgetItem(self.tree, ["Éditeur de code"])
        cat_ed.setFont(0, QFont("SansSerif", 10, QFont.Bold))
        cat_ed.setIcon(0, create_icon("doc", size=18))

        self.item_font = QTreeWidgetItem(cat_ed, ["Police & Affichage"])
        self.item_font.setData(0, Qt.UserRole, 2)
        self.item_colors = QTreeWidgetItem(cat_ed, ["Couleurs de syntaxe"])
        self.item_colors.setData(0, Qt.UserRole, 3)

        self.tree.expandAll()
        self.tree.currentItemChanged.connect(self._on_tree_item_changed)
        self.splitter.addWidget(self.tree)

        # -------------------------------------------------------------
        # Right Panel: Stacked Pages
        # -------------------------------------------------------------
        self.pages = QStackedWidget()

        self.page_theme = self._create_page_theme()
        self.page_palette = self._create_page_palette()
        self.page_editor = self._create_page_editor()
        self.page_colors = self._create_page_colors()

        self.pages.addWidget(self.page_theme)    # Index 0
        self.pages.addWidget(self.page_palette)  # Index 1
        self.pages.addWidget(self.page_editor)   # Index 2
        self.pages.addWidget(self.page_colors)   # Index 3

        self.splitter.addWidget(self.pages)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        main_layout.addWidget(self.splitter, 1)

        # -------------------------------------------------------------
        # Bottom Buttons
        # -------------------------------------------------------------
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.btn_defaults = QPushButton("Rétablir par défaut")
        self.btn_defaults.clicked.connect(self._on_reset_defaults)
        bottom_layout.addWidget(self.btn_defaults)

        bottom_layout.addStretch()

        self.btn_apply = QPushButton("Appliquer")
        self.btn_apply.clicked.connect(self.apply_preferences)
        bottom_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setStyleSheet("font-weight: bold;")
        self.btn_ok.clicked.connect(self._on_ok_clicked)
        bottom_layout.addWidget(self.btn_ok)

        main_layout.addLayout(bottom_layout)

        # Select first page by default
        self.tree.setCurrentItem(self.item_theme)

    # -----------------------------------------------------------------
    # Pages Construction
    # -----------------------------------------------------------------
    def _create_page_theme(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        header = QLabel("Mode de Thème (Thème Global)")
        header.setFont(QFont("SansSerif", 13, QFont.Bold))
        layout.addWidget(header)

        desc = QLabel(
            "Choisissez le mode d'affichage de l'environnement de développement. "
            "Le mode Système s'adapte automatiquement aux réglages de votre système d'exploitation."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6c7086;" if self.is_dark else "color: #64748b;")
        layout.addWidget(desc)

        box = QGroupBox("Sélectionnez le mode :")
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(12)

        self.btn_group_mode = QButtonGroup(self)

        self.rb_system = QRadioButton("💻  Système (Automatique)")
        self.rb_system.setToolTip("Suit automatiquement le thème clair/sombre de votre système d'exploitation")
        self.btn_group_mode.addButton(self.rb_system, 0)
        box_layout.addWidget(self.rb_system)

        self.rb_light = QRadioButton("☀️  Mode Clair (Light)")
        self.rb_light.setToolTip("Active en permanence le thème clair style Thonny / Slate")
        self.btn_group_mode.addButton(self.rb_light, 1)
        box_layout.addWidget(self.rb_light)

        self.rb_dark = QRadioButton("🌙  Mode Sombre (Dark)")
        self.rb_dark.setToolTip("Active en permanence le thème sombre moderne Catppuccin Mocha")
        self.btn_group_mode.addButton(self.rb_dark, 2)
        box_layout.addWidget(self.rb_dark)

        layout.addWidget(box)

        # System detection info card
        sys_detected = "Sombre (Dark)" if detect_system_dark_mode() else "Clair (Light)"
        self.lbl_sys_info = QLabel(f"ℹ️  Thème système actuellement détecté : <b>{sys_detected}</b>")
        self.lbl_sys_info.setStyleSheet("padding: 8px; border-radius: 6px; background-color: rgba(137, 180, 250, 0.12);")
        layout.addWidget(self.lbl_sys_info)

        layout.addStretch()
        return page

    def _create_page_palette(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        header = QLabel("Thème global & Variantes de Palette")
        header.setFont(QFont("SansSerif", 13, QFont.Bold))
        layout.addWidget(header)

        desc = QLabel("Personnalisez le style visuel de l'interface et les teintes d'accentuation.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        form_frame = QFrame()
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(12)

        form_layout.addWidget(QLabel("Palette visuelle globale :"), 0, 0)
        self.combo_global_theme = QComboBox()
        self.combo_global_theme.addItems([
            "Catppuccin (Mocha & Latte)",
            "Slate Moderne (Épuré)",
            "Nordic Minimal"
        ])
        form_layout.addWidget(self.combo_global_theme, 0, 1)

        form_layout.addWidget(QLabel("Couleur d'accentuation :"), 1, 0)
        self.combo_accent = QComboBox()
        self.combo_accent.addItems([
            "Bleu Algoo (#89b4fa / #2563eb)",
            "Mauve / Lavande (#cba6f7)",
            "Émeraude (#a6e3a1)",
            "Flamme / Corail (#fab387)"
        ])
        form_layout.addWidget(self.combo_accent, 1, 1)

        layout.addWidget(form_frame)
        layout.addStretch()
        return page

    def _create_page_editor(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        header = QLabel("Paramètres de l'Éditeur de code")
        header.setFont(QFont("SansSerif", 13, QFont.Bold))
        layout.addWidget(header)

        # Font and Tabs
        grid_frame = QFrame()
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)

        grid.addWidget(QLabel("Police de caractères :"), 0, 0)
        self.combo_font_family = QComboBox()
        self.combo_font_family.addItems([
            "JetBrains Mono",
            "Consolas",
            "Fira Code",
            "Source Code Pro",
            "Courier New",
            "Monospace"
        ])
        grid.addWidget(self.combo_font_family, 0, 1)

        grid.addWidget(QLabel("Taille de police (pt) :"), 1, 0)
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 32)
        self.spin_font_size.setValue(11)
        grid.addWidget(self.spin_font_size, 1, 1)

        grid.addWidget(QLabel("Taille de tabulation :"), 2, 0)
        self.spin_tab_size = QSpinBox()
        self.spin_tab_size.setRange(2, 8)
        self.spin_tab_size.setSingleStep(2)
        self.spin_tab_size.setValue(4)
        grid.addWidget(self.spin_tab_size, 2, 1)

        layout.addWidget(grid_frame)

        # Checkboxes
        box = QGroupBox("Affichage et comportement")
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(8)

        self.chk_line_numbers = QCheckBox("Afficher les numéros de ligne")
        self.chk_line_numbers.setChecked(True)
        box_layout.addWidget(self.chk_line_numbers)

        self.chk_highlight_line = QCheckBox("Surligner la ligne courante")
        self.chk_highlight_line.setChecked(True)
        box_layout.addWidget(self.chk_highlight_line)

        self.chk_auto_indent = QCheckBox("Indentation automatique après une structure (Si, Pour, etc.)")
        self.chk_auto_indent.setChecked(True)
        box_layout.addWidget(self.chk_auto_indent)

        layout.addWidget(box)
        layout.addStretch()
        return page

    def _create_page_colors(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        header = QLabel("Couleurs de Syntaxe du Code")
        header.setFont(QFont("SansSerif", 13, QFont.Bold))
        layout.addWidget(header)

        desc = QLabel(
            "Personnalisez les couleurs de chaque élément syntaxique pour vos algorithmes. "
            "Les modifications s'affichent instantanément dans l'aperçu ci-dessous."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Mode selector for color palette
        mode_bar = QHBoxLayout()
        mode_bar.addWidget(QLabel("Modifier les couleurs pour :"))
        self.combo_color_palette_mode = QComboBox()
        self.combo_color_palette_mode.addItems(["Thème Sombre (Dark)", "Thème Clair (Light)"])
        self.combo_color_palette_mode.currentIndexChanged.connect(self._on_color_palette_mode_changed)
        mode_bar.addWidget(self.combo_color_palette_mode)
        mode_bar.addStretch()

        self.btn_reset_colors = QPushButton("Réinitialiser couleurs")
        self.btn_reset_colors.clicked.connect(self._reset_syntax_colors)
        mode_bar.addWidget(self.btn_reset_colors)
        layout.addLayout(mode_bar)

        # Color Grid
        color_frame = QFrame()
        self.color_grid = QGridLayout(color_frame)
        self.color_grid.setSpacing(8)

        # Color items
        self.color_buttons: Dict[str, ColorButton] = {}
        tokens = [
            ("keyword", "Mots-clés (ALGORITHME, DEBUT, FIN)", 0, 0),
            ("control", "Structures de contrôle (Si, Pour, TantQue)", 0, 1),
            ("type", "Types de données (Entier, Réel, Tableau)", 1, 0),
            ("builtin", "Fonctions prédéfinies (Lire, Ecrire)", 1, 1),
            ("operator", "Opérateurs (←, Div, Mod, Et, Ou)", 2, 0),
            ("string", "Chaînes de caractères (\"...\")", 2, 1),
            ("literal", "Nombres & Booléens (42, Vrai, Faux)", 3, 0),
            ("comment", "Commentaires (// ...)", 3, 1),
        ]

        for token, label_text, r, c in tokens:
            col_idx = c * 2
            lbl = QLabel(label_text)
            btn = ColorButton("#89b4fa")
            btn.color_changed.connect(lambda hex_val, t=token: self._on_token_color_changed(t, hex_val))
            self.color_buttons[token] = btn
            self.color_grid.addWidget(lbl, r, col_idx)
            self.color_grid.addWidget(btn, r, col_idx + 1)

        layout.addWidget(color_frame)

        # Live Code Preview
        lbl_preview = QLabel("Aperçu du code en temps réel :")
        lbl_preview.setFont(QFont("SansSerif", 9, QFont.Bold))
        layout.addWidget(lbl_preview)

        self.preview_editor = AlgoCodeEditor(is_dark=self.is_dark)
        self.preview_editor.setReadOnly(True)
        self.preview_editor.setFixedHeight(150)
        self.preview_editor.setPlainText(SAMPLE_ALGO_CODE)
        layout.addWidget(self.preview_editor)

        return page

    # -----------------------------------------------------------------
    # Navigation & Value Synchronization
    # -----------------------------------------------------------------
    def _on_tree_item_changed(self, current, _):
        if not current:
            return
        page_idx = current.data(0, Qt.UserRole)
        if page_idx is not None:
            self.pages.setCurrentIndex(page_idx)

    def _load_values(self):
        # 1. Mode
        mode = self.current_theme_mode
        if mode == "light":
            self.rb_light.setChecked(True)
        elif mode == "dark":
            self.rb_dark.setChecked(True)
        else:
            self.rb_system.setChecked(True)

        # 2. Editor settings
        ed = self.editor_settings
        idx = self.combo_font_family.findText(ed.get("font_family", "JetBrains Mono"))
        if idx >= 0:
            self.combo_font_family.setCurrentIndex(idx)
        self.spin_font_size.setValue(ed.get("font_size", 11))
        self.spin_tab_size.setValue(ed.get("tab_size", 4))
        self.chk_line_numbers.setChecked(ed.get("show_line_numbers", True))
        self.chk_highlight_line.setChecked(ed.get("highlight_current_line", True))
        self.chk_auto_indent.setChecked(ed.get("auto_indent", True))

        # 3. Colors
        is_dark_active = (self.current_theme_mode == "dark") or (
            self.current_theme_mode == "system" and detect_system_dark_mode()
        )
        self.combo_color_palette_mode.setCurrentIndex(0 if is_dark_active else 1)
        self._sync_color_buttons()
        self._update_preview()

    def _on_color_palette_mode_changed(self, idx: int):
        self._sync_color_buttons()
        self._update_preview()

    def _sync_color_buttons(self):
        is_dark_palette = (self.combo_color_palette_mode.currentIndex() == 0)
        active_colors = self.colors_dark if is_dark_palette else self.colors_light
        for token, btn in self.color_buttons.items():
            if token in active_colors:
                btn.set_color(active_colors[token])

    def _on_token_color_changed(self, token: str, hex_val: str):
        is_dark_palette = (self.combo_color_palette_mode.currentIndex() == 0)
        if is_dark_palette:
            self.colors_dark[token] = hex_val
        else:
            self.colors_light[token] = hex_val
        self._update_preview()

    def _reset_syntax_colors(self):
        is_dark_palette = (self.combo_color_palette_mode.currentIndex() == 0)
        if is_dark_palette:
            self.colors_dark = dict(DEFAULT_SYNTAX_COLORS_DARK)
        else:
            self.colors_light = dict(DEFAULT_SYNTAX_COLORS_LIGHT)
        self._sync_color_buttons()
        self._update_preview()

    def _update_preview(self):
        is_dark_palette = (self.combo_color_palette_mode.currentIndex() == 0)
        active_colors = self.colors_dark if is_dark_palette else self.colors_light

        self.preview_editor.set_dark_mode(is_dark_palette, active_colors)
        ed_settings = self._collect_editor_settings()
        self.preview_editor.apply_settings(ed_settings, active_colors)

    def _collect_editor_settings(self) -> Dict[str, Any]:
        return {
            "font_family": self.combo_font_family.currentText(),
            "font_size": self.spin_font_size.value(),
            "tab_size": self.spin_tab_size.value(),
            "show_line_numbers": self.chk_line_numbers.isChecked(),
            "highlight_current_line": self.chk_highlight_line.isChecked(),
            "auto_indent": self.chk_auto_indent.isChecked(),
        }

    def _on_reset_defaults(self):
        res = QMessageBox.question(
            self,
            "Rétablir par défaut",
            "Voulez-vous réinitialiser toutes les préférences (mode système, polices et couleurs) ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            self.rb_system.setChecked(True)
            self.combo_global_theme.setCurrentIndex(0)
            self.combo_accent.setCurrentIndex(0)
            self.combo_font_family.setCurrentIndex(0)
            self.spin_font_size.setValue(11)
            self.spin_tab_size.setValue(4)
            self.chk_line_numbers.setChecked(True)
            self.chk_highlight_line.setChecked(True)
            self.chk_auto_indent.setChecked(True)
            self.colors_dark = dict(DEFAULT_SYNTAX_COLORS_DARK)
            self.colors_light = dict(DEFAULT_SYNTAX_COLORS_LIGHT)
            self._sync_color_buttons()
            self._update_preview()

    def apply_preferences(self):
        """Saves settings to database and notifies parent to apply them immediately."""
        # 1. Mode
        if self.rb_light.isChecked():
            chosen_mode = "light"
        elif self.rb_dark.isChecked():
            chosen_mode = "dark"
        else:
            chosen_mode = "system"

        self.db.set_theme_mode(chosen_mode)

        # 2. Global theme and accent
        self.db.set_global_theme(self.combo_global_theme.currentText())

        # 3. Editor settings
        ed = self._collect_editor_settings()
        self.db.set_editor_settings(ed)

        # 4. Custom colors
        self.db.set_syntax_colors(self.colors_dark, is_dark=True)
        self.db.set_syntax_colors(self.colors_light, is_dark=False)

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
        self.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)

        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background-color: {'#181825' if is_dark else '#ffffff'}; "
            f"border: 1px solid {'#313244' if is_dark else '#e2e8f0'}; border-radius: 6px; padding: 4px; }}"
        )
        self.btn_apply.setIcon(create_icon("step", icon_color, 14))
        self.btn_cancel.setIcon(create_icon("close", icon_color, 14))
        self.btn_defaults.setIcon(create_icon("refresh", icon_color, 14))
