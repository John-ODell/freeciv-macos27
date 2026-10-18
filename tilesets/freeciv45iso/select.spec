; Re-cut from amplio2/select.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.
[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Jason Dorje Short <jdorje@freeciv.org>
    Eleazar / J. W. Bjerk <www.jwbjerk.com>
    qwm
"

[file]
gfx = "freeciv45iso/select"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
   0,  0, "unit.select0"
   0,  1, "unit.select1"
   0,  2, "unit.select2"
   0,  3, "unit.select3"
}

