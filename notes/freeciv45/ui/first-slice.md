# The first slice of the Freeciv45 unit bar: an unapplied client diff

Date: 2026-10-17. Design: `panels.md` section 5.3. Issue: #95.

`first-slice.diff` in this folder is the minimum unit bar, prepared as a diff against the fork's Qt client. It is
**not applied** to `port/freeciv` and is **not** in `patches/`: the ruleset work owns both right now. Everything
below was done in a scratch copy of the fork (`git archive HEAD` of the fork at `6777c85`, built with meson in
`/private/tmp`), and the fork itself was only read.

## What it does

With the new Qt client option "Freeciv45 unit bar" (`gui_qt_freeciv45_panels`, default on, Interface section):

- The focus unit is shown in a bar centred at the bottom of the map: its map image at 64 px with a health bar
  under it (green above two thirds, yellow above one third, red below), its name in bold, its veteran level and
  home city on a second line, and a third line "str A / D   moves M   hp h/H", with "(Selected N units)" after it
  when more than one unit is in focus.
- To the right, one chip per own unit on the focus tile (at most eight, then a "+N" chip that opens the stack
  chooser). The focus units have a highlight ring. Click a chip to focus that unit alone, Shift+click to add it.
- Under the chips, the actions: go to (G), fortify (F, only when the unit can fortify), sentry (S, only when it
  can), skip (W) and done (Space). Icons are the theme's `goto`, `fortify`, `sentry`, `wait` and `done` icons; the key
  hint comes from the shortcut table, so a rebound key shows the new one; the tooltip is the menu's text.
- The bar hides when nothing is in focus, and the old `hud_units` widget hides while the option is on. Switch the
  option off and the old widget is back; the bar then stays hidden.
- A click on the portrait centres the map on the unit.

Not in this slice (design sections 5.4 and 2.4): the combat odds tooltip, `[` and `]` chip cycling, the build and
pillage and upgrade and disband actions of the first row (John's decision 2), theming through `resource.qss`
(the bar uses the palette: `QPalette::Base` for chips and buttons, `Highlight` for the focus ring and hover).

## Files

| File | Change |
|---|---|
| `client/gui-qt/unitbar.h`, `unitbar.cpp` | New: `unit_portrait`, `unit_chip`, `unit_action_button`, `unit_bar` |
| `client/options.h`, `client/options.c` | The option, its default and its entry in the options table |
| `client/gui-qt/gui_main.cpp` | `apply_panels` callback: refresh the bar and the old widget when the option flips |
| `client/gui-qt/fc_client.h`, `fc_client.cpp` | `unitbar_wdg` member, nulled in the constructor, re-placed on resize |
| `client/gui-qt/pages.cpp` | Create the bar on the map view next to the other overlays |
| `client/gui-qt/mapview.cpp` | `update_unit_info_label` feeds the bar on every focus change |
| `client/gui-qt/hudwidget.cpp` | `hud_units::update_actions` hides and returns while the option is on |
| `meson.build`, `client/gui-qt/Makefile.am` | The new files in the moc and source lists |

688 lines added, 2 removed, 12 files.

## Apply and build

From the repo root, with the fork clean (check with `git -C port/freeciv status`):

```bash
git -C port/freeciv apply --check notes/freeciv45/ui/first-slice.diff
```

```bash
git -C port/freeciv apply notes/freeciv45/ui/first-slice.diff
```

```bash
scripts/build.sh qt
```

Then run `~/freeciv-builds/qt/bin/freeciv-qt` as usual. To make it patch 0008 later: commit it on the fork's
`macos27-port` branch and `git -C port/freeciv format-patch -1 -o ../../patches --start-number 8`, as the earlier
patches were made (unverified: the exact command the ruleset lane uses).

`git apply --check` passed against the fork at `6777c85` (the commit the scratch copy was taken from) and again at
`be05401` (the fork's head on 2026-10-17 16:05, after the ruleset lane's later commits; dry run only, the fork was
not changed).

## Tested

- Builds clean: `ninja -C build freeciv-qt` in the scratch copy, Qt 6.12.0 from Homebrew, meson release
  build with `-Dclients=qt -Dnls=false -Daudio=none`; no warnings from the new files.
- Ran the scratch client against the installed server (`~/freeciv-builds/qt/bin/freeciv-server`, civ45
  ruleset, map size 2, `revealmap START`, trident tileset, fresh options file) and captured the window at turn 1:
  - `first-slice-on.png`: the bar for the start stack's Explorer: portrait and full health bar, "Explorer",
    "green", "str 0 / 1   moves 1   hp 10/10", three chips (Settlers, Workers, Explorer, the focus ring on the
    Explorer), and four actions (go to, sentry, skip, done; fortify is absent because an Explorer cannot fortify).
    `hud_units` is hidden. `first-slice-bar.png` is the bar alone at Retina size.
  - `first-slice-off.png`: the same client restarted with `gui_qt_freeciv45_panels = FALSE` in the options file:
    today's `hud_units` panel is back and the bar is hidden.
- The two screenshots are the "before and after" that design section 5.6 asks for.

## Not tested

- Clicks on chips, buttons and the portrait, and the hover colour: the machine has no Accessibility grant for
  scripted input (#87), so they were not exercised. The handlers call the same functions the menu and keyboard
  use (`key_unit_fortify`, `key_unit_sentry`, `key_unit_wait`, `key_unit_done`, `execute_shortcut(SC_GOTO)`,
  `unit_focus_set`, `unit_focus_add`, `unit_select_dialog_popup`), so the risk is in the wiring, not the actions.
- Flipping the option while the game runs (`apply_panels`); only a restart with the option off was tried.
- A stack of more than eight own units (the "+N" chip), a wounded unit's bar colours, a unit with a home city,
  and more than one unit in focus.
- Retina sharpness of the portrait: the pixmap carries the pixel ratio, and the capture at 2x looks sharp, but
  the map image it is cut from is the tileset's 1x sprite scaled up, so it is as soft as the sprite.
- The autotools lists (`Makefile.am`) were edited by hand and not built; our builds use meson.
- Fonts: the name uses the client's default font in bold and the two lines under it the notify-label font
  (Monospace 8 by default), which reads small at 1x. Worth a look on a non-Retina screen.

## Known rough edges, for the next slices

- Chips and buttons take their box colour from `QPalette::Base`, which is light in the NightStalker theme, so they
  show as white squares. Design section 2.5 wants them themed through `resource.qss`; the widgets have object
  names (`unit_bar`) ready for it but no stylesheet yet.
- The old `hud_units` is hidden by an early return in `update_actions`; its `unit_info_pos` settings and the
  drag handling still exist and are harmless.
- The bar is a child of the map view and is placed on every resize, but it is not moved when the sidebar is
  toggled; the map view resizes then, so the resize event covers it (not verified).
