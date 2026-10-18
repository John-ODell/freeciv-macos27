# Tileset T0: painted ground in the Qt client (issue 74, 2026-10-17)

The first look at Freeciv45's own tileset format in a running game: `tilesets/freeciv45test`, 96 px overhead
squares, every tag the civ45 ruleset needs (trident's sprites scaled 3.2x as placeholders) and the grassland and
plains ground from run 6 of the painted terrain sheet, ten variants each. Where each sprite came from is in
`tilesets/freeciv45test/RECORD.md`; `tilesets/make-freeciv45test.py` rebuilds it. This covers plan row T0 and
the loading half of T1 (`notes/freeciv45-plan.md`, "Look").

## How it was run

`scripts/tileset-look.sh logs/tileset-t0-run4` (the script is new in this change): a local server from
`~/freeciv-builds/qt` plays civ45 (its installed copy) on a size 3 map with `revealmap START`, seeds 7 and 7,
aifill 4; the Qt client autoconnects with `-t freeciv45test` and `FREECIV_DATA_PATH` starting with this repo's
`tilesets/`, on its own options file. After the start every client window is captured, then the human's first
unit is moved one tile east three times from the server's Lua console (`unit:move`), with captures 0.3 s, 0.8 s
and 3 s after each move. The client's `smooth_move_unit_msec` is set to 1500 for the run so a move animation
would be long enough to capture. Runs 1-4 and two auto-accept runs are in `logs/tileset-t0-*` (git-ignored);
the three pictures kept are in `notes/freeciv45/tileset-t0/`:

- `map-start.jpg`: the map at turn 1, half size.
- `painted-ground-1to1.png`: a 1:1 crop (Retina pixels, so each 96 px tile is 192 screen pixels) with painted
  plains and grassland next to trident's water, swamp and coast.
- `moves.jpg`: crops around the start stack: the map before, then 0.3 s, 0.8 s and 3 s after move 1, and 0.3 s
  and 3 s after moves 2 and 3.

For John's own client: `~/.freeciv/3.2/freeciv45test.tilespec` and `~/.freeciv/3.2/freeciv45test` are symlinks
into this repo (logged in `notes/installed.md`), so `freeciv-qt -t freeciv45test` or the tileset menu finds it.

## What works

- The client loads the tileset complete with civ45: no missing-sprite error, no warning (run 1 had one
  duplicate-tag warning, fixed by dropping trident's `t.l0.grassland1` from the re-cut `tiles.spec`).
- The painted ground draws and the variants show: adjacent plains and grassland tiles differ in shade. The
  client's variant choice (tile index hashed, `client/tilespec.c` `MATCH_NONE`) spreads the ten cells well.
- Three units of movement on the new ground (`moves.jpg`): the explorer leaves the stack, the stack keeps its
  "+2 units" label, the focus box follows. Nothing broke at 96 px: coast cells (48 px corners), the 288 px nuke
  sprite grid, roads, rivers, fog, city sprites and the unit sheet with its 1 px borders all re-cut cleanly.
- Trident's unit sprites at 3.2x nearest are blocky but readable; the selection box, hit point bar and flag
  sit where they should.

## What looks wrong

1. **Hue of the grassland.** At map scale the run 6 meadow reads olive to yellow-green and is close to the
   plains in tone; next to trident's saturated green hills and forest it looks dry. The 30 % check in the
   run's RECORD.md saw the same ("not strictly monotonic", flower drifts). A judgement for the next sheet run:
   grassland wants more green than gold.
2. **Straight tile edges between variants.** Each cell is seamless with itself, but the ten cells differ in
   brightness, so a 2 x 2 block of different variants shows its tile boundaries as straight lines
   (`painted-ground-1to1.png`, the three plains in a row). Rule for the sheet: variants of one terrain need the
   same edge tone and density, or the cutter needs a cross-variant blend. Filed in the art repo
   (Brothers-Keeper-Art issue 26, with findings 1 and 3).
3. **Cutter ghosting.** The half-shift blend leaves a faint cross and doubled marks in the middle band of
   some cells; at 96 px it is faint but visible once seen (r2c3's light patch, the plains' earth patches).
4. **Scale at 96 px.** The LANCZOS 192 to 96 step keeps the painted detail; nothing is blurry, but the
   finest marks turn to noise. 96 px masters cut straight from the panel (about 240 px interior per cell) would
   skip a resample; worth comparing in T1 (#81). One caveat on every blur judgement here: the Qt map ignores
   the display's pixel ratio (plan row Q1), so on this Retina screen the whole map is drawn at 1x and shown
   doubled; the softness that adds is the client's, not the art's.
5. **Trident on top of paint.** Rivers (blue strokes with green banks) and the coast cells (a green fringe
   around land) are trident's, so a gold plains tile by the sea or on a river gets a green border and a
   pixel-art river through it. Hills, forest, mountains and the specials are whole trident tiles, so the map
   is mostly 1991 pixel art with painted patches. All of that is T1's placeholder work (#81); the painted ground
   itself is fine.
6. **No move animation in Qt.** With `smooth_move_unit_msec` at 1500 the frames 0.3 s and 0.8 s after the
   move still show the unit on its old tile, and the 3 s frame shows it on the new one, with no in-between
   frame in any of the three moves (and the pixel diff between the 0.3 s and 0.8 s frames is empty). The
   generic animation loop (`client/mapview_common.c:2716`, `move_unit_map_canvas`) only calls Qt's
   `gui_flush`, which is `mapview_wdg->update()`, a repaint request that nothing services while the loop
   blocks; only the GTK clients set `frame_by_frame_animation`. So the client freezes for the animation time,
   then the unit jumps. This confirms plan row Q1 (#82); the default 30 ms makes the freeze invisible.
7. **The tileset suggestion dialog** still pops ("Modpack suggests using trident", issue 53); it is a separate
   window, so the map capture is clean, but a player who clicks "Load tileset" leaves the test tileset.
8. **One client crash.** Run 3's client crashed 1.5 s after launch (crash report
   `~/Library/Logs/DiagnosticReports/freeciv-qt-2026-10-17-153034.ips`, `EXC_BAD_ACCESS` at 0x8, stack
   `client_handle_packet` into the tileset setup near `tileset_setup_city_tiles`; the build has no debug
   symbols, so the names are the nearest exports) right after logging `Loading tileset "trident"`, which is
   the reread message, although the client was started with `-t freeciv45test` and nobody answered the
   dialog. Runs 1, 2 and 4 and the two auto-accept runs (which reread trident on purpose from freeciv45test
   and from amplio2 and did not crash) did not reproduce it. Issue 80 has the report path.

Not done: moving the unit with the client's own keyboard or mouse. macOS refuses scripted keystrokes
(`osascript is not allowed to send keystrokes`, an Accessibility grant John would have to give), so the moves
came from the server; the drawing path is the same (the client animates any unit move it is told about), but
the goto line, the keyboard handler and the click handler were not exercised.

## What T1 still needs

- Own placeholders at 96 px for everything that frames the painted ground: coast and lake cells (48 px
  corners, `t.l0.coast_cell_*`), rivers (`road.river_s_*`, 16 plus 4 outlets), roads and rails, irrigation and
  farmland, fog and darkness cells, the grid. Flat colour or scripted shapes beat scaled trident here.
- The other terrains from the next sheets (hills, forest, jungle, mountains, desert, tundra, arctic, swamp,
  and water) as numbered variants like grassland and plains; the matching sprites trident uses for them
  (`_n0e0s0w0` sets) are not needed for whole-tile variants.
- Units, cities, specials and the small overlays at 96 px (sheets 3 to 5 of the plan's T2), with
  `unit_flag_offset`, `city_flag_offset` and `occupied_offset` set for the new sprites.
- The sheet rules from findings 1 and 2 above (Brothers-Keeper-Art issue 26), and a decision on 96 px masters
  versus 192 px masters scaled. The placeholder work is issue 81; the move animation is issue 82; the script's
  hang when the server dies at start (same as harness-test.sh's old #66) is issue 79.
- A client that does not need the suggestion dialog: either `preferred = "freeciv45"` in civ45's
  `game.ruleset` once the tileset has its final name, or auto-accept.

## Forest and jungle from panel 4 (issue 126, 2026-10-17)

Panel 4 of the terrain sheet is in `freeciv45test` now: ten forest cells from run 8 rows 1-2 (r2c2 and r2c4
autumn), ten jungle cells from run 8 row 3 and run 9 row 4, cut and wired like the run 6 ground (forest and
jungle lose trident's 16 edge-matched sprites and draw numbered variants; sources in
`tilesets/freeciv45test/RECORD.md`). Pine is not in: see below.

### How it was run

Two new options in `scripts/tileset-look.sh`: `--serv LINE` adds a server setting before the start and
`--at-start LINE` sends a server command once the game runs. Natural maps put only a few forest and jungle tiles
in the start view, so the main look paints a 13 x 7 patch around the first unit (default map, seeds 7) with fog
of war off, because a fogged tile keeps the terrain the player last saw:

    PATCH='lua cmd local n = 0; for p in players_iterate() do if p:is_human() then for u in p:units_iterate() do local x0, y0 = u.tile.nat_x, u.tile.nat_y; for dy = -3, 3 do for dx = -6, 6 do local t = find.tile(x0 + dx, y0 + dy); local name = (dx <= -3 and "Grassland") or (dx <= 1 and "Forest") or "Jungle"; if t then edit.change_terrain(t, find.terrain(name)); n = n + 1 end end end; log.normal("tileset-look: patch of %d tiles around %d,%d", n, x0, y0); break end end end'
    scripts/tileset-look.sh OUT --port 5731 --moves "" --serv "set fogofwar DISABLED" --at-start "$PATCH"

(columns -6 to -3 from the unit grassland, -2 to 1 forest, 2 to 6 jungle). A generated map was checked too:
`--serv "set wetness 80" --serv "set temperature 70" --serv "set mapseed 11"`. The runs used scratch builds through
`--tilesets`; the one without olive pine is byte-identical to the committed tileset. The client loaded it with no
sprite error or warning in every run. Pictures, all from the Qt client on this Retina screen, so each 96 px tile is 192 screen
pixels:

- `forest-jungle-1to1.png`: 1:1 crop of the patch: run 6 grassland (left), forest, jungle (right).
- `forest-jungle-map.jpg`: the whole map window at 40 %.
- `generated-map-1to1.jpg`: 1:1 crop of the seed 11 map: forest (one autumn tile) and jungle among
  grassland, hills, salt flats and trident's swamp.
- `olive-pine-1to1.jpg`: the same patch with run 9's olive pine added as two more forest variants.

### What it shows

1. **Forest and jungle read right at 96 px.** The forest is a leafy broadleaf roof with crowns of mixed size;
   the two autumn cells read as autumn without shouting; the pine accents in r1c2 and r1c4 show only as a few
   darker blue-green crowns. The jungle is clearly a different terrain: darker, bluer green and finer-grained. Nothing turns to noise
   the way the finest grass marks did, because a canopy is texture at every scale.
2. **Against the run 6 grassland the forest is the better green.** Forest averages about RGB 74,109,35; the
   meadow next to it reads yellow-olive and dry. That is finding 1 above again, now with a target: grassland
   should sit between this forest and the plains, not next to the plains. The forest-grassland boundary is a
   hard straight tile edge (whole tiles, no transition), which looks like a field edge and is acceptable.
3. **The variant brightness steps show, less than on grassland.** On the 4 x 7 forest block the tile grid is
   visible softly; in the jungle it shows mostly where the darkest and lightest cells land. Mean luminance at 96 px:
   forest 68-103 (spread 35), jungle 50-76 (27), against grassland 85-166 (81) and plains 122-196 (74).
   **r3c5 is the dark outlier** as expected: luminance 50, a dark square wherever it lands; r3c1 is the light end
   (76). Every row was prompted "light to deeper green left to right", which builds the steps in.
4. **A light line across the middle of the tiles.** Besides the tile edges, many tiles show a faint light
   horizontal line half way down near their left and right edges. All 20 cells are lighter at the top than at the
   bottom (top 20 px minus bottom 20 px: +3 to +27 luminance, 16 cells +12 or more; left minus right has no
   common sign), and the cutter's half-shift wrap puts that top-meets-bottom seam across the middle. Brothers-Keeper-Art
   issue 35.
5. **Mist specks.** The pale mist puffs in r3c1 and run 9's r4c1, r4c3 and r4c5 repeat as small light specks,
   one per tile of that variant. Faint; the only detail that reads as a motif.
6. **Coasts.** Trident's green coast fringe around land now frames forest and jungle too (finding 5 above).

### Pine

Run 9's pine row is two colour families: cool blue-green c1-c3 and warm olive c4-c5.

- **Cool pine is left out.** It belongs on forest next to tundra or glacier, and Freeciv 3.2's tilespec cannot pick
  a whole-tile cell set by neighbour terrain: a whole-tile layer either picks a numbered variant by tile index or
  one of 16 sprites by whether each neighbour has the *same* match type, and whole-tile `MATCH_PAIR`/`MATCH_FULL`
  are "Not yet defined" (`fc_assert(FALSE)` in `client/tilespec.c`, loader and drawing). Corner cells with
  `MATCH_PAIR` do see neighbours, but only as quarter-tile overlays, and glacier is a `water` match on layer 1.
  The hooks that would work (a client patch for neighbour-chosen variant sets, a Boreal Forest terrain in the
  ruleset, or a latitude rule) are written up in issue 127.
- **Olive pine does not join the temperate forest.** Added as `forest11` and `forest12` (`--olive-pine`), the two
  cells show as dark squares with black gaps between star-shaped crowns among the broadleaf tiles
  (`olive-pine-1to1.jpg`; luminance 62 and 58 against 68-103): a patchwork. The committed build leaves them out.

### For the next art prompt

- Same mean lightness across all five cells of a row; put the light-dark variety inside each cell
  (Brothers-Keeper-Art issue 26, comment of 2026-10-17).
- No light gradient across a cell, top to bottom included; measure the edge bands in QA (issue 35).
- Jungle: no mist or pale patches at all; retake r3c5 at the row's mid lightness or drop it (issue 36).
- Grassland: match its green to this forest's family rather than the plains (issue 26).
- Pine: decide its terrain hook first (issue 127); if pine stays a forest look, one colour family only.

## Variants matched in tone (issue 138, 2026-10-17)

John saw hard square edges all over the painted ground. Inside one terrain they came from finding 2 above: each of
the ten cells is seamless with itself, but the cells differ in lightness and colour, so wherever the client puts
two of them side by side the boundary is a straight step. No new art was made: `tilesets/make-freeciv45test.py`
now matches the cells of each terrain to each other before it scales them to 96 px (`match_tone`: in CIE Lab each
channel of each cell gets the terrain's mean level and mean contrast, contrast scale held to 0.75-1.33; details and
the before/after luma table in `tilesets/freeciv45test/RECORD.md`). Only `terrain45.png` changes; `--no-tone-match`
rebuilds the old sheet byte for byte.

### How it was checked

A 25 x 17 field around the start stack was painted from the server's Lua console, grassland west of the stack and
forest from it eastwards, fog of war off, and the Qt client was shot through the in-process driver with no window
on screen (`QT_QPA_PLATFORM=offscreen` on a 1600 x 1000 virtual screen; the shot is the widget's own grab, so 1 px
per tileset pixel). `scripts/ui-drive.sh` takes the tileset, the extra server lines and the screen through new
`FREECIV_DRIVE_*` variables and now runs offscreen unless `FREECIV_DRIVE_VISIBLE=1`:

    FREECIV_DRIVE_PREFIX=<driver build>/qt FREECIV_DRIVE_TILESET=freeciv45test FREECIV_DRIVE_TILESETS=<build out> \
    FREECIV_DRIVE_SERV="set fogofwar DISABLED" FREECIV_DRIVE_QPA="offscreen:configfile=$PWD/notes/freeciv45/tileset-t0/screen-1600x1000.json" \
    scripts/ui-drive.sh notes/freeciv45/tileset-t0/field.txt <outdir> 5741

once with a scratch build made with `--no-tone-match` and once with the new one (the driver build is the fork at
0baacdb plus `notes/freeciv45/ui/bar-test/uidrive.diff`; same seed, so the same tiles get the same variants).
Pictures: `tileset-t0/variant-tone-before.jpg` and `variant-tone-after.jpg` (whole window, grassland left, forest
right, the chat box over the bottom left). `scripts/tile-edge-steps.py` (new) measures the tile grid in a shot: the
mean difference between the 8 px bands on either side of each tile edge, against the same measure across the
tile's middle line, which is the terrain's own variation:

| field | tile edges before | tile edges after | tile middles (both) |
|---|---|---|---|
| grassland (71 edge segments) | 30.5 | 5.2 | 7.9 |
| forest (97 edge segments) | 14.6 | 6.8 | 8.2 |

### What it looks like now

- **The patchwork is gone.** The grassland field reads as one meadow instead of a chequerboard of gold and olive
  squares, and the forest as one canopy; the tone step at a tile edge is now smaller than the variation across the
  middle of a tile.
- **Still visible, faintly:** the texture itself is cut at the edge. A clump of grass or a crown of trees stops at
  a straight line where the next cell's pattern starts, so at 1:1 a careful eye still finds the grid, more in the
  forest (big crowns) than in the meadow. Matching tone cannot fix that; a soft blend across the edge or
  edge-matched cells from the cutter could.
- **Still visible:** the light line across the middle of many cells (finding 4 above, Brothers-Keeper-Art issue 35)
  is untouched, since it is inside each cell; now that the edges are quiet it is the most visible straight line in
  the forest.
- **Autumn is quieter.** The two autumn forest cells keep their orange crowns but are pulled towards the forest's
  green with the rest; at map scale they read as a hint of autumn rather than an orange tile.
- The grassland is still gold-olive, not green (finding 1): the tone match brings every cell to the meadow's mean
  and leaves that mean alone.
- Edges between different terrains (the grassland-forest line in the pictures) are unchanged; that is issue 141's
  overhead blending.

## Terrains blended at the edge (issue 141, 2026-10-17)

The other half of John's hard edges: where two terrains meet, overhead view draws a straight line, because Freeciv
3.2 blends terrains only in isometric view (`client/tilespec.c`: the blend sprites are quarter tiles at iso offsets,
masked by `t.dither_tile`, which is loaded for isometric tilesets only; "This only works in iso-view!").

**Fork patch 0019** (`patches/0019-Tilespec-blend-neighbouring-terrains-in-overhead-vie.patch`, client only): an
overhead square tileset that provides `t.blend_mask` gets blending. The mask is 3 x 3 tiles with a terrain's own tile
in the middle and says how strongly that terrain shows in each of the eight tiles around it. For every terrain with
a blender the client crops eight whole-tile sprites from it through the mask, one per direction; a tile whose
terrain has `blend_layer` then draws, after that layer, the sprite of each neighbour of another blending terrain:
across the edge for the four sides, into the corner for the diagonals, and a corner is skipped when a side neighbour
next to it already has the corner's terrain. Without `t.blend_mask` the old code runs untouched: isometric
tilesets, trident (no blend_layer) and hex2t (overhead hex, which sets blend_layer) draw as before.

**freeciv45test**: `blend.spec` carries the mask, generated by `make-freeciv45test.py` (0.5 opacity at the shared
edge, smoothstep down to 0 at 24 px, a quarter tile; corners are the product of the two edge fades, so they join the
edges without a seam). Both sides of an edge blend, so the edge itself is half and half and each terrain thins out
over 24 px on the other side. The nine land terrains have `blend_layer = 1`, under trident's coast cells; the five
drawn from trident's edge-matched sprites (desert, hills, mountains, swamp, tundra) fade out with their
all-neighbours-alike sprite through `t.blend.<terrain>` aliases. Arctic, lake and ocean do not blend. Details in
RECORD.md.

### How it was checked

The same offscreen driver run as for issue 138, with `notes/freeciv45/tileset-t0/mix.txt`: a painted patch around
the start stack with grassland next to a 5 x 5 forest block (with one grassland tile inside it), a 5 x 5 plains
block and a 3 x 3 hills block, plus a lone forest and a lone hills tile in the grassland, fog of war off. The driver
build is the fork at 0baacdb with this patch and `uidrive.diff` as it was at 204b400; "before" is main's tileset (no blend_layer, no
mask) in the same patched client, "after" is the new build. The patch was then rebased onto 0a0ff8e (patch 0018,
which does not touch `tilespec.c`) and the fork built clean with the same 48 compiler warnings as before, none in
`tilespec.c`.

- `tileset-t0/blend-before.jpg`, `blend-after.jpg`: the whole window (the chat box covers the bottom left).
- `tileset-t0/blend-closeup.jpg`: 1:1 crops, before left and after right: the forest block with its grassland hole;
  the hills block next to the plains; the lone forest and hills tiles.

Mean luma in 8 px bands across two edges (offsets in px from the edge, 192 px of edge averaged):

| edge | -40 | -32 | -24 | -16 | -8 | 0 | +8 | +16 | +24 | +32 |
|---|---|---|---|---|---|---|---|---|---|---|
| forest \| grassland, before | 79 | 86 | 85 | 83 | 86 | 132 | 131 | 133 | 127 | 124 |
| forest \| grassland, after | 80 | 86 | 89 | 96 | 110 | 107 | 120 | 130 | 127 | 124 |
| grassland \| plains, before | 130 | 133 | 137 | 133 | 132 | 166 | 169 | 169 | 168 | 167 |
| grassland \| plains, after | 130 | 133 | 138 | 142 | 147 | 149 | 157 | 166 | 167 | 166 |

A one-pixel step of 46 (forest) and 34 (plains) becomes a ramp about 48 px wide.

Isometric and other tilesets unchanged: the same game was shot with an unpatched and a patched driver build on
trident (overhead), amplio2 (isometric, `set topology ISO`) and hex2t (overhead hex, `set topology HEX`). Trident is
pixel-identical. Amplio2 differs only on the focus unit, and so do two runs of the unpatched build (it blinks).
Hex2t differs only where AI units stand on another tile in each run; its terrain and blending are identical.

### What it looks like now

- **Grassland and forest** meet in a soft band: the canopy thins into the meadow over a quarter tile and the meadow
  reaches a quarter tile under the trees, and the block's corners round off. A lone forest tile reads as a grove, not
  a pasted square. A grassland tile inside the forest becomes a clearing with soft sides.
- **Grassland and plains** fade gold into olive with no line; at map scale the edge is gone.
- **Grassland and hills**: the line around trident's hills is softened, and a lone hill sits in the meadow as a soft
  blob. The hills themselves are still trident's pixel art at 3.2x, so the clash of styles stays until hills are
  painted (panel 5 and issue 81).
- **Still visible:** in the fade band the neighbour shows as its own texture at half strength or less, so at 1:1 the
  forest edge looks like a thin veil of trees over the grass rather than single trees standing in it; and the band
  is the same width all along an edge, so a long edge still reads as a straight, soft line. Painted edge cells, or a
  noisy mask (the band wandering in and out), would break that up; neither is in this change.
- **Still visible:** the faint variant grid inside a terrain (issue 138's residue) and the mid-cell light line
  (Brothers-Keeper-Art issue 35); trident's rivers, lakes and resource icons sit on top unblended.
- Not checked here: desert, jungle, mountains, swamp and tundra edges (they blend by the same rule), a long game, the
  GTK and SDL clients (they share `tilespec.c` and the same `crop_sprite` mask formula, but were not run), and
  performance (eight extra sprites per blending terrain at load; at most eight extra draws per tile).
