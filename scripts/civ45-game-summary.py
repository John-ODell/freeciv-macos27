#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read Freeciv45 (civ45) autogame saves for the AI's armies, its wars and its empires.

Usage: scripts/civ45-game-summary.py --ruleset DIR [--every N] SAVE[.gz]...

DIR is the civ45 data directory the game ran on (for each unit type's attack, defence and flags). With
--every N only saves whose turn is a multiple of N are read (default 25), plus the last one given.

Per save it prints one line: the turn; the civs alive (barbarians and animals left out); their cities and
citizens; their military units (attack above 0 and no NonMil flag) and how many stand outside cities; the
largest military stack outside a city and the next two, with their owners; how many field tiles hold 3 or more
and 6 or more military units of one owner; how many of those stand next to a foreign city; and the pairs of civs
at war, in a ceasefire or armistice, at peace, and allied. A stack is military units of one owner on one tile,
not inside a transport and not on a city tile.
"""
import csv, gzip, os, re, sys
from collections import Counter, defaultdict

def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def sections(lines):
    """Yield (section, {key: value}, {table: (header, rows)})."""
    sect, kv, tabs = None, {}, {}
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("[") and ln.endswith("]"):
            if sect is not None: yield sect, kv, tabs
            sect, kv, tabs = ln[1:-1], {}, {}
        elif "={" in ln and ln.split("={", 1)[0].isidentifier():
            key = ln.split("={", 1)[0]
            header = next(csv.reader([ln[len(key) + 2:]]))
            rows = []; i += 1
            while i < len(lines) and not lines[i].startswith("}"):
                if lines[i].strip(): rows.append(next(csv.reader([lines[i]])))
                i += 1
            tabs[key] = (header, rows)
        elif "=" in ln:
            k, v = ln.split("=", 1)
            kv[k] = v.strip('"')
        i += 1
    if sect is not None: yield sect, kv, tabs

def unit_types(rsdir):
    """Unit type rule name -> (attack, defense, flags)."""
    text = open(os.path.join(rsdir, "units.ruleset"), encoding="utf-8").read()
    out = {}
    for sect in re.split(r"(?m)^(?=\[unit_)", text):
        if not sect.startswith("[unit_"): continue
        name = re.search(r'(?m)^name\s*=\s*_?\(?"([^"]+)"', sect)
        rule = re.search(r'(?m)^rule_name\s*=\s*"([^"]+)"', sect)
        att = re.search(r'(?m)^attack\s*=\s*(\d+)', sect)
        dfn = re.search(r'(?m)^defense\s*=\s*(\d+)', sect)
        fl = re.search(r'(?ms)^flags\s*=\s*(.*?)(?=^\w)', sect)
        key = rule.group(1) if rule else (name.group(1) if name else None)
        if key:
            out[key] = (int(att.group(1)) if att else 0, int(dfn.group(1)) if dfn else 0,
                        set(re.findall(r'"([^"]+)"', fl.group(1))) if fl else set())
    return out

def summarize(path, utypes):
    lines = load(path)
    turn = None; players = {}; cities = {}; units = []
    for sect, kv, tabs in sections(lines):
        if sect == "game" and "turn" in kv and turn is None:
            turn = int(kv["turn"])
        m = re.fullmatch(r"player(\d+)", sect or "")
        if not m: continue
        pid = int(m.group(1))
        civ = kv.get("is_alive") == "TRUE" and kv.get("nation") not in ("Barbarian", "Pirate", "Animal Kingdom")
        dipl = [r[0] for r in tabs.get("diplstate", ([], []))[1]]
        players[pid] = {"name": kv.get("name", "?"), "civ": civ, "dipl": dipl, "nation": kv.get("nation", "")}
        if "c" in tabs:
            h, rows = tabs["c"]
            for r in rows:
                cities[(int(r[h.index("x")]), int(r[h.index("y")]))] = (pid, int(r[h.index("size")]))
        if "u" in tabs:
            h, rows = tabs["u"]
            for r in rows:
                units.append((pid, r[h.index("type_by_name")], int(r[h.index("x")]), int(r[h.index("y")]),
                              r[h.index("transported_by")] != "-1"))
    civs = [p for p, v in players.items() if v["civ"]]
    ncity = sum(1 for (p, s) in cities.values() if p in civs)
    pop = sum(s for (p, s) in cities.values() if p in civs)
    mil = 0; field_mil = 0; stacks = Counter()
    for pid, ut, x, y, carried in units:
        if pid not in civs: continue
        a, d, fl = utypes.get(ut, (0, 0, set()))
        if a <= 0 or "NonMil" in fl: continue
        mil += 1
        if carried or (x, y) in cities: continue
        field_mil += 1; stacks[(pid, x, y)] += 1
    top = stacks.most_common(3)
    big3 = [k for k, n in stacks.items() if n >= 3]; big6 = [k for k, n in stacks.items() if n >= 6]
    def near_foreign_city(k):
        pid, x, y = k
        return any((x + dx, y + dy) in cities and cities[(x + dx, y + dy)][0] != pid
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    at_city = sum(1 for k in big3 if near_foreign_city(k))
    pairs = Counter()
    for i in civs:
        for j in civs:
            if j <= i: continue
            d = players[i]["dipl"]
            s = d[j] if j < len(d) else "?"
            pairs[s] += 1
    tops = ", ".join(f"{n} ({players[p]['name']})" for (p, x, y), n in top) or "-"
    return (f"T{turn}: civs {len(civs)}, cities {ncity}, citizens {pop}; military {mil}, in the field {field_mil}; "
            f"largest field stacks {tops}; stacks of 3+ {len(big3)} (next to a foreign city {at_city}), 6+ {len(big6)}; "
            f"pairs: " + ", ".join(f"{k} {v}" for k, v in sorted(pairs.items())))

def turn_of(path):
    m = re.search(r"-T(\d+)-", os.path.basename(path))
    return int(m.group(1)) if m else -1

if __name__ == "__main__":
    args = sys.argv[1:]; rsdir = None; every = 25
    while args[:1] in (["--ruleset"], ["--every"]):
        if args[0] == "--ruleset": rsdir = args[1]
        else: every = int(args[1])
        args = args[2:]
    if not args or rsdir is None: print(__doc__); sys.exit(2)
    utypes = unit_types(rsdir)
    paths = sorted(args, key=turn_of)
    pick = [p for p in paths if turn_of(p) % every == 0]
    if paths[-1] not in pick: pick.append(paths[-1])
    for p in pick:
        print(summarize(p, utypes))
