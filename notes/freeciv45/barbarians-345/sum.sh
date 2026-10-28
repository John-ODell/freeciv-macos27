#!/bin/bash
# sum.sh <out dir>...: barbarian units seen (land/boat/sea), first turn, and cities barbarians took
for d in "$@"; do L=$d/server.log; B=$(grep FC45BARB $L | sed -E 's/.* of (.*) (land|sea|boat)$/\1/' | sort -u | paste -sd'|' -)
echo "== $(basename $d) errors $(grep -ci 'lua error\|stack traceback' $L) first $(grep -m1 FC45BARB $L | awk '{print $4}') units: $(grep FC45BARB $L | grep -v 'Barbarian Leader' | awk '{print $NF}' | sort | uniq -c | tr -s ' ' | tr '\n' ' ') uprisings: $(grep FC45BARB $L | grep -c 'Barbarian Leader')"
[ -n "$B" ] && echo "   taken by barbarians: $(grep FC45CITY $L | grep -E " to ($B) reason" | grep -c .)  barbarian attacks: $(grep FC45COMBAT $L | grep -E "of ($B) ->" | grep -c .)"
done
