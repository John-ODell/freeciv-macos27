#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the freeciv45test tileset: trident's sprites scaled to 96 px squares, with the grassland and plains
ground replaced by cells cut from a painted terrain panel.

Every spec file that trident.tilespec lists under trident/ is re-cut: each grid's cells are cropped from the
30 px sheet, scaled by 96/30 with nearest-neighbour sampling (the pixel art stays crisp; placeholders only),
and laid out again on a clean grid with no pixel border, so the new spec files carry the same tags with new
coordinates. The tilespec is trident's with the sizes and offsets scaled, the file list renamed, a new
terrain45.spec added, and plains switched from 16 edge-matched sprites to plain variants like grassland.

The painted ground comes from a 5 x 5 ChatGPT panel: rows 1-2 are grassland, rows 3-4 plains (row 5, the
damp grassland, is left out). Each cell goes through the art repo's seamless cutter (192 px master, edges
wrapped) and is then scaled to 96 px, giving t.l0.grassland1..10 and t.l0.plains1..10; the client picks a
variant per tile from the tile index.

usage: make-freeciv45test.py --data ~/freeciv-builds/qt/share/freeciv --panel PANEL.png
                             --cutter ~/Desktop/asset_generator/freeciv45/tools/seamless.py [--out tilesets]
Needs Pillow (python3.14 on this Mac has it).
"""
import argparse, importlib.util, os, re
from PIL import Image

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

def recut(data, spec_rel, out_dir, record):
    """Re-cut one trident spec file (e.g. trident/tiles.spec) to <out_dir>/<base>.spec and .png."""
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

def painted(panel, cutter, out_dir, record):
    """Cut rows 1-4 of the panel into 96 px seamless ground variants; write terrain45.png and terrain45.spec."""
    spec = importlib.util.spec_from_file_location("seamless", cutter); seamless = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seamless)
    im = Image.open(panel).convert("RGB"); boxes = seamless.cells(im)
    plan = [("grassland", ["r1c%d" % c for c in range(1, 6)] + ["r2c%d" % c for c in range(1, 6)]),
            ("plains", ["r3c%d" % c for c in range(1, 6)] + ["r4c%d" % c for c in range(1, 6)])]
    sheet = Image.new("RGB", (TILE * 5, TILE * 4)); lines = []
    for ti, (terrain, names) in enumerate(plan):
        for vi, name in enumerate(names):
            x0, y0, x1, y1 = boxes[name]; inset = 3
            cell = im.crop((x0 + inset, y0 + inset, x1 - inset, y1 - inset))
            side = min(cell.size)
            master = seamless.make_seamless(cell.crop((0, 0, side, side)).resize((192, 192), Image.LANCZOS))
            tile = master.resize((TILE, TILE), Image.LANCZOS)
            r, c = ti * 2 + vi // 5, vi % 5
            sheet.paste(tile, (c * TILE, r * TILE))
            lines.append('  %d, %d, "t.l0.%s%d"   ; panel cell %s' % (r, c, terrain, vi + 1, name))
    sheet.save(os.path.join(out_dir, "terrain45.png"), optimize=True)
    with open(os.path.join(out_dir, "terrain45.spec"), "w") as f:
        f.write("; Painted ground for the Freeciv45 test tileset, cut from a ChatGPT terrain panel by\n"
                "; tilesets/make-%s.py (see RECORD.md). Each cell: seamless.py 192 px master, then 96 px.\n\n"
                '[spec]\n\noptions = "+Freeciv-3.2-spec"\n\n[info]\n\nartists = "\n    John O\'Dell (sheet workflow)\n"\n\n'
                '[file]\ngfx = "%s/terrain45"\n\n[grid_main]\n\nx_top_left = 0\ny_top_left = 0\ndx = %d\ndy = %d\n\n'
                'tiles = { "row", "column", "tag"\n%s\n}\n' % (NAME, NAME, TILE, TILE, "\n".join(lines)))
    record.append("| `%s/terrain45.spec` | panel `%s`, rows 1-4 (20 cells) through `%s` | LANCZOS 192 then 96 | %dx%d |"
                  % (NAME, os.path.basename(panel), os.path.basename(cutter), TILE * 5, TILE * 4))

def tilespec(data, out_root, files):
    """trident.tilespec with sizes, offsets, name and file list changed, plains as plain variants."""
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
        if key == "summary": out.append('summary = _("Freeciv45 test tileset: 96 px overhead squares, painted grassland and plains, scaled trident placeholders.")'); continue
        if section == "tile_plains" and key == "layer0_match_with": continue   # plains1..N variants, no edge matching
        out.append(line)
    text = "\n".join(out) + "\n"
    text = text.replace("[tilespec]\n", "[tilespec]\n\n; Freeciv45 test tileset, built by tilesets/make-%s.py from trident.tilespec; see RECORD.md.\n" % NAME, 1)
    open(os.path.join(out_root, NAME + ".tilespec"), "w").write(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a Freeciv data dir with trident.tilespec and trident/")
    ap.add_argument("--panel", required=True); ap.add_argument("--cutter", required=True)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    out_dir = os.path.join(a.out, NAME); os.makedirs(out_dir, exist_ok=True)
    spec_text = open(os.path.join(a.data, "trident.tilespec"), errors="replace").read()
    listed = re.findall(r'"([^"]+\.spec)"', spec_text.split("files =", 1)[1].split("*include", 1)[0])
    files, record = [], []
    for rel in listed:
        if rel.startswith("trident/"):
            recut(a.data, rel, out_dir, record); files.append("%s/%s" % (NAME, os.path.basename(rel)))
            if rel == "trident/tiles.spec": files.append("%s/terrain45.spec" % NAME)
        else: files.append(rel)
    painted(a.panel, a.cutter, out_dir, record)
    tilespec(a.data, a.out, files)
    print("| spec | source | scaling | sheet |\n|---|---|---|---|\n" + "\n".join(record))

if __name__ == "__main__":
    main()
