# Freeciv45 unit roster and upgrade chains: implementation-ready design

Date: 2026-10-17. Status: design for roadmap slice 10 (roster) and the parts of slice 3 (upgrades) it fixes.
Labels: observed, derived, inferred, unverified. Paths as in `victory.md`: `up/` is `refs/freeciv-S3_2/`,
`civ45/` is `port/freeciv/data/civ45/` at fork commit f55003f. Spec: `notes/freeciv45/mechanics.md` 2.5 (one
strength), 2.7 (experience), 2.8 (roster shape). Feasibility: `notes/freeciv45/in-freeciv.md` 2.4 (bonuses and
`Combat_Rounds`) and 4.1 (upgrades keep veterancy, resource gating). Plan decisions 2 and 7 in
`notes/freeciv45-plan.md`. Tech names marked † are new and defined in `tech-tree.md`; the others are civ45's.

## 1. Rules the whole roster follows

| Rule | Freeciv form | Where (observed) |
|---|---|---|
| One strength S per unit | `attack = S`, `defense = S` in every `[unit_*]`; the strength share decides each round (`unit_versus_unit()`) | `up/server/unittools.c:288-340`; decision 7 |
| Defence-only units | `attack = 0`, the one exception to the rule (Machine Gunners, Air Defence Infantry, Radar Plane, transports) | `civ45/units.ruleset:2399` (Carrier today) |
| Hit points | 10 for eras I-III, 20 for IV-VI, 30 for armour, capital ships and era VII; `firepower = 1` throughout. Each round the loser loses the winner's firepower in hit points, so hit points set how long a fight lasts, not who wins | `up/server/unittools.c:330-340`; civ45 already uses 10/20/30 |
| Fights to the death, fast units break off | `Combat_Rounds` 0 base and a cap for the `Withdraws` flag (slice 2, issue 75) | `up/doc/README.effects:324-326` |
| Siege wounds stacks | `Collateral` flag and `bombard_rate` (slice 2) | `up/doc/README.actions:774-828` |
| Counter "+N% against class Y" on unit X | Two `bonuses` rows, both on X and both keyed on Y's flag: `"<Y flag>", "DefenseMultiplierPct", N` (when Y attacks X: the defender's rows are read against the attacker's flags) and `"<Y flag>", "DefenseDividerPct", N` (when X attacks Y: the attacker's rows are read against the defender's flags, `up/common/combat.c:681-684`). Corrected 2026-10-17 (issue 111): the first draft put the divider row on every Y unit keyed on an X flag, which the server reads the other way round, so it cancelled the multiplier; the rules test caught it (Pikemen won 8 of 20 fights against War Elephants instead of about 16). No counter flags are needed, only the eight class flags | `up/common/unittype.h:451-463`; `up/common/combat.c:645-690`, `up/common/unittype.c:2821-2824`; `civ45/units.ruleset:345-366` (the type list) |
| City attack "+N% against cities" | One `Attack_Bonus` effect per flag with reqs `UnitFlag <flag> Local` and `CityTile Center Tile`: the effect is evaluated with the attacker as the unit and the defender's tile as the tile | `up/common/combat.c:610-633` |
| City defence "+N% in cities" for a class | `Fortify_Defense_Bonus` with reqs `UnitFlag <flag> Local` and `CityTile Center Tile`: its unit reqs are the defender | `up/doc/README.effects:366-369`; precedent `civ45/effects.ruleset:344-353` |
| Walls and gunpowder | `Defend_Bonus` reqs apply to the attacking type, so walls are worth +100% against `Melee`, `Archer`, `Mounted`, `Siege` attackers and nothing against `Gun` and later (change the `UnitClassFlag Ground` req at `civ45/effects.ruleset:2120-2127` to a list of `UnitFlag` reqs) | `up/doc/README.effects:332-335` |
| Resource gating | Until slice 4 lands: `"Extra", "<name>", "City"` in `reqs`, as Legion does today; after slice 4: `"Building", "<name> supply", "Player"`, the marker small wonder Lua keeps. The resource column below names the resource; the slice writes whichever form is current | `civ45/units.ruleset:871`; roadmap row 4 |
| Unit flags added | `Melee`, `Archer`, `Mounted`, `Gun`, `Siege`, `Armour`, `Naval`, `Recon`: 8 more of the 50 user flags (24 used at f55003f, 26 with slice 2's `Collateral` and `Withdraws`) | `civ45/units.ruleset:28-55` |
| Veteran levels kept | green, veteran, hardened, elite at 100/150/175/200% stay; `upgrade_veteran_loss` and `autoupgrade_veteran_loss` go from 1 to 0 (slice 3) | `civ45/units.ruleset:80-98`; `civ45/game.ruleset:125,128` |
| Classes kept | Land, Small Land, Big Land, Merchant, Sea, Trireme, Helicopter, Air, Missile; no new class | `civ45/units.ruleset:159-235` |

### Upgrade price

`unit_upgrade_price()` charges `2 * missing + missing² / 20`, where `missing` is the new unit's cost minus the old
unit's shield value, then applies `Upgrade_Price_Pct` (`up/common/unittype.c:1731-1746`, observed). civ45 halves
the old unit's shield value for the price (`Unit_Shield_Value_Pct` -50 with an `Action Upgrade Unit` req) and
halves the whole price after Invention (`Upgrade_Price_Pct` -50) (`civ45/effects.ruleset:548-553` and the
`unit_shield_value_in_upgrade_price_calc` effect, observed). Keep both. Worked examples (derived):

| From → to | Costs | missing | Price before Invention | After |
|---|---|---|---|---|
| Spearmen → Pikemen | 20 → 45 | 35 | 131 | 65 |
| Musketeers → Riflemen | 60 → 90 | 60 | 300 | 150 |
| Cavalry → Armoured Cars | 100 → 100 | 50 | 225 | 112 |

The quadratic term makes skipping an era expensive (Spearmen → Infantry would be 110 missing, 825 gold), which
is the intent: upgrade every era or rebuild. "Upgrade Unit" still needs a domestic city on the unit's tile
(`up/doc/README.actions:504-515`); upgrading in the field is in-freeciv.md 4.2 (User Action 4) and not in this
roster.

## 2. The roster by era

Columns: S strength, M moves, C shield cost, HP hit points. "Counters" lists the `bonuses` rows in words; the
flag in brackets after the class is the unit's own class flag. Status: stay (name and role as today), rename
(today's name in brackets), new. Costs and strengths are Freeciv45's own numbers chosen for the curve in
section 3.

### Era I, Ancient (HP 10)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Warriors | Land [Melee] | none | 1 | 1 | 10 | | `FirstBuild`, `DefendOk` | Swordsmen | stay |
| Scout | Small Land [Recon] | Hunting† | 1 | 2 | 15 | | `NonMil`, `IgTer`, `Explorer`, vision 5; cannot attack | Explorer | new |
| Spearmen | Land [Melee] | Bronze Working | 2 | 1 | 20 | | +100% vs Mounted; `DefendGood` | Pikemen | rename (Phalanx) |
| Axemen | Land [Melee] | Bronze Working | 3 | 1 | 25 | Copper | +50% vs Melee | Macebearers | new |
| Archers | Land [Archer] | Archery† | 3 | 1 | 25 | | +50% in cities (Fortify_Defense_Bonus); `Hut` | Longbowmen | stay |
| Horsemen | Land [Mounted] | Horseback Riding | 2 | 2 | 20 | Horses | `Withdraws`; +50% vs Siege | Horse Bowmen | stay |
| Chariot | Big Land [Mounted] | The Wheel | 4 | 2 | 30 | Horses | `Withdraws`; -50% vs Spearmen (takes the Melee divider); cannot enter hills or forest (`move_type` terrain costs as today) | Knights | stay |
| Trireme | Trireme [Naval] | Map Making | 1 | 3 | 25 | | cargo 2 Land/Small Land, coast only; `Ferryboat` | Galleon | stay |
| Settlers | Small Land | none | 0 | 1 | 30 | | pop 2 as today | none | stay |
| Workers | Small Land | none | 0 | 1 | 20 | | | Engineers | stay |
| Migrants | Small Land | Pottery | 0 | 1 | 10 | | pop 1, sandbox migration unit | none | stay |
| Levy | Land [Melee] | Bronze Working | 2 | 1 | 10 | | draft unit for eras I-III: `pop_cost 1`, a government in `build_reqs` (slice 3) | none | new |

Rule of thumb: Axemen beat Spearmen and Warriors, Spearmen beat Horsemen and Chariots, Chariots beat Archers and
Axemen in the open. A city with Archers behind walls holds against anything of its era (derived).

### Era II, Classical (HP 10)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Swordsmen | Land [Melee] | Iron Working | 6 | 1 | 40 | Iron | +25% vs cities (Attack_Bonus); `Marines` flag dropped | Macebearers | rename (Legion) |
| Horse Bowmen | Land [Mounted] | Archery† + Horseback Riding | 5 | 2 | 40 | Horses | `Withdraws`; +50% vs Siege | Knights | new |
| War Elephants | Big Land [Mounted] | Horseback Riding | 8 | 1 | 50 | Ivory | +50% vs Mounted; no `Withdraws` | Dragoons | rename (Elephants) |
| Catapult | Big Land [Siege] | Mathematics | 5 | 1 | 40 | | `Collateral`, `bombard_rate` 5; +50% vs cities; -50% defence vs Mounted | Trebuchet | stay |
| War Galley | Trireme [Naval] | Seafaring | 3 | 3 | 35 | | no cargo, coast only; `Hunter` | Frigate | new |
| Caravan | Merchant | Trade | 0 | 1 | 50 | | `TradeRoute`, `HelpWonder` | Freight | stay |
| Diplomat | Small Land | Writing | 0 | 2 | 30 | | | Spy | stay |

### Era III, Medieval (HP 10)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Macebearers | Land [Melee] | Machinery† | 8 | 1 | 55 | Iron | +50% vs Melee | Grenadiers | new |
| Pikemen | Land [Melee] | Feudalism | 6 | 1 | 45 | | +100% vs Mounted; `DefendGood` | Musketeers | stay |
| Longbowmen | Land [Archer] | Feudalism | 6 | 1 | 45 | | +50% in cities; +25% on hills (`Defend_Bonus` cannot do this per defender; use `Fortify_Defense_Bonus` with a `Terrain Hills Tile` req, inferred) | Riflemen | new |
| Crossbowmen | Land [Archer] | Machinery† | 6 | 1 | 50 | Iron | +50% vs Melee | Riflemen | new |
| Knights | Land [Mounted] | Chivalry | 10 | 2 | 70 | Horses, Iron | `Withdraws`; +50% vs Siege | Dragoons | stay |
| Zealots | Land [Mounted] | Monotheism | 8 | 2 | 50 | Horses | `Withdraws`; +50% vs Siege; no armour, so no Iron: the cheap rider of the era (civ45's Crusaders under a nation-neutral name) | Knights | back, John 2026-10-17 |
| Trebuchet | Big Land [Siege] | Machinery† | 4 | 1 | 50 | | `Collateral`, `bombard_rate` 8; +100% vs cities | Cannon | new |
| Caravel | Sea [Naval] | Optics† | 3 | 3 | 40 | | cargo 1 (Small Land only), may cross ocean | Galleon | stay |
| Explorer | Small Land [Recon] | Optics† | 1 | 2 | 30 | | `NonMil`, `IgTer`, `IgZOC` | none | stay |

### Era IV, Renaissance (HP 20)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Musketeers | Land [Gun] | Gunpowder | 9 | 1 | 60 | | walls give nothing against Gun attackers; `DefendGood` | Riflemen | stay |
| Grenadiers | Land [Gun] | Chemistry | 12 | 1 | 80 | | +50% vs Gun | Infantry | new |
| Dragoons | Land [Mounted] | Leadership | 12 | 2 | 85 | Horses | `Withdraws`; +50% vs Siege | Cavalry | stay |
| Cannon | Big Land [Siege] | Metallurgy | 12 | 1 | 80 | Iron | `Collateral`, `bombard_rate` 10; +100% vs cities | Artillery | stay |
| Galleon | Sea [Naval] | Astronomy | 4 | 4 | 60 | | cargo 3 Land/Small Land/Big Land/Merchant | Transport | stay |
| Frigate | Sea [Naval] | Magnetism | 8 | 4 | 70 | | cargo 1; `Hunter` | Ironclad | stay |
| Ship of the Line | Sea [Naval] | Navigation | 12 | 4 | 100 | Iron | +50% vs cities (naval bombardment) | Ironclad | new |
| Militia | Land [Gun] | Gunpowder | 8 | 1 | 20 | | draft unit for eras IV-V (slice 3) | none | new |

### Era V, Industrial (HP 20)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Riflemen | Land [Gun] | Conscription | 14 | 1 | 90 | | +25% vs Mounted; `DefendGood` | Infantry | stay |
| Infantry | Land [Gun] | Machine Tools | 20 | 1 | 120 | | `DefendGood`, `Marines` flag dropped | Mechanized Infantry | new |
| Machine Gunners | Land [Gun] | Machine Tools | 18 | 1 | 110 | | attack 0; +50% vs Gun and Melee; `DefendGood` | Mechanized Infantry | new |
| Cavalry | Land [Mounted] | Tactics | 15 | 2 | 100 | Horses | `Withdraws`; +50% vs Siege | Armoured Cars | stay |
| Alpine Troops | Land [Gun] | Tactics | 14 | 1 | 100 | | `IgTer` (every tile costs one move); `DefendOk` | Infantry | back, John 2026-10-17 |
| Artillery | Big Land [Siege] | Steel | 18 | 1 | 110 | | `Collateral`, `bombard_rate` 14; +100% vs cities; `CityBuster` dropped (one strength, so firepower stays 1) | Howitzer | stay |
| Ironclad | Sea [Naval] | Steam Engine | 14 | 4 | 90 | Iron, Coal | coast only (`Trireme`-style restriction through `unitclass` is not possible for class Sea; use the built-in `CoastStrict` flag, `civ45/units.ruleset:387`) | Destroyer | stay |
| Transport | Sea [Naval] | Industrialization | 3 | 5 | 50 | | attack 0; cargo 4 (John 2026-10-17; the first build had 8) | none | stay |
| Engineers | Small Land | Explosives | 0 | 2 | 30 | | `Transform` | none | stay |
| Freight | Merchant | The Corporation | 0 | 2 | 50 | | | none | stay |
| Spy | Small Land | Espionage | 0 | 3 | 30 | | | none | stay |
| Conscripts | Land [Gun] | Conscription | 14 | 1 | 25 | | draft unit for eras V-VII (slice 3) | none | new |

### Era VI, Modern (HP 20; 30 for Tank, Battleship, Carrier)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Armoured Cars | Big Land [Armour] | Automobile | 16 | 3 | 100 | Oil | `Withdraws`; +50% vs Siege and Gun in the open (an `Attack_Bonus` with `CityTile Center Tile FALSE`) | Tank | new |
| Tank | Big Land [Armour] | Mobile Warfare | 28 | 2 | 150 | Oil | +25% vs cities | Main Battle Tank | rename (Armor) |
| Marines | Land [Gun] | Amphibious Warfare | 24 | 1 | 120 | | `Marines` (attack from boats); +25% vs cities | none | stay |
| Paratroopers | Land [Gun] | Advanced Flight | 20 | 1 | 120 | | `Paratroopers` | none | stay |
| Partisan | Land [Gun] | Guerilla Warfare | 12 | 1 | 60 | | `IgTer`, `IgZOC`, `Partisan` role; +50% on hills and forest | none | stay |
| Fighter | Air | Flight | 20 | 8 | 100 | Oil | `AirAttacker`; intercepts (targets Air, Missile, Helicopter); fuel 1 | Jet Fighter | stay |
| Bomber | Air | Advanced Flight | 16 | 8 | 120 | Oil | `Bombarder`, `bombard_rate` 3, `OneAttack`; fuel 2 | Stealth Bomber | stay |
| Destroyer | Sea [Naval] | Combustion | 24 | 6 | 110 | Oil | sees submarines (vision 8); ×2 vs Submarine | none | stay |
| Cruiser | Sea [Naval] | Steel | 28 | 5 | 130 | Oil | +50% vs cities | Missile Cruiser | stay |
| Battleship | Sea [Naval] | Automobile | 36 | 4 | 180 | Oil | HP 30; +100% vs cities | none | stay |
| Submarine | Sea [Naval] | Combustion | 24 | 5 | 110 | Oil | `Submarine`, `Only_Native_Attack`, invisible (`vision_layer`) | Missile Submarine | stay |
| Carrier | Sea [Naval] | Advanced Flight | 16 | 5 | 180 | Oil | HP 30; attack 0; cargo 4 Air/Missile/Helicopter | none | stay |
| Cruise Missile | Missile | Rocketry | 30 | 12 | 50 | | `OneAttack`, `FieldUnit`; fuel 1 | none | stay |
| Atom Bomb | Missile | Nuclear Fission | 99 | 0 | 160 | Uranium | `Nuclear`; needs the Manhattan Project wonder | none | rename (Nuclear) |

### Era VII, Information (HP 30)

| Name | Class [flag] | Tech | S | M | C | Resource | Counters and notes | Upgrades to | Status |
|---|---|---|---|---|---|---|---|---|---|
| Main Battle Tank | Big Land [Armour] | Robotics | 40 | 3 | 200 | Oil, Aluminium | +25% vs cities | none | new |
| Mechanized Infantry | Big Land [Gun] | Labor Union | 32 | 3 | 160 | Oil | `DefendGood`; +50% vs Armour | none | rename (Mech. Inf.) |
| Gunship | Helicopter | Combined Arms | 32 | 6 | 150 | Oil | `OneAttack`, `Bombarder` dropped; +100% vs Armour; cannot take cities | none | rename (Helicopter) |
| Air Defence Infantry | Land [Gun] | Rocketry | 24 | 1 | 120 | | ×4 vs `AirAttacker` (as AEGIS today); attack 0 | none | new |
| Howitzer | Big Land [Siege] | Robotics | 32 | 2 | 170 | | `Collateral`, `bombard_rate` 20; +100% vs cities; walls give nothing against it | none | stay |
| Jet Fighter | Air | Advanced Flight | 32 | 12 | 140 | Oil, Aluminium | as Fighter; fuel 1 | Stealth Fighter | new |
| Stealth Fighter | Air | Stealth | 40 | 14 | 180 | Aluminium | invisible until adjacent | none | stay |
| Stealth Bomber | Air | Stealth | 32 | 12 | 200 | Aluminium | `Bombarder`, `bombard_rate` 4; fuel 2 | none | stay |
| Radar Plane | Air | Computers | 1 | 16 | 140 | Oil | attack 0; vision 26 | none | rename (AWACS) |
| Missile Cruiser | Sea [Naval] | Computers | 40 | 5 | 170 | Aluminium | ×4 vs `AirAttacker`; cargo 2 Missile | none | rename (AEGIS Cruiser) |
| Missile Submarine | Sea [Naval] | Nuclear Power | 30 | 5 | 200 | Uranium | `Submarine`; cargo 8 Missile | none | rename (SSBN) |
| Nuclear Missile | Missile | Rocketry + Nuclear Fission | 99 | 0 | 180 | Uranium | `NuclearOP` (unlimited range); Manhattan Project | none | rename (ICBM) |

### Kept special units and what goes

| Unit | Verdict | Why |
|---|---|---|
| Leader, Barbarian Leader, Storm | stay | Sandbox machinery: the game-loss unit, barbarian ransom, weather (`civ45/units.ruleset:3012-3160`) |
| Fanatics | stay | The Fundamentalism unit; it already has `AddToCity` and a government requirement, so it is the model for the draft units |
| Jaguar Warrior, Immortal | go | The reference game's own unique units by name; the unique-unit pass (section 4) brings nation units back under Freeciv45 names |
| Alpine Troops | back (John 2026-10-17) | The first build dropped it; it returns nation-neutral at Tactics, strength 14, `IgTer`, until the unique-unit pass |
| Crusaders | renamed Zealots (John 2026-10-17) | The first build dropped it; the name belongs to one faith, so it returns as Zealots: Monotheism, strength 8, move 2, Horses, no Iron |
| Mechanic | go | Sandbox's infrastructure repair unit; Workers and Engineers take its `Transform` and repair roles |
| Great people (7) | new, in `great-people.md` | |

Count: 46 units stay, 12 are renamed (Crusaders to Zealots among them), 3 go, 18 are new here (15 military and recon
plus 3 draft units), plus Alpine Troops back and the 7 great people: 85 unit types in `units.ruleset` before unique units
(78 of the roster and the 7 great people). Of the 62 today, every one has a verdict above.

## 3. Balance logic per era

**Era I.** Everything is cheap and weak, and the only counter that matters is spears against horses, so the
early game is about settling and scouting, not fighting. Copper gates Axemen, the first unit that beats a
Spearman, so an empire without copper defends with Archers behind walls and attacks with Chariots. The curve
starts at strength 1 to 4 and the draft Levy is a Spearman that costs a citizen instead of hammers.

**Era II.** Iron doubles the top strength (Swordsmen 6, War Elephants 8) and the first siege unit arrives. The
Catapult is the first unit whose value is not its strength: it wounds a whole stack (slice 2) and gets +50%
against cities, but loses half its defence to any Mounted attacker, which is why Horse Bowmen exist. A stack
of Swordsmen, Catapults and Spearmen is the classical army; its answer is Horse Bowmen against the siege and
Spearmen against the horse.

**Era III.** The widest spread of the game: three foot lines (mace, pike, bow) at strength 6 to 8 and Knights
at 10. Nothing beats a Knight head on except Pikemen, so Pikemen stay cheap (45) and the Knight stays dear (70
and two resources). Longbowmen and Crossbowmen split the archer role into city defence and anti-melee so that a
player who lacks iron still has a strong garrison. Trebuchet strength drops to 4: it is a wall-breaker and
stack-wounder, not a fighter.

**Era IV.** Gunpowder resets the counters: walls stop helping against Gun units (section 1), Musketeers cost no
resource, and Grenadiers are the first unit with a bonus against their own class. The mounted line (Dragoons
12) keeps pace with the foot line (Grenadiers 12) for the last time. Naval strength jumps (Ship of the Line 12)
so coastal cities need Musketeers, not just walls.

**Era V.** Strength climbs from 14 to 20 and hit points stay 20, so fights take longer and veterancy matters
more. Machine Gunners are the first defence-only unit and the counter to the Infantry and Cavalry that
dominate the era; Artillery at 18 is strong enough to fight, not just bombard. Ironclads need two resources
(Iron and Coal) and keep to the coast, so the ocean still belongs to Frigates until Destroyers.

**Era VI.** Oil gates almost everything: armour, every aircraft, every warship. A player without oil is stuck
with Infantry, Marines and Partisans against Tanks at 28 and Battleships at 36. Armoured Cars (16, moves 3) are
the first unit that breaks off from a lost fight at speed; Tanks do not withdraw, so they are the city takers.
Air units are a separate game: Fighters intercept, Bombers wound stacks, and nothing on the ground touches them
until Air Defence Infantry in era VII, which is deliberate.

**Era VII.** Top strengths 32 to 40 with 30 hit points. Every counter has an answer: Gunships beat Armour,
Mechanized Infantry beats Armour on defence, Air Defence Infantry and Missile Cruisers quadruple against
aircraft, Stealth units are invisible until adjacent. Aluminium gates the jets and the Missile Cruiser,
Uranium the nuclear units, so late wars are fought over three resources.

**Across eras (derived).** Strength roughly grows by 1.5 to 2 per era, which with the strength-share round
rule (`up/server/unittools.c:288-340`) means a unit one era behind wins about a quarter of fights and two eras
behind almost none. Costs grow slower than strength, so an empire that keeps upgrading gets more strength per
hammer each era; the quadratic upgrade price (section 1) is what stops skipping eras.

## 4. Unique units per nation (later)

One unit per nation, a renamed copy of a standard unit with one modest edge (+1 strength, one extra move, a
free veteran level or a dropped resource), built with `"Nation", "<name>", "Player"` in `reqs` and the standard
unit given a `"Nation", "<name>", "Player", FALSE` req, exactly as Jaguar Warrior and Warriors do today
(`civ45/units.ruleset:723-792`, observed). civ45 uses the default nation list (`civ45/nations.ruleset`, 570
nations through `default/nationlist.ruleset`), so the pass covers the nations the AI fills from and gives the
rest the standard unit. Names, nations and edges are a separate design note once the roster has played.

## 5. Test plan

| Check | How | Pass when |
|---|---|---|
| Ruleset loads | `scripts/civ45-rules-test.sh ~/freeciv-builds/qt` | 8 existing cases pass, no Lua error, no "unknown flag" warning in `server.log` |
| One strength | Lua's `Unit_Type` has no attack or defence getter (`up/common/scriptcore/tolua_game.pkg:460-480`, observed), so `scripts/civ45-rules-test.sh` adds a shell check: a Python one-liner over `units.ruleset` sections comparing `attack` and `defense` | Equal for all but the listed attack-0 types |
| Counters | Tester Spearmen vs Animal Horsemen on open ground, 20 fights through `perform_action(find.action("Attack"), tile)` (the pattern of the slice 1 combat case, `scripts/civ45-rules-test.lua`) | Spearmen win at least 15 |
| Upgrade keeps veterancy | A veteran Spearmen in a city with Feudalism known: "Upgrade Unit" | `unit.veteran` unchanged, type Pikemen, gold down by the section 1 price |
| Autogame | `FREECIV_DATA_PATH=port/freeciv/data scripts/test.sh ~/freeciv-builds/qt --ruleset civ45 --no-client --turns 300` | Units of every era appear by turn 300 (count types in the final save), largest stack and cities taken reported as in issue 49 |

## Open questions for John

1. Draft units: three (Levy, Militia, Conscripts) spanning the eras, or one per era as roadmap row 3 says?
2. Hit points 10/20/30 as today, or 10 everywhere with firepower 1 so every fight is at most ten rounds?
3. Keep Cruiser and Ship of the Line (two capital ships the reference roster lacks), or cut them for art?
4. Should Alpine Troops and Crusaders go, or stay as nation-neutral units until the unique-unit pass?
5. Transport cargo: 8 as today (Freeciv) or 4 (fewer, bigger invasions)?

Answered by John 2026-10-17 (plan decision 11): three draft units as built; hit points 10/20/30 as built; both
Cruiser and Ship of the Line stay; Alpine Troops come back as they were and Crusaders come back as Zealots, both
nation-neutral until the unique-unit pass; Transport cargo 4. Horses gate the mounted units from this build on
(the resource exists on grassland and plains), not from slice 4.

## Implementation order

1. `civ45/units.ruleset`: the 8 class flags in `[control] flags`; rename the 11 units (keep `rule_name` as the
   old name so saves load); delete the 5; add the 18 with the stats above; set `attack = defense` everywhere;
   `obsolete_by` chains; `bonuses` rows; `CoastStrict` on Ironclad.
2. `civ45/effects.ruleset`: `Attack_Bonus` city rows per flag; `Fortify_Defense_Bonus` city and hill rows;
   rewrite `effect_city_walls_0` and `effect_coastal_defense` reqs by attacker flag.
3. `civ45/game.ruleset`: `upgrade_veteran_loss 0`, `autoupgrade_veteran_loss 0`.
4. `civ45/buildings.ruleset`: nothing (Barracks stay); `civ45/README.civ45` roster paragraph.
5. `scripts/civ45-rules-test.lua` cases from section 5; the autogame; fork patch after slice 2's.
6. Tileset: 18 new sprite tags for civ45-tileset to draw (`graphic` names to be listed in the slice PR).
