# Play test at patch 0073 (2026-10-30)

One tester session, offscreen only, sound off (the driver client never opens a sound device). Build: the driver build `port/drv-0073` (the series 0001-0073 plus the test-only UI driver, `ui/bar-test/uidrive.diff`), civ45, tileset freeciv45iso, John's client options. Every client and server I started is gone. Scripts and run commands are in `playtest-0073/scripts/`; the run folders stay under `port/runs/test-0073/` and are not in the repo.

**What "played" means here.** The client was driven by scripts through the UI driver: end of turn, the "Unit needs orders" button, picks in the production chooser, `key f` to fortify. Nobody looked at a screen. New cities after the first came from Lua (`edit.create_city`), not from Settlers walking out. I measured what the driver's state log says; where I only read code or guessed, it says so.

## Findings

| # | Severity | Finding |
|---|---|---|
| [384](https://github.com/John-ODell/freeciv-macos27/issues/384) | High | A chooser stays open for a city that was removed on the server; a pick then runs on the freed city. With `MallocScribble=1` the client dies with SIGSEGV in `city_get_queue`. |
| [385](https://github.com/John-ODell/freeciv-macos27/issues/385) | Medium | In the 100-turn game the minimap, chat and "what next" button vanished at turn 12 and never came back (cause not found). |
| [386](https://github.com/John-ODell/freeciv-macos27/issues/386) | Low | The diplomacy tab for an Egyptian AI was named "Iroquois" (the player) and had no portrait. |

Comments on [332](https://github.com/John-ODell/freeciv-macos27/issues/332) and [363](https://github.com/John-ODell/freeciv-macos27/issues/363) with the autogame result.

## 1. Long human-seat game (the main test)

`scripts/gen2.sh 100 > p100.txt`, then `FREECIV_DRIVE_AIFILL=6 FREECIV_DRIVE_REVEAL= FREECIV_DRIVE_DISP= FREECIV_DRIVE_START="set startunits ccwwxdd" scripts/drive.sh p100.txt out-p100 5732` (`drive.sh` is `scripts/ui-drive.sh` with a longer loop limit and settings from the environment). Seed 42, six AIs, civ45 defaults (barbarians "Raging hordes", map size from the ruleset's tiles per player). 100 turns in 3016 s.

Each turn the script: closes the city overlay ("Return to map"), every third turn founds a city by Lua beside the player's others (from turn 40 every fifth), tries the chooser four times with a row that rotates between the sections, clicks the what-next button and fortifies three times, then ends the turn.

| Measured | Result |
|---|---|
| Turns | 100, no crash, no hang |
| Choosers that opened by themselves | 98, on 78 of the 100 turns; two on 20 of those turns (the chain: after a pick the next city's chooser opened) |
| Rows in a chooser | 10 at the start, 31 at the end (the list grows with the techs) |
| Player cities at the end | 22 (the capital from the Settlers, 21 from Lua); none lost |
| AI cities at the end | 4 to 15 (issue 346's picture) |
| Server log | no error, assert or warning; client log: only Qt offscreen notices |
| Barbarian units (player 7) | 6 at T50, 17 at T75, 13 at T100; no city of the player's was taken |

- **0073 chain**: it held for the 78 turns that needed it. It stopped being reachable by button from turn 12, see [385](https://github.com/John-ODell/freeciv-macos27/issues/385).
- **0072 list**: sections, turn counts and Cancel were exercised (picks in rows 2 to 5, `chooser last`). I did not look at the list on a screen in this run; `ui/production/list.jpg` is still the only picture.
- **0071 centring**: exact in the three mid-map samples (`coal.txt` run: the centre tile equalled the unit's tile at 21,24, 23,27 and 25,29, and the 2 to 4 tile offsets seen for units within a few tiles of the map edge look like the edge clamp; inferred). In the long game the button was gone after turn 12, so only the first 11 turns have clicks, and those were all on the capital's own stack.
- One thing the player does: the stock new-city overlay covers the map and hides the minimap, chat and the button until "Return to map" is clicked; the chooser opens beside it. Clicking anywhere else closes a chooser unpicked and stops the chain for that turn (as designed). A test that clicked "Return to map" before the first pick lost the whole turn's chain, which cost me three restarts.
- The game window was reported inactive in 63 of 108 state lines from turn 23 on. The chain does not run in an inactive window by design; whether this happens with a real window I can't say (offscreen driver).
- Picks from the first rows built a lot of Settlers, Workers and Warriors: 121 units and 2 gold at turn 100. That is my pick pattern, not a finding.

Screenshot: `playtest-0073/long-game-t60.jpg` (turn 60: no minimap, no button, two Historian boxes).

## 2. Breaking the chooser

Seven scenarios, each its own game (`scripts/gen3.sh`, split into `sc1.txt` … `sc9.txt`, run by `runsc.sh <n> <scribble>`), human seat plus two AIs, a chooser opened by the 0073 chain, then the event. With `MallocScribble=1` in the environment (freed memory filled with 0x55) except where noted.

| Event with the chooser open | Result |
|---|---|
| City removed (`City:remove`), then a pick | **Crash** in `city_get_queue` ([384](https://github.com/John-ODell/freeciv-macos27/issues/384)); the chooser stayed on screen after the removal. Without scribble: no crash (`sc1`, scribble 0) |
| City transferred to an AI, then a pick | Chooser stays open, `no own city`; pick goes out; no crash |
| Turn change | Chooser closed, no crash |
| Diplomacy meeting opened (`meet`) | Chooser stays, pick works |
| City dialog opened (`opencity`) | Chooser stays, pick works |
| City removed, then Cancel | No crash |
| Game ended (`endturn` on the last turn) with the chooser open | No crash; the chooser stays on screen after the game over (not picked afterwards: my edit to try that did not apply) |

Screenshot: `playtest-0073/chooser-open-before-removal.jpg` (the chooser open for the new city, before the removal).

Not tested: incite (no way to trigger it by script; transfer is the closest), a city sold (the Lua API has no sell), the worklist filled from the city screen while the chain runs (the driver has no worklist command; `opencity` with a chooser open worked). The code reading is in 384: `qtg_popdown_city_dialog` and `client_remove_city` close the city dialog but nothing closes a `production_widget`.

## 3. Barbarians against a light defence

Taken from the long game, not a separate run: the player's cities each held one Warriors; none of 22 was lost in 100 turns, barbarian units peaked at 17 (T75). In the 12-AI game below barbarians took 2 cities and the log has 16 city transfers in all. No "Cannot even build a fallback" line and no error spam in either server log. Compared with `barbarians-357.md` (map seed 7, one Spearmen per city, 1 of 5 games lost a city): same order of size, but this is a default-map game with a lot of land to hide in, so it says little about fairness on an island map. "Feels fair in a real seat": not assessed.

## 4. Coal, badges, borders, city sizes (264, 261, 251)

**Not done.** I tried to paint a 13 x 13 patch of glacier, tundra, desert and grass with coal on hills, iron and gold on mountains (`scripts/coal.txt`) and centre on it with the what-next button. The Lua only changed terrain next to land and the patch landed on the map edge or in the sea, so I never got coal next to iron and gold on screen. No screenshots, nothing checked for tundra or desert hills, and nothing for badges, river outlets, borders over snow and desert, or city sizes.

## 5. Twelve-AI autogame

`scripts/auto475.sh 42 out-auto42`: seed 42, 12 AIs, civ45 defaults (victories SPACERACE|ALLIED|CULTURE, barbarians on), the 0073 driver build's server, to turn 475. Ended at the turn limit in under 25 minutes. Server log: no error, assert, crash or "Cannot even build" line. The server announced "Scenario victory to the Malis" (Mali, 9 cities). Largest at the end: Russians and Mongols, 15 cities each; the player-seat Hittites had 4. All 12 civs were still alive; the Barbarians held 2 cities. `spaceship.state=0` for all 14 players in the final save: no ship was started, so nothing new against 332 and 363 (see the comments there). Tech lists were not read.

## 6. Diplomacy portraits

`scripts/port.txt` with `playernation` for Egyptian, Danish, French and Marco Polo for the player, then `meet` for each AI. 

- Danes tab: the Danish portrait shows on the right (`portrait-danes.jpg`).
- French tab (not painted): no portrait, no error (`portrait-french-fallback.jpg`).
- Egyptian partner: tab named after the player and no portrait ([386](https://github.com/John-ODell/freeciv-macos27/issues/386), `portrait-egyptian-missing.jpg`).
- Mood against attitude: **not tested.** The driver's `hover portrait` found no target, and I had no way to move an AI's love by script.

## How it felt to play

Honest limits first: this was a driven session, so "felt" means what the logs and a few screenshots show, not hands on a mouse.

- The 0073 chain does what it says over a long game. 98 choosers in 100 turns with a growing list never blocked a turn, hung the client or opened for the wrong city while the cities were only added.
- The break test is where the design is thin: the chooser trusts a pointer, and the pointer can go away. Everything else I threw at it (turn change, a meeting, the city dialog, game over) it survived.
- A wide player will see the chooser every third turn or so in my script, always beside a city that now has the overlay open behind it. The overlay hiding the minimap and the button until closed is easy to forget; if 385 is real, forgetting it is permanent.
- The first rows of the chooser are units, so a quick pick builds units. With 22 cities that ran the treasury to 2 gold at turn 100 in my script. A player would pick buildings; I can't tell from here whether the list's order nudges them towards units.
- The game itself: by turn 100 the six AIs sat on 4 to 15 cities each, the player on 22 only because Lua founded them.

## Not tested

Coal, badges, river outlets, borders, city sizes (item 4); mood against attitude (6); a real Settlers-led expansion; incite and sell; worklist from the city screen while the chain runs; a real window (everything was offscreen); an island-map barbarian game with a human; the 0072 list's look in other Qt themes (377).
