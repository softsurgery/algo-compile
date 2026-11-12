"""
Tests for live system theme detection, immediate transitions without window reopening,
and SystemThemeWatcher behavior.
"""

import sys
import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow
from ui.theme_utils import (
    detect_system_dark_mode,
    get_system_theme_watcher,
    SystemThemeWatcher,
    apply_os_window_theme
)
from ui.dialogs import PreferencesDialog
from database import DatabaseManager
import tempfile

app = QApplication.instance() or QApplication(sys.argv)


class TestLiveThemeTransition(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_theme.db")
        self.db = DatabaseManager(self.db_path)
        self.win = MainWindow(db=self.db)
        self.win.show()

    def tearDown(self):
        self.win.close()
        self.db.close()
        self.temp_dir.cleanup()

    def test_theme_watcher_singleton(self):
        w1 = get_system_theme_watcher()
        w2 = get_system_theme_watcher()
        self.assertIs(w1, w2)
        self.assertIsInstance(w1, SystemThemeWatcher)

    def test_window_not_reopened_on_theme_toggle(self):
        """Verifies that window handle / ID remains identical and window stays visible without recreating."""
        initial_win_id = int(self.win.winId())
        self.assertTrue(self.win.isVisible())

        # Toggle to opposite
        self.win.toggle_theme()
        # Window ID must remain identical because native window was NOT destroyed
        self.assertEqual(int(self.win.winId()), initial_win_id)
        self.assertTrue(self.win.isVisible())

        # Toggle back
        self.win.toggle_theme()
        self.assertEqual(int(self.win.winId()), initial_win_id)
        self.assertTrue(self.win.isVisible())

    def test_live_system_transition_reflection(self):
        """When theme mode is 'system', system transitions must reflect immediately."""
        self.db.set_theme_mode("system")
        self.assertEqual(self.db.get_theme_mode(), "system")

        # Simulate system transition to Dark
        self.win._on_system_theme_changed(True)
        self.assertTrue(self.win.is_dark_mode)

        # Simulate system transition to Light
        self.win._on_system_theme_changed(False)
        self.assertFalse(self.win.is_dark_mode)

        # Simulate system transition to Dark again
        self.win._on_system_theme_changed(True)
        self.assertTrue(self.win.is_dark_mode)

    def test_manual_mode_ignores_system_transition(self):
        """When theme mode is explicit 'dark' or 'light', system transitions must not override user's setting."""
        # 1. User chose dark mode
        self.db.set_theme_mode("dark")
        self.win.is_dark_mode = True
        self.win.apply_theme()

        # System transitions to Light
        self.win._on_system_theme_changed(False)
        # Should remain Dark
        self.assertTrue(self.win.is_dark_mode)

        # 2. User chose light mode
        self.db.set_theme_mode("light")
        self.win.is_dark_mode = False
        self.win.apply_theme()

        # System transitions to Dark
        self.win._on_system_theme_changed(True)
        # Should remain Light
        self.assertFalse(self.win.is_dark_mode)

    def test_window_manager_always_follows_os(self):
        """The window manager must always follow the OS regardless of app theme preference."""
        from PyQt5.QtGui import QPalette

        # 1. App in manual light mode, OS transitions to Dark
        self.db.set_theme_mode("light")
        self.win.is_dark_mode = False
        self.win._on_system_theme_changed(True)
        # Window manager palette should be dark (#181825)
        self.assertEqual(app.palette().color(QPalette.Active, QPalette.Window).name(), "#181825")
        # But app remains light
        self.assertFalse(self.win.is_dark_mode)

        # 2. App in manual dark mode, OS transitions to Light
        self.db.set_theme_mode("dark")
        self.win.is_dark_mode = True
        self.win._on_system_theme_changed(False)
        # Window manager palette should be light (#f7f9fa)
        self.assertEqual(app.palette().color(QPalette.Active, QPalette.Window).name(), "#f7f9fa")
        # But app remains dark
        self.assertTrue(self.win.is_dark_mode)

    def test_preferences_dialog_live_system_update(self):
        """PreferencesDialog updates its system info label live when system theme changes."""
        dlg = PreferencesDialog(self.win, is_dark=self.win.is_dark_mode, db=self.db)
        dlg.show()

        # Simulate system transition to Dark
        dlg._on_system_theme_changed(True)
        self.assertIn("Sombre", dlg.page_theme.lbl_sys_info.text())

        # Simulate system transition to Light
        dlg._on_system_theme_changed(False)
        self.assertIn("Clair", dlg.page_theme.lbl_sys_info.text())

        dlg.close()


if __name__ == "__main__":
    unittest.main()
