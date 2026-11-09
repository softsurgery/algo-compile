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

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from ui.theme_utils import (
    detect_system_dark_mode,
    create_dark_palette,
    create_light_palette
)
from ui.main_window import MainWindow

def main():
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Algoo")
    app.setApplicationDisplayName("Algoo")
    app.setOrganizationName("softsurgery")

    # Determine theme preference and pre-configure application palette
    settings = QSettings("softsurgery", "Algoo")
    if settings.contains("dark_mode"):
        is_dark = settings.value("dark_mode", type=bool)
    else:
        is_dark = detect_system_dark_mode()

    app.setPalette(create_dark_palette() if is_dark else create_light_palette())

    # Set default app font
    font = QFont("-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Ubuntu, sans-serif", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
