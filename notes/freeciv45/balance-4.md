# Freeciv45 balance report 4 (2026-10-24): pacing with religion, resources, cottages and civics

Issue 284. Religion, resources and cottages (patches 0051 to 0053) sped up the economy, and seed 13 won by culture
about 100 turns sooner than before (`design/cottages.md` section 6). This report reruns the pacing on everything
merged through patch 0062 (civics sliders, `design/civics.md`), on three seeds. It ends with one change, patch 0063:
the culture victory needs 50,000 points instead of 30,000.

## 1. The games

All ran with `scripts/test.sh <driver build> --no-client --turns 475 --ruleset civ45 --data <series data>`, with
`AUTOGAME_LIMIT=6000` under `nice`, one at a time. Ten Normal AIs, all victories on, `gameseed` = `mapseed` = the
seed, and the tech and combat loggers concatenated into one `--lua` file. The binary is the driver build of
series-0061. 0062 and 0063 change only data, so `--data` carries them. The logs are in `logs/test-qt-<id>/` (git-ignored).

| Seed | Rules | Log | How it ended |
|---|---|---|---|
| 7 | through 0062 | 20261024-130219 | **culture victory at T306** (Alfonso el Sabio) |
| 13 | through 0062 | 20261024-131436 | culture victory at T399 (Aleksandr Nevsky) |
| 42 | through 0062 | 20261024-133047 | score at T475 (the Swedes) |
| 7 | **+ 0063** | 20261024-135235 | culture victory at **T402** (Alfonso el Sabio) |
| 13 | **+ 0063** | 20261024-141019 | score at T475 (the Zulus) |

Seed 42 needs no rerun with 0063. After T300 its culture leader is never more than 23 % ahead, short of the 25 %
the victory needs, so the higher bar can't change how it ends. The seed-7 rerun matches the first seed-7 game
exactly up to T200 (the same culture to the point), so the two are a clean comparison.

## 2. Eras

`scripts/civ45-tech-summary.py` on each log: the turn the first civ reached each era, and the median civ.

| Game | Era IV first / median | Era V | Era VI | Era VII | Techs per civ at the end |
|---|---|---|---|---|---|
| 7, through 0062 | T109 / T130 | T145 / T146 | T205 / T242 | none by T306 | 57 to 65 (9 civs) |
| 7, + 0063 | T109 / T130 | T145 / T146 | T205 / T247 | **T384** | 63 to 70 (9 civs) |
| 13, through 0062 | T130 / T167 | T231 / T237 | T358 | none by T399 | 37 to 59 (10 civs) |
| 13, + 0063 | T130 / T167 | T233 / T265 | none | none | 47 to 56 (9 civs) |
| 42, through 0062 | T112 / T155 | T139 / T191 | T272 / T282 | **T390** | 55 to 76 (10 civs) |

The ranges at the end leave out the one or two civs that were nearly wiped out (under 25 techs).

- The late eras arrive around turn 400 on seeds 7 and 42: the first civ reaches era VII at T384 and T390. Report 3
  had nobody in era VII on seed 42, and era VI only at T384, so the systems since then put that seed on target.
- Seed 13 is a slow map. No civ reaches era VI by T475 in the rerun, and the first game's single era-VI civ (T358)
  depended on how that game ran after T200. The two seed-13 games split after T200, the way the two seed-7 games
  split after T250. This report does not change era costs for one slow seed.

## 3. Culture

`culture=` from each save's score sections. Lead is the leader over the runner-up.

| Game | T200 | T300 | T400 | Best lead after T300 |
|---|---|---|---|---|
| 7, through 0062 | 9,479 (20 %) | 28,946 (39 %) | ended T306 at 30,337 | 40 % |
| 7, + 0063 | 9,479 (20 %) | 27,437 (44 %) | 49,714 (47 %); won T402 at 50,380 | 50 % |
| 13, through 0062 | 6,206 (3 %) | 16,642 (26 %) | won T399 at 30,282 (45 %) | 45 % |
| 13, + 0063 | 6,270 (8 %) | 19,285 (28 %) | 29,466 (25 %); 37,835 (17 %) at T475 | 29 % |
| 42, through 0062 | 9,804 (32 %) | 27,373 (23 %) | 47,296 (11 %); 61,694 (13 %) at T475 | 23 % |

- At 30,000 points the bar falls between T300 and T400 on every seed. A leader with a steady lead won as early
  as T306.
- At 50,000 the leaders reach it near T400 (seed 7 at T402; seed 42 between T410 and T415, but with a 12 % lead) or not at
  all (seed 13). A dominant culture still wins, but only around the time the late eras arrive, which is the target
  in #284.
- Seed 7's world culture at T300 is 120,225 here, against 65,594 in the 0053 game (cottages.md section 6); seed
  13's is about the same (71,309 against 78,998). Since 0053 the only rule changes are 0061 (Settlers found only)
  and 0062 (civics), and these games can't tell which, if either, made the difference on seed 7.

## 4. World totals

Sums over each save's `[scoreN]` sections (techs minus "None" per civ; trade is `bnp`).

| Game, turn | Techs | Trade | Unhappy | Cities | Culture |
|---|---|---|---|---|---|
| 7, T150 | 323 | 1,237 | 9 | 113 | 12,011 |
| 7, T300 (+ 0063) | 563 | 1,542 | 1 | 117 | 116,015 |
| 7, T400 (+ 0063) | 621 | 1,738 | 6 | 121 | 205,206 |
| 13, T150 | 288 | 918 | 5 | 114 | 10,476 |
| 13, T300 (+ 0063) | 468 | 1,262 | 29 | 116 | 69,115 |
| 13, T475 (+ 0063) | 550 | 1,264 | 58 | 116 | 160,480 |
| 42, T150 | 278 | 924 | 3 | 92 | 12,564 |
| 42, T300 | 555 | 1,501 | 4 | 99 | 121,076 |
| 42, T475 | 773 | 1,692 | 14 | 101 | 287,454 |

Trade at T300 is 1,262 to 1,542, in the range of the 0053 games (1,375 and 1,661). Cottage trade was left alone:
with the culture bar raised and two of three seeds on time for the late eras, there is nothing to correct it
for.

## 5. Civics in long games

The AI's four slider values at T300 (Labour, Trade, Faith, Service), one group per civ:

- seed 42: 4000 4000 3000 0000 4000 1000 4000 0030 1000 3000 (and the barbarians);
- seed 7 + 0063: 2000 0000 3000 4000 0000 4000 0010 2000 1001 4001.

Labour is the AI's slider: most civs hold it at 2 to 4. Faith shows up in two civs, Service in two, and Trade in
none. That matches the 150-turn game in `design/civics-test/README.md`. Whether Trade and Faith are worth more to
a human than the AI thinks is for play-testing, not autogames.

## 6. What changed and what is left

- **Patch 0063:** `victory_min_points` 30000 → 50000 in `civ45/game.ruleset`, with its comment, the victory
  helptext and README.civ45. The 25 % lead is unchanged.
- **Not changed:** era costs and cottage trade (sections 2 and 4).
- **Left:** seed 13's slow tech (no era VI by T475) is one seed of three; another slow seed would make the case
  for cheaper late eras. The AI hardly uses Trade or Faith (section 5).
