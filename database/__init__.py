"""
Database module for Algoo IDE.
Exposes DatabaseManager, base connection management, domain mixins, and utilities.
"""

from database.base import BaseDatabaseManager
from database.settings import SettingsMixin
from database.files import FilesMixin
from database.manager import DatabaseManager
from database.utilities import (
    get_default_db_path,
    get_database,
    reset_database_instance,
)

__all__ = [
    "BaseDatabaseManager",
    "SettingsMixin",
    "FilesMixin",
    "DatabaseManager",
    "get_database",
    "reset_database_instance",
    "get_default_db_path",
]
