; Map extras for the Freeciv45 iso tileset: the Freeciv45 art pack's freeciv45/09_map_extras runs 1 to 4
; (improvements, forts, airfields, overlays, road, rail and river bands), cut and painted by tilesets/make-freeciv45iso.py
; (see RECORD.md).

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/extras"

[grid_full]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 144

tiles = { "row", "column", "tag"
  0, 0, "tx.mine_mg"
  0, 1, "tx.oil_mine_mg"
  0, 2, "tx.oil_rig_mg"
  0, 3, "tx.village_mg"
  0, 4, "tx.hermit_mg"
  0, 5, "extra.transport_hub_mg"
  0, 6, "base.buoy_mg"
  0, 7, "base.outpost_bg"
  0, 8, "base.outpost_fg"
  0, 9, "base.fortress_bg"
  1, 0, "base.fortress_fg"
  1, 1, "base.castle_bg"
  1, 2, "base.castle_fg"
  1, 3, "base.airstrip_bg"
  1, 4, "base.airbase_bg"
}

[grid_tile]

x_top_left = 0
y_top_left = 288
dx = 192
dy = 96

tiles = { "row", "column", "tag"
  0, 0, "tx.irrigation"
  0, 1, "tx.farmland"
  0, 2, "tx.pollution"
  0, 3, "tx.fallout"
  0, 4, "road.road_isolated"
  0, 5, "road.road_n"
  0, 6, "road.road_ne"
  0, 7, "road.road_e"
  0, 8, "road.road_se"
  0, 9, "road.road_s"
  1, 0, "road.road_sw"
  1, 1, "road.road_w"
  1, 2, "road.road_nw"
  1, 3, "road.rail_isolated"
  1, 4, "road.rail_n"
  1, 5, "road.rail_ne"
  1, 6, "road.rail_e"
  1, 7, "road.rail_se"
  1, 8, "road.rail_s"
  1, 9, "road.rail_sw"
  2, 0, "road.rail_w"
  2, 1, "road.rail_nw"
  2, 2, "road.river_s_n0e0s0w0"
  2, 3, "road.river_s_n0e0s0w1"
  2, 4, "road.river_s_n0e0s1w0"
  2, 5, "road.river_s_n0e0s1w1"
  2, 6, "road.river_s_n0e1s0w0"
  2, 7, "road.river_s_n0e1s0w1"
  2, 8, "road.river_s_n0e1s1w0"
  2, 9, "road.river_s_n0e1s1w1"
  3, 0, "road.river_s_n1e0s0w0"
  3, 1, "road.river_s_n1e0s0w1"
  3, 2, "road.river_s_n1e0s1w0"
  3, 3, "road.river_s_n1e0s1w1"
  3, 4, "road.river_s_n1e1s0w0"
  3, 5, "road.river_s_n1e1s0w1"
  3, 6, "road.river_s_n1e1s1w0"
  3, 7, "road.river_s_n1e1s1w1"
  3, 8, "road.river_outlet_n"
  3, 9, "road.river_outlet_e"
  4, 0, "road.river_outlet_s"
  4, 1, "road.river_outlet_w"
}

