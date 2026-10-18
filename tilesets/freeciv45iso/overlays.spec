; Re-cut from misc/overlays.spec by tilesets/make-freeciv45iso.py: every sprite scaled 3x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Jason Dorje Short <jdorje@freeciv.org>
"

[file]
gfx = "freeciv45iso/overlays"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 384
dy = 192

tiles = { "row", "column", "tag"
   0,  0, "colors.overlay_0"
   0,  1, "colors.overlay_1"
   1,  0, "colors.overlay_2"
   1,  1, "colors.overlay_3"
   0,  2, "mask.worked_tile"
   1,  2, "mask.unworked_tile"
}

