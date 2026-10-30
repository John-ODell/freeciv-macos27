# SPDX-License-Identifier: GPL-2.0-or-later
# summary.py <run log>...: for each night-5 game, how it ended, the start map, and how the bonuses split between
# the civs. Reads the test log (for the log folder and the result line), the autogame log (FC45START, FC45MAP,
# FC45WONDER, FC45GP, FC45REL lines) and the last save's [playerN]/[scoreN] sections.
import collections, glob, gzip, os, re, sys

FCM = os.path.expanduser("~/Desktop/freeciv-port/port/fcm")

def save_scores(folder):
    fs = sorted(glob.glob(folder + "/freeciv-T*.sav.gz"))
    if not fs: return None, {}
    last = fs[-1]; turn = int(re.search(r"-T(\d+)-", last).group(1))
    players = {}; cur = None; kind = None
    for line in gzip.open(last, "rt", encoding="utf-8", errors="replace"):
        m = re.match(r"\[(player|score)(\d+)\]", line)
        if m: kind, cur = m.group(1), int(m.group(2)); players.setdefault(cur, {}); continue
        if line.startswith("["): kind = None; continue
        if kind and "=" in line:
            k, v = line.rstrip("\n").split("=", 1)
            if kind == "player" and k in ("name", "nation", "is_alive"): players[cur][k] = v.strip('"')
            if kind == "score" and k in ("total", "culture", "techs", "cities", "wonders", "spaceship", "landarea"):
                players[cur][k] = int(v)
    return turn, {p["name"]: p for p in players.values() if "name" in p and p.get("nation") not in ("Barbarian", "Pirate", "Animal Kingdom")}

def shares(counter, names):
    tot = sum(counter.values())
    if not tot: return "none"
    top = counter.most_common(1)[0]
    return "%d, top %s %d (%d %%), %d of %d civs got any" % (tot, top[0], top[1], round(100 * top[1] / tot),
                                                           len([n for n in names if counter[n]]), len(names))

for path in sys.argv[1:]:
    text = open(path, errors="replace").read()
    m = re.search(r"logs/test-[^ )\n]+", text)
    if not m: print("##", path, "no log folder"); continue
    folder = os.path.join(FCM, m.group(0)); log = open(folder + "/autogame.log", errors="replace").read()
    result = (re.findall(r"^autogame: .*$", text, re.M) or ["?"])[0]
    turn, players = save_scores(folder)
    names = sorted(players)
    starts = dict(re.findall(r"FC45START (.+?) \| .+? \| continent \d+ of (\d+) tiles", log))
    mapline = (re.findall(r"FC45MAP (.*)", log) or ["?"])[0]
    wonders = collections.Counter(re.findall(r"FC45WONDER turn \d+ .+? by (.+?) in ", log))
    if not wonders: wonders = collections.Counter({n: p.get("wonders", 0) for n, p in players.items()})  # held at the end
    gp = collections.Counter(re.findall(r"FC45GP turn \d+ born Great \w+ of (.+?) in ", log))
    ages = collections.Counter(re.findall(r"FC45GP turn \d+ golden age \d+ of (.+?) begins", log))
    faiths = collections.Counter(re.findall(r"FC45REL turn \d+ [A-Za-z ]+? founded in .+? of (.+)", log))
    print("## %s\n%s\nmap: %s\nlast save T%s" % (os.path.basename(path)[:-4], result, mapline, turn))
    print("wonders: %s\ngreat people: %s\ngolden ages: %s\nfaiths founded: %s" %
          (shares(wonders, names), shares(gp, names), shares(ages, names), shares(faiths, names)))
    rows = sorted(players.values(), key=lambda p: -p.get("total", 0))
    print("| rank | leader | nation | alive | score | culture | techs | cities | start land | wonders | GP | ages | faiths |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, p in enumerate(rows, 1):
        n = p["name"]
        print("| %d | %s | %s | %s | %d | %d | %d | %d | %s | %d | %d | %d | %d |" % (
            i, n, p.get("nation", "?"), "yes" if p.get("is_alive") == "TRUE" else "no", p.get("total", 0),
            p.get("culture", 0), p.get("techs", 1) - 1, p.get("cities", 0), starts.get(n, "?"),
            wonders[n], gp[n], ages[n], faiths[n]))
    print()
