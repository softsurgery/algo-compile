"""
Dialogs package for Algoo IDE.
Contains modular dialog implementations for About, Insert Code, and Preferences.
"""

from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.insert_code_dialog import InsertCodeDialog
from ui.dialogs.preferences_dialog import PreferencesDialog

__all__ = [
    "AboutDialog",
    "InsertCodeDialog",
    "PreferencesDialog",
]
