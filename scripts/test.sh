#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Smoke-test a Freeciv install: server autogame, then (for each client binary present) the FIFO-driven
# save/load/restart probe from scripts/game-probe.sh with per-window screenshots and crash-report diff.
#
# Usage: scripts/test.sh <prefix-or-bin-dir> [--turns N] [--no-client] [--port P] [--ruleset NAME] [--data DIR] [--lua FILE] [--extra CMD]...
#   e.g. scripts/test.sh ~/freeciv-builds/qt
#   --data DIR  data path for the autogame server only, e.g. port/freeciv/data for the source tree's rulesets;
#               without it the server reads FREECIV_DATA_PATH or its installed data. The client probes keep theirs.
#   --lua FILE  a Lua script the autogame server loads before the game starts (e.g. an observer that logs combat)
#   --extra CMD a server command added to the autogame's setup, e.g. --extra "set diplomacy DISABLED" for a war game,
#               or --extra "set victories SPACERACE|CULTURE" to run civ45 past the ten AIs' allied win (issue 84)
# Output: <repo>/logs/test-<name>-<timestamp>/ ; exit status non-zero on any failure. The result line names the
# directory the autogame's ruleset was read from.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { sed -n '3,11p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
P="$1"; shift
BIN="$P"; [ -d "$P/bin" ] && BIN="$P/bin"
TURNS=100; CLIENTS=1; PORT=5590; RULESET=""; DATA=""; LUA=""; EXTRA=""
while [ $# -gt 0 ]; do case "$1" in --turns) TURNS="$2"; shift;; --no-client) CLIENTS=0;; --port) PORT="$2"; shift;; --ruleset) RULESET="$2"; shift;; --data) DATA="$2"; shift;; --lua) [ -f "$2" ] || { echo "no such file: $2"; exit 1; }; LUA="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; shift;; --extra) EXTRA="$EXTRA$2"$'\n'; shift;; *) echo "unknown $1"; exit 1;; esac; shift; done
NAME="$(basename "$(cd "$BIN/.." && pwd)")"
OUT="$ROOT/logs/test-$NAME-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$ROOT/logs"; mkdir "$OUT" 2>/dev/null || { OUT="$OUT-$$"; mkdir "$OUT"; }   # two runs in one second: mkdir is the atomic check
FAIL=0
echo "== test $NAME -> $OUT"

# The server reads <ruleset>/game.ruleset from the first directory on its data path that has one. The path is
# --data, else FREECIV_DATA_PATH, else the build's default ".:data:~/.freeciv/<x.y>:<prefix>/share/freeciv"
# (port/freeciv/meson.build:214), where "." and "data" are relative to the directory this script runs in.
DPATH="${DATA:-${FREECIV_DATA_PATH:-}}"
if [ -z "$DPATH" ]; then
  VER="$("$BIN/freeciv-server" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)"
  DPATH=".:data:$HOME/.freeciv/$VER:$(cd "$BIN/.." && pwd)/share/freeciv"
fi
RS="${RULESET:-civ2civ3}"; RSDIR=""   # civ2civ3: the server's default (common/game.h:676)
IFS=: read -ra DIRS <<<"$DPATH"
for d in "${DIRS[@]}"; do d="${d/#\~/$HOME}"; [ -f "$d/$RS/game.ruleset" ] && { RSDIR="$(cd "$d" && pwd)"; break; }; done
# A missing ruleset is an error the server shrugs off: it keeps its default and the autogame still passes.
[ -n "$RSDIR" ] || { echo "ruleset: FAILED, no $RS/game.ruleset on $DPATH"; echo "== result: FAIL ($OUT)"; exit 1; }
echo "ruleset: $RS from $RSDIR"
SENV=(); [ -z "$DATA" ] || SENV=("FREECIV_DATA_PATH=$DATA")

# 1. server autogame (timeout -1 = autogame; 'end' after TURNS turns; fixed seeds for reproducibility)
cat > "$OUT/autogame.serv" <<EOS
${RULESET:+rulesetdir $RULESET}
set aifill 10
set minplayers 0
set endturn $TURNS
set timeout -1
set gameseed 42
set mapseed 42
$EXTRA
EOS
START=$(date +%s)
# 'start' must arrive on the console (stdin) after the rulesets are loaded, and stdin must stay open
# (on EOF the server stops reading it), so drive it through a FIFO held open until the server exits.
rm -f "$OUT/fifo"; mkfifo "$OUT/fifo"
env ${SENV[@]+"${SENV[@]}"} "$BIN/freeciv-server" -p "$((PORT+1))" --Announce none --read "$OUT/autogame.serv" --saves "$OUT" -e < "$OUT/fifo" > "$OUT/autogame.log" 2>&1 &
SPID=$!
exec 3>"$OUT/fifo"
trap '' PIPE   # a server that quits at startup (a ruleset it cannot read) must not kill this script mid-write
sleep 4; [ -z "$LUA" ] || { echo "lua file $LUA" >&3; sleep 1; }   # loads only in pregame, before start
echo start >&3
LIMIT=${AUTOGAME_LIMIT:-900}
while kill -0 $SPID 2>/dev/null; do
  if [ $(( $(date +%s) - START )) -gt $LIMIT ]; then echo "autogame: FAILED, no end after ${LIMIT}s, killing"; kill $SPID; FAIL=1; break; fi
  sleep 2
done
wait $SPID; SRC=$?
exec 3>&-; rm -f "$OUT/fifo"
# The game ends at the turn limit or, earlier, by a victory (allied, conquest, culture, spaceship, or a
# ruleset script's "Scenario victory"); either is a finished game.
END=$(grep -oE "Game ended as the turn limit was exceeded|Game ended in [a-z ]*victory for .*|(Scenario|Allied|Team) victory to .*" "$OUT/autogame.log" | head -1)
# The final save is named for the turn after the last one played (endturn 20 writes freeciv-T0021-...-final).
LAST=$(ls "$OUT" | sed -n 's/^.*-T0*\([0-9][0-9]*\)-.*final.*$/\1/p' | tail -1)
[ -z "$LAST" ] || LAST=$((LAST - 1))
case "$END" in
  "Game ended as the turn limit was exceeded") HOW="reached the turn limit" ;;
  *) HOW="ended by a victory in turn ${LAST:-?}" ;;
esac
if [ $SRC = 0 ] && [ -n "$END" ]; then
  AIS=$(awk '$1 == "set" && $2 == "aifill" {n = $3} END {print n}' "$OUT/autogame.serv")   # the last one wins, as in the server
  echo "autogame: ok, $HOW, up to $TURNS turns, $AIS AIs, $(( $(date +%s) - START )) s; $END"
else
  echo "autogame: FAILED (exit $SRC; see $OUT/autogame.log)"; grep -E "Starting game|rror|Turn" "$OUT/autogame.log" | tail -3; FAIL=1
fi

# 2. client probes
if [ $CLIENTS = 1 ]; then
  for c in freeciv-qt freeciv-gtk4 freeciv-gtk3.22 freeciv-sdl2; do
    [ -x "$BIN/$c" ] || continue
    echo "-- probe $c"
    "$ROOT/scripts/game-probe.sh" "$BIN/$c" "$OUT/$c" "$PORT" > "$OUT/$c.probe.log" 2>&1
    PORT=$((PORT+2))
    R="$OUT/$c/run.txt"
    ok=1
    grep -q "server_exit=0" "$R" || ok=0
    ls "$OUT/$c"/probe1*.sav* >/dev/null 2>&1 || ok=0
    grep -q "no new crash reports" "$R" || ok=0
    grep -qE "shot 02-ingame|shot 05-after-reload-ingame" "$R" || ok=0
    grep -qE "Game saved|saved" "$OUT/$c/server.log" || ok=0
    if [ $ok = 1 ]; then echo "probe $c: ok (save/load/restart, no crash reports, $(ls "$OUT/$c"/*.png 2>/dev/null | wc -l | tr -d ' ') screenshots)"; else echo "probe $c: FAILED (see $OUT/$c/run.txt and $OUT/$c.probe.log)"; grep -E "crash|exit=|still" "$R"; FAIL=1; fi
  done
fi
echo "== result: $([ $FAIL = 0 ] && echo PASS || echo FAIL) ($RS from $RSDIR; $OUT)"
exit $FAIL
