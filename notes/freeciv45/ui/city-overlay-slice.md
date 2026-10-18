# The first slice of the Freeciv45 city overlay: an unapplied client diff

Date: 2026-10-17. Design: `panels.md` section 3 and item 3 of its 5.4. Issue: #135.

`city-overlay-slice.diff` in this folder is the minimum city overlay, prepared as a diff against the fork's Qt
client at `49ba373` (patch 0016), the same way `first-slice.diff` was for the unit bar. It was prepared in scratch
copies of the fork (everything under "Checked" below) and then applied to `port/freeciv` unchanged as patch 0017
(issue #137; see "On the fork" at the end).

## What it does

With the Freeciv45 panels option on (`gui_qt_freeciv45_panels`, the unit bar's switch, default on), opening one
of the player's own cities no longer opens the city dialog over the map. The map stays, scrolls to centre the city
and draws its worked tiles (the client's own city colouring, `toggle_city_color`), and four parts sit on the map's
edges:

- **Yields, top left (360 px wide).** The city name and size; "grows in N turns", "starving in N turns", "growth
  blocked" or "not growing", and the granary as stock/size; then one tile per yield: food, shields, trade and gold
  as their surplus with a sign, luxury and science as their total, and the city's culture. Each tile's tooltip is
  the full dialog's breakdown (`get_city_dialog_output_text`, `get_city_dialog_culture_text`).
- **Sections, right (300 px wide).** A column of sections that fold with a click on their heading (the arrow
  turns; the column shrinks with them), the state kept for the session: **Citizens**, the tileset's citizen icons
  in their final mood and a count line ("1 content"; specialists by their plural name); **Buildings**, what the
  city has, wonders first and in bold, the upkeep total in the heading, each row's tooltip the building's help
  text (the full dialog's `get_tooltip_improvement`). The list is as tall as its rows and scrolls once the map has
  no more room.
- **Production, bottom left (380 px wide).** Change and Buy above the current build: its sprite, its name, the
  full dialog's "s/S N turns" line and a thin progress bar. Change opens today's production chooser
  (`production_widget`); a click there changes the build now. Buy shows the price, asks with the same box as the
  full dialog and buys; it is greyed out with a tooltip that says why (bought already this turn, the city was
  founded this turn, nothing to buy, or the treasury in gold).
- **Footer, bottom centre (340 px wide).** "Full dialog" (also Enter) closes the overlay and opens today's dialog
  for the same city; "Return to map" (also Escape) closes it.

While the overlay is open the unit bar, the minimap and the chat give their edges up and come back when it closes
(each only if it was showing before). The focus unit is kept. A click on another own city swaps the overlay to it;
a click on the same city keeps it open. Closing stops the worked-tile drawing if the overlay started it and leaves
the map where it is. The overlay refreshes from the same calls as the dialog (`real_city_dialog_refresh`), and
also from the info label's update, so the treasury and a new turn reach Buy and the worked-tile drawing (a new turn
turns every city's drawing off, `handle_start_phase`). It closes itself when the city is lost.

Switch the option off and a city opens the full dialog as today; switching it off while the overlay is open closes
the overlay. Foreign cities (those the player may inspect) still open the dialog, and close the overlay first.

## Not in this slice

As `panels.md` 5.4 orders them: the round city marker and its hit test, the header (name, rename, previous and
next city, status icons), the production queue, the Units section, specialist clicks in Citizens, selling a
building, worked-tile clicks on the map, keyboard Tab order and the arrow keys, the chooser anchored to the
production part (it opens at the pointer, as it does from the dialog), Great people, and the Classic and Necrophos
theme blocks.

## Files

| File | Change |
|---|---|
| `client/gui-qt/cityoverlay.h`, `cityoverlay.cpp` | New: `city_part` (the base of the four parts), `city_yields`, `city_section`, `city_sections`, `city_production`, `city_footer`, and `city_overlay`, the mode: `open_for`, `refresh`, `close_overlay`, `full_dialog`, `place` |
| `client/gui-qt/citydlg.h`, `citydlg.cpp` | `qtg_real_city_dialog_popup` sends own cities to the overlay (and hides the dialog if it is up); its old body is now `real_city_dialog_popup_full`; refresh, is-open and the two popdowns consult the overlay too |
| `client/gui-qt/fc_client.h`, `fc_client.cpp` | `cityoverlay_wdg` member, nulled in the constructor, re-placed on resize |
| `client/gui-qt/pages.cpp` | Create the overlay on the map view next to the unit bar |
| `client/gui-qt/mapview.cpp` | `fc_client::update_info_label` refreshes the open overlay (gold, turn) |
| `client/gui-qt/mapctrl.cpp` | Escape closes the overlay (then cancels as before); Enter opens the full dialog while it is open |
| `client/gui-qt/unitbar.cpp` | The bar stays hidden while the overlay is open |
| `client/gui-qt/gui_main.cpp` | The option's callback closes the overlay when the option goes off |
| `data/themes/gui-qt/NightStalker/resource.qss`, `System/resource.qss` | `city_part` blocks: the unit bar's translucent box and text colours, a transparent buildings list, the progress bar |
| `meson.build`, `client/gui-qt/Makefile.am` | The new files in the moc and source lists |

1163 lines added, 2 removed, 15 files. No change to `common/`, `server/` or `client/*.c`.

The parts are themed like the unit bar: they are `QFrame`s with `Q_OBJECT`, so `resource.qss` type selectors
reach them (`city_part` matches all four, `city_yields` and the rest one each). A first version painted its own
box from the palette; in NightStalker that was a light box under the theme's light label text and could not be
read, so the box moved to the stylesheet.

## Apply and build

From the repo root, with the fork clean:

```bash
git -C port/freeciv apply --check "$PWD/notes/freeciv45/ui/city-overlay-slice.diff"
```

```bash
git -C port/freeciv apply "$PWD/notes/freeciv45/ui/city-overlay-slice.diff"
```

```bash
scripts/build.sh qt
```

`git apply --check` is clean against the fork at `49ba373`. The diff also applies before or after the test
driver's `bar-test/uidrive.diff` in either order (checked both).

## Checked

- **Build.** A fresh `git archive` of the fork at `49ba373` with only this diff, built with
  `FREECIV_SRC=<copy> FREECIV_PREFIX_ROOT=<scratch> scripts/build.sh qt --no-install-deps` (Qt 6.12.0, meson release):
  clean, and none of the 48 warnings is in `client/gui-qt` (they are the bundled Lua and the server's, as on every
  build). `logs/build-qt.log` was put back afterwards. The autotools list was edited by hand and not built.
- **In a running game,** with the test driver (`bar-test/uidrive.diff`, which gained `button`, `label`, `city`,
  `chooser`, `accept` and `endturn` for this) in a second copy and `scripts/ui-drive.sh`, script `city-test/city.txt`, shots cropped or scaled from the 2x window grabs:
  civ45, three AIs, seeds 42, map size 2, trident, NightStalker, Qt 6.12. The city came from
  `/lua cmd edit.create_city` on the start stack's tile, the gold for Buy from `edit.change_gold`.

| Check | Result | Shot (`city-test/`) |
|---|---|---|
| A new city | Opens the overlay at once (the server asks for the popup); Escape closes it | `01-new-city` |
| Click on the city tile | The overlay, not the dialog: the four parts, the unit bar, minimap and chat hidden, the worked tiles drawn | `02-overlay` |
| Yields | "Testburg size 1", "grows in 10 turns granary 0/20", +2 +2 +2 +1 0 1 0; hover on Food gives the breakdown | `03-hover-food` |
| Sections | Citizens (one content), Buildings (Palace, upkeep 0); Citizens folds and the column shrinks from 131 to 90 px, and unfolds again | `04-hover-buildings-heading`, `05-citizens-folded` |
| Buy on the founding turn | Greyed out, "Cannot buy in the turn the city was founded" | `06-buy-founding-turn` |
| Change | Opens the chooser; picking an item changes the build to Axemen, the part follows (0/25, 13 turns) | `07-chooser`, `08-changed` |
| Next turn, gold added | The worked tiles still drawn, Buy enabled at 72 gold, "Treasury contains 451 gold." | `09-turn2` |
| Buy | The question box; OK buys: stock 25/25, "1 turn", gold 451 to 379, Buy greyed out at "0 gold" (as the full dialog shows it) | `10-buy-box`, `11-bought` |
| Escape | The parts close, the bar, minimap and chat come back, the worked tiles are no longer drawn | `12-closed` |
| Enter | Opens today's full dialog for the city | `13-full-dialog` |
| Open again with the dialog up | The dialog hides, the overlay opens | `14-reopened` |
| Return to map | Closes as Escape does | log only |
| Option off | A click on the city opens the full dialog; no overlay | `15-option-off` |

What the runs turned up, all fixed in the diff before it was written down:

- The parts painted a light box from the palette under NightStalker's light text: unreadable. Now themed in
  `resource.qss` like the unit bar.
- After End Turn the worked tiles were no longer drawn while the overlay stayed open: the client clears every
  city's colouring at the start of a phase. The overlay draws it again on refresh.
- Buy stayed greyed out after the treasury grew: gold arrives with the player's info, not the city's. The info
  label's update now refreshes the overlay.
- Folding Citizens left the column at its old height: the scroll area kept its own size hint. The buildings list
  is now sized to its rows and the column's layout is redone on a fold.
- Found reading the diff for review, not in a run: a foreign city's dialog would have opened with an own city's
  overlay still up. It now closes the overlay first. The diff-only build (incrementally) and the drive script ran again after
  this change: same log, line for line.

Noticed, not filed:

- The test city sits two tiles from the map's top edge, and the map does not scroll past an edge it does not wrap,
  so the "centred" city shows near the top of the view, under the yields part's height. A real game would show the
  same at any non-wrapping edge.
- The chooser opens at the real pointer (`QCursor::pos()`), which the driver does not move (`07-chooser`), as
  `first-slice.md` found for the stack chooser. Anchoring it to the production part is listed for a later slice.
- After the full dialog had been open once, the parts came back a few pixels taller (the yields part from 68 to
  76 px). Probably a font refresh from the dialog; unverified, harmless.

Not exercised: the System, Classic and Necrophos themes, a non-Retina screen, a city big enough for the buildings
list to scroll, a city lost while open, a foreign city, swapping straight from one own city to another, real
hardware input (the driver's events go through Qt's window path), and the autotools build.

## On the fork (patch 0017, issue #137)

Applied unchanged to `port/freeciv` as commit `0baacdb` and exported as
`patches/0017-Freeciv45-city-overlay-an-own-city-opens-as-panels-o.patch`. `git -C` runs `apply` inside the fork, so
the diff's path must be absolute (`$PWD/...` above); a relative path is read from `port/freeciv` and is not found.

- `scripts/build.sh qt --no-install-deps` built it into `~/freeciv-builds/qt` with no compiler warnings; the installed
  `freeciv-qt` carries the overlay (`nm -C` lists 18 `city_overlay::` symbols) and the installed NightStalker and
  System `resource.qss` have the `city_part` blocks.
- The installed client started a civ45 game under `QT_QPA_PLATFORM=offscreen` and stayed up; no window was shown.
- The driver build (`git archive` of the fork at `0baacdb` plus `bar-test/uidrive.diff`) ran `city-test/city.txt`
  offscreen: all 84 lines and 15 shots, the same states as the table above. The offscreen screen was 1600 x 1000 at
  1x through `QT_QPA_PLATFORM="offscreen:configfile=<json>"` with one `screens` entry (the default offscreen screen
  is about 800 x 800). `city-overlay-on-map.jpg` is the overlay on a new city from that run.

