# freeciv45iso: the painted terrain on the angled map (issue 190, 2026-10-18)

civ45 plays on the angled map since issue 188 (topology ISO, patch 0032), and John prefers that look. His words:
"convert our painted terrain into angled tiles, and use amplio2 units and cities for now". This note says what
was built, what changed in the client (patch 0033), and how it was checked. Labels: observed (seen in a run or read
in the source), inferred (my reading), unverified (not checked).

## What it is

- **Geometry:** amplio2's 96 x 48 diamond doubled, 192 x 96 px at `pixel_ratio = 2` (patch 0025). On a 2x screen a
  tile is 96 x 48 points like amplio2, and every pixel of the painted ground is drawn.
- **Painted ground:** the same cells freeciv45test uses, cut the same way. `make-freeciv45iso.py` imports
  `make-freeciv45test.py`, so it has the same `PANELS` and `PLAN` from the TERRAIN_GROUND.md runs log, the same
  seamless cutter, the same tone match and the same cool pine. Each 192 px square master is then turned 45 degrees and
  squashed 2:1. A square tile point (u, v) lands on x = (u - v) / 2 + 96, y = (u + v) / 4, so the tile's north edge
  becomes the diamond's upper right edge, as the client draws map north.
  - Each pixel averages 4 x 4 point samples of the master, which wraps, so neighbouring diamonds join as the square
    tiles do.
  - The outline is binary: a pixel belongs to a tile when its centre does, so diamonds never overlap or leave gaps.
- **Shore:** freeciv45test's coastline cells (beach on both sides of a coast, ice next to glacier), turned the same
  way into the client's isometric corner cells (96 x 48, the top, bottom, right and left quarters of the diamond).
- **Blending:** freeciv45test's four wandering masks, turned tile by tile. Each of the 3 x 3 tiles is a diamond in its
  own rectangle, in map order. Land fades into land and water into water (patch 0031).
  - There is no `t.blend_mask_same` in iso, because its strips are square. Two variants of one terrain meet without a
    fade, as they do in amplio2.
- **From amplio2:** everything else, scaled 2x with nearest-neighbour sampling, with its artists' credits kept in each
  spec. That covers units, cities, rivers, roads, specials and resources, bases, fog, borders, grid, select and
  explosions.
  - Left out: amplio2's forest, jungle, hills and mountains overlays, its ocean corner cells, its lake and ice cells,
    and its `t.blend.*` textures. The painted ground replaces them.
  - `misc/citybar` and `misc/overlays` are re-cut, as freeciv45test does.
- **Size:** 8.9 MB, of which 7.7 MB is the painted sheet. freeciv45test is larger (its square sheet alone is 14 MB).
- **Retakes:** when runs 18 to 21 land, add them to `PANELS` and `PLAN` in `make-freeciv45test.py` and run both
  builders. Two builds in a row give identical files (observed).

## Patch 0033 (fork `client/tilespec.c`)

- **Observed, source:** the masks were read only for overhead square tilesets. An isometric tileset got only
  `t.dither_tile`, and amplio2's dither tile is a thin diagonal line, so amplio2 barely blends.
- Now any square tileset can have the masks, overhead or isometric. With them, the client uses the masks in place of
  the dither tile. `t.blend_mask_same` stays overhead only.
- **Observed, run:** the first run drew the blend pieces half a tile too high. They were added at the "full tile"
  offset, which is 0 in overhead view but -H/2 in isometric view (a full iso tile is 1.5 tiles tall), and the next
  tiles painted over most of them.
  - The pieces are one tile in size, so they now go at the tile's own origin.
  - Overhead tilesets are unchanged: there the full tile is the tile, so the offset was 0 before and after (inferred
    from the source; freeciv45test was not re-run on the patched client).
- An unpatched client still loads freeciv45iso and blends it through amplio2's dither tile (inferred).

## Check (observed)

Offscreen client on the driver build (patch 0033 plus `../ui/bar-test/uidrive.diff`), `QT_SCALE_FACTOR=2` on the
1728 x 1030 pt screen, scene `field.txt`.

- The scene paints every civ45 terrain in 3 x 3 blocks, in map coordinates, south of the start stack, on the ISO
  civ45 map. The same game and view were run with amplio2 and with freeciv45iso.
- The client log for freeciv45iso has no tileset error or warning, and amplio2's run has none either.
  - The first build listed `misc/flags.spec` twice and logged 1154 duplicate-flag warnings. That is fixed, and the
    count is now 0.

![amplio2 and freeciv45iso, 1:1 device pixels](field-amplio2-vs-freeciv45iso-1to1.jpg)

- The whole windows, at half size: `field-window-amplio2.jpg` and `field-window-freeciv45iso.jpg`. The top strip,
  edge column, unit card, what-next button and minimap sit where they do with amplio2.
- Desert into tundra, tundra into glacier, forest into jungle, ocean into lake and lake into deep ocean all fade over
  wandering edges.
  - Beaches run along every coast.
  - The ice edge shows where water meets glacier.
  - amplio2's rivers, specials, cities and units draw on the painted ground.

## Relief for hills and mountains (issue 194, 2026-10-18)

A painted square seen from above, once turned into a diamond, reads as flat ground. Its light also swings toward the
left. That suits grassland, plains, desert, tundra, swamp, glacier and water. Hills and mountains need relief.

**Chosen for now:**
- Hills and mountains draw amplio2's relief overlays over flat painted ground.
  - Hills stand on plains cells (run 6 row 3), mountains on rocky desert (run 12 row 5).
  - The painted hills and mountains stay in freeciv45test.
- Forest, jungle and the cool pine keep the painted canopy, which reads as forest at the angle (picture above).

**How (observed, source and run):**
- The overlays come in 16 forms each, matched to same-type neighbours on the four edges.
  - In the client, a 1 digit in `_n1e0s0w0` means "same type", and hills and mountains join each other.
  - Mountains are tall (96x66 in amplio2, 192x132 here), 12 px lower.
- They go on layer 2, because the land tiles' layer 1 holds the beach.
- So the water tiles' ice edge on layer 2 is now matched as a pair, water against arctic (`t.l2.<water>_cell_u_a_w_w`).
  - As a "same" match, every hill next to water would have drawn an ice edge.
  - The run shows ice by the glacier and none by the hills.
- The painted base was tried too (`--relief-base painted`). amplio2's hill overlay covers the whole diamond and the
  mountains leave only small gaps, so the two bases look almost the same. The flat base also fades into the
  neighbours in plain ground colours.

![amplio2, freeciv45iso before, freeciv45iso with relief; 1:1](relief-1to1.jpg)

The whole window, half size: `relief-window.jpg`.

**From the FCW and amplio2 study (the parent session's read-only report), checked here:**
- Relief is a separate overlay layer: yes, `hills.spec` and `mountains.spec` hold only `t.l1` overlays.
- Mountains are 96x66: yes.
- Units are 64x48: yes.
- "u.freight and u.container carry a real trademark": **not confirmed**. Stock amplio2's freight truck says "GPL" on its
  side, and the container ship shows no brand at this size. Both stay as stock amplio2 GPL art.
- Only stock amplio2 is used (from the build's data), nothing from FCW's own additions.
- Later ideas, not done:
  - painted iso relief overlays for hills, mountains and forest, as a Codex art job;
  - sparse transparent detail sprites as extra numbered variants (FCW does this; the 3.2 client picks a variant per
    tile).

## The look in a real game (issue 198, 2026-10-18)

The parent session played civ45 with freeciv45iso (size 4, mapseed 21, gameseed 21, revealmap START, turn 1, John's
options) and listed five faults. This section covers the first three. Forest and jungle overlays and a brightness lift
come later. All changes are in `make-freeciv45iso.py`. freeciv45test and the client are unchanged.

1. **"Grassland looks like orange sand."** Observed in the game's save: the start area is mostly plains, with some
   grassland and desert.
   - The plains cells were run 6's golden rows 3 and 4 and run 14's sandy bank, and next to the desert they read as
     sand.
   - The iso build now uses run 6's yellow-green rows 1 and 2.
   - Each terrain was checked by name on the labelled field below. The orange left in the start view is desert, which
     amplio2 paints pale beige, so our sand is more golden.
2. **Boxy coasts.** The beach is narrower and wanders more, and bays are rounded over a wider soft minimum.
   - These are make-freeciv45test.py's `SHORE_*` and `LAND_*` values, overridden for the iso build only (`SHORE`):
     - beach depth on the water side 0.13 to 0.07 of a tile, and on the land side 0.16 to 0.08;
     - wave 0.4 and 0.5 to 0.6;
     - bay rounding 0.03 to 0.15.
   - Lakes keep the shore. Two lake variants were tried:
     - no beach at all;
     - sand on the land side only.
   - Both made a one-tile lake a hard diamond. With the rounded shore it reads as a pond.
3. **Deep ocean as a black hole.** It is graded toward deep blue in CIE Lab (`GRADE`, floor +28 L, +2 a, -20 b).
   - The fades between terrains now reach 37.5 % of a tile (`BLEND_DEPTH`), up from 25 %.
   - A diamond is half as deep across an edge as a square, so the old fades looked short in iso.

**Check (observed):** the same seed and the same 3680 x 2284 device-pixel window as the parent's shot, on the driver
build, offscreen. The crops are at the parent's `mid.png` offset, so the three rows show the same tiles.
- amplio2's run and ours have the same map and start.
- The client log has no tileset error or warning.
  - The first try of "no beach" named a new layer 1 match type "lake". The client refused it, because its initial
    clashes with "land", and the game never started.

![amplio2, before, now; same seed, 1:1](look-seed21-1to1.jpg)

![deep ocean: amplio2, before, now; 1:1](look-deep-1to1.jpg)

![every civ45 terrain by name: amplio2 and now; 1:1](look-terrain-names-1to1.jpg)

**Still open:**
- Grassland and plains are close in hue: plains are yellow-green, grassland a duller green.
- Desert is golden where amplio2's is pale.
- A diagonal coast still steps tile by tile, as amplio2's does, but softer.
- Forest and jungle overlays and a brightness lift are the parent's items 4 and 5.

## Not done, and findings

- Hills and mountains had no relief in the first build (issue 194). They now draw amplio2's relief (see above).
- **Inaccessible against deep ocean is a hard edge.** It is the same in freeciv45test, because civ45's Inaccessible
  is not in the water class.
- **Two variants of one terrain meet without a fade** in iso (see above).
- **Not checked:** a real Cocoa window on John's screen, an unpatched client, the GTK and SDL clients (which ignore
  `pixel_ratio`), fog of war and borders on the painted ground in a long game, and drawing speed.
