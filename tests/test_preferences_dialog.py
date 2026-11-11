"""
Unit tests for PreferencesDialog, theme modes, code color customization, and editor settings.
"""

import unittest
import os
import tempfile
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
from database import DatabaseManager
from ui.preferences_dialog import PreferencesDialog
from ui.editor import AlgoCodeEditor, DEFAULT_SYNTAX_COLORS_DARK, DEFAULT_SYNTAX_COLORS_LIGHT

app = QApplication.instance() or QApplication([])


class TestPreferencesDialog(unittest.TestCase):
    def setUp(self):
        self.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_file.close()
        self.db = DatabaseManager(self.temp_db_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_db_file.name):
            try:
                os.remove(self.temp_db_file.name)
            except OSError:
                pass

    def test_preferences_dialog_init_and_navigation(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        self.assertIsNotNone(dlg.tree)
        self.assertIsNotNone(dlg.pages)
        self.assertEqual(dlg.tree.topLevelItemCount(), 2)

        # Check top level items
        item_app = dlg.tree.topLevelItem(0)
        self.assertIn("Thème", item_app.text(0))
        self.assertEqual(item_app.childCount(), 2)

        item_editor = dlg.tree.topLevelItem(1)
        self.assertIn("Éditeur", item_editor.text(0))
        self.assertEqual(item_editor.childCount(), 2)

        # Test selecting page via tree
        child_item = item_editor.child(1) # Couleurs de syntaxe
        dlg.tree.setCurrentItem(child_item)
        self.assertEqual(dlg.pages.currentIndex(), 3)
        dlg.close()

    def test_theme_mode_selection_and_saving(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        
        # Default is system
        self.assertTrue(dlg.rb_system.isChecked())

        # Select Dark mode
        dlg.rb_dark.setChecked(True)
        dlg.apply_preferences()

        # Verify DB
        self.assertEqual(self.db.get_theme_mode(), "dark")
        self.assertTrue(self.db.is_dark_mode())

        # Select Light mode
        dlg.rb_light.setChecked(True)
        dlg.apply_preferences()
        self.assertEqual(self.db.get_theme_mode(), "light")
        self.assertFalse(self.db.is_dark_mode())

        # Select System mode
        dlg.rb_system.setChecked(True)
        dlg.apply_preferences()
        self.assertEqual(self.db.get_theme_mode(), "system")
        dlg.close()

    def test_editor_settings_customization(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        dlg.spin_font_size.setValue(16)
        dlg.spin_tab_size.setValue(2)
        dlg.chk_line_numbers.setChecked(False)
        dlg.chk_highlight_line.setChecked(False)

        dlg.apply_preferences()

        saved = self.db.get_editor_settings()
        self.assertEqual(saved["font_size"], 16)
        self.assertEqual(saved["tab_size"], 2)
        self.assertFalse(saved["show_line_numbers"])
        self.assertFalse(saved["highlight_current_line"])

        # Test applying to AlgoCodeEditor
        editor = AlgoCodeEditor(is_dark=False)
        editor.apply_settings(saved)
        self.assertEqual(editor.font().pointSize(), 16)
        self.assertEqual(editor.tab_size, 2)
        self.assertFalse(editor.show_line_numbers)
        self.assertFalse(editor.highlight_line_enabled)
        dlg.close()

    def test_syntax_colors_customization_and_reset(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        
        # Set light palette in selector
        dlg.combo_color_palette_mode.setCurrentIndex(1)
        test_color = "#ff007f"
        dlg.colors_light["keyword"] = test_color
        dlg.color_buttons["keyword"].set_color(test_color)
        dlg.apply_preferences()

        # Check DB
        saved_colors = self.db.get_syntax_colors(is_dark=False)
        self.assertEqual(saved_colors["keyword"], test_color)

        # Check editor syntax highlighting
        editor = AlgoCodeEditor(is_dark=False)
        editor.apply_settings({}, saved_colors)
        fmt = editor.highlighter.fmt_keyword
        self.assertEqual(fmt.foreground().color().name().lower(), test_color.lower())

        # Reset to defaults
        dlg._reset_syntax_colors()
        self.assertEqual(dlg.colors_light["keyword"], DEFAULT_SYNTAX_COLORS_LIGHT["keyword"])
        dlg.apply_preferences()

        saved_reset = self.db.get_syntax_colors(is_dark=False)
        self.assertEqual(saved_reset["keyword"], DEFAULT_SYNTAX_COLORS_LIGHT["keyword"])
        dlg.close()

    def test_global_theme_selection(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        dlg.combo_global_theme.setCurrentIndex(1)
        selected_text = dlg.combo_global_theme.currentText()
        dlg.apply_preferences()

        self.assertEqual(self.db.get_global_theme(), selected_text)
        dlg.close()


if __name__ == "__main__":
    unittest.main()
