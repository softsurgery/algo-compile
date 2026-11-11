"""
Algorithm Code Editor with Syntax Highlighting, Line Numbers,
Auto-Indentation, and Error/Step Line Highlighting.
"""

import re
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtGui import (
    QColor, QTextFormat, QPainter, QFont, QSyntaxHighlighter,
    QTextCharFormat, QTextCursor
)
from PyQt5.QtCore import Qt, QRect, QSize


DEFAULT_SYNTAX_COLORS_DARK = {
    "keyword": "#89b4fa",
    "control": "#cba6f7",
    "type": "#fab387",
    "builtin": "#94e2d5",
    "operator": "#f38ba8",
    "string": "#a6e3a1",
    "literal": "#a6e3a1",
    "comment": "#6c7086",
}

DEFAULT_SYNTAX_COLORS_LIGHT = {
    "keyword": "#0969da",
    "control": "#8250df",
    "type": "#953800",
    "builtin": "#0550ae",
    "operator": "#cf222e",
    "string": "#0a7029",
    "literal": "#1a7f37",
    "comment": "#6e7781",
}


class AlgoHighlighter(QSyntaxHighlighter):
    """Syntax Highlighter for Algorithmic Code."""

    def __init__(self, parent=None, is_dark=False, custom_colors=None):
        super().__init__(parent)
        self.is_dark = is_dark
        self.custom_colors = custom_colors or {}
        self.highlighting_rules = []
        self._setup_formats()
        self._build_rules()

    def set_custom_colors(self, custom_colors: dict):
        self.custom_colors = custom_colors or {}
        self._setup_formats()
        self._build_rules()
        self.rehighlight()

    def set_dark_mode(self, is_dark: bool, custom_colors: dict = None):
        self.is_dark = is_dark
        if custom_colors is not None:
            self.custom_colors = custom_colors
        self._setup_formats()
        self._build_rules()
        self.rehighlight()

    def _setup_formats(self):
        palette = dict(DEFAULT_SYNTAX_COLORS_DARK if self.is_dark else DEFAULT_SYNTAX_COLORS_LIGHT)
        if self.custom_colors:
            palette.update(self.custom_colors)

        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setFontWeight(QFont.Bold)
        self.fmt_keyword.setForeground(QColor(palette["keyword"]))

        self.fmt_control = QTextCharFormat()
        self.fmt_control.setFontWeight(QFont.Bold)
        self.fmt_control.setForeground(QColor(palette["control"]))

        self.fmt_type = QTextCharFormat()
        self.fmt_type.setFontWeight(QFont.DemiBold)
        self.fmt_type.setForeground(QColor(palette["type"]))

        self.fmt_builtin = QTextCharFormat()
        self.fmt_builtin.setForeground(QColor(palette["builtin"]))

        self.fmt_operator = QTextCharFormat()
        self.fmt_operator.setFontWeight(QFont.Bold)
        self.fmt_operator.setForeground(QColor(palette["operator"]))

        self.fmt_literal = QTextCharFormat()
        self.fmt_literal.setForeground(QColor(palette["literal"]))

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(QColor(palette["string"]))

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setFontItalic(True)
        self.fmt_comment.setForeground(QColor(palette["comment"]))

    def _build_rules(self):
        self.highlighting_rules = []

        # Block & structure keywords
        keywords = [
            r'\bALGORITHME\b', r'\bDEBUT\b', r'\bDÉBUT\b', r'\bFIN\b',
            r'\bFonction\b', r'\bProcédure\b', r'\bProcedure\b', r'\bRetourner\b',
            r'\bTableau\s+de\s+déclaration\s+des\s+objets(?:\s+globaux|\s+locaux)?\b',
            r'\bDéclaration\s+des\s+objets(?:\s+globaux|\s+locaux)?\b',
            r'\bTableau\s+de\s+déclaration\s+des\s+nouveaux\s+types\b',
            r'\bDéclaration\s+des\s+nouveaux\s+types\b',
            r'\bTDOG\b', r'\bTDOL\b', r'\bTDO\b', r'\bTDNT\b'
        ]
        for pattern in keywords:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_keyword)
            self.highlighting_rules.append(rule)

        # Control keywords
        control_keywords = [
            r'\bSi\b', r'\bAlors\b', r'\bSinon\b', r'\bSinon\s*Si\b', r'\bFinSi\b', r'\bFin\s*Si\b',
            r'\bSelon\b', r'\bFin\s*Selon\b', r'\bFinSelon\b',
            r'\bPour\b', r'\bde\b', r'\bà\b', r'\ba\b', r'\bPas\b', r'\bFaire\b', r'\bFin\s*Pour\b', r'\bFinPour\b',
            r'\bTant\s*que\b', r'\bFin\s*Tant\s*que\b', r'\bFinTantQue\b',
            r'\bRépéter\b', r'\bRepeter\b', r'\bJusqu[\'’]à\b', r'\bJusqu[\'’]a\b'
        ]
        for pattern in control_keywords:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_control)
            self.highlighting_rules.append(rule)

        # Types
        types = [
            r'\bEntier\b', r'\bRéel\b', r'\bReel\b', r'\bBooléen\b', r'\bBooleen\b',
            r'\bCaractère\b', r'\bCaractere\b', r'\bChaîne\s+de\s+caractères\b',
            r'\bChaîne\b', r'\bChaine\b', r'\bTableau\b', r'\bEnregistrement\b',
            r'\bFichier\s+Texte\b', r'\bFichier\b'
        ]
        for pattern in types:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_type)
            self.highlighting_rules.append(rule)

        # Predefined functions and I/O
        builtins = [
            r'\bLire\b', r'\bLire_ligne\b', r'\bEcrire\b', r'\bÉcrire\b',
            r'\bEcrire_nl\b', r'\bÉcrire_nl\b',
            r'\bArrondi\b', r'\bRacineCarré\b', r'\bRacineCarre\b', r'\bAléa\b', r'\bAlea\b',
            r'\bEnt\b', r'\bAbs\b', r'\bOrd\b', r'\bChr\b', r'\bLong\b', r'\bPos\b',
            r'\bConvch\b', r'\bEstnum\b', r'\bValeur\b', r'\bSous_chaine\b',
            r'\bEffacer\b', r'\bMajus\b', r'\bOuvrir\b', r'\bFermer\b', r'\bFin_fichier\b'
        ]
        for pattern in builtins:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_builtin)
            self.highlighting_rules.append(rule)

        # Algorithmic Operators
        operators = [
            r'<-', r'←', r'\uf0e7', r'', r':=',
            r'\bDiv\b', r'\bMod\b', r'\bEt\b', r'\bOu\b', r'\bNon\b', r'\bdans\b',
            r'≠', r'<>', r'≤', r'<=', r'≥', r'>=', r'', r'∈'
        ]
        for pattern in operators:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_operator)
            self.highlighting_rules.append(rule)

        # Literals (Vrai, Faux, numbers)
        literals = [
            r'\bVrai\b', r'\bFaux\b',
            r'\b[0-9]+(?:\.[0-9]+)?\b'
        ]
        for pattern in literals:
            rule = (re.compile(pattern, re.IGNORECASE), self.fmt_literal)
            self.highlighting_rules.append(rule)

    def highlightBlock(self, text: str):
        # Apply standard rules
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)

        # Strings ("..." or '...')
        string_pattern = re.compile(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')')
        for match in string_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.fmt_string)

        # Comments (// ... or # ...)
        comment_pattern = re.compile(r'(//.*|#.*)')
        for match in comment_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.fmt_comment)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class AlgoCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.line_number_area = LineNumberArea(self)
        self.highlighter = AlgoHighlighter(self.document(), is_dark=is_dark)

        # Font configuration - Crisp modern monospace
        font = QFont("JetBrains Mono", 11)
        font.setStyleHint(QFont.Monospace)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
            if not font.exactMatch():
                font = QFont("Courier New", 11)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        self.current_error_line = None
        self.current_exec_line = None

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def set_dark_mode(self, is_dark: bool, custom_colors: dict = None):
        self.is_dark = is_dark
        self.highlighter.set_dark_mode(is_dark, custom_colors)
        self.highlight_current_line()
        self.line_number_area.update()

    def apply_settings(self, settings: dict = None, custom_colors: dict = None):
        """Applies font family, size, tab width, line number visibility, and custom colors."""
        if settings:
            family = settings.get("font_family")
            size = settings.get("font_size", 11)
            if family:
                f = QFont(family, size)
                f.setStyleHint(QFont.Monospace)
                self.setFont(f)

            self.tab_size = settings.get("tab_size", 4)
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * self.tab_size)

            self.show_line_numbers = settings.get("show_line_numbers", True)
            self.line_number_area.setVisible(self.show_line_numbers)
            if not self.show_line_numbers:
                self.setViewportMargins(0, 0, 0, 0)
            else:
                self.update_line_number_area_width(0)

            self.highlight_line_enabled = settings.get("highlight_current_line", True)
            self.highlight_current_line()

        if custom_colors is not None:
            self.highlighter.set_custom_colors(custom_colors)

    def line_number_area_width(self):
        digits = 1
        m = max(1, self.blockCount())
        while m >= 10:
            m //= 10
            digits += 1
        space = 15 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly() and getattr(self, "highlight_line_enabled", True):
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#313244") if self.is_dark else QColor("#f1f5f9")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        # Highlight error line if any
        if self.current_error_line is not None:
            err_sel = QTextEdit.ExtraSelection()
            err_color = QColor("#552732") if self.is_dark else QColor("#ffe3e3")
            err_sel.format.setBackground(err_color)
            err_sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            cursor = QTextCursor(self.document().findBlockByNumber(self.current_error_line - 1))
            err_sel.cursor = cursor
            extra_selections.append(err_sel)

        # Highlight step line if any
        if self.current_exec_line is not None:
            exec_sel = QTextEdit.ExtraSelection()
            exec_color = QColor("#1a3328") if self.is_dark else QColor("#d3f9d8")
            exec_sel.format.setBackground(exec_color)
            exec_sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            cursor = QTextCursor(self.document().findBlockByNumber(self.current_exec_line - 1))
            exec_sel.cursor = cursor
            extra_selections.append(exec_sel)

        self.setExtraSelections(extra_selections)

    def set_error_line(self, line_num):
        self.current_error_line = line_num
        self.highlight_current_line()
        if line_num is not None:
            self.goto_line(line_num)

    def set_exec_line(self, line_num):
        self.current_exec_line = line_num
        self.highlight_current_line()
        if line_num is not None:
            self.goto_line(line_num)

    def goto_line(self, line_num):
        block = self.document().findBlockByNumber(line_num - 1)
        if block.isValid():
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)
            self.ensureCursorVisible()

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        bg_color = QColor("#181825") if self.is_dark else QColor("#f8fafc")
        fg_color = QColor("#6c7086") if self.is_dark else QColor("#94a3b8")
        current_line_fg = QColor("#89b4fa") if self.is_dark else QColor("#2563eb")

        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        current_block_num = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                f = QFont(self.font())
                if block_number == current_block_num:
                    painter.setPen(current_line_fg)
                    f.setBold(True)
                else:
                    painter.setPen(fg_color)
                    f.setBold(False)
                painter.setFont(f)

                painter.drawText(
                    0, top, self.line_number_area.width() - 6,
                    self.fontMetrics().height(), Qt.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def toggle_comment(self):
        """Toggles line comment (//) on the current line or across selected lines."""
        cursor = self.textCursor()
        orig_block_no = cursor.blockNumber()
        orig_col = cursor.positionInBlock()
        has_selection = cursor.hasSelection()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()

        cursor.beginEditBlock()

        start_block = self.document().findBlock(start_pos)
        end_block = self.document().findBlock(end_pos)

        # If selection ends at start of next block, don't include that block
        if end_pos > start_pos and end_pos == end_block.position():
            end_block = end_block.previous()

        blocks = []
        curr = start_block
        while curr.isValid():
            blocks.append(curr)
            if curr == end_block:
                break
            curr = curr.next()

        # Check if all non-empty lines are already commented with //
        all_commented = True
        has_content = False
        for b in blocks:
            txt = b.text().strip()
            if txt:
                has_content = True
                if not txt.startswith("//"):
                    all_commented = False
                    break

        delta_col = 0
        if has_content and all_commented:
            # Uncomment lines
            for b in blocks:
                text = b.text()
                m = re.match(r'^(\s*)//\s?(.*)$', text)
                if m:
                    new_text = m.group(1) + m.group(2)
                    removed_len = len(text) - len(new_text)
                    if b.blockNumber() == orig_block_no:
                        delta_col = -removed_len
                    c = QTextCursor(b)
                    c.movePosition(QTextCursor.StartOfBlock)
                    c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                    c.insertText(new_text)
        else:
            # Comment out lines
            for b in blocks:
                text = b.text()
                m = re.match(r'^(\s*)(.*)$', text)
                if m:
                    new_text = f"{m.group(1)}// {m.group(2)}"
                    added_len = len(new_text) - len(text)
                    if b.blockNumber() == orig_block_no:
                        delta_col = added_len
                    c = QTextCursor(b)
                    c.movePosition(QTextCursor.StartOfBlock)
                    c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                    c.insertText(new_text)

        cursor.endEditBlock()

        if not has_selection:
            target_block = self.document().findBlockByNumber(orig_block_no)
            if target_block.isValid():
                new_col = max(0, min(orig_col + delta_col, max(0, target_block.length() - 1)))
                new_cursor = self.textCursor()
                new_cursor.setPosition(target_block.position() + new_col)
                self.setTextCursor(new_cursor)

    def keyPressEvent(self, event):
        """Auto-indent on Enter, Ctrl +/- zoom, and Ctrl+/ toggle comment."""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Slash or event.text() == '/':
                self.toggle_comment()
                event.accept()
                return
            elif event.key() in (Qt.Key_Plus, Qt.Key_Equal) or event.text() in ('+', '='):
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

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            block_text = cursor.block().text()
            
            # Find current indentation
            indent_match = re.match(r'^(\s*)', block_text)
            current_indent = indent_match.group(1) if indent_match else ""

            # Check if block ended with an indent-trigger keyword
            stripped = block_text.strip().lower()
            triggers = ['alors', 'faire', 'debut', 'début', 'selon', 'répéter', 'repeter', 'sinon']
            increase = any(stripped.endswith(t) for t in triggers)

            super().keyPressEvent(event)

            new_indent = current_indent + ("  " if increase else "")
            if new_indent:
                self.insertPlainText(new_indent)
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        """Ctrl + Mouse Wheel zoom feature."""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def zoom_in(self, delta=1):
        cur = self.font().pointSize()
        if cur <= 0:
            cur = 11
        if cur < 36:
            step = min(delta, 36 - cur)
            self.zoomIn(step)
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
            self.update_line_number_area_width(0)
            self.line_number_area.update()

    def zoom_out(self, delta=1):
        cur = self.font().pointSize()
        if cur <= 0:
            cur = 11
        if cur > 6:
            step = min(delta, cur - 6)
            self.zoomOut(step)
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
            self.update_line_number_area_width(0)
            self.line_number_area.update()

    def reset_zoom(self):
        cur = self.font().pointSize()
        if cur <= 0:
            cur = 11
        diff = 11 - cur
        if diff > 0:
            self.zoomIn(diff)
        elif diff < 0:
            self.zoomOut(-diff)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self.update_line_number_area_width(0)
        self.line_number_area.update()
