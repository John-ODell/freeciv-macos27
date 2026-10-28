# Leader portraits in the diplomacy dialog (issue 347, patch 0068)

John's play test, 2026-10-27: "We need faces for the different countries/leaders".

## Art

The Freeciv45 art pack's leader run 1 (`freeciv45/15_leaders`): 12 invented rulers, one per nation of John's game
(Tupi, Celtic, Roman, Carthaginian, Hunnic, Korean, Egyptian, Japanese, Babylonian, Aztec, Mayan, Danish), each
painted full length and then as a sheet of six moods from that portrait, so the face matches. All 24 images were kept.
`tilesets/make-freeciv45iso-leaders.py` builds `freeciv45iso/leaders.jpg` (12 rows × 6 moods, 192 px cells; JPEG,
because the PNG was 4.4 MB and the JPEG is 0.75 MB) and `leaders.spec`. The full-length portraits are not shipped yet.

## Client (patch 0068)

- The meeting tab shows the other leader's portrait to the right of the two sides of the treaty, 192 px high
  (`client/gui-qt/diplodlg.cpp`, `update_portrait`, called on every update of the tab).
- Tags: `leader.<nation>.<male|female>.<mood>` first, then `leader.<nation>.<mood>`; `<nation>` is the nation's
  rule name in lower case with spaces as underscores. A later run with a ruler of each sex only adds tags.
- Mood, from the AI's love for us (`ai_common.love`, sent to every client; thresholds as in `love_text`,
  `common/player.c`): up to −50 % angry, up to −10 % annoyed, up to +10 % neutral, up to +50 % pleased, above that
  delighted; sad when it is at war with us although it likes us (above +10 %). Players start at war in Freeciv, so a
  first meeting is neutral. A human leader stays neutral. The tooltip is the AI's attitude.
- A nation with no portrait (any but the 12) shows the dialog as before.

## Test

`ui/leaders/tabs.txt` with the offscreen driver (`scripts/ui-drive.sh`, sound off): a civ45 game where the test
player is Roman, the AIs Egyptian, Danish and French; the Lua line gives the Romans Marco Polo's Embassy, a turn
passes (its contact effect applies at turn change), and the driver's new `meet` command asks each AI for a meeting
and `dtab` shows each tab. Screenshots: `ui/leaders/meeting-0.jpg` (Egyptian, neutral), `meeting-1.jpg` (Danish,
neutral), `meeting-2.jpg` (French, no portrait, as before).

A first run showed both queens sad: the first rule was "sad at war unless hostile", and players start at war.
Changed to "sad at war although it likes us" before the patch.

## Not checked

- The other five moods in a real game: they need an AI's attitude to move, which takes many turns. The mapping is
  the few lines above.
- The client on a real screen, and Retina sharpness (the pixmap is scaled to the screen's pixel ratio).
