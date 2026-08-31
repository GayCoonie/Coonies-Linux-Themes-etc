#!/usr/bin/env bash
set -u

THEME_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/themes"
FONT_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
failures=0

ok() { printf '  [ok] %s\n' "$1"; }
bad() { printf '  [!!] %s\n' "$1"; failures=$((failures + 1)); }

printf '%s\n' 'Darkcold NG diagnostic'
if command -v cinnamon >/dev/null; then
  version="$(cinnamon --version 2>/dev/null || true)"
  printf '  Cinnamon: %s\n' "${version:-unknown}"
else
  printf '%s\n' '  Cinnamon: not present in this environment (package validation only)'
fi

for theme in Darkcold-NG Darkcold-Coonie; do
  base="$THEME_HOME/$theme"
  if [[ -d "$base" ]]; then
    ok "$theme installed"
  else
    bad "$theme missing"
    continue
  fi
  for required in index.theme gtk-2.0/gtkrc gtk-3.0/gtk.css gtk-3.20/gtk.css gtk-4.0/gtk.css cinnamon/cinnamon.css metacity-1/metacity-theme-3.xml; do
    [[ -s "$base/$required" ]] && ok "$theme/$required" || bad "$theme/$required"
  done
done

[[ -s "$FONT_HOME/BelligerentMadness-Regular.ttf" ]] && ok 'Belligerent Madness installed' || bad 'Belligerent Madness not installed'

if ((failures)); then
  printf '%d problem(s) found.\n' "$failures"
  exit 1
fi
printf '%s\n' 'Everything expected is present.'
