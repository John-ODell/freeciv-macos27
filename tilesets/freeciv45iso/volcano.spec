; Re-cut from amplio2/volcano.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    XYZ
"

[file]
gfx = "freeciv45iso/volcano"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
   0,  0, "t.l0.volcano1"
   1,  0, "t.l0.erupting_volcanoa1"
   2,  0, "t.l0.erupting_volcanob1"
}

