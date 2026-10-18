# FCW art pipeline study (for Freeciv45 iso tileset)

Read-only study of `refs/fcw.org-server` (FCW, shallow clone, one commit e27cac3, 2025-03-25), compared with `refs/freeciv-web` and `refs/freeciv-S3_2`. Paths below are relative to `~/Desktop/freeciv-port/refs/`. Short names used: **FCW-data** = `fcw.org-server/freeciv/freeciv/data`, **S32-data** = `freeciv-S3_2/data`, **FCW-js** = `fcw.org-server/freeciv-web/src/main/webapp/javascript`.

## Most useful for us

1. **Base terrain is flat and has no directional light. All relief is a separate layer.** Amplio2's base diamonds are plain flat textures with hard edges: exactly 2304 opaque px of 4608 in a 96x48 cell, with no soft alpha. Hills, mountains, forest and jungle are transparent overlays painted directly in iso (S32-data/amplio2/terrain1.png, hills.png, mountains.png, terrain2.png). So our square-to-diamond script is only safe for flat ground textures. Paint relief natively in iso.
2. **The base under an overlay is a neutral "bg" ground.** "Forest bg", "Hills bg" and "Mountains bg" are generic greens (mean #7d9d30 and #809a4f). Dither blending happens between base layers, so they must blend well with their neighbours.
3. **FCW's best trick is random detail decals.** FCW adds 16 sparse transparent decal sprites per terrain (tufts, rocks, dunes, reeds) for grassland, plains, desert and swamp. One is picked per tile by a seeded hash to break up repetition (FCW-data/amplio2/grassland.png, plains.png, desert.png, swamp.png; FCW-js/2dcanvas/tilespec.js `MATCH_RANDOM`). The native 3.2 client can already do this with no code change: it picks randomly among numbered `t.lN.<terrain>1..N` sprites (`freeciv-S3_2/client/tilespec.c` around lines 4189 and 5286).
4. **Anchors at 96x48.** Units are 64x48, drawn at (+19, −6) from the diamond's bounding-box top-left. Cities are 96x72, drawn at (0, −24): they fill the full width and are bottom-aligned, with 24 px of headroom. Tall mountains are 96x66, bottom-aligned, so 18 px of headroom. At 192x96, double all of these.
5. **Light comes from the upper-left and shadows fall right or lower-right** on trees, mountains, cities and units. Units face screen-left.
6. **The coast is painted on the water tile, not the land tile.** Each of 81 ocean "cellgroups" carries its own beach and shallow-water strip (S32-data/amplio2/ocean.png).

## 1. Tilesets FCW ships and how the web client packs them

- **Only amplio2.** The extractor builds a single tileset, `amplio2`. Its trident and isotrident entries are commented out (`fcw.org-server/scripts/freeciv-img-extract/img-extract.py`). The client loads only `tileset_config_amplio2.js` and `tileset_spec_amplio2.js` (FCW-js/2dcanvas/mapview.js, `init_mapview`).
- **Geometry.** Isometric, not hex. Normal tile 96x48, small tile 15x20, `fog_style` Darkness, `darkness_style` Corner (FCW-data/amplio2.tilespec; FCW-js/2dcanvas/tileset_config_amplio2.js). The native client derives a 96x72 "full tile" for iso, 3/2 of the tile height (`freeciv-S3_2/client/tilespec.c` ~2101–2106).
- **Sprite grid sizes** (from each `.spec` `[grid_main]`): terrain, hills, rivers, roads, fog, grid and select are 96x48. Mountains are 96x66. Cities and bases are 96x72. Units, veterancy and animals are 64x48. Activity icons are 28x24. Coast and lake cells are 48x24. Upkeep icons are 96x19. Unit explosions are 30x30 and the nuke is 180x176. Cursors are 32x32 with hot spots (S32-data/amplio2/*.spec, S32-data/misc/cursors.spec). FCW adds oversize units at 84x60 (FCW-data/amplio2/units_oversize.spec).
- **Packing script.** `img-extract.py` parses each `.spec` with ConfigParser after text patching. It crops every grid cell using `x_top_left`, `dx`/`dy` and `pixel_border`, then shelf-packs the cells row by row onto 2020x1400 RGBA sheets. A comment cites an iPhone Safari limit of 3 Mpx per image. It writes `tag → (x, y, w, h, sheet#)` to `tileset_spec_amplio2.js`, and `sync.sh` runs pngcrush on the output. Cellgroups are cut into four masked quarter-cells using `mask.tile`. Dithered transitions are **precomputed**: for every pair of ditherable terrains and each of 4 directions, it pastes the neighbour through `t.dither_tile` and crops a quarter. Arctic is dithered twice to soften contrast. Grid, border and nuke sprites are skipped (`img-extract.py`; `sync.sh`; `fcw.org-server/freeciv-web/build-images.sh`).
- **Scaling.** None for the map. Each sprite is cached in its own canvas, `imageSmoothingEnabled = false`, and there is no map zoom. Only base flags (0.6x) and frontier flags (0.4x) are scaled (FCW-js/2dcanvas/mapview.js `init_cache_sprites`; tilespec.js ~944, ~1126). Borders, the map grid and goto lines are drawn as canvas vector lines, not sprites (mapview.js `mapview_put_border_line`, `mapview_put_grid_line`, `mapview_put_goto_line`).
- Upstream freeciv-web uses the same script, without FCW's added spec files and without the random-decal layer (`freeciv-web/scripts/freeciv-img-extract/img-extract.py`; no `MATCH_RANDOM` in upstream `tilespec.js`).

## 2. Art FCW added or changed, with credit and licence

FCW's freeciv tree is 3.0.92-dev (`fcw.org-server/freeciv/freeciv/fc_version`). Its art lives in FCW-data/amplio2. The repository LICENSE.txt covers code only (server GPL, client AGPL). No file states a licence for the art, so the FCW additions are presumably GPL like the rest of the Freeciv data, but that is **not stated**.

| Addition | File | Credit in spec | Notes |
|---|---|---|---|
| Random terrain decals (16 each) | grassland/plains/desert.png | Lexxie9952 | not in amplio2.tilespec, web-only |
| Swamp decals | swamp.spec | "Unknown", "modified substantially by Lexxie" | **provenance unclear** |
| ~45 new or reworked units (`u.longboat`, `u.zealots`, `u.queen`, …) | units.spec | Lexxie, plus Scenario League tags | `u.war_galley` credited "???" — **unclear** |
| Oversize units 84x60 (`*_o`, wagon, truck, zeppelin) | units_oversize.spec | Lexxie, GB, Nemo | |
| `u.container`, `u.freight` | units.png | Lexxie / CT, qwm | **show the "MAERSK" trademark: avoid** |
| Crossed-swords death animation | swords.spec | Lexxie | |
| Great Wall as a river-style extra (`road.wall_s_*`) | walls.spec | Lexxie9952 | |
| Canal, sea bridge (`road.canal_s_*`, `road.sea_bridge_s_*`) | canal/seabridge.spec | GriffonSpade | |
| City coastal and fortification overlay/underlay, citadel | cities.spec row 10 | ";Lexxie" | |
| Naval base, radar, quay, bunker, tile claim, castle2; `city.revolt`, `city.starve` | bases.spec | Lexxie; spec also lists "Wesnoth [VC]" for ruins | Wesnoth art is GPL v2 |
| New resources: rubber, boar, berries, goat, hippo | terrain1.spec | none per item | **unclear**. The terrain1 panel lists sources "Wesnoth, Wikipedia, opengameart.org, FreeCol"; Wikipedia/OGA items may be CC |
| 5% HP bars, stack counters 2–9, stack shield rings, trade digits 10–21 | tiles.spec | none | |
| ~25 activity icons (hidden, vigil, canal, cargo…) | activities.spec | Lexxie | |
| Veteran badge order changed | veterancy.spec | — | |
| User marks, pollution ring | grid.spec | — | |
| 76 extra flag PNGs not referenced by flags.spec | FCW-data/flags | none | **orphans, no credit**; flags.spec otherwise credits each flag (public domain / Wikimedia) |
| Web UI icons: orders, governments, help terrain images, ~724 emoji in images/e | FCW webapp `images/` | none | **licence unclear**, don't reuse |

Some leftover work files also exist ("- Copy.png", terrain1.bak.png, select-alpha1/2.png). Stock amplio2 sheets carry "License: GPL v2" on their panels (S32-data/amplio2/terrain1.png, hills.png, mountains.png, cities.png). Forest and jungle are from Battle for Wesnoth (terrain2.png panel). The extractor stamps "GPL v2 Licensed … The Freeciv Artists" on each output sheet.

## 3. Tag checklist for an iso tileset (Freeciv 3.2 naming)

Source: S32-data/amplio2*.spec and misc/*.spec, plus `freeciv-S3_2/doc/README.graphics`. ⟨nesw⟩ means the 16 forms `n0e0s0w0`…`n1e1s1w1`.

**Terrain base and blending (layer 0)**
- Base tiles: `t.l0.<terrain>1` (add `2..N` for random variants) for desert, plains, grassland, forest, hills, mountains, tundra, arctic, swamp, jungle, inaccessible, plus volcano / erupting_volcanoa / erupting_volcanob in 3.2.
- Helpers: `t.dither_tile` (blend mask), `mask.tile` (diamond mask for cutting cells), `t.unknown1`, optional `t.blend.<terrain>` (amplio2 has arctic, coast and lake).

**Overlays (layer 1)**
- `t.l1.hills_⟨nesw⟩`, `t.l1.mountains_⟨nesw⟩` (tall), `t.l1.forest_⟨nesw⟩`, `t.l1.jungle_⟨nesw⟩`: 16 each, matched to same-type neighbours.
- Arctic uses three layers: `t.l0/l1/l2.arctic1`.
- Optional random decals: `t.l1.<terrain>1..N`.

**Coast and cell layers**
- Ocean: `t.l0.cellgroup_<a>_<b>_<c>_<d>` with each letter one of l/s/d (land, shallow, deep), giving 81 full 96x48 tiles that are split into quarters.
- Lake: `t.l0.lake_cell_<u|d|l|r>_<l|s>_<l|s>_<l|s>` (32 cells of 48x24).
- Ice edges: `t.l1.coast_cell_<u|d|l|r>_<i|w>_<i|w>_<i|w>` (32).

**Rivers**: `road.river_s_⟨nesw⟩` (16) and `road.river_outlet_n/e/s/w` (4).

**Roads and rails**: `road.road_isolated`, `road.road_n`, `_ne`, `_e`, `_se`, `_s`, `_sw`, `_w`, `_nw`, and the same set for `road.rail_*` and `road.maglev_*` (RoadAllSeparate: 9 sprites each).

**Other extras**
- `tx.irrigation`, `tx.farmland` (Cardinals style: one sprite, or optional `_⟨nesw⟩` variants, see `tilespec.c` ~3928).
- `tx.mine`, `tx.oil_mine`, `tx.oil_rig`, `tx.nets`, `tx.pollution`, `tx.fallout`, `tx.village` (hut).
- Bases use 3Layer naming: `base.<name>_bg`, `_mg`, `_fg` for fortress, outpost, airbase, airstrip, buoy, castle and castle2. Also `extra.ruins_mg`, `extra.transport_hub_mg`, `tx.airbase_full`.

**Resources**: `ts.` plus oasis, oil, buffalo, wheat, pheasant, silk, coal, wine, gold, iron, tundra_game, furs, arctic_ivory, arctic_oil, peat, spice, gems, fruit, fish, whales, seals, forest_game, horses, grassland_resources, river_resources.

**Units**
- Unit sprites are `u.<graphic>` from units.ruleset `graphic`/`graphic_alt` (64x48). Animals are separate.
- Selection: `unit.select0..3`.
- HP bars: `unit.hp_0`, `unit.hp_10` … `unit.hp_100`.
- Veteran badges: `unit.vet_1..9`, full-size 64x48 overlays.
- Status: `unit.lowfuel`, `unit.tired`, `unit.loaded`, `unit.stack`, `unit.connect`, `unit.auto_attack`, `unit.auto_settler`.
- Activities (28x24): fortified, fortifying, sentry, goto, patrol, pillage, irrigate, mine, transform, plant, cultivate, road, rail, maglev, fortress, airbase, airstrip, outpost, buoy, convert, pollution, fallout, oil_mine, oil_rig, farmland, auto_explore, action_decision_want.
- Upkeep icons: `upkeep.food`/`shield`/`gold`/`unhappy` with counts 2–10.
- Flags: `f.<nation>`, `f.shield.<nation>`.
- Explosions: `explode.unit_0..4`, `explode.nuke`.

**Cities**
- `city.<style>_city_0..4` and `city.<style>_wall_0..4`. The walled sprites are complete city images with the wall drawn round the diamond edge, not overlays. Native 3.2 picks the index from the `City_Image` effect; FCW's web client hard-codes the size bands 1–3, 4–7, 8–11, 12–15 and 16+ (FCW-js/2dcanvas/tilespec.js `get_city_sprite`).
- Optional 3.2 walls by building: `<style>_bldg_<n>_<i>`.
- Occupied flag: `city.<style>_occupied_0`. Defaults: `cd.city`, `cd.city_wall`, `cd.occupied`. Disorder: `city.disorder`.
- Size numbers: `city.size_0..9`, plus tens and hundreds forms. Tile outputs: `city.t_food_0..9`, `city.t_shields_0..9`, `city.t_trade_0..9`.
- City bar: `citybar.*`. Worked-tile overlays: `colors.overlay_0..3`, `mask.worked_tile`, `mask.unworked_tile`.
- Styles in amplio2: european, classical, asian, tropical, celtic, babylonian, industrial, electricage, modern, postmodern.

**Fog**: `t.fog_<x>_<x>_<x>_<x>` with x one of u/f/k (unknown, fogged, known), 81 sprites for the Corner style. Also `tx.fog` and `tx.darkness`.

**Borders and grid**: `grid.main.ns/we`, `grid.city.ns/we`, `grid.worked.ns/we`, `grid.selected.ns/we`, `grid.coastline.ns/we`, `grid.borders.n/e/s/w`, `grid.unavailable`, `grid.nonnative`.

**Cursors and goto**: `cursor.<goto|patrol|paradrop|nuke|select|invalid|attack|edit_paint|edit_add|wait|teleport>0..5` (32x32 with hot spot). Goto path markers: `path.step`, `path.normal`, `path.exhausted_mp`, `path.waypoint`. Also `user.attention`, `user.infratile`.

The UI sets — `misc/small`, `events`, `governments`, `specialists`, `buildings-large`, `wonders-large`, `techs`, `treaty`, `space`, `editor`, `icons`, `shields-large` — can be borrowed unchanged from stock.

## 4. Lessons for image-model prompts

- **Diamond.** 96x48, a 2:1 ratio with ≈26.6° edges. A square source of about 67.9 px per side becomes 96x48 after a 45° rotation and 50% vertical squash. North of the map is the screen's upper-right edge, because `DIR8_NORTH` is drawn from the top vertex to the right vertex (FCW-js/2dcanvas/mapview.js `mapview_put_grid_line`). So west is screen upper-left and east is screen lower-right.
- **Unit anchor.** The 64x48 sprite is drawn at (19, −6) in the native client (S32-data/amplio2.tilespec `unit_offset_*`; `client/tilespec.c` FULL_TILE offsets). So the feet or hull sit about 6 px above the bottom vertex and the sprite is roughly centred. FCW's web client draws units at (+16, −11) and adds per-unit tweaks for unit, shield and badge positions (FCW-js/2dcanvas/tilespec.js `create_unit_offset_arrays`).
- **Unit framing.** Units fill most of the 64x48 cell (alpha bounds about x 0–64, y 5–48). Keep the upper-left corner clear: the nation shield is drawn at (25, 16) and the HP bar sits above it (`unit_flag_offset_*`). Activity icons go at (49, 0). Prompt for: one subject, three-quarter view facing left, soft grey drop shadow to the lower-right, transparent background, no ground plane.
- **City anchor.** 96x72, drawn at (0, −24). The footprint stays inside the diamond; buildings rise up to 24 px above the tile top. Small cities are compact clusters (alpha bounds about 44x26); size 4 fills most of the cell. The city flag goes at (2, 9). Prompt for: an isometric town block on a diamond plot, light from the upper-left, lit south-west faces, shaded south-east faces.
- **Terrain features are overlays, never full tiles.** Hills are about 75x41 lumps on a transparent background over a green bg base. Mountains are 96x66 tall sprites (`layer1_is_tall`) whose rock peaks rise about 18 px above the tile, with a grassy apron at the base. Forest and jungle are tree clusters with shadows cast to the right. All of these come in 16 forms keyed by same-type neighbours, so ridges and canopies run continuously across tiles (hills.spec, mountains.spec, terrain2.spec). Prompt each as an isolated object with a soft, irregular footprint fading into transparency. Never fill the diamond to its edges.
- **Light.** Upper-left key light, shadows right and lower-right, no hard cast shadow on base ground.
- **Palette** (mean colours of amplio2 bases, S32-data/amplio2/terrain1.png and ocean.png):

  | Terrain | Mean colour |
  |---|---|
  | desert | #cebd91 |
  | plains / forest bg / jungle bg | #7c9d30 |
  | grassland | #4d8f2e |
  | hills / mountains bg | #809a4f |
  | tundra | #a2a484 |
  | arctic | #eff3f3 |
  | swamp | #5d7153 |
  | shallow sea | #1d40a2 |
  | deep sea | #00197f |

  The palette is saturated and bright, Civ2-like. Keep neighbouring base colours close enough in value that a pixel dither between them reads as a soft edge.

## 5. Other things that make iso terrain look good

- **Dither mask.** `t.dither_tile` is a 96x48 alpha mask whose noise is concentrated in a band along the diamond edges (thicker on the upper-left). The client cuts each neighbour's base sprite into quarters through this mask and draws them over the tile edges (`client/tilespec.c` ~4374–4392; `blend_layer` in the tilespec). For painted art, a softer noise band (8–12 px) hides seams better than amplio2's sparse speckle. Seams were still visible in FCW's own screenshot (`fcw.org-server/fcw-2021.png`). Only the first base variant is used as the blender, so variant 1 should be the most "average" tile.
- **Corner darkness and fog.** There are 81 fog sprites, one per combination of the four corner states. Fogged areas are black at about 52% alpha (alpha 133), unknown areas are opaque black, and the corners grade between them (S32-data/amplio2/fog.png, by Yautja). This gives smooth edges to unexplored areas without any per-terrain art.
- **Coast cells.** Water tiles carry the beach, foam and lighter shallows on their land-facing quarters, so land art never has to know about water (ocean.png, 81 cellgroups). Keep land textures borderless.
- **Variation.** Randomly chosen whole-tile variants plus sparse decals (FCW's 16 per terrain, mostly empty space) remove grid repetition cheaply. Keep decals small (10–20 px), with soft alpha and the same lighting as the overlays.
- **Edges.** Base diamonds use hard 1-bit edges for exact tiling. Overlays use soft partial alpha (164–570 semi-transparent pixels per sprite in hills and desert) so they sit into the ground.
- **No smoothing.** FCW turns image smoothing off and never rescales map sprites, so art is authored at final pixel size. If we render at 192x96, paint at 192 and don't upscale amplio2's 96 px units without a matching pass.
