"""
App logo icon provider.
Loads the official Algoo logo from assets or project root.
"""

import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


def get_logo_path() -> str:
    """Finds the absolute path to logo.png."""
    from ui.platform_utils import get_resource_path

    ui_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        get_resource_path("ui", "assets", "logo.png"),
        get_resource_path("logo.png"),
        os.path.join(ui_dir, "assets", "logo.png"),
        os.path.join(os.path.dirname(ui_dir), "logo.png"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def get_pixmap(size: int = 128) -> QPixmap:
    """Returns a QPixmap of the logo scaled to the given size with smooth transformation."""
    path = get_logo_path()
    if not path:
        return QPixmap()
    pix = QPixmap(path)
    if pix.isNull():
        return pix
    if size > 0:
        return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pix


def get_icon(color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    """Returns a QIcon for the logo containing multiple standard resolutions."""
    path = get_logo_path()
    if not path:
        return QIcon()
    pix = QPixmap(path)
    if pix.isNull():
        return QIcon(path)

    icon = QIcon()
    for s in (16, 24, 32, 48, 64, 128, 256, 512):
        icon.addPixmap(pix.scaled(s, s, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    return icon
