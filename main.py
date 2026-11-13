#!/usr/bin/env python3
"""
Algoo IDE Entry Point.
Developed by softsurgery (https://github.com/softsurgery/algoo).
"""

import sys
import os

# Ensure the root directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Use the native OS window manager on Linux desktop sessions (via xcb)
# for all decorations, title bars, borders, resizing, moving, minimizing,
# maximizing, and positioning rather than Qt5's client-side Wayland decoration.
if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
    if os.environ.get("QT_QPA_PLATFORM", "") in ("", "wayland", "wayland-egl"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from ui.icons import get_app_icon
from ui.theme_utils import (
    detect_system_dark_mode,
    create_dark_palette,
    create_light_palette,
    get_system_theme_watcher
)
from ui.main_window import MainWindow
from database import get_database

def main():
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Algoo")
    app.setApplicationDisplayName("Algoo")
    app.setOrganizationName("softsurgery")
    app.setDesktopFileName("algoo.desktop")
    app.setWindowIcon(get_app_icon())

    # Initialize live system theme watcher
    get_system_theme_watcher()

    # Determine theme preference from SQLite database, with fallback to system
    db = get_database()
    theme_mode = db.get_theme_mode(None)
    if theme_mode is None:
        db.set_theme_mode("system")
        is_dark = detect_system_dark_mode()
    elif theme_mode == "system":
        is_dark = detect_system_dark_mode()
    elif theme_mode == "dark":
        is_dark = True
    elif theme_mode == "light":
        is_dark = False
    else:
        saved_dark = db.is_dark_mode()
        is_dark = saved_dark if saved_dark is not None else detect_system_dark_mode()

    app.setPalette(create_dark_palette() if is_dark else create_light_palette())

    # Set default app font
    font = QFont("-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Ubuntu, sans-serif", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
