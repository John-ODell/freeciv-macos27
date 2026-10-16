#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Launch a Freeciv client binary for N seconds, capture stderr, a screenshot, a stack sample
# and any new crash report. Usage: launch-probe.sh <binary> <outdir> [seconds] [extra args...]
set -u
BIN="$1"; OUT="$2"; SECS="${3:-20}"; shift 3 || shift $#
mkdir -p "$OUT"
BEFORE=$(ls ~/Library/Logs/DiagnosticReports/ 2>/dev/null | sort)
"$BIN" "$@" > "$OUT/stderr.log" 2>&1 &
PID=$!
echo "pid=$PID bin=$BIN args=$*" | tee "$OUT/run.txt"
sleep "$SECS"
if kill -0 $PID 2>/dev/null; then
  echo "state=RUNNING after ${SECS}s" | tee -a "$OUT/run.txt"
  screencapture -x "$OUT/shot.png"
  sample $PID 2 -file "$OUT/sample.txt" >/dev/null 2>&1
  echo "--- main thread top frames:"; grep -m1 -A14 "Call graph" "$OUT/sample.txt" | tail -13
  echo "--- SIGTERM"; kill $PID; sleep 2
  if kill -0 $PID 2>/dev/null; then echo "still alive after SIGTERM, SIGKILL" | tee -a "$OUT/run.txt"; kill -9 $PID; fi
  wait $PID 2>/dev/null; echo "exit_after_term=$?" | tee -a "$OUT/run.txt"
else
  wait $PID; echo "state=EXITED early, exit=$?" | tee -a "$OUT/run.txt"
fi
AFTER=$(ls ~/Library/Logs/DiagnosticReports/ 2>/dev/null | sort)
NEW=$(comm -13 <(echo "$BEFORE") <(echo "$AFTER"))
if [ -n "$NEW" ]; then echo "NEW CRASH REPORTS: $NEW" | tee -a "$OUT/run.txt"; for f in $NEW; do cp ~/Library/Logs/DiagnosticReports/$f "$OUT/"; done; else echo "no new crash reports" | tee -a "$OUT/run.txt"; fi
echo "--- stderr (first 40 lines):"; head -40 "$OUT/stderr.log"
