"""
Unit tests for reusable prop-driven UI components (AppCheckBox, AppRadioButton, AppSelect).
"""

import unittest
from PyQt5.QtWidgets import QApplication, QCheckBox, QRadioButton, QComboBox, QTextBrowser, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtTest import QTest

from ui.components import (
    AppCheckBox,
    AppMarkdownReader,
    AppRadioButton,
    AppRotatingChevron,
    AppSelect,
    AppTreeView,
    NoFocusDelegate,
)


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

    def test_app_tree_view_props_filtering_and_theme(self):
        selected_calls = []
        current_calls = []
        tree = AppTreeView(
            headers=["Items"],
            indentation=16,
            icon_size=20,
            min_width=220,
            is_dark=True,
            on_selection_changed=lambda: selected_calls.append(True),
            on_current_item_changed=lambda cur, prev: current_calls.append(cur.text(0) if cur else None),
            object_name="tree_test",
        )
        self.assertIsInstance(tree, QTreeWidget)
        self.assertIsInstance(tree.itemDelegate(), NoFocusDelegate)
        self.assertFalse(tree.isHeaderHidden())
        self.assertEqual(tree.headerItem().text(0), "Items")
        self.assertEqual(tree.indentation(), 16)
        self.assertEqual(tree.iconSize(), QSize(20, 20))
        self.assertEqual(tree.minimumWidth(), 220)
        self.assertEqual(tree.objectName(), "tree_test")
        self.assertIn("#181825", tree.styleSheet())

        cat_a = QTreeWidgetItem(tree, ["Algorithms"])
        child_1 = QTreeWidgetItem(cat_a, ["QuickSort"])
        child_2 = QTreeWidgetItem(cat_a, ["BinarySearch"])
        cat_b = QTreeWidgetItem(tree, ["Structures"])
        child_3 = QTreeWidgetItem(cat_b, ["LinkedList"])

        tree.setCurrentItem(child_1)
        self.assertEqual(current_calls, ["QuickSort"])
        self.assertGreaterEqual(len(selected_calls), 1)

        # Default filter: matching child keeps parent visible & expanded, hides non-matching
        tree.filter_items("binary")
        self.assertFalse(cat_a.isHidden())
        self.assertTrue(child_1.isHidden())
        self.assertFalse(child_2.isHidden())
        self.assertTrue(cat_b.isHidden())
        self.assertTrue(cat_a.isExpanded())

        # Parent match with show_children_on_parent_match=True keeps all its children visible
        tree.filter_items("algorithms", show_children_on_parent_match=True)
        self.assertFalse(cat_a.isHidden())
        self.assertFalse(child_1.isHidden())
        self.assertFalse(child_2.isHidden())
        self.assertTrue(cat_b.isHidden())

        # Clear filter restores everything
        tree.filter_items("")
        self.assertFalse(cat_a.isHidden())
        self.assertFalse(child_1.isHidden())
        self.assertFalse(cat_b.isHidden())
        self.assertFalse(child_3.isHidden())

        tree.set_dark_mode(False)
        self.assertIn("#ffffff", tree.styleSheet())
        tree.resize(240, 200)
        self.assertFalse(tree.grab().isNull())

    def test_app_tree_view_branch_chevron_and_rotation(self):
        tree = AppTreeView(indentation=16, is_dark=True)
        tree.resize(240, 200)

        parent_item = QTreeWidgetItem(tree, ["Category"])
        QTreeWidgetItem(parent_item, ["Child"])
        leaf_item = QTreeWidgetItem(tree, ["Leaf"])

        parent_idx = tree.indexFromItem(parent_item)
        leaf_idx = tree.indexFromItem(leaf_item)

        def _has_painted_pixels(idx):
            img = QImage(16, 24, QImage.Format_ARGB32_Premultiplied)
            img.fill(Qt.transparent)
            painter = QPainter(img)
            tree.drawBranches(painter, QRect(0, 0, 16, 24), idx)
            painter.end()
            for y in range(img.height()):
                for x in range(img.width()):
                    if img.pixelColor(x, y).alpha() > 0:
                        return True
            return False

        # Expandable item draws a visible chevron; leaf item does not
        self.assertTrue(_has_painted_pixels(parent_idx))
        self.assertFalse(_has_painted_pixels(leaf_idx))

        # Initial collapsed angle is 0.0
        self.assertEqual(tree._branch_angle(parent_idx), 0.0)

        # Expanding starts rotation animation toward 90.0
        tree.expandItem(parent_item)
        self.assertEqual(tree._chevron_animator.active_count(), 1)
        QTest.qWait(200)
        self.assertEqual(tree._branch_angle(parent_idx), 90.0)
        self.assertEqual(tree._chevron_animator.active_count(), 0)

        # Collapsing rotates back to 0.0
        tree.collapseItem(parent_item)
        self.assertEqual(tree._chevron_animator.active_count(), 1)
        QTest.qWait(200)
        self.assertEqual(tree._branch_angle(parent_idx), 0.0)
        self.assertEqual(tree._chevron_animator.active_count(), 0)

        # Clearing tree stops and removes active animations
        tree.expandItem(parent_item)
        self.assertEqual(tree._chevron_animator.active_count(), 1)
        tree.clear()
        self.assertEqual(tree._chevron_animator.active_count(), 0)

    def test_app_rotating_chevron_component(self):
        toggled_states = []
        chevron = AppRotatingChevron(
            expanded=False,
            closed_angle=0.0,
            open_angle=90.0,
            duration_ms=80,
            size=18,
            clickable=True,
            is_dark=True,
            on_toggled=lambda state: toggled_states.append(state),
            object_name="test_chevron",
        )
        self.assertEqual(chevron.objectName(), "test_chevron")
        self.assertEqual(chevron.sizeHint(), QSize(18, 18))
        self.assertFalse(chevron.is_expanded())
        self.assertEqual(chevron.angle, 0.0)

        # Click toggles expanded state and animates to 90.0
        QTest.mouseClick(chevron, Qt.LeftButton)
        self.assertTrue(chevron.is_expanded())
        self.assertEqual(toggled_states, [True])
        QTest.qWait(120)
        self.assertEqual(chevron.angle, 90.0)

        # Programmatic collapse without animation snaps immediately
        chevron.set_expanded(False, animated=False)
        self.assertFalse(chevron.is_expanded())
        self.assertEqual(chevron.angle, 0.0)

        chevron.set_dark_mode(False)
        self.assertFalse(chevron.grab().isNull())

    def test_app_markdown_reader_props_zoom_and_theme(self):
        zoom_events = []
        reader = AppMarkdownReader(
            is_dark=True,
            zoom_level=1,
            border_radius=8,
            padding=12,
            on_zoom_changed=lambda lvl: zoom_events.append(lvl),
            object_name="md_reader",
        )
        self.assertIsInstance(reader, QTextBrowser)
        self.assertEqual(reader.zoom_level, 1)
        self.assertEqual(reader.objectName(), "md_reader")
        self.assertIn("#11111b", reader.styleSheet())
        self.assertIn("border-radius: 8px", reader.styleSheet())

        reader.set_markdown_content("# Title\n\n```algo\nALGORITHME Demo\nDEBUT\n  x <- 1\nFIN\n```")
        html_dark = reader.toHtml()
        self.assertIn("Title", html_dark)
        self.assertIn("ALGORITHME", html_dark)

        reader.zoom_in(2)
        self.assertEqual(reader.zoom_level, 3)
        self.assertEqual(zoom_events, [3])

        reader.zoom_out(1)
        self.assertEqual(reader.zoom_level, 2)

        reader.reset_zoom()
        self.assertEqual(reader.zoom_level, 0)

        reader.set_dark_mode(False)
        self.assertIn("#ffffff", reader.styleSheet())
        reader.resize(300, 200)
        self.assertFalse(reader.grab().isNull())


if __name__ == "__main__":
    unittest.main()
