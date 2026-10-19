# freeciv45iso: where every sprite came from

The isometric Freeciv45 tileset (issue 190): 192x96 diamonds at `pixel_ratio = 2`, amplio2's tile doubled, so the
patched Qt client shows each tile at amplio2's size and, on a Retina screen, draws every pixel. Built by
`tilesets/make-freeciv45iso.py`, which imports `make-freeciv45test.py` for the painted cells; nothing in this folder but
the files it writes. Rebuild with (`T` is the art repo's `freeciv45/01_terrain_ground`)

    python3.14 -I tilesets/make-freeciv45iso.py --data ~/freeciv-builds/qt/share/freeciv --art $T

When new runs of the painted ground land, add them to `PANELS` and `PLAN` in `make-freeciv45test.py` and rebuild
both tilesets: the iso cells come from the same cut.

Licence of the whole folder: GPL-2.0-or-later, like Freeciv, amplio2 and the Freeciv45 art pack. Soft edges between
terrains need the fork's patch 0033 (an unpatched client blends through amplio2's `t.dither_tile`).

## From amplio2, scaled

Every spec file that `amplio2.tilespec` lists under `amplio2/`, except `terrain2.spec`, `ocean.spec` (cells the painted ground
replaces), is re-cut from Freeciv 3.2.6's amplio2 tileset (GPL-2.0-or-later; the artists are
named in each spec's `[info]` section, copied verbatim): each sprite scaled 2x with nearest-neighbour sampling, so it
looks as amplio2 does on a 2x screen today. `water.spec` keeps only the rivers. `hills.spec` and `mountains.spec` are the relief
over the flat hills and mountains ground (issue 194), moved from layer 1 to layer 2. `misc/citybar` and `misc/overlays`
are re-cut too, because the client draws them on the map; the other `misc/` files are read from the installed data.

| spec | source | scaling | sheet |
|---|---|---|---|
| `freeciv45iso/terrain1.spec` | `amplio2/terrain1.spec` (41 tags, 1 grids) | nearest 2x | 1728x1536 |
| `freeciv45iso/maglev.spec` | `amplio2/maglev.spec` (9 tags, 1 grids) | nearest 2x | 1728x96 |
| `freeciv45iso/water.spec` | `amplio2/water.spec` (20 tags, 1 grids) | nearest 2x | 1536x480 |
| `freeciv45iso/volcano.spec` | `amplio2/volcano.spec` (3 tags, 1 grids) | nearest 2x | 192x288 |
| `freeciv45iso/tiles.spec` | `amplio2/tiles.spec` (76 tags, 1 grids) | nearest 2x | 2112x672 |
| `freeciv45iso/upkeep.spec` | `amplio2/upkeep.spec` (40 tags, 1 grids) | nearest 2x | 1920x152 |
| `freeciv45iso/activities.spec` | `amplio2/activities.spec` (28 tags, 1 grids) | nearest 2x | 280x288 |
| `freeciv45iso/fog.spec` | `amplio2/fog.spec` (80 tags, 1 grids) | nearest 2x | 1728x864 |
| `freeciv45iso/units.spec` | `amplio2/units.spec` (57 tags, 1 grids) | nearest 2x | 2560x288 |
| `freeciv45iso/extra_units.spec` | `amplio2/extra_units.spec` (107 tags, 1 grids) | nearest 2x | 1920x1056 |
| `freeciv45iso/animals.spec` | `amplio2/animals.spec` (7 tags, 1 grids) | nearest 2x | 384x288 |
| `freeciv45iso/veterancy.spec` | `amplio2/veterancy.spec` (11 tags, 1 grids) | nearest 2x | 1408x96 |
| `freeciv45iso/nuke.spec` | `amplio2/nuke.spec` (1 tags, 1 grids) | nearest 2x | 360x352 |
| `freeciv45iso/explosions.spec` | `amplio2/explosions.spec` (5 tags, 1 grids) | nearest 2x | 60x300 |
| `freeciv45iso/cities.spec` | `amplio2/cities.spec` (100 tags, 1 grids) | nearest 2x | 1920x1440 |
| `freeciv45iso/bases.spec` | `amplio2/bases.spec` (28 tags, 1 grids) | nearest 2x | 1344x432 |
| `freeciv45iso/select.spec` | `amplio2/select.spec` (4 tags, 1 grids) | nearest 2x | 768x96 |
| `freeciv45iso/grid.spec` | `amplio2/grid.spec` (16 tags, 1 grids) | nearest 2x | 1152x288 |
| `freeciv45iso/overlays.spec` | `misc/overlays.spec` (6 tags, 1 grids) | nearest 3x | 1152x384 |
| `freeciv45iso/citybar.spec` | `misc/citybar.spec` (9 tags, 3 grids) | nearest 2x | 796x376 |

## Painted ground, shore and blend masks

Cut as `make-freeciv45test.py` cuts them (the same panels, cells, cutter and tone match), then turned into diamonds.

| spec | source | scaling | sheet |
|---|---|---|---|
| `freeciv45iso/terrain45.spec` | `run6` (grassland_and_plains.png): plains 10, hills 5, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run10` (shallow_ocean_and_lake.png): coast 15, lake 10, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run11` (deep_ocean_and_impassable.png): floor 15, inaccessible 5, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run12` (desert_and_tundra.png): desert 10, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run13` (glacier_and_swamp.png): arctic 15, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run14` (shores_and_banks.png): desert 5, tundra 5, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run15` (grassland_and_plains.png): grassland 10, forest 10, jungle 10, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run18` (glacier_and_swamp.png): swamp 10, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| `freeciv45iso/terrain45.spec` | `run19` (desert_and_tundra.png): mountains 5, desert 5, tundra 10, forest_tundra 5, through `seamless.py` | LANCZOS 192, level | 960x6144 |
| tone match | on | mean luma per variant at 192 px, min-max | grassland 92-116 -> 104-104; plains 85-166 -> 128-128; forest 92-116 -> 104-104; jungle 92-116 -> 104-104; hills 98-164 -> 134-134; mountains 176-178 -> 177-177; desert 173-182 -> 176-176; tundra 115-132 -> 123-124; arctic 191-197 -> 193-193; swamp 74-76 -> 75-75; coast 120-130 -> 125-126; lake 73-77 -> 74-75; floor 29-33 -> 32-32; inaccessible 67-69 -> 68-68; forest_tundra 119-132 -> 126-127 |
| `freeciv45iso/terrain45.spec` | the cells above, each turned 45 degrees and squashed 2:1 (to_iso, 4x4 samples, binary outline); graded in Lab: floor +28 +2 -20, desert +0 -12 -14, mountains -6 -13 -32 | 192x96 diamonds | 960x3072 |
| `freeciv45iso/resources.spec` | the art pack's resource props (`freeciv45/03_resources`, cut by `tools/props.py`), one pick per tag: wheat `run1/wheat_1`, buffalo `run1/buffalo_1`, horses `run1/horses_1`, grassland_resources `run1/grassland_resources_2`, fruit `run1/fruit_1`, gems `run2/gems_1`, oasis `run1/oasis_1`, oil `run2/oil_1`, pheasant `run1/pheasant_1`, silk `run2/silk_1`, coal `run2/coal_2`, wine `run2/wine_1`, gold `run2/gold_1`, iron `run2/iron_1`, tundra_game `run1/tundra_game_2`, furs `run1/furs_1`, arctic_ivory `run1/arctic_ivory_1`, peat `run2/peat_1`, spice `run2/spice_1`, fish `run1/fish_2`, whales `run1/whales_1` | none (as cut, 192x96) | 960x480 |
| `freeciv45iso/coast.spec` | `run14` r1c3 (shores_and_banks.png), through `seamless.py`: beach cells for water tiles next to land, layer 1 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | `run14` r1c3 (shores_and_banks.png), through `seamless.py`: sand cells for land tiles next to water, layer 1 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | `run13` r1c1 (glacier_and_swamp.png), through `seamless.py`: ice cells for water tiles next to glacier, layer 2 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | the shore cells above as isometric corner cells (to_iso, each quarter padded by its own edge) | 96x48 cells | 3072x144 |
| `freeciv45iso/blend.spec` | generated: freeciv45test's `t.blend_mask` and `_2`-`_4` (seeds 1-4) turned per tile; `mask.tile`, the diamond | none | 2304x384 |
| `freeciv45iso/features.spec` | the art pack's standing props (`freeciv45/02_terrain_features`, runs 4-8, `post/raw`): `clump_broadleaf_1`, `clump_broadleaf_2`, `clump_jungle_1`, `clump_jungle_2`, `clump_jungle_3`, `clump_jungle_4`, `clump_mixed_1`, `clump_pine_1`, `clump_pine_2`, `cluster_dry_1`, `cluster_green_1`, `cluster_green_2`, `cluster_green_3`, `cluster_green_4`, `cluster_green_5`, `cluster_rocky_1`, `peak_cold_1`, `peak_cold_2`, `peak_cold_3`, `peak_cold_4`, `peak_cold_5`, `peak_dark_1`, `peak_dark_2`, `peak_dark_3`, `peak_dark_4`, `peak_dark_5`, `peak_tipped_1`, `peak_tipped_2`, `peak_tipped_3`, `peak_tipped_4`, `peak_tipped_5`, `peak_warm_broad`, `peak_warm_sharp`, `peak_warm_stepped`, `peak_warm_twin`, `peak_warm_worn`, `range_l1`, `range_l2`, `range_l3`, `range_l4`, `range_l5`, `range_r1`, `range_r2`, `range_r3`, `range_r4`, `range_r5`, `ridge_dry_l1`, `ridge_dry_l2`, `ridge_dry_r1`, `ridge_dry_r2`, `ridge_green_l1`, `ridge_green_l2`, `ridge_green_l3`, `ridge_green_l4`, `ridge_green_l5`, `ridge_green_r1`, `ridge_green_r2`, `ridge_green_r3`, `ridge_green_r4`, `ridge_green_r5`, `ridge_rocky_l1`, `ridge_rocky_l2`, `ridge_rocky_r1`, `ridge_rocky_r2`, `stand_autumn_1`, `stand_autumn_2`, `stand_autumn_3`, `stand_broadleaf_1`, `stand_broadleaf_2`, `stand_broadleaf_3`, `stand_broadleaf_4`, `stand_broadleaf_5`, `stand_jungle_1`, `stand_jungle_2`, `stand_jungle_3`, `stand_jungle_4`, `stand_jungle_5`, `stand_jungle_palm_1`, `stand_jungle_palm_2`, `stand_jungle_tall_2`, `stand_mangrove_1`, `stand_mangrove_2`, `stand_mixed_1`, `stand_mixed_2`, `stand_mixed_3`, `stand_mixed_4`, `stand_mixed_5`, `stand_pine_1`, `stand_pine_2`, `stand_pine_3`, `stand_pine_4`, `stand_pine_5`, `stand_reeds_1`, `stand_reeds_2`, `stand_snags_1`, `stand_snowpine_1`, `stand_snowpine_2`, `swamp_reed_tuft`, `swamp_sedge`, `swamp_small_snag`; variants forest 33, forest_tundra 7, jungle 13, swamp 10, hills 6, hills_desert 1, mountains 10, mountains_tundra 5, inaccessible 5; ridges and ranges per grid line hills 7, hills_desert 2, mountains 5, mountains_tundra 5 | LANCZOS (TREES and RELIEF2 scales) | 1920x1728 |

## Resources

`resources.spec` / `resources.png`: the 21 resource sprites, one per `ts.*` tag of civ45's `terrain.ruleset`, from the Freeciv45 art pack (John O'Dell's sheet workflow with OpenAI image generation through Codex, art repo folder `freeciv45/03_resources`, runs 1 and 2, the picks in its `RESOURCES.md`). Each is an isometric prop on a transparent 192x96 tile, cut by the art repo's `tools/props.py` (standing on the tile's foot point, soft contact shadow) and copied unchanged. Only the picks the tileset draws are copied: no alternates, panels or 1x copies. They replace amplio2's resource sprites of the same tags (issue 206). GPL-2.0-or-later, like the rest of the folder.

## Trees, hills and mountains

`features.spec` / `features.png`: forest, jungle, swamp, hills, mountains and inaccessible drawn with the Freeciv45 art pack's standing props (John O'Dell's sheet workflow with OpenAI image generation through Codex, art repo folder `freeciv45/02_terrain_features`, runs 5 to 8 and run 4's dark peaks, placed as its `TREES_AND_RELIEF_2.md` says). The props are stood (a stand of trees with a clump, or one hill or mountain) on 192x144 full tiles in a few variants per terrain, so the client draws one sprite per tile on layer 2; hills and mountains draw a ridge or range along the grid line their own kind continues on (issues 224 and 229, patch 0034). Only these 100 props are used, and only inside the baked variants: `clump_broadleaf_1`, `clump_broadleaf_2`, `clump_jungle_1`, `clump_jungle_2`, `clump_jungle_3`, `clump_jungle_4`, `clump_mixed_1`, `clump_pine_1`, `clump_pine_2`, `cluster_dry_1`, `cluster_green_1`, `cluster_green_2`, `cluster_green_3`, `cluster_green_4`, `cluster_green_5`, `cluster_rocky_1`, `peak_cold_1`, `peak_cold_2`, `peak_cold_3`, `peak_cold_4`, `peak_cold_5`, `peak_dark_1`, `peak_dark_2`, `peak_dark_3`, `peak_dark_4`, `peak_dark_5`, `peak_tipped_1`, `peak_tipped_2`, `peak_tipped_3`, `peak_tipped_4`, `peak_tipped_5`, `peak_warm_broad`, `peak_warm_sharp`, `peak_warm_stepped`, `peak_warm_twin`, `peak_warm_worn`, `range_l1`, `range_l2`, `range_l3`, `range_l4`, `range_l5`, `range_r1`, `range_r2`, `range_r3`, `range_r4`, `range_r5`, `ridge_dry_l1`, `ridge_dry_l2`, `ridge_dry_r1`, `ridge_dry_r2`, `ridge_green_l1`, `ridge_green_l2`, `ridge_green_l3`, `ridge_green_l4`, `ridge_green_l5`, `ridge_green_r1`, `ridge_green_r2`, `ridge_green_r3`, `ridge_green_r4`, `ridge_green_r5`, `ridge_rocky_l1`, `ridge_rocky_l2`, `ridge_rocky_r1`, `ridge_rocky_r2`, `stand_autumn_1`, `stand_autumn_2`, `stand_autumn_3`, `stand_broadleaf_1`, `stand_broadleaf_2`, `stand_broadleaf_3`, `stand_broadleaf_4`, `stand_broadleaf_5`, `stand_jungle_1`, `stand_jungle_2`, `stand_jungle_3`, `stand_jungle_4`, `stand_jungle_5`, `stand_jungle_palm_1`, `stand_jungle_palm_2`, `stand_jungle_tall_2`, `stand_mangrove_1`, `stand_mangrove_2`, `stand_mixed_1`, `stand_mixed_2`, `stand_mixed_3`, `stand_mixed_4`, `stand_mixed_5`, `stand_pine_1`, `stand_pine_2`, `stand_pine_3`, `stand_pine_4`, `stand_pine_5`, `stand_reeds_1`, `stand_reeds_2`, `stand_snags_1`, `stand_snowpine_1`, `stand_snowpine_2`, `swamp_reed_tuft`, `swamp_sedge`, `swamp_small_snag`. No panels, alternates or other files from the art repo. GPL-2.0-or-later, like the rest of the folder.
