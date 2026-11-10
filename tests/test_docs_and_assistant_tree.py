"""
Tests for docs directory structure and AssistantView tree view navigation.
"""

import os
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.assistant_view import AssistantView, _clean_category_name, _extract_doc_title

# Ensure QApplication exists for GUI tests
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestDocsAndAssistantTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

    def test_docs_directory_exists_and_populated(self):
        """Verifies that the docs/ folder exists and contains category folders with .md docs."""
        self.assertTrue(os.path.isdir(self.docs_dir), f"docs directory not found at {self.docs_dir}")
        categories = [d for d in os.listdir(self.docs_dir) if os.path.isdir(os.path.join(self.docs_dir, d))]
        self.assertGreaterEqual(len(categories), 5, "Expected at least 5 category folders in docs/")

        total_md_files = 0
        for cat in categories:
            cat_path = os.path.join(self.docs_dir, cat)
            md_files = [f for f in os.listdir(cat_path) if f.endswith(".md")]
            self.assertGreater(len(md_files), 0, f"Category folder {cat} has no .md files")
            total_md_files += len(md_files)
            for f in md_files:
                full_p = os.path.join(cat_path, f)
                with open(full_p, "r", encoding="utf-8") as fp:
                    content = fp.read()
                self.assertGreater(len(content.strip()), 20, f"File {f} in {cat} is empty or too short")

        self.assertGreaterEqual(total_md_files, 15, "Expected at least 15 markdown doc files in docs/")

    def test_helper_clean_and_extract_titles(self):
        """Tests category name formatting and markdown title extraction."""
        cat_cleaned = _clean_category_name("01_Structure_et_Declarations")
        self.assertEqual(cat_cleaned, "1. Structure et Declarations")

        cat_no_prefix = _clean_category_name("General")
        self.assertEqual(cat_no_prefix, "General")

        # Test title extraction from sample file
        sample_path = os.path.join(self.docs_dir, "01_Structure_et_Declarations", "01_Forme_Generale.md")
        if os.path.exists(sample_path):
            title = _extract_doc_title(sample_path)
            self.assertIn("Forme Générale", title)

    def test_assistant_view_tree_population(self):
        """Verifies that AssistantView populates the QTreeWidget with categories and documents."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        self.assertGreater(view.tree.topLevelItemCount(), 0, "Tree widget should have top level items")

        first_top = view.tree.topLevelItem(0)
        self.assertGreater(first_top.childCount(), 0, "Top level category should contain child doc items")

        # Check that current selection loaded valid HTML into browser
        self.assertGreater(len(view.browser.toHtml()), 50, "Browser should contain rendered document HTML")
        self.assertIn("Forme Générale", view.lbl_title.text(), "Header title should reflect current document")
        self.assertFalse(first_top.icon(0).isNull(), "Category item should have a valid vector icon")
        if first_top.childCount() > 0:
            self.assertFalse(first_top.child(0).icon(0).isNull(), "Document item should have a valid vector icon")

    def test_assistant_view_selection_change(self):
        """Tests that selecting another item updates the browser and title."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        first_top = view.tree.topLevelItem(0)
        if first_top.childCount() > 1:
            second_child = first_top.child(1)
            view._load_item(second_child)
            second_title = second_child.text(0).strip()
            self.assertIn(second_title, view.lbl_title.text())

    def test_search_filtering(self):
        """Tests filtering the tree by keyword."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        view.search_edit.setText("boucle")
        # Ensure that top levels or children containing 'boucle' or child matches are visible
        visible_items = 0
        for i in range(view.tree.topLevelItemCount()):
            top = view.tree.topLevelItem(i)
            if not top.isHidden():
                visible_items += 1
        self.assertGreater(visible_items, 0, "Filtering by 'boucle' should keep matching categories visible")

        # Clear search
        view.search_edit.setText("")
        for i in range(view.tree.topLevelItemCount()):
            self.assertFalse(view.tree.topLevelItem(i).isHidden(), "Clearing search should restore all categories")

    def test_layout_orientation_toggle(self):
        """Tests switching layout orientation between vertical and horizontal."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        initial_orient = view.splitter.orientation()
        view._toggle_splitter_orientation()
        self.assertNotEqual(view.splitter.orientation(), initial_orient)
        view._toggle_splitter_orientation()
        self.assertEqual(view.splitter.orientation(), initial_orient)

    def test_error_advice_and_back_to_guide(self):
        """Tests display of error advice and switching back to documentation."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        initial_title = view.lbl_title.text()

        # Trigger error advice
        view.show_error_advice("Variable 'x' non déclarée dans le TDOG", line_no=12)
        self.assertTrue(view._is_error_view)
        self.assertIn("Diagnostic & Aide", view.lbl_title.text())
        self.assertFalse(view.btn_back_to_guide.isHidden())
        self.assertIn("TDOG", view.browser.toHtml())

        # Click back to guide
        view._on_back_to_guide_clicked()
        self.assertFalse(view._is_error_view)
        self.assertTrue(view.btn_back_to_guide.isHidden())
        self.assertEqual(view.lbl_title.text(), initial_title)

    def test_dark_mode_toggle(self):
        """Tests dark mode stylesheet updates and high-contrast text rendering."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        view.set_dark_mode(True)
        self.assertTrue(view.is_dark)

        # Ensure no black text (#000000) is rendered in dark mode
        rendered_html = view.browser.toHtml()
        self.assertNotIn("#000000", rendered_html, "Dark mode HTML should not contain black text (#000000)")

        view.set_dark_mode(False)
        self.assertFalse(view.is_dark)

    def test_code_block_syntax_highlighting(self):
        """Verifies that code blocks in docs are properly syntax-colored."""
        view = AssistantView(is_dark=True, docs_dir=self.docs_dir)
        algo_doc = """# Test
```algo
ALGORITHME Demo
DEBUT
  // Ceci est un commentaire
  x <- 42
  Ecrire_nl("Bonjour", x)
FIN
```
"""
        view._render_markdown_content(algo_doc)
        html_out = view.browser.toHtml()
        # Verify colored spans exist for keywords, comments, numbers, strings, etc.
        self.assertIn("style=", html_out)
        self.assertIn("ALGORITHME", html_out)
        self.assertIn("DEBUT", html_out)
        self.assertIn("Bonjour", html_out)

        # Light mode highlighting
        view.set_dark_mode(False)
        view._render_markdown_content(algo_doc)
        html_light = view.browser.toHtml()
        self.assertIn("style=", html_light)

    def test_documentation_zoom_scaling(self):
        """Verifies that documentation zoom scales text and code blocks proportionally."""
        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        test_doc = """# Test Zoom
```algo
x <- 10
```
"""
        view._render_markdown_content(test_doc)
        self.assertEqual(view.zoom_level, 0)
        initial_html = view.browser.toHtml()
        self.assertTrue("font-size:12px;" in initial_html or "font-size: 12px;" in initial_html)

        # Zoom in
        view.zoom_in(3)
        self.assertEqual(view.zoom_level, 3)
        zoomed_in_html = view.browser.toHtml()
        self.assertTrue("font-size:15px;" in zoomed_in_html or "font-size: 15px;" in zoomed_in_html)

        # Zoom out
        view.zoom_out(1)
        self.assertEqual(view.zoom_level, 2)
        zoomed_html = view.browser.toHtml()
        self.assertTrue("font-size:14px;" in zoomed_html or "font-size: 14px;" in zoomed_html)

        # Reset zoom
        view.reset_zoom()
        self.assertEqual(view.zoom_level, 0)
        reset_html = view.browser.toHtml()
        self.assertTrue("font-size:12px;" in reset_html or "font-size: 12px;" in reset_html)

    def test_doc_browser_ctrl_wheel_and_keys(self):
        """Tests that Ctrl+Wheel and Ctrl+/-/0 on DocBrowser trigger zoom actions."""
        from PyQt5.QtGui import QWheelEvent, QKeyEvent
        from PyQt5.QtCore import QPointF, QPoint

        view = AssistantView(is_dark=False, docs_dir=self.docs_dir)
        view._current_content = "# Doc\n```algo\nx <- 1\n```"
        view._render_markdown_content(view._current_content)

        # Simulate Ctrl + Wheel Up
        wheel_up = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, 120), Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False)
        view.browser.wheelEvent(wheel_up)
        self.assertEqual(view.zoom_level, 1)

        # Simulate Ctrl + Wheel Down
        wheel_down = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, -120), Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False)
        view.browser.wheelEvent(wheel_down)
        self.assertEqual(view.zoom_level, 0)

        # Simulate Ctrl + Key_Plus
        key_plus = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Plus, Qt.ControlModifier, "+")
        view.browser.keyPressEvent(key_plus)
        self.assertEqual(view.zoom_level, 1)

        # Simulate Ctrl + Key_Minus
        key_minus = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Minus, Qt.ControlModifier, "-")
        view.browser.keyPressEvent(key_minus)
        self.assertEqual(view.zoom_level, 0)

        # Zoom in then reset with Ctrl + 0
        view.zoom_in(2)
        self.assertEqual(view.zoom_level, 2)
        key_zero = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_0, Qt.ControlModifier, "0")
        view.browser.keyPressEvent(key_zero)
        self.assertEqual(view.zoom_level, 0)


if __name__ == "__main__":
    unittest.main()
