#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Roster summary for a Freeciv45 (civ45) autogame: which unit types are alive in a save, by era of the roster
# (notes/freeciv45/design/units-and-upgrades.md), the largest stack on one tile, and, from an autogame log
# written with scripts/civ45-combat-log.lua, which types attacked and which died.
# Usage: scripts/civ45-roster-summary.py [<autogame.log>] <save.sav.gz>...
import collections, csv, gzip, re, sys

# Rule names (the renamed units keep their old ones; the display name is in units.ruleset).
ERAS = [
    ("I", ["Warriors", "Scout", "Phalanx", "Axemen", "Archers", "Horsemen", "Horse Bowmen", "Chariot", "Trireme", "Levy"]),
    ("II", ["Legion", "Elephants", "Catapult", "War Galley"]),
    ("III", ["Macebearers", "Pikemen", "Longbowmen", "Crossbowmen", "Knights", "Trebuchet", "Caravel", "Explorer"]),
    ("IV", ["Musketeers", "Grenadiers", "Dragoons", "Cannon", "Galleon", "Frigate", "Ship of the Line", "Militia"]),
    ("V", ["Riflemen", "Infantry", "Machine Gunners", "Cavalry", "Artillery", "Ironclad", "Transport", "Conscripts"]),
    ("VI", ["Armoured Cars", "Armor", "Marines", "Paratroopers", "Partisan", "Fanatics", "Fighter", "Bomber", "Destroyer",
            "Cruiser", "Battleship", "Submarine", "Carrier", "Cruise Missile", "Nuclear"]),
    ("VII", ["Main Battle Tank", "Mech. Inf.", "Helicopter", "Air Defence Infantry", "Howitzer", "Jet Fighter",
             "Stealth Fighter", "Stealth Bomber", "AWACS", "AEGIS Cruiser", "SSBN", "ICBM"]),
]
ERA_OF = {u: e for e, us in ERAS for u in us}

def units(save_path):
    # Each [playerN] holds its units as a table u={"col",...} followed by one row per unit.
    with gzip.open(save_path, "rt", encoding="utf-8", errors="replace") as f:
        cols, player = None, None
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"\[(player\d+)\]", line)
            if m:
                player = m.group(1)
            if cols is None:
                if line.startswith("u={"):
                    cols = next(csv.reader([line[3:]]))
                continue
            if line == "}":
                cols = None
                continue
            row = next(csv.reader([line]))
            if len(row) == len(cols):
                d = dict(zip(cols, row))
                d["player"] = player
                yield d

def save_summary(path):
    by_type = collections.Counter(); by_era = collections.Counter(); stacks = collections.Counter()
    by_player = collections.Counter()
    for u in units(path):
        t = u.get("type_by_name", "?")
        by_type[t] += 1
        by_era[ERA_OF.get(t, "other")] += 1
        by_player[u["player"]] += 1
        stacks[(u.get("x"), u.get("y"))] += 1
    m = re.search(r"T(\d+)", path)
    turn = m.group(1).lstrip("0") if m else "?"
    total = sum(by_type.values())
    print(f"{path}: turn {turn}, {total} units of {len(by_type)} types")
    print("  by era: " + ", ".join(f"{e} {by_era[e]}" for e, _ in ERAS) + f", other {by_era['other']}")
    print("  top types: " + ", ".join(f"{t} {n}" for t, n in by_type.most_common(12)))
    if stacks:
        (x, y), n = stacks.most_common(1)[0]
        print(f"  largest stack: {n} units at ({x},{y}); players with most units: "
              + ", ".join(f"{p} {n}" for p, n in by_player.most_common(3)))
    return by_type

def log_summary(path):
    attacks = collections.Counter(); lost = collections.Counter(); cities = 0; eras = collections.Counter()
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"FC45COMBAT turn (\d+) (.+?) (ok|failed) (.+?) of ", line)
            if m and m.group(3) == "ok":
                attacks[m.group(4)] += 1
                eras[ERA_OF.get(m.group(4), "other")] += 1
                continue
            m = re.search(r"FC45LOST turn \d+ (.+?) of .+ reason (\S+)", line)
            if m:
                lost[(m.group(1), m.group(2))] += 1
                continue
            if "FC45CITY" in line:
                cities += 1
    print(f"{path}: {sum(attacks.values())} attack-type actions, {sum(lost.values())} units lost, {cities} city changes")
    print("  attacks by era: " + ", ".join(f"{e} {eras[e]}" for e, _ in ERAS) + f", other {eras['other']}")
    print("  attackers: " + ", ".join(f"{t} {n}" for t, n in attacks.most_common(12)))
    killed = collections.Counter()
    for (t, r), n in lost.items():
        if r == "killed":
            killed[t] += n
    print("  killed in combat: " + ", ".join(f"{t} {n}" for t, n in killed.most_common(12)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__ or "usage: civ45-roster-summary.py [<autogame.log>] <save.sav.gz>..."); sys.exit(2)
    for p in sys.argv[1:]:
        if p.endswith(".log"):
            log_summary(p)
        else:
            save_summary(p)
