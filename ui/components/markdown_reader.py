"""
Reusable MarkdownReader (QTextBrowser) component with declarative props,
theme-aware styling, fenced code syntax highlighting, and Ctrl+Wheel / Ctrl+/- zoom.
"""

import html
import re
from typing import Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QTextBrowser, QWidget

from ui.components._theme import resolve_is_dark

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def highlight_algo_syntax(code_text: str, is_dark: bool) -> str:
    """Highlights Algorithmic code with high-contrast, theme-adapted colors."""
    if is_dark:
        c_kw = "#89b4fa"      # blue (structure keywords)
        c_ctrl = "#cba6f7"    # mauve/purple (control keywords)
        c_type = "#fab387"    # peach/orange (types)
        c_builtin = "#94e2d5" # teal (builtins and I/O)
        c_op = "#f38ba8"      # red/pink (operators)
        c_num = "#fab387"     # peach (numbers)
        c_str = "#a6e3a1"     # green (strings)
        c_com = "#6c7086"     # grey (comments)
        c_bool = "#fab387"    # peach (booleans)
        c_ident = "#cdd6f4"   # light text
    else:
        c_kw = "#0969da"      # dark blue
        c_ctrl = "#8250df"    # purple
        c_type = "#953800"    # brown/rust
        c_builtin = "#0550ae" # navy
        c_op = "#cf222e"      # red
        c_num = "#0969da"     # blue
        c_str = "#0a7029"     # dark green
        c_com = "#6e7781"     # grey
        c_bool = "#1a7f37"    # green
        c_ident = "#0f172a"   # dark text

    tokens = [
        ("COMMENT", r"#.*"),
        ("STRING", r"\"(?:[^\"\\]|\\.)*\"|\x27(?:[^\x27\\]|\\.)*\x27"),
        ("OPERATOR", r"<-|←|:=|≠|<>|<=|>=|≤|≥|∈||\b(?:Div|Mod|Et|Ou|Non|dans)\b"),
        ("KW_STRUCT", r"\b(?:ALGORITHME|DEBUT|DÉBUT|FIN|Fonction|Procédure|Procedure|Retourner|Tableau\s+de\s+déclaration\s+des\s+objets(?:\s+globaux|\s+locaux)?|Tableau\s+de\s+déclaration\s+des\s+nouveaux\s+types|Déclaration\s+des\s+objets(?:\s+globaux|\s+locaux)?|Déclaration\s+des\s+nouveaux\s+types|TDOG|TDOL|TDNT|TDO|Fin\s+Enregistrement|Enregistrement)\b"),
        ("KW_CTRL", r"\b(?:Si|Alors|Sinon|Fin\s*Si|FinSi|Selon|Fin\s*Selon|FinSelon|Pour|de|à|a|Pas|Faire|Fin\s*Pour|FinPour|Tant\s*que|Fin\s*Tant\s*que|FinTantQue|Répéter|Repeter|Jusqu[\x27’]à|Jusqu[\x27’]a)\b"),
        ("TYPE", r"\b(?:Entier|Réel|Reel|Booléen|Booleen|Caractère|Caractere|Chaîne(?:\s+de\s+caractères)?|Chaine(?:\s+de\s+caractères)?|Tableau(?:\s+de)?|Fichier\s+Texte|Fichier\s+de|Fichier)\b"),
        ("BUILTIN", r"\b(?:Lire_ligne|Lire|Écrire_nl|Ecrire_nl|Écrire|Ecrire|Ouvrir|Fermer|Fin_fichier|Arrondi|RacineCarré|RacineCarre|Aléa|Alea|Ent|Abs|Ord|Chr|Long|Pos|Convch|Estnum|Valeur|Sous_chaine|Effacer|Majus)\b"),
        ("BOOL", r"\b(?:Vrai|Faux|True|False)\b"),
        ("NUM", r"\b\d+(?:\.\d+)?\b"),
        ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
        ("OTHER", r"[^\s\w]"),
    ]

    regex = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in tokens), re.IGNORECASE)

    out = []
    last_end = 0
    for m in regex.finditer(code_text):
        start, end = m.span()
        if start > last_end:
            out.append(f'<span style="color:{c_ident};">{html.escape(code_text[last_end:start])}</span>')
        last_end = end
        kind = m.lastgroup
        text = html.escape(m.group())

        if kind == "COMMENT":
            out.append(f'<span style="color:{c_com}; font-style:italic;">{text}</span>')
        elif kind == "STRING":
            out.append(f'<span style="color:{c_str}; font-weight:500;">{text}</span>')
        elif kind == "OPERATOR":
            out.append(f'<span style="color:{c_op}; font-weight:bold;">{text}</span>')
        elif kind == "KW_STRUCT":
            out.append(f'<span style="color:{c_kw}; font-weight:bold;">{text}</span>')
        elif kind == "KW_CTRL":
            out.append(f'<span style="color:{c_ctrl}; font-weight:bold;">{text}</span>')
        elif kind == "TYPE":
            out.append(f'<span style="color:{c_type}; font-weight:bold;">{text}</span>')
        elif kind == "BUILTIN":
            out.append(f'<span style="color:{c_builtin}; font-weight:bold;">{text}</span>')
        elif kind == "BOOL":
            out.append(f'<span style="color:{c_bool}; font-weight:bold;">{text}</span>')
        elif kind == "NUM":
            out.append(f'<span style="color:{c_num};">{text}</span>')
        else:
            out.append(f'<span style="color:{c_ident};">{text}</span>')

    if last_end < len(code_text):
        out.append(f'<span style="color:{c_ident};">{html.escape(code_text[last_end:])}</span>')

    return "".join(out)


def highlight_python_syntax(code_text: str, is_dark: bool) -> str:
    """Highlights Python code with high-contrast, theme-adapted colors."""
    if is_dark:
        c_kw = "#cba6f7"
        c_builtin = "#89b4fa"
        c_str = "#a6e3a1"
        c_com = "#6c7086"
        c_num = "#fab387"
        c_bool = "#fab387"
        c_op = "#f38ba8"
        c_ident = "#cdd6f4"
    else:
        c_kw = "#8250df"
        c_builtin = "#0969da"
        c_str = "#0a7029"
        c_com = "#6e7781"
        c_num = "#0969da"
        c_bool = "#1a7f37"
        c_op = "#cf222e"
        c_ident = "#0f172a"

    tokens = [
        ("COMMENT", r"#.*"),
        ("STRING", r"\"\"\"[\s\S]*?\"\"\"|\x27\x27\x27[\s\S]*?\x27\x27\x27|\"(?:[^\"\\]|\\.)*\"|\x27(?:[^\x27\\]|\\.)*\x27"),
        ("KEYWORD", r"\b(?:def|class|return|if|elif|else|for|while|in|break|continue|import|from|as|try|except|finally|with|pass|lambda|yield|raise|global|nonlocal|and|or|not|is|match|case)\b"),
        ("BUILTIN", r"\b(?:print|input|len|range|open|close|read|readline|write|int|float|str|list|dict|set|tuple|bool|min|max|sum|abs|round|enumerate|zip|isinstance|load|dump|array)\b"),
        ("BOOL", r"\b(?:True|False|None)\b"),
        ("NUM", r"\b\d+(?:\.\d+)?\b"),
        ("OPERATOR", r"==|!=|<=|>=|[+\-*/%=<>]"),
        ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
        ("OTHER", r"[^\s\w]"),
    ]
    regex = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in tokens))

    out = []
    last_end = 0
    for m in regex.finditer(code_text):
        start, end = m.span()
        if start > last_end:
            out.append(f'<span style="color:{c_ident};">{html.escape(code_text[last_end:start])}</span>')
        last_end = end
        kind = m.lastgroup
        text = html.escape(m.group())

        if kind == "COMMENT":
            out.append(f'<span style="color:{c_com}; font-style:italic;">{text}</span>')
        elif kind == "STRING":
            out.append(f'<span style="color:{c_str}; font-weight:500;">{text}</span>')
        elif kind == "KEYWORD":
            out.append(f'<span style="color:{c_kw}; font-weight:bold;">{text}</span>')
        elif kind == "BUILTIN":
            out.append(f'<span style="color:{c_builtin}; font-weight:bold;">{text}</span>')
        elif kind == "BOOL":
            out.append(f'<span style="color:{c_bool}; font-weight:bold;">{text}</span>')
        elif kind == "NUM":
            out.append(f'<span style="color:{c_num};">{text}</span>')
        elif kind == "OPERATOR":
            out.append(f'<span style="color:{c_op}; font-weight:bold;">{text}</span>')
        else:
            out.append(f'<span style="color:{c_ident};">{text}</span>')

    if last_end < len(code_text):
        out.append(f'<span style="color:{c_ident};">{html.escape(code_text[last_end:])}</span>')

    return "".join(out)


class AppMarkdownReader(QTextBrowser):
    """Themed, prop-driven QTextBrowser for rendering Markdown with syntax highlighting and zoom."""

    _FENCE_PATTERN = re.compile(
        r'^[ \t]*(?:```|~~~)([a-zA-Z0-9_\-]*)[ \t]*\r?\n(.*?)\r?\n[ \t]*(?:```|~~~)[ \t]*$',
        re.DOTALL | re.MULTILINE,
    )

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        is_dark: Optional[bool] = None,
        zoom_level: int = 0,
        min_zoom: int = -4,
        max_zoom: int = 15,
        border_radius: int = 6,
        padding: int = 10,
        open_external_links: bool = True,
        on_zoom_changed: Optional[Callable[[int], None]] = None,
        object_name: Optional[str] = None,
    ):
        super().__init__(parent)
        self._is_dark = is_dark
        self.is_dark = resolve_is_dark(self, is_dark)
        self.zoom_level = zoom_level
        self._min_zoom = min_zoom
        self._max_zoom = max_zoom
        self._border_radius = border_radius
        self._padding = padding
        self._current_md = ""
        self._on_zoom_changed = on_zoom_changed

        self.setOpenExternalLinks(open_external_links)
        if object_name is not None:
            self.setObjectName(object_name)
        self._apply_style()

    def set_dark_mode(self, is_dark: bool) -> None:
        """Sets explicit light or dark mode, updates styling, and re-renders current markdown."""
        self._is_dark = is_dark
        self.is_dark = is_dark
        self._apply_style()
        if self._current_md:
            self._re_render_preserving_scroll()

    def zoom_in(self, delta: int = 1) -> None:
        """Increases zoom level up to max_zoom and re-renders preserving scroll."""
        new_level = min(self._max_zoom, self.zoom_level + delta)
        if new_level != self.zoom_level:
            self.zoom_level = new_level
            self._re_render_preserving_scroll()
            if self._on_zoom_changed is not None:
                self._on_zoom_changed(self.zoom_level)

    def zoom_out(self, delta: int = 1) -> None:
        """Decreases zoom level down to min_zoom and re-renders preserving scroll."""
        new_level = max(self._min_zoom, self.zoom_level - delta)
        if new_level != self.zoom_level:
            self.zoom_level = new_level
            self._re_render_preserving_scroll()
            if self._on_zoom_changed is not None:
                self._on_zoom_changed(self.zoom_level)

    def reset_zoom(self) -> None:
        """Resets zoom level to 0 and re-renders preserving scroll."""
        if self.zoom_level != 0:
            self.zoom_level = 0
            self._re_render_preserving_scroll()
            if self._on_zoom_changed is not None:
                self._on_zoom_changed(self.zoom_level)

    def _re_render_preserving_scroll(self) -> None:
        vbar = self.verticalScrollBar()
        scroll_pos = vbar.value() if vbar else 0
        if self._current_md:
            self.set_markdown_content(self._current_md)
        if vbar:
            vbar.setValue(min(scroll_pos, vbar.maximum()))

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.modifiers() & Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal) or event.text() in ("+", "="):
                self.zoom_in()
                event.accept()
                return
            if event.key() == Qt.Key_Minus or event.text() == "-":
                self.zoom_out()
                event.accept()
                return
            if event.key() == Qt.Key_0 or event.text() == "0":
                self.reset_zoom()
                event.accept()
                return
        super().keyPressEvent(event)

    def _apply_style(self) -> None:
        is_dark = resolve_is_dark(self, self._is_dark)
        self.is_dark = is_dark
        bg = "#11111b" if is_dark else "#ffffff"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        border = "#313244" if is_dark else "#e2e8f0"

        pal = self.palette()
        pal.setColor(QPalette.Base, QColor(bg))
        pal.setColor(QPalette.Text, QColor(fg))
        self.setPalette(pal)

        self.setStyleSheet(
            f"QTextBrowser {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; "
            f"border-radius: {self._border_radius}px; padding: {self._padding}px; }}"
        )

    def _highlight_fenced_code_blocks(self, md_text: str, pre_font_size: int, is_dark: bool) -> str:
        c_default = "#cdd6f4" if is_dark else "#0f172a"

        def replacer(m):
            lang = (m.group(1) or "").strip().lower()
            code_content = m.group(2)
            if lang in ("algo", "algorithme", "alg"):
                highlighted = highlight_algo_syntax(code_content, is_dark)
            elif lang in ("python", "py"):
                highlighted = highlight_python_syntax(code_content, is_dark)
            else:
                highlighted = f'<span style="color:{c_default};">{html.escape(code_content)}</span>'
            return (
                f'\n\n<pre class="code-block language-{lang}" '
                f'style="font-size: {pre_font_size}px; color: {c_default};">'
                f'<code style="font-size: {pre_font_size}px; color: {c_default};">'
                f'{highlighted}</code></pre>\n\n'
            )

        return self._FENCE_PATTERN.sub(replacer, md_text)

    def set_markdown_content(self, md_text: str) -> None:
        """Converts Markdown to themed HTML with syntax-highlighted code blocks and displays it."""
        self._current_md = md_text
        if not md_text.strip():
            self.setHtml("")
            return

        is_dark = resolve_is_dark(self, self._is_dark)
        self.is_dark = is_dark

        base_font_size = max(9, min(36, 13 + self.zoom_level))
        pre_font_size = max(8, min(34, 12 + self.zoom_level))
        code_font_size = max(8, min(34, 11 + self.zoom_level))
        h1_font_size = max(13, min(42, 17 + self.zoom_level))
        h2_font_size = max(11, min(38, 15 + self.zoom_level))
        h3_font_size = max(10, min(36, 14 + self.zoom_level))
        table_font_size = max(8, min(34, 12 + self.zoom_level))

        default_font = self.font()
        default_font.setPointSize(max(7, 10 + self.zoom_level))
        self.document().setDefaultFont(default_font)

        if is_dark:
            body_fg = "#cdd6f4"
            bold_fg = "#ffffff"
            h1_color = "#89b4fa"
            h2_color = "#cba6f7"
            h3_color = "#89dceb"
            pre_bg = "#181825"
            pre_fg = "#cdd6f4"
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

        processed_md = self._highlight_fenced_code_blocks(md_text, pre_font_size, is_dark)

        if HAS_MARKDOWN:
            html_body = markdown.markdown(processed_md, extensions=["tables", "fenced_code", "nl2br"])
        else:
            html_body = f"<pre class='code-block' style='font-size:{pre_font_size}px;'>{html.escape(processed_md)}</pre>"

        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
          body, p, li, td, div {{
            color: {body_fg};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: {base_font_size}px;
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
            font-size: {h1_font_size}px;
            font-weight: 700;
            margin-top: 4px;
            margin-bottom: 10px;
            border-bottom: 1px solid {hr_color};
            padding-bottom: 4px;
          }}
          h2 {{
            color: {h2_color};
            font-size: {h2_font_size}px;
            font-weight: 700;
            margin-top: 14px;
            margin-bottom: 6px;
          }}
          h3, h4 {{
            color: {h3_color};
            font-size: {h3_font_size}px;
            font-weight: 600;
            margin-top: 10px;
            margin-bottom: 4px;
          }}
          pre, pre code, pre span {{
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
            font-size: {pre_font_size}px;
          }}
          pre, pre.code-block {{
            background-color: {pre_bg};
            color: {pre_fg};
            border: 1px solid {pre_border};
            border-radius: 6px;
            padding: 10px 12px;
            line-height: 1.48;
            margin-top: 6px;
            margin-bottom: 12px;
            overflow-x: auto;
          }}
          pre code {{
            color: inherit;
            background-color: transparent;
            border: none;
            padding: 0;
          }}
          code {{
            background-color: {code_bg};
            color: {code_fg};
            border: 1px solid {code_border};
            border-radius: 3px;
            padding: 2px 5px;
            font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
            font-size: {code_font_size}px;
          }}
          table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 8px;
            margin-bottom: 12px;
            font-size: {table_font_size}px;
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
        self.setHtml(styled_html)
