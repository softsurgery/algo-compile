"""
Theme and Window Title Bar utilities for Algoo IDE.
Supports dynamic dark/light title bar color adaptation across Linux (Wayland & X11),
Windows (DWM Immersive Dark Mode), and macOS.
"""

import sys
import shutil
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor


def detect_system_dark_mode() -> bool:
    """Detects whether the operating system is currently configured for dark mode."""
    # 1. Linux GNOME / Freedesktop
    try:
        res = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True, text=True, timeout=1
        )
        if "dark" in res.stdout.lower():
            return True
        res_gtk = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True, timeout=1
        )
        if "dark" in res_gtk.stdout.lower():
            return True
    except Exception:
        pass

    # 2. Freedesktop Portal (KDE / modern Wayland compositors)
    try:
        res = subprocess.run(
            [
                "dbus-send", "--session", "--print-reply=literal",
                "--dest=org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Settings.Read",
                "string:org.freedesktop.appearance", "string:color-scheme"
            ],
            capture_output=True, text=True, timeout=1
        )
        if "uint32 1" in res.stdout:
            return True
    except Exception:
        pass

    # 3. Windows 10/11 Personalize Registry
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return val == 0
        except Exception:
            pass

    return False


def create_dark_palette() -> QPalette:
    """Builds a comprehensive dark QPalette matching Catppuccin Mocha / IDE Dark theme."""
    pal = QPalette()
    dark_bg = QColor("#181825")      # Window bar / Title bar / Mantle
    dark_base = QColor("#1e1e2e")    # Editor / Base
    dark_alt = QColor("#11111b")     # Crust
    text_color = QColor("#cdd6f4")
    dim_text = QColor("#a6adc8")
    disabled_text = QColor("#6c7086")
    highlight_color = QColor("#3b82f6")

    # Active
    pal.setColor(QPalette.Window, dark_bg)
    pal.setColor(QPalette.WindowText, text_color)
    pal.setColor(QPalette.Base, dark_base)
    pal.setColor(QPalette.AlternateBase, dark_alt)
    pal.setColor(QPalette.ToolTipBase, dark_base)
    pal.setColor(QPalette.ToolTipText, text_color)
    pal.setColor(QPalette.Text, text_color)
    pal.setColor(QPalette.Button, dark_bg)
    pal.setColor(QPalette.ButtonText, text_color)
    pal.setColor(QPalette.BrightText, QColor("#ffffff"))
    pal.setColor(QPalette.Highlight, highlight_color)
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.Light, QColor("#313244"))
    pal.setColor(QPalette.Midlight, QColor("#262637"))
    pal.setColor(QPalette.Mid, QColor("#1e1e2e"))
    pal.setColor(QPalette.Dark, QColor("#11111b"))
    pal.setColor(QPalette.Shadow, QColor("#0c0c14"))

    # Inactive state (title bar unfocused)
    pal.setColor(QPalette.Inactive, QPalette.Window, dark_bg)
    pal.setColor(QPalette.Inactive, QPalette.WindowText, dim_text)
    pal.setColor(QPalette.Inactive, QPalette.Button, dark_bg)
    pal.setColor(QPalette.Inactive, QPalette.ButtonText, dim_text)
    pal.setColor(QPalette.Inactive, QPalette.Highlight, QColor("#283d5a"))
    pal.setColor(QPalette.Inactive, QPalette.HighlightedText, text_color)

    # Disabled state
    pal.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
    pal.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
    return pal


def create_light_palette() -> QPalette:
    """Builds a clean light QPalette for Light theme."""
    pal = QPalette()
    light_bg = QColor("#f7f9fa")
    light_base = QColor("#ffffff")
    text_color = QColor("#2c3e50")
    dim_text = QColor("#64748b")
    disabled_text = QColor("#94a3b8")
    highlight_color = QColor("#3b82f6")

    # Active
    pal.setColor(QPalette.Window, light_bg)
    pal.setColor(QPalette.WindowText, text_color)
    pal.setColor(QPalette.Base, light_base)
    pal.setColor(QPalette.AlternateBase, QColor("#f1f5f9"))
    pal.setColor(QPalette.ToolTipBase, light_base)
    pal.setColor(QPalette.ToolTipText, text_color)
    pal.setColor(QPalette.Text, text_color)
    pal.setColor(QPalette.Button, light_bg)
    pal.setColor(QPalette.ButtonText, text_color)
    pal.setColor(QPalette.BrightText, QColor("#ffffff"))
    pal.setColor(QPalette.Highlight, highlight_color)
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.Light, QColor("#ffffff"))
    pal.setColor(QPalette.Midlight, QColor("#f8fafc"))
    pal.setColor(QPalette.Mid, QColor("#cbd5e1"))
    pal.setColor(QPalette.Dark, QColor("#94a3b8"))
    pal.setColor(QPalette.Shadow, QColor("#64748b"))

    # Inactive
    pal.setColor(QPalette.Inactive, QPalette.Window, light_bg)
    pal.setColor(QPalette.Inactive, QPalette.WindowText, dim_text)
    pal.setColor(QPalette.Inactive, QPalette.Button, light_bg)
    pal.setColor(QPalette.Inactive, QPalette.ButtonText, dim_text)

    # Disabled
    pal.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
    pal.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
    return pal


def apply_os_window_theme(window, is_dark: bool):
    """
    Applies dark or light theme directly to the operating system's window frame / title bar:
    1. Sets Qt application & window palettes (used by Wayland client-side decorations like libbradient).
    2. Sets _GTK_THEME_VARIANT on Linux X11/XWayland so Mutter/GNOME renders dark server-side title bars.
    3. Sets DWMWA_USE_IMMERSIVE_DARK_MODE on Windows 10/11 DWM title bars.
    """
    pal = create_dark_palette() if is_dark else create_light_palette()
    app = QApplication.instance()
    if app:
        app.setPalette(pal)
    if window:
        window.setPalette(pal)

    # 1. Linux X11 / XWayland via xprop
    if window:
        try:
            win_id = int(window.winId())
            if win_id > 1:
                variant = "dark" if is_dark else "light"
                if shutil.which("xprop"):
                    subprocess.run(
                        [
                            "xprop", "-id", str(win_id),
                            "-f", "_GTK_THEME_VARIANT", "8s",
                            "-set", "_GTK_THEME_VARIANT", variant
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False
                    )
        except Exception:
            pass

    # 2. Windows 10/11 DWM Immersive Dark Mode
    if window and sys.platform == "win32":
        try:
            import ctypes
            hwnd = int(window.winId())
            val = ctypes.c_int(1 if is_dark else 0)
            # DWMWA_USE_IMMERSIVE_DARK_MODE (20 on newer Win10/11, 19 on older Win10)
            res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(val), ctypes.sizeof(val)
            )
            if res != 0:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 19, ctypes.byref(val), ctypes.sizeof(val)
                )
        except Exception:
            pass
