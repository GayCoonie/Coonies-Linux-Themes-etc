#!/usr/bin/env python3
"""Build Coonie's Aero Hoard from a deliberately unruly set of icon themes."""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


THEME_DIRNAME = "Coonie-Aero-Hoard"
THEME_NAME = "Coonie's Aero Hoard"
IMAGE_SUFFIXES = {".png", ".svg", ".xpm"}
SIZE_RE = re.compile(r"^(\d+)(?:x\1)?$")

CATEGORY_ALIASES = {
    "actions": "actions",
    "animations": "animations",
    "applets": "apps",
    "apps": "apps",
    "apps-extra": "apps",
    "apps-evolution": "apps",
    "categories": "categories",
    "devices": "devices",
    "emblems": "emblems",
    "emotes": "emotes",
    "filesystems": "places",
    "intl": "intl",
    "mimetypes": "mimetypes",
    "panel": "panel",
    "places": "places",
    "preferences": "categories",
    "status": "status",
    "stock": "actions",
    "symbolic": "symbolic",
}

CONTEXTS = {
    "actions": "Actions",
    "animations": "Animations",
    "apps": "Applications",
    "categories": "Categories",
    "devices": "Devices",
    "emblems": "Emblems",
    "emotes": "Emotes",
    "intl": "International",
    "mimetypes": "MimeTypes",
    "panel": "Status",
    "places": "Places",
    "status": "Status",
    "symbolic": "Status",
}

DEFAULT_WEIGHTS = {
    "ocd": 7,
    "crystal-remix": 6,
    "oxygen-refit": 5,
    "nuovext": 4,
    "gnome-colors": 3,
    "gnome-noble": 3,
    "newaita": 3,
}

CATEGORY_WEIGHTS = {
    "actions": {"ocd": 8, "crystal-remix": 6, "oxygen-refit": 8, "nuovext": 4, "gnome-colors": 4, "gnome-noble": 3, "newaita": 1},
    "apps": {"ocd": 5, "crystal-remix": 6, "oxygen-refit": 3, "nuovext": 5, "gnome-colors": 2, "gnome-noble": 2, "newaita": 8},
    "categories": {"ocd": 7, "crystal-remix": 7, "oxygen-refit": 5, "nuovext": 4, "gnome-colors": 4, "gnome-noble": 4, "newaita": 3},
    "devices": {"ocd": 8, "crystal-remix": 8, "oxygen-refit": 6, "nuovext": 4, "gnome-colors": 3, "gnome-noble": 3, "newaita": 2},
    "emblems": {"ocd": 7, "crystal-remix": 6, "oxygen-refit": 6, "nuovext": 4, "gnome-colors": 5, "gnome-noble": 5, "newaita": 2},
    "emotes": {"ocd": 8, "crystal-remix": 8, "oxygen-refit": 6, "nuovext": 5, "gnome-colors": 3, "gnome-noble": 3, "newaita": 2},
    "mimetypes": {"ocd": 8, "crystal-remix": 7, "oxygen-refit": 7, "nuovext": 5, "gnome-colors": 3, "gnome-noble": 3, "newaita": 2},
    "panel": {"newaita": 10, "ocd": 3, "crystal-remix": 2, "oxygen-refit": 2},
    "places": {"ocd": 8, "crystal-remix": 8, "oxygen-refit": 7, "nuovext": 6, "gnome-colors": 5, "gnome-noble": 7, "newaita": 3},
    "status": {"ocd": 7, "crystal-remix": 6, "oxygen-refit": 7, "nuovext": 5, "gnome-colors": 5, "gnome-noble": 5, "newaita": 3},
    "symbolic": {"newaita": 10, "gnome-colors": 3, "gnome-noble": 3},
}

FOLDER_SIZES = (16, 22, 24, 32, 40, 48, 64, 72, 96, 128, 256)
MINT_NEMO_PLACE_SIZES = (16, 22, 24, 32, 48, 64, 96, 128)
NEMO_TOOLBAR_REGULAR_SIZES = (16, 22, 24, 32, 48)
NEMO_TOOLBAR_REGULAR_FALLBACKS = ("go-previous", "edit-find")

# Nemo 6.0 (the file manager shipped with Mint 21.3) uses several names for
# the same directory depending on view, state, and whether GIO supplied a MIME
# icon. Keep these aliases in the same Crystal family so it cannot fall back
# to a visually unrelated modern folder.
CRYSTAL_FOLDER_ALIASES = {
    "folder-bookmarks": "folder-favorites",
    "folder-desktop": "user-desktop",
    "folder-drag-accept": "folder-download",
    "folder-empty": "folder",
    "folder-home": "user-home",
    "folder-new": "folder",
    "folder-open": "folder",
    "folder-publicshare": "folder-public",
    "folder-recent": "folder-favorites",
    "folder-saved-search": "folder-favorites",
    "folder-search": "folder-favorites",
    "folder-visiting": "folder",
}

# Crystal Remix contains native vertical variants for blue, green, grey, red,
# and yellow. These extra colors keep the same hard-edged, translucent Y2K
# silhouette while intentionally allowing a little candy-store unruliness.
TINTED_FOLDER_COLORS = {
    "aqua": ("#073b55", "#21d8d1", "#e7ffff"),
    "cyan": ("#063b73", "#20b9ff", "#e8fbff"),
    "seagreen": ("#064838", "#1fd09d", "#e7fff7"),
    "teal": ("#073d48", "#27b8b1", "#e9ffff"),
    "purple": ("#28105f", "#9158ed", "#f2eaff"),
    "pink": ("#651044", "#f05aaa", "#fff0fa"),
    "orange": ("#743412", "#f29428", "#fff0d6"),
    "brown": ("#40251d", "#9b6447", "#f3dfd1"),
    "black": ("#080b12", "#333b4d", "#d7e6f5"),
    "white": ("#526b85", "#b3d5e6", "#ffffff"),
}

MINT_ALIASES = {
    "apps": {
        "cinnamon": "preferences-desktop",
        "cinnamon-settings": "preferences-system",
        "org.cinnamon.Settings": "preferences-system",
        "nemo": "system-file-manager",
        "org.cinnamon.Nemo": "system-file-manager",
        "xed": "accessories-text-editor",
        "pix": "applications-graphics",
        "mintinstall": "system-software-install",
        "mintupdate": "system-software-update",
        "mintbackup": "drive-harddisk",
        "mintdrivers": "preferences-system",
        "mintreport": "dialog-information",
        "mintwelcome": "start-here",
        "mintstick": "drive-removable-media-usb",
        "lightdm-settings": "preferences-system-login",
        "hypnotix": "video-television",
        "warpinator": "folder-remote",
        "sticky": "accessories-text-editor",
        "webapp-manager": "internet-web-browser",
        "bulky": "edit-rename",
        "thingy": "x-office-document",
        "blueberry": "preferences-system-bluetooth",
        "timeshift": "document-revert",
        "celluloid": "multimedia-video-player",
        "drawing": "applications-graphics",
    }
}


@dataclass(frozen=True)
class Asset:
    source: str
    root: Path
    path: Path
    relative: str
    category: str
    name: str
    size: str
    suffix: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    return parser.parse_args()


def source_roots(sources: Path) -> dict[str, Path]:
    return {
        "ocd": sources / "ocd/usr/share/icons/ocd",
        "crystal-remix": sources / "crystal-remix",
        "oxygen-refit": sources / "oxygenrefit2-gitlab",
        "nuovext": sources / "nuovext/nuoveXT23",
        "gnome-colors": sources / "gnome-colors/gnome-colors/gnome-colors-common",
        "gnome-noble": sources / "gnome-colors/gnome-colors/gnome-noble",
        "newaita": sources / "newaita-reborn/Newaita-reborn",
        "papirus": sources / "papirus/Papirus",
    }


def normalize_size(token: str) -> str | None:
    if token == "scalable" or token == "symbolic":
        return "scalable"
    match = SIZE_RE.match(token)
    if not match:
        return None
    number = int(match.group(1))
    return f"{number}x{number}"


def classify(root: Path, path: Path, source: str) -> Asset | None:
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        return None
    parts = relative_path.parts
    if len(parts) < 3 or path.suffix.lower() not in IMAGE_SUFFIXES:
        return None

    category = None
    size = None
    for part in parts[:-1]:
        if category is None and part in CATEGORY_ALIASES:
            category = CATEGORY_ALIASES[part]
        if size is None:
            size = normalize_size(part)
    if not category or not size:
        return None
    if category == "symbolic":
        category = "symbolic"
    elif "symbolic" in parts[:-1]:
        category = "symbolic"
        size = "scalable"

    try:
        resolved = path.resolve(strict=True)
    except (FileNotFoundError, RuntimeError):
        return None
    if not resolved.is_file():
        return None

    return Asset(
        source=source,
        root=root,
        path=resolved,
        relative=str(relative_path),
        category=category,
        name=path.stem,
        size=size,
        suffix=path.suffix.lower(),
    )


def index_sources(roots: dict[str, Path]) -> tuple[dict[tuple[str, str], dict[str, list[Asset]]], Counter]:
    indexed: dict[tuple[str, str], dict[str, list[Asset]]] = defaultdict(lambda: defaultdict(list))
    counts: Counter = Counter()
    for source, root in roots.items():
        if not root.is_dir():
            raise SystemExit(f"missing source tree: {root}")
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [name for name in dirnames if not name.startswith(".") and name not in {"Extra", "extra"}]
            base = Path(dirpath)
            for filename in filenames:
                if filename.startswith("."):
                    continue
                asset = classify(root, base / filename, source)
                if asset:
                    indexed[(asset.category, asset.name)][source].append(asset)
                    counts[source] += 1
    return indexed, counts


def numeric_size(size: str) -> int:
    return 512 if size == "scalable" else int(size.split("x", 1)[0])


def preferred_sources(category: str, candidates: dict[str, list[Asset]]) -> list[str]:
    aesthetic = [source for source in candidates if source != "papirus"]
    if not aesthetic:
        return ["papirus"] if "papirus" in candidates else []

    if category in {"apps", "categories", "devices", "emblems", "mimetypes", "places"}:
        large = [
            source
            for source in aesthetic
            if any(numeric_size(asset.size) >= 48 for asset in candidates[source])
        ]
        if large:
            aesthetic = large
    return aesthetic


def choose_source(category: str, name: str, candidates: dict[str, list[Asset]]) -> str:
    sources = preferred_sources(category, candidates)
    if not sources:
        raise RuntimeError(f"no candidate for {category}/{name}")
    if len(sources) == 1:
        return sources[0]

    weights = CATEGORY_WEIGHTS.get(category, DEFAULT_WEIGHTS)
    weighted = [(source, max(1, weights.get(source, DEFAULT_WEIGHTS.get(source, 1)))) for source in sorted(sources)]
    total = sum(weight for _, weight in weighted)
    value = int.from_bytes(hashlib.blake2b(f"{category}/{name}".encode(), digest_size=8).digest(), "big") % total
    for source, weight in weighted:
        if value < weight:
            return source
        value -= weight
    return weighted[-1][0]


def choose_assets(assets: list[Asset]) -> list[Asset]:
    by_size: dict[str, list[Asset]] = defaultdict(list)
    for asset in assets:
        by_size[asset.size].append(asset)
    selected = []
    for size, options in sorted(by_size.items(), key=lambda item: numeric_size(item[0])):
        def preference(asset: Asset) -> tuple[int, int, str]:
            if size == "scalable":
                ext_rank = {".svg": 0, ".png": 1, ".xpm": 2}.get(asset.suffix, 3)
            else:
                ext_rank = {".png": 0, ".svg": 1, ".xpm": 2}.get(asset.suffix, 3)
            return ext_rank, len(asset.relative), asset.relative

        selected.append(sorted(options, key=preference)[0])
    return selected


class Copier:
    def __init__(self, theme_root: Path):
        self.theme_root = theme_root
        self.manifest: dict[str, dict[str, str]] = {}

    def install_bytes(self, data: bytes, relative: Path, source: str, source_path: str) -> None:
        target = self.theme_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        digest = hashlib.sha256(data).hexdigest()
        # Keep every installed path independent. Hard-link deduplication made
        # later size sanitation ambiguous when a malformed legacy sprite and a
        # valid alias happened to share bytes.
        target.write_bytes(data)
        self.manifest[str(relative)] = {
            "path": str(relative),
            "source": source,
            "source_path": source_path,
            "sha256": digest,
        }

    def install_file(self, source_file: Path, relative: Path, source: str, source_path: str) -> None:
        data = source_file.read_bytes()
        if source_file.suffix.lower() == ".svg":
            try:
                ET.fromstring(data)
            except ET.ParseError:
                marker_start = data.find(b"<!--\n<!-- Creative Commons Public Domain")
                marker_end = data.find(b"\n-->\n<svg", marker_start)
                if marker_start >= 0 and marker_end >= 0:
                    replacement = (
                        b"<!-- Legacy public-domain metadata was malformed by nested XML comments; "
                        b"the upstream file and attribution are recorded in the provenance manifest. -->"
                    )
                    data = data[:marker_start] + replacement + data[marker_end + 5 :]
                    ET.fromstring(data)
                else:
                    raise
        self.install_bytes(data, relative, source, source_path)


def remove_icon(copier: Copier, category: str, name: str) -> None:
    for path in copier.theme_root.glob(f"*/{category}/{name}.*"):
        if path.is_file():
            path.unlink()
            copier.manifest.pop(str(path.relative_to(copier.theme_root)), None)


def render_svg(svg: Path, output: Path, size: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["inkscape", str(svg), f"--export-filename={output}", f"--export-width={size}", f"--export-height={size}"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def crystal_rasters(crystal_root: Path, name: str) -> dict[int, Path]:
    rasters = {}
    for path in crystal_root.glob(f"*x*/places/{name}.png"):
        size = normalize_size(path.parent.parent.name)
        if size:
            rasters[numeric_size(size)] = path
    return rasters


def nearest_raster(rasters: dict[int, Path], size: int) -> Path:
    if not rasters:
        raise RuntimeError("no Crystal raster candidates")
    return rasters[min(rasters, key=lambda candidate: (abs(candidate - size), -candidate))]


def render_folder_png(source: Path, output: Path, size: int, tint: tuple[str, str, str] | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = opened.convert("RGBA")
    if tint:
        alpha = image.getchannel("A")
        luminance = ImageOps.grayscale(image.convert("RGB"))
        image = ImageOps.colorize(
            luminance,
            black=tint[0],
            mid=tint[1],
            white=tint[2],
            midpoint=122,
        ).convert("RGBA")
        image.putalpha(alpha)
    if image.size != (size, size):
        image = image.resize((size, size), Image.Resampling.LANCZOS)
    image.save(output, format="PNG", optimize=True)


def install_crystal_icon(
    copier: Copier,
    sources: Path,
    work: Path,
    crystal_root: Path,
    source_name: str,
    target_name: str,
    category: str = "places",
    tint: tuple[str, str, str] | None = None,
) -> None:
    rasters = crystal_rasters(crystal_root, source_name)
    if not rasters:
        raise RuntimeError(f"Crystal Remix is missing places/{source_name}.png")
    remove_icon(copier, category, target_name)
    for size in FOLDER_SIZES:
        source = nearest_raster(rasters, size)
        relative = Path(f"{size}x{size}/{category}/{target_name}.png")
        if not tint and source == rasters.get(size):
            copier.install_file(source, relative, "crystal-remix-folder-layer", str(source.relative_to(sources)))
        else:
            rendered = work / category / f"{target_name}-{size}.png"
            render_folder_png(source, rendered, size, tint)
            provenance = "crystal-remix-folder-tint" if tint else "crystal-remix-folder-resize"
            copier.install_file(rendered, relative, provenance, str(source.relative_to(sources)))


def install_crystal_folders(copier: Copier, sources: Path, work: Path) -> set[str]:
    crystal_root = sources / "crystal-remix"
    native_names = sorted({path.stem for path in crystal_root.glob("*x*/places/folder*.png")})
    installed = set(native_names)

    # Make the whole folder family vertical and crystalline, not just the one
    # generic icon seen in an icon-grid view.
    for name in native_names:
        install_crystal_icon(copier, sources, work, crystal_root, name, name)

    # Crystal's home/desktop/network/trash objects are part of the same older,
    # glossy vocabulary and remain readable in Nemo's compact sidebar.
    for name in ("network-workgroup", "user-desktop", "user-home", "user-trash", "user-trash-full"):
        install_crystal_icon(copier, sources, work, crystal_root, name, name)
        installed.add(name)

    for alias, target in sorted(CRYSTAL_FOLDER_ALIASES.items()):
        install_crystal_icon(copier, sources, work, crystal_root, target, alias)
        installed.add(alias)

    # GIO can hand Nemo inode-directory instead of folder. Install it in both
    # standard contexts so generic directories cannot change silhouette between
    # list, compact, icon-grid, and desktop views.
    for category in ("places", "mimetypes"):
        install_crystal_icon(copier, sources, work, crystal_root, "folder", "inode-directory", category)

    for color, tint in sorted(TINTED_FOLDER_COLORS.items()):
        name = f"folder-{color}"
        install_crystal_icon(copier, sources, work, crystal_root, "folder", name, tint=tint)
        installed.add(name)

    return installed


def install_mint_nemo_places(copier: Copier, folder_names: set[str]) -> int:
    """Duplicate the folder layer in Mint-Y's category-first Places layout."""
    names = set(folder_names) | {"inode-directory"}
    count = 0
    for size in MINT_NEMO_PLACE_SIZES:
        for name in sorted(names):
            source = copier.theme_root / f"{size}x{size}/places/{name}.png"
            if not source.is_file():
                continue
            target = Path(f"places/{size}/{name}.png")
            copier.install_file(source, target, "mint-nemo-places-compat", f"alias:{size}x{size}/places/{name}")
            count += 1
    return count


def install_nemo_toolbar_regular_fallbacks(copier: Copier, work: Path) -> int:
    """Give Nemo exact small regular icons when GTK strips `-symbolic`.

    Mint 21.3's Nemo asks for go-previous-symbolic and edit-find-symbolic, but
    a GTK theme may deliberately request their full-color regular counterparts.
    The donor mosaic only has those two regular names at 128px, which lets the
    unscaled legacy artwork determine the toolbar's natural height. Preserve the
    same glossy art while supplying the fixed sizes GTK expects for buttons.
    """
    count = 0
    for name in NEMO_TOOLBAR_REGULAR_FALLBACKS:
        source = copier.theme_root / f"128x128/actions/{name}.png"
        if not source.is_file():
            raise RuntimeError(f"missing 128px Nemo toolbar donor: actions/{name}.png")
        with Image.open(source) as opened:
            image = opened.convert("RGBA")
        for size in NEMO_TOOLBAR_REGULAR_SIZES:
            rendered = work / "nemo-toolbar" / f"{size}x{size}" / f"{name}.png"
            rendered.parent.mkdir(parents=True, exist_ok=True)
            image.resize((size, size), Image.Resampling.LANCZOS).save(
                rendered, format="PNG", optimize=True
            )
            relative = Path(f"{size}x{size}/actions/{name}.png")
            copier.install_file(
                rendered,
                relative,
                "mint-21.3-nemo-toolbar-regular-fallback",
                f"scaled:128x128/actions/{name}.png",
            )
            count += 1
    return count


def sanitize_legacy_rasters(copier: Copier, work: Path) -> Counter:
    """Prevent mislabeled legacy PNGs from escaping their advertised GTK size."""
    counts = Counter()
    for path in sorted(copier.theme_root.rglob("*.png")):
        relative = path.relative_to(copier.theme_root)
        if len(relative.parts) < 3:
            continue
        size = normalize_size(relative.parts[0])
        category = relative.parts[1]
        if not size or size == "scalable":
            continue
        declared = numeric_size(size)
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
        width, height = image.size

        # The old OCD checkout includes raw sprite strips but no animation
        # metadata. GTK/Nemo can display the whole strip as one enormous icon.
        if category == "animations" and (width, height) != (declared, declared):
            path.unlink()
            copier.manifest.pop(str(relative), None)
            counts["removed_unindexed_animation_strips"] += 1
            continue

        if width <= declared and height <= declared:
            continue

        aspect = max(width / max(1, height), height / max(1, width))
        if aspect > 4:
            path.unlink()
            copier.manifest.pop(str(relative), None)
            counts["removed_static_sprite_strips"] += 1
            continue

        image.thumbnail((declared, declared), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (declared, declared), (0, 0, 0, 0))
        canvas.alpha_composite(image, ((declared - image.width) // 2, (declared - image.height) // 2))
        rendered = work / "sanitized" / relative
        rendered.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(rendered, format="PNG", optimize=True)
        prior = copier.manifest.get(str(relative), {})
        copier.install_file(
            rendered,
            relative,
            "normalized-legacy-raster",
            prior.get("source_path", str(relative)),
        )
        counts["resized_oversized_static_pngs"] += 1

    # Finish with a no-write purge after every normalization install is complete
    # so later builder changes cannot accidentally leave a strip behind.
    for path in sorted(copier.theme_root.rglob("*.png")):
        relative = path.relative_to(copier.theme_root)
        if len(relative.parts) < 3:
            continue
        size = normalize_size(relative.parts[0])
        category = relative.parts[1]
        if not size or size == "scalable":
            continue
        declared = numeric_size(size)
        with Image.open(path) as opened:
            width, height = opened.size
        aspect = max(width / max(1, height), height / max(1, width))
        unsafe_animation = category == "animations" and (width, height) != (declared, declared)
        unsafe_static = (width > declared or height > declared) and aspect > 4
        if unsafe_animation or unsafe_static:
            path.unlink(missing_ok=True)
            copier.manifest.pop(str(relative), None)
            counts["final_hardlink_purge"] += 1

    return counts


def find_icon_files(theme_root: Path, category: str, name: str) -> list[Path]:
    return sorted(path for path in theme_root.glob(f"*/{category}/{name}.*") if path.is_file())


def clone_icon(copier: Copier, category: str, source_name: str, alias_name: str, provenance: str) -> int:
    if source_name == alias_name:
        return 0
    source_files = find_icon_files(copier.theme_root, category, source_name)
    count = 0
    for source_file in source_files:
        relative = source_file.relative_to(copier.theme_root)
        alias_relative = relative.with_name(f"{alias_name}{source_file.suffix}")
        copier.install_file(source_file, alias_relative, provenance, f"alias:{category}/{source_name}")
        count += 1
    return count


def add_mint_aliases(copier: Copier) -> Counter:
    counts = Counter()
    for category, aliases in MINT_ALIASES.items():
        for alias, target in aliases.items():
            if find_icon_files(copier.theme_root, category, alias):
                continue
            copied = clone_icon(copier, category, target, alias, "mint-cinnamon-alias")
            if not copied:
                for fallback_category in ("categories", "places", "actions", "devices", "status", "mimetypes"):
                    copied = clone_icon(copier, fallback_category, target, alias, "mint-cinnamon-alias")
                    if copied:
                        break
            counts[alias] = copied
    return counts


def write_index(theme_root: Path) -> list[str]:
    dirs = []

    # Linux Mint's own Mint-Y theme exposes Places with category-first paths.
    # List these first so Nemo 5.8/6.0 receives exact fixed-size candidates.
    places_root = theme_root / "places"
    if places_root.is_dir():
        for size_dir in sorted(places_root.iterdir(), key=lambda path: numeric_size(path.name)):
            if size_dir.is_dir() and normalize_size(size_dir.name):
                if any(path.suffix.lower() in IMAGE_SUFFIXES for path in size_dir.iterdir() if path.is_file()):
                    dirs.append(f"places/{size_dir.name}")

    size_roots = (
        path
        for path in theme_root.iterdir()
        if path.is_dir() and (path.name == "scalable" or SIZE_RE.match(path.name))
    )
    for size_dir in sorted(size_roots, key=lambda path: (numeric_size(path.name), path.name)):
        for category_dir in sorted(path for path in size_dir.iterdir() if path.is_dir()):
            if any(path.suffix.lower() in IMAGE_SUFFIXES for path in category_dir.iterdir() if path.is_file()):
                dirs.append(f"{size_dir.name}/{category_dir.name}")

    lines = [
        "[Icon Theme]",
        f"Name={THEME_NAME}",
        "Comment=A maximal Y2K/Frutiger-aero mosaic with vertical Crystal folders and exhaustive Nemo coverage",
        "Example=folder",
        "DisplayDepth=32",
        "Inherits=hicolor,Adwaita",
        "Hidden=false",
        "DesktopDefault=48",
        "DesktopSizes=16,22,24,32,48,64,72,84,96,128,256",
        "ToolbarDefault=22",
        "ToolbarSizes=16,22,24,32,48",
        "MainToolbarDefault=24",
        "MainToolbarSizes=16,22,24,32,48",
        "SmallDefault=16",
        "SmallSizes=8,16,18,22,24,32",
        "PanelDefault=24",
        "PanelSizes=16,18,22,24,32,42,48,64,84,96,128",
        "DialogDefault=48",
        "DialogSizes=16,22,24,32,48,64,72,84,96,128,256",
        "Directories=" + ",".join(dirs),
        "",
    ]

    for directory in dirs:
        first, second = directory.split("/", 1)
        if normalize_size(first):
            size_token, category = first, second
        else:
            category, size_token = first, second
        lines.append(f"[{directory}]")
        lines.append(f"Context={CONTEXTS.get(category, 'Applications')}")
        if size_token == "scalable":
            lines.extend(("Size=128", "Type=Scalable", "MinSize=8", "MaxSize=512"))
        else:
            size = int(size_token.split("x", 1)[0])
            lines.extend((f"Size={size}", "Type=Fixed"))
        lines.append("")

    (theme_root / "index.theme").write_text("\n".join(lines), encoding="utf-8")
    return dirs


def copy_licenses(project_root: Path, sources: Path, theme_root: Path) -> None:
    destination = theme_root / "licenses"
    destination.mkdir(parents=True, exist_ok=True)
    license_files = {
        "OCD-LICENSE.txt": sources / "ocd/usr/share/icons/ocd/LICENSE",
        "OCD-README.txt": sources / "ocd/README.md",
        "OxygenRefit2-LGPL-3.0.txt": sources / "oxygenrefit2-gitlab/COPYING.LGPL",
        "OxygenRefit2-CREDITS.txt": sources / "oxygenrefit2-gitlab/CREDITS",
        "NuoveXT-LGPL-3.0.txt": sources / "nuovext/COPYING",
        "GNOME-Colors-GPL-2.0.txt": sources / "gnome-colors/gnome-colors/COPYING",
        "Newaita-Reborn-GPL-3.0.txt": sources / "newaita-reborn/LICENSE",
        "Papirus-GPL-3.0.txt": sources / "papirus/LICENSE",
        "Crystal-Remix-README.txt": sources / "crystal-remix/README.md",
    }
    for name, path in license_files.items():
        if path.exists():
            shutil.copy2(path, destination / name)
    shutil.copy2(project_root / "SOURCE-AND-LICENSES.md", theme_root / "SOURCE-AND-LICENSES.md")
    shutil.copy2(project_root / "README.md", theme_root / "README.md")
    shutil.copy2(project_root / "CHANGELOG.md", theme_root / "CHANGELOG.md")


def validate_index(theme_root: Path, directories: list[str]) -> None:
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    parser.read(theme_root / "index.theme", encoding="utf-8")
    listed = parser["Icon Theme"]["Directories"].split(",")
    if listed != directories:
        raise SystemExit("index.theme directory list does not match generated directories")
    for directory in listed:
        if directory not in parser or not (theme_root / directory).is_dir():
            raise SystemExit(f"invalid index.theme directory: {directory}")


def main() -> None:
    args = parse_args()
    sources = args.sources.resolve()
    output = args.output.resolve()
    project_root = args.project_root.resolve()
    theme_root = output / THEME_DIRNAME
    work = output / ".render-work"
    if output.exists():
        shutil.rmtree(output)
    theme_root.mkdir(parents=True)
    work.mkdir(parents=True)

    roots = source_roots(sources)
    indexed, indexed_counts = index_sources(roots)
    copier = Copier(theme_root)
    chosen_donors: Counter = Counter()

    for (category, name), candidates in sorted(indexed.items()):
        source = choose_source(category, name, candidates)
        chosen_donors[source] += 1
        for asset in choose_assets(candidates[source]):
            relative = Path(asset.size) / category / f"{name}{asset.suffix}"
            copier.install_file(asset.path, relative, source, asset.relative)

    crystal_folder_names = install_crystal_folders(copier, sources, work)
    alias_counts = add_mint_aliases(copier)
    mint_nemo_places_files = install_mint_nemo_places(copier, crystal_folder_names)
    nemo_toolbar_regular_files = install_nemo_toolbar_regular_fallbacks(copier, work)
    raster_safety = sanitize_legacy_rasters(copier, work)
    directories = write_index(theme_root)
    copy_licenses(project_root, sources, theme_root)
    validate_index(theme_root, directories)
    shutil.rmtree(work)

    actual_icon_paths = {
        str(path.relative_to(theme_root))
        for path in theme_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_SUFFIXES
        and not ({"licenses", "manifest"} & set(path.relative_to(theme_root).parts))
    }
    tracked_icon_paths = set(copier.manifest)
    if actual_icon_paths != tracked_icon_paths:
        untracked = sorted(actual_icon_paths - tracked_icon_paths)
        missing = sorted(tracked_icon_paths - actual_icon_paths)
        raise SystemExit(f"provenance mismatch: untracked={untracked[:20]} missing={missing[:20]}")

    manifest_dir = theme_root / "manifest"
    manifest_dir.mkdir()
    with (manifest_dir / "icons.jsonl").open("w", encoding="utf-8") as handle:
        for row in sorted(copier.manifest.values(), key=lambda row: row["path"]):
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    installed_counts = Counter(row["source"] for row in copier.manifest.values())

    summary = {
        "theme": THEME_NAME,
        "theme_directory": THEME_DIRNAME,
        "indexed_assets_by_source": dict(sorted(indexed_counts.items())),
        "icon_names_selected_by_source": dict(sorted(chosen_donors.items())),
        "installed_files_by_source": dict(sorted(installed_counts.items())),
        "mint_alias_files": dict(sorted(alias_counts.items())),
        "mint_nemo_places_files": mint_nemo_places_files,
        "nemo_toolbar_regular_files": nemo_toolbar_regular_files,
        "raster_size_safety": dict(sorted(raster_safety.items())),
        "indexed_icon_names": len(indexed),
        "installed_icon_files": len(copier.manifest),
        "index_directories": len(directories),
        "crystal_folder_names": sorted(crystal_folder_names),
        "nemo_6_folder_layer": True,
    }
    (manifest_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
