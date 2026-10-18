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

Then run `~/freeciv-builds/qt/bin/freeciv-qt` as usual. It is patch 0015 (applied 2026-10-17, issue 123): it was committed on the fork's
`macos27-port` branch and `git -C port/freeciv format-patch -1 -o ../../patches --start-number 15`, as the earlier
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
  showed as white squares. Fixed in patch 0015 (issue 99): see "Patch 0015" below.
- The old `hud_units` is hidden by an early return in `update_actions`; its `unit_info_pos` settings and the
  drag handling still exist and are harmless.
- The bar is a child of the map view and is placed on every resize, but it is not moved when the sidebar is
  toggled; the map view resizes then, so the resize event covers it (not verified).

## Patch 0015 (2026-10-17, issue 123)

The diff above went onto the fork's `macos27-port` as commit 31e5b14 and `patches/0015-Freeciv45-unit-bar-a-bar-under-the-map-for-the-focus.patch`,
with three changes for issue 99 on top:

- `unit_action_button` has a `hint_color` property (`Q_PROPERTY(QColor hint_color MEMBER hint_color)`, default the
  old yellow), so a theme sets the key hint colour with `qproperty-hint_color`.
- NightStalker's `resource.qss` gives `unit_bar` a dark translucent background, light label text, dark chip and
  button boxes, a light focus ring and a yellow hint. The chips and buttons paint from their palette, which the
  stylesheet's `background-color` (Base), `color` (Text) and `selection-background-color` (Highlight) set
  (type selectors work because all three classes have `Q_OBJECT`).
- System's `resource.qss` gives the bar a light background with dark text, since the native palette's black text
  was unreadable on a see-through bar over the map. Classic and Necrophos have no rules yet.

`git apply` was clean on the fork at 9c9b25c (after patch 0014). `scripts/build.sh qt` (with
`FREECIV_SRC=port/freeciv`, since the worktree has no fork of its own) built and installed it with no warnings
from the new files. The client then ran against the installed civ45 server (`set revealmap START`, 4 AIs,
`dispersion 0`, seeds 42), with a throwaway `HOME` whose options file named the theme, and each client window was
captured alone with `screencapture -l` at turn 1:

| File | What it shows |
|---|---|
| `unit-bar-stack-nightstalker.png` | NightStalker, the start stack: the Explorer in focus (ringed), Workers and Settlers as chips, go to, sentry, wait and done with G, S, W and Space |
| `unit-bar-unit-nightstalker.png` | NightStalker, `set startunits x`: one Explorer, one chip |
| `unit-bar-stack-system.png` | System, the same stack on the light bar |
| `unit-bar-window-nightstalker.jpg` | The whole window with the bar in place under the map |

Not exercised: clicks on chips, buttons and the portrait, the hover colour, and a unit moving (the shell has no
Accessibility grant for scripted input, and that setting is John's); the "+N" chip; a wounded unit; the option
switched off; the Classic and Necrophos themes. The client log repeats `qt.svg: Invalid path data; path
truncated.` from an icon the bar does not draw (unverified which).

## Exercised in a running game (2026-10-17, issue 125, patch 0016)

Every control of the bar was clicked and hovered in a local civ45 game, and the option was switched off and on while
the game ran. Scripted input from outside the process is refused on this Mac (#87), so the clicks come from inside
it: `bar-test/uidrive.diff` adds a small driver to a copy of the fork (never to the fork itself) that reads a
script, sends input through QTest to the main window, the path a real mouse takes (Qt hit-tests, sends enter and
leave, starts the tooltip timer), logs the focus, the stack and the bar after each step and grabs the window with
every open top-level painted on. `scripts/ui-drive.sh` starts the server and the driver client; `bar-test/bar.txt`
is the script; how to build the driver copy is in the script's header.

The game: civ45, three AIs, seeds 42, map size 2, `revealmap START`, `dispersion 0`, `startunits cwxdd` (two
Warriors, an Explorer, Workers and Settlers on one tile), trident, NightStalker, Qt 6.12, turn 1. Damage and the
ninth to thirteenth unit came from `/lua cmd` lines (`edit.unit_add_hitpoints`, `edit.create_unit`).

| Check | Result | Shot (`bar-test/`) |
|---|---|---|
| Bar for the start stack | Warriors in focus and ringed, five chips, all five actions | `01-start` |
| Tooltips: action buttons | "Go to Tile (G)", "Fortify Unit (F)"; the hovered button lights up | `02-hover-goto`, `03-hover-fortify` |
| Tooltips: chips, portrait, "+N" | "Explorer HP:10/10 Idle", `unit_description()` on the portrait, "4 more units on this tile" | `04-hover-chip`, `06b-hover-portrait`, `18-hover-plus` |
| Click a chip | Focus moves to that unit alone (#107 to #106), the bar follows | `05-chip-select` |
| Shift+click a chip | Both in focus, "(Selected 2 units)", fortify left out since the Explorer cannot fortify | `06-chip-shift-add` |
| W on the keyboard | Focus moves on (#107 to #106) and the bar follows | log only |
| Fortify | The Warriors are Fortifying, focus moves to the next unit | `07-fortify`, `12b-hover-fortified-chip` |
| Sentry | The second Warriors are Sentry, focus moves on | `08-sentry` |
| Skip (wait) | Focus moves to the Workers; the Explorer stays idle and comes back after the others | `09-skip` |
| Done | Focus moves to the Settlers; after the go-to, focus passes over the Workers to the Explorer, so they are done for the turn | `10-done` |
| Go to | The button enters goto mode (`hover_state` 1); a tile picked two south, one west sends the Settlers off: one step taken, orders left, focus moves on | `11-goto-mode`, `12-goto-moved` |
| Portrait click | The map, scrolled 400 by 300 px away, centres on the unit again | log only |
| Wounded unit | Health bar yellow at 5/10, red at 2/10; the hp in the stats line and the chip tooltip follow | `13-wounded-yellow`, `14-wounded-red` |
| Option off, then on, in game | Off: the bar hides and today's `hud_units` is back. On: the bar is back, `hud_units` hidden | `15-option-off`, `16-option-on` |
| Twelve own units on the tile | Eight chips and "+4"; the "+4" chip opens today's stack chooser with all twelve | `17-plus-chip`, `19-plus-chooser` |

What broke, all fixed in patch 0016 (`client/gui-qt/unitbar.cpp` only):

- **#129** After any focus change while the bar was up it shrank from 465 to 249 px and the chips, buttons and
  stats line piled up: children added to a visible widget stay hidden until the next event loop pass, so
  `adjustSize()` measured the bar without them. Each new chip and button is shown before the bar is measured.
- **#130** `clear_row` deleted every chip and button with `delete`, including the one whose press or click handler
  was still running (a chip's `unit_focus_set`, a button's `key_unit_*` both refresh the bar). They are now hidden
  and deleted later. The driver itself crashed on this once, by sending the release to the freed chip.
- **#131** No portrait tooltip, and no activity on the chips; both now as `panels.md` section 2 says.
- **#132** With several units in focus, fortify and sentry were offered when only the head unit could do them.

Noticed, not filed:

- At game start two modal boxes block the main window until closed: the ruleset's "Welcome to this game" message
  and, when the client is not on trident yet, the tileset suggestion. A player closes them; the driver's `dismiss`
  closes the welcome box. Declining the suggestion leaves the square map drawn by amplio2, as `client-look.md` found.
- The stack chooser opens at the real pointer (`QCursor::pos()`), which the driver does not move, so its place in
  `19-plus-chooser` is wherever the mouse happened to be.
- The bar's width follows its contents (465 px for a Warriors stack, 426 px with four actions), so it shifts a little
  as the focus moves; a fixed width per stack size could come with the second action row.
- The client keeps its options path in a 256-byte buffer (`client/options.c`); a throwaway HOME under the long
  session scratch path truncated it, so the runner points `FREECIV_OPT` at a short relative path.

Not exercised: the Classic and Necrophos themes, a non-Retina screen, more than one turn, and real hardware input
(the driver's events go through Qt's own window path, not through macOS). One run was disturbed by a click into the
client window while it was on screen (a sentry hit the wrong unit and the client was closed); the reruns are clean
and give the same log line for line.
