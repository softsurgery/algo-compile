"""
Domain-specific settings and preferences management for Algoo IDE.
Handles key-value settings, theme preferences, code editor font and behavior, and syntax colors.
"""

import json
from typing import Optional, Dict, Any


class SettingsMixin:
    """Mixin for managing user settings, themes, and editor options in DatabaseManager."""

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a setting value by key."""
        with self._lock:
            if self._conn is None:
                return default
            cur = self._conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Sets or updates a setting value."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """, (key, str(value)))
            self._conn.commit()

    def remove_setting(self, key: str) -> None:
        """Removes a setting by key."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM settings WHERE key = ?", (key,))
            self._conn.commit()

    def get_theme(self, default: Optional[str] = None) -> Optional[str]:
        """Returns 'dark', 'light', or 'system', or default if not set."""
        mode = self.get_setting("theme_mode", None)
        if mode in ("dark", "light", "system"):
            return mode
        return self.get_setting("theme", default)

    def set_theme(self, theme: str) -> None:
        """Sets theme preference ('dark', 'light', or 'system')."""
        t = theme.lower().strip()
        if t in ("system", "système", "auto"):
            norm_theme = "system"
        elif t.startswith("dark") or t.startswith("sombre"):
            norm_theme = "dark"
        else:
            norm_theme = "light"
        self.set_setting("theme", "dark" if norm_theme == "dark" else "light")
        self.set_setting("theme_mode", norm_theme)

    def get_theme_mode(self, default: str = "system") -> str:
        """Returns 'system', 'dark', or 'light'."""
        mode = self.get_setting("theme_mode", None)
        if mode in ("system", "dark", "light"):
            return mode
        return default

    def set_theme_mode(self, mode: str) -> None:
        """Stores theme mode ('system', 'dark', or 'light')."""
        self.set_theme(mode)

    def is_dark_mode(self, default: Optional[bool] = None) -> Optional[bool]:
        """Returns True if dark mode is configured, False if light mode, or default."""
        mode = self.get_theme_mode(None)
        if mode == "system":
            try:
                from ui.theme_utils import detect_system_dark_mode
                return detect_system_dark_mode()
            except Exception:
                return default
        if mode in ("dark", "light"):
            return mode == "dark"
        theme = self.get_setting("theme", None)
        if theme is None:
            return default
        return theme == "dark"

    def set_dark_mode(self, is_dark: bool) -> None:
        """Convenience method to set dark mode boolean."""
        self.set_setting("theme", "dark" if is_dark else "light")
        # Preserve 'system' theme_mode if currently configured as system
        if self.get_theme_mode(None) != "system":
            self.set_setting("theme_mode", "dark" if is_dark else "light")

    def get_global_theme(self, default: str = "catppuccin") -> str:
        """Returns global theme variant name ('catppuccin', 'slate', 'nord', etc.)."""
        return self.get_setting("global_theme", default)

    def set_global_theme(self, name: str) -> None:
        """Stores global theme variant name."""
        self.set_setting("global_theme", name)

    def get_editor_settings(self) -> Dict[str, Any]:
        """Returns dictionary of editor font and behavior preferences."""
        raw = self.get_setting("editor_settings", None)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return {
            "font_family": "JetBrains Mono",
            "font_size": 11,
            "tab_size": 4,
            "show_line_numbers": True,
            "highlight_current_line": True,
            "auto_indent": True,
        }

    def set_editor_settings(self, settings: Dict[str, Any]) -> None:
        """Persists dictionary of editor preferences."""
        self.set_setting("editor_settings", json.dumps(settings))

    def get_syntax_preset(self, default: str = "Algoo") -> str:
        """Returns active syntax colors preset name."""
        return self.get_setting("syntax_preset", default)

    def set_syntax_preset(self, preset_name: str) -> None:
        """Persists chosen syntax colors preset name."""
        self.set_setting("syntax_preset", preset_name)

    def get_syntax_colors(self, is_dark: bool) -> Dict[str, str]:
        """Returns custom syntax highlighting colors or empty dict if default."""
        key = "syntax_colors_dark" if is_dark else "syntax_colors_light"
        raw = self.get_setting(key, None)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return {}

    def set_syntax_colors(self, colors: Dict[str, str], is_dark: bool) -> None:
        """Persists custom syntax highlighting colors."""
        key = "syntax_colors_dark" if is_dark else "syntax_colors_light"
        self.set_setting(key, json.dumps(colors))
