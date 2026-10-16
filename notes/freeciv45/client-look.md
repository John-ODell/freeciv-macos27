# Freeciv45 in the Qt client (issue 50, 2026-10-16)

How civ45, the ruleset of Freeciv45 (patch 0006), looks in the bundled Qt client. Checked with
`scripts/ruleset-look.sh ~/freeciv-builds/apps/Freeciv.app/Contents/MacOS/Freeciv OUT`, once with the client's
options at their defaults and once with `-- -t trident`. The bundle is v3.2.6-mac1 and carries no civ45 of its own,
so the script's server reads the rulesets from `port/freeciv/data`; the client is the bundle's, with its own data.
Seeds 7 and 7 with aifill 4, as in `scripts/game-probe.sh`. Screenshots and logs are in
`logs/look-civ45-20261016-181139/` (git-ignored, not committed). An earlier run with John's own client options and
the build's client in `~/freeciv-builds/qt` looked the same.

## What a new player sees

1. At pregame a dialog: "Modpack suggests using trident tileset. It might not work with other tilesets. You are
   currently using tileset hexemplio.", with Keep current tileset and Load tileset (observed,
   `default/01-pregame-w1.png`). Auto-accept is off by default (`client/options.c:153`), so everyone sees it.
2. Behind the dialog the client switches to amplio2 by itself and logs `Loading tileset "amplio2"` (observed,
   `default/client.log`). It starts on hexemplio because its default topology is iso-hex (`client/options.c:86`,
   `client/client_main.c:334-337`); the server sends the rulesets before the topology (`server/connecthand.c:191`
   and `:197-199`), so the dialog is written while hexemplio is loaded, and the topology packet then loads the
   tileset set for square maps (`client/packhand.c:2208-2224`). The dialog's "currently using" is stale by the time
   the player reads it (#53).
3. Keep current tileset, or no answer: amplio2's isometric diamonds on the square map, and a diamond minimap
   (observed, `default/02-turn1-w3.png`). The rules are the same, iso only changes the drawing; the client treats
   it as a soft mismatch (`client/mapview_common.c:4094-4096`). It is not the overhead square look the ruleset asks
   for.
4. Load tileset (or `-t trident`): overhead square tiles and a rectangular minimap. The start stack shows as
   "EXPLORER MP: 1 HP:10/10 +2 UNITS" (observed, `trident/02-turn1-w2.png`).

Nothing crashed. The client log has one warning worth its own fix: the bundle's client has no SVG support and draws
PNG flags, because `scripts/bundle.sh` copies no Qt SVG plugin (#54). On that path the client reads one element
before its image format list (`client/svgflag.c:89`), harmless as far as can be seen (#55).

## What it means for Freeciv45

- The suggestion dialog is the only thing between a new player and the isometric look. A ruleset cannot force a
  tileset, it can only suggest one (`[tileset] preferred`, `data/civ45/game.ruleset:71`; the client only offers or auto-accepts it,
  `client/packhand.c:3463-3472`).
- Trident is the stock overhead square tileset, so it is the stopgap until Freeciv45 has its own (look steps T0 to
  T2 in `notes/freeciv45-plan.md`). Whether Freeciv45 should be overhead at all is decision 3 in that plan; amplio2
  on a square map is what declining the suggestion gives today.
