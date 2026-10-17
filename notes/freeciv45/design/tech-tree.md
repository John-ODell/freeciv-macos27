# Freeciv45 tech tree: implementation-ready design

Date: 2026-10-17. Status: design for the tech part of roadmap slice 10; the roster in `units-and-upgrades.md`
and the buildings in today's `civ45/buildings.ruleset` hang off it. Labels: observed, derived, inferred,
unverified. Paths as in `victory.md`: `up/` is `refs/freeciv-S3_2/`, `civ45/` is `port/freeciv/data/civ45/` at
fork commit f55003f. Spec: `notes/freeciv45/mechanics.md` 2.8 (seven eras, strength per era). Feasibility:
`notes/civ45-planning.md:49` (techs.ruleset, cost styles). Names marked † are Freeciv45's own; the rest are
civ45's today (sandbox's, which are generic Freeciv names).

## 1. Shape

| Fact | Value | Where |
|---|---|---|
| Techs | 92: 86 of civ45's 89 kept, 3 dropped (Ruler Apotheosis, Nanomaterials, Labor Union), 6 added (Agriculture, Hunting, Archery, Machinery, Compass, Printing) | section 2; `civ45/techs.ruleset` |
| Eras | Seven, as tech classes: `[techclass_*]` sections, each advance names its class with `class = "..."` | `up/server/ruleset.c:1571-1575,1638-1641,1687-1692` (observed) |
| Prerequisites | Two at most (`req1`, `req2`), always in the same or an earlier era; roots have none | `civ45/techs.ruleset:127-131` (format) |
| Cost style | `Linear`: a tech costs `base_tech_cost` × `num_reqs`, where `num_reqs` is every tech it needs, counted recursively, plus itself (`advance_req_iterate` yields the tech too, so a root tech has `num_reqs` 1 and costs `base_tech_cost`, above `min_tech_cost`); the Tier column below is `num_reqs` − 1. Corrected 2026-10-17 by the tech slice (issue 109): the first draft counted the tech itself out | `up/common/tech.c:230-243`; `up/common/tech.h:299-307`; `civ45/game.ruleset:342-352` |
| Era curve | The tech class's `cost_pct` multiplies that cost | `up/common/tech.c:273` (observed) |
| Then | × `Tech_Cost_Factor` (civ45: 3, `civ45/effects.ruleset` `tech_cost_base`), tech leakage from embassies, × `sciencebox` | `up/common/research.c:868-1043` |
| Flags kept | `Bonus_Tech` on Philosophy, `Bridge` on Bridge Building, `Build_Airborne` on Flight | `civ45/techs.ruleset` (observed) |
| Check | `scripts/tech-tree-check.py --buildings port/freeciv/data/civ45/buildings.ruleset` reads the tables below and the roster and prints PASS or every finding; `--fill` rewrites the Tier column | section 4 |

Era boundaries, in words: I Ancient (the roots and the first cities), II Classical (iron, law, the first
governments), III Medieval (feudal arms, universities, the compass), IV Renaissance (gunpowder, printing,
ocean sailing, democracy), V Industrial (steam, rail, factories, conscription), VI Modern (oil, flight, the
atom), VII Information (computers, rockets, space). The city style changes (`civ45/styles.ruleset`: University,
Railroad, Automobile, Rocketry, Superconductors) land at the III/IV, IV/V, V/VI, VI/VII boundaries and inside
VII, which fits.

### Cost per era

With `base_tech_cost` 10, `Tech_Cost_Factor` 3 and `sciencebox` 100, bulbs = 30 × (tier + 1) × cost_pct / 100.
The tiers come from the tree below (section 4 prints them); the `cost_pct` column is the lever. The bulbs column
below was written with 30 × tier and is one step low throughout: the rules test measured Alphabet 30, Gunpowder
648 (tier 17) and Fusion Power 3,195 (tier 70) on the built tree (issue 109).

| Era | Techs | Tier range (num_reqs) | `cost_pct` | Bulbs, cheapest to dearest | Why |
|---|---|---|---|---|---|
| I | 13 | 0 to 2 | 100 | 10 (min cost) to 60 | Roots are nearly free so the first turns are choices, not waits |
| II | 14 | 1 to 8 | 100 | 30 to 240 | Linear depth already multiplies costs; no extra lever yet |
| III | 12 | 5 to 14 | 110 | 165 to 462 | A gentle nudge; the medieval era is where tech leakage starts to matter |
| IV | 10 | 10 to 22 | 120 | 360 to 792 | |
| V | 14 | 20 to 49 | 130 | 780 to 1,911 | Machine Tools (49) is the era's deep end: it needs Steel and Tactics |
| VI | 14 | 28 to 58 | 140 | 1,176 to 2,436 | Atomic Theory (28) is cheap on purpose: a detour, not the main road |
| VII | 15 | 49 to 70 | 150 | 2,205 to 3,150 | The space race should take the last fifty turns, not twenty |

Derived: with eight to twelve cities of civ2civ3-like science a player makes roughly 30 bulbs a turn in era
III and 300 in era VI (unverified; the autogame in section 5 measures it), which gives about eight turns per
tech in both, so the curve keeps the pace even rather than racing through the late game as a flat cost would.

## 2. The tree

Columns: Req 1 and Req 2 are the prerequisites (`none` for roots); Tier is `num_reqs` as the script computes
it; Unlocks lists units (U), buildings (B), wonders (W), governments (G) and abilities (A). "(prerequisite)"
means the tech only opens later ones. Building and wonder names are today's; the roster's unit names are
`units-and-upgrades.md`'s.

### Era I, Ancient

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Agriculture† | I | none | none | 0 | A: irrigation (the Irrigation extra gets a `Tech Agriculture Player` req) |
| Hunting† | I | none | none | 0 | U: Scout |
| Pottery | I | none | none | 0 | B: Granary; U: Migrants; W: Hanging Gardens |
| Alphabet | I | none | none | 0 | (prerequisite) |
| Ceremonial Burial | I | none | none | 0 | B: Temple; W: Mausoleum of Mausolos |
| Warrior Code | I | none | none | 0 | B: Barracks (new req); W: Chichen Itza |
| Bronze Working | I | none | none | 0 | U: Spearmen, Axemen, Levy; W: Colossus |
| Masonry | I | none | none | 0 | B: City Walls; W: Pyramids |
| Horseback Riding | I | Agriculture | none | 1 | U: Horsemen |
| The Wheel | I | Horseback Riding | none | 2 | U: Chariot |
| Mysticism | I | Ceremonial Burial | none | 1 | W: Temple of Artemis |
| Writing | I | Alphabet | none | 1 | B: Library; U: Diplomat |
| Map Making | I | Alphabet | none | 1 | U: Trireme; W: Lighthouse |

### Era II, Classical

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Archery† | II | Hunting | Warrior Code | 2 | U: Archers, Horse Bowmen |
| Iron Working | II | Bronze Working | Warrior Code | 2 | U: Swordsmen |
| Mathematics | II | Alphabet | Masonry | 2 | U: Catapult |
| Currency | II | Bronze Working | none | 1 | B: Marketplace, Bazaar (Arab) |
| Code of Laws | II | Alphabet | none | 1 | B: Courthouse |
| Literacy | II | Writing | Code of Laws | 3 | W: Great Library |
| Monarchy | II | Ceremonial Burial | Code of Laws | 3 | G: Monarchy; W: Altar to The Divine Ruler (re-homed) |
| Polytheism | II | Horseback Riding | Ceremonial Burial | 3 | W: Statue of Zeus; B: Amêzârâkian Mysteries (small wonder) |
| Philosophy | II | Mysticism | Literacy | 6 | A: free tech (`Bonus_Tech`) |
| Construction | II | Masonry | Iron Working | 4 | B: Amphitheater, Aqueduct; W: Great Wall; U: War Elephants |
| Seafaring | II | Pottery | Map Making | 3 | B: Harbor; U: War Galley |
| Trade | II | Currency | Pottery | 3 | U: Caravan; W: Marco Polo's Embassy |
| The Republic | II | Code of Laws | Literacy | 4 | G: Republic |
| Bridge Building | II | The Wheel | Construction | 8 | A: roads over rivers (`Bridge`) |

### Era III, Medieval

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Feudalism | III | Iron Working | Monarchy | 7 | U: Pikemen, Longbowmen; W: Sun Tzu's War Academy |
| Chivalry | III | Feudalism | Horseback Riding | 10 | U: Knights; W: King Richard's Crusade |
| Astronomy | III | Mysticism | Mathematics | 5 | W: Copernicus' Observatory |
| Monotheism | III | Astronomy | Polytheism | 9 | B: Cathedral; W: Michelangelo's Chapel |
| Theology | III | Philosophy | Monotheism | 14 | G: Fundamentalism; W: J.S. Bach's Cathedral, Treuga Dei; B: Ecclesiastical Palace (small wonder) |
| Machinery† | III | Iron Working | Mathematics | 6 | U: Macebearers, Crossbowmen, Trebuchet |
| Physics | III | Machinery | Astronomy | 10 | (prerequisite) |
| Invention | III | Bridge Building | Literacy | 13 | W: Leonardo's Workshop; A: upgrade price halved |
| Banking | III | Trade | The Republic | 9 | B: Bank |
| Compass† | III | Seafaring | Astronomy | 9 | U: Caravel, Explorer |
| University | III | Mathematics | Philosophy | 9 | B: University |
| Medicine | III | Philosophy | Trade | 11 | (prerequisite) |

### Era IV, Renaissance

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Gunpowder | IV | Invention | Feudalism | 17 | U: Musketeers, Militia; B: Barracks II |
| Printing† | IV | Machinery | Literacy | 10 | W: Shakespeare's Theatre (re-homed) |
| Navigation | IV | Compass | Invention | 22 | U: Galleon, Ship of the Line; B: Coastal Defense |
| Magnetism | IV | Compass | Physics | 15 | U: Frigate; W: Magellan's Expedition |
| Theory of Gravity | IV | Physics | University | 16 | W: Isaac Newton's College |
| Economics | IV | Banking | University | 16 | B: Stock Exchange; W: A.Smith's Trading Co.; G: Federation |
| Chemistry | IV | University | Medicine | 15 | U: Grenadiers |
| Leadership | IV | Chivalry | Gunpowder | 19 | U: Dragoons |
| Metallurgy | IV | Gunpowder | Mathematics | 19 | U: Cannon |
| Democracy | IV | Banking | Invention | 19 | G: Democracy; W: Statue of Liberty |

### Era V, Industrial

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Steam Engine | V | Chemistry | Navigation | 29 | U: Ironclad; W: Darwin's Voyage |
| Railroad | V | Steam Engine | Metallurgy | 34 | A: railroad; W: Eiffel Tower |
| Industrialization | V | Railroad | Banking | 37 | B: Factory; U: Transport |
| Conscription | V | Democracy | Metallurgy | 26 | U: Riflemen, Conscripts; W: Women's Suffrage |
| Electricity | V | Metallurgy | Theory of Gravity | 27 | (prerequisite) |
| Engineering | V | Electricity | Steam Engine | 38 | (prerequisite) |
| Steel | V | Engineering | Industrialization | 43 | U: Artillery, Cruiser |
| Explosives | V | Gunpowder | Chemistry | 27 | U: Engineers |
| Sanitation | V | Bridge Building | Medicine | 20 | B: Sewer System |
| Tactics | V | Conscription | Leadership | 29 | U: Cavalry |
| Machine Tools | V | Steel | Tactics | 49 | U: Infantry, Machine Gunners |
| Refining | V | Explosives | Industrialization | 39 | B: Power Plant |
| The Corporation | V | Economics | Industrialization | 39 | U: Freight |
| Communism | V | Theology | Industrialization | 41 | G: Communism; B: Police Station; W: United Nations |

### Era VI, Modern

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Combustion | VI | Refining | Engineering | 45 | U: Destroyer, Submarine |
| Automobile | VI | Combustion | Steel | 47 | U: Armoured Cars, Battleship; B: Super Highways |
| Flight | VI | Combustion | Tactics | 51 | U: Fighter; A: air units (`Build_Airborne`) |
| Electronics | VI | The Corporation | Electricity | 44 | B: Hydro Plant; W: Hoover Dam |
| Radio | VI | Flight | Electronics | 55 | B: Airport |
| Mass Production | VI | Automobile | The Corporation | 50 | B: Mass Transit |
| Refrigeration | VI | Sanitation | Electricity | 33 | B: Supermarket; A: farmland |
| Atomic Theory | VI | Theory of Gravity | Electricity | 28 | (prerequisite) |
| Nuclear Fission | VI | Mass Production | Atomic Theory | 52 | W: Manhattan Project; U: Atom Bomb |
| Mobile Warfare | VI | Automobile | Machine Tools | 54 | U: Tank; B: Barracks III |
| Advanced Flight | VI | Radio | Machine Tools | 58 | U: Bomber, Carrier, Paratroopers |
| Amphibious Warfare | VI | Engineering | Tactics | 46 | U: Marines; B: Port Facility |
| Guerilla Warfare | VI | Communism | Tactics | 47 | U: Partisan |
| Espionage | VI | Communism | Democracy | 43 | U: Spy |

### Era VII, Information

| Name | Era | Req 1 | Req 2 | Tier | Unlocks |
|---|---|---|---|---|---|
| Miniaturization | VII | Combustion | Electronics | 49 | B: Offshore Platform |
| Computers | VII | Miniaturization | Radio | 57 | B: Research Lab; W: Internet; U: Radar Plane, Missile Cruiser |
| Rocketry | VII | Advanced Flight | Miniaturization | 60 | U: Cruise Missile, Jet Fighter, Air Defence Infantry, Nuclear Missile; B: SAM Battery |
| Nuclear Power | VII | Nuclear Fission | Miniaturization | 55 | B: Nuclear Plant; U: Missile Submarine |
| Robotics | VII | Mobile Warfare | Computers | 62 | U: Main Battle Tank, Howitzer, Mechanized Infantry (re-homed) |
| Combined Arms | VII | Mobile Warfare | Advanced Flight | 61 | U: Gunship |
| Space Flight | VII | Computers | Rocketry | 62 | W: Apollo Program; B: Space Structural |
| Plastics | VII | Mass Production | Robotics | 64 | B: Mfg. Plant |
| Recycling | VII | Mass Production | Sanitation | 52 | B: Recycling Center |
| Laser | VII | Computers | Nuclear Power | 64 | B: SDI Defense |
| Superconductors | VII | Space Flight | Laser | 69 | B: Space Component, Space Elevator, Space Elevator Tether (re-homed) |
| Stealth | VII | Plastics | Space Flight | 68 | U: Stealth Fighter, Stealth Bomber |
| Genetic Engineering | VII | Refrigeration | Computers | 60 | W: Cure For Cancer |
| Environmentalism | VII | Recycling | Space Flight | 67 | B: Solar Plant, Space Module; W: Guidestones |
| Fusion Power | VII | Superconductors | Nuclear Power | 70 | A: heavy airlift (the `HeavyWeight` class flag text, `civ45/units.ruleset:65`) |

### Re-homed buildings and units

| Old tech | New tech | Buildings moved |
|---|---|---|
| Ruler Apotheosis | Monarchy | Altar to The Divine Ruler |
| Nanomaterials | Superconductors | Space Elevator, Space Elevator Tether |
| Labor Union | Robotics | (unit) Mechanized Infantry |
| Optics† | Compass† | (units) Caravel, Explorer: the roster named a tech this tree folds into Compass |
| Sanitation | Printing† | Shakespeare's Theatre (kept at Sanitation in the check; the slice moves it) |
| none | Warrior Code | Barracks (today it has no tech) |

Prerequisites changed from civ45's: Physics (was The Wheel + Magnetism), Magnetism (was Seafaring +
Astronomy), Navigation (was Invention + Physics), Atomic Theory (was Chemistry + Refrigeration), Genetic
Engineering (was Refrigeration + The Corporation), Fusion Power (was Superconductors + Labor Union), Monotheism
and Theology unchanged. Everything else keeps civ45's two prerequisites (observed by diff of the table against
`civ45/techs.ruleset`).

## 3. What this changes in the roster

Five rows of `units-and-upgrades.md` change because their tech does, and the roster slice applies them: Archers
move to era II (Archery sits in era II: its prerequisites Hunting and Warrior Code are era I roots, and one
tech cannot unlock an era I and an era II unit, so Horse Bowmen keep era II); Mechanized Infantry's tech is
Robotics (Labor Union is dropped); Caravel's and Explorer's tech is Compass (the roster's Optics is folded into
it); Cruise Missile moves to era VII (Rocketry is era VII here). The checker in section 4 carries these as
re-homed rows so it passes against the merged roster as it stands.

## 4. Consistency check

Output of `scripts/tech-tree-check.py --buildings port/freeciv/data/civ45/buildings.ruleset` on 2026-10-17
(the script is in the repo; the slice re-runs it after every edit):

```
techs: 92
  era I: 13
  era II: 14
  era III: 12
  era IV: 10
  era V: 14
  era VI: 14
  era VII: 15
units read from roster: 72
buildings read: 81
  no tech (allowed): Aqueduct, Lake
  no tech (allowed): Aqueduct, River
  no tech (allowed): Barracks
  no tech (allowed): Palace
  no tech (allowed): Coinage
root techs: 8: Agriculture, Alphabet, Bronze Working, Ceremonial Burial, Hunting, Masonry, Pottery, Warrior Code
deepest tier: 70
result: PASS
```

What it proves: every prerequisite exists and is in the same or an earlier era; the tree is acyclic; the
Tier column equals `num_reqs`; every roster unit's tech is in the tree; every building in today's
`buildings.ruleset` has at most one tech requirement and it is in the tree or re-homed; no tech is an orphan.
Buildings with no tech requirement (Palace, Barracks, the two Aqueduct variants, Coinage) are listed, not
failed; Barracks gets Warrior Code in the slice.

## 5. Test plan

| Check | How | Pass when |
|---|---|---|
| The tree loads | `scripts/civ45-rules-test.sh ~/freeciv-builds/qt` | No "unknown tech" or "cycle" error in `server.log`; 8 cases pass |
| Costs | A test case prints `player:tech_cost(find.tech_type("Gunpowder"))` and `("Fusion Power")` for Tester (`up/common/scriptcore/tolua_game.pkg:209-213`, observed) | 612 and 3,150 at sciencebox 100 (tiers 17 and 70 times 30, times 1.2 and 1.5) |
| Era classes | `server.log` at load lists seven tech classes (unverified that it logs them; else a Lua `find.tech_type("Flight")` has no class getter, so the slice greps `techs.ruleset`) | Every advance has a `class` |
| Pace | The 480-turn autogame of `victory.md` section 4; read `techs=` per `[scoreN]` and the research log | The best AI reaches era IV by turn 200 and era VII by turn 400; if not, lower `cost_pct` for VI and VII |

## Open questions for John

1. Archery in era II (so Archers come after Spearmen and Axemen), or in era I with Horse Bowmen pushed to a
   later tech such as Polytheism?
2. Drop Ruler Apotheosis, Nanomaterials and Labor Union (sandbox leftovers) and re-home their four unlocks, or
   keep all 89 and add the 6 for 95 techs?
3. The `cost_pct` curve 100 to 150: steeper (space race later) or flat (trust Linear depth alone)?
4. Should new techs get Freeciv45 names in more places (Physics, Medicine and Electricity unlock nothing and
   could become themed prerequisites), or stay generic?

## Implementation order

1. `civ45/techs.ruleset`: seven `[techclass_*]` sections with `cost_pct`; delete 3 advances; add 6; set
   `class` on all 92; rewrite the changed `req1`/`req2` rows; keep `graphic` tags, with `graphic_alt = "-"`
   for the six new ones until civ45-tileset draws icons.
2. `civ45/buildings.ruleset`: the five re-homed rows of section 2; `civ45/units.ruleset`: Mechanized
   Infantry's tech (with the roster slice).
3. `civ45/terrain.ruleset`: `Tech Agriculture Player` on the Irrigation extra's reqs.
4. `civ45/game.ruleset`: nothing (`Linear`, `base_tech_cost 10`, `min_tech_cost 10` stay).
5. `scripts/tech-tree-check.py` run; `scripts/civ45-rules-test.lua` cost case; the autogame; fork patch after
   the roster's.
