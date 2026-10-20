; Badges for the Freeciv45 iso tileset: the Freeciv45 art pack's freeciv45/09_map_extras run 6, placed
; where amplio2 draws its badges by tilesets/make-freeciv45iso.py, the counted upkeep and tile output drawn with a number
; (see RECORD.md).

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/badges"

[grid_act]

x_top_left = 0
y_top_left = 0
dx = 56
dy = 48

tiles = { "row", "column", "tag"
  0, 0, "unit.maglev"
  0, 1, "unit.oil_mine"
  0, 2, "unit.oil_rig"
  0, 3, "unit.airstrip"
  0, 4, "unit.outpost"
  0, 5, "unit.buoy"
  0, 6, "unit.fallout"
}

[grid_tile]

x_top_left = 0
y_top_left = 48
dx = 192
dy = 96

tiles = { "row", "column", "tag"
  0, 0, "unit.stack"
  0, 1, "unit.loaded"
  0, 2, "unit.connect"
  0, 3, "unit.auto_attack"
  0, 4, "unit.auto_settler"
  0, 5, "city.t_food_0"
  0, 6, "city.t_food_1"
  0, 7, "city.t_food_2"
  0, 8, "city.t_food_3"
  0, 9, "city.t_food_4"
  1, 0, "city.t_food_5"
  1, 1, "city.t_food_6"
  1, 2, "city.t_food_7"
  1, 3, "city.t_food_8"
  1, 4, "city.t_food_9"
  1, 5, "city.t_shields_0"
  1, 6, "city.t_shields_1"
  1, 7, "city.t_shields_2"
  1, 8, "city.t_shields_3"
  1, 9, "city.t_shields_4"
  2, 0, "city.t_shields_5"
  2, 1, "city.t_shields_6"
  2, 2, "city.t_shields_7"
  2, 3, "city.t_shields_8"
  2, 4, "city.t_shields_9"
  2, 5, "city.t_trade_0"
  2, 6, "city.t_trade_1"
  2, 7, "city.t_trade_2"
  2, 8, "city.t_trade_3"
  2, 9, "city.t_trade_4"
  3, 0, "city.t_trade_5"
  3, 1, "city.t_trade_6"
  3, 2, "city.t_trade_7"
  3, 3, "city.t_trade_8"
  3, 4, "city.t_trade_9"
}

[grid_city]

x_top_left = 0
y_top_left = 432
dx = 192
dy = 144

tiles = { "row", "column", "tag"
  0, 0, "cd.occupied", "city.european_occupied_0", "city.classical_occupied_0", "city.asian_occupied_0", "city.tropical_occupied_0", "city.celtic_occupied_0", "city.babylonian_occupied_0", "city.industrial_occupied_0", "city.electricage_occupied_0", "city.modern_occupied_0", "city.postmodern_occupied_0"
  0, 1, "city.disorder"
}

[grid_upkeep]

x_top_left = 0
y_top_left = 576
dx = 192
dy = 38

tiles = { "row", "column", "tag"
  0, 0, "upkeep.shield"
  0, 1, "upkeep.shield2"
  0, 2, "upkeep.shield3"
  0, 3, "upkeep.shield4"
  0, 4, "upkeep.shield5"
  0, 5, "upkeep.shield6"
  0, 6, "upkeep.shield7"
  0, 7, "upkeep.shield8"
  0, 8, "upkeep.shield9"
  0, 9, "upkeep.shield10"
  1, 0, "upkeep.gold"
  1, 1, "upkeep.gold2"
  1, 2, "upkeep.gold3"
  1, 3, "upkeep.gold4"
  1, 4, "upkeep.gold5"
  1, 5, "upkeep.gold6"
  1, 6, "upkeep.gold7"
  1, 7, "upkeep.gold8"
  1, 8, "upkeep.gold9"
  1, 9, "upkeep.gold10"
  2, 0, "upkeep.food"
  2, 1, "upkeep.food2"
  2, 2, "upkeep.food3"
  2, 3, "upkeep.food4"
  2, 4, "upkeep.food5"
  2, 5, "upkeep.food6"
  2, 6, "upkeep.food7"
  2, 7, "upkeep.food8"
  2, 8, "upkeep.food9"
  2, 9, "upkeep.food10"
  3, 0, "upkeep.unhappy"
  3, 1, "upkeep.unhappy2"
  3, 2, "upkeep.unhappy3"
  3, 3, "upkeep.unhappy4"
  3, 4, "upkeep.unhappy5"
  3, 5, "upkeep.unhappy6"
  3, 6, "upkeep.unhappy7"
  3, 7, "upkeep.unhappy8"
  3, 8, "upkeep.unhappy9"
  3, 9, "upkeep.unhappy10"
}

