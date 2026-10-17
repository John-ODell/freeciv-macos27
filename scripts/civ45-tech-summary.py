#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Read the FC45TECH lines scripts/civ45-tech-log.lua wrote to an autogame log and print, per era of the tech
# tree design (notes/freeciv45/design/tech-tree.md), the turn the first and the median player learned their
# first tech of that era, plus each player's tech count at the end.
# Usage: scripts/civ45-tech-summary.py <autogame.log> [--tree notes/freeciv45/design/tech-tree.md]
import collections, re, statistics, sys

ERAS = ["I", "II", "III", "IV", "V", "VI", "VII"]

def eras_from_tree(path):
    era_of = {}; rows = False
    for line in open(path, encoding="utf-8"):
        if line.startswith("| Name | Era | Req 1 | Req 2 | Tier | Unlocks |"):
            rows = True; continue
        if rows and line.startswith("|---"): continue
        if rows and line.startswith("|"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            era_of[c[0].replace("†", "").strip()] = c[1]
        else:
            rows = False
    return era_of

def main():
    args = sys.argv[1:]
    tree = "notes/freeciv45/design/tech-tree.md"
    if "--tree" in args:
        i = args.index("--tree"); tree = args[i + 1]; del args[i:i + 2]
    if not args:
        sys.exit("usage: civ45-tech-summary.py <autogame.log> [--tree TREE.md]")
    era_of = eras_from_tree(tree)
    first = collections.defaultdict(dict)   # player -> era -> turn
    count = collections.Counter(); unknown = set(); last_turn = 0
    for line in open(args[0], encoding="utf-8", errors="replace"):
        m = re.search(r"FC45TECH turn (\d+) (.+?) learned (.+?) by (\S+)$", line)
        if not m:
            continue
        turn, player, tech = int(m.group(1)), m.group(2), m.group(3)
        last_turn = max(last_turn, turn)
        if m.group(4) == "lost":
            continue
        count[player] += 1
        era = era_of.get(tech)
        if era is None:
            unknown.add(tech); continue
        first[player].setdefault(era, turn)
    print(f"{args[0]}: {sum(count.values())} techs learned by {len(count)} players up to turn {last_turn}")
    for era in ERAS:
        turns = sorted(t[era] for t in first.values() if era in t)
        if turns:
            print(f"  era {era}: first player at turn {turns[0]}, median of {len(turns)} at {statistics.median(turns):.0f}, last at {turns[-1]}")
        else:
            print(f"  era {era}: nobody")
    print("  techs per player at the end: " + ", ".join(f"{p} {n}" for p, n in count.most_common()))
    if unknown:
        print("  techs not in the tree: " + ", ".join(sorted(unknown)))

if __name__ == "__main__":
    main()
