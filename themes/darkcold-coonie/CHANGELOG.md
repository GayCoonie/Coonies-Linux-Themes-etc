# Changelog

## 2.2.2 — 2026-08-29

- Added Cinnamon's supported `-st-icon-style: regular` override globally, so battery, network, sound, Bluetooth, popup menus, OSDs, notifications, switchers, and other Cinnamon UI resolve full-color artwork even when their JavaScript requests symbolic icons.
- Reinforced the override on panel and icon actors so later base-theme rules cannot quietly restore symbolic rendering there.
- Extended the same full-color preference across the GTK 3 and optional GTK 4 application layers.
- Preserved the user's independently selected icon theme; this changes Cinnamon's lookup style, not the active icon-theme setting.

## 2.2.1 — 2026-08-29

- Rebalanced the Coonie application chrome around a dark bisexual purple/pink body, with blue reduced to a narrow cool shadow and aqua reserved for sharp electrical rims.
- Changed GTK 2/3/4 and Cinnamon scrollbar hover/active states from blue-centered glow to deep purple, magenta, and hot-pink glass with a small aqua edge.
- Made focused Muffin and client-side titlebars use the same purple/pink-first ramp.
- Restored Original DarkCold's nine-slice bitmap wells for panel buttons, window-list items, applets, status buttons, and scrollbar handles instead of relying on flattenable CSS backgrounds.
- Restored full-color applet artwork treatment and dimensional icon shadows while retaining an aqua fallback for symbolic status icons.

## 2.2.0 — 2026-08-29

- Replaced the global brightness-based Coonie recolor with component-aware spectral ramps modeled on SlickCold's layered state system.
- Restored multicolor glow to focused titlebars, Cinnamon panel chrome, selected rows, menus, buttons, progress fills, tabs, and GTK 4 compatibility styling.
- Gave minimize, maximize/restore, menu, and close controls distinct purple, seagreen, spectral, and hot-pink identities while preserving the original glass relief.
- Added subdued color to unfocused window chrome instead of falling back to plain grayscale.
- Stopped changing the active icon theme by default; packaged inheritance shims now require explicit `--icons` opt-in.
- Made uninstall preserve any separately selected icon theme, including an icon theme chosen after an older Darkcold release was applied.

## 2.1.1 — 2026-08-29

- Fixed the GTK 3.24 selector and unsupported sizing properties reported when Muffin loaded the theme on Mint 21.3.
- Unified GTK client-side and Muffin server-side window controls on the same artwork and dimensions.
- Added restore/unmaximize client-side decoration states.
- Reworked the Cinnamon panel and task buttons with the original textured glass assets, sharper relief, and stronger etched accents.

## 2.1.0 — 2026-08-29

- Rebased GTK 2, GTK 3, and GTK 3.20 on OriginalSeed's image-backed DarkCold renderer after live Mint 21.3 comparison.
- Restored the original etched rules, black-metal gradients, compact sizing, square bevels, glossy titlebars, and old-school controls.
- Added shading-preserving raster recoloring for the Coonie purple, seagreen, vivid-blue, and pink edition.
- Kept current headerbar, popover, file chooser, places sidebar, switch, decoration, and CSD coverage from DarkCold's GTK 3.20 stylesheet.
- Removed the build-time Sass dependency and added validation for the authentic DarkCold assets.

## 2.0.0 — 2026-08-29

- Rebuilt DarkCold as a paired modern Cinnamon theme family.
- Added Cinnamon 6.0–6.6+ compatibility architecture.
- Added the Coonie purple, seagreen, blue, pink, and white variant.
- Integrated GTK 2, GTK 3, GTK 4/libadwaita compatibility, and Muffin/Metacity.
- Added Belligerent Madness with fallback glyph coverage.
- Added icon inheritance, Plank, Firefox, and terminal modules.
- Added reversible per-user install/apply/uninstall behavior and diagnostics.
- Added reproducible builds, structural validation, sandbox install tests, and packaging.
