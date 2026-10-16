#!/bin/bash
# Start a local server + autoconnecting client and bring it in-game, then leave both running.
# Usage: game-hold.sh <client-binary> <outdir> <port>   (server stdin stays open on <outdir>/fifo)
set -u
CLIENT="$1"; OUT="$2"; PORT="$3"
SERVER="$(dirname "$CLIENT")/freeciv-server"
mkdir -p "$OUT"; rm -f "$OUT/fifo"; mkfifo "$OUT/fifo"
printf 'set aifill 4\nset timeout 0\nset minp 1\nset gameseed 7\nset mapseed 7\n' > "$OUT/game.serv"
"$SERVER" -p "$PORT" --Announce none -F --read "$OUT/game.serv" --saves "$OUT" < "$OUT/fifo" > "$OUT/server.log" 2>&1 &
echo $! > "$OUT/server.pid"
( exec sleep 7200 ) > "$OUT/fifo" &
echo $! > "$OUT/holder.pid"
sleep 3
"$CLIENT" -a -s localhost -p "$PORT" -n Probe > "$OUT/client.log" 2>&1 &
echo $! > "$OUT/client.pid"
sleep 12
echo start > "$OUT/fifo"
sleep 15
echo "server=$(cat $OUT/server.pid) client=$(cat $OUT/client.pid)"
~/Desktop/freeciv-port/scripts/windows-of-pid $(cat "$OUT/client.pid")
