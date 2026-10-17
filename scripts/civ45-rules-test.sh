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
for want in 'victory_min_points = 8000' 'victory_lead_pct   = 50' '"endturn", 475, FALSE' '"endspaceship", "ENABLED", FALSE' \
            'upgrade_veteran_loss     = 0' 'autoupgrade_veteran_loss = 0'; do
  if grep -qF "$want" "$RS"; then echo "FC45TEST PASS game.ruleset has $want"; else echo "FC45TEST FAIL game.ruleset lacks $want"; RC=1; fi
done
# The tech tree's shape (techs.ruleset; Lua has no class getter): seven era classes, and every advance in one.
TR="$DATA/civ45/techs.ruleset"
NC=$(grep -c '^\[techclass_' "$TR"); NA=$(grep -c '^\[advance_' "$TR"); NCL=$(grep -c '^class    = "' "$TR")
if [ "$NC" = 7 ] && [ "$NA" = 92 ] && [ "$NCL" = 92 ]; then echo "FC45TEST PASS techs.ruleset: 7 era classes, 92 advances, each in a class"
else echo "FC45TEST FAIL techs.ruleset: $NC classes, $NA advances, $NCL with a class (want 7, 92, 92)"; RC=1; fi
# The draft units cost a citizen (units.ruleset; Lua has no pop_cost getter).
for u in levy militia conscripts; do
  if sed -n "/^\[unit_$u\]/,/^\[unit_/p" "$DATA/civ45/units.ruleset" | grep -q '^pop_cost      = 1'; then
    echo "FC45TEST PASS units.ruleset: $u costs one citizen"; else echo "FC45TEST FAIL units.ruleset: $u lacks pop_cost 1"; RC=1; fi
done
# The roster's shape (units.ruleset): 83 unit types (76 of the roster and 7 great people), one strength number for attack and defence unless one of
# them is 0, firepower 1 everywhere, and City Walls keyed on the attacker's class flag rather than the Ground class.
UR="$DATA/civ45/units.ruleset"
NU=$(grep -c '^\[unit_' "$UR")
UNEVEN=$(awk '/^\[unit_/{n=$0} /^attack  *=/{a=$3} /^defense  *=/{d=$3} /^firepower  *=/{if ((a!=0 && d!=0 && a!=d) || $3!=1) print n}' "$UR" | tr '\n' ' ')
if [ "$NU" = 83 ] && [ -z "$UNEVEN" ]; then echo "FC45TEST PASS units.ruleset: 83 unit types, one strength each, firepower 1"
else echo "FC45TEST FAIL units.ruleset: $NU unit types, uneven or firepower not 1: $UNEVEN"; RC=1; fi
NW=$(grep -c '^\[effect_city_walls_\(melee\|archer\|mounted\|siege\)\]' "$DATA/civ45/effects.ruleset")
if [ "$NW" = 4 ] && ! grep -q '^\[effect_city_walls_0\]' "$DATA/civ45/effects.ruleset"; then
  echo "FC45TEST PASS effects.ruleset: City Walls are keyed on the attacker's class flag"
else echo "FC45TEST FAIL effects.ruleset: City Walls are not keyed on the attacker's class flag"; RC=1; fi
# Great people: the points table in script.lua mirrors the User_Effect_3 rows, and the counters are saved
# (scalar globals in the first autosave after the pledge case, written right after the test's first turn; the
# save after the second turn may not be written before the runner stops the server).
if python3 -I "$ROOT/scripts/gp-points-check.py" "$DATA/civ45" >/dev/null 2>&1; then
  echo "FC45TEST PASS script.lua's great-person sources match the User_Effect_3 rows"
else echo "FC45TEST FAIL script.lua's great-person sources differ from the User_Effect_3 rows"; RC=1; fi
if grep -q "FC45TEST golden age:" "$OUT/server.log"; then
  T=$(awk '/FC45TEST golden age:/{f=1} f && /^Game saved as .*auto\.sav\.gz/{print $4; exit}' "$OUT/server.log")
  # grep -c, not -q: with pipefail, -q's early exit would fail the pipeline through gzip's SIGPIPE.
  if [ -n "$T" ] && [ "$(gzip -dc "$T" 2>/dev/null | grep -c '^fc45_golden_count_[0-9]*=1')" -gt 0 ]; then
    echo "FC45TEST PASS the great-person counters are in the autosave ($(basename "$T"))"
  else echo "FC45TEST FAIL no great-person counter in the autosave after the test"; RC=1; fi
fi
# The 30 shields a disbanded Levy gave Testerburg, in the first autosave written after the test (the server
# autosaves right after a turn's start, so that save holds the test's actions but not yet the city's own
# production or a finished build, which would reset the count).
if grep -q "FC45TEST expect disbanded shields" "$OUT/server.log"; then
  T=$(awk '/FC45TEST expect disbanded shields/{f=1} f && /^Game saved as .*auto\.sav\.gz/{print $4; exit}' "$OUT/server.log")
  GOT=$(python3 -I "$ROOT/scripts/civ45-draft-summary.py" --city Testerburg disbanded_shields "$T" 2>/dev/null)
  if [ "$GOT" = 30 ]; then echo "FC45TEST PASS the disbanded Levy put 30 shields into Testerburg's build ($(basename "$T"))"
  else echo "FC45TEST FAIL Testerburg's disbanded_shields is '${GOT:-missing}' in ${T:-no autosave}"; RC=1; fi
fi
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
