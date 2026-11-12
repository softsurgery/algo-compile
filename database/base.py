"""
Base SQLite Database Manager for Algoo IDE.
Handles connection lifecycle, concurrency locks, and schema setup.
"""

import os
import sqlite3
import threading
from typing import Optional


class BaseDatabaseManager:
    """Core SQLite database connection and schema management."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from database.utilities import get_default_db_path
            self.db_path = get_default_db_path()
        else:
            self.db_path = db_path

        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_connection()
        self._create_tables()

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
