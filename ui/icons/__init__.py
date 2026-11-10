"""
Modular vector icons generator using QPainter and QPixmap.
Each icon is implemented in its own dedicated module.
"""

from PyQt5.QtGui import QIcon
from . import (
    base,
    new,
    open,
    save,
    run,
    stop,
    step,
    python,
    copy,
    clear,
    zoom_in,
    zoom_out,
    theme,
    help,
    close,
)

ICONS = {
    "new": new.get_icon,
    "open": open.get_icon,
    "save": save.get_icon,
    "run": run.get_icon,
    "stop": stop.get_icon,
    "step": step.get_icon,
    "python": python.get_icon,
    "copy": copy.get_icon,
    "clear": clear.get_icon,
    "zoom_in": zoom_in.get_icon,
    "zoom_out": zoom_out.get_icon,
    "theme": theme.get_icon,
    "help": help.get_icon,
    "close": close.get_icon,
}

def create_icon(name: str, color_hex: str = "#2c3e50", size: int = 24) -> QIcon:
    """Generates a QIcon with the specified name and color."""
    generator = ICONS.get(name)
    if generator:
        return generator(color_hex, size)
    
    # Fallback default dot
    def _draw_default(p, s, margin, color):
        p.setPen(color)
        p.setBrush(color)
        p.drawEllipse(int(s / 2), int(s / 2), 3, 3)

    return base.make_icon(_draw_default, color_hex, size)
