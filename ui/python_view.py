"""
Generated Python Preview Panel.
Displays the transpiled Python code with syntax highlighting,
line numbers, and copy/export functionality.
"""

import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox, QApplication
)
from PyQt5.QtGui import (
    QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QIcon
)
from PyQt5.QtCore import Qt


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._setup_rules()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        self._setup_rules()
        self.rehighlight()

    def _setup_rules(self):
        self.rules = []
        kw_fmt = QTextCharFormat()
        kw_fmt.setFontWeight(QFont.Bold)
        kw_fmt.setForeground(QColor("#cba6f7" if self.is_dark else "#8250df"))

        fn_fmt = QTextCharFormat()
        fn_fmt.setForeground(QColor("#89b4fa" if self.is_dark else "#0969da"))

        str_fmt = QTextCharFormat()
        str_fmt.setForeground(QColor("#a6e3a1" if self.is_dark else "#0a7029"))

        comment_fmt = QTextCharFormat()
        comment_fmt.setFontItalic(True)
        comment_fmt.setForeground(QColor("#6c7086" if self.is_dark else "#6e7781"))

        keywords = [
            r'\bdef\b', r'\breturn\b', r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bin\b', r'\bwhile\b', r'\bbreak\b', r'\bcontinue\b',
            r'\bimport\b', r'\bfrom\b', r'\bmatch\b', r'\bcase\b', r'\bpass\b',
            r'\bTrue\b', r'\bFalse\b', r'\bNone\b', r'\band\b', r'\bor\b', r'\bnot\b'
        ]
        for kw in keywords:
            self.rules.append((re.compile(kw), kw_fmt))

        builtins = [r'\bprint\b', r'\binput\b', r'\brange\b', r'\blen\b', r'\bint\b', r'\bfloat\b', r'\bstr\b', r'\barray\b']
        for b in builtins:
            self.rules.append((re.compile(b), fn_fmt))

        self.str_fmt = str_fmt
        self.comment_fmt = comment_fmt

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

        # Strings
        for match in re.finditer(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', text):
            self.setFormat(match.start(), match.end() - match.start(), self.str_fmt)

        # Comments
        for match in re.finditer(r'#.*', text):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_fmt)


class PythonView(QWidget):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self._setup_ui()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header toolbar
        header = QHBoxLayout()
        header.setContentsMargins(4, 2, 4, 2)

        title = QLabel("Code Python (Implémentation 2024-2025)")
        title.setFont(QFont("SansSerif", 9, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self.btn_copy = QPushButton("Copier")
        self.btn_copy.setFixedHeight(24)
        self.btn_copy.clicked.connect(self._copy_code)
        header.addWidget(self.btn_copy)

        self.btn_export = QPushButton("Exporter (.py)")
        self.btn_export.setFixedHeight(24)
        self.btn_export.clicked.connect(self._export_file)
        header.addWidget(self.btn_export)

        layout.addLayout(header)

        # Code display
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        font = QFont("JetBrains Mono", 10)
        font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)
        self.highlighter = PythonHighlighter(self.editor.document(), is_dark=self.is_dark)
        layout.addWidget(self.editor, 1)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        self.highlighter.set_dark_mode(is_dark)
        if is_dark:
            self.editor.setStyleSheet("background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px;")
        else:
            self.editor.setStyleSheet("background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 4px;")

    def set_python_code(self, code: str):
        self.editor.setPlainText(code)

    def get_python_code(self) -> str:
        return self.editor.toPlainText()

    def _copy_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editor.toPlainText())
        self.btn_copy.setText("Copié !")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.btn_copy.setText("Copier"))

    def _export_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter en fichier Python", "algorithme.py", "Python (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Exportation réussie", f"Fichier enregistré sous:\n{path}")
