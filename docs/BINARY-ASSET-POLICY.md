# Binary Asset Policy

The repository keeps exact portable release archives so a working package is never reconstructed from partial Git history.

DarkCold's browsable tree includes its code, CSS/SCSS, XML, SVG, metadata, tests, and documentation. Its 1,000+ generated or inherited raster assets and font binary remain complete in both 2.2.2 release archives under `releases/darkcold/`; this avoids turning ordinary source review into a wall of opaque blobs while preserving the exact installable payload.

Coonie Aero Gel keeps its reproducible source atlases and builder browsable, with the complete installable Xcursor tree in `releases/cursors/Coonie-Aero-Gel-v1.tar.gz`.

Coonie's Aero Hoard is different: its complete install archive and Debian package each exceed GitHub's 100 MB per-file limit. Git therefore keeps the reproducible source/packaging kit, audit, preview, summary, and checksum ledger. See `docs/RELEASES.md` for the recorded Library-held binaries.

Do not unpack generated binary forests into Git merely to increase file count. Add browsable source when it materially helps maintenance; add exact releases when they are necessary for reproduction or rollback; use Git LFS or GitHub Releases for future oversized artifacts.
