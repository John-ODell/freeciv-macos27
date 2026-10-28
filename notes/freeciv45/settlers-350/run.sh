#!/bin/bash
# run.sh <datadir> <seed> <out>: 40-turn civ45 autogame, 12 AIs, saves at turn 40
D=$1; S=$2; O=$3; mkdir -p $O; rm -f $O/in
printf 'rulesetdir civ45\nset minplayers 0\nset aifill 12\nset endturn 40\nset timeout -1\nset gameseed %s\nset mapseed %s\nset saveturns 40\nset autosaves "TURN|GAMEOVER"\nstart\n' $S $S > $O/cmd
mkfifo $O/in
(cat $O/cmd; sleep 900) > $O/in & H=$!
FREECIV_DATA_PATH=$D perl -e 'alarm 900; exec @ARGV' ~/freeciv-builds/qt/bin/freeciv-server --saves $O --exit-on-end --port 56$((RANDOM%90+10)) < $O/in > $O/server.log 2>&1
pkill -P $H sleep; kill $H 2>/dev/null; rm -f $O/in
