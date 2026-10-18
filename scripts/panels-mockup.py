#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Draws notes/freeciv45/ui/panels-mockup.svg for panels.md: two 1440 x 900 frames at 1x, "Map view" and "City view".
# Usage: scripts/panels-mockup.py notes/freeciv45/ui/panels-mockup.svg
import sys

W, H, GAP = 1440, 900, 40
TOP = 32          # top strip height
COL = 64          # right-edge column width
MAPR = W - COL    # map's right edge

out = []
def a(s): out.append(s)

def text(x, y, s, size=11, fill="#c9d1d9", anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{w}>{s}</text>')

def box(x, y, w, h, fill="#141a21", op="0.94", stroke="#2b3441", rx=6):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}"/>')

def note(x, y, s, anchor="start"):
    text(x, y, s, size=9, fill="#6b7480", anchor=anchor)

def top_strip(oy):
    a('<g id="top_strip">' if oy == 0 else '<g>')
    a(f'<rect x="0" y="{oy+30}" width="{W}" height="{TOP}" fill="#141a21" stroke="#2b3441"/>')
    items = [(16, "research: Bronze Working  +4 bulbs, 6 t"), (300, "gold 123 (+5)"), (420, "tax 40 / lux 0 / sci 60"),
             (600, "culture 210 (+3)"), (760, "(strategic resources, later slice)")]
    for x, s in items:
        text(x, oy + 51, s, size=12, fill="#e6edf3" if "later" not in s else "#6b7480")
    text(W - 100, oy + 51, "3500 BCE  T:12", size=12, fill="#e6edf3", anchor="end")
    a(f'<rect x="{W-90}" y="{oy+36}" width="26" height="20" rx="3" fill="#2b3441"/>')
    text(W - 77, oy + 51, "≡", size=13, fill="#e6edf3", anchor="middle")
    a('</g>')

def edge_column(oy, badges=True):
    a('<g id="edge_column">' if oy == 0 else '<g>')
    x0, y0 = MAPR, oy + 30 + TOP
    a(f'<rect x="{x0}" y="{y0}" width="{COL}" height="{H-30-TOP}" fill="#141a21" stroke="#2b3441"/>')
    cx = x0 + COL // 2
    for i, s in enumerate(["res", "dip", "cty", "unt", "eco", "≡"]):
        cy = y0 + 34 + i * 54
        a(f'<circle cx="{cx}" cy="{cy}" r="22" fill="#1c2531" stroke="#3a4350"/>')
        text(cx, cy + 4, s, size=11, fill="#e6edf3", anchor="middle")
    note(cx, y0 + 34 + 6 * 54 - 10, "overviews", anchor="middle")
    if badges:
        by = y0 + 34 + 6 * 54 + 30
        for i, (s, col) in enumerate([("city", "#f2b632"), ("war", "#c23b3b"), ("dipl", "#3a7bd5"), ("+2", "#2b3441")]):
            cy = by + i * 46
            a(f'<circle cx="{cx}" cy="{cy}" r="18" fill="{col}" stroke="#e6edf3" stroke-width="1"/>')
            text(cx, cy + 4, s, size=9, fill="#101418", anchor="middle", weight="bold")
            if i < 3:
                a(f'<circle cx="{cx+13}" cy="{cy-13}" r="6" fill="#ffffff"/>')
                text(cx + 13, cy - 10, "!", size=9, fill="#c23b3b", anchor="middle", weight="bold")
        note(cx, by + 4 * 46 - 6, "badges", anchor="middle")
    a('</g>')

def map_base(oy):
    a(f'<rect x="0" y="{oy+30+TOP}" width="{MAPR}" height="{H-30-TOP}" fill="url(#sea)"/>')
    a(f'<rect x="336" y="{oy+158}" width="720" height="528" fill="url(#grid)"/>')
    a(f'<rect x="1056" y="{oy+302}" width="192" height="240" fill="url(#grid)"/>')
    a(f'<rect x="192" y="{oy+398}" width="144" height="192" fill="url(#grid)"/>')

def frame_title(oy, s):
    a(f'<rect x="0" y="{oy}" width="{W}" height="{H}" fill="#101418"/>')
    text(12, oy + 20, s, size=13, fill="#9aa3ad")

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{2*H+GAP}" viewBox="0 0 {W} {2*H+GAP}" font-family="Helvetica, Arial, sans-serif">')
a('<!-- Freeciv45 panel mockup, drawn for notes/freeciv45/ui/panels.md (revised 2026-10-17, issue 118). 1x sizes in px. Our own layout; nothing traced from any game. GPL-2.0-or-later. -->')
a('<defs>')
a('<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><rect width="48" height="48" fill="#3f6b3a"/><path d="M48 0H0V48" fill="none" stroke="#365e32" stroke-width="1"/></pattern>')
a('<pattern id="sea" width="48" height="48" patternUnits="userSpaceOnUse"><rect width="48" height="48" fill="#1f3f6e"/><path d="M48 0H0V48" fill="none" stroke="#1a3760" stroke-width="1"/></pattern>')
a('</defs>')
a(f'<rect x="0" y="0" width="{W}" height="{2*H+GAP}" fill="#0a0d10"/>')

# ======================= frame 1: map view =======================
oy = 0
frame_title(oy, "Map view, 1x: window 1440 x 900; top strip 32 px, right-edge column 64 px; the left sidebar is gone while the switch is on")
map_base(oy)
top_strip(oy)
edge_column(oy)

# a city on the map, closed
a('<g id="city_marker">')
a(f'<rect x="528" y="{oy+350}" width="48" height="48" fill="#8a7b5a"/>')
a(f'<rect x="496" y="{oy+402}" width="112" height="16" rx="3" fill="#0b0f14" fill-opacity="0.8"/>')
text(552, oy + 414, "Lookton", size=11, fill="#e6edf3", anchor="middle")
a(f'<circle cx="552" cy="{oy+374}" r="14" fill="#f2b632" stroke="#fff3c4" stroke-width="2"/>')
text(552, oy + 379, "4", size=13, fill="#1a1a1a", anchor="middle", weight="bold")
text(576, oy + 380, "city_marker: a click opens the city view (frame 2)", size=10, fill="#fff3c4")
a('</g>')

# selected unit and an enemy stack with the odds tooltip
a(f'<rect x="672" y="{oy+446}" width="48" height="48" fill="none" stroke="#ffffff" stroke-width="2"/>')
a(f'<rect x="684" y="{oy+454}" width="24" height="30" rx="3" fill="#3a7bd5"/>')
a(f'<rect x="816" y="{oy+446}" width="48" height="48" fill="#6b3f3a"/>')
a(f'<rect x="828" y="{oy+454}" width="24" height="30" rx="3" fill="#c23b3b"/>')
a('<g id="odds_tooltip">')
box(872, oy + 412, 252, 92, fill="#0b0f14", stroke="#3a4350", rx=4)
text(882, oy + 432, "Attack Warriors (fortified, hills)", size=12, fill="#e6edf3", weight="bold")
a(f'<rect x="882" y="{oy+440}" width="232" height="10" fill="#7a2626"/><rect x="882" y="{oy+440}" width="158" height="10" fill="#2e8b57"/>')
text(882, oy + 466, "Chance to win: A: 68%   D: 32%", size=11)
text(882, oy + 482, "A 1 x FP1 HP 10/10  vs  D 1.5 x FP1 HP 8/10", size=11)
note(882, oy + 498, "odds tooltip at the cursor (plan row Q2)")
a('</g>')

# chat stays bottom left
box(8, oy + 690, 300, 200, fill="#0b0f14", op="0.7", stroke="#2b3441", rx=4)
text(18, oy + 710, "info_tab: chat and the message log (kept)", size=10, fill="#8b949e")

# unit bar, bottom centre
ux, uy = 328, oy + 786
a('<g id="unit_bar">')
box(ux, uy, 720, 104)
note(ux + 4, uy - 6, "unit_bar: 720 x 104 at 1x, bottom centre, hidden when nothing is selected or a city is open")
a(f'<rect x="{ux+12}" y="{uy+12}" width="80" height="80" rx="4" fill="#1c2531"/>')
a(f'<rect x="{ux+32}" y="{uy+22}" width="40" height="52" rx="4" fill="#3a7bd5"/>')
a(f'<rect x="{ux+16}" y="{uy+80}" width="72" height="6" fill="#222"/><rect x="{ux+16}" y="{uy+80}" width="58" height="6" fill="#4caf50"/>')
for i in range(2):  # veteran badges
    a(f'<circle cx="{ux+100}" cy="{uy+20+i*14}" r="5" fill="#ffd54a" stroke="#141a21"/>')
note(ux + 96, uy + 106, "vet badges", anchor="middle")
text(ux + 120, uy + 28, "‹", size=18, fill="#e6edf3")
text(ux + 138, uy + 28, "Warriors", size=15, fill="#e6edf3", weight="bold")
text(ux + 214, uy + 28, "›", size=18, fill="#e6edf3")
text(ux + 228, uy + 28, "W", size=9, fill="#ffd54a")
note(ux + 120, uy + 40, "‹ › previous / next unit needing orders: 3 need orders")
text(ux + 120, uy + 58, "(Lookton)", size=11)
text(ux + 120, uy + 76, "str 1 / 1   moves 1 of 1   hp 8/10", size=12, fill="#e6edf3")
text(ux + 120, uy + 92, "fortified, upkeep 1 shield", size=10, fill="#8b949e")
for i, col in enumerate(["#3a7bd5", "#3a7bd5", "#8a7b5a"]):
    st = ' stroke="#ffffff" stroke-width="2"' if i == 0 else ""
    a(f'<rect x="{ux+390+i*36}" y="{uy+12}" width="30" height="30" rx="4" fill="{col}"{st}/>')
a(f'<rect x="{ux+498}" y="{uy+12}" width="30" height="30" rx="4" fill="#2b3441"/>')
text(ux + 513, uy + 32, "+2", size=10, fill="#e6edf3", anchor="middle")
acts = [("go", "G"), ("fort", "F"), ("sntr", "S"), ("bld", "B"), ("pil", "⇧P"), ("upg", "⇧U"), ("dis", "⇧D"), ("skip", "W"), ("done", "␣")]
for i, (s, k) in enumerate(acts):
    x = ux + 330 + i * 42
    fill = "#2e8b57" if s == "done" else "#1c2531"
    a(f'<rect x="{x}" y="{uy+56}" width="36" height="36" rx="4" fill="{fill}" stroke="#2b3441"/>')
    text(x + 18, uy + 78, s, size=11, fill="#e6edf3", anchor="middle")
    text(x + 33, uy + 90, k, size=9, fill="#ffd54a", anchor="end")
a('</g>')

# minimap corner: tile box, what next, minimap
mx = MAPR - 8 - 224
a('<g id="tile_box">')
box(mx, oy + 610, 224, 76, fill="#0b0f14", stroke="#3a4350", rx=4)
text(mx + 10, oy + 628, "Grassland, river", size=11, fill="#e6edf3", weight="bold")
text(mx + 10, oy + 644, "road; owner: Hittites (Lookton)", size=10)
text(mx + 10, oy + 660, "food 3  shield 0  trade 2", size=10)
note(mx + 10, oy + 678, "tile_box: the hovered tile (kept on leave)")
a('</g>')
a('<g id="what_next">')
a(f'<rect x="{mx}" y="{oy+694}" width="224" height="40" rx="6" fill="#2e8b57" stroke="#9be7b4"/>')
text(mx + 112, oy + 719, "Unit needs orders", size=14, fill="#ffffff", anchor="middle", weight="bold")
text(mx + 216, oy + 728, "1 of 3", size=9, fill="#d2f5de", anchor="end")
a('</g>')
a(f'<rect x="{mx}" y="{oy+742}" width="224" height="148" fill="#0b0f14" stroke="#3a4350"/>')
a(f'<rect x="{mx+40}" y="{oy+770}" width="90" height="60" fill="#3f6b3a"/><rect x="{mx+150}" y="{oy+800}" width="40" height="50" fill="#3f6b3a"/>')
note(mx + 112, oy + 884, "minimap (as today)", anchor="middle")

# ======================= frame 2: city view =======================
oy = H + GAP
frame_title(oy, "City view, 1x: the map stays, centred on the city with its worked tiles; the city's parts sit on the edges")
map_base(oy)
top_strip(oy)
edge_column(oy, badges=True)

# the city in the centre, worked tiles ringed with yields
cx0, cy0 = 664, oy + 446
a('<g fill="none" stroke="#ffd54a" stroke-width="2">')
for dx, dy in [(-48, -48), (0, -48), (48, 0), (-48, 48)]:
    a(f'<rect x="{cx0+dx}" y="{cy0+dy}" width="48" height="48"/>')
a('</g>')
a('<g fill="none" stroke="#ffd54a" stroke-width="1" stroke-dasharray="4 3">')
for dx, dy in [(48, -48), (-96, 0), (0, 48), (48, 48), (-96, -48), (96, 0)]:
    a(f'<rect x="{cx0+dx}" y="{cy0+dy}" width="48" height="48"/>')
a('</g>')
for (dx, dy), s in zip([(-48, -48), (0, -48), (48, 0), (-48, 48)], ["2/1/0", "1/2/0", "3/0/1", "1/1/2"]):
    text(cx0 + dx + 4, cy0 + dy + 12, s, size=9, fill="#ffd54a")
a(f'<rect x="{cx0}" y="{cy0}" width="48" height="48" fill="#8a7b5a"/>')
a(f'<circle cx="{cx0+24}" cy="{cy0+24}" r="14" fill="#f2b632" stroke="#fff3c4" stroke-width="2"/>')
a(f'<circle cx="{cx0+24}" cy="{cy0+24}" r="19" fill="none" stroke="#ffffff" stroke-width="1.5"/>')
text(cx0 + 24, cy0 + 29, "4", size=13, fill="#1a1a1a", anchor="middle", weight="bold")
note(cx0 - 96, cy0 + 116, "worked tiles solid, free ones dashed; a click toggles a worker")

a('<g id="city_overlay">')
# yields, top left
yx, yy = 8, oy + 30 + TOP + 8
a('<g id="city_yields">')
box(yx, yy, 360, 96)
text(yx + 12, yy + 20, "size 4   grows in 6 turns   granary 12/24", size=11, fill="#e6edf3")
for i, (n, v) in enumerate([("food", "+2"), ("shields", "+3"), ("trade", "+3"), ("gold", "+1"), ("bulbs", "2"), ("culture", "+1")]):
    x = yx + 12 + i * 56
    a(f'<rect x="{x}" y="{yy+32}" width="52" height="36" rx="3" fill="#1c2531"/>')
    text(x + 6, yy + 45, n, size=9, fill="#8b949e")
    text(x + 6, yy + 61, v, size=13, fill="#e6edf3")
note(yx + 12, yy + 86, "city_yields: tooltips give each breakdown")
a('</g>')
# header, top centre
hx = (MAPR - 400) // 2
a('<g id="city_header">')
box(hx, yy, 400, 56)
a(f'<circle cx="{hx+28}" cy="{yy+28}" r="12" fill="#f2b632"/>')
text(hx + 28, yy + 32, "4", size=12, fill="#1a1a1a", anchor="middle", weight="bold")
text(hx + 120, yy + 26, "‹", size=18, fill="#e6edf3")
text(hx + 200, yy + 26, "Lookton", size=16, fill="#e6edf3", anchor="middle", weight="bold")
text(hx + 272, yy + 26, "›", size=18, fill="#e6edf3")
text(hx + 200, yy + 46, "governor ·  celebrating", size=10, fill="#8b949e", anchor="middle")
text(hx + 384, yy + 22, "x", size=14, fill="#e6edf3", anchor="end")
a('</g>')
# sections, right
sx, sw = MAPR - 8 - 300, 300
a('<g id="city_sections">')
box(sx, yy, sw, H - 30 - TOP - 16)
y = yy + 22
def heading(label, open_):
    global y
    text(sx + 12, y, ("▾ " if open_ else "▸ ") + label, size=11, fill="#8b949e", weight="bold")
    y += 18
heading("CITIZENS", True)
for i, col in enumerate(["#4caf50", "#4caf50", "#c9d1d9", "#c23b3b"]):
    a(f'<circle cx="{sx+22+i*20}" cy="{y}" r="8" fill="{col}"/>')
a(f'<circle cx="{sx+102}" cy="{y}" r="8" fill="#3a7bd5"/>')
text(sx + 118, y + 4, "2 happy, 1 content, 1 unhappy", size=10)
y += 22
text(sx + 12, y, "health: plague risk 1.2%   pollution 0", size=10)
y += 30
heading("BUILDINGS (upkeep 1)", True)
for b in ["Palace", "Barracks", "Granary"]:
    text(sx + 20, y, b, size=11); y += 16
note(sx + 20, y, "hover: help text; right-click: sell"); y += 26
heading("UNITS  here 3, supported 2", True)
for i, col in enumerate(["#3a7bd5", "#3a7bd5", "#8a7b5a"]):
    a(f'<rect x="{sx+20+i*34}" y="{y-6}" width="28" height="28" rx="3" fill="{col}"/>')
y += 46
heading("GREAT PEOPLE", False)
note(sx + 20, y, "later: one bar per kind (patch 0013 points)"); y += 26
heading("SPECIALIST BUILDINGS", False)
note(sx + 20, y + 4, "later")
note(sx + 12, yy + H - 30 - TOP - 26, "city_sections: 300 px wide, each heading folds its section")
a('</g>')
# production, bottom left
px, py = 8, oy + H - 8 - 200
a('<g id="city_production">')
box(px, py, 380, 200)
a(f'<rect x="{px+12}" y="{py+12}" width="80" height="22" rx="3" fill="#2b3441"/>')
text(px + 52, py + 27, "Change", size=11, fill="#e6edf3", anchor="middle")
a(f'<rect x="{px+100}" y="{py+12}" width="100" height="22" rx="3" fill="#2b3441"/>')
text(px + 150, py + 27, "Buy  50 gold", size=11, fill="#e6edf3", anchor="middle")
a(f'<rect x="{px+268}" y="{py+12}" width="100" height="22" rx="3" fill="#1c2531" stroke="#2b3441"/>')
text(px + 318, py + 27, "Show queue ▴", size=10, fill="#c9d1d9", anchor="middle")
a(f'<rect x="{px+12}" y="{py+48}" width="64" height="64" rx="4" fill="#3a7bd5"/>')
text(px + 88, py + 66, "Warriors", size=15, fill="#e6edf3", weight="bold")
text(px + 88, py + 84, "4/10 shields, 2 turns   upkeep 1 shield", size=11)
a(f'<rect x="{px+88}" y="{py+94}" width="270" height="4" fill="#2b3441"/><rect x="{px+88}" y="{py+94}" width="108" height="4" fill="#4caf50"/>')
text(px + 12, py + 136, "Defends well in hills and forest; the first", size=10, fill="#8b949e")
text(px + 12, py + 150, "unit of era I (help text, scrolls).", size=10, fill="#8b949e")
note(px + 12, py + 190, "city_production: 380 x 200; the queue unfolds upwards")
a('</g>')
# footer, bottom centre
fx = (MAPR - 340) // 2
a('<g id="city_footer">')
box(fx, oy + H - 8 - 40, 340, 40)
for i, (s, w) in enumerate([("Worked tiles [on]", 104), ("Full dialog (Enter)", 108), ("Return to map (Esc)", 104)]):
    x = fx + 8 + sum([104, 108, 104][:i]) + i * 4
    a(f'<rect x="{x}" y="{oy+H-8-32}" width="{w}" height="24" rx="3" fill="#2b3441"/>')
    text(x + w // 2, oy + H - 8 - 16, s, size=10, fill="#e6edf3", anchor="middle")
a('</g>')
a('</g>')
note(MAPR - 8 - 300 - 8, oy + H - 60, "hidden while a city is open: unit bar, chat, minimap,", anchor="end")
note(MAPR - 8 - 300 - 8, oy + H - 48, "tile box and what next; they come back on Return to map", anchor="end")

a('</svg>')
open(sys.argv[1], "w").write("\n".join(out) + "\n")
