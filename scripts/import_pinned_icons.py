#!/usr/bin/env python3
"""One-time migration of pinned public donor artwork into the live source tree.

Ordinary installs and packages NEVER invoke this script or access the network.
Every imported image must match the saved 1.1.2 per-file SHA256 witness.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'icons/coonie-aero-hoard'
THEME = PROJECT / 'Coonie-Aero-Hoard'
NAMES = {'crystal-remix': 'crystal-remix', 'gnome-colors': 'gnome-colors',
         'newaita': 'newaita-reborn', 'nuovext': 'nuovext', 'ocd': 'ocd',
         'oxygen-refit': 'oxygenrefit2-gitlab', 'papirus': 'papirus'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    records = [json.loads(line) for p in sorted((THEME / 'manifest/icons').rglob('*.jsonl'))
               for line in p.read_text().splitlines()]
    assert len(records) == 115933
    needed = {r['sha256'] for r in records}
    pins = json.loads((ROOT / 'docs/provenance/aero-hoard-1.1.2-donors.json').read_text())
    with tempfile.TemporaryDirectory(prefix='coonie-source-import-') as tmp:
        sources = Path(tmp) / 'donors'
        def fetch(item):
            name, pin = item
            dest = sources / NAMES[name]
            subprocess.run(['git', 'init', '-q', str(dest)], check=True)
            subprocess.run(['git', '-C', str(dest), 'fetch', '--quiet', '--depth', '1',
                            pin['remote'], pin['commit']], check=True)
            subprocess.run(['git', '-C', str(dest), 'checkout', '-q', 'FETCH_HEAD'], check=True)
            actual = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'HEAD'], text=True).strip()
            assert actual == pin['commit'], name
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
            list(pool.map(fetch, pins.items()))
        found = {}
        for p in sources.rglob('*'):
            if p.suffix.lower() in {'.png', '.svg', '.xpm'} and p.is_file():
                sha = digest(p)
                if sha in needed:
                    found.setdefault(sha, p)
        print('Exact public donor matches:', len(found), flush=True)

        spec = importlib.util.spec_from_file_location('builder', PROJECT / 'scripts/build_theme.py')
        builder = importlib.util.module_from_spec(spec)
        sys.modules['builder'] = builder
        spec.loader.exec_module(builder)
        generated = Path(tmp) / 'generated'
        generated.mkdir()
        work = Path(tmp) / 'work'
        work.mkdir()
        copier = builder.Copier(generated)
        roots = builder.source_roots(sources)
        for row in records:
            if row['source'] == 'normalized-legacy-raster':
                choices = [r / row['source_path'] for r in roots.values()
                           if (r / row['source_path']).is_file()]
                if not choices:
                    raise RuntimeError(f"Missing raster donor: {row['path']}")
                copier.install_file(choices[0], Path(row['path']), 'before-normalize', row['source_path'])
        builder.sanitize_legacy_rasters(copier, work)
        folders = builder.install_crystal_folders(copier, sources, work)
        builder.install_mint_nemo_places(copier, folders)
        for p in generated.rglob('*'):
            if p.is_file():
                found.setdefault(digest(p), p)
        # Explicitly restored modifications take precedence; all are hash-checked.
        for row in records:
            p = THEME / row['path']
            if p.is_file() and digest(p) == row['sha256']:
                found[row['sha256']] = p
        absent = [r['path'] for r in records if r['sha256'] not in found]
        if absent:
            raise RuntimeError(f'{len(absent)} unrecovered assets; first 20: {absent[:20]}')
        for row in records:
            relative = Path(row['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError(relative)
            dest = THEME / relative
            src = found[row['sha256']]
            if src != dest:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
            assert digest(dest) == row['sha256'], relative
        print(f'Restored and verified {len(records):,} actual icon paths.', flush=True)

if __name__ == '__main__':
    main()
