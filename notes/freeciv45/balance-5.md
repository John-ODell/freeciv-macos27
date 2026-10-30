# Freeciv45 balance report 5: win types alone, map types, and whether one leader runs away (issue 330)

John's ask (2026-10-24): test the win types against each other (which is easiest, which hardest), then different land
types (islands, one large connected continent, separate continents), and see whether the bonuses skew towards one
leader.

## Setup

16 AI-only games, run one at a time from 23:19 on 2026-10-24 to 05:40 on 2026-10-25, 899 to 2079 s each
(`balance-5/progress.txt`):

    OUT=<folder> SEEDS="7 42" notes/freeciv45/balance-5/run.sh 475 culture space allied domination conquest islands continents regular

`run.sh` calls `scripts/test.sh <driver build> --no-client --turns 475 --ruleset civ45 --data <series data>` with
`gameseed` = `mapseed` = the seed: ten Normal AIs, civ45 at patch 0063 (the series tree at `eb20321`), turn limit 475.
Every game loads `balance-5/bias.lua`: the tech and combat loggers of report 4, plus one line per civ at the start (its
land mass and that mass's size), a map line (land tiles, land masses, how many of them have civs), and a line per great
wonder built. It changes nothing in the game, except that the win-type games other than domination switch the
domination check off (`FC45_DOM_FROM_TURN` past the game's end).

| Game | Server settings | Wins on |
|---|---|---|
| culture | `victories CULTURE` | culture, conquest, score at T475 |
| space | `victories SPACERACE` | space, conquest, score |
| allied | `victories ALLIED` | alliance, conquest, score |
| domination | `victories ""` | domination (Lua), conquest, score |
| conquest | `victories ""` | conquest, score |
| islands | `generator ISLAND`, `startpos SINGLE` | all six (civ45's defaults) |
| continents | `generator ISLAND`, `startpos 2or3` | all six |
| regular | civ45's defaults | all six |

Read with `balance-5/summary.py` (results, who got the bonuses: `summary.md`), `reach.py` (how close each win came:
`reach.md`) and `start.py` (each civ's start and the land it owned at T50, T100 and T200: `start.md`).

### The maps (checked before the run, and in each game's `FC45MAP` line)

- **The regular civ45 map already is one big continent.** On both seeds all ten civs start on one land mass: 1,124 of
  1,643 land tiles on seed 7, 895 of 1,468 on seed 42 (`summary.md`, regular games). So "one large connected
  continent" is today's default, and `generator FRACTAL` with `startpos ALL` made the same map (3-turn checks).
- **Islands** (`ISLAND` + `SINGLE`): one civ per island, 63 to 85 land tiles each (`start.md`).
- **Separate continents** (`ISLAND` + `2or3`): two civs to a continent of 145 to 149 tiles, five such continents on
  both seeds. `ISLAND` with `startpos ALL` also gave pairs on five continents, not one land mass (3-turn check, seed 7).

## Results

| Game | Seed 7 | Seed 42 |
|---|---|---|
| culture | **culture victory T440**, Alfonso el Sabio | score at T475, Rama Thibodi |
| space | score at T475, Alfonso el Sabio | score at T475, Rama Thibodi |
| allied | score at T475, Alfonso el Sabio | score at T475, Rama Thibodi |
| domination | score at T475, Alfonso el Sabio | score at T475, Rama Thibodi |
| conquest | score at T475, Alfonso el Sabio | score at T475, Rama Thibodi |
| islands | score at T475, Jadwiga | score at T475, Harald Blåtand |
| continents | score at T475, Ferdinand IV | score at T475, François Mitterrand |
| regular | **culture victory T421**, Alfonso el Sabio | score at T475, Rama Thibodi |

## 1. Win types, easiest to hardest

Each win was possible in eight games: its own and the three map games (which use all six), except conquest and the
score, which are always on.

| Rank | Win | Wins | Closest it came (`reach.md`) |
|---|---|---|---|
| 1 | **Culture** (50,000 points and 25 % ahead) | 2 of 8 | Won at T421 (regular, seed 7: 50,228, 26 % ahead) and T440 (culture, seed 7: 50,409, 70 % ahead). Misses: seed 42's regular game had 56,722 but only 12 % ahead; its culture game 40,268, 33 % ahead, short of the points. Islands and continents topped out at 26,315 to 38,002. |
| 2 | **Score at T475** | 14 of 16 | The fallback whenever nothing else fires. |
| 3 | **Domination** (60 % of land and 50 % of people, 3 turns) | 0 of 8 | Best in any game: Rama Thibodi in seed 42's conquest game at T476, 27.8 % of the land and 45.8 % of the people, 46 % of the way. With domination on, best 41 % (seed 42's domination game, T425: 24.4 % land, 37.3 % people). People come close; land never passes 28 %. |
| 4 | **Alliance** (every civ left allied together) | 0 of 8 | The biggest group of civs all allied to each other at the end: 8 of 10 (islands, seed 7); otherwise 4 to 7. |
| 5 | **Space** (a ship that arrives) | 0 of 8 | No ship launched. Space Flight came at T300 (islands, seed 7), T403 to T468 in five games, and never in islands and continents on seed 42. Only seed 7's islands game built real ships, and they have no frame (below). |
| 6 | **Conquest** (every rival dead) | 0 of 16 | At most one civ died in a game (four games). Seed 42's conquest game had the most fighting: 54 cities taken by force, all eleven civs (one born in a civil war) alive at the end. |

### Space: ships with no frame

In seed 7's islands game six civs started ships and none could launch (`spaceship.*` in the T476 save). Three have all
16 components; Mary Tudor and Rama Thibodi also have 9 and 6 modules; Zachary Taylor has the whole set of 16 components
and 12 modules but only **6 structurals**; the other five have **none**. A Space Structural costs 50 shields against 100
for a Space Component and 200 for a Space Module (`civ45/buildings.ruleset:1346,1242,1308`). So the AI builds the dear parts and
not the cheap frame that connects them. Issue 164 found the opposite in earlier games: structurals and a few
components, no modules. Seed 42's space game reached Space Flight at T418 and Apollo at T439, and two civs
built 13 and 5 structurals and nothing else.

In the eight games with the space race off, nobody learned Space Flight; in the eight with it on, someone did in six,
by T475. Space Flight's research want seems to come from the space parts (inferred, not traced in the AI code).

### What it means

- Culture is the only win that happens, and only on one seed's one-continent map. The bar change in patch 0063 (30,000
  to 50,000) holds: both wins came after T420.
- Domination, alliance, space and conquest never fire in 475 turns of AI play. For space, that is an AI problem (the
  missing frame) on top of the pace (Space Flight after T400 on the regular map). For domination, the land bar is the
  wall: 60 % of the land against a best of 28 %.

## 2. Map types

| Map | Seed | Land masses (with civs) | First and last score | Cities changed hands | Civs with a wonder | Top culture | Top techs | Space Flight |
|---|---|---|---|---|---|---|---|---|
| islands | 7 | 16 (10) | Jadwiga 1,274; Mohandas Gandhi 398 | 24 | 7 of 10 | 38,002 | 109 | T300 |
| islands | 42 | 19 (10) | Harald Blåtand 872; Tokugawa Ieyasu 608 | 14 | 8 of 10 | 26,315 | 67 | never |
| continents | 7 | 39 (5) | Ferdinand IV 1,275; Rama Thibodi 104 | 26 | 6 of 10 | 26,378 | 76 | T462 |
| continents | 42 | 36 (5) | François Mitterrand 1,134; Olof Palme 31 (dead) | 24 | 6 of 10 | 34,153 | 74 | never |
| one continent (regular) | 7 | 12 (1) | Alfonso el Sabio 1,335; Oscar II 75 | 16 | 7 of 10 | 50,228 (won) | 70 | T403 |
| one continent (regular) | 42 | 15 (1) | Rama Thibodi 1,536; Deganawidah 374 | 16 | 6 of 10 | 56,722 | 81 | T451 |

Top techs count future techs (109 is 92 advances and 17 future techs). Cities changed hands counts the combat
observer's `FC45CITY` lines (conquest, incite and civil war).

- **Islands are the closest games.** Seed 42's first and last are 872 and 608, and its top two 872 and 869. Wonders reach
  7 and 8 civs. Seed 7's islands game was also the fastest in tech of all 16 (Space Flight at T300), the only one with
  real spaceships, and the alliance came nearest there (8 of 10). No civ can be squeezed out early, since nobody shares
  its land.
- **Separate continents are the most lopsided.** Each pair fights for one continent, and the loser of the pair falls
  far behind: 104 points on seed 7, and on seed 42 Olof Palme is dead, having held 5 land tiles at T50 (`start.md`).
  Ferdinand IV took 251 land tiles by T100, the most of any civ in any of the map games.
- **One continent** (today's default) gives the highest culture (the only culture win among the map games) and wide
  gaps (1,335 against 75).

## 3. Does one leader run away?

### The rules give no leader a head start

- No effect in `civ45/effects.ruleset` names a nation except the Animal Kingdom rule (`effects.ruleset:198`).
- AI personalities: civ45 sets every trait to 30-90 with default 50 (`civ45/nations.ruleset:33-60`), and the server's
  default `traitdistribution` is FIXED (`common/game.h:512`), so every AI plays with the defaults. No nation file
  gives its own traits (`grep` of `data/nation/*.ruleset`; the one hit, `yakut.ruleset:12`, is the word "expansionist"
  in its history text).
- Every civ gets the same start units.

### The map picks the winner

On a given map the same civ wins whatever wins are switched on. Seed 7's regular map: **Alfonso el Sabio is first in
all six** games on it (five win-type games and the regular one), and Oscar II is last in all six. Seed 42's: **Rama
Thibodi is first in all six**, and Deganawidah last in all six (`summary.md`). Put the same nations on another map and
the order changes: on seed 7, Rama Thibodi is sixth to eighth on the regular map, second on the islands and last on
the continents; Jadwiga is third to fifth on the regular map and wins the islands.

What the winners share is **room to expand in the first 50 turns** (`start.md`, land owned):

| Map | Winner, land at T50 | Most land at T50 | Last place, land at T50 |
|---|---|---|---|
| regular, seed 7 | Alfonso el Sabio 112 | Alfonso el Sabio 112 (next 85) | Oscar II 27 |
| regular, seed 42 | Rama Thibodi 97 | Rama Thibodi 97 | Deganawidah 42 |
| continents, seed 7 | Ferdinand IV 99 | Ferdinand IV 99 | Rama Thibodi 55 |
| continents, seed 42 | François Mitterrand 86 | Tokugawa Ieyasu 99 (second at the end) | Olof Palme 5 |
| islands, seed 7 | Jadwiga 80 | Mary Tudor 83 (three civs at 80-83) | Mohandas Gandhi 81 |
| islands, seed 42 | Harald Blåtand 73 | Rudolf II 80 (second, 3 points behind) | Tokugawa Ieyasu 57 |

On the one-continent and continent maps the winner had the most or second-most land at T50 in all four games, and the
two perennial last places start pressed against the sea: Oscar II has 29 water tiles of 49 within three tiles of his
start, Deganawidah 18. On islands, where every civ has about the same land, the early land count does not decide it.

### The bonuses snowball, unevenly

Across the 16 games (`summary.md`, each game's header lines):

| Bonus | The biggest holder's share | Civs that got any |
|---|---|---|
| Great wonders (built, `FC45WONDER`) | 25 to 43 % | 6 to 8 of 10 to 12 |
| Faiths founded (7 a game) | 29 to 57 % (2 to 4 of the 7) | 2 to 6 |
| Great people born | 11 to 18 % | 9 to 12 of 10 to 12 (all, or all but one) |
| Golden ages | 12 to 16 % | 9 to 12 of 10 to 12 |

- **Wonders and faiths pile up**, on the winner or the runner-up. Alfonso el Sabio built 6 to 8 of seed 7's 23 to 26
  wonders in every one-continent game; Mohandas Gandhi founded 4 of the 7 faiths in four of them. On seed 42 Tokugawa
  Ieyasu built 8 or 9 wonders in four games, more than the winner, and was second in two of them.
- **Great people and golden ages spread out.** Every civ, or all but one, gets some, and the leader's share stays under
  a fifth, as the great-person cost curve of patch 0036 intended.
- So one leader does run away, but the cause is the start: more land early, then more cities, wonders and culture. No
  nation or leader is favoured by the rules.

## 4. Findings (new issues)

- The AI builds spaceship components and modules but not the structurals that connect them, so no ship launches
  (seed 7 islands): issue 331.
- Domination, alliance, space and conquest never win in 475 turns of AI play: the bars (above) are John's call: issue 332.
- The regular civ45 map puts every civ on one continent; separate continents need `generator ISLAND`: issue 333.
- The start decides the winner on the shared-land maps: the civ with the most land at T50 wins, and coastal or cramped
  starts finish last. Options to weigh: a fairer start (`startpos`, `dispersion`, or a fair-islands map), or more
  ways back for a cramped civ: issue 334.

## Not checked

- Two seeds per setting: a third would show whether seed 7's culture wins are typical.
- Human play: the AI does not aim for a win type, so "never fires" means the AIs never got there, not that a player
  can't.
- Space Flight's research want (section 1) is inferred from the eight games, not traced in `ai/default`.
