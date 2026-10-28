#!/bin/bash
# sweep2.sh: map seed 7, game seeds 1-5, 1 Phalanx per city; today's rule (H30), NORMAL (N30), NORMAL from turn 40 (N40)
cd "$(dirname "$0")"
for g in 1 2 3 4 5; do
  GSEED=$g PASSIVE=pg1.lua EXTRA="" ./one.sh 7 H30-$g 100
  GSEED=$g PASSIVE=pg1.lua EXTRA="set barbarians NORMAL\n" ./one.sh 7 N30-$g 100
  GSEED=$g PASSIVE=pg1.lua EXTRA="set barbarians NORMAL\nset onsetbarbs 40\n" ./one.sh 7 N40-$g 100
done
