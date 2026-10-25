#!/bin/bash
# Balance report 5 (night of 2026-10-24): win types alone, map types, and who wins. One game at a time.
# Usage: run.sh <turns> <name>... ; names are defined below; seeds from SEEDS (default "7 42").
W=~/Desktop/freeciv-port/port; N=$(cd "$(dirname "$0")" && pwd); cd $W/fcm
O=${OUT:-$W/runs/night5}; mkdir -p $O     # logs, done marks and progress.txt go here, not into the notes
{ echo "FC45_NO_DOMINATION = true"; cat $N/bias.lua; } > $O/bias-nodom.lua   # bias.lua with domination off
TURNS=$1; shift
for s in ${SEEDS:-7 42}; do for name in "$@"; do
  lua=$O/bias-nodom.lua; ex=()
  case $name in
    culture)    ex=(--extra "set victories CULTURE") ;;
    space)      ex=(--extra "set victories SPACERACE") ;;
    allied)     ex=(--extra "set victories ALLIED") ;;
    domination) ex=(--extra "set victories \"\""); lua=$N/bias.lua ;;
    conquest)   ex=(--extra "set victories \"\"") ;;
    islands)    ex=(--extra "set generator ISLAND" --extra "set startpos SINGLE"); lua=$N/bias.lua ;;
    pangaea)    ex=(--extra "set generator FRACTAL" --extra "set startpos ALL"); lua=$N/bias.lua ;;
    continents) ex=(--extra "set generator ISLAND" --extra "set startpos 2or3"); lua=$N/bias.lua ;;
    regular)    lua=$N/bias.lua ;;
    *) echo "unknown $name"; continue ;;
  esac
  log=$O/$name-s$s.log
  [ -f $O/$name-s$s.done ] && { echo "skip $name-s$s (done)"; continue; }
  AUTOGAME_LIMIT=6000 nice -n 10 scripts/test.sh $W/drv/qt --no-client --turns $TURNS --ruleset civ45 --port $((5800+s)) \
    --data "$W/s61/data:$W/drv/qt/share/freeciv" --lua $lua \
    --extra "set gameseed $s" --extra "set mapseed $s" "${ex[@]}" > $log 2>&1
  rc=$?
  echo "$(date +%H:%M) $name s$s rc=$rc $(grep -m1 -oE 'logs/test-[^ )]+' $log) $(grep '^autogame' $log)" | tee -a $O/progress.txt
  [ $TURNS -ge 400 ] && touch $O/$name-s$s.done
done; done
