#!/usr/bin/env bash
set -euo pipefail

THEME_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/themes"
LEGACY_THEME_HOME="$HOME/.themes"
ICON_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
FONT_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}/darkcold-ng"

if [[ -f "$STATE_HOME/original-gsettings.txt" && -x "$(command -v gsettings || true)" ]]; then
  while IFS='|' read -r schema key value; do
    [[ -n "$schema" && -n "$key" ]] || continue
    if [[ "$key" == "icon-theme" ]]; then
      current="$(gsettings get "$schema" "$key" 2>/dev/null || true)"
      [[ "$current" == *Darkcold-NG-Icons* || "$current" == *Darkcold-Coonie-Icons* ]] || continue
    fi
    gsettings set "$schema" "$key" "$value" 2>/dev/null || true
  done < "$STATE_HOME/original-gsettings.txt"
fi

for file in gtk.css gtk-dark.css; do
  target="$CONFIG_HOME/gtk-4.0/$file"
  if [[ -L "$target" && "$(readlink "$target")" == *'/Darkcold-'* ]]; then
    rm -f "$target"
    [[ -e "$STATE_HOME/gtk4-backup/$file" ]] && mv "$STATE_HOME/gtk4-backup/$file" "$target"
  fi
done

for theme in Darkcold-NG Darkcold-Coonie; do
  [[ -L "$LEGACY_THEME_HOME/$theme" ]] && rm -f "$LEGACY_THEME_HOME/$theme"
  [[ -d "$THEME_HOME/$theme" ]] && rm -rf -- "$THEME_HOME/$theme"
done
for icons in Darkcold-NG-Icons Darkcold-Coonie-Icons; do
  [[ -d "$ICON_HOME/$icons" ]] && rm -rf -- "$ICON_HOME/$icons"
done
rm -f "$FONT_HOME/BelligerentMadness-Regular.ttf"
rm -f "$CONFIG_HOME/fontconfig/conf.d/99-darkcold-belligerent.conf"
command -v fc-cache >/dev/null && fc-cache -f "$FONT_HOME" >/dev/null || true
printf '%s\n' 'Removed Darkcold NG and restored owned settings; a separately selected icon theme was left untouched.'
