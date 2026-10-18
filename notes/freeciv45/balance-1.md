# Freeciv45 balance report 1 (2026-10-17)

Six long headless autogames of the Freeciv45 ruleset (civ45), AIs only, read with the summary scripts. Issue 168.
Every number below comes from the game's server log (the FC45 lines) or its saves; the logs and every 25th save
are kept in `logs/balance-1/<game>/` (git-ignored, not committed).

## 1. The games

All ran with `scripts/test.sh <prefix> --ruleset civ45 --no-client --turns 475` on the fork's civ45 with
patches 0021 (issue 121, great-person pledges) and 0024 (issue 107, draft unrest), plus the issue 83 Siege Rest
attempt, which changed nothing here (one bombardment in all six games). The Lua loggers were
`scripts/civ45-combat-log.lua`, `civ45-draft-log.lua` and `civ45-tech-log.lua`; the great-person lines are
written by civ45's own `script.lua`. AI skill level is the server default.

| Game | Settings beyond the defaults | Turns played | How it ended |
|---|---|---|---|
| b1 | seed 42; victories SPACERACE and CULTURE (allied off) | 475 | score winner at the turn limit (the Thai) |
| b2 | seed 11; allied off | 275 | culture victory at turn 275 (Christian IV) |
| b3 | seed 23; `diplomacy DISABLED`, so every civ that meets is at war | 475 | score winner at the turn limit (the Sumerians) |
| b4 | seed 5; allied off; `tilesperplayer 200` (big map) | 326 | stopped at turn 326 (the machine was overloaded) |
| b5 | seed 8; allied off; `tilesperplayer 60`, 6 AIs (small map) | 475 | score winner at the turn limit (the Austrians) |
| b6 | seed 3, all defaults (allied on) | 424 | stopped at turn 424 (as b4) |

Seeds are both `gameseed` and `mapseed`. Ten AIs unless the table says otherwise; barbarians and animals are
left out of every count.

## 2. Victories

No space race in any game, one culture victory, and the rest end on score at the turn limit.

- **Space race never fires** (issue 164). Four AIs in b1, two in b5 and one in b6 started a ship, but the best
  ship anywhere had 23 structurals, 2 components and no modules (`spaceship.*` in the last saves), so nobody
  launched.
- **Culture** (issue 165). The top civ passes `victory_min_points` 8000 at turn 225 in four games, at 250 on the
  big map, and at 400 in the war game. victory.md section 3 wants that near turn 350 to 400. After that only the
  50% lead decides, and only b2 reached it (15,339 against 10,185 at turn 275). Elsewhere the largest lead in any
  25th-turn save was 19 to 46%, while the top totals reached 40,000 to 45,000 by the end.
- **Allied** stayed off in five games (decision 13, issue 159). In b6, where it was on, the AIs had not all allied
  by turn 424.
- **Domination** (the Lua rule) never fired. The most cities changing hands in one game was 95 (b4).

## 3. Tech pace against tech-tree.md

From `scripts/civ45-tech-summary.py`: the turn the first civ and the median civ learned their first tech of each
era. tech-tree.md section 5 wants the best AI in era IV by turn 200 and in era VII by turn 400.

| Game | Era IV first / median | Era V first | Era VI first | Era VII first / median |
|---|---|---|---|---|
| b1 | 107 / 131 | 125 | 191 | 276 / 292 |
| b2 | 107 / 130 | 147 | 203 | 243 / - |
| b3 (war) | 133 / 170 | 203 | 339 | none |
| b4 (big) | 108 / 157 | 159 | 249 | 305 / - |
| b5 (small) | 97 / 139 | 138 | 210 | 247 / 264 |
| b6 | 110 / 131 | 123 | 196 | 275 / 282 |

Era IV comes well inside its limit. In peaceful games era VII comes 95 to 157 turns early, and the field moves
as a pack (median 16 turns behind the leader in b1). The war game is the exception: it never reaches era VII
(issue 167). One runaway: b1's Rudolf II ended with 241 techs, 146 of them Future techs, against 94 to 121 for
the others.

## 4. Great people and golden ages

From `scripts/civ45-gp-summary.py`. great-people.md section 3 expects 3 to 6 per player per game without wonders
and 8 to 12 with them.

| Game | Born | Per AI civ | Most for one civ | Golden ages | Ages per AI civ |
|---|---|---|---|---|---|
| b1 | 206 | 20.6 | 32 | 41 | 4.1 |
| b2 (275 turns) | 88 | 8.8 | 12 | 26 | 2.6 |
| b3 (war) | 73 | 7.3 | 14 | 23 | 2.3 |
| b4 (326 turns) | 114 | 11.4 | 17 | 30 | 3.0 |
| b5 (6 AIs) | 130 | 21.7 | 26 | 23 | 3.8 |
| b6 (424 turns) | 153 | 15.3 | 27 | 36 | 3.6 |

- Too many in long peaceful games, about twice the upper bound (issue 166).
- Births are almost all from city points. Only 4 a game are first-to-a-tech, and Commanders come 0 to 3 a game
  since combat births are not built yet.
- Kinds: Sages and Magnates lead (b1: 58 and 57 of 206), then Oracles (37) and Spymasters (30). Virtuosos number
  6 to 20, Builders 2 to 5.
- The AI uses them at once (median 1 turn from birth to use). About two in three are pledged for a golden
  age, most of the rest go on deeds, and a few settle (b1: 129 pledges, 64 deeds, 6 settled).
- Since patch 0021 every AI reaches later golden ages: 2 to 4 per civ. The first great person is born between turn 97 and
  120.

## 5. Drafts and whips

From `scripts/civ45-draft-summary.py` and the FC45UNREST and FC45DRAFTS lines (patch 0024).

| Game | Draft units (Levy is the whip) | First | Unrest records | Draft limit reached | Units disbanded into a build |
|---|---|---|---|---|---|
| b1 | 8 (Levy 5, Conscripts 3) | 152 | 8 | never | 18 |
| b2 | 8 (Militia 7, Conscripts 1) | 129 | 8 | never | 18 |
| b3 (war) | 53 (Conscripts 39, Levy 8, Militia 6) | 96 | 53 | never | 52 |
| b4 | 36 (Levy 16, Militia 11, Conscripts 9) | 120 | 36 | never | 36 |
| b5 | 0 | - | 0 | never | 13 |
| b6 | 20 (Conscripts 15, Militia 4, Levy 1) | 136 | 20 | never | 57 |

The AI drafts little, and only at war. No city held more than 7 unrest at once. The per-turn draft limit never
bit in these games. Nothing degenerate here.

## 6. Wars, armies and captures

From `scripts/civ45-combat-summary.py` and `scripts/civ45-game-summary.py` (new in this change: per save the
civs, cities, citizens, military units, field stacks and pairs of civs by diplomatic state; run with
`--every 50`).

| Game | Attacks | Leading attackers | Cities changing hands | Pairs at war (of 45, or 15 in b5) |
|---|---|---|---|---|
| b1 | 467 | AEGIS Cruiser 150, Galleon 108 | 25 | 0 until T350; 45 of 45 allied T200-T350; 32 at war from T400 (an 11th civ) |
| b2 | 167 | Galleon 103 | 6 | 9 to 10 |
| b3 (war) | 831 | Galleon 281, Phalanx 138, Riflemen 108 | 44 | 19 to 43 |
| b4 (big) | 540 | Musketeers 115, Frigate 108, Galleon 96 | 95 | 9 to 11 |
| b5 (small) | 19 | AEGIS Cruiser 19 | 2 | 0 in 475 turns, 12 to 14 of 15 allied |
| b6 | 281 | Galleon 73, AEGIS Cruiser 40 | 33 | 8 to 18 |

- **Wars are fought from the sea.** Galleons are the first or second attacker in five games; AEGIS Cruisers lead in
  b1 and b5.
- **Land armies stay small** (issue 49). The largest military stack outside a city in the 50-turn saves is 2 to 4
  in four games, and 8 and 15 in b3 and b6. Stacks of 3 or more next to a foreign city never number more than 2.
- **Siege units are missing** (issue 83). There was one bombardment in all six games, and the AI builds almost no
  siege units.
- **The allied bloc** (issue 159). In b1 and b5 the AIs ally into one bloc and do not fight for hundreds of turns,
  with allied victory off.
- **Barbarians** ("Storm" units) die 4 to 46 times a game. They are not a factor.

## 7. Other observations

- **Population falls late in peaceful games.** b5 went from 424 citizens at turn 250 to 318 at 350, b1 from 760 at
  T300 to 689 at T450, and b6 from 820 at T300 to 714 at T400. War does not explain it (b5 had 19 attacks), and
  starving units are few. Not investigated yet: plague, pollution or happiness limits. A candidate for
  balance report 2.
- **Diplomats and Spies are numerous.** 45 to 60 units in mid-game saves, an AI habit.
- **Run time** was 275 to 910 s for 475 turns with up to six games at once, which overloaded the machine. Later
  runs keep to two at a time, under `nice`.

## 8. The three biggest problems

1. **Victories don't line up with the design.** Space race never fires (164). Culture fires by chance, about
   turn 275 at the earliest (165). Most games end on score at turn 475.
2. **The AI does not make war well.** Peaceful games become one allied bloc (159). The wars that happen are naval:
   Galleons, Frigates and Cruisers against coastal cities. Land armies stay at 1 to 4 units, with no siege (49, 83).
3. **The economy runs fast.** Peaceful games get two to four times the expected great people (166), and era VII
   comes 100 to 150 turns before the design's turn 400 (167). The game is too short for its own tech tree and too
   generous with great people.

No ruleset number was changed in this pass. The design notes give the direction for each problem but not the new
value, so each is an issue for a decision.
