# Coonie's Linux Themes, Icons, Cursors, and App Skins

The working repository for **Linux and general Theming**: a maintained habitat of tactile, colorful, mid-2000s/Y2K/Frutiger-Aero desktop parts for Linux Mint Cinnamon and the applications that escape the desktop theme.

This is compatibility archaeology, not a modernization exercise. Vista glass, XP-era readable structure, DarkCold machinery, dimensional controls, image-backed chrome, saturated aqua/purple/pink accents, pictorial icons, and a little productive weirdness are intentional.

![DarkCold Coonie preview](assets/previews/darkcold-theme-preview-uploaded.png)

## What is here

| Component | Current witness | Editable source | Exact release |
| --- | --- | --- | --- |
| GTK/Cinnamon/Muffin theme | DarkCold Coonie 2.2.2 | [`themes/darkcold-coonie/`](themes/darkcold-coonie/) | [`releases/darkcold/`](releases/darkcold/) |
| Icon ecology | Coonie's Aero Hoard 1.1.2 | [`icons/coonie-aero-hoard/`](icons/coonie-aero-hoard/) | Source kit and release records in [`releases/icons/`](releases/icons/) |
| Xcursor theme | Coonie Aero Gel v1 | [`cursors/coonie-aero-gel-v1/`](cursors/coonie-aero-gel-v1/) | [`releases/cursors/`](releases/cursors/) |
| ChatGPT skin | Coonieglass Aqua Hoard Terminal | [`userstyles/Coonieglass-ChatGPT.user.css`](userstyles/Coonieglass-ChatGPT.user.css) | Same file is the installable UserCSS |
| Continuity | project instructions, history, field notes | [`docs/`](docs/) | versioned in Git |
| Maintenance method | theme-ecology skill | [`skills/maintain-linux-theme-ecologies/`](skills/maintain-linux-theme-ecologies/) | versioned in Git |

## Start here

- Theme work: read [`themes/darkcold-coonie/README.md`](themes/darkcold-coonie/README.md). For the full asset test, extract the 2.2.2 release archive and run `tools/test.sh` inside the extracted tree.
- Icon work: read [`icons/coonie-aero-hoard/README.md`](icons/coonie-aero-hoard/README.md). The compact source kit expects curated donor repositories beside it in `../sources`.
- Cursor work: read [`cursors/coonie-aero-gel-v1/README.md`](cursors/coonie-aero-gel-v1/README.md). Its source bundle rebuilds the Xcursor files from the atlases.
- Cross-component work: read [`docs/COMPONENT-MATRIX.md`](docs/COMPONENT-MATRIX.md), [`docs/REGRESSION-CHECKLIST.md`](docs/REGRESSION-CHECKLIST.md), and [`AGENTS.md`](AGENTS.md).

## Repository validation

```bash
python3 scripts/validate_repository.py
```

This performs structural, archive, metadata, UserCSS, and cursor-alias checks without installing anything. Runtime visual checks still require the target Mint/Cinnamon/Nemo environment.

## Current target

The strongest concrete compatibility witness is Linux Mint 21.3 with Cinnamon 6.0.x and Nemo 6.0/5.8-era icon behavior. Later Cinnamon 6.x is supported by the current DarkCold package where its selectors and settings probing allow it, but each future toolkit release must be verified rather than assumed.

See [`STATUS.md`](STATUS.md) for known limits and the next useful work.
