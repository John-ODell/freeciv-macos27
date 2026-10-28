#!/bin/bash
# sum.sh <dir>...: cities Oscar lost, first barbarian turn, barbarian units seen
for d in "$@"; do
  L=$d/server.log
  lost=$(grep -c 'FC45CITY.*from Oscar' $L); first=$(grep -m1 -o 'FC45BARB turn [0-9]*' $L | grep -o '[0-9]*$')
  fl=$(grep -m1 -o 'FC45CITY turn [0-9]* .*from Oscar' $L | grep -o 'turn [0-9]*' | grep -o '[0-9]*')
  land=$(grep -c 'FC45BARB.* land$' $L); boat=$(grep -c 'FC45BARB.* boat$' $L)
  last=$(grep -o 'FC45STATE turn [0-9]*' $L | tail -1 | grep -o '[0-9]*$')
  echo "$d: lost $lost (first T${fl:--}), first barb T${first:--}, land $land, boat-borne $boat, last state T$last, errs $(grep -c 'Cannot even build' $L)"
done
