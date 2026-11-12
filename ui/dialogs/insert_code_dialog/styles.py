"""
Stylesheets and style helpers for InsertCodeDialog in Dark and Light modes.
"""

def get_secondary_button_style(is_dark: bool) -> str:
    if is_dark:
        return (
            "QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
            "QPushButton:hover { background-color: #45475a; border-color: #585b70; }"
            "QPushButton:pressed { background-color: #585b70; }"
        )
    return (
        "QPushButton { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
        "QPushButton:hover { background-color: #f1f5f9; border-color: #94a3b8; }"
        "QPushButton:pressed { background-color: #e2e8f0; }"
    )


def get_primary_insert_button_style() -> str:
    return (
        "QPushButton { background-color: #2563eb; color: #ffffff; font-weight: bold; border: none; padding: 6px 16px; border-radius: 6px; }"
        "QPushButton:hover { background-color: #1d4ed8; }"
        "QPushButton:pressed { background-color: #1e40af; }"
    )


def apply_compat_widget_styles(dialog, is_dark: bool):
    """Applies contextual dark/light styling to search input, list widget, and preview editor."""
    if is_dark:
        if hasattr(dialog, "search_input"):
            dialog.search_input.setStyleSheet(
                "QLineEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #89b4fa; }"
            )
        if hasattr(dialog, "list_widget"):
            dialog.list_widget.setStyleSheet(
                "QListWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #cdd6f4; }"
                "QListWidget::item:hover { background-color: #313244; }"
                "QListWidget::item:selected { background-color: #45475a; color: #ffffff; font-weight: bold; }"
            )
        if hasattr(dialog, "preview_editor"):
            dialog.preview_editor.setStyleSheet(
                "QPlainTextEdit { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }"
            )
    else:
        if hasattr(dialog, "search_input"):
            dialog.search_input.setStyleSheet(
                "QLineEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #3b82f6; }"
            )
        if hasattr(dialog, "list_widget"):
            dialog.list_widget.setStyleSheet(
                "QListWidget { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #1e293b; }"
                "QListWidget::item:hover { background-color: #f1f5f9; }"
                "QListWidget::item:selected { background-color: #e2e8f0; color: #0f172a; font-weight: bold; }"
            )
        if hasattr(dialog, "preview_editor"):
            dialog.preview_editor.setStyleSheet(
                "QPlainTextEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; }"
            )
