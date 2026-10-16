#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# See a ruleset in a real client: a local server reads its rulesets from the source tree, so a ruleset that is in
# no build or bundle yet can be played; a client autoconnects, and every client window is captured at pregame and
# at turn 1. The client runs on its own options file in <outdir>, so the player's options are never written.
#
# Usage: scripts/ruleset-look.sh <client> <outdir> [--ruleset NAME] [--port N] [--data DIR] [--options FILE]
#                                [-- client args...]
#   <client>   the bundle's launcher (~/freeciv-builds/apps/Freeciv.app/Contents/MacOS/Freeciv) or a client
#              binary (~/freeciv-builds/qt/bin/freeciv-qt); the freeciv-server next to it is used
#   --ruleset  ruleset directory to play (default civ45)
#   --data     FREECIV_DATA_PATH for the server only (default port/freeciv/data); the client keeps its own data
#   --options  client options file to start from, copied first; without it the client starts from its defaults
#   after --   client arguments, e.g. -- -t trident to force a tileset
# Output in <outdir>: 01-pregame-wN.png and 02-turn1-wN.png (N counts the client's windows), client.log,
# server.log, game.serv, the turn 1 autosave, and client.rc if the client saved its options.
set -u
[ $# -ge 2 ] || { sed -n '3,16p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
CLIENT="$1"; OUT="$2"; shift 2
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULESET=civ45; PORT=5710; DATA="$ROOT/port/freeciv/data"; OPTIONS=""
while [ $# -gt 0 ]; do case "$1" in
  --ruleset) RULESET="$2"; shift;; --port) PORT="$2"; shift;; --data) DATA="$2"; shift;;
  --options) OPTIONS="$2"; shift;; --) shift; break;; *) echo "unknown option $1"; exit 2;; esac; shift; done
[ -x "$ROOT/scripts/windows-of-pid" ] || swiftc -O "$ROOT/scripts/windows-of-pid.swift" -o "$ROOT/scripts/windows-of-pid"
SERVER="$(dirname "$CLIENT")/freeciv-server"
[ -x "$SERVER" ] || { echo "no freeciv-server next to $CLIENT"; exit 1; }
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"   # absolute: the server prefixes relative save paths with --saves
rm -f "$OUT"/*.png "$OUT"/fifo "$OUT"/client.rc
[ -z "$OPTIONS" ] || cp "$OPTIONS" "$OUT/client.rc"
cat > "$OUT/game.serv" <<EOS
rulesetdir $RULESET
set aifill 4
set timeout 0
set minp 1
set gameseed 7
set mapseed 7
EOS
mkfifo "$OUT/fifo"
FREECIV_DATA_PATH="$DATA" "$SERVER" -p "$PORT" --Announce none --read "$OUT/game.serv" --saves "$OUT" \
  < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!; exec 3>"$OUT/fifo"
sleep 4
FREECIV_OPT="$OUT/client.rc" "$CLIENT" -a -s localhost -p "$PORT" -n Look "$@" > "$OUT/client.log" 2>&1 &
CPID=$!   # the bundle's launcher execs the client, so this stays the client's pid
shot() { local i=0 W
  for W in $("$ROOT/scripts/windows-of-pid" $CPID | grep -v " 0x0 " | sed -E 's/window_id=([0-9]+).*/\1/'); do
    i=$((i+1)); screencapture -x -l "$W" "$OUT/$1-w$i.png" && echo "shot $1-w$i"; done; }
sleep 12; shot 01-pregame
echo start >&3
sleep 20; shot 02-turn1
echo quit >&3; sleep 4; exec 3>&-
kill $CPID 2>/dev/null; sleep 2; kill -9 $CPID 2>/dev/null; wait $SPID 2>/dev/null
grep -iE "tileset|topology|error" "$OUT/client.log" | head -10
