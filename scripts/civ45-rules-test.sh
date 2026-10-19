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
for want in 'victory_min_points = 30000' 'victory_lead_pct   = 25' '"endturn", 475, FALSE' '"endspaceship", "ENABLED", FALSE' \
            'upgrade_veteran_loss     = 0' 'autoupgrade_veteran_loss = 0'; do
  if grep -qF "$want" "$RS"; then echo "FC45TEST PASS game.ruleset has $want"; else echo "FC45TEST FAIL game.ruleset lacks $want"; RC=1; fi
done
# The tech tree's shape (techs.ruleset; Lua has no class getter): seven era classes, and every advance in one.
TR="$DATA/civ45/techs.ruleset"
NC=$(grep -c '^\[techclass_' "$TR"); NA=$(grep -c '^\[advance_' "$TR"); NCL=$(grep -c '^class    = "' "$TR")
if [ "$NC" = 7 ] && [ "$NA" = 95 ] && [ "$NCL" = 95 ]; then echo "FC45TEST PASS techs.ruleset: 7 era classes, 95 advances, each in a class"
else echo "FC45TEST FAIL techs.ruleset: $NC classes, $NA advances, $NCL with a class (want 7, 95, 95)"; RC=1; fi
# The era cost curve (decision 10, John 2026-10-17; eras V to VII lowered to 200 for issue 167): 100, 150, 175, 200, 200, 200, 200.
PCT=$(grep "^cost_pct" "$TR" | awk '{print $3}' | tr "\n" " ")
if [ "$PCT" = "100 150 175 200 200 200 200 " ]; then echo "FC45TEST PASS techs.ruleset: era cost_pct 100 150 175 200 200 200 200"
else echo "FC45TEST FAIL techs.ruleset: era cost_pct is $PCT"; RC=1; fi
# The draft units cost a citizen (units.ruleset; Lua has no pop_cost getter).
for u in levy militia conscripts; do
  if sed -n "/^\[unit_$u\]/,/^\[unit_/p" "$DATA/civ45/units.ruleset" | grep -q '^pop_cost      = 1'; then
    echo "FC45TEST PASS units.ruleset: $u costs one citizen"; else echo "FC45TEST FAIL units.ruleset: $u lacks pop_cost 1"; RC=1; fi
done
# A draft leaves the city 3 citizens and a whip 2 (issue 158): MinSize 4 on Militia and Conscripts, 3 on the Levy.
for p in levy:3 militia:4 conscripts:4; do
  if sed -n "/^\[unit_${p%%:*}\]/,/^\[unit_/p" "$DATA/civ45/units.ruleset" | grep -q "\"MinSize\", \"${p##*:}\", \"City\", TRUE"; then
    echo "FC45TEST PASS units.ruleset: ${p%%:*} needs a city of size ${p##*:}"; else echo "FC45TEST FAIL units.ruleset: ${p%%:*} lacks MinSize ${p##*:}"; RC=1; fi
done
# The roster's shape (units.ruleset): 85 unit types (78 of the roster and 7 great people), one strength number for attack and defence unless one of
# them is 0, firepower 1 everywhere, and City Walls keyed on the attacker's class flag rather than the Ground class.
UR="$DATA/civ45/units.ruleset"
NU=$(grep -c '^\[unit_' "$UR")
UNEVEN=$(awk '/^\[unit_/{n=$0} /^attack  *=/{a=$3} /^defense  *=/{d=$3} /^firepower  *=/{if ((a!=0 && d!=0 && a!=d) || $3!=1) print n}' "$UR" | tr '\n' ' ')
if [ "$NU" = 85 ] && [ -z "$UNEVEN" ]; then echo "FC45TEST PASS units.ruleset: 85 unit types, one strength each, firepower 1"
else echo "FC45TEST FAIL units.ruleset: $NU unit types, uneven or firepower not 1: $UNEVEN"; RC=1; fi
# No BadCityDefender unit is a city defender for the AI (issue 187): none carries DefendGood or DefendOk.
BAD=$(awk '/^\[unit_/{n=$0; f=0} /^flags/{f=($0 ~ /BadCityDefender/)} /^roles/{if (f && $0 ~ /Defend(Good|Ok)/) print n}' "$UR" | tr "\n" " ")
if [ -z "$BAD" ]; then echo "FC45TEST PASS units.ruleset: no BadCityDefender unit has a defend role"
else echo "FC45TEST FAIL units.ruleset: BadCityDefender units with a defend role: $BAD"; RC=1; fi
# Transport cargo 4 and the Horses gate on the seven mounted units (decision 11, John 2026-10-17); Lua reads neither.
if sed -n "/^\[unit_transport\]/,/^\[unit_/p" "$UR" | grep -q '^transport_cap = 4'; then echo "FC45TEST PASS units.ruleset: a Transport carries 4"
else echo "FC45TEST FAIL units.ruleset: the Transport's transport_cap is not 4"; RC=1; fi
NH=$(grep -c '"Extra", "Horses", "City"' "$UR")
if [ "$NH" = 7 ] && grep -q '^\[extra_horses\]' "$DATA/civ45/terrain.ruleset" && grep -q '^\[resource_horses\]' "$DATA/civ45/terrain.ruleset"; then
  echo "FC45TEST PASS Horses is a resource and seven mounted units need it in the city's radius"
else echo "FC45TEST FAIL Horses: $NH units need it (want 7), or terrain.ruleset lacks the extra or resource"; RC=1; fi
# The AIs play at Normal (issue 159): game.ruleset sets ailevel, and the server gives it to the AIs made before.
if grep -qF '"ailevel", "Normal", FALSE' "$RS"; then echo "FC45TEST PASS game.ruleset sets ailevel Normal"
else echo "FC45TEST FAIL game.ruleset does not set ailevel Normal"; RC=1; fi
NW=$(grep -c '^\[effect_city_walls_\(melee\|archer\|mounted\|siege\)\]' "$DATA/civ45/effects.ruleset")
if [ "$NW" = 4 ] && ! grep -q '^\[effect_city_walls_0\]' "$DATA/civ45/effects.ruleset"; then
  echo "FC45TEST PASS effects.ruleset: City Walls are keyed on the attacker's class flag"
else echo "FC45TEST FAIL effects.ruleset: City Walls are not keyed on the attacker's class flag"; RC=1; fi
# The Great Library shares techs with its owner only (issue 239): Tech_Parasite 2 at Player range, not a world-wide share.
GL=$(sed -n '/^\[effect_great_library\]/,/^\[effect_great_library_1\]/p' "$DATA/civ45/effects.ruleset")
if echo "$GL" | grep -q '"Tech_Parasite"' && echo "$GL" | grep -q '"Building", "Great Library", "Player"' && ! echo "$GL" | grep -q 'World'; then
  echo "FC45TEST PASS effects.ruleset: the Great Library gives techs to its owner only"
else echo "FC45TEST FAIL effects.ruleset: the Great Library is not owner-only"; RC=1; fi
# Space parts (issue 164): the tech, the Apollo Program and a Factory are all they need, at 50, 100 and 200 shields.
BR="$DATA/civ45/buildings.ruleset"
for p in structural:50 component:100 module:200; do
  SEC=$(sed -n "/^\[building_space_${p%%:*}\]/,/^obsolete_by/p" "$BR")
  NB=$(echo "$SEC" | grep -c '"Building"'); FAC=$(echo "$SEC" | grep -c '"Building", "Factory", "City"')
  COST=$(sed -n "/^\[building_space_${p%%:*}\]/,/^\[building_/p" "$BR" | sed -n 's/^build_cost\t*= *//p')
  if [ "$NB" = 1 ] && [ "$FAC" = 1 ] && [ "$COST" = "${p##*:}" ]; then echo "FC45TEST PASS buildings.ruleset: Space ${p%%:*} needs only a Factory and costs ${p##*:}"
  else echo "FC45TEST FAIL buildings.ruleset: Space ${p%%:*} has $NB building reqs (Factory $FAC) and costs $COST (want 1, 1, ${p##*:})"; RC=1; fi
done
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
