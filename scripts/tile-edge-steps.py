#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""How strongly the tile grid shows in a map screenshot: for each tile edge segment inside a box (one tile long),
the difference between the mean luma of the 8 px band on one side and the band on the other side, averaged over
all segments; and the same measure across the tiles' middle lines, where there is no edge, as the baseline of
the terrain's own variation. Tile edges at or below the baseline do not read as a grid of tone steps.

usage: tile-edge-steps.py SHOT.png [SHOT2.png ...] --box L,T,R,B --origin X,Y [--tile 96] [--band 8]
  --box     the area to measure, in screenshot pixels (one terrain only, few units on it)
  --origin  any tile corner in screenshot pixels (the client's tile grid)
Needs Pillow.
"""
import argparse
from PIL import Image, ImageStat

def steps(im, box, origin, off, tile, band):
    (l, t, r, b), (x0, y0) = box, origin
    mean = lambda c: ImageStat.Stat(im.crop(c)).mean[0]
    first = lambda o, lo: o + ((lo - o) // tile) * tile        # first grid line at or before lo
    diffs = []
    for gx in range(first(x0, l) + off, r, tile):              # vertical lines, one segment per tile row
        for gy in range(first(y0, t), b - tile + 1, tile):
            if gx - band >= l and gx + band <= r and gy >= t:
                diffs.append(abs(mean((gx - band, gy, gx, gy + tile)) - mean((gx, gy, gx + band, gy + tile))))
    for gy in range(first(y0, t) + off, b, tile):              # horizontal lines
        for gx in range(first(x0, l), r - tile + 1, tile):
            if gy - band >= t and gy + band <= b and gx >= l:
                diffs.append(abs(mean((gx, gy - band, gx + tile, gy)) - mean((gx, gy, gx + tile, gy + band))))
    return sum(diffs) / len(diffs), len(diffs)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("shots", nargs="+")
    ap.add_argument("--box", required=True); ap.add_argument("--origin", required=True)
    ap.add_argument("--tile", type=int, default=96); ap.add_argument("--band", type=int, default=8)
    a = ap.parse_args()
    box = tuple(int(v) for v in a.box.split(",")); origin = tuple(int(v) for v in a.origin.split(","))
    for shot in a.shots:
        im = Image.open(shot).convert("L")
        edge, n = steps(im, box, origin, 0, a.tile, a.band)
        middle, _ = steps(im, box, origin, a.tile // 2, a.tile, a.band)
        print("%s: tone step at tile edges %.1f (%d segments), across tile middles %.1f" % (shot, edge, n, middle))

if __name__ == "__main__":
    main()
