; Painted ground for the Freeciv45 test tileset, cut from ChatGPT terrain panels by
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
  0, 0, "t.l0.grassland1"   ; panel1 r1c1
  0, 1, "t.l0.grassland2"   ; panel1 r1c2
  0, 2, "t.l0.grassland3"   ; panel1 r1c3
  0, 3, "t.l0.grassland4"   ; panel1 r1c4
  0, 4, "t.l0.grassland5"   ; panel1 r1c5
  1, 0, "t.l0.grassland6"   ; panel1 r2c1
  1, 1, "t.l0.grassland7"   ; panel1 r2c2
  1, 2, "t.l0.grassland8"   ; panel1 r2c3
  1, 3, "t.l0.grassland9"   ; panel1 r2c4
  1, 4, "t.l0.grassland10"   ; panel1 r2c5
  2, 0, "t.l0.plains1"   ; panel1 r3c1
  2, 1, "t.l0.plains2"   ; panel1 r3c2
  2, 2, "t.l0.plains3"   ; panel1 r3c3
  2, 3, "t.l0.plains4"   ; panel1 r3c4
  2, 4, "t.l0.plains5"   ; panel1 r3c5
  3, 0, "t.l0.plains6"   ; panel1 r4c1
  3, 1, "t.l0.plains7"   ; panel1 r4c2
  3, 2, "t.l0.plains8"   ; panel1 r4c3
  3, 3, "t.l0.plains9"   ; panel1 r4c4
  3, 4, "t.l0.plains10"   ; panel1 r4c5
  4, 0, "t.l0.forest1"   ; panel4 r1c1
  4, 1, "t.l0.forest2"   ; panel4 r1c2
  4, 2, "t.l0.forest3"   ; panel4 r1c3
  4, 3, "t.l0.forest4"   ; panel4 r1c4
  4, 4, "t.l0.forest5"   ; panel4 r1c5
  5, 0, "t.l0.forest6"   ; panel4 r2c1
  5, 1, "t.l0.forest7"   ; panel4 r2c2
  5, 2, "t.l0.forest8"   ; panel4 r2c3
  5, 3, "t.l0.forest9"   ; panel4 r2c4
  5, 4, "t.l0.forest10"   ; panel4 r2c5
  6, 0, "t.l0.jungle1"   ; panel4 r3c1
  6, 1, "t.l0.jungle2"   ; panel4 r3c2
  6, 2, "t.l0.jungle3"   ; panel4 r3c3
  6, 3, "t.l0.jungle4"   ; panel4 r3c4
  6, 4, "t.l0.jungle5"   ; panel4 r3c5
  7, 0, "t.l0.jungle6"   ; panel4_retake r4c1
  7, 1, "t.l0.jungle7"   ; panel4_retake r4c2
  7, 2, "t.l0.jungle8"   ; panel4_retake r4c3
  7, 3, "t.l0.jungle9"   ; panel4_retake r4c4
  7, 4, "t.l0.jungle10"   ; panel4_retake r4c5
}
