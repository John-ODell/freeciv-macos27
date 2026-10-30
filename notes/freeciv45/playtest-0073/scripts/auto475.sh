#!/bin/bash
# auto475.sh <seed> <out>: 12-AI civ45 autogame to turn 475, barbarians on (default), 0073 driver build's server
S=$1; O=$2; mkdir -p $O; rm -f $O/in
P=$HOME/Desktop/freeciv-port/port/drv-0073/qt
printf 'rulesetdir civ45\nset minplayers 0\nset aifill 12\nset endturn 475\nset timeout -1\nset gameseed %s\nset mapseed %s\nset saveturns 100\nset autosaves "TURN|GAMEOVER"\nlua file /Users/johnodell/Desktop/freeciv-port/port/fcm/scripts/civ45-combat-log.lua\nlua file /Users/johnodell/Desktop/freeciv-port/port/runs/s345/barbwatch.lua\nstart\n' $S $S > $O/cmd
mkfifo $O/in
(cat $O/cmd; sleep 5400) > $O/in & H=$!
FREECIV_DATA_PATH=$P/share/freeciv perl -e 'alarm 5400; exec @ARGV' $P/bin/freeciv-server --saves $O --exit-on-end --port 5744 < $O/in > $O/server.log 2>&1
pkill -P $H sleep; kill $H 2>/dev/null; rm -f $O/in
