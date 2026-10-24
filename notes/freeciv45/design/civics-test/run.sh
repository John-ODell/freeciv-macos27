#!/bin/bash
# run.sh <save> <name> <L> <T> <F> <S>: one variant of the turn-120 save, two turns, score log on
W=~/Desktop/freeciv-port/port; D=$W/runs/civics/fx/$2; rm -rf "$D"; mkdir -p "$D"
python3 -I $W/runs/civics/fx/variant.py "$1" "$D/in.sav.gz" player${FXPLAYER:-2} "$3" "$4" "$5" "$6"
cat > "$D/cmd.serv" <<EOS
set scorelog enabled
set scorefile score.log
set endturn 122
set timeout -1
set autosaves ""
start
EOS
cd "$D" && FREECIV_DATA_PATH="${FXDATA:+$FXDATA:}$W/s61/data:$W/drv/qt/share/freeciv" perl -e 'alarm 240; exec @ARGV' \
  $W/drv/qt/bin/freeciv-server -p 5651 --Announce none -f "$D/in.sav.gz" --read "$D/cmd.serv" --saves "$D" -e \
  < /dev/null > "$D/server.log" 2>&1
echo "$2 rc=$?"
