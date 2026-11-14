"""
Sync version.py with a release version or GitHub tag (e.g. v1.2.3 -> 1.2.3).
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_VERSION_FILE = ROOT_DIR / "version.py"
VERSION_LINE_RE = re.compile(r'^(__version__\s*=\s*)(["\'])([^"\']*)(["\'])', re.MULTILINE)


def normalize_version(raw: str) -> str:
    """Strips leading 'v'/'V' and whitespace from a tag or version string."""
    cleaned = raw.strip().lstrip("vV")
    if not cleaned or not re.match(r"^\d+(\.\d+)*([+-].*)?$", cleaned):
        raise ValueError(f"Invalid version string: {raw!r}")
    return cleaned


def sync_version_file(new_version: str, version_file: Path = DEFAULT_VERSION_FILE) -> str:
    """Updates __version__ in `version_file` to the normalized `new_version`."""
    normalized = normalize_version(new_version)
    content = version_file.read_text(encoding="utf-8")
    updated, count = VERSION_LINE_RE.subn(rf'\g<1>\g<2>{normalized}\g<4>', content, count=1)
    if count != 1:
        raise RuntimeError(f"Could not find __version__ assignment in {version_file}")
    version_file.write_text(updated, encoding="utf-8")
    return normalized


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sync version.py with a tag or version string.")
    parser.add_argument(
        "version",
        nargs="?",
        help="Version or tag (e.g. v1.2.3 or 1.2.3). Defaults to GITHUB_REF_NAME if on a tag.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_VERSION_FILE,
        help="Path to version.py",
    )
    args = parser.parse_args(argv)

    raw = args.version
    if not raw:
        ref = os.environ.get("GITHUB_REF", "")
        if ref.startswith("refs/tags/"):
            raw = os.environ.get("GITHUB_REF_NAME") or ref.removeprefix("refs/tags/")
        else:
            raw = os.environ.get("ALGOO_VERSION", "")

    if not raw:
        print("No tag or version provided; leaving version.py unchanged.")
        return 0

    synced = sync_version_file(raw, args.file)
    print(f"Synced {args.file} to __version__ = {synced!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
