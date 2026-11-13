"""
Syntax highlighting colors and live code preview page for PreferencesDialog.
"""

from typing import Dict, Any, List, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QButtonGroup, QFrame, QScrollArea
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QSize
from ui.components import AppRadioButton, AppSelect
from ui.editor import AlgoCodeEditor
from ui.editor_themes import SYNTAX_PRESETS
from ui.dialogs.preferences_dialog.header import create_section_header
from ui.icons import create_icon

SAMPLE_ALGO_CODE = """ALGORITHME ExemplePreferences
# Aperçu en temps réel de votre jeu de couleurs
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


class ColorsPage(QScrollArea):
    """Scrollable page for choosing syntax color presets and live previewing them."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setObjectName("colors_scroll_area")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("QScrollArea#colors_scroll_area { background: transparent; }")
        self._setup_ui()

    def _setup_ui(self):
        container = QWidget()
        container.setObjectName("colors_container")
        container.setStyleSheet("QWidget#colors_container { background: transparent; }")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        layout.addWidget(create_section_header(
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

        self.combo_syntax_preset = AppSelect(items=list(SYNTAX_PRESETS.keys()))
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
        self.chip_labels: List[Tuple[str, QLabel]] = []
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
        self.rb_preview_dark = AppRadioButton("Mode Sombre", icon_size=18)
        self.rb_preview_light = AppRadioButton("Mode Clair", icon_size=18)
        self.btn_preview_group.addButton(self.rb_preview_dark, 0)
        self.btn_preview_group.addButton(self.rb_preview_light, 1)

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

        self.setWidget(container)

    def update_chips_and_preview(self, editor_settings: Dict[str, Any]):
        preset_name = self.combo_syntax_preset.currentText()
        preset = SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])
        self.lbl_preset_desc.setText(preset.get("description", ""))

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
        self.preview_editor.apply_settings(editor_settings, colors)

    def update_icons(self, is_dark: bool):
        self.rb_preview_dark.setIcon(create_icon("moon", "#89b4fa" if is_dark else "#2563eb", size=18))
        self.rb_preview_light.setIcon(create_icon("sun", "#f59e0b", size=18))
