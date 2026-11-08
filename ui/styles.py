"""
Modern stylesheets for the IDE: Light (Thonny style) and Modern Dark themes.
"""

LIGHT_THEME = """
/* Global Window and Base Controls */
QMainWindow {
    background-color: #f7f9fa;
    color: #2c3e50;
}

QWidget {
    color: #2c3e50;
}

/* ToolBar - Thonny style */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e1e8ed;
    padding: 4px 8px;
    spacing: 6px;
}

QToolButton {
    background-color: transparent;
    color: #2c3e50;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #edf2f7;
    border: 1px solid #cbd5e1;
}

QToolButton:pressed {
    background-color: #e2e8f0;
}

/* Specific Accent Buttons */
QToolButton#btn_run {
    background-color: #ebfbee;
    border: 1px solid #8ce99a;
    color: #2b8a3e;
    font-weight: bold;
}
QToolButton#btn_run:hover {
    background-color: #d3f9d8;
    border: 1px solid #69db7c;
}

QToolButton#btn_stop {
    background-color: #fff5f5;
    border: 1px solid #ffc9c9;
    color: #c92a2a;
    font-weight: bold;
}
QToolButton#btn_stop:hover {
    background-color: #ffe3e3;
    border: 1px solid #ffa8a8;
}

QToolButton#btn_python {
    background-color: #e7f5ff;
    border: 1px solid #a5d8ff;
    color: #1971c2;
    font-weight: bold;
}
QToolButton#btn_python:hover {
    background-color: #d0ebff;
    border: 1px solid #74c0fc;
}

/* MenuBar */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e1e8ed;
    padding: 2px 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #edf2f7;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #ebf5fb;
    color: #1d70b8;
}

QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 4px 6px;
}

/* Tabs */
QTabWidget::tab-bar {
    left: 6px;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #edf2f7;
    color: #4a5568;
    margin-left: 6px;
    padding-left: 14px;
    padding-right: 25px;
    padding-top: 6px;
    padding-bottom: 6px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1a202c;
    border-top: 2px solid #3182ce;
    border-left: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
}

QTabBar::close-button {
    subcontrol-position: right;
    margin-left: 6px;
    padding: 2px;
}

QTabBar::close-button:hover {
    background-color: #fee2e2;
    border-radius: 3px;
}

/* Splitters */
QSplitter::handle {
    background-color: #e2e8f0;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

/* Text Editors & Inputs */
QPlainTextEdit, QTextEdit {
    background-color: #ffffff;
    color: #1a202c;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    selection-background-color: #bbf7d0;
    selection-color: #000000;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #4a5568;
    padding: 2px 6px;
}

QStatusBar::item {
    border: none;
}

/* Tables (TDO, Variables) */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    gridline-color: #e2e8f0;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #edf2f7;
    color: #2d3748;
    padding: 6px;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
}

/* Push Buttons */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 5px 12px;
    color: #1e293b;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton:pressed {
    background-color: #e2e8f0;
}
"""

DARK_THEME = """
/* Global Window and Base Controls */
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    color: #cdd6f4;
}

/* ToolBar */
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 4px 8px;
    spacing: 6px;
}

QToolButton {
    background-color: transparent;
    color: #cdd6f4;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #313244;
    border: 1px solid #45475a;
}

QToolButton:pressed {
    background-color: #45475a;
}

/* Specific Accent Buttons */
QToolButton#btn_run {
    background-color: #1a3328;
    border: 1px solid #2ecc71;
    color: #a6e3a1;
    font-weight: bold;
}
QToolButton#btn_run:hover {
    background-color: #234d38;
}

QToolButton#btn_stop {
    background-color: #3e1f26;
    border: 1px solid #e74c3c;
    color: #f38ba8;
    font-weight: bold;
}
QToolButton#btn_stop:hover {
    background-color: #552732;
}

QToolButton#btn_python {
    background-color: #1e2d42;
    border: 1px solid #89b4fa;
    color: #89dceb;
    font-weight: bold;
}
QToolButton#btn_python:hover {
    background-color: #283d5a;
}

/* MenuBar */
QMenuBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 2px 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenu {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #313244;
    color: #89b4fa;
}

QMenu::separator {
    height: 1px;
    background-color: #313244;
    margin: 4px 6px;
}

/* Tabs */
QTabWidget::tab-bar {
    left: 6px;
}

QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #181825;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1e1e2e;
    color: #a6adc8;
    margin-left: 6px;
    padding-left: 14px;
    padding-right: 25px;
    padding-top: 6px;
    padding-bottom: 6px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #181825;
    color: #cdd6f4;
    border-top: 2px solid #89b4fa;
    border-left: 1px solid #313244;
    border-right: 1px solid #313244;
}

QTabBar::tab:hover:!selected {
    background-color: #313244;
}

QTabBar::close-button {
    subcontrol-position: right;
    margin-left: 6px;
    padding: 2px;
}

QTabBar::close-button:hover {
    background-color: #fee2e2;
    border-radius: 3px;
}

/* Splitters */
QSplitter::handle {
    background-color: #313244;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

/* Text Editors & Inputs */
QPlainTextEdit, QTextEdit {
    background-color: #11111b;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    selection-background-color: #45475a;
    selection-color: #ffffff;
}

/* Status Bar */
QStatusBar {
    background-color: #181825;
    border-top: 1px solid #313244;
    color: #a6adc8;
    padding: 2px 6px;
}

QStatusBar::item {
    border: none;
}

/* Tables */
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #11111b;
    color: #cdd6f4;
    padding: 6px;
    border: none;
    border-right: 1px solid #313244;
    border-bottom: 1px solid #313244;
    font-weight: 600;
}

/* Push Buttons */
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px 12px;
    color: #cdd6f4;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}
"""
