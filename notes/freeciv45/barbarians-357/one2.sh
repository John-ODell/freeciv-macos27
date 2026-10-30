#!/bin/bash
# one.sh <seed> <out> <endturn>: civ45, one passive AI ('away') with 2 cities+1 warrior each, no other players
S=$1; O=$2; E=${3:-100}; X=${EXTRA:-}; mkdir -p $O; rm -f $O/in
A=$HOME/freeciv-builds/apps/Freeciv45.app/Contents
printf 'rulesetdir civ45\nset minplayers 0\nset aifill 0\nremove AI*1\nremove AI*2\nremove AI*3\nremove AI*4\nremove AI*5\nremove AI*6\nremove AI*7\nremove AI*8\nremove AI*9\nremove AI*10\nremove AI*11\nremove AI*12\ncreate Oscar\naway Oscar\nset endturn %s\nset timeout -1\nset gameseed %s\nset mapseed %s\nset startunits cccdwx\n%bset saveturns 20\nset autosaves "TURN|GAMEOVER"\nlua file /Users/johnodell/Desktop/freeciv-port/port/fcm/scripts/civ45-combat-log.lua\nlua file /Users/johnodell/Desktop/freeciv-port/port/runs/s345/barbwatch.lua\nlua file /Users/johnodell/Desktop/freeciv-port/port/runs/test-0067/'${PASSIVE:-passive.lua}'\nstart\n' $E ${GSEED:-$S} $S "$X" > $O/cmd
mkfifo $O/in
(cat $O/cmd; sleep 20; sleep 900) > $O/in & H=$!
FREECIV_DATA_PATH=${DP} perl -e 'alarm 900; exec @ARGV' $HOME/freeciv-builds/qt/bin/freeciv-server --saves $O --exit-on-end --port 5701 < $O/in > $O/server.log 2>&1
pkill -P $H sleep; kill $H 2>/dev/null; rm -f $O/in
