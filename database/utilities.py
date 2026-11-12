"""
Database utilities and helper functions for Algoo IDE.
Includes default path resolution and singleton instance management.
"""

import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database.manager import DatabaseManager


_GLOBAL_DB: Optional["DatabaseManager"] = None


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


def get_database(db_path: Optional[str] = None) -> "DatabaseManager":
    """Returns the shared DatabaseManager instance or a new one for custom path."""
    global _GLOBAL_DB
    from database.manager import DatabaseManager
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
