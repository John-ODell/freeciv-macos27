> Research record of 2026-10-16, written before slice 1 (PR 47) changed civ45: its `civ45/` line numbers and
> "today" columns describe the one-unit-per-tile ruleset that is now civ54. Plan: `notes/freeciv45-plan.md`.

# Civ4 play in civ45: a design study for Freeciv 3.2

Date: 2026-10-16. Research and design only: nothing under `~/Desktop/freeciv-port` was changed.
This note extends `notes/civ45-planning.md` and does not repeat its Tier A/B/C rows.

Labels: **observed** (read at the cited place), **derived** (follows from observed facts),
**inferred** (plausible, not checked), **unknown**.
Paths: `up/` is `refs/freeciv-S3_2/` (3.2.6+, commit 44e6898c) and `civ45/` is `port/freeciv/data/civ45/`.
The fork is upstream plus two build commits and the two civ45 commits (observed, `git log` in
`port/freeciv`), so engine line numbers should match in both trees (inferred).
Civ4 behaviour comes only from public fan sites and Wikipedia, paraphrased and linked. No game files,
manuals, SDK or data tables were read or copied.

## Summary

- **Stacks back** is mostly deletion: nine enabler blocks in `civ45/actions.ruleset:2763-2901`, two unit
  flags with 23 uses, the Lua block `civ45/script.lua:531-741` and two texts. `effects.ruleset` and
  `luadata.txt` hold no 1UPT logic: the three `MaxUnitsOnTile` reqs in `effects.ruleset` are sandbox rules
  (observed), so that lead in the brief does not hold.
- **Killstack** is a server setting, default TRUE (`up/common/game.h:547`, lead confirmed), that a ruleset
  can set and lock in `[settings]`. civ45 does not set it, so today every stack outside a city dies with
  its defender (derived). One `[settings]` row turns it off.
- **Defender choice** already works the Civ4 way: the unit with the best odds against this attacker.
- **Collateral damage** does not exist (lead confirmed: outside the ChangeLog the only hit is the comment
  at `up/server/cityturn.c:3063`). The cheapest stand-in is "Bombard 2" for siege units, enabled only against
  stacks (Tier A). A faithful version is engine work in `do_attack()`.
- **First strikes** do not exist. `Combat_Rounds` (civ45: 15) is the only break-off, and the odds the AI
  uses ignore it.
- **Square map**: `topology ""` with civ45's `init_city_radius_sq = 5` gives exactly 21 tiles, the Civ4
  fat cross. The culture radius steps must go. `"ISO"` keeps the same rules with iso art; trident is the
  only overhead square tileset.
- **New systems**: luxury happiness, resource health, specialists, drafting, upgrade tweaks and cottages
  are Tier A; Great Generals, leader traits and upgrades in own territory are Tier B; whipping, culture and
  espionage rates, Civ4-style unhappiness, vassals and corporations need the engine.
- **Slices**: (1) stacks back, killstack off; (2) square map; (3) upgrades and drafting; (4) siege
  collateral and to-the-death combat; (5) luxury happiness and resource health; (6) cottages; (7) Great
  Generals; (8) leader traits.

## 1. Back to stacks

### 1.1 Every one-unit-per-tile site in civ45

"Today" is observed (grep and sed, 2026-10-16); "Change" is derived. "Sandbox" lines are in
`up/data/sandbox/actions.ruleset`.

| # | Place | Today | Change |
|---|---|---|---|
| 1 | `civ45/actions.ruleset:2863-2876` `[actionenabler_regular_move]`, req at 2875 | Comment 2863-2865; target req `MaxUnitsOnTile 0 Tile`: moves only into empty tiles | Delete comment and `target_reqs` (sandbox `:2817` has none) |
| 2 | `:2878-2887` `[actionenabler_regular_move_stacks_anywhere]` | StacksAnywhere units may move onto occupied tiles | Delete |
| 3 | `:2889-2901` `[actionenabler_regular_move_into_port]` | StacksInPort ships may enter occupied cities | Delete |
| 4 | `:2763-2775` `[actionenabler_disembark_from_native_tile]`, req at 2774 | Landing needs an empty tile | Delete comment and `target_reqs` (sandbox `:2763`) |
| 5 | `:2777-2785` its `_stacks_anywhere` twin | Exemption | Delete |
| 6 | `:2787-2799` `[actionenabler_disembark_from_native_city]`, req at 2798 | As 4 | As 4 (sandbox `:2772`) |
| 7 | `:2801-2809` twin | Exemption | Delete |
| 8 | `:2811-2824` `[actionenabler_disembark_from_non_native]`, req at 2823 | As 4, for "Transport Disembark 2" | As 4 (sandbox `:2781`) |
| 9 | `:2826-2835` twin | Exemption | Delete |
| 10 | `civ45/units.ruleset:54-55` flag definitions; 9 uses of StacksAnywhere (Fighter 1778 to AWACS 3125), 14 of StacksInPort (Trireme 1994 to Storm 3159) | Exemption flags | Delete definitions and all 23 uses |
| 11 | `civ45/script.lua:531-741` | Constants 555-556, helpers 563-712, `unit_built` handler 714-723, `turn_begin` sweep 725-741 | Delete; lines 1-529 are sandbox's script and stay |
| 12 | `civ45/game.ruleset:39-49` summary; `civ45/README.civ45:14-34` | Describe hex, 1UPT, culture radius, range-2 bombard | Rewrite for Civ4 |
| 13 | `civ45/game.ruleset:908-938` `[settings]` | No `killstack` row, so the default TRUE applies | Add `"killstack", FALSE, TRUE` (lock: open question 1) |
| keep | `civ45/actions.ruleset:1446,1675,1692,1710,1728` | "Conquer City" needs an empty city tile | Sandbox rule, not 1UPT: keep |
| keep | `civ45/effects.ruleset:214,2200,4240` | Barbarian leader escape, incite cost, bombard may not empty a city | Sandbox rules (same lines in `up/data/sandbox/effects.ruleset`): keep |
| none | `civ45/luadata.txt` | Sandbox turn messages; identical to sandbox's (`diff -q`) | Nothing |

Fork history: slice 1 is commit 0e5af48 and slice 2 is 7913d4b, and the fork has no tags (observed,
`git log`, `git tag`). Rows 2-11 came with slice 2 and row 1 with slice 1 (derived from
`notes/civ45-planning.md:95,121-134`), so reverting 7913d4b and then deleting row 1 by hand is the shortest
path (inferred). Tag 7913d4b first (say `civ45-1upt`) so civ54 can start from it; patches 0003 and 0004 keep
a copy too. Issues 30-32 (`notes/game-directions.md:29-30,65-66,93-94`) move to civ54 (inferred).

### 1.2 What the rules test needs instead

`scripts/civ45-rules-test.lua` tests 1UPT: it calls `civ45_turn_begin_callback` (`:46,106`), expects an
occupied city to refuse a Phalanx (`:87-89`) and reads both flags (`:110,119-120`) (observed). Every case
breaks or inverts after 1.1, so replace the file rather than patch it (derived). Proposed cases, all with
existing Lua calls:

| Case | How | Pass when |
|---|---|---|
| killstack off | `server.setting.get("killstack")` returns the value name (`up/server/scripting/api_server_base.c:112-127`; names `up/server/settings.c:629-636`, observed) | `"DISABLED"` |
| sweep gone | `civ45_turn_begin_callback == nil` | true |
| move onto a friend | Tester Phalanx: `perform_action(find.action("Unit Move"), t)` onto a tile holding a Tester unit | true; 2 units on `t` |
| enter an occupied city | old case at `:87-89`, inverted | true |
| stacks persist | 3 Tester units on one tile at turn 12, recount at turn 13. Tester is human with no client, so nothing moves them (derived) | 3 |
| killstack and defender in combat | A Phalanx and 2 Warriors for the Animal Kingdom (`up/data/nation/animals.ruleset:5`), which is at war with everyone (`up/server/animals.c:143` calls `barbarian_initial_wars`, `up/server/barbarian.c:765`), on free land next to a Tester Armor; `armor:perform_action(find.action("Attack"), t)` | Phalanx dead, both Warriors alive (killstack would leave none). `Combat_Rounds` 15 can end a fight undecided, so retry with a second Armor before failing |

`scripts/civ45-rules-test.sh` can stay: it loads the Lua in pregame, creates the human-controlled "Tester"
and fails on FAIL, SKIP or a Lua error (observed, `civ45-rules-test.sh:15-25,45-49`); only its header
comment changes. `scripts/check-stacking.py` exits 1 on any stack outside a city (`:84-85`, observed), which
is now the normal state: add a report-only mode (stacked tiles, largest stack, exit 0) and keep the old mode
for civ54; its `--ruleset` exemptions (`:38-50,71-72`) become no-ops (derived). For the AI, run
`scripts/test.sh --ruleset civ45 --no-client --turns 200` and compare with the slice 2 table
(`notes/civ45-planning.md:139-146`) plus the largest stack per save.

## 2. Civ4 stack combat

### 2.1 Killstack: where it is configured

- Engine default TRUE (`up/common/game.h:547`), applied at `up/common/game.c:280`; server setting at
  `up/server/settings.c:2428-2436`, class `SSET_RULES_SCENARIO`, so it can change until the game starts
  (`:3402-3420`); write access `ALLOW_BASIC` (`:2430`) (observed). Unlocked, any basic-access player can
  flip it in pregame (inferred from the access level).
- The ruleset can set it, so the answer is "both": every `GEN_BOOL` is `ruleset_settable` (`:1411-1418`),
  and `[settings]` rows are name, value, lock (`settings_ruleset()` `:4376-4447`, `setting_ruleset_one()`
  `:4455-4637`) (observed). Precedent: webperimental ships it disabled and unlocked
  (`up/data/webperimental/game.ruleset:724`, `README.webperimental:15`) and gates two enablers on it with a
  `ServerSetting` req (`up/data/webperimental/actions.ruleset:678,716`) (observed).
- A ruleset lock also beats saved games: `settings_game_load()` applies a saved value only if
  `setting_is_changeable()` allows it (`:4990-4995`), which refuses ruleset locks (`:3457-3486`) (observed).
- What it does: `is_stack_vulnerable()` is killstack AND no `NoStackDeath` extra AND no city
  (`up/common/combat.c:989-994`). `kill_unit()` then wipes every at-war unit on the tile that the killer
  could reach (`up/server/unittools.c:2259-2282`); `CanEscape` units may flee on a coin flip if they have
  more moves left than the killer, unless it has `CanKillEscaping` (`:2309-2343`) (observed). civ45 has no
  `NoStackDeath` extra and no `CanEscape` unit (only doc comments at `civ45/terrain.ruleset:1250` and
  `civ45/units.ruleset:424-431`, observed), so today a field stack dies whole (derived).
- Civ4: the stack survives when its top defender loses
  (https://forum.quartertothree.com/t/civ-4-combat-resolution/28489, observed), so `killstack` FALSE is the
  Civ4 rule (derived).
- AI: it prices risk through `is_stack_vulnerable()` (`up/ai/default/aitools.c:1307-1312` `stack_cost()`,
  `daimilitary.c:1277`, `daiunit.c:548`, `aiparatrooper.c:159`, `up/server/advisors/advgoto.c:479`,
  observed), so it should adapt to killstack off without code changes (inferred; long games unmeasured).

### 2.2 How Freeciv picks the defender

`get_defender()` (`up/common/combat.c:836-898`) looks at each unit that can defend here
(`up/common/movement.c:174-196`; a unit in a transport defends only as the transport's `tp_defense` allows)
and that this attacker may attack. It scores each as 100000 × (1 − attacker's win chance) and keeps the
best; ties go to the cheaper unit, then to the better defense rating (`:853-891`). A `GameLoss` unit
defends last unless the stack is vulnerable (`:868-873`) (observed). The win chance counts current hp and
firepower (`:332`, `:478-495`), so wounded units step back (derived). Civ4 also sends the unit with the
best odds against that attacker (quartertothree page above, observed). No change needed (derived).

### 2.3 Collateral damage

- `grep -rni collateral` over `up/server`, `up/common`, `up/ai` and `up/doc` finds one comment, in
  `uk_rem_gold_callback()` (`up/server/cityturn.c:3057-3065`), about units dying as side effects of
  actions; `up/ChangeLog-1.0-S3_0:26207-26251` uses the word for an upkeep bug. No mechanic exists
  (observed). The fork has the same single hit (`port/freeciv/server/cityturn.c:3063`, observed).
- Nearest form: the Bombard family. `unit_bombard()` (`up/server/unithand.c:4527-4631`) runs
  `unit_bombs_unit()` against every reachable unit on the tile (`:4545-4561`): `bombard_rate` rounds in
  which only the defender can lose hp (`up/server/unittools.c:356-401`, rate `:361`, loop `:381-384`).
  Plain Bombard leaves at least 1 hp (`:387-392`); "Bombard Lethal" may kill
  (`up/doc/README.actions:774-828`) (observed).
- civ45 enables only plain "Bombard", for units flagged `Bombarder` (`civ45/actions.ruleset:1202-1264`):
  Bomber, Helicopter and Stealth Bomber (`bombard_rate` 3, 2, 4 at `civ45/units.ruleset:1835,1884,1962`).
  It has no "Bombard 2-4" or "Bombard Lethal" enablers, and Catapult, Cannon, Artillery and Howitzer only
  attack (observed).
- Civ4: a siege attack also damages several other units on the defending tile and never kills with that
  damage (https://forums.civfanatics.com/threads/what-is-collateral-damage.195680, observed); a per-unit
  damage limit and siege immunity exist (inferred: search summary of
  https://civfanatics.com/civ4/civilopedia/units/).

### 2.4 First strikes and withdrawal

Civ4 fights in rounds; first strikes are rounds a unit can win without risk; withdrawal lets an attacker
escape when it would die
(https://apolyton.net/forum/civilization-iv/civilization-iv-general/155903-the-civ-iv-combat-system, observed).

| Civ4 idea | Freeciv analogue | Gap | Label |
|---|---|---|---|
| Rounds, odds by strength | `unit_versus_unit()`: each round the attacker wins with p = A/(A+D); the loser loses the winner's firepower in hp (`up/server/unittools.c:288-340`) | Same model | observed |
| First strikes | None: every round can hurt either side (`:330-340`) | Engine: free rounds per unit type, plus AI odds | observed absence |
| Withdrawal | `Combat_Rounds` caps rounds and at the cap both live (`:329-333`; `up/doc/README.effects:324-326`). It is read for the attacker, so reqs can make it per type, class or flag. civ45 sets 15 for all (`civ45/effects.ruleset:544-546`) | A fixed cap, not "escape at death"; `win_chance()` has no rounds parameter (`up/common/combat.c:332`), so AI odds and defender choice ignore it | observed; gap derived |
| Promotions such as "+% against mounted" | `Attack_Bonus` (attacker reqs, can be per action) and `Defend_Bonus` (reqs on the attacking type) (`up/doc/README.effects:216-219,332-335`); linear veteran levels (`civ45/units.ruleset:82`) | No per-unit choice (planning Tier C row) | observed |
| Hit points, firepower | Unit fields; `CityBuster`, `BadCityDefender` and low-firepower rules adjust firepower (`up/common/combat.c:409-476`) | None | observed |

Civ4 feel in Tier A: base `Combat_Rounds` 0 (to the death) plus, for a new `Withdraws` flag, a positive cap
such as 8, so fast units break off (derived; numbers are placeholders).

### 2.5 Cheapest route to collateral damage

| Route | How | Fidelity | AI | Cost |
|---|---|---|---|---|
| A. Ruleset: siege "Bombard 2" against stacks | New unit flag `Collateral` and a `bombard_rate` on the four siege units; enablers for "Bombard 2" copying civ45's Bombard actor reqs (`civ45/actions.ruleset:1202-1264`) with flag `Collateral`, plus target req `"MaxUnitsOnTile", "1", "Tile", FALSE` (two or more units). Range is already 1 (`:171`); add "Bombard 2" to `attack_actions` (`:36-37`) | Hits every unit, never kills (1 hp floor). The siege unit takes no damage and does not also fight the top defender, unlike Civ4; no per-type limit | `dai_unit_attack()` tries Bombard 2 before Attack whenever it is enabled (`up/ai/default/aitools.c:835-880`, observed); the two-unit req keeps siege attacking lone defenders (derived) | S |
| B. Lua after an attack | Remember the attacker in `action_started_unit_units` (`up/server/scripting/script_server.c:538`); in `action_finished_unit_units` (`:542`, emitted by `ACTION_PERFORM_UNIT_UNITS`, `up/server/unithand.c:3535`) call `edit.unit_add_hitpoints(u, -k)` (`up/server/scripting/tolua_server.pkg:135-137`) on up to N enemy units | Lua cannot read hp (Unit fields, `up/common/scriptcore/tolua_game.pkg:58-67`), and a result ≤ 0 wipes the unit (`up/server/scripting/api_server_edit.c:592-598`), so it can kill, unlike Civ4 | Unaware | S-M |
| C. Engine | After `unit_versus_unit()` in `do_attack()` (`up/server/unithand.c:4964`), loop over the other units as `unit_bombard()` does (`:4545-4615`), with new unit-type fields (count, damage, floor %) loaded in `server/ruleset.c` and sent in `common/networking/packets.def` (protocol change); AI: count it in attack want and `stack_cost()` | Full | Needs AI work | M, plus AI M (civ54 or upstream) |

Recommendation: A in civ45 now, C in civ54 (inferred). Not checked: whether a bombard spends all of the
unit's moves, which decides whether one unit can bombard and attack in the same turn (unknown).

## 3. Map

### 3.1 civ45 today

`"topology", "ISO|HEX"` and `"wrap", "WRAPX|WRAPY"`, both unlocked (`civ45/game.ruleset:915,917`);
`init_city_radius_sq = 5` (`:108`) and `init_vis_radius_sq = 5` (`:111`); culture adds 4 at 300 points
and 4 more at 1500 (`civ45/effects.ruleset:5442-5459`) (observed). On hex that is 19, then 37, then 37
tiles: the second step adds nothing, and the comment "Base radius_sq is 5 (21 tiles)" (`:5443`) is true
only on a square map (derived, table below).

### 3.2 Square, non-iso, 8 directions, 21-tile radius

Only HEX removes two of the eight directions (`up/common/map.c:1245-1259`). On square maps, with or
without ISO, the squared distance is dx² + dy²; on hex it is the hex distance squared (`:614-625`). A city
works the tiles with dx² + dy² ≤ radius_sq (`up/common/city.h:81`) (observed). ISO only changes how
native coordinates map to map coordinates (`up/common/map.h:42,165-185`), so `""` and `"ISO"` give
identical game rules (derived).

| radius_sq | 2 | 4 | 5 | 8 | 9 | 10 | 13 | 17 |
|---|---|---|---|---|---|---|---|---|
| Square tiles | 9 | 13 | **21** | 25 | 29 | 37 | 45 | 57 |
| Hex tiles | 7 | 19 | 19 | 19 | 37 | 37 | 37 | 61 |

The table is derived: tiles counted with the two distance rules. Civ4's work area is a fixed 21-tile fat
cross (https://apolyton.net/forum/civilization-iv/civilization-iv-general/156369-fat-cross-questions,
observed). So:

- Set `"topology", ""` in `[settings]` and keep `init_city_radius_sq = 5` (derived).
- Delete the two culture radius effects; on square they would make 29 and then 45 tiles (derived). The
  Space Elevator radius effects (`civ45/effects.ruleset:411-455`) come from sandbox (open question 11).
- Borders: radius_sq is `radius_sq_city` 5 plus city size × `size_effect` 1 (`civ45/game.ruleset:303,306`;
  `up/common/borders.c:44-49`); strength is (size + 2) × `Border_Strength_Pct` (`:80-82`) (observed). No
  effect changes the radius, so planning's row "Borders that grow with culture"
  (`notes/civ45-planning.md:34`) only holds for contested tiles (derived). Civ4-style culture rings need an
  engine effect (4.3).
- Vision radius_sq 5 becomes the same 21 tiles (derived). `citymindist` 3 (`civ45/game.ruleset:922`)
  should be rechecked on the new grid (inferred).

### 3.3 Settings, locks and scenarios

`topology` is `SSET_MAP_SIZE` (`up/server/settings.c:1557-1586`), changeable only while the map is empty
(`:3390-3400`) (observed). The ruleset row sets the default when civ45 loads; unlocked, players can still
pick hex in pregame (derived). Scenarios carry their own map and settings: `up/data/scenarios/earth-small.sav`
has `"topology",""` at `:121`, `ruleset_locked=FALSE` at `:13` and `rulesetdir="classic"` at `:22`
(observed). Because a ruleset lock beats a saved value (2.1), what a locked civ45 topology does to a
scenario map made for another topology is unknown; leave topology unlocked (inferred).

### 3.4 Tilesets

trident is the only overhead square tileset (`up/data/trident.tilespec`: `type = "overhead"`, `is_hex =
FALSE` at `:34`); hex2t is overhead hex; amplio, amplio2, cimpletoon and isotrident are iso square; alio,
hexemplio, isophex and toonhex are hex (observed: `type` and `is_hex` in each tilespec). An iso square
tileset on a non-iso map is only a soft mismatch (`up/client/mapview_common.c:4091-4096`), and the client
takes its "Tileset (Square)" option for both `""` and ISO (`up/client/options.c:6585-6593`) (observed), so
an amplio2 user keeps amplio2 on the new map (derived; the look is unverified). Setting
`[tileset] preferred = "trident"` (`civ45/game.ruleset:65-68`, now commented out) makes the client load
trident or offer it, depending on the player's auto-accept option (`up/client/packhand.c:3463-3472`, observed).

## 4. Civ4 systems not yet in civ45-planning.md

Effort: S ≤ 1 day, M 2-4 days, L ≥ 1 week, each with its test (inferred). "AI" says whether the default
AI can use the result. Civ4 descriptions paraphrase the numbered sources (observed unless marked).

### 4.1 Tier A additions (ruleset only)

| Civ4 system | civ45 mechanism | Effort | AI | Citations | Label |
|---|---|---|---|---|---|
| Happiness cap and luxuries: a base number of content citizens, +1 per connected luxury; extra citizens are unhappy and idle [1] | `City_Unhappy_Size` is the cap (civ45: 4). One `Make_Content` +1 effect per luxury extra with req `Extra <name> City`; `Traderoute` range stands in for "connected". City range counts every tile in the radius, worked or not, owned or not | S | Values `Make_Content` | `civ45/effects.ruleset:167-169`; `up/doc/README.effects:70,308,453`; `up/common/requirements.c:2837-2873`; `up/ai/default/daieffects.c:238` | observed; mapping derived |
| Health from resources: unhealthiness above health costs food; food resources add health [2] | Plague is on (`civ45/game.ruleset:207-219`). Per food resource: `Health_Pct` (less plague) and `Size_Adj` (higher size cap) with `Extra <name> City`. A food malus through negative `Output_Bonus` at large sizes is possible but untested | S | Values `Health_Pct` (illness is on) and `Size_Adj` | `up/doc/README.effects:403,543,638`; `daieffects.c:308-312,393` | observed; malus inferred |
| Specialists: several kinds, each feeding one great-person type [3]; building-gated slots (inferred, search summary) | New `[specialist_*]` with reqs (e.g. a Building) and `Specialist_Output`, up to 20 kinds. Not expressible: culture (outputs are food, shield, trade, gold, luxury, science), great-person points, slots per building. The `Specialist` req is Local only, so city effects cannot count specialists | S | CM handles any specialist; `Specialist_Output` valued | `civ45/cities.ruleset:47,64,79`; `up/common/fc_types.h:103,411`; `up/doc/README.effects:92,650`; `up/common/aicore/cm.c:165-173`; `daieffects.c:196` | observed; slots inferred |
| Drafting: a civic turns population into a unit at once, with temporary anger and a per-turn limit [4] | Draft unit types with `pop_cost` 1 and a government in `build_reqs`, cheap through `Unit_Build_Cost_Pct`; still one turn to build or gold to buy. Anger: 4.2 | S | Checks city size against `pop_cost` | `civ45/units.ruleset:272`; `up/doc/README.effects:731`; `up/ai/default/daicity.c:610-611,712-732` | observed; fit derived |
| Upgrades keep promotions (inferred, search summary only) | `upgrade_veteran_loss` and `autoupgrade_veteran_loss` from 1 to 0; price through `Upgrade_Price_Pct`. "Upgrade Unit" still needs a domestic city on the same tile and an `obsolete_by` type | S | Upgrades in cities; values `Upgrade_Price_Pct` | `civ45/game.ruleset:122,125`; `civ45/effects.ruleset:548-553`; `up/doc/README.actions:504-515`; `daicity.c:381`; `daieffects.c:570` | observed |
| Resource-gated units and the Civ4 resource set | Already Tier A (`notes/civ45-planning.md:38`). Add `Traderoute` range for "connected" and the missing resources (civ45's 20 resource extras have no Horse, Copper, Stone, Marble, Aluminium or Uranium), reusing sprites through `graphic_alt` | S-M | Builds only what its cities may build (inferred) | `civ45/terrain.ruleset:2027-2294`; `civ45/units.ruleset:871,1558` | observed; AI inferred |
| Cottages: Cottage, Hamlet, Village, Town grow only while worked; pillage sets them back [5] | Four extras. Each next stage has `appearance_reqs` "previous stage on the tile" and `CityTile Worked`; the previous stage disappears (chance 10000) once the next exists. Disappearance runs before appearance each turn, so yields (`Output_Add_Tile`, trade) need "next stage absent" reqs for the one-turn overlap. Growth is random (mean 10000/chance turns), not a fixed count; pillage removes a stage outright (inferred). Lua cannot do better: it has no "tile is worked" call | M | Workers see the yield, not the growth (inferred) | `up/server/srv_main.c:1705-1760`; `up/common/extras.c:1122-1144`; `up/doc/README.effects:128-129,540`; precedent `civ45/terrain.ruleset:1480-1508`; `up/common/scriptcore/tolua_game.pkg:358-415` | observed parts; design derived; art unknown |
| Culture slider [6] | A multiplier "Arts funding" whose steps scale `History` up and science `Output_Bonus` down, as goldkeep's policies scale effects; civ45 already has five sandbox multipliers | S | Hill-climbs multipliers | `civ45/governments.ruleset:470-522`; `up/data/goldkeep/governments.ruleset:246`; `up/data/goldkeep/effects.ruleset:441-455`; `up/ai/default/daidata.c:442-512` | observed precedent; fit derived |
| Collateral; to-the-death combat with withdrawal | 2.5 route A; 2.4 | S-M | See 2.5 | above | derived |

[1] https://civfanatics.com/civ4/strategy/empire-management/ways-into-happiness/
[2] https://civfanatics.com/civ4/strategy/empire-management/ways-into-health/
[3] https://civfanatics.com/civ4/strategy/game-mechanics/great-people-points-explained/
[4] https://civfanatics.com/civ4/strategy/military/drafting-for-fun-and-profit/
[5] https://forums.civfanatics.com/threads/cottages.346384
[6] https://apolyton.net/forum/civilization-iv/civilization-iv-general/216337-the-culture-slider

### 4.2 Tier B additions (ruleset plus Lua)

civ45 already uses User Actions 1 and 2 (`civ45/actions.ruleset:473-484`; handlers `civ45/script.lua:475,522`),
so only 3 and 4 are free (observed). Lua saves only scalar globals across saves, not tables
(`up/common/scriptcore/tolua_common_a.pkg:137-170`), so per-player or per-city state needs one global per
id (observed; consequence derived). The AI scores ruleset-defined actions as 0, "We have no idea what they
do" (`up/ai/default/daicity.c:1275-1277`), so it will not use the User Actions below (inferred).

| Civ4 system | Mechanism | Effort | AI | Citations | Label |
|---|---|---|---|---|---|
| Great Generals: combat experience fills a pool that yields a general, who joins a unit, settles in a city or founds a Military Academy [7] | Count each player's attacks in `action_finished_unit_units` and losses in `unit_lost` (which has no killer argument) in scalar globals; at a rising threshold `edit.create_unit` a General. User Action 3 (handled in `action_started_unit_self`): raise every unit on the tile one veteran level with `Unit:transform(unit.utype, -1)`, which clamps at the top level, or in a city `edit.create_building` a Military Academy with `Veteran_Build` | M | No | `up/server/scripting/script_server.c:507,538,542,570`; `up/server/scripting/tolua_server.pkg:119,149-150,571-572`; `up/server/scripting/api_server_edit.c:71-91`; `up/doc/README.effects:789` | observed API; design derived; target kind "self" for a User Action inferred |
| Leader traits: each leader has traits that grant bonuses [8]; two per leader (inferred, [9]) | No `Trait` req exists; Freeciv's four nation traits only steer the AI. Route 1 (Tier A): trait effects with `NationGroup` reqs; groups live in the shared nation list and nation files, so civ45 needs its own nation list (570 includes), as alien has. Route 2 (Tier B): when a player founds its first city (`city_built`), Lua adds a hidden small wonder carrying the trait's effects | M | Gets the effects; never "chooses" a trait | `up/common/traits.h:21-29`; `up/doc/README.effects:79-80`; `up/data/default/nationlist.ruleset:59`; `up/data/nation/french.ruleset:7`; `up/data/alien/nations.ruleset:103`; `script_server.c:444` | observed; route 1 derived, route 2 inferred |
| Upgrade anywhere in own territory, for gold, with the resource [10] | User Action 4 with actor reqs `CityTile Claimed Tile` and `DiplRelTile Foreign Local FALSE` (tile is ours). Handler: `Unit:upgrade(0)`, which charges nothing, then `edit.change_gold(owner, -price)` with a price computed in Lua from `Unit_Type:build_shield_cost()` | M | No; it still upgrades in cities | `up/doc/README.effects:128-130,844,873-877`; `api_server_edit.c:535-547`; `tolua_server.pkg:176`; `tolua_game.pkg:479` | observed API; reqs inferred |
| Draft anger | On `unit_built` of a draft unit, add a hidden building with `Make_Content` -1 and a per-city global holding the turn; remove it N turns later | S | Sees the malus | `script_server.c:456`; `tolua_server.pkg:149-152` | derived |
| Corporations: founded with a great person and a tech, spread by executives, consume resources, pay the headquarters [11] | Executive unit plus a User Action that adds a hidden branch building with resource-keyed effects; Lua pays the HQ owner each turn. Needs a fifth User Action or dropping a sandbox one | M-L | No | `tolua_server.pkg:149-150,176` | inferred |
| Vassals: the master decides war and peace and gets tribute [12] | Only a shadow: an alliance plus a Lua flag and tribute through `edit.change_gold`; no master-vassal state, and the AI ignores it. The real thing stays Tier C (`notes/civ45-planning.md:77`) | M | No | `tolua_server.pkg:176` | inferred |

[7] https://apolyton.net/articles/civilization-news/civ4/p-reviews-ac/9313015-civilization-iv-warlords-review-by-solver/contentpage3
[8] https://civfanatics.com/civ4/strategy/introductory/analysis-of-the-civilization-traits/
[9] https://apolyton.net/forum/civilization-iv/civilization-iv-general/189756-leader-traits
[10] https://apolyton.net/forum/civilization-iv/civilization-iv-general/205404-how-do-you-upgrade-your-units
[11] https://en.wikipedia.org/wiki/Civilization_IV:_Beyond_the_Sword
[12] https://civfanatics.com/civ4/strategy/game-mechanics/explaining-the-vassal-system/

### 4.3 Tier C additions (engine)

| Civ4 system | Why the engine is in the way | Effort | Citations | Label |
|---|---|---|---|---|
| Whipping: under Slavery, population finishes production, with anger [13] | Buying is gold only (`really_handle_city_buy()`); Lua can read a city's size but cannot change it or the shield stock. A pop-cost "labour" unit disbanded into production is a poor stand-in ("Disband Unit Recover" adds half its shields) | M plus AI | `up/server/cityhand.c:294-360` (cost at `:328`); `tolua_game.pkg:264-265`; `up/doc/README.actions:476` | observed absence |
| Culture and espionage rates; espionage points per rival [6] [11] | Rates are tax, luxury and science only (`struct player_economic`); a fourth rate touches player data, packets, the tax dialog and the AI. Proxies: the multiplier in 4.1, and one scaling `Action_Odds_Pct` and `Spy_Resistant`, which the building AI does not value | L | `up/common/player.h:60-66`; `up/doc/README.effects:165,480,654`; `daieffects.c:578,607` | observed; proxy derived |
| True collateral; first strikes | 2.5 route C; 2.4 | M each plus AI | above | derived |
| Civ4 unhappiness: unhappy citizens idle and the city keeps working [1] | Freeciv riots when happy citizens are fewer than unhappy plus twice angry (`city_unhappy()`); the ruleset cannot change that | M-L | `up/common/city.c:1626-1631` | observed; impact inferred |
| Culture-driven border rings | The border radius reads only settings and city size; a new effect in `tile_border_source_radius_sq()` is small and general (upstream candidate) | S-M | `up/common/borders.c:33-63` | observed; proposal inferred |
| Lua gaps: read unit hp; set city size and shield stock; "tile is worked" | Each would make a Tier B item exact (collateral route B, whipping, cottages); small and general (upstream candidates) | S each | `tolua_game.pkg:58-67,358-415`; `tolua_server.pkg:117-254` | observed absence |

[13] https://forums.civfanatics.com/threads/question-about-whipping.188268

## 5. Slice plan

Each slice is one issue, branch, PR and fork patch, as slices 1 and 2 were (PRs 24 and 29, patches 0003
and 0004; observed in `notes/game-directions.md:16` and `patches/`), with the rules test extended and a
200-turn autogame. Smallest first.

| # | Slice | Main changes | Test | Effort | Main risk |
|---|---|---|---|---|---|
| 1 | Stacks back, killstack off | 1.1 rows 1-13; tag the 1UPT commit | 1.2 cases; check-stacking report mode; autogame against the slice 2 numbers | S | Doom stacks with no counter until slice 4; AI wars past turn 100 unmeasured |
| 2 | Square map, fixed fat cross | `topology ""` (unlocked), `[tileset] preferred = "trident"`, culture radius effects deleted, texts | `server.setting.get("topology") == ""` (`up/server/settings.c:4145-4154` yields "" when no flag is set); `City:map_sq_radius()` 5 and 21 tiles from `circle_iterate(5)`; after `edit.add_city_history(c, 2000)` (`tolua_server.pkg:241`), `effects.city_bonus(c, "City_Radius_Sq")` is 0 | S | Art (trident looks dated; amplio2 draws iso on a flat map); AI city spacing on the new grid |
| 3 | Upgrades and drafting | Veteran loss 0; one draft unit per era with `pop_cost` 1 behind a government | "Upgrade Unit" in a city keeps `unit.veteran`; a built draft unit lowers `city:size()` by 1 | S | The AI drafts its cities small |
| 4 | Siege collateral, to-the-death combat | 2.5 route A; `Combat_Rounds` 0 plus a `Withdraws` cap | "Bombard 2" on a 3-unit animal stack leaves 3 alive and is refused against a lone unit; `effects.unit_bonus(u, p, "Combat_Rounds")` is 0, or the cap for `Withdraws` | S-M | AI siege bombards instead of taking cities; tuning `bombard_rate` |
| 5 | Luxury happiness, resource health | 4.1 rows 1-2 | `edit.create_extra` a luxury in a city radius; `effects.city_bonus(c, "Make_Content")` rises by 1; same for `Health_Pct` and `Size_Adj` | S-M | Balance: resources count anywhere in the radius |
| 6 | Cottages | 4.1 cottage row | 10 Cottages on worked tiles at turn 12: at least one Hamlet by turn 40, never both stages for two turns; `effects.tile_bonus(t, c, "trade", "Output_Add_Tile")` per stage | M | Random growth; workers or the AI replacing cottages; sprites |
| 7 | Great Generals | 4.2 row 1 | Attacks on animals until a General appears (test lowers the threshold global); User Action 3 raises `unit.veteran` of stacked units by 1 | M | The AI never uses it; counting is approximate |
| 8 | Leader traits | 4.2 row 2, route 2 first | `effects.player_bonus(p, ...)` matches each player's trait | M | Choosing traits per nation; nation list upkeep |

The test hooks are observed: `effects.*_bonus` (`tolua_game.pkg:639-651`), `City:map_sq_radius()`
(`:272-273`), `Unit.veteran` (`:58-67`), `edit.create_extra` (`tolua_server.pkg:156-157`). Move slice 4 up
if slice 1's autogame shows runaway stacks (inferred). Engine items (4.3, route C) go to civ54 or upstream.

## Open questions

1. Lock `killstack` FALSE so nobody can turn it back on, or leave it adjustable as webperimental does?
2. Keep hex as a pregame choice (topology unlocked), or lock square?
3. `""` with trident or `"ISO"` with amplio2 (same rules, different look)? Keep `WRAPX|WRAPY`?
4. Bombard range 2 (`civ45/actions.ruleset:164`) was for Civ5 ranged units: back to 1?
5. What happens when a scenario's topology differs from a locked ruleset topology? Unknown; test before
   locking anything map-related.
6. Traits: which nations get which traits, and is route 2 (a Lua hidden wonder) acceptable as a start?
7. How should the AI be judged with killstack off over 200+ turns: largest stack, battles per turn, cities
   taken?
8. Engine items: civ54 only, or offer the general ones (border effect, Lua hp read, collateral fields)
   upstream?
9. "Promotions kept on upgrade" in Civ4 rests on a search summary; confirm from another public description.
10. Does a bombard spend all of the unit's moves? Not checked; it decides bombard-then-attack in one turn.
11. Keep sandbox's Space Elevator radius bonus on a square map?
12. Keep `Combat_Rounds` 15 (sandbox) or go to the death as Civ4 does (2.4)?
