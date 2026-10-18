; Re-cut from trident/explosions.spec by tilesets/make-freeciv45test.py: every sprite scaled 6.4x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Explosions from xgalaga <https://sourceforge.net/projects/xgalaga/>
    Credits:
    Joe Rumsey <ogre@atomic.com>
    Mike McGrath <mcgrath@epx.cis.umn.edu>
"

[file]
gfx = "freeciv45test/explosions"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 192

tiles = { "row", "column", "tag"
   0,  0, "explode.unit_0"
   1,  0, "explode.unit_1"
   2,  0, "explode.unit_2"
   3,  0, "explode.unit_3"
   4,  0, "explode.unit_4"
}

