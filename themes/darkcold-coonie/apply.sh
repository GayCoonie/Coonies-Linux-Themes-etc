#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
THEME_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/themes"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}/darkcold-ng"
ENABLE_GTK4=0
SET_FONT=1
SET_ICONS=0

case "${1:-}" in
  darkcold|normal) THEME="Darkcold-NG"; ICONS="Darkcold-NG-Icons" ;;
  coonie|purple|seagreen) THEME="Darkcold-Coonie"; ICONS="Darkcold-Coonie-Icons" ;;
  *) printf '%s\n' 'Usage: ./apply.sh darkcold|coonie [--gtk4] [--icons] [--no-font]' >&2; exit 2 ;;
esac
shift
while (($#)); do
  case "$1" in
    --gtk4) ENABLE_GTK4=1 ;;
    --icons) SET_ICONS=1 ;;
    --no-font) SET_FONT=0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
  shift
done

if [[ ! -d "$THEME_HOME/$THEME" ]]; then
  printf 'Theme is not installed at %s. Run ./install.sh first.\n' "$THEME_HOME/$THEME" >&2
  exit 1
fi

mkdir -p "$STATE_HOME"
SETTINGS_STATE="$STATE_HOME/original-gsettings.txt"
touch "$SETTINGS_STATE"

schema_has_key() {
  gsettings list-keys "$1" 2>/dev/null | grep -Fxq "$2"
}

remember_once() {
  local schema="$1" key="$2"
  grep -Fq "$schema|$key|" "$SETTINGS_STATE" 2>/dev/null || \
    printf '%s|%s|%s\n' "$schema" "$key" "$(gsettings get "$schema" "$key")" >> "$SETTINGS_STATE"
}

gset() {
  local schema="$1" key="$2" value="$3"
  command -v gsettings >/dev/null || return 0
  schema_has_key "$schema" "$key" || return 0
  remember_once "$schema" "$key"
  gsettings set "$schema" "$key" "$value"
}

gset org.cinnamon.desktop.interface gtk-theme "$THEME"
gset org.cinnamon.desktop.wm.preferences theme "$THEME"
gset org.cinnamon.theme name "$THEME"
gset org.gnome.desktop.interface gtk-theme "$THEME"
gset org.gnome.desktop.interface color-scheme prefer-dark

if ((SET_ICONS)); then
  gset org.cinnamon.desktop.interface icon-theme "$ICONS"
  gset org.gnome.desktop.interface icon-theme "$ICONS"
fi

if ((SET_FONT)); then
  gset org.cinnamon.desktop.interface font-name 'Darkcold Belligerent 11'
  gset org.cinnamon.desktop.interface document-font-name 'Darkcold Belligerent 11'
  gset org.cinnamon.desktop.wm.preferences titlebar-font 'Darkcold Belligerent Bold 11'
  gset org.gnome.desktop.interface font-name 'Darkcold Belligerent 11'
  gset org.gnome.desktop.interface document-font-name 'Darkcold Belligerent 11'
  gset org.gnome.desktop.wm.preferences titlebar-font 'Darkcold Belligerent Bold 11'
fi

if ((ENABLE_GTK4)); then
  gtk4="$CONFIG_HOME/gtk-4.0"
  mkdir -p "$gtk4" "$STATE_HOME/gtk4-backup"
  for file in gtk.css gtk-dark.css; do
    if [[ -e "$gtk4/$file" && ! -L "$gtk4/$file" && ! -e "$STATE_HOME/gtk4-backup/$file" ]]; then
      cp -a "$gtk4/$file" "$STATE_HOME/gtk4-backup/$file"
    fi
    rm -f "$gtk4/$file"
    ln -s "$THEME_HOME/$THEME/gtk-4.0/$file" "$gtk4/$file"
  done
  printf '%s\n' "$THEME" > "$STATE_HOME/gtk4-theme"
fi

printf 'Applied %s. Cinnamon should update live; log out and back in if an app caches its old theme.\n' "$THEME"
if ((SET_ICONS == 0)); then
  printf '%s\n' 'Your current icon theme was left untouched.'
fi
