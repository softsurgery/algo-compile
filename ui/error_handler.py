"""
Centralized error handling for Algoo IDE.
Routes all errors and unhandled exceptions to stderr and the in-app AlgoConsole
instead of displaying QMessageBox or independent error popups.
"""

import sys
import threading
import traceback
from typing import Optional

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication


_registered_console = None
_dispatcher = None


class _ErrorDispatcher(QObject):
    """Thread-safe bridge to deliver error messages to AlgoConsole on the GUI thread."""

    error_logged = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_logged.connect(self._on_error_logged, Qt.QueuedConnection)

    def _on_error_logged(self, message: str, traceback_text: str):
        console = _find_console()
        if console is not None and hasattr(console, "log_error"):
            console.log_error(message, traceback_text or None)


def register_console(console) -> None:
    """Registers the primary AlgoConsole instance for error routing."""
    global _registered_console
    _registered_console = console
    _ensure_dispatcher()


def _ensure_dispatcher() -> Optional[_ErrorDispatcher]:
    global _dispatcher
    app = QApplication.instance()
    if app is None:
        return None
    if _dispatcher is None:
        _dispatcher = _ErrorDispatcher(app)
    return _dispatcher


def _find_console(parent=None):
    """Finds an active AlgoConsole instance from parent, registry, or top-level widgets."""
    if parent is not None:
        if hasattr(parent, "log_error"):
            return parent
        if hasattr(parent, "console") and hasattr(parent.console, "log_error"):
            return parent.console
        win = parent.window() if hasattr(parent, "window") else None
        if win is not None and hasattr(win, "console") and hasattr(win.console, "log_error"):
            return win.console

    if _registered_console is not None:
        try:
            # Verify Qt C++ object is still alive
            _registered_console.isVisible()
            return _registered_console
        except RuntimeError:
            pass

    app = QApplication.instance()
    if app is not None:
        for widget in app.topLevelWidgets():
            if hasattr(widget, "console") and hasattr(widget.console, "log_error"):
                return widget.console
    return None


def report_error(
    title: str,
    message: str,
    traceback_text: Optional[str] = None,
    parent=None,
) -> None:
    """Logs an error to stderr and to the in-app AlgoConsole without any popup."""
    full_message = f"{title} : {message}" if title else str(message)
    try:
        sys.stderr.write(f"[ERROR] {full_message}\n")
        if traceback_text:
            sys.stderr.write(f"{traceback_text.rstrip()}\n")
        sys.stderr.flush()
    except Exception:
        pass

    try:
        app = QApplication.instance()
        if app is None:
            return

        console = _find_console(parent)
        on_gui_thread = QThread.currentThread() == app.thread()

        if on_gui_thread and console is not None and hasattr(console, "log_error"):
            console.log_error(full_message, traceback_text)
        else:
            dispatcher = _ensure_dispatcher()
            if dispatcher is not None:
                dispatcher.error_logged.emit(full_message, traceback_text or "")
    except Exception:
        pass


def _sys_excepthook(exc_type, exc_value, exc_tb) -> None:
    """Global sys.excepthook routing unhandled exceptions to console only."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    report_error("Exception non gérée", str(exc_value) or exc_type.__name__, tb_text)


def _threading_excepthook(args) -> None:
    """Global threading.excepthook routing thread exceptions to console only."""
    if issubclass(args.exc_type, KeyboardInterrupt):
        return

    tb_text = "".join(
        traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
    )
    thread_name = getattr(args.thread, "name", "Thread")
    report_error(
        f"Exception non gérée ({thread_name})",
        str(args.exc_value) or args.exc_type.__name__,
        tb_text,
    )


def install_exception_hooks() -> None:
    """Installs global exception hooks so unhandled errors go to console without popups."""
    sys.excepthook = _sys_excepthook
    if hasattr(threading, "excepthook"):
        threading.excepthook = _threading_excepthook
