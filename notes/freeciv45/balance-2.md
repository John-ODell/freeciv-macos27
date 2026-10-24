# Freeciv45 balance report 2 (2026-10-18)

Long headless autogames of the Freeciv45 ruleset (civ45) after the fixes for balance report 1's findings, AIs only,
read with the same summary scripts. Issue 222. Every number below comes from the game's server log (the FC45
lines) or its saves; the logs are in `port/night-repo/logs/test-qt-20261018-<game>/` (git-ignored, not committed).

The fixes, one PR each, merged in patch number order (main took 0034 for the tilespec patch of #230 and 0042 for
drag-to-pan, #235, so the culture patch moved to the end as 0043, #237):

| PR | Issue | Patch | Change |
|---|---|---|---|
| #213 | #164 | 0035 | space parts need a Factory and cost 50/100/200; the AI launches an unfinished ship before `endturn` |
| #216 | #166 | 0036 | great-person threshold step 200 (was 75) |
| #217 | #167 | 0037 | era cost_pct 100, 150, 175, 200, 200, 200, 200 (was up to 275) |
| #218 | #187 | 0038 | warships lose their defend roles |
| #219 | #159, #49 | 0039 | AIs play at Normal, not the server's Easy |
| #220 | #157 | 0040 | the `City_Unrest` effect: draft and whip unrest reaches base content citizens |
| #221 | #158 | 0041 | a Levy needs a city of size 3, Militia and Conscripts size 4 |
| #212, #237 | #165 | 0043 | culture victory needs 30000 points and a 25 % lead (was 8000 and 50 %) |

`patches/0001` to `0043` on main apply in number order on upstream S3_2 (44e6898) with `git am` (checked
2026-10-18). The fork commits are not on `macos27-port` yet.

## 1. The games

All ran with `scripts/test.sh <prefix> --ruleset civ45 --no-client --turns 475` and the same Lua loggers as
report 1, two games at a time at most, under `nice`. Ten AIs, seeds are both `gameseed` and `mapseed`, and
barbarians and animals are left out of every count. All games in this table ran on the square overhead map
(`topology ""`): the data they loaded predates patch 0032's ISO setting. Section 8 has the later games, the first on
ISO. The map was `tilesperplayer` 100; from issue 211 civ45 uses 110, so the next games run at 110.

| Game | Level | Rules beyond `macos27-port` | Victories | How it ended |
|---|---|---|---|---|
| 130950 | Normal | none (the baseline) | all | score at T475 (the Danes) |
| 132811 | Normal | culture 30000/25 %, warships, draft sizes, first `City_Unrest`; GP step 300; space parts at a third of the cost | all | **culture victory T417** (Harun al-Rashid) |
| 134116 | Normal | as 132811; eras VI and VII at 225 % | space, allied | score at T475 |
| 135649 | Normal | as 132811 with GP step 150 | space, allied | score at T475 |
| 141701 | Normal | as 135649; space parts with Factory, launch deadline; eras VI and VII at 225 % | space, allied | score at T475 |
| 143926 | Normal | every balance-2 rule (step 200, eras V to VII at 200 %); level by command | space, allied | score at T475 |
| 152537 | Easy | every balance-2 rule; seed 42 | space only | **space victory T394** (Rudolf II) |
| 160612 | Normal from the ruleset | every balance-2 rule, no level command; seed 42 | all | score at T475 (the Mayas) |

Seed 3 unless the table says seed 42. Before #219 the level came from `--extra normal` (or `easy`). 160612 is the
only game that got its level from the ruleset alone: its T2 save has all 11 AI players at Normal. 160612 ran the
first version of `City_Unrest`, which missed cities smaller than the base content number (fixed in #220).

## 2. Victories

| Victory | Report 1 | Now |
|---|---|---|
| Space race | never; best ship 23 structurals, 2 components, no modules | fires at Easy (T394); never at Normal |
| Culture | 8000 passed at T225 to T275; fired once in six games | fires near T417 when one civ leads by 25 %; 30000 not reached on seed 42 |
| Allied | one bloc in two games | no bloc at Normal (from T250 on, 13 to 30 pairs allied and 22 to 38 at war) |
| Score | most games | most games |

- **Space** (#213). At Easy on seed 42 the Apollo Program came at T290, four civs built 60, 46, 26 and 16 parts,
  and Rudolf II launched a complete ship in 1948 and arrived at T394. The **deadline test** loaded that game's T370
  save with `endturn 385` (160525): Rudolf II launched a 32/16/6 ship (100 % success) at T370 and won at T379.
  A complete ship would have arrived too late.
- **Space at Normal** (#215). No Normal game built a part. Space Flight came at T414 on seed 3 (one civ) and never on
  seed 42. The **space tests** loaded 143926's T380 save and gave three civs every tech:
  - 150431: Apollo at T438, no part by T475.
  - 151200, with the AI's space-part and Apollo wants doubled for every civ (test build only): Apollo at T454, no
    part.
  - 151847, with the AI's defender pick skipping BadCityDefender units (test build only): 45 to 50 of 102 cities
    still building AEGIS Cruisers.
  Neither test change is in a PR.
- **Culture** (#212). Top culture at T475 is 28k to 41k on seed 3, and the lead decides: 132811's leader was 60 to
  78 % ahead from T350 and won at T417, while 135649's lead stayed at 0 to 2 % after T300. On seed 42 the top
  civ had 13.6k at the end.

## 3. Tech pace against tech-tree.md

From `scripts/civ45-tech-summary.py`: the turn the first civ learned its first tech of each era, and the leader's
techs from the saves (`techs=` minus one, for "None"). tech-tree.md section 5 wants the best AI in era IV by turn
200 and in era VII by turn 400.

| Game | GP step | Eras V / VI / VII cost | Leader's techs T300 / T400 | Era IV / V / VI / VII first |
|---|---|---|---|---|
| 130950 | 75 | 225 / 250 / 275 | 63 / 86 | 111 / 129 / 222 / **347** |
| 132811 | 300 | 225 / 250 / 275 | - | 123 / 191 / 270 / none by T417 |
| 134116 | 300 | 225 / 225 / 225 | - / 64 | 123 / 191 / 305 / 450 |
| 135649 | 150 | 225 / 250 / 275 | 56 / 69 | 123 / 182 / 339 / 415 |
| 141701 | 150 | 225 / 225 / 225 | 59 / 68 | 123 / 182 / 233 / 467 |
| **143926** | **200** | **200 / 200 / 200** | 60 / 74 | 123 / 198 / 301 / **360** |
| 152537 (Easy, seed 42) | 200 | 200 / 200 / 200 | - | 112 / 138 / 223 / 241 |
| **160612** (seed 42) | **200** | **200 / 200 / 200** | 48 / 57 | 142 / 241 / 345 / none |

- At Normal the AIs fight, and with fewer great people the tree slows a great deal: era VII moved from T347
  (130950) to T415 with step 150 (135649) and T450 with step 300 (134116). #217's flatter late curve brought it
  back to T360 on seed 3 with step 200.
- On seed 42 the AIs fight hardest (1,730 attacks) and reach only era VI by turn 475. The pace depends on war more
  than on any cost number.
- At Easy era VII still comes at T241. Report 1's pace was the Easy level, not the curve.
- No runaway: with the fixes the leader ended with 65 to 91 techs (130950's leader had 164).

## 4. Great people and golden ages

From `scripts/civ45-gp-summary.py`. great-people.md wants 3 to 12 per civ in a full game.

| Game | GP step | Born | Most for one civ | Golden ages |
|---|---|---|---|---|
| 130950 | 75 | 175 | 26 | 37 |
| 132811 (417 turns) | 300 | 47 | 9 | 20 |
| 134116 | 300 | 64 | 10 | 20 |
| 135649 | 150 | 96 | 19 | 27 |
| 141701 | 150 | 98 | 18 | 27 |
| **143926** | **200** | **75** | 15 | 26 |
| 152537 (Easy, 394 turns) | 200 | 101 | 15 | 30 |
| **160612** (seed 42) | **200** | **53** | 9 | 18 |

- Step 200 keeps most civs inside 3 to 12 (2 to 9 on seed 42); the largest empires on seed 3 reach 14 and 15.
- Step 300 fits the count best but slows the tree the most (era VII at T450), because Great Sages and golden
  ages feed research.
- In 160612 the AI used every great person within 2 turns of its birth. Magnates and Oracles lead the births (160612: 21 and 15 of
  53), then Spymasters.

## 5. Drafts and whips

From `scripts/civ45-draft-summary.py`. The size after a draft is the city's size in the next save.

| Game | Draft units | City size after the draft | Unrest records |
|---|---|---|---|
| 130950 (no size rule) | 9 (Conscripts 6, Militia 3) | **size 2: 4**, 3: 2, 4: 1, 5: 2 | 9 |
| 132811 | 4 (Conscripts 3, Levy 1) | 3: 1, 4: 1, 6: 2 | 4 |
| 135649 | 14 (Conscripts 14) | 4: 6, 5: 3, 6: 2, 7: 2, 12: 1 | 14 |
| 143926 | 24 (Conscripts 24) | 4 to 15, smallest 4 | 24 |
| 160612 (seed 42) | 7 (Conscripts 7) | 5: 2, 6: 1, 9: 2, 10: 2 | 7 |

- With #221 no draft left a city below size 3, and the AI kept drafting. It almost never uses the Levy as a whip.
- Every draft wrote its unrest record. The rules test shows that `City_Unrest` puts a size-1 city with no
  buildings into disorder, which `Make_Content` could not (#220). No full game ran after #220's city.c fix.
- The draft limit bit 0 to 3 times a game.

## 6. Wars, armies and captures

From `scripts/civ45-combat-summary.py` and `scripts/civ45-game-summary.py --every 50`.

| Game | Attacks | Cities changing hands | Pairs allied / at war, T100 | at the end | Largest field stack | Most stacks of 6+ in one save |
|---|---|---|---|---|---|---|
| 130950 | 748 | 38 | 25 / 7 | 30 / 24 | 19 | 3 |
| 132811 | 1,036 | 52 | 20 / 20 | 22 / 31 | 18 | 6 |
| 135649 | 1,202 | 47 | 20 / 20 | 22 / 23 | 22 | 6 |
| 141701 | 1,089 | 48 | 20 / 20 | 22 / 23 | 18 | 9 |
| 143926 | 1,059 | 53 | 20 / 20 | 29 / 25 | 44 | 9 |
| 152537 (Easy) | 71 | 22 | 38 / 0 | 44 / 0 at T250 | 4 | 0 |
| 160612 (Normal from the ruleset) | **1,730** | 47 | 16 / 29 | 16 / 38 | 19 | 4 |

Pairs are of 45 (55 once an eleventh civ appears).

- **No bloc at Normal** (#219). Easy is what built report 1's bloc: 152537 had 44 of 45 pairs allied and 71
  attacks in 394 turns. Which Easy handicap does it (cease-fire at first contact, naive diplomacy, defensive play) is
  not isolated.
- **Stacks exist** (#49, closed by #219). At Normal the AIs keep up to 9 stacks of six or more in the field, and the
  largest stack is 13 to 44.
- **Galleons still lead the attacks** in every Normal game; Musketeers and Riflemen follow.
- **Siege is still missing** (#202). The AI builds no siege units, so #83's bombard fix has nothing to work on;
  the fork's commit 047ae90 for it was not reused.
- **Warships no longer garrison** (#218). Cities building AEGIS Cruisers fell from 76 of 107 at the end of 130950
  to 0 in 143926 and 160612, and to 8 and 23 in two other games. Late in the game, with every tech known, about
  half of all cities build one as the roster's best unit for its cost (#214).

## 7. Other observations

- **Population keeps growing at Normal.** Report 1's late fall does not show: 130950 grew from 715 citizens at T300
  to 901 at the end, 160612 from 488 to 581. The fall was a feature of the peaceful Easy games.
- **The rules test's great-person autosave check is flaky.** One run failed "no great-person counter in the
  autosave" and the rerun passed with nothing changed.
- **README.civ45 is out of date** in two places: it says the tech tree has 92 advances (techs.ruleset has 95) and
  that the victory thresholds are "first values, untuned".
- **The isometric map** (patch 0032, civ45's default since #189) was not used by the games in section 1. The one
  ISO game (section 8) ended in an allied victory at T173, but it also lacked the Great Library gift, so the two are
  not separated.

## 8. The Great Library gift (found after the first draft)

civ45's Great Library (inherited from sandbox) is `Tech_Parasite_Pct_Max` 30 at **World** range with `survives`
(`effects.ruleset`, `[effect_great_library]`). Once anyone has built it, **every** player, barbarians included, gets
one free tech a turn that 30 % of all players ever in the game know (`server/techtools.c`,
`do_tech_parasite_effects`). The tech logger reports these techs as "stolen", the same word as a diplomat's theft.
The lead came from `notes/freeciv45/fcw/rules.md` (ideas only, nothing copied).

| Game (seed 42, Normal) | Map | Techs "stolen" | Diplomat thefts | Leader's techs T300 / T400 | Era V / VI first | Techs per civ at the end |
|---|---|---|---|---|---|---|
| 160612, all balance-2 rules | square | **429 of 721** | not logged | 48 / 57 | T241 / T345 | 57 to 65 |
| 164815, the same without the gift (test.sh's 900 s limit stopped it at T437) | square | 34 of 420 | 18 actions logged | 41 / 47 | T296 / none | 20 to 49 |
| 164540, the same without the gift | ISO | 1 of 414 | - | - | - | allied victory at T173 |

- About **half of all techs** in 160612 came from the gift, and they went to all 13 players (1 to 60 each), most to
  the laggards. It is the main reason the field researches as a pack.
- Without it the leader is about 10 techs behind by T400 and never reaches era VI on seed 42, and the field spreads
  out.
- `techleak` (100, the server default, with `tech_leakage "Embassies"`) is the other catch-up rule. It is not
  measured yet.

**Recommended fix:** make the gift the owner's, as in Freeciv's classic ruleset: `Tech_Parasite` 2 at **Player**
range without `survives`, so only the Great Library's owner gets techs that two other civs know, and only while it
stands. That keeps a reason to build the wonder and ends the world-wide catch-up. Expect a slower tree: the no-gift
game is the lower bound, so #217's curve would need another autogame (at `tilesperplayer` 110) after the change.
John decides; nothing is changed here.

## 9. What is left

1. **Space at Normal** (#215). The rules allow a ship, and an Easy AI builds and launches one, but a Normal AI
   reaches Space Flight late or never and does not build parts. It needs AI work, not a cost change.
2. **AEGIS Cruisers** (#214). Strength 40 for 170 shields makes it the best unit per shield, so the late AI builds
   it in half its cities. A roster question for John.
3. **Siege** (#202, then #83). The AI does not build siege units, so the bombard behaviour cannot be tested.
4. **Pace on war maps.** Seed 42 reaches only era VI. Lowering costs further would undo most of the steep curve.

## 10. Decisions for John

- **Plan decision 8** said to keep the culture numbers until the culture slice. #212 re-tunes them now, from the
  autogames.
- **Plan decision 10** chose the steep curve to 275 %. #217 flattens it at 200 % after era IV.
- **Plan row 14** (#220): `City_Unrest` is an engine change, small enough to offer upstream.
- **Draft sizes** (#221): Levy size 3, Militia and Conscripts size 4, no cap on whipping.
- **AEGIS Cruiser** (#214) and **space at Normal** (#215), from section 9.
- **The Great Library gift** (section 8): owner only, as recommended, or keep the world-wide gift.
