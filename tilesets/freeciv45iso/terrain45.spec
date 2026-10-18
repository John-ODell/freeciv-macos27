; Painted ground for the Freeciv45 iso tileset, cut from ChatGPT terrain panels by
; tilesets/make-freeciv45iso.py (see RECORD.md). Each cell: seamless.py 192 px master, then 192 px.
; Then turned into 192x96 isometric cells (make-freeciv45iso.py, to_iso).

[spec]

options = "+Freeciv-3.2-spec"

[info]

artists = "
    John O'Dell (sheet workflow)
"

[file]
gfx = "freeciv45iso/terrain45"

[grid_main]

x_top_left = 0
y_top_left = 0
dx = 192
dy = 96

tiles = { "row", "column", "tag"
  0, 0, "t.l0.grassland1"   ; run15 r1c1
  0, 1, "t.l0.grassland2"   ; run15 r1c2
  0, 2, "t.l0.grassland3"   ; run15 r1c3
  0, 3, "t.l0.grassland4"   ; run15 r1c4
  0, 4, "t.l0.grassland5"   ; run15 r1c5
  1, 0, "t.l0.grassland6"   ; run15 r2c1
  1, 1, "t.l0.grassland7"   ; run15 r2c2
  1, 2, "t.l0.grassland8"   ; run15 r2c3
  1, 3, "t.l0.grassland9"   ; run15 r2c4
  1, 4, "t.l0.grassland10"   ; run15 r2c5
  2, 0, "t.l0.plains1"   ; run6 r3c1
  2, 1, "t.l0.plains2"   ; run6 r3c2
  2, 2, "t.l0.plains3"   ; run6 r3c3
  2, 3, "t.l0.plains4"   ; run6 r3c4
  2, 4, "t.l0.plains5"   ; run6 r3c5
  3, 0, "t.l0.plains6"   ; run6 r4c1
  3, 1, "t.l0.plains7"   ; run6 r4c2
  3, 2, "t.l0.plains8"   ; run6 r4c3
  3, 3, "t.l0.plains9"   ; run6 r4c4
  3, 4, "t.l0.plains10"   ; run6 r4c5
  4, 0, "t.l0.plains11"   ; run14 r3c1
  4, 1, "t.l0.plains12"   ; run14 r3c2
  4, 2, "t.l0.plains13"   ; run14 r3c3
  4, 3, "t.l0.plains14"   ; run14 r3c4
  4, 4, "t.l0.plains15"   ; run14 r3c5
  5, 0, "t.l0.forest1"   ; run8 r1c1
  5, 1, "t.l0.forest2"   ; run8 r1c2
  5, 2, "t.l0.forest3"   ; run8 r1c3
  5, 3, "t.l0.forest4"   ; run8 r1c4
  5, 4, "t.l0.forest5"   ; run8 r1c5
  6, 0, "t.l0.forest6"   ; run8 r2c1
  6, 1, "t.l0.forest7"   ; run8 r2c2
  6, 2, "t.l0.forest8"   ; run8 r2c3
  6, 3, "t.l0.forest9"   ; run8 r2c4
  6, 4, "t.l0.forest10"   ; run8 r2c5
  7, 0, "t.l0.jungle1"   ; run17 r3c1
  7, 1, "t.l0.jungle2"   ; run17 r3c2
  7, 2, "t.l0.jungle3"   ; run17 r3c3
  7, 3, "t.l0.jungle4"   ; run17 r3c4
  7, 4, "t.l0.jungle5"   ; run17 r3c5
  8, 0, "t.l0.jungle6"   ; run17 r4c1
  8, 1, "t.l0.jungle7"   ; run17 r4c2
  8, 2, "t.l0.jungle8"   ; run17 r4c3
  8, 3, "t.l0.jungle9"   ; run17 r4c4
  8, 4, "t.l0.jungle10"   ; run17 r4c5
  9, 0, "t.l0.hills1"   ; run6 r3c1
  9, 1, "t.l0.hills2"   ; run6 r3c2
  9, 2, "t.l0.hills3"   ; run6 r3c3
  9, 3, "t.l0.hills4"   ; run6 r3c4
  9, 4, "t.l0.hills5"   ; run6 r3c5
  10, 0, "t.l0.mountains1"   ; run12 r5c1
  10, 1, "t.l0.mountains2"   ; run12 r5c2
  10, 2, "t.l0.mountains3"   ; run12 r5c3
  10, 3, "t.l0.mountains4"   ; run12 r5c4
  10, 4, "t.l0.mountains5"   ; run12 r5c5
  11, 0, "t.l0.desert1"   ; run12 r1c1
  11, 1, "t.l0.desert2"   ; run12 r1c2
  11, 2, "t.l0.desert3"   ; run12 r1c3
  11, 3, "t.l0.desert4"   ; run12 r1c4
  11, 4, "t.l0.desert5"   ; run12 r1c5
  12, 0, "t.l0.desert6"   ; run12 r2c1
  12, 1, "t.l0.desert7"   ; run12 r2c2
  12, 2, "t.l0.desert8"   ; run12 r2c3
  12, 3, "t.l0.desert9"   ; run12 r2c4
  12, 4, "t.l0.desert10"   ; run12 r2c5
  13, 0, "t.l0.desert11"   ; run12 r5c1
  13, 1, "t.l0.desert12"   ; run12 r5c2
  13, 2, "t.l0.desert13"   ; run12 r5c3
  13, 3, "t.l0.desert14"   ; run12 r5c4
  13, 4, "t.l0.desert15"   ; run12 r5c5
  14, 0, "t.l0.desert16"   ; run14 r4c1
  14, 1, "t.l0.desert17"   ; run14 r4c2
  14, 2, "t.l0.desert18"   ; run14 r4c3
  14, 3, "t.l0.desert19"   ; run14 r4c4
  14, 4, "t.l0.desert20"   ; run14 r4c5
  15, 0, "t.l0.tundra1"   ; run12 r3c1
  15, 1, "t.l0.tundra2"   ; run12 r3c2
  15, 2, "t.l0.tundra3"   ; run12 r3c3
  15, 3, "t.l0.tundra4"   ; run12 r3c4
  15, 4, "t.l0.tundra5"   ; run12 r3c5
  16, 0, "t.l0.tundra6"   ; run12 r4c1
  16, 1, "t.l0.tundra7"   ; run12 r4c2
  16, 2, "t.l0.tundra8"   ; run12 r4c3
  16, 3, "t.l0.tundra9"   ; run12 r4c4
  16, 4, "t.l0.tundra10"   ; run12 r4c5
  17, 0, "t.l0.tundra11"   ; run14 r5c1
  17, 1, "t.l0.tundra12"   ; run14 r5c2
  17, 2, "t.l0.tundra13"   ; run14 r5c3
  17, 3, "t.l0.tundra14"   ; run14 r5c4
  17, 4, "t.l0.tundra15"   ; run14 r5c5
  18, 0, "t.l0.arctic1"   ; run13 r1c1
  18, 1, "t.l0.arctic2"   ; run13 r1c2
  18, 2, "t.l0.arctic3"   ; run13 r1c3
  18, 3, "t.l0.arctic4"   ; run13 r1c4
  18, 4, "t.l0.arctic5"   ; run13 r1c5
  19, 0, "t.l0.arctic6"   ; run13 r2c1
  19, 1, "t.l0.arctic7"   ; run13 r2c2
  19, 2, "t.l0.arctic8"   ; run13 r2c3
  19, 3, "t.l0.arctic9"   ; run13 r2c4
  19, 4, "t.l0.arctic10"   ; run13 r2c5
  20, 0, "t.l0.arctic11"   ; run13 r5c1
  20, 1, "t.l0.arctic12"   ; run13 r5c2
  20, 2, "t.l0.arctic13"   ; run13 r5c3
  20, 3, "t.l0.arctic14"   ; run13 r5c4
  20, 4, "t.l0.arctic15"   ; run13 r5c5
  21, 0, "t.l0.swamp1"   ; run13 r3c1
  21, 1, "t.l0.swamp2"   ; run13 r3c2
  21, 2, "t.l0.swamp3"   ; run13 r3c3
  21, 3, "t.l0.swamp4"   ; run13 r3c4
  21, 4, "t.l0.swamp5"   ; run13 r3c5
  22, 0, "t.l0.swamp6"   ; run13 r4c1
  22, 1, "t.l0.swamp7"   ; run13 r4c2
  22, 2, "t.l0.swamp8"   ; run13 r4c3
  22, 3, "t.l0.swamp9"   ; run13 r4c4
  22, 4, "t.l0.swamp10"   ; run13 r4c5
  23, 0, "t.l0.coast1"   ; run10 r1c1
  23, 1, "t.l0.coast2"   ; run10 r1c2
  23, 2, "t.l0.coast3"   ; run10 r1c3
  23, 3, "t.l0.coast4"   ; run10 r1c4
  23, 4, "t.l0.coast5"   ; run10 r1c5
  24, 0, "t.l0.coast6"   ; run10 r2c1
  24, 1, "t.l0.coast7"   ; run10 r2c2
  24, 2, "t.l0.coast8"   ; run10 r2c3
  24, 3, "t.l0.coast9"   ; run10 r2c4
  24, 4, "t.l0.coast10"   ; run10 r2c5
  25, 0, "t.l0.coast11"   ; run10 r3c1
  25, 1, "t.l0.coast12"   ; run10 r3c2
  25, 2, "t.l0.coast13"   ; run10 r3c3
  25, 3, "t.l0.coast14"   ; run10 r3c4
  25, 4, "t.l0.coast15"   ; run10 r3c5
  26, 0, "t.l0.lake1"   ; run10 r4c1
  26, 1, "t.l0.lake2"   ; run10 r4c2
  26, 2, "t.l0.lake3"   ; run10 r4c3
  26, 3, "t.l0.lake4"   ; run10 r4c4
  26, 4, "t.l0.lake5"   ; run10 r4c5
  27, 0, "t.l0.lake6"   ; run10 r5c1
  27, 1, "t.l0.lake7"   ; run10 r5c2
  27, 2, "t.l0.lake8"   ; run10 r5c3
  27, 3, "t.l0.lake9"   ; run10 r5c4
  27, 4, "t.l0.lake10"   ; run10 r5c5
  28, 0, "t.l0.floor1"   ; run11 r1c1
  28, 1, "t.l0.floor2"   ; run11 r1c2
  28, 2, "t.l0.floor3"   ; run11 r1c3
  28, 3, "t.l0.floor4"   ; run11 r1c4
  28, 4, "t.l0.floor5"   ; run11 r1c5
  29, 0, "t.l0.floor6"   ; run11 r2c1
  29, 1, "t.l0.floor7"   ; run11 r2c2
  29, 2, "t.l0.floor8"   ; run11 r2c3
  29, 3, "t.l0.floor9"   ; run11 r2c4
  29, 4, "t.l0.floor10"   ; run11 r2c5
  30, 0, "t.l0.floor11"   ; run11 r3c1
  30, 1, "t.l0.floor12"   ; run11 r3c2
  30, 2, "t.l0.floor13"   ; run11 r3c3
  30, 3, "t.l0.floor14"   ; run11 r3c4
  30, 4, "t.l0.floor15"   ; run11 r3c5
  31, 0, "t.l0.inaccessible1"   ; run11 r4c1
  31, 1, "t.l0.inaccessible2"   ; run11 r4c2
  31, 2, "t.l0.inaccessible3"   ; run11 r4c3
  31, 3, "t.l0.inaccessible4"   ; run11 r4c4
  31, 4, "t.l0.inaccessible5"   ; run11 r4c5
  32, 0, "t.l0.forest_tundra1"   ; run9 r5c1
  32, 1, "t.l0.forest_tundra2"   ; run9 r5c2
  32, 2, "t.l0.forest_tundra3"   ; run9 r5c3
}
