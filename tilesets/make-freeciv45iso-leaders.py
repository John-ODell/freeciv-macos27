#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Builds freeciv45iso/leaders.jpg and leaders.spec, the leader portraits the Qt client shows in the
diplomacy dialog, from the Freeciv45 art pack's leader run (freeciv45/15_leaders, cut by its cut_moods.py).

One row per nation, six moods per row (neutral, pleased, delighted, annoyed, angry, sad), CELL px each.
Sprite tags are leader.<nation>.<mood>, <nation> being the nation's rule name in lower case with spaces
as underscores; the client also looks for leader.<nation>.<male|female>.<mood> first, for a later run
with a ruler of each sex.

Usage: make-freeciv45iso-leaders.py <art run dir with post/<id>/<mood>.png> <rulers.names>
"""
import os, sys
from PIL import Image

CELL = 192
MOODS = ["neutral", "pleased", "delighted", "annoyed", "angry", "sad"]
here = os.path.dirname(os.path.abspath(__file__))
run, names = sys.argv[1], sys.argv[2]
rows = [l.rstrip("\n").split("\t") for l in open(names) if l.strip()]
sheet = Image.new("RGB", (CELL * len(MOODS), CELL * len(rows)))
tiles = []
for r, (rid, nation, label) in enumerate(rows):
    tag = nation.lower().replace(" ", "_")
    for c, mood in enumerate(MOODS):
        im = Image.open(os.path.join(run, "post", rid, mood + ".png")).convert("RGB")
        sheet.paste(im.resize((CELL, CELL), Image.LANCZOS), (c * CELL, r * CELL))
        tiles.append(f'  {r}, {c}, "leader.{tag}.{mood}"')
# photographic, so JPEG (a tenth of the PNG); the Qt client bundles the JPEG plugin
sheet.save(os.path.join(here, "freeciv45iso", "leaders.jpg"), quality=90)
with open(os.path.join(here, "freeciv45iso", "leaders.spec"), "w") as f:
    f.write(f"""; Leader portraits for the Qt client's diplomacy dialog, one row per nation, one column per mood.
; Painted for Freeciv45 (art pack freeciv45/15_leaders run 1, see RECORD.md), built by
; tilesets/make-freeciv45iso-leaders.py. Invented rulers, not likenesses of real people.

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/leaders"

[grid_leaders]

x_top_left = 0
y_top_left = 0
dx = {CELL}
dy = {CELL}

tiles = {{ "row", "column", "tag"
""" + "\n".join(tiles) + "\n}\n")
print(len(rows), "nations,", len(tiles), "sprites")
