#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Package an .app made by scripts/bundle.sh as a compressed DMG with an /Applications drop link, optionally
# Developer-ID signed and notarized.
#
# Usage: scripts/dmg.sh <App.app> [--out DIR] [--sign "Developer ID Application: Name (TEAMID)"]
#                                 [--notarize-profile PROFILE] [--volname NAME]
#
#   default: ad-hoc signed app (as bundle.sh leaves it), unsigned DMG, sha256 sidecar written next to it.
#   --sign              sign the DMG with the identity (name or SHA-1 hash), and the app too (scripts/sign-app.sh:
#                       inside-out, hardened runtime, secure timestamp) unless it already carries that identity
#   --notarize-profile  `xcrun notarytool submit --wait` with a keychain profile made by
#                       `xcrun notarytool store-credentials PROFILE`, then `xcrun stapler staple` on the DMG.
#                       Needs a paid Apple Developer account; nothing here is done automatically without it.
# Output: <out>/<Name>-<version>-arm64.dmg and .dmg.sha256 (both git-ignored). DMGs are never committed.
set -euo pipefail
[ $# -ge 1 ] || { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
APP="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; shift
OUT="$(dirname "$APP")"; SIGN=""; PROFILE=""; VOLNAME=""
while [ $# -gt 0 ]; do case "$1" in
  --out) OUT="$2"; shift;; --sign) SIGN="$2"; shift;; --notarize-profile) PROFILE="$2"; shift;; --volname) VOLNAME="$2"; shift;;
  *) echo "unknown option $1"; exit 1;; esac; shift; done
[ -d "$APP/Contents" ] || { echo "$APP is not an app bundle"; exit 1; }
NAME="$(basename "$APP" .app)"
VER="$(plutil -extract CFBundleShortVersionString raw "$APP/Contents/Info.plist")"
ARCH="$(lipo -archs "$APP/Contents/MacOS/freeciv-server" | tr ' ' '-')"
: "${VOLNAME:=$NAME $VER}"
DMG="$OUT/$NAME-$VER-$ARCH.dmg"
mkdir -p "$OUT"

if [ -n "$SIGN" ]; then
  # Re-sign the app unless bundle.sh --sign already signed it with this identity and hardened runtime. A 40-hex
  # --sign is a certificate SHA-1 (as `security find-identity` prints it); codesign -dv shows only names, so compare
  # it with the SHA-1 of the app's leaf certificate instead.
  INFO="$(codesign -dv --verbose=2 "$APP" 2>&1 || true)"
  SAME=0
  if [[ "$SIGN" =~ ^[0-9A-Fa-f]{40}$ ]]; then
    CERTS="$(mktemp -d)"
    if (cd "$CERTS" && codesign -d --extract-certificates "$APP" 2>/dev/null) && [ -f "$CERTS/codesign0" ]; then
      [ "$(shasum -a 1 "$CERTS/codesign0" | cut -d' ' -f1)" = "$(tr 'A-F' 'a-f' <<<"$SIGN")" ] && SAME=1
    fi
    rm -rf "$CERTS"
  elif grep -qF "Authority=$SIGN" <<<"$INFO"; then
    SAME=1
  fi
  if grep -q "^Signature=adhoc" <<<"$INFO" || ! grep -q "flags=.*runtime" <<<"$INFO" || [ "$SAME" = 0 ]; then
    echo "== signing the app with: $SIGN"
    "$(dirname "$0")/sign-app.sh" "$APP" "$SIGN"
  else
    echo "== app already signed with: $SIGN (hardened runtime)"
  fi
fi
codesign --verify --strict --deep "$APP"
echo "app signature: $(codesign -dv --verbose=2 "$APP" 2>&1 | grep -E '^Signature=adhoc|^Authority=' | head -1)"
spctl -a -t exec -vv "$APP" 2>&1 | head -2 || true   # 'rejected' is expected for ad-hoc; informational

# staging folder: the app + an /Applications symlink
STAGE="$(mktemp -d)"; trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
cat > "$STAGE/README.txt" <<EOR
$NAME $VER for macOS (Apple Silicon)

Drag $NAME.app to the Applications folder.

Freeciv is free software under the GNU GPL v2 or later: https://www.freeciv.org
Licence text: $NAME.app/Contents/Resources/COPYING. Exact source commit and patches: Contents/Resources/SOURCE.txt.
Bundled third-party libraries, their licences and sources: Contents/Resources/licenses/THIRD-PARTY-NOTICES.txt.
Source tarball, packaging scripts and patches: https://github.com/John-ODell/freeciv-macos27/releases
$( [ -z "$SIGN" ] && echo "
This copy is not notarized. If macOS says the app is damaged or from an unidentified developer:
open System Settings > Privacy & Security and choose Open Anyway, or run
  xattr -dr com.apple.quarantine \"/Applications/$NAME.app\"" )
EOR

rm -f "$DMG"
hdiutil create -volname "$VOLNAME" -srcfolder "$STAGE" -ov -format UDZO -imagekey zlib-level=9 "$DMG" >/dev/null
if [ -n "$SIGN" ]; then codesign --force --sign "$SIGN" --timestamp "$DMG"; fi
if [ -n "$PROFILE" ]; then
  echo "== notarizing (this uploads the DMG to Apple)"
  xcrun notarytool submit "$DMG" --keychain-profile "$PROFILE" --wait
  xcrun stapler staple "$DMG"
fi
( cd "$OUT" && shasum -a 256 "$(basename "$DMG")" > "$(basename "$DMG").sha256" )
echo "== $DMG ($(du -h "$DMG" | cut -f1))"; cat "$DMG.sha256"
echo "verify: hdiutil verify \"$DMG\"   mount: open \"$DMG\""
