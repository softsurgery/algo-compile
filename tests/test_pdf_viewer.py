"""
Unit tests for LightPdfViewer, PdfReaderWindow, fullscreen capabilities, and PDF integration in snippet files viewer.
"""

import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.pdf_viewer import LightPdfViewer, PdfReaderWindow
from ui.snippets_view import SnippetFilesViewer
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])

_DEFAULT_TEST_PDF = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "snippets", "01_Arithmetique", "somme_diviseurs", "MiniProjet1.pdf"
)
_FALLBACK_TEST_PDF = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "docs", "Convention Algorithmique 2024.pdf"
)
TEST_PDF = _DEFAULT_TEST_PDF if os.path.exists(_DEFAULT_TEST_PDF) else _FALLBACK_TEST_PDF


class TestPdfViewerAndFullscreen(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(TEST_PDF), f"Test PDF not found at {TEST_PDF}")

    def test_light_pdf_viewer_loading_and_pages(self):
        viewer = LightPdfViewer(is_dark=False)
        viewer.load_pdf(TEST_PDF)
        self.assertGreaterEqual(viewer.page_count, 2)
        self.assertEqual(viewer.current_page, 0)
        self.assertIsNotNone(viewer.lbl_page.pixmap())

        # Next page
        viewer.next_page()
        self.assertEqual(viewer.current_page, 1)

        # Prev page
        viewer.prev_page()
        self.assertEqual(viewer.current_page, 0)

        # Zoom in & out
        init_zoom = viewer.zoom_factor
        viewer.zoom_in()
        self.assertGreater(viewer.zoom_factor, init_zoom)
        viewer.zoom_out()
        self.assertEqual(viewer.zoom_factor, init_zoom)

        # Fit functions
        viewer.fit_width()
        viewer.fit_page()

        # Dark mode toggle
        viewer.set_dark_mode(True)
        viewer.set_dark_mode(False)
        viewer.close()

    def test_pdf_reader_window_and_fullscreen_toggle(self):
        win = PdfReaderWindow(TEST_PDF, is_dark=False, start_fullscreen=False)
        self.assertGreaterEqual(win.viewer.page_count, 2)

        # Verify no icon in window header
        self.assertFalse(win.windowIcon().isNull())
        self.assertEqual(win.windowIcon().pixmap(1, 1).width(), 1)

        # Test fullscreen toggle
        self.assertFalse(win.isFullScreen())
        win.toggle_fullscreen()
        self.assertTrue(win.isFullScreen())
        self.assertEqual(win.btn_fs.text(), "Quitter plein écran")

        win.toggle_fullscreen()
        self.assertFalse(win.isFullScreen())
        self.assertEqual(win.btn_fs.text(), "Plein écran")

        # Theme toggle
        win.set_dark_mode(True)
        win.set_dark_mode(False)
        win.close()

    def test_pdf_reader_keyboard_and_wheel_events(self):
        from PyQt5.QtGui import QKeyEvent, QWheelEvent
        from PyQt5.QtCore import QPoint, QPointF
        win = PdfReaderWindow(TEST_PDF, is_dark=False, start_fullscreen=False)
        win.show()
        viewer = win.viewer

        # Test navigation keys
        # Next page via Key_Right
        key_ev = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Right, Qt.NoModifier)
        viewer.keyPressEvent(key_ev)
        self.assertEqual(viewer.current_page, 1)

        # Prev page via Key_Left
        key_ev = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)
        viewer.keyPressEvent(key_ev)
        self.assertEqual(viewer.current_page, 0)

        # Zoom in via Ctrl++
        z0 = viewer.zoom_factor
        key_ev = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Plus, Qt.ControlModifier)
        viewer.keyPressEvent(key_ev)
        self.assertGreater(viewer.zoom_factor, z0)

        # Reset zoom via Ctrl+0
        key_ev = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_0, Qt.ControlModifier)
        viewer.keyPressEvent(key_ev)
        self.assertEqual(viewer.zoom_factor, 1.0)

        # Wheel zoom with Ctrl modifier on viewport
        ctrl_wheel = QWheelEvent(QPointF(50, 50), QPointF(50, 50), QPoint(0, 0), QPoint(0, 120), Qt.NoButton, Qt.ControlModifier, Qt.ScrollUpdate, False)
        app.sendEvent(viewer.scroll_area.viewport(), ctrl_wheel)
        self.assertGreater(viewer.zoom_factor, 1.0)

        # Escape closes window or exits fullscreen
        win._on_escape()
        win.close()

    def test_snippet_files_viewer_handles_pdf(self):
        viewer = SnippetFilesViewer(is_dark=False)
        viewer.show()
        # Pass a list containing PDF and text file
        viewer.set_files([TEST_PDF])
        self.assertEqual(viewer.table.rowCount(), 1)

        # Verify PDF preview is selected (page 2 in stack)
        self.assertEqual(viewer.preview_stack.currentIndex(), 2)
        self.assertGreaterEqual(viewer.pdf_viewer.page_count, 2)
        self.assertFalse(viewer.btn_open_pdf_fs.isHidden())
        self.assertFalse(viewer.btn_insert_content.isEnabled())
        self.assertFalse(viewer.btn_insert_content.isVisible())

        # Detach PDF window request
        viewer._open_pdf_detached(TEST_PDF)
        self.assertIsNotNone(viewer._pdf_window)
        self.assertGreaterEqual(viewer._pdf_window.viewer.page_count, 2)
        viewer._pdf_window.close()
        viewer.close()

    def test_main_window_fullscreen_and_pdf_reader(self):
        win = MainWindow()
        win.show()
        self.assertTrue(hasattr(win, "act_fullscreen"))
        self.assertTrue(hasattr(win, "toggle_fullscreen"))

        # Test fullscreen toggle
        self.assertFalse(win.isFullScreen())
        win.toggle_fullscreen()
        self.assertTrue(win.isFullScreen() or win._is_fullscreen)
        win.toggle_fullscreen()
        self.assertFalse(win.isFullScreen())

        # Test loading PDF opens PDF Reader window
        win.load_file(TEST_PDF)
        self.assertTrue(hasattr(win, "_pdf_window"))
        self.assertGreaterEqual(win._pdf_window.viewer.page_count, 2)
        win._pdf_window.close()
        win.close()


if __name__ == "__main__":
    unittest.main()
