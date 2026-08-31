# Project Status

## Preserved and editable

- DarkCold Coonie 2.2.2: complete source/build/install/test tree plus `.tar.gz` and `.zip` release witnesses.
- Coonie Aero Gel v1: ready-to-install Xcursor tree, aliases, generated atlases, original Library master sheets, deterministic builder, and release archive.
- Coonie's Aero Hoard 1.1.2: compact reproducible source/packaging kit, preview, audit, checksums, and release summary.
- Coonieglass ChatGPT UserCSS.
- Project custom instructions, historical microhistory, field note, maintenance skill, and regression protocol.

## Known gaps

- The Aero Hoard install archive and Debian package are about 203–205 MB each and exceed GitHub's 100 MB single-file limit. They are intentionally represented by source, checksums, audit, preview, and summary rather than a misleading partial payload.
- The Aero Hoard source kit requires its curated donor repositories to rebuild all 115,933 installed icon files. Those donor checkouts are not embedded here.
- No live Linux Mint 21.3 Cinnamon/Nemo session was available during repository assembly, so static checks do not replace runtime visual verification.
- Nemo's huge-icon regression remains a required runtime witness across icon, compact, and list views.
- GitHub currently reports workflow `startup_failure`/`BuildFailed` before allocating any job. The workflow is preserved, and both of its commands pass locally; repository/account Actions enablement or billing policy must be checked before remote CI can run.

## Next useful work

1. Run the repository validator and component-native tests on Mint 21.3.
2. Capture a baseline screenshot set for panel, menu, Nemo views, GTK dialogs, titlebars, and cursor roles.
3. Record exact donor revisions for an Aero Hoard rebuild and decide whether large binaries belong in Git LFS or GitHub Releases.
4. Turn every runtime defect into a narrow component-specific issue with before/after evidence.
