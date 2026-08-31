#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
THEME_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/themes"
LEGACY_THEME_HOME="$HOME/.themes"
ICON_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
FONT_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
FONTCONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}/fontconfig/conf.d"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}/darkcold-ng"
INSTALL_FONT=1
APPLY_VARIANT=""
ENABLE_GTK4=0
APPLY_ICONS=0

usage() {
  printf '%s\n' \
    'Usage: ./install.sh [--apply darkcold|coonie] [--gtk4] [--icons] [--no-font]' \
    '' \
    'Installs both variants for the current user. --apply selects one immediately.' \
    '--gtk4 enables the reversible GTK 4/libadwaita compatibility layer.' \
    '--icons explicitly selects the packaged inheritance theme; icons are otherwise untouched.'
}

while (($#)); do
  case "$1" in
    --apply) APPLY_VARIANT="${2:-}"; shift 2 ;;
    --gtk4) ENABLE_GTK4=1; shift ;;
    --icons) APPLY_ICONS=1; shift ;;
    --no-font) INSTALL_FONT=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -d "$ROOT_DIR/dist/themes/Darkcold-NG" || ! -d "$ROOT_DIR/dist/themes/Darkcold-Coonie" ]]; then
  printf '%s\n' 'Prebuilt themes are missing. Run tools/build.py first.' >&2
  exit 1
fi

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_root="$STATE_HOME/backups/$timestamp"
mkdir -p "$THEME_HOME" "$LEGACY_THEME_HOME" "$ICON_HOME" "$FONT_HOME" "$FONTCONFIG_HOME" "$backup_root"

install_tree() {
  local source="$1" destination="$2" name
  name="$(basename "$source")"
  if [[ -e "$destination/$name" && ! -L "$destination/$name" ]]; then
    mkdir -p "$backup_root/$(basename "$destination")"
    mv "$destination/$name" "$backup_root/$(basename "$destination")/$name"
  else
    rm -f "$destination/$name"
  fi
  cp -a "$source" "$destination/$name"
}

for theme in Darkcold-NG Darkcold-Coonie; do
  install_tree "$ROOT_DIR/dist/themes/$theme" "$THEME_HOME"
  rm -f "$LEGACY_THEME_HOME/$theme"
  ln -s "$THEME_HOME/$theme" "$LEGACY_THEME_HOME/$theme"
done
for icons in Darkcold-NG-Icons Darkcold-Coonie-Icons; do
  install_tree "$ROOT_DIR/dist/icons/$icons" "$ICON_HOME"
done

if ((INSTALL_FONT)); then
  install -m 0644 "$ROOT_DIR/assets/fonts/BelligerentMadness-Regular.ttf" "$FONT_HOME/BelligerentMadness-Regular.ttf"
  install -m 0644 "$ROOT_DIR/assets/fonts/99-darkcold-belligerent.conf" "$FONTCONFIG_HOME/99-darkcold-belligerent.conf"
  command -v fc-cache >/dev/null && fc-cache -f "$FONT_HOME" >/dev/null
fi

if [[ -n "$APPLY_VARIANT" ]]; then
  args=("$APPLY_VARIANT")
  ((ENABLE_GTK4)) && args+=(--gtk4)
  ((APPLY_ICONS)) && args+=(--icons)
  ((INSTALL_FONT == 0)) && args+=(--no-font)
  "$ROOT_DIR/apply.sh" "${args[@]}"
fi

printf '%s\n' 'Installed Darkcold-NG and Darkcold-Coonie.'
if [[ -z "$APPLY_VARIANT" ]]; then
  printf '%s\n' 'Apply one with: ./apply.sh darkcold  or  ./apply.sh coonie'
fi
