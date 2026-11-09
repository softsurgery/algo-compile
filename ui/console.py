"""
Thonny-style Interactive Shell and Execution Console.
Executes code asynchronously via QProcess with full stdin/stdout support,
colored output, and error navigation.
"""

import sys
import os
import tempfile
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel
)
from PyQt5.QtGui import QColor, QTextCursor, QFont
from PyQt5.QtCore import Qt, QProcess, pyqtSignal


from ui.icons import create_icon


class ConsoleOutputEdit(QTextEdit):
    def __init__(self, console, parent=None):
        super().__init__(parent)
        self.console = console

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.console.zoom_in()
            elif delta < 0:
                self.console.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal) or event.text() in ('+', '='):
                self.console.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key_Minus or event.text() == '-':
                self.console.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key_0 or event.text() == '0':
                self.console.reset_zoom()
                event.accept()
                return
        super().keyPressEvent(event)


class ConsoleInputEdit(QLineEdit):
    def __init__(self, console, parent=None):
        super().__init__(parent)
        self.console = console

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.console.zoom_in()
            elif delta < 0:
                self.console.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal) or event.text() in ('+', '='):
                self.console.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key_Minus or event.text() == '-':
                self.console.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key_0 or event.text() == '0':
                self.console.reset_zoom()
                event.accept()
                return
        super().keyPressEvent(event)


class AlgoConsole(QWidget):
    # Signals
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(int)
    error_line_clicked = pyqtSignal(int)
    variable_state_updated = pyqtSignal(dict)

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.process = None
        self.temp_script_path = None
        self.current_font_size = 10

        self._setup_ui()
        self.set_dark_mode(is_dark)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header bar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)
        
        self.title_label = QLabel("Console / Shell (Python 3)")
        self.title_label.setFont(QFont("SansSerif", 9, QFont.Bold))
        header_layout.addWidget(self.title_label)

        self.status_badge = QLabel(" ● Prêt ")
        self.status_badge.setStyleSheet("color: #2b8a3e; font-weight: bold;")
        header_layout.addWidget(self.status_badge)

        header_layout.addStretch()

        # Zoom buttons in console header
        self.btn_zoom_out = QPushButton()
        self.btn_zoom_out.setIcon(create_icon("zoom_out", "#64748b", 16))
        self.btn_zoom_out.setToolTip("Zoom arrière (Ctrl -)")
        self.btn_zoom_out.setFixedSize(26, 24)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        header_layout.addWidget(self.btn_zoom_out)

        self.btn_zoom_in = QPushButton()
        self.btn_zoom_in.setIcon(create_icon("zoom_in", "#64748b", 16))
        self.btn_zoom_in.setToolTip("Zoom avant (Ctrl +)")
        self.btn_zoom_in.setFixedSize(26, 24)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        header_layout.addWidget(self.btn_zoom_in)

        self.btn_clear = QPushButton("Effacer")
        self.btn_clear.setFixedHeight(24)
        self.btn_clear.clicked.connect(self.clear_console)
        header_layout.addWidget(self.btn_clear)

        self.btn_stop = QPushButton("Arrêter")
        self.btn_stop.setFixedHeight(24)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_execution)
        header_layout.addWidget(self.btn_stop)

        layout.addLayout(header_layout)

        # Output text area
        self.output_text = ConsoleOutputEdit(self)
        self.output_text.setReadOnly(True)
        font = QFont("JetBrains Mono", self.current_font_size)
        font.setStyleHint(QFont.Monospace)
        self.output_text.setFont(font)
        layout.addWidget(self.output_text, 1)

        # Input line (for interactive Lire() / input())
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(4)

        self.prompt_label = QLabel(">>> ")
        self.prompt_label.setFont(font)
        self.prompt_label.setStyleSheet("color: #3182ce; font-weight: bold;")
        input_layout.addWidget(self.prompt_label)

        self.input_line = ConsoleInputEdit(self)
        self.input_line.setFont(font)
        self.input_line.setPlaceholderText("Entrez une valeur pour Lire() et appuyez sur Entrée...")
        self.input_line.returnPressed.connect(self._handle_input_submit)
        input_layout.addWidget(self.input_line, 1)

        self.btn_send = QPushButton("Envoyer")
        self.btn_send.setFixedHeight(26)
        self.btn_send.clicked.connect(self._handle_input_submit)
        input_layout.addWidget(self.btn_send)

        layout.addLayout(input_layout)

        self._print_banner()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        if is_dark:
            self.output_text.setStyleSheet("background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px;")
            self.input_line.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 3px;")
            self.title_label.setStyleSheet("color: #a6adc8;")
        else:
            self.output_text.setStyleSheet("background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 4px;")
            self.input_line.setStyleSheet("background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 4px; padding: 3px;")
            self.title_label.setStyleSheet("color: #475569;")

    def _print_banner(self):
        banner_color = "#3b82f6" if not self.is_dark else "#89b4fa"
        self.output_text.append(
            f"<span style='color: {banner_color}; font-weight: bold;'>"
            f"=== Algoo ===<br>"
            f"Prêt pour la compilation et l'exécution interactive.<br>"
            f"</span><br>"
        )

    def clear_console(self):
        self.output_text.clear()
        self._print_banner()

    def zoom_in(self, delta=1):
        cur = self.output_text.font().pointSize()
        if cur <= 0:
            cur = self.current_font_size
        if cur < 36:
            step = min(delta, 36 - cur)
            self.current_font_size = cur + step
            self.output_text.zoomIn(step)
            f = self.output_text.font()
            self.prompt_label.setFont(f)
            self.input_line.setFont(f)

    def zoom_out(self, delta=1):
        cur = self.output_text.font().pointSize()
        if cur <= 0:
            cur = self.current_font_size
        if cur > 6:
            step = min(delta, cur - 6)
            self.current_font_size = cur - step
            self.output_text.zoomOut(step)
            f = self.output_text.font()
            self.prompt_label.setFont(f)
            self.input_line.setFont(f)

    def reset_zoom(self):
        cur = self.output_text.font().pointSize()
        if cur <= 0:
            cur = self.current_font_size
        diff = 10 - cur
        if diff > 0:
            self.output_text.zoomIn(diff)
        elif diff < 0:
            self.output_text.zoomOut(-diff)
        self.current_font_size = 10
        f = self.output_text.font()
        self.prompt_label.setFont(f)
        self.input_line.setFont(f)

    def run_python_code(self, py_code: str):
        """Executes Python code asynchronously via QProcess."""
        if self.is_running():
            self.stop_execution()

        # Save to temporary file in workspace to allow imports of compiler.runtime
        workspace_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
        # Add variable tracing wrapper if desired
        full_code = py_code

        temp_fd, temp_path = tempfile.mkstemp(suffix=".py", prefix="_algo_exec_", dir=workspace_dir)
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(full_code)

        self.temp_script_path = temp_path

        self.process = QProcess(self)
        self.process.setWorkingDirectory(workspace_dir)

        # Setup environment
        env = self.process.processEnvironment()
        python_path = os.environ.get("PYTHONPATH", "")
        if workspace_dir not in python_path:
            python_path = f"{workspace_dir}:{python_path}" if python_path else workspace_dir
        env.insert("PYTHONPATH", python_path)
        env.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(env)

        self.process.readyReadStandardOutput.connect(self._on_stdout_ready)
        self.process.readyReadStandardError.connect(self._on_stderr_ready)
        self.process.finished.connect(self._on_process_finished)

        start_color = "#10b981" if not self.is_dark else "#a6e3a1"
        self.output_text.append(f"<span style='color: {start_color}; font-weight: bold;'>% Exécution de l'algorithme...</span><br>")
        self.status_badge.setText(" ● En cours d'exécution ")
        self.status_badge.setStyleSheet("color: #d97706; font-weight: bold;")
        self.btn_stop.setEnabled(True)
        self.execution_started.emit()

        # Start python process
        self.process.start(sys.executable, ["-u", temp_path])

    def _on_stdout_ready(self):
        if not self.process:
            return
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        # Format stdout
        text_color = "#1e293b" if not self.is_dark else "#cdd6f4"
        escaped = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.output_text.insertHtml(f"<span style='color: {text_color};'>{escaped}</span>")
        self.output_text.moveCursor(QTextCursor.End)

    def _on_stderr_ready(self):
        if not self.process:
            return
        data = self.process.readAllStandardError().data().decode('utf-8', errors='replace')
        err_color = "#dc2626" if not self.is_dark else "#f38ba8"

        # Check if traceback has line number in our temp file
        m = re.search(r'File ".*?", line (\d+)', data)
        if m:
            err_line = int(m.group(1))
            self.error_line_clicked.emit(err_line)

        escaped = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        self.output_text.insertHtml(f"<span style='color: {err_color}; font-weight: bold;'>{escaped}</span>")
        self.output_text.moveCursor(QTextCursor.End)

    def _on_process_finished(self, exit_code, exit_status):
        self.status_badge.setText(" ● Prêt ")
        self.status_badge.setStyleSheet("color: #2b8a3e; font-weight: bold;")
        self.btn_stop.setEnabled(False)

        info_color = "#64748b" if not self.is_dark else "#9399b2"
        self.output_text.append(f"<br><span style='color: {info_color}; font-style: italic;'>=== Sortie du programme (code {exit_code}) ===</span><br>")
        self.output_text.moveCursor(QTextCursor.End)

        # Clean temp file
        if self.temp_script_path and os.path.exists(self.temp_script_path):
            try:
                os.remove(self.temp_script_path)
            except OSError:
                pass
            self.temp_script_path = None

        self.execution_finished.emit(exit_code)

    def _handle_input_submit(self):
        text = self.input_line.text()
        self.input_line.clear()

        if self.is_running():
            # Echo input in console
            input_color = "#7c3aed" if not self.is_dark else "#cba6f7"
            escaped = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            self.output_text.insertHtml(f"<span style='color: {input_color}; font-weight: bold;'>{escaped}</span><br>")
            self.output_text.moveCursor(QTextCursor.End)

            # Send to process stdin
            bytes_data = (text + "\n").encode('utf-8')
            self.process.write(bytes_data)
        else:
            self.output_text.append(f"<span style='color: #94a3b8;'>Aucun programme en cours d'exécution.</span><br>")

    def stop_execution(self):
        """Immediately terminates the running process."""
        if self.is_running():
            self.process.kill()
            self.process.waitForFinished(1000)
            stop_color = "#ef4444" if not self.is_dark else "#f38ba8"
            self.output_text.append(f"<br><span style='color: {stop_color}; font-weight: bold;'>[Processus arrêté par l'utilisateur]</span><br>")
            self.status_badge.setText(" ● Arrêté ")
            self.status_badge.setStyleSheet("color: #dc2626; font-weight: bold;")
            self.btn_stop.setEnabled(False)

    def is_running(self):
        return self.process is not None and self.process.state() == QProcess.Running
