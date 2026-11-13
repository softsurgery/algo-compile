"""
In-app update checker for Algoo IDE.
Queries GitHub Releases API in a background QThread and selects the platform-native installer.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox

from version import (
    APP_NAME,
    GITHUB_RELEASES_API,
    GITHUB_RELEASES_URL,
    __version__,
    is_newer_version,
    select_platform_asset,
)


def fetch_latest_release(
    api_url: str = GITHUB_RELEASES_API,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Fetches and parses the latest release metadata from GitHub Releases API."""
    req = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{APP_NAME}/{__version__}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    tag_name = str(data.get("tag_name", "")).strip()
    release_url = str(data.get("html_url", "") or GITHUB_RELEASES_URL)
    notes = str(data.get("body", "") or "").strip()
    assets = data.get("assets", []) or []
    asset = select_platform_asset(assets)
    download_url = str(asset.get("browser_download_url")) if asset else release_url

    return {
        "version": tag_name.lstrip("vV") or "0.0.0",
        "tag_name": tag_name,
        "download_url": download_url,
        "release_url": release_url,
        "notes": notes,
    }


class UpdateCheckWorker(QThread):
    """Background worker that checks for a newer Algoo release without blocking the UI."""

    update_available = pyqtSignal(str, str, str)
    up_to_date = pyqtSignal(str)
    check_failed = pyqtSignal(str)

    def __init__(self, parent=None, api_url: str = GITHUB_RELEASES_API):
        super().__init__(parent)
        self._api_url = api_url

    def run(self) -> None:
        try:
            info = fetch_latest_release(self._api_url)
            latest = info["version"]
            if is_newer_version(latest, __version__):
                self.update_available.emit(latest, info["download_url"], info["notes"])
            else:
                self.up_to_date.emit(__version__)
        except Exception as exc:
            self.check_failed.emit(str(exc))


def check_for_updates(parent=None, silent: bool = False) -> Optional[UpdateCheckWorker]:
    """Starts an asynchronous update check; prompts only if an update exists when silent=True."""
    if silent and os.environ.get("ALGOO_DISABLE_UPDATE_CHECK") == "1":
        return None

    worker = UpdateCheckWorker(parent)
    if parent is not None:
        parent._update_worker = worker

    def _on_update_available(latest: str, download_url: str, notes: str) -> None:
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Mise à jour disponible")
        msg.setText(
            f"Une nouvelle version d'{APP_NAME} (v{latest}) est disponible !\n"
            f"Version actuelle : v{__version__}"
        )
        if notes:
            preview = notes if len(notes) <= 400 else notes[:397] + "..."
            msg.setInformativeText(preview)
        btn_dl = msg.addButton("Télécharger", QMessageBox.AcceptRole)
        msg.addButton("Plus tard", QMessageBox.RejectRole)
        msg.exec_()
        if msg.clickedButton() == btn_dl:
            QDesktopServices.openUrl(QUrl(download_url))

    def _on_up_to_date(current: str) -> None:
        if not silent:
            QMessageBox.information(
                parent,
                "Mises à jour",
                f"Vous utilisez déjà la dernière version d'{APP_NAME} (v{current}).",
            )

    def _on_failed(err: str) -> None:
        if not silent:
            QMessageBox.warning(
                parent,
                "Vérification impossible",
                f"Impossible de vérifier les mises à jour pour le moment.\n\nDétail : {err}",
            )

    worker.update_available.connect(_on_update_available)
    worker.up_to_date.connect(_on_up_to_date)
    worker.check_failed.connect(_on_failed)
    worker.start()
    return worker
