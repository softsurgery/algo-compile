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
        # Ensure tests do not overwrite the user's persisted preferences
        from PyQt5.QtCore import QSettings
        settings = QSettings("softsurgery", "Algoo")
        settings.remove("dark_mode")
        settings.sync()

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

    def test_app_logo_icon_and_about_dialog(self):
        from ui.icons import get_app_icon, get_logo_pixmap, get_logo_path
        from ui.about_dialog import AboutDialog
        from PIL import Image
        import numpy as np

        # Verify logo path resolution
        logo_path = get_logo_path()
        self.assertTrue(logo_path.endswith("logo.png"))

        # Verify logo has transparent background (no background box)
        img = Image.open(logo_path)
        arr = np.array(img)
        self.assertEqual(arr.shape[2], 4, "Logo must be RGBA")
        self.assertEqual(arr[0, 0, 3], 0, "Top-left corner must be transparent")
        self.assertEqual(arr[100, 100, 3], 0, "Outer margin must be transparent")

        # Verify application icon is valid (for OS icon bar / dock)
        app_icon = get_app_icon()
        self.assertFalse(app_icon.isNull(), "get_app_icon() must return a valid QIcon")

        # Verify MainWindow window header does not display the logo
        win_icon_size = self.win.windowIcon().actualSize(self.win.size())
        self.assertEqual(win_icon_size.width(), 1, "MainWindow must use transparent 1x1 icon to avoid showing in header")

        # Verify logo pixmap
        pix = get_logo_pixmap(96)
        self.assertFalse(pix.isNull(), "Logo pixmap must not be null")
        self.assertLessEqual(pix.width(), 96)
        self.assertLessEqual(pix.height(), 96)

        # Verify About dialog in light mode
        dlg_light = AboutDialog(self.win, is_dark=False)
        self.assertFalse(dlg_light.windowIcon().isNull())
        self.assertFalse(dlg_light.logo_label.pixmap().isNull())
        self.assertIn("softsurgery", dlg_light.details_label.text())
        self.assertIn("github.com/softsurgery/algoo", dlg_light.details_label.text())
        self.assertIn("background-color: #ffffff;", dlg_light.styleSheet())
        dlg_light.btn_close.click()

        # Verify About dialog in dark mode
        dlg_dark = AboutDialog(self.win, is_dark=True)
        self.assertFalse(dlg_dark.logo_label.pixmap().isNull())
        self.assertIn("background-color: #1e1e2e;", dlg_dark.styleSheet())
        dlg_dark.btn_close.click()

    def test_window_bar_dark_mode_palette_and_themes(self):
        from ui.theme_utils import (
            create_dark_palette,
            create_light_palette,
            detect_system_dark_mode,
            apply_os_window_theme
        )
        from PyQt5.QtGui import QPalette

        # 1. Palette colors validation
        dark_pal = create_dark_palette()
        self.assertEqual(dark_pal.color(QPalette.Active, QPalette.Window).name(), "#181825")
        self.assertEqual(dark_pal.color(QPalette.Active, QPalette.WindowText).name(), "#cdd6f4")

        light_pal = create_light_palette()
        self.assertEqual(light_pal.color(QPalette.Active, QPalette.Window).name(), "#f7f9fa")

        # 2. System dark mode detection returns boolean
        is_dark_sys = detect_system_dark_mode()
        self.assertIsInstance(is_dark_sys, bool)

        # 3. Apply dark theme to window
        self.win.is_dark_mode = True
        self.win.apply_theme(recreate_native=False)
        self.assertEqual(app.palette().color(QPalette.Active, QPalette.Window).name(), "#181825")
        self.assertEqual(self.win.palette().color(QPalette.Active, QPalette.Window).name(), "#181825")
        self.assertIn("#a6adc8", self.win.symbols_bar.lbl_sym.styleSheet())

        # 4. Toggle theme back to light
        self.win.toggle_theme()
        self.assertFalse(self.win.is_dark_mode)
        self.assertEqual(app.palette().color(QPalette.Active, QPalette.Window).name(), "#f7f9fa")
        self.assertEqual(self.win.palette().color(QPalette.Active, QPalette.Window).name(), "#f7f9fa")
        self.assertIn("#64748b", self.win.symbols_bar.lbl_sym.styleSheet())

    def test_scrollbar_theme_colors(self):
        from ui.styles import LIGHT_THEME, DARK_THEME
        from PyQt5.QtGui import QPainter, QImage

        # Verify styles define QScrollBar rules
        self.assertIn("QScrollBar:vertical", LIGHT_THEME)
        self.assertIn("#cbd5e1", LIGHT_THEME)  # Light scrollbar handle
        self.assertIn("QScrollBar:vertical", DARK_THEME)
        self.assertIn("#45475a", DARK_THEME)  # Dark scrollbar handle

        editor = self.win.current_editor()
        editor.setPlainText("\n".join(["Ligne " + str(i) for i in range(100)]))
        vsb = editor.verticalScrollBar()

        # In light mode
        self.win.is_dark_mode = False
        self.win.apply_theme()
        img_light = QImage(vsb.size(), QImage.Format_ARGB32)
        p = QPainter(img_light)
        vsb.render(p)
        p.end()
        colors_light = {img_light.pixelColor(vsb.width() // 2, y).name() for y in range(img_light.height())}
        self.assertIn("#cbd5e1", colors_light, "Light mode scrollbar should contain #cbd5e1 handle")

        # In dark mode
        self.win.is_dark_mode = True
        self.win.apply_theme()
        img_dark = QImage(vsb.size(), QImage.Format_ARGB32)
        p = QPainter(img_dark)
        vsb.render(p)
        p.end()
        colors_dark = {img_dark.pixelColor(vsb.width() // 2, y).name() for y in range(img_dark.height())}
        self.assertIn("#45475a", colors_dark, "Dark mode scrollbar should contain #45475a handle")

    def test_tab_border_radius_and_close_button(self):
        from ui.styles import LIGHT_THEME, DARK_THEME

        # Verify border-radius is reduced to 3px on tabs and pane
        self.assertIn("border-top-left-radius: 3px;", LIGHT_THEME)
        self.assertIn("border-top-right-radius: 3px;", LIGHT_THEME)
        self.assertIn("border-top-left-radius: 3px;", DARK_THEME)
        self.assertIn("border-top-right-radius: 3px;", DARK_THEME)

        # Verify close button has image rules configured in both themes
        self.assertIn("QTabBar::close-button", LIGHT_THEME)
        self.assertIn("QTabBar::close-button", DARK_THEME)
        self.assertIn("image: url(", LIGHT_THEME)
        self.assertIn("image: url(", DARK_THEME)

        # Verify close button hover in dark theme does NOT turn white (#fee2e2)
        close_dark_hover_start = DARK_THEME.find("QTabBar::close-button:hover")
        self.assertNotEqual(close_dark_hover_start, -1)
        close_dark_hover_block = DARK_THEME[close_dark_hover_start:close_dark_hover_start + 200]
        self.assertNotIn("#fee2e2", close_dark_hover_block, "Dark mode close button hover must not be white/fee2e2")
        self.assertIn("#313244", close_dark_hover_block, "Dark mode close button hover should use #313244")


if __name__ == '__main__':
    unittest.main()
