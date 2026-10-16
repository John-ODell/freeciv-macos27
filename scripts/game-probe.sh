#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Drive a client through a real game without GUI clicks: local server + autoconnect client,
# server-side start / save / load / quit sent over a FIFO. Captures per-window screenshots.
# Usage: game-probe.sh <client-binary> <outdir> <port>
set -u
CLIENT="$1"; OUT="$2"; PORT="$3"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -x "$ROOT/scripts/windows-of-pid" ] || swiftc -O "$ROOT/scripts/windows-of-pid.swift" -o "$ROOT/scripts/windows-of-pid"
SERVER="$(dirname "$CLIENT")/freeciv-server"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"   # absolute: the server prefixes relative 'save' paths with --saves
rm -f "$OUT"/*.png "$OUT"/*.sav* "$OUT"/fifo
cat > "$OUT/game.serv" <<EOS
set aifill 4
set timeout 0
set minp 1
set gameseed 7
set mapseed 7
EOS
BEFORE=$(ls ~/Library/Logs/DiagnosticReports/ 2>/dev/null | sort)
mkfifo "$OUT/fifo"
"$SERVER" -p "$PORT" --Announce none --read "$OUT/game.serv" --saves "$OUT" < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!
exec 3>"$OUT/fifo"
cmd() { echo ">>> $1" | tee -a "$OUT/run.txt"; echo "$1" >&3; }
sleep 4
"$CLIENT" -a -s localhost -p "$PORT" -n Probe > "$OUT/client.log" 2>&1 &
CPID=$!
echo "server=$SPID client=$CPID" | tee "$OUT/run.txt"
shot() { local WID=$($ROOT/scripts/windows-of-pid $CPID | grep -v " 0x0 " | head -1 | sed -E 's/window_id=([0-9]+).*/\1/'); $ROOT/scripts/windows-of-pid $CPID >> "$OUT/run.txt"; [ -n "$WID" ] && screencapture -x -l "$WID" "$OUT/$1.png" && echo "shot $1 wid=$WID" | tee -a "$OUT/run.txt"; }
sleep 12; shot 01-pregame
cmd "list"
cmd "start"
sleep 25; shot 02-ingame
sample $CPID 2 -file "$OUT/sample-ingame.txt" >/dev/null 2>&1
cmd "save $OUT/probe1"
sleep 6; ls "$OUT"/probe1* >> "$OUT/run.txt" 2>&1; shot 03-after-save
SAV=$(ls "$OUT"/probe1* 2>/dev/null | head -1)
cmd "load $SAV"
sleep 8; shot 04-after-load-pregame
cmd "start"
sleep 25; shot 05-after-reload-ingame
cmd "quit"
sleep 8; shot 06-after-server-quit
exec 3>&-
wait $SPID; echo "server_exit=$?" | tee -a "$OUT/run.txt"
sleep 2
if kill -0 $CPID 2>/dev/null; then echo "client still running after server quit (expected: shows disconnect)" | tee -a "$OUT/run.txt"; kill $CPID; sleep 3; if kill -0 $CPID 2>/dev/null; then echo "client ignored SIGTERM, SIGKILL" | tee -a "$OUT/run.txt"; kill -9 $CPID; fi; wait $CPID 2>/dev/null; echo "client_exit=$?" | tee -a "$OUT/run.txt"; else wait $CPID; echo "client_exit=$?" | tee -a "$OUT/run.txt"; fi
rm -f "$OUT/fifo"
AFTER=$(ls ~/Library/Logs/DiagnosticReports/ 2>/dev/null | sort)
NEW=$(comm -13 <(echo "$BEFORE") <(echo "$AFTER")); if [ -n "$NEW" ]; then echo "NEW CRASH REPORTS: $NEW" | tee -a "$OUT/run.txt"; for f in $NEW; do cp ~/Library/Logs/DiagnosticReports/$f "$OUT/"; done; else echo "no new crash reports" | tee -a "$OUT/run.txt"; fi
echo "--- saves:"; ls -la "$OUT"/*.sav* 2>/dev/null
echo "--- server log (key lines):"; grep -nE "Game saved|Loading|loaded|Starting game|has connected|Lost|error|Error|Turn|quit|Game ended|rules the" "$OUT/server.log" | head -30
echo "--- client log:"; grep -vE "^3:     [0-9]+: " "$OUT/client.log" | head -30
