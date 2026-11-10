"""
UI module export for DatabaseManager.
"""

from database import (
    DatabaseManager,
    get_database,
    reset_database_instance
)

__all__ = ["DatabaseManager", "get_database", "reset_database_instance"]
