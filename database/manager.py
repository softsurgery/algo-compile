"""
DatabaseManager assembling BaseDatabaseManager and domain mixins (Settings, Files).
"""

from typing import Optional
from database.base import BaseDatabaseManager
from database.settings import SettingsMixin
from database.files import FilesMixin
from database.utilities import get_default_db_path


class DatabaseManager(SettingsMixin, FilesMixin, BaseDatabaseManager):
    """Manages SQLite storage for Algoo IDE."""

    get_default_db_path = staticmethod(get_default_db_path)
