#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Count units per tile in Freeciv savegames (one-unit-per-tile check).

Usage: scripts/check-stacking.py [--ruleset DIR] SAVE[.gz]...

With --ruleset (e.g. port/freeciv/data/civ54) the civ54 exemptions are applied: unit types flagged
StacksAnywhere are never counted and types flagged StacksInPort are not counted on city tiles.
Prints, per save: players, cities, units, units not inside a transport, tiles holding more than one
such unit, and the worst tiles. Transported units sit on their carrier's tile by design and are skipped.
Stacks inside cities are reported separately and do not fail the check: most rulesets build units there by
necessity (civ54 resolves them by script, so a civ54 save should show none). Exit 1 if any save has a stack
outside a city.
"""
import csv, gzip, io, os, sys
from collections import Counter, defaultdict

def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def tables(lines, key):
    """Yield (section, rows) for every 'key={' table; rows are lists of raw fields."""
    sect = None; i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("[") and ln.endswith("]"): sect = ln[1:-1]
        elif ln.startswith(key + "={"):
            header = next(csv.reader([ln[len(key) + 2:]]))
            rows = []; i += 1
            while i < len(lines) and not lines[i].startswith("}"):
                if lines[i].strip(): rows.append(next(csv.reader([lines[i]])))
                i += 1
            yield sect, header, rows
        i += 1

def ruleset_flags(rsdir):
    """Map unit type rule name -> set of flags from DIR/units.ruleset."""
    import re
    text = open(os.path.join(rsdir, "units.ruleset"), encoding="utf-8").read()
    flags = {}
    for sect in re.split(r"(?m)^(?=\[unit_)", text):
        if not sect.startswith("[unit_"): continue
        name = re.search(r'(?m)^name\s*=\s*_?\(?"([^"]+)"', sect)
        rule = re.search(r'(?m)^rule_name\s*=\s*"([^"]+)"', sect)
        fl = re.search(r'(?ms)^flags\s*=\s*(.*?)(?=^\w)', sect)
        key = rule.group(1) if rule else (name.group(1) if name else None)
        if key: flags[key] = set(re.findall(r'"([^"]+)"', fl.group(1))) if fl else set()
    return flags

def main(paths, uflags=None):
    uflags = uflags or {}
    bad = 0
    for p in paths:
        lines = load(p)
        players = sum(1 for l in lines if l.startswith("[player") and l.endswith("]"))
        city_tiles = {}
        for sect, hdr, rows in tables(lines, "c"):
            ix, iy, iname = hdr.index("x"), hdr.index("y"), hdr.index("name")
            for r in rows: city_tiles[(int(r[ix]), int(r[iy]))] = f"{sect}:{r[iname]}"
        cities = len(city_tiles)
        per_tile = Counter(); total = 0; onmap = 0; owner = {}
        for sect, hdr, rows in tables(lines, "u"):
            ix, iy, it = hdr.index("x"), hdr.index("y"), hdr.index("transported_by")
            ity = hdr.index("type_by_name")
            for r in rows:
                total += 1
                if r[it] != "-1": continue
                t = (int(r[ix]), int(r[iy])); f = uflags.get(r[ity], set())
                if "StacksAnywhere" in f: continue
                if "StacksInPort" in f and t in city_tiles: continue
                onmap += 1; per_tile[t] += 1
                owner.setdefault(t, []).append(f"{sect}:{r[ity]}")
        stacked = {t: n for t, n in per_tile.items() if n > 1}
        in_city = {t: n for t, n in stacked.items() if t in city_tiles}
        field = {t: n for t, n in stacked.items() if t not in city_tiles}
        print(f"{p}: players={players} cities={cities} units={total} on_map={onmap} "
              f"stacked_tiles={len(stacked)} (in_city={len(in_city)} field={len(field)})")
        for t, n in sorted(field.items(), key=lambda kv: -kv[1])[:12]:
            print(f"  FIELD tile {t}: {n} units: {', '.join(owner[t])}")
        for t, n in sorted(in_city.items(), key=lambda kv: -kv[1])[:4]:
            print(f"  city  tile {t} {city_tiles[t]}: {n} units: {', '.join(owner[t])}")
        bad += bool(field)
    return 1 if bad else 0

if __name__ == "__main__":
    args = sys.argv[1:]; uflags = None
    if args[:1] == ["--ruleset"] and len(args) >= 2:
        uflags = ruleset_flags(args[1]); args = args[2:]
    if not args: print(__doc__); sys.exit(2)
    sys.exit(main(args, uflags))
