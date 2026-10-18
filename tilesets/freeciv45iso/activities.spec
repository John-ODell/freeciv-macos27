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
   0,  0, "unit.road"
   0,  1, "unit.rail"
   0,  2, "unit.maglev"
   1,  0, "unit.outpost"
   1,  1, "unit.airstrip"
   1,  2, "unit.fortress"
   1,  3, "unit.airbase"
   1,  4, "unit.buoy"
   2,  0, "unit.fortified"
   2,  1, "unit.fortifying"
   2,  2, "unit.sentry"
   2,  3, "unit.patrol"
   2,  4, "unit.pillage"
   3,  0, "unit.cultivate", "unit.irrigate"
   3,  1, "unit.plant"
   3,  2, "unit.transform"
   3,  3, "unit.pollution"
   3,  4, "unit.fallout"
   4,  0, "unit.goto"
   4,  1, "unit.convert"
   4,  2, "unit.auto_explore"
   4,  3, "unit.action_decision_want"
   5,  0, "unit.irrigation"
   5,  1, "unit.farmland"
   5,  2, "unit.mine"
   5,  3, "unit.oil_mine"
   5,  4, "unit.oil_rig"
}

