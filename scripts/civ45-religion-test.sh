#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Run scripts/civ45-religion-test.lua in a civ45 (Freeciv45) game: start a 4-AI autogame with one
# human-controlled player ("Tester", no client attached), print the FC45TEST lines, then check that the save the
# test makes once the faith has spread holds the religion record (holy city, founder, state faith).
# Exit 0 only if every case passed and the server log holds no Lua error.
# Usage: scripts/civ45-religion-test.sh <prefix-or-bin-dir> [--data DIR] [--port P]
#   --data   Freeciv data dir holding civ45 (default: port/freeciv/data, the source tree)
set -uo pipefail
[ $# -ge 1 ] || { sed -n '2,8p' "$0"; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$1"; shift; [ -d "$BIN/bin" ] && BIN="$BIN/bin"
DATA="$ROOT/port/freeciv/data"; PORT=5712
while [ $# -gt 0 ]; do case "$1" in --data) DATA="$2"; shift;; --port) PORT="$2"; shift;;
  *) echo "unknown $1"; exit 2;; esac; shift; done
OUT="$ROOT/logs/civ45-religion-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
cat > "$OUT/game.serv" <<EOS
rulesetdir civ45
set aifill 5
set minplayers 0
set endturn 95
set timeout -1
set gameseed 42
set mapseed 42
set compresstype PLAIN
create Tester
aitoggle Tester
EOS
rm -f "$OUT/fifo"; mkfifo "$OUT/fifo"
FREECIV_DATA_PATH="$DATA" "$BIN/freeciv-server" -p "$PORT" --Announce none --read "$OUT/game.serv" \
  --saves "$OUT" -e < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!
exec 3>"$OUT/fifo"
trap '' PIPE
# Load the test in pregame: an autogame (timeout -1) reads no console input once it runs.
sleep 4; echo "lua file $ROOT/scripts/civ45-religion-test.lua" >&3
sleep 1; echo start >&3
for _ in $(seq 1 600); do
  grep -q "FC45TEST DONE" "$OUT/server.log" && break
  kill -0 $SPID 2>/dev/null || break
  sleep 1
done
kill -0 $SPID 2>/dev/null && echo quit >&3; exec 3>&-
wait $SPID 2>/dev/null; rm -f "$OUT/fifo"
grep "FC45TEST" "$OUT/server.log" | sed 's/^[0-9]*: //'
RC=0
SAVE=$(ls "$OUT"/rel* 2>/dev/null | head -1)
for v in fc45_rel_founded_1 fc45_rel_holy_1 fc45_rel_state_; do
  if [ -n "$SAVE" ] && grep -q "$v" "$SAVE"; then echo "FC45TEST PASS the save holds $v"
  else echo "FC45TEST FAIL the save holds $v"; RC=1; fi
done
grep -q "FC45TEST FAIL" "$OUT/server.log" && RC=1
grep -q "FC45TEST DONE" "$OUT/server.log" || { echo "FC45TEST FAIL the test did not finish"; RC=1; }
grep -qi "lua error\|stack traceback" "$OUT/server.log" && { echo "FC45TEST FAIL Lua error in $OUT/server.log"; RC=1; }
echo "log: $OUT"
exit $RC
