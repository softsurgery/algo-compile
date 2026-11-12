"""
Modern stylesheets for the IDE: Light (Thonny style) and Modern Dark themes.
"""

import os
from PyQt5.QtGui import QImageReader

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS_DIR = os.path.join(_BASE_DIR, "assets")

_EXT = "svg" if b"svg" in QImageReader.supportedImageFormats() else "png"
_TAB_CLOSE_LIGHT = os.path.join(_ASSETS_DIR, f"tab_close_light.{_EXT}").replace("\\", "/")
_TAB_CLOSE_LIGHT_HOVER = os.path.join(_ASSETS_DIR, f"tab_close_light_hover.{_EXT}").replace("\\", "/")
_TAB_CLOSE_DARK = os.path.join(_ASSETS_DIR, f"tab_close_dark.{_EXT}").replace("\\", "/")
_TAB_CLOSE_DARK_HOVER = os.path.join(_ASSETS_DIR, f"tab_close_dark_hover.{_EXT}").replace("\\", "/")

_LIGHT_THEME_TEMPLATE = """
/* Global Window and Base Controls */
QMainWindow, QDialog {
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

#symbols_bar {
    background-color: #ffffff;
    border-bottom: 1px solid #e1e8ed;
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
    border-radius: 3px;
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
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
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
    image: url("__TAB_CLOSE_LIGHT__");
    subcontrol-position: right;
    margin-left: 6px;
    padding: 2px;
}

QTabBar::close-button:hover {
    image: url("__TAB_CLOSE_LIGHT_HOVER__");
    background-color: #fee2e2;
    border-radius: 3px;
}

QTabBar::close-button:pressed {
    background-color: #fecaca;
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

/* Combo Boxes / Select */
QComboBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 10px;
    min-height: 24px;
}
QComboBox:hover {
    border-color: #94a3b8;
    background-color: #f8fafc;
}
QComboBox:focus {
    border-color: #3b82f6;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #e2e8f0;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: #f8fafc;
}
QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #64748b;
    margin-right: 6px;
}
QComboBox::down-arrow:hover {
    border-top-color: #1e293b;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    selection-background-color: #e0e7ff;
    selection-color: #1d4ed8;
    outline: none;
    padding: 4px;
}

/* Radio Buttons */
QRadioButton {
    color: #1e293b;
    spacing: 8px;
    font-size: 11pt;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #94a3b8;
    background-color: #ffffff;
}
QRadioButton::indicator:hover {
    border-color: #3b82f6;
}
QRadioButton::indicator:checked {
    border: 5px solid #3b82f6;
    background-color: #ffffff;
}

/* Check Boxes */
QCheckBox {
    color: #1e293b;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #94a3b8;
    background-color: #ffffff;
}
QCheckBox::indicator:hover {
    border-color: #3b82f6;
}
QCheckBox::indicator:checked {
    border-color: #3b82f6;
    background-color: #3b82f6;
}

/* Spin Boxes */
QSpinBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 4px 8px;
}
QSpinBox:hover {
    border-color: #94a3b8;
}
QSpinBox:focus {
    border-color: #3b82f6;
}

/* List & Tree Widgets */
QListWidget, QTreeWidget, QTreeView {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    outline: none;
    show-decoration-selected: 0;
}

QListWidget::item, QTreeWidget::item, QTreeView::item {
    padding: 5px 8px;
    border-radius: 4px;
    color: #1e293b;
    border: none;
    outline: none;
}

QListWidget::item:hover, QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #f1f5f9;
    border: none;
    outline: none;
}

QListWidget::item:selected, QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #e2e8f0;
    color: #0f172a;
    border: none;
    outline: none;
}

QListWidget::item:focus, QTreeWidget::item:focus, QTreeView::item:focus {
    border: none;
    outline: none;
}

QTreeWidget::branch {
    background: transparent;
    border: none;
    outline: none;
}

QTreeWidget::branch:selected {
    background: transparent;
    border: none;
    outline: none;
}

/* Scrollbars - Light Theme */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::handle:vertical:pressed {
    background-color: #64748b;
}

QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #94a3b8;
}

QScrollBar::handle:horizontal:pressed {
    background-color: #64748b;
}

QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}

QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    background: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

_DARK_THEME_TEMPLATE = """
/* Global Window and Base Controls */
QMainWindow, QDialog {
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

#symbols_bar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
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
    border-radius: 3px;
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
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
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
    image: url("__TAB_CLOSE_DARK__");
    subcontrol-position: right;
    margin-left: 6px;
    padding: 2px;
}

QTabBar::close-button:hover {
    image: url("__TAB_CLOSE_DARK_HOVER__");
    background-color: #313244;
    border-radius: 3px;
}

QTabBar::close-button:pressed {
    background-color: #45475a;
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

/* Combo Boxes / Select */
QComboBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px 10px;
    min-height: 24px;
}
QComboBox:hover {
    border-color: #45475a;
    background-color: #1e1e2e;
}
QComboBox:focus {
    border-color: #89b4fa;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #313244;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: #1e1e2e;
}
QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a6adc8;
    margin-right: 6px;
}
QComboBox::down-arrow:hover {
    border-top-color: #cdd6f4;
}
QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    selection-background-color: #313244;
    selection-color: #89b4fa;
    outline: none;
    padding: 4px;
}

/* Radio Buttons */
QRadioButton {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 11pt;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #45475a;
    background-color: #181825;
}
QRadioButton::indicator:hover {
    border-color: #89b4fa;
}
QRadioButton::indicator:checked {
    border: 5px solid #89b4fa;
    background-color: #181825;
}

/* Check Boxes */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #181825;
}
QCheckBox::indicator:hover {
    border-color: #89b4fa;
}
QCheckBox::indicator:checked {
    border-color: #89b4fa;
    background-color: #89b4fa;
}

/* Spin Boxes */
QSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 4px 8px;
}
QSpinBox:hover {
    border-color: #45475a;
}
QSpinBox:focus {
    border-color: #89b4fa;
}

/* List & Tree Widgets */
QListWidget, QTreeWidget, QTreeView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
    show-decoration-selected: 0;
}

QListWidget::item, QTreeWidget::item, QTreeView::item {
    padding: 5px 8px;
    border-radius: 4px;
    color: #cdd6f4;
    border: none;
    outline: none;
}

QListWidget::item:hover, QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #313244;
    border: none;
    outline: none;
}

QListWidget::item:selected, QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #45475a;
    color: #ffffff;
    border: none;
    outline: none;
}

QListWidget::item:focus, QTreeWidget::item:focus, QTreeView::item:focus {
    border: none;
    outline: none;
}

QTreeWidget::branch {
    background: transparent;
    border: none;
    outline: none;
}

QTreeWidget::branch:selected {
    background: transparent;
    border: none;
    outline: none;
}

/* Line Edits */
QLineEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 4px;
    padding: 4px 6px;
}

/* Scrollbars - Dark Theme (Catppuccin Mocha) */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::handle:vertical:pressed {
    background-color: #6c7086;
}

QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}

QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QScrollBar::handle:horizontal:pressed {
    background-color: #6c7086;
}

QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}

QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    background: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}
"""

LIGHT_THEME = (
    _LIGHT_THEME_TEMPLATE.replace("__TAB_CLOSE_LIGHT__", _TAB_CLOSE_LIGHT)
    .replace("__TAB_CLOSE_LIGHT_HOVER__", _TAB_CLOSE_LIGHT_HOVER)
)

DARK_THEME = (
    _DARK_THEME_TEMPLATE.replace("__TAB_CLOSE_DARK__", _TAB_CLOSE_DARK)
    .replace("__TAB_CLOSE_DARK_HOVER__", _TAB_CLOSE_DARK_HOVER)
)

from ui.theme_utils import (
    detect_system_dark_mode,
    create_dark_palette,
    create_light_palette,
    apply_os_window_theme,
    SystemThemeWatcher,
    get_system_theme_watcher,
)
