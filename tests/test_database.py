"""
Unit and integration tests for SQLite DatabaseManager and MainWindow session persistence.
"""

import os
import tempfile
import unittest
from PyQt5.QtWidgets import QApplication
from database import DatabaseManager, get_database, reset_database_instance
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_algoo.db")
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_tables_created(self):
        with self.db._lock:
            cur = self.db._conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row["name"] for row in cur.fetchall()}
            self.assertIn("settings", tables)
            self.assertIn("opened_files", tables)

    def test_theme_settings_dark_and_light(self):
        # Default when empty
        self.assertIsNone(self.db.get_theme())
        self.assertIsNone(self.db.is_dark_mode())

        # Set dark
        self.db.set_dark_mode(True)
        self.assertEqual(self.db.get_theme(), "dark")
        self.assertTrue(self.db.is_dark_mode())

        # Set light
        self.db.set_dark_mode(False)
        self.assertEqual(self.db.get_theme(), "light")
        self.assertFalse(self.db.is_dark_mode())

        # Generic settings and removal
        self.db.set_setting("custom_key", "custom_val")
        self.assertEqual(self.db.get_setting("custom_key"), "custom_val")
        self.db.remove_setting("custom_key")
        self.assertIsNone(self.db.get_setting("custom_key"))

    def test_opened_files_and_history(self):
        file1 = os.path.join(self.temp_dir.name, "test1.algo")
        file2 = os.path.join(self.temp_dir.name, "test2.algo")
        for f in (file1, file2):
            with open(f, "w", encoding="utf-8") as fp:
                fp.write("ALGORITHME Test\nDEBUT\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n")

        # Record file1 opened
        self.db.record_file_opened(file1, is_open=True, is_active=True, tab_order=0)
        self.assertEqual(self.db.get_open_files(), [os.path.abspath(file1)])
        self.assertEqual(self.db.get_active_file(), os.path.abspath(file1))

        # Record file2 opened
        self.db.record_file_opened(file2, is_open=True, is_active=True, tab_order=1)
        self.assertEqual(self.db.get_active_file(), os.path.abspath(file2))
        open_files = self.db.get_open_files()
        self.assertEqual(len(open_files), 2)
        self.assertEqual(open_files[0], os.path.abspath(file1))
        self.assertEqual(open_files[1], os.path.abspath(file2))

        # Close file1
        self.db.record_file_closed(file1)
        self.assertEqual(self.db.get_open_files(), [os.path.abspath(file2)])
        
        # Recent files should still contain both file2 and file1
        recent = self.db.get_latest_opened_files(10)
        self.assertIn(os.path.abspath(file1), recent)
        self.assertIn(os.path.abspath(file2), recent)

        # Clear recent files
        self.db.clear_recent_files()
        recent_after_clear = self.db.get_latest_opened_files(10)
        # file1 was closed so it should be cleared; file2 is open so it remains
        self.assertNotIn(os.path.abspath(file1), recent_after_clear)
        self.assertIn(os.path.abspath(file2), recent_after_clear)

    def test_sync_open_tabs(self):
        f1 = os.path.join(self.temp_dir.name, "tab1.algo")
        f2 = os.path.join(self.temp_dir.name, "tab2.algo")
        for f in (f1, f2):
            with open(f, "w") as fp:
                fp.write("ALGORITHME Tab\nDEBUT\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n")

        tabs = [
            {"file_path": f1, "tab_order": 0, "is_active": False},
            {"file_path": f2, "tab_order": 1, "is_active": True},
        ]
        self.db.sync_open_tabs(tabs)
        self.assertEqual(self.db.get_open_files(), [os.path.abspath(f1), os.path.abspath(f2)])
        self.assertEqual(self.db.get_active_file(), os.path.abspath(f2))


class TestMainWindowDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "session_test.db")
        self.db = DatabaseManager(self.db_path)

        # Create two sample algorithm files
        self.sample1 = os.path.join(self.temp_dir.name, "algo_one.algo")
        with open(self.sample1, "w", encoding="utf-8") as f:
            f.write("ALGORITHME AlgoOne\nDEBUT\n  Ecrire_nl(\"Un\")\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n")

        self.sample2 = os.path.join(self.temp_dir.name, "algo_two.algo")
        with open(self.sample2, "w", encoding="utf-8") as f:
            f.write("ALGORITHME AlgoTwo\nDEBUT\n  Ecrire_nl(\"Deux\")\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n")

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()
        reset_database_instance()

    def test_theme_toggle_persists_in_sqlite(self):
        win = MainWindow(db=self.db)
        win.show()

        # Initial theme saved in db
        initial_dark = win.is_dark_mode
        self.assertEqual(self.db.is_dark_mode(), initial_dark)

        # Toggle theme
        win.toggle_theme()
        self.assertEqual(win.is_dark_mode, not initial_dark)
        self.assertEqual(self.db.is_dark_mode(), not initial_dark)

        win.close()

    def test_opened_files_restoration_across_sessions(self):
        # Session 1: open both sample files, select sample2 as active
        win1 = MainWindow(db=self.db)
        win1.show()
        win1.load_file(self.sample1)
        win1.load_file(self.sample2)
        win1.tab_widget.setCurrentIndex(win1.tab_widget.count() - 1)
        win1.close()

        # Verify DB recorded both files as open with sample2 active
        open_files = self.db.get_open_files()
        self.assertIn(os.path.abspath(self.sample1), open_files)
        self.assertIn(os.path.abspath(self.sample2), open_files)
        self.assertEqual(self.db.get_active_file(), os.path.abspath(self.sample2))

        # Session 2: Launch a new MainWindow using the same DB
        win2 = MainWindow(db=self.db)
        win2.show()

        # Both files should be reopened in tabs
        tab_paths = [
            win2.tab_widget.widget(i).property("file_path")
            for i in range(win2.tab_widget.count())
        ]
        self.assertIn(os.path.abspath(self.sample1), tab_paths)
        self.assertIn(os.path.abspath(self.sample2), tab_paths)

        # Active tab should be sample2
        curr_editor = win2.current_editor()
        self.assertIsNotNone(curr_editor)
        self.assertEqual(curr_editor.property("file_path"), os.path.abspath(self.sample2))

        win2.close()

    def test_recent_files_menu_actions(self):
        win = MainWindow(db=self.db)
        win.show()

        self.assertIsNotNone(win.menu_recent)
        win.load_file(self.sample1)

        # Recent files menu should contain sample1
        actions = [a.text() for a in win.menu_recent.actions()]
        self.assertTrue(any(os.path.basename(self.sample1) in a for a in actions))
        self.assertTrue(any("Ouvrir les derniers fichiers" in a for a in actions))
        self.assertTrue(any("Effacer l'historique" in a for a in actions))

        # Clear history
        win._clear_recent_files_history()
        actions_after = [a.text() for a in win.menu_recent.actions()]
        # sample1 is still open, but if we close the tab and clear history:
        for i in range(win.tab_widget.count()):
            if win.tab_widget.widget(i).property("file_path") == os.path.abspath(self.sample1):
                win._on_close_tab(i)
                break

        win._clear_recent_files_history()
        self.assertNotIn(os.path.abspath(self.sample1), self.db.get_latest_opened_files())

        win.close()


if __name__ == '__main__':
    unittest.main()
