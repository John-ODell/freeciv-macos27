# The first slice of the Freeciv45 map edges: top strip and right-edge column (patch 0018)

Date: 2026-10-17. Design: `panels.md` section 8 (8.1, 8.2 and 8.5) and decision 9. Issue: #140.

John played the Freeciv45 client and found that the left side "still has the same old things": the Qt sidebar of
`qt-today.md` (`qt-today-sidebar.png`). Patch 0018 on the fork replaces it, behind its own option.

## What it does

A new Qt client option, **`gui_qt_freeciv45_edges`** ("Freeciv45 top strip and edge buttons", Interface page,
default on), hides the sidebar and puts two frames around the map. It is a separate switch from the unit bar's
`gui_qt_freeciv45_panels`, so either can be turned off alone.

- **Top strip** (`top_strip`, 32 px at 1x, full width over the map and the column). Left to right: research (the
  tech, bulbs per turn, "done/cost (N turns)"; "Choose research" in the theme's attention colour when nothing is
  set), gold and income "50 (+1)", the rates "Tax 40 Lux 0 Sci 60", culture "Culture 1100 (+1)", then at the right
  end the year and turn and **End turn**. Each number is a button: research opens the science report, gold the
  economy report, the rates the rates dialog, culture the nations report, and the turn returns to the map. End turn
  is greyed out while the turn cannot be ended and takes the attention colour when every unit has moved, as the
  sidebar's Turn Done did (`side_disable_endturn`, `side_blink_endturn`). Tooltips: the science text, the government's
  maximum rate, and `get_info_label_text_popup()` on the turn.
- **Right-edge column** (`edge_column`, 64 px wide). Round 44 px buttons (`edge_button`): Map, Research, Nations,
  Cities, Units and Economy, each opening today's report as the sidebar did (a second click closes it), and More, a
  menu for Demographics, Wonders of the World, Top Cities, Achievements and Spaceship.

The strip refreshes with the sidebar's tooltips (`fc_client::update_sidebar_tooltips`), which run on the player,
research and turn packets. Culture's "(+N)" is the history gained this turn (`nation_history_gain` plus each city's
`city_history_gain`), the part that accumulates; the total is the server's figure and also counts performance.
With the city overlay open both frames stay (decision 8). Switching the option off brings the sidebar back and
removes both frames at once, in game.

## Not in this slice

- Notification badges on the right edge: #143.
- The "what next" button above the minimap: #144. Until then End turn sits at the right end of the strip.
- The tile box above the minimap (8.4), strategic resources in the strip (a later ruleset slice), overviews as a
  modal over a dimmed map (they open as today's report tabs), the sidebar's mouse-wheel and right-click extras
  (next city, next enemy unit, the indicators menu), and the Classic and Necrophos theme blocks.

## Files

| File | Change |
|---|---|
| `client/gui-qt/edgebar.h`, `edgebar.cpp` | New: `top_strip`, `edge_button`, `edge_column`, `apply_freeciv45_edges()` |
| `client/options.h`, `options.c` | `gui_qt_freeciv45_edges`, default on |
| `client/gui-qt/gui_main.cpp` | The option's callback |
| `client/gui-qt/pages.cpp` | Build the strip in row 0 and the column in column 3 of the game page grid; hide the sidebar or them by the option; refresh the strip with the sidebar's tooltips |
| `client/gui-qt/sidebar.cpp` | End turn's enabled and attention states follow the Turn Done widget's |
| `client/gui-qt/fc_client.h`, `fc_client.cpp` | `topstrip_wdg`, `edgecolumn_wdg` |
| `data/themes/gui-qt/NightStalker/resource.qss`, `System/resource.qss` | `top_strip`, `edge_column`, `edge_button` blocks |
| `meson.build`, `client/gui-qt/Makefile.am` | The new files |

The game page is built inside `fc_client`'s constructor, before `gui()` is set and before the page's layout is put
on its widget, so the page only hides there: calling `gui()` crashed the first build at start, and showing a
widget that has no parent yet would open it as a window of its own.

## Checked

- `scripts/build.sh qt --no-install-deps` into `~/freeciv-builds/qt`: no compiler warnings.
- The test driver (`bar-test/uidrive.diff`, which gained `tip TEXT` targets for icon-only buttons, `option NAME
  on|off`, closing an open menu on `dismiss`, and the strip, column, sidebar and current report tab in each state
  line) on a copy of the fork at patch 0018, `scripts/ui-drive.sh edges-test/edges.txt`, civ45 with three AIs, seed 42,
  map size 2, trident, NightStalker, offscreen at 1600 x 1000 (1x). Every line ran:

| Check | Result | Shot |
|---|---|---|
| Start | Sidebar hidden; strip 1600 x 32 with research, gold, rates, culture, turn, End turn; column at x 1536, 64 wide, seven buttons | `edges-strip-column.jpg` |
| Hover gold | Its tooltip | `edges-test/02-hover-gold.jpg` |
| Research, Nations, Cities, Economy | Each opens its report tab (`science_report`, `plr_report`, `city_report`, `eco_report`); the strip and column stay | `edges-test/03-research.jpg` |
| Map | Back to the map tab | log |
| Units, twice | The units report opens over the map, then closes | `edges-test/07-units.jpg` |
| Rates, culture, gold on the strip | The rates dialog, the nations report, the economy report | log |
| More | The menu with five entries | `edges-test/09-more-menu.jpg` |
| End turn on the strip | Turn 2, 3950 BCE | `edges-test/10-turn2.jpg` |
| Option off | Strip and column gone, sidebar back | `edges-test/11-option-off.jpg` |
| Option on, then a new city | Strip and column with the city overlay; research "+1 0/30 (30 turns)", gold "+1", culture "+1" | `edges-test/12-city-overlay.jpg` |

- The same start in the System theme: `edges-strip-column-system.jpg`.
- `scripts/ui-drive.sh` now runs the client offscreen by default (a 1600 x 1000 screen through
  `QT_QPA_PLATFORM=offscreen:configfile=...`), so a drive run opens no window over the desktop; `UI_DRIVE_VISIBLE=1`
  shows it again.

Found and fixed during the runs: the start-up crash above; the column's icons drew at about 18 px inside the
circles because the theme's 100 px icons are mostly padding (now 38 px icons in a 44 px button); and More used the
`preferences-other` icon, which reads as a close cross (now `list-add`).

Not exercised: a real mouse and keyboard on John's screen, Retina 2x, the Classic and Necrophos themes, a turn
timeout (the strip appends the timeout text to the turn), an observer connection (the strip then shows only the
turn), and the autotools build.
