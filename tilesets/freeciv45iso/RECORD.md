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

Every spec file that `amplio2.tilespec` lists under `amplio2/`, except `terrain2.spec`, `ocean.spec` (the forest and jungle overlays
and ocean cells the painted ground replaces), is re-cut from Freeciv 3.2.6's amplio2 tileset (GPL-2.0-or-later; the artists are
named in each spec's `[info]` section, copied verbatim): each sprite scaled 2x with nearest-neighbour sampling, so it
looks as amplio2 does on a 2x screen today. `water.spec` keeps only the rivers. `hills.spec` and `mountains.spec` are the relief
over the flat hills and mountains ground (issue 194), moved from layer 1 to layer 2. `misc/citybar` and `misc/overlays`
are re-cut too, because the client draws them on the map; the other `misc/` files are read from the installed data.

| spec | source | scaling | sheet |
|---|---|---|---|
| `freeciv45iso/terrain1.spec` | `amplio2/terrain1.spec` (62 tags, 1 grids) | nearest 2x | 1728x1536 |
| `freeciv45iso/maglev.spec` | `amplio2/maglev.spec` (9 tags, 1 grids) | nearest 2x | 1728x96 |
| `freeciv45iso/hills.spec` | `amplio2/hills.spec` (16 tags, 1 grids) | nearest 2x | 768x384 |
| `freeciv45iso/mountains.spec` | `amplio2/mountains.spec` (16 tags, 1 grids) | nearest 2x | 768x528 |
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
| `freeciv45iso/terrain45.spec` | `run6` (grassland_and_plains.png): plains 10, hills 5, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run8` (forest_and_jungle.png): forest 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run9` (forest_and_jungle.png): forest_tundra 3, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run10` (shallow_ocean_and_lake.png): coast 15, lake 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run11` (deep_ocean_and_impassable.png): floor 15, inaccessible 5, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run12` (desert_and_tundra.png): mountains 5, desert 15, tundra 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run13` (glacier_and_swamp.png): arctic 15, swamp 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run14` (shores_and_banks.png): plains 5, desert 5, tundra 5, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run15` (grassland_and_plains.png): grassland 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| `freeciv45iso/terrain45.spec` | `run17` (forest_and_jungle.png): jungle 10, through `seamless.py` | LANCZOS 192, level | 960x6336 |
| tone match | on | mean luma per variant at 192 px, min-max | grassland 92-116 -> 104-104; plains 122-196 -> 158-158; forest 68-103 -> 83-83; jungle 54-75 -> 64-64; hills 132-196 -> 168-169; mountains 166-176 -> 171-171; desert 166-182 -> 175-175; tundra 115-142 -> 127-127; arctic 191-197 -> 193-193; swamp 68-73 -> 70-71; coast 120-130 -> 125-126; lake 73-77 -> 74-75; floor 29-33 -> 32-32; inaccessible 67-69 -> 68-68; forest_tundra 56-63 -> 60-61 |
| `freeciv45iso/terrain45.spec` | the cells above, each turned 45 degrees and squashed 2:1 (to_iso, 4x4 samples, binary outline) | 192x96 diamonds | 960x3168 |
| `freeciv45iso/coast.spec` | `run14` r1c3 (shores_and_banks.png), through `seamless.py`: beach cells for water tiles next to land, layer 1 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | `run14` r1c3 (shores_and_banks.png), through `seamless.py`: sand cells for land tiles next to water, layer 1 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | `run13` r1c1 (glacier_and_swamp.png), through `seamless.py`: ice cells for water tiles next to glacier, layer 2 | generated, 96 px quarter cells | 3072x288 |
| `freeciv45iso/coast.spec` | the shore cells above as isometric corner cells (to_iso, each quarter padded by its own edge) | 96x48 cells | 3072x144 |
| `freeciv45iso/blend.spec` | generated: freeciv45test's `t.blend_mask` and `_2`-`_4` (seeds 1-4) turned per tile; `mask.tile`, the diamond | none | 2304x384 |
