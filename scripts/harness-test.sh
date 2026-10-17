#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Play a game in which the harness hook (patch 0007, ai/default/daiharness.c) hands one AI player's build and
# research decisions to scripts/harness-chooser.py, then check them with scripts/harness-check.py. A control
# game on the same seeds without the harness variables must not mention the harness at all; the tested
# player's final score in both games is printed for comparison.
#
# usage: scripts/harness-test.sh PREFIX [--turns N] [--mode random|first] [--ruleset NAME] [--data DIR] [--port N]
#   PREFIX     install prefix (or its bin/) whose freeciv-server has patch 0007
#   --turns    game length, default 50
#   --mode     the chooser: random (default), or first, always the AI's own pick
#   --ruleset  default civ45, read from --data, default port/freeciv/data (the source tree)
# The chooser leaves question 3 unanswered and answers question 5 with an option that doesn't exist, so both
# fallbacks run. No model is involved. Logs go to logs/harness-<ruleset>-<time>/.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { sed -n '3,14p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
P="$1"; shift
BIN="$P"; [ -d "$P/bin" ] && BIN="$P/bin"
TURNS=50; MODE=random; RULESET=civ45; DATA="$ROOT/port/freeciv/data"; PORT=5720
while [ $# -gt 0 ]; do case "$1" in
  --turns) TURNS="$2"; shift;; --mode) MODE="$2"; shift;; --ruleset) RULESET="$2"; shift;;
  --data) DATA="$2"; shift;; --port) PORT="$2"; shift;; *) echo "unknown option $1"; exit 2;; esac; shift; done
[ -x "$BIN/freeciv-server" ] || { echo "no freeciv-server in $BIN"; exit 1; }
DATA="$(cd "$DATA" 2>/dev/null && pwd)"
[ -f "$DATA/$RULESET/game.ruleset" ] || { echo "no $RULESET/game.ruleset in ${DATA:-the --data directory}"; exit 1; }
OUT="$ROOT/logs/harness-$RULESET-$(date +%Y%m%d-%H%M%S)"; [ -e "$OUT" ] && OUT="$OUT-$$"
PLAYER=Tested; SKIP=3; BAD=5; FAIL=0
mkdir -p "$OUT/game/harness" "$OUT/control"
echo "== harness test: $RULESET from $DATA, $TURNS turns, chooser $MODE -> $OUT"

# start_game NAME TURNS PORT [VAR=VALUE...]: an autogame with one created AI player and two from aifill. Only the
# variables given turn the hook on; any FREECIV_HARNESS_* in the caller's environment are dropped.
start_game() {
  local dir="$OUT/$1" turns="$2" port="$3"; shift 3
  cat > "$dir/game.serv" <<EOS
rulesetdir $RULESET
set minplayers 0
set aifill 3
set size 2
set endturn $turns
set timeout -1
set gameseed 7
set mapseed 7
set saveturns 10
create $PLAYER
EOS
  rm -f "$dir/fifo"; mkfifo "$dir/fifo"
  env -u FREECIV_HARNESS_DIR -u FREECIV_HARNESS_PLAYERS -u FREECIV_HARNESS_TIMEOUT FREECIV_DATA_PATH="$DATA" "$@" \
    "$BIN/freeciv-server" -p "$port" --Announce none --read "$dir/game.serv" --saves "$dir" -e \
    < "$dir/fifo" > "$dir/server.log" 2>&1 &
  SPID=$!
  # 'start' has to come on the console after the settings file; keep the FIFO open until the server exits.
  exec 3>"$dir/fifo"
  sleep 4; echo start >&3
}

# wait_game NAME LIMIT: wait for the server to end the game and exit.
wait_game() {
  local dir="$OUT/$1" limit="$2" start rc
  start=$(date +%s)
  while kill -0 "$SPID" 2>/dev/null; do
    if [ $(( $(date +%s) - start )) -gt "$limit" ]; then
      echo "$1: FAILED, no end after ${limit}s, killing"; kill "$SPID"; FAIL=1; break
    fi
    sleep 2
  done
  wait "$SPID"; rc=$?
  exec 3>&-; rm -f "$dir/fifo"
  [ "$rc" = 0 ] || { echo "$1: FAILED, server exit $rc (see $dir/server.log)"; FAIL=1; }
}

# 1. The harness game.
START=$(date +%s)
start_game game "$TURNS" "$PORT" FREECIV_HARNESS_DIR="$OUT/game/harness" FREECIV_HARNESS_PLAYERS="$PLAYER" \
  FREECIV_HARNESS_TIMEOUT=3
python3 "$ROOT/scripts/harness-chooser.py" "$OUT/game/harness" --mode "$MODE" --seed 7 \
  --log "$OUT/game/chooser.jsonl" --keep "$OUT/game/questions" --skip "$SKIP" --bad "$BAD" --pid "$SPID" \
  > "$OUT/game/chooser.out" 2>&1 &
CPID=$!
wait_game game 1200
wait "$CPID" || { echo "chooser: FAILED (see $OUT/game/chooser.out)"; FAIL=1; }
SECS=$(( $(date +%s) - START ))

# 2. The control game: the same settings and seeds, without the harness variables.
start_game control "$TURNS" "$((PORT+1))"
wait_game control 1200

echo "game: ${SECS}s, $(grep -c 'harness: q' "$OUT/game/server.log") decisions in the server log"
if grep -q "harness: on for $PLAYER" "$OUT/game/server.log"; then echo "hook: ok, on for $PLAYER"
else echo "hook: FAILED, no 'harness: on' line in $OUT/game/server.log"; FAIL=1; fi
if grep -E "harness: (there is no|can't|FREECIV_)|isn't AI-controlled" "$OUT/game/server.log"; then
  echo "hook: FAILED, the lines above are errors"; FAIL=1
fi
touch "$OUT/game/chooser.jsonl" "$OUT/game/harness/applied.jsonl"
python3 "$ROOT/scripts/harness-check.py" "$OUT/game" --player "$PLAYER" --turns "$TURNS" --skip "$SKIP" --bad "$BAD" \
  --control "$OUT/control" || FAIL=1
# The control game must not mention the harness at all.
N="$(grep -c "harness: " "$OUT/control/server.log")"
if [ "$N" = 0 ] && grep -q "Game ended" "$OUT/control/server.log"; then echo "control: ok, $TURNS turns, no harness lines"
else echo "control: FAILED, $N harness lines or no game end (see $OUT/control/server.log)"; FAIL=1; fi

echo "== result: $([ $FAIL = 0 ] && echo PASS || echo FAIL) ($OUT)"
exit $FAIL
