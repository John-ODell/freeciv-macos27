; Re-cut from amplio2/animals.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.
[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    David Fernandez (bard)
"

[file]
gfx = "freeciv45iso/animals"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 128
dy = 96

tiles = { "row", "column", "tag"
   0,  0, "u.wolf"
   0,  1, "u.leopard"
   0,  2, "u.tiger"
   1,  1, "u.bear"
   1,  2, "u.snake"
   2,  0, "u.crocodile"
   2,  1, "u.gorilla"
}

