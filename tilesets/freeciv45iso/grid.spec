; Re-cut from amplio2/grid.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Jason Dorje Short <jdorje@freeciv.org>
    Hogne Håskjold    <hogne@freeciv.org>
    Eleazar / J. W. Bjerk <www.jwbjerk.com>
"

[file]
gfx = "freeciv45iso/grid"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
   0,  0, "grid.main.we"
   1,  0, "grid.main.ns"
   0,  1, "grid.city.we"
   1,  1, "grid.city.ns"
   0,  2, "grid.worked.we"
   1,  2, "grid.worked.ns"
   0,  3, "grid.unavailable"
   1,  3, "grid.nonnative"
   0,  4, "grid.selected.we"
   1,  4, "grid.selected.ns"
   0,  5, "grid.coastline.we"
   1,  5, "grid.coastline.ns"
}

