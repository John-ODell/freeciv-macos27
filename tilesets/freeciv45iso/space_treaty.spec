; Spaceship parts and treaty marks for the Freeciv45 iso tileset: the Freeciv45 art pack's
; freeciv45/13_ui_icons run 3, fitted by tilesets/make-freeciv45iso.py (see RECORD.md) at the stock sizes.
; Listed after misc/treaty.spec, so these tags override the stock pictures.

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/space_treaty"

[grid_space]

x_top_left = 0
y_top_left = 0
dx = 60
dy = 60

tiles = { "row", "column", "tag"
  0, 0, "spaceship.solar_panels"
  0, 1, "spaceship.life_support"
  0, 2, "spaceship.habitation"
  0, 3, "spaceship.structural"
  0, 4, "spaceship.fuel"
  0, 5, "spaceship.propulsion"
  0, 6, "spaceship.exhaust"
}

[grid_treaty]

x_top_left = 0
y_top_left = 60
dx = 30
dy = 30

tiles = { "row", "column", "tag"
  0, 0, "treaty.agree_thumb_up"
  0, 1, "treaty.disagree_thumb_down"
}

