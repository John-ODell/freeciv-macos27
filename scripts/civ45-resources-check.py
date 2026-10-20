#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read the res-before and res-after saves that scripts/civ45-resources-test.lua makes and check the
Tester's own map (savegame3: "playerN.map_eNN_YYYY", four extras per hex character, in the order of
savefile.extras_vector) on the tiles the test logged (native coordinates): each resource is on the real map in both saves,
missing from the Tester's map before its tech, and there after. Also counts the resources the Tester
knows map-wide. Usage: civ45-resources-check.py <log dir>; exit 1 on any failure."""
import glob, re, sys

out = sys.argv[1]
log = open(f"{out}/server.log").read()
tiles = [(m[0], int(m[1]), int(m[2])) for m in re.findall(r"FC45TEST TILE (\w+) (\d+) (\d+)", log)]

def load(name):
    path = (glob.glob(f"{out}/{name}*.sav") + glob.glob(f"{out}/{name}*"))[0]
    sec, data = None, {}
    for line in open(path, errors="replace"):
        m = re.match(r"^\[(\w+)\]", line)
        if m:
            sec = m[1]; continue
        m = re.match(r'^(\w+)\s*=\s*"?(.*?)"?\s*$', line)
        if m and sec:
            data.setdefault(sec, {})[m[1]] = m[2]
    return data

def extras_order(d):
    raw = d["savefile"]["extras_vector"]
    return re.findall(r'"([^"]*)"', '"' + raw + '"')

def has(d, sec, prefix, names, extra, x, y):
    i = names.index(extra)
    row = d[sec][f"{prefix}e{i // 4:02d}_{y:04d}"]
    return bool(int(row[x], 16) & (1 << (i % 4)))

rc = 0
def check(what, ok):
    global rc
    print(f"FC45TEST {'PASS' if ok else 'FAIL'} {what}")
    rc |= not ok

for label in ("before", "after"):
    d = load(f"res-{label}")
    names = extras_order(d)
    tester = next(s for s, v in d.items() if s.startswith("player") and v.get("name") == "Tester")
    for extra, x, y in tiles:
        check(f"{label}: the map has {extra} at {x},{y}", has(d, "map", "", names, extra, x, y))
        seen = has(d, tester, "map_", names, extra, x, y)
        check(f"{label}: the Tester's map {'shows' if seen else 'hides'} {extra} at {x},{y}",
              seen == (label == "after"))
    counts = []
    for extra in ("Iron", "Horses", "Coal", "Oil"):
        i = names.index(extra)
        n = sum(bool(int(ch, 16) & (1 << (i % 4)))
                for k, row in d[tester].items() if k.startswith(f"map_e{i // 4:02d}_")
                for ch in row if ch in "0123456789abcdef")
        counts.append(f"{extra} {n}")
    print(f"FC45TEST INFO {label}: the Tester's map holds " + ", ".join(counts))
sys.exit(rc)
