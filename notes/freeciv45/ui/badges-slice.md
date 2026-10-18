# Notification badges on the right edge (patches 0022 and 0023)

Date: 2026-10-18. Design: `panels.md` section 8.2, `hud-layout.md` section 5. Issue: #143. Follows the top strip and
right-edge column of patch 0018 (`edges-slice.md`).

## What it does

With `gui_qt_freeciv45_edges` on, the right-edge column shows a round badge under its buttons for each unvisited
message that has a place to go, newest at the top.

- **Which messages.** Every message in the client's message list (`struct message`) with a tile
  (`location_ok`) and not yet visited. The list is what the messages log shows, so the client's message options
  decide what gets in: with the default options the city founding (`E_CITY_BUILD`), worklist (`E_WORKLIST`) and
  production-changed events never reach it, and so never become badges (observed, `client/options.c`
  `message_options_init`).
- **How many.** As many as fit under the buttons, at most eight, then a "+N" badge for the rest. On the
  1600 x 1000 test screen all nine fit; a shorter window shows fewer and a bigger N, recomputed when the column's
  height changes.
- **Kind.** The event's section of the message options picks the icon and the border colour: city (city,
  improvement and wonder events; Cities icon, gold), diplomacy (diplomat actions, enemy diplomats, treaties;
  Nations icon, blue), military (unit events; Units icon, red), research (Research icon, green), and other (nation,
  global, hut, vote and the rest; a flag, grey). `common/events.h` now exports `enum event_section_n` and
  `get_event_section()`, which were private to `events.c`. The tooltip is the message text.
- **Click.** An own city's city event opens the city overlay (`meswin_popup_city`); anything else centres the map on
  the tile (`meswin_goto`), closing an open overlay first. Either way the message is marked visited: the badge goes
  and the message turns italic in the log, as a click in the log does. A click in the log removes the badge too.
- **"+N".** Closes the overlay, returns to the map tab and scrolls the messages log to the oldest message that has
  no badge. The log stays where it is today (bottom left, the chat's widget), as `panels.md` 8.2 says.

## Files

| File | Change |
|---|---|
| `client/gui-qt/edgebar.h`, `edgebar.cpp` | `edge_badge`; `edge_column::update_badges()` and its resize hook |
| `client/gui-qt/messagewin.h`, `messagewin.cpp` | `real_meswin_dialog_update` and a click in the log refresh the badges; `messagewdg::show_unvisited()` |
| `common/events.h`, `events.c` | `enum event_section_n` moved to the header, `get_event_section()` |
| `data/themes/gui-qt/NightStalker/resource.qss`, `System/resource.qss` | `edge_badge` blocks, one border colour per kind |

## Checked

- `scripts/build.sh qt --no-install-deps` on a clean worktree of the fork: 48 compiler warnings, the same set as the
  build before the change, none in `client/gui-qt` or `common/events.c`.
- The test driver on a copy of the fork with the change, `scripts/ui-drive.sh badges-test/badges.txt`, civ45 with
  three AIs, seed 42, trident, NightStalker, offscreen at 1600 x 1000 (1x). The messages came from the server's
  Lua (`notify.event` with a tile and an event of each kind). Every line ran:

| Check | Result | Shot |
|---|---|---|
| Start | No badges (the start messages have no tile) | log |
| One message of each kind, then a city | Five badges, newest at the top: city (gold), research (green), hut (grey), diplomacy (blue), military (red) | `badges-test/01-badges.jpg` |
| Hover the military badge | The message text as the tooltip | `edges-badges.jpg` |
| Click it | The map centres on its tile (origin 299 to 389), the badge goes, four left | `badges-test/03-military-visited.jpg` |
| Click the city badge | The city overlay opens on Testburg, the badge goes | `badges-test/04-city-badge-overlay.jpg` |
| Ten more messages | Eight badges and "+5" (13 waiting) | `badges-test/05-plus-badge.jpg` |
| Hover "+5" | "5 more messages; opens the messages log" | `badges-test/06-hover-plus.jpg` |
| Click "+5" | The log scrolls to the oldest message without a badge | `badges-test/07-plus-log.jpg` |
| Option off, on | Column hidden, then back with the same badges | log |
| End turn | Turn 2; the badges stay, since the turn's messages are kept | log |
| The same on a 1600 x 700 screen (`badges-test/badges-short.txt`) | Four badges and "+9", the last one clear of the column's bottom margin | `badges-test/09-short-screen.jpg` |

Patch 0023 is the review's fix: the room for badges first ran to the column's bottom edge, so a window with just
enough height for one more badge would have pushed the last one into the 10 px bottom margin.

- The driver (`bar-test/uidrive.diff`) now lists only the visible buttons of the column in each state line, with a
  badge's text ("+5") before its tooltip.

Not exercised: a real mouse on John's screen, Retina 2x, the Classic and Necrophos themes (they have no
`edge_badge` block, so badges draw as plain tool buttons there), a message whose city is gone by the time of the
click (the client's own `meswin_popup_city` guard then only centres), and the autotools build.
