#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the freeciv45test tileset: trident's sprites scaled to 192 px squares, with the ground of every terrain
replaced by cells cut from painted terrain panels.

Every spec file that trident.tilespec lists under trident/ is re-cut: each grid's cells are cropped from the
30 px sheet, scaled by 192/30 with nearest-neighbour sampling (the pixel art stays crisp; placeholders only),
and laid out again on a clean grid with no pixel border, so the new spec files carry the same tags with new
coordinates. The tilespec is trident's with the sizes and offsets scaled, the file list renamed, a new
terrain45.spec added, and every PAINTED terrain switched from trident's edge-matched sprites to plain variants
like grassland.

The painted ground comes from 5 x 5 ChatGPT panels in the art repo's freeciv45/01_terrain_ground (PANELS and PLAN
below; --art names that folder): grassland run 15, plains run 6 (row 5, the damp grassland, is left out), forest
run 8, jungle run 17, hills run 16, mountains run 7 (without r4c3, whose ridges share one diagonal with its
neighbours), desert, tundra and rocky desert run 12, glacier, swamp and sea ice run 13, the plains and desert
banks and the tundra shore run 14, shallow ocean and lake run 10, deep ocean and inaccessible run 11. Run 9's
pine row gives t.l0.forest_tundra1..3 (cool c1-c3), the forest drawn on a tile with tundra or glacier among its eight
neighbours (issue 127: forest gets layer0_match_with = "tundra", which the fork's patch 0030 reads as a second
variant set; glacier's layer 0 match type is tundra too) and, with --olive-pine, two warm olive forest variants. Each cell goes through
the art repo's seamless cutter as `seamless.py --size 192 --inset 3 --level` does it (192 px LANCZOS master,
straight light gradient removed, edges wrapped), giving t.l0.<terrain>1..N; the client picks a variant per tile
from the tile index. Because the client puts any two variants side by side, the masters of each terrain are first
matched in tone (match_tone): in CIE Lab every cell is moved to the terrain's mean lightness and colour and its
contrast to the terrain's mean contrast, so the texture stays and only the cell's overall level changes.
--no-tone-match skips it, --no-level the gradient removal.

Water (ocean, lake, deep ocean, inaccessible) gets painted layer 0, and the coastline builder (coastline, issue 184,
part of 81) draws the shore: layer 1 of every water and land tile becomes corner cells, four quarter tiles each
picked by the three neighbours around that corner, with run 14's beach on both sides of every coast; layer 2 of the
water tiles draws run 13's glacier as an ice edge next to glacier. The water depths blend into each
other like the land terrains (fork patch 0031 keeps land and water from blending into each other).

Neighbouring land terrains fade into each other at the tile edge: they get blend_layer = 1, and blend.spec holds
t.blend_mask, a generated 3 x 3 tile alpha mask that says how strongly a terrain shows in each tile around it
(BLEND_PEAK at the shared edge, nothing BLEND_DEPTH pixels in). Freeciv 3.2 blends only in isometric view; the
fork's patch 0019 uses this mask in overhead view, fading variant 1 of each terrain. The fork's patch 0028 picks one of
BLEND_MASKS masks per edge, each with a band that wanders along the edge, and fades two variants of one terrain into
each other with t.blend_mask_same (issues 148 and 152). --no-blend leaves it all out.

usage: make-freeciv45test.py --data ~/freeciv-builds/qt/share/freeciv
                             --art ~/Desktop/asset_generator/freeciv45/01_terrain_ground [--cutter SEAMLESS.py]
                             [--out tilesets] [--olive-pine] [--no-tone-match] [--no-level] [--no-blend] [--tile 96]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, importlib.util, math, os, random, re
from PIL import Image, ImageCms, ImageStat

NAME = "freeciv45test"
TILE = 192                       # tile size in pixels (--tile); the map shows it as TILE / PIXEL_RATIO points
SRC_TILE = 30
SCALE = TILE / SRC_TILE          # 6.4 (3.2 for --tile 96)
MASTER = 192                     # seamless.py master size; painted cells are scaled from it to TILE

def set_tile(tile):
    """Switch the build to TILE px tiles: 192 (the default, pixel_ratio 2, sharp on a Retina screen) or 96 (pixel_ratio
    1, the build before issue 161)."""
    global TILE, SCALE, BLEND_DEPTH, SAME_DEPTH
    TILE, SCALE, BLEND_DEPTH, SAME_DEPTH = tile, tile / SRC_TILE, round(24 * tile / 96), round(18 * tile / 96)

def pixel_ratio():
    """Tileset pixels per screen point: 96 px tiles are 96 points, 192 px tiles are 96 points at twice the density."""
    return TILE / 96

def parse_spec(path):
    """Return (header_lines, grids). grids: list of dict(name, params, cells) in file order; cells is a list of
    (row, col, [tags]) in file order."""
    header, grids, grid, in_tiles, row, col = [], [], None, False, None, None
    for raw in open(path, errors="replace"):
        line = raw.split(";")[0].rstrip()
        if grid is None:
            m = re.match(r"\s*\[grid_(\w+)\]", line)
            if m:
                grid = {"name": m.group(1), "params": {}, "cells": []}; grids.append(grid); continue
            header.append(raw.rstrip("\n")); continue
        if not line.strip(): continue
        m = re.match(r"\s*\[grid_(\w+)\]", line)
        if m:
            grid = {"name": m.group(1), "params": {}, "cells": []}; grids.append(grid); in_tiles = False; continue
        m = re.match(r"\s*(\w+)\s*=\s*(\d+)", line)
        if m and not in_tiles: grid["params"][m.group(1)] = int(m.group(2)); continue
        if re.match(r"\s*tiles\s*=\s*\{", line): in_tiles = True; row = col = None; continue
        if in_tiles and line.strip() == "}": in_tiles = False; continue
        if in_tiles:
            m = re.match(r"\s*(\d+)\s*,\s*(\d+)\s*,\s*(.*)", line)
            if m:
                row, col, rest = int(m.group(1)), int(m.group(2)), m.group(3)
                grid["cells"].append((row, col, re.findall(r'"([^"]+)"', rest)))
            elif row is not None:
                grid["cells"][-1][2].extend(re.findall(r'"([^"]+)"', line))
    return header, grids

OVERRIDDEN = {"t.l0.grassland1", "t.l0.inaccessible1"}    # terrain45.spec provides these; dropping them here avoids a duplicate-tag warning

# Blending between terrains (patch 0019 in the fork): which terrains take part, and the shape of the fade.
BLEND_TERRAINS = ("arctic", "desert", "forest", "grassland", "hills", "jungle", "mountains", "plains", "swamp", "tundra",
                  "coast", "floor", "lake", "inaccessible")    # water blends only with water (fork patch 0031)
BLEND_DEPTH = 48      # px into the neighbouring tile where the fade reaches nothing (a quarter tile; set_tile)
BLEND_PEAK = 0.5      # opacity at the shared edge; both sides blend, so the edge itself is half and half
# The band wanders (issue 148): BLEND_MASKS masks, the client picking one per edge (fork patch 0028). Along each edge
# the depth moves by up to BLEND_WANDER times BLEND_DEPTH and the opacity at the edge by up to BLEND_SWAY, the two
# sides of an edge moving opposite ways so they still add up to one; BLEND_CLUMPS is patchy noise inside the band.
BLEND_MASKS = 4
BLEND_WANDER = 0.6
BLEND_SWAY = 0.25
BLEND_CLUMPS = 0.6
# Two variants of one terrain (issue 152): t.blend_mask_same, a straight band SAME_DEPTH px deep (within the quarter
# tile the client cuts for it).
SAME_DEPTH = 36

# Spec files from misc/ whose sprites the client draws on the map: re-cut at the map's density so they keep their size
# on screen (the misc/ files that only widgets show stay trident's, read from the installed data). The overlay colour
# sprites are cropped to the tile, so they must be at least a tile high (64 px in misc/overlays.png).
def map_misc_scale(spec_rel):
    return {"misc/citybar.spec": pixel_ratio(), "misc/overlays.spec": max(1.0, TILE / 64)}.get(spec_rel)

def recut(data, spec_rel, out_dir, record, scale=None):
    """Re-cut one spec file (e.g. trident/tiles.spec) to <out_dir>/<base>.spec and .png, every sprite scaled by scale
    (default SCALE, trident's 30 px to TILE) with nearest-neighbour sampling."""
    scale = SCALE if scale is None else scale
    header, grids = parse_spec(os.path.join(data, spec_rel))
    for g in grids:
        g["cells"] = [(r, c, [t for t in tags if t not in OVERRIDDEN]) for r, c, tags in g["cells"]]
        g["cells"] = [cell for cell in g["cells"] if cell[2]]
    gfx = next(re.search(r'gfx\s*=\s*"([^"]+)"', h).group(1) for h in header if re.search(r'gfx\s*=\s*"', h))
    src = Image.open(os.path.join(data, gfx + ".png")).convert("RGBA")
    base = os.path.basename(spec_rel)[:-5]
    width, height, placed = 0, 0, []
    for g in grids:
        p = g["params"]; dx, dy, pb = p["dx"], p["dy"], p.get("pixel_border", 0)
        x0, y0 = p.get("x_top_left", 0), p.get("y_top_left", 0)
        ndx, ndy = round(dx * scale), round(dy * scale)
        cells = sorted({(r, c) for r, c, _ in g["cells"]})
        rows = max(r for r, _ in cells) + 1; cols = max(c for _, c in cells) + 1
        g["new"] = {"x_top_left": 0, "y_top_left": height, "dx": ndx, "dy": ndy}
        for r, c in cells:
            sx, sy = x0 + c * (dx + pb), y0 + r * (dy + pb)
            placed.append((src.crop((sx, sy, sx + dx, sy + dy)).resize((ndx, ndy), Image.NEAREST),
                           c * ndx, height + r * ndy))
        width = max(width, cols * ndx); height += rows * ndy
    sheet = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for im, x, y in placed: sheet.paste(im, (x, y))
    sheet.save(os.path.join(out_dir, base + ".png"), optimize=True)
    with open(os.path.join(out_dir, base + ".spec"), "w") as f:
        f.write("; Re-cut from %s by tilesets/make-%s.py: every sprite scaled %gx with nearest-neighbour\n"
                "; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.\n"
                % (spec_rel, NAME, scale))
        for h in header:
            f.write(re.sub(r'gfx\s*=\s*"[^"]+"', 'gfx = "%s/%s"' % (NAME, base), h) + "\n")
        for g in grids:
            n = g["new"]
            f.write("[grid_%s]\n\nx_top_left = %d\ny_top_left = %d\ndx = %d\ndy = %d\n\n"
                    % (g["name"], n["x_top_left"], n["y_top_left"], n["dx"], n["dy"]))
            f.write('tiles = { "row", "column", "tag"\n')
            for r, c, tags in g["cells"]:
                f.write("  %2d, %2d, %s\n" % (r, c, ", ".join('"%s"' % t for t in tags)))
            f.write("}\n\n")
    ntags = sum(len(t) for g in grids for _, _, t in g["cells"])
    record.append("| `%s/%s.spec` | `%s` (%d tags, %d grids) | nearest %gx | %dx%d |"
                  % (NAME, base, spec_rel, ntags, len(grids), scale, width, height))

# The panels, in the art repo's freeciv45/01_terrain_ground (--art): the kept run of each, TERRAIN_GROUND.md's runs log.
PANELS = {
    "run6": "run6/panel1/grassland_and_plains.png", "run7": "run7/panel5/hills_and_mountains.png",
    "run8": "run8/panel4/forest_and_jungle.png", "run9": "run9/panel4/forest_and_jungle.png",
    "run10": "run10/panel6/shallow_ocean_and_lake.png", "run11": "run11/panel7/deep_ocean_and_impassable.png",
    "run12": "run12/panel2/desert_and_tundra.png", "run13": "run13/panel3/glacier_and_swamp.png",
    "run14": "run14/panel8/shores_and_banks.png", "run15": "run15/panel1/grassland_and_plains.png",
    "run16": "run16/panel5/hills_and_mountains.png", "run17": "run17/panel4/forest_and_jungle.png",
}

def row(r, cols=range(1, 6)):
    return ["r%dc%d" % (r, c) for c in cols]

# Painted ground, in sheet order: (tag, panel key, panel cells). Each tag's cells become t.l0.<tag>1..N and start on
# a new sheet row, five to a row. The tags are the ruleset's graphic names (terrain.ruleset), and forest_tundra is
# forest next to tundra (PAIRED).
# Not cut as ground: run 14 rows 1-2 (beach, rocky shore: SHORES, the coastline builder) and run 11 row 5 (ice on
# deep water: as a deep ocean variant it would sit on every ocean).
PLAN = [
    ("grassland", "run15", row(1) + row(2)),
    ("plains", "run6", row(3) + row(4)),
    ("plains", "run14", row(3)),                                   # plains bank
    ("forest", "run8", row(1) + row(2)),
    ("jungle", "run17", row(3) + row(4)),
    ("hills", "run16", row(1) + row(2) + row(3)),
    ("mountains", "run7", ["r4c1", "r4c2", "r4c4", "r4c5"] + row(5)),
    ("desert", "run12", row(1) + row(2) + row(5)),                 # dunes, then rocky desert
    ("desert", "run14", row(4)),                                   # desert bank
    ("tundra", "run12", row(3) + row(4)),
    ("tundra", "run14", row(5)),                                   # tundra shore
    ("arctic", "run13", row(1) + row(2) + row(5)),                 # glacier, then sea ice
    ("swamp", "run13", row(3) + row(4)),
    ("coast", "run10", row(1) + row(2) + row(3)),
    ("lake", "run10", row(4) + row(5)),
    ("floor", "run11", row(1) + row(2) + row(3)),
    ("inaccessible", "run11", row(4)),
    ("forest_tundra", "run9", row(5, (1, 2, 3))),                  # cool pine, issue 127
]
OLIVE_PINE = ("forest", "run9", row(5, (4, 5)))   # run 9's warm olive pine; --olive-pine adds it
# Tile sections drawn from the painted variants instead of trident's matched sprites (grassland already is).
PAINTED = ("plains", "forest", "jungle", "hills", "mountains", "desert", "tundra", "arctic", "swamp", "coast", "lake",
           "floor", "inaccessible")
# Painted terrains whose trident layers 1 and 2 would cover the painted ground: trident's glacier draws its whole ice
# cap on layer 1, so the tile keeps its layers' match types (water on layer 1, so no beach by the ice; arctic on layer
# 2, so the water tiles draw the ice edge) but no sprites on them (the shore is drawn by the water tiles).
LAYER0_ONLY = ("arctic",)
# Painted terrains with a second variant set, t.l0.<terrain>_<type>1..N, drawn where one of the eight neighbours has
# layer 0 match type <type> (fork patch 0030; an unpatched client draws no ground for these terrains).
PAIRED = {"forest": "tundra"}

# The coastline builder (issue 184). Layer 1 draws the beach where land meets water, on both sides of the edge:
# water tiles (WATER) and land tiles (LAND) get corner cells matched as a pair (water against land), so the sand runs
# across the tile edge without a seam. Glacier is neither (its layer 1 match type is "ice"), so it gets no beach.
# Layer 2 draws the ice edge on water next to glacier (matched as before: water against anything else on layer 2,
# where only glacier differs). Each look is (panel, cell, look name).
WATER = ("coast", "floor", "lake", "inaccessible")
LAND = ("desert", "forest", "grassland", "hills", "jungle", "mountains", "plains", "swamp", "tundra")
BEACH = ("run14", "r1c3", "beach")      # run 14's rocky shore (row 2) stays unused: a lake's shore meets land cells too
ICE = ("run13", "r1c1", "ice")
# Shape of the shore, as shares of the tile: on the water side the solid band (sand, then wet sand) reaches
# SHORE_DEPTH into the tile, give or take SHORE_WAVE of it (smooth noise that repeats every tile, so neighbouring
# tiles join), then the sand shows through shallow water for SHORE_SHALLOW more; on the land side the sand reaches
# LAND_DEPTH, give or take LAND_WAVE, thinning out into the ground. Ice: ICE_DEPTH, ICE_WAVE and ICE_FADE. Every band
# with its fade stays inside half a tile, so each quarter cell needs only its own three neighbours.
SHORE_DEPTH, SHORE_WAVE, SHORE_SHALLOW = 0.13, 0.4, 0.12
LAND_DEPTH, LAND_WAVE = 0.16, 0.5
ICE_DEPTH, ICE_WAVE, ICE_FADE = 0.28, 0.25, 0.10
SHORE_ROUND = 0.03       # the inner corner of a bay is rounded over this share of the tile (a soft minimum)
# The quarter cells of a tile in the client's order (u d r l: the north, south, east and west corners of the tile
# in its direction4 order), each with its top left in the tile and its three neighbours as (dx, dy), in the order of
# the tag's three digits or letters.
QUARTERS = (("u", (0, 0), ((-1, 0), (-1, -1), (0, -1))), ("d", (1, 1), ((1, 0), (1, 1), (0, 1))),
            ("r", (1, 0), ((0, -1), (1, -1), (1, 0))), ("l", (0, 1), ((0, 1), (-1, 1), (-1, 0))))

CONTRAST_CLAMP = (0.75, 1.33)    # how far match_tone may scale a cell's contrast, so each cell keeps its own texture

def lab_transforms():
    srgb, lab = ImageCms.createProfile("sRGB"), ImageCms.createProfile("LAB")
    return (ImageCms.buildTransformFromOpenProfiles(srgb, lab, "RGB", "LAB"),
            ImageCms.buildTransformFromOpenProfiles(lab, srgb, "LAB", "RGB"))

def match_tone(tiles):
    """Match RGB tiles of one terrain to each other in tone, keeping each one's texture. In CIE Lab (Pillow stores
    a and b offset by 128), each channel of each tile is mapped linearly so its mean becomes the mean of all the
    tiles' means and its standard deviation the mean of their standard deviations, the scale clamped to
    CONTRAST_CLAMP. Returns the new tiles."""
    to_lab, to_rgb = lab_transforms()
    labs = [ImageCms.applyTransform(t, to_lab) for t in tiles]
    stats = [ImageStat.Stat(lab) for lab in labs]
    mean = [sum(st.mean[i] for st in stats) / len(stats) for i in range(3)]
    std = [sum(st.stddev[i] for st in stats) / len(stats) for i in range(3)]
    lo, hi = CONTRAST_CLAMP; out = []
    for lab, st in zip(labs, stats):
        bands = []
        for i, band in enumerate(lab.split()):
            k = min(max(std[i] / st.stddev[i], lo), hi) if st.stddev[i] else 1.0
            lut = [max(0, min(255, round((v - st.mean[i]) * k + mean[i]))) for v in range(256)]
            bands.append(band.point(lut))
        out.append(ImageCms.applyTransform(Image.merge("LAB", bands), to_rgb))
    return out

def luma_range(tiles):
    """(min, max) of the tiles' mean luma (Pillow's L), the measure notes/freeciv45/tileset-t0.md uses."""
    means = [ImageStat.Stat(t.convert("L")).mean[0] for t in tiles]
    return min(means), max(means)

def load_cutter(cutter):
    spec = importlib.util.spec_from_file_location("seamless", cutter); seamless = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seamless); return seamless

def cut_master(seamless, image, box, level=True):
    """One panel cell as seamless.py --size MASTER --inset 3 [--level] cuts it: the MASTER px seamless master."""
    x0, y0, x1, y1 = box; inset = 3
    cell = image.crop((x0 + inset, y0 + inset, x1 - inset, y1 - inset))
    side = min(cell.size)
    master = cell.crop((0, 0, side, side)).resize((MASTER, MASTER), Image.LANCZOS)
    if level: master = seamless.level(master)          # as seamless.py --level: before the edges wrap
    return seamless.make_seamless(master)

def painted(panels, cutter, out_dir, record, plan, tone_match=True, level=True):
    """Cut the planned panel cells into TILE px seamless ground variants; write terrain45.png and terrain45.spec."""
    seamless = load_cutter(cutter)
    panels = {key: path for key, path in panels.items() if any(k == key for _, k, _ in plan)}
    images = {key: Image.open(path).convert("RGB") for key, path in panels.items()}
    boxes = {key: seamless.cells(im) for key, im in images.items()}
    placed, lines, count, srow, prev = [], [], {}, -1, None
    for terrain, key, names in plan:
        for i, name in enumerate(names):
            n = count.get(terrain, 0); count[terrain] = n + 1
            if terrain != prev or n % 5 == 0: srow += 1
            prev = terrain
            master = cut_master(seamless, images[key], boxes[key][name], level)
            placed.append([master, n % 5, srow, terrain])
            lines.append('  %d, %d, "t.l0.%s%d"   ; %s %s' % (srow, n % 5, terrain, n + 1, key, name))
    tones = []
    for terrain in dict.fromkeys(p[3] for p in placed):
        group = [p for p in placed if p[3] == terrain]
        before = luma_range([p[0].resize((TILE, TILE), Image.LANCZOS) for p in group])
        if tone_match:
            for p, tile in zip(group, match_tone([p[0] for p in group])): p[0] = tile
        after = luma_range([p[0].resize((TILE, TILE), Image.LANCZOS) for p in group])
        tones.append("%s %.0f-%.0f -> %.0f-%.0f" % (terrain, before[0], before[1], after[0], after[1]))
    sheet = Image.new("RGB", (TILE * 5, TILE * (srow + 1)))
    for master, c, r, _ in placed:
        sheet.paste(master if master.size == (TILE, TILE) else master.resize((TILE, TILE), Image.LANCZOS),
                    (c * TILE, r * TILE))
    sheet.save(os.path.join(out_dir, "terrain45.png"), optimize=True)
    with open(os.path.join(out_dir, "terrain45.spec"), "w") as f:
        f.write("; Painted ground for the Freeciv45 test tileset, cut from ChatGPT terrain panels by\n"
                "; tilesets/make-%s.py (see RECORD.md). Each cell: seamless.py %d px master, then %d px.\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/terrain45"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n' % (NAME, MASTER, TILE, NAME, TILE, TILE, "\n".join(lines)))
    for key, path in panels.items():
        used = ", ".join("%s %d" % (t, len(c)) for t, k, c in plan if k == key)
        record.append("| `%s/terrain45.spec` | `%s` (%s): %s, through `%s` | %s | %dx%d |"
                      % (NAME, key, os.path.basename(path), used, os.path.basename(cutter),
                         "LANCZOS %d" % MASTER + (", level" if level else "") + ("" if TILE == MASTER else " then %d" % TILE),
                         TILE * 5, TILE * (srow + 1)))
    record.append("| tone match | %s | mean luma per variant at %d px, min-max |" % ("on" if tone_match else "off", TILE)
                  + " %s |" % "; ".join(tones))

def smoothstep_fade(d, depth):
    """Opacity factor at d px from the shared edge: 1 at the edge, 0 from depth on, flat at both ends."""
    u = min(max(d / depth, 0.0), 1.0); return 1.0 - u * u * (3 - 2 * u)

def edge_wave(rng):
    """One edge's wander, a value in -1..1 for each pixel s along the edge: a few random harmonics of the tile, times
    sin(pi s / TILE) so it is 0 at the tile corners, where every mask must agree."""
    terms = [(rng.uniform(0.5, 1.0) / j, j, rng.uniform(0, 2 * math.pi)) for j in (1, 2, 3, 5)]
    raw = [sum(a * math.sin(2 * math.pi * j * (s + 0.5) / TILE + ph) for a, j, ph in terms)
           * math.sin(math.pi * (s + 0.5) / TILE) for s in range(TILE)]
    top = max(abs(v) for v in raw); return [v / top for v in raw]

def clump_noise(rng):
    """Smooth value noise in -1..1 that repeats every TILE px both ways (two octaves), as a function of (x, y)."""
    octaves = [(g, a, [[rng.uniform(-1, 1) for _ in range(g)] for _ in range(g)]) for g, a in ((4, 0.7), (8, 0.3))]
    def at(x, y):
        v = 0.0
        for g, a, grid in octaves:
            fx, fy = (x % TILE) / TILE * g, (y % TILE) / TILE * g
            i, j = int(fx), int(fy); tx, ty = fx - i, fy - j
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            v00, v10 = grid[j % g][i % g], grid[j % g][(i + 1) % g]
            v01, v11 = grid[(j + 1) % g][i % g], grid[(j + 1) % g][(i + 1) % g]
            v += a * ((v00 * (1 - tx) + v10 * tx) * (1 - ty) + (v01 * (1 - tx) + v11 * tx) * ty)
        return v
    return at

def one_mask(depth, rng=None):
    """A 3 x 3 tile mask, white with an alpha that is the opacity of the middle tile's terrain in each of its eight
    neighbours. Edge tiles: BLEND_PEAK at the shared edge falling to 0 at depth (smoothstep); with rng the band wanders
    (edge_wave: the east and south edges move one way, west and north the other, so the two masks that meet at an
    edge add up to one there) and gets clumps (clump_noise, none at the edge itself or at the tile corners). Corner
    tiles: the product of two plain edge fades over BLEND_PEAK, the same in every mask, so whichever masks the edges
    beside a corner use, it joins them without a seam. The middle tile stays transparent."""
    side = 3 * TILE; mask = Image.new("RGBA", (side, side), (255, 255, 255, 0)); px = mask.load()
    vertical = edge_wave(rng) if rng else [0.0] * TILE      # east and west edges, by y
    horizontal = edge_wave(rng) if rng else [0.0] * TILE    # north and south edges, by x
    clump = clump_noise(rng) if rng else (lambda x, y: 0.0)
    def dist(v):                     # distance of pixel row/column v outside the middle tile, 0 inside it
        return TILE - v - 0.5 if v < TILE else v + 0.5 - 2 * TILE if v >= 2 * TILE else 0.0
    for y in range(side):
        for x in range(side):
            dx, dy = dist(x), dist(y)
            if dx and dy:
                a = BLEND_PEAK * smoothstep_fade(dx, depth) * smoothstep_fade(dy, depth)
            elif dx or dy:
                d, s = (dx, y - TILE) if dx else (dy, x - TILE)
                n = (vertical if dx else horizontal)[s] * (1 if (x >= 2 * TILE or y >= 2 * TILE) else -1)
                envelope = math.sin(math.pi * (s + 0.5) / TILE)
                lumps = 1 + BLEND_CLUMPS * clump(x, y) * envelope * min(d / (TILE / 16), 1.0)
                a = (BLEND_PEAK + BLEND_SWAY * n) * smoothstep_fade(d, depth * (1 + BLEND_WANDER * n)) * lumps
            else:
                continue
            px[x, y] = (255, 255, 255, max(0, min(255, round(255 * a))))
    return mask

def blend_mask(out_dir, record):
    """Write blend.png and blend.spec: t.blend_mask and t.blend_mask_2 .. BLEND_MASKS, wandering masks (one_mask with
    a fixed seed each) for the fade between two terrains, and t.blend_mask_same, a straight SAME_DEPTH band for the
    fade between two variants of one terrain. The client picks a mask per edge (fork patch 0028); a client with only
    patch 0019 uses t.blend_mask everywhere."""
    side = 3 * TILE
    tags = ["t.blend_mask"] + ["t.blend_mask_%d" % k for k in range(2, BLEND_MASKS + 1)] + ["t.blend_mask_same"]
    masks = [one_mask(BLEND_DEPTH, random.Random(k)) for k in range(1, BLEND_MASKS + 1)] + [one_mask(SAME_DEPTH)]
    sheet = Image.new("RGBA", (side * len(masks), side), (255, 255, 255, 0))
    for i, m in enumerate(masks): sheet.paste(m, (i * side, 0))
    sheet.save(os.path.join(out_dir, "blend.png"), optimize=True)
    with open(os.path.join(out_dir, "blend.spec"), "w") as f:
        f.write("; Blend masks for the Freeciv45 test tileset, generated by tilesets/make-%s.py (blend_mask):\n"
                "; 3 x 3 tiles each, how strongly a terrain shows in each tile around it. Used by blend_layer in\n"
                "; overhead view (fork patches 0019 and 0028).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    Generated (no artist)\n"\n\n'
                '[file]\ngfx = "%s/blend"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n'
                % (NAME, NAME, side, side, "\n".join('  0, %d, "%s"' % (i, tag) for i, tag in enumerate(tags))))
    record.append("| `%s/blend.spec` | generated: `t.blend_mask` and `_2`-`_%d`, peak %g +- %g at the edge, %d px +- %d%% "
                  "deep, clumps %g; `t.blend_mask_same`, %d px | none | %dx%d |"
                  % (NAME, BLEND_MASKS, BLEND_PEAK, BLEND_SWAY, BLEND_DEPTH, round(100 * BLEND_WANDER), BLEND_CLUMPS,
                     SAME_DEPTH, side * len(masks), side))

def shore_cell(tex, look, quarter, land, noise, grain=None):
    """One quarter cell (TILE/2 px, RGBA) of a shore. quarter is a QUARTERS entry, land the three neighbours' flags in
    its order (the other side of the shore: land for a water tile, water for a land tile); tex the TILE px texture,
    sampled at the pixel's place in the tile, so cells side by side and tiles side by side join. The distance to the
    other side (a soft minimum over the flagged neighbours, each a whole tile) against the band's depth there gives
    the shape. Looks: "beach" and "ice" on the water side, "sand" on the land side (grain thins its inner edge)."""
    half = TILE // 2; (qx, qy), near = quarter[1], quarter[2]
    out = Image.new("RGBA", (half, half), (0, 0, 0, 0)); px, tx = out.load(), tex.load()
    boxes = [(dx * TILE, dy * TILE) for (dx, dy), on in zip(near, land) if on]
    if not boxes: return out
    if look == "ice": depth, wave, fade = ICE_DEPTH * TILE, ICE_WAVE, ICE_FADE * TILE
    elif look == "sand": depth, wave, fade = LAND_DEPTH * TILE, LAND_WAVE, 0
    else: depth, wave, fade = SHORE_DEPTH * TILE, SHORE_WAVE, SHORE_SHALLOW * TILE
    k = SHORE_ROUND * TILE
    foam_strength = {"beach": 0.55, "ice": 0.0, "sand": 0.0}[look]
    for y in range(half):
        for x in range(half):
            X, Y = qx * half + x + 0.5, qy * half + y + 0.5
            ds = [math.hypot(max(bx - X, 0, X - bx - TILE), max(by - Y, 0, Y - by - TILE)) for bx, by in boxes]
            d = min(ds) if len(ds) == 1 else -k * math.log(sum(math.exp(-v / k) for v in ds))
            band = depth * (1 + wave * noise(X, Y))
            u = d / band
            r, g, b = tx[int(X) % TILE, int(Y) % TILE]
            if look == "sand":
                # solid at the edge, then thinning out in grains into the land's own ground
                a = smoothstep_fade(max(u - 0.35, 0) / 0.65 + 0.35 * grain(X, Y) * min(u / 0.35, 1), 1.0)
                if a > 0.004: px[x, y] = (r, g, b, round(255 * a))
                continue
            if look == "ice":
                rim = math.exp(-((u - 0.92) / 0.07) ** 2)                 # a bright lip at the ice front
                r, g, b = (min(255, c * (1 + 0.18 * rim)) for c in (r, g, b))
                if u <= 1: a = 1.0
                else:
                    a = 0.55 * smoothstep_fade(d - band, fade)           # ice under the water, fading out
                    r, g, b = (0.6 * c + 0.4 * w for c, w in zip((r, g, b), (175, 212, 232)))
            else:
                wet = 1 - 0.28 * min(max((u - 0.55) / 0.45, 0), 1) ** 2   # sand darkens towards the water
                r, g, b = r * wet, g * wet, b * wet
                a = 1.0 if u <= 1 else 0.6 * smoothstep_fade(d - band, fade)
                foam = foam_strength * math.exp(-((u - 1.0) / 0.06) ** 2)
                if foam > 0.01:
                    na = max(a, foam)
                    mix = foam / na
                    r, g, b = (c * (1 - mix) + f * mix for c, f in zip((r, g, b), (236, 240, 234)))
                    a = na
            if a > 0.004: px[x, y] = (round(r), round(g), round(b), round(255 * min(a, 1.0)))
    return out

def pair_tag(layer, terrain, q, flags, own, other):
    """A corner cell tag of a layer matched as a pair: the neighbours' match types by first letter."""
    return "t.l%d.%s_cell_%s_%s" % (layer, terrain, q, "_".join(other if f else own for f in flags))

def coastline(panels, cutter, out_dir, record, level=True):
    """Write coast.png and coast.spec, three rows of 32 quarter cells (QUARTERS, three neighbour flags each): the
    beach on water tiles (t.l1.<water>_cell_<q>_<w|l>_<w|l>_<w|l>), the sand on land tiles
    (t.l1.<land>_cell_<q>_<l|w>_...), both cut from BEACH, and the ice edge on water tiles from ICE
    (t.l2.<water>_cell_<q><abc>, a MATCH_SAME layer: digit 1 where the neighbour is glacier)."""
    seamless = load_cutter(cutter)
    rows = [(BEACH, "beach", [(lambda q, f, w=w: pair_tag(1, w, q, f, "w", "l")) for w in WATER],
             "water tiles next to land, layer 1"),
            (BEACH, "sand", [(lambda q, f, t=t: pair_tag(1, t, q, f, "l", "w")) for t in LAND],
             "land tiles next to water, layer 1"),
            (ICE, "ice", [(lambda q, f, w=w: "t.l2.%s_cell_%s%d%d%d" % (w, q, *f)) for w in WATER],
             "water tiles next to glacier, layer 2")]
    images, masters = {}, {}
    half = TILE // 2; tag_lines = []
    sheet = Image.new("RGBA", (half * 32, half * len(rows)), (0, 0, 0, 0))
    for row_no, ((key, name, _), look, tags, what) in enumerate(rows):
        if key not in images: images[key] = Image.open(panels[key]).convert("RGB")
        if (key, name) not in masters:
            master = cut_master(seamless, images[key], seamless.cells(images[key])[name], level)
            masters[key, name] = master.resize((TILE, TILE), Image.LANCZOS) if master.size != (TILE, TILE) else master
        noise = clump_noise(random.Random(184 if look != "ice" else 185))   # beach and sand share it: they meet
        grain = clump_noise(random.Random(186))
        fine = lambda x, y: grain(x * 4, y * 4)       # four times finer, still repeating every tile
        col = 0
        for q in QUARTERS:
            for value in range(8):
                flags = [(value >> i) & 1 for i in range(3)]
                sheet.paste(shore_cell(masters[key, name], look, q, flags, noise, fine), (col * half, row_no * half))
                tag_lines.extend('  %d, %d, "%s"' % (row_no, col, tag(q[0], flags)) for tag in tags)
                col += 1
        record.append("| `%s/coast.spec` | `%s` %s (%s), through `%s`: %s cells for %s | generated, %d px quarter cells "
                      "| %dx%d |" % (NAME, key, name, os.path.basename(panels[key]), os.path.basename(cutter), look, what,
                                     half, half * 32, half * len(rows)))
    sheet.save(os.path.join(out_dir, "coast.png"), optimize=True)
    with open(os.path.join(out_dir, "coast.spec"), "w") as f:
        f.write("; Shore cells for the Freeciv45 test tileset, generated by tilesets/make-%s.py (coastline) from\n"
                "; painted cells: quarter tiles of beach on both sides of a coast (layer 1) and of ice on water next\n"
                "; to glacier (layer 2).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/coast"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n' % (NAME, NAME, half, half, "\n".join(tag_lines)))

def tilespec(data, out_root, files, blend=True):
    """trident.tilespec with sizes, offsets, name and file list changed; the PAINTED terrains as plain variants;
    with blend, blend_layer 1 for BLEND_TERRAINS."""
    k = TILE / 96             # the offsets below were set for 96 px tiles
    scaled = {"normal_tile_width": TILE, "normal_tile_height": TILE, "stack_size_offset_x": round(64 * k),
              "stack_size_offset_y": round(32 * k), "citybar_offset_y": round(86 * k), "tilelabel_offset_y": round(32 * k),
              "unit_upkeep_small_offset_y": round(64 * k), "svg_height": round(44 * k)}
    out, section, in_files = [], None, False
    for raw in open(os.path.join(data, "trident.tilespec"), errors="replace"):
        line = raw.rstrip("\n")
        m = re.match(r"\s*\[(\w+)\]", line)
        if m: section = m.group(1)
        if in_files:
            if line.strip().endswith(",") or line.strip().startswith('"'):
                if not line.strip().endswith(","): in_files = False
                continue
            in_files = False
        m = re.match(r"\s*(\w+)\s*=", line)
        key = m.group(1) if m else None
        if key == "files":
            out.append("files =\n" + ",\n".join('  "%s"' % f for f in files)); in_files = True; continue
        if key in scaled:
            out.append("%s = %d" % (key, scaled[key]))
            if key == "normal_tile_height" and pixel_ratio() != 1:
                out.append("\n; Tileset pixels per screen point: the map shows a %d px tile as %d points, so on a 2x (Retina)\n"
                           "; screen every pixel is drawn (Freeciv45 fork, Qt client); other clients show the tiles at %d points.\n"
                           "pixel_ratio = %g" % (TILE, TILE / pixel_ratio(), TILE, pixel_ratio()))
            continue
        if key == "name": out.append('name = "Freeciv45 test"'); continue
        if key == "priority": out.append("priority = 4"); continue
        if key == "summary": out.append('summary = _("Freeciv45 test tileset: %d px overhead squares, painted ground for every terrain, scaled trident placeholders.")' % TILE); continue
        if section and section[5:] in PAINTED and key in ("layer0_match_with", "layer0_sprite_type"):
            continue    # <terrain>1..N variants from terrain45.spec, no edge or corner matching
        if section and section[5:] in PAIRED and key == "layer0_match_type":
            out.append(line)
            out.append('layer0_match_with = "%s"' % PAIRED[section[5:]]); continue    # the second variant set
        if section == "layer1" and key == "match_types":
            out.append('match_types = "water", "land", "ice"'); continue         # ice: glacier, which gets no beach
        if section and section[5:] in LAYER0_ONLY:
            if key and re.match(r"layer[12]_(match_with|sprite_type)", key): continue    # match types only, no sprites
            if key == "layer1_match_type": out.append('layer1_match_type = "ice"'); continue
        if section and section[5:] in WATER:                                     # coast.spec: beach and ice cells
            if key == "layer1_match_with": out.append('layer1_match_with = "land"'); continue
            if key == "layer2_match_with":
                out.append(line); out.append('layer1_sprite_type = "corner"\nlayer2_sprite_type = "corner"'); continue
        if section and section[5:] in LAND and key == "layer1_match_type":    # coast.spec: sand cells
            out.append(line); out.append('layer1_match_with = "water"\nlayer1_sprite_type = "corner"'); continue
        if blend and key == "blend_layer" and section and section[5:] in BLEND_TERRAINS:
            out.append("blend_layer = 1"); continue     # neighbours fade in after layer 0, under the coast cells
        out.append(line)
    text = "\n".join(out) + "\n"
    text = text.replace("[tilespec]\n", "[tilespec]\n\n; Freeciv45 test tileset, built by tilesets/make-%s.py from trident.tilespec; see RECORD.md.\n" % NAME, 1)
    open(os.path.join(out_root, NAME + ".tilespec"), "w").write(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a Freeciv data dir with trident.tilespec and trident/")
    ap.add_argument("--art", required=True, help="the art repo's freeciv45/01_terrain_ground, with the runs in PANELS")
    ap.add_argument("--olive-pine", action="store_true", help="add run 9's r5c4 and r5c5 as forest11 and forest12")
    ap.add_argument("--cutter", help="seamless.py (default: tools/seamless.py next to --art)")
    ap.add_argument("--no-tone-match", action="store_true", help="leave each painted cell's tone as cut (the build before issue 138)")
    ap.add_argument("--no-level", action="store_true", help="keep each cell's light gradient (seamless.py without --level)")
    ap.add_argument("--no-blend", action="store_true", help="no blending between terrains (the build before issue 141)")
    ap.add_argument("--tile", type=int, choices=(96, 192), default=192,
                    help="tile size: 192 px at pixel_ratio 2 (default), or 96 px, the build before issue 161")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    set_tile(a.tile)
    out_dir = os.path.join(a.out, NAME); os.makedirs(out_dir, exist_ok=True)
    spec_text = open(os.path.join(a.data, "trident.tilespec"), errors="replace").read()
    listed = re.findall(r'"([^"]+\.spec)"', spec_text.split("files =", 1)[1].split("*include", 1)[0])
    files, record = [], []
    for rel in listed:
        if rel.startswith("trident/"):
            recut(a.data, rel, out_dir, record)
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
            if rel == "trident/tiles.spec":
                files.append("%s/terrain45.spec" % NAME)
                files.append("%s/coast.spec" % NAME)
                if not a.no_blend: files.append("%s/blend.spec" % NAME)
        elif map_misc_scale(rel) and map_misc_scale(rel) != 1:
            recut(a.data, rel, out_dir, record, scale=map_misc_scale(rel))
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
        else: files.append(rel)
    plan = PLAN + ([OLIVE_PINE] if a.olive_pine else [])
    plan.sort(key=lambda p: [t for t, _, _ in PLAN].index(p[0]))     # keep each terrain's cells together
    cutter = a.cutter or os.path.join(os.path.dirname(os.path.abspath(a.art)), "tools", "seamless.py")
    painted({key: os.path.join(a.art, rel) for key, rel in PANELS.items()}, cutter, out_dir, record, plan,
            tone_match=not a.no_tone_match, level=not a.no_level)
    coastline({key: os.path.join(a.art, rel) for key, rel in PANELS.items()}, cutter, out_dir, record,
              level=not a.no_level)
    if not a.no_blend: blend_mask(out_dir, record)
    tilespec(a.data, a.out, files, blend=not a.no_blend)
    print("| spec | source | scaling | sheet |\n|---|---|---|---|\n" + "\n".join(record))

if __name__ == "__main__":
    main()
