; Painted ground for the Freeciv45 test tileset, cut from a ChatGPT terrain panel by
; tilesets/make-freeciv45test.py (see RECORD.md). Each cell: seamless.py 192 px master, then 96 px.

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45test/terrain45"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 96
dy = 96

tiles = { "row", "column", "tag"
  0, 0, "t.l0.grassland1"   ; panel cell r1c1
  0, 1, "t.l0.grassland2"   ; panel cell r1c2
  0, 2, "t.l0.grassland3"   ; panel cell r1c3
  0, 3, "t.l0.grassland4"   ; panel cell r1c4
  0, 4, "t.l0.grassland5"   ; panel cell r1c5
  1, 0, "t.l0.grassland6"   ; panel cell r2c1
  1, 1, "t.l0.grassland7"   ; panel cell r2c2
  1, 2, "t.l0.grassland8"   ; panel cell r2c3
  1, 3, "t.l0.grassland9"   ; panel cell r2c4
  1, 4, "t.l0.grassland10"   ; panel cell r2c5
  2, 0, "t.l0.plains1"   ; panel cell r3c1
  2, 1, "t.l0.plains2"   ; panel cell r3c2
  2, 2, "t.l0.plains3"   ; panel cell r3c3
  2, 3, "t.l0.plains4"   ; panel cell r3c4
  2, 4, "t.l0.plains5"   ; panel cell r3c5
  3, 0, "t.l0.plains6"   ; panel cell r4c1
  3, 1, "t.l0.plains7"   ; panel cell r4c2
  3, 2, "t.l0.plains8"   ; panel cell r4c3
  3, 3, "t.l0.plains9"   ; panel cell r4c4
  3, 4, "t.l0.plains10"   ; panel cell r4c5
}
