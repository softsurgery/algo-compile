import io
import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication, QMessageBox

from database import DatabaseManager
from ui.console import AlgoConsole
from ui.error_handler import install_exception_hooks, register_console, report_error
from ui.main_window import MainWindow


class TestConsoleErrorHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        self.db = DatabaseManager(self.db_path)
        self.win = MainWindow(db=self.db)

    def tearDown(self):
        self.win.close()
        self.tmpdir.cleanup()

    def test_console_log_error_escapes_html(self):
        console = self.win.console
        console.log_error("Erreur <inattendue> & grave", "Traceback <line 1>")
        plain = console.output_text.toPlainText()
        self.assertIn("Erreur <inattendue> & grave", plain)
        self.assertIn("Traceback <line 1>", plain)

    def test_translate_error_logs_to_console_without_qmessagebox(self):
        editor = self.win.current_editor()
        editor.setPlainText("Algorithme Test\nDebut\n  X <- \nFin")

        with patch.object(QMessageBox, "warning") as mock_warn, \
             patch.object(QMessageBox, "critical") as mock_crit:
            result = self.win.translate_to_python()

        self.assertEqual(result, "")
        mock_warn.assert_not_called()
        mock_crit.assert_not_called()
        self.assertIn("Erreur de compilation", self.win.console.output_text.toPlainText())

    def test_save_file_error_logs_to_console_without_qmessagebox(self):
        editor = self.win.current_editor()
        # Point to a non-existent directory so open() fails
        editor.setProperty("file_path", os.path.join(self.tmpdir.name, "missing_dir", "file.algo"))

        with patch.object(QMessageBox, "critical") as mock_crit, \
             patch.object(QMessageBox, "warning") as mock_warn:
            ok = self.win.save_file()

        self.assertFalse(ok)
        mock_crit.assert_not_called()
        mock_warn.assert_not_called()
        self.assertIn("Erreur d'enregistrement", self.win.console.output_text.toPlainText())

    def test_load_file_error_logs_to_console_without_qmessagebox(self):
        missing = os.path.join(self.tmpdir.name, "does_not_exist.algo")
        with patch.object(QMessageBox, "critical") as mock_crit, \
             patch.object(QMessageBox, "warning") as mock_warn:
            self.win.load_file(missing, record=False)

        mock_crit.assert_not_called()
        mock_warn.assert_not_called()
        self.assertIn("Erreur d'ouverture", self.win.console.output_text.toPlainText())

    def test_sys_excepthook_routes_to_console_and_stderr_without_popup(self):
        old_sys_hook = sys.excepthook
        old_thread_hook = getattr(threading, "excepthook", None)
        try:
            install_exception_hooks()
            register_console(self.win.console)
            stderr_buf = io.StringIO()

            with patch.object(sys, "stderr", stderr_buf), \
                 patch.object(QMessageBox, "critical") as mock_crit, \
                 patch.object(QMessageBox, "warning") as mock_warn:
                try:
                    raise RuntimeError("boom-unhandled")
                except RuntimeError:
                    sys.excepthook(*sys.exc_info())

            mock_crit.assert_not_called()
            mock_warn.assert_not_called()
            self.assertIn("boom-unhandled", stderr_buf.getvalue())
            plain = self.win.console.output_text.toPlainText()
            self.assertIn("Exception non gérée", plain)
            self.assertIn("boom-unhandled", plain)
        finally:
            sys.excepthook = old_sys_hook
            if old_thread_hook is not None:
                threading.excepthook = old_thread_hook

    def test_threading_excepthook_routes_to_console_without_popup(self):
        old_sys_hook = sys.excepthook
        old_thread_hook = getattr(threading, "excepthook", None)
        try:
            install_exception_hooks()
            register_console(self.win.console)
            stderr_buf = io.StringIO()

            def _worker():
                raise ValueError("thread-boom")

            with patch.object(sys, "stderr", stderr_buf), \
                 patch.object(QMessageBox, "critical") as mock_crit, \
                 patch.object(QMessageBox, "warning") as mock_warn:
                t = threading.Thread(target=_worker, name="TestWorker")
                t.start()
                t.join(timeout=5)
                self.app.processEvents()

            mock_crit.assert_not_called()
            mock_warn.assert_not_called()
            self.assertIn("thread-boom", stderr_buf.getvalue())
            plain = self.win.console.output_text.toPlainText()
            self.assertIn("thread-boom", plain)
        finally:
            sys.excepthook = old_sys_hook
            if old_thread_hook is not None:
                threading.excepthook = old_thread_hook


if __name__ == "__main__":
    unittest.main()
