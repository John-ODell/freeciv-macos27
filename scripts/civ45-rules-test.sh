#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Run scripts/civ45-rules-test.lua in a civ45 (Freeciv45) game: load the test, start a 10-AI autogame on the
# civ45 ruleset with one human-controlled player ("Tester", no client attached), print the FC45TEST lines.
# Exit 0 only if every case passed and the server log holds no Lua error.
# Usage: scripts/civ45-rules-test.sh <prefix-or-bin-dir> [--data DIR] [--port P] [--extra CMD]...
#   --data   Freeciv data dir holding civ45 (default: port/freeciv/data, the source tree)
#   --extra  a server command added after the setup, e.g. --extra "set killstack enabled" for a control
#            run that must fail, or --extra "set endturn 6" to see the score winner named at the last turn (the test ends at turn 6)
set -uo pipefail
[ $# -ge 1 ] || { sed -n '2,8p' "$0"; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$1"; shift; [ -d "$BIN/bin" ] && BIN="$BIN/bin"
DATA="$ROOT/port/freeciv/data"; PORT=5700; EXTRA=""
while [ $# -gt 0 ]; do case "$1" in --data) DATA="$2"; shift;; --port) PORT="$2"; shift;;
  --extra) EXTRA="$EXTRA$2"$'\n'; shift;; *) echo "unknown $1"; exit 2;; esac; shift; done
OUT="$ROOT/logs/civ45-rules-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
cat > "$OUT/game.serv" <<EOS
rulesetdir civ45
set aifill 10
set minplayers 0
set endturn 40
set timeout -1
set gameseed 42
set mapseed 42
create Tester
aitoggle Tester
$EXTRA
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
  grep -q "FC45TEST DONE" "$OUT/server.log" && break
  kill -0 $SPID 2>/dev/null || break
  sleep 1
done
# With endturn set to the turn the test finishes on, the game ends that turn with the ruleset's score
# winner: wait for the server's victory line before quitting.
if grep -q "FC45TEST expect victory" "$OUT/server.log"; then
  for _ in $(seq 1 90); do grep -q "victory to" "$OUT/server.log" && break; kill -0 $SPID 2>/dev/null || break; sleep 1; done
fi
kill -0 $SPID 2>/dev/null && echo quit >&3; exec 3>&-
wait $SPID 2>/dev/null; rm -f "$OUT/fifo"
grep "FC45TEST" "$OUT/server.log" | sed 's/^[0-9]*: //'
RC=0
# The victory keys Lua cannot read, checked in the ruleset file the server loaded.
RS="$DATA/civ45/game.ruleset"
for want in 'victory_min_points = 8000' 'victory_lead_pct   = 50' '"endturn", 475, FALSE' '"endspaceship", "ENABLED", FALSE'; do
  if grep -qF "$want" "$RS"; then echo "FC45TEST PASS game.ruleset has $want"; else echo "FC45TEST FAIL game.ruleset lacks $want"; RC=1; fi
done
if EXP=$(sed -n 's/.*FC45TEST expect victory to the \(.*\) (score.*/\1/p' "$OUT/server.log" | head -1) && [ -n "$EXP" ]; then
  if grep -q "Scenario victory to the $EXP\." "$OUT/server.log"; then echo "FC45TEST PASS the highest score, the $EXP, won at the last turn"
  else echo "FC45TEST FAIL no 'Scenario victory to the $EXP' in $OUT/server.log"; RC=1; fi
fi
grep -q "FC45TEST DONE" "$OUT/server.log" || { echo "civ45-rules-test: no result (see $OUT/server.log)"; RC=1; }
grep -q "FC45TEST FAIL\|FC45TEST SKIP" "$OUT/server.log" && RC=1
if grep -q "lua error" "$OUT/server.log"; then
  echo "civ45-rules-test: Lua errors in $OUT/server.log:"; grep -A2 "lua error" "$OUT/server.log" | head -12; RC=1
fi
exit $RC
