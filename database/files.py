"""
Domain-specific opened files and tab sessions management for Algoo IDE.
Handles tab session persistence, active file tracking, and recent files history.
"""

import os
from typing import Optional, List, Dict, Any


class FilesMixin:
    """Mixin for managing opened files and tabs session in DatabaseManager."""

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
