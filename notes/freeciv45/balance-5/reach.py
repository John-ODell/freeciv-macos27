# SPDX-License-Identifier: GPL-2.0-or-later
# reach.py <run log>...: how close each night-5 game came to each win, read from its saves.
# - domination: per save (every 25 turns and the last), each civ's share of the land tiles (t rows: every letter
#   but ocean " ", deep ocean ":" and lake "+") it owns (owner rows) and of all citizens ([scoreN] happy + content +
#   unhappy + angry + specialists); the best civ by min(land/60, pop/50), the script's two bars (script.lua:539-540).
# - culture: the leader's culture at the last save and its lead over the second (bars: 50000 and 25 %).
# - alliance: the biggest group of civs all allied to each other at the last save (diplstate current "Alliance").
# - conquest: civs alive at the last save; cities that changed hands (FC45CITY lines of the combat observer).
# - space: Space Flight's first turn, and spaceship parts at the last save.
import glob, gzip, itertools, os, re, sys

FCM = os.path.expanduser("~/Desktop/freeciv-port/port/fcm")
SKIP = ("Barbarian", "Pirate", "Animal Kingdom")

def read(path):
    rows_t, rows_o = {}, {}; pl = {}; cur = None; kind = None; dipl = None
    for line in gzip.open(path, "rt", encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"\[(player|score)(\d+)\]$", line)
        if m: kind, cur = m.group(1), int(m.group(2)); pl.setdefault(cur, {"dipl": []}); dipl = None; continue
        if line.startswith("["): kind = None; dipl = None; continue
        m = re.match(r"(t|owner)(\d{4})=\"(.*)\"$", line)
        if m and kind is None:
            (rows_t if m.group(1) == "t" else rows_o)[int(m.group(2))] = m.group(3); continue
        if kind == "player":
            if line.startswith("diplstate={"): dipl = []; continue
            if dipl is not None:
                if line.startswith("}"): pl[cur]["dipl"] = dipl; dipl = None
                else: dipl.append(line.split(",")[0].strip("\""))
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                if k in ("name", "nation", "is_alive"): pl[cur][k] = v.strip('"')
                if k.startswith("spaceship.") and k[10:] in ("structurals", "components", "modules"): pl[cur][k[10:]] = int(v)
        if kind == "score" and "=" in line:
            k, v = line.split("=", 1)
            if k in ("happy", "content", "unhappy", "angry", "specialists0", "specialists1", "specialists2"):
                pl[cur]["pop"] = pl[cur].get("pop", 0) + int(v)
            if k == "culture": pl[cur]["culture"] = int(v)
    land = 0; owned = {}
    for y, row in rows_t.items():
        own = rows_o.get(y, "").split(",")
        for x, ch in enumerate(row):
            if ch in " :+": continue
            land += 1
            if x < len(own) and own[x] not in ("-", ""): owned[int(own[x])] = owned.get(int(own[x]), 0) + 1
    civs = {i: p for i, p in pl.items() if p.get("nation") not in SKIP and "name" in p}
    return land, owned, civs

for path in sys.argv[1:]:
    text = open(path, errors="replace").read()
    folder = os.path.join(FCM, re.search(r"logs/test-[^ )\n]+", text).group(0))
    saves = sorted(glob.glob(folder + "/freeciv-T*.sav.gz"))
    turns = {int(re.search(r"-T(\d+)-", s).group(1)): s for s in saves}
    pick = [t for t in sorted(turns) if t % 25 == 0] + [max(turns)]
    best = (0, None, None, 0, 0)
    for t in pick:
        land, owned, civs = read(turns[t])
        pops = sum(p.get("pop", 0) for p in civs.values() if p.get("is_alive") == "TRUE") or 1
        for i, p in civs.items():
            lp, pp = 100 * owned.get(i, 0) / land, 100 * p.get("pop", 0) / pops
            r = min(lp / 60, pp / 50)
            if r > best[0]: best = (r, t, p["name"], lp, pp)
    last_t = max(turns); land, owned, civs = read(turns[last_t])
    alive = [p for p in civs.values() if p.get("is_alive") == "TRUE"]
    cult = sorted((p.get("culture", 0), p["name"]) for p in alive)[::-1]
    lead = 100 * (cult[0][0] - cult[1][0]) / cult[1][0] if len(cult) > 1 and cult[1][0] else 0
    idx = [i for i, p in civs.items() if p.get("is_alive") == "TRUE"]
    big = 1
    for n in range(len(idx), 1, -1):
        if any(all(len(civs[a]["dipl"]) > b and civs[a]["dipl"][b] == "Alliance" for a, b in itertools.permutations(g, 2))
               for g in itertools.combinations(idx, n)):
            big = n; break
    log = open(folder + "/autogame.log", errors="replace").read()
    moves = re.findall(r"FC45CITY turn \d+ .+? from .+? to .+? reason (\S+)", log)
    sf = re.findall(r"FC45TECH turn (\d+) .+? learned Space Flight", log)
    parts = ["%s %d/%d/%d" % (p["name"], p.get("structurals", 0), p.get("components", 0), p.get("modules", 0))
             for p in civs.values() if p.get("structurals")]
    print("## %s (last save T%d)" % (os.path.basename(path)[:-4], last_t))
    print("- domination: closest %s at T%s, land %.1f %% (bar 60), people %.1f %% (bar 50), %.0f %% of the way"
          % (best[2], best[1], best[3], best[4], 100 * best[0]))
    print("- culture: %s %d, %.0f %% ahead of %s %d" % (cult[0][1], cult[0][0], lead, cult[1][1], cult[1][0]))
    print("- alliance: biggest all-allied group %d of %d alive civs" % (big, len(alive)))
    print("- conquest: %d of %d civs alive; cities changed hands %d times (%s)"
          % (len(alive), len(civs), len(moves), ", ".join("%s %d" % (k, moves.count(k)) for k in sorted(set(moves))) or "-"))
    print("- space: Space Flight first at %s; parts (structurals/components/modules): %s"
          % ("T" + sf[0] if sf else "never", "; ".join(parts) or "none"))
