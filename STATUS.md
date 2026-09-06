# Project status

## Live source recovery

- DarkCold Coonie 2.2.2: source, font and raster assets plus the complete installation tree; checkout-based build and tests.
- Aero Hoard 1.1.2: 115,933 actual icon paths, restored against every saved artwork SHA256, with 140 browsable per-directory provenance files, exact donor revisions and license texts.
- Aero Gel v1: complete cursor roles/aliases, master atlases and builder retained.
- Coonieglass: existing editable UserCSS retained.
- Packaging and CI operate on the checkout; optional release witnesses do not supply missing files.

## Remaining limits

- No live Mint 21.3 Cinnamon/Nemo desktop is available in the recovery environment. Huge Nemo icons and other appearance regressions still require the user's runtime witnesses.
- Recovery restores the saved 1.1.2 pixels; it does not claim another visual fix.
- The historical donor-selection builder is retained as `scripts/rebuild-from-donors.sh` in the icon component. Its GNOME Noble input was generated rather than directly present in the pinned donor checkout. It is historical tooling, not the normal packaging path or a claim of a fully automated original build environment.
- The one-time source import uses pinned public donors and verifies exact output bytes. Once the source files are committed, neither that import nor its network access is needed again.

See `docs/SOURCE-RECOVERY.md` for the measured recovery and connector results.
