"""
Main Application Window (Thonny-like IDE for Algerian & Tunisian Algorithm Conventions).
Built with PyQt5 and modern design standards.
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QToolBar, QAction, QFileDialog, QMessageBox,
    QStatusBar, QLabel, QMenu, QToolButton, QApplication
)
from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtCore import Qt, QFileInfo

from compiler.transpiler import AlgoTranspiler, CompileError
from ui.editor import AlgoCodeEditor
from ui.console import AlgoConsole
from ui.python_view import PythonView
from ui.variables_view import VariablesView
from ui.tdo_view import TDOView
from ui.assistant_view import AssistantView
from ui.symbols_bar import SymbolsBar
from ui.icons import create_icon
from ui.styles import LIGHT_THEME, DARK_THEME


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thonny Algo-IDE - Conventions Algorithmiques 2024/2025")
        self.resize(1200, 800)

        self.is_dark_mode = False
        self.transpiler = AlgoTranspiler()

        self._setup_ui()
        self._setup_toolbar()
        self._setup_menus()
        self._setup_statusbar()
        self.apply_theme()

        # Open initial starter tab
        self._open_default_example()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Quick algorithmic symbols bar
        self.symbols_bar = SymbolsBar(self, is_dark=self.is_dark_mode)
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

        # 2. Variables View
        self.variables_view = VariablesView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.variables_view, "Variables")

        # 3. TDO View
        self.tdo_view = TDOView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.tdo_view, "Tableau T.D.O.")

        # 4. Assistant & Conventions View
        self.assistant_view = AssistantView(self, is_dark=self.is_dark_mode)
        self.side_tabs.addTab(self.assistant_view, "Guide et Aide")

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
        self.act_new.triggered.connect(self.new_file)
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
        self.act_zoom_out = QAction(create_icon("zoom_out"), "Zoom -", self)
        self.act_zoom_out.setShortcuts([QKeySequence.ZoomOut, QKeySequence("Ctrl+-")])
        self.act_zoom_out.setToolTip("Zoom arrière (Ctrl - ou Ctrl + Molette bas)")
        self.act_zoom_out.triggered.connect(self.zoom_out)
        self.toolbar.addAction(self.act_zoom_out)

        self.act_zoom_in = QAction(create_icon("zoom_in"), "Zoom +", self)
        self.act_zoom_in.setShortcuts([QKeySequence.ZoomIn, QKeySequence("Ctrl+="), QKeySequence("Ctrl++")])
        self.act_zoom_in.setToolTip("Zoom avant (Ctrl + ou Ctrl + Molette haut)")
        self.act_zoom_in.triggered.connect(self.zoom_in)
        self.toolbar.addAction(self.act_zoom_in)

        self.toolbar.addSeparator()

        # Examples menu in toolbar
        self.btn_examples = QToolButton(self)
        self.btn_examples.setText("Exemples Bac")
        self.btn_examples.setPopupMode(QToolButton.InstantPopup)
        self.examples_menu = QMenu(self)
        self._populate_examples_menu(self.examples_menu)
        self.btn_examples.setMenu(self.examples_menu)
        self.toolbar.addWidget(self.btn_examples)

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

        act_show_var = QAction("Variables", self)
        act_show_var.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.variables_view))
        menu_view.addAction(act_show_var)

        act_show_tdo = QAction("Tableau T.D.O.", self)
        act_show_tdo.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.tdo_view))
        menu_view.addAction(act_show_tdo)

        act_show_guide = QAction("Assistant & Conventions", self)
        act_show_guide.triggered.connect(lambda: self.side_tabs.setCurrentWidget(self.assistant_view))
        menu_view.addAction(act_show_guide)
        menu_view.addSeparator()

        menu_view.addAction(self.act_zoom_in)
        menu_view.addAction(self.act_zoom_out)
        act_zoom_reset = QAction("Réinitialiser le zoom", self)
        act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_zoom_reset.triggered.connect(self.reset_zoom)
        menu_view.addAction(act_zoom_reset)
        menu_view.addSeparator()

        menu_view.addAction(self.act_theme)

        # Aide
        menu_help = menubar.addMenu("&Aide")
        act_about = QAction("À propos de Thonny Algo-IDE", self)
        act_about.triggered.connect(self._show_about_dialog)
        menu_help.addAction(act_about)

    def _setup_statusbar(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.lbl_cursor = QLabel("Ligne: 1, Col: 1")
        self.lbl_status = QLabel("Prêt")
        self.lbl_backend = QLabel("Conventions 2024/2025 | Python 3 + NumPy")

        self.status_bar.addWidget(self.lbl_status, 1)
        self.status_bar.addPermanentWidget(self.lbl_cursor)
        self.status_bar.addPermanentWidget(self.lbl_backend)

    def _populate_examples_menu(self, menu: QMenu):
        menu.clear()
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        if os.path.exists(examples_dir):
            for fname in sorted(os.listdir(examples_dir)):
                if fname.endswith(".algo"):
                    label = fname.replace(".algo", "").replace("_", " ").title()
                    filepath = os.path.join(examples_dir, fname)
                    act = QAction(label, self)
                    act.triggered.connect(lambda _, p=filepath: self.load_file(p))
                    menu.addAction(act)

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

    def apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(DARK_THEME)
            color_hex = "#cdd6f4"
        else:
            self.setStyleSheet(LIGHT_THEME)
            color_hex = "#2c3e50"

        # Update icons
        self.act_new.setIcon(create_icon("new", color_hex))
        self.act_open.setIcon(create_icon("open", color_hex))
        self.act_save.setIcon(create_icon("save", color_hex))
        self.act_zoom_in.setIcon(create_icon("zoom_in", color_hex))
        self.act_zoom_out.setIcon(create_icon("zoom_out", color_hex))
        self.act_theme.setIcon(create_icon("theme", color_hex))

        # Propagate to sub-widgets
        self.console.set_dark_mode(self.is_dark_mode)
        self.python_view.set_dark_mode(self.is_dark_mode)
        self.variables_view.set_dark_mode(self.is_dark_mode)
        self.tdo_view.set_dark_mode(self.is_dark_mode)
        self.assistant_view.set_dark_mode(self.is_dark_mode)

        # Propagate to all open editors
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, AlgoCodeEditor):
                editor.set_dark_mode(self.is_dark_mode)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
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

    def new_file(self, title: str = "Sans-titre.algo", content: str = ""):
        editor = AlgoCodeEditor(self, is_dark=self.is_dark_mode)
        
        default_content = content or (
            "ALGORITHME MonAlgorithme\n"
            "DEBUT\n"
            "  Ecrire_nl(\"Bonjour le monde !\")\n"
            "FIN\n"
            "Déclaration des objets\n"
            "Objet          Type / Nature\n"
        )
        editor.setPlainText(default_content)
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
        editor.textChanged.connect(self._on_editor_text_changed)

        idx = self.tab_widget.addTab(editor, f" {title} ")
        self.tab_widget.setCurrentIndex(idx)
        editor.setProperty("file_path", None)
        editor.setProperty("is_dirty", False)
        return editor

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un algorithme", "",
            "Fichiers Algorithme (*.algo *.alg *.txt);;Tous les fichiers (*.*)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str):
        # Check if already open
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if ed.property("file_path") == path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()

        filename = os.path.basename(path)
        editor = self.new_file(filename, content)
        editor.setProperty("file_path", path)
        editor.setProperty("is_dirty", False)
        self.lbl_status.setText(f"Fichier ouvert : {filename}")

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
            self.lbl_status.setText(f"Enregistré : {os.path.basename(path)}")
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
            editor.setProperty("file_path", path)
            return self.save_file()
        return False

    def _on_close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if editor.property("is_dirty"):
            fname = self.tab_widget.tabText(index).replace("*", "")
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

        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.new_file()

    def _on_tab_changed(self, index):
        self._on_cursor_position_changed()

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

    def _on_insert_symbol(self, text: str):
        editor = self.current_editor()
        if editor:
            editor.insertPlainText(text)
            editor.setFocus()

    def _open_default_example(self):
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples", "somme_diviseurs.algo"
        )
        if os.path.exists(example_path):
            self.load_file(example_path)
        else:
            self.new_file()

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

        try:
            py_code = self.transpiler.compile(algo_code)
            self.python_view.set_python_code(py_code)

            # Update declared objects in TDO and Variables views
            self.tdo_view.update_tdo(self.transpiler.declared_objects)
            self.variables_view.update_declared_variables(self.transpiler.declared_objects)

            self.side_tabs.setCurrentWidget(self.python_view)
            self.lbl_status.setText("Traduction Python terminée avec succès")
            return py_code
        except Exception as e:
            self.lbl_status.setText("Erreur de compilation")
            self.assistant_view.show_error_advice(str(e))
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

        try:
            py_code = self.transpiler.compile(algo_code)
            self.python_view.set_python_code(py_code)
            self.tdo_view.update_tdo(self.transpiler.declared_objects)
            self.variables_view.update_declared_variables(self.transpiler.declared_objects)

            self.lbl_status.setText("Exécution en cours...")
            self.console.run_python_code(py_code)
        except Exception as e:
            self.lbl_status.setText("Erreur de compilation")
            self.assistant_view.show_error_advice(str(e))
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
            "À propos de Thonny Algo-IDE",
            "<h3>Thonny Algo-IDE</h3>"
            "<p>Environnement de développement moderne et pédagogique pour l'Algorithmique scolaire et universitaire.</p>"
            "<p><b>Conformité stricte :</b></p>"
            "<ul>"
            "  <li><i>Les Conventions Algorithmiques (Septembre 2024)</i></li>"
            "  <li><i>Implémentation en Python des Conventions Algorithmiques (2024/2025)</i></li>"
            "</ul>"
            "<p>Développé avec <b>PyQt5</b> et <b>NumPy</b> sous Linux.</p>"
        )
