#!/usr/bin/env python3
"""Non-installing structural checks for the theming ecology repository."""

from __future__ import annotations

import configparser
import json
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def require(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.exists():
        ERRORS.append(f"missing: {path}")
    return candidate


def check_archive(path: Path) -> None:
    if not path.is_file():
        return
    try:
        if path.suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    ERRORS.append(f"corrupt member in {path.relative_to(ROOT)}: {bad}")
        else:
            with tarfile.open(path):
                pass
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as exc:
        ERRORS.append(f"archive error in {path.relative_to(ROOT)}: {exc}")


def check_index_theme(path: Path) -> None:
    if not path.is_file():
        return
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, configparser.Error) as exc:
        ERRORS.append(f"invalid index.theme {path.relative_to(ROOT)}: {exc}")
        return
    if not parser.has_section("Icon Theme"):
        ERRORS.append(f"missing [Icon Theme] in {path.relative_to(ROOT)}")


def main() -> int:
    required = [
        "README.md",
        "AGENTS.md",
        "docs/PROJECT-CUSTOM-INSTRUCTIONS.md",
        "themes/darkcold-coonie/README.md",
        "themes/darkcold-coonie/tools/test.sh",
        "icons/coonie-aero-hoard/README.md",
        "icons/coonie-aero-hoard/scripts/build_theme.py",
        "cursors/coonie-aero-gel-v1/Coonie-Aero-Gel/index.theme",
        "cursors/coonie-aero-gel-v1/source-build/build.py",
        "userstyles/Coonieglass-ChatGPT.user.css",
        "skills/maintain-linux-theme-ecologies/SKILL.md",
    ]
    for item in required:
        require(item)

    for archive in sorted((ROOT / "releases").rglob("*")):
        if archive.is_file() and (archive.name.endswith((".tar.gz", ".tar.xz", ".zip"))):
            check_archive(archive)

    for index_theme in sorted(ROOT.rglob("index.theme")):
        relative_parts = index_theme.relative_to(ROOT).parts
        if "icons" in relative_parts or "cursors" in relative_parts:
            check_index_theme(index_theme)

    summary = require("releases/icons/Coonie-Aero-Hoard-1.1.2-summary.json")
    if summary.is_file():
        try:
            data = json.loads(summary.read_text(encoding="utf-8"))
            if data.get("installed_icon_files", 0) < 100_000:
                ERRORS.append("Aero Hoard summary unexpectedly reports fewer than 100,000 icons")
        except (OSError, json.JSONDecodeError) as exc:
            ERRORS.append(f"invalid Aero Hoard summary: {exc}")

    usercss = require("userstyles/Coonieglass-ChatGPT.user.css")
    if usercss.is_file() and "==UserStyle==" not in usercss.read_text(encoding="utf-8", errors="replace"):
        ERRORS.append("Coonieglass file lacks a UserStyle metadata block")

    cursor_dir = require("cursors/coonie-aero-gel-v1/Coonie-Aero-Gel/cursors")
    if cursor_dir.is_dir() and len(list(cursor_dir.iterdir())) < 60:
        ERRORS.append("cursor alias set is unexpectedly small")

    if ERRORS:
        print("Repository validation failed:")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
