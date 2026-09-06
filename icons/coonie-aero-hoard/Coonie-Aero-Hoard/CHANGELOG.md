# Changelog

## 1.1.2 — 2026-08-29

- Fixed the giant Back and Search buttons in Linux Mint 21.3's Nemo toolbar.
- Added exact 16, 22, 24, 32, and 48 pixel regular `go-previous` and
  `edit-find` PNGs. This covers GTK themes that intentionally replace Nemo's
  requested `*-symbolic` names with full-color regular artwork.
- Preserved the same glossy cyan arrow and paper-and-magnifier designs instead
  of replacing them with flat symbolic icons.
- Added release-audit checks for all ten toolbar fallback files and their exact
  pixel dimensions.
- Kept the v1.1.1 Crystal/Nova7 folders, default user/avatar artwork,
  application icons, and remaining interface artwork unchanged.

## 1.1.1 — 2026-08-29

- Added Mint-Y-compatible `places/16`, `places/22`, `places/24`, `places/32`,
  `places/48`, `places/64`, `places/96`, and `places/128` mappings for every
  Crystal/Nova7 folder and Nemo directory-state name.
- Changed fixed-size index entries from threshold matching to exact `Fixed`
  matching, preventing Nemo from choosing a neighboring oversized candidate.
- Removed malformed legacy animation/action sprite strips that GTK could render
  as one enormous icon because the upstream PNGs lacked animation metadata.
- Resized every remaining static PNG whose pixels exceeded its advertised GTK
  directory, including old double-size emblems and mislabeled legacy assets.
- Added release-audit rejection for any oversized PNG that could regress this
  behavior.
- Removed build-time hard-link deduplication so every installed icon path is
  independent during sanitation and package upgrades.
- Kept the v1.1.0 Crystal folder artwork, application icons, and default
  user/avatar asset unchanged.

## 1.1.0 — 2026-08-29

- Replaced the rounded GNOME-Colors folder override with Crystal Remix's
  vertical white-and-blue folder family, matching the Nova7-era silhouette.
- Added native Crystal special folders for Downloads, Documents, Music,
  Pictures, Videos, Templates, public folders, remote folders, home, desktop,
  network, and trash.
- Added Nemo 5.8/6.0 state coverage for `folder-open`, `folder-visiting`,
  `folder-drag-accept`, singular `folder-download`, and related aliases.
- Installed `inode-directory` in both Places and MIME contexts so GIO-backed
  directories do not fall through to a different donor.
- Added hand-sized 16, 22, 24, 32, 40, 48, 64, 72, 96, 128, and 256 pixel
  coverage for the complete Crystal folder layer.
- Rebuilt aqua, cyan, seagreen, teal, purple, pink, orange, brown, black, and
  white variants on the Crystal silhouette; native Crystal blue, green, grey,
  red, and yellow art is preserved.
- Preserved the non-folder icon selection from 1.0.0, including the default
  user/avatar artwork.

## 1.0.0 — 2026-08-29

- Initial maximal Y2K/Frutiger-aero mosaic release.
