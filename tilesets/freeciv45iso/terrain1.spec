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
   0,  2, "ts.oasis"
   0,  4, "ts.oil"
   1,  2, "ts.buffalo"
   1,  4, "ts.wheat"
   2,  2, "ts.pheasant"
   2,  4, "ts.silk"
   3,  2, "ts.coal"
   3,  4, "ts.wine"
   4,  2, "ts.gold"
   4,  4, "ts.iron"
   5,  2, "ts.tundra_game"
   5,  4, "ts.furs"
   6,  2, "ts.arctic_ivory"
   6,  4, "ts.arctic_oil"
   7,  2, "ts.peat"
   7,  4, "ts.spice"
   8,  2, "ts.gems"
   8,  4, "ts.fruit"
   9,  2, "ts.fish"
   9,  4, "ts.whales"
  10,  2, "ts.seals"
  10,  4, "ts.forest_game"
  11,  2, "ts.horses"
  11,  4, "ts.grassland_resources", "ts.river_resources"
  12,  0, "road.road_isolated"
  12,  1, "road.road_n"
  12,  2, "road.road_ne"
  12,  3, "road.road_e"
  12,  4, "road.road_se"
  12,  5, "road.road_s"
  12,  6, "road.road_sw"
  12,  7, "road.road_w"
  12,  8, "road.road_nw"
  13,  0, "road.rail_isolated"
  13,  1, "road.rail_n"
  13,  2, "road.rail_ne"
  13,  3, "road.rail_e"
  13,  4, "road.rail_se"
  13,  5, "road.rail_s"
  13,  6, "road.rail_sw"
  13,  7, "road.rail_w"
  13,  8, "road.rail_nw"
   0,  6, "tx.oil_mine"
   1,  6, "tx.irrigation"
   2,  6, "tx.farmland"
   3,  6, "tx.mine"
   4,  6, "tx.pollution"
   5,  6, "tx.village"
   6,  6, "tx.fallout"
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

