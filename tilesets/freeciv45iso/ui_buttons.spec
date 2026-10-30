; The Qt client's right-edge buttons and unit-bar actions for the Freeciv45 iso tileset: the
; Freeciv45 art pack's freeciv45/13_ui_icons run 2, fitted by tilesets/make-freeciv45iso.py (see RECORD.md)
; at twice the size the client draws them.

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/ui_buttons"

[grid_edge]

x_top_left = 0
y_top_left = 0
dx = 76
dy = 76

tiles = { "row", "column", "tag"
  0, 0, "ui.edge.map"
  0, 1, "ui.edge.research"
  0, 2, "ui.edge.nations"
  0, 3, "ui.edge.cities"
  0, 4, "ui.edge.units"
  0, 5, "ui.edge.economy"
  0, 6, "ui.edge.more"
}

[grid_action]

x_top_left = 0
y_top_left = 76
dx = 48
dy = 48

tiles = { "row", "column", "tag"
  0, 0, "ui.action.settle"
  0, 1, "ui.action.road"
  0, 2, "ui.action.irrigate"
  0, 3, "ui.action.mine"
  0, 4, "ui.action.goto"
  0, 5, "ui.action.fortify"
  0, 6, "ui.action.sentry"
  0, 7, "ui.action.wait"
  0, 8, "ui.action.done"
}

