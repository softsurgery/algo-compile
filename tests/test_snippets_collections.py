"""
Unit tests for Snippets Tree View, Collections hierarchy, and file attachments (.md, images, actual data files).
"""

import os
import shutil
import tempfile
import unittest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from ui.snippets_manager import (
    SnippetItem, CollectionNode, scan_snippets_tree,
    get_all_snippets_flat, join_file_to_snippet, create_snippet_bundle
)
from ui.snippets_view import (
    SnippetsWidget, SnippetMarkdownBrowser, SnippetImageViewer,
    SnippetFilesViewer, SnippetTreeWidget
)
from ui.insert_code_dialog import InsertCodeDialog
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


class TestSnippetsAndCollections(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="algo_snippets_test_")
        # Build collection hierarchy:
        # temp_dir/
        #   01_Calcul/
        #     somme/
        #       somme.algo
        #       somme.md
        #       somme_schema.png
        #       data.csv
        #   02_Tris/
        #     standalone_tri.algo
        self.col1 = os.path.join(self.temp_dir, "01_Calcul")
        os.makedirs(self.col1, exist_ok=True)
        self.bundle1 = os.path.join(self.col1, "somme")
        os.makedirs(self.bundle1, exist_ok=True)

        with open(os.path.join(self.bundle1, "somme.algo"), "w", encoding="utf-8") as f:
            f.write("ALGORITHME Somme\nDEBUT\nEcrire(1 + 1)\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n/ /\n")

        with open(os.path.join(self.bundle1, "somme.md"), "w", encoding="utf-8") as f:
            f.write("# Somme\nExplication mathématique de l'algorithme.")

        with open(os.path.join(self.bundle1, "somme_schema.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\x9f\x01\x01\x04\x01\x03\x18\xed\x00\x00\x00\x00IEND\xaeB`\x82")

        with open(os.path.join(self.bundle1, "data.csv"), "w", encoding="utf-8") as f:
            f.write("a,b,c\n1,2,3\n")

        self.col2 = os.path.join(self.temp_dir, "02_Tris")
        os.makedirs(self.col2, exist_ok=True)
        with open(os.path.join(self.col2, "standalone_tri.algo"), "w", encoding="utf-8") as f:
            f.write("ALGORITHME Tri\nDEBUT\nEcrire(0)\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n/ /\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scanner_collection_and_bundle_discovery(self):
        collections = scan_snippets_tree(root_dirs=[self.temp_dir])
        self.assertEqual(len(collections), 2)

        # First collection
        c1 = next((c for c in collections if "Calcul" in c.name), None)
        self.assertIsNotNone(c1)
        self.assertEqual(len(c1.snippets), 1)

        snippet = c1.snippets[0]
        self.assertEqual(snippet.title, "Somme")
        self.assertTrue(snippet.is_bundle)
        self.assertIsNotNone(snippet.md_file)
        self.assertTrue(snippet.md_file.endswith(".md"))
        self.assertEqual(len(snippet.image_files), 1)
        self.assertTrue(snippet.image_files[0].endswith(".png"))
        # All files except .algo and primary .md are listed in companion_files
        self.assertEqual(len(snippet.companion_files), 2)
        self.assertTrue(any(f.endswith(".csv") for f in snippet.companion_files))
        self.assertTrue(any(f.endswith(".png") for f in snippet.companion_files))

        # Verify Markdown content retrieval and 4-line description
        md_text = snippet.get_md_content()
        self.assertIn("Explication mathématique", md_text)
        first_lines = snippet.get_first_lines_md(4)
        self.assertIn("Explication mathématique", first_lines)

    def test_join_file_to_bundle(self):
        collections = scan_snippets_tree(root_dirs=[self.temp_dir])
        c1 = next(c for c in collections if "Calcul" in c.name)
        snippet = c1.snippets[0]

        # Create external companion file
        ext_doc = os.path.join(self.temp_dir, "notes_prof.txt")
        with open(ext_doc, "w", encoding="utf-8") as f:
            f.write("Notes pédagogiques complémentaires")

        dest = join_file_to_snippet(snippet, ext_doc)
        self.assertTrue(os.path.exists(dest))
        self.assertIn(dest, snippet.companion_files)

        # Create external extra image
        ext_img = os.path.join(self.temp_dir, "extra_graph.png")
        shutil.copy2(snippet.image_files[0], ext_img)
        dest_img = join_file_to_snippet(snippet, ext_img)
        self.assertTrue(os.path.exists(dest_img))
        self.assertIn(dest_img, snippet.image_files)

    def test_join_file_to_standalone_snippet_converts_to_bundle(self):
        collections = scan_snippets_tree(root_dirs=[self.temp_dir])
        c2 = next(c for c in collections if "Tris" in c.name)
        snippet = c2.snippets[0]
        self.assertFalse(snippet.is_bundle)

        # Join an external md documentation
        ext_md = os.path.join(self.temp_dir, "tri_doc.md")
        with open(ext_md, "w", encoding="utf-8") as f:
            f.write("# Guide du Tri\nAlgorithme de tri optimisé.")

        join_file_to_snippet(snippet, ext_md)
        self.assertTrue(snippet.is_bundle)
        self.assertIsNotNone(snippet.md_file)
        self.assertTrue(snippet.md_file.endswith("tri_doc.md"))
        self.assertIn("Guide du Tri", snippet.get_md_content())

    def test_create_snippet_bundle(self):
        new_snip = create_snippet_bundle(
            self.col1,
            "Recherche Dichotomique",
            algo_code="ALGORITHME Dicho\nDEBUT\nFIN\nTableau de déclaration des objets globaux\nObjet Type\n/ /\n",
            md_content="# Recherche Dicho\nComplexité en O(log n)"
        )
        self.assertTrue(new_snip.is_bundle)
        self.assertTrue(os.path.isdir(new_snip.folder_path))
        self.assertTrue(os.path.exists(new_snip.code_file))
        self.assertTrue(os.path.exists(new_snip.md_file))
        self.assertIn("O(log n)", new_snip.get_md_content())

    def test_snippets_widget_ui(self):
        widget = SnippetsWidget(is_dark=False)
        self.assertGreaterEqual(widget.tree_widget.topLevelItemCount(), 1)

        # Verify tree view column count is 1 and does NOT mention joints
        self.assertEqual(widget.tree_widget.columnCount(), 1)
        headers = [widget.tree_widget.headerItem().text(i) for i in range(widget.tree_widget.columnCount())]
        self.assertNotIn("Joints", headers)

        # Select a snippet with companion files (e.g. somme_diviseurs) to verify all 3 tabs
        for col in widget._collections:
            for snip in col.snippets:
                if snip.companion_files:
                    widget._on_snippet_selected(snip)
                    break

        # Check tab count and tab names: strictly 3 tabs (Code, Documentation, Fichiers associés)
        self.assertEqual(widget.tabs.count(), 3)
        tab_names = [widget.tabs.tabText(i) for i in range(widget.tabs.count())]
        self.assertTrue(any("Code" in t for t in tab_names))
        self.assertTrue(any("Documentation" in t or ".md" in t for t in tab_names))
        self.assertTrue(any("Fichiers" in t for t in tab_names))
        self.assertFalse(any("Image" in t or "Schéma" in t for t in tab_names))

        # Verify description at top of dialog widget displays the 4-line description
        if widget.current_snippet:
            self.assertTrue(len(widget.lbl_desc.text()) > 0)

        # Verify tab icons and buttons are loaded (not null)
        for i in range(widget.tabs.count()):
            self.assertFalse(widget.tabs.tabIcon(i).isNull())
        self.assertFalse(widget.btn_refresh.icon().isNull())

        # Verify UI does not allow user joining / deleting files (managed via app files)
        self.assertFalse(hasattr(widget, "btn_join_file"))
        self.assertFalse(hasattr(widget.image_viewer, "btn_join_pic"))
        self.assertFalse(hasattr(widget.files_viewer, "btn_join"))
        self.assertFalse(hasattr(widget.files_viewer, "btn_delete"))

        # Check search filtering
        widget._on_search_changed("tri")
        # Ensure widgets don't crash on theme toggle or zoom
        widget.set_dark_mode(True)
        widget.zoom_in()
        widget.zoom_out()
        widget.set_dark_mode(False)
        widget.close()

    def test_file_tab_visibility_based_on_companion_files(self):
        widget = SnippetsWidget(is_dark=False)
        widget.show()
        all_snips = [c.get_all_snippets() for c in widget._collections]
        flat = [s for sub in all_snips for s in sub]

        # Find a snippet with files and one without files
        snip_with_files = next((s for s in flat if s.companion_files), None)
        snip_without_files = next((s for s in flat if not s.companion_files), None)

        self.assertIsNotNone(snip_with_files)
        self.assertIsNotNone(snip_without_files)

        # When selecting snippet with files, "Fichiers associés" tab must be present
        widget._on_snippet_selected(snip_with_files)
        self.assertNotEqual(widget.tabs.indexOf(widget.files_viewer), -1)

        # When selecting snippet without files, "Fichiers associés" tab must NOT be shown
        widget._on_snippet_selected(snip_without_files)
        self.assertEqual(widget.tabs.indexOf(widget.files_viewer), -1)

        # Switching back to snippet with files restores the tab
        widget._on_snippet_selected(snip_with_files)
        self.assertNotEqual(widget.tabs.indexOf(widget.files_viewer), -1)
        widget.close()

    def test_insert_code_dialog_size_and_icons(self):
        dlg = InsertCodeDialog(None, is_dark=False)
        self.assertGreaterEqual(dlg.width(), 1150)
        self.assertGreaterEqual(dlg.height(), 700)
        self.assertFalse(dlg.btn_insert.icon().isNull())
        self.assertFalse(dlg.btn_new_tab.icon().isNull())
        self.assertFalse(dlg.btn_cancel.icon().isNull())
        self.assertFalse(hasattr(dlg, "btn_copy"))
        self.assertFalse(hasattr(dlg, "btn_fullscreen"))
        self.assertEqual(dlg.tree_widget.columnCount(), 1)
        # Verify top-left app icon is removed (1x1 transparent icon)
        icon = dlg.windowIcon()
        self.assertFalse(icon.isNull())
        self.assertEqual(icon.pixmap(1, 1).size().width(), 1)
        # Verify no duplicate bottom action buttons inside dialog
        self.assertFalse(dlg.snippets_widget.bottom_actions_bar.isVisible())
        dlg.close()

    def test_main_window_snippets_tab_and_insert(self):
        win = MainWindow()
        # Verify "Extraits & Collections" tab is removed from side panels
        tab_titles = [win.side_tabs.tabText(i) for i in range(win.side_tabs.count())]
        self.assertNotIn("Extraits & Collections", tab_titles)

        # Test side insertion
        test_code = "ALGORITHME TestInsert\nDEBUT\nEcrire(42)\nFIN\n"
        win._on_snippet_side_insert(test_code, "Snippet Test")
        editor = win.current_editor()
        self.assertIsNotNone(editor)
        self.assertIn("TestInsert", editor.toPlainText())

        # Test new tab from snippet
        win._on_snippet_side_new_tab(test_code, "Onglet Test")
        self.assertGreaterEqual(win.tab_widget.count(), 2)
        win.close()

    def test_snippet_markdown_browser_zoom_scales_all_text(self):
        from PyQt5.QtGui import QWheelEvent, QKeyEvent
        from PyQt5.QtCore import Qt, QPoint, QPointF, QEvent

        browser = SnippetMarkdownBrowser(is_dark=False)
        browser.set_markdown_content(
            "# Heading 1\n\nParagraph body text\n\n- List item\n\n### Heading 3\n\n```algo\nx <- 1\n```"
        )

        def get_block_sizes():
            sizes = {}
            blk = browser.document().begin()
            while blk.isValid():
                it = blk.begin()
                if not it.atEnd():
                    f = it.fragment().charFormat().font()
                    size = f.pixelSize() if f.pixelSize() > 0 else f.pointSizeF()
                    sizes[blk.text().strip()] = size
                blk = blk.next()
            return sizes

        base = get_block_sizes()
        for _ in range(3):
            browser.zoom_in()
        zoomed_in = get_block_sizes()

        for key in ("Heading 1", "Paragraph body text", "List item", "Heading 3", "x <- 1"):
            self.assertGreater(zoomed_in[key], base[key], f"{key} did not grow on zoom_in")

        # Test Ctrl + Wheel zoom_out and zoom_in
        wheel_up = QWheelEvent(
            QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, 120),
            Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False
        )
        browser.wheelEvent(wheel_up)
        self.assertEqual(browser.zoom_level, 4)

        wheel_down = QWheelEvent(
            QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, -120),
            Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False
        )
        browser.wheelEvent(wheel_down)
        self.assertEqual(browser.zoom_level, 3)

        # Test Ctrl + 0 resets zoom
        key_reset = QKeyEvent(QEvent.KeyPress, Qt.Key_0, Qt.ControlModifier, "0")
        browser.keyPressEvent(key_reset)
        self.assertEqual(browser.zoom_level, 0)
        self.assertEqual(get_block_sizes(), base)
        browser.close()


if __name__ == "__main__":
    unittest.main()
