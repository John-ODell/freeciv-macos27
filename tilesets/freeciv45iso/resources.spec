; Resources for the Freeciv45 iso tileset: the Freeciv45 art pack's isometric props (freeciv45/03_resources),
; one pick per tag, copied by tilesets/make-freeciv45iso.py (see RECORD.md).

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/resources"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
  0, 0, "ts.wheat"
  0, 1, "ts.buffalo"
  0, 2, "ts.horses"
  0, 3, "ts.grassland_resources"
  0, 4, "ts.fruit"
  1, 0, "ts.gems"
  1, 1, "ts.oasis"
  1, 2, "ts.oil"
  1, 3, "ts.pheasant"
  1, 4, "ts.silk"
  2, 0, "ts.coal"
  2, 1, "ts.wine"
  2, 2, "ts.gold"
  2, 3, "ts.iron"
  2, 4, "ts.tundra_game"
  3, 0, "ts.furs"
  3, 1, "ts.arctic_ivory"
  3, 2, "ts.peat"
  3, 3, "ts.spice"
  3, 4, "ts.fish"
  4, 0, "ts.whales"
}
