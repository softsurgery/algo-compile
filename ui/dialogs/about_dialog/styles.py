"""
Stylesheets for AboutDialog in Dark and Light modes.
"""

def get_about_dialog_stylesheet(is_dark: bool) -> str:
    """Returns the CSS stylesheet for AboutDialog according to dark/light mode."""
    if is_dark:
        return """
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel#about_title {
                color: #cdd6f4;
            }
            QLabel#about_version {
                color: #a6adc8;
                font-size: 12px;
            }
            QLabel#about_desc {
                color: #bac2de;
                font-size: 13px;
            }
            QFrame#about_card {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
            }
            QLabel#about_details {
                color: #cdd6f4;
            }
            QLabel#about_details a {
                color: #89b4fa;
                text-decoration: none;
            }
            QLabel#about_details a:hover {
                text-decoration: underline;
            }
            QPushButton#about_btn_github {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton#about_btn_github:hover {
                background-color: #45475a;
            }
            QPushButton#about_btn_close {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton#about_btn_close:hover {
                background-color: #b4befe;
            }
        """
    else:
        return """
            QDialog {
                background-color: #ffffff;
                color: #1e293b;
            }
            QLabel#about_title {
                color: #0f172a;
            }
            QLabel#about_version {
                color: #64748b;
                font-size: 12px;
            }
            QLabel#about_desc {
                color: #475569;
                font-size: 13px;
            }
            QFrame#about_card {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel#about_details {
                color: #334155;
            }
            QLabel#about_details a {
                color: #2563eb;
                text-decoration: none;
            }
            QLabel#about_details a:hover {
                text-decoration: underline;
            }
            QPushButton#about_btn_github {
                background-color: #f1f5f9;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton#about_btn_github:hover {
                background-color: #e2e8f0;
            }
            QPushButton#about_btn_close {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton#about_btn_close:hover {
                background-color: #1d4ed8;
            }
        """
