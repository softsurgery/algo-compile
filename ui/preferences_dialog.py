"""
Preferences and Settings Dialog for Algoo IDE.
Features:
- Tree View navigation on the left (Thème, Éditeur de code).
- Theme Mode: Dark, Light, or System mode with dedicated crisp vector icons.
- Code Editor settings: Font family, size, tab width, line numbers, highlight current line.
- Syntax Highlighting Presets: Beautiful curated color palettes applying to both Dark and Light modes.
- Interactive live code preview for both dark and light modes.
"""

from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QRadioButton, QButtonGroup,
    QComboBox, QSpinBox, QCheckBox, QFrame, QSplitter,
    QScrollArea, QGridLayout, QMessageBox, QGroupBox,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from database import get_database, DatabaseManager
from ui.editor import (
    AlgoCodeEditor, SYNTAX_PRESETS, DEFAULT_SYNTAX_COLORS_DARK, DEFAULT_SYNTAX_COLORS_LIGHT
)
from ui.icons import create_icon
from ui.styles import DARK_THEME, LIGHT_THEME
from ui.theme_utils import detect_system_dark_mode


SAMPLE_ALGO_CODE = """ALGORITHME ExemplePreferences
// Aperçu en temps réel de votre jeu de couleurs
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


class NoFocusDelegate(QStyledItemDelegate):
    """Prevents Qt from drawing dotted or rectangular focus artifacts on tree items."""
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.state &= ~QStyle.State_HasFocus
        super().paint(painter, opt, index)


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

    def _create_header(self, title: str, description: str) -> QWidget:
        """Helper to create a unified, elegant header block for each settings page."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("SansSerif", 13, QFont.Bold))
        lay.addWidget(lbl_title)

        lbl_desc = QLabel(description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setObjectName("pref_desc")
        lbl_desc.setFont(QFont("SansSerif", 9))
        lay.addWidget(lbl_desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("pref_separator")
        lay.addWidget(sep)

        return w

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
        self.tree = QTreeWidget()
        self.tree.setItemDelegate(NoFocusDelegate(self.tree))
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(12)
        self.tree.setRootIsDecorated(False)
        self.tree.setIconSize(QSize(22, 22))
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.setFocusPolicy(Qt.NoFocus)
        self.tree.setMinimumWidth(200)
        self.tree.setMaximumWidth(320)

        # Category 1: Thème
        self.item_theme = QTreeWidgetItem(self.tree, ["Thème"])
        self.item_theme.setData(0, Qt.UserRole, 0)
        self.item_theme.setSizeHint(0, QSize(0, 38))

        # Category 2: Éditeur de code
        self.cat_ed = QTreeWidgetItem(self.tree, ["Éditeur de code"])
        self.cat_ed.setFont(0, QFont("SansSerif", 10, QFont.Bold))
        self.cat_ed.setSizeHint(0, QSize(0, 38))

        self.item_font = QTreeWidgetItem(self.cat_ed, ["Police & Affichage"])
        self.item_font.setData(0, Qt.UserRole, 1)
        self.item_font.setSizeHint(0, QSize(0, 36))

        self.item_colors = QTreeWidgetItem(self.cat_ed, ["Couleurs de syntaxe"])
        self.item_colors.setData(0, Qt.UserRole, 2)
        self.item_colors.setSizeHint(0, QSize(0, 36))

        self.tree.expandAll()
        self.tree.currentItemChanged.connect(self._on_tree_item_changed)
        self.splitter.addWidget(self.tree)

        # -------------------------------------------------------------
        # Right Panel: Stacked Pages
        # -------------------------------------------------------------
        self.pages = QStackedWidget()
        self.pages.setMinimumWidth(560)

        self.page_theme = self._create_page_theme()
        self.page_editor = self._create_page_editor()
        self.page_colors = self._create_page_colors()

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

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(4, 2, 4, 2)
        bottom_layout.setSpacing(10)

        self.btn_defaults = QPushButton("Rétablir par défaut")
        self.btn_defaults.setCursor(Qt.PointingHandCursor)
        self.btn_defaults.setIconSize(QSize(18, 18))
        self.btn_defaults.clicked.connect(self._on_reset_defaults)
        bottom_layout.addWidget(self.btn_defaults)

        bottom_layout.addStretch()

        self.btn_apply = QPushButton("Appliquer")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setIconSize(QSize(18, 18))
        self.btn_apply.clicked.connect(self.apply_preferences)
        bottom_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setIconSize(QSize(18, 18))
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setIconSize(QSize(18, 18))
        self.btn_ok.setStyleSheet("font-weight: bold; min-width: 75px;")
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
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        layout.addWidget(self._create_header(
            "Thème de l'interface",
            "Choisissez le mode d'affichage de l'environnement de développement. "
            "Le mode Système s'adapte automatiquement aux réglages de votre système d'exploitation."
        ))

        box = QGroupBox("Mode d'affichage :")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 18, 16, 16)
        box_layout.setSpacing(14)

        self.btn_group_mode = QButtonGroup(self)

        self.rb_system = QRadioButton("Système (Automatique)")
        self.rb_system.setToolTip("Suit automatiquement le thème clair/sombre de votre système d'exploitation")
        self.rb_system.setStyleSheet("font-size: 11pt; padding: 4px 6px;")
        self.rb_system.setIconSize(QSize(24, 24))
        self.btn_group_mode.addButton(self.rb_system, 0)
        box_layout.addWidget(self.rb_system)

        self.rb_light = QRadioButton("Mode Clair (Light)")
        self.rb_light.setToolTip("Active en permanence le thème clair épuré")
        self.rb_light.setStyleSheet("font-size: 11pt; padding: 4px 6px;")
        self.rb_light.setIconSize(QSize(24, 24))
        self.btn_group_mode.addButton(self.rb_light, 1)
        box_layout.addWidget(self.rb_light)

        self.rb_dark = QRadioButton("Mode Sombre (Dark)")
        self.rb_dark.setToolTip("Active en permanence le thème sombre moderne")
        self.rb_dark.setStyleSheet("font-size: 11pt; padding: 4px 6px;")
        self.rb_dark.setIconSize(QSize(24, 24))
        self.btn_group_mode.addButton(self.rb_dark, 2)
        box_layout.addWidget(self.rb_dark)

        layout.addWidget(box)

        # System detection info card
        sys_detected = "Sombre (Dark)" if detect_system_dark_mode() else "Clair (Light)"
        self.lbl_sys_info = QLabel(f"ℹ️  Thème système actuellement détecté : <b>{sys_detected}</b>")
        self.lbl_sys_info.setObjectName("pref_sys_info")
        layout.addWidget(self.lbl_sys_info)

        layout.addStretch()
        return page

    def _create_page_editor(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        layout.addWidget(self._create_header(
            "Paramètres de l'Éditeur de code",
            "Configurez la police, la taille du texte, les tabulations et le confort visuel de saisie."
        ))

        # Font and Tabs frame
        grid_frame = QFrame()
        grid_frame.setObjectName("pref_card")
        grid = QGridLayout(grid_frame)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(14)

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

        grid.addWidget(QLabel("Taille de tabulation (espaces) :"), 2, 0)
        self.spin_tab_size = QSpinBox()
        self.spin_tab_size.setRange(2, 8)
        self.spin_tab_size.setSingleStep(2)
        self.spin_tab_size.setValue(4)
        grid.addWidget(self.spin_tab_size, 2, 1)

        layout.addWidget(grid_frame)

        # Checkboxes
        box = QGroupBox("Affichage et comportement")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 18, 16, 16)
        box_layout.setSpacing(12)

        self.chk_line_numbers = QCheckBox("Afficher les numéros de ligne dans la marge gauche")
        self.chk_line_numbers.setChecked(True)
        self.chk_line_numbers.setStyleSheet("padding: 2px 0px;")
        box_layout.addWidget(self.chk_line_numbers)

        self.chk_highlight_line = QCheckBox("Surligner la ligne courante active du curseur")
        self.chk_highlight_line.setChecked(True)
        self.chk_highlight_line.setStyleSheet("padding: 2px 0px;")
        box_layout.addWidget(self.chk_highlight_line)

        self.chk_auto_indent = QCheckBox("Indentation automatique après une structure (Si, Pour, TantQue...)")
        self.chk_auto_indent.setChecked(True)
        self.chk_auto_indent.setStyleSheet("padding: 2px 0px;")
        box_layout.addWidget(self.chk_auto_indent)

        layout.addWidget(box)
        layout.addStretch()
        return page

    def _create_page_colors(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        layout.addWidget(self._create_header(
            "Couleurs de Syntaxe du Code",
            "Choisissez un jeu de couleurs prédéfini (Preset) pour vos algorithmes. "
            "Chaque preset s'applique automatiquement et harmonieusement en mode sombre et en mode clair."
        ))

        # Preset selection frame
        card = QFrame()
        card.setObjectName("pref_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        lbl_preset = QLabel("Jeu de couleurs (Preset) :")
        lbl_preset.setFont(QFont("SansSerif", 10, QFont.Bold))
        top_row.addWidget(lbl_preset)

        self.combo_syntax_preset = QComboBox()
        self.combo_syntax_preset.addItems(list(SYNTAX_PRESETS.keys()))
        self.combo_syntax_preset.currentIndexChanged.connect(self._on_syntax_preset_changed)
        top_row.addWidget(self.combo_syntax_preset, 1)

        card_layout.addLayout(top_row)

        self.lbl_preset_desc = QLabel()
        self.lbl_preset_desc.setObjectName("pref_desc")
        self.lbl_preset_desc.setFont(QFont("SansSerif", 9))
        self.lbl_preset_desc.setWordWrap(True)
        card_layout.addWidget(self.lbl_preset_desc)

        # Color chips preview row (showing the 8 palette tokens)
        self.chips_layout = QHBoxLayout()
        self.chips_layout.setSpacing(6)
        self.chip_labels = []
        token_names = [
            ("keyword", "Mots-clés"),
            ("control", "Contrôle"),
            ("type", "Types"),
            ("builtin", "Fonctions"),
            ("operator", "Opérateurs"),
            ("string", "Chaînes"),
            ("literal", "Littéraux"),
            ("comment", "Commentaires"),
        ]
        for token_key, token_label in token_names:
            chip = QLabel(token_label)
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(26)
            chip.setStyleSheet("border-radius: 4px; font-weight: bold; font-size: 8.5pt; padding: 2px 6px;")
            self.chips_layout.addWidget(chip)
            self.chip_labels.append((token_key, chip))

        card_layout.addLayout(self.chips_layout)
        layout.addWidget(card)

        # Preview mode bar
        preview_bar = QHBoxLayout()
        preview_bar.setSpacing(14)
        lbl_preview = QLabel("Aperçu en temps réel :")
        lbl_preview.setFont(QFont("SansSerif", 10, QFont.Bold))
        preview_bar.addWidget(lbl_preview)

        self.btn_preview_group = QButtonGroup(self)
        self.rb_preview_dark = QRadioButton("🌙 Mode Sombre")
        self.rb_preview_dark.setIconSize(QSize(18, 18))
        self.rb_preview_light = QRadioButton("☀️ Mode Clair")
        self.rb_preview_light.setIconSize(QSize(18, 18))
        self.btn_preview_group.addButton(self.rb_preview_dark, 0)
        self.btn_preview_group.addButton(self.rb_preview_light, 1)

        self.rb_preview_dark.toggled.connect(self._update_chips_and_preview)
        self.rb_preview_light.toggled.connect(self._update_chips_and_preview)

        preview_bar.addWidget(self.rb_preview_dark)
        preview_bar.addWidget(self.rb_preview_light)
        preview_bar.addStretch()
        layout.addLayout(preview_bar)

        # Live Code Preview Editor
        self.preview_editor = AlgoCodeEditor(is_dark=self.is_dark)
        self.preview_editor.setReadOnly(True)
        self.preview_editor.setMinimumHeight(320)
        self.preview_editor.setPlainText(SAMPLE_ALGO_CODE)
        layout.addWidget(self.preview_editor, 1)

        scroll.setWidget(container)
        return scroll

    # -----------------------------------------------------------------
    # Navigation & Value Synchronization
    # -----------------------------------------------------------------
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

    def _on_syntax_preset_changed(self, _=None):
        preset_name = self.combo_syntax_preset.currentText()
        preset = SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])
        self.lbl_preset_desc.setText(preset.get("description", ""))
        self._update_chips_and_preview()

    def _update_chips_and_preview(self, _=None):
        preset_name = self.combo_syntax_preset.currentText()
        preset = SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])
        is_dark_preview = self.rb_preview_dark.isChecked()
        colors = preset["dark"] if is_dark_preview else preset["light"]

        # Update color chips
        for token_key, chip in self.chip_labels:
            color_hex = colors.get(token_key, "#888888")
            c = QColor(color_hex)
            brightness = (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000
            text_color = "#000000" if brightness > 140 else "#ffffff"
            chip.setStyleSheet(
                f"background-color: {color_hex};"
                f"color: {text_color};"
                f"border-radius: 4px;"
                f"font-weight: bold;"
                f"font-size: 8.5pt;"
                f"padding: 2px 6px;"
            )

        # Update preview editor
        self.preview_editor.set_dark_mode(is_dark_preview, colors)
        ed_settings = self._collect_editor_settings()
        self.preview_editor.apply_settings(ed_settings, colors)

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
        if self.rb_light.isChecked():
            chosen_mode = "light"
        elif self.rb_dark.isChecked():
            chosen_mode = "dark"
        else:
            chosen_mode = "system"

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
        self.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)

        if is_dark:
            tree_bg = "#181825"
            tree_border = "#313244"
            item_fg = "#cdd6f4"
            item_hover = "rgba(205, 214, 244, 0.08)"
            sel_bg = "#313244"
            sel_fg = "#89b4fa"
            icon_color = "#cdd6f4"
            sub_icon_color = "#89b4fa"
            handle_bg = "#45475a"
            card_bg = "#181825"
            card_border = "#313244"
            desc_fg = "#a6adc8"
            sep_color = "#313244"
            sys_card_bg = "rgba(137, 180, 250, 0.12)"
            sys_card_border = "rgba(137, 180, 250, 0.25)"
        else:
            tree_bg = "#f8fafc"
            tree_border = "#cbd5e1"
            item_fg = "#334155"
            item_hover = "#f1f5f9"
            sel_bg = "#e0e7ff"
            sel_fg = "#1d4ed8"
            icon_color = "#475569"
            sub_icon_color = "#2563eb"
            handle_bg = "#cbd5e1"
            card_bg = "#ffffff"
            card_border = "#e2e8f0"
            desc_fg = "#64748b"
            sep_color = "#e2e8f0"
            sys_card_bg = "rgba(37, 99, 235, 0.08)"
            sys_card_border = "rgba(37, 99, 235, 0.2)"

        # Style left tree view with minimal margin and NO square borders
        self.tree.setStyleSheet(
            f"QTreeWidget {{"
            f"  background-color: {tree_bg};"
            f"  border: 1px solid {tree_border};"
            f"  border-radius: 8px;"
            f"  padding: 4px 2px;"
            f"  outline: none;"
            f"  show-decoration-selected: 0;"
            f"}}"
            f"QTreeWidget::item {{"
            f"  padding: 6px 6px;"
            f"  margin: 1px 2px;"
            f"  border-radius: 6px;"
            f"  color: {item_fg};"
            f"  border: none;"
            f"  outline: none;"
            f"}}"
            f"QTreeWidget::item:hover {{"
            f"  background-color: {item_hover};"
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
        )

        # Style splitter handle
        self.splitter.setStyleSheet(
            f"QSplitter::handle:horizontal {{"
            f"  background-color: transparent;"
            f"  width: 6px;"
            f"}}"
            f"QSplitter::handle:horizontal:hover {{"
            f"  background-color: {handle_bg};"
            f"  border-radius: 3px;"
            f"}}"
        )

        # Style card containers, descriptions and separators inside pages
        card_style = (
            f"QFrame#pref_card {{"
            f"  background-color: {card_bg};"
            f"  border: 1px solid {card_border};"
            f"  border-radius: 8px;"
            f"}}"
            f"QGroupBox {{"
            f"  background-color: {card_bg};"
            f"  border: 1px solid {card_border};"
            f"  border-radius: 8px;"
            f"  margin-top: 12px;"
            f"  padding: 14px 14px 14px 14px;"
            f"  font-weight: bold;"
            f"}}"
            f"QGroupBox::title {{"
            f"  subcontrol-origin: margin;"
            f"  left: 14px;"
            f"  padding: 0 4px;"
            f"  color: {sel_fg};"
            f"}}"
            f"QLabel#pref_desc {{"
            f"  color: {desc_fg};"
            f"}}"
            f"QFrame#pref_separator {{"
            f"  border: none;"
            f"  background-color: {sep_color};"
            f"  height: 1px;"
            f"  max-height: 1px;"
            f"}}"
            f"QLabel#pref_sys_info {{"
            f"  background-color: {sys_card_bg};"
            f"  border: 1px solid {sys_card_border};"
            f"  border-radius: 6px;"
            f"  padding: 10px 14px;"
            f"}}"
        )
        self.pages.setStyleSheet(card_style)

        # Update icons on tree items
        if hasattr(self, "item_theme"):
            self.item_theme.setIcon(0, create_icon("theme", icon_color, size=24))
        if hasattr(self, "cat_ed"):
            self.cat_ed.setIcon(0, create_icon("settings", icon_color, size=24))
        if hasattr(self, "item_font"):
            self.item_font.setIcon(0, create_icon("font", sub_icon_color, size=22))
        if hasattr(self, "item_colors"):
            self.item_colors.setIcon(0, create_icon("syntax", sub_icon_color, size=22))

        # Update icons on theme mode radio options
        if hasattr(self, "rb_system"):
            self.rb_system.setIcon(create_icon("system", icon_color, size=24))
        if hasattr(self, "rb_light"):
            self.rb_light.setIcon(create_icon("sun", "#f59e0b", size=24))
        if hasattr(self, "rb_dark"):
            self.rb_dark.setIcon(create_icon("moon", "#89b4fa" if is_dark else "#2563eb", size=24))

        # Update preview mode icons
        if hasattr(self, "rb_preview_dark"):
            self.rb_preview_dark.setIcon(create_icon("moon", "#89b4fa" if is_dark else "#2563eb", size=18))
        if hasattr(self, "rb_preview_light"):
            self.rb_preview_light.setIcon(create_icon("sun", "#f59e0b", size=18))

        # Update button icons and sizes
        self.btn_apply.setIcon(create_icon("check", icon_color, size=20))
        self.btn_cancel.setIcon(create_icon("close", icon_color, size=20))
        self.btn_defaults.setIcon(create_icon("refresh", icon_color, size=20))
        self.btn_ok.setIcon(create_icon("check", "#ffffff", size=20))
