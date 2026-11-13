"""
Cross-platform path and frozen-bundle utilities for Algoo IDE.
Works identically in source checkouts, PyInstaller bundles, and OS system installs.
"""

import os
import sys


def is_frozen() -> bool:
    """Returns True when running from a frozen PyInstaller executable."""
    return bool(getattr(sys, "frozen", False))


def get_bundle_dir() -> str:
    """Returns the base directory containing bundled application resources."""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return os.path.abspath(getattr(sys, "_MEIPASS"))
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def get_resource_path(*parts: str) -> str:
    """Resolves a path inside the application bundle or source tree."""
    return os.path.join(get_bundle_dir(), *parts)


def get_user_data_dir() -> str:
    """Returns a writable per-user data directory across Linux, Windows, and macOS."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        path = os.path.join(base, "softsurgery", "Algoo")
    elif sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support/softsurgery/Algoo")
    else:
        xdg = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        path = os.path.join(xdg, "softsurgery", "Algoo")
    os.makedirs(path, exist_ok=True)
    return path
