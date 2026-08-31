# Component Matrix

| Layer | Repository owner | Activation | Primary failure evidence |
| --- | --- | --- | --- |
| GTK 2/3 widgets | `themes/darkcold-coonie/dist/themes/*/gtk-*` | Cinnamon theme settings | controls, selections, scrollbars, dialogs |
| GTK 4/libadwaita bridge | DarkCold optional compatibility layer | explicit `--gtk4` install/apply option | CSD/headerbars escaping classic theme |
| Muffin/Metacity decoration | `themes/darkcold-coonie/dist/themes/*/metacity-*` | window-border setting | titlebar color, buttons, drag/resize |
| Cinnamon shell | `themes/darkcold-coonie/dist/themes/*/cinnamon` | desktop/shell theme setting | panel, menu, OSD, calendar, applets |
| Icons | `icons/coonie-aero-hoard` | icon-theme setting | missing names, fallback drift, Nemo scale |
| Status symbols | Cinnamon selectors plus Aero Hoard names | shell lookup and CSS | battery/Wi-Fi/audio flattened or recolored |
| Cursors | `cursors/coonie-aero-gel-v1` | cursor-theme setting | wrong role, hotspot, alias, timing, scale |
| ChatGPT skin | `userstyles/Coonieglass-ChatGPT.user.css` | Stylus/UserCSS manager | web app escaping desktop language |
| Typography | DarkCold font assets and Fontconfig | installer/apply options | hostile fallback, missing glyphs, metrics |

The active desktop may select these independently. Diagnose the exact owner before editing a neighboring layer.
