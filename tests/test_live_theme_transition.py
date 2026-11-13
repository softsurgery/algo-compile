"""
Tests for live system theme detection, immediate transitions without window reopening,
and SystemThemeWatcher behavior.
"""

import sys
import os
import unittest

if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
    if os.environ.get("QT_QPA_PLATFORM", "") in ("", "wayland", "wayland-egl"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"

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

    def test_standard_qt_window_flags_and_native_window_manager(self):
        """Verifies all windows use standard Qt window flags and native OS window management."""
        from ui.dialogs import InsertCodeDialog
        from ui.pdf_viewer import PdfReaderWindow

        # MainWindow must use standard Qt.Window and never FramelessWindowHint or CustomizeWindowHint
        win_flags = int(self.win.windowFlags())
        self.assertTrue(bool(win_flags & int(Qt.Window)))
        self.assertFalse(bool(win_flags & int(Qt.FramelessWindowHint)))
        self.assertFalse(bool(win_flags & int(Qt.CustomizeWindowHint)))

        # PreferencesDialog
        dlg_pref = PreferencesDialog(self.win, is_dark=False, db=self.db)
        pref_flags = int(dlg_pref.windowFlags())
        self.assertFalse(bool(pref_flags & int(Qt.FramelessWindowHint)))
        self.assertFalse(bool(pref_flags & int(Qt.CustomizeWindowHint)))
        dlg_pref.close()

        # InsertCodeDialog
        dlg_ins = InsertCodeDialog(self.win, is_dark=False)
        ins_flags = int(dlg_ins.windowFlags())
        self.assertFalse(bool(ins_flags & int(Qt.FramelessWindowHint)))
        self.assertFalse(bool(ins_flags & int(Qt.CustomizeWindowHint)))
        dlg_ins.close()

        # PdfReaderWindow
        pdf_win = PdfReaderWindow("", parent=self.win, is_dark=False)
        pdf_flags = int(pdf_win.windowFlags())
        self.assertTrue(bool(pdf_flags & int(Qt.Window)))
        self.assertFalse(bool(pdf_flags & int(Qt.FramelessWindowHint)))
        self.assertFalse(bool(pdf_flags & int(Qt.CustomizeWindowHint)))
        pdf_win.close()

    def test_dark_to_light_transition_components(self):
        """Verifies QComboBox and QRadioButton transition cleanly from dark to light mode."""
        from PyQt5.QtGui import QImage

        self.win.is_dark_mode = True
        self.win.apply_theme()

        dlg = PreferencesDialog(self.win, is_dark=True, db=self.db)
        dlg.settings_applied.connect(self.win._apply_all_preferences)
        dlg.show()

        # Transition from dark to light via radio button
        dlg.rb_light.click()

        self.assertFalse(dlg.is_dark)
        self.assertFalse(self.win.is_dark_mode)

        # Render combo_syntax_preset on ColorsPage and verify light background
        dlg.pages.setCurrentIndex(2)
        img_combo = QImage(dlg.combo_syntax_preset.size(), QImage.Format_ARGB32)
        dlg.combo_syntax_preset.render(img_combo)
        mid_color = img_combo.pixelColor(img_combo.width() // 2, img_combo.height() // 2).name()
        self.assertEqual(mid_color, "#ffffff")

        dlg.close()


if __name__ == "__main__":
    unittest.main()
