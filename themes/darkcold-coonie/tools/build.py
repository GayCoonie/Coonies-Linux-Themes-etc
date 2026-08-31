#!/usr/bin/env python3
"""Build the installable Darkcold NG theme families from their maintained source."""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required to recolor the DarkCold image chrome: python3 -m pip install pillow") from exc


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"


VARIANTS = {
    "darkcold": {
        "name": "Darkcold-NG",
        "display": "Darkcold NG",
        "icon": "Darkcold-NG-Icons",
        "accent": "#6ebefe",
        "accent_bg": "#0d479f",
        "accent_deep": "#002e83",
        "accent_hot": "#11b8ff",
        "accent_shadow": "#032c70",
        "secondary": "#2670cc",
        "attention": "#ff4f5e",
        "panel": "#08090b",
        "surface": "#16181c",
        "surface_alt": "#25282e",
        "text": "#f8fbff",
        "muted": "#a9b8c7",
        "icon_inherits": "Mint-Y-Dark,Adwaita,hicolor",
    },
    "coonie": {
        "name": "Darkcold-Coonie",
        "display": "Darkcold Coonie — Purple & Seagreen",
        "icon": "Darkcold-Coonie-Icons",
        "accent": "#00ffbf",
        "accent_bg": "#460087",
        "accent_deep": "#260047",
        "accent_hot": "#0000ff",
        "accent_shadow": "#17105f",
        "secondary": "#ff4fbf",
        "attention": "#ff4fbf",
        "panel": "#08060d",
        "surface": "#17111f",
        "surface_alt": "#25172f",
        "text": "#ffffff",
        "muted": "#c9b8da",
        "icon_inherits": "Mint-Y-Purple,Mint-Y-Dark,Adwaita,hicolor",
    },
}


COONIE_REMAP = {
    "#0d377c": "#460087", "#002e83": "#460087", "#0d479f": "#460087",
    "#0d479e": "#460087", "#0448c2": "#8d007e", "#11b8ff": "#00ffbf",
    "#3e8cd3": "#00ffbf", "#2670cc": "#460087", "#2362b9": "#460087",
    "#1d57b2": "#8d007e", "#275cbd": "#00cfa4", "#408dd3": "#00ffbf",
    "#16609e": "#460087", "#032c70": "#260047", "#0851b8": "#8d007e",
    "#1c77cc": "#00ffbf", "#1f5db9": "#460087", "#1851b0": "#460087",
    "#1850a4": "#460087", "#0064f3": "#00ffbf", "#60b0e9": "#00ffbf",
    "#0811b8": "#460087", "#1327ec": "#00ffbf", "#8713ac": "#ff4fbf",
    "#8888ff": "#ff4fbf", "#5d5dfd": "#ff4fbf", "#3a3a5a": "#460087",
    "#4b4bcc": "#460087", "#1c1c5c": "#260047", "#4b6bcc": "#00ffbf",
    "#6ebefe": "#00ffbf", "#4a90d9": "#00ffbf",
    "#00455f": "#260047", "#0082b2": "#00ffbf", "#06439c": "#460087",
    "#2c85e2": "#00ffbf", "#1864b2": "#8d007e", "#3e90e5": "#00ffbf",
    "#00a5ff": "#00ffbf", "#071f46": "#460087",
    "#3584e4": "#460087", "#78aeed": "#00ffbf", "#1c71d8": "#8d007e",
    "#cc575d": "#ff4fbf", "#d7787d": "#ff4fbf", "#be3841": "#b0008f",
}


# SlickCold's renderer keeps each state as a stack of separate gradients rather
# than treating blue as one interchangeable accent.  The image-backed DarkCold
# renderer needs the same distinction, so these ramps are selected per asset.
COONIE_RAMPS = {
    # The application chrome is deliberately bisexual-dark first: black-violet,
    # purple and hot pink own almost the entire surface.  Indigo is only a short
    # cool shadow before the seagreen electrical rim.
    "dark_bisexual": (
        (0.00, "#190025"), (0.18, "#2d004f"), (0.38, "#460087"),
        (0.58, "#8d007e"), (0.73, "#ff4fbf"), (0.84, "#460087"),
        (0.91, "#17105f"), (0.97, "#00ffbf"), (1.00, "#460087"),
    ),
    "spectrum": (
        (0.00, "#260047"), (0.14, "#460087"), (0.30, "#b400b8"),
        (0.43, "#ff4fbf"), (0.56, "#0000ff"), (0.70, "#00a8ff"),
        (0.84, "#00ffbf"), (1.00, "#460087"),
    ),
    "purple": (
        (0.00, "#190025"), (0.28, "#35005f"), (0.55, "#460087"),
        (0.76, "#8d007e"), (0.90, "#b0008f"), (0.97, "#00ffbf"),
        (1.00, "#460087"),
    ),
    "seagreen": (
        (0.00, "#004c55"), (0.25, "#00a884"), (0.54, "#00ffbf"),
        (0.76, "#00a8ff"), (1.00, "#460087"),
    ),
    "pink": (
        (0.00, "#460087"), (0.28, "#b0008f"), (0.58, "#ff4fbf"),
        (0.82, "#ff7bd2"), (1.00, "#460087"),
    ),
    "muted": (
        (0.00, "#170b22"), (0.42, "#32134b"), (0.72, "#176050"),
        (1.00, "#25172f"),
    ),
}


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def mix_channel(start: int, end: int, amount: float) -> int:
    return round(start + (end - start) * amount)


def ramp_color(name: str, position: float) -> tuple[int, int, int]:
    stops = COONIE_RAMPS[name]
    position = max(0.0, min(1.0, position))
    for (start_at, start_hex), (end_at, end_hex) in zip(stops, stops[1:]):
        if position <= end_at:
            amount = 0.0 if end_at == start_at else (position - start_at) / (end_at - start_at)
            start = hex_rgb(start_hex)
            end = hex_rgb(end_hex)
            return tuple(mix_channel(a, b, amount) for a, b in zip(start, end))
    return hex_rgb(stops[-1][1])


def asset_profile(path: Path) -> tuple[str, bool]:
    """Return the color ramp and whether neutral relief receives a subtle tint."""
    name = path.name.lower()
    location = path.as_posix().lower()
    if "button-close" in name or name in {"close-window.png", "close.png"}:
        return "pink", True
    if "button-maximize" in name:
        return "seagreen", True
    if "button-unmaximize" in name:
        return "dark_bisexual", True
    if "button-minimize" in name:
        return "purple", True
    if "button-menu" in name:
        return "purple", True
    if "unfocused" in name:
        return "muted", "titlebar" in location or "frame-" in name
    if "titlebar" in location or "titlebar" in name:
        return "dark_bisexual", True
    if name in {"panel-bg.png", "panel-bg2.png", "menubar.png", "toolbar.png", "toolbar2.png"}:
        return "dark_bisexual", True
    if "/scrollbars/" in location or "scrollbar" in name:
        return "purple", False
    if any(token in location for token in (
        "check-radio", "checkbox-focused", "radiobutton-focused", "switcher-on",
    )):
        return "seagreen", False
    if any(token in location for token in (
        "prelight", "hover", "active", "selected", "progressbar",
        "slider",
        "menubar-item-active", "menuitem", "line-h", "line-v", "border",
    )):
        return "dark_bisexual", False
    return "dark_bisexual", False


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(f"@@{key.upper()}@@", value)
    return text


def remap_colors(text: str, mapping: dict[str, str]) -> str:
    for old, new in sorted(mapping.items(), key=lambda item: -len(item[0])):
        text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
    return text


def normalize_text_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+(?=\n)", "", text)
    text = re.sub(r"(?m)^ +\t", "\t", text)
    return text.rstrip() + "\n"


def normalize_legacy_rgb(text: str) -> str:
    """Round Sass color math so Cinnamon 6.0's older CSS parser sees integer RGB."""
    def replace(match: re.Match[str]) -> str:
        channels = [part.strip() for part in match.group(1).split(",")]
        if len(channels) != 3:
            return match.group(0)
        try:
            rounded = [str(max(0, min(255, round(float(channel))))) for channel in channels]
        except ValueError:
            return match.group(0)
        return f"rgb({', '.join(rounded)})"
    return re.sub(r"rgb\(([^)]*)\)", replace, text)


def write_text(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def recolor_darkcold_asset(path: Path) -> None:
    """Recompose DarkCold accents with state-aware Coonie ramps and preserved relief."""
    try:
        source_image = Image.open(path)
    except FileNotFoundError:
        return
    with source_image as source:
        rgba = source.convert("RGBA")
        width, height = rgba.size
        ramp, tint_relief = asset_profile(path)
        pixels = []
        changed = False
        for index, (red, green, blue, alpha) in enumerate(rgba.get_flattened_data()):
            if not alpha:
                pixels.append((red, green, blue, alpha))
                continue
            x = index % width
            y = index // width
            x_position = x / max(1, width - 1)
            y_position = y / max(1, height - 1)
            hue, saturation, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
            blue_accent = saturation >= 0.14 and value >= 0.06 and 0.46 <= hue <= 0.78
            red_accent = saturation >= 0.24 and value >= 0.08 and (hue <= 0.06 or hue >= 0.88)
            accent_weight = 0.94 if blue_accent or red_accent else 0.0
            panel_asset = path.name.lower() in {"panel-bg.png", "panel-bg2.png"}

            # Focused titlebars and panels contain large neutral bevel areas.  A
            # faint spectral tint there restores the oil-on-black color seen in
            # DarkCold while leaving the silver lip and black trough readable.
            relief_weight = 0.0
            if tint_relief and saturation < 0.18 and 0.025 < value < 0.82:
                lower_glow = math.exp(-((y_position - 0.76) / 0.20) ** 2)
                upper_glint = math.exp(-((y_position - 0.18) / 0.16) ** 2)
                relief_weight = (0.08 + 0.30 * lower_glow + 0.08 * upper_glint) * (1.0 - value * 0.45)
            if panel_asset and saturation < 0.18:
                panel_glow = math.exp(-((y_position - 0.88) / 0.15) ** 2)
                relief_weight = max(relief_weight, 0.10 + 0.78 * panel_glow)

            weight = max(accent_weight, relief_weight)
            if weight <= 0.0:
                pixels.append((red, green, blue, alpha))
                continue

            # Wide assets are stretched across controls, so their x coordinate
            # becomes a real multi-color gradient instead of a brightness-based
            # hue substitution. Tall assets use y to avoid a one-pixel color bar.
            position = x_position if width >= height or panel_asset else 1.0 - y_position
            target = ramp_color(ramp, position)
            boost = 0.13 * (1.0 - value) if accent_weight else 0.0
            if panel_asset:
                boost = max(boost, 0.30 * math.exp(-((y_position - 0.88) / 0.15) ** 2) * (1.0 - value))
            target_value = min(1.0, value + boost)
            # Preserve the source value/relief even for intrinsically dark hues
            # such as #460087; otherwise purple loses against cyan solely because
            # its brightest RGB channel is numerically lower.
            target_peak = max(target) or 1
            target = tuple(round(channel / target_peak * 255 * target_value) for channel in target)
            pixels.append(tuple(mix_channel(channel, colored, weight) for channel, colored in zip(
                (red, green, blue), target
            )) + (alpha,))
            changed = True
        if not changed:
            return
        rgba.putdata(pixels)
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            rgba.convert("RGB").save(path, quality=95, subsampling=0)
        else:
            rgba.save(path, optimize=True)


def apply_coonie_palette(theme_dir: Path) -> None:
    for path in theme_dir.rglob("*"):
        relative = path.relative_to(theme_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if not path.is_file() or path.name.startswith("thumbnail"):
            continue
        if path.suffix.lower() in {".css", ".rc", ".xml", ".ini", ".svg"} or path.name == "gtkrc":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            mapped = normalize_text_whitespace(remap_colors(text, COONIE_REMAP))
            write_text(path, mapped, executable=bool(path.stat().st_mode & 0o111))
        elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            recolor_darkcold_asset(path)

    gtk_override = (SRC / "coonie-gtk3-overrides.css").read_text(encoding="utf-8")
    for gtk_dir in ("gtk-3.0", "gtk-3.20"):
        css_path = theme_dir / gtk_dir / "gtk.css"
        write_text(css_path, css_path.read_text(encoding="utf-8").rstrip() + "\n\n" + gtk_override.rstrip() + "\n")


def sync_window_chrome(theme_dir: Path) -> None:
    """Use the Muffin decoration artwork for GTK client-side controls too."""
    source = theme_dir / "metacity-1"
    destination = theme_dir / "gtk-3.20" / "darkelements" / "titlebar" / "buttons"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "titlebar-mid-focused.png", destination.parent / "titlebar-mid-focused.png")
    shutil.copy2(source / "titlebar-mid-unfocused.png", destination.parent / "titlebar-mid-unfocused.png")
    for name in (
        "button-close-focused.png", "button-close-focused-active.png",
        "button-close-pressed.png", "button-close-unfocused.png",
        "button-maximize-focused.png", "button-maximize-focused-active.png",
        "button-maximize-pressed.png", "button-maximize-unfocused.png",
        "button-minimize-focused.png", "button-minimize-focused-active.png",
        "button-minimize-pressed.png", "button-minimize-unfocused.png",
        "button-unmaximize-focused.png", "button-unmaximize-focused-active.png",
        "button-unmaximize-pressed.png", "button-unmaximize-unfocused.png",
    ):
        shutil.copy2(source / name, destination / name)


def build_cinnamon(theme_dir: Path, data: dict[str, str], variant: str) -> None:
    cinnamon = theme_dir / "cinnamon"
    cinnamon.mkdir(parents=True, exist_ok=True)
    legacy = SRC / "cinnamon-legacy"
    modern = SRC / "cinnamon-modern"
    for path in legacy.iterdir():
        if path.is_file() and path.name not in {"cinnamon.css", "metadata.json", "theme.json"}:
            shutil.copy2(path, cinnamon / path.name)
    for path in modern.iterdir():
        if path.is_file() and path.suffix in {".svg", ".png"}:
            shutil.copy2(path, cinnamon / path.name)
    shutil.copy2(ROOT / "assets" / f"thumbnail-{variant}.png", cinnamon / "thumbnail.png")

    css = (modern / "cinnamon-base.css").read_text(encoding="utf-8")
    default_map = {
        "#3584e4": data["accent_bg"], "#78aeed": data["accent"],
        "#1c71d8": data["accent"], "#242424": data["surface"],
        "#303030": data["surface_alt"], "#1a1a1a": data["panel"],
        "#393939": data["surface_alt"], "#454545": data["surface_alt"],
        "#e74b37": data["attention"],
    }
    css = normalize_legacy_rgb(remap_colors(css, default_map))
    overlay = render((SRC / "cinnamon-overrides.css.in").read_text(encoding="utf-8"), data)
    write_text(cinnamon / "cinnamon.css", css + "\n\n" + overlay)
    metadata = {
        "uuid": data["name"],
        "name": data["display"],
        "description": "DarkCold rebuilt for Cinnamon 6.0–6.6+",
        "cinnamon-version": ["6.0", "6.2", "6.4", "6.6"],
    }
    write_text(cinnamon / "metadata.json", json.dumps(metadata, indent=2) + "\n")
    write_text(cinnamon / "theme.json", json.dumps({"cinnamon-theme": {
        "name": data["display"], "author": "OriginalSeed, Mystia-Izakaya, Coonie/Adam and OpenAI Codex",
        "version": "2.2.2", "type": "custom", "thumbnail": "thumbnail.png",
        "url": "https://github.com/GayCoonie/darkcold-coonie-theme"
    }}, indent=2) + "\n")


def build_variant(variant: str) -> None:
    data = dict(VARIANTS[variant])
    theme_dir = DIST / "themes" / data["name"]
    icon_dir = DIST / "icons" / data["icon"]
    copy_tree(SRC / "gtk-2.0", theme_dir / "gtk-2.0")
    copy_tree(SRC / "gtk-3.0", theme_dir / "gtk-3.0")
    copy_tree(SRC / "gtk-3.20", theme_dir / "gtk-3.20")
    copy_tree(SRC / "metacity-1", theme_dir / "metacity-1")
    sync_window_chrome(theme_dir)
    (theme_dir / "extras").mkdir(parents=True, exist_ok=True)

    for xml in (theme_dir / "metacity-1").glob("*.xml"):
        text = xml.read_text(encoding="utf-8").replace("SlickCold", data["name"]).replace("DarkCold", data["name"])
        if variant == "coonie":
            text = remap_colors(text, COONIE_REMAP)
            text = re.sub(r'(<title\s+color=")#ffffff(")', r'\1#00ffbf\2', text, flags=re.IGNORECASE)
            text = re.sub(r'(<title\s+color=")#afafaf(")', r'\1#c9b8da\2', text, flags=re.IGNORECASE)
        write_text(xml, text)

    build_cinnamon(theme_dir, data, variant)

    index = render((SRC / "index.theme.in").read_text(encoding="utf-8"), data)
    write_text(theme_dir / "index.theme", index)
    gtk4 = render((SRC / "gtk4.css.in").read_text(encoding="utf-8"), data)
    write_text(theme_dir / "gtk-4.0" / "gtk.css", gtk4)
    write_text(theme_dir / "gtk-4.0" / "gtk-dark.css", gtk4)
    write_text(theme_dir / "extras" / "plank" / "dock.theme", render((SRC / "plank.dock.theme.in").read_text(encoding="utf-8"), data))
    write_text(theme_dir / "extras" / "firefox-userChrome.css", render((SRC / "firefox-userChrome.css.in").read_text(encoding="utf-8"), data))
    write_text(theme_dir / "extras" / "terminal-palette.txt", render((SRC / "terminal-palette.txt.in").read_text(encoding="utf-8"), data))

    icon_index = render((SRC / "icons.index.theme.in").read_text(encoding="utf-8"), data)
    write_text(icon_dir / "index.theme", icon_index)
    if variant == "coonie":
        apply_coonie_palette(theme_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["all", *VARIANTS], default="all")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if args.clean and DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)
    selected = VARIANTS if args.variant == "all" else [args.variant]
    for variant in selected:
        build_variant(variant)
    print("Built:", ", ".join(VARIANTS[v]["name"] for v in selected))


if __name__ == "__main__":
    main()
