# Working Rules for This Repository

Treat this desktop as a layered ecology, not one monolithic theme. Before editing, identify the owning layer: GTK widgets, Muffin/Metacity decoration, Cinnamon shell, icons and symbolic fallbacks, Xcursor, application overrides, or typography.

Preserve the intended gestalt: tactile mid-2000s software, Vista glass, XP-era readable structure, DarkCold machinery, bevels, glow, gradients, pictorial assets, and strong aqua/sea-green/purple/pink/blue color. Do not flatten or desaturate the work into a generic contemporary dark theme.

Use existing screenshots, archives, source trees, and earlier working packages as primary witnesses. Keep historical upstream material, Coonie adaptations, generated output, and new repairs distinguishable. Preserve licenses and provenance records.

For every visual change:

1. Name the exact component and target Mint/Cinnamon/Nemo/toolkit version.
2. Keep an unmodified witness or versioned release.
3. Make the narrowest repair that owns the failure.
4. Run static validation and capture before/after runtime evidence when possible.
5. Check the regressions in `docs/REGRESSION-CHECKLIST.md`.
6. Record untested runtime surfaces honestly.

Do not silently replace full-color panel or file-manager artwork with symbolic glyphs. Do not let active purple/multicolor states drift back to generic dark blue. Do not assume a GTK theme includes Cinnamon shell or Muffin decoration. Do not treat syntactic validity as proof of visual correctness.
