# Live source recovery — 2026-09-06

## Correcting the incomplete repository

The starting main commit was `ada81b7b42ab6a3d9eda31cca91d5ba2b7c285c5`, with 329 file entries. Aero Hoard artwork was absent, and DarkCold raster assets/font were confined to release archives. Earlier completeness claims were too strong.

The preserved Aero Hoard 1.1.2 package has SHA256 `d6c633ea96dcbcb15ff6c7e53fd0589b997e571f5c7ba41614f6addcfe352ef0`. Its 115,933 artwork paths all match its original provenance manifest. The package also contains the donor revision ledger previously missing from Git.

Recovery uses seven pinned public donor checkouts. 73,793 distinct artwork contents match donors directly. The existing normalization/folder functions reproduce another 561 distinct contents byte for byte. Eighteen remaining distinct files (ten Nemo toolbar PNGs and eight SVGs) are restored directly from the saved source witness. Duplicate installation paths remain independent ordinary files.

No provenance summary substitutes for actual image bytes. Import fails before committing if any path cannot be recovered or its checksum differs. Ordinary validation likewise compares every file with its recorded SHA256 and rejects missing or unrecorded artwork.

## Connector methods tested

- Creating a branch through the GitHub connector succeeded without a separate CLI login.
- Creating binary blobs with base64 succeeded, including the actual Belligerent Madness font.
- The connector's `fetch_blob` wrapper fails on PNG bytes because it attempts UTF-8 decoding. Binary write success must instead be checked through Git tree/blob hashes and checkout bytes.
- Temporary arbitrary chunks of the saved release archive were rejected by automatic approval review. That route was abandoned. The accepted approach restores specific source files and checksum-verified public donor artwork.
- GitHub Actions starts jobs now. The first run failed because Pillow was missing, after checkout and the old metadata-only validator had passed. The workflow now installs its dependencies and tests the live source tree.
- Git tree creation permits multiple file changes in one commit; commit/ref operations provide a path for incremental maintenance through the connector.

## Structure and provenance

`icons/coonie-aero-hoard/Coonie-Aero-Hoard/` is the editable installation source. `manifest/icons/` splits the original JSONL provenance by actual icon directory; it is plain text and browsable. Original source revisions, summary and licensing material are retained. Runtime-generated `icon-theme.cache` is excluded from Git and regenerated during installation/audit.

DarkCold's original source and install paths are preserved, now with their missing images and font restored. Cursor masters, compiled cursor roles, symlinks, and UserCSS remain in their component directories.

The old whole-repo checksum files are retained under `docs/provenance/pre-source-recovery-*` as historical records, not current completeness validators. Release archives remain optional witnesses.

## Install and rollback

Install icons with `bash icons/coonie-aero-hoard/install.sh --user`; it preserves an existing installation in a timestamped backup directory. Run the component uninstall helper to remove the new selection and restore that backup as described in its README. DarkCold's installer/uninstaller preserve their existing rollback behavior.

For repository rollback, the starting commit above retains the previous state. Use a separate checkout or a normal revert when needed; no force-push or history rewrite is required.

The source recovery makes no visual redesign. Linux Mint 21.3/Cinnamon/Nemo visual behavior was not exercised; the existing runtime regression list remains authoritative for that follow-up.

## Executed validation

GitHub import run https://github.com/GayCoonie/Coonies-Linux-Themes-etc/actions/runs/34004890192 passed all recovery gates and committed the full source tree as `2d1d6037e0bd05ffe899201e6789958f256b97d6`. That job independently verified the 115,933 artwork hashes, indexed directories, DarkCold structural/install/uninstall behavior, image formats, and GTK icon-cache generation on Ubuntu with Python 3.12/Pillow 12.3.0.

The local source packaging test also produced a complete portable package and a Debian package accepted by `dpkg-deb --info`. The source tree, rather than those test packages, is the delivered result.

## Remote checkout verification and subsequent edit

After the import, an independent Git fetch verified all 115,933 icon blobs against the saved source bytes. The live tree contains 117,519 file entries, including 1,282 DarkCold files and 99 cursor files/aliases. Main was advanced without force to `0303d5f7f8d2d5f5ca3a584b0fc8c2c6e95e147e`.

This verification section was added through a subsequent ordinary connector `update_file` operation on the existing file in `main`, using its current blob SHA. It demonstrates ongoing Contents API edits after the bulk source import, without a separate CLI login.
