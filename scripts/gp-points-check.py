#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# The great-person point numbers live twice in civ45: as User_Effect_3 rows in effects.ruleset (the server
# adds them up) and in script.lua's fc45_gp_sources table (Lua draws the kind from them). This diffs the two.
# Usage: scripts/gp-points-check.py port/freeciv/data/civ45   (exit 0 when they match)
import re, sys, pathlib

d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "port/freeciv/data/civ45")
effects = {}
text = (d / "effects.ruleset").read_text()
for m in re.finditer(r'\[effect_gp_points_[^\]]+\]\ntype\s*=\s*"User_Effect_3"\nvalue\s*=\s*(\d+)\nreqs\s*=\n\s*\{[^}]*?"Building",\s*"([^"]+)",\s*"City"', text):
    effects[m.group(2)] = int(m.group(1))
lua = {}
script = (d / "script.lua").read_text()
block = re.search(r"fc45_gp_sources = \{\n(.*?)\n\}", script, re.S)
for m in re.finditer(r'\["([^"]+)"\]\s*=\s*\{\s*"[A-Za-z]+",\s*(\d+)\s*\}', block.group(1) if block else ""):
    lua[m.group(1)] = int(m.group(2))
bad = False
for name in sorted(set(effects) | set(lua)):
    if effects.get(name) != lua.get(name):
        print(f"{name}: effects.ruleset {effects.get(name)}, script.lua {lua.get(name)}")
        bad = True
print(f"{len(effects)} User_Effect_3 rows, {len(lua)} script.lua sources, {'DIFFER' if bad else 'match'}")
sys.exit(1 if bad or not effects else 0)
