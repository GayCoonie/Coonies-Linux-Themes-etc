#!/usr/bin/env bash
set -euo pipefail

theme_name="Coonie-Aero-Hoard"
mode="user"
destination=""

usage() {
  echo "Usage: ./uninstall.sh [--user | --system | --destination DIRECTORY]"
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

case "$mode" in
  user) destination="${XDG_DATA_HOME:-$HOME/.local/share}/icons" ;;
  system) destination="/usr/share/icons" ;;
esac

target="$destination/$theme_name"
if [[ "$mode" == "system" && -e "$target" && ! -w "$destination" ]]; then
  command -v sudo >/dev/null 2>&1 || {
    echo "System removal needs root access, but sudo is unavailable." >&2
    exit 1
  }
  sudo bash "$0" --destination "$destination"
  exit $?
fi

if [[ ! -e "$target" ]]; then
  echo "$theme_name is not installed at $target"
  exit 0
fi

trash_root="${XDG_DATA_HOME:-$HOME/.local/share}/Trash/files"
if [[ "$mode" == "user" ]]; then
  mkdir -p "$trash_root"
  recovery="$trash_root/${theme_name}.$(date +%Y%m%d-%H%M%S)"
  mv "$target" "$recovery"
  echo "Removed the theme; recoverable copy: $recovery"
else
  recovery="$destination/${theme_name}.removed.$(date +%Y%m%d-%H%M%S)"
  mv "$target" "$recovery"
  echo "Removed the theme; recoverable copy: $recovery"
fi

