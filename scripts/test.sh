#!/bin/bash
# Smoke-test a Freeciv install: server autogame, then (for each client binary present) the FIFO-driven
# save/load/restart probe from scripts/game-probe.sh with per-window screenshots and crash-report diff.
#
# Usage: scripts/test.sh <prefix-or-bin-dir> [--turns N] [--no-client] [--port P]
#   e.g. scripts/test.sh ~/freeciv-builds/qt
# Output: <repo>/logs/test-<name>-<timestamp>/ ; exit status non-zero on any failure.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { sed -n '2,8p' "$0"; exit 1; }
P="$1"; shift
BIN="$P"; [ -d "$P/bin" ] && BIN="$P/bin"
TURNS=100; CLIENTS=1; PORT=5590
while [ $# -gt 0 ]; do case "$1" in --turns) TURNS="$2"; shift;; --no-client) CLIENTS=0;; --port) PORT="$2"; shift;; *) echo "unknown $1"; exit 1;; esac; shift; done
NAME="$(basename "$(cd "$BIN/.." && pwd)")"
OUT="$ROOT/logs/test-$NAME-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$OUT"
FAIL=0
echo "== test $NAME -> $OUT"

# 1. server autogame (timeout -1 = autogame; 'end' after TURNS turns; fixed seeds for reproducibility)
cat > "$OUT/autogame.serv" <<EOS
set aifill 10
set minplayers 0
set endturn $TURNS
set timeout -1
set gameseed 42
set mapseed 42
EOS
START=$(date +%s)
# 'start' must arrive on the console (stdin) after the rulesets are loaded, and stdin must stay open
# (on EOF the server stops reading it), so drive it through a FIFO held open until the server exits.
rm -f "$OUT/fifo"; mkfifo "$OUT/fifo"
"$BIN/freeciv-server" -p "$((PORT+1))" --Announce none --read "$OUT/autogame.serv" --saves "$OUT" -e < "$OUT/fifo" > "$OUT/autogame.log" 2>&1 &
SPID=$!
exec 3>"$OUT/fifo"
sleep 4; echo start >&3
LIMIT=${AUTOGAME_LIMIT:-900}
while kill -0 $SPID 2>/dev/null; do
  if [ $(( $(date +%s) - START )) -gt $LIMIT ]; then echo "autogame: FAILED, no end after ${LIMIT}s, killing"; kill $SPID; FAIL=1; break; fi
  sleep 2
done
wait $SPID; SRC=$?
exec 3>&-; rm -f "$OUT/fifo"
if [ $SRC = 0 ] && grep -q "Game ended as the turn limit" "$OUT/autogame.log"; then
  echo "autogame: ok, $TURNS turns, 10 AIs, $(( $(date +%s) - START )) s"
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
echo "== result: $([ $FAIL = 0 ] && echo PASS || echo FAIL) ($OUT)"
exit $FAIL
