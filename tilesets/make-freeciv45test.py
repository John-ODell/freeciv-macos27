#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the freeciv45test tileset: trident's sprites scaled to 96 px squares, with the grassland, plains, forest
and jungle ground replaced by cells cut from painted terrain panels.

Every spec file that trident.tilespec lists under trident/ is re-cut: each grid's cells are cropped from the
30 px sheet, scaled by 96/30 with nearest-neighbour sampling (the pixel art stays crisp; placeholders only),
and laid out again on a clean grid with no pixel border, so the new spec files carry the same tags with new
coordinates. The tilespec is trident's with the sizes and offsets scaled, the file list renamed, a new
terrain45.spec added, and plains, forest and jungle switched from 16 edge-matched sprites to plain variants
like grassland.

The painted ground comes from 5 x 5 ChatGPT panels (PLAN below): panel 1 rows 1-2 grassland and rows 3-4 plains
(row 5, the damp grassland, is left out); panel 4 rows 1-2 forest and row 3 jungle from run 8, row 4 jungle
from run 9's retake (its row 5 is pine: the warm olive c4-c5 only with --olive-pine, the cool c1-c3 not at
all, since the tilespec cannot pick a forest variant by neighbouring terrain). Each cell goes through the art
repo's seamless cutter (192 px master, edges wrapped) and is then scaled to 96 px, giving t.l0.<terrain>1..N;
the client picks a variant per tile from the tile index. Because the client puts any two variants side by side, the
masters of each terrain are first matched in tone (match_tone): in CIE Lab every cell is moved to the terrain's mean
lightness and colour and its contrast to the terrain's mean contrast, so the texture stays and only the cell's
overall level changes. --no-tone-match skips it.

Neighbouring terrains fade into each other at the tile edge: the land terrains get blend_layer = 1, and blend.spec
holds t.blend_mask, a generated 3 x 3 tile alpha mask that says how strongly a terrain shows in each tile around it
(BLEND_PEAK at the shared edge, nothing BLEND_DEPTH pixels in). Freeciv 3.2 blends only in isometric view; the fork's
patch 0019 uses this mask in overhead view. Terrains drawn from trident's 16 edge-matched sprites get a t.blend.<tag>
alias on their all-neighbours-alike sprite, which the client takes as the texture that fades out. --no-blend
leaves all of that out.

usage: make-freeciv45test.py --data ~/freeciv-builds/qt/share/freeciv --panel PANEL1.png --panel4 RUN8.png
                             --panel4-retake RUN9.png [--olive-pine]
                             --cutter ~/Desktop/asset_generator/freeciv45/tools/seamless.py [--out tilesets]
                             [--no-tone-match] [--no-blend]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, importlib.util, os, re
from PIL import Image, ImageCms, ImageStat

NAME = "freeciv45test"
TILE = 96
SRC_TILE = 30
SCALE = TILE / SRC_TILE          # 3.2

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

OVERRIDDEN = {"t.l0.grassland1"}      # terrain45.spec provides these; dropping them here avoids a duplicate-tag warning

# Blending between terrains (patch 0019 in the fork): which terrains take part, and the shape of the fade.
BLEND_TERRAINS = ("desert", "forest", "grassland", "hills", "jungle", "mountains", "plains", "swamp", "tundra")
BLEND_ALIASES = {"t.l0.%s_n1e1s1w1" % t: "t.blend.%s" % t for t in ("desert", "hills", "mountains", "swamp", "tundra")}
BLEND_DEPTH = 24      # px into the neighbouring tile where the fade reaches nothing (a quarter tile)
BLEND_PEAK = 0.5      # opacity at the shared edge; both sides blend, so the edge itself is half and half

def recut(data, spec_rel, out_dir, record, aliases={}):
    """Re-cut one trident spec file (e.g. trident/tiles.spec) to <out_dir>/<base>.spec and .png."""
    header, grids = parse_spec(os.path.join(data, spec_rel))
    for g in grids:
        g["cells"] = [(r, c, [t for t in tags if t not in OVERRIDDEN] + [aliases[t] for t in tags if t in aliases])
                      for r, c, tags in g["cells"]]
        g["cells"] = [cell for cell in g["cells"] if cell[2]]
    gfx = next(re.search(r'gfx\s*=\s*"([^"]+)"', h).group(1) for h in header if re.search(r'gfx\s*=\s*"', h))
    src = Image.open(os.path.join(data, gfx + ".png")).convert("RGBA")
    base = os.path.basename(spec_rel)[:-5]
    width, height, placed = 0, 0, []
    for g in grids:
        p = g["params"]; dx, dy, pb = p["dx"], p["dy"], p.get("pixel_border", 0)
        x0, y0 = p.get("x_top_left", 0), p.get("y_top_left", 0)
        ndx, ndy = round(dx * SCALE), round(dy * SCALE)
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
                % (spec_rel, NAME, SCALE))
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
                  % (NAME, base, spec_rel, ntags, len(grids), SCALE, width, height))

# Painted ground, in sheet order: (terrain, panel key, panel cells). Each terrain's cells become t.l0.<terrain>1..N
# and start on a new sheet row, five to a row. Panel keys are the --panel options.
PLAN = [
    ("grassland", "panel1", ["r1c%d" % c for c in range(1, 6)] + ["r2c%d" % c for c in range(1, 6)]),
    ("plains", "panel1", ["r3c%d" % c for c in range(1, 6)] + ["r4c%d" % c for c in range(1, 6)]),
    ("forest", "panel4", ["r1c%d" % c for c in range(1, 6)] + ["r2c%d" % c for c in range(1, 6)]),
    ("jungle", "panel4", ["r3c%d" % c for c in range(1, 6)]),
    ("jungle", "panel4_retake", ["r4c%d" % c for c in range(1, 6)]),
]
OLIVE_PINE = ("forest", "panel4_retake", ["r5c4", "r5c5"])   # run 9's warm olive pine; --olive-pine adds it

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

def painted(panels, cutter, out_dir, record, plan, tone_match=True):
    """Cut the planned panel cells into 96 px seamless ground variants; write terrain45.png and terrain45.spec."""
    spec = importlib.util.spec_from_file_location("seamless", cutter); seamless = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seamless)
    images = {key: Image.open(path).convert("RGB") for key, path in panels.items()}
    boxes = {key: seamless.cells(im) for key, im in images.items()}
    placed, lines, count, row, prev = [], [], {}, -1, None
    for terrain, key, names in plan:
        for i, name in enumerate(names):
            n = count.get(terrain, 0); count[terrain] = n + 1
            if terrain != prev or n % 5 == 0: row += 1
            prev = terrain
            x0, y0, x1, y1 = boxes[key][name]; inset = 3
            cell = images[key].crop((x0 + inset, y0 + inset, x1 - inset, y1 - inset))
            side = min(cell.size)
            master = seamless.make_seamless(cell.crop((0, 0, side, side)).resize((192, 192), Image.LANCZOS))
            placed.append([master, n % 5, row, terrain])
            lines.append('  %d, %d, "t.l0.%s%d"   ; %s %s' % (row, n % 5, terrain, n + 1, key, name))
    tones = []
    for terrain in dict.fromkeys(p[3] for p in placed):
        group = [p for p in placed if p[3] == terrain]
        before = luma_range([p[0].resize((TILE, TILE), Image.LANCZOS) for p in group])
        if tone_match:
            for p, tile in zip(group, match_tone([p[0] for p in group])): p[0] = tile
        after = luma_range([p[0].resize((TILE, TILE), Image.LANCZOS) for p in group])
        tones.append("%s %.0f-%.0f -> %.0f-%.0f" % (terrain, before[0], before[1], after[0], after[1]))
    sheet = Image.new("RGB", (TILE * 5, TILE * (row + 1)))
    for master, c, r, _ in placed: sheet.paste(master.resize((TILE, TILE), Image.LANCZOS), (c * TILE, r * TILE))
    sheet.save(os.path.join(out_dir, "terrain45.png"), optimize=True)
    with open(os.path.join(out_dir, "terrain45.spec"), "w") as f:
        f.write("; Painted ground for the Freeciv45 test tileset, cut from ChatGPT terrain panels by\n"
                "; tilesets/make-%s.py (see RECORD.md). Each cell: seamless.py 192 px master, then 96 px.\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/terrain45"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n' % (NAME, NAME, TILE, TILE, "\n".join(lines)))
    for key, path in panels.items():
        used = ", ".join("%s %d" % (t, len(c)) for t, k, c in plan if k == key)
        record.append("| `%s/terrain45.spec` | `%s` (%s): %s, through `%s` | LANCZOS 192 then 96 | %dx%d |"
                      % (NAME, key, os.path.basename(path), used, os.path.basename(cutter), TILE * 5, TILE * (row + 1)))
    record.append("| tone match | %s | mean luma per variant at 96 px, min-max |" % ("on" if tone_match else "off")
                  + " %s |" % "; ".join(tones))

def blend_mask(out_dir, record):
    """Write blend.png and blend.spec: t.blend_mask, 3 x 3 tiles, white with an alpha that is the opacity of the middle
    tile's terrain where it fades into each of its eight neighbours. Across an edge the opacity falls from BLEND_PEAK
    at the edge to 0 at BLEND_DEPTH (smoothstep, so it starts and ends flat); in a corner tile it is the product of
    the two edge fades over BLEND_PEAK, which joins the edge fades of the tiles beside it without a seam. The
    middle tile is never used and stays transparent."""
    side = 3 * TILE; mask = Image.new("RGBA", (side, side), (255, 255, 255, 0)); px = mask.load()
    def fade(d):                     # d: distance in px from the shared edge, at the pixel centre
        u = min(d / BLEND_DEPTH, 1.0); return 1.0 - u * u * (3 - 2 * u)
    def dist(v):                     # distance of pixel row/column v outside the middle tile, 0 inside it
        return TILE - v - 0.5 if v < TILE else v + 0.5 - 2 * TILE if v >= 2 * TILE else 0.0
    for y in range(side):
        for x in range(side):
            dx, dy = dist(x), dist(y)
            if dx or dy: px[x, y] = (255, 255, 255, round(255 * BLEND_PEAK * fade(dx) * fade(dy)))
    mask.save(os.path.join(out_dir, "blend.png"), optimize=True)
    with open(os.path.join(out_dir, "blend.spec"), "w") as f:
        f.write("; Blend mask for the Freeciv45 test tileset, generated by tilesets/make-%s.py (blend_mask):\n"
                "; 3 x 3 tiles, how strongly a terrain shows in each tile around it. Used by blend_layer in\n"
                "; overhead view (fork patch 0019).\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    Generated (no artist)\n"\n\n'
                '[file]\ngfx = "%s/blend"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n  0, 0, "t.blend_mask"\n}\n' % (NAME, NAME, side, side))
    record.append("| `%s/blend.spec` | generated: `t.blend_mask`, peak %g at the edge, %d px deep | none | %dx%d |"
                  % (NAME, BLEND_PEAK, BLEND_DEPTH, side, side))

def tilespec(data, out_root, files, blend=True):
    """trident.tilespec with sizes, offsets, name and file list changed; plains, forest and jungle as plain variants;
    with blend, blend_layer 1 for BLEND_TERRAINS."""
    scaled = {"normal_tile_width": TILE, "normal_tile_height": TILE, "stack_size_offset_x": 64,
              "stack_size_offset_y": 32, "citybar_offset_y": 86, "tilelabel_offset_y": 32,
              "unit_upkeep_small_offset_y": 64}
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
        if key in scaled: out.append("%s = %d" % (key, scaled[key])); continue
        if key == "name": out.append('name = "Freeciv45 test"'); continue
        if key == "priority": out.append("priority = 4"); continue
        if key == "summary": out.append('summary = _("Freeciv45 test tileset: 96 px overhead squares, painted grassland, plains, forest and jungle, scaled trident placeholders.")'); continue
        if section in ("tile_plains", "tile_forest", "tile_jungle") and key == "layer0_match_with":
            continue    # <terrain>1..N variants from terrain45.spec, no edge matching
        if blend and key == "blend_layer" and section and section[5:] in BLEND_TERRAINS:
            out.append("blend_layer = 1"); continue     # neighbours fade in after layer 0, under the coast cells
        out.append(line)
    text = "\n".join(out) + "\n"
    text = text.replace("[tilespec]\n", "[tilespec]\n\n; Freeciv45 test tileset, built by tilesets/make-%s.py from trident.tilespec; see RECORD.md.\n" % NAME, 1)
    open(os.path.join(out_root, NAME + ".tilespec"), "w").write(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a Freeciv data dir with trident.tilespec and trident/")
    ap.add_argument("--panel", required=True, help="panel 1 (grassland and plains), run 6")
    ap.add_argument("--panel4", required=True, help="panel 4 (forest and jungle), run 8: rows 1-3")
    ap.add_argument("--panel4-retake", required=True, help="panel 4, run 9: rows 4 (jungle) and 5 (pine)")
    ap.add_argument("--olive-pine", action="store_true", help="add run 9's r5c4 and r5c5 as forest11 and forest12")
    ap.add_argument("--cutter", required=True)
    ap.add_argument("--no-tone-match", action="store_true", help="leave each painted cell's tone as cut (the build before issue 138)")
    ap.add_argument("--no-blend", action="store_true", help="no blending between terrains (the build before issue 141)")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    out_dir = os.path.join(a.out, NAME); os.makedirs(out_dir, exist_ok=True)
    spec_text = open(os.path.join(a.data, "trident.tilespec"), errors="replace").read()
    listed = re.findall(r'"([^"]+\.spec)"', spec_text.split("files =", 1)[1].split("*include", 1)[0])
    files, record = [], []
    for rel in listed:
        if rel.startswith("trident/"):
            recut(a.data, rel, out_dir, record, {} if a.no_blend else BLEND_ALIASES)
            files.append("%s/%s" % (NAME, os.path.basename(rel)))
            if rel == "trident/tiles.spec":
                files.append("%s/terrain45.spec" % NAME)
                if not a.no_blend: files.append("%s/blend.spec" % NAME)
        else: files.append(rel)
    plan = PLAN + ([OLIVE_PINE] if a.olive_pine else [])
    plan.sort(key=lambda p: [t for t, _, _ in PLAN].index(p[0]))     # keep each terrain's cells together
    painted({"panel1": a.panel, "panel4": a.panel4, "panel4_retake": a.panel4_retake}, a.cutter, out_dir, record, plan,
            tone_match=not a.no_tone_match)
    if not a.no_blend: blend_mask(out_dir, record)
    tilespec(a.data, a.out, files, blend=not a.no_blend)
    print("| spec | source | scaling | sheet |\n|---|---|---|---|\n" + "\n".join(record))

if __name__ == "__main__":
    main()
