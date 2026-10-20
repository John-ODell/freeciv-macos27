; Re-cut from amplio2/terrain1.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Hogne Håskjold
    Daniel Speyer
    Yautja
    CapTVK
    GriffonSpade
    Gyubal Wahazar
    Canik
"

[file]
gfx = "freeciv45iso/terrain1"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
   6,  4, "ts.arctic_oil"
  10,  2, "ts.seals"
  10,  4, "ts.forest_game"
  11,  4, "ts.river_resources"
   0,  6, "tx.oil_mine"
   3,  6, "tx.mine"
   5,  6, "tx.village"
   7,  6, "tx.oil_rig"
   8,  6, "tx.nets"
  15,  0, "t.dither_tile"
  15,  0, "tx.darkness"
  15,  2, "t.unknown1"
  15,  4, "user.attention"
  15,  5, "tx.fog"
  15,  6, "user.infratile"
  14,  7, "path.step"
  14,  8, "path.exhausted_mp"
  15,  7, "path.normal"
  15,  8, "path.waypoint"
}

