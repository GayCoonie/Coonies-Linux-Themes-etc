#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
python3 -m py_compile tools/build.py
python3 - <<'PY'
import json
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path('dist')
for name in ('Darkcold-NG', 'Darkcold-Coonie'):
    theme = root / 'themes' / name
    required = ('index.theme', 'gtk-2.0/gtkrc', 'gtk-3.0/gtk.css', 'gtk-3.20/gtk.css',
                'gtk-3.20/darkelements/titlebar/buttons/button-close-focused.png', 'gtk-4.0/gtk.css',
                'cinnamon/cinnamon.css', 'cinnamon/metadata.json', 'metacity-1/metacity-theme-3.xml')
    for item in required:
        path = theme / item
        assert path.is_file() and path.stat().st_size, path
    css = (theme / 'cinnamon/cinnamon.css').read_text()
    assert css.count('{') == css.count('}'), f'unbalanced Cinnamon CSS: {name}'
    json.loads((theme / 'cinnamon/metadata.json').read_text())
    ET.parse(theme / 'metacity-1/metacity-theme-3.xml')
    assert '@@' not in css
    assert 'border-image: url("button-normal.png") 3 3 3 3 stretch stretch;' in css
    assert 'border-image: url("button-prelight.png") 3 3 3 3 stretch stretch;' in css
    assert 'border-image: url("slider-vert-active.png") 3 3 3 3 stretch stretch;' in css
    assert '.panel-status-button, .panel-launcher, .applet-box' in css
    assert '#panel StIcon, #panel .panel-status-button, #panel .applet-box' in css
    assert css.count('-st-icon-style: regular;') >= 5
    overlay_stage = css.rindex('stage {')
    assert '-st-icon-style: regular;' in css[overlay_stage:css.index('}', overlay_stage)]
    gtk3 = (theme / 'gtk-3.20/gtk.css').read_text()
    gtk3_legacy = (theme / 'gtk-3.0/gtk.css').read_text()
    gtk4 = (theme / 'gtk-4.0/gtk.css').read_text()
    assert 'darkelements/button-normal.png' in gtk3
    assert 'headerbar' in gtk3 and 'decoration' in gtk3
    assert 'button.not(' not in gtk3
    assert 'max-height:' not in gtk3 and 'max-width:' not in gtk3
    assert (theme / 'gtk-3.20/darkelements/titlebar/buttons/button-close-focused.png').read_bytes() == \
           (theme / 'metacity-1/button-close-focused.png').read_bytes()
    assert (theme / 'gtk-3.20/darkelements/titlebar/titlebar-mid-focused.png').read_bytes() == \
           (theme / 'metacity-1/titlebar-mid-focused.png').read_bytes()
    assert 'button-close-unfocused.png' in gtk3 and 'headerbar:backdrop' in gtk3
    assert '-gtk-icon-style: regular;' in gtk3
    assert '-gtk-icon-style: regular;' in gtk3_legacy
    assert '-gtk-icon-style: regular;' in gtk4
    if name == 'Darkcold-Coonie':
        assert '@define-color coonie_pink #ff4fbf;' in gtk3
        assert '@define-color coonie_seagreen #00ffbf;' in gtk3
        assert '@define-color coonie_blue_shadow #17105f;' in gtk3
        assert '@define-color coonie_blue #0000ff;' not in gtk3
        assert 'scrollbar slider:hover' in gtk3
        assert 'linear-gradient(to right' in gtk3
assert (root / 'themes/Darkcold-NG/gtk-3.20/darkelements/button-normal.png').read_bytes() != \
       (root / 'themes/Darkcold-Coonie/gtk-3.20/darkelements/button-normal.png').read_bytes()
assert (root / 'themes/Darkcold-Coonie/metacity-1/button-minimize-focused.png').read_bytes() != \
       (root / 'themes/Darkcold-Coonie/metacity-1/button-maximize-focused.png').read_bytes()
from tools.build import asset_profile
assert asset_profile(Path('gtk-3.20/darkelements/titlebar/titlebar-mid-focused.png'))[0] == 'dark_bisexual'
assert asset_profile(Path('gtk-2.0/Scrollbars/slider-vert-active.png'))[0] == 'purple'
print('Structural validation passed.')
PY

if rg -n 'gset .*icon-theme' apply.sh | rg -v '^[0-9]+:  gset '; then
  printf '%s\n' 'Icon theme must only be applied inside the explicit --icons branch.' >&2
  exit 1
fi
rg -q -- '--icons' apply.sh install.sh README.md

test_home="$(mktemp -d)"
trap 'rm -rf -- "$test_home"' EXIT
HOME="$test_home" XDG_DATA_HOME="$test_home/.local/share" XDG_CONFIG_HOME="$test_home/.config" XDG_STATE_HOME="$test_home/.local/state" ./install.sh --no-font
for theme in Darkcold-NG Darkcold-Coonie; do
  test -s "$test_home/.local/share/themes/$theme/cinnamon/cinnamon.css"
done
HOME="$test_home" XDG_DATA_HOME="$test_home/.local/share" XDG_CONFIG_HOME="$test_home/.config" XDG_STATE_HOME="$test_home/.local/state" ./uninstall.sh
for theme in Darkcold-NG Darkcold-Coonie; do
  test ! -e "$test_home/.local/share/themes/$theme"
done
printf '%s\n' 'Sandbox install/uninstall validation passed.'
