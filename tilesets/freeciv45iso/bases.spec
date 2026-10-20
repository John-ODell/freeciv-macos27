; Re-cut from amplio2/bases.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.
[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Hogne Håskjold <hogne@freeciv.org>[HH]
    Eleazar [El](buoy)
    Anton Ecker (Kaldred) (ruins)
    GriffonSpade [GS]
    Sveinung Kvilhaugsvik [SK]
    Lexxie L. [Lexxie]
"

[file]
gfx = "freeciv45iso/bases"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 144

tiles = { "row", "column", "tag"
   0,  0, "base.airbase_mg"
   0,  1, "tx.airbase_full"
   1,  0, "base.airstrip_mg"
   2,  2, "base.castle2_fg"
   2,  3, "base.castle2_bg"
   0,  6, "cd.city", "cd.city_wall"
}

