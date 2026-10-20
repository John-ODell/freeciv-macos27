# Synthetic check for issue 259: the shipped border masks, tinted as the client tints them, drawn on the tileset's own terrain
# cells at an edge between two owners. Usage: python3.14 borders-montage.py TILESET_DIR OUT.jpg
import re, sys
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
W, H = 192, 96
sheet = Image.open(d + "/terrain45.png").convert("RGBA")
spec = open(d + "/terrain45.spec").read()
def cell(tag):
    m = re.search(r'(\d+),\s*(\d+),\s*"%s"' % re.escape(tag), spec); r, c = int(m.group(1)), int(m.group(2))
    return sheet.crop((c * W, r * H, (c + 1) * W, (r + 1) * H))
masks = Image.open(d + "/borders.png").convert("RGBA")
def tint(k, rgb):
    m = masks.crop((k * W, 0, (k + 1) * W, H)); t = Image.new("RGBA", (W, H), rgb + (255,)); t.putalpha(m.getchannel("A")); return t
RED, BLUE = (225, 40, 40), (40, 90, 235)
# n/s: owners above-right and below-left of a down-right edge; w/e: above-left and below-right of an up-right edge
tiles = {"n": (48, -24), "s": (-48, 24), "w": (-48, -24), "e": (48, 24)}
terrains = [("grassland", "t.l0.grassland1", "t.l0.grassland6"), ("desert", "t.l0.desert1", "t.l0.desert2"),
            ("snow", "t.l0.arctic1", "t.l0.arctic2"), ("water", "t.l0.lake1", "t.l0.lake1"),
            ("tundra", "t.l0.tundra1", "t.l0.tundra2")]
pad = 60; cw, ch = W + 2 * pad, H + 2 * pad
img = Image.new("RGBA", (cw * len(terrains), ch * 2), (18, 18, 18, 255))
for i, (name, a, b) in enumerate(terrains):
    for row, (t1, t2, k1, k2) in enumerate((("n", "s", 0, 1), ("w", "e", 2, 3))):
        cv = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        for t, tag in ((t1, a), (t2, b)):
            ox, oy = tiles[t]; cv.alpha_composite(cell(tag), (pad + ox, pad + oy))
        cv.alpha_composite(tint(k1, RED), (pad, pad))
        cv.alpha_composite(tint(k2, BLUE), (pad, pad))
        img.alpha_composite(cv, (i * cw, row * ch))
img.convert("RGB").save(out, quality=90)
