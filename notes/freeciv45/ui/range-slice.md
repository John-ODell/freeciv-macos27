# A selected unit's movement range (patch 0044)

Date: 2026-10-18. Issue: #232. Goes onto the fork after drag-to-pan (patch 0042, `pan-slice.md`).

## What it does

- With `gui_qt_freeciv45_panels` on, the tiles the head focus unit can reach with the moves it has left are lit
  on the map. The fill is faint (warm white at about a fifth opacity), so terrain, resources and units show
  through, and a pale gold line runs along the range's outer edge, where a lit tile meets an unlit one. The line
  is a 64th of the tile width and at least 2 canvas pixels (3 at 192 x 96, 1.5 pt at 2x). Iso diamonds and
  overhead squares are both drawn.
- The tiles come from the client goto's own path finding, so the range matches where a goto can go this turn:
  moves left, terrain costs, rivers and roads, zones of control, borders, and only tiles the player knows.
  Unknown tiles stay black. Tiles more than a turn away are left out.
- Path finding counts a tile reached on the last move point as next turn with full moves. So the test is the
  moves a tile costs (`total_MC` no more than the unit's moves left), not the turn number.
- The range is worked out again when the focus unit, its tile, its moves or the turn change, checked on the map's
  200 ms timer, and every two seconds anyway for other players' moves (zones of control, borders). It clears
  with no focus unit, when the turn is done, while the city overlay is open, and for a unit the player can't
  order.
- Clicking the focus unit's own tile:
  - While an order is being given (G, patrol, connect and the other modes), the click cancels the order and the
    goto line goes with it. The unit stays selected with no order, and the range is hidden.
  - With no order, the click hides or shows the range. It replaces the stack's selection popup; the unit bar's
    chips select tile mates.
  - On an own city, the click still opens the city, as before.
  - A drag from the unit still sets a goto (patch 0042).
- A hidden range shows again for the next unit or the next turn.

## Files

| File | Change |
|---|---|
| `client/gui-qt/moverange.cpp`, `moverange.h` | New: works out, keeps and paints the range |
| `client/goto.c`, `goto.h` | `fill_move_range_parameter()`, the goto's path-finding parameter for a unit, exported |
| `client/gui-qt/mapview.cpp` | The map's paint draws the range in canvas pixels before the trade routes; the timer checks it |
| `client/gui-qt/mapctrl.cpp`, `mapview.h` | The click on the focus unit: cancel, or show and hide |
| `meson.build` | `moverange.cpp` |

## Checked

- `scripts/build.sh qt --no-install-deps` on the driver's copy of the fork (patch 0044's sources plus the driver's
  four files, `bar-test/uidrive.diff`, which now logs the range): 0 compiler warnings.
- The test driver, `scripts/ui-drive.sh range-test/range.txt` with `FREECIV_DRIVE_SERV="set citymindist 1"` (so
  Lua can make a city next to the start's castle), civ45, freeciv45iso, NightStalker, offscreen on a
  3456 x 2060 screen with `QT_SCALE_FACTOR=2` (1728 x 1030 pt, Retina 2x). The driver's `drag unit 0 0` is a
  click on the focus unit's tile through the window. Every line ran:

| Check | Result | Shot |
|---|---|---|
| Start, Warriors #115 (1 move) on a peninsula tip | 2 tiles: its own and the one land neighbour | `range-test/01-warriors-range.jpg` |
| W twice, Scout #113 (2 moves) | 31 tiles, outlined | `range-test/02-scout-range.jpg` |
| Drag from the Scout to move it | It moves to (10,28), 1 move left; 26 tiles | `range-test/03-scout-moved.jpg` |
| Click on the Scout | Range hidden, 0 tiles, the Scout still in focus with no orders | `range-test/04-click-hides.jpg` |
| Click again | 26 tiles again | log |
| G, then click on the Scout | Hover state 1 to 0, no orders, range hidden | `range-test/05-goto-cancelled.jpg` |
| W, Workers #112 | Range shown again, 2 tiles | log |
| A Lua city made under the Workers, its overlay closed, then a click on the Workers | The city overlay opens, as before; no range while it is open, 2 tiles once it is closed | `range-test/06-click-in-city.jpg` |
| Space for every unit | No focus, 0 tiles | `range-test/07-no-focus.jpg` |
| End turn | Turn 2, the Scout in focus, 70 tiles with full moves | `range-test/08-new-turn.jpg` |

The state between the end of the turn and the new turn wasn't caught: the AIs finished inside the driver's
300 ms wait. `phase_done` clears the range in the code.

Not exercised: a real mouse on John's screen, a stack's selection popup now replaced by the toggle, the hover
modes other than goto, a zone of control or border changing mid-turn, ships and air units with fuel, overhead
tilesets, the 1x screen, and the autotools build.
