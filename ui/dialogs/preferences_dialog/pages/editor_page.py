"""
Code Editor settings page for PreferencesDialog (Font, Size, Tabs, Indentation).
"""

from typing import Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox,
    QCheckBox, QFrame, QGridLayout, QGroupBox
)
from ui.dialogs.preferences_dialog.header import create_section_header


class EditorPage(QWidget):
    """Page for configuring Code Editor font, tabs, and typing behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(16)

        layout.addWidget(create_section_header(
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

    def get_editor_settings(self) -> Dict[str, Any]:
        return {
            "font_family": self.combo_font_family.currentText(),
            "font_size": self.spin_font_size.value(),
            "tab_size": self.spin_tab_size.value(),
            "show_line_numbers": self.chk_line_numbers.isChecked(),
            "highlight_current_line": self.chk_highlight_line.isChecked(),
            "auto_indent": self.chk_auto_indent.isChecked(),
        }

    def set_editor_settings(self, ed: Dict[str, Any]):
        idx = self.combo_font_family.findText(ed.get("font_family", "JetBrains Mono"))
        if idx >= 0:
            self.combo_font_family.setCurrentIndex(idx)
        self.spin_font_size.setValue(ed.get("font_size", 11))
        self.spin_tab_size.setValue(ed.get("tab_size", 4))
        self.chk_line_numbers.setChecked(ed.get("show_line_numbers", True))
        self.chk_highlight_line.setChecked(ed.get("highlight_current_line", True))
        self.chk_auto_indent.setChecked(ed.get("auto_indent", True))
