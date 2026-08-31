#!/usr/bin/env bash
set -euo pipefail

theme_name="Coonie-Aero-Hoard"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source_theme="$script_dir/$theme_name"
mode="user"
destination=""

usage() {
  echo "Usage: ./install.sh [--user | --system | --destination DIRECTORY]"
}

while (($#)); do
  case "$1" in
    --user) mode="user" ;;
    --system) mode="system" ;;
    --destination)
      shift
      [[ $# -gt 0 ]] || { usage >&2; exit 2; }
      mode="custom"
      destination="$1"
      ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
  shift
done

[[ -f "$source_theme/index.theme" ]] || {
  echo "The $theme_name directory must be beside install.sh." >&2
  exit 1
}

case "$mode" in
  user) destination="${XDG_DATA_HOME:-$HOME/.local/share}/icons" ;;
  system) destination="/usr/share/icons" ;;
esac

install_direct() {
  local icon_root="$1"
  local target="$icon_root/$theme_name"
  local incoming="$icon_root/.${theme_name}.incoming.$$"
  mkdir -p "$icon_root"
  cp -a "$source_theme" "$incoming"
  if [[ -e "$target" ]]; then
    local backup="$icon_root/${theme_name}.backup.$(date +%Y%m%d-%H%M%S)"
    mv "$target" "$backup"
    echo "Previous installation preserved as: $backup"
  fi
  mv "$incoming" "$target"
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$target" >/dev/null
  fi
}

if [[ "$mode" == "system" && ! -w "$destination" ]]; then
  command -v sudo >/dev/null 2>&1 || {
    echo "System installation needs root access, but sudo is unavailable." >&2
    exit 1
  }
  sudo bash "$0" --destination "$destination"
  exit $?
fi

install_direct "$destination"
echo "Installed $theme_name to $destination/$theme_name"
echo "Select “Coonie's Aero Hoard” in your desktop's icon-theme settings."

