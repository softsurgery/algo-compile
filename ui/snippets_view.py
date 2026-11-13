"""
Snippets and Collections UI Components for Algoo IDE.
Features:
- Hierarchical Tree View mirroring the folder structure of snippet collections.
- Multi-tab viewer for Code, Markdown documentation, Pictures/Diagrams, and Companion files.
- Capability to join / attach .md files, pictures (.png, .jpg, .svg), or any actual files.
"""

import os
import html
from typing import Optional, List, Dict

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QLineEdit, QTabWidget, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QMenu, QAction, QFileDialog, QMessageBox,
    QInputDialog, QFrame, QTextBrowser, QComboBox, QPlainTextEdit, QApplication,
    QStackedWidget
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QDesktopServices, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QSize

from ui.editor import AlgoCodeEditor
from ui.icons import create_icon
from ui.pdf_viewer import LightPdfViewer, PdfReaderWindow
from ui.snippets_manager import (
    SnippetItem, CollectionNode, scan_snippets_tree, join_file_to_snippet,
    create_snippet_bundle, IMAGE_EXTENSIONS, MD_EXTENSIONS
)
from ui.assistant_view import highlight_algo_syntax, highlight_python_syntax

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


class SnippetMarkdownBrowser(QTextBrowser):
    """High-contrast, themed markdown documentation browser for snippets."""

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.zoom_level = 0
        self._current_md = ""
        self.setOpenExternalLinks(True)
        self._apply_style()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        self._apply_style()
        if self._current_md:
            self.set_markdown_content(self._current_md)

    def zoom_in(self, delta: int = 1):
        if self.zoom_level < 15:
            self.zoom_level = min(15, self.zoom_level + delta)
            self._re_render_preserving_scroll()

    def zoom_out(self, delta: int = 1):
        if self.zoom_level > -4:
            self.zoom_level = max(-4, self.zoom_level - delta)
            self._re_render_preserving_scroll()

    def reset_zoom(self):
        if self.zoom_level != 0:
            self.zoom_level = 0
            self._re_render_preserving_scroll()

    def _re_render_preserving_scroll(self):
        if not self._current_md:
            return
        vbar = self.verticalScrollBar()
        scroll_pos = vbar.value() if vbar else 0
        self.set_markdown_content(self._current_md)
        if vbar:
            vbar.setValue(min(scroll_pos, vbar.maximum()))

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal) or event.text() in ('+', '='):
                self.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key_Minus or event.text() == '-':
                self.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key_0 or event.text() == '0':
                self.reset_zoom()
                event.accept()
                return
        super().keyPressEvent(event)

    def _apply_style(self):
        bg = "#11111b" if self.is_dark else "#ffffff"
        fg = "#cdd6f4" if self.is_dark else "#1e293b"
        border = "#313244" if self.is_dark else "#e2e8f0"
        self.setStyleSheet(
            f"QTextBrowser {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; padding: 10px; }}"
        )

    def set_markdown_content(self, md_text: str):
        self._current_md = md_text
        if not md_text.strip():
            self.setHtml("")
            return

        base_font_size = max(9, min(28, 13 + self.zoom_level))
        pre_font_size = max(8, min(26, 12 + self.zoom_level))
        h1_font_size = max(13, min(34, 17 + self.zoom_level))
        h2_font_size = max(11, min(30, 15 + self.zoom_level))
        h3_font_size = max(10, min(28, 14 + self.zoom_level))

        default_font = self.font()
        default_font.setPointSize(max(7, 10 + self.zoom_level))
        self.document().setDefaultFont(default_font)

        if self.is_dark:
            body_fg = "#cdd6f4"
            bold_fg = "#ffffff"
            h1_color = "#89b4fa"
            h2_color = "#cba6f7"
            pre_bg = "#181825"
            pre_fg = "#cdd6f4"
            pre_border = "#313244"
            code_bg = "#313244"
            code_fg = "#f9e2af"
            table_border = "#313244"
            th_bg = "#1e1e2e"
            th_fg = "#89b4fa"
            td_bg = "#11111b"
            td_fg = "#cdd6f4"
            hr_color = "#313244"
        else:
            body_fg = "#1e293b"
            bold_fg = "#0f172a"
            h1_color = "#1d4ed8"
            h2_color = "#2563eb"
            pre_bg = "#f8fafc"
            pre_fg = "#0f172a"
            pre_border = "#cbd5e1"
            code_bg = "#f1f5f9"
            code_fg = "#b45309"
            table_border = "#cbd5e1"
            th_bg = "#f1f5f9"
            th_fg = "#0f172a"
            td_bg = "#ffffff"
            td_fg = "#334155"
            hr_color = "#e2e8f0"

        # Syntax highlight fenced code blocks
        def replacer(m):
            lang = (m.group(1) or "").strip().lower()
            code_content = m.group(2)
            if lang in ("algo", "algorithme", "alg"):
                highlighted = highlight_algo_syntax(code_content, self.is_dark)
            elif lang in ("python", "py"):
                highlighted = highlight_python_syntax(code_content, self.is_dark)
            else:
                c_def = "#cdd6f4" if self.is_dark else "#0f172a"
                highlighted = f'<span style="color:{c_def};">{html.escape(code_content)}</span>'
            return f'\n\n<pre class="code-block" style="font-size: {pre_font_size}px;"><code style="font-size: {pre_font_size}px;">{highlighted}</code></pre>\n\n'

        import re
        pattern = re.compile(r'^[ \t]*(?:```|~~~)([a-zA-Z0-9_\-]*)[ \t]*\r?\n(.*?)\r?\n[ \t]*(?:```|~~~)[ \t]*$', re.DOTALL | re.MULTILINE)
        processed_md = pattern.sub(replacer, md_text)

        if HAS_MARKDOWN:
            html_body = markdown.markdown(processed_md, extensions=["tables", "fenced_code", "nl2br"])
        else:
            html_body = f"<pre>{html.escape(processed_md)}</pre>"

        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          body, p, li, td, th, div {{
            color: {body_fg};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: {base_font_size}px;
            line-height: 1.55;
            padding: 4px;
          }}
          h1 {{ color: {h1_color}; font-size: {h1_font_size}px; border-bottom: 1px solid {hr_color}; padding-bottom: 4px; }}
          h2 {{ color: {h2_color}; font-size: {h2_font_size}px; margin-top: 14px; margin-bottom: 6px; }}
          h3, h4 {{ color: {h2_color}; font-size: {h3_font_size}px; margin-top: 10px; margin-bottom: 4px; }}
          b, strong {{ color: {bold_fg}; font-weight: bold; }}
          code {{
            background-color: {code_bg};
            color: {code_fg};
            padding: 2px 5px;
            border-radius: 4px;
            font-family: "JetBrains Mono", Consolas, monospace;
            font-size: {max(7, pre_font_size - 1)}px;
          }}
          pre, pre code, pre span {{
            font-family: "JetBrains Mono", Consolas, monospace;
            font-size: {pre_font_size}px;
          }}
          pre.code-block {{
            background-color: {pre_bg};
            border: 1px solid {pre_border};
            border-radius: 6px;
            padding: 8px 12px;
            margin: 8px 0;
            overflow-x: auto;
          }}
          table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
            border: 1px solid {table_border};
            font-size: {base_font_size}px;
          }}
          th {{
            background-color: {th_bg};
            color: {th_fg};
            font-weight: bold;
            padding: 6px 10px;
            border: 1px solid {table_border};
            text-align: left;
          }}
          td {{
            background-color: {td_bg};
            color: {td_fg};
            padding: 6px 10px;
            border: 1px solid {table_border};
          }}
        </style>
        </head>
        <body>
        {html_body}
        </body>
        </html>
        """
        self.setHtml(styled_html)


class SnippetImageViewer(QWidget):
    """Interactive Image viewer for snippets with zoom, aspect ratio preservation, and picture switching."""

    join_image_requested = pyqtSignal()

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.image_paths: List[str] = []
        self._current_pixmap: Optional[QPixmap] = None
        self._zoom_factor = 1.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Toolbar
        self.toolbar_widget = QWidget()
        tb_layout = QHBoxLayout(self.toolbar_widget)
        tb_layout.setContentsMargins(4, 4, 4, 4)
        tb_layout.setSpacing(6)

        self.cb_images = QComboBox()
        self.cb_images.currentIndexChanged.connect(self._on_image_selected)
        tb_layout.addWidget(self.cb_images, 1)

        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setFixedSize(28, 26)
        self.btn_zoom_out.setToolTip("Zoom arrière")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        tb_layout.addWidget(self.btn_zoom_out)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setFixedWidth(45)
        self.lbl_zoom.setAlignment(Qt.AlignCenter)
        tb_layout.addWidget(self.lbl_zoom)

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setFixedSize(28, 26)
        self.btn_zoom_in.setToolTip("Zoom avant")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_fit = QPushButton("Adapter")
        self.btn_zoom_fit.setFixedHeight(26)
        self.btn_zoom_fit.setToolTip("Adapter l'image à la vue")
        self.btn_zoom_fit.clicked.connect(self.fit_to_view)
        tb_layout.addWidget(self.btn_zoom_fit)

        layout.addWidget(self.toolbar_widget)

        # Scroll area for the image label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.lbl_image)

        # Empty state container
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(10)

        self.lbl_empty_icon = QLabel()
        self.lbl_empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.lbl_empty_icon)

        self.lbl_empty_msg = QLabel("Aucune image ou schéma disponible pour cet extrait.")
        self.lbl_empty_msg.setAlignment(Qt.AlignCenter)
        self.lbl_empty_msg.setFont(QFont("SansSerif", 10))
        empty_layout.addWidget(self.lbl_empty_msg)

        layout.addWidget(self.scroll_area, 1)
        layout.addWidget(self.empty_widget, 1)

        self.set_dark_mode(self.is_dark)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.btn_zoom_in.setIcon(create_icon("zoom_in", icon_color, 14))
        self.btn_zoom_out.setIcon(create_icon("zoom_out", icon_color, 14))
        self.lbl_empty_icon.setPixmap(create_icon("image", icon_color, 48).pixmap(48, 48))

        bg = "#11111b" if is_dark else "#ffffff"
        border = "#313244" if is_dark else "#e2e8f0"
        self.scroll_area.setStyleSheet(
            f"QScrollArea {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        self.empty_widget.setStyleSheet(
            f"QWidget {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        msg_color = "#9399b2" if is_dark else "#64748b"
        self.lbl_empty_msg.setStyleSheet(f"color: {msg_color};")

    def set_images(self, paths: List[str]):
        self.image_paths = paths
        self.cb_images.blockSignals(True)
        self.cb_images.clear()

        if not paths:
            self.toolbar_widget.setVisible(False)
            self.scroll_area.setVisible(False)
            self.empty_widget.setVisible(True)
            self._current_pixmap = None
            self.cb_images.blockSignals(False)
            return

        self.empty_widget.setVisible(False)
        self.scroll_area.setVisible(True)
        self.toolbar_widget.setVisible(True)

        for p in paths:
            self.cb_images.addItem(os.path.basename(p), p)

        self.cb_images.blockSignals(False)
        self._load_image(paths[0])

    def _on_image_selected(self, index: int):
        if 0 <= index < len(self.image_paths):
            self._load_image(self.image_paths[index])

    def _load_image(self, path: str):
        if not os.path.exists(path):
            return
        pix = QPixmap(path)
        if pix.isNull():
            return
        self._current_pixmap = pix
        self._zoom_factor = 1.0
        self.fit_to_view()

    def fit_to_view(self):
        if not self._current_pixmap:
            return
        area_size = self.scroll_area.viewport().size()
        if area_size.width() <= 10 or area_size.height() <= 10:
            self._zoom_factor = 1.0
        else:
            w_ratio = area_size.width() / self._current_pixmap.width()
            h_ratio = area_size.height() / self._current_pixmap.height()
            self._zoom_factor = min(w_ratio, h_ratio, 1.0)
        self._update_display()

    def zoom_in(self):
        if self._zoom_factor < 5.0:
            self._zoom_factor *= 1.25
            self._update_display()

    def zoom_out(self):
        if self._zoom_factor > 0.1:
            self._zoom_factor /= 1.25
            self._update_display()

    def _update_display(self):
        if not self._current_pixmap:
            return
        target_w = max(20, int(self._current_pixmap.width() * self._zoom_factor))
        target_h = max(20, int(self._current_pixmap.height() * self._zoom_factor))
        scaled_pix = self._current_pixmap.scaled(
            target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.lbl_image.setPixmap(scaled_pix)
        self.lbl_zoom.setText(f"{int(self._zoom_factor * 100)}%")


class SnippetFilesViewer(QWidget):
    """Viewer for companion and joined actual files (.txt, .csv, .json, .in, etc.)."""

    insert_content_requested = pyqtSignal(str)
    join_file_requested = pyqtSignal()
    file_deleted_requested = pyqtSignal(str)

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.file_paths: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Top file table
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nom du fichier", "Type", "Taille"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_file_selected)
        layout.addWidget(self.table, 1)

        # File preview editor / viewer
        self.lbl_preview = QLabel("Aperçu du contenu du fichier sélectionné :")
        self.lbl_preview.setFont(QFont("SansSerif", 9, QFont.Bold))
        layout.addWidget(self.lbl_preview)

        self.preview_stack = QStackedWidget()

        # Page 0: Text Preview
        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setFont(QFont("JetBrains Mono", 10))
        self.preview_stack.addWidget(self.text_preview)

        # Page 1: Image Preview
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_scroll.setAlignment(Qt.AlignCenter)
        self.lbl_image_preview = QLabel()
        self.lbl_image_preview.setAlignment(Qt.AlignCenter)
        self.image_scroll.setWidget(self.lbl_image_preview)
        self.preview_stack.addWidget(self.image_scroll)

        # Page 2: PDF Preview (Light PDF Viewer)
        self.pdf_viewer = LightPdfViewer(self, is_dark=self.is_dark)
        self.pdf_viewer.detach_requested.connect(self._open_pdf_detached)
        self.preview_stack.addWidget(self.pdf_viewer)

        layout.addWidget(self.preview_stack, 2)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.btn_open_system = QPushButton("Ouvrir avec le système")
        self.btn_open_system.clicked.connect(self._open_in_system)
        btn_layout.addWidget(self.btn_open_system)

        self.btn_open_pdf_fs = QPushButton("Lecteur PDF plein écran")
        self.btn_open_pdf_fs.setVisible(False)
        self.btn_open_pdf_fs.clicked.connect(self._on_open_pdf_fs_clicked)
        btn_layout.addWidget(self.btn_open_pdf_fs)

        self.btn_insert_content = QPushButton("Insérer le contenu")
        self.btn_insert_content.clicked.connect(self._on_insert_clicked)
        btn_layout.addWidget(self.btn_insert_content)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.set_dark_mode(self.is_dark)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.btn_open_system.setIcon(create_icon("open", icon_color, 16))
        self.btn_open_pdf_fs.setIcon(create_icon("fullscreen", icon_color, 16))
        self.btn_insert_content.setIcon(create_icon("step", icon_color, 16))
        self.btn_open_system.setIconSize(QSize(16, 16))
        self.btn_open_pdf_fs.setIconSize(QSize(16, 16))
        self.btn_insert_content.setIconSize(QSize(16, 16))

        if hasattr(self, "pdf_viewer"):
            self.pdf_viewer.set_dark_mode(is_dark)

        bg = "#11111b" if is_dark else "#ffffff"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        border = "#313244" if is_dark else "#e2e8f0"
        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        self.text_preview.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        self.image_scroll.setStyleSheet(
            f"QScrollArea {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        lbl_c = "#9399b2" if is_dark else "#64748b"
        self.lbl_preview.setStyleSheet(f"color: {lbl_c};")

    def set_files(self, paths: List[str]):
        self.file_paths = paths
        self.table.setRowCount(0)
        self.text_preview.clear()
        self.lbl_image_preview.clear()

        for p in paths:
            if not os.path.exists(p):
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)

            fname = os.path.basename(p)
            ext = os.path.splitext(p)[1].upper() or "FICHIER"
            sz_bytes = os.path.getsize(p)
            sz_str = f"{sz_bytes} B" if sz_bytes < 1024 else f"{sz_bytes / 1024:.1f} KB"

            it_name = QTableWidgetItem(fname)
            it_name.setData(Qt.UserRole, p)
            if ext == ".PDF":
                it_name.setIcon(create_icon("pdf", "#ef4444", 16))
            elif ext.lower() in IMAGE_EXTENSIONS:
                it_name.setIcon(create_icon("image", "#10b981", 16))
            else:
                it_name.setIcon(create_icon("doc", "#89b4fa" if self.is_dark else "#2563eb", 16))

            it_type = QTableWidgetItem(ext)
            it_size = QTableWidgetItem(sz_str)

            self.table.setItem(row, 0, it_name)
            self.table.setItem(row, 1, it_type)
            self.table.setItem(row, 2, it_size)

        if self.table.rowCount() > 0:
            self.table.selectRow(0)

    def _selected_path(self) -> Optional[str]:
        row = self.table.currentRow()
        if row >= 0:
            it = self.table.item(row, 0)
            if it:
                return it.data(Qt.UserRole)
        return None

    def _on_file_selected(self):
        p = self._selected_path()
        if not p or not os.path.exists(p):
            self.text_preview.setPlainText("")
            self.lbl_image_preview.clear()
            self.preview_stack.setCurrentIndex(0)
            self.btn_insert_content.setEnabled(False)
            self.btn_insert_content.setVisible(False)
            self.btn_open_pdf_fs.setVisible(False)
            return

        ext = os.path.splitext(p)[1].lower()

        # 1. PDF File
        if ext == ".pdf":
            self.preview_stack.setCurrentIndex(2)
            self.pdf_viewer.load_pdf(p)
            self.btn_insert_content.setEnabled(False)
            self.btn_insert_content.setVisible(False)
            self.btn_open_pdf_fs.setVisible(True)
            return

        self.btn_open_pdf_fs.setVisible(False)

        # 2. Image File
        if ext in IMAGE_EXTENSIONS:
            self.preview_stack.setCurrentIndex(1)
            pix = QPixmap(p)
            if not pix.isNull():
                scaled = pix.scaled(600, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_image_preview.setPixmap(scaled)
            else:
                self.lbl_image_preview.setText("Impossible de charger l'image.")
            self.btn_insert_content.setEnabled(False)
            self.btn_insert_content.setVisible(False)
            return

        # 3. Text/Data File
        self.preview_stack.setCurrentIndex(0)
        self.btn_insert_content.setVisible(True)
        self.btn_insert_content.setEnabled(True)
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read(50000)
            self.text_preview.setPlainText(content)
        except UnicodeDecodeError:
            try:
                with open(p, "r", encoding="latin-1") as f:
                    content = f.read(50000)
                self.text_preview.setPlainText(content)
            except Exception:
                self.text_preview.setPlainText("[Fichier binaire ou format non affichable en texte direct]")
                self.btn_insert_content.setEnabled(False)
        except Exception as e:
            self.text_preview.setPlainText(f"Erreur lors de la lecture : {e}")
            self.btn_insert_content.setEnabled(False)

    def _open_pdf_detached(self, pdf_path: str):
        """Opens the PDF reader in a separate top-level window."""
        parent_win = self.window() if self.window() else None
        self._pdf_window = PdfReaderWindow(pdf_path, parent=parent_win, is_dark=self.is_dark, start_fullscreen=False)
        self._pdf_window.show()
        self._pdf_window.raise_()
        self._pdf_window.activateWindow()

    def _on_open_pdf_fs_clicked(self):
        """Opens the selected PDF directly in a separate full-screen window."""
        p = self._selected_path()
        if p and p.lower().endswith(".pdf"):
            parent_win = self.window() if self.window() else None
            self._pdf_window = PdfReaderWindow(p, parent=parent_win, is_dark=self.is_dark, start_fullscreen=True)
            self._pdf_window.show()
            self._pdf_window.raise_()
            self._pdf_window.activateWindow()

    def _open_in_system(self):
        p = self._selected_path()
        if p and os.path.exists(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def _on_insert_clicked(self):
        txt = self.text_preview.toPlainText()
        if txt and not txt.startswith("["):
            self.insert_content_requested.emit(txt)

    def _on_delete_clicked(self):
        p = self._selected_path()
        if p:
            self.file_deleted_requested.emit(p)


class SnippetTreeWidget(QTreeWidget):
    """Tree Widget displaying collections and snippets matching disk folder hierarchy."""

    snippet_selected = pyqtSignal(object)  # SnippetItem
    snippet_double_clicked = pyqtSignal(object)  # SnippetItem
    snippet_new_tab_requested = pyqtSignal(object)  # SnippetItem
    join_file_requested = pyqtSignal(object)  # SnippetItem
    new_snippet_requested = pyqtSignal(str)  # collection_path
    new_collection_requested = pyqtSignal(str)  # parent_path
    delete_snippet_requested = pyqtSignal(object)  # SnippetItem

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setColumnCount(1)
        self.setHeaderLabels(["Collections & Extraits"])
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.setAnimated(True)
        self.setIndentation(16)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_double_clicked)
        self._apply_style()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        self._apply_style()

    def _apply_style(self):
        bg = "#181825" if self.is_dark else "#ffffff"
        fg = "#cdd6f4" if self.is_dark else "#1e293b"
        border = "#313244" if self.is_dark else "#e2e8f0"
        hover = "#313244" if self.is_dark else "#f1f5f9"
        sel_bg = "#45475a" if self.is_dark else "#e2e8f0"
        sel_fg = "#ffffff" if self.is_dark else "#0f172a"

        self.setStyleSheet(
            f"QTreeWidget {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; outline: none; }}"
            f"QTreeWidget::item {{ padding: 5px 6px; border-radius: 4px; }}"
            f"QTreeWidget::item:hover {{ background-color: {hover}; }}"
            f"QTreeWidget::item:selected {{ background-color: {sel_bg}; color: {sel_fg}; font-weight: bold; }}"
            f"QHeaderView::section {{ background-color: {bg}; color: {fg}; border: none; border-bottom: 1px solid {border}; padding: 4px; font-weight: bold; }}"
        )

    def populate(self, collections: List[CollectionNode]):
        self.clear()
        folder_icon = create_icon("folder", "#fab387" if self.is_dark else "#d97706")
        code_icon = create_icon("python", "#89b4fa" if self.is_dark else "#2563eb")

        def add_collection_node(col: CollectionNode, parent_item=None):
            if parent_item is None:
                item = QTreeWidgetItem(self)
            else:
                item = QTreeWidgetItem(parent_item)

            item.setText(0, col.name)
            item.setIcon(0, folder_icon)
            item.setData(0, Qt.UserRole, ("collection", col))
            item.setExpanded(True)

            # Subcollections
            for sub_col in col.subcollections:
                add_collection_node(sub_col, item)

            # Snippets
            for snip in col.snippets:
                s_item = QTreeWidgetItem(item)
                s_item.setText(0, snip.title)
                s_item.setIcon(0, code_icon)
                s_item.setData(0, Qt.UserRole, ("snippet", snip))

        for c in collections:
            add_collection_node(c)

    def _on_selection_changed(self):
        items = self.selectedItems()
        if not items:
            return
        item = items[0]
        data = item.data(0, Qt.UserRole)
        if data and data[0] == "snippet":
            self.snippet_selected.emit(data[1])

    def _on_double_clicked(self, item: QTreeWidgetItem, col: int):
        data = item.data(0, Qt.UserRole)
        if data and data[0] == "snippet":
            self.snippet_double_clicked.emit(data[1])

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        menu = QMenu(self)
        icon_color = "#cdd6f4" if self.is_dark else "#475569"

        current_snippet: Optional[SnippetItem] = None
        current_col_path: str = ""

        if item:
            data = item.data(0, Qt.UserRole)
            if data:
                if data[0] == "snippet":
                    current_snippet = data[1]
                    current_col_path = current_snippet.folder_path
                elif data[0] == "collection":
                    current_col_path = data[1].folder_path

        if current_snippet:
            act_insert = menu.addAction("Insérer dans l'éditeur")
            act_insert.setIcon(create_icon("step", icon_color))
            act_insert.triggered.connect(lambda: self.snippet_double_clicked.emit(current_snippet))

            act_new_tab = menu.addAction("Ouvrir dans un nouvel onglet")
            act_new_tab.setIcon(create_icon("new", icon_color))
            act_new_tab.triggered.connect(lambda: self.snippet_new_tab_requested.emit(current_snippet))

            menu.addSeparator()

            act_open_folder = menu.addAction("Ouvrir le dossier dans l'explorateur")
            act_open_folder.setIcon(create_icon("folder", icon_color))
            act_open_folder.triggered.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(current_snippet.folder_path)))

        if not menu.isEmpty():
            menu.exec_(self.viewport().mapToGlobal(pos))

    def filter_tree(self, query: str):
        """Filters nodes matching query, expanding branches containing matches."""
        query = query.strip().lower()

        def check_item(item: QTreeWidgetItem) -> bool:
            data = item.data(0, Qt.UserRole)
            matches_self = False

            if data:
                kind, obj = data
                if kind == "snippet":
                    searchable = f"{obj.title} {obj.category} {obj.desc} {obj.filename} {obj.code}".lower()
                    if query in searchable:
                        matches_self = True
                elif kind == "collection":
                    if query in obj.name.lower():
                        matches_self = True

            any_child_matches = False
            for i in range(item.childCount()):
                child = item.child(i)
                child_matches = check_item(child)
                if child_matches:
                    any_child_matches = True

            visible = (not query) or matches_self or any_child_matches
            item.setHidden(not visible)
            if query and any_child_matches:
                item.setExpanded(True)

            return visible

        for i in range(self.topLevelItemCount()):
            check_item(self.topLevelItem(i))


class SnippetsWidget(QWidget):
    """
    Main reusable Snippet Collection Widget.
    Embeddable in InsertCodeDialog and in MainWindow side panel.
    """

    insert_requested = pyqtSignal(str, str)  # (code, title)
    new_tab_requested = pyqtSignal(str, str)  # (code, title)

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.current_snippet: Optional[SnippetItem] = None
        self._collections: List[CollectionNode] = []

        self._setup_ui()
        self.reload_tree()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Main splitter (Tree on left, Multi-tab preview on right)
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel: Search + Tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(4)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher (tri, matrice, condition)...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input, 1)

        self.btn_refresh = QPushButton()
        self.btn_refresh.setFixedSize(28, 28)
        self.btn_refresh.setToolTip("Rafraîchir les snippets et collections")
        self.btn_refresh.clicked.connect(self.reload_tree)
        search_layout.addWidget(self.btn_refresh)

        left_layout.addLayout(search_layout)

        self.tree_widget = SnippetTreeWidget(self, is_dark=self.is_dark)
        self.tree_widget.snippet_selected.connect(self._on_snippet_selected)
        self.tree_widget.snippet_double_clicked.connect(self._on_snippet_double_clicked)
        self.tree_widget.snippet_new_tab_requested.connect(lambda snip: self.new_tab_requested.emit(snip.code, snip.filename))
        left_layout.addWidget(self.tree_widget, 1)

        self.lbl_count = QLabel("")
        left_layout.addWidget(self.lbl_count)

        self.splitter.addWidget(left_widget)

        # Right panel: Header card + Tab widget + Bottom buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Header Info Card
        self.header_card = QFrame()
        self.header_card.setFrameShape(QFrame.StyledPanel)
        h_card_layout = QHBoxLayout(self.header_card)
        h_card_layout.setContentsMargins(10, 8, 10, 8)
        h_card_layout.setSpacing(8)

        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)
        self.lbl_title = QLabel("Sélectionnez un snippet dans la collection")
        self.lbl_title.setFont(QFont("SansSerif", 11, QFont.Bold))
        meta_layout.addWidget(self.lbl_title)

        self.lbl_desc = QLabel("Consultez le code, les explications Markdown et les schémas.")
        self.lbl_desc.setFont(QFont("SansSerif", 9))
        self.lbl_desc.setWordWrap(True)
        meta_layout.addWidget(self.lbl_desc)

        self.lbl_badges = QLabel("")
        self.lbl_badges.setFont(QFont("SansSerif", 8))
        meta_layout.addWidget(self.lbl_badges)

        h_card_layout.addLayout(meta_layout, 1)

        right_layout.addWidget(self.header_card)

        # Multi-tab view
        self.tabs = QTabWidget()

        # Tab 1: Code
        self.tab_code = QWidget()
        code_layout = QVBoxLayout(self.tab_code)
        code_layout.setContentsMargins(0, 4, 0, 0)
        self.preview_editor = AlgoCodeEditor(is_dark=self.is_dark)
        self.preview_editor.setReadOnly(True)
        self.preview_editor.set_dark_mode(self.is_dark)
        code_layout.addWidget(self.preview_editor)
        self.tabs.addTab(self.tab_code, "Code")

        # Tab 2: Markdown
        self.md_browser = SnippetMarkdownBrowser(self, is_dark=self.is_dark)
        self.tabs.addTab(self.md_browser, "Documentation (.md)")

        # Tab 3: Companion & associated files (including pictures, diagrams, and data files)
        self.files_viewer = SnippetFilesViewer(self, is_dark=self.is_dark)
        self.files_viewer.insert_content_requested.connect(lambda txt: self.insert_requested.emit(txt, "Contenu fichier"))
        self.tabs.addTab(self.files_viewer, "Fichiers associés")

        # Standalone image viewer instance retained for compatibility
        self.image_viewer = SnippetImageViewer(self, is_dark=self.is_dark)

        right_layout.addWidget(self.tabs, 1)

        # Action bar at bottom of right panel (for side panel use; hidden in dialog to avoid duplication)
        self.bottom_actions_bar = QWidget()
        action_layout = QHBoxLayout(self.bottom_actions_bar)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)

        self.btn_copy = QPushButton("Copier le code")
        self.btn_copy.clicked.connect(self._copy_code)
        action_layout.addWidget(self.btn_copy)

        action_layout.addStretch()

        self.btn_new_tab = QPushButton("Ouvrir dans un nouvel onglet")
        self.btn_new_tab.clicked.connect(self._open_new_tab)
        action_layout.addWidget(self.btn_new_tab)

        self.btn_insert = QPushButton("Insérer dans l'éditeur")
        self.btn_insert.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: #ffffff; font-weight: bold; border: none; padding: 6px 14px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:pressed { background-color: #1e40af; }"
        )
        self.btn_insert.clicked.connect(self._insert_code)
        action_layout.addWidget(self.btn_insert)

        right_layout.addWidget(self.bottom_actions_bar)

        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 35)
        self.splitter.setStretchFactor(1, 65)

        main_layout.addWidget(self.splitter, 1)

        self.set_dark_mode(self.is_dark)

    def set_bottom_actions_visible(self, visible: bool):
        """Allows container dialogs to hide bottom action bar to avoid button duplication."""
        if hasattr(self, "bottom_actions_bar"):
            self.bottom_actions_bar.setVisible(visible)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        icon_color = "#cdd6f4" if is_dark else "#475569"

        self.btn_refresh.setIcon(create_icon("refresh", icon_color, 16))
        self.btn_copy.setIcon(create_icon("copy", icon_color, 16))
        self.btn_new_tab.setIcon(create_icon("new", icon_color, 16))
        self.btn_insert.setIcon(create_icon("step", "#ffffff", 16))

        self.tabs.setTabIcon(0, create_icon("python", "#89b4fa" if is_dark else "#2563eb", 16))
        self.tabs.setTabIcon(1, create_icon("doc", icon_color, 16))
        idx_files = self.tabs.indexOf(self.files_viewer)
        if idx_files != -1:
            self.tabs.setTabIcon(idx_files, create_icon("folder", icon_color, 16))

        self.tree_widget.set_dark_mode(is_dark)
        self.preview_editor.set_dark_mode(is_dark)
        self.md_browser.set_dark_mode(is_dark)
        if hasattr(self, "image_viewer"):
            self.image_viewer.set_dark_mode(is_dark)
        self.files_viewer.set_dark_mode(is_dark)

        bg = "#181825" if is_dark else "#ffffff"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        border = "#313244" if is_dark else "#e2e8f0"
        sub_fg = "#9399b2" if is_dark else "#64748b"

        self.header_card.setStyleSheet(
            f"QFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        self.lbl_title.setStyleSheet(f"color: {fg}; font-weight: bold;")
        self.lbl_desc.setStyleSheet(f"color: {sub_fg};")
        self.lbl_badges.setStyleSheet(f"color: {'#89b4fa' if is_dark else '#2563eb'};")
        self.lbl_count.setStyleSheet(f"color: {sub_fg}; font-size: 11px;")

        self.search_input.setStyleSheet(
            f"QLineEdit {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; padding: 5px 8px; }}"
            f"QLineEdit:focus {{ border: 1px solid {'#89b4fa' if is_dark else '#2563eb'}; }}"
        )

    def zoom_in(self):
        if hasattr(self, 'preview_editor'):
            self.preview_editor.zoom_in()
        if hasattr(self, 'md_browser'):
            self.md_browser.zoom_in()

    def zoom_out(self):
        if hasattr(self, 'preview_editor'):
            self.preview_editor.zoom_out()
        if hasattr(self, 'md_browser'):
            self.md_browser.zoom_out()

    def reset_zoom(self):
        if hasattr(self, 'preview_editor'):
            self.preview_editor.reset_zoom()
        if hasattr(self, 'md_browser'):
            self.md_browser.reset_zoom()

    def reload_tree(self):
        """Scans collections and populates the tree view."""
        self._collections = scan_snippets_tree()
        self.tree_widget.populate(self._collections)

        total_snips = sum(len(c.get_all_snippets()) for c in self._collections)
        self.lbl_count.setText(f"{total_snips} snippet(s) dans {len(self._collections)} collection(s)")

        # Select first snippet if available
        if self.tree_widget.topLevelItemCount() > 0:
            top = self.tree_widget.topLevelItem(0)
            if top.childCount() > 0:
                self.tree_widget.setCurrentItem(top.child(0))
            else:
                idx = self.tabs.indexOf(self.files_viewer)
                if idx != -1:
                    self.tabs.removeTab(idx)
        else:
            idx = self.tabs.indexOf(self.files_viewer)
            if idx != -1:
                self.tabs.removeTab(idx)

    def _on_search_changed(self, text: str):
        self.tree_widget.filter_tree(text)

    def _on_snippet_selected(self, snippet: SnippetItem):
        self.current_snippet = snippet

        # Update Header: 4 lines from md description
        self.lbl_title.setText(f"{snippet.title}  ({snippet.filename} - {snippet.lines_count} lignes)")
        md_desc = snippet.get_first_lines_md(4)
        if md_desc:
            self.lbl_desc.setText(md_desc)
        elif snippet.desc:
            self.lbl_desc.setText(snippet.desc)
        else:
            self.lbl_desc.setText(f"Collection : {snippet.category} | {snippet.filename}")

        badges = [f"Code : {snippet.lines_count} lignes"]
        if snippet.md_file:
            badges.append("Documentation Markdown")
        if snippet.companion_files:
            badges.append(f"{len(snippet.companion_files)} fichier(s) associé(s)")

        self.lbl_badges.setText("  •  ".join(badges))

        # Update Code tab
        self.preview_editor.setPlainText(snippet.code)

        # Update Markdown tab
        md_text = snippet.get_md_content()
        if md_text:
            self.md_browser.set_markdown_content(md_text)
        else:
            self.md_browser.set_markdown_content(
                f"# {snippet.title}\n\n*Aucune documentation Markdown n'est associée à ce snippet.*"
            )

        # Update Files tab (only shown if companion/associated files exist)
        if snippet.companion_files:
            if self.tabs.indexOf(self.files_viewer) == -1:
                self.tabs.addTab(self.files_viewer, "Fichiers associés")
                icon_color = "#cdd6f4" if self.is_dark else "#475569"
                idx = self.tabs.indexOf(self.files_viewer)
                self.tabs.setTabIcon(idx, create_icon("folder", icon_color, 16))
            self.files_viewer.set_files(snippet.companion_files)
        else:
            idx = self.tabs.indexOf(self.files_viewer)
            if idx != -1:
                self.tabs.removeTab(idx)

    def _on_snippet_double_clicked(self, snippet: SnippetItem):
        self.insert_requested.emit(snippet.code, snippet.title)

    def _insert_code(self):
        if self.current_snippet:
            self.insert_requested.emit(self.current_snippet.code, self.current_snippet.title)

    def _open_new_tab(self):
        if self.current_snippet:
            self.new_tab_requested.emit(self.current_snippet.code, self.current_snippet.filename)

    def _copy_code(self):
        if self.current_snippet:
            QApplication.clipboard().setText(self.current_snippet.code)

    def _on_join_file_dialog(self, snippet: Optional[SnippetItem], filter_type: str = "all"):
        if not snippet:
            QMessageBox.information(self, "Information", "Veuillez d'abord sélectionner un snippet dans l'arborescence.")
            return

        filters = "Tous les fichiers (*);;Fichiers Markdown (*.md);;Images (*.png *.jpg *.jpeg *.svg *.bmp *.webp);;Fichiers Données (*.txt *.csv *.json *.dat)"
        if filter_type == "image":
            filters = "Images (*.png *.jpg *.jpeg *.svg *.bmp *.webp);;Tous les fichiers (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Joindre un fichier au snippet « {snippet.title} »", "", filters
        )
        if not file_path:
            return

        try:
            dest_file = join_file_to_snippet(snippet, file_path)
            self.reload_tree()
            # Select snippet
            self._on_snippet_selected(snippet)

            ext = os.path.splitext(dest_file)[1].lower()
            if ext in MD_EXTENSIONS:
                self.tabs.setCurrentWidget(self.md_browser)
            else:
                self.tabs.setCurrentWidget(self.files_viewer)

            QMessageBox.information(
                self, "Fichier joint avec succès",
                f"Le fichier « {os.path.basename(dest_file)} » a été joint à l'extrait « {snippet.title} »."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de joindre le fichier :\n{e}")

    def _on_detach_file(self, file_path: str):
        if not os.path.exists(file_path):
            return
        ans = QMessageBox.question(
            self, "Détacher le fichier",
            f"Voulez-vous détacher et supprimer le fichier joint :\n{os.path.basename(file_path)} ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            try:
                os.remove(file_path)
                if self.current_snippet:
                    self.current_snippet.reload()
                    self._on_snippet_selected(self.current_snippet)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression : {e}")

    def _on_new_snippet_dialog(self, collection_dir: str):
        if not collection_dir or not os.path.isdir(collection_dir):
            if self._collections:
                collection_dir = self._collections[0].folder_path
            else:
                return

        name, ok = QInputDialog.getText(
            self, "Nouveau snippet", "Nom du snippet / de l'algorithme :"
        )
        if not ok or not name.strip():
            return

        try:
            new_snip = create_snippet_bundle(collection_dir, name.strip())
            self.reload_tree()
            self._on_snippet_selected(new_snip)
            QMessageBox.information(
                self, "Snippet créé", f"Le snippet « {name} » a été créé dans la collection."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de créer le snippet :\n{e}")

    def _on_new_collection_dialog(self, parent_dir: str):
        if not parent_dir or not os.path.isdir(parent_dir):
            if self._collections:
                parent_dir = os.path.dirname(self._collections[0].folder_path)
            else:
                return

        col_name, ok = QInputDialog.getText(
            self, "Nouvelle collection", "Nom du dossier de la collection :"
        )
        if not ok or not col_name.strip():
            return

        new_dir = os.path.join(parent_dir, col_name.strip())
        try:
            os.makedirs(new_dir, exist_ok=True)
            self.reload_tree()
            QMessageBox.information(
                self, "Collection créée", f"La collection « {col_name} » a été créée."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de créer le dossier :\n{e}")

    def _on_delete_snippet(self, snippet: SnippetItem):
        ans = QMessageBox.warning(
            self, "Supprimer le snippet",
            f"Êtes-vous sûr de vouloir supprimer définitivement le snippet « {snippet.title} » et ses fichiers joints ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans != QMessageBox.Yes:
            return

        try:
            import shutil
            if snippet.is_bundle and os.path.isdir(snippet.folder_path):
                shutil.rmtree(snippet.folder_path)
            elif os.path.isfile(snippet.code_file):
                os.remove(snippet.code_file)
            self.reload_tree()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression :\n{e}")
