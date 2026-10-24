# Freeciv45 balance report 3 (2026-10-19)

Two autogames of the Freeciv45 ruleset (civ45) with the owner-only Great Library (issue 239, patch 0047), read with
the same summary scripts as report 2. Issue 246. Every number below comes from the game's server log (the FC45 lines)
or its saves; the logs are in `port/night-repo/logs/test-qt-<game>/` (git-ignored, not committed).

Report 2 (section 8) found that the world-wide Great Library gave about half of all techs, and John decided to make
it owner-only. This report measures what that did to the tech pace, against report 2's game 160612 (called G9).

## 1. The games

All ran with `scripts/test.sh <prefix> --ruleset civ45 --no-client --turns 475` (`AUTOGAME_LIMIT` 2400), one at a
time, under `nice`. Seed 42 (both `gameseed` and `mapseed`), ten AIs, all victories on. The AI level comes from the
ruleset alone: every game's T2 save has all AI players at Normal. The data were S3_2 plus main's patches 0001 to
0044 and 0047 (the square game on a copy of the data with `topology ""`). Map size 110 comes from
`--extra "set tilesperplayer 110"`, because patch 0045 was not in that tree. The loggers are report 2's plus a new
one for diplomat tech theft (`FC45STEAL`).

| Game | Map | `tilesperplayer` | Great Library | How it ended |
|---|---|---|---|---|
| G9, 160612 (report 2) | square, 72 x 48 | 100 | world-wide (30 % of players) | score at T475 (the Mayas) |
| **205029** | square, 72 x 48 | 110 | owner only | score at T475 (the Mayas) |
| **111756** | ISO, 54 x 72 | 110 | owner only | **culture victory at T416** (Rama Thibodi) |

## 2. What 110 does to the map

The map generator rounds the size, so a change of 10 % does not always change the map.

| `tilesperplayer` | Topology | Tiles requested | Map made |
|---|---|---|---|
| 100 | square | 3,333 | 72 x 48 = 3,456 |
| **110** | square | 3,666 | **72 x 48 = 3,456 (the same)** |
| 100 | ISO | 3,333 | 48 x 64 = 3,072 |
| **110** | ISO | 3,666 | **54 x 72 = 3,888** |

- On the square map at seed 42, 110 makes **no difference**: 205029 and G9 are on the same map, and their saves are
  identical at T100 (the same 76 cities, 298 citizens and techs per civ). That makes 205029 a clean comparison for the
  library change alone.
- On the ISO map, which is civ45's default since #189, 110 grows the map by 27 % (3,072 to 3,888 tiles).

## 3. The Great Library gift

The tech logger reports a tech from the library, a diplomat's theft and a few other sources all as "stolen". The
theft logger separates the diplomat actions that succeeded.

| Game | Techs learned | "Stolen" | Diplomat thefts that succeeded | Left (the library, and other sources) |
|---|---|---|---|---|
| G9 | 721 | 429 (59 %) | not logged | most of 429 |
| 205029 | 439 | 55 (13 %) | 19 | up to 36 (8 %) |
| 111756 | 508 | 46 (9 %) | 10 | up to 36 (7 %) |

- The gift fell from about **430 techs to about 36** a game, and it no longer reaches the whole field.
- **To whom.** In 205029 the Thai (Rama Thibodi) built the Great Library by T130. Harald Blåtand took Chiang Mai
  between T150 and T175 and held it to about T440, and Henry II (a late civ) held it at the end. Harald got 18 of the
  34 "stolen" techs that came on turns with no successful theft, and 14 of his 20 stolen techs fall between T150 and
  T249. In 111756 Kan Ek' (the
  Mayas) built it by T125 and **keeps it all game**: he got 26 of the 34 techs on turns with no theft. The other
  receivers have one to three each, which are the unlogged sources.
- The owner ends high in both games: Harald Blåtand has the most techs at the end of 205029 (55), and Kan Ek' is
  third in 111756 (56, behind Rama Thibodi's 62 and Ivan Grozny's 58).

## 4. Tech pace against G9 and #217's curve

Techs per civ are `techs=` from the saves minus one (the save counts "None"), highest first.

| Turn | G9 | 205029 (square) | 111756 (ISO) |
|---|---|---|---|
| T100 | 17 17 16 15 15 12 12 11 9 7 | the same | 20 17 16 14 14 13 13 13 11 11 |
| T200 | 38 38 37 37 37 37 37 37 37 37 | **37 36 36 34 32 31 30 23 17 15** | 42 41 38 37 36 36 34 33 33 31 |
| T300 | 48 48 47 47 47 47 47 47 47 47 | **48 48 47 43 42 39 33 26 20 18** | 49 49 47 46 46 45 41 41 40 33 |
| T400 | 57 57 56 55 55 55 55 55 55 55 | **53 51 51 50 46 45 34 30 30 19** | 58 56 55 52 51 50 46 44 43 37 |

| Game | Leader's techs T300 / T400 | Era IV / V / VI / VII first | Techs per civ at the end |
|---|---|---|---|
| G9 | 48 / 57 | T142 / T241 / T345 / none | 57 to 65 |
| 205029 (square) | 48 / 53 | T142 / T202 / none / none | 23 to 55 |
| 111756 (ISO) | 49 / 58 | T110 / T140 / T384 / none | 37 to 62 |

- **The leader's pace is nearly unchanged.** At T300 it is 48 in both square games; by T400 the square leader is four
  techs behind G9 (53 against 57) and the ISO leader is one ahead (58, on a bigger map).
- **The pack is gone.** In G9 eight civs held 37 techs at T200 and eight held 47 at T300. With the owner-only
  library the same map spreads from 37 to 15 at T200 and 48 to 18 at T300: the laggards fall far behind (23 at the
  end against 57). The ISO map keeps a tighter field (31 to 42 at T200); a bigger map may give every civ more room,
  but no game here tests that.
- **#217's curve (eras V to VII at 200 %).** Report 2 measured it with a leader at era VII on seed 3 at T360. On seed
  42 nobody reaches era VII in any of the three games, and the best reaches era VI at T345 (G9), T384 (ISO) or not at
  all (square, owner-only). So the curve does not reach turn 400 on seed 42 with or without the library; what the
  library change took away is the laggards' catch-up, not the leader's pace. The target of tech-tree.md section 5 (best
  AI in era VII by about turn 400) was not tested on seed 3 with the owner-only library; that needs another game.

## 5. Other observations

| | G9 | 205029 (square) | 111756 (ISO) |
|---|---|---|---|
| Great people born | 53 | 57 | 69 |
| Most for one civ | 9 | 9 | 11 |
| Golden ages | 18 | 23 | 25 |
| Attacks | 1,730 | 1,154 | 1,291 |
| Cities changing hands | 47 | 58 | 19 |
| Pairs at war, end (of 45) | 38 | 30 | 21 |
| Citizens at the end | 581 | 529 | 716 |
| Draft units / smallest city after one | 7 / 5 | 26 / 4 | 17 / 3 |

- **Culture victory at T416** in the ISO game (Rama Thibodi, 31,000 points and a 37 % lead). It is the first time the
  30000 / 25 % rule has ended a game on the default map; its lead stayed between 33 % and 120 % from T200 on.
- **The ISO game has less war** (21 pairs at war against 30 to 38) and more people (716 against 581).
- Most great people for one civ is 9 to 11 in all three games, inside the design's 12.
- The 900 s limit of `scripts/test.sh` stops a 475-turn game on a loaded machine (a no-library test run was cut off at
  T437); `AUTOGAME_LIMIT=2400` avoided it here.
- An earlier no-library test on the ISO map at 100 ended in an allied victory at T173. That did not recur on the
  larger ISO map at 110; the earlier run also had a different map (48 x 64) and no library change, so the cause is
  not known.

## 6. What is left

1. **Era VII by turn 400** is not met on seed 42 in any of the three games, and the owner-only library has no seed 3
   game yet. Report 2's seed-3 result (era VII at T360, library world-wide) is the only point on the curve.
2. **The laggard gap.** Four of ten civs end under 35 techs in the square game. This may be right (the Great Library
   rewards the owner and a tech leader's lead is a feature of Civ games), or it may need a floor such as `techleak`
   (100, the server default, with `tech_leakage "Embassies"`), which is still not measured.
3. **Space at Normal** (#215), **AEGIS Cruisers** (#214) and **siege** (#202) are as in report 2.

## 7. Decisions for John

- None new. Report 2's decisions stand. John may want a seed 3 game and a `techleak` game before judging the
  catch-up.
