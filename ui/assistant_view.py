"""
Assistant & Guide View.
Provides contextual error diagnostics and an interactive tree-view reference browser
powered by Markdown documentation from the docs/ directory.
Uses native vector icons (no missing emoji font issues) and high-contrast, theme-aware styling.
"""

import os
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QTreeWidget, QTreeWidgetItem, QLineEdit, QPushButton,
    QLabel, QSplitter, QToolButton
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from ui.icons import create_icon

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

_DEFAULT_DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

FALLBACK_TOPICS = {
    "1. Structure Générale, TDOG & TDOL": """
# Structure Générale d'un Algorithme
```algo
Procedure Exemple(@x: Entier)
DEBUT
  // Traitement local
FIN
Tableau de déclaration des objets locaux
Objet          Type / Nature
/              /

ALGORITHME Nom
DEBUT
  Traitements...
FIN
Tableau de déclaration des objets globaux
Objet          Type / Nature
n, s, i        Entier
T              Tableau de 20 Entier
```
""",
    "2. Opérations Élémentaires": """
# Opérations Élémentaires
| Algorithmique | Python | Description |
|---|---|---|
| `Lire(x)` | `x = input()` | Saisie clavier |
| `Ecrire("msg", x)` | `print("msg", x, end='')` | Affichage sans retour |
| `Ecrire_nl("msg", x)` | `print("msg", x)` | Affichage avec retour |
| `x <- expr` | `x = expr` | Affectation |
"""
}


def _clean_category_name(folder_name: str) -> str:
    """Format a folder name like 01_Structure_et_Declarations into '1. Structure et Déclarations'."""
    m = re.match(r"^(\d+)[_-](.*)$", folder_name)
    if m:
        num, rest = m.groups()
        title = rest.replace("_", " ").strip()
        return f"{int(num)}. {title}"
    return folder_name.replace("_", " ").strip()


def _extract_doc_title(file_path: str) -> str:
    """Extract display title from markdown file (first # header) or file name."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("# "):
                    return s[2:].strip()
    except Exception:
        pass
    base = os.path.splitext(os.path.basename(file_path))[0]
    m = re.match(r"^(\d+)[_-](.*)$", base)
    if m:
        num, rest = m.groups()
        return f"{int(num)}. {rest.replace('_', ' ').strip()}"
    return base.replace("_", " ").strip()


class AssistantView(QWidget):
    """
    Documentation and contextual help browser with a tree-view for all markdown docs.
    """

    def __init__(self, parent=None, is_dark=False, docs_dir=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.docs_dir = docs_dir or _DEFAULT_DOCS_DIR
        self._current_file_path = None
        self._current_content = ""
        self._is_error_view = False
        self._last_selected_doc_path = None

        self._setup_ui()
        self.reload_docs()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # Top Control Bar (Search & Quick Actions)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(4)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Rechercher un sujet ou guide...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self.search_edit, 1)

        self.btn_expand = QToolButton()
        self.btn_expand.setText("+")
        self.btn_expand.setToolTip("Déplier tous les dossiers")
        self.btn_expand.clicked.connect(self._expand_all)
        top_bar.addWidget(self.btn_expand)

        self.btn_collapse = QToolButton()
        self.btn_collapse.setText("−")
        self.btn_collapse.setToolTip("Replier tous les dossiers")
        self.btn_collapse.clicked.connect(self._collapse_all)
        top_bar.addWidget(self.btn_collapse)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setToolTip("Actualiser les documents depuis le dossier docs/")
        self.btn_refresh.clicked.connect(self.reload_docs)
        top_bar.addWidget(self.btn_refresh)

        self.btn_layout_toggle = QToolButton()
        self.btn_layout_toggle.setText("⇋")
        self.btn_layout_toggle.setToolTip("Basculer la disposition (Haut/Bas ↔ Gauche/Droite)")
        self.btn_layout_toggle.clicked.connect(self._toggle_splitter_orientation)
        top_bar.addWidget(self.btn_layout_toggle)

        main_layout.addLayout(top_bar)

        # Splitter containing Tree on one side and Document on other
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)

        # 1. Tree View (Left / Top)
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(2)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(18)
        self.tree.setIconSize(QSize(18, 18))
        self.tree.itemSelectionChanged.connect(self._on_tree_selection_changed)
        self.tree.itemClicked.connect(self._load_item)
        tree_layout.addWidget(self.tree)

        self.splitter.addWidget(tree_container)

        # 2. Document Reader View (Right / Bottom)
        reader_container = QWidget()
        reader_layout = QVBoxLayout(reader_container)
        reader_layout.setContentsMargins(0, 0, 0, 0)
        reader_layout.setSpacing(4)

        # Reader Title Bar
        self.reader_header = QWidget()
        reader_header_layout = QHBoxLayout(self.reader_header)
        reader_header_layout.setContentsMargins(8, 5, 8, 5)
        reader_header_layout.setSpacing(6)

        self.lbl_icon = QLabel()
        reader_header_layout.addWidget(self.lbl_icon)

        self.lbl_title = QLabel("Guide et Documentation")
        self.lbl_title.setFont(QFont("SansSerif", 9, QFont.Bold))
        reader_header_layout.addWidget(self.lbl_title, 1)

        self.btn_back_to_guide = QPushButton("← Retour au guide")
        self.btn_back_to_guide.setVisible(False)
        self.btn_back_to_guide.clicked.connect(self._on_back_to_guide_clicked)
        reader_header_layout.addWidget(self.btn_back_to_guide)

        reader_layout.addWidget(self.reader_header)

        # Document Browser
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        reader_layout.addWidget(self.browser, 1)

        self.splitter.addWidget(reader_container)

        # Proportions: 35% tree, 65% reader
        self.splitter.setStretchFactor(0, 35)
        self.splitter.setStretchFactor(1, 65)

        main_layout.addWidget(self.splitter, 1)

    def _toggle_splitter_orientation(self):
        """Switches splitter between Vertical and Horizontal layout."""
        if self.splitter.orientation() == Qt.Vertical:
            self.splitter.setOrientation(Qt.Horizontal)
            self.splitter.setSizes([180, 320])
        else:
            self.splitter.setOrientation(Qt.Vertical)
            self.splitter.setSizes([160, 340])

    def _expand_all(self):
        self.tree.expandAll()

    def _collapse_all(self):
        self.tree.collapseAll()

    def reload_docs(self):
        """Scans the docs/ folder and populates the tree view."""
        self.tree.clear()

        icon_folder = create_icon("folder", size=18)
        icon_doc = create_icon("doc", size=18)

        if not os.path.isdir(self.docs_dir):
            self._load_fallback_topics()
            return

        entries = sorted(os.listdir(self.docs_dir))
        first_doc_item = None

        has_categories = any(os.path.isdir(os.path.join(self.docs_dir, e)) for e in entries)

        if has_categories:
            for entry in entries:
                cat_path = os.path.join(self.docs_dir, entry)
                if not os.path.isdir(cat_path):
                    continue
                # Category item
                cat_title = _clean_category_name(entry)
                cat_item = QTreeWidgetItem(self.tree)
                cat_item.setText(0, cat_title)
                cat_item.setIcon(0, icon_folder)
                cat_item.setFont(0, QFont("SansSerif", 9, QFont.Bold))
                cat_item.setData(0, Qt.UserRole, None)

                # Sub-files (.md)
                files = sorted(os.listdir(cat_path))
                for f in files:
                    if not f.lower().endswith(".md"):
                        continue
                    file_path = os.path.join(cat_path, f)
                    doc_title = _extract_doc_title(file_path)
                    doc_item = QTreeWidgetItem(cat_item)
                    doc_item.setText(0, doc_title)
                    doc_item.setIcon(0, icon_doc)
                    doc_item.setData(0, Qt.UserRole, file_path)
                    if first_doc_item is None:
                        first_doc_item = doc_item

                cat_item.setExpanded(True)
        else:
            # Flat docs folder
            for f in entries:
                if not f.lower().endswith(".md"):
                    continue
                file_path = os.path.join(self.docs_dir, f)
                doc_title = _extract_doc_title(file_path)
                doc_item = QTreeWidgetItem(self.tree)
                doc_item.setText(0, doc_title)
                doc_item.setIcon(0, icon_doc)
                doc_item.setData(0, Qt.UserRole, file_path)
                if first_doc_item is None:
                    first_doc_item = doc_item

        # Support standalone .md files in root docs/ alongside categories
        for f in entries:
            file_path = os.path.join(self.docs_dir, f)
            if os.path.isfile(file_path) and f.lower().endswith(".md"):
                doc_title = _extract_doc_title(file_path)
                doc_item = QTreeWidgetItem(self.tree)
                doc_item.setText(0, doc_title)
                doc_item.setIcon(0, icon_doc)
                doc_item.setData(0, Qt.UserRole, file_path)
                if first_doc_item is None:
                    first_doc_item = doc_item

        # Select first item by default if available
        if first_doc_item:
            self.tree.setCurrentItem(first_doc_item)
            self._load_item(first_doc_item)
        elif self.tree.topLevelItemCount() == 0:
            self._load_fallback_topics()

    def _load_fallback_topics(self):
        """Loads built-in fallback topics if docs/ directory is missing or empty."""
        first_item = None
        icon_doc = create_icon("doc", size=18)
        for title, md_content in FALLBACK_TOPICS.items():
            item = QTreeWidgetItem(self.tree)
            item.setText(0, title)
            item.setIcon(0, icon_doc)
            item.setData(0, Qt.UserRole, f"virtual:{title}")
            if first_item is None:
                first_item = item
        if first_item:
            self.tree.setCurrentItem(first_item)
            self._load_item(first_item)

    def _on_search_changed(self, text: str):
        """Filters the tree view based on search query."""
        q = text.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            top_item = self.tree.topLevelItem(i)
            top_text = top_item.text(0).lower()
            top_match = q in top_text

            child_matched = False
            for j in range(top_item.childCount()):
                child = top_item.child(j)
                c_text = child.text(0).lower()
                matches = top_match or (q in c_text)
                child.setHidden(not matches if q else False)
                if matches:
                    child_matched = True

            top_item.setHidden(not (top_match or child_matched) if q else False)
            if q and (top_match or child_matched):
                top_item.setExpanded(True)

    def _load_item(self, item: QTreeWidgetItem):
        """Loads and displays the document associated with the tree item."""
        if not item:
            return
        data = item.data(0, Qt.UserRole)
        if not data:
            # It's a category header; toggle its expansion
            item.setExpanded(not item.isExpanded())
            return

        self._is_error_view = False
        self.btn_back_to_guide.setVisible(False)
        clean_title = item.text(0).strip()
        self.lbl_title.setText(clean_title)
        self.lbl_icon.setPixmap(create_icon("doc", size=16).pixmap(16, 16))

        if isinstance(data, str) and data.startswith("virtual:"):
            key = data.split("virtual:", 1)[1]
            content = FALLBACK_TOPICS.get(key, "")
            self._current_file_path = None
            self._current_content = content
            self._render_markdown_content(content)
        elif isinstance(data, str) and os.path.isfile(data):
            self._current_file_path = data
            self._last_selected_doc_path = data
            try:
                with open(data, "r", encoding="utf-8") as f:
                    content = f.read()
                self._current_content = content
                self._render_markdown_content(content)
            except Exception as e:
                self.browser.setHtml(f"<p style='color:red;'>Erreur lors de la lecture du fichier : {e}</p>")

    def _on_tree_selection_changed(self):
        """Handles user clicking or moving selection in the tree."""
        items = self.tree.selectedItems()
        if items:
            self._load_item(items[0])

    def open_doc_by_keyword(self, keyword: str):
        """Finds and selects the first doc matching keyword."""
        low = keyword.lower()
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                data = ch.data(0, Qt.UserRole)
                if data and low in ch.text(0).lower():
                    top.setExpanded(True)
                    self.tree.setCurrentItem(ch)
                    self._load_item(ch)
                    return True
                if data and low in str(data).lower():
                    top.setExpanded(True)
                    self.tree.setCurrentItem(ch)
                    self._load_item(ch)
                    return True
        return False

    def _on_back_to_guide_clicked(self):
        """Restores the last selected doc after an error diagnostic."""
        self._is_error_view = False
        self.btn_back_to_guide.setVisible(False)
        if self._last_selected_doc_path and os.path.isfile(self._last_selected_doc_path):
            self.open_doc_by_path(self._last_selected_doc_path)
        else:
            cur = self.tree.currentItem()
            if cur:
                self._load_item(cur)
            elif self.tree.topLevelItemCount() > 0:
                top = self.tree.topLevelItem(0)
                if top.childCount() > 0:
                    self.tree.setCurrentItem(top.child(0))
                    self._load_item(top.child(0))

    def open_doc_by_path(self, target_path: str):
        """Selects and opens a document given its absolute or relative path."""
        norm_target = os.path.abspath(target_path)
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            top_path = top.data(0, Qt.UserRole)
            if top_path and os.path.abspath(top_path) == norm_target:
                self.tree.setCurrentItem(top)
                self._load_item(top)
                return True
            for j in range(top.childCount()):
                ch = top.child(j)
                p = ch.data(0, Qt.UserRole)
                if p and os.path.abspath(p) == norm_target:
                    top.setExpanded(True)
                    self.tree.setCurrentItem(ch)
                    self._load_item(ch)
                    return True
        return False

    def _render_markdown_content(self, md_text: str):
        """Converts Markdown to styled HTML with high contrast and adapted dark/light themes."""
        if self.is_dark:
            body_fg = "#cdd6f4"
            bold_fg = "#ffffff"
            h1_color = "#89b4fa"
            h2_color = "#cba6f7"
            h3_color = "#89dceb"
            pre_bg = "#181825"
            pre_fg = "#a6e3a1"
            pre_border = "#313244"
            code_bg = "#313244"
            code_fg = "#f9e2af"
            code_border = "#45475a"
            table_border = "#313244"
            th_bg = "#1e1e2e"
            th_fg = "#89b4fa"
            td_bg = "#11111b"
            td_fg = "#cdd6f4"
            quote_bg = "#181825"
            quote_fg = "#bac2de"
            quote_border = "#89b4fa"
            hr_color = "#313244"
            link_color = "#89b4fa"
        else:
            body_fg = "#1e293b"
            bold_fg = "#0f172a"
            h1_color = "#1d4ed8"
            h2_color = "#2563eb"
            h3_color = "#1e40af"
            pre_bg = "#f8fafc"
            pre_fg = "#0f172a"
            pre_border = "#cbd5e1"
            code_bg = "#f1f5f9"
            code_fg = "#b45309"
            code_border = "#e2e8f0"
            table_border = "#cbd5e1"
            th_bg = "#f1f5f9"
            th_fg = "#0f172a"
            td_bg = "#ffffff"
            td_fg = "#334155"
            quote_bg = "#f8fafc"
            quote_fg = "#334155"
            quote_border = "#3b82f6"
            hr_color = "#e2e8f0"
            link_color = "#2563eb"

        if HAS_MARKDOWN:
            html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "nl2br"])
        else:
            html_body = f"<pre>{md_text}</pre>"

        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          body, p, li, td, span, div {{
            color: {body_fg};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
            line-height: 1.55;
            margin: 0;
            padding: 0;
          }}
          p {{
            margin-top: 4px;
            margin-bottom: 8px;
          }}
          b, strong {{
            color: {bold_fg};
            font-weight: 700;
          }}
          h1 {{
            color: {h1_color};
            font-size: 17px;
            font-weight: 700;
            margin-top: 4px;
            margin-bottom: 10px;
            border-bottom: 1px solid {hr_color};
            padding-bottom: 4px;
          }}
          h2 {{
            color: {h2_color};
            font-size: 14px;
            font-weight: 700;
            margin-top: 14px;
            margin-bottom: 6px;
          }}
          h3, h4 {{
            color: {h3_color};
            font-size: 13px;
            font-weight: 600;
            margin-top: 10px;
            margin-bottom: 4px;
          }}
          pre {{
            background-color: {pre_bg};
            color: {pre_fg};
            border: 1px solid {pre_border};
            border-radius: 6px;
            padding: 10px;
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
            font-size: 12px;
            line-height: 1.45;
            margin-top: 6px;
            margin-bottom: 10px;
            overflow-x: auto;
          }}
          pre code {{
            color: {pre_fg};
            background-color: transparent;
            border: none;
            padding: 0;
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
          }}
          code {{
            background-color: {code_bg};
            color: {code_fg};
            border: 1px solid {code_border};
            border-radius: 3px;
            padding: 2px 5px;
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
            font-size: 12px;
          }}
          table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 8px;
            margin-bottom: 12px;
            font-size: 12px;
          }}
          th {{
            background-color: {th_bg};
            color: {th_fg};
            border: 1px solid {table_border};
            padding: 7px 9px;
            font-weight: 700;
            text-align: left;
          }}
          td {{
            background-color: {td_bg};
            color: {td_fg};
            border: 1px solid {table_border};
            padding: 6px 9px;
            text-align: left;
          }}
          ul, ol {{
            margin-top: 4px;
            margin-bottom: 8px;
            padding-left: 20px;
          }}
          li {{
            margin-bottom: 3px;
            color: {body_fg};
          }}
          blockquote {{
            border-left: 4px solid {quote_border};
            background-color: {quote_bg};
            color: {quote_fg};
            padding: 8px 12px;
            margin: 8px 0;
            border-radius: 0 4px 4px 0;
          }}
          hr {{
            border: 0;
            height: 1px;
            background-color: {hr_color};
            margin: 12px 0;
          }}
          a {{
            color: {link_color};
            text-decoration: none;
          }}
          a:hover {{
            text-decoration: underline;
          }}
        </style>
        </head>
        <body style="padding: 6px;">
          {html_body}
        </body>
        </html>
        """
        self.browser.setHtml(styled_html)

    def set_dark_mode(self, is_dark: bool):
        """Applies theme to tree, browser, inputs and re-renders current document."""
        self.is_dark = is_dark
        bg = "#11111b" if is_dark else "#ffffff"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        border = "#313244" if is_dark else "#e2e8f0"
        header_bg = "#181825" if is_dark else "#f8fafc"
        input_bg = "#181825" if is_dark else "#ffffff"
        btn_fg = "#cdd6f4" if is_dark else "#475569"

        # Update QPalette on QTextBrowser so default fallback text is always themed
        pal = self.browser.palette()
        pal.setColor(QPalette.Base, QColor(bg))
        pal.setColor(QPalette.Text, QColor(fg))
        self.browser.setPalette(pal)

        # Search edit
        self.search_edit.setStyleSheet(
            f"QLineEdit {{ background-color: {input_bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: 4px; padding: 4px 8px; }}"
        )

        # Quick action tool buttons
        btn_style = (
            f"QToolButton {{ background-color: {header_bg}; color: {btn_fg}; border: 1px solid {border}; "
            f"border-radius: 4px; padding: 3px 6px; font-weight: bold; font-size: 13px; }} "
            f"QToolButton:hover {{ background-color: {'#313244' if is_dark else '#e2e8f0'}; }}"
        )
        self.btn_expand.setStyleSheet(btn_style)
        self.btn_collapse.setStyleSheet(btn_style)
        self.btn_refresh.setStyleSheet(btn_style)
        self.btn_layout_toggle.setStyleSheet(btn_style)

        # Set refresh button vector icon
        self.btn_refresh.setIcon(create_icon("refresh", color_hex=btn_fg, size=15))

        # Tree widget
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: 4px; padding: 4px; }}"
            f"QTreeWidget::item {{ padding: 3px 4px; border-radius: 3px; }}"
            f"QTreeWidget::item:hover {{ background-color: {'#313244' if is_dark else '#f1f5f9'}; }}"
            f"QTreeWidget::item:selected {{ background-color: {'#45475a' if is_dark else '#e2e8f0'}; "
            f"color: {'#ffffff' if is_dark else '#0f172a'}; }}"
        )

        # Reader title bar
        self.reader_header.setStyleSheet(
            f"QWidget {{ background-color: {header_bg}; border: 1px solid {border}; border-radius: 4px; }}"
        )
        self.lbl_title.setStyleSheet(f"QLabel {{ color: {'#89b4fa' if is_dark else '#1d4ed8'}; font-weight: bold; }}")

        # Update header icon
        self.lbl_icon.setPixmap(create_icon("doc", size=16).pixmap(16, 16))

        # Browser
        self.browser.setStyleSheet(
            f"QTextBrowser {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: 4px; padding: 8px; }}"
        )

        # Re-render content if currently displayed
        if not self._is_error_view and self._current_content:
            self._render_markdown_content(self._current_content)

    def show_error_advice(self, error_message: str, line_no: int = None):
        """Displays helpful advice and quick links when a compilation or runtime error occurs."""
        self._is_error_view = True
        self.btn_back_to_guide.setVisible(True)

        title_text = f"Diagnostic & Aide {'(Ligne ' + str(line_no) + ')' if line_no else ''}"
        self.lbl_title.setText(title_text)
        self.lbl_icon.setPixmap(create_icon("help", size=16).pixmap(16, 16))

        err_color = "#f38ba8" if self.is_dark else "#dc2626"
        bg_pre = "#181825" if self.is_dark else "#fef2f2"
        border_err = "#ef4444" if self.is_dark else "#fca5a5"
        text_color = "#cdd6f4" if self.is_dark else "#1e293b"
        accent_color = "#89b4fa" if self.is_dark else "#2563eb"
        code_color = "#f9e2af" if self.is_dark else "#b45309"

        tips = []
        doc_recommendations = []
        low = error_message.lower()

        if "indent" in low:
            tips.append("Vérifiez l'indentation de vos blocs d'instructions (après <code>DEBUT</code>, <code>Alors</code>, <code>Faire</code>).")
            doc_recommendations.append(("Forme Générale", "01_Forme_Generale.md"))
        if "tdol" in low or "objets locaux" in low:
            tips.append("Chaque sous-programme doit être suivi de son <b>Tableau de déclaration des objets locaux (TDOL)</b> placé immédiatement après son <code>FIN</code>.")
            doc_recommendations.append(("Guide TDOL", "03_Tableau_Objets_Locaux_TDOL.md"))
        if "tdog" in low or "objets globaux" in low:
            tips.append("L'algorithme principal doit obligatoirement posséder son <b>Tableau de déclaration des objets globaux (TDOG)</b> placé sous son <code>FIN</code>.")
            doc_recommendations.append(("Guide TDOG", "02_Tableau_Objets_Globaux_TDOG.md"))
        if "nameerror" in low or "not defined" in low or "non déclaré" in low:
            tips.append("Assurez-vous que l'objet est bien déclaré dans la table correspondante (<b>TDOL</b> pour les sous-programmes ou <b>TDOG</b> pour l'algorithme) avec son type.")
            doc_recommendations.append(("Guide TDOG", "02_Tableau_Objets_Globaux_TDOG.md"))
            doc_recommendations.append(("Types Standards", "01_Types_Standards.md"))
        if "type manquant" in low or "type obligatoire" in low or "types sont obligatoires" in low:
            tips.append("Tous les objets, paramètres et fonctions doivent obligatoirement posséder un type défini (ex: <code>x : Entier</code>, <code>f(a: Entier) : Booléen</code>).")
            doc_recommendations.append(("Types Standards", "01_Types_Standards.md"))
        if "fin" in low and "manquant" in low:
            tips.append("Vérifiez que votre algorithme principal et tous vos sous-programmes se terminent par le mot-clé obligatoire <b>FIN</b>.")
            tips.append("Vérifiez également que chaque structure ouverte (<code>Si</code>, <code>Pour</code>, <code>Tant que</code>, <code>Selon</code>, <code>Répéter</code>) est bien fermée.")
            doc_recommendations.append(("Forme Générale", "01_Forme_Generale.md"))
        if "syntaxerror" in low:
            tips.append("Vérifiez la concordance des mots clés (ex: <code>Si ... FinSi</code>, <code>Pour ... Fin Pour</code>).")
            tips.append("Vérifiez que le symbole d'affectation est bien <code>&larr;</code> ou <code>&lt;-</code>.")
            doc_recommendations.append(("Opérations Élémentaires", "02_Operations_Elementaires.md"))
        if "fichier" in low or "ouvrir" in low:
            tips.append("Pour ouvrir un fichier selon les conventions, utilisez : <code>Ouvrir(\"chemin\", Nom_logique, \"mode\")</code>.")
            tips.append("Assurez-vous que le nom logique est déclaré dans le TDOG/TDOL avec le type <code>Fichier Texte</code> ou <code>Fichier de &lt;Type&gt;</code>.")
            tips.append("N'oubliez pas de fermer le fichier avec <code>Fermer(Nom_logique)</code>.")
            doc_recommendations.append(("Guide des Fichiers", "04_Fichiers.md"))
        if not tips:
            tips.append("Consultez l'arbre des fiches de référence pour la syntaxe exacte de l'instruction concernée.")
            doc_recommendations.append(("Guide des Erreurs", "01_Resolution_Erreurs.md"))

        tips_html = "".join(f"<li style='margin-bottom:6px; color:{text_color};'>{t}</li>" for t in tips)

        rec_html = ""
        if doc_recommendations:
            rec_items = []
            for name, filename in doc_recommendations:
                rec_items.append(f"<li style='color:{text_color};'><b>{name}</b> (accessible dans l'arbre de gauche)</li>")
            rec_html = f"<h4 style='color:{accent_color}; margin-top:12px; margin-bottom:6px;'>Sujets recommandés à consulter :</h4><ul style='padding-left:20px;'>{''.join(rec_items)}</ul>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: {text_color}; font-size: 13px; line-height: 1.5; padding: 4px;">
          <h3 style="color: {err_color}; margin-top: 4px; font-size: 15px;">Erreur détectée {"à la ligne " + str(line_no) if line_no else ""}</h3>
          <pre style="background: {bg_pre}; color: {err_color}; border: 1px solid {border_err}; padding: 8px; border-radius: 4px; font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; line-height: 1.45;">{error_message}</pre>
          <h4 style="color: {accent_color}; margin-top: 10px; margin-bottom: 6px;">Conseils de l'assistant :</h4>
          <ul style="padding-left: 20px;">{tips_html}</ul>
          {rec_html}
          <p style="margin-top: 14px; font-style: italic; color: {'#a6adc8' if self.is_dark else '#64748b'};">
            Astuce : Cliquez sur le bouton « Retour au guide » ci-dessus ou sélectionnez n'importe quel sujet dans l'arbre pour revenir à la documentation.
          </p>
        </body>
        </html>
        """
        self.browser.setHtml(html)
