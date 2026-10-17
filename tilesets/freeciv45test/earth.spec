; Re-cut from trident/earth.spec by tilesets/make-freeciv45test.py: every sprite scaled 3.2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.
[spec]
; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]
artists = "
    Tatu Rissanen <tatu.rissanen@hut.fi>
    Jeff Mallatt <jjm@codewell.com> (miscellaneous)
"

[file]
gfx = "freeciv45test/earth"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 96
dy = 96

tiles = { "row", "column", "tag"
   0,  0, "tx.denmark_00"
   0,  1, "tx.denmark_01"
   0,  2, "tx.denmark_02"
   1,  0, "tx.denmark_10"
   1,  1, "tx.denmark_11"
   1,  2, "tx.denmark_12"
}

