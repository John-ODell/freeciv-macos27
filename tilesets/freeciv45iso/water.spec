; Re-cut from amplio2/water.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Hogne Håskjold
    Tim F. Smith <yoohootim@hotmail.com>
    Yautja
    Daniel Speyer
    Eleazar
"

[file]
gfx = "freeciv45iso/water"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
   2,  0, "road.river_s_n0e0s0w0"
   2,  1, "road.river_s_n0e0s0w1"
   2,  2, "road.river_s_n0e0s1w0"
   2,  3, "road.river_s_n0e0s1w1"
   2,  4, "road.river_s_n0e1s0w0"
   2,  5, "road.river_s_n0e1s0w1"
   2,  6, "road.river_s_n0e1s1w0"
   2,  7, "road.river_s_n0e1s1w1"
   3,  0, "road.river_s_n1e0s0w0"
   3,  1, "road.river_s_n1e0s0w1"
   3,  2, "road.river_s_n1e0s1w0"
   3,  3, "road.river_s_n1e0s1w1"
   3,  4, "road.river_s_n1e1s0w0"
   3,  5, "road.river_s_n1e1s0w1"
   3,  6, "road.river_s_n1e1s1w0"
   3,  7, "road.river_s_n1e1s1w1"
   4,  0, "road.river_outlet_n"
   4,  1, "road.river_outlet_e"
   4,  2, "road.river_outlet_s"
   4,  3, "road.river_outlet_w"
}

