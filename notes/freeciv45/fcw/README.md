# What the FCW fork of Freeciv-web teaches Freeciv45

FCW is the community fork of Freeciv-web that runs freecivweb.com (https://github.com/Lexxie9952/fcw.org-server).
It was cloned on 2026-10-18 to `refs/fcw.org-server` (shallow, commit e27cac3 of 2025-03-25, git-ignored, read
only) and studied in three parts:

- [art.md](art.md): tilesets, sprite packing, iso geometry and anchors, the full list of sprite tags by layer,
  and lessons for image prompts.
- [rules.md](rules.md): the MP2 rulesets and what they suggest for our open balance issues.
- [engine.md](engine.md): FCW's server changes, web client features worth having in our Qt client, the 3D
  renderer in upstream Freeciv-web, and the browser stack.

## Most useful for Freeciv45

**Art, for the isometric tileset (issue 81 and the freeciv45iso work)**
- Amplio2's base terrain is a flat, unlit diamond. Hills, mountains, forest and jungle are transparent overlays
  painted in iso, in forms matched to their neighbours. A script can turn our square painted cells into
  diamonds for flat ground; relief has to be painted in iso.
- At 96x48 (double for 192x96), units are 64x48, cities are 96x72 with 24 px above the tile, and tall mountains
  are 96x66. Light comes from the upper left, and units face left.
- The beach belongs to the water tile, so land art never needs a water edge.
- Random detail sprites per terrain break up repetition. The 3.2 client already picks among numbered
  `t.lN.<terrain>` sprites with no code change (read from `client/tilespec.c`, not tried yet).

**Rules, for the balance issues**
- Tech pace (167): civ45's tech leakage at the default `techleak` and its world-range Great Library tech sharing
  are the first suspects. MP2 uses a lower leak and no tech sharing.
- The allied bloc (159): MP2 grants casus belli for border infractions, which in 3.2 turns AI goodwill into
  revenge wars.
- Bombard (83): an action-enabler requirement on siege units' Attack can force the AI to bombard again.
- Siege against walls: MP2 grades the walls bonus per siege unit with plain `Defend_Bonus` rows.
- Great people (166): MP2 limits its free-tech gift by turn and by research level.
- Nothing in FCW helps the spaceship (164), culture victory (165) or whip and draft (157, 158) problems.

**Client and engine**
- Ideas for our Qt slices: unit icons inside messages, hotkeys on the hovered city, a cycling city-bar mode,
  stack badges by unit type, empire tables with mass change and buy, a battle-odds tooltip, a tile popup with
  yield arrows, selection filters, and a minimap that redraws only on change.
- FCW's server is a full 3.1-dev tree with about 32 extra settings (stack-kill escape, extended bombard,
  diplomacy timers and more). It is useful for ideas, but not as patches for 3.2.
- A browser version of Freeciv45 later could rebuild our server with Freeciv 3.2's own `-Dserver=freeciv-web`
  option and either adopt the AGPL web client or build our Qt client for WebAssembly.

## Licences, and what we may take

- The web client is AGPL-3.0, so we take ideas only and never copy its code into our GPL-2.0-or-later patches.
- FCW's server C is GPL-2.0-or-later, but it is a 3.1-dev tree, so rewriting is cleaner than porting.
- FCW states no licence for its added art. Some items are credited "Unknown" or "???", some resource icons may
  be Creative Commons, and two cargo units show a real trademark. Stock amplio2 (GPL v2, partly from Battle for
  Wesnoth, GPL v2) is the only art we borrow, taken from Freeciv itself, not from FCW.
- The MP2 rulesets are written for a newer format and FCW's own engine changes. We take ideas and rewrite them in
  our data. Their wiki-derived help text is CC BY-SA, so it is not copied.
- The music, emoji and order icons in the web client have no stated licence.
