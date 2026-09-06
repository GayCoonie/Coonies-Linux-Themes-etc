#!/usr/bin/env python3
"""One-time recovery from the already-committed public release witness.

The archive is migration input only. Build, install and CI use the live tree.
"""
import hashlib
import shutil
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
archive = ROOT / 'releases/darkcold/darkcold-coonie-theme-2.2.2.tar.gz'
with tempfile.TemporaryDirectory() as tmp:
    with tarfile.open(archive) as tf:
        tf.extractall(tmp, filter='data')
    source = Path(tmp) / 'darkcold-coonie-theme'
    target = ROOT / 'themes/darkcold-coonie'
    count = 0
    for p in sorted(source.rglob('*')):
        if p.is_dir():
            continue
        dest = target / p.relative_to(source)
        # Preserve current editable files; restore only the previously omitted assets.
        if dest.exists() or dest.is_symlink():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if p.is_symlink():
            dest.symlink_to(p.readlink())
        else:
            shutil.copy2(p, dest)
            assert hashlib.sha256(dest.read_bytes()).digest() == hashlib.sha256(p.read_bytes()).digest()
        count += 1
    print(f'Restored {count} missing DarkCold source and installation assets.')
