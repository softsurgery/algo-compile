"""
Theme and Window Title Bar utilities for Algoo IDE.
Supports dynamic dark/light title bar color adaptation across Linux (Wayland & X11),
Windows (DWM Immersive Dark Mode), and macOS.
"""

import sys
import os
import subprocess
from typing import Optional

# Ensure Linux desktop sessions use the native OS window manager (via xcb)
# for all window decorations, title bars, borders, resizing, moving, minimizing,
# maximizing, and positioning rather than Qt5's client-side Wayland decoration.
if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
    if os.environ.get("QT_QPA_PLATFORM", "") in ("", "wayland", "wayland-egl"):
        os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QObject, QTimer, QEvent, pyqtSignal, QFileSystemWatcher

try:
    from PyQt5.QtDBus import QDBusConnection, QDBusMessage
    HAS_QTDBUS = True
except ImportError:
    HAS_QTDBUS = False
    QDBusMessage = None


def detect_system_dark_mode() -> bool:
    """Detects whether the operating system is currently configured for dark mode."""
    # 1. Linux Freedesktop Portal (via in-process QtDBus, ~0.2ms)
    dbus_connected = False
    has_dbus_env = bool(os.environ.get("DBUS_SESSION_BUS_ADDRESS"))
    if HAS_QTDBUS and sys.platform.startswith("linux") and has_dbus_env:
        try:
            bus = QDBusConnection.sessionBus()
            if bus.isConnected():
                dbus_connected = True
                iface = bus.interface()
                if iface and iface.isServiceRegistered("org.freedesktop.portal.Desktop").value():
                    msg = QDBusMessage.createMethodCall(
                        "org.freedesktop.portal.Desktop",
                        "/org/freedesktop/portal/desktop",
                        "org.freedesktop.portal.Settings",
                        "Read"
                    )
                    msg.setArguments(["org.freedesktop.appearance", "color-scheme"])
                    reply = bus.call(msg)
                    if reply.type() == QDBusMessage.ReplyMessage and reply.arguments():
                        val = reply.arguments()[0]
                        if val == 1:
                            return True
                        elif val in (0, 2):
                            return False
        except Exception:
            pass

    # 2. Linux Freedesktop Portal (dbus-send fallback, only if QtDBus wasn't available/connected)
    if sys.platform.startswith("linux") and not dbus_connected and has_dbus_env:
        try:
            res = subprocess.run(
                [
                    "dbus-send", "--session", "--print-reply=literal",
                    "--dest=org.freedesktop.portal.Desktop",
                    "/org/freedesktop/portal/desktop",
                    "org.freedesktop.portal.Settings.Read",
                    "string:org.freedesktop.appearance", "string:color-scheme"
                ],
                capture_output=True, text=True, timeout=0.5
            )
            if res.returncode == 0:
                if "uint32 1" in res.stdout:
                    return True
                elif "uint32 0" in res.stdout or "uint32 2" in res.stdout:
                    return False
        except Exception:
            pass

    # 3. Linux GNOME / Freedesktop GSettings color-scheme
    if sys.platform.startswith("linux"):
        try:
            res = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True, text=True, timeout=1
            )
            if res.returncode == 0:
                val = res.stdout.strip().strip("'").strip('"').lower()
                if "dark" in val:
                    return True
                elif "light" in val or val == "default":
                    return False
        except Exception:
            pass

        # Legacy GNOME / XFCE / MATE: check gtk-theme only if color-scheme is absent
        try:
            res_gtk = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, timeout=1
            )
            if res_gtk.returncode == 0:
                val_gtk = res_gtk.stdout.strip().strip("'").strip('"').lower()
                if "dark" in val_gtk:
                    return True
                elif "light" in val_gtk:
                    return False
        except Exception:
            pass

    # 4. macOS AppleInterfaceStyle
    if sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True, timeout=1
            )
            if res.returncode == 0 and "dark" in res.stdout.lower():
                return True
            return False
        except Exception:
            pass

    # 5. Windows 10/11 Personalize Registry
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

    # 6. Fallback to QApplication palette lightness if available
    app = QApplication.instance()
    if app:
        try:
            return app.palette().color(QPalette.Window).lightness() < 128
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


def apply_os_window_theme(window, is_dark: Optional[bool] = None):
    """
    Applies the standard Qt dark or light palette to QApplication and the target window,
    leaving all window management (decorations, title bars, borders, resizing, moving,
    minimizing, maximizing, and positioning) to the native OS window manager.
    """
    if is_dark is None:
        is_dark = detect_system_dark_mode()

    pal = create_dark_palette() if is_dark else create_light_palette()
    app = QApplication.instance()
    if app:
        app.setPalette(pal)
    if window:
        window.setPalette(pal)
        window.update()


class SystemThemeWatcher(QObject):
    """
    Watches system dark/light theme changes in real-time across:
    - Linux Wayland & X11 (via Freedesktop Portal Settings D-Bus signals and GNOME settings)
    - Windows (via periodic checks and window activation)
    - macOS (via AppleInterfaceStyle checks and window activation)

    Emits theme_changed(bool) immediately when a system transition occurs without
    requiring app or window restarts.
    """
    theme_changed = pyqtSignal(bool)

    _instance = None

    @classmethod
    def instance(cls) -> "SystemThemeWatcher":
        if cls._instance is None:
            cls._instance = SystemThemeWatcher()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_is_dark: Optional[bool] = detect_system_dark_mode()
        self._setup_dbus()
        self._setup_file_watcher()
        self._setup_timer()
        self._setup_event_filter()

    def _setup_dbus(self):
        if HAS_QTDBUS and sys.platform.startswith("linux") and os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
            try:
                bus = QDBusConnection.sessionBus()
                if bus.isConnected():
                    # Listen for Portal SettingChanged signals
                    bus.connect(
                        "",
                        "/org/freedesktop/portal/desktop",
                        "org.freedesktop.portal.Settings",
                        "SettingChanged",
                        self._on_dbus_setting_changed
                    )
                    bus.connect(
                        "",
                        "",
                        "org.freedesktop.portal.Settings",
                        "SettingChanged",
                        self._on_dbus_setting_changed
                    )
            except Exception:
                pass

    if HAS_QTDBUS:
        from PyQt5.QtCore import pyqtSlot
        @pyqtSlot(QDBusMessage)
        def _on_dbus_setting_changed(self, msg: QDBusMessage = None):
            self.check_theme()
    else:
        def _on_dbus_setting_changed(self, msg=None):
            self.check_theme()

    def _setup_file_watcher(self):
        """Monitors GNOME/dconf settings files directly via inotify for instantaneous detection."""
        if sys.platform.startswith("linux"):
            try:
                self._fs_watcher = QFileSystemWatcher(self)
                dconf_path = os.path.expanduser("~/.config/dconf/user")
                dconf_dir = os.path.expanduser("~/.config/dconf")
                paths = []
                if os.path.exists(dconf_path):
                    paths.append(dconf_path)
                if os.path.exists(dconf_dir):
                    paths.append(dconf_dir)
                if paths:
                    self._fs_watcher.addPaths(paths)
                    self._fs_watcher.fileChanged.connect(self._on_dconf_changed)
                    self._fs_watcher.directoryChanged.connect(self._on_dconf_changed)
            except Exception:
                pass

    def _on_dconf_changed(self, path=None):
        # Trigger immediate check and re-add file in case dconf rewrote it atomically
        QTimer.singleShot(20, self.check_theme)
        if hasattr(self, "_fs_watcher"):
            dconf_path = os.path.expanduser("~/.config/dconf/user")
            if os.path.exists(dconf_path) and dconf_path not in self._fs_watcher.files():
                self._fs_watcher.addPath(dconf_path)

    def _setup_timer(self):
        # 300ms fallback interval for polling detection across all desktop environments
        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self.check_theme)
        if "unittest" not in sys.modules:
            self._timer.start()

    def _setup_event_filter(self):
        app = QApplication.instance()
        if app and "unittest" not in sys.modules:
            app.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Check immediately when user switches focus to this application
        if event.type() in (QEvent.ApplicationActivate, QEvent.WindowActivate, QEvent.ApplicationPaletteChange):
            self.check_theme()
        return super().eventFilter(obj, event)

    def is_dark_mode(self) -> bool:
        if self._last_is_dark is None:
            self._last_is_dark = detect_system_dark_mode()
        return self._last_is_dark

    def check_theme(self) -> bool:
        """Checks system theme immediately and emits theme_changed if transitioned."""
        current = detect_system_dark_mode()
        if self._last_is_dark != current:
            self._last_is_dark = current
            self.theme_changed.emit(current)
        return current


def get_system_theme_watcher() -> SystemThemeWatcher:
    """Returns the singleton SystemThemeWatcher instance."""
    return SystemThemeWatcher.instance()

