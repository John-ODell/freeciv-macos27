# SPDX-License-Identifier: GPL-2.0-or-later
# start.py <run log> <turn>...: each civ's start (its first city in the T1 save, or else its Settlers), the terrain within 3 tiles of it
# (real distance, so a 7 x 7 square), and the land tiles it owns at each given turn.
import glob, gzip, os, re, sys
FCM = os.path.expanduser("~/Desktop/freeciv-port/port/fcm")
def load(path):
    t, o, pl, cur, kind, units = {}, {}, {}, None, None, False
    for line in gzip.open(path, "rt", encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"\[player(\d+)\]$", line)
        if m: cur = int(m.group(1)); pl[cur] = {}; kind = "p"; continue
        if line.startswith("["): kind = None; continue
        m = re.match(r"(t|owner)(\d{4})=\"(.*)\"$", line)
        if m and kind is None: (t if m.group(1) == "t" else o)[int(m.group(2))] = m.group(3); continue
        if kind == "p":
            if line.startswith("name="): pl[cur]["name"] = line[5:].strip('"')
            if line.startswith("nation="): pl[cur]["nation"] = line[7:].strip('"')
            if line.startswith("c={"): units = "c"; continue
            if line.startswith("u={"): units = "u"; continue
            if line.startswith("}"): units = False; continue
            if units == "c" and "xy" not in pl[cur] and re.match(r"-?\d+,-?\d+,", line):       # c: y, x, ...
                y, x = line.split(",")[:2]; pl[cur]["xy"] = (int(x), int(y))
            if units == "u" and "xy" not in pl[cur] and '"Settlers"' in line:                   # u: id, x, y, ...
                x, y = line.split(",")[1:3]; pl[cur]["xy"] = (int(x), int(y))
    return t, o, pl
text = open(sys.argv[1], errors="replace").read()
folder = os.path.join(FCM, re.search(r"logs/test-[^ )\n]+", text).group(0))
t, o, pl = load(glob.glob(folder + "/freeciv-T0001-*.sav.gz")[0])
H, W = len(t), len(t[0])
owned = {}
for turn in sys.argv[2:]:
    f = glob.glob(folder + "/freeciv-T%04d-*.sav.gz" % int(turn))
    if not f: continue
    tt, oo, _ = load(f[0]); c = {}
    for y, row in tt.items():
        own = oo[y].split(",")
        for x, ch in enumerate(row):
            if ch not in " :+" and own[x] != "-": c[int(own[x])] = c.get(int(own[x]), 0) + 1
    owned[turn] = c
print("| civ | start | grass+plains | hills | forest+jungle | desert+tundra+glacier+swamp | mountains | water |" + "".join(" land T%s |" % k for k in owned))
print("|---|---|---|---|---|---|---|---|" + "---|" * len(owned))
for i, p in sorted(pl.items()):
    if "xy" not in p or p.get("nation") in ("Barbarian", "Pirate", "Animal Kingdom"): continue
    x0, y0 = p["xy"]; n = {}
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            y, x = y0 + dy, (x0 + dx) % W
            if 0 <= y < H: ch = t[y][x]; n[ch] = n.get(ch, 0) + 1
    g = lambda s: sum(n.get(ch, 0) for ch in s)
    print("| %s | %d,%d | %d | %d | %d | %d | %d | %d |" % (p["name"], x0, y0, g("gp"), g("h"), g("fj"), g("dtas"), g("m"), g(" :+"))
          + "".join(" %d |" % owned[k].get(i, 0) for k in owned))
