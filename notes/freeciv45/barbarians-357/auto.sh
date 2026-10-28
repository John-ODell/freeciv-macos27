#!/bin/bash
# run.sh <datadir> <seed> <out>: 40-turn civ45 autogame, 12 AIs, saves at turn 40
D=$1; S=$2; O=$3; X=${EXTRA:-}; mkdir -p $O; rm -f $O/in
printf 'rulesetdir civ45\nset minplayers 0\nset aifill 12\nset endturn 80\nset timeout -1\nset gameseed %s\nset mapseed %s\nset saveturns 80\nset autosaves "TURN|GAMEOVER"\n%blua file /Users/johnodell/Desktop/freeciv-port/port/fcm/scripts/civ45-combat-log.lua\nlua file /Users/johnodell/Desktop/freeciv-port/port/runs/s345/barbwatch.lua\nstart\n' $S $S "$X" > $O/cmd
mkfifo $O/in
(cat $O/cmd; sleep 1500) > $O/in & H=$!
FREECIV_DATA_PATH=$D perl -e 'alarm 1500; exec @ARGV' ${SERVER:-$HOME/freeciv-builds/qt/bin/freeciv-server} --saves $O --exit-on-end --port 56$((RANDOM%90+10)) < $O/in > $O/server.log 2>&1
pkill -P $H sleep; kill $H 2>/dev/null; rm -f $O/in
