# The sidebar's extras on the map's edges (patch 0027)

Date: 2026-10-18. Design: `panels.md` sections 8.1 and 8.2. Issue: #146, found in the review of #145. Follows the
top strip and right-edge column (patch 0018, `edges-slice.md`), the badges (0022 and 0023) and "what next" (0026).

## What it does

With `gui_qt_freeciv45_edges` on the left sidebar is hidden, and until now its wheel and right-click extras and its
four indicator icons went with it. They are back, on the new edges:

| Where | Wheel up | Wheel down | Right-click |
|---|---|---|---|
| Cities button | The other nations' cities, one by one | Your cities | (none) |
| Nations button | The other nations' capitals | Your capital | The current diplomacy meeting; an observer gets the observe menu |
| Units button | The other nations' units | Wait and the next unit, as W does | Centre on the focus unit |
| Research button | (none) | (none) | A menu of the advances that can be researched now |
| Indicators in the top strip | (none) | (none) | The government menu, as a left click |

- Each extra adds a line to its button's tooltip, for example "Wheel: other nations' cities (up), your cities
  (down)".
- The same functions run as on the sidebar (`center_next_enemy_city`, `center_next_player_city`,
  `center_next_player_capital`, `key_center_capital`, `cycle_enemy_units`, `key_unit_wait`, `side_center_unit`,
  `side_right_click_diplomacy`, `side_right_click_science`); nothing about them changed.
- The wheel first returns to the map tab and closes the city overlay, so it also works from a report. A mouse
  sends one notch (120) a step; a touchpad's smaller steps add up to one, and each notch runs one step.
- The indicators (research progress, global warming, nuclear winter, government) sit left of the year and turn
  as one flat button, each sprite fitted to the strip's 18 px icon height, with the game summary
  (`get_info_label_text_popup()`) and "Click: change the government" as the tooltip. A click or a right-click
  opens the government menu under the button, for a player who can give orders. They are redrawn when the client
  changes the sidebar's (`set_indicator_icons`) and with the strip's numbers.
- Dropped on purpose: the sidebar's fallback right-click, which returned to the map from any button without its
  own. The Map button does that. The sidebar's left click on the indicators also only returned to the map; here a
  left click opens the government menu instead.

## Files

| File | Change |
|---|---|
| `client/gui-qt/edgebar.h`, `edgebar.cpp` | `edge_button` gains a right-click and a wheel action with a tooltip line each; `edge_column::button()` finds a button by its icon; the strip's indicators button and its government menu |
| `client/gui-qt/pages.cpp` | Gives the Research, Nations, Cities and Units buttons the sidebar's extras, next to the sidebar's own wiring |
| `client/gui-qt/mapview.cpp` | `set_indicator_icons` redraws the strip's indicators too |

No theme changes: the indicators button is a flat tool button like the strip's numbers.

## Checked

- `scripts/build.sh qt --no-install-deps` on the driver's copy of the fork, whose sources are patch 0027's plus
  the driver's four files: 0 compiler warnings.
- The test driver, `scripts/ui-drive.sh extras-test/extras.txt` with `FREECIV_DRIVE_SERV="set fogofwar DISABLED"`
  (the start map is revealed, so with no fog the other nations' cities and units are in sight), civ45 with three
  AIs, seed 42, trident, NightStalker, offscreen at 1600 x 1000 (1x). The driver gained `rclick` (the right
  button, through the window as `click` does) and `wheel DELTA tip TEXT`, and logs the indicators and the items
  of an open menu. The map's origin in each state line shows where the map went. Every line ran:

| Turn | Check | Result | Shot |
|---|---|---|---|
| 1 | Start, own city Testburg made with Lua | The four indicators at 1269,21 left of "4000 BCE  Turn 1", icon 78 x 18 | `extras-test/01-start.jpg` |
| 1 | Hover the indicators | The game summary, then "Click: change the government" | `edges-indicators.jpg` |
| 1 | Click, then right-click | The government menu each time: Revolution..., Tribal, Despotism, the rest greyed out | `extras-test/03-gov-menu.jpg` |
| 2 | Cities, wheel up three times | The map goes to the other nations' two cities in turn: origin 299 to 1049, 689, 1049 | `extras-test/04-cities-wheel-up.jpg` |
| 2 | Cities, wheel down | Back to Testburg (origin 299) | log |
| 2 | Cities, touchpad steps of 40 | One step does nothing; after the map is scrolled away (599), two more make a notch and it goes back to Testburg (299) | log |
| 2 | Nations, wheel up twice | The two other capitals in turn: 1049, 689 | `extras-test/05-nations-wheel-up.jpg` |
| 2 | Nations, wheel down | `key_center_capital` ran: the messages log shows its "no capital" line, since the Lua-made Testburg is no capital to the client even with a Palace added by Lua | log |
| 2 | Units, wheel up | The map goes to another nation's unit (origin 1049) | log |
| 2 | Units, wheel down | The focus moves from unit 107 to unit 106, as W does | log |
| 2 | Map scrolled away, right-click Units | Centred on the focus unit again (origin 369 to 299) | log |
| 2 | Right-click Research | A menu of seven advances: Alphabet, Ceremonial Burial, Currency, Hunting, Masonry, Pottery, Warrior Code | `extras-test/06-research-menu.jpg` |
| 2 | Right-click Nations, no meeting open | Nothing happens, as on the sidebar | log |
| 2 | Cities report open, wheel down | Back on the map tab, centred on Testburg | log |
| 2 | City overlay open on Testburg, Cities wheel up | The overlay closes and the map goes to another nation's city (689) | `extras-test/07-after-overlay.jpg` |
| 2 | Option off, on | The old sidebar is back with its own indicators, then the edges again | `extras-test/08-sidebar.jpg` |

In the research menu shot the menu sits at the top left: it opens at the mouse cursor, as on the sidebar, and the
offscreen platform has no cursor of its own.

Not exercised: a real mouse wheel or touchpad on John's screen (the driver sends the wheel event to the button),
the Nations wheel down reaching a real capital, a diplomacy meeting open for the Nations right-click, an observer,
Retina 2x, the System, Classic and Necrophos themes, and the autotools build.
