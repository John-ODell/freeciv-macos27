#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the freeciv45iso tileset: the Freeciv45 painted ground as isometric diamonds, with amplio2's sprites (scaled
2x) for everything there is no Freeciv45 art for yet.

civ45 plays on the angled map (topology ISO, fork patch 0032), so the map needs an isometric tileset. The tile is
amplio2's 96 x 48 diamond doubled: 192 x 96 px at pixel_ratio 2 (fork patch 0025), so the patched Qt client shows
it at amplio2's size and, on a Retina screen, draws every pixel.

The painted ground is cut exactly as freeciv45test cuts it (make-freeciv45test.py, imported from next to this file:
the same PANELS and PLAN, the seamless cutter, tone match, cool pine): each 192 px square master is then turned 45
degrees and squashed 2:1 into a 192 x 96 diamond (to_iso). A square tile point (u, v), u east and v south, lands on
x = (u - v) W / 2T + W / 2, y = (u + v) H / 2T: the tile's north-west corner is the diamond's top, its north edge
the diamond's upper right edge, as the client draws map north. Every pixel is the average of SS x SS point samples
of the master, which wraps, so neighbouring diamonds join like the square tiles do; the diamond's own outline is
binary (a pixel is in the tile when its centre is), so the diamonds of a map cover it with no gap or overlap.

The coastline (beach on both sides, ice by glacier) is freeciv45test's: its square quarter cells are turned the
same way into the client's isometric corner cells (W/2 x H/2, the top, bottom, right and left quarters of the
diamond). The blend masks (t.blend_mask, _2 to _4: wandering edges, land into land and water into water) are the
square masks turned per tile: each of the 3 x 3 tiles becomes a diamond in its own W x H rectangle, the layout the
fork's patch 0033 reads for isometric tilesets. There is no t.blend_mask_same in iso (its strips are square), so
two variants of one terrain meet without a fade, as in amplio2.

Hills and mountains (issue 194): a painted square seen from above reads as flat ground once turned, so they draw
amplio2's relief overlays (RELIEF, on layer 2) over flat painted ground (RELIEF_BASE). Forest and jungle (issue
199): the painted canopy read flat in a real game, so they draw amplio2's tree overlays the same way (CANOPY) over
painted grassland (CANOPY_BASE), until our own tree props replace them; --canopy painted keeps the canopy.

Units and cities (issue 245): the 85 civ45 unit sprites, the ten city styles in five sizes (open and walled; in iso the
walled sprite is the whole city), the activity and veteran marks and extra.ruins come from the art repo's
freeciv45/04_units and 05_cities runs (UNIT_RUNS, CITY_PICK, MARK_RUN). Each panel cell is cleaned (stray specks out, the
colour fringe of the semi-transparent edge defringed, see defringe), turned to face left where the art drew it facing
right (UNIT_FLIP), scaled to a common figure size and set on a 160 x 128 cell (units.spec, ten to a row) or a 192 x 144
one (cities.spec). amplio2's units.spec, extra_units.spec, cities.spec and veterancy.spec go; its sprites stay only
where the art pack has none (see RECORD.md); --no-bk-units keeps amplio2's units, cities and marks.

Tech icons and building pictures (issue 254): the art repo's freeciv45/06_tech_icons (runs 1, 2, 5 and 6) and
07_building_icons (runs 1 to 5), cleaned like the units and fitted into the client's own icon cells (48 x 48 for a
tech, 64 x 48 for a building, the sizes the Qt client draws at 1x and 2x alike). They go in tech_icons.spec and
building_icons.spec, listed after misc/techs.spec and misc/wonders-large.spec under duplicates_ok, so they override the
stock icons they cover and the rest stay as they were; --no-bk-icons leaves the stock icons alone.

National borders (issue 259): amplio2's dashed grid.borders.n/s/w/e are replaced by generated white masks the client
tints per nation (borders.spec, see BORDER_CORE and BORDER_FADE): a solid band along each diamond edge, crisp on the outer
side and fading inward; --no-borders keeps amplio2's.

Map extras (issue 262): mines, oil wells and platforms, huts, hermits, the transport hub, buoys, Fort, Fortress and Castle,
airstrips and airbases, irrigation, farmland, pollution, fallout, roads, rails, rivers and the badges come from the art repo's
freeciv45/09_map_extras runs 1 to 6 (extras.spec, badges.spec; see EXTRA_RUNS): standing props on the full tile, the forts split
into back and front halves, the overlays turned like the ground, the road, rail and river pieces painted from seamless bands,
the counted badges drawn with a number; --no-bk-extras keeps all of amplio2's.

From amplio2 (Freeciv 3.2.6, GPL-2.0-or-later, the artists named in each spec's [info] section, copied verbatim):
every spec file amplio2.tilespec lists under amplio2/ except the ocean cells the painted ground replaces
(SKIPPED; the forest and jungle overlays too with --canopy painted), each sprite scaled 2x with nearest-neighbour sampling (recut). The tilespec is amplio2's with the sizes
and offsets doubled, pixel_ratio 2, the file list renamed, and freeciv45test's layer and terrain sections.

usage: make-freeciv45iso.py --data ~/freeciv-builds/qt/share/freeciv
                            --art ~/Desktop/asset_generator/freeciv45/01_terrain_ground [--cutter SEAMLESS.py]
                            [--out tilesets] [--olive-pine] [--no-tone-match] [--no-level] [--no-blend]
                            [--no-relief] [--relief-base flat|painted] [--canopy amplio2|painted]
                            [--land-grade L,A,B] [--units-art 04_units] [--cities-art 05_cities] [--no-bk-units]
                            [--extras-art 09_map_extras] [--no-bk-extras]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, glob, importlib.util, math, os, random, re, tempfile
from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("make_freeciv45test", os.path.join(HERE, "make-freeciv45test.py"))
sq = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sq)

NAME = "freeciv45iso"
W, H = 192, 96          # the diamond: amplio2's 96 x 48, doubled
T = 192                 # the square masters and freeciv45test's tile (make-freeciv45test.py --tile 192)
SS = 4                  # point samples per pixel, per axis
AMPLIO_SCALE = 2
# amplio2 spec files left out: the ocean's corner cells, which the painted ground replaces, and the forest and jungle
# overlays unless --canopy amplio2 (CANOPY, the default) takes them back. water.spec stays for the rivers; its lake and ice cells are dropped (DROP_PREFIX), and so
# are terrain1.spec's t.blend.* textures, which the client would fade in instead of the painted variant 1.
SKIPPED = ("amplio2/terrain2.spec", "amplio2/ocean.spec")
# amplio2 spec files the art pack's units and cities replace (issue 245): the new spec that stands in for each, or None. The
# extra units are other rulesets' (civ45 uses none of them).
BK_REPLACED = {"amplio2/units.spec": "units.spec", "amplio2/extra_units.spec": None, "amplio2/cities.spec": "cities.spec"}
DROP_PREFIX = {"amplio2/water.spec": ("t.l0.", "t.l1."), "amplio2/terrain1.spec": ("t.blend.",)}
# Relief (issue 194). A painted square seen from above turned into a diamond reads as flat ground, so hills and
# mountains get amplio2's relief: transparent overlays in 16 forms, each matched to the same-type neighbours on the
# four edges (hills and mountains join each other), mountains drawn tall. They go on layer 2, because the land tiles'
# layer 1 holds the beach; so the water tiles' ice edge on layer 2 is matched as a pair (water against arctic) instead
# of against everything else. RELIEF_BASE is the ground under them: the flat cells cut for each instead of the
# painted relief, which would fight the overlay's own light. --no-relief leaves both out (the build of issue 190).
RELIEF = {"amplio2/hills.spec": "hills", "amplio2/mountains.spec": "mountains"}
# The look in a real game (issue 198). Plains: run 6's yellow-green rows 1 and 2 instead of its golden rows 3 and 4 and
# run 14's sandy bank, which read as sand next to the orange desert. Shore: a narrower beach that wanders more, with
# bays rounded over a wider soft minimum, so a diagonal coast reads less like stair steps (make-freeciv45test.py's
# SHORE_* and LAND_* values, overridden here only). Lakes keep the same shore: tried without a beach, a one-tile lake
# read as a hard diamond, while the rounded shore makes it a pond. Deep ocean: graded toward deep blue (GRADE: CIE Lab
# offsets on Pillow's 0-255 scale, L then a then b) so it reads as darker water, not a hole; and the fades between
# terrains reach further in (BLEND_DEPTH, a share of the tile), since a diamond is half as deep across an edge as a
# square.
ISO_PLAINS = [("plains", "run6", ["r1c%d" % c for c in range(1, 6)] + ["r2c%d" % c for c in range(1, 6)])]
SHORE = {"SHORE_DEPTH": 0.07, "SHORE_WAVE": 0.6, "SHORE_SHALLOW": 0.10, "LAND_DEPTH": 0.08, "LAND_WAVE": 0.6,
         "SHORE_ROUND": 0.15}
# Desert (issue 209): graded from orange (a +16, b +44) toward straw at the same lightness, so the ground round a
# desert start no longer reads as orange sand.
GRADE = {"floor": (28, 2, -20), "desert": (0, -12, -14), "mountains": (-6, -13, -32)}
BLEND_DEPTH = 0.375
RELIEF_BASE = [
    ("hills", "run6", ["r3c1", "r3c2", "r3c3", "r3c4", "r3c5"]),        # plains, under the hills
    ("mountains", "run19", ["r5c1", "r5c2", "r5c3", "r5c4", "r5c5"]),   # rocky desert, under the mountains
]
# Forest and jungle (issue 199): --canopy amplio2 draws amplio2's tree overlays (terrain2.spec, 16 forms each, matched
# to same-type neighbours) on layer 2 like the relief, over flat grassland (CANOPY_BASE) instead of the painted
# canopy. The cool pine next to tundra stays painted ground under the trees.
CANOPY = {"amplio2/terrain2.spec": ("forest", "jungle")}
CANOPY_BASE = [("forest", "run15", sq.row(1) + sq.row(2)), ("jungle", "run15", sq.row(1) + sq.row(2))]
# A CIE Lab offset (L, a, b, as GRADE) for every painted land cell, after GRADE (issue 199; --land-grade).
LAND_GRADE = (0, 0, 0)
# Resources (issue 206): the Freeciv45 art pack's isometric props (the art repo's freeciv45/03_resources, --resources),
# already cut by its tools/props.py to 192x96 tiles standing on the tile's foot point with a soft contact shadow, the
# size and anchor of amplio2's resource sprites doubled. Only the pick for each of civ45's 21 ts.* tags is copied
# (RESOURCES.md, "Runs and retakes"; John: "we should only ship the chosen final assets"); they replace amplio2's.
# Coal (issue 208): run 2's coal_2 nearly vanished on the hills, so it is run 3's retake, coal_a_1, a heap the size of gold
# and iron with bright facets.
RESOURCE_RUNS = {"run1": "run1/panel1/post", "run2": "run2/panel2/post", "run3": "run3/panel3/post"}
RESOURCES = [
    ("ts.wheat", "run1", "wheat_1"), ("ts.buffalo", "run1", "buffalo_1"), ("ts.horses", "run1", "horses_1"),
    ("ts.grassland_resources", "run1", "grassland_resources_2"), ("ts.fruit", "run1", "fruit_1"),
    ("ts.gems", "run2", "gems_1"), ("ts.oasis", "run1", "oasis_1"), ("ts.oil", "run2", "oil_1"),
    ("ts.pheasant", "run1", "pheasant_1"), ("ts.silk", "run2", "silk_1"), ("ts.coal", "run3", "coal_a_1"),
    ("ts.wine", "run2", "wine_1"), ("ts.gold", "run2", "gold_1"), ("ts.iron", "run2", "iron_1"),
    ("ts.tundra_game", "run1", "tundra_game_2"), ("ts.furs", "run1", "furs_1"),
    ("ts.arctic_ivory", "run1", "arctic_ivory_1"), ("ts.peat", "run2", "peat_1"), ("ts.spice", "run2", "spice_1"),
    ("ts.fish", "run1", "fish_2"), ("ts.whales", "run1", "whales_1"),
]

# Trees, hills and mountains (issues 224 and 229): the Freeciv45 art pack's standing props, set 2 (the art repo's
# freeciv45/02_terrain_features, --features-art, runs 5 to 8; run 4's dark peaks for inaccessible), cut at 192 px = one
# tile wide (post/raw), placed the way its TREES_AND_RELIEF_2.md ("Runs 5 to 8") says. The client draws one sprite per
# layer per tile, so each terrain gets variants baked here, each one stand of trees (with a clump) or one hill or
# mountain on a full tile (W x 3H/2, drawn tall on layer 2); the client picks one per tile. A "<terrain>_<type>" set is
# drawn where one of the eight neighbours has that layer 2 match type (patch 0030): pines next to tundra, dry hills
# next to desert, cold peaks next to tundra or glacier. Hills and mountains also have sets per neighbour form (patch
# 0034): a ridge or range along the grid line their own kind continues on. Only the props named here end up in the
# tileset, baked into features.png.
FH = H * 3 // 2                       # the full tile: the diamond at the bottom, half a tile of headroom
FEATURE_PANELS = {"forest": "run5/panel5", "wet": "run6/panel6", "hills": "run7/panel7", "peaks": "run8/panel8",
                  "dark": "run4/panel4"}
# tag: (panel, stands (a pattern twice makes those stands twice as common), stand scale, clump scale, share of
# variants with a clump). One variant per stand: the stand's foot 24 px below the diamond centre, a clump of its kind
# (CLUMPS) 44 px to one side and 34 px below.
TREES = {
    "forest": ("forest", ["stand_broadleaf_*", "stand_mixed_*", "stand_pine_*"] * 2 + ["stand_autumn_*"], 0.82, 0.65,
               1),                    # autumn on about one forest tile in eleven
    "forest_tundra": ("forest", ["stand_pine_*", "stand_snowpine_*"], 0.82, 0.65, 1),
    "jungle": ("wet", ["stand_jungle_[1-5]", "stand_jungle_[1-5]", "stand_jungle_palm_*", "stand_jungle_tall_2"],
               0.82, 0.65, 1),        # the tall emergents look like mushrooms: one of them, rarely
    "swamp": ("wet", ["stand_mangrove_*", "stand_reeds_*", "stand_snags_*"] * 2, 0.5, 0.4, 0.6),
}
CLUMPS = {"stand_broadleaf": "clump_broadleaf_*", "stand_autumn": "clump_broadleaf_*", "stand_mixed": "clump_mixed_*",
          "stand_pine": "clump_pine_*", "stand_snowpine": "clump_pine_*", "stand_jungle": "clump_jungle_*",
          "stand_jungle_palm": "clump_jungle_*", "stand_jungle_tall": "clump_jungle_*", "stand_mangrove": "swamp_*",
          "stand_reeds": "swamp_*", "stand_snags": "swamp_*"}
# tag: (panel, singles, ridges or ranges along the right-rising grid line, along the left-rising one, single scale,
# ridge scale, a single's foot below the diamond centre in px). One variant per prop. A ridge's foot is a quarter of
# its width below the centre, so its ends meet the next tile's on the grid line. A tile with its own kind on one grid
# line only (cardinal forms, patch 0034) draws a ridge along it; one with its kind on both or neither, a single.
RELIEF2 = {
    "hills": ("hills", ["cluster_green_*", "cluster_rocky_*"], ["ridge_green_r*", "ridge_rocky_r*"],
              ["ridge_green_l*", "ridge_rocky_l*"], 0.9, 1.1, 22),
    "hills_desert": ("hills", ["cluster_dry_*"], ["ridge_dry_r*"], ["ridge_dry_l*"], 0.9, 1.1, 22),
    "mountains": ("peaks", ["peak_warm_*", "peak_tipped_*"], ["range_r*"], ["range_l*"], 0.85, 1.15, 22),
    "mountains_tundra": ("peaks", ["peak_cold_*"], ["range_r*"], ["range_l*"], 0.85, 1.15, 22),
    "inaccessible": ("dark", ["peak_dark_*"], [], [], 0.82, 0, 30),
}
CLEAN = ("range_l1", "range_l2")      # edge fragments next to the range (run 8 r4c1 and r4c2)
# The client's cardinal forms (n, e, s, w): north and south lie on the right-rising grid line in the iso view.
LINE_FORMS = {"r": ["n1e0s0w0", "n0e0s1w0", "n1e0s1w0"], "l": ["n0e1s0w0", "n0e0s0w1", "n0e1s0w1"]}
# Each tile's layer 2: (match type, the neighbour types of its second set, named after the first).
FEATURE_TILES = {"forest": ("forest", ["tundra"]), "jungle": ("jungle", []), "swamp": ("swamp", []),
                 "hills": ("hills", ["desert"]), "mountains": ("mountains", ["tundra", "arctic"]),
                 "inaccessible": ("inaccessible", [])}
# Ground under the props: green-gold plains under hills, tundra under the pines next to tundra (forest_tundra), and
# under mountains the rocky desert, graded grey-brown (GRADE). Forest and jungle stand on CANOPY_BASE's grassland.
FEATURE_BASE = [("hills", "run6", sq.row(1)), ("mountains", "run19", sq.row(5)), ("forest_tundra", "run19", sq.row(3))]

def square_point(x, y):
    """The square tile point (u, v) under the diamond's pixel centre (x, y)."""
    a, b = x + 0.5 - W / 2, y + 0.5
    return T * (a / W + b / H), T * (b / H - a / W)

def region_mask(w, h, ox, oy, u0, u1, v0, v1):
    """Binary L mask of the w x h rectangle at (ox, oy) in the diamond's frame: 255 where the pixel centre's square
    point lies in [u0, u1) x [v0, v1). The centres never fall on a tile or quarter edge (u is x + 2y - 94.5 for
    192 x 96), so neighbouring masks share no pixel and leave none out."""
    m = Image.new("L", (w, h), 0); px = m.load()
    for y in range(h):
        for x in range(w):
            u, v = square_point(ox + x, oy + y)
            if u0 <= u < u1 and v0 <= v < v1: px[x, y] = 255
    return m

DIAMOND = region_mask(W, H, 0, 0, 0, T, 0, T)
# The client's corner cells in isometric view, in its order (u d r l, the QUARTERS of make-freeciv45test.py): the
# top left of each W/2 x H/2 cell in the diamond.
CELL_ORIGIN = {"u": (W // 4, 0), "d": (W // 4, H // 2), "r": (W // 2, H // 4), "l": (0, H // 4)}

def to_iso(src, u0, v0, size, origin):
    """The w x h part at origin (ox, oy) of the diamond's frame, sampled from the square image src whose pixel
    (0, 0) is square point (u0, v0): SS x SS nearest samples per pixel, averaged with premultiplied alpha. RGBA."""
    (w, h), (ox, oy) = size, origin
    a, b = T / (W * SS), T / (H * SS)
    c = (ox - W / 2) * T / W + oy * T / H - u0
    f = -(ox - W / 2) * T / W + oy * T / H - v0
    big = src.convert("RGBA").convert("RGBa").transform((w * SS, h * SS), Image.AFFINE, (a, b, c, -a, b, f),
                                                        resample=Image.NEAREST)
    return big.reduce(SS).convert("RGBA")

def iso_ground(square):
    """A T px seamless square ground cell as a W x H diamond (the square wraps, so the samples at the outline read
    the neighbouring tile's side of the texture)."""
    wrap = Image.new("RGB", (3 * T, 3 * T))
    for j in range(3):
        for i in range(3): wrap.paste(square, (i * T, j * T))
    out = to_iso(wrap, -T, -T, (W, H), (0, 0)); out.putalpha(DIAMOND)
    return out

def pad(im, p):
    """im with p more pixels on every side, copied from its outermost row or column (so samples just past a cell's
    edge read the cell)."""
    w, h = im.size; out = Image.new(im.mode, (w + 2 * p, h + 2 * p)); out.paste(im, (p, p))
    out.paste(im.crop((0, 0, 1, h)).resize((p, h)), (0, p)); out.paste(im.crop((w - 1, 0, w, h)).resize((p, h)), (p + w, p))
    out.paste(out.crop((0, p, w + 2 * p, p + 1)).resize((w + 2 * p, p)), (0, 0))
    out.paste(out.crop((0, p + h - 1, w + 2 * p, p + h)).resize((w + 2 * p, p)), (0, p + h))
    return out

def iso_corner(cell, q):
    """One square quarter cell (T/2 px, RGBA; quarter q) as the client's isometric corner cell, W/2 x H/2."""
    (qx, qy), half, p = sq.QUARTERS[[n for n, _, _ in sq.QUARTERS].index(q)][1], T // 2, 8
    ox, oy = CELL_ORIGIN[q]
    out = to_iso(pad(cell, p), qx * half - p, qy * half - p, (W // 2, H // 2), (ox, oy))
    mask = region_mask(W // 2, H // 2, ox, oy, qx * half, (qx + 1) * half, qy * half, (qy + 1) * half)
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return out

def iso_blend_mask(square_mask):
    """A 3T x 3T square blend mask as 3 x 3 diamonds, each in its own W x H rectangle (map order): 3W x 3H."""
    out = Image.new("RGBA", (3 * W, 3 * H), (255, 255, 255, 0))
    for cy in range(3):
        for cx in range(3):
            if (cx, cy) == (1, 1): continue
            alpha = to_iso(square_mask, -cx * T, -cy * T, (W, H), (0, 0)).getchannel("A")
            cell = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            cell.putalpha(ImageChops.multiply(alpha, DIAMOND))
            out.paste(cell, (cx * W, cy * H))
    return out

def rewrite_spec(path, dx, dy):
    """A spec make-freeciv45test.py wrote, for the isometric cells: the grid's new cell size and this tileset's
    wording. Returns its tags as (row, col, tag)."""
    text = open(path).read()
    text = text.replace("Freeciv45 test tileset", "Freeciv45 iso tileset")
    text = re.sub(r"\ndx = \d+\ndy = \d+\n", "\ndx = %d\ndy = %d\n" % (dx, dy), text, count=1)
    text = text.replace("\n\n[spec]", "\n; Then turned into %dx%d isometric cells (make-%s.py, to_iso).\n\n[spec]"
                        % (dx, dy, NAME), 1)
    open(path, "w").write(text)
    _, grids = sq.parse_spec(path)
    return [(r, c, tags[0]) for g in grids for r, c, tags in g["cells"]]

def grade(im, dl, da, db):
    """im (RGB) moved in CIE Lab by (dl, da, db), keeping its texture."""
    to_lab, to_rgb = sq.lab_transforms()
    bands = [band.point(lambda v, d=d: max(0, min(255, v + d)))
             for band, d in zip(ImageCms.applyTransform(im, to_lab).split(), (dl, da, db))]
    return ImageCms.applyTransform(Image.merge("LAB", bands), to_rgb)

def ground(out_dir, record):
    """terrain45.png: freeciv45test's square sheet, each cell as a diamond (GRADE first)."""
    path = os.path.join(out_dir, "terrain45.png"); square = Image.open(path).convert("RGB")
    cells = rewrite_spec(os.path.join(out_dir, "terrain45.spec"), W, H)
    rows, cols = max(r for r, _, _ in cells) + 1, max(c for _, c, _ in cells) + 1
    sheet = Image.new("RGBA", (cols * W, rows * H), (0, 0, 0, 0))
    for r, c, tag in cells:
        cell = square.crop((c * T, r * T, (c + 1) * T, (r + 1) * T))
        terrain = re.match(r"t\.l0\.([a-z_]+?)\d+$", tag).group(1)
        if terrain in GRADE: cell = grade(cell, *GRADE[terrain])
        if any(LAND_GRADE) and terrain not in sq.WATER: cell = grade(cell, *LAND_GRADE)
        sheet.paste(iso_ground(cell), (c * W, r * H))
    sheet.save(path, optimize=True)
    record.append("| `%s/terrain45.spec` | the cells above, each turned 45 degrees and squashed 2:1 (to_iso, %dx%d "
                  "samples, binary outline); graded in Lab: %s%s | %dx%d diamonds | %dx%d |"
                  % (NAME, SS, SS, ", ".join("%s %+d %+d %+d" % ((t,) + g) for t, g in GRADE.items()),
                     "; land %+d %+d %+d" % LAND_GRADE if any(LAND_GRADE) else "", W, H, cols * W, rows * H))
    return {tag for _, _, tag in cells}

def coast(out_dir, record, relief=True):
    """coast.png: freeciv45test's square quarter cells as isometric corner cells (32 columns, 8 per quarter)."""
    path = os.path.join(out_dir, "coast.png"); square = Image.open(path).convert("RGBA")
    cells = rewrite_spec(os.path.join(out_dir, "coast.spec"), W // 2, H // 2)
    half = T // 2; rows = max(r for r, _, _ in cells) + 1
    sheet = Image.new("RGBA", (32 * W // 2, rows * H // 2), (0, 0, 0, 0))
    for r in range(rows):
        for c in range(32):
            q = sq.QUARTERS[c // 8][0]
            cell = square.crop((c * half, r * half, (c + 1) * half, (r + 1) * half))
            sheet.paste(iso_corner(cell, q), (c * W // 2, r * H // 2))
    sheet.save(path, optimize=True)
    if relief:      # t.l2.<water>_cell_<q><abc> (1: the neighbour differs) -> _<q>_<a|w>_<a|w>_<a|w> (a: arctic)
        spec = os.path.join(out_dir, "coast.spec"); text = open(spec).read()
        text = re.sub(r'"t\.l2\.(\w+?)_cell_([udrl])([01])([01])([01])"',
                      lambda m: '"t.l2.%s_cell_%s_%s"' % (m.group(1), m.group(2),
                                                          "_".join("a" if d == "1" else "w" for d in m.group(3, 4, 5))),
                      text)
        open(spec, "w").write(text)
    record.append("| `%s/coast.spec` | the shore cells above as isometric corner cells (to_iso, each quarter "
                  "padded by its own edge) | %dx%d cells | %dx%d |" % (NAME, W // 2, H // 2, 16 * W, rows * H // 2))

def blend(out_dir, record):
    """blend.png and blend.spec: t.blend_mask and _2 .. sq.BLEND_MASKS (freeciv45test's wandering masks, seeds 1 up,
    turned per tile) and mask.tile, the diamond (replacing amplio2's, so fog and overlays follow the same outline)."""
    tags = ["t.blend_mask"] + ["t.blend_mask_%d" % k for k in range(2, sq.BLEND_MASKS + 1)]
    masks = [iso_blend_mask(sq.one_mask(sq.BLEND_DEPTH, random.Random(k))) for k in range(1, sq.BLEND_MASKS + 1)]
    sheet = Image.new("RGBA", (3 * W * len(masks), 3 * H + H), (255, 255, 255, 0))
    for i, m in enumerate(masks): sheet.paste(m, (i * 3 * W, 0))
    sheet.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 3 * H), DIAMOND)
    sheet.save(os.path.join(out_dir, "blend.png"), optimize=True)
    with open(os.path.join(out_dir, "blend.spec"), "w") as f:
        f.write("; Blend masks and the tile outline for the Freeciv45 iso tileset, generated by tilesets/make-%s.py:\n"
                "; 3 x 3 tiles each in map order, every tile a %dx%d diamond in its own rectangle, how strongly a\n"
                "; terrain shows in each tile around it (fork patches 0019, 0028 and 0033).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    Generated (no artist)\n"\n\n'
                '[file]\ngfx = "%s/blend"\n\n[grid_masks]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n\n'
                '[grid_tile]\n\nx_top_left = 0\ny_top_left = %d\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n  0, 0, "mask.tile"\n}\n'
                % (NAME, W, H, NAME, 3 * W, 3 * H, "\n".join('  0, %d, "%s"' % (i, t) for i, t in enumerate(tags)),
                   3 * H, W, H))
    record.append("| `%s/blend.spec` | generated: freeciv45test's `t.blend_mask` and `_2`-`_%d` (seeds 1-%d) turned "
                  "per tile; `mask.tile`, the diamond | none | %dx%d |"
                  % (NAME, sq.BLEND_MASKS, sq.BLEND_MASKS, 3 * W * len(masks), 4 * H))

def resources(res_dir, out_dir, record):
    """resources.png and resources.spec: RESOURCES' picks, five to a row, each as cut (192x96, RGBA)."""
    cols = 5; rows = (len(RESOURCES) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * W, rows * H), (0, 0, 0, 0))
    for i, (tag, run, pick) in enumerate(RESOURCES):
        prop = Image.open(os.path.join(res_dir, RESOURCE_RUNS[run], pick + ".png")).convert("RGBA")
        assert prop.size == (W, H), (pick, prop.size)
        sheet.paste(prop, ((i % cols) * W, (i // cols) * H))
    sheet.save(os.path.join(out_dir, "resources.png"), optimize=True)
    with open(os.path.join(out_dir, "resources.spec"), "w") as f:
        f.write("; Resources for the Freeciv45 iso tileset: the Freeciv45 art pack's isometric props (freeciv45/03_resources),\n"
                "; one pick per tag, copied by tilesets/make-%s.py (see RECORD.md).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/resources"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n'
                % (NAME, NAME, W, H, "\n".join('  %d, %d, "%s"' % (i // cols, i % cols, t)
                                               for i, (t, _, _) in enumerate(RESOURCES))))
    record.append("| `%s/resources.spec` | the art pack's resource props (`freeciv45/03_resources`, cut by `tools/props.py`), "
                  "one pick per tag: %s | none (as cut, %dx%d) | %dx%d |"
                  % (NAME, ", ".join("%s `%s/%s`" % (t[3:], run, pick) for t, run, pick in RESOURCES), W, H,
                     cols * W, rows * H))
    return {t for t, _, _ in RESOURCES}

def largest(im):
    """The prop with only its largest piece of alpha (and that piece's soft rim), then trimmed: drops the fragments of
    a neighbouring cell at the edge."""
    a = im.getchannel("A"); w, h = a.size; px = a.load(); seen = bytearray(w * h); best = []
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] < 16 or seen[y0 * w + x0]: continue
            todo, piece = [(x0, y0)], []; seen[y0 * w + x0] = 1
            while todo:
                x, y = todo.pop(); piece.append((x, y))
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny] >= 16:
                            seen[ny * w + nx] = 1; todo.append((nx, ny))
            if len(piece) > len(best): best = piece
    keep = Image.new("L", (w, h), 0); kp = keep.load()
    for x, y in best: kp[x, y] = 255
    keep = keep.filter(ImageFilter.MaxFilter(5))
    im = im.copy(); im.putalpha(ImageChops.multiply(a, keep)); return im.crop(im.getbbox())

def scaled(im, s):
    im = im.convert("RGBa").resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return im.convert("RGBA")

def features(feat_dir, out_dir, record):
    """features.png and features.spec: TREES' and RELIEF2's variants, ten to a row, each a W x FH full tile. A cell
    drawn for several sets (the ranges, for mountains and cold mountains, on each of a line's three forms) carries all
    their tags."""
    def props(panel, pats):
        out = []
        for pat in pats:
            for path in sorted(glob.glob(os.path.join(feat_dir, FEATURE_PANELS[panel], "post", "raw", pat + ".png"))):
                name = os.path.basename(path)[:-4]
                im = Image.open(path).convert("RGBA")
                out.append((name, largest(im) if name in CLEAN else im.crop(im.getbbox())))
        assert out, (panel, pats)
        return out
    cx, cy = W / 2, FH - H / 2           # the diamond's centre on the canvas
    cells, made, used = [], {}, set()
    def put(canvas, tag, key=None):
        if key in made: cells[made[key]][0].append(tag); return
        if key: made[key] = len(cells)
        cells.append(([tag], canvas))
    def stand(canvas, name, im, s, x, foot):
        """im scaled by s, no larger than the full tile, its foot foot px below the centre and its middle at x."""
        im = scaled(im, min(s, (cy + foot) / im.height, W / im.width))
        x = min(max(x, im.width / 2), W - im.width / 2)
        canvas.alpha_composite(im, (round(x - im.width / 2), round(min(FH, cy + foot)) - im.height)); used.add(name)
    for tag, (panel, pats, scale, cscale, share) in TREES.items():
        for k, (name, im) in enumerate(props(panel, pats)):
            rng = random.Random("%s %d" % (tag, k)); canvas = Image.new("RGBA", (W, FH), (0, 0, 0, 0))
            stand(canvas, name, im, scale * rng.uniform(0.94, 1.04), cx + rng.randint(-6, 6), 24)
            if rng.random() < share:
                cname, cim = rng.choice(props(panel, [CLUMPS[name.rstrip("0123456789").rstrip("_")]]))
                stand(canvas, cname, cim, cscale * rng.uniform(0.94, 1.04), cx + rng.choice((-44, 44)), 34)
            put(canvas, "t.l2.%s%d" % (tag, k + 1))
    for tag, (panel, singles, right, left, scale, rscale, foot) in RELIEF2.items():
        rng = random.Random(tag)
        for k, (name, im) in enumerate(props(panel, singles)):
            canvas = Image.new("RGBA", (W, FH), (0, 0, 0, 0))
            stand(canvas, name, im, scale * rng.uniform(0.94, 1.04), cx, foot)
            put(canvas, "t.l2.%s%d" % (tag, k + 1))
        for line, pats in (("r", right), ("l", left)):
            for k, (name, im) in enumerate(props(panel, pats) if pats else []):
                canvas = None
                if (panel, name) not in made:
                    canvas = Image.new("RGBA", (W, FH), (0, 0, 0, 0)); s = min(rscale, W / im.width)
                    stand(canvas, name, im, s, cx, round(im.width * s) / 4 + 4)
                for form in LINE_FORMS[line]:
                    put(canvas, "t.l2.%s_%s_%d" % (tag, form, k + 1), (panel, name))
    cols = 10; rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * W, rows * FH), (0, 0, 0, 0))
    for i, (_, canvas) in enumerate(cells): sheet.paste(canvas, ((i % cols) * W, (i // cols) * FH))
    sheet.save(os.path.join(out_dir, "features.png"), optimize=True)
    with open(os.path.join(out_dir, "features.spec"), "w") as f:
        f.write("; Trees, hills and mountains for the Freeciv45 iso tileset: the Freeciv45 art pack's standing props\n"
                "; (freeciv45/02_terrain_features), stood on full tiles by tilesets/make-%s.py (see RECORD.md).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/features"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n'
                % (NAME, NAME, W, FH, "\n".join('  %d, %d, %s' % (i // cols, i % cols, ", ".join('"%s"' % t for t in ts))
                                               for i, (ts, _) in enumerate(cells))))
    tags = [t for ts, _ in cells for t in ts]
    sets = ["%s %d" % (t, sum(1 for c in tags if re.fullmatch(r"t\.l2\.%s\d+" % t, c))) for t in list(TREES) + list(RELIEF2)]
    forms = ["%s %d" % (t, sum(1 for c in tags if re.fullmatch(r"t\.l2\.%s_n1e0s1w0_\d+" % t, c)))
             for t in RELIEF2 if RELIEF2[t][2]]
    record.append("| `%s/features.spec` | the art pack's standing props (`freeciv45/02_terrain_features`, runs 4-8, "
                  "`post/raw`): %s; variants %s; ridges and ranges per grid line %s | LANCZOS (TREES and RELIEF2 "
                  "scales) | %dx%d |" % (NAME, ", ".join("`%s`" % n for n in sorted(used)), ", ".join(sets),
                                         ", ".join(forms), cols * W, rows * FH))
    return set(tags), sorted(used)

def feature_sections(ours):
    """freeciv45test's sections with the props on layer 2 (FEATURE_TILES): whole-tile variants, tall, with a second
    set where a neighbour has the pair type; tundra and desert get their own layer 2 types for those pairs (they draw
    nothing there), and the water tiles' ice edge is matched as a pair against arctic."""
    types = ["water", "arctic", "tundra", "desert"] + [t for t, _ in FEATURE_TILES.values()]
    assert len({t[0] for t in types}) == len(types)            # the client tells match types by their first letter
    out = {}
    for name, text in ours.items():
        terrain = name[5:]
        if name == "layer2":
            text = re.sub(r'match_types = "water", "arctic"', "match_types = " + ", ".join('"%s"' % t for t in types), text)
        elif terrain in FEATURE_TILES:
            kind, pair = FEATURE_TILES[terrain]
            text = re.sub(r'layer2_match_type = "water"\n(layer2_match_with = "\w+"\n)?',
                          'layer2_match_type = "%s"\n%slayer2_is_tall = TRUE\n'
                          % (kind, 'layer2_match_with = %s\n' % ", ".join('"%s"' % p for p in pair) if pair else ""),
                          text)
            text = text.replace('layer2_sprite_type = "corner"\n', "")
        elif terrain in ("tundra", "desert"):
            text = text.replace('layer2_match_type = "water"', 'layer2_match_type = "%s"' % terrain)
        elif terrain in sq.WATER:
            text = text.replace('layer2_match_with = "water"', 'layer2_match_with = "arctic"')
        out[name] = text
    for terrain, (kind, pair) in FEATURE_TILES.items():
        assert 'layer2_match_type = "%s"' % kind in out["tile_" + terrain] and "layer2_is_tall" in out["tile_" + terrain]
    return out

class Drop:
    """Tags recut() leaves out: the ones this tileset draws itself, and DROP_PREFIX's for the spec being cut."""
    def __init__(self, own): self.own, self.prefixes = own, ()
    def __contains__(self, tag): return tag in self.own or tag.startswith(self.prefixes)

def square_sections(data, files):
    """freeciv45test's [layerN] and [tile_*] sections, as make-freeciv45test.py writes them from trident."""
    with tempfile.TemporaryDirectory() as tmp:
        sq.tilespec(data, tmp, files)
        text = open(os.path.join(tmp, sq.NAME + ".tilespec")).read()
    sections, name = {}, None
    for line in text.split("\n"):
        m = re.match(r"\s*\[(\w+)\]", line)
        if m: name = m.group(1); sections[name] = []
        if name and (name.startswith("layer") or name.startswith("tile_")): sections[name].append(line)
    return {k: "\n".join(v).rstrip() + "\n" for k, v in sections.items() if k.startswith(("layer", "tile_"))}

def relief_sections(ours, canopy=False):
    """freeciv45test's sections with RELIEF on layer 2: hills and mountains matched as "hills" (amplio2's
    16 forms), mountains tall and 12 px lower (amplio2's 6, doubled), and the water tiles' ice edge matched as a pair
    against arctic, so a hill next to water draws no ice. With canopy, forest and jungle are matched the same way on
    layer 2, each as its own type."""
    trees = [t for ts in CANOPY.values() for t in ts] if canopy else []
    out = {}
    for name, text in ours.items():
        if name == "layer2":
            text = re.sub(r'match_types = "water", "arctic"',
                          'match_types = "water", "arctic", "hills"' + "".join(', "%s"' % t for t in trees), text)
        elif name[5:] in trees:
            text = text.replace('layer2_match_type = "water"',
                                'layer2_match_type = "%s"\nlayer2_match_with = "%s"' % (name[5:], name[5:]))
        elif name[5:] in RELIEF.values():
            extra = '\nlayer2_is_tall = TRUE\nlayer2_offset_y = %d' % (6 * AMPLIO_SCALE) if name == "tile_mountains" else ""
            text = text.replace('layer2_match_type = "water"',
                                'layer2_match_type = "hills"\nlayer2_match_with = "hills"' + extra)
        elif name[5:] in sq.WATER:
            text = text.replace('layer2_match_with = "water"', 'layer2_match_with = "arctic"')
        out[name] = text
    assert "hills" in out["layer2"] and 'layer2_match_with = "hills"' in out["tile_mountains"]
    assert all('layer2_match_with = "%s"' % t in out["tile_" + t] for t in trees)
    return out

def tilespec(data, out_root, files, blend=True, relief=True, canopy=False, bk=False, units=False, icons=False):
    """amplio2.tilespec with sizes and offsets doubled, pixel_ratio 2, the file list renamed, and freeciv45test's
    layer and terrain sections in place of amplio2's (amplio2's other terrains kept, matched as mountains)."""
    ours = square_sections(data, files)
    if bk: ours = feature_sections(ours)
    elif relief: ours = relief_sections(ours, canopy)
    out, section, in_files, inserted, skipping = [], None, False, False, False
    for raw in open(os.path.join(data, "amplio2.tilespec"), errors="replace"):
        line = raw.rstrip("\n")
        m = re.match(r"\s*\[(\w+)\]", line)
        if m:
            section = m.group(1); skipping = section in ours
            if skipping and not inserted:
                out.append("; Layers and terrains: freeciv45test's (make-freeciv45test.py), painted ground on layer 0,\n"
                           "; the shore on layers 1 and 2.\n")
                for text in ours.values():
                    out.append(text if blend else re.sub(r"blend_layer = 1", "blend_layer = 0", text))
                inserted = True
        if skipping: continue
        if in_files:
            if line.strip().endswith(",") or line.strip().startswith('"'):
                if not line.strip().endswith(","): in_files = False
                continue
            in_files = False
        m = re.match(r"\s*(\w+)\s*=\s*(-?\d+)?", line)
        key, num = (m.group(1), m.group(2)) if m else (None, None)
        if section == "tilespec":
            if key == "files":
                out.append("files =\n" + ",\n".join('  "%s"' % f for f in files)); in_files = True; continue
            if icons and key == "options":       # tech_icons.spec and building_icons.spec come after the stock misc/ ones
                out.append(line.rstrip().rstrip('"') + ' duplicates_ok"'); continue
            if key == "name": out.append('name = "Freeciv45 iso"'); continue
            if key == "priority": out.append("priority = 4"); continue
            if key == "summary":
                out.append('summary = _("Freeciv45 iso tileset: %dx%d diamonds, painted ground for every terrain, '
                           'amplio2 for the rest.")' % (W, H)); continue
            if units and key in ("unit_offset_x", "unit_offset_y"):      # UNIT_CELL's top left, from the full tile's
                out.append("%s = %d" % (key, (W - UNIT_CELL[0]) // 2 if key.endswith("x") else 0)); continue
            if num is not None and (key in ("normal_tile_width", "normal_tile_height", "svg_height")
                                    or key.endswith(("_offset_x", "_offset_y"))):
                out.append("%s = %d" % (key, int(num) * AMPLIO_SCALE))
                if key == "citybar_offset_y":       # patch 0049 (issue 252): the flag is a chip, not a banner over the city
                    out.append("\n; The city bar draws the nation flag as a chip this high (tileset pixels), so the flag does not\n"
                               "; cover the city's own art; 0 draws it at its own size\ncitybar_flag_height = 32")
                if key == "normal_tile_height":
                    out.append("\n; Tileset pixels per screen point: the map shows a %dx%d tile as %dx%d points, so on a 2x\n"
                               "; (Retina) screen every pixel is drawn (Freeciv45 fork, Qt client).\npixel_ratio = %d"
                               % (W, H, W // AMPLIO_SCALE, H // AMPLIO_SCALE, AMPLIO_SCALE))
                continue
        if section and section.startswith("tile_") and key == "layer0_match_type":
            out.append('layer0_match_type = "mountains"'); continue      # amplio2's volcanoes; "land" is not a type here
        out.append(line)
    text = "\n".join(out) + "\n"
    text = text.replace("[tilespec]\n", "[tilespec]\n\n; Freeciv45 iso tileset, built by tilesets/make-%s.py from "
                        "amplio2.tilespec; see RECORD.md.\n" % NAME, 1)
    open(os.path.join(out_root, NAME + ".tilespec"), "w").write(text)

# Units, cities, marks and ruins (issue 245): the Freeciv45 art pack's units (freeciv45/04_units runs 1 to 5, --units-art) and
# cities (freeciv45/05_cities, --cities-art), cut at 192 px = one tile wide (post/raw, sizes as drawn), in place of
# amplio2's. Which sprites: the ruleset's. Every `graphic` of civ45's units.ruleset gets its unit (the better take, UNIT_PICK;
# flipped to face screen-left, UNIT_FLIP) and every `city.<style>` of its styles.ruleset gets city_0 to 4 and wall_0 to 4;
# nothing else of the runs ships (the second takes, the unused ruins, the panels). Each sprite is tidied first: stray
# pieces of the neighbouring cell dropped, the colour of the translucent edge pixels bled in from the opaque ones (the cut
# has a red and yellow fringe), trimmed.
UNIT_RUNS = ("run1/panel1", "run2/panel2", "run3/panel3", "run4/panel4")
UNIT_PICK = {"musketeers": "musketeers_alt"}     # the first take faces right; the second faces left
UNIT_FLIP = ("grenadiers",)                       # the one pick that faces right
UNIT_CELL = (160, 128)    # a unit's cell: drawn at unit_offset (16, 0), so its middle is the tile's middle and its top is the full tile's
UNIT_FOOT = 108           # the foot of a unit in its cell: 12 px below the diamond's centre (the full tile's top is 48 px above the tile)
UNIT_SCALE = 0.7          # the cut's 192 px cell to the map's (a standing person comes out 80 px tall, amplio2's 90)
UNIT_MAX = (150, UNIT_FOOT)
CITY_PICK = ("city_0", "city_1", "city_2", "city_3", "city_4", "wall_0", "wall_1", "wall_2", "wall_3", "wall_4")
RUINS_PICK = "ruins_1"                            # ruins_2 to 5 are takes for the other styles
# The marks (04_units run 5): tag of the tileset, the cut's name. unit.irrigate and unit.cultivate are two marks here (the
# axe and the water channel); amplio2 shared one.
MARK_RUN = "run5/panel5"
ACTIVITIES = [("unit.road", "road"), ("unit.rail", "rail"), ("unit.fortress", "fortress"), ("unit.airbase", "airbase"),
              ("unit.fortified", "fortified"), ("unit.fortifying", "fortifying"), ("unit.sentry", "sentry"),
              ("unit.patrol", "patrol"), ("unit.pillage", "pillage"), ("unit.cultivate", "cultivate"),
              ("unit.irrigate", "irrigate"), ("unit.irrigation", "irrigate"), ("unit.plant", "plant"),
              ("unit.transform", "transform"), ("unit.pollution", "pollution"), ("unit.goto", "goto"),
              ("unit.convert", "convert"), ("unit.auto_explore", "auto_explore"),
              ("unit.action_decision_want", "action_decision_want"), ("unit.farmland", "farmland"), ("unit.mine", "mine")]
VET = [("unit.vet_1", "vet_1"), ("unit.vet_2", "vet_2"), ("unit.vet_3", "vet_3"), ("unit.tired", "tired"),
       ("unit.lowfuel", "lowfuel")]
VET_UNUSED = ["unit.vet_%d" % k for k in range(4, 10)]        # civ45 has four levels: green, veteran, hardened, elite
MARK_CELL, VET_CELL = (56, 48), (128, 112)
VET_SLOTS = {"unit.tired": 80, "unit.lowfuel": 112}           # the badges' centres across a vet cell; the vets are at 48

def pieces(im, share=0.6, floor=8):
    """The prop with only its pieces of alpha (8-connected, from alpha floor) at least `share` of the largest, each with
    its soft rim 2 px out; the rest (fragments of the neighbouring cell) is cleared."""
    a = im.getchannel("A"); w, h = a.size; px = a.load(); seen = bytearray(w * h); found = []
    for y0 in range(h):
        for x0 in range(w):
            if px[x0, y0] < floor or seen[y0 * w + x0]: continue
            todo, piece = [(x0, y0)], []; seen[y0 * w + x0] = 1
            while todo:
                x, y = todo.pop(); piece.append((x, y))
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny] >= floor:
                            seen[ny * w + nx] = 1; todo.append((nx, ny))
            found.append(piece)
    big = max(len(p) for p in found); keep = Image.new("L", (w, h), 0); kp = keep.load()
    for piece in found:
        if len(piece) >= share * big:
            for x, y in piece: kp[x, y] = 255
    keep = keep.filter(ImageFilter.MaxFilter(5))
    out = im.copy(); out.putalpha(ImageChops.multiply(a, keep)); return out

def defringe(im, floor=200, reach=4):
    """The colour of every pixel below alpha `floor` replaced by the distance-weighted mean colour of the pixels at or
    above it within `reach` px (alpha kept), so a translucent edge no longer carries the cut's red and yellow fringe."""
    w, h = im.size; px = im.load(); out = im.copy(); op = out.load()
    offs = [(dx, dy, 1.0 / (dx * dx + dy * dy)) for dy in range(-reach, reach + 1) for dx in range(-reach, reach + 1)
            if dx or dy]
    for y in range(h):
        for x in range(w):
            a = px[x, y][3]
            if a == 0 or a >= floor: continue
            sr = sg = sb = sw = 0.0
            for dx, dy, wt in offs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    r, g, b, na = px[nx, ny]
                    if na >= floor: sr += r * wt; sg += g * wt; sb += b * wt; sw += wt
            if sw: op[x, y] = (round(sr / sw), round(sg / sw), round(sb / sw), a)
    return out

def tidy(path, whole=False):
    """A cut sprite as the tileset uses it: pieces (unless whole), defringed, trimmed."""
    im = Image.open(path).convert("RGBA")
    if not whole: im = pieces(im)
    im = defringe(im)
    return im.crop(im.getchannel("A").point(lambda v: 255 if v >= 16 else 0).getbbox())

def write_spec(out_dir, base, comment, grids):
    """base.spec for base.png: grids is [(name, y_top_left, dx, dy, [(row, column, [tags])])]."""
    with open(os.path.join(out_dir, base + ".spec"), "w") as f:
        f.write("; %s\n\n" % comment.replace("\n", "\n; ") +
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/%s"\n\n' % (NAME, base))
        for name, y, dx, dy, cells in grids:
            f.write('[grid_%s]\n\nx_top_left = 0\ny_top_left = %d\ndx = %d\ndy = %d\n\ntiles = { "row", "column", "tag"\n%s\n}\n\n'
                    % (name, y, dx, dy, "\n".join('  %d, %d, %s' % (r, c, ", ".join('"%s"' % t for t in tags))
                                                 for r, c, tags in cells)))

def ruleset_graphics(data, ruleset, prefix):
    """The `graphic` tags of a civ45 ruleset file that start with prefix, in file order."""
    text = open(os.path.join(data, "civ45", ruleset), errors="replace").read()
    out = []
    for g in re.findall(r'^graphic\s*=\s*"(%s[^"]*)"' % re.escape(prefix), text, re.M):
        if g not in out: out.append(g)
    return out

def find_cut(base, runs, name):
    paths = [os.path.join(base, r, "post", "raw", name + ".png") for r in runs]
    found = [p for p in paths if os.path.exists(p)]
    assert len(found) == 1, (name, found)
    return found[0]

def units(art, data, out_dir, record):
    """units.png and units.spec: civ45's 85 unit sprites (`u.<name>_Idle`), ten to a row, each a UNIT_CELL."""
    tags = [g[2:] for g in ruleset_graphics(data, "units.ruleset", "u.")]
    cw, ch = UNIT_CELL; cols = 10; rows = (len(tags) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0)); used = []
    for i, name in enumerate(tags):
        pick = UNIT_PICK.get(name, name); used.append(pick)
        im = tidy(find_cut(art, UNIT_RUNS, pick))
        if name in UNIT_FLIP: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        s = min(UNIT_SCALE, UNIT_MAX[0] / im.width, UNIT_MAX[1] / im.height)
        im = scaled(im, s); a = im.getchannel("A"); px = a.load(); tot = sx = 0
        for y in range(0, im.height, 2):
            for x in range(im.width): v = px[x, y]; tot += v; sx += v * x
        mid = sx / tot if tot else im.width / 2                  # the body's middle, not the weapon's reach
        x0 = min(max(round(cw / 2 - mid), 0), cw - im.width)
        sheet.alpha_composite(im, ((i % cols) * cw + x0, (i // cols) * ch + UNIT_FOOT - im.height))
    sheet.save(os.path.join(out_dir, "units.png"), optimize=True)
    write_spec(out_dir, "units", "Units for the Freeciv45 iso tileset: the Freeciv45 art pack's units (freeciv45/04_units), one\n"
               "per ruleset graphic, tidied and placed by tilesets/make-%s.py (see RECORD.md). A %dx%d cell, drawn at\n"
               "unit_offset (16, 0), stands on the tile's middle." % (NAME, cw, ch),
               [("main", 0, cw, ch, [(i // cols, i % cols, ["u.%s_Idle" % t]) for i, t in enumerate(tags)])])
    record.append("| `%s/units.spec` | the art pack's units (`freeciv45/04_units`, `post/raw`): the %d sprites of civ45's `units.ruleset`; "
                  "%s | cleaned (pieces, fringe), x%g (at most %dx%d), %s flipped | %dx%d |"
                  % (NAME, len(tags), ", ".join("`%s`" % u for u in sorted(used)), UNIT_SCALE, UNIT_MAX[0], UNIT_MAX[1],
                     ", ".join("`%s`" % u for u in UNIT_FLIP), cols * cw, rows * ch))
    return {"u.%s_Idle" % t for t in tags}, sorted(used)

def cities(art, data, out_dir, record):
    """cities.png and cities.spec: for every style of civ45's styles.ruleset city_0 to 4 and wall_0 to 4, ten to a row, each
    192x144 (a style scaled together, no bigger than the full tile), and the ruins as extra.ruins_mg."""
    styles = [g[5:] for g in ruleset_graphics(data, "styles.ruleset", "city.")]
    cw, ch = W, H * 3 // 2; cols = 10
    def fit(im, s):
        im = scaled(im, s); canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.alpha_composite(im, ((cw - im.width) // 2, min(ch, H + im.width // 4) - im.height)); return canvas
    cells, used = [], []
    for style in styles:
        runs = ["run%d/panel%d" % (k, k) for k in range(1, 6)]
        ims = []
        for p in CITY_PICK:
            name = "%s_%s" % (style, p); used.append(name); ims.append((p, tidy(find_cut(art, runs, name))))
        s = min([1.0] + [min(cw / im.width, ch / im.height) for _, im in ims])
        for p, im in ims: cells.append(("city.%s_%s" % (style, p), fit(im, s)))
    ruin = tidy(find_cut(art, ["run%d/panel%d" % (k, k) for k in range(1, 6)], RUINS_PICK)); used.append(RUINS_PICK)
    cells.append(("extra.ruins_mg", fit(ruin, min(1.0, cw / ruin.width, ch / ruin.height))))
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
    for i, (_, c) in enumerate(cells): sheet.paste(c, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(os.path.join(out_dir, "cities.png"), optimize=True)
    write_spec(out_dir, "cities", "Cities and ruins for the Freeciv45 iso tileset: the Freeciv45 art pack's cities (freeciv45/05_cities),\n"
               "five sizes open and walled for each style of styles.ruleset, tidied and placed by tilesets/make-%s.py (see\n"
               "RECORD.md). In the isometric view the walled sprite is the whole city (client/tilespec.c)." % NAME,
               [("main", 0, cw, ch, [(i // cols, i % cols, [t]) for i, (t, _) in enumerate(cells)])])
    record.append("| `%s/cities.spec` | the art pack's cities (`freeciv45/05_cities`, `post/raw`): %d styles, `city_0`-`city_4` and "
                  "`wall_0`-`wall_4` of each, and `%s` as `extra.ruins_mg` | cleaned (pieces, fringe), each style scaled together to fit "
                  "%dx%d (never up) | %dx%d |" % (NAME, len(styles), RUINS_PICK, cw, ch, cols * cw, rows * ch))
    return {t for t, _ in cells}, sorted(used)

def marks(art, out_dir, record):
    """marks.png and marks.spec: ACTIVITIES (56x48 cells, drawn at the activity offset) and VET (vet_1 to 3, tired,
    lowfuel: 128x112 cells drawn from the full tile's top left, the badges on the unit's left)."""
    badges = {}
    def badge(name):
        if name not in badges: badges[name] = tidy(find_cut(art, [MARK_RUN], name), whole=True)
        return badges[name]
    cols = 10; arows = (len(ACTIVITIES) + cols - 1) // cols
    width = max(10 * MARK_CELL[0], len(VET) * VET_CELL[0])
    sheet = Image.new("RGBA", (width, arows * MARK_CELL[1] + VET_CELL[1]), (0, 0, 0, 0))
    cells = []
    for i, (tag, name) in enumerate(ACTIVITIES):
        b = badge(name); b = scaled(b, min(52 / b.width, 44 / b.height))
        x, y = (i % 10) * 56, (i // 10) * 48
        sheet.alpha_composite(b, (x + (56 - b.width) // 2, y + (48 - b.height) // 2)); cells.append((i // 10, i % 10, [tag]))
    vet_y = arows * MARK_CELL[1]
    for i, (tag, name) in enumerate(VET):
        b = badge(name); b = scaled(b, min(30 / b.width, 30 / b.height)); cx = VET_SLOTS.get(tag, 48)
        sheet.alpha_composite(b, (i * VET_CELL[0] + cx - b.width // 2, vet_y + 84 - b.height // 2))
    sheet.save(os.path.join(out_dir, "marks.png"), optimize=True)
    write_spec(out_dir, "marks", "Marks on units for the Freeciv45 iso tileset: the Freeciv45 art pack's badges (freeciv45/04_units\n"
               "run 5), scaled by tilesets/make-%s.py (see RECORD.md): the activities in %dx%d cells, veteran levels, tired\n"
               "and low fuel in %dx%d cells." % (NAME, MARK_CELL[0], MARK_CELL[1], VET_CELL[0], VET_CELL[1]),
               [("activities", 0, MARK_CELL[0], MARK_CELL[1], cells),
                ("vet", vet_y, VET_CELL[0], VET_CELL[1], [(0, i, [t]) for i, (t, _) in enumerate(VET)])])
    record.append("| `%s/marks.spec` | the art pack's marks (`freeciv45/04_units/%s`, `post/raw`): %s | cleaned (fringe), scaled to fit "
                  "52x44 (activities) or 30x30 (veteran, tired, low fuel) | %dx%d |"
                  % (NAME, MARK_RUN, ", ".join("`%s`" % n for n in sorted({n for _, n in ACTIVITIES + VET})), sheet.width, sheet.height))
    return {t for t, _ in ACTIVITIES + VET} | set(VET_UNUSED), sorted(badges)

# Tech icons and building pictures (issue 254): the art pack's freeciv45/06_tech_icons and 07_building_icons, cut at 192 px (post/raw).
# The client draws the research screen's icons at 48 x 48 and a building's picture at 64 x 48, whatever pixel_ratio is (only the
# map follows it), so each picture is fitted into that cell. What ships (issue 255 completed it): every tech, the ancient and
# classical panels (runs 1 and 2) and the retaken industrial and modern ones (runs 5 and 6), with run 6's second takes for the
# wheel and the republic (TECH_PICK); every building and wonder picture, the second takes of the colossus and the pyramids and
# run 5's retakes of the four wonders (BUILD_PICK). Ours are listed after the stock misc/ files and the tilespec says
# duplicates_ok, so ours win; a tag the runs do not give would keep its stock icon.
TECH_RUNS = ("run1/panel1", "run2/panel2", "run5/panel3", "run6/panel4")      # ancient, classical, industrial, modern (retakes, issue 255)
TECH_PICK = {"the_wheel": "the_wheel_alt", "the_republic": "the_republic_alt"}  # run 6's row 5 retakes of the two weak cells
TECH_CELL, TECH_FILL = 48, 44
BUILD_RUNS = ("run1/panel1", "run2/panel2", "run3/panel3", "run4/panel4")
BUILD_RUNS += ("run5/panel5",)
BUILD_PICK = {"colossus": "colossus_alt", "pyramids": "pyramids_alt", "georgia_guidestones": "georgia_guidestones_r1",
              "united_nations": "united_nations_r3", "shakespeares_theatre": "shakespeares_theatre_r1",
              "statue_of_liberty": "statue_of_liberty_r1"}      # run 5's wonder retakes (issue 255); its lighthouse row is spares
BUILD_CELL, BUILD_FILL = (64, 48), (62, 46)

def raw_names(base, runs):
    """The names of the cuts in post/raw of each run, in run order."""
    out = []
    for r in runs:
        d = os.path.join(base, r, "post", "raw")
        out += [f[:-4] for f in sorted(os.listdir(d)) if f.endswith(".png")]
    return out

def icon_sheet(base, runs, names, cell, fill, out_dir, sheet_name, tag_prefix, comment):
    """sheet_name.png and .spec: the named cuts, tidied and fitted into fill, centred in cells of `cell`, ten to a row."""
    cw, ch = cell; cols = 10; rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0)); cells = []
    for i, (tag, name) in enumerate(names):
        im = tidy(find_cut(base, runs, name)); im = scaled(im, min(fill[0] / im.width, fill[1] / im.height))
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.alpha_composite(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2)); cells.append((i // cols, i % cols, [tag_prefix + tag]))
    sheet.save(os.path.join(out_dir, sheet_name + ".png"), optimize=True)
    write_spec(out_dir, sheet_name, comment, [("main", 0, cw, ch, cells)])
    return sheet.size

def icons(tech_art, build_art, out_dir, record):
    """tech_icons.spec (a.<tech>) and building_icons.spec (b.<building>); returns the two tag lists."""
    techs = [n for n in raw_names(tech_art, TECH_RUNS) if not n.endswith("_alt")]
    assert len(techs) == len(set(techs)) and set(TECH_PICK) <= set(techs), "a tech has two cuts, or a pick has no first take"
    size = icon_sheet(tech_art, TECH_RUNS, [(n, TECH_PICK.get(n, n)) for n in techs], (TECH_CELL, TECH_CELL), (TECH_FILL, TECH_FILL), out_dir,
                      "tech_icons", "a.", "Tech icons for the Freeciv45 iso tileset: the Freeciv45 art pack's freeciv45/06_tech_icons\n"
                      "runs 1, 2, 5 and 6, fitted by tilesets/make-%s.py (see RECORD.md) into %dx%d cells." % (NAME, TECH_CELL, TECH_CELL))
    record.append("| `%s/tech_icons.spec` | the art pack's tech icons (`freeciv45/06_tech_icons`, %s, `post/raw`), %d of civ45's techs: %s | cleaned "
                  "(specks, fringe), fitted into %dx%d | %dx%d |" % (NAME, ", ".join("`%s`" % r for r in TECH_RUNS), len(techs),
                  ", ".join("`%s`" % n for n in techs), TECH_FILL, TECH_FILL, *size))
    names = [n for n in raw_names(build_art, BUILD_RUNS) if not n.endswith("_alt") and not re.search(r"_r\d$", n)]
    pick = [(n, BUILD_PICK.get(n, n)) for n in names + [n for n in BUILD_PICK if n not in names and BUILD_PICK[n][-3:-1] == "_r"]]
    size = icon_sheet(build_art, BUILD_RUNS, pick, BUILD_CELL, BUILD_FILL, out_dir, "building_icons", "b.",
                      "Building and wonder pictures for the Freeciv45 iso tileset: the Freeciv45 art pack's\n"
                      "freeciv45/07_building_icons runs 1 to 5, fitted by tilesets/make-%s.py (see RECORD.md) into %dx%d cells."
                      % (NAME, *BUILD_CELL))
    record.append("| `%s/building_icons.spec` | the art pack's building pictures (`freeciv45/07_building_icons`, %s, `post/raw`), %d of civ45's: %s "
                  "| cleaned (specks, fringe), fitted into %dx%d | %dx%d |" % (NAME, ", ".join("`%s`" % r for r in BUILD_RUNS), len(pick),
                  ", ".join("`%s`" % (b if b == n else "%s` (as `%s" % (b, n)) for n, b in pick), *BUILD_FILL, *size))
    return techs, [n for n, _ in pick], [b for n, b in pick]

# National borders (issue 259): grid.borders.n/s/w/e are white masks the client tints with each nation's colour at load (only
# the alpha matters). The client draws the owner's mask on each edge between two tiles that have different owners, and the
# edge's cell is W x H with the edge's midpoint at its centre, so a mask is a band inside the owning diamond along its edge
# that faces the neighbour: n is the owner above-right of a down-right edge, s below-left of it, w above-left of an
# up-right edge, e below-right (amplio2's dashes sit the same way). Solid for BORDER_CORE px from the edge, crisp on the outer
# side, then fading to nothing over BORDER_FADE px (at 2x), clipped to the owner's diamond so a straight frontier's bands join
# exactly where the tiles meet. Two nations side by side meet with crisp edges on the grid line, one band each.
BORDER_CORE, BORDER_FADE, BORDER_CURVE = 4.0, 10.0, 1.5
BORDER_EDGES = (("n", (W * 3 // 4, H // 4), (1, -2)), ("s", (W // 4, H * 3 // 4), (-1, 2)),
                ("w", (W // 4, H // 4), (-1, -2)), ("e", (W * 3 // 4, H * 3 // 4), (1, 2)))   # owner's centre in the cell, inward normal
BORDER_TAGS = {"grid.borders." + e for e, _, _ in BORDER_EDGES}

def border_alpha(d):
    """The band's coverage at distance d from the edge into the owner's tile."""
    if d < 0: return 0.0
    if d < BORDER_CORE: return 1.0
    t = (d - BORDER_CORE) / BORDER_FADE
    return (1.0 - t) ** BORDER_CURVE if t < 1 else 0.0

def borders(out_dir, record, ss=4):
    """borders.png and borders.spec: grid.borders.n, s, w and e as W x H masks, in a row."""
    sheet = Image.new("RGBA", (W * len(BORDER_EDGES), H), (255, 255, 255, 0)); px = sheet.load()
    for k, (edge, (cx, cy), (nx, ny)) in enumerate(BORDER_EDGES):
        norm = (nx * nx + ny * ny) ** 0.5
        for y in range(H):
            for x in range(W):
                if abs(x + 0.5 - cx) / (W / 2) + abs(y + 0.5 - cy) / (H / 2) >= 1: continue     # the owner's diamond, by pixel centre
                a = sum(border_alpha(((x + (i + 0.5) / ss - W / 2) * nx + (y + (j + 0.5) / ss - H / 2) * ny) / norm)
                        for i in range(ss) for j in range(ss)) / (ss * ss)
                if a > 0: px[k * W + x, y] = (255, 255, 255, round(a * 255))
    sheet.save(os.path.join(out_dir, "borders.png"), optimize=True)
    write_spec(out_dir, "borders", "National border masks for the Freeciv45 iso tileset, generated by tilesets/make-%s.py "
               "(see RECORD.md); the client tints them." % NAME,
               [("main", 0, W, H, [(0, k, ["grid.borders." + e]) for k, (e, _, _) in enumerate(BORDER_EDGES)])])
    record.append("| `%s/borders.spec` | generated (`borders`): `grid.borders.n`, `s`, `w`, `e`, white masks the client tints: a solid band "
                  "%g px wide along the owner's diamond edge facing the neighbour, then a fade to nothing over %g px "
                  "(exponent %g), clipped to the owner's diamond; amplio2's dashes are dropped | none | %dx%d |"
                  % (NAME, BORDER_CORE, BORDER_FADE, BORDER_CURVE, *sheet.size))
    return set(BORDER_TAGS)

# Map extras (issue 262): the art pack's freeciv45/09_map_extras runs 1 to 6 (--extras-art), in place of amplio2's improvements,
# bases, roads, rails, rivers and badges; the picks follow its MAP_EXTRAS.md ("Runs 1 to 6: verdicts").
# - Standing props (EXTRA_PROPS: mines, oil well and platform, hut, hermit, transport hub, buoy) are drawn 3Layer, as `_mg` on the
#   full tile (W x FH, under the units), so they can stand taller than the diamond; the tilespec's [extras] styles say so
#   (EXTRA_3LAYER) and add tx.hermit, which amplio2 drew as its village. Run 1's props cross the even grid's row lines, so they
#   are cut from the whole panel: every piece of alpha goes to the cell its middle lies in (panel_props).
# - Fort, Fortress and Castle (EXTRA_FORTS; civ45's Fort draws base.outpost) are split into `_bg` and `_fg` along the top of
#   the front walls (the footprint's lower edges raised by FORT_WALL of its width), so a unit stands inside; the airstrip and
#   airbase are `_bg` pads.
# - Irrigation, farmland, pollution and fallout (EXTRA_OVERLAYS) are run 3's straight-down seamless squares turned into the
#   diamond like the ground.
# - Roads, rails and rivers are painted in square tile space from run 4's seamless bands (ROAD_BANDS: the middle of the band,
#   feathered, at a set width), one piece from the tile's middle to each neighbour (to an edge's middle, or to a corner for a
#   diagonal) with a round end at the middle, then turned into the W x H rectangle like the ground (the ends past a corner
#   overlap the neighbour, as amplio2's do). Rivers: the 16 cardinal forms and the outlets, drawn on the ocean tile from the
#   river's edge, widening and fading into the water. The maglev is run 7's retake band, painted like the rail (issue 279).
# - amplio2's airbase and airstrip `_mg` runways (EXTRA_DROPPED) would draw over our `_bg` pads, so they are left out.
# - Badges (run 6): the activity marks the units art lacks, stacked, loaded, connecting and the two auto modes, occupied and
#   disorder, and the counted upkeep (1 to 4 symbols, then a symbol and a number) and tile output (a symbol and a number) drawn
#   by script, at amplio2's places. The numbers are Pillow's built-in Aileron Regular (CC0).
# civ45 has no animal units, so run 5's animals wait in the art repo.
EXTRA_RUNS = {"props": "run1/panel1/built_on_tiles.png", "forts": "run2/panel2", "overlays": "run3/panel3", "roads": "run4/panel4",
              "badges": "run6/panel6", "maglev": "run7/panel7"}
EXTRA_DROPPED = {"base.airbase_mg", "base.airstrip_mg"}
# tag: (cut, width as a share of W, foot y on the full tile, at most this tall)
EXTRA_PROPS = {"tx.mine": ("mine_1", 0.46, 106, 92), "tx.oil_mine": ("oil_mine_1", 0.40, 106, 92),
               "tx.oil_rig": ("oil_rig_1", 0.50, 108, 100), "tx.village": ("village_1", 0.56, 110, 90),
               "tx.hermit": ("hermit_1", 0.48, 108, 92), "extra.transport_hub": ("transport_hub_1", 0.62, 114, 80),
               "base.buoy": ("buoy_1", 0.18, 104, 56)}
EXTRA_3LAYER = ("tx.mine", "tx.oil_mine", "tx.oil_rig", "tx.village", "tx.hermit")
# tag: (cut, footprint width as a share of W, wall height as a share of the footprint width; 0: a pad, all _bg)
EXTRA_FORTS = {"base.outpost": ("outpost_2", 0.62, 0.16), "base.fortress": ("fortress_1", 0.86, 0.13),
               "base.castle": ("castle_1", 0.88, 0.19), "base.airstrip": ("airstrip_1", 0.90, 0),
               "base.airbase": ("airbase_1", 0.90, 0)}
FORT_FROM_PROPS = ("outpost_",)          # cuts that come from run 1's panel, not run 2's post/raw
# tag: (seamless cell of run 3, opacity, rolled by half a tile: seamless.py moved irrigation's crossing ditches to the edges)
EXTRA_OVERLAYS = {"tx.irrigation": ("r1c1", 1.0, True), "tx.farmland": ("r2c2", 0.95, False),
                  "tx.pollution": ("r3c1", 0.9, False), "tx.fallout": ("r4c1", 0.9, False)}
# kind: (seamless cell of run 4, share of the band's height kept, width in square tile px, feathered share of each edge,
# colour scale[, EXTRA_RUNS key when not run 4]). The road keeps its wheel ruts, darkened a little and soft at the edges, so it
# reads as a track, not a plank. The maglev deck fills nearly all its band (MAP_EXTRAS.md, run 7: 34.5 px of the cut).
ROAD_BANDS = {"road": ("r1c1", 0.75, 20, 0.35, 0.85), "rail": ("r2c1", 0.9, 26, 0.15, 1.0),
              "river": ("r4c1", 0.62, 30, 0.25, 0.92), "maglev": ("r4c1", 0.95, 28, 0.12, 1.0, "maglev")}
ROAD_DIRS = [("n", 0, -1), ("ne", 1, -1), ("e", 1, 0), ("se", 1, 1), ("s", 0, 1), ("sw", -1, 1), ("w", -1, 0), ("nw", -1, -1)]
# Badges: (tag or tags, cut, cell kind, centre x, centre y, size): the activity marks (56 x 48), the unit badges on a W x H cell,
# the city ones on the full tile; the places are amplio2's.
BADGES = [(("unit.maglev",), "maglev", "act"), (("unit.oil_mine",), "oil_mine", "act"), (("unit.oil_rig",), "oil_rig", "act"),
          (("unit.airstrip",), "airstrip", "act"), (("unit.outpost",), "outpost", "act"), (("unit.buoy",), "buoy", "act"),
          (("unit.fallout",), "fallout", "act")]
TILE_BADGES = [("unit.stack", "stack_1", 57, 81, 30), ("unit.loaded", "loaded", 128, 62, 28),
               ("unit.connect", "connect_1", 76, 11, 22), ("unit.auto_attack", "auto_attack", 76, 11, 22),
               ("unit.auto_settler", "auto_worker", 76, 11, 22)]
CITY_STYLES = ("european", "classical", "asian", "tropical", "celtic", "babylonian", "industrial", "electricage", "modern",
               "postmodern")
CITY_BADGES = [(["cd.occupied"] + ["city.%s_occupied_0" % s for s in CITY_STYLES], "occupied_1", 18, 18, 28),
               (["city.disorder"], "disorder_1", 95, 68, 44)]
UPKEEP = [("shield", "upkeep_shield"), ("gold", "upkeep_gold"), ("food", "upkeep_food"), ("unhappy", "upkeep_unhappy")]
UPKEEP_CELL, UPKEEP_SIZE, UPKEEP_STEP = (W, 38), 28, 26
OUTPUT = [("food", "food", 52), ("shields", "shields", 96), ("trade", "trade", 140)]     # tag, cut, group's centre x on the tile
OUTPUT_Y, OUTPUT_SIZE = 72, 20

def panel_props(panel, names, grid=5, floor=24):
    """name: the cell's prop, cut from the whole panel (RGBA): every 8-connected piece of alpha (from floor, found on a
    half-size mask) goes to the grid cell its middle lies in, so a prop that crosses into the next row stays whole and the
    pieces of it that cross are not left in the neighbour."""
    im = Image.open(panel).convert("RGBA"); w, h = im.size
    small = im.getchannel("A").resize((w // 2, h // 2), Image.BOX); sw, sh = small.size; px = small.load()
    label = [0] * (sw * sh); cells = {}
    for y0 in range(sh):
        for x0 in range(sw):
            if px[x0, y0] < floor or label[y0 * sw + x0]: continue
            todo, piece = [(x0, y0)], []; label[y0 * sw + x0] = -1
            while todo:
                x, y = todo.pop(); piece.append((x, y))
                for nx in (x - 1, x, x + 1):
                    for ny in (y - 1, y, y + 1):
                        if 0 <= nx < sw and 0 <= ny < sh and not label[ny * sw + nx] and px[nx, ny] >= floor:
                            label[ny * sw + nx] = -1; todo.append((nx, ny))
            mx = sum(x for x, _ in piece) / len(piece); my = sum(y for _, y in piece) / len(piece)
            k = min(grid - 1, int(my * grid / sh)) * grid + min(grid - 1, int(mx * grid / sw)) + 1
            for x, y in piece: label[y * sw + x] = k
    out = {}
    for k, name in enumerate(names, 1):
        if name == "-": continue
        m = Image.new("L", (sw, sh), 0); mp = m.load()
        for i, v in enumerate(label):
            if v == k: mp[i % sw, i // sw] = 255
        m = m.resize((w, h), Image.NEAREST).filter(ImageFilter.MaxFilter(5))
        prop = im.copy(); prop.putalpha(ImageChops.multiply(im.getchannel("A"), m))
        box = prop.getchannel("A").point(lambda v: 255 if v >= 16 else 0).getbbox()
        if box: out[name] = defringe(prop.crop(box))
    return out

def read_names(path):
    return [l.split("#", 1)[0].strip() for l in open(path) if l.split("#", 1)[0].strip()]

def stand(im, width, foot, top):
    """im scaled to `width` px wide (at most `top` px tall), centred on the full tile with its foot at y = foot."""
    im = scaled(im, min(width / im.width, top / im.height)); cell = Image.new("RGBA", (W, FH), (0, 0, 0, 0))
    cell.alpha_composite(im, ((W - im.width) // 2, max(0, foot - im.height))); return cell

def fort_halves(im, share, wall):
    """A fort (or a pad, wall 0) on the full tile: scaled to share x W wide, its footprint's bottom corner near the diamond's,
    split into the back (`_bg`) and the front walls (`_fg`, below the footprint's lower edges raised by wall x its width)."""
    fw = share * W; im = scaled(im, fw / im.width)
    bottom = min(FH - 1, round(H + H / 2 + fw / 4 + 2)); x0, y0 = (W - im.width) // 2, max(0, bottom - im.height)
    whole = Image.new("RGBA", (W, FH), (0, 0, 0, 0)); whole.alpha_composite(im, (x0, y0))
    if not wall: return whole, None
    cx, cy, rise = W / 2, bottom - fw / 4, wall * fw
    front = Image.new("L", (W, FH), 0); fp = front.load()
    for y in range(FH):
        for x in range(W):
            if y + 0.5 > cy + (fw / 2 - abs(x + 0.5 - cx)) / 2 - rise: fp[x, y] = 255
    a = whole.getchannel("A"); bg, fg = whole.copy(), whole.copy()
    bg.putalpha(ImageChops.multiply(a, ImageChops.invert(front))); fg.putalpha(ImageChops.multiply(a, front))
    return bg, fg

def iso_overlay(square, opacity=1.0):
    """A T px seamless RGBA square (alpha where the ground shows through) as the W x H diamond."""
    wrap = Image.new("RGBA", (3 * T, 3 * T), (0, 0, 0, 0))
    for j in range(3):
        for i in range(3): wrap.paste(square, (i * T, j * T))
    out = to_iso(wrap, -T, -T, (W, H), (0, 0))
    out.putalpha(ImageChops.multiply(out.getchannel("A").point(lambda v: round(v * opacity)), DIAMOND)); return out

def band(cell, keep, feather=0.12, tone=1.0):
    """The middle `keep` share of a seamless band cell's opaque rows, its long edges feathered over `feather` of its height
    and its colour scaled by `tone`: the texture a piece repeats."""
    box = cell.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    top, bot = box[1], box[3]; cut = (bot - top) * (1 - keep) / 2
    tex = cell.crop((0, round(top + cut), cell.width, round(bot - cut))).convert("RGBA"); th = tex.height
    if tone != 1.0:
        a = tex.getchannel("A"); tex = tex.convert("RGB").point(lambda v: min(255, round(v * tone))).convert("RGBA"); tex.putalpha(a)
    ramp = Image.new("L", (1, th)); rp = ramp.load(); f = max(2, th * feather)
    for y in range(th): rp[0, y] = round(255 * min(1.0, (y + 0.5) / f, (th - y - 0.5) / f))
    tex.putalpha(ImageChops.multiply(tex.getchannel("A"), ramp.resize(tex.size))); return tex

def strip(tex, width, length, cap=True, widen=0.0, fade=False):
    """The band texture repeated to `length` px at `width` px wide (scaled evenly), plus width/2 before 0 with a round end
    when cap; widen grows it toward the far end (outlets: the strip is drawn twice as wide and masked), fade lets it vanish."""
    width = round(width); s = width / tex.height; t = scaled(tex, s); pre = width // 2 if cap else 0
    room = round(width * (1 + widen)); total = round(length) + pre
    out = Image.new("RGBA", (total, room), (0, 0, 0, 0)); tt = scaled(tex, room / tex.height) if widen else t
    x = 0
    while x < total: out.alpha_composite(tt, (x, 0)); x += tt.width
    m = Image.new("L", out.size, 0); mp = m.load(); r = width / 2; cy = room / 2
    for y in range(room):
        for x in range(total):
            a = x - pre; half = r * (1 + widen * max(0.0, a) / length) if widen else r
            inside = abs(y + 0.5 - cy) <= half if a >= 0 else (cap and (a + 0.5) ** 2 + (y + 0.5 - cy) ** 2 <= r * r)
            if inside: mp[x, y] = round(255 * (1 - max(0.0, a) / length) ** 1.5) if fade else 255
    out.putalpha(ImageChops.multiply(out.getchannel("A"), m)); return out, pre

def piece_on(canvas, st, pre, start, d):
    """Draw strip st (its point (pre, middle) at square point start, running along unit vector d) onto the 3T square canvas."""
    dx, dy = d; cx, cy = start[0] + T, start[1] + T; ch = st.height / 2
    big = st.convert("RGBa").transform(canvas.size, Image.AFFINE,
                                        (dx, dy, -dx * cx - dy * cy + pre, -dy, dx, dy * cx - dx * cy + ch),
                                        resample=Image.BICUBIC)
    canvas.alpha_composite(big.convert("RGBA"))

def road_tile(tex, width, dirs, outlet=None, pond=False):
    """A W x H sprite: pieces from the tile's middle toward each of dirs (ROAD_DIRS names); an outlet from that edge's middle
    toward the middle; a pond (a disc) when there is nothing else."""
    canvas = Image.new("RGBA", (3 * T, 3 * T), (0, 0, 0, 0)); mid = (T / 2, T / 2)
    for name, ux, uy in ROAD_DIRS:
        if name not in dirs: continue
        n = (ux * ux + uy * uy) ** 0.5; st, pre = strip(tex, width, T / 2 * n)
        piece_on(canvas, st, pre, mid, (ux / n, uy / n))
    if outlet:
        ux, uy = [(a, b) for name, a, b in ROAD_DIRS if name == outlet][0]
        st, pre = strip(tex, width, T * 0.3, cap=False, widen=1.2, fade=True)
        piece_on(canvas, st, pre, (T / 2 + ux * T / 2, T / 2 + uy * T / 2), (-ux, -uy))
    if pond or not (dirs or outlet):
        st, pre = strip(tex, width * 2, 1)
        piece_on(canvas, st, pre, mid, (1, 0))
    return to_iso(canvas, -T, -T, (W, H), (0, 0))

def digits_on(im, text, x, y, size):
    font = ImageFont.load_default(size=size)
    ImageDraw.Draw(im).text((x, y), text, font=font, fill=(255, 255, 255, 255), stroke_width=max(1, size // 8),
                            stroke_fill=(20, 20, 20, 255), anchor="lm")

def extras(art, out_dir, record):
    """extras.png/.spec (props, forts and pads on W x FH cells; overlays, roads, rails and rivers on W x H cells) and
    badges.png/.spec; returns the tags drawn and the cuts used."""
    props = panel_props(os.path.join(art, EXTRA_RUNS["props"]), read_names(os.path.join(art, "built_on_tiles.names")))
    def fort_cut(name):
        if name.startswith(FORT_FROM_PROPS): return props[name]
        return tidy(os.path.join(art, EXTRA_RUNS["forts"], "post", "raw", name + ".png"))
    full, flat, used = [], [], []
    for tag, (name, share, foot, top) in EXTRA_PROPS.items():
        full.append((tag + "_mg", stand(props[name], share * W, foot, top))); used.append(name)
    for tag, (name, share, wall) in EXTRA_FORTS.items():
        bg, fg = fort_halves(fort_cut(name), share, wall); used.append(name)
        full.append((tag + "_bg", bg))
        if fg: full.append((tag + "_fg", fg))
    seam = os.path.join(art, EXTRA_RUNS["overlays"], "post", "seamless")
    for tag, (cell, opacity, roll) in EXTRA_OVERLAYS.items():
        sqr = Image.open(os.path.join(seam, cell + ".png")).convert("RGBA")
        if roll: sqr = ImageChops.offset(sqr, T // 2, T // 2)
        flat.append((tag, iso_overlay(sqr, opacity)))
        used.append("%s (overlays %s)" % (tag[3:], cell))
    texs = {}
    for kind, (cell, keep, width, feather, tone, *run) in ROAD_BANDS.items():
        run = EXTRA_RUNS[run[0] if run else "roads"]
        texs[kind] = (band(Image.open(os.path.join(art, run, "post", "seamless", cell + ".png")), keep, feather, tone), width)
        used.append("%s band (%s %s)" % (kind, run.split("/")[0], cell))
    for kind in ("road", "rail", "maglev"):
        tex, width = texs[kind]
        flat.append(("road.%s_isolated" % kind, road_tile(tex, width, [], pond=True)))
        for name, _, _ in ROAD_DIRS: flat.append(("road.%s_%s" % (kind, name), road_tile(tex, width, [name])))
    tex, width = texs["river"]
    for code in range(16):
        n, e, s, w_ = (code >> 3) & 1, (code >> 2) & 1, (code >> 1) & 1, code & 1
        dirs = [d for d, on in zip("nesw", (n, e, s, w_)) if on]
        flat.append(("road.river_s_n%de%ds%dw%d" % (n, e, s, w_), road_tile(tex, width, dirs)))
    for d in "nesw": flat.append(("road.river_outlet_" + d, road_tile(tex, width, [], outlet=d)))
    cols = 10; frows, trows = (len(full) + cols - 1) // cols, (len(flat) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * W, frows * FH + trows * H), (0, 0, 0, 0))
    for i, (_, c) in enumerate(full): sheet.paste(c, ((i % cols) * W, (i // cols) * FH))
    for i, (_, c) in enumerate(flat): sheet.paste(c, ((i % cols) * W, frows * FH + (i // cols) * H))
    sheet.save(os.path.join(out_dir, "extras.png"), optimize=True)
    write_spec(out_dir, "extras", "Map extras for the Freeciv45 iso tileset: the Freeciv45 art pack's freeciv45/09_map_extras runs 1 to 4\n"
               "and 7 (improvements, forts, airfields, overlays, road, rail, river and maglev bands), cut and painted by\n"
               "tilesets/make-%s.py (see RECORD.md)." % NAME,
               [("full", 0, W, FH, [(i // cols, i % cols, [t]) for i, (t, _) in enumerate(full)]),
                ("tile", frows * FH, W, H, [(i // cols, i % cols, [t]) for i, (t, _) in enumerate(flat)])])
    record.append("| `%s/extras.spec` | the art pack's map extras (`freeciv45/09_map_extras`, runs 1 to 4 and 7): %s | props scaled "
                  "onto the full tile, forts split into back and front, overlays turned into diamonds, road, rail, river and maglev "
                  "pieces painted from the bands | %dx%d |" % (NAME, ", ".join("`%s`" % u for u in used), *sheet.size))
    tags = {t for t, _ in full + flat}
    btags, bused = badges(art, out_dir, record)
    return tags | btags | EXTRA_DROPPED, used + bused

def badges(art, out_dir, record):
    raw = os.path.join(art, EXTRA_RUNS["badges"], "post", "raw"); got = {}
    def b(name, size):
        if name not in got: got[name] = tidy(os.path.join(raw, name + ".png"), whole=True)
        im = got[name]; return scaled(im, min(size / im.width, size / im.height))
    act = []
    for tags, name, _ in BADGES:
        c = Image.new("RGBA", MARK_CELL, (0, 0, 0, 0)); im = b(name, 44)
        c.alpha_composite(im, ((MARK_CELL[0] - im.width) // 2, (MARK_CELL[1] - im.height) // 2)); act.append((list(tags), c))
    tile = []
    for tag, name, cx, cy, size in TILE_BADGES:
        c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im = b(name, size)
        c.alpha_composite(im, (round(cx - im.width / 2), max(0, round(cy - im.height / 2)))); tile.append(([tag], c))
    for tag, name, cx in OUTPUT:
        for k in range(10):
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im = b(name, OUTPUT_SIZE)
            c.alpha_composite(im, (round(cx - 12 - im.width / 2), round(OUTPUT_Y - im.height / 2)))
            digits_on(c, str(k), cx - 1, OUTPUT_Y, 18); tile.append((["city.t_%s_%d" % (tag, k)], c))
    city = []
    for tags, name, cx, cy, size in CITY_BADGES:
        c = Image.new("RGBA", (W, FH), (0, 0, 0, 0)); im = b(name, size)
        c.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2))); city.append((tags, c))
    upkeep = []
    for kind, name in UPKEEP:
        for n in range(1, 11):
            c = Image.new("RGBA", UPKEEP_CELL, (0, 0, 0, 0)); im = b(name, UPKEEP_SIZE); y = (UPKEEP_CELL[1] - im.height) // 2
            if n <= 4:
                for i in range(n): c.alpha_composite(im, (i * UPKEEP_STEP, y))
            else:
                c.alpha_composite(im, (0, y)); digits_on(c, str(n), im.width + 2, UPKEEP_CELL[1] // 2, 22)
            upkeep.append((["upkeep.%s%s" % (kind, "" if n == 1 else n)], c))
    grids, y, sheet_w = [], 0, 10 * W
    parts = [("act", MARK_CELL, act), ("tile", (W, H), tile), ("city", (W, FH), city), ("upkeep", UPKEEP_CELL, upkeep)]
    height = sum(((len(cells) + (sheet_w // cw) - 1) // (sheet_w // cw)) * ch for _, (cw, ch), cells in parts)
    sheet = Image.new("RGBA", (sheet_w, height), (0, 0, 0, 0))
    for gname, (cw, ch), cells in parts:
        cols = sheet_w // cw
        for i, (_, c) in enumerate(cells): sheet.paste(c, ((i % cols) * cw, y + (i // cols) * ch))
        grids.append((gname, y, cw, ch, [(i // cols, i % cols, t) for i, (t, _) in enumerate(cells)]))
        y += ((len(cells) + cols - 1) // cols) * ch
    sheet.save(os.path.join(out_dir, "badges.png"), optimize=True)
    write_spec(out_dir, "badges", "Badges for the Freeciv45 iso tileset: the Freeciv45 art pack's freeciv45/09_map_extras run 6, placed\n"
               "where amplio2 draws its badges by tilesets/make-%s.py, the counted upkeep and tile output drawn with a number\n"
               "(see RECORD.md)." % NAME, grids)
    record.append("| `%s/badges.spec` | the art pack's badges (`freeciv45/09_map_extras` run 6, `post/raw`): %s | cleaned (fringe), "
                  "scaled to amplio2's places; upkeep 1 to 4 symbols, then a symbol and a number; tile output a symbol and a "
                  "number (Aileron Regular, CC0) | %dx%d |" % (NAME, ", ".join("`%s`" % n for n in sorted(got)), *sheet.size))
    return {t for _, _, cells in parts for ts, _ in cells for t in ts}, sorted(got)

def extras_styles(path):
    """The tilespec's [extras] styles: EXTRA_3LAYER's tags drawn 3Layer, and tx.hermit added (amplio2 draws its village)."""
    text = open(path).read()
    for tag in EXTRA_3LAYER:
        text, n = re.subn(r'("%s",\s*)"Single1"' % re.escape(tag), r'\1"3Layer"', text)
        if tag != "tx.hermit": assert n == 1, tag
    if '"tx.hermit"' not in text:
        text = re.sub(r'(\n(\s*)"tx.village",[^\n]*)', r'\1\n\2"tx.hermit",     "3Layer"', text, count=1)
    open(path, "w").write(text)

RECORD_HEAD = """# %(name)s: where every sprite came from

The isometric Freeciv45 tileset (issue 190): %(w)dx%(h)d diamonds at `pixel_ratio = 2`, amplio2's tile doubled, so the
patched Qt client shows each tile at amplio2's size and, on a Retina screen, draws every pixel. Built by
`tilesets/make-%(name)s.py`, which imports `make-freeciv45test.py` for the painted cells; nothing in this folder but
the files it writes. Rebuild with (`T` is the art repo's `freeciv45/01_terrain_ground`)

    python3.14 -I tilesets/make-%(name)s.py --data ~/freeciv-builds/qt/share/freeciv --art $T

When new runs of the painted ground land, add them to `PANELS` and `PLAN` in `make-freeciv45test.py` and rebuild
both tilesets: the iso cells come from the same cut.

Licence of the whole folder: GPL-2.0-or-later, like Freeciv, amplio2 and the Freeciv45 art pack. Soft edges between
terrains need the fork's patch 0033 (an unpatched client blends through amplio2's `t.dither_tile`).

## From amplio2, scaled

Every spec file that `amplio2.tilespec` lists under `amplio2/`, except %(skipped)s (cells the painted ground
replaces), is re-cut from Freeciv 3.2.6's amplio2 tileset (GPL-2.0-or-later; the artists are
named in each spec's `[info]` section, copied verbatim): each sprite scaled 2x with nearest-neighbour sampling, so it
looks as amplio2 does on a 2x screen today. `water.spec` keeps only the rivers. `hills.spec` and `mountains.spec` are the relief
over the flat hills and mountains ground (issue 194), moved from layer 1 to layer 2.%(canopy)s `misc/citybar` and `misc/overlays`
are re-cut too, because the client draws them on the map; the other `misc/` files are read from the installed data.

| spec | source | scaling | sheet |
|---|---|---|---|
"""

def main():
    global LAND_GRADE
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a Freeciv data dir with amplio2.tilespec, amplio2/ and trident.tilespec")
    ap.add_argument("--art", required=True, help="the art repo's freeciv45/01_terrain_ground, with the runs in PANELS")
    ap.add_argument("--olive-pine", action="store_true", help="add run 9's r5c4 and r5c5 as forest11 and forest12")
    ap.add_argument("--cutter", help="seamless.py (default: tools/seamless.py next to --art)")
    ap.add_argument("--no-tone-match", action="store_true", help="leave each painted cell's tone as cut")
    ap.add_argument("--no-level", action="store_true", help="keep each cell's light gradient (seamless.py without --level)")
    ap.add_argument("--no-blend", action="store_true", help="no blending between terrains")
    ap.add_argument("--no-relief", action="store_true", help="no amplio2 relief: painted hills and mountains, flat")
    ap.add_argument("--relief-base", choices=("flat", "painted"), default="flat",
                    help="the ground under the relief: RELIEF_BASE's flat cells, or the painted hills and mountains")
    ap.add_argument("--canopy", choices=("painted", "amplio2"), default="amplio2",
                    help="forest and jungle: the painted canopy, or amplio2's tree overlays over CANOPY_BASE")
    ap.add_argument("--land-grade", default=",".join(map(str, LAND_GRADE)), metavar="L,A,B",
                    help="CIE Lab offset for the painted land, after GRADE")
    ap.add_argument("--features", choices=("bk", "amplio2"), default="bk",
                    help="trees, hills and mountains: the art pack's props (bk), or amplio2's overlays (--canopy, "
                         "--no-relief and --relief-base apply)")
    ap.add_argument("--features-art", help="the art repo's freeciv45/02_terrain_features (default: next to --art)")
    ap.add_argument("--resources", help="the art repo's freeciv45/03_resources (default: next to --art)")
    ap.add_argument("--no-resources", action="store_true", help="keep amplio2's resource sprites")
    ap.add_argument("--units-art", help="the art repo's freeciv45/04_units (default: next to --art)")
    ap.add_argument("--cities-art", help="the art repo's freeciv45/05_cities (default: next to --art)")
    ap.add_argument("--tech-art", help="the art repo's freeciv45/06_tech_icons (default: next to --art)")
    ap.add_argument("--building-art", help="the art repo's freeciv45/07_building_icons (default: next to --art)")
    ap.add_argument("--no-borders", action="store_true", help="keep amplio2's dashed national borders")
    ap.add_argument("--no-bk-icons", action="store_true", help="keep the stock tech icons and building pictures")
    ap.add_argument("--no-bk-units", action="store_true", help="keep amplio2's units, cities and marks")
    ap.add_argument("--extras-art", help="the art repo's freeciv45/09_map_extras (default: next to --art)")
    ap.add_argument("--no-bk-extras", action="store_true", help="keep amplio2's improvements, bases, roads, rivers and badges")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    sq.set_tile(T); sq.NAME = NAME
    LAND_GRADE = tuple(int(v) for v in a.land_grade.split(","))
    bk = a.features == "bk"
    bku = not a.no_bk_units
    canopy = a.canopy == "amplio2" and not bk
    if canopy and a.no_relief: ap.error("--canopy amplio2 needs the relief layer (no --no-relief)")
    sq.BLEND_DEPTH = round(BLEND_DEPTH * T)
    for key, value in SHORE.items(): setattr(sq, key, value)
    out_dir = os.path.join(a.out, NAME); os.makedirs(out_dir, exist_ok=True)
    cutter = a.cutter or os.path.join(os.path.dirname(os.path.abspath(a.art)), "tools", "seamless.py")
    panels = {key: os.path.join(a.art, rel) for key, rel in sq.PANELS.items()}
    relief = not a.no_relief and not bk
    plan = sq.PLAN + ([sq.OLIVE_PINE] if a.olive_pine else [])
    if relief and a.relief_base == "flat":
        plan = [p for p in plan if p[0] not in RELIEF.values()] + RELIEF_BASE
    plan = [p for p in plan if p[0] != "plains"] + ISO_PLAINS
    if canopy or bk:
        plan = [p for p in plan if p[0] not in [t for ts in CANOPY.values() for t in ts]] + CANOPY_BASE
    if bk:
        plan = [p for p in plan if p[0] not in [t for t, _, _ in FEATURE_BASE]] + FEATURE_BASE
    plan.sort(key=lambda p: [t for t, _, _ in sq.PLAN].index(p[0]))
    painted_record, amplio_record, feature_props = [], [], []
    sq.painted(panels, cutter, out_dir, painted_record, plan, tone_match=not a.no_tone_match, level=not a.no_level)
    own = ground(out_dir, painted_record) | {"mask.tile"}
    if not a.no_resources:
        own |= resources(a.resources or os.path.join(os.path.dirname(os.path.abspath(a.art)), "03_resources"),
                         out_dir, painted_record)
    unit_props = city_props = mark_props = []
    if bku:
        base = os.path.dirname(os.path.abspath(a.art))
        new, unit_props = units(a.units_art or os.path.join(base, "04_units"), a.data, out_dir, painted_record); own |= new
        new, city_props = cities(a.cities_art or os.path.join(base, "05_cities"), a.data, out_dir, painted_record); own |= new
        new, mark_props = marks(a.units_art or os.path.join(base, "04_units"), out_dir, painted_record); own |= new
    tech_props = building_props = []
    if not a.no_bk_icons:
        base = os.path.dirname(os.path.abspath(a.art))
        tech_props, building_props, _ = icons(a.tech_art or os.path.join(base, "06_tech_icons"),
                                              a.building_art or os.path.join(base, "07_building_icons"), out_dir, painted_record)
    if not a.no_borders: own |= borders(out_dir, painted_record)
    extra_props = []
    if not a.no_bk_extras:
        new, extra_props = extras(a.extras_art or os.path.join(os.path.dirname(os.path.abspath(a.art)), "09_map_extras"),
                                  out_dir, painted_record)
        own |= new
    sq.coastline(panels, cutter, out_dir, painted_record, level=not a.no_level)
    coast(out_dir, painted_record, relief or bk)
    if not a.no_blend: blend(out_dir, painted_record)
    if bk:
        tags, feature_props = features(a.features_art or os.path.join(os.path.dirname(os.path.abspath(a.art)),
                                                                      "02_terrain_features"), out_dir, painted_record)
        own |= tags
    spec_text = open(os.path.join(a.data, "amplio2.tilespec"), errors="replace").read()
    listed = re.findall(r'"([^"]+\.spec)"', spec_text.split("files =", 1)[1].split("files_", 1)[0])  # not files_svg
    files, drop = [], Drop(own)
    sq.OVERRIDDEN = drop
    for rel in listed:
        if (rel in SKIPPED and not (canopy and rel in CANOPY)) or (rel in RELIEF and not relief): continue
        if bku and rel in BK_REPLACED:      # the art pack's units and cities take them over
            if BK_REPLACED[rel]: files.append("%s/%s" % (NAME, BK_REPLACED[rel]))
            continue
        if rel.startswith("amplio2/"):
            drop.prefixes = DROP_PREFIX.get(rel, ())
            if bku and rel == "amplio2/activities.spec": files.append("%s/marks.spec" % NAME)
            if not a.no_bk_extras and rel == "amplio2/tiles.spec": files.append("%s/badges.spec" % NAME)
            if bku and not any(t not in drop for g in sq.parse_spec(os.path.join(a.data, rel))[1]
                               for _, _, tags in g["cells"] for t in tags): continue   # nothing of amplio2's left in it
            sq.recut(a.data, rel, out_dir, amplio_record, scale=AMPLIO_SCALE)
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
            if not a.no_borders and rel.endswith("grid.spec"): files.append("%s/borders.spec" % NAME)
            if rel in RELIEF:       # amplio2 draws its relief on layer 1; here it is layer 2
                spec = os.path.join(out_dir, os.path.basename(rel)); text = open(spec).read()
                open(spec, "w").write(text.replace('"t.l1.%s_' % RELIEF[rel], '"t.l2.%s_' % RELIEF[rel]))
            if rel in CANOPY:       # the same for the trees
                spec = os.path.join(out_dir, os.path.basename(rel)); text = open(spec).read()
                for t in CANOPY[rel]: text = text.replace('"t.l1.%s_' % t, '"t.l2.%s_' % t)
                open(spec, "w").write(text)
            if rel == "amplio2/terrain1.spec":
                files += ["%s/terrain45.spec" % NAME, "%s/coast.spec" % NAME] + ([] if a.no_blend else ["%s/blend.spec" % NAME])
                files += [] if a.no_resources else ["%s/resources.spec" % NAME]
                files += ["%s/features.spec" % NAME] if bk else []
                files += [] if a.no_bk_extras else ["%s/extras.spec" % NAME]
        elif sq.map_misc_scale(rel) and sq.map_misc_scale(rel) != 1:
            drop.prefixes = ()
            sq.recut(a.data, rel, out_dir, amplio_record, scale=sq.map_misc_scale(rel))
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
        else:
            files.append(rel)
            if not a.no_bk_icons and rel == "misc/techs.spec": files.append("%s/tech_icons.spec" % NAME)
            if not a.no_bk_icons and rel == "misc/wonders-large.spec": files.append("%s/building_icons.spec" % NAME)
    tilespec(a.data, a.out, files, blend=not a.no_blend, relief=relief, canopy=canopy, bk=bk, units=bku, icons=not a.no_bk_icons)
    if not a.no_bk_extras: extras_styles(os.path.join(a.out, NAME + ".tilespec"))
    with open(os.path.join(out_dir, "RECORD.md"), "w") as f:
        f.write(RECORD_HEAD % {"name": NAME, "w": W, "h": H, "skipped": ", ".join("`%s`" % s[8:] for s in SKIPPED if not (canopy and s in CANOPY)),
                             "canopy": " `terrain2.spec`, the forest and jungle overlays, moves the same way over painted "
                                       "grassland (issue 199)." if canopy else ""})
        f.write("\n".join(amplio_record) + "\n\n## Painted ground, shore and blend masks\n\n"
                "Cut as `make-freeciv45test.py` cuts them (the same panels, cells, cutter and tone match), then turned "
                "into diamonds.\n\n| spec | source | scaling | sheet |\n|---|---|---|---|\n"
                + "\n".join(painted_record) + "\n")
        if not a.no_resources:
            f.write("\n## Resources\n\n`resources.spec` / `resources.png`: the %d resource sprites, one per `ts.*` tag of civ45's "
                    "`terrain.ruleset`, from the Freeciv45 art pack (John O'Dell's sheet workflow with OpenAI image "
                    "generation through Codex, art repo folder `freeciv45/03_resources`, runs 1 and 2, the picks in its "
                    "`RESOURCES.md`). Each is an isometric prop on a transparent %dx%d tile, cut by the art repo's "
                    "`tools/props.py` (standing on the tile's foot point, soft contact shadow) and copied unchanged. Only "
                    "the picks the tileset draws are copied: no alternates, panels or 1x copies. They replace amplio2's "
                    "resource sprites of the same tags (issue 206). GPL-2.0-or-later, like the rest of the folder.\n"
                    % (len(RESOURCES), W, H))
        if bk:
            f.write("\n## Trees, hills and mountains\n\n`features.spec` / `features.png`: forest, jungle, swamp, hills, "
                    "mountains and inaccessible drawn with the Freeciv45 art pack's standing props (John O'Dell's sheet "
                    "workflow with OpenAI image generation through Codex, art repo folder `freeciv45/02_terrain_features`, "
                    "runs 5 to 8 and run 4's dark peaks, placed as its `TREES_AND_RELIEF_2.md` says). The props are "
                    "stood (a stand of trees with a clump, or one hill or mountain) on %dx%d full tiles in a few "
                    "variants per terrain, so the client draws one sprite per tile on layer 2; hills and mountains "
                    "draw a ridge or range along the grid line their own kind continues on (issues 224 and 229, "
                    "patch 0034). Only these %d props are used, and only inside the baked "
                    "variants: %s. No panels, alternates or other files from the art repo. GPL-2.0-or-later, like the "
                    "rest of the folder.\n" % (W, FH, len(feature_props), ", ".join("`%s`" % n for n in feature_props)))
        if bku:
            f.write("\n## Units, cities, marks and ruins\n\n`units.spec`, `cities.spec` and `marks.spec`: the Freeciv45 art pack's "
                    "units, cities and marks (John O'Dell's sheet workflow with OpenAI image generation through Codex, art repo "
                    "folders `freeciv45/04_units` and `freeciv45/05_cities`, runs 1 to 5, issue 245), in place of amplio2's. "
                    "Only the sprites the ruleset uses ship, one per tag (the better take of each unit; the unused takes, "
                    "ruins, panels and art-repo records stay in the art repo). Units used (%d): %s. Cities and the ruins (%d): "
                    "%s. Marks (%d): %s. GPL-2.0-or-later, like the rest of the folder. Left from amplio2 (`bases.spec`, `tiles.spec` and "
                    "the rest of the scaled files): %s.\n" % (len(unit_props), ", ".join("`%s`" % n for n in unit_props), len(city_props),
                                           ", ".join("`%s`" % n for n in city_props), len(mark_props),
                                           ", ".join("`%s`" % n for n in mark_props),
                                           "the hit point bars, the city size digits and the ruins' and castle2's "
                                           "leftovers" if extra_props else "the maglev, oil mine, oil rig, airstrip, outpost, buoy "
                                           "and fallout marks, the occupied and disorder badges and the fortress, airbase, "
                                           "castle and outpost bases"))
        if extra_props:
            f.write("\n## Map extras and badges\n\n`extras.spec` and `badges.spec`: the Freeciv45 art pack's map extras (John "
                    "O'Dell's sheet workflow with OpenAI image generation through Codex, art repo folder "
                    "`freeciv45/09_map_extras`, runs 1 to 4, 6 and 7, the picks in its `MAP_EXTRAS.md`; issues 262 and 279), in "
                    "place of "
                    "amplio2's. Standing props are drawn `3Layer` as `_mg` on the %dx%d full tile (the tilespec's `[extras]` "
                    "styles say so for %s, and add `tx.hermit`); Fort (`base.outpost`), Fortress and Castle are split into "
                    "`_bg` and `_fg` along the top of the front walls so a unit stands inside; the airstrip and airbase are "
                    "`_bg` pads (amplio2's `_mg` runways are left out); irrigation, farmland, pollution and fallout are the straight-down seamless squares turned "
                    "into diamonds; road, rail, river and maglev pieces are painted in square tile space from the seamless bands "
                    "and turned the same way. The badges sit where amplio2's do; the counted upkeep (1 to 4 symbols, then "
                    "a symbol and a number) and tile output (a symbol and a number) are drawn by the builder, the numbers "
                    "in Pillow's built-in Aileron Regular (CC0). Used: %s. Nothing else of the art repo ships (no panels, "
                    "other takes or records). GPL-2.0-or-later, like the rest of "
                    "the folder.\n" % (W, FH, ", ".join("`%s`" % t for t in EXTRA_3LAYER),
                                         ", ".join("`%s`" % n for n in extra_props)))
        if not a.no_bk_icons:
            f.write("\n## Tech icons and building pictures\n\n`tech_icons.spec` and `building_icons.spec`: the Freeciv45 art pack's "
                    "tech icons and building and wonder pictures (John O'Dell's sheet workflow with OpenAI image generation "
                    "through Codex, art repo folders `freeciv45/06_tech_icons` and `freeciv45/07_building_icons`, issue 254). "
                    "Each cell is cleaned (stray specks out, the colour fringe of the semi-transparent edge defringed, see "
                    "`defringe`), scaled to fit and centred on the client's own icon cell: %dx%d for a tech, %dx%d for a "
                    "building, the sizes the Qt client draws at 1x and 2x alike (only the map follows `pixel_ratio`). The "
                    "tilespec sets `duplicates_ok` and lists the two specs after `misc/techs.spec` and "
                    "`misc/wonders-large.spec`, so these tags override the stock icons and every other tag keeps its stock "
                    "icon. Techs (%d, runs 1, 2, 5 and 6; `the_wheel` and `the_republic` are run 6's `_alt` takes): %s. "
                    "Buildings (%d, runs 1 to 5): %s. The picks that are not the first take: %s. Every tech and building the "
                    "ruleset names has a picture, so no stock icon is left for these tags. GPL-2.0-or-later, like the rest of "
                    "the folder.\n"
                    % (TECH_CELL, TECH_CELL, *BUILD_CELL, len(tech_props), ", ".join("`%s`" % n for n in tech_props),
                       len(building_props), ", ".join("`%s`" % n for n in building_props),
                       ", ".join("`%s` (`%s`)" % kv for kv in sorted({**TECH_PICK, **BUILD_PICK}.items()))))
    print("\n".join(amplio_record + painted_record))

if __name__ == "__main__":
    main()
