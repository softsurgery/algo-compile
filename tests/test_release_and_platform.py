"""
Unit tests for release versioning, platform-specific path resolution,
frozen-binary --run-script execution, and the update checker.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from version import __version__, is_newer_version, parse_version, select_platform_asset
from ui.platform_utils import get_bundle_dir, get_resource_path, get_user_data_dir, is_frozen
from ui.updater import fetch_latest_release
from ui.dialogs.about_dialog.header import AboutHeaderWidget

app = QApplication.instance() or QApplication([])


class TestReleaseAndPlatform(unittest.TestCase):
    def test_version_parsing_and_comparison(self):
        self.assertEqual(parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("1.0.0"), (1, 0, 0))
        self.assertTrue(is_newer_version("v1.1.0", "1.0.0"))
        self.assertTrue(is_newer_version("2.0.0", "1.9.9"))
        self.assertFalse(is_newer_version("1.0.0", "1.0.0"))
        self.assertFalse(is_newer_version("0.9.9", "1.0.0"))

    def test_select_platform_asset(self):
        assets = [
            {"name": "algoo_1.2.0_amd64.deb", "browser_download_url": "https://example.com/algoo.deb"},
            {"name": "Algoo-Setup-1.2.0.exe", "browser_download_url": "https://example.com/algoo.exe"},
            {"name": "Algoo-1.2.0-macOS.dmg", "browser_download_url": "https://example.com/algoo.dmg"},
        ]
        self.assertEqual(select_platform_asset(assets, "linux")["name"], "algoo_1.2.0_amd64.deb")
        self.assertEqual(select_platform_asset(assets, "win32")["name"], "Algoo-Setup-1.2.0.exe")
        self.assertEqual(select_platform_asset(assets, "darwin")["name"], "Algoo-1.2.0-macOS.dmg")
        self.assertIsNone(select_platform_asset(assets, "freebsd"))

    def test_platform_utils_source_and_frozen(self):
        self.assertFalse(is_frozen())
        self.assertTrue(os.path.isdir(get_resource_path("docs")))
        self.assertTrue(os.path.isdir(get_user_data_dir()))

        with tempfile.TemporaryDirectory() as tmp_meipass:
            with patch.object(sys, "frozen", True, create=True), patch.object(
                sys, "_MEIPASS", tmp_meipass, create=True
            ):
                self.assertTrue(is_frozen())
                self.assertEqual(get_bundle_dir(), os.path.abspath(tmp_meipass))
                self.assertEqual(
                    get_resource_path("docs", "guide.md"),
                    os.path.join(os.path.abspath(tmp_meipass), "docs", "guide.md"),
                )

    def test_main_cli_version_and_run_script(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        main_py = os.path.join(root_dir, "main.py")

        res_ver = subprocess.run(
            [sys.executable, main_py, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res_ver.returncode, 0)
        self.assertIn(__version__, res_ver.stdout)

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write("print('HELLO_FROZEN_RUNNER')\n")
            script_path = tf.name

        try:
            res_run = subprocess.run(
                [sys.executable, main_py, "--run-script", script_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(res_run.returncode, 0)
            self.assertIn("HELLO_FROZEN_RUNNER", res_run.stdout)
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def test_fetch_latest_release_mocked(self):
        payload = {
            "tag_name": "v2.0.0",
            "html_url": "https://github.com/softsurgery/algoo/releases/tag/v2.0.0",
            "body": "Release notes",
            "assets": [
                {"name": "algoo_2.0.0_amd64.deb", "browser_download_url": "https://dl/algoo.deb"},
                {"name": "Algoo-Setup-2.0.0.exe", "browser_download_url": "https://dl/algoo.exe"},
                {"name": "Algoo-2.0.0-macOS.dmg", "browser_download_url": "https://dl/algoo.dmg"},
            ],
        }

        class _MockResp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        with patch("urllib.request.urlopen", return_value=_MockResp(json.dumps(payload).encode("utf-8"))):
            info = fetch_latest_release("https://api.github.com/repos/softsurgery/algoo/releases/latest")
            self.assertEqual(info["version"], "2.0.0")
            self.assertEqual(info["notes"], "Release notes")
            self.assertTrue(info["download_url"].startswith("https://dl/"))

    def test_about_header_uses_version(self):
        header = AboutHeaderWidget()
        self.assertIn(__version__, header.version_label.text())
        header.close()


if __name__ == "__main__":
    unittest.main()
