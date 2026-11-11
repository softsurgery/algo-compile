"""
SQLite Database Manager for Algoo IDE.
Persists application settings (dark/light mode), open tabs session, and recently opened files.
"""

import os
import sqlite3
import threading
from typing import Optional, List, Dict, Any


class DatabaseManager:
    """Manages SQLite storage for Algoo IDE."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = self.get_default_db_path()
        else:
            self.db_path = db_path

        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_connection()
        self._create_tables()

    @staticmethod
    def get_default_db_path() -> str:
        """Determines the standard persistent path for algoo.db."""
        try:
            from PyQt5.QtCore import QStandardPaths
            base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        except Exception:
            base_dir = ""

        if not base_dir:
            base_dir = os.path.expanduser("~/.local/share/softsurgery/Algoo")

        try:
            os.makedirs(base_dir, exist_ok=True)
        except OSError:
            base_dir = os.path.expanduser("~/.config/algoo")
            os.makedirs(base_dir, exist_ok=True)

        return os.path.join(base_dir, "algoo.db")

    def _init_connection(self):
        """Initializes SQLite connection with safe concurrency defaults."""
        if self.db_path != ":memory:":
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        self._conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        self._conn.row_factory = sqlite3.Row

        if self.db_path != ":memory:":
            try:
                self._conn.execute("PRAGMA journal_mode = WAL;")
                self._conn.execute("PRAGMA synchronous = NORMAL;")
            except sqlite3.Error:
                pass

    def _create_tables(self):
        """Creates settings and opened_files tables if they do not exist."""
        with self._lock:
            cur = self._conn.cursor()
            # 1. Key-value settings table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

            # 2. Opened and recent files table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS opened_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    is_open INTEGER NOT NULL DEFAULT 1,
                    tab_order INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    last_opened TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_opened_files_is_open ON opened_files(is_open);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_opened_files_last_opened ON opened_files(last_opened);")
            self._conn.commit()

    # -------------------------------------------------------------------------
    # Settings Management (Dark/Light mode & generic configuration)
    # -------------------------------------------------------------------------
    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a setting value by key."""
        with self._lock:
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
        legacy = self.get_setting("theme", None)
        if legacy in ("dark", "light"):
            return legacy
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
        self.set_theme("dark" if is_dark else "light")

    def get_global_theme(self, default: str = "catppuccin") -> str:
        """Returns global theme variant name ('catppuccin', 'slate', 'nord', etc.)."""
        return self.get_setting("global_theme", default)

    def set_global_theme(self, name: str) -> None:
        """Stores global theme variant name."""
        self.set_setting("global_theme", name)

    def get_editor_settings(self) -> Dict[str, Any]:
        """Returns dictionary of editor font and behavior preferences."""
        import json
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
        import json
        self.set_setting("editor_settings", json.dumps(settings))

    def get_syntax_colors(self, is_dark: bool) -> Dict[str, str]:
        """Returns custom syntax highlighting colors or empty dict if default."""
        import json
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
        import json
        key = "syntax_colors_dark" if is_dark else "syntax_colors_light"
        self.set_setting(key, json.dumps(colors))

    # -------------------------------------------------------------------------
    # Opened Files & Tabs Session Management
    # -------------------------------------------------------------------------
    def record_file_opened(
        self,
        file_path: str,
        is_open: bool = True,
        is_active: bool = False,
        tab_order: int = 0
    ) -> None:
        """
        Records a file as opened, updating its last_opened timestamp and tab state.
        """
        norm_path = os.path.abspath(file_path)
        with self._lock:
            cur = self._conn.cursor()
            if is_active:
                cur.execute("UPDATE opened_files SET is_active = 0")

            cur.execute("""
                INSERT INTO opened_files (file_path, is_open, tab_order, is_active, last_opened)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(file_path) DO UPDATE SET
                    is_open = excluded.is_open,
                    tab_order = excluded.tab_order,
                    is_active = excluded.is_active,
                    last_opened = CURRENT_TIMESTAMP;
            """, (norm_path, 1 if is_open else 0, tab_order, 1 if is_active else 0))
            self._conn.commit()

    def record_file_closed(self, file_path: str) -> None:
        """Marks a file as no longer open in tabs while retaining it in history."""
        norm_path = os.path.abspath(file_path)
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("""
                UPDATE opened_files
                SET is_open = 0, is_active = 0
                WHERE file_path = ?;
            """, (norm_path,))
            self._conn.commit()

    def set_active_file(self, file_path: Optional[str]) -> None:
        """Sets the active file in the tab session."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("UPDATE opened_files SET is_active = 0")
            if file_path:
                norm_path = os.path.abspath(file_path)
                cur.execute("UPDATE opened_files SET is_active = 1 WHERE file_path = ?", (norm_path,))
            self._conn.commit()

    def sync_open_tabs(self, tabs: List[Dict[str, Any]]) -> None:
        """
        Synchronizes currently open tabs with the database in a single atomic transaction.
        Each item in tabs should be a dict with:
          - file_path: str
          - tab_order: int (optional)
          - is_active: bool (optional)
        """
        with self._lock:
            cur = self._conn.cursor()
            # Mark all as closed first
            cur.execute("UPDATE opened_files SET is_open = 0, is_active = 0;")

            for i, tab in enumerate(tabs):
                raw_path = tab.get("file_path")
                if not raw_path:
                    continue
                norm_path = os.path.abspath(raw_path)
                tab_order = tab.get("tab_order", i)
                is_active = 1 if tab.get("is_active", False) else 0

                cur.execute("""
                    INSERT INTO opened_files (file_path, is_open, tab_order, is_active, last_opened)
                    VALUES (?, 1, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(file_path) DO UPDATE SET
                        is_open = 1,
                        tab_order = excluded.tab_order,
                        is_active = excluded.is_active,
                        last_opened = CURRENT_TIMESTAMP;
                """, (norm_path, tab_order, is_active))

            self._conn.commit()

    def get_open_files(self, check_exists: bool = True) -> List[str]:
        """
        Returns list of file paths currently recorded as open in tabs,
        ordered by tab_order ASC and last_opened ASC.
        """
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT file_path FROM opened_files
                WHERE is_open = 1
                ORDER BY tab_order ASC, last_opened ASC;
            """)
            rows = cur.fetchall()

            result = []
            missing = []
            for row in rows:
                path = row["file_path"]
                if check_exists and not os.path.exists(path):
                    missing.append(path)
                else:
                    result.append(path)

            if missing:
                cur.executemany(
                    "UPDATE opened_files SET is_open = 0, is_active = 0 WHERE file_path = ?;",
                    [(p,) for p in missing]
                )
                self._conn.commit()

            return result

    def get_active_file(self) -> Optional[str]:
        """Returns the file path of the currently active open tab, if any."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT file_path FROM opened_files
                WHERE is_open = 1 AND is_active = 1
                LIMIT 1;
            """)
            row = cur.fetchone()
            if row:
                path = row["file_path"]
                if os.path.exists(path):
                    return path
            return None

    def get_latest_opened_files(self, limit: int = 10, check_exists: bool = True) -> List[str]:
        """
        Returns list of the most recently opened file paths,
        ordered by last_opened DESC.
        """
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("""
                SELECT file_path FROM opened_files
                ORDER BY last_opened DESC
                LIMIT ?;
            """, (limit * 2 if check_exists else limit,))
            rows = cur.fetchall()

            result = []
            for row in rows:
                path = row["file_path"]
                if check_exists and not os.path.exists(path):
                    continue
                result.append(path)
                if len(result) >= limit:
                    break

            return result

    def clear_recent_files(self) -> None:
        """Clears the history of recent files not currently open in tabs."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM opened_files WHERE is_open = 0;")
            self._conn.commit()

    def clear_all(self) -> None:
        """Wipes all rows from settings and opened_files (useful for testing)."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM settings;")
            cur.execute("DELETE FROM opened_files;")
            self._conn.commit()

    def close(self):
        """Closes the underlying SQLite connection."""
        with self._lock:
            if self._conn:
                try:
                    self._conn.close()
                except Exception:
                    pass
                self._conn = None


# Global singleton instance
_GLOBAL_DB: Optional[DatabaseManager] = None


def get_database(db_path: Optional[str] = None) -> DatabaseManager:
    """Returns the shared DatabaseManager instance or a new one for custom path."""
    global _GLOBAL_DB
    if db_path is not None:
        return DatabaseManager(db_path)
    if _GLOBAL_DB is None or _GLOBAL_DB._conn is None:
        _GLOBAL_DB = DatabaseManager()
    return _GLOBAL_DB


def reset_database_instance():
    """Resets and closes the shared DatabaseManager singleton."""
    global _GLOBAL_DB
    if _GLOBAL_DB is not None:
        try:
            _GLOBAL_DB.close()
        except Exception:
            pass
        _GLOBAL_DB = None
