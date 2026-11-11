"""
Lightweight, high-performance PDF Viewer component for Algoo IDE.
Features:
- Renders PDF pages crisply with zoom, fit-width, fit-page, and page navigation.
- Engine: pypdfium2 with seamless fallback to pdftoppm (poppler-utils).
- Dark and light mode themed viewer matching Catppuccin / Slate palette.
- Pop-out capability into a standalone, full-screenable separate window (PdfReaderWindow).
"""

import os
import shutil
import tempfile
import subprocess
from typing import Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSpinBox, QFrame, QDialog, QShortcut, QApplication, QMessageBox, QSizePolicy, QLayout
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QKeySequence, QWheelEvent, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QEvent, QTimer

from ui.icons import create_icon
from ui.styles import DARK_THEME, LIGHT_THEME

# Check for pypdfium2
try:
    import pypdfium2 as pdfium
    HAS_PYPDFIUM2 = True
except ImportError:
    pdfium = None
    HAS_PYPDFIUM2 = False

HAS_PDFTOPPM = shutil.which("pdftoppm") is not None


class LightPdfViewer(QWidget):
    """
    Lightweight, fast PDF viewer widget.
    Can be embedded inside SnippetFilesViewer or used standalone.
    """

    detach_requested = pyqtSignal(str)  # Emits file_path when separate window requested

    def __init__(self, parent=None, is_dark: bool = False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.file_path: Optional[str] = None
        self.page_count: int = 0
        self.current_page: int = 0  # 0-indexed
        self.zoom_factor: float = 1.0
        self.fit_mode: str = "none"  # "none", "width", "page"

        self._doc = None  # pypdfium2 PdfDocument if available
        self._temp_dir: Optional[str] = None

        self._setup_ui()
        self.set_dark_mode(self.is_dark)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Top Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFrameShape(QFrame.StyledPanel)
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(4, 4, 4, 4)
        tb_layout.setSpacing(6)

        # Page Navigation
        self.btn_prev = QPushButton()
        self.btn_prev.setFixedSize(32, 28)
        self.btn_prev.setIconSize(QSize(18, 18))
        self.btn_prev.setToolTip("Page précédente (Flèche gauche / Page préc.)")
        self.btn_prev.clicked.connect(self.prev_page)
        tb_layout.addWidget(self.btn_prev)

        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setMaximum(1)
        self.spin_page.setValue(1)
        self.spin_page.setFixedWidth(55)
        self.spin_page.setFixedHeight(28)
        self.spin_page.setAlignment(Qt.AlignCenter)
        self.spin_page.valueChanged.connect(self._on_spin_page_changed)
        tb_layout.addWidget(self.spin_page)

        self.lbl_page_count = QLabel("/ 1")
        self.lbl_page_count.setStyleSheet("font-size: 11px; font-weight: bold;")
        tb_layout.addWidget(self.lbl_page_count)

        self.btn_next = QPushButton()
        self.btn_next.setFixedSize(32, 28)
        self.btn_next.setIconSize(QSize(18, 18))
        self.btn_next.setToolTip("Page suivante (Flèche droite / Page suiv.)")
        self.btn_next.clicked.connect(self.next_page)
        tb_layout.addWidget(self.btn_next)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setFrameShadow(QFrame.Sunken)
        tb_layout.addWidget(sep1)

        # Zoom controls
        self.btn_zoom_out = QPushButton()
        self.btn_zoom_out.setFixedSize(32, 28)
        self.btn_zoom_out.setIconSize(QSize(18, 18))
        self.btn_zoom_out.setToolTip("Zoom arrière (Ctrl -)")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        tb_layout.addWidget(self.btn_zoom_out)

        self.lbl_zoom = QLabel("100%")
        self.lbl_zoom.setFixedWidth(46)
        self.lbl_zoom.setAlignment(Qt.AlignCenter)
        self.lbl_zoom.setStyleSheet("font-size: 11px;")
        tb_layout.addWidget(self.lbl_zoom)

        self.btn_zoom_in = QPushButton()
        self.btn_zoom_in.setFixedSize(32, 28)
        self.btn_zoom_in.setIconSize(QSize(18, 18))
        self.btn_zoom_in.setToolTip("Zoom avant (Ctrl +)")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        tb_layout.addWidget(self.btn_zoom_in)

        self.btn_fit_width = QPushButton("Largeur")
        self.btn_fit_width.setFixedHeight(28)
        self.btn_fit_width.setToolTip("Ajuster à la largeur de la vue")
        self.btn_fit_width.clicked.connect(self.fit_width)
        tb_layout.addWidget(self.btn_fit_width)

        self.btn_fit_page = QPushButton("Page")
        self.btn_fit_page.setFixedHeight(28)
        self.btn_fit_page.setToolTip("Ajuster à la page entière")
        self.btn_fit_page.clicked.connect(self.fit_page)
        tb_layout.addWidget(self.btn_fit_page)

        tb_layout.addStretch()

        # Detach / Separate Window button
        self.btn_detach = QPushButton("Plein écran (Fenêtre)")
        self.btn_detach.setFixedHeight(28)
        self.btn_detach.setIconSize(QSize(18, 18))
        self.btn_detach.setToolTip("Ouvrir le lecteur PDF dans une fenêtre séparée en plein écran")
        self.btn_detach.clicked.connect(self._on_detach_clicked)
        tb_layout.addWidget(self.btn_detach)

        layout.addWidget(self.toolbar)

        # Content Area: ScrollArea containing page label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setFocusPolicy(Qt.StrongFocus)
        self.setFocusPolicy(Qt.StrongFocus)

        self.container_widget = QWidget()
        container_layout = QVBoxLayout(self.container_widget)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSizeConstraint(QLayout.SetMinimumSize)

        self.lbl_page = QLabel()
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.lbl_page.setFocusPolicy(Qt.ClickFocus)
        self.lbl_page.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lbl_page.setStyleSheet("background-color: transparent;")
        container_layout.addWidget(self.lbl_page)

        self.scroll_area.setWidget(self.container_widget)
        # Event filter on viewport to intercept wheel zoom, page flips and clicks
        self.scroll_area.viewport().installEventFilter(self)
        layout.addWidget(self.scroll_area, 1)

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        icon_color = "#cdd6f4" if is_dark else "#475569"

        self.btn_prev.setIcon(create_icon("prev", icon_color, 18))
        self.btn_next.setIcon(create_icon("next", icon_color, 18))
        self.btn_zoom_in.setIcon(create_icon("zoom_in", icon_color, 18))
        self.btn_zoom_out.setIcon(create_icon("zoom_out", icon_color, 18))
        self.btn_detach.setIcon(create_icon("fullscreen", icon_color, 18))

        bg = "#11111b" if is_dark else "#ffffff"
        tb_bg = "#181825" if is_dark else "#f8fafc"
        border = "#313244" if is_dark else "#e2e8f0"
        fg = "#cdd6f4" if is_dark else "#1e293b"
        btn_bg = "#313244" if is_dark else "#ffffff"

        self.toolbar.setStyleSheet(
            f"QFrame {{ background-color: {tb_bg}; border: 1px solid {border}; border-radius: 6px; }}"
            f"QLabel {{ color: {fg}; }}"
            f"QSpinBox {{ background-color: {btn_bg}; color: {fg}; border: 1px solid {border}; border-radius: 4px; padding: 2px; }}"
            f"QPushButton {{ background-color: {btn_bg}; color: {fg}; border: 1px solid {border}; border-radius: 4px; padding: 3px 8px; }}"
            f"QPushButton:hover {{ background-color: {'#45475a' if is_dark else '#f1f5f9'}; }}"
        )
        self.scroll_area.setStyleSheet(
            f"QScrollArea {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}"
        )
        self.container_widget.setStyleSheet(f"background-color: {bg};")

    def load_pdf(self, file_path: str):
        """Loads and displays the specified PDF document."""
        if not file_path or not os.path.isfile(file_path):
            self.lbl_page.setText("Fichier PDF introuvable.")
            return

        self.file_path = file_path
        self._close_document()

        try:
            if HAS_PYPDFIUM2:
                self._doc = pdfium.PdfDocument(file_path)
                self.page_count = len(self._doc)
            elif HAS_PDFTOPPM:
                self._doc = "pdftoppm"
                self.page_count = self._get_page_count_poppler(file_path)
            else:
                self.lbl_page.setText(
                    "Aucun moteur de rendu PDF disponible.\n"
                    "Installez pypdfium2 (pip install pypdfium2) ou poppler-utils (pdftoppm)."
                )
                return

            self.current_page = 0
            self.spin_page.blockSignals(True)
            self.spin_page.setMaximum(max(1, self.page_count))
            self.spin_page.setValue(1)
            self.spin_page.blockSignals(False)
            self.lbl_page_count.setText(f"/ {self.page_count}")

            self.zoom_factor = 1.0
            self.fit_mode = "none"
            self.render_page(self.current_page)

        except Exception as e:
            self.lbl_page.setText(f"Erreur lors du chargement du PDF :\n{e}")

    def _get_page_count_poppler(self, path: str) -> int:
        """Determines page count using pdfinfo or trial render."""
        pdfinfo = shutil.which("pdfinfo")
        if pdfinfo:
            try:
                res = subprocess.run([pdfinfo, path], capture_output=True, text=True, check=True)
                for line in res.stdout.splitlines():
                    if line.startswith("Pages:"):
                        return int(line.split(":")[1].strip())
            except Exception:
                pass
        return 1

    def render_page(self, page_idx: int):
        """Renders page_idx (0-indexed) with the current zoom/scale setting."""
        if self.page_count == 0 or page_idx < 0 or page_idx >= self.page_count:
            return

        self.current_page = page_idx
        self.spin_page.blockSignals(True)
        self.spin_page.setValue(page_idx + 1)
        self.spin_page.blockSignals(False)

        self.btn_prev.setEnabled(page_idx > 0)
        self.btn_next.setEnabled(page_idx < self.page_count - 1)

        pixmap = None

        if HAS_PYPDFIUM2 and self._doc is not None and not isinstance(self._doc, str):
            try:
                page = self._doc[page_idx]
                # Base scale 1.5 for crisp retina quality
                scale = max(0.2, min(5.0, 1.5 * self.zoom_factor))
                bitmap = page.render(scale=scale)
                pil_img = bitmap.to_pil()
                data = pil_img.convert("RGBA").tobytes("raw", "RGBA")
                qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimg)
            except Exception as e:
                self.lbl_page.setText(f"Erreur de rendu page {page_idx + 1} : {e}")
                return

        elif HAS_PDFTOPPM and self.file_path:
            try:
                dpi = int(120 * self.zoom_factor)
                cmd = ["pdftoppm", "-png", "-f", str(page_idx + 1), "-l", str(page_idx + 1), "-r", str(dpi), self.file_path]
                res = subprocess.run(cmd, capture_output=True)
                # Read generated stdout or temporary file
                if res.returncode == 0 and res.stdout:
                    qimg = QImage()
                    qimg.loadFromData(res.stdout, "PNG")
                    pixmap = QPixmap.fromImage(qimg)
            except Exception as e:
                self.lbl_page.setText(f"Erreur pdftoppm : {e}")
                return

        if pixmap and not pixmap.isNull():
            self.lbl_page.setPixmap(pixmap)
            self.lbl_page.setFixedSize(pixmap.size())
            self.lbl_zoom.setText(f"{int(self.zoom_factor * 100)}%")

    def goto_page(self, page_idx: int):
        """Jumps directly to a given 0-indexed page."""
        if 0 <= page_idx < self.page_count and page_idx != self.current_page:
            self.render_page(page_idx)
            self.scroll_area.verticalScrollBar().setValue(0)

    def prev_page(self):
        if self.current_page > 0:
            self.render_page(self.current_page - 1)
            self.scroll_area.verticalScrollBar().setValue(0)

    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.render_page(self.current_page + 1)
            self.scroll_area.verticalScrollBar().setValue(0)

    def _on_spin_page_changed(self, val: int):
        target = val - 1
        if 0 <= target < self.page_count and target != self.current_page:
            self.render_page(target)
            self.scroll_area.verticalScrollBar().setValue(0)

    def zoom_in(self):
        if self.zoom_factor < 4.0:
            self.zoom_factor = round(self.zoom_factor * 1.25, 2)
            self.fit_mode = "none"
            self.render_page(self.current_page)

    def zoom_out(self):
        if self.zoom_factor > 0.25:
            self.zoom_factor = round(self.zoom_factor / 1.25, 2)
            self.fit_mode = "none"
            self.render_page(self.current_page)

    def fit_width(self):
        """Calculates scale to fit viewport width."""
        if not self.lbl_page.pixmap():
            return
        viewport_w = self.scroll_area.viewport().width() - 40
        current_w = self.lbl_page.pixmap().width() / self.zoom_factor
        if current_w > 0 and viewport_w > 50:
            self.zoom_factor = max(0.25, min(4.0, viewport_w / current_w))
            self.fit_mode = "width"
            self.render_page(self.current_page)

    def fit_page(self):
        """Calculates scale to fit whole page inside viewport."""
        if not self.lbl_page.pixmap():
            return
        viewport_h = self.scroll_area.viewport().height() - 40
        viewport_w = self.scroll_area.viewport().width() - 40
        current_h = self.lbl_page.pixmap().height() / self.zoom_factor
        current_w = self.lbl_page.pixmap().width() / self.zoom_factor
        if current_h > 0 and current_w > 0:
            ratio_h = viewport_h / current_h
            ratio_w = viewport_w / current_w
            self.zoom_factor = max(0.25, min(4.0, min(ratio_h, ratio_w)))
            self.fit_mode = "page"
            self.render_page(self.current_page)

    def eventFilter(self, watched, event):
        """Intercepts viewport wheel and mouse events for zoom and fluid page flips."""
        if hasattr(self, "scroll_area") and watched == self.scroll_area.viewport():
            if event.type() == QEvent.Wheel:
                if event.modifiers() & Qt.ControlModifier:
                    delta = event.angleDelta().y()
                    if delta > 0:
                        self.zoom_in()
                    elif delta < 0:
                        self.zoom_out()
                    return True
                else:
                    vbar = self.scroll_area.verticalScrollBar()
                    delta = event.angleDelta().y()
                    if vbar.maximum() == 0:
                        # Page fits vertically: mouse wheel flips pages smoothly
                        if delta < 0 and self.current_page < self.page_count - 1:
                            self.next_page()
                            return True
                        elif delta > 0 and self.current_page > 0:
                            self.prev_page()
                            return True
                    else:
                        # Boundary page flip when scrolling past top/bottom
                        if delta < -40 and vbar.value() >= vbar.maximum():
                            if self.current_page < self.page_count - 1:
                                self.next_page()
                                vbar.setValue(0)
                                return True
                        elif delta > 40 and vbar.value() <= vbar.minimum():
                            if self.current_page > 0:
                                self.prev_page()
                                vbar.setValue(vbar.maximum())
                                return True
            elif event.type() == QEvent.MouseButtonPress:
                self.setFocus()

        return super().eventFilter(watched, event)

    def keyPressEvent(self, event):
        """Keyboard navigation: Left/Right, PageUp/PageDown, Up/Down, Zoom shortcuts."""
        key = event.key()
        modifiers = event.modifiers()
        if key in (Qt.Key_Left, Qt.Key_PageUp):
            self.prev_page()
            event.accept()
            return
        elif key in (Qt.Key_Right, Qt.Key_PageDown, Qt.Key_Space):
            self.next_page()
            event.accept()
            return
        elif key == Qt.Key_Home:
            self.goto_page(0)
            event.accept()
            return
        elif key == Qt.Key_End:
            self.goto_page(self.page_count - 1)
            event.accept()
            return
        elif key == Qt.Key_Up:
            vbar = self.scroll_area.verticalScrollBar()
            if vbar.value() <= vbar.minimum() and self.current_page > 0:
                self.prev_page()
                vbar.setValue(vbar.maximum())
            else:
                vbar.setValue(vbar.value() - 40)
            event.accept()
            return
        elif key == Qt.Key_Down:
            vbar = self.scroll_area.verticalScrollBar()
            if vbar.value() >= vbar.maximum() and self.current_page < self.page_count - 1:
                self.next_page()
                vbar.setValue(0)
            else:
                vbar.setValue(vbar.value() + 40)
            event.accept()
            return
        elif modifiers & Qt.ControlModifier and key in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_in()
            event.accept()
            return
        elif modifiers & Qt.ControlModifier and key == Qt.Key_Minus:
            self.zoom_out()
            event.accept()
            return
        elif modifiers & Qt.ControlModifier and key == Qt.Key_0:
            self.zoom_factor = 1.0
            self.fit_mode = "none"
            self.render_page(self.current_page)
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom with Ctrl + Scroll Wheel, or scroll normally."""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.fit_mode == "width":
            self.fit_width()
        elif self.fit_mode == "page":
            self.fit_page()

    def _on_detach_clicked(self):
        if self.file_path:
            self.detach_requested.emit(self.file_path)

    def _close_document(self):
        if self._doc and HAS_PYPDFIUM2 and not isinstance(self._doc, str):
            try:
                self._doc.close()
            except Exception:
                pass
        self._doc = None

    def closeEvent(self, event):
        self._close_document()
        super().closeEvent(event)


class PdfReaderWindow(QWidget):
    """
    Dedicated, top-level window for viewing PDF documents in a separate window.
    Features:
    - Full screen toggle (F11 or button).
    - Page navigation and zoom.
    - Responsive event handling under Wayland and X11.
    - Minimal title bar / clean styling without top-left app icon.
    """

    def __init__(self, file_path: str, parent=None, is_dark: bool = False, start_fullscreen: bool = False):
        super().__init__(parent, Qt.Window)
        self.file_path = file_path
        self.is_dark = is_dark
        self._is_fullscreen = False
        self._start_fullscreen = start_fullscreen

        # Remove app icon in top left
        empty_pm = QPixmap(1, 1)
        empty_pm.fill(Qt.transparent)
        self.setWindowIcon(QIcon(empty_pm))

        fname = os.path.basename(file_path) if file_path else "Document"
        self.setWindowTitle(f"{fname} — Lecteur PDF Algoo")

        # Enable maximize and minimize buttons
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )

        self.resize(1000, 750)
        self.setMinimumSize(600, 400)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet(DARK_THEME if self.is_dark else LIGHT_THEME)

        self._setup_ui()

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._on_escape)
        QShortcut(QKeySequence(Qt.Key_Left), self, self.viewer.prev_page)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.viewer.next_page)
        QShortcut(QKeySequence(Qt.Key_PageUp), self, self.viewer.prev_page)
        QShortcut(QKeySequence(Qt.Key_PageDown), self, self.viewer.next_page)
        QShortcut(QKeySequence(Qt.Key_Space), self, self.viewer.next_page)
        QShortcut(QKeySequence("Ctrl++"), self, self.viewer.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.viewer.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.viewer.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self._reset_zoom)

        if file_path:
            self.viewer.load_pdf(file_path)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header bar with Fullscreen toggle
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(4, 2, 4, 2)
        top_bar.setSpacing(8)

        self.lbl_icon = QLabel()
        self.lbl_icon.setPixmap(create_icon("pdf", "#ef4444", 20).pixmap(20, 20))
        top_bar.addWidget(self.lbl_icon)

        self.lbl_title = QLabel(os.path.basename(self.file_path) if self.file_path else "Document PDF")
        self.lbl_title.setFont(QFont("SansSerif", 10, QFont.Bold))
        top_bar.addWidget(self.lbl_title, 1)

        icon_color = "#cdd6f4" if self.is_dark else "#475569"

        self.btn_fs = QPushButton("Plein écran")
        self.btn_fs.setFixedHeight(30)
        self.btn_fs.setIconSize(QSize(18, 18))
        self.btn_fs.setIcon(create_icon("fullscreen", icon_color, 18))
        self.btn_fs.setToolTip("Basculer en mode plein écran (F11)")
        self.btn_fs.clicked.connect(self.toggle_fullscreen)
        top_bar.addWidget(self.btn_fs)

        self.btn_close = QPushButton("Fermer")
        self.btn_close.setFixedHeight(30)
        self.btn_close.setIconSize(QSize(18, 18))
        self.btn_close.setIcon(create_icon("close", icon_color, 18))
        self.btn_close.clicked.connect(self.close)
        top_bar.addWidget(self.btn_close)

        layout.addLayout(top_bar)

        # Embedded PDF Viewer
        self.viewer = LightPdfViewer(self, is_dark=self.is_dark)
        # Hide the inner detach button inside standalone window
        self.viewer.btn_detach.setVisible(False)
        layout.addWidget(self.viewer, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus()
        if hasattr(self, "viewer"):
            self.viewer.setFocus()
        if getattr(self, "_start_fullscreen", False):
            self._start_fullscreen = False
            # Safely transition to fullscreen once the window surface is mapped
            # to prevent Wayland compositor configure deadlocks
            QTimer.singleShot(50, self._apply_initial_fullscreen)

    def _apply_initial_fullscreen(self):
        self.showFullScreen()
        self._is_fullscreen = True
        self.btn_fs.setText("Quitter plein écran")
        self.setFocus()
        if hasattr(self, "viewer"):
            self.viewer.setFocus()
            self.viewer.fit_page()

    def _reset_zoom(self):
        self.viewer.zoom_factor = 1.0
        self.viewer.fit_mode = "none"
        self.viewer.render_page(self.viewer.current_page)

    def toggle_fullscreen(self):
        """Toggles between full screen and normal window."""
        if self.isFullScreen() or self._is_fullscreen:
            self.showNormal()
            self._is_fullscreen = False
            self.btn_fs.setText("Plein écran")
        else:
            self.showFullScreen()
            self._is_fullscreen = True
            self.btn_fs.setText("Quitter plein écran")
        self.setFocus()
        if hasattr(self, "viewer"):
            self.viewer.setFocus()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self._on_escape()
            event.accept()
            return
        elif key == Qt.Key_F11:
            self.toggle_fullscreen()
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_escape(self):
        if self.isFullScreen() or self._is_fullscreen:
            self.toggle_fullscreen()
        else:
            self.close()

    def set_dark_mode(self, is_dark: bool):
        self.is_dark = is_dark
        self.setStyleSheet(DARK_THEME if is_dark else LIGHT_THEME)
        self.viewer.set_dark_mode(is_dark)
        icon_color = "#cdd6f4" if is_dark else "#475569"
        self.btn_fs.setIcon(create_icon("fullscreen", icon_color, 18))
        self.btn_close.setIcon(create_icon("close", icon_color, 18))
