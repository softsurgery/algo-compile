"""
Unit tests for PreferencesDialog, theme modes, syntax presets, and editor settings.
"""

import unittest
import os
import tempfile
from PyQt5.QtWidgets import QApplication
from database import DatabaseManager
from ui.preferences_dialog import PreferencesDialog
from ui.editor import (
    AlgoCodeEditor, SYNTAX_PRESETS, DEFAULT_SYNTAX_COLORS_DARK, DEFAULT_SYNTAX_COLORS_LIGHT
)

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

        # Check top level items: Thème and Éditeur de code
        item_theme = dlg.tree.topLevelItem(0)
        self.assertIn("Thème", item_theme.text(0))

        item_editor = dlg.tree.topLevelItem(1)
        self.assertIn("Éditeur", item_editor.text(0))
        self.assertEqual(item_editor.childCount(), 2)

        # Test selecting page via tree
        child_item = item_editor.child(1) # Couleurs de syntaxe
        dlg.tree.setCurrentItem(child_item)
        self.assertEqual(dlg.pages.currentIndex(), 2)

        # Select Thème
        dlg.tree.setCurrentItem(item_theme)
        self.assertEqual(dlg.pages.currentIndex(), 0)

        # Verify spacing and resizing configuration
        self.assertGreaterEqual(dlg.tree.minimumWidth(), 200)
        self.assertFalse(dlg.splitter.childrenCollapsible())
        self.assertGreaterEqual(item_theme.sizeHint(0).height(), 34)
        self.assertGreaterEqual(child_item.sizeHint(0).height(), 32)

        # Verify smooth splitter resize
        dlg.show()
        dlg.splitter.setSizes([260, 700])
        self.assertEqual(dlg.splitter.sizes()[0], 260)
        dlg.close()

    def test_theme_mode_selection_and_icons(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        
        # Verify vector icons on options
        self.assertFalse(dlg.rb_system.icon().isNull())
        self.assertFalse(dlg.rb_light.icon().isNull())
        self.assertFalse(dlg.rb_dark.icon().isNull())

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

    def test_syntax_presets_and_application(self):
        dlg = PreferencesDialog(parent=None, is_dark=False, db=self.db)
        
        # Verify presets exist
        self.assertIn("Algoo", SYNTAX_PRESETS)
        self.assertIn("VS Code", SYNTAX_PRESETS)
        self.assertIn("Monokai", SYNTAX_PRESETS)
        self.assertIn("Nord", SYNTAX_PRESETS)

        # Select VS Code preset
        idx = dlg.combo_syntax_preset.findText("VS Code")
        self.assertGreaterEqual(idx, 0)
        dlg.combo_syntax_preset.setCurrentIndex(idx)
        dlg.apply_preferences()

        # Check DB persistence
        self.assertEqual(self.db.get_syntax_preset(), "VS Code")
        saved_dark = self.db.get_syntax_colors(is_dark=True)
        saved_light = self.db.get_syntax_colors(is_dark=False)

        self.assertEqual(saved_dark["keyword"], SYNTAX_PRESETS["VS Code"]["dark"]["keyword"])
        self.assertEqual(saved_light["keyword"], SYNTAX_PRESETS["VS Code"]["light"]["keyword"])

        # Check AlgoCodeEditor highlighter with the preset
        editor = AlgoCodeEditor(is_dark=True)
        editor.apply_settings({}, saved_dark)
        self.assertEqual(
            editor.highlighter.fmt_keyword.foreground().color().name().lower(),
            SYNTAX_PRESETS["VS Code"]["dark"]["keyword"].lower()
        )

        # Select Monokai preset
        idx_mono = dlg.combo_syntax_preset.findText("Monokai")
        dlg.combo_syntax_preset.setCurrentIndex(idx_mono)
        dlg.apply_preferences()

        self.assertEqual(self.db.get_syntax_preset(), "Monokai")
        saved_mono_light = self.db.get_syntax_colors(is_dark=False)
        self.assertEqual(saved_mono_light["keyword"], SYNTAX_PRESETS["Monokai"]["light"]["keyword"])
        dlg.close()


if __name__ == "__main__":
    unittest.main()
