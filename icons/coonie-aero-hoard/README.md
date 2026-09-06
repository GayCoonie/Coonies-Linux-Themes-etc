# Working with the live source tree

All 115,933 icons now live in `Coonie-Aero-Hoard/` beside `install.sh`. Edit those actual PNG/SVG/XPM files and their corresponding plain-text provenance rows in `manifest/icons/`.

- Install directly: `bash install.sh --user` (preserves a timestamped backup).
- Package current source without donors or release extraction: `bash scripts/build-release.sh`.
- Per-file attribution and hashes: `Coonie-Aero-Hoard/manifest/icons/`.
- Exact historical donor pins: `Coonie-Aero-Hoard/manifest/source-commits.json`.

The older donor-selection rebuild instructions below describe historical development tooling. That workflow is now named `scripts/rebuild-from-donors.sh`; the default packaging command above uses checked-out artwork. GNOME Noble was a generated donor input, so the historical recipe alone does not reproduce the complete original environment.

---

# Coonie's Aero Hoard

An intentionally overstuffed, glossy, colorful Linux icon theme for Cinnamon,
GNOME, MATE, Xfce, and other freedesktop.org desktops.

This is not a restrained design system. It is a cabinet full of candy-colored
glass, plastic, chrome, jewel gradients, smiling old KDE weirdness, late-GNOME
skeuomorphism, and modern app coverage. A deterministic mosaic builder chooses
one visual family per icon name, while vertical Crystal Remix folders—with
layered white sheets, blue glass spines, and hard specular edges—give the theme
a recognizably Nova7-era center.

## Install the release archive

Extract the release and run:

```bash
./install.sh
```

The default is a per-user installation in `~/.local/share/icons`. No root
access is needed. Then choose **Coonie's Aero Hoard** in Cinnamon's Themes
settings. Log out and back in if an already-running application holds stale
icons.

Other installer modes:

```bash
./install.sh --system
./install.sh --destination /some/icon/theme/directory
./uninstall.sh
```

`--system` installs to `/usr/share/icons` and uses `sudo` when necessary.

## What is covered

- Actions, applications, categories, devices, emblems, emotes, international
  markers, MIME types, panel icons, places, status icons, and symbolic names.
- Fixed sizes from 8 through 256 pixels wherever upstream art exists, plus
  scalable SVGs.
- Modern application IDs through Papirus and Newaita-derived coverage.
- Explicit Linux Mint/Cinnamon aliases for Cinnamon, Nemo, Xed, Pix,
  MintInstall, Update Manager, Warpinator, Hypnotix, Timeshift, Blueberry,
  Webapp Manager, and their friends.
- Nemo 5.8 and 6.0 directory-state coverage: singular and plural Downloads,
  open, visiting, drag-target, templates, saved search, `inode-directory` in
  both Places and MIME contexts, and the matching symbolic fallback names.
- Mint-Y-compatible category-first Places directories and exact fixed-size
  matching, so Nemo cannot accidentally render a neighboring or malformed
  legacy raster at an enormous size.
- Aqua, seagreen, cyan, teal, purple, blue, pink, green, yellow, orange, red,
  brown, grey, black, and white folder names.
- A final `hicolor` and `Adwaita` inheritance safety net for future names.

## Build from the curated source checkouts

The build is reproducible once the source repositories are present beside this
project in `../sources`:

```bash
./scripts/build-release.sh
```

Every installed icon has a row in `manifest/icons.jsonl`, including its donor,
upstream path, and SHA-256 digest. `manifest/summary.json` gives counts by
source. See `SOURCE-AND-LICENSES.md` before redistributing.

## Compatibility

The theme follows the freedesktop.org icon-theme layout and generates a GTK
icon cache. It is explicitly audited against the icon vocabulary in Nemo 5.8.5
and Nemo 6.0.2 (the Cinnamon 6 generation used by Linux Mint 21.3), while
remaining freedesktop-compatible with Cinnamon, GNOME, MATE, and Xfce. GNOME's
own shell may deliberately force symbolic icons in a few surfaces, but GTK
applications and file managers use the full-color art normally.
