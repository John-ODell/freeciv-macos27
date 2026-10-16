#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Run scripts/civ45-rules-test.lua in a civ45 game: load the test, start a 10-AI autogame on the civ45
# ruleset, print the CIV45TEST lines. Exit 0 only if every case passed.
# Usage: scripts/civ45-rules-test.sh <prefix-or-bin-dir> [--data DIR] [--port P]
#   --data  Freeciv data dir holding civ45 (default: port/freeciv/data, the source tree)
set -uo pipefail
[ $# -ge 1 ] || { sed -n '2,6p' "$0"; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$1"; shift; [ -d "$BIN/bin" ] && BIN="$BIN/bin"
DATA="$ROOT/port/freeciv/data"; PORT=5700
while [ $# -gt 0 ]; do case "$1" in --data) DATA="$2"; shift;; --port) PORT="$2"; shift;; *) echo "unknown $1"; exit 2;; esac; shift; done
OUT="$ROOT/logs/civ45-rules-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
cat > "$OUT/game.serv" <<EOS
rulesetdir civ45
set aifill 10
set minplayers 0
set endturn 40
set timeout -1
set gameseed 42
set mapseed 42
EOS
rm -f "$OUT/fifo"; mkfifo "$OUT/fifo"
FREECIV_DATA_PATH="$DATA" "$BIN/freeciv-server" -p "$PORT" --Announce none --read "$OUT/game.serv" \
  --saves "$OUT" -e < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!
exec 3>"$OUT/fifo"
trap '' PIPE   # the server may already have ended the game when we write to it
# Load the test in pregame: once an autogame (timeout -1) runs, the server reads no console input
# (server/sernet.c, "Don't wait if timeout == -1"). The test hooks itself to turn_begin and runs at turn 12.
sleep 4; echo "lua file $ROOT/scripts/civ45-rules-test.lua" >&3
sleep 1; echo start >&3
for _ in $(seq 1 180); do
  grep -q "CIV45TEST DONE" "$OUT/server.log" && break
  kill -0 $SPID 2>/dev/null || break
  sleep 1
done
kill -0 $SPID 2>/dev/null && echo quit >&3; exec 3>&-
wait $SPID 2>/dev/null; rm -f "$OUT/fifo"
grep "CIV45TEST" "$OUT/server.log" | sed 's/^[0-9]*: //'
grep -q "CIV45TEST DONE" "$OUT/server.log" || { echo "civ45-rules-test: no result (see $OUT/server.log)"; exit 1; }
grep -q "CIV45TEST FAIL" "$OUT/server.log" && exit 1
grep -q "CIV45TEST SKIP" "$OUT/server.log" && exit 1
exit 0
