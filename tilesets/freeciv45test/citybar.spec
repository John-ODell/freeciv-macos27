; Re-cut from misc/citybar.spec by tilesets/make-freeciv45test.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
     Freim <...>
     Madeline Book <madeline.book@gmail.com> (citybar.trade)
"

[file]
gfx = "freeciv45test/citybar"

[grid_big]

x_top_left = 0
y_top_left = 0
dx = 36
dy = 36

tiles = { "row", "column", "tag"
   0,  0, "citybar.shields"
   0,  1, "citybar.food"
   0,  2, "citybar.trade"
}

[grid_star]

x_top_left = 0
y_top_left = 36
dx = 22
dy = 36

tiles = { "row", "column", "tag"
   0,  0, "citybar.occupied"
   0,  1, "citybar.occupancy_0"
   0,  2, "citybar.occupancy_1"
   0,  3, "citybar.occupancy_2"
   0,  4, "citybar.occupancy_3"
}

[grid_bg]

x_top_left = 0
y_top_left = 72
dx = 796
dy = 304

tiles = { "row", "column", "tag"
   0,  0, "citybar.background"
}

