#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Drive the Qt client from a script, for click and hover checks and screenshots on a Mac where scripted input
# from outside the process is refused (#87). A local civ45 server starts, a test build of the client autoconnects
# with the driver in notes/freeciv45/ui/bar-test/uidrive.diff switched on, the game starts, and the client runs
# the drive script line by line; shots and drive.log land in <outdir>.
#
# Usage: scripts/ui-drive.sh <drive-script> <outdir> [port] [theme]
#   FREECIV_DRIVE_PREFIX  install prefix of the driver build (required; see below)
#   port                  server port (default 5720); theme: Qt theme name (default NightStalker)
#
# The driver is test code and never goes into the fork or a release. Build it in a copy:
#   git -C port/freeciv archive HEAD | tar -x -C <copy>
#   git -C <copy> apply notes/freeciv45/ui/bar-test/uidrive.diff     (or patch -p1 -d <copy> < ...)
#   FREECIV_SRC=<copy> FREECIV_PREFIX_ROOT=<prefix-root> scripts/build.sh qt --no-install-deps
#   FREECIV_DRIVE_PREFIX=<prefix-root>/qt scripts/ui-drive.sh notes/freeciv45/ui/bar-test/bar.txt <outdir>
# build.sh overwrites logs/build-qt.log; put the real build's log back afterwards if it matters.
#
# The game: civ45, 3 AIs, seeds 42, map size 2, revealmap START, dispersion 0, startunits cwxdd (Settlers,
# Workers, Explorer, two defenders on one tile), the trident tileset (-t, so no tileset suggestion box), a
# throwaway HOME with a copy of ~/.freeciv/freeciv-client-rc-3.2. The client reads its options through a short
# relative FREECIV_OPT because the options path is a 256-byte buffer (client/options.c) and a long <outdir>
# truncates it. The connection gets cmdlevel admin after the start, so "chat /lua cmd ..." lines work.
# The client runs offscreen (QT_QPA_PLATFORM=offscreen on a 1600x1000 1x screen), so no window opens over the
# desktop; UI_DRIVE_VISIBLE=1 shows the window instead, and clicking into it then changes the run.
set -u
[ $# -ge 2 ] || { sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
SCRIPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$2"; PORT="${3:-5720}"; THEME="${4:-NightStalker}"
BIN="${FREECIV_DRIVE_PREFIX:?set FREECIV_DRIVE_PREFIX to the install prefix of the driver build}/bin"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"
# Only an empty folder or an earlier run's output is cleared
if [ -n "$(ls -A "$OUT")" ] && [ ! -f "$OUT/drive.log" ] && [ ! -f "$OUT/game.serv" ]; then
  echo "$OUT is not empty and holds no earlier run; pick a new folder"; exit 1
fi
rm -rf "${OUT:?}"/*; mkdir -p "$OUT/home/.freeciv"
if [ -f ~/.freeciv/freeciv-client-rc-3.2 ]; then
  sed -e "s/^gui_qt_default_theme_name=.*/gui_qt_default_theme_name=\"$THEME\"/" \
      ~/.freeciv/freeciv-client-rc-3.2 > "$OUT/home/.freeciv/freeciv-client-rc-3.2"
else
  printf '[client]\ngui_qt_default_theme_name="%s"\n' "$THEME" > "$OUT/home/.freeciv/freeciv-client-rc-3.2"
fi
mkfifo "$OUT/fifo"
cat > "$OUT/game.serv" <<SERV
rulesetdir civ45
set aifill 3
set timeout 0
set minp 1
set gameseed 42
set mapseed 42
set size 2
set revealmap START
set dispersion 0
set startunits cwxdd
SERV
HOME="$OUT/home" "$BIN/freeciv-server" -p "$PORT" --Announce none --read "$OUT/game.serv" --saves "$OUT" \
  < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
SPID=$!
( exec sleep 1800 ) > "$OUT/fifo" &
HPID=$!
sleep 3
if [ "${UI_DRIVE_VISIBLE:-0}" = 1 ]; then
  QPA="${QT_QPA_PLATFORM:-}"
else
  cat > "$OUT/offscreen.json" <<'JSON'
{ "windowFrameMargins": false,
  "screens": [ { "name": "drive", "x": 0, "y": 0, "width": 1600, "height": 1000,
                 "logicalDpi": 96, "logicalBaseDpi": 96, "dpr": 1 } ] }
JSON
  QPA="offscreen:configfile=$OUT/offscreen.json"
fi
( cd "$OUT" && if [ -n "$QPA" ]; then export QT_QPA_PLATFORM="$QPA"; fi
  HOME="$OUT/home" FREECIV_OPT=home/.freeciv/freeciv-client-rc-3.2 FREECIV_UI_DRIVE="$SCRIPT" \
  FREECIV_UI_DRIVE_OUT="$OUT" exec "$BIN/freeciv-qt" -a -s localhost -p "$PORT" -n Probe -t trident \
  > "$OUT/client.log" 2>&1 ) &
CPID=$!
sleep 10
echo start > "$OUT/fifo"
sleep 8
echo "cmdlevel admin Probe" > "$OUT/fifo"
# The driver writes "== quit" instead of quitting: leaving a running game opens a confirmation box.
for i in $(seq 1 400); do
  kill -0 $CPID 2>/dev/null || break
  grep -q "^== quit" "$OUT/drive.log" 2>/dev/null && break
  sleep 1
done
{ kill $CPID; sleep 1; kill -9 $CPID; wait $CPID; } 2>/dev/null
echo quit > "$OUT/fifo"; sleep 1
{ kill $SPID $HPID; wait $SPID $HPID; } 2>/dev/null
rm -f "$OUT/fifo"
echo "done after ${i}s: $(grep -c '^> ' "$OUT/drive.log" 2>/dev/null || echo 0) lines run, log $OUT/drive.log"
