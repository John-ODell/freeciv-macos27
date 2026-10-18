# The "what next" button above the minimap (patch 0026)

Date: 2026-10-18. Design: `panels.md` section 8.3 and decision 10, `hud-layout.md` section 1. Issue: #144. Follows the
top strip and right-edge column (patch 0018, `edges-slice.md`) and the badges (patches 0022 and 0023,
`badges-slice.md`).

## What it does

With `gui_qt_freeciv45_edges` on, one 224 x 40 button sits right-aligned with the minimap, 8 px above it. It follows
the minimap when the minimap moves or changes size, and hides with it: while the city overlay is open (decision 8)
and while a report tab covers the map. If the minimap sits at the top of the map, the button goes below it instead.

It says what the turn needs next, in decision 10's order, and a click does it:

| Step | When | A click |
|---|---|---|
| Choose research | Nothing is being researched (`researching == A_UNSET`) | Opens the research report |
| Unit needs orders | An own unit is idle, has moves left (or never moves), has no orders, is not done and not automated: the units the client's focus cycles through, waiting ones included | The next unit, as W does; the first such unit if the focus unit already has its orders |
| City needs production | An own city finished something at this turn's start, or was founded this turn, has nothing queued after the current item, and was not seen this turn | Opens the city (the overlay, or the full dialog with the panels off) |
| End turn | Nothing above waits | Ends the turn, as Turn Done does |

- "1 of N" shows on the right when more than one thing waits, counting research, every waiting unit and every
  waiting city.
- The tooltip says what the click does: "5 units wait for orders; shows the next one, as W does", "Testburg has
  nothing queued; opens the city", "End the turn (Shift+Return); nothing else waits".
- End turn is greyed out while the turn cannot be ended and turns green when every unit has moved, as the sidebar's
  Turn Done and the strip's End turn do (`side_disable_endturn`, `side_blink_endturn`).
- The button checks again twice a second, so it follows unit, city and research packets without hooks in each.
- Shift+Return still ends the turn from the keyboard, whatever the button says.

### Cities: from the city's data, not from messages

`panels.md` 8.3 planned to find these cities through this turn's "worklist is empty" and "production complete"
messages. With the client's default message options those events (`E_WORKLIST`, `E_CITY_PRODUCTION_CHANGED`,
`E_CITY_BUILD`) never reach the message list (`client/options.c`, `message_options_init`), so the button reads the
city instead: `city_built_last_turn()` and an empty worklist. Founding stamps `turn_last_built` with the founding
turn, so a stamp equal to `turn_founded` is not counted as a finished build (the first run counted every city
founded the turn before). A city counts as seen for the rest of the turn once it is opened from the button or shown
in the overlay, however it was opened; otherwise a player who keeps the advisor's choice would be asked again until
the turn ends. Not covered: a city founded on turn T that finishes a build at the very next turn change is not asked
about on T+1 (its stamp equals its founding turn; #176).

### The strip's End turn stays

Issue #144 left it to John whether the strip's End turn button goes once "what next" exists. It stays for now,
recorded as decision 12 in `panels.md`; removing it is one line in `top_strip`'s constructor.

## Files

| File | Change |
|---|---|
| `client/gui-qt/edgebar.h`, `edgebar.cpp` | `what_next_button`; `apply_freeciv45_edges()` places it |
| `client/gui-qt/pages.cpp` | Create it with the minimap, as a child of the map, hidden |
| `client/gui-qt/fc_client.h`, `fc_client.cpp` | `whatnext_wdg` |
| `client/gui-qt/sidebar.cpp` | End turn's enabled and attention states reach the button too |
| `data/themes/gui-qt/NightStalker/resource.qss`, `System/resource.qss` | `what_next_button` blocks: amber while something waits, grey for End turn, green when every unit has moved; the labels carry the button's `step` property, since a pseudo-state such as `:disabled` on an ancestor never reaches a child in a Qt style sheet (the first build drew every label in the disabled grey) |

## Checked

- `scripts/build.sh qt --no-install-deps` on a clean worktree of the fork at patch 0026: no warnings in
  `client/gui-qt`; the three the incremental build printed are in the baseline list.
- The test driver on a copy of the fork, `scripts/ui-drive.sh whatnext-test/whatnext.txt` with
  `FREECIV_DRIVE_SERV="set sciencebox 1"` (so each advance is done at the next turn change and nothing is chosen
  next, the one way found to get an unset research in a driven game: Lua's `edit.give_tech` left the research on the
  learned advance), civ45, seed 42, trident, NightStalker, offscreen at 1600 x 1000 (1x). Every line ran:

| Turn | Check | Result | Shot |
|---|---|---|---|
| 1 | Start | "Unit needs orders", "1 of 5"; button at 1293,699, 224 x 40, minimap at 1287,747 230 wide (right edges equal, 8 px gap) | `whatnext-test/01-units.jpg` |
| 1 | Hover | "5 units wait for orders; shows the next one, as W does" | `edges-what-next.jpg` |
| 1 | Click | Focus moves from unit 107 to unit 106, still "1 of 5" | log |
| 1 | Space on all five | "End turn" | `whatnext-test/03-end-turn.jpg` |
| 1 | A new city (Lua), `popup_new_cities` off | "City needs production" | `whatnext-test/04-new-city.jpg` |
| 1 | Click | The city overlay opens; the button hides with the minimap | `whatnext-test/05-city-overlay.jpg` |
| 1 | Return to map | "End turn"; a click on it ends the turn | log |
| 2 | Agriculture done, nothing chosen | "Choose research", "1 of 6" (research and five units; the city founded on turn 1 is not counted) | `whatnext-test/06-turn2-research.jpg` |
| 2 | Click | The research report opens; the button hides with the map | log |
| 2 | Pottery chosen, the city's Spearmen bought, units done | "Unit needs orders", then "End turn" | log |
| 3 | Start | "Choose research", "1 of 8" (research, six units, the city) | `whatnext-test/08-turn3-research-first.jpg` |
| 3 | Alphabet chosen, units done | "City needs production" (the bought Spearmen finished) | `whatnext-test/09-city-finished-build.jpg` |
| 3 | Click, Return to map | The overlay opens; then "End turn" | `whatnext-test/10-end-turn-again.jpg` |
| 3 | Shift+Return | Turn 4 | log |
| 4 | Option off, on | The button hides, then comes back with "Choose research", "1 of 7" | log |

- The System theme at the start: `edges-what-next-system.jpg` (`whatnext-test/whatnext-system.txt`).
- The driver (`bar-test/uidrive.diff`) gained `research NAME`, `opencity NAME` and `key shift+enter`, and logs the
  button's place, text, count, step and the minimap's place in each state line.

Not exercised: the green "every unit has moved" state (the strip's End turn did not blink in these offscreen runs
either, so neither did the button), a real mouse on John's screen, Retina 2x, the Classic and Necrophos themes (no
`what_next_button` block: a plain button there), a minimap moved to the top of the map, alternating-movement phases,
an observer connection, and the autotools build.
