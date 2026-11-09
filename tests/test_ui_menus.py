"""
Unit tests for UI menus, Tools menu, and InsertCodeDialog.
"""

import unittest
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.insert_code_dialog import InsertCodeDialog

app = QApplication.instance() or QApplication([])


class TestUIMenusAndDialogs(unittest.TestCase):
    def setUp(self):
        self.win = MainWindow()
        self.win.show()

    def tearDown(self):
        self.win.close()

    def test_toolbar_buttons_and_no_examples_button(self):
        # btn_examples must not be on the window or toolbar
        self.assertFalse(hasattr(self.win, "btn_examples"))

        # Check action widgets for run, python, stop
        tool_widgets = [self.win.toolbar.widgetForAction(act) for act in self.win.toolbar.actions()]
        names = [w.objectName() for w in tool_widgets if w]
        self.assertIn("btn_run", names)
        self.assertIn("btn_python", names)
        self.assertIn("btn_stop", names)

    def test_tools_menu_and_insert_code_action(self):
        menubar = self.win.menuBar()
        menus = menubar.findChildren(type(menubar.addMenu("")))
        tools_menu = next((m for m in menus if "Tools" in m.title()), None)
        self.assertIsNotNone(tools_menu, "Tools menu should exist in menubar")

        actions = [a.text() for a in tools_menu.actions()]
        self.assertTrue(any("Insert Code" in a for a in actions), "Insert Code action must be present")

    def test_insert_code_dialog_functionality(self):
        dlg = InsertCodeDialog(self.win, is_dark=False)
        self.assertGreaterEqual(dlg.list_widget.count(), 6)

        # Select first item and verify preview
        dlg.list_widget.setCurrentRow(0)
        self.assertTrue(len(dlg.preview_editor.toPlainText()) > 0)

        # Filter
        dlg.search_input.setText("palindrome")
        self.assertEqual(dlg.list_widget.count(), 1)
        item = dlg.list_widget.item(0)
        self.assertIn("Palindrome", item.text())

        # Insert action
        dlg._on_insert_clicked()
        self.assertEqual(dlg.action_mode, "insert")
        self.assertIn("palindrome", dlg.selected_code.lower())

        # New tab action
        dlg._on_open_new_tab()
        self.assertEqual(dlg.action_mode, "new_tab")
        dlg.close()

    def test_buttons_have_no_custom_background_or_border(self):
        # Both light and dark theme stylesheets should not have custom background/border rules for these buttons
        light_style = self.win.styleSheet()
        self.assertNotIn("QToolButton#btn_run", light_style)
        self.assertNotIn("QToolButton#btn_stop", light_style)
        self.assertNotIn("QToolButton#btn_python", light_style)

        self.win.toggle_theme()
        dark_style = self.win.styleSheet()
        self.assertNotIn("QToolButton#btn_run", dark_style)
        self.assertNotIn("QToolButton#btn_stop", dark_style)
        self.assertNotIn("QToolButton#btn_python", dark_style)

    def test_insert_code_dialog_dark_theme(self):
        dlg_dark = InsertCodeDialog(self.win, is_dark=True)
        self.assertIn("#1e1e2e", dlg_dark.styleSheet())
        self.assertIn("#181825", dlg_dark.list_widget.styleSheet())
        self.assertIn("#181825", dlg_dark.search_input.styleSheet())
        self.assertIn("#11111b", dlg_dark.preview_editor.styleSheet())
        dlg_dark.close()

    def test_algoo_app_branding_and_links(self):
        # Window title should reflect Algoo
        self.assertIn("Algoo", self.win.windowTitle())

        # Check Help menu
        menubar = self.win.menuBar()
        menus = menubar.findChildren(type(menubar.addMenu("")))
        help_menu = next((m for m in menus if "Aide" in m.title()), None)
        self.assertIsNotNone(help_menu, "Aide menu should exist")

        actions = [a.text() for a in help_menu.actions()]
        self.assertTrue(any("softsurgery/algoo" in a for a in actions), "GitHub repository action should be present")
        self.assertTrue(any("Algoo" in a for a in actions), "About Algoo action should be present")

        # Check console banner
        self.assertIn("Algoo", self.win.console.output_text.toPlainText())


if __name__ == '__main__':
    unittest.main()
