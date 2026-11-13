"""
Unit tests for comment / uncomment shortcut (Ctrl + /) in AlgoCodeEditor.
"""

import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QKeyEvent, QTextCursor
from PyQt5.QtCore import Qt
from ui.editor import AlgoCodeEditor
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


class TestEditorComment(unittest.TestCase):
    def setUp(self):
        self.editor = AlgoCodeEditor()

    def test_single_line_comment_and_uncomment(self):
        self.editor.setPlainText("x <- 10")
        c = self.editor.textCursor()
        c.setPosition(2)
        self.editor.setTextCursor(c)

        # Toggle comment -> comments line
        self.editor.toggle_comment()
        self.assertEqual(self.editor.toPlainText(), "# x <- 10")

        # Toggle comment again -> uncomments line
        self.editor.toggle_comment()
        self.assertEqual(self.editor.toPlainText(), "x <- 10")

    def test_indentation_preserved(self):
        self.editor.setPlainText("    x <- 10")
        c = self.editor.textCursor()
        c.setPosition(6)
        self.editor.setTextCursor(c)

        # Should place comment after indentation
        self.editor.toggle_comment()
        self.assertEqual(self.editor.toPlainText(), "    # x <- 10")

        # Should restore exact original indentation
        self.editor.toggle_comment()
        self.assertEqual(self.editor.toPlainText(), "    x <- 10")

    def test_multiline_selection_toggle(self):
        self.editor.setPlainText("line 1\nline 2\nline 3")
        c = self.editor.textCursor()
        c.setPosition(0)
        c.setPosition(13, QTextCursor.KeepAnchor) # covers line 1 and line 2
        self.editor.setTextCursor(c)

        # Comment both lines
        self.editor.toggle_comment()
        lines = self.editor.toPlainText().splitlines()
        self.assertEqual(lines[0], "# line 1")
        self.assertEqual(lines[1], "# line 2")
        self.assertEqual(lines[2], "line 3")

        # Select both commented lines again and toggle -> uncomment
        c.setPosition(0)
        c.setPosition(17, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(c)
        self.editor.toggle_comment()
        lines_uncommented = self.editor.toPlainText().splitlines()
        self.assertEqual(lines_uncommented[0], "line 1")
        self.assertEqual(lines_uncommented[1], "line 2")
        self.assertEqual(lines_uncommented[2], "line 3")

    def test_key_event_ctrl_slash(self):
        self.editor.setPlainText("a <- b + c")
        c = self.editor.textCursor()
        c.setPosition(3)
        self.editor.setTextCursor(c)

        # Simulate Ctrl + / key event
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Slash, Qt.ControlModifier, "/")
        self.editor.keyPressEvent(event)
        self.assertEqual(self.editor.toPlainText(), "# a <- b + c")

        # Toggle back
        self.editor.keyPressEvent(event)
        self.assertEqual(self.editor.toPlainText(), "a <- b + c")

    def test_undo_restores_pre_comment_state(self):
        self.editor.setPlainText("test line")
        self.editor.toggle_comment()
        self.assertEqual(self.editor.toPlainText(), "# test line")

        self.editor.undo()
        self.assertEqual(self.editor.toPlainText(), "test line")

    def test_main_window_menu_action(self):
        win = MainWindow()
        win.show()
        editor = win.new_file("temp_comment_test.algo", "my_var <- 42")
        editor.setProperty("is_dirty", False)
        c = editor.textCursor()
        c.setPosition(4)
        editor.setTextCursor(c)

        # Find Commenter action in Edit menu
        menubar = win.menuBar()
        menus = menubar.findChildren(type(menubar.addMenu("")))
        edit_menu = next((m for m in menus if "Édition" in m.title()), None)
        self.assertIsNotNone(edit_menu)

        comment_act = next((a for a in edit_menu.actions() if "Commenter" in a.text()), None)
        self.assertIsNotNone(comment_act)
        self.assertIn("Ctrl+/", comment_act.shortcut().toString())

        # Trigger action
        comment_act.trigger()
        self.assertEqual(editor.toPlainText(), "# my_var <- 42")

        # Trigger again to uncomment
        comment_act.trigger()
        self.assertEqual(editor.toPlainText(), "my_var <- 42")

        editor.setProperty("is_dirty", False)
        win.close()


if __name__ == '__main__':
    unittest.main()
