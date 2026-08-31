---
name: maintain-linux-theme-ecologies
description: Maintain, port, audit, or repair Coonie's layered Linux desktop themes, icon themes, cursor themes, and application skins while preserving their historical visual character. Use for GTK/Cinnamon/Muffin, Nemo, icon fallback or symbolic overrides, Xcursor, or cross-toolkit theme work; not for generic UI redesign.
---

# Maintain Linux Theme Ecologies

Treat a desktop appearance as a cooperating ecology of independently selected layers, not one monolithic theme. Preserve the existing visual language while repairing the exact compatibility boundary that failed.

## Begin with the intended gestalt

For Coonie's theming work, the stable aim is a personal, tactile, colorful desktop with mid-2000s/Y2K/Frutiger-Aero energy: Vista glass and software candy, XP-era readable structure, DarkCold machinery, beveled or dimensional controls, real images, and visible character. Aqua/sea-green, blue, purple, pink, chocolate, cream, and near-black may coexist; purple or multicolor accents should not silently collapse into generic dark blue.

This is compatibility archaeology, not modernization. Preserve weirdness that is part of the identity. Do not flatten controls, remove glow or gradients, replace image icons with monochrome glyphs, or optimize for contemporary visual cohesion unless Coonie specifically asks. Coverage and character outrank minimalism.

Use screenshots, installed sources, and earlier working packages as primary witnesses. Labels such as “Frutiger Aero” or “2005” are routing descriptions, not substitutes for inspecting the actual reference.

## Resolve the real component boundary

Before editing, record the exact target environment and active component for each layer that matters: GTK widgets, Muffin/Metacity decorations, Cinnamon shell, icons and symbolic fallbacks, status assets, Xcursor, application overrides, and typography. Do not infer that a GTK package also supplies Cinnamon or working Muffin decorations.

## Audit before patching

1. Preserve the supplied package and reference screenshots.
2. Inventory metadata, inheritance, imports, asset paths, aliases, and supported toolkit versions.
3. Reproduce the issue at the smallest owning layer.
4. Compare both the reference appearance and current runtime rendering.
5. Distinguish missing source, wrong inheritance, selector drift, scaling, toolkit behavior, packaging, and caching.

Keep historical source, adaptation, generated derivative, and current patch distinct. Record borrowed assets and licenses.

## Make bounded repairs

Patch the narrowest owning layer first. Reuse dimensional source assets where possible. When recoloring, inspect gradients, shadows, borders, disabled/hover/active states, titlebars, scrollbars, and image assets—not only variables. Preserve full-color panel artwork, fixed icon-size semantics, cursor masters/hotspots/timing, and unrelated user changes.

## Required regression witnesses

Check titlebar controls and drag/resize, purple or multicolor active states, colorful glow, pictorial panel icons, Nemo icon/compact/list sizes on Mint 21.3, fallback inheritance, the DarkCold “tiny black coffin,” cursor roles and hotspots, and readable fonts/dialogs/disabled states. Capture before/after screenshots for meaningful visual changes.

## Package and hand off

Validate directory names, metadata, imports, executable helpers, archive contents, and install paths. State tested versions and unexercised layers. End with component changes, governing witnesses, checked regressions, remaining gaps, and reversible install/rollback instructions.
