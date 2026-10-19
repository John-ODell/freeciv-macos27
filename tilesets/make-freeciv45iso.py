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

From amplio2 (Freeciv 3.2.6, GPL-2.0-or-later, the artists named in each spec's [info] section, copied verbatim):
every spec file amplio2.tilespec lists under amplio2/ except the ocean cells the painted ground replaces
(SKIPPED; the forest and jungle overlays too with --canopy painted), each sprite scaled 2x with nearest-neighbour sampling (recut). The tilespec is amplio2's with the sizes
and offsets doubled, pixel_ratio 2, the file list renamed, and freeciv45test's layer and terrain sections.

usage: make-freeciv45iso.py --data ~/freeciv-builds/qt/share/freeciv
                            --art ~/Desktop/asset_generator/freeciv45/01_terrain_ground [--cutter SEAMLESS.py]
                            [--out tilesets] [--olive-pine] [--no-tone-match] [--no-level] [--no-blend]
                            [--no-relief] [--relief-base flat|painted] [--canopy amplio2|painted]
                            [--land-grade L,A,B]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, glob, importlib.util, math, os, random, re, tempfile
from PIL import Image, ImageChops, ImageCms, ImageDraw, ImageFilter

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
RESOURCE_RUNS = {"run1": "run1/panel1/post", "run2": "run2/panel2/post"}
RESOURCES = [
    ("ts.wheat", "run1", "wheat_1"), ("ts.buffalo", "run1", "buffalo_1"), ("ts.horses", "run1", "horses_1"),
    ("ts.grassland_resources", "run1", "grassland_resources_2"), ("ts.fruit", "run1", "fruit_1"),
    ("ts.gems", "run2", "gems_1"), ("ts.oasis", "run1", "oasis_1"), ("ts.oil", "run2", "oil_1"),
    ("ts.pheasant", "run1", "pheasant_1"), ("ts.silk", "run2", "silk_1"), ("ts.coal", "run2", "coal_2"),
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

def tilespec(data, out_root, files, blend=True, relief=True, canopy=False, bk=False):
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
            if key == "name": out.append('name = "Freeciv45 iso"'); continue
            if key == "priority": out.append("priority = 4"); continue
            if key == "summary":
                out.append('summary = _("Freeciv45 iso tileset: %dx%d diamonds, painted ground for every terrain, '
                           'amplio2 for the rest.")' % (W, H)); continue
            if num is not None and (key in ("normal_tile_width", "normal_tile_height", "svg_height")
                                    or key.endswith(("_offset_x", "_offset_y"))):
                out.append("%s = %d" % (key, int(num) * AMPLIO_SCALE))
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
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    sq.set_tile(T); sq.NAME = NAME
    LAND_GRADE = tuple(int(v) for v in a.land_grade.split(","))
    bk = a.features == "bk"
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
        if rel.startswith("amplio2/"):
            drop.prefixes = DROP_PREFIX.get(rel, ())
            sq.recut(a.data, rel, out_dir, amplio_record, scale=AMPLIO_SCALE)
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
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
        elif sq.map_misc_scale(rel) and sq.map_misc_scale(rel) != 1:
            drop.prefixes = ()
            sq.recut(a.data, rel, out_dir, amplio_record, scale=sq.map_misc_scale(rel))
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
        else: files.append(rel)
    tilespec(a.data, a.out, files, blend=not a.no_blend, relief=relief, canopy=canopy, bk=bk)
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
    print("\n".join(amplio_record + painted_record))

if __name__ == "__main__":
    main()
