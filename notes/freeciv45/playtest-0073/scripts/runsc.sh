#!/bin/bash
# runsc.sh <n> <scribble 0|1>
cd ~/Desktop/freeciv-port/port/runs/test-0073
export FREECIV_DRIVE_PREFIX=~/Desktop/freeciv-port/port/drv-0073/qt FREECIV_DRIVE_TILESET=freeciv45iso FREECIV_DRIVE_TILESETS=~/Desktop/freeciv-port/tilesets
[ "$2" = 1 ] && export MallocScribble=1
FREECIV_DRIVE_AIFILL=2 FREECIV_DRIVE_REVEAL= FREECIV_DRIVE_DISP= FREECIV_DRIVE_START="set startunits ccwwxdd" ./drive.sh sc$1.txt out-sc$1-s$2 573$1
