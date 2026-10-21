# Freeciv45 as a game of its own

John, 2026-10-20: "Lets do this, but really give it a good effort". Today Freeciv45 is Freeciv with the civ45
ruleset and the freeciv45iso tileset chosen by hand. This plan makes it a game of its own in four parts: its own app,
its own start screen and defaults, its own art throughout, and systems that make it play differently. It stays
GPL and says "built on Freeciv"; the clean-room rule still holds (no Firaxis or 2K names, art, text or data).

Sources: the surveys of 2026-10-20 (packaging, leftover art, systems), cited by file below. `S` is the patched
source tree, `port/freeciv` at patch 0050.

## 1. Its own app (#271)

Now: `scripts/bundle.sh qt` builds `Freeciv.app`, with display name "Freeciv", id `org.freeciv.qt` and the stock
icon `S/data/freeciv-client.icns` (bundle.sh:32-35, 61). The launcher passes argv through unchanged (launcher.c:133-135).
The window title "Freeciv (%1)" and "Welcome to Freeciv" are compiled in (S/client/gui-qt/fc_client.cpp:143-152, 180).

| Unit | What | Kind |
|---|---|---|
| 1a | `bundle.sh --game freeciv45`: `Freeciv45.app`, display name Freeciv45, its own bundle id (not `org.freeciv.*`), the freeciv45iso tileset inside the app, its own `.icns`, and Info and copyright strings that say "Freeciv45, built on Freeciv" | script |
| 1b | The launcher gets the game name at build time and sets `FREECIV_GAME_NAME`; the client uses it for the window title, the welcome line and the About entry, falling back to "Freeciv". One client binary serves both apps | client patch |
| 1c | `dmg.sh` and the DMG README name the game | script |

## 2. Its own start screen and defaults (#272)

Now: "Start new game" passes `--ruleset` from the tileset's `for_ruleset` (S/client/connectdlg_common.c:296,
S/client/tilespec.c:2058-2062). freeciv45iso leaves it unset (freeciv45iso.tilespec:24), so the server falls
back to civ2civ3 (S/common/game.h:674-676). The tileset reaches John's client only through his own rc file and
symlinks (notes/installed.md:126-132). The start image is the tileset's `main_intro_file`, stock `misc/intro`
(freeciv45iso.tilespec:146).

| Unit | What | Kind |
|---|---|---|
| 2a | `for_ruleset = "civ45"` in freeciv45iso.tilespec, so every local game starts on civ45 | data |
| 2b | Freeciv45.app's launcher passes `-t freeciv45iso` until its options file names a tileset, unless the player gives `-t` (so a tileset picked later is kept) | launcher |
| 2c | Our own title picture as `main_intro_file`, and our own window and city icons (`icon.freeciv`, `icon.cityicon`) | art + data |

## 3. Our own art throughout

The tileset is ours for terrain, extras, resources, units, cities, borders, techs and buildings. These parts are still
stock Freeciv, listed by how visible they are in play (freeciv45iso.tilespec:152-197, RECORD.md:84):

| Sheet | Contents | Stock source | Visible |
|---|---|---|---|
| 10 UI on the map | Unit HP bars (11), city size and goto digits (30), focus ring (4), city bar icons (9), goto dots and waypoint (7) | amplio2 tiles, select and terrain1 specs; misc/citybar | high |
| 13 UI icons | Citizens by era (38), specialists (6 used), governments (9), tax, luxury and science icons, the warming sun and cooling flake | misc/small, governments, specialists | high |
| 14 Title art | The start picture, app icon, window and city icons | misc/intro, misc/icons, freeciv-client.icns | high |
| 11 Cursors | goto, attack, nuke, paradrop, patrol, select, teleport, wait, invalid, edit; 6 frames each | misc/cursors | high |
| 15 Effects | Unit explosions (5), nuke blast (1) | amplio2 | medium |
| script | Fog corners (80), map grid (12), city work overlays (6), made like the borders | amplio2 | medium |
| later | Event icons (144), treaty thumbs, spaceship parts, editor tools | misc | low |
| keep | Nation flags and shields: stock Freeciv flags, real-world and GPL, credited | misc/flags | high |

Already made but not yet in the tileset: the maglev retake (art 09 run 7). The airstrip and airbase still draw
amplio2's middle layer over ours (amplio2 bases.spec:30-32), so those tags go.

## 4. Systems that play differently

Built and already unlike Freeciv: stacks where only the loser dies, siege collateral, one strength number with class
counters, great people and golden ages, culture victory, drafting and the whip, strategic resources hidden until
their tech. Still stock Freeciv: governments with anarchy, riots and celebrations, pollution, plague, caravans,
three specialists, the tax/lux/sci rates (mechanics.md; freeciv45-plan.md rows 4 to 12).

The four slices that would most change how a game plays, in the order proposed:

| Order | Slice (freeciv45-plan.md) | Why it changes play | Kind | Size |
|---|---|---|---|---|
| 1 | Religion, simplified (row 12, #273) | Founding a faith with a tech, its spread, temples and a state religion give every game a second map of loyalties, and diplomacy has a reason | Lua, buildings, effects, an AI rule like the great people's | L |
| 2 | Civics in columns (row 8, #274) | Governments become one column of five; each column is a choice with upkeep, so an empire is built from policies rather than one government | Lua swaps one policy building per column; a client panel later | L |
| 3 | Cottages (row 5, #275) | Worked land grows from hamlet to town, so where a city works matters over centuries | ruleset extras | M |
| 4 | Resource happiness and health (row 4, #276) | Each luxury and food resource your nation reaches lifts every city, so trade and conquest are about resources | Lua marker buildings | M |

Each slice gets its own design note in `notes/freeciv45/design/`, a rules test, and a balance game before and after.

## Order of work

1. Units 2a and 1a to 1c, since they only need scripts and data.
2. Codex queues for sheets 14, 10 and 13, then 11 and 15. Each sheet is wired in as it lands, and the maglev
   retake now.
3. Unit 2c once the title art exists.
4. The four slices, one at a time, each with its own issue.
