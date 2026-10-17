#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Count the FC45GP lines civ45's script.lua writes in an autogame log: births by kind and cause, uses by
# kind and how (deed, settle, pledge), golden ages, and the turns from a great person's birth to its use.
# Usage: scripts/civ45-gp-summary.py <autogame.log>...
import collections, re, statistics, sys

for path in sys.argv[1:]:
    births = collections.Counter(); causes = collections.Counter(); uses = collections.Counter()
    born_turn = {}; latency = []; ages = 0; ended = 0; per_player = collections.Counter(); first = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"FC45GP turn (\d+) born (Great \w+) of (.+?) in .+? by (.+?) unit (\d+)", line)
            if m:
                births[m.group(2)] += 1; causes["points" if m.group(4) == "points" else "first to a tech"] += 1
                born_turn[m.group(5)] = int(m.group(1)); per_player[m.group(3)] += 1
                first = first or int(m.group(1))
                continue
            m = re.search(r"FC45GP turn (\d+) ai (deed|settle|pledge) by (Great \w+) of .+? unit (\d+)", line)
            if m:
                uses[(m.group(3), m.group(2))] += 1
                if m.group(4) in born_turn:
                    latency.append(int(m.group(1)) - born_turn.pop(m.group(4)))
                continue
            if "golden age" in line and "begins" in line:
                ages += 1
            elif "golden age" in line and "ended" in line:
                ended += 1
    print(f"{path}: {sum(births.values())} great people born (first at turn {first}), {sum(uses.values())} used by the AI, "
          f"{ages} golden ages begun, {ended} ended, {len(born_turn)} unused at the end")
    print("  births: " + ", ".join(f"{k} {n}" for k, n in births.most_common()) + "; " + ", ".join(f"{c} {n}" for c, n in causes.items()))
    print("  uses: " + ", ".join(f"{k} {how} {n}" for (k, how), n in sorted(uses.items())))
    if latency:
        print(f"  turns from birth to use: median {statistics.median(latency)}, max {max(latency)}, "
              f"{sum(1 for l in latency if l <= 20)} of {len(latency)} within 20")
    print("  per player: " + ", ".join(f"{p} {n}" for p, n in per_player.most_common(5)))
