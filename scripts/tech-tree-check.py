#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Check the Freeciv45 tech tree design against the roster design and a buildings.ruleset.

Usage: scripts/tech-tree-check.py [--fill] [--buildings PATH] [--units PATH] [TREE.md]

Reads the "| Name | Era | Req 1 | Req 2 | Tier | Unlocks |" tables of notes/freeciv45/design/tech-tree.md
and checks: every prerequisite exists and sits in the same or an earlier era; no cycles; the tier of each
tech (Freeciv's num_reqs: the techs it needs, counted recursively, itself excluded; common/tech.c:230-243);
every unit in units-and-upgrades.md has its tech in the tree; every building in buildings.ruleset has its
tech in the tree or in the tree document's "re-homed" table; no tech is an orphan (unlocks nothing and
nothing needs it). --fill rewrites the Tier column of the tree document in place. Exit 1 on any finding.
"""
import re
import sys

ERAS = ["I", "II", "III", "IV", "V", "VI", "VII"]


def md_tables(text, header_start):
    rows = []
    in_table = False
    for line in text.splitlines():
        if line.startswith(header_start):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
        else:
            in_table = False
    return rows


def main():
    args = sys.argv[1:]
    fill = "--fill" in args
    args = [a for a in args if a != "--fill"]
    buildings = units = None
    tree_path = "notes/freeciv45/design/tech-tree.md"
    while args:
        a = args.pop(0)
        if a == "--buildings":
            buildings = args.pop(0)
        elif a == "--units":
            units = args.pop(0)
        else:
            tree_path = a
    units = units or "notes/freeciv45/design/units-and-upgrades.md"
    text = open(tree_path).read()
    rows = md_tables(text, "| Name | Era | Req 1 | Req 2 | Tier | Unlocks |")
    tree = {}
    findings = []
    for name, era, r1, r2, tier, unlocks in rows:
        name = name.replace("†", "").strip()
        reqs = [r.replace("†", "").strip() for r in (r1, r2) if r.strip().lower() != "none"]
        if name in tree:
            findings.append(f"duplicate tech {name}")
        tree[name] = {"era": era, "reqs": reqs, "unlocks": unlocks, "tier": tier}
    print(f"techs: {len(tree)}")
    for era in ERAS:
        n = sum(1 for t in tree.values() if t["era"] == era)
        print(f"  era {era}: {n}")
    # prerequisites exist, era order
    for name, t in tree.items():
        if t["era"] not in ERAS:
            findings.append(f"{name}: bad era {t['era']}")
            continue
        for r in t["reqs"]:
            if r not in tree:
                findings.append(f"{name}: prerequisite {r} is not in the tree")
            elif ERAS.index(tree[r]["era"]) > ERAS.index(t["era"]):
                findings.append(f"{name} ({t['era']}): prerequisite {r} is in a later era ({tree[r]['era']})")
    # cycles and tiers
    tiers = {}

    def ancestors(name, stack):
        if name in stack:
            findings.append(f"cycle through {name}")
            return set()
        if name in tiers:
            return tiers[name]
        out = set()
        for r in tree.get(name, {"reqs": []})["reqs"]:
            if r in tree:
                out.add(r)
                out |= ancestors(r, stack + [name])
        tiers[name] = out
        return out

    for name in tree:
        ancestors(name, [])
    num_reqs = {n: len(a) for n, a in tiers.items()}
    rehome = {}
    for old, new, what in md_tables(text, "| Old tech | New tech | Buildings moved |"):
        rehome[old.replace("†", "").strip()] = new.replace("†", "").strip()
    # units
    utext = open(units).read()
    urows = md_tables(utext, "| Name | Class [flag] | Tech |")
    unit_techs = {}
    for cells in urows:
        uname, tech = cells[0], cells[2]
        primary = tech.replace("†", "").split("+")[0].strip()
        unit_techs[uname] = primary
        if primary.lower() == "none":
            continue
        if primary not in tree and rehome.get(primary) not in tree:
            findings.append(f"unit {uname}: tech {primary} is not in the tree and not re-homed")
    print(f"units read from roster: {len(unit_techs)}")
    # buildings
    building_techs = {}
    if buildings:
        btext = open(buildings).read()
        for m in re.finditer(r"\[building_[^\]]+\]\n(.*?)(?=\n\[|\Z)", btext, re.S):
            body = m.group(1)
            bname = re.search(r'^name\s*=\s*_\("([^"]+)"\)', body, re.M)
            reqs_block = re.search(r"^reqs\s*=\s*(.*?)(?=^\w+\s*=|\Z)", body, re.M | re.S)
            techs = re.findall(r'"Tech",\s*"([^"]+)"', reqs_block.group(1)) if reqs_block else []
            building_techs[bname.group(1)] = techs
        print(f"buildings read: {len(building_techs)}")
        for b, techs in building_techs.items():
            if not techs:
                print(f"  no tech (allowed): {b}")
            elif len(techs) > 1:
                findings.append(f"building {b}: {len(techs)} tech reqs")
            else:
                t = rehome.get(techs[0], techs[0])
                if t not in tree:
                    findings.append(f"building {b}: tech {techs[0]} is not in the tree and not re-homed")
    # orphans
    needed = set()
    for t in tree.values():
        needed.update(t["reqs"])
    for name, t in tree.items():
        unlocks = t["unlocks"].strip()
        if (unlocks == "" or unlocks.startswith("(prereq")) and name not in needed:
            findings.append(f"orphan tech {name}: unlocks nothing and nothing needs it")
    roots = [n for n, t in tree.items() if not t["reqs"]]
    print(f"root techs: {len(roots)}: {', '.join(sorted(roots))}")
    # fill tiers
    if fill:
        out = []
        for line in text.splitlines():
            m = re.match(r"^\| ([^|]+) \| (I{1,3}|IV|V|VI|VII) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| (.*) \|$", line)
            if m and m.group(1).replace("†", "").strip() in tree:
                n = m.group(1).replace("†", "").strip()
                line = f"| {m.group(1)} | {m.group(2)} | {m.group(3)} | {m.group(4)} | {num_reqs[n]} | {m.group(6)} |"
            out.append(line)
        open(tree_path, "w").write("\n".join(out) + "\n")
        print("tiers written")
    else:
        for name, t in tree.items():
            if t["tier"].strip() != str(num_reqs[name]):
                findings.append(f"{name}: tier column says {t['tier']}, num_reqs is {num_reqs[name]}")
    mx = max(num_reqs.values()) if num_reqs else 0
    print(f"deepest tier: {mx}")
    for f in findings:
        print("FINDING:", f)
    print("result:", "FAIL" if findings else "PASS")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
