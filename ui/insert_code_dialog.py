"""
Dialog for browsing and inserting algorithmic code examples and templates.
Accessible from Tools -> Insert Code...
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QLineEdit, QWidget,
    QFrame
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from ui.editor import AlgoCodeEditor
from ui.icons import create_icon
from ui.styles import LIGHT_THEME, DARK_THEME


KNOWN_EXAMPLES_META = {
    "somme_diviseurs.algo": {
        "title": "Somme des Diviseurs",
        "category": "Boucle Pour & Procédure",
        "desc": "Calcul de la somme des diviseurs d'un entier avec boucle Pour et procédure avec passage par variable (@n)."
    },
    "palindrome.algo": {
        "title": "Vérification de Palindrome",
        "category": "Chaînes & Boucle Répéter",
        "desc": "Algorithme vérifiant si un mot est un palindrome avec boucle Répéter...Jusqu'à."
    },
    "gestion_eleves.algo": {
        "title": "Mention des Élèves",
        "category": "Enregistrement & Selon",
        "desc": "Structure de données Enregistrement (Record) et aiguillage conditionnel Selon (match/case) avec intervalles."
    },
    "tri_bulles.algo": {
        "title": "Tri à Bulles",
        "category": "Tableau & Algorithme de Tri",
        "desc": "Tri classique d'un tableau d'entiers avec permutation et boucle Tant que / Pour."
    },
    "matrice_alea.algo": {
        "title": "Matrice Aléatoire",
        "category": "Tableau 2D & Aléa",
        "desc": "Remplissage et affichage d'une matrice à 2 dimensions avec la fonction Aléa."
    },
    "players_ranking.algo": {
        "title": "Classement des Joueurs",
        "category": "Tableau d'Enregistrements",
        "desc": "Gestion complète d'un tournoi avec tableau d'enregistrements (Player), saisie, rounds et classement."
    }
}


class InsertCodeDialog(QDialog):
    """Modern modal dialog to browse, preview, and insert algorithmic code."""

    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.setWindowTitle("Outils — Insérer du code (Insert Code)")
        self.resize(850, 560)
        self.setMinimumSize(680, 420)

        # Apply global theme to dialog window
        self.setStyleSheet(DARK_THEME if self.is_dark else LIGHT_THEME)

        self.selected_code = ""
        self.selected_title = ""
        self.action_mode = None  # 'insert' or 'new_tab'

        self._examples_data = []
        self._load_examples()
        self._setup_ui()
        self._populate_list()

    def _load_examples(self):
        """Scans examples directory and loads all .algo files."""
        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        if not os.path.exists(examples_dir):
            return

        for fname in sorted(os.listdir(examples_dir)):
            if fname.endswith(".algo"):
                filepath = os.path.join(examples_dir, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code = f.read()
                except UnicodeDecodeError:
                    with open(filepath, "r", encoding="latin-1") as f:
                        code = f.read()

                meta = KNOWN_EXAMPLES_META.get(fname, {
                    "title": fname.replace(".algo", "").replace("_", " ").title(),
                    "category": "Algorithme",
                    "desc": f"Exemple officiel {fname}"
                })

                self._examples_data.append({
                    "filename": fname,
                    "filepath": filepath,
                    "title": meta["title"],
                    "category": meta["category"],
                    "desc": meta["desc"],
                    "code": code,
                    "lines_count": len(code.splitlines())
                })

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Header description
        header_lbl = QLabel("Sélectionnez un algorithme ou modèle pour l'insérer dans votre projet :")
        header_lbl.setFont(QFont("SansSerif", 10, QFont.Bold))
        header_lbl.setStyleSheet("color: #a6adc8;" if self.is_dark else "color: #475569;")
        main_layout.addWidget(header_lbl)

        # Main splitter (List on left, Preview on right)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Search + List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un algorithme (ex: tri, matrice, selon)...")
        if self.is_dark:
            self.search_input.setStyleSheet(
                "QLineEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #89b4fa; }"
            )
        else:
            self.search_input.setStyleSheet(
                "QLineEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; }"
                "QLineEdit:focus { border: 1px solid #3b82f6; }"
            )
        self.search_input.textChanged.connect(self._filter_list)
        left_layout.addWidget(self.search_input)

        self.list_widget = QListWidget()
        if self.is_dark:
            self.list_widget.setStyleSheet(
                "QListWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #cdd6f4; }"
                "QListWidget::item:hover { background-color: #313244; }"
                "QListWidget::item:selected { background-color: #45475a; color: #ffffff; font-weight: bold; }"
            )
        else:
            self.list_widget.setStyleSheet(
                "QListWidget { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; outline: none; }"
                "QListWidget::item { padding: 8px 10px; border-radius: 4px; color: #1e293b; }"
                "QListWidget::item:hover { background-color: #f1f5f9; }"
                "QListWidget::item:selected { background-color: #e2e8f0; color: #0f172a; font-weight: bold; }"
            )
        self.list_widget.currentRowChanged.connect(self._on_item_selected)
        self.list_widget.itemDoubleClicked.connect(self._on_double_clicked)
        left_layout.addWidget(self.list_widget, 1)

        splitter.addWidget(left_widget)

        # Right panel: Metadata + Code Preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Info card
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        if self.is_dark:
            info_frame.setStyleSheet("background-color: #181825; border: 1px solid #313244; border-radius: 6px; padding: 4px;")
        else:
            info_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px;")

        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 8, 10, 8)
        info_layout.setSpacing(3)

        self.lbl_title = QLabel("Titre de l'algorithme")
        self.lbl_title.setFont(QFont("SansSerif", 11, QFont.Bold))
        self.lbl_title.setStyleSheet("color: #cdd6f4; font-weight: bold;" if self.is_dark else "color: #1e293b; font-weight: bold;")
        info_layout.addWidget(self.lbl_title)

        self.lbl_desc = QLabel("Description de l'algorithme")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #9399b2; font-size: 11px;" if self.is_dark else "color: #64748b; font-size: 11px;")
        info_layout.addWidget(self.lbl_desc)

        right_layout.addWidget(info_frame)

        # Code preview editor
        self.preview_editor = AlgoCodeEditor(is_dark=self.is_dark)
        self.preview_editor.setReadOnly(True)
        self.preview_editor.set_dark_mode(self.is_dark)
        if self.is_dark:
            self.preview_editor.setStyleSheet("QPlainTextEdit { background-color: #11111b; color: #cdd6f4; border: 1px solid #313244; border-radius: 6px; }")
        else:
            self.preview_editor.setStyleSheet("QPlainTextEdit { background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-radius: 6px; }")
        right_layout.addWidget(self.preview_editor, 1)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        main_layout.addWidget(splitter, 1)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color: #6c7086; font-size: 11px;" if self.is_dark else "color: #94a3b8; font-size: 11px;")
        bottom_layout.addWidget(self.lbl_count)

        bottom_layout.addStretch()

        if self.is_dark:
            btn_sec_style = (
                "QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
                "QPushButton:hover { background-color: #45475a; border-color: #585b70; }"
                "QPushButton:pressed { background-color: #585b70; }"
            )
        else:
            btn_sec_style = (
                "QPushButton { background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 14px; font-weight: 500; }"
                "QPushButton:hover { background-color: #f1f5f9; border-color: #94a3b8; }"
                "QPushButton:pressed { background-color: #e2e8f0; }"
            )

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setFixedWidth(90)
        self.btn_cancel.setStyleSheet(btn_sec_style)
        self.btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(self.btn_cancel)

        self.btn_new_tab = QPushButton("Ouvrir dans un nouvel onglet")
        self.btn_new_tab.setStyleSheet(btn_sec_style)
        self.btn_new_tab.clicked.connect(self._on_open_new_tab)
        bottom_layout.addWidget(self.btn_new_tab)

        self.btn_insert = QPushButton("Insérer dans l'éditeur")
        self.btn_insert.setDefault(True)
        self.btn_insert.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: #ffffff; font-weight: bold; border: none; padding: 6px 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:pressed { background-color: #1e40af; }"
        )
        self.btn_insert.clicked.connect(self._on_insert_clicked)
        bottom_layout.addWidget(self.btn_insert)

        main_layout.addLayout(bottom_layout)

    def _populate_list(self):
        """Fills the list widget with examples."""
        self.list_widget.clear()
        query = self.search_input.text().strip().lower()

        matched_count = 0
        for item in self._examples_data:
            if query:
                searchable = f"{item['title']} {item['category']} {item['desc']} {item['filename']} {item['code']}".lower()
                if query not in searchable:
                    continue

            list_item = QListWidgetItem()
            list_item.setText(f"{item['title']}\n  • {item['category']}")
            list_item.setIcon(create_icon("open", "#3b82f6" if not self.is_dark else "#89b4fa"))
            list_item.setData(Qt.UserRole, item)
            self.list_widget.addItem(list_item)
            matched_count += 1

        self.lbl_count.setText(f"{matched_count} algorithme(s) disponible(s)")

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _filter_list(self):
        self._populate_list()

    def _on_item_selected(self, row: int):
        if row < 0:
            return
        item = self.list_widget.item(row)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return

        self.lbl_title.setText(f"{data['title']}  ({data['filename']} - {data['lines_count']} lignes)")
        self.lbl_desc.setText(f"Catégorie: {data['category']} | {data['desc']}")
        self.preview_editor.setPlainText(data['code'])

    def _on_double_clicked(self, item: QListWidgetItem):
        self._on_insert_clicked()

    def _on_insert_clicked(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            data = item.data(Qt.UserRole)
            self.selected_code = data['code']
            self.selected_title = data['title']
            self.action_mode = 'insert'
            self.accept()

    def _on_open_new_tab(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            item = self.list_widget.item(row)
            data = item.data(Qt.UserRole)
            self.selected_code = data['code']
            self.selected_title = data['filename']
            self.action_mode = 'new_tab'
            self.accept()
