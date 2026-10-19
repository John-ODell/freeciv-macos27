; Marks on units for the Freeciv45 iso tileset: the Freeciv45 art pack's badges (freeciv45/04_units
; run 5), scaled by tilesets/make-freeciv45iso.py (see RECORD.md): the activities in 56x48 cells, veteran levels, tired
; and low fuel in 128x112 cells.

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/marks"

[grid_activities]

x_top_left = 0
y_top_left = 0
dx = 56
dy = 48

tiles = { "row", "column", "tag"
  0, 0, "unit.road"
  0, 1, "unit.rail"
  0, 2, "unit.fortress"
  0, 3, "unit.airbase"
  0, 4, "unit.fortified"
  0, 5, "unit.fortifying"
  0, 6, "unit.sentry"
  0, 7, "unit.patrol"
  0, 8, "unit.pillage"
  0, 9, "unit.cultivate"
  1, 0, "unit.irrigate"
  1, 1, "unit.irrigation"
  1, 2, "unit.plant"
  1, 3, "unit.transform"
  1, 4, "unit.pollution"
  1, 5, "unit.goto"
  1, 6, "unit.convert"
  1, 7, "unit.auto_explore"
  1, 8, "unit.action_decision_want"
  1, 9, "unit.farmland"
  2, 0, "unit.mine"
}

[grid_vet]

x_top_left = 0
y_top_left = 144
dx = 128
dy = 112

tiles = { "row", "column", "tag"
  0, 0, "unit.vet_1"
  0, 1, "unit.vet_2"
  0, 2, "unit.vet_3"
  0, 3, "unit.tired"
  0, 4, "unit.lowfuel"
}

