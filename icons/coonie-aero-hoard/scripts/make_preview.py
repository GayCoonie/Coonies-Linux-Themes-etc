#!/usr/bin/env python3
"""Render a contact sheet for the finished icon theme."""

from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SAMPLES = [
    ("places", "folder", "generic folder"),
    ("places", "folder-open", "open state"),
    ("places", "folder-drag-accept", "drop target"),
    ("places", "folder-download", "downloads"),
    ("places", "folder-documents", "documents"),
    ("places", "folder-music", "music"),
    ("places", "folder-pictures", "pictures"),
    ("places", "folder-videos", "videos"),
    ("mimetypes", "inode-directory", "GIO directory"),
    ("places", "folder-aqua", "aqua folder"),
    ("places", "folder-purple", "purple folder"),
    ("places", "folder-pink", "pink folder"),
    ("places", "user-home", "home"),
    ("places", "user-desktop", "desktop"),
    ("status", "avatar-default", "kept: user"),
    ("apps", "system-file-manager", "Nemo"),
    ("apps", "internet-web-browser", "web"),
    ("apps", "utilities-terminal", "terminal"),
    ("apps", "preferences-system", "settings"),
    ("devices", "computer", "computer"),
    ("devices", "drive-harddisk", "hard disk"),
    ("devices", "camera-photo", "camera"),
    ("mimetypes", "application-pdf", "PDF"),
    ("status", "dialog-warning", "warning"),
]


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("theme", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def find_icon(theme: Path, category: str, name: str) -> Path | None:
    sizes = ("256x256", "128x128", "96x96", "84x84", "64x64", "48x48", "scalable", "32x32")
    for size in sizes:
        for suffix in (".png", ".svg", ".xpm"):
            path = theme / size / category / f"{name}{suffix}"
            if path.is_file():
                return path
    return None


def load_icon(path: Path, size: int, temp: Path) -> Image.Image:
    if path.suffix.lower() == ".svg":
        rendered = temp / (path.stem + "-rendered.png")
        subprocess.run(
            ["inkscape", str(path), f"--export-filename={rendered}", f"--export-width={size}", f"--export-height={size}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        path = rendered
    image = Image.open(path).convert("RGBA")
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    return image


def gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            fx = x / width
            fy = y / height
            glow = max(0.0, 1.0 - math.hypot(fx - 0.18, fy - 0.10) * 1.45)
            sea = max(0.0, 1.0 - math.hypot(fx - 0.82, fy - 0.80) * 1.6)
            r = int(8 + 27 * glow + 20 * sea)
            g = int(19 + 47 * glow + 74 * sea)
            b = int(40 + 77 * glow + 82 * sea)
            pixels[x, y] = (r, g, b)
    return image


def main() -> None:
    parsed = args()
    theme = parsed.theme.resolve()
    width, height = 1600, 1000
    canvas = gradient(width, height).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle((42, 36, width - 42, height - 34), 42, fill=(4, 10, 26, 115), outline=(89, 255, 221, 170), width=3)
    draw.text((78, 60), "COONIE'S AERO HOARD", font=font(52, True), fill=(205, 255, 246, 255), stroke_width=2, stroke_fill=(46, 0, 135, 255))
    draw.text((82, 123), "v1.1.2 • vertical Crystal folders • Mint 21.3 toolbar fix • the good weird stuff stays", font=font(22), fill=(174, 218, 255, 255))

    cols = 8
    rows = 3
    left, top = 74, 188
    cell_w, cell_h = 181, 245
    icon_size = 126

    with tempfile.TemporaryDirectory(prefix="coonie-aero-preview-") as temp_name:
        temp = Path(temp_name)
        for index, (category, name, label) in enumerate(SAMPLES[: cols * rows]):
            col, row = index % cols, index // cols
            x = left + col * cell_w
            y = top + row * cell_h
            tile = (x, y, x + 157, y + 215)
            draw.rounded_rectangle(tile, 23, fill=(13, 31, 60, 255), outline=(91, 229, 255, 150), width=2)
            path = find_icon(theme, category, name)
            if path:
                icon = load_icon(path, icon_size, temp)
                shadow = Image.new("RGBA", (icon_size + 28, icon_size + 28), (0, 0, 0, 0))
                shadow_alpha = Image.new("L", shadow.size, 0)
                shadow_alpha.paste(icon.getchannel("A"), (14, 14))
                shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(8))
                shadow.putalpha(shadow_alpha)
                shadow.paste((0, 0, 0, 130), (0, 0, shadow.width, shadow.height), shadow)
                canvas.alpha_composite(shadow, (x + 1, y + 8))
                canvas.alpha_composite(icon, (x + (157 - icon.width) // 2, y + 13 + (126 - icon.height) // 2))
            label_box = draw.textbbox((0, 0), label, font=font(17, True))
            label_w = label_box[2] - label_box[0]
            draw.text((x + (157 - label_w) / 2, y + 170), label, font=font(17, True), fill=(235, 247, 255, 255))
            donor = category.upper()
            donor_box = draw.textbbox((0, 0), donor, font=font(11))
            donor_w = donor_box[2] - donor_box[0]
            draw.text((x + (157 - donor_w) / 2, y + 194), donor, font=font(11), fill=(117, 255, 221, 210))

    footer = "Nova7-shaped again: hard edges, layered sheets, blue glass spine, full-color sidebar objects."
    draw.text((82, 937), footer, font=font(20, True), fill=(205, 255, 246, 240))
    parsed.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(parsed.output, quality=95)


if __name__ == "__main__":
    main()
