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
