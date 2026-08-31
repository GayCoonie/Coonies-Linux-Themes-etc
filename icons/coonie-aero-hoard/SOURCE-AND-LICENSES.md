# Sources, provenance, and licenses

Coonie's Aero Hoard is a curated aggregate. Each icon remains under its donor
project's license; the build scripts and original packaging text are GPL-3.0-or-later.
The per-file `manifest/icons.jsonl` identifies the donor and exact upstream path
for every installed asset. Trademarked application logos belong to their
respective owners.

| Donor | Role in this theme | Upstream | License represented in the checkout |
| --- | --- | --- | --- |
| Oxygen Crystal Diamond (`ocd`) | Primary KDE 3/4-era glossy library; itself combines Oxygen, Crystal Diamond, Crystal Project, and related free icon work | https://github.com/niko-yanev/ocd | Mixed free-art notices collected in its `LICENSE` and README; principally LGPL-2.1+/LGPL-3+, with identified GPL components |
| Crystal Remix | Modernized Crystal names and classic Everaldo art | https://github.com/dangvd/crystal-remix-icon-theme | LGPL (upstream README; original Crystal Clear notice is LGPL-2.1+) |
| Oxygen Refit 2 | Glossy GNOME/GTK actions, MIME types, devices, and status art | https://gitlab.com/Nanolx/oxygenrefit2 | LGPL-3.0 |
| nuoveXT 2.3 | Golden folders and unabashedly mid-2000s GTK art | https://github.com/redtide/icon-theme-nuovext | LGPL-3.0 |
| GNOME Colors / GNOME Noble | Colorful GNOME 2-era vocabulary and folder source art | https://github.com/gnome-colors/gnome-colors | GPL-2.0 |
| Newaita Reborn | Newer application names with dimensional, colorful art | https://github.com/cbrnix/Newaita-reborn | GPL-3.0 |
| Papirus | Last-resort modern name coverage only; never chosen when an aesthetic donor has the icon | https://github.com/PapirusDevelopmentTeam/papirus-icon-theme | GPL-3.0 |

The exact commits used for the packaged release are recorded in
`manifest/source-commits.json`. Complete license texts and upstream credit files
are installed in the theme's `licenses/` directory.

## Crystal / Nova7-style folder layer

The default folder family uses Crystal Remix's vertical, translucent PNG art,
including its hand-tuned fixed-size files and its native blue, green, grey, red,
and yellow variants. Coonie's Aero Hoard adds resized Nemo view steps and
colorized aqua, cyan, seagreen, teal, purple, pink, orange, brown, black, and
white derivatives from that same Crystal Remix art. These derivatives retain
the upstream Crystal Remix LGPL terms.

Nemo compatibility aliases such as `folder-open`, `folder-visiting`,
`folder-drag-accept`, and `inode-directory` intentionally resolve to this same
family. The latter is installed in both Places and MIME contexts because GIO
and Nemo can request either vocabulary.

## Redistribution note

This package preserves the source-format SVG where upstream supplies it and
preserves PNG as the preferred modification form where that is all the donor
distributes. Keep this document, the `licenses/` directory, and the manifest
with redistributed copies. Because the aggregate contains GPL-covered assets,
do not relicense the whole archive under more restrictive terms.
