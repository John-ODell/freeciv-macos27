# Production chooser: a list that opens by itself (issues 372, 373, 374; patches 0071 to 0073)

John's play test, 2026-10-29:
- clicking "Unit needs orders" should snap the map so the unit is in the centre;
- "If a city needs to make something, the screen for what that city can make should pop";
- it should be a list, not rows, separated into "units", "buildings", "great wonders" and so on.

## Changes

- **0071** (`client/gui-qt/edgebar.cpp`): every click on "Unit needs orders" centres the map on the unit it leaves selected. Before, moving to the next unit (as W does) scrolled only when that unit was off screen.
- **0072** (`client/gui-qt/citydlg.cpp`): with the Freeciv45 layout, the production chooser is one column. It shows the city's name, then Units, Buildings, Great Wonders, Small Wonders and Other, each under a heading that can't be picked, then Cancel. Each row has the picture, the name and the turns to build. Screenshot: `ui/production/list.jpg`.
- **0073** (`client/gui-qt/edgebar.cpp`): with the Freeciv45 layout, during the player's own phase and while the game window is active, a city that finished its build with nothing queued, or was just founded, centres the map and opens its chooser beside it.
  - After a pick, the next such city opens.
  - Closing one without a pick stops this for the rest of the turn; the "City needs production" button still lists the rest.
  - The button opens the chooser too, instead of the city dialog.
  - No chooser opens while a modal box or another popup is up.
  - Screenshot: `ui/production/chain.jpg`.

## Tests

Offscreen UI driver (`scripts/ui-drive.sh`, sound off), civ45 with freeciv45iso, John's client options. `uidrive.diff` gained `center` (log the tile at the middle of the map view), `activate` and `chooser last`. `dismiss` no longer closes a production chooser. Scripts: `ui/production/choose2.txt` and `choose4.txt`. The key log lines are in `run-choose2.txt` and `run-choose4.txt`.

| Check | Result |
|---|---|
| Unit centring | Two Warriors placed mid-continent. The centre tile went from 13,31 to 25,27 (the unit's tile) on each of two clicks. |
| Founding two cities | A chooser opened at once for one (11 rows). After picking Scout, the other's opened (9 rows). Cancel closed it with no further chooser. |
| Founding a third after Cancel | No chooser that turn (stopped by the Cancel). |
| Turn start | At turn 6 Gamma, Alpha and Beta had finished their builds. Gamma's chooser opened by itself; after a pick, Beta's opened. |

## Found while testing

- The city overlay opens for a newly founded city (the stock new-city popup), and the "what next" button treats a city shown in the overlay as seen. So the chooser keeps its own record of the cities it has opened this turn; otherwise a new city never got one.
- The driver's `dismiss` closes any popup, so in the first turn-start runs it closed the chooser the moment it opened. The test, not the client, was at fault; `dismiss` now leaves the chooser alone.

## Not checked

- A real screen and a visible window (all runs offscreen).
- Heading colours in other themes (issue 377).
- A turn start with many cities waiting, in a long game.
