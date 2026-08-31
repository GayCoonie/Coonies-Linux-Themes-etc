#!/usr/bin/env bash
set -euo pipefail

theme_name="Coonie-Aero-Gel"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
install_dir="$install_root/$theme_name"

mkdir -p "$install_root"
if [[ "$script_dir" != "$install_dir" ]]; then
  if [[ -e "$install_dir" ]]; then
    backup_dir="$install_dir.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$install_dir" "$backup_dir"
    echo "Existing theme moved to: $backup_dir"
  fi
  cp -a "$script_dir" "$install_dir"
fi

gsettings set org.cinnamon.desktop.interface cursor-theme "$theme_name"
echo "Installed and selected: $theme_name"
echo "If one application keeps its old cursor, log out and back in once."
