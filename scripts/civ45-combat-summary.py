#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Summarize the lines scripts/civ45-combat-log.lua wrote into an autogame's server log.

Usage: scripts/civ45-combat-summary.py LOG...

For each log: the turn the game ended, how many times each attack-type action was done and by which unit
types, how often a bombardment hit a city tile, the units lost by reason, and the cities that changed hands.
"""
import re, sys
from collections import Counter, defaultdict

ACT = re.compile(r"FC45COMBAT turn (\d+) (.+?) (ok|failed) (.+?) -> \((\d+),(\d+)\) units (\d+) city (.*)$")
LOST = re.compile(r"FC45LOST turn (\d+) (.+?) of (.+?) reason (.+)$")
CITY = re.compile(r"FC45CITY turn (\d+) (.+?) from (.+?) to (.+?) reason (.+)$")

def summarize(path):
    actions = Counter(); actors = defaultdict(Counter); city_targets = Counter(); lost = Counter()
    killed_types = Counter(); cities = []; last_turn = 0; ended = ""
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = ACT.search(ln)
            if m:
                turn, act, ok, actor, x, y, n, city = m.groups()
                last_turn = max(last_turn, int(turn))
                key = act if ok == "ok" else act + " (failed)"
                actions[key] += 1
                utype = "(attacker died)" if actor == "dead" else actor.split(" of ")[0]
                actors[act][utype] += 1
                if city != "-": city_targets[act] += 1
                continue
            m = LOST.search(ln)
            if m:
                turn, utype, player, reason = m.groups()
                lost[reason] += 1
                if reason == "killed": killed_types[utype] += 1
                continue
            m = CITY.search(ln)
            if m:
                cities.append(m.groups())
                continue
            if "Game ended" in ln or "victory to" in ln:
                ended = ln.strip().split(": ", 1)[-1]
    print(f"== {path}")
    print(f"ended: {ended or 'no end line'}; last combat turn {last_turn}")
    print("actions:", ", ".join(f"{k} {v}" for k, v in actions.most_common()) or "none")
    for act, c in actors.items():
        print(f"  {act} by: " + ", ".join(f"{k} {v}" for k, v in c.most_common()) + f"; on a city tile {city_targets[act]}")
    print("units lost:", ", ".join(f"{k} {v}" for k, v in lost.most_common()) or "none")
    if killed_types:
        print("  killed: " + ", ".join(f"{k} {v}" for k, v in killed_types.most_common()))
    print(f"cities changing hands: {len(cities)}")
    for turn, city, old, new, reason in cities:
        print(f"  turn {turn} {city}: {old} -> {new} ({reason})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    for p in sys.argv[1:]:
        summarize(p)
