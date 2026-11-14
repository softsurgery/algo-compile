# Release & Packaging Guide

This guide explains how to set up the Python bundling environment, build installers locally for each platform, publish automated releases via GitHub Actions, and how in-app updates work.

---

## 1. Python Bundling Environment (`.venv`)

Algoo uses a project-local Python virtual environment (`.venv/`) with dependencies pinned in `requirements.txt` (including `PyQt5`, `numpy`, `Markdown`, `PyMuPDF`, and `pyinstaller`).

### Linux / macOS
```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
```

> **Note:** All packaging scripts (`build_deb.sh`, `build_win.ps1`, `build_macos.sh`) automatically detect and use `.venv` when present.

---

## 2. Automated Release Pipeline (Recommended)

The GitHub Actions workflow in `.github/workflows/release.yml` automatically runs the test suite, builds native installers for Linux, Windows, and macOS, generates `SHA256SUMS.txt`, and publishes a GitHub Release.

### Steps to Cut a Release
1. **Optionally bump the version** in `version.py` (the GitHub Actions release workflow also automatically syncs `version.py` with the pushed `v*.*.*` tag during CI builds so the release binary, installers, and updater always match the tag):
   ```python
   __version__ = "1.1.0"
   ```
2. **Run tests locally** with `.venv`:
   ```bash
   .venv/bin/python -m unittest discover -s tests
   ```
3. **Commit and push** the version bump:
   ```bash
   git add version.py
   git commit -m "chore(release): bump version to 1.1.0"
   git push origin main
   ```
4. **Create and push the release tag** (`v` prefix must match `v*.*.*`):
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
5. **Monitor GitHub Actions**:
   - `test` runs the full `unittest` suite under `xvfb-run`.
   - `build-linux` produces `algoo_1.1.0_amd64.deb`.
   - `build-windows` produces `Algoo-Setup-1.1.0.exe`.
   - `build-macos` produces `Algoo-1.1.0-macOS.dmg`.
   - `publish-release` attaches all installers + `SHA256SUMS.txt` to the GitHub Release `v1.1.0`.

> You can also trigger a dry-run build manually from the GitHub **Actions → Release → Run workflow** button (`workflow_dispatch`).

---

## 3. Building Installers Locally

Each platform must be built on its target OS because PyInstaller produces native binaries.

### Linux (`.deb`)
Requires `dpkg-dev` (`sudo apt install dpkg-dev`).
```bash
bash packaging/linux/build_deb.sh
```
Output: `dist/algoo_<version>_amd64.deb`

To inspect or test-install the generated `.deb`:
```bash
dpkg-deb -I dist/algoo_*_amd64.deb
dpkg-deb -c dist/algoo_*_amd64.deb
sudo dpkg -i dist/algoo_*_amd64.deb
```

### Windows (`Setup .exe`)
Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php) installed (`ISCC.exe`).
```powershell
.\packaging\windows\build_win.ps1
```
Output: `dist\Algoo-Setup-<version>.exe`

### macOS (`.dmg`)
```bash
bash packaging/macos/build_macos.sh
```
Output: `dist/Algoo-<version>-macOS.dmg`

---

## 4. How In-App Updates Work

- **Source of truth**: `version.py` defines `__version__` and `GITHUB_RELEASES_API`.
- **Startup background check**: `MainWindow` schedules `check_for_updates(self, silent=True)` 3 seconds after launch via `ui/updater.py`.
  - Uses a non-blocking `QThread` (`UpdateCheckWorker`).
  - Only prompts the user if a newer tag exists on GitHub Releases; network errors or up-to-date checks stay silent.
  - Set `ALGOO_DISABLE_UPDATE_CHECK=1` to disable the startup check if needed.
- **Manual check**: Users can click **Aide → Vérifier les mises à jour...** at any time.
- **Platform asset matching**: `select_platform_asset()` automatically picks `.deb` on Linux, `.exe` on Windows, and `.dmg` on macOS from the release assets.

---

## 5. Platform-Specific Runtime Behavior

When Algoo is installed in a read-only system directory (`/opt/algoo`, `C:\Program Files\Algoo`, `/Applications/Algoo.app`):
- **Bundled assets** (`docs/`, `snippets/`, `examples/`, `ui/assets/`) are resolved via `ui/platform_utils.py` (`get_resource_path`, using `sys._MEIPASS` when frozen).
- **User data & SQLite DB** (`algoo.db`) are stored in the OS-standard writable app-data folder (`get_user_data_dir()` / `QStandardPaths.AppDataLocation`).
- **Algorithm execution** (`ui/console.py`) writes temporary `_algo_exec_*.py` scripts to `tempfile.gettempdir()` and invokes the frozen binary with `--run-script <path>` (handled in `main.py` before Qt loads).
