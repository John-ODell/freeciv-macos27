; Re-cut from amplio2/activities.spec by tilesets/make-freeciv45iso.py: every sprite scaled 2x with nearest-neighbour
; sampling (placeholders until Freeciv45 art exists). Original artists are credited below.

[spec]

; Format and options of this spec file:
options = "+Freeciv-3.2-spec"

[info]

artists = "
    Tatu Rissanen <tatu.rissanen@hut.fi>
    Jeff Mallatt <jjm@codewell.com> (miscellaneous)
    GriffonSpade [GS]
    Sveinung Kvilhaugsvik (action_decision_want)
"

[file]
gfx = "freeciv45iso/activities"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 56
dy = 48

tiles = { "row", "column", "tag"
   0,  2, "unit.maglev"
   1,  0, "unit.outpost"
   1,  1, "unit.airstrip"
   1,  4, "unit.buoy"
   3,  4, "unit.fallout"
   5,  3, "unit.oil_mine"
   5,  4, "unit.oil_rig"
}

