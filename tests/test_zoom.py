"""
Unit tests for Zoom functionality in Editor and Console.
"""

import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QWheelEvent, QKeyEvent
from PyQt5.QtCore import Qt, QPoint, QPointF
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])

class TestZoomFeatures(unittest.TestCase):
    def setUp(self):
        self.win = MainWindow()
        self.win.show()
        self.editor = self.win.current_editor()
        self.console = self.win.console

    def tearDown(self):
        self.win.close()

    def test_editor_zoom(self):
        initial = self.editor.font().pointSize()
        self.assertEqual(initial, 11)

        self.editor.zoom_in(2)
        self.assertEqual(self.editor.font().pointSize(), 13)

        self.editor.zoom_out(1)
        self.assertEqual(self.editor.font().pointSize(), 12)

        self.editor.reset_zoom()
        self.assertEqual(self.editor.font().pointSize(), 11)

    def test_console_zoom(self):
        initial_out = self.console.output_text.font().pointSize()
        initial_in = self.console.input_line.font().pointSize()
        self.assertEqual(initial_out, 10)
        self.assertEqual(initial_in, 10)

        self.console.zoom_in(3)
        self.assertEqual(self.console.output_text.font().pointSize(), 13)
        self.assertEqual(self.console.input_line.font().pointSize(), 13)

        self.console.zoom_out(1)
        self.assertEqual(self.console.output_text.font().pointSize(), 12)
        self.assertEqual(self.console.input_line.font().pointSize(), 12)

        self.console.reset_zoom()
        self.assertEqual(self.console.output_text.font().pointSize(), 10)
        self.assertEqual(self.console.input_line.font().pointSize(), 10)

    def test_ctrl_wheel_zoom(self):
        wheel_up = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, 120), Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False)
        wheel_down = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, -120), Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False)

        # Editor
        self.editor.wheelEvent(wheel_up)
        self.assertEqual(self.editor.font().pointSize(), 12)
        self.editor.wheelEvent(wheel_down)
        self.assertEqual(self.editor.font().pointSize(), 11)

        # Console Output
        self.console.output_text.wheelEvent(wheel_up)
        self.assertEqual(self.console.output_text.font().pointSize(), 11)
        self.assertEqual(self.console.input_line.font().pointSize(), 11)

        # Console Input
        self.console.input_line.wheelEvent(wheel_down)
        self.assertEqual(self.console.output_text.font().pointSize(), 10)
        self.assertEqual(self.console.input_line.font().pointSize(), 10)

    def test_key_press_zoom(self):
        key_plus = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Plus, Qt.ControlModifier, "+")
        key_minus = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Minus, Qt.ControlModifier, "-")
        key_zero = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_0, Qt.ControlModifier, "0")

        # Editor keys
        self.editor.keyPressEvent(key_plus)
        self.assertEqual(self.editor.font().pointSize(), 12)
        self.editor.keyPressEvent(key_minus)
        self.assertEqual(self.editor.font().pointSize(), 11)
        self.editor.zoom_in(4)
        self.editor.keyPressEvent(key_zero)
        self.assertEqual(self.editor.font().pointSize(), 11)

        # Console output keys
        self.console.output_text.keyPressEvent(key_plus)
        self.assertEqual(self.console.output_text.font().pointSize(), 11)
        self.console.output_text.keyPressEvent(key_zero)
        self.assertEqual(self.console.output_text.font().pointSize(), 10)

        # Console input keys
        self.console.input_line.keyPressEvent(key_plus)
        self.assertEqual(self.console.output_text.font().pointSize(), 11)
        self.console.input_line.keyPressEvent(key_zero)
        self.assertEqual(self.console.output_text.font().pointSize(), 10)

    def test_toolbar_zoom_and_focus(self):
        self.editor.setFocus()
        self.win.act_zoom_in.trigger()
        self.assertEqual(self.editor.font().pointSize(), 12)
        self.assertEqual(self.console.output_text.font().pointSize(), 10)

        self.console.output_text.setFocus()
        self.win.act_zoom_in.trigger()
        self.assertEqual(self.editor.font().pointSize(), 12)
        self.assertEqual(self.console.output_text.font().pointSize(), 11)

        self.win.act_zoom_out.trigger()
        self.assertEqual(self.console.output_text.font().pointSize(), 10)


if __name__ == '__main__':
    unittest.main()
