# Drag the map to pan it (patch 0042)

Date: 2026-10-18. Issue: #231. Goes onto the fork on top of patch 0034 (the map session's freeciv45iso work).

## What it does

- A left press on the map that starts no goto, followed by a drag past the platform's drag distance, pans the view
  grab-style: the ground under the pointer stays under the pointer. The cursor turns into a closed hand while it
  pans, and the map moves at once, with no slide.
- A press that stays within the drag distance is still a click: it selects and moves as before.
- A press and drag from the focus unit's own tile still sets a goto, with the goto line following the pointer.
- With an order mode on (G and the others, `hover_state` not none) the press takes the order and the drag does
  not pan.
- Two-finger trackpad scrolling pans the map with the fingers (Qt's pixel delta). A mouse wheel notch moves it a
  sixth of the view's height. The wheel with Ctrl or Cmd held is left alone.
- A pan ends without a click: the release selects nothing and gives no order, and the auto-centre option is put
  back as it was at the press.

### The keyboardless goto change

Stock Freeciv arms keyboardless goto on a left press anywhere on the map while a unit has focus: in
`do_map_click` a press sets `keyboardless_goto_button_down`, and a drag then becomes a goto from the focus unit to
wherever the pointer ends up. With that rule a pan could never start while a unit is in focus, which in a game is
almost always. The patch keeps keyboardless goto to presses on a focus unit's tile; a press elsewhere disarms it,
so the drag pans instead. The test driver had hidden this at first: offscreen, `QCursor::pos()` was (0, 0), off the
map, so the press never armed the goto at all. The driver now moves the cursor before each press.

## Files

| File | Change |
|---|---|
| `client/gui-qt/mapctrl.cpp` | The press arms a pan when no goto or order mode took it; keyboardless goto only from a focus unit's tile; the move pans past the drag distance; the release ends a pan without a click; `wheelEvent` pans |
| `client/gui-qt/mapview.h`, `mapview.cpp` | `pan_to` (sets the origin with no slide), the pan state and `wheelEvent` |

## Checked

- `scripts/build.sh qt --no-install-deps` on the driver's copy of the fork (patch 0042's sources plus the driver's
  four files, `bar-test/uidrive.diff`): 0 new compiler warnings.
- The test driver, `scripts/ui-drive.sh pan-test/pan.txt` and `pan-test/pan-vertical.txt`, civ45, freeciv45iso,
  NightStalker, offscreen on a 3456 x 2060 screen with `QT_SCALE_FACTOR=2` (1728 x 1030 pt, Retina 2x). The
  vertical run used `set mapsize XYSIZE`, `set xsize 40`, `set ysize 120`, since the default small map has no room
  to pan up and down. The driver gained `drag X Y DX DY`, `drag unit DX DY` (from the focus unit's tile centre) and
  `mapwheel DX DY [notch]`; the drags press, move in eight steps and release through the window. Origins are in
  canvas pixels, two to a point at 2x.

| Check | Result | Shot |
|---|---|---|
| Start, Warriors #115 in focus | Origin 2466,1440 | `pan-test/01-start.jpg` |
| Drag on open ground, 240 pt left and 120 pt down | Origin x +480 (the map followed the pointer); y held by the small map's top edge | `pan-test/02-dragged-left-down.jpg` |
| Drag back | Origin back to the start | log |
| Drag of 2,1 pt | No pan: a click | log |
| Trackpad 120 pt right | Origin x -240 | log |
| Trackpad back, mouse notch down and up | The map pans and comes back | log |
| Tall map, drag 200 pt up, then down | Origin y 3390 to 3790, then back to 3390 | log |
| Tall map, drag 160 pt right and 100 pt up | Origin x -320 (wrapping round the map), y +200 | `pan-test/05-vertical-diagonal.jpg` |
| Tall map, trackpad up and down | Origin y +240, then back | log |
| Drag from Warriors #115, 96 pt down | The map stays; #115 gets orders and moves to (9,26) | `pan-test/03-goto-drag.jpg` |
| G, then press and drag 240 pt left | The map stays; Warriors #114 gets the goto | `pan-test/04-goto-key.jpg` |

Not exercised: a real trackpad and mouse on John's screen (the driver sends the wheel events to the map), the
trackpad's momentum after the fingers lift (macOS sends those as more pixel deltas, which pan the same way), the
right-button recentre with a drag, overhead tilesets, and the autotools build.
