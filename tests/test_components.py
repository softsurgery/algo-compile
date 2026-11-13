"""
Unit tests for reusable prop-driven UI components (AppCheckBox, AppRadioButton, AppSelect).
"""

import unittest
from PyQt5.QtWidgets import QApplication, QCheckBox, QRadioButton, QComboBox
from PyQt5.QtCore import QSize

from ui.components import AppCheckBox, AppRadioButton, AppSelect


class TestComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_app_checkbox_props_and_callbacks(self):
        toggled_vals = []
        chk = AppCheckBox(
            "Enable feature",
            checked=True,
            tooltip="Feature tooltip",
            enabled=False,
            is_dark=True,
            on_toggled=lambda v: toggled_vals.append(v),
            object_name="chk_feat",
        )
        self.assertIsInstance(chk, QCheckBox)
        self.assertEqual(chk.text(), "Enable feature")
        self.assertTrue(chk.isChecked())
        self.assertEqual(chk.toolTip(), "Feature tooltip")
        self.assertFalse(chk.isEnabled())
        self.assertEqual(chk.objectName(), "chk_feat")
        self.assertEqual(chk._is_dark, True)

        chk.setEnabled(True)
        chk.setChecked(False)
        self.assertEqual(toggled_vals, [False])

        chk.set_dark_mode(False)
        self.assertEqual(chk._is_dark, False)

        # Verify optional icon + sizeHint + custom paintEvent
        from ui.icons import create_icon
        chk_icon = AppCheckBox(
            "With icon",
            icon=create_icon("check", "#2563eb", 16),
            icon_size=16,
            checked=True,
        )
        self.assertGreater(chk_icon.sizeHint().width(), chk.sizeHint().width() - 20)
        chk_icon.resize(chk_icon.sizeHint())
        self.assertFalse(chk_icon.grab().isNull())

    def test_app_radio_button_props_and_callbacks(self):
        toggled_vals = []
        rb = AppRadioButton(
            "Dark Mode",
            checked=True,
            tooltip="Use dark theme",
            icon_size=24,
            is_dark=False,
            on_toggled=lambda v: toggled_vals.append(v),
            object_name="rb_dark",
        )
        self.assertIsInstance(rb, QRadioButton)
        self.assertEqual(rb.text(), "Dark Mode")
        self.assertTrue(rb.isChecked())
        self.assertEqual(rb.toolTip(), "Use dark theme")
        self.assertEqual(rb.iconSize(), QSize(24, 24))
        self.assertEqual(rb.objectName(), "rb_dark")
        self.assertEqual(rb._is_dark, False)

        rb2 = AppRadioButton("Light Mode", on_toggled=lambda v: toggled_vals.append(("rb2", v)))
        rb.set_dark_mode(True)
        self.assertEqual(rb._is_dark, True)

        # Unchecking a radio button happens when toggling from False -> True or via another button
        rb2.setChecked(True)
        self.assertEqual(toggled_vals, [("rb2", True)])

        # Verify custom paintEvent renders circular indicator + optional icon without error
        from ui.icons import create_icon
        rb.setIcon(create_icon("moon", "#89b4fa", 24))
        rb.resize(rb.sizeHint())
        self.assertFalse(rb.grab().isNull())

    def test_app_select_props_and_items(self):
        changed_indices = []
        sel = AppSelect(
            items=[("First", "a"), ("Second", "b"), "Third"],
            current="Second",
            tooltip="Pick one",
            fixed_height=24,
            min_width=150,
            compact=True,
            is_dark=True,
            on_changed=lambda idx: changed_indices.append(idx),
            object_name="sel_test",
        )
        self.assertIsInstance(sel, QComboBox)
        self.assertEqual(sel.count(), 3)
        self.assertEqual(sel.currentText(), "Second")
        self.assertEqual(sel.currentData(), "b")
        self.assertEqual(sel.toolTip(), "Pick one")
        self.assertEqual(sel.height(), 24)
        self.assertEqual(sel.minimumWidth(), 150)
        self.assertEqual(sel.objectName(), "sel_test")
        self.assertIn("font-size: 11px;", sel.styleSheet())

        sel.setCurrentIndex(2)
        self.assertEqual(changed_indices, [2])

        sel.set_items(["Second", "Fourth"], keep_selection=False)
        self.assertEqual(sel.count(), 2)
        sel.set_items(["Alpha", "Fourth"], keep_selection=True)
        self.assertEqual(sel.currentText(), "Alpha")

        sel.set_dark_mode(False)
        self.assertIn("#ffffff", sel.styleSheet())
        sel.resize(180, 28)
        self.assertFalse(sel.grab().isNull())


if __name__ == "__main__":
    unittest.main()
