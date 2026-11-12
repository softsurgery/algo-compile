"""
Synchronized compatibility list and search filtering helper for InsertCodeDialog.
Preserves backward-compatibility with tests expecting list_widget and its selection behavior.
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from ui.snippets_manager import get_all_snippets_flat


class CompatibilityListManager:
    """Manages the hidden QListWidget to keep backward-compatible test hooks in sync."""

    def __init__(self, dialog):
        self.dialog = dialog
        self.list_widget = QListWidget()
        self.list_widget.setVisible(False)
        self.list_widget.currentRowChanged.connect(self._on_compat_list_row_changed)

    def sync(self):
        """Populates and filters list_widget for backward compatibility."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        query = self.dialog.search_input.text().strip().lower()
        all_snippets = get_all_snippets_flat()

        matched = []
        for s in all_snippets:
            if query:
                searchable = f"{s.title} {s.category} {s.desc} {s.filename} {s.code}".lower()
                if query not in searchable:
                    continue
            item = QListWidgetItem()
            item.setText(f"{s.title}\n  • {s.category}")
            item.setData(Qt.UserRole, {
                "title": s.title,
                "category": s.category,
                "filename": s.filename,
                "filepath": s.code_file,
                "code": s.code,
                "desc": s.desc,
                "lines_count": s.lines_count,
                "snippet_obj": s
            })
            self.list_widget.addItem(item)
            matched.append(s)

        self.list_widget.blockSignals(False)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            first = matched[0]
            self.dialog.selected_code = first.code
            self.dialog.selected_title = first.title
            self.dialog.preview_editor.setPlainText(first.code)
            self.dialog.snippets_widget._on_snippet_selected(first)
        else:
            self.dialog.selected_code = ""
            self.dialog.selected_title = ""

    def _on_compat_list_row_changed(self, row: int):
        if row < 0 or row >= self.list_widget.count():
            return
        item = self.list_widget.item(row)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if data:
            self.dialog.selected_code = data["code"]
            self.dialog.selected_title = data["title"]
            self.dialog.preview_editor.setPlainText(self.dialog.selected_code)
            if "snippet_obj" in data:
                self.dialog.snippets_widget._on_snippet_selected(data["snippet_obj"])
