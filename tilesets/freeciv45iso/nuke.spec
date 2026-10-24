; Re-cut from amplio2/nuke.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.
[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Michael Johnson <justaguest>
"

[file]
gfx = "freeciv45iso/nuke"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 360
dy = 352

tiles = { "row", "column", "tag"
   0,  0, "explode.nuke"
}

