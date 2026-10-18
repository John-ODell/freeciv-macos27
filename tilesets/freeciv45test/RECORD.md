# freeciv45test: where every sprite came from

A test tileset for Freeciv45 (plan rows T0 and T1 in `notes/freeciv45-plan.md`): 96 px overhead squares,
`is_hex FALSE`. Built by `tilesets/make-freeciv45test.py`; nothing in this folder but this file is hand-edited.
Rebuild with (`T` is the art repo's `freeciv45/01_terrain_ground`)

    python3.14 -I tilesets/make-freeciv45test.py --data ~/freeciv-builds/qt/share/freeciv \
        --panel $T/run6/panel1/grassland_and_plains.png --panel4 $T/run8/panel4/forest_and_jungle.png \
        --panel4-retake $T/run9/panel4/forest_and_jungle.png --cutter ~/Desktop/asset_generator/freeciv45/tools/seamless.py

(`--no-tone-match` gives the build from before issue 138, byte for byte.)

Licence of the whole folder: GPL-2.0-or-later, like Freeciv and like the Freeciv45 art pack.

## Placeholders: trident, scaled

Every spec file that `trident.tilespec` lists under `trident/` is re-cut from Freeciv 3.2.6's trident tileset
(GPL-2.0-or-later, artists named in each spec's `[info]` section, copied verbatim): each sprite is cropped from
the 30 px sheet, scaled 3.2x with nearest-neighbour sampling, and laid out again on a clean grid (no pixel
border), so the tags are trident's with new coordinates. The `misc/` spec files are not copied; the tilespec
reads them from the installed data like trident does.

| spec | source | scaling | sheet |
|---|---|---|---|
| `tiles.spec` | `trident/tiles.spec` (672 tags, 3 grids; `t.l0.grassland1` dropped, see below) | nearest 3.2x | 1920x2544 |
| `earth.spec` | `trident/earth.spec` (6 tags) | nearest 3.2x | 288x192 |
| `units.spec` | `trident/units.spec` (57 tags) | nearest 3.2x | 1920x288 |
| `extra_units.spec` | `trident/extra_units.spec` (115 tags) | nearest 3.2x | 1440x1056 |
| `select.spec` | `trident/select.spec` (4 tags) | nearest 3.2x | 384x96 |
| `grid.spec` | `trident/grid.spec` (16 tags) | nearest 3.2x | 576x288 |
| `roads.spec` | `trident/roads.spec` (101 tags, 3 grids) | nearest 3.2x | 1728x768 |
| `highways.spec` | `trident/highways.spec` (35 tags) | nearest 3.2x | 1728x192 |
| `fog.spec` | `trident/fog.spec` (80 tags) | nearest 3.2x | 864x864 |
| `cities.spec` | `trident/cities.spec` (44 tags) | nearest 3.2x | 480x864 |
| `explosions.spec` | `trident/explosions.spec` (5 tags) | nearest 3.2x | 96x480 |

`freeciv45test.tilespec` is `trident.tilespec` with the tile size 96, the pixel offsets scaled (stack size
number, city bar, tile label, upkeep), the file list renamed, `terrain45.spec` added after `tiles.spec`, and
`[tile_plains]`, `[tile_forest]` and `[tile_jungle]` without `layer0_match_with`, so they draw from numbered
variants like grassland instead of trident's 16 edge-matched sprites (which stay in `tiles.spec`, unused).

## Painted ground: run 6 of panel 1

`terrain45.spec` / `terrain45.png` (480x768, rows 0-3 of it): 20 cells of `grassland_and_plains.png`, run 6 of panel 1 of the
Freeciv45 terrain sheet, made 2026-10-17 with John's ChatGPT sheet workflow (OpenAI image_gen through Codex,
prompts and checks in that run's RECORD.md) in the Brothers-Keeper-Art repo, commit 26f6afc on branch
`docs/20-run6-panel1`, folder `freeciv45/01_terrain_ground/run6/panel1/`. The panel is 1254x1254, a 5x5
grid; rows 1-2 are grassland, 3-4 plains, 5 damp grassland (not used here). Each cell is cut with the art
repo's `tools/seamless.py` (3 px inset, square, 192 px LANCZOS master, edges wrapped by its half-shift blend)
and then scaled to 96 px with LANCZOS.

| tag | panel cell | tag | panel cell |
|---|---|---|---|
| `t.l0.grassland1`-`5` | r1c1-r1c5 | `t.l0.plains1`-`5` | r3c1-r3c5 |
| `t.l0.grassland6`-`10` | r2c1-r2c5 | `t.l0.plains6`-`10` | r4c1-r4c5 |

The client picks one variant per tile from the tile index (`client/tilespec.c`, `MATCH_NONE`).
Licence inputs: the panel is original generated art, intended GPL-2.0-or-later; its look reference
(`references/inspiration/terrain-3x3-ai-grid.webp`, licence unknown) was inspiration only and no pixel of it
is in the panel or here.

## Painted forest and jungle: runs 8 and 9 of panel 4

Rows 4-7 of `terrain45.png`: 20 cells of `forest_and_jungle.png`, panel 4 of the same sheet (forest and jungle),
made 2026-10-17 with the same workflow, in the Brothers-Keeper-Art repo on main: run 8
(`freeciv45/01_terrain_ground/run8/panel4/`, commit 62d9b9f, PR 31) for rows 1-3 and run 9's retake
(`run9/panel4/`, commit 1f5634f, PR 34) for row 4. Both panels are 1254x1254, 5x5. Cut the same way as panel 1
(`tools/seamless.py` at commit 58d08c9: 3 px inset, 192 px LANCZOS master, half-shift wrap; then 96 px LANCZOS);
before the tone match below, every cell is pixel-identical to `seamless.py PANEL OUT --all --size 192 --inset 3`
scaled to 96 px.

| tag | panel cell | tag | panel cell |
|---|---|---|---|
| `t.l0.forest1`-`5` | run 8 r1c1-r1c5 (r1c2, r1c4 with a few pines) | `t.l0.jungle1`-`5` | run 8 r3c1-r3c5 |
| `t.l0.forest6`-`10` | run 8 r2c1-r2c5 (r2c2, r2c4 autumn) | `t.l0.jungle6`-`10` | run 9 r4c1-r4c5 |

Not used: run 8 rows 4-5 (replaced by run 9's retake), run 9 rows 1-3 (the retake was for rows 4 and 5 only), and
run 9 row 5, the pine. Its cool blue-green c1-c3 would only fit forest next to tundra or glacier, which the tilespec
cannot select (freeciv-macos27 issue 127); its warm olive c4-c5 shows as a patchwork among the broadleaf cells in
game (`--olive-pine` adds them as `forest11`-`12` for that test; see `notes/freeciv45/tileset-t0.md`).
Licence inputs: original generated art, intended GPL-2.0-or-later; John's iPhone forest picture and the 3x3 grid
reference were inspiration only (run 8's RECORD.md), and no pixel of them is in the panels or here.

## Tone match of the variants (issue 138)

The client puts any two variants of a terrain side by side, so a field showed every tile boundary as a straight
step in brightness and colour. Since issue 138 the build matches the 192 px masters of each terrain to each other
before scaling them to 96 px (`match_tone` in the script): in CIE Lab (Pillow's ImageCms, sRGB profile) each
channel of each cell is mapped linearly so that its mean is the mean of the terrain's cells and its standard
deviation the mean of their standard deviations, the contrast scale held to 0.75-1.33 so a cell keeps its own
texture. Only the levels change; no pixel moves. Mean luma per variant at 96 px, before and after:

| terrain | before (min-max) | after |
|---|---|---|
| grassland (10) | 85-166 | 128 |
| plains (10) | 122-196 | 166 |
| forest (10) | 68-103 | 83 |
| jungle (10) | 50-76 | 62 |

The two autumn forest cells (r2c2, r2c4) are pulled towards the forest's green with the rest: their orange crowns
are still there but quieter. Results in game: `notes/freeciv45/tileset-t0.md`, "Variants matched in tone".
