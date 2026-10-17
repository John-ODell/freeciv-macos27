#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Count the FC45DRAFT / FC45SHRINK / FC45WHIP lines scripts/civ45-draft-log.lua wrote to an autogame log, and
# the sizes of the cities in a final save (the save's city "size=" lines).
# Usage: scripts/civ45-draft-summary.py <autogame.log> [<final.sav.gz>]...
#        scripts/civ45-draft-summary.py --city <name> <field> <save.sav.gz>   (prints that city's field)
import collections, csv, gzip, re, sys

def cities(save_path):
    # Each [playerN] holds its cities as a table c={"col",...} followed by one row per city.
    with gzip.open(save_path, "rt", encoding="utf-8", errors="replace") as f:
        cols = None
        for line in f:
            line = line.rstrip("\n")
            if cols is None:
                if line.startswith("c={"):
                    cols = next(csv.reader([line[3:]]))
                continue
            if line == "}":
                cols = None
                continue
            row = next(csv.reader([line]))
            if len(row) == len(cols):
                yield dict(zip(cols, row))

def summarize(log_path):
    drafts = collections.Counter(); sizes = collections.Counter(); whips = collections.Counter()
    shrinks = 0; first = None
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"FC45DRAFT turn (\d+) (\S+) of (.+?) in (.+?) size (\d+)$", line)
            if m:
                drafts[m.group(2)] += 1; sizes[int(m.group(5))] += 1
                first = first or int(m.group(1))
                continue
            if "FC45SHRINK" in line:
                shrinks += 1
                continue
            m = re.search(r"FC45WHIP turn (\d+) (\S+) of (.+?) into (.+?) (draft|other)$", line)
            if m:
                whips[(m.group(2), m.group(5))] += 1
    print(f"{log_path}:")
    print(f"  draft units built: {sum(drafts.values())} ({', '.join(f'{k} {v}' for k, v in drafts.most_common()) or 'none'})"
          + (f", first at turn {first}" if first else ""))
    print(f"  city size after the draft: {', '.join(f'size {k}: {v}' for k, v in sorted(sizes.items())) or 'none'}")
    print(f"  cities shrunk by a build: {shrinks}")
    print(f"  disbanded into a build: {sum(whips.values())} ({', '.join(f'{t} ({k}) {v}' for (t, k), v in whips.most_common()) or 'none'})")

def city_sizes(save_path):
    sizes = [int(c["size"]) for c in cities(save_path)]
    if not sizes:
        print(f"{save_path}: no city sizes found"); return
    small = sum(1 for s in sizes if s <= 2)
    print(f"{save_path}: {len(sizes)} cities, mean size {sum(sizes)/len(sizes):.1f}, largest {max(sizes)}, "
          f"size 1-2: {small} ({100*small//len(sizes)}%)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__ or "usage: civ45-draft-summary.py <autogame.log> [<save.sav.gz>]...")
    if sys.argv[1] == "--city":
        for c in cities(sys.argv[4]):
            if c.get("name") == sys.argv[2]:
                print(c.get(sys.argv[3], "")); sys.exit(0)
        sys.exit(1)
    for p in sys.argv[1:]:
        if p.endswith(".gz"):
            city_sizes(p)
        else:
            summarize(p)
