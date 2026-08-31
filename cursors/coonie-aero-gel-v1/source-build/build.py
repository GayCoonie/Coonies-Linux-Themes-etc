#!/usr/bin/env python3
"""Build the Coonie Aero Gel XCursor theme from its two generated atlases.

ImageMagick performs all atlas slicing, normalization, compositing, and preview
work.  The small XCursor writer keeps the project rebuildable on systems where
the optional `xcursorgen` utility is not installed.
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
WORK = ROOT / "work"
THEME = ROOT / "dist" / "Coonie-Aero-Gel"
CURSORS = THEME / "cursors"
SIZES = (24, 32, 48, 64)

ATLAS_NAMES = (
    "left_ptr", "pointer", "crosshair", "text",
    "move", "ns-resize", "ew-resize", "nwse-resize",
    "nesw-resize", "not-allowed", "help", "grab",
    "grabbing", "copy", "link", "pencil",
)

# Hotspots are fractions of the final canvas.  Arrow-derived roles use the
# visible point; symmetric roles use their center.
HOTSPOTS = {
    "left_ptr": (.17, .14), "pointer": (.51, .10),
    "crosshair": (.50, .50), "text": (.50, .50),
    "move": (.50, .50), "ns-resize": (.50, .50),
    "ew-resize": (.50, .50), "nwse-resize": (.50, .50),
    "nesw-resize": (.50, .50), "not-allowed": (.50, .50),
    "help": (.15, .14), "grab": (.50, .48),
    "grabbing": (.50, .48), "copy": (.16, .14),
    "link": (.16, .14), "pencil": (.17, .14),
    "wait": (.50, .50), "progress": (.17, .14),
}

ALIASES = {
    "left_ptr": (
        "default", "arrow", "top_left_arrow", "X_cursor",
        "00008160000006810000408080010102",
    ),
    "pointer": (
        "hand", "hand1", "hand2", "link_select",
        "9d800788f1b08800ae810202380a0822",
        "e29285e634086352946a0e7090d73106",
    ),
    "crosshair": ("cross", "cross_reverse", "cell", "tcross"),
    "text": ("xterm", "ibeam", "vertical-text"),
    "move": ("fleur", "size_all", "all-scroll", "dnd-move"),
    "ns-resize": (
        "n-resize", "s-resize", "top_side", "bottom_side",
        "sb_v_double_arrow", "row-resize", "v_double_arrow",
    ),
    "ew-resize": (
        "e-resize", "w-resize", "left_side", "right_side",
        "sb_h_double_arrow", "col-resize", "h_double_arrow",
    ),
    "nwse-resize": (
        "nw-resize", "se-resize", "top_left_corner",
        "bottom_right_corner", "fd_double_arrow",
    ),
    "nesw-resize": (
        "ne-resize", "sw-resize", "top_right_corner",
        "bottom_left_corner", "bd_double_arrow",
    ),
    "not-allowed": (
        "forbidden", "no-drop", "crossed_circle",
        "03b6e0fcb3499374a867c041f52298f0",
    ),
    "help": ("question_arrow", "whats_this", "context-menu"),
    "grab": ("openhand", "open_hand"),
    "grabbing": ("closedhand", "closed_hand"),
    "copy": (
        "dnd-copy", "plus", "1081e37283d90000800003c07f3ef6bf",
        "08e8e1c95fe2fc01f976f1e063a24ccd",
    ),
    "link": (
        "dnd-link", "alias", "6407b0e94181790501fd1e167b474872",
    ),
    "pencil": ("draft", "color-picker"),
    "wait": ("watch",),
    "progress": ("left_ptr_watch", "half-busy"),
}


def run(*args: str | Path) -> None:
    subprocess.run([str(a) for a in args], check=True)


def imagemagick(*args: str | Path) -> None:
    run("convert", *args)


def prepare_dirs() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    if THEME.exists():
        shutil.rmtree(THEME)
    (WORK / "tiles").mkdir(parents=True)
    (WORK / "frames").mkdir(parents=True)
    CURSORS.mkdir(parents=True)


def split_atlases() -> None:
    atlas = SOURCE / "cursor-atlas.png"
    busy = SOURCE / "busy-atlas.png"
    if not atlas.exists() or not busy.exists():
        raise SystemExit("Missing source/cursor-atlas.png or source/busy-atlas.png")

    # The generated masters are off by two pixels from exact cell multiples.
    # Normalizing once makes every subsequent crop mathematically exact.
    normalized = WORK / "cursor-atlas-1256.png"
    imagemagick(atlas, "-filter", "Lanczos", "-resize", "1256x1256!", normalized)
    for i, name in enumerate(ATLAS_NAMES):
        x, y = (i % 4) * 314, (i // 4) * 314
        imagemagick(normalized, "-crop", f"314x314+{x}+{y}", "+repage",
                    WORK / "tiles" / f"{name}.png")

    normalized_busy = WORK / "busy-atlas-1776.png"
    imagemagick(busy, "-filter", "Lanczos", "-resize", "1776x888!", normalized_busy)
    for i in range(8):
        x, y = (i % 4) * 444, (i // 4) * 444
        imagemagick(normalized_busy, "-crop", f"444x444+{x}+{y}", "+repage",
                    WORK / "frames" / f"wait-{i:02}.png")


def normalize(source: Path, destination: Path, size: int, occupancy: float = .91) -> None:
    inner = max(8, round(size * occupancy))
    imagemagick(
        source, "-trim", "+repage", "-filter", "Lanczos",
        "-resize", f"{inner}x{inner}", "-gravity", "center",
        "-background", "none", "-extent", f"{size}x{size}", destination,
    )


def composite_progress(size: int, destination: Path) -> None:
    arrow = WORK / "rendered" / f"left_ptr-{size}.png"
    spinner = WORK / "rendered" / f"wait-00-{size}.png"
    small = WORK / "rendered" / f"wait-small-{size}.png"
    imagemagick(spinner, "-filter", "Lanczos", "-resize", f"{size // 2}x{size // 2}", small)
    imagemagick(
        "-size", f"{size}x{size}", "xc:none",
        arrow, "-gravity", "northwest", "-composite",
        small, "-gravity", "southeast", "-geometry", "+0+0", "-composite",
        destination,
    )


def rgba_to_argb32(path: Path) -> tuple[int, int, bytes]:
    image = Image.open(path).convert("RGBA")
    out = bytearray()
    for r, g, b, a in image.get_flattened_data():
        # XCursor stores premultiplied ARGB words.  Packing a uint32 little-endian
        # yields byte order BB GG RR AA on the Linux machines consuming the file.
        pr = (r * a + 127) // 255
        pg = (g * a + 127) // 255
        pb = (b * a + 127) // 255
        out += struct.pack("<I", (a << 24) | (pr << 16) | (pg << 8) | pb)
    return image.width, image.height, bytes(out)


def write_xcursor(destination: Path, frames: list[tuple[int, Path, int, int, int]]) -> None:
    """Write XCursor 1.0 image chunks.

    frames: (nominal_size, png_path, xhot, yhot, delay_ms)
    """
    image_type = 0xFFFD0002
    entries = []
    for nominal, path, xhot, yhot, delay in frames:
        width, height, pixels = rgba_to_argb32(path)
        entries.append((nominal, width, height, xhot, yhot, delay, pixels))

    toc_end = 16 + 12 * len(entries)
    positions = []
    position = toc_end
    for _, width, height, *_ in entries:
        positions.append(position)
        position += 36 + 4 * width * height

    with destination.open("wb") as f:
        f.write(struct.pack("<4I", 0x72756358, 16, 0x00010000, len(entries)))
        for (entry, pos) in zip(entries, positions):
            nominal = entry[0]
            f.write(struct.pack("<3I", image_type, nominal, pos))
        for nominal, width, height, xhot, yhot, delay, pixels in entries:
            f.write(struct.pack("<9I", 36, image_type, nominal, 1,
                                width, height, xhot, yhot, delay))
            f.write(pixels)


def build_cursors() -> None:
    rendered = WORK / "rendered"
    rendered.mkdir()

    for name in ATLAS_NAMES:
        for size in SIZES:
            normalize(WORK / "tiles" / f"{name}.png",
                      rendered / f"{name}-{size}.png", size)

    for frame in range(8):
        for size in SIZES:
            normalize(WORK / "frames" / f"wait-{frame:02}.png",
                      rendered / f"wait-{frame:02}-{size}.png", size, .88)

    for size in SIZES:
        composite_progress(size, rendered / f"progress-{size}.png")

    for name in ATLAS_NAMES:
        hx, hy = HOTSPOTS[name]
        records = []
        for size in SIZES:
            records.append((size, rendered / f"{name}-{size}.png",
                            min(size - 1, round(size * hx)),
                            min(size - 1, round(size * hy)), 0))
        write_xcursor(CURSORS / name, records)

    wait_records = []
    for size in SIZES:
        for frame in range(8):
            wait_records.append((size, rendered / f"wait-{frame:02}-{size}.png",
                                 size // 2, size // 2, 75))
    write_xcursor(CURSORS / "wait", wait_records)

    progress_records = []
    for size in SIZES:
        hx, hy = HOTSPOTS["progress"]
        progress_records.append((size, rendered / f"progress-{size}.png",
                                 round(size * hx), round(size * hy), 0))
    write_xcursor(CURSORS / "progress", progress_records)


def make_aliases() -> None:
    for target, names in ALIASES.items():
        for name in names:
            alias = CURSORS / name
            if alias.exists() or alias.is_symlink():
                alias.unlink()
            os.symlink(target, alias)


def write_theme_metadata() -> None:
    (THEME / "index.theme").write_text(
        "[Icon Theme]\n"
        "Name=Coonie Aero Gel\n"
        "Comment=Glossy purple, sea-green and hot-pink Y2K/Frutiger Aero cursors\n"
        "Inherits=DMZ-White\n",
        encoding="utf-8",
    )
    shutil.copy2(ROOT / "THEME-README.md", THEME / "README.md")
    install = THEME / "install.sh"
    shutil.copy2(ROOT / "install.sh", install)
    install.chmod(0o755)


def make_preview() -> None:
    preview = ROOT / "dist" / "Coonie-Aero-Gel-preview.png"
    sources = [WORK / "rendered" / f"{name}-64.png" for name in ATLAS_NAMES]
    sources += [WORK / "rendered" / "wait-00-64.png", WORK / "rendered" / "progress-64.png"]
    run("montage", *sources, "-tile", "6x3", "-geometry", "96x96+10+10",
        "-background", "#160b25", preview)


def main() -> None:
    prepare_dirs()
    split_atlases()
    build_cursors()
    make_aliases()
    write_theme_metadata()
    make_preview()
    print(f"Built {THEME}")


if __name__ == "__main__":
    main()
