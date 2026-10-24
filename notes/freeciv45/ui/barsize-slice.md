# The unit bar sized to its actions (patch 0046)

Date: 2026-10-18. Issue: #233. John: "The size of the bar for units is huge too. It only needs to fit the boxes that
contain a unit action, or possibly units' actions, and those boxes can stack." Follows the unit bar (patch 0015,
`first-slice.md`), its width fix (#129) and the shared actions for several units (#132).

## Why it was big

Not the fixed width of #129. That issue was a bar measured before its new chips and buttons were shown, and it
is fixed: the bar keeps no width of its own. The size came from the layout. The bar was one row of three things
side by side: the portrait (80 pt), a text column holding the stats line `str 1 / 1   moves 1   hp 10/10` as one
line, and a column of the chips over the actions. The row was as wide as all of them together, 467 to 495 pt
for a unit with four or five actions, while the actions themselves need 204 pt at most.

## What it does

The bar is one column now:

1. The portrait (56 pt, from 80) with the unit's lines to its right: name, rank and home city, moves and hit
   points, strength (and, with several units in focus, ", 3 selected" after it).
2. The chips of the units on the tile, only when the unit is not alone on it. A lone unit's portrait already
   shows it. They take the bar's width and wrap after it.
3. The action boxes: goto, fortify and sentry when every unit in focus can, wait and done. Nothing is reserved
   for an action that isn't there, and several selected units show the actions they share, as before.

The width is the widest of the action boxes (36 pt each, 6 pt apart), the unit's longest line with the
portrait, and the chip row, never more than six boxes' worth. Past that the boxes (and chips) wrap onto another
row and the bar grows downward instead. A line wider than its room is cut with an ellipsis and carries the whole
text as a tooltip.

| Case | Before | After |
|---|---|---|
| Warriors, 5 actions, a stack of 5 | 495 x 98 | 228 x 160 |
| Workers, 4 actions, a stack of 5 | 467 x 98 | 198 x 152 |
| 3 units selected, 4 shared actions | 582 x 98 | 202 x 152 |

The area falls by a quarter to a third (48.5k to 36.5k pt^2 for Warriors, 45.8k to 30.1k for Workers). The bar is
half as wide and 54 to 62 pt taller (152 to 160 pt, from 98), so it covers less of the map's width and a little more
of its height.

## Files

| File | Change |
|---|---|
| `client/gui-qt/unitbar.cpp`, `unitbar.h` | A column of header, chip grid and action grid in place of the row; the width worked out from its contents; `fill_grid`, `set_fitted`; the portrait at 56 pt |

No theme changes. `stats_label` became `moves_label` and `strength_label`; nothing outside the bar used it. The
translatable strings `moves %1  hp %2/%3`, `str %1 / %2` and `, %1 selected` replace `str %1 / %2   moves %3   hp
%4/%5` and `   (Selected %1 unit/units)`.

## Checked

- `scripts/build.sh qt --no-install-deps` on the driver's copy of the fork (patches 0042 and 0044 and this
  one, plus the driver's four files, `bar-test/uidrive.diff`): 0 compiler warnings.
- The test driver, `scripts/ui-drive.sh barsize-test/barsize.txt` (Warriors, Workers by W three times, three
  chips picked with shift), civ45, freeciv45iso, NightStalker, offscreen at 1440 x 900 (1x) and on a
  3456 x 2060 screen with `QT_SCALE_FACTOR=2` (1728 x 1030 pt). Before and after were taken with the same
  script; "before" is the build of patch 0044. The sizes above are the driver's `bar visible` lines, and the
  same at 1x and 2x.

| Check | Result | Shot |
|---|---|---|
| Warriors at 1440 x 900 | 572,674 228 x 160, was 438,736 495 x 98 | `before-1x-warriors.jpg`, `after-1x-warriors.jpg` |
| Warriors at 2x | 228 x 160 | `before-2x-warriors.jpg`, `after-2x-warriors.jpg` |
| Workers at 2x | 4 actions, no fortify: 198 x 152, was 467 x 98 | `before-2x-workers.jpg`, `after-2x-workers.jpg` |
| Three selected at 2x | The four shared actions, "str 0 / 1, 3 selected": 202 x 152, was 582 x 98 | `before-2x-three-selected.jpg`, `after-2x-three-selected.jpg` |
| The cap lowered to 3 boxes (driver build only) | Five boxes wrap 3 and 2, chips wrap too; 144 pt wide; the lines are cut to "moves ..." with the whole text in the tooltip | `wrap-3-columns-2x-warriors.jpg` |
| The old bar script, `bar-test/bar.txt`: every control, the hover tips, chips, shift-click, fortify, sentry, wait, done, goto, option off and on, the "+N" chip | All 79 lines ran, no failed step | log |

The six-box cap never wraps today, since no unit has more than five actions. The wrap was exercised with the cap
at 3 in a throwaway build.

Not exercised: a real mouse and a Retina laptop, the System, Classic and Necrophos themes, a long unit or city
name against the six-box cap, a translation with longer lines, a unit alone on its tile with no chip row (the start
map has a stack, so it wasn't shot), and the autotools build.
