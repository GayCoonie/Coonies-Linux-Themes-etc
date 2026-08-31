# Coonie Aero Gel

A custom XCursor theme for Linux Mint 21.3 / Cinnamon: glossy purple shells,
sea-green gel, hot-pink edge light, selective electric blue, bubbles, chrome,
and enough Y2K/Frutiger Aero excess to make a sensible desktop nervous.

## Install on Linux Mint

Extract the archive, open the `Coonie-Aero-Gel` folder in a terminal, and run:

```bash
./install.sh
```

That installs the theme for your user and selects it in Cinnamon. Alternatively,
copy the folder to `~/.local/share/icons/`, then choose **Coonie Aero Gel** under
**System Settings → Themes → Mouse Pointer**.

The cursor files contain native 24, 32, 48, and 64 pixel variants. `wait` is an
eight-frame animated jelly ring. Common Cinnamon, GTK, X11, Nemo, Firefox, and
drag-and-drop cursor names and legacy hashes are supplied as aliases.

## Rebuild from source

The source bundle requires Python 3, Pillow, and ImageMagick (`convert` and
`montage`):

```bash
python3 build.py
```

Generated atlases remain in `source/`; sliced working images go to `work/`; the
installable theme and preview go to `dist/`.

## Design map

- normal select: translucent aqua arrow with dark-purple/magenta rim
- links: absurdly friendly gel hand
- text/crosshair/resize: conventional silhouettes with candy acrylic depth
- grab/grabbing: open and clenched squishy hands
- forbidden: extremely pink circle-slash, because errors deserve presentation
- wait: animated orbit of glossy rainbow jelly beans
- progress: arrow plus compact jelly spinner

The fallback inheritance is `DMZ-White`, so an obscure cursor name stays usable
instead of disappearing.
