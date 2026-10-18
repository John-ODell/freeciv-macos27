#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# See a tileset in a real game and watch a unit move on it: a local server plays civ45 on a small revealed map
# and the Qt client autoconnects with the tileset forced. After the start the client's windows are captured;
# then the human player's first unit is moved one tile at a time from the server's Lua console (macOS does not
# let a script send keystrokes to the client without an Accessibility grant), with captures shortly after each
# move and again once it has settled, so a smooth move animation would show as a unit between two tiles.
#
# Usage: scripts/tileset-look.sh <outdir> [--tileset NAME] [--tilesets DIR] [--build DIR] [--port N]
#                                [--moves "e e e"] [--ruleset NAME] [--anim-msec N] [--rc LINE] [--serv LINE]
#                                [--at-start LINE] [-- client args...]
#   --tileset   tileset to force (default freeciv45test); --tilesets: a dir with its .tilespec, put first on
#               the client's FREECIV_DATA_PATH (default this repo's tilesets/)
#   --build     a build prefix with bin/freeciv-server and bin/freeciv-qt (default ~/freeciv-builds/qt); the
#               server reads the ruleset from that build's share/freeciv
#   --moves     directions (n s e w ne nw se sw) for the unit, one tile each (default "e e e"); a move onto
#               water or off the map is skipped and logged in server.log
#   --anim-msec the client's smooth_move_unit_msec (default 1500, so a move animation is long enough to capture)
#   --rc LINE   an extra line for the client's options file, e.g. "autoaccept_tileset_suggestion = TRUE"
#   --serv LINE an extra server command after the defaults (size 3, seeds 7), e.g. "set wetness 80" for a
#               map with more forest and jungle; repeat for several
#   --at-start LINE a server command sent once the game has started, 20 s before the captures, e.g. a "lua cmd ..."
#               that paints terrain around the first unit with edit.change_terrain; repeat for several
# Output in <outdir>: 01-start-wN.png (every window, including the tileset suggestion dialog), 02-map-wN.png,
# 03-move-K-DIR-{a,b,c}-wN.png (0.3 s, 0.8 s and 3 s after move K), client.log, server.log, game.serv, client.rc.
# Needs scripts/windows-of-pid (built if missing).
set -u
[ $# -ge 1 ] || { sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
OUT="$1"; shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TILESET=freeciv45test; TILESETS="$ROOT/tilesets"; BUILD="$HOME/freeciv-builds/qt"; PORT=5720
MOVES="e e e"; RULESET=civ45; ANIM=1500; RC=""; SERV=""; AT_START=""
while [ $# -gt 0 ]; do case "$1" in
  --tileset) TILESET="$2"; shift;; --tilesets) TILESETS="$2"; shift;; --build) BUILD="$2"; shift;;
  --port) PORT="$2"; shift;; --moves) MOVES="$2"; shift;; --ruleset) RULESET="$2"; shift;;
  --anim-msec) ANIM="$2"; shift;; --rc) RC="$RC
$2"; shift;; --serv) SERV="$SERV$2
"; shift;;
  --at-start) AT_START="$AT_START$2
"; shift;; --) shift; break;; *) echo "unknown option $1"; exit 2;; esac; shift; done
[ -x "$ROOT/scripts/windows-of-pid" ] || swiftc -O "$ROOT/scripts/windows-of-pid.swift" -o "$ROOT/scripts/windows-of-pid" || exit 1
SERVER="$BUILD/bin/freeciv-server"; CLIENT="$BUILD/bin/freeciv-qt"
[ -x "$SERVER" ] && [ -x "$CLIENT" ] || { echo "no freeciv-server and freeciv-qt under $BUILD/bin"; exit 1; }
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; rm -f "$OUT"/*.png "$OUT"/fifo
cat > "$OUT/game.serv" <<EOS
rulesetdir $RULESET
set aifill 4
set timeout 0
set minp 1
set gameseed 7
set mapseed 7
set size 3
set revealmap START
set borders ENABLED
EOS
printf '%s' "$SERV" >> "$OUT/game.serv"
printf '[client]\nsmooth_move_unit_msec = %d%s\n' "$ANIM" "$RC" > "$OUT/client.rc"
mkfifo "$OUT/fifo"
"$SERVER" -p "$PORT" --Announce none --read "$OUT/game.serv" --saves "$OUT" < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!; exec 3>"$OUT/fifo"; sleep 4
FREECIV_DATA_PATH="$TILESETS:$BUILD/share/freeciv" FREECIV_OPT="$OUT/client.rc" \
  "$CLIENT" -a -s localhost -p "$PORT" -n Look -t "$TILESET" "$@" > "$OUT/client.log" 2>&1 &
CPID=$!; sleep 10; echo start >&3; sleep 25
[ -n "$AT_START" ] && { printf '%s' "$AT_START" >&3; sleep 20; }   # land from sea resends the map per tile
shoot() { for W in $("$ROOT/scripts/windows-of-pid" $CPID | grep -v " 0x0 " | sed -E 's/window_id=([0-9]+).*/\1/'); do
  screencapture -x -l "$W" "$OUT/$1-w$W.png"; done; }
move() { case "$1" in n) D="0, -1";; s) D="0, 1";; e) D="1, 0";; w) D="-1, 0";; ne) D="1, -1";; nw) D="-1, -1";;
    se) D="1, 1";; sw) D="-1, 1";; *) echo "bad direction $1"; return;; esac
  echo "lua cmd local dx, dy = $D; for p in players_iterate() do if p:is_human() then for u in p:units_iterate() do local t = find.tile(u.tile.nat_x + dx, u.tile.nat_y + dy); if t and t.terrain:class_name() == \"Land\" then log.normal(\"tileset-look: %s from %d,%d to %d,%d\", u.utype:rule_name(), u.tile.nat_x, u.tile.nat_y, t.nat_x, t.nat_y); u:move(t, 0) else log.normal(\"tileset-look: %s stays at %d,%d, no land $1 of it\", u.utype:rule_name(), u.tile.nat_x, u.tile.nat_y) end; break end end end" >&3; }
shoot 01-start
WIN=$("$ROOT/scripts/windows-of-pid" $CPID | sed -E 's/window_id=([0-9]+) .* ([0-9]+)x[0-9]+ .*/\2 \1/' | sort -n | tail -1 | cut -d' ' -f2)   # the widest window: the map
shoot 02-map
N=0; for M in $MOVES; do N=$((N + 1)); move "$M"; sleep 0.3; screencapture -x -l "$WIN" "$OUT/03-move-$N-$M-a-w$WIN.png"
  sleep 0.5; screencapture -x -l "$WIN" "$OUT/03-move-$N-$M-b-w$WIN.png"; sleep 2.2; screencapture -x -l "$WIN" "$OUT/03-move-$N-$M-c-w$WIN.png"; done
echo quit >&3; sleep 3; exec 3>&-; kill $CPID 2>/dev/null; sleep 2; kill -9 $CPID 2>/dev/null; wait 2>/dev/null
rm -f "$OUT/fifo"; ls "$OUT"/*.png | sed "s|$OUT/||" | tr '\n' ' '; echo
grep "tileset-look" "$OUT/server.log"
grep -i -E "error|warning|sprite" "$OUT/client.log" | grep -v "qt.svg" | head -20
