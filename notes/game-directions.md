# Game directions: the port, civ45 and civ54

Date: 2026-10-16. Status: proposal, decision is John's.
Labels as in the brief: observed, derived, inferred, unknown.

John's goal (2026-10-16): civ45 should feel more like Civilization V than IV, accepting that some of
Civ5 needs engine and art work. Proposed split: keep "civ45" as the game we can ship now (closer to
Civ4 where the engine forces it) and start "civ54" later as the game that is closer to Civ5.
He left the choice between a two-game and a three-game direction open.

## The three pieces

| | Freeciv for macOS (the port) | civ45 | civ54 |
|---|---|---|---|
| What it is | Stock Freeciv 3.2 rules, our two build patches | Ruleset + Lua on top of stock Freeciv 3.2 (`port/freeciv/data/civ45`, patches 0003+) | A fork of the Freeciv engine (C in `common/`, `server/`, `ai/`, `client/gui-qt`) with its own ruleset and art |
| Status | Released as v3.2.6-mac1 (observed) | Slices 1 and 2 merged (PRs 24 and 29), in no release yet (observed, see Next steps) | Not started |
| Runs on | Our macOS build | Any Freeciv 3.2 build: our DMG, upstream Windows and Linux installers, other people's servers (derived: it is data only) | Only builds of the fork |
| Multiplayer with stock Freeciv | Yes | Yes: only the server needs the civ45 files, it sends the rules to each client as it connects (observed, `server/connecthand.c:191`, `client/packhand.c:3607`) | No: the fork must change its network capability string and savegame format (inferred) |
| AI | Stock | Stock AI, steered through the ruleset | Needs AI work for every new mechanic |
| Art | Freeciv's GPL tilesets | Same (hex: `hexemplio`, `isophex`, `hex2t`, observed in `data/`) | New original hex art, GPL-compatible |

## What civ45 can and cannot be

civ45 gets every Civ5 rule the ruleset and Lua can express. Done or ready (citations in
`notes/civ45-planning.md`): hex map, one unit per tile including cities, culture-driven borders
and city radius, cultural victory, unique units and buildings, strategic resources, policy sliders
(multipliers). Newly found: Civ5-style ranged attacks fit too. The 3.2 action "Bombard Lethal"
can kill, has its own `bombard_lethal_max_range`, and needs no adjacency (observed,
`refs/freeciv-S3_2/doc/README.actions:811-820`). Whether the default AI uses it is unknown
(issue 32).

What stays Civ4-like in civ45 because the engine decides it (derived from the Tier C list):
per-city happiness instead of a global pool, one linear promotion ladder, no city-states, no
"pass through friendly units" movement, the stack-era AI, and Freeciv's interface.

## Option A: two games

The port, plus one game that starts as civ45 and turns into Civ5 in place as engine work lands.

- For: one product, one name, one ruleset to balance.
- Against: the first engine change ends civ45's ability to run on stock Freeciv, so no upstream
  Windows/Linux installers and no stock multiplayer servers. Every engine slice blocks the whole game
  until it is finished, and balance work done for the stock engine is redone.

## Option B: three games (recommended)

The port, civ45 frozen at "ruleset and Lua only", and civ54 as the engine fork that starts from a
copy of civ45's ruleset.

- For: civ45 ships now on every platform and keeps working on future Freeciv releases (the ruleset
  can be migrated with `freeciv-ruleup`, which our build installs; observed in `~/freeciv-builds/qt/bin`). civ54 can break compatibility freely. Engine features that are
  general, such as a unit-class-aware tile limit, can be offered upstream; if Freeciv adopts them,
  civ45 can use them later.
- Against: two rulesets diverge and both need balancing; civ54 needs its own Windows build.

Recommendation: B. It gets a playable game in people's hands now and keeps the risky work in a
separate tree. The cost is a second ruleset, which civ54 would rewrite anyway.

## civ54 roadmap (engine slices, smallest useful first)

1. **Civ5 tile rules.** One military and one civilian unit per tile, moving through friendly units
   but not ending a move stacked, a city garrison slot, aircraft and ships counted separately.
   Movement checks, the pathfinder and the AI must all know the rule. This replaces civ45's
   relocation script. Areas: `common/movement.c`, `server/unithand.c`, `common/aicore/pf_tools.c`,
   `ai/default/` (inferred from the 3.2 layout). The first gap is tracked as issue 30: today's tile
   limit counts every unit (`common/requirements.c:2749`), so a ship in port keeps land units out.
2. **Ranged combat for the AI.** civ45 can give units "Bombard Lethal" at range 2; civ54 adds
   city ranged strikes and teaches the AI to use ranged units.
3. **Global happiness.** One empire-wide pool fed by luxury resources, replacing per-city content
   and unhappy citizens (`server/cityturn.c`, every city dialog).
4. **Social policy trees.** Culture buys policies in branches; Freeciv's multipliers become the
   effect layer underneath.
5. **City-states.** A minor-civ player kind with influence, quests and gifts.
6. **Hex-first Qt client.** Civ5-style city screen, unit panel and tech web, plus a new art set.

Religion, espionage depth and Civ5's expansion content come after these.

## Assets and naming

- No Firaxis or 2K assets, text or sounds (rule from the brief). civ45 uses Freeciv's GPL art.
  New civ54 art must be original or under a licence that can ship with GPL-2.0-or-later code; check
  each licence before accepting art. The FSF lists CC BY 4.0 as compatible with all versions of the
  GPL (observed, https://www.gnu.org/licenses/license-list.html#ccby, read 2026-10-16). CC BY-SA 4.0
  is only one-way compatible with GPLv3 (same page, `#ccbysa`), so CC BY-SA art would make the
  combined civ54 package GPLv3, which Freeciv's "or later" allows (derived). Avoid NonCommercial and
  NoDerivatives licences: the same page says neither qualifies as free (`#CC-BY-NC`, `#CC-BY-ND`).
- "civ45" and "civ54" follow Freeciv's own ruleset names (`civ1`, `civ2`, `civ2civ3`, observed in
  `refs/freeciv-S3_2/data/`). A public product name, store page or website should avoid
  "Civilization", a trademark of Take-Two Interactive (inferred, not legal advice).

## Next steps if B is chosen

1. civ45: ranged units via "Bombard Lethal" (issue 32) and a late-era AI check of one unit per
   tile (issue 31), then the Lua layer (Great People, golden ages, culture flipping), then a balance
   pass. Ship each slice in the macOS DMG and as a modpack for upstream Windows and Linux builds.
   The published v3.2.6-mac1 DMG does not contain civ45 yet (observed: the `Freeciv.app` it was
   made from has no `share/freeciv/civ45`, and the DMG was written at 13:09, before civ45 reached the
   install prefix at 13:10). The next release will be the first with civ45.
2. civ54: create a `civ54` branch in `port/freeciv` from S3_2 plus `patches/`, copy civ45's
   ruleset, and start slice 1 (issue 30).
