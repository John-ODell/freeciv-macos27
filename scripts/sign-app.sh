#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Sign an .app made by scripts/bundle.sh from the inside out: every Mach-O library and plugin, the
# frameworks, every executable in Contents/MacOS (the compiled launcher too), then the bundle.
#
# Usage: scripts/sign-app.sh <App.app> <IDENTITY>
#
#   IDENTITY "-"  ad-hoc: no timestamp, no hardened runtime. Runs locally; Gatekeeper rejects a downloaded copy.
#   otherwise     e.g. "Developer ID Application: Name (TEAMID)" or its SHA-1: hardened runtime and a secure
#                 timestamp on every Mach-O, as notarization requires. No entitlements: nothing in the bundle
#                 needs one (Lua 5.4 has no JIT, nothing sets DYLD_ variables, and every library carries the
#                 same signature, so library validation passes).
# Used by bundle.sh (--sign) and dmg.sh (--sign).
set -euo pipefail
[ $# -eq 2 ] || { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
APP="$1"; SIGN="$2"; C="$APP/Contents"
[ -d "$C/MacOS" ] || { echo "sign-app: $APP is not an app bundle"; exit 1; }
if [ "$SIGN" = "-" ]; then CS=(--force --sign - --timestamp=none); else CS=(--force --sign "$SIGN" --options runtime --timestamp); fi
n=0
while IFS= read -r -d '' f; do
  if file -b "$f" | grep -q Mach-O; then codesign "${CS[@]}" "$f"; n=$((n + 1)); fi
done < <(find "$C/Frameworks" "$C/PlugIns" -type f \( -name "*.dylib" -o -name "*.so" -o -perm +111 \) -print0 2>/dev/null)
while IFS= read -r -d '' f; do codesign "${CS[@]}" "$f"; n=$((n + 1)); done \
  < <(find "$C/Frameworks" -maxdepth 1 -name "*.framework" -print0 2>/dev/null)
for f in "$C"/MacOS/*; do codesign "${CS[@]}" "$f"; n=$((n + 1)); done
codesign "${CS[@]}" "$APP"
codesign --verify --strict --deep "$APP"
echo "codesign verify: ok ($SIGN, $n items plus the bundle)"
