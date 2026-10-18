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

From amplio2 (Freeciv 3.2.6, GPL-2.0-or-later, the artists named in each spec's [info] section, copied verbatim):
every spec file amplio2.tilespec lists under amplio2/ except the terrain overlays the painted ground replaces
(SKIPPED), each sprite scaled 2x with nearest-neighbour sampling (recut). The tilespec is amplio2's with the sizes
and offsets doubled, pixel_ratio 2, the file list renamed, and freeciv45test's layer and terrain sections.

usage: make-freeciv45iso.py --data ~/freeciv-builds/qt/share/freeciv
                            --art ~/Desktop/asset_generator/freeciv45/01_terrain_ground [--cutter SEAMLESS.py]
                            [--out tilesets] [--olive-pine] [--no-tone-match] [--no-level] [--no-blend]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, importlib.util, os, random, re, tempfile
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("make_freeciv45test", os.path.join(HERE, "make-freeciv45test.py"))
sq = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sq)

NAME = "freeciv45iso"
W, H = 192, 96          # the diamond: amplio2's 96 x 48, doubled
T = 192                 # the square masters and freeciv45test's tile (make-freeciv45test.py --tile 192)
SS = 4                  # point samples per pixel, per axis
AMPLIO_SCALE = 2
# amplio2 spec files left out: the forest, jungle, hills and mountains overlays and the ocean's corner cells, which
# the painted ground replaces. water.spec stays for the rivers; its lake and ice cells are dropped (DROP_PREFIX), and so
# are terrain1.spec's t.blend.* textures, which the client would fade in instead of the painted variant 1.
SKIPPED = ("amplio2/terrain2.spec", "amplio2/hills.spec", "amplio2/mountains.spec", "amplio2/ocean.spec")
DROP_PREFIX = {"amplio2/water.spec": ("t.l0.", "t.l1."), "amplio2/terrain1.spec": ("t.blend.",)}

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

def ground(out_dir, record):
    """terrain45.png: freeciv45test's square sheet, each cell as a diamond."""
    path = os.path.join(out_dir, "terrain45.png"); square = Image.open(path).convert("RGB")
    cells = rewrite_spec(os.path.join(out_dir, "terrain45.spec"), W, H)
    rows, cols = max(r for r, _, _ in cells) + 1, max(c for _, c, _ in cells) + 1
    sheet = Image.new("RGBA", (cols * W, rows * H), (0, 0, 0, 0))
    for r, c, _ in cells:
        sheet.paste(iso_ground(square.crop((c * T, r * T, (c + 1) * T, (r + 1) * T))), (c * W, r * H))
    sheet.save(path, optimize=True)
    record.append("| `%s/terrain45.spec` | the cells above, each turned 45 degrees and squashed 2:1 (to_iso, %dx%d "
                  "samples, binary outline) | %dx%d diamonds | %dx%d |" % (NAME, SS, SS, W, H, cols * W, rows * H))
    return {tag for _, _, tag in cells}

def coast(out_dir, record):
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

def tilespec(data, out_root, files, blend=True):
    """amplio2.tilespec with sizes and offsets doubled, pixel_ratio 2, the file list renamed, and freeciv45test's
    layer and terrain sections in place of amplio2's (amplio2's other terrains kept, matched as mountains)."""
    ours = square_sections(data, files)
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

Every spec file that `amplio2.tilespec` lists under `amplio2/`, except %(skipped)s (the terrain overlays and ocean
cells the painted ground replaces), is re-cut from Freeciv 3.2.6's amplio2 tileset (GPL-2.0-or-later; the artists are
named in each spec's `[info]` section, copied verbatim): each sprite scaled 2x with nearest-neighbour sampling, so it
looks as amplio2 does on a 2x screen today. `water.spec` keeps only the rivers. `misc/citybar` and `misc/overlays`
are re-cut too, because the client draws them on the map; the other `misc/` files are read from the installed data.

| spec | source | scaling | sheet |
|---|---|---|---|
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a Freeciv data dir with amplio2.tilespec, amplio2/ and trident.tilespec")
    ap.add_argument("--art", required=True, help="the art repo's freeciv45/01_terrain_ground, with the runs in PANELS")
    ap.add_argument("--olive-pine", action="store_true", help="add run 9's r5c4 and r5c5 as forest11 and forest12")
    ap.add_argument("--cutter", help="seamless.py (default: tools/seamless.py next to --art)")
    ap.add_argument("--no-tone-match", action="store_true", help="leave each painted cell's tone as cut")
    ap.add_argument("--no-level", action="store_true", help="keep each cell's light gradient (seamless.py without --level)")
    ap.add_argument("--no-blend", action="store_true", help="no blending between terrains")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    sq.set_tile(T); sq.NAME = NAME
    out_dir = os.path.join(a.out, NAME); os.makedirs(out_dir, exist_ok=True)
    cutter = a.cutter or os.path.join(os.path.dirname(os.path.abspath(a.art)), "tools", "seamless.py")
    panels = {key: os.path.join(a.art, rel) for key, rel in sq.PANELS.items()}
    plan = sq.PLAN + ([sq.OLIVE_PINE] if a.olive_pine else [])
    plan.sort(key=lambda p: [t for t, _, _ in sq.PLAN].index(p[0]))
    painted_record, amplio_record = [], []
    sq.painted(panels, cutter, out_dir, painted_record, plan, tone_match=not a.no_tone_match, level=not a.no_level)
    own = ground(out_dir, painted_record) | {"mask.tile"}
    sq.coastline(panels, cutter, out_dir, painted_record, level=not a.no_level)
    coast(out_dir, painted_record)
    if not a.no_blend: blend(out_dir, painted_record)
    spec_text = open(os.path.join(a.data, "amplio2.tilespec"), errors="replace").read()
    listed = re.findall(r'"([^"]+\.spec)"', spec_text.split("files =", 1)[1].split("files_", 1)[0])  # not files_svg
    files, drop = [], Drop(own)
    sq.OVERRIDDEN = drop
    for rel in listed:
        if rel in SKIPPED: continue
        if rel.startswith("amplio2/"):
            drop.prefixes = DROP_PREFIX.get(rel, ())
            sq.recut(a.data, rel, out_dir, amplio_record, scale=AMPLIO_SCALE)
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
            if rel == "amplio2/terrain1.spec":
                files += ["%s/terrain45.spec" % NAME, "%s/coast.spec" % NAME] + ([] if a.no_blend else ["%s/blend.spec" % NAME])
        elif sq.map_misc_scale(rel) and sq.map_misc_scale(rel) != 1:
            drop.prefixes = ()
            sq.recut(a.data, rel, out_dir, amplio_record, scale=sq.map_misc_scale(rel))
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
        else: files.append(rel)
    tilespec(a.data, a.out, files, blend=not a.no_blend)
    with open(os.path.join(out_dir, "RECORD.md"), "w") as f:
        f.write(RECORD_HEAD % {"name": NAME, "w": W, "h": H, "skipped": ", ".join("`%s`" % s[8:] for s in SKIPPED)})
        f.write("\n".join(amplio_record) + "\n\n## Painted ground, shore and blend masks\n\n"
                "Cut as `make-freeciv45test.py` cuts them (the same panels, cells, cutter and tone match), then turned "
                "into diamonds.\n\n| spec | source | scaling | sheet |\n|---|---|---|---|\n"
                + "\n".join(painted_record) + "\n")
    print("\n".join(amplio_record + painted_record))

if __name__ == "__main__":
    main()
