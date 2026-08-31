#!/usr/bin/env python3
"""Structural, format, coverage, and cache audit for the release theme."""

from __future__ import annotations

import argparse
import configparser
import json
import lzma
import os
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".png", ".svg", ".xpm"}
KNOWN_CONTEXTS = {
    "actions", "animations", "apps", "categories", "devices", "emblems",
    "emotes", "intl", "mimetypes", "panel", "places", "status", "symbolic",
}
REQUIRED_NAMES = {
    "actions": {"document-open", "document-save", "edit-copy", "edit-cut", "edit-paste", "media-playback-start"},
    "apps": {"cinnamon", "cinnamon-settings", "nemo", "xed", "pix", "mintinstall", "mintupdate", "utilities-terminal", "internet-web-browser"},
    "devices": {"computer", "drive-harddisk", "drive-removable-media-usb", "camera-photo"},
    "mimetypes": {"text-x-generic", "application-pdf", "audio-x-generic", "video-x-generic", "inode-directory"},
    "places": {
        "folder",
        "folder-aqua",
        "folder-documents",
        "folder-download",
        "folder-downloads",
        "folder-drag-accept",
        "folder-music",
        "folder-open",
        "folder-pictures",
        "folder-publicshare",
        "folder-purple",
        "folder-remote",
        "folder-saved-search",
        "folder-seagreen",
        "folder-templates",
        "folder-videos",
        "folder-visiting",
        "inode-directory",
        "network-workgroup",
        "user-desktop",
        "user-home",
        "user-trash",
        "user-trash-full",
    },
    "status": {"dialog-error", "dialog-information", "dialog-warning"},
    "symbolic": {
        "folder-documents-symbolic",
        "folder-download-symbolic",
        "folder-drag-accept-symbolic",
        "folder-new-symbolic",
        "folder-open-symbolic",
        "folder-symbolic",
        "user-desktop-symbolic",
        "user-home-symbolic",
        "user-trash-symbolic",
    },
}
NEMO_TOOLBAR_REGULAR_SIZES = (16, 22, 24, 32, 48)
NEMO_TOOLBAR_REGULAR_FALLBACKS = ("go-previous", "edit-find")


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("theme", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    parsed = args()
    theme = parsed.theme.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    counts = Counter()
    names: dict[str, set[str]] = defaultdict(set)
    actual_paths: set[str] = set()
    hardlinked_icons: list[str] = []

    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    parser.read(theme / "index.theme", encoding="utf-8")
    if "Icon Theme" not in parser:
        raise SystemExit("index.theme has no [Icon Theme] section")
    listed_dirs = parser["Icon Theme"].get("Directories", "").split(",")
    listed_dirs = [item for item in listed_dirs if item]

    for directory in listed_dirs:
        path = theme / directory
        if not path.is_dir():
            errors.append(f"listed directory is missing: {directory}")
        if directory not in parser:
            errors.append(f"listed directory has no index section: {directory}")

    for dirpath, _, filenames in os.walk(theme):
        base = Path(dirpath)
        relative_base = base.relative_to(theme)
        if any(part in {"licenses", "manifest"} for part in relative_base.parts):
            continue
        for filename in filenames:
            path = base / filename
            suffix = path.suffix.lower()
            if suffix not in IMAGE_SUFFIXES:
                continue
            if path.stat().st_nlink > 1:
                hardlinked_icons.append(str(path.relative_to(theme)))
            counts[suffix] += 1
            actual_paths.add(str(path.relative_to(theme)))
            parts = relative_base.parts
            if len(parts) >= 2:
                category = parts[0] if parts[0] in KNOWN_CONTEXTS else parts[1]
                names[category].add(path.stem)
                if str(relative_base) not in listed_dirs:
                    errors.append(f"icon lives in unlisted directory: {path.relative_to(theme)}")
            if suffix == ".png":
                try:
                    with Image.open(path) as image:
                        width, height = image.size
                        image.verify()
                    declared = None
                    if parts and "x" in parts[0]:
                        declared = int(parts[0].split("x", 1)[0])
                    elif len(parts) >= 2 and parts[1].split("@", 1)[0].isdigit():
                        declared = int(parts[1].split("@", 1)[0])
                    if declared and (width > declared or height > declared):
                        errors.append(
                            f"oversized PNG {path.relative_to(theme)}: {width}x{height} in {declared}px directory"
                        )
                except Exception as exc:
                    errors.append(f"invalid PNG {path.relative_to(theme)}: {exc}")
            elif suffix == ".svg":
                try:
                    ET.parse(path)
                except Exception as exc:
                    errors.append(f"invalid SVG {path.relative_to(theme)}: {exc}")

    broken_links = []
    for path in theme.rglob("*"):
        if path.is_symlink() and not path.exists():
            broken_links.append(str(path.relative_to(theme)))
    if broken_links:
        errors.extend(f"broken symlink: {path}" for path in broken_links)
    if hardlinked_icons:
        errors.append("hard-linked icon paths: " + ", ".join(hardlinked_icons[:30]))

    for category, required in REQUIRED_NAMES.items():
        missing = sorted(required - names.get(category, set()))
        if missing:
            errors.append(f"missing required {category} names: {', '.join(missing)}")

    for name in NEMO_TOOLBAR_REGULAR_FALLBACKS:
        for size in NEMO_TOOLBAR_REGULAR_SIZES:
            path = theme / f"{size}x{size}/actions/{name}.png"
            if not path.is_file():
                errors.append(f"missing Nemo regular toolbar fallback: {path.relative_to(theme)}")
                continue
            with Image.open(path) as image:
                if image.size != (size, size):
                    errors.append(
                        f"wrong Nemo toolbar fallback size {path.relative_to(theme)}: "
                        f"{image.width}x{image.height}"
                    )

    cache = subprocess.run(
        ["gtk-update-icon-cache", "-f", "-t", str(theme)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if cache.returncode:
        errors.append("gtk-update-icon-cache failed: " + cache.stdout.strip())

    manifest_path = theme / "manifest/icons.jsonl.xz"
    plain_manifest = theme / "manifest/icons.jsonl"
    if not manifest_path.exists() and not plain_manifest.exists():
        errors.append("per-file provenance manifest is missing")

    manifest_lines = None
    if plain_manifest.exists():
        manifest_lines = plain_manifest.read_text(encoding="utf-8").splitlines()
    elif manifest_path.exists():
        with lzma.open(manifest_path, "rt", encoding="utf-8") as handle:
            manifest_lines = handle.read().splitlines()

    if manifest_lines is not None:
        manifest_paths = {json.loads(line)["path"] for line in manifest_lines if line}
        untracked = sorted(actual_paths - manifest_paths)
        missing_assets = sorted(manifest_paths - actual_paths)
        if untracked:
            errors.append("untracked image files: " + ", ".join(untracked[:30]))
        if missing_assets:
            errors.append("manifest paths missing from theme: " + ", ".join(missing_assets[:30]))

    summary = json.loads((theme / "manifest/summary.json").read_text(encoding="utf-8"))
    if summary.get("installed_icon_files") != sum(counts.values()):
        errors.append(
            f"manifest count {summary.get('installed_icon_files')} differs from actual image count {sum(counts.values())}"
        )

    lines = [
        "# Release audit",
        "",
        f"Result: **{'PASS' if not errors else 'FAIL'}**",
        "",
        f"- Icon files: {sum(counts.values()):,}",
        f"- PNG: {counts['.png']:,}",
        f"- SVG: {counts['.svg']:,}",
        f"- XPM: {counts['.xpm']:,}",
        f"- Indexed directories: {len(listed_dirs):,}",
        f"- Unique names: {sum(len(value) for value in names.values()):,}",
        f"- Broken symlinks: {len(broken_links)}",
        f"- Hard-linked icon paths: {len(hardlinked_icons)}",
        f"- GTK cache build: {'pass' if cache.returncode == 0 else 'fail'}",
        "",
        "## Name coverage by context",
        "",
        "| Context | Unique names |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {category} | {len(category_names):,} |" for category, category_names in sorted(names.items()))
    if warnings:
        lines.extend(("", "## Warnings", ""))
        lines.extend(f"- {warning}" for warning in warnings)
    if errors:
        lines.extend(("", "## Errors", ""))
        lines.extend(f"- {error}" for error in errors[:100])
        if len(errors) > 100:
            lines.append(f"- …and {len(errors) - 100} more")

    parsed.report.parent.mkdir(parents=True, exist_ok=True)
    parsed.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:20]))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
