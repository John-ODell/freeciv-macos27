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
   0,  3, "base.fortress_fg"
   0,  4, "base.fortress_bg"
   1,  0, "base.airstrip_mg"
   1,  1, "base.buoy_mg"
   1,  3, "base.outpost_fg"
   1,  4, "base.outpost_bg"
   1,  5, "extra.transport_hub_mg"
   2,  2, "base.castle2_fg"
   2,  3, "base.castle2_bg"
   2,  4, "base.castle_fg"
   2,  5, "base.castle_bg"
   0,  2, "cd.occupied", "city.european_occupied_0", "city.classical_occupied_0", "city.asian_occupied_0", "city.tropical_occupied_0", "city.celtic_occupied_0", "city.babylonian_occupied_0", "city.industrial_occupied_0", "city.electricage_occupied_0", "city.modern_occupied_0", "city.postmodern_occupied_0"
   0,  5, "city.disorder"
   0,  6, "cd.city", "cd.city_wall"
}

