# FCW rulesets compared with civ45 (read-only study, 2026-10-18)

Path shorthands: **FCW** = `~/Desktop/freeciv-port/refs/fcw.org-server`, **D** = `FCW/freeciv/freeciv/data/mp2-dragoon`,
**C45** = `~/Desktop/freeciv-port/port/freeciv/data/civ45`, **FC32** = `~/Desktop/freeciv-port/port/freeciv` (our 3.2 tree).
Nothing was modified.

**MP2-Elephant is not in this clone.** The newest MP2 ruleset here is MP2-Dragoon (`D/game.ruleset:27`); the web client's
ruleset menu stops at Caravel (`FCW/freeciv-web/src/main/webapp/javascript/pregame.js:710`) and its rules switch knows
"MP2 Dragoon" as the latest (`packhand.js:793`). Everything below is from Dragoon and its ancestors; Elephant would need a
newer pull.

## Most useful for us

1. **Our tech leakage is probably what makes the field research as a pack (issue 167).** civ45 uses `tech_leakage = "Embassies"`
   (`C45/game.ruleset:374`) with `techleak` at the 3.2 default of 100 (not set in C45's `[settings]`). In 3.2 the cost cut is
   base cost x (players who know it and with whom you have an embassy) / players (`FC32/common/research.c:943-970`): with
   embassies everywhere and 9 of 10 rivals knowing a tech, it costs 10%. MP2 sets `techleak 25` (`D/game.ruleset:3430`).
2. **civ45's Great Library shares techs with everyone forever.** `Tech_Parasite_Pct_Max 30` at World range with `survives`
   (`C45/effects.ruleset:3514-3520`; meaning in `FC32/doc/README.effects:683-693`) hands every player any tech 30% of players
   know, once anyone builds it. MP2 has no parasite effect at all.
3. **Casus belli for border infractions (issue 159).** MP2 grants casus belli for roads, bases, terraforming and pillage in
   foreign land, and for military moves into foreign land under ceasefire (`D/effects.ruleset:7241-7275, 8000`). In 3.2 a
   casus belli makes the AI lose love sharply and, at level 2, plan a revenge war (`FC32/ai/default/daidiplomacy.c:1085-1095,
   1624-1631`). civ45 has the pillage trigger but none for roads, bases, terraforming or movement (its 46 rows cover attacks, pillage, spies and nukes).
4. **Deny plain Attack to siege units against stacks (issue 83).** MP2 shapes who may "Attack" entirely with enablers
   (`D/game.ruleset:1626-1690`). The 3.2 AI already prefers any enabled Bombard over Attack (`FC32/ai/default/aitools.c:845-869`),
   so a target requirement on civ45's siege Attack enablers would force a second bombardment.
5. **Graded siege versus walls** with plain `Defend_Bonus` rows per unit type (walls 3x, 2.75x vs Catapult, 2.5x vs Cannon,
   2.25x vs Artillery: `D/effects.ruleset:2533-2568`). Stock 3.2, fits our City Walls rule.
6. **Philosophy-style gating in Lua** (time cutoff plus "you must not know the next tier yet": `D/script.lua:25-42, 120-160`) is
   a ready pattern for taming our first-to-tech great-person gifts (issue 166).

Caveat for all borrowing: Caravel and Dragoon need FCW's patched server. They pack special-attack parameters into the
`city_size` and `paratroopers_mr_sub` fields as bit fields (`D/units.ruleset:4373`), use 13 effect types 3.2 lacks
(Stack_Escape_Pct, Gulag, Unit_Work_Pct, Coinage_Bonus_Pm and others) and about 17 FCW-only server settings. Take ideas, not files.

## 1. What FCW ships

All FCW rulesets are format_version 20 with the 3.1-development capability string (e.g. `D/game.ruleset:14-15`); the bundled
server reports 3.0.92-dev (`FCW/freeciv/freeciv/fc_version:8-12`), a 3.1 development snapshot (upstream baseline noted in
`FCW/freeciv/advanced_backports.txt`). civ45 is format 30, 3.2.

| Directory (under `FCW/freeciv/freeciv/data/`) | Name | Parent | What it changes |
|---|---|---|---|
| `multiplayer` | Multiplayer | classic (upstream) | Upstream Freeciv ruleset; "1.0 (old)" in the web menu |
| `mpplus` (second, diverged copy in `FCW/rulesets/mpplus`) | Multiplayer-Plus | multiplayer | Conservative fixes: tech costs evened across eras, Philosophy cutoff, Darwin made like Colossus, mountain vision, no bribing aircraft, swamp transform 12 (`mpplus/README.mpplus`) |
| `mp2` | Multiplayer-Evolution | multiplayer | Big rework: ancient ship line, more air units, Fort before Fortress, one foreign trade route per city, 9x rails, 7 veteran levels, "ReWonder", Courthouse rework (`mp2/README.mp2`) |
| `ag` | Avant-garde | mp2 | Freer imports from other rulesets and later commercial games (`ag/README.ag`) |
| `mp2-brava` | MP2 Brava | mp2/ag line | Trains, capturable transport, Sea Bridge, Tribesmen, early herds, wonders without Trade (`mp2-brava/changelog.txt`) |
| `mp2-brava2` | headers say Avant-garde | ag | Mislabelled AG variant; differs from brava in four files |
| `mp2-caravel` | MP2 Caravel | brava | Special unit attacks, Siege Ram, Catapult line as wall-breakers, Fortifications/Walls split, Magna Carta, Theocracy, Nationalism, casus belli expansion, Castle/Bunker, trade rebalance (`mp2-caravel/changelog.txt`) |
| `mp2-dragoon` | MP2 Dragoon | caravel | Faster granary curve, despotic founding food, Scout, Ziggurat/Agoge, new tech tiers, Goods at Pottery (`D/changelog.txt`). Note `mp2-dragoon.serv` points at `mp2-caravel` |
| `classic`, `civ1`, `civ2`, `civ2civ3`, `sandbox`, `webperimental`, `experimental`, `granularity`, `alien`, `stub`, `maptest` | upstream | - | Freeciv's own, 3.1-dev era |
| `.historic/*` | old mp2, ag2, mp2sandbox | - | Archived predecessors |

## 2. MP2 mechanics worth borrowing

- **Unit classes and counters.** Classes split land units by what they may do: `LandNoKill` (no population loss), `LandRoad`
  (road-bound Siege Ram, Truck), `LandRail`, `Cargo`, `Heli`, several air classes (`D/units.ruleset:190-330`). Counters are
  flag bonuses: Pikemen double against `Horse`; Knights get defence bonuses against horse and foot (`D/units.ruleset:1284, 1945`).
  Our Melee/Mounted/Siege flags already do this; a `LandNoKill`-style class is a cheap way to stop light units razing cities.
- **Siege.** Bombard is limited per unit: number of targets, maximum kills, move cost, staying fortified (Battleship hits 4,
  kills at most 1, spends 5 moves). That needs FCW's server. Stock-compatible parts: graded wall penalties (above); Siege Ram
  against Fortresses, gated off once anyone knows Metallurgy (`D/game.ruleset:1293-1322`); siege units given "ranged defence"
  retaliation (Caravel changelog, Ballistic section).
- **Veterans.** Seven levels, power 100/150/175/200/210/220/230, extra move only at the top three (`D/units.ruleset:98-116`);
  per-unit overrides (`D/units.ruleset` Battleship) and per-wonder promotion boosts via `Veteran_Combat` (`D/effects.ruleset:4785,
  5377`). civ45 has four levels (`C45/units.ruleset:94-110`); Civ4's promotions map better onto more levels.
- **Stacks.** MP2 keeps killstack on; Forts and Fortresses shield stacks. Not useful to us with killstack off, except the
  "CanEscape" flag (exists in 3.2: `FC32/common/unittype.h:271`).
- **Terrain and movement.** 9 move fragments, roads 1/3, rails 1/9 (not infinite), restrictinfra on, Hills give half the
  mountain vision bonus, Forest/Swamp 1.33x (`D/terrain.ruleset:74, 459-697`; `D/changelog.txt` item 12).
- **Governments.** Eight, with Constitutional Monarchy via the Magna Carta wonder, Theocracy and Nationalism; empire-size
  limits per government (`D/effects.ruleset:1596-1718`); unit unhappiness scaled by `Unhappy_Factor` per government.
- **Wonders.** Most classic wonders are small wonders, so every nation can have them and must choose (`D/buildings.ruleset`,
  genus fields). Fits Civ4 national wonders; it would also cut great-person points from wonders.
- **Tech cost.** Hand-set "Classic+" costs from 24 to 11,920 bulbs, about 500x (`D/techs.ruleset:116-999`, style at
  `D/game.ruleset:2977`), against civ45's 30 to 5,857, about 195x (`notes/freeciv45/mechanics.md` section 12).
- **City growth.** Granary 16, 23, 31, 40, 50, 60, 70 then +1 per size (`D/game.ruleset:89-90`), capped near 70.
- **Happiness.** Foreign citizens unhappy at 45% plus one (`D/effects.ruleset:94-106`); Courthouse content for all governments.
- **Trade and caravans.** One route per city (`D/effects.ruleset:583`), foreign only, inactive at war (`D/game.ruleset:3122-3135`),
  minimum distance 15, simple revenue style, revenue cut 40% by Railroad (`D/effects.ruleset:594`).
- **Culture.** None to speak of (below).
- **AI tuning.** Only `builder_default 60` in `D/nations.ruleset` versus our 50 (`C45/nations.ruleset`); no AI-specific Lua.

## 3. Our open issues against FCW

- **164, no spaceship launch.** Nothing in FCW helps the AI; MP2 goes the other way: parts cost 500/1000/2000
  (`D/buildings.ruleset:1195-1277`, ours 150/300/600), Apollo is a per-player small wonder enabling space
  (`D/effects.ruleset:4908`), travel time 225% (`D/game.ruleset:3425`; in 3.2 the setting is `spaceship_travel_pct`). The fix is AI
  code, not data.
- **165, culture late or never.** MP2 has culture victory off (`D/game.ruleset:3450`) and its only history source is +1 per
  animal killed from Lua (`D/script.lua:243`). The usable idea is the call itself: `edit.add_player_history` can grant culture on
  events. Not from FCW, but both rulesets leave `history_interest_pml` at 0 (`C45/game.ruleset:404`); interest would let an early
  leader pull away and meet the 50% lead sooner.
- **166, too many great people.** FCW has none. Patterns: the Philosophy bonus ends at turn 85 and is withheld from anyone who
  already knows a next-tier tech (`D/script.lua:25-42, 120-160`); Darwin no longer gives techs (`mp2/README.mp2`, Tech 3).
  The same tests in our `fc45_gp_tech` (`C45/script.lua:944`) could cap gifts by era.
- **167, tech too fast.** The leakage and Great Library points above; MP2's steeper cost range; `freecost 1`
  (`D/game.ruleset:3398`) so free techs cost bulbs; tech trades and conquests taxed through FCW-only `blueprints`, whose stock
  equivalents are `diplbulbcost` and `conquercost`. civ45's Cities tech upkeep (`C45/game.ruleset:381`) is already stronger than MP2's none.
- **159, one allied bloc.** Casus belli rows above, plus United Nations giving the whole world casus belli against an
  intruder (`D/effects.ruleset:7920`, value 1000). Caution: MP2's Pax Dei and UN use `Has_Senate`, a peace device
  (`D/effects.ruleset:6073`); civ45 also gives a senate to Democracy, Federation and, under UN conditions, everyone
  (`C45/effects.ruleset:1800-1818, 4097-4106`). Not FCW, same file family: raising `aggressive_default` in
  `C45/nations.ruleset` raises the AI's war threshold (`FC32/ai/default/daidiplomacy.c:1709-1713`). MP2 keeps ALLIED victory on.
- **83, attack instead of a second bombard.** FCW's AI only learned to pick Bombard 2/3 (`FCW/freeciv/freeciv/ai/default/aitools.c:857-871`),
  which 3.2 already does. Useful: enabler-shaped Attack (point 4 above) and bombards that cost part of the turn rather than all
  of it (MP2 spends 5 moves; ours ends the turn).
- **157/158, whip and draft unhappiness.** MP2 has no whip. Its pop units (Pilgrims, Proletarians) rely on an FCW split of
  pop cost and pop added; `hangry`, `fulldisorder` and the `Gulag` effect are FCW engine patches. That FCW changed the engine
  here matches our finding that 3.2 cannot lower base content from a city effect. `Enemy_Citizen_Unhappy_Pct` is the only
  stock effect that makes citizens unhappy, and it applies to foreigners only.

## 4. Lua and settings FCW uses that we don't

Lua in `D/script.lua`: Philosophy bonus with turn and tier cutoffs (73-186); ruins on destroyed cities (45, civ45 has the same);
gold and history for killing animals (220-255); Chand Baori adds a river (257-266); Code of Hammurabi grants Code of Laws or
Writing; Women's Suffrage notice; flavour messages on turns 2, 20, 79-85, 99. `D/default.lua` is a copy of the upstream
huts/partisans file.

Settings in `D/game.ruleset:3361-3455` that exist in 3.2 and civ45 leaves at default or sets differently: `techleak 25`,
`freecost 1`, `conquercost 0`, `diplbulbcost 0`, `diplgoldcost 5`, `contactturns 10`, `revolen 1`, `trademindist 15`,
`trade_revenue_style SIMPLE`, `borders SEE_INSIDE`, `airliftingstyle`, `autoattack`, `huts 10`, `barbarians DISABLED`, `animals 0`,
`globalwarming`/`nuclearwinter_percent`, spaceship travel. FCW-only (absent from `FC32/server/settings.c`): `blueprints`,
`casusbelliturns` (casus belli lasts 12 turns), `fulldisorder`, `hangry`, `killcitizen_pct`, `city_output_style`, `slot_control`,
`trademinforeign`, `universal_unload`, `unload_override`, `zoc_purity`, `move_bonus_in_frags`, `autoattack_style`,
`unitwaittime_style`, `ceasefirelength`, `armisticelength`, `latejoin_gold`, `hideouts`, `nukes_minor`/`major`, `polarstrip`.

## 5. Licence

The rulesets sit inside the Freeciv tree, whose `COPYING` is GPL-2 (`FCW/freeciv/freeciv/COPYING`), and the Lua files carry the
Freeciv GPL-2-or-later header (`D/script.lua:1-10`). Flags:
- The `.ruleset` files and changelogs carry no licence header, and the MP2 line is written by FCW contributors, not upstream.
- The repository's `FCW/LICENSE.txt` says the C server is GPL and the web client AGPL-3, without naming the data. GPL-2-or-later
  is the reasonable reading for rulesets, but it is not stated.
- `mpplus/DETAILS.mpplus.pdf` has no licence; author metadata only.
- READMEs link to Fandom wiki manuals (CC BY-SA); the web client's `freeciv-wiki-doc.js` holds Wikipedia-style unit summaries
  (CC BY-SA). Do not copy that text.
- AG says it imports ideas from later commercial games (`ag/README.ag`). Ideas are fine, but under our clean-room rule we should
  not lift its help text or names that come from Firaxis titles.
