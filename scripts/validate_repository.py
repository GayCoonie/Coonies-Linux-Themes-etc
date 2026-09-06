#!/usr/bin/env python3
"""Validate actual checkout assets; no release archives or summary proxies."""
import configparser
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def validate():
    errors = []
    def require(relative):
        p = ROOT / relative
        if not p.is_file() or not p.stat().st_size:
            errors.append(f'Missing or empty: {relative}')
        return p
    for p in ['README.md', 'AGENTS.md', 'docs/COMPONENT-MATRIX.md',
              'themes/darkcold-coonie/assets/fonts/BelligerentMadness-Regular.ttf',
              'themes/darkcold-coonie/tools/build.py',
              'icons/coonie-aero-hoard/scripts/build-release.sh',
              'cursors/coonie-aero-gel-v1/source-build/build.py']:
        require(p)
    theme = ROOT / 'icons/coonie-aero-hoard/Coonie-Aero-Hoard'
    index = require(str(theme.relative_to(ROOT) / 'index.theme'))
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.read(index)
    if not cfg.has_section('Icon Theme'):
        errors.append('Icon index lacks [Icon Theme]')
    else:
        for d in cfg['Icon Theme'].get('Directories', '').split(','):
            if d and (not (theme / d).is_dir() or not cfg.has_section(d)):
                errors.append(f'Missing indexed icon directory or metadata: {d}')
    rows = [json.loads(line) for p in sorted((theme / 'manifest/icons').rglob('*.jsonl'))
            for line in p.read_text().splitlines()]
    paths = set()
    for row in rows:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            errors.append(f'Unsafe icon path: {relative}')
            continue
        if row['path'] in paths:
            errors.append(f'Duplicate manifest path: {relative}')
        paths.add(row['path'])
        p = theme / relative
        if not p.is_file():
            errors.append(f'Missing artwork: {relative}')
        elif hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            errors.append(f'Artwork checksum differs from manifest: {relative}')
    actual = {str(p.relative_to(theme)) for p in theme.rglob('*')
              if p.suffix.lower() in {'.png', '.svg', '.xpm'} and p.is_file()}
    if len(rows) < 115933:
        errors.append(f'Incomplete manifest: {len(rows)} entries; recovery baseline is 115933')
    if actual != paths:
        errors.append(f'Artwork/manifest difference: {len(actual - paths)} unrecorded, {len(paths - actual)} absent')
    for layer in ['Darkcold-NG', 'Darkcold-Coonie']:
        for path in ['cinnamon/button-normal.png', 'cinnamon/cinnamon.css',
                     'metacity-1/button-close-focused.png', 'metacity-1/metacity-theme-3.xml',
                     'gtk-2.0/gtkrc', 'gtk-3.20/gtk.css',
                     'gtk-3.20/darkelements/titlebar/buttons/button-close-focused.png', 'gtk-4.0/gtk.css']:
            require(f'themes/darkcold-coonie/dist/themes/{layer}/{path}')
    cursor = ROOT / 'cursors/coonie-aero-gel-v1/Coonie-Aero-Gel/cursors'
    if not cursor.is_dir() or len(list(cursor.iterdir())) < 60:
        errors.append('Incomplete cursor role/alias set')
    for p in cursor.glob('*'):
        if not p.exists():
            errors.append(f'Broken cursor alias: {p.name}')
    usercss = require('userstyles/Coonieglass-ChatGPT.user.css')
    if usercss.is_file() and '==UserStyle==' not in usercss.read_text():
        errors.append('Missing UserStyle metadata')
    if errors:
        print('\n'.join(errors[:40]), file=sys.stderr)
        print(f'FAILED: {len(errors)} errors', file=sys.stderr)
        return 1
    print(f'PASS: {len(actual):,} actual icons match provenance; DarkCold assets and cursor aliases exist.')
    return 0
if __name__ == '__main__':
    sys.exit(validate())
