# freeciv45test: where every sprite came from

A test tileset for Freeciv45 (plan rows T0 and T1 in `notes/freeciv45-plan.md`): 96 px overhead squares,
`is_hex FALSE`. Built by `tilesets/make-freeciv45test.py`; nothing in this folder is hand-edited. Rebuild with

    python3.14 -I tilesets/make-freeciv45test.py --data ~/freeciv-builds/qt/share/freeciv \
        --panel <run 6 panel 1>/grassland_and_plains.png --cutter ~/Desktop/asset_generator/freeciv45/tools/seamless.py

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
`[tile_plains]` without `layer0_match_with`, so plains draw from numbered variants like grassland instead of
trident's 16 edge-matched sprites (which stay in `tiles.spec`, unused).

## Painted ground: run 6 of panel 1

`terrain45.spec` / `terrain45.png` (480x384): 20 cells of `grassland_and_plains.png`, run 6 of panel 1 of the
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
