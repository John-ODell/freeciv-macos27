# Freeciv45 build plan

Date: 2026-10-16. Status: proposal; every decision in it is John's.
Labels as in the brief: observed, derived, inferred, unknown. Effort: S about a day, M two to four days,
L a week or more (inferred, each with its test).

Freeciv45 is the game civ45 became on 2026-10-16: an empire game in the style of the fourth game in the series.
Units travel in stacks on a square map (seen at an angle, topology ISO, since issue 188 on 2026-10-18), there are
many unit types, and the look is modern, with our own art. It is built on Freeciv 3.2 and is GPL. No Firaxis or 2K
code, data, art, text or names are used. Mechanics come from public descriptions, written in our own words.

Sources: four research reports, written by separate agents from public sources and the Freeciv tree.
- `notes/freeciv45/in-freeciv.md`: how each system maps onto Freeciv 3.2, and a slice plan.
- `notes/freeciv45/video-notes.md`: what a player does and looks at in a mid-game session (a public video).
- The graphics report, which proposes the tileset, the asset list, the art pipeline and the licence rules. It
  quotes John's private art repo, so it is kept with the art, not here; its conclusions are in "Look" below.
- `notes/freeciv45/mechanics.md`: the clean-room mechanics spec. It describes 18 systems from 101 public sources,
  rates each MUST, LATER or SKIP for a first playable, and ends with open questions. Its header records what
  changed after it was written and which of its engine claims were checked against the source.

## Where it stands

| Done | Evidence |
|---|---|
| The one-unit-per-tile hex rules kept as `civ54` for the later engine game | PR 45; `scripts/civ54-rules-test.sh` 11/11 |
| Slice 1: stacks, a square map seen from above that wraps east to west, only the defender dies (`killstack` off), cities work the 21-tile fat cross | PR 47; `scripts/civ45-rules-test.sh` 8/8, control run with killstack on fails; 100-turn autogame, `notes/civ45-planning.md` |
| A first look in the bundled Qt client: trident is offered at pregame; declined, amplio2 draws the square map as diamonds | PR 56; `notes/freeciv45/client-look.md` |
| A hook (patch 0007) that hands an AI player's builds and research to an outside chooser, so the play harness can play-test Freeciv45 | PR 63; `scripts/harness-test.sh`, all checks pass with a random chooser and with the AI's own pick; `notes/freeciv45/harness.md` |
| Slice 2, Combat (patch 0008): siege units wound every unit of a stack of two or more and kill none ("Bombard 2" with a new `Collateral` flag), fights go to the death (`Combat_Rounds` 0) except for `Withdraws` attackers, which break off after 12 rounds per 10 hit points, and aircraft bombard at range 1 | PR 89 (issue 75); `scripts/civ45-rules-test.sh` 18/18, 11/18 on the slice 1 rules; four 200-turn autogames with `scripts/civ45-combat-log.lua`, `notes/freeciv45/mechanics.md` section 6 |
| Six ways to win (patch 0009): conquest, domination (Lua: 60 % of the land and 50 % of the citizens for 3 turns, from turn 100), culture at 8000 points with a 50 % lead, the spaceship's arrival, the allied win, and the best score at turn 475 (Lua names the winner) | PR 100 (issue 92); `scripts/civ45-rules-test.sh` 24/24 and the score winner with `--extra "set endturn 6"`; two 475-turn autogames (allied victory at 152, cultural victory at 437), `notes/freeciv45/mechanics.md` section 7 |
| Slice 3, upgrades and the draft (patch 0010): upgrades keep veteran levels; Levy, Militia and Conscripts are raised from a citizen under the stronger governments; any of them disbanded in a city puts 30 shields into the build, the whip until Lua can shrink a city | PR 108 (issue 106); `scripts/civ45-rules-test.sh` 28/28 plus ten shell checks; a 300-turn autogame with `scripts/civ45-draft-log.lua`, `notes/freeciv45/mechanics.md` section 8 |
| Tech slice (patch 0011), ahead of the roster because its new units need the tree's techs: 92 advances in seven era classes with cost_pct 100 to 150, six techs added, three sandbox leftovers dropped and their unlocks re-homed, irrigation behind Agriculture | PR 110 (issue 109); `scripts/civ45-rules-test.sh` 32/32 plus eleven shell checks; `scripts/tech-tree-check.py --ruleset` PASS; a 400-turn autogame with `scripts/civ45-tech-log.lua`, `notes/freeciv45/mechanics.md` section 9 |
| Roster slice (patch 0012): 76 unit types in seven eras with one strength number, hit points 10/20/30 by era, firepower 1, eight class flags with the counters as paired bonuses rows on the unit that has one, city-attack and terrain-defence effects, City Walls keyed on the attacker's class; 16 new units, 11 renamed (rule names kept), 5 dropped | PR 112 (issue 111); `scripts/civ45-rules-test.sh` 38/38 plus thirteen shell checks; two 400-turn autogames with `scripts/civ45-combat-log.lua` read by `scripts/civ45-roster-summary.py`, `notes/freeciv45/mechanics.md` section 10 |
| Great people slice (patch 0013): seven kinds born from a city's points (User_Effect_3 per building, 150 + 75 per birth), the first to four techs, Residents through Join City, deeds through User Action 3 (tech, gold, 400 history, the Sanctum, a veteran level for the stack), golden ages through User Action 4 (a timed small wonder: +1 shield and trade, double points, no anarchy), and a turn_begin rule that spends the AI's great people | PR 114 (issue 113); `scripts/civ45-rules-test.sh` 50/50 plus fifteen shell checks; `scripts/gp-points-check.py`; two 400-turn autogames read by `scripts/civ45-gp-summary.py`, `notes/freeciv45/mechanics.md` section 11 |
| The Qt client's unit bar (patch 0015): the first-slice diff on the fork, the key hint colour a theme property, NightStalker and System rules so the bar reads on both (issue 99) | PR 124 (issue 123); `scripts/build.sh qt`; screenshots of a stack, a lone unit and the light theme in `notes/freeciv45/ui/` (clicks and hover not exercised: no Accessibility grant) |
| The unit bar clicked, hovered and switched in a running civ45 game, and fixed (patch 0016): it keeps its width after a focus change (#129), retires chips and buttons with `deleteLater` (#130), the portrait and chip tooltips the design asks for (#131), only the actions every unit in focus can do (#132) | PR for issue 125; `scripts/ui-drive.sh` with `notes/freeciv45/ui/bar-test/bar.txt` (an in-process QTest driver, `uidrive.diff`, built in a copy of the fork); 21 shots and the results in `first-slice.md` |
| The city overlay on the fork (patch 0017): an own city opens as yields, citizens and buildings, production with Change and Buy, and a footer on the map's edges, the map centred with the worked tiles drawn; the full dialog behind Enter | PR 139 (issue 137); `scripts/build.sh qt` into `~/freeciv-builds/qt`; `city-test/city.txt` run offscreen on a driver copy, `notes/freeciv45/ui/city-overlay-on-map.jpg` |
| The map's edges, first slice (patch 0018): a top strip with research, gold and income, rates, culture, year and turn and End turn, and a right-edge column of round buttons for Map, Research, Nations, Cities, Units, Economy and More, replacing the sidebar behind `gui_qt_freeciv45_edges` (default on) | PR for issue 140; `scripts/build.sh qt`; `edges-test/edges.txt` with `scripts/ui-drive.sh` (offscreen), shots in `notes/freeciv45/ui/edges-test/` and `edges-strip-column*.jpg`; badges #143 and "what next" #144 filed |
| John's decisions 9 to 12 applied (patch 0014): Archery in era I, a Horses resource gating the seven mounted units, the three dropped techs back (95) with the Altar, the Space Elevator and its Tether on them and Women's Suffrage on Labor Union, the steep era curve (`cost_pct` 100 to 275), the Siege Workshop, Apothecary and Telegraph Office on Physics, Medicine and Electricity, Alpine Troops and Zealots back, Transport cargo 4, Residents re-created for a city's new owner, golden ages pledged by great people of different kinds | PR 122 (issue 115); `scripts/civ45-rules-test.sh` 55/55 plus eighteen shell checks; `scripts/tech-tree-check.py` against the ruleset and buildings; two 400-turn autogames before and after the curve read by `scripts/civ45-tech-summary.py` (section 12 of the mechanics note) |
| Design notes for the next rules slices, each implementable without re-deriving anything: the six wins (built as patch 0009), the 82-unit roster with class counters and upgrade chains, a 92-tech seven-era tree with a consistency checker, and great people with deeds, golden ages and an AI auto-use rule | PRs 77, 90, 96 and 101 (issues 76, 88, 93, 97); `notes/freeciv45/design/{victory,units-and-upgrades,tech-tree,great-people}.md`; `scripts/tech-tree-check.py` passes against the tree, the roster and `civ45/buildings.ruleset` |

Open from slice 1: `test.sh` reads the installed ruleset unless told otherwise (#48), and the AI's stack use in
later eras (#49). The client look (#50) found a stale line in the tileset dialog (#53) and a missing SVG plugin in
the bundle (#54, and #55 upstream).

Open from slice 2: the default AI bombards a stack every turn instead of attacking it, and never follows a
bombardment with an attack (#83); with diplomacy allowed the ten AIs all ally and an autogame ends by allied victory
around turn 150, which `test.sh` reports as a failure (#84; `test.sh` passes a victory since PR 100 and names the turn, and allied victory stays on, decision 13). The siege rates and the break-off cap are placeholders
until the one-strength decision (7) is confirmed from the roster autogames (section 10 of the mechanics note).

Open from the victory slice: the design note's five questions (decision 8), and no AI came near the domination
thresholds in 437 turns, so that rule is untested in play.

Open from slice 3: no unhappiness or limit follows a draft (#107, built as patch 0024: unrest that cancels content from buildings and a per-turn draft quota, section 13 of the mechanics note); the AI's drafting is whatever the autogame shows
(section 8 of the mechanics note); the draft units are the first with one strength number (decision 7).

Open from the tech slice: the design's four questions (decision 10); the six new techs borrow icons; the cost
formula counts the tech itself, so every cost is one tier above the design's table (corrected in the note).

Open from the roster slice: the design's five questions (decision 11); the AI attacks with its cheapest
defenders now that attack equals defence (Spearmen made 155 of 894 attacks in the war game and died 295 times,
section 10 of the mechanics note), which is the first evidence on decision 7; the 16 new units borrow sprites until
civ45-tileset draws them; Copper, Aluminium and Uranium gating waits for slice 4 (Horses gates since patch 0014);
the design note's counter row was corrected (the divider row belongs on the unit that has the counter).

Open from the great people slice: the design's five questions (decision 12); the AI's first great person always
pledges a golden age (section 11 of the mechanics note); the seven units and ten buildings borrow art; points from
specialists and the Commander from combat wait for Lua support and slice 6.

Open from the decisions unit (patch 0014, section 12 of the mechanics note): the Horses gate is a city-range
requirement that Lua cannot test (`Player:can_build_direct` reads player-range requirements only), so the rules
test greps it; the pledge markers and the Golden Age itself are small wonders in the capital and go with it when
the capital falls, which forgets the pledges; Horse Bowmen keep era II in the roster table though both their techs
are era I now; the reference game's era cost ratios are not in the notes, so the steep curve's target shape is
unverified and the numbers are ours; the borrowed building art (`b.siege_workshop`, `b.apothecary`,
`b.telegraph_office`, `b.pledge`) and the `u.zealots` sprite wait for civ45-tileset.

Open from the design notes: their questions are decisions 9 to 11. Findings while writing them: the committed fork
sets `victory_min_points 20000`, which no autogame came within half of before the victory slice replaced it;
`Output_Bonus_Absolute` is clamped to zero or below in 3.2 (`common/city.c:2409`), the opposite of its README
entry; only `User_Effect_3`/`_4` and "User Action 3"/"4" are free because the sandbox leftovers hold 1 and 2;
and the sandbox tree the fork inherits places several techs out of era order (tech-tree.md section 3).

## Decisions for John

| # | Question | Recommendation |
|---|---|---|
| 1 | Does Freeciv45 stay "rules and Lua on the stock Freeciv server", so it runs on any Freeciv 3.2 and its servers take stock clients, with our own work allowed in the Mac client? | Yes. Client patches don't change the rules or the network protocol (derived: the server sends the rules to each client, `notes/game-directions.md`). Engine-only systems go to civ54 or upstream. |
| 2 | Combat: fights to the death, with a break-off for fast units; siege units damage whole stacks; bombard range back to 1 (2 was for fifth-game ranged units) | Yes, as the next slice. Stacks with no counter invite one huge stack (inferred). Built 2026-10-17 as slice 2, see "Where it stands". |
| 3 | Map look until our art exists: trident (square, 30 px, dated) as now; amplio2 drawn on the square map (a diamond look, seen in #50); or the `ISO` topology (same rules, amplio2's look) | Keep square with trident for now. The client offers trident at pregame, and a player who declines gets amplio2's diamonds (`notes/freeciv45/client-look.md`). The target is our own 96 px square tileset. |
| 4 | Art: 96 px tiles from 192 px masters; units with one facing in v1 (8 facings later); the proposed "gouache atlas" style; which image tool (OpenAI API, ChatGPT app, Gemini) | Yes to sizes and one facing. Style and tool are John's taste. |
| 5 | Lock `killstack` and `topology` in the ruleset, or leave them as pregame choices? | Leave unlocked, as Freeciv's own webperimental does with killstack (`refs/freeciv-S3_2/data/webperimental/game.ruleset:724`). |
| 6 | Public name "Freeciv45" | Fine as a working name. It follows the "Freeciv21" fork's pattern and avoids "Civilization"/"Civ" (inferred; Freeciv's naming guidance not checked). |
| 8 | Victory numbers: domination at 60 % of the land and 50 % of the citizens for 3 turns (the spec says about 65 % plus a population lead); allies do not pool for it (Lua cannot see alliances); `endturn` 475 as the shipped default; culture 8000 with a 50 % lead before the culture slice; the score winner announced by Lua | Built with these values 2026-10-17 (PR 100). Keep them until the culture and roster slices, then re-tune from autogames. Culture re-tuned 2026-10-18 from autogames for balance report 2 (issue 165, `notes/freeciv45/balance-2.md`): 30000 points with a 25 % lead. |
| 9 | Draft units: three spanning the eras (Levy, Militia, Conscripts; the design note's question 1) or one per era; raised only under Tribal, Despotism, Monarchy, Communism and Fundamentalism until civics (row 8) give the draft a column of its own; 30 shields per whipped citizen at every era | Decided by John 2026-10-17: keep the three draft units (Levy, Militia, Conscripts) as built in PR 108, no change; the governments are revisited with row 8. |
| 10 | The tree's open questions: Archery in era II (Archers after Spearmen and Axemen) or in era I; drop Ruler Apotheosis, Nanomaterials and Labor Union; the cost curve 100 to 150 per era, steeper or flat; themed names for Physics, Medicine and Electricity | Decided by John 2026-10-17 (issue 115): Archery in era I; Ruler Apotheosis, Nanomaterials and Labor Union kept (95 techs) with the Altar, the Space Elevator and its Tether back on them, Women's Suffrage moved to Labor Union and Mechanized Infantry left at Robotics; the steep curve `cost_pct` 100, 150, 175, 200, 225, 250, 275 instead of 100 to 150; Physics, Medicine and Electricity unlock the Siege Workshop, the Apothecary and the Telegraph Office. The AI's pace before and after is in section 12 of the mechanics note. |
| 11 | The roster's open questions: three draft units or one per era; hit points 10/20/30 by era; keep both Cruiser and Ship of the Line; Alpine Troops and Crusaders dropped or kept as themed variants; Transport cargo 8 or 4 | Decided by John 2026-10-17 (issue 115): three draft units, no change; hit points 10/20/30, no change; both Cruiser and Ship of the Line, no change; Alpine Troops back as they were and Crusaders back as Zealots, nation-neutral until the unique-unit pass; Transport cargo 4; Horses gate the seven mounted units from this build on (a grassland and plains resource), not from slice 4. |
| 12 | Great people's open questions: point values in effect rows and the Lua table (kept with `scripts/gp-points-check.py`), Residents lost on capture, great people kept out of Disband Unit Recover, pledges of any kind, the Spymaster with the native diplomat actions for a deed | Decided by John 2026-10-17 (issue 115): point values stay in the effect rows and the Lua table with `scripts/gp-points-check.py`, no change; Residents stay with a captured city, re-created for the new owner; no recycling of great people into production, the Builder's Help Wonder stays, no change; each golden age needs great people of different kinds, one more than the last; the Spymaster keeps the native diplomat actions as its deed, no change. |
| 13 | Allied victory in AI-only games: in a 10-AI civ45 autogame with diplomacy allowed, all ten can ally and win together with no war at all (turn 142 on seeds 42/42 with patch 0020's rules: 40 of 45 pairs allied by turn 60, no attack in the whole game; on seeds 11/11 wars go on to turn 400). Keep `ALLIED` in `victories`, or drop it? | Keep it (issue 84). `notes/freeciv45/design/victory.md` 2.5 keeps the allied win so a human and an AI partner can finish together, and it only fires when every living player is allied with every other, so a human who stays out of the alliance stops it. `scripts/test.sh` counts a victory as a finished game and says so ("ended by a victory in turn N"); autogames that must run their full length add `--extra "set victories SPACERACE\|CULTURE"` (or `set diplomacy DISABLED` for a war game). Why ten AIs ally so readily in civ45 when civ2civ3 and sandbox keep wars going on the same seeds is a balance question: #159. |
| 14 | Draft and whip unrest on base content (issue 157): an engine change, or accept that `Make_Content` -N only cancels content from buildings | Built as an engine change for balance report 2, 2026-10-18 (John to confirm): a Freeciv45 effect `City_Unrest` (fork `common/city.c`, `citizen_base_mood`, documented in `doc/README.effects`) turns N base content citizens of a city unhappy; the Draft Unrest buildings use it (`notes/freeciv45/mechanics.md` section 13). It is small enough to offer upstream later. |
| 7 | One strength number per unit, for attack and defence alike, as in the reference game (spec 2.5, rated MUST), or Freeciv's separate attack and defence values? | One strength, brought in with slice 2 and the roster (slice 10), with an autogame before and after. Freeciv already decides each round by strength share; only the damage per round stays fixed (spec 2.5). Built in the roster slice (issue 111); the AI's attacking with Spearmen (mechanics note section 10) is the first thing to weigh against it. |
| 9 | Roster: HP by era (10/20/30), the five dropped sandbox units, the 11 renames, resource gating by `Extra` until slice 4, and the three draft units (`notes/freeciv45/design/units-and-upgrades.md`, "Open questions for John") | Take the note's defaults; re-tune after the first roster autogame. |
| 10 | Tech tree: six added and three dropped techs, era cost percents 100 to 150, the building re-homing table, and whether the checker runs in `test.sh` (`notes/freeciv45/design/tech-tree.md`, "Open questions for John") | Take the note's tree as the slice 10 baseline; add the checker to `test.sh`. |
| 11 | Great people: one source of truth for point values (effects or Lua), Residents on capture, whether every great person may "Disband Unit Recover", golden age pledges of any kind, and the Spymaster without a deed (`notes/freeciv45/design/great-people.md`, "Open questions for John") | Lua as the single source for points, Residents lost on capture, no recover, any kind pledges, Spymaster stays native. |

## Roadmap

Each row is one issue, branch, PR and fork patch, with a rules-test case and an autogame, as slice 1 was.
Slice names use the reference game's terms as working labels only; what ships in the ruleset gets names of its
own, as the clean-room rule asks.

### Rules (ruleset and Lua, runs on stock Freeciv)

| # | Slice | Main change | Effort | Main risk |
|---|---|---|---|---|
| 2 | Combat | Siege "Bombard 2" allowed only against two or more units, so it wounds a stack without killing it; `Combat_Rounds` 0 (to the death) plus a capped break-off for a new `Withdraws` flag; bombard range 1 | S-M | The AI bombards instead of taking cities; tuning |
| 3 | Upgrades, drafting and whipping | Upgrades keep veteran levels along the chains and at the prices in `notes/freeciv45/design/units-and-upgrades.md` (sections 1 and 2, `upgrade_veteran_loss 0`); one draft unit per era that costs a citizen, behind a government (the Levy, Militia and Conscripts rows there); whipping as the spec's levy unit, which costs a citizen and is recycled into the build, because Lua cannot shrink a city | S-M | The AI drafts its cities small |
| 4 | Happiness and health from resources | +1 content per luxury and +health per food resource the nation can reach, through a marker building per resource that Lua keeps (an Extra requirement stops at TradeRoute range); the missing resources (horses, copper, stone, marble, aluminium, uranium) | M | Lua decides what counts as connected; its turn-start cost on big maps |
| 5 | Cottages | Four tile improvements that grow while worked and give more trade | M | Growth is random, not a fixed count of turns |
| 6 | Great Generals | Lua counts combat; a General joins a stack to promote it or settles as a military academy | M | The AI never uses it |
| 7 | Leader traits | Trait bonuses per nation, as hidden small wonders at first | M | Picking traits per nation |
| 8 | Culture and civics | A culture rate as a Freeciv "multiplier" slider; culture levels that add city defence (`MinCulture`); civics as governments plus, as the spec proposes, one policy building per column that Lua swaps | M | Five columns of exclusive choices are not native; the AI won't pick policies |
| 9 | Economy | Linear food box, content and health caps at the reference values, national gold upkeep for buildings and units, seven specialists (spec 2.4) | M | Freeciv riots where the reference game idles unhappy citizens (spec question 9) |
| 10 | Roster and tech tree | The 82 unit types, eight class flags and paired counter bonuses of `notes/freeciv45/design/units-and-upgrades.md` (46 kept, 11 renamed, 5 dropped, 18 new, 7 great people), on the 92-tech seven-era tree of `notes/freeciv45/design/tech-tree.md` with its building re-homing table and `scripts/tech-tree-check.py`; resource gating from slice 4; a unique unit per nation later (spec 2.8) | L | Every unit needs art (T2); balance |
| 11 | Great People and golden ages | As `notes/freeciv45/design/great-people.md`: `User_Effect_3` points and `User_Effect_4` percent read by Lua each turn (no specialist count), seven kinds (Sage, Builder, Magnate, Virtuoso, Oracle, Commander, Spymaster) that settle through "Join City" as Resident buildings, do a deed through "User Action 3" or native "Help Wonder", and pledge a 10-turn golden age ("User Action 4", a timed small wonder); a `turn_begin` rule spends AI great people through the same enablers (spec 2.9) | M | The AI cannot plan around them; `Output_Bonus_Absolute` is unusable, so settled greats give percents and centre-tile output |
| 12 | Religion, simplified | Seven Lua-founded religions as city marker buildings with passive spread, temples, state-religion happiness and shrine gold (spec 2.10) | L | The same AI gap; no missionaries at first |

Slice 2 moves first because slice 1 brought stacks back with no counter to them (mapping study, risk column of its slice 1).
Measure the AI (#49) after slice 2. Slices 9 to 12 complete the spec's first playable (its section 3). What it
defers (flanking, first strikes, ratio damage, automatic trade routes, espionage points, corporations, vassals and
votes, random events, AI personalities) waits for civ54 or a later pass.

### Look (tileset and Mac client)

| # | Step | What | Effort |
|---|---|---|---|
| T0 | Test tileset | Two terrains drawn by script, to prove the overhead corner cells and tall layers nobody has tried yet | S |
| T1 | Tileset v0 | Every tag the ruleset needs at 96 px, with scripted placeholders where no art exists yet, so the game loads complete | M |
| T2 | Painted art | About 430 kept cells from 7 sheets made with John's sheet workflow (ground, features, resources, units, cities, tech and building icons), plus about 630 sprites made by script (edges, fog, roads, rivers, overlays) | L, John and Claude |
| Q1 | Smooth Qt map | Non-blocking move animation (GTK has it, Qt doesn't; S) and Retina rendering (the Qt map ignores the display's pixel ratio; M) | M |
| Q2 | Numbers on hover | Tile, unit and city hover summaries and a combat odds tooltip before attacking (the video's top takeaway; Freeciv already computes the odds) | M |
| Q3 | Fast paths | Tech-learned popup (an empty stub in Qt), a chooser when a build completes, the build queue from the map | S-M |

Licence rules for the art: Freeciv45 art ships as GPL-2.0-or-later. Allowed inputs are only CC0, public domain,
CC BY 4.0 and GPL. No CC BY-SA, NonCommercial or NoDerivatives. There is one provenance record per image, and
no game screenshots or other studios' art as references. The OpenAI terms could not be read (HTTP 403 on
2026-10-16), so John records the version he agreed to.

### Engine (civ54 or upstream, not Freeciv45)

True collateral damage and first strikes, a full religion system, a real Great People system, the fourth game's
unhappiness (idle citizens instead of disorder), culture-driven border rings, ratio-based combat damage, Lua calls
that read a unit's hit points or change a city's size (neither exists: `common/scriptcore/tolua_game.pkg:58-66`,
`server/scripting/tolua_server.pkg:118-250`), Extra requirements at Player range, and a 3D client (a Godot front
end on Freeciv's C client core, XL). Lua can already cut hit points after an attack
(`server/scripting/api_server_edit.c:592-598`, signal `action_finished_unit_units`), but without reading them it
cannot keep the cut non-lethal. Some are small and general enough to offer upstream: a border-radius effect, Lua
hit point and city size calls, collateral fields.

## Shipping

Each finished slice goes into the next macOS release (notarized once the Apple ID password is reset) and,
because it is data, into a modpack that stock Windows and Linux Freeciv can load. Client patches ship only in our
Mac app.
