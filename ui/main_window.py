"""
Main Application Window (Algoo - Modern IDE for Algorithmic Development).
Developed by softsurgery (https://github.com/softsurgery/algoo).
Built with PyQt5 and modern design standards.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QToolBar, QAction, QFileDialog, QMessageBox,
    QStatusBar, QLabel, QMenu, QToolButton, QApplication, QDialog
)
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QDesktopServices
from PyQt5.QtCore import Qt, QFileInfo, QUrl, QSettings

from compiler.transpiler import AlgoTranspiler, CompileError
from ui.editor import AlgoCodeEditor
from ui.console import AlgoConsole
from ui.python_view import PythonView
from ui.tdo_view import TDOView
from ui.tdnt_view import TDNTView
from ui.assistant_view import AssistantView
from ui.symbols_bar import SymbolsBar
from ui.icons import create_icon
from ui.styles import (
    LIGHT_THEME, DARK_THEME,
    detect_system_dark_mode, apply_os_window_theme
)
from ui.insert_code_dialog import InsertCodeDialog
from database import get_database, DatabaseManager
from typing import Optional


class MainWindow(QMainWindow):
    def __init__(self, db: Optional[DatabaseManager] = None):
        super().__init__()
        self.setWindowTitle("Algoo - IDE Algorithmique")
        self.resize(1200, 800)

        # Database initialization & theme preference
        self.db = db or get_database()
        self.settings = QSettings("softsurgery", "Algoo")

        saved_dark = self.db.is_dark_mode()
        if saved_dark is not None:
            self.is_dark_mode = saved_dark
        elif self.settings.contains("dark_mode"):
            self.is_dark_mode = self.settings.value("dark_mode", type=bool)
            self.db.set_dark_mode(self.is_dark_mode)
        else:
            self.is_dark_mode = detect_system_dark_mode()
            self.db.set_dark_mode(self.is_dark_mode)

        self.transpiler = AlgoTranspiler()

        self._setup_ui()
        self._setup_toolbar()
        self._setup_menus()
        self._setup_statusbar()
        self.apply_theme(recreate_native=False)

        # Restore latest opened files or open starter default example
        self._restore_opened_files()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Quick algorithmic symbols bar
        self.symbols_bar = SymbolsBar(self, is_dark=self.is_dark_mode)
        self.symbols_bar.setObjectName("symbols_bar")
        self.symbols_bar.insert_requested.connect(self._on_insert_symbol)
        main_layout.addWidget(self.symbols_bar)

        # 2. Main Horizontal Splitter (Editor + Console on left, Side panels on right)
        self.h_splitter = QSplitter(Qt.Horizontal)

        # Left Vertical Splitter (Editor tabs on top, Console on bottom)
        self.v_splitter = QSplitter(Qt.Vertical)

        # Multi-tab code editor
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setFont(QFont("SansSerif", 10))
        self.tab_widget.tabCloseRequested.connect(self._on_close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        self.v_splitter.addWidget(self.tab_widget)

        # Interactive Console
        self.console = AlgoConsole(self, is_dark=self.is_dark_mode)
        self.console.error_line_clicked.connect(self._on_error_line_clicked)
        self.v_splitter.addWidget(self.console)

        # Set vertical split proportions (65% editor, 35% console)
        self.v_splitter.setStretchFactor(0, 65)
        self.v_splitter.setStretchFactor(1, 35)

        self.h_splitter.addWidget(self.v_splitter)

        # Right Side Panel (Thonny style side tabs)
        self.side_tabs = QTabWidget()
        self.side_tabs.setTabPosition(QTabWidget.North)

        # 1. Python Code View
        self.python_view = PythonView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.python_view, "Code Python")

        # 2. TDO View (Separate TDOG and TDOL tables)
        self.tdo_view = TDOView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.tdo_view, "Tableau T.D.O.")

        # 3. TDNT View
        self.tdnt_view = TDNTView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.tdnt_view, "Tableau T.D.N.T.")

        # 4. Guide & Assistant View
        self.assistant_view = AssistantView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.assistant_view, "Guide et Aide")

        self.side_tabs.currentChanged.connect(self._on_side_tab_changed)

        self.h_splitter.addWidget(self.side_tabs)

        # Proportions: 62% left work area, 38% right panels
        self.h_splitter.setStretchFactor(0, 62)
        self.h_splitter.setStretchFactor(1, 38)

        main_layout.addWidget(self.h_splitter, 1)

    def _setup_toolbar(self):
        self.toolbar = QToolBar("Barre d'outils principale", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(self.toolbar.iconSize())
        self.addToolBar(self.toolbar)

        # New file
        self.act_new = QAction(create_icon("new"), "Nouveau", self)
        self.act_new.setShortcut(QKeySequence.New)
        self.act_new.setToolTip("Nouveau fichier algorithmique (Ctrl+N)")
        self.act_new.triggered.connect(lambda checked=False: self.new_file())
        self.toolbar.addAction(self.act_new)

        # Open file
        self.act_open = QAction(create_icon("open"), "Ouvrir", self)
        self.act_open.setShortcut(QKeySequence.Open)
        self.act_open.setToolTip("Ouvrir un fichier algorithmique (Ctrl+O)")
        self.act_open.triggered.connect(self.open_file)
        self.toolbar.addAction(self.act_open)

        # Save file
        self.act_save = QAction(create_icon("save"), "Enregistrer", self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.setToolTip("Enregistrer le fichier actuel (Ctrl+S)")
        self.act_save.triggered.connect(self.save_file)
        self.toolbar.addAction(self.act_save)

        self.toolbar.addSeparator()

        # Run action (F5) - Prominent green button
        self.act_run = QAction(create_icon("run"), "Exécuter", self)
        self.act_run.setShortcut(Qt.Key_F5)
        self.act_run.setToolTip("Exécuter l'algorithme (F5)")
        self.act_run.triggered.connect(self.run_algorithm)
        self.toolbar.addAction(self.act_run)

        # Set specific object name for styling
        run_btn = self.toolbar.widgetForAction(self.act_run)
        if run_btn:
            run_btn.setObjectName("btn_run")

        # Compile / Translate to Python (F6)
        self.act_translate = QAction(create_icon("python"), "Traduire en Python", self)
        self.act_translate.setShortcut(Qt.Key_F6)
        self.act_translate.setToolTip("Traduire en code Python sans exécuter (F6)")
        self.act_translate.triggered.connect(self.translate_to_python)
        self.toolbar.addAction(self.act_translate)

        py_btn = self.toolbar.widgetForAction(self.act_translate)
        if py_btn:
            py_btn.setObjectName("btn_python")

        # Stop action
        self.act_stop = QAction(create_icon("stop"), "Arrêter", self)
        self.act_stop.setShortcut(Qt.Key_Escape)
        self.act_stop.setToolTip("Arrêter l'exécution du programme (Échap)")
        self.act_stop.triggered.connect(self.stop_execution)
        self.toolbar.addAction(self.act_stop)

        stop_btn = self.toolbar.widgetForAction(self.act_stop)
        if stop_btn:
            stop_btn.setObjectName("btn_stop")

        self.toolbar.addSeparator()

        # Zoom in/out for Editor & Console
        self.act_zoom_out = QAction(create_icon("zoom_out"), "Zoom arrière\tCtrl -", self)
        self.act_zoom_out.setShortcut(QKeySequence.ZoomOut)
        self.act_zoom_out.setToolTip("Zoom arrière (Ctrl - ou Ctrl + Molette bas)")
        self.act_zoom_out.triggered.connect(self.zoom_out)
        self.toolbar.addAction(self.act_zoom_out)

        self.act_zoom_in = QAction(create_icon("zoom_in"), "Zoom avant\tCtrl +", self)
        self.act_zoom_in.setShortcuts([QKeySequence.ZoomIn, QKeySequence("Ctrl+=")])
        self.act_zoom_in.setToolTip("Zoom avant (Ctrl + ou Ctrl + Molette haut)")
        self.act_zoom_in.triggered.connect(self.zoom_in)
        self.toolbar.addAction(self.act_zoom_in)

        # Spacer to push theme button to right
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Expanding, spacer.sizePolicy().Preferred)
        self.toolbar.addWidget(spacer)

        # Theme toggle button
        self.act_theme = QAction(create_icon("theme"), "Thème", self)
        self.act_theme.setToolTip("Basculer entre le thème clair et le thème sombre")
        self.act_theme.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.act_theme)

    def _setup_menus(self):
        menubar = self.menuBar()

        # Fichier
        menu_file = menubar.addMenu("&Fichier")
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_open)

        # Fichiers récents
        self.menu_recent = menu_file.addMenu("Fichiers récents")
        self._populate_recent_files_menu()

        menu_file.addAction(self.act_save)
        
        act_save_as = QAction("Enregistrer sous...", self)
        act_save_as.setShortcut(QKeySequence.SaveAs)
        act_save_as.triggered.connect(self.save_file_as)
        menu_file.addAction(act_save_as)
        menu_file.addSeparator()

        # Exemples sub-menu
        menu_ex = menu_file.addMenu("Exemples d'algorithmes")
        self._populate_examples_menu(menu_ex)
        menu_file.addSeparator()

        act_exit = QAction("Quitter", self)
        act_exit.setShortcut(QKeySequence.Quit)
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        # Édition
        menu_edit = menubar.addMenu("&Édition")
        act_undo = QAction("Annuler", self)
        act_undo.setShortcut(QKeySequence.Undo)
        act_undo.triggered.connect(lambda: self.current_editor().undo() if self.current_editor() else None)
        menu_edit.addAction(act_undo)

        act_redo = QAction("Rétablir", self)
        act_redo.setShortcut(QKeySequence.Redo)
        act_redo.triggered.connect(lambda: self.current_editor().redo() if self.current_editor() else None)
        menu_edit.addAction(act_redo)
        menu_edit.addSeparator()

        act_cut = QAction("Couper", self)
        act_cut.setShortcut(QKeySequence.Cut)
        act_cut.triggered.connect(lambda: self.current_editor().cut() if self.current_editor() else None)
        menu_edit.addAction(act_cut)

        act_copy = QAction("Copier", self)
        act_copy.setShortcut(QKeySequence.Copy)
        act_copy.triggered.connect(lambda: self.current_editor().copy() if self.current_editor() else None)
        menu_edit.addAction(act_copy)

        act_paste = QAction("Coller", self)
        act_paste.setShortcut(QKeySequence.Paste)
        act_paste.triggered.connect(lambda: self.current_editor().paste() if self.current_editor() else None)
        menu_edit.addAction(act_paste)
        menu_edit.addSeparator()

        act_comment = QAction("Commenter / Décommenter\tCtrl+/", self)
        act_comment.setShortcut(QKeySequence("Ctrl+/"))
        act_comment.setToolTip("Commenter ou décommenter la ligne actuelle (Ctrl+/)")
        act_comment.triggered.connect(lambda: self.current_editor().toggle_comment() if self.current_editor() else None)
        menu_edit.addAction(act_comment)

        # Exécuter
        menu_run = menubar.addMenu("&Exécuter")
        menu_run.addAction(self.act_run)
        menu_run.addAction(self.act_translate)
        menu_run.addAction(self.act_stop)
        menu_run.addSeparator()

        act_clear = QAction("Effacer la console", self)
        act_clear.triggered.connect(self.console.clear_console)
        menu_run.addAction(act_clear)

        # Affichage
        menu_view = menubar.addMenu("&Affichage")
        act_show_py = QAction("Code Python", self)
        act_show_py.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.python_view))
        menu_view.addAction(act_show_py)

        act_show_tdo = QAction("Tableau T.D.O.", self)
        act_show_tdo.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.tdo_view))
        menu_view.addAction(act_show_tdo)

        act_show_tdnt = QAction("Tableau T.D.N.T.", self)
        act_show_tdnt.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.tdnt_view))
        menu_view.addAction(act_show_tdnt)

        act_show_guide = QAction("Guide et Aide", self)
        act_show_guide.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.assistant_view))
        menu_view.addAction(act_show_guide)
        menu_view.addSeparator()

        menu_view.addAction(self.act_zoom_in)
        menu_view.addAction(self.act_zoom_out)
        act_zoom_reset = QAction("Réinitialiser le zoom\tCtrl 0", self)
        act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_zoom_reset.triggered.connect(self.reset_zoom)
        menu_view.addAction(act_zoom_reset)
        menu_view.addSeparator()

        menu_view.addAction(self.act_theme)

        # Tools
        menu_tools = menubar.addMenu("&Tools")
        act_insert_code = QAction("Insert Code...", self)
        act_insert_code.setIcon(create_icon("open"))
        act_insert_code.setShortcut(QKeySequence("Ctrl+I"))
        act_insert_code.setToolTip("Ouvrir la boîte de dialogue pour choisir et insérer un code (Ctrl+I)")
        act_insert_code.triggered.connect(self.show_insert_code_dialog)
        menu_tools.addAction(act_insert_code)

        # Aide
        menu_help = menubar.addMenu("&Aide")
        act_github = QAction("Dépôt GitHub (softsurgery/algoo)", self)
        act_github.setToolTip("Ouvrir la page GitHub du projet Algoo")
        act_github.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/softsurgery/algoo")))
        menu_help.addAction(act_github)
        menu_help.addSeparator()

        act_about = QAction("À propos d'Algoo", self)
        act_about.triggered.connect(self._show_about_dialog)
        menu_help.addAction(act_about)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.lbl_cursor = QLabel("Ligne: 1, Col: 1")
        self.lbl_status = QLabel("Prêt")
        self.lbl_backend = QLabel("Algorithmique | Python 3 + NumPy")

        self.status_bar.addWidget(self.lbl_status, 1)
        self.status_bar.addPermanentWidget(self.lbl_cursor)
        self.status_bar.addPermanentWidget(self.lbl_backend)

    def _populate_examples_menu(self, menu: QMenu):
        menu.clear()
        act_browse = QAction("Choisir dans la liste (Insert Code)...", self)
        act_browse.setIcon(create_icon("open"))
        act_browse.triggered.connect(self.show_insert_code_dialog)
        menu.addAction(act_browse)
        menu.addSeparator()

        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        if os.path.exists(examples_dir):
            for fname in sorted(os.listdir(examples_dir)):
                if fname.endswith(".algo"):
                    label = fname.replace(".algo", "").replace("_", " ").title()
                    filepath = os.path.join(examples_dir, fname)
                    act = QAction(label, self)
                    act.triggered.connect(lambda _, p=filepath: self.load_file(p))
                    menu.addAction(act)

    def show_insert_code_dialog(self):
        """Displays the code selection and insertion dialog."""
        dlg = InsertCodeDialog(self, is_dark=self.is_dark_mode)
        if dlg.exec_() == QDialog.Accepted and dlg.selected_code:
            if dlg.action_mode == 'new_tab':
                self.new_file(dlg.selected_title, dlg.selected_code)
                self.lbl_status.setText(f"Exemple ouvert dans un nouvel onglet : {dlg.selected_title}")
            else:
                editor = self.current_editor()
                if not editor:
                    self.new_file(dlg.selected_title, dlg.selected_code)
                else:
                    if not editor.toPlainText().strip():
                        editor.setPlainText(dlg.selected_code)
                    else:
                        cursor = editor.textCursor()
                        cursor.insertText(dlg.selected_code)
                        editor.setTextCursor(cursor)
                self.lbl_status.setText(f"Code inséré : {dlg.selected_title}")

    def _is_console_focused(self) -> bool:
        focus_w = self.focusWidget() or QApplication.focusWidget()
        if not focus_w:
            return False
        w = focus_w
        while w:
            if w is self.console:
                return True
            w = w.parentWidget()
        return False

    def zoom_in(self):
        if self._is_console_focused():
            self.console.zoom_in()
        else:
            editor = self.current_editor()
            if editor:
                editor.zoom_in()
            self.python_view.zoom_in()

    def zoom_out(self):
        if self._is_console_focused():
            self.console.zoom_out()
        else:
            editor = self.current_editor()
            if editor:
                editor.zoom_out()
            self.python_view.zoom_out()

    def reset_zoom(self):
        if self._is_console_focused():
            self.console.reset_zoom()
        else:
            editor = self.current_editor()
            if editor:
                editor.reset_zoom()
            self.python_view.reset_zoom()

    def apply_theme(self, recreate_native: bool = False):
        if self.is_dark_mode:
            theme_qss = DARK_THEME
            color_hex = "#cdd6f4"
        else:
            theme_qss = LIGHT_THEME
            color_hex = "#2c3e50"

        app = QApplication.instance()
        if app:
            app.setStyleSheet(theme_qss)
        self.setStyleSheet(theme_qss)

        # Apply dark/light colors to OS window frame and title bar
        apply_os_window_theme(self, self.is_dark_mode)

        # Update icons
        self.act_new.setIcon(create_icon("new", color_hex))
        self.act_open.setIcon(create_icon("open", color_hex))
        self.act_save.setIcon(create_icon("save", color_hex))
        self.act_zoom_in.setIcon(create_icon("zoom_in", color_hex))
        self.act_zoom_out.setIcon(create_icon("zoom_out", color_hex))
        self.act_theme.setIcon(create_icon("theme", color_hex))

        # Propagate to sub-widgets
        if hasattr(self, "symbols_bar"):
            self.symbols_bar.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "console"):
            self.console.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "python_view"):
            self.python_view.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "tdo_view"):
            self.tdo_view.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "tdnt_view"):
            self.tdnt_view.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "assistant_view"):
            self.assistant_view.set_dark_mode(self.is_dark_mode)

        # Propagate to all open editors
        if hasattr(self, "tab_widget"):
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if isinstance(editor, AlgoCodeEditor):
                    editor.set_dark_mode(self.is_dark_mode)

        # On Wayland (e.g. GNOME Wayland), client-side decorations (Bradient/QtWayland)
        # determine their colors upon window handle instantiation. Recreating the native
        # window handle on runtime toggle immediately applies the new palette to the title bar.
        if recreate_native and self.isVisible():
            app = QApplication.instance()
            if app and app.platformName().startswith("wayland"):
                save_geom = self.saveGeometry()
                state = self.windowState()
                self.destroy()
                self.create()
                self.restoreGeometry(save_geom)
                self.setWindowState(state)
                self.show()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if hasattr(self, "db") and self.db:
            self.db.set_dark_mode(self.is_dark_mode)
        if hasattr(self, "settings"):
            self.settings.setValue("dark_mode", self.is_dark_mode)
        self.apply_theme(recreate_native=True)
        mode_str = "sombre" if self.is_dark_mode else "clair"
        self.lbl_status.setText(f"Thème {mode_str} activé")

    # -------------------------------------------------------------------------
    # Editor & Tabs Management
    # -------------------------------------------------------------------------
    def current_editor(self) -> AlgoCodeEditor:
        w = self.tab_widget.currentWidget()
        if isinstance(w, AlgoCodeEditor):
            return w
        return None

    def new_file(self, title: str = "Nouveau Script", content: str = ""):
        if isinstance(title, bool) or not title:
            title = "Nouveau Script"
        editor = AlgoCodeEditor(self, is_dark=self.is_dark_mode)
        
        default_content = content or (
            "ALGORITHME MonAlgorithme\n"
            "DEBUT\n"
            "  Ecrire_nl(\"Bonjour le monde !\")\n"
            "FIN\n"
            "Tableau de déclaration des objets globaux\n"
            "Objet          Type / Nature\n"
        )
        editor.setPlainText(default_content)
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        editor.textChanged.connect(self._on_editor_text_changed)

        idx = self.tab_widget.addTab(editor, f" {title} ")
        self.tab_widget.setCurrentIndex(idx)
        editor.setProperty("file_path", None)
        editor.setProperty("is_dirty", False)
        self._update_window_title()
        return editor

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un algorithme", "",
            "Fichiers Algorithme (*.algo *.alg *.txt);;Tous les fichiers (*.*)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str, record: bool = True):
        # Check if already open
        norm_target = os.path.abspath(path)
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            ed_path = ed.property("file_path")
            if ed_path and os.path.abspath(ed_path) == norm_target:
                self.tab_widget.setCurrentIndex(i)
                if record and hasattr(self, "db") and self.db:
                    self.db.record_file_opened(norm_target, is_open=True, is_active=True, tab_order=i)
                    self._populate_recent_files_menu()
                return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()

        filename = os.path.basename(path)
        editor = self.new_file(filename, content)
        editor.setProperty("file_path", norm_target)
        editor.setProperty("is_dirty", False)
        self.lbl_status.setText(f"Fichier ouvert : {filename}")
        self.update_inspectors(content)

        if record and hasattr(self, "db") and self.db:
            idx = self.tab_widget.currentIndex()
            self.db.record_file_opened(norm_target, is_open=True, is_active=True, tab_order=idx)
            self._sync_tabs_to_db()
            self._populate_recent_files_menu()

    def save_file(self) -> bool:
        editor = self.current_editor()
        if not editor:
            return False

        path = editor.property("file_path")
        if not path:
            return self.save_file_as()

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            editor.setProperty("is_dirty", False)
            idx = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(idx, f" {os.path.basename(path)} ")
            self._update_window_title()
            self.lbl_status.setText(f"Enregistré : {os.path.basename(path)}")
            if hasattr(self, "db") and self.db:
                norm_path = os.path.abspath(path)
                editor.setProperty("file_path", norm_path)
                self.db.record_file_opened(norm_path, is_open=True, is_active=True, tab_order=idx)
                self._sync_tabs_to_db()
                self._populate_recent_files_menu()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'enregistrement", str(e))
            return False

    def save_file_as(self) -> bool:
        editor = self.current_editor()
        if not editor:
            return False

        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", "algorithme.algo",
            "Fichiers Algorithme (*.algo);;Tous les fichiers (*.*)"
        )
        if path:
            editor.setProperty("file_path", os.path.abspath(path))
            return self.save_file()
        return False

    def _on_close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if editor.property("is_dirty"):
            fname = self.tab_widget.tabText(index).replace("*", "").strip()
            res = QMessageBox.question(
                self, "Modifications non enregistrées",
                f"Voulez-vous enregistrer les modifications apportées à '{fname}' ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if res == QMessageBox.Save:
                self.tab_widget.setCurrentIndex(index)
                if not self.save_file():
                    return
            elif res == QMessageBox.Cancel:
                return

        file_path = editor.property("file_path")
        if file_path and hasattr(self, "db") and self.db:
            self.db.record_file_closed(file_path)

        self.tab_widget.removeTab(index)
        self._sync_tabs_to_db()
        self._populate_recent_files_menu()

        if self.tab_widget.count() == 0:
            self.new_file()
        else:
            self._update_window_title()

    def _update_window_title(self):
        idx = self.tab_widget.currentIndex()
        if idx >= 0:
            tab_text = self.tab_widget.tabText(idx).strip()
            self.setWindowTitle(f"{tab_text} — Algoo - IDE Algorithmique")
        else:
            self.setWindowTitle("Algoo - IDE Algorithmique")

    def _on_tab_changed(self, index):
        self._on_cursor_position_changed()
        self._update_window_title()
        self.update_inspectors()
        if hasattr(self, "db") and self.db:
            editor = self.current_editor()
            if editor and editor.property("file_path"):
                self.db.set_active_file(editor.property("file_path"))

    def _on_side_tab_changed(self, index):
        cur = self.side_tabs.widget(index)
        if cur in (getattr(self, "tdo_view", None),
                   getattr(self, "tdnt_view", None)):
            self.update_inspectors()

    def _on_cursor_position_changed(self):
        editor = self.current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.lbl_cursor.setText(f"Ligne: {line}, Col: {col}")

    def _on_editor_text_changed(self):
        editor = self.current_editor()
        if editor:
            editor.setProperty("is_dirty", True)
            idx = self.tab_widget.currentIndex()
            title = self.tab_widget.tabText(idx)
            if not title.endswith("*"):
                self.tab_widget.setTabText(idx, title + "*")
            self._update_window_title()

    def _on_insert_symbol(self, text: str):
        editor = self.current_editor()
        if editor:
            editor.insertPlainText(text)
            editor.setFocus()

    def _sync_tabs_to_db(self):
        """Synchronizes open tabs and their active state to the SQLite database."""
        if not hasattr(self, "db") or not self.db:
            return
        tabs = []
        current_idx = self.tab_widget.currentIndex()
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if isinstance(ed, AlgoCodeEditor):
                p = ed.property("file_path")
                if p:
                    tabs.append({
                        "file_path": p,
                        "tab_order": i,
                        "is_active": (i == current_idx)
                    })
        self.db.sync_open_tabs(tabs)

    def _populate_recent_files_menu(self):
        """Populates the recent files submenu from the SQLite database."""
        if not hasattr(self, "menu_recent") or not hasattr(self, "db") or not self.db:
            return
        self.menu_recent.clear()

        act_open_latest = QAction("Ouvrir les derniers fichiers ouverts", self)
        act_open_latest.setToolTip("Rouvrir les fichiers récemment ouverts")
        act_open_latest.triggered.connect(lambda: self.open_latest_opened_files(5))
        self.menu_recent.addAction(act_open_latest)
        self.menu_recent.addSeparator()

        recent_files = self.db.get_latest_opened_files(limit=10)
        valid_files = [f for f in recent_files if os.path.exists(f)]

        if valid_files:
            for path in valid_files:
                fname = os.path.basename(path)
                act = QAction(fname, self)
                act.setToolTip(path)
                act.triggered.connect(lambda _, p=path: self.load_file(p))
                self.menu_recent.addAction(act)

            self.menu_recent.addSeparator()
            act_clear = QAction("Effacer l'historique", self)
            act_clear.triggered.connect(self._clear_recent_files_history)
            self.menu_recent.addAction(act_clear)
        else:
            act_empty = QAction("(Aucun fichier récent)", self)
            act_empty.setEnabled(False)
            self.menu_recent.addAction(act_empty)

    def _clear_recent_files_history(self):
        """Clears recent file history in SQLite database."""
        if hasattr(self, "db") and self.db:
            self.db.clear_recent_files()
            self._populate_recent_files_menu()
            self.lbl_status.setText("Historique des fichiers récents effacé")

    def open_latest_opened_files(self, limit: int = 5):
        """Opens the most recently opened files from SQLite database."""
        if not hasattr(self, "db") or not self.db:
            return
        latest_files = self.db.get_latest_opened_files(limit=limit)
        opened_count = 0
        for path in latest_files:
            if os.path.exists(path):
                self.load_file(path)
                opened_count += 1
        if opened_count > 0:
            self.lbl_status.setText(f"{opened_count} fichier(s) récent(s) ouvert(s)")
        else:
            self.lbl_status.setText("Aucun fichier récent à ouvrir")

    def _restore_opened_files(self):
        """Restores previously open tabs from SQLite database or latest opened files."""
        opened_any = False
        target_tab_index = 0

        if hasattr(self, "db") and self.db:
            open_files = self.db.get_open_files()
            active_file = self.db.get_active_file()

            if open_files:
                for path in open_files:
                    if os.path.exists(path):
                        self.load_file(path, record=False)
                        opened_any = True
                        if active_file and os.path.abspath(path) == os.path.abspath(active_file):
                            target_tab_index = self.tab_widget.count() - 1

                if opened_any and self.tab_widget.count() > 0:
                    self.tab_widget.setCurrentIndex(target_tab_index)

            # If no open tabs were restored, open the latest opened file
            if not opened_any:
                latest_files = self.db.get_latest_opened_files(limit=1)
                for path in latest_files:
                    if os.path.exists(path):
                        self.load_file(path, record=True)
                        opened_any = True
                        break

        # If nothing could be restored, fall back to default example
        if not opened_any:
            self._open_default_example()
        else:
            self._sync_tabs_to_db()
            self._populate_recent_files_menu()

    def closeEvent(self, event):
        """Handles window closing: prompts for unsaved changes and saves session to DB."""
        if self.isVisible():
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if editor and editor.property("is_dirty"):
                    fname = self.tab_widget.tabText(i).replace("*", "").strip()
                    res = QMessageBox.question(
                        self, "Modifications non enregistrées",
                        f"Voulez-vous enregistrer les modifications apportées à '{fname}' ?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                        QMessageBox.Cancel
                    )
                    if res == QMessageBox.Save:
                        self.tab_widget.setCurrentIndex(i)
                        if not self.save_file():
                            event.ignore()
                            return
                    elif res == QMessageBox.Cancel:
                        event.ignore()
                        return

        self._sync_tabs_to_db()
        event.accept()
        super().closeEvent(event)

    def _open_default_example(self):
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "somme_diviseurs.algo"
        )
        if os.path.exists(example_path):
            self.load_file(example_path)
        else:
            self.new_file()

    def update_inspectors(self, algo_code: str = None):
        """Extracts and populates Variables, TDO, and TDNT views with all symbols."""
        if algo_code is None:
            editor = self.current_editor()
            if not editor:
                return
            algo_code = editor.toPlainText()

        symbols = self.transpiler.extract_symbols(algo_code)
        if hasattr(self, "tdo_view"):
            self.tdo_view.update_tdo(symbols.get('tdo_tables', []))
        if hasattr(self, "tdnt_view"):
            self.tdnt_view.update_tdnt(symbols.get('custom_types', {}))

    # -------------------------------------------------------------------------
    # Compilation and Execution
    # -------------------------------------------------------------------------
    def translate_to_python(self) -> str:
        """Translates current algorithm code to Python and updates views."""
        editor = self.current_editor()
        if not editor:
            return ""

        editor.set_error_line(None)
        algo_code = editor.toPlainText()

        # Update inspectors immediately
        self.update_inspectors(algo_code)

        try:
            py_code = self.transpiler.compile(algo_code)
            self.python_view.set_python_code(py_code)

            self.side_tabs.setCurrentWidget(self.python_view)
            self.lbl_status.setText("Traduction Python terminée avec succès")
            return py_code
        except Exception as e:
            self.lbl_status.setText("Erreur de compilation")
            line_no = getattr(e, 'line_num', None)
            if line_no and editor:
                editor.set_error_line(line_no)
            self.assistant_view.show_error_advice(str(e), line_no=line_no)
            self.side_tabs.setCurrentWidget(self.assistant_view)
            QMessageBox.warning(self, "Erreur de compilation", str(e))
            return ""

    def run_algorithm(self):
        """Compiles and executes the current algorithm in the shell."""
        editor = self.current_editor()
        if not editor:
            return

        editor.set_error_line(None)
        algo_code = editor.toPlainText()

        # Update inspectors immediately
        self.update_inspectors(algo_code)

        try:
            py_code = self.transpiler.compile(algo_code)
            self.python_view.set_python_code(py_code)

            self.lbl_status.setText("Exécution en cours...")
            self.console.run_python_code(py_code)
        except Exception as e:
            self.lbl_status.setText("Erreur de compilation")
            line_no = getattr(e, 'line_num', None)
            if line_no and editor:
                editor.set_error_line(line_no)
            self.assistant_view.show_error_advice(str(e), line_no=line_no)
            self.side_tabs.setCurrentWidget(self.assistant_view)
            self.console.output_text.append(f"<span style='color: #ef4444; font-weight: bold;'>Erreur de compilation : {e}</span>")

    def stop_execution(self):
        self.console.stop_execution()
        self.lbl_status.setText("Programme arrêté")

    def _on_error_line_clicked(self, line_num: int):
        editor = self.current_editor()
        if editor:
            editor.set_error_line(line_num)

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            "À propos d'Algoo",
            "<h3>Algoo</h3>"
            "<p>Environnement de développement moderne et pédagogique pour l'Algorithmique scolaire et universitaire.</p>"
            "<p><b>Développeur :</b> softsurgery</p>"
            "<p><b>Code source & GitHub :</b> <a href='https://github.com/softsurgery/algoo'>https://github.com/softsurgery/algoo</a></p>"
            "<p>Développé avec <b>PyQt5</b> et <b>NumPy</b> sous Linux.</p>"
        )
