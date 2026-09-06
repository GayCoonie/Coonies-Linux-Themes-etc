# Source asset policy

The working Git tree contains the actual artwork, fonts, cursor files, CSS, metadata, aliases, scripts and licenses required to maintain and install the themes. Binary images are first-class source assets, not optional release baggage.

Do not replace artwork with a reconstruction recipe, checksum, preview or a statement that it exists elsewhere. A fresh checkout must work without unpacking a release archive or fetching an untracked donor tree.

Release archives are optional historical witnesses and distribution products. Their per-file size restrictions do not justify omitting the ordinary PNG/SVG/XPM files they contain. Preserve upstream attribution and licenses. Keep intentionally distinct paths even when Git internally deduplicates identical blobs.

For future updates, commit changed assets through connector blob/tree/commit/ref operations or an already-authorized Git workflow, and verify the remote commit. A local change or returned blob SHA alone is not a saved branch update.
