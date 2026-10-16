#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Make a minimal .app wrapper around an installed freeciv client binary (for testing only:
# no dylib bundling, data path is the compiled-in install prefix). Usage: mk-min-app.sh <binary> <AppName> <bundle-id>
set -eu
BIN="$1"; NAME="$2"; BID="$3"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${FREECIV_SRC:-$ROOT/port/freeciv}"
APP=${APPDIR:-$HOME/freeciv-builds/apps}/$NAME.app
rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/$(basename "$BIN")"
if [ -f "$SRC/data/freeciv-client.icns" ]; then cp "$SRC/data/freeciv-client.icns" "$APP/Contents/Resources/"; else echo "warning: no icon at $SRC/data/freeciv-client.icns (set FREECIV_SRC); bundle gets the generic icon"; fi
cat > "$APP/Contents/Info.plist" <<EOP
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key><string>en</string>
  <key>CFBundleExecutable</key><string>$(basename "$BIN")</string>
  <key>CFBundleIconFile</key><string>freeciv-client</string>
  <key>CFBundleIdentifier</key><string>$BID</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>CFBundleName</key><string>$NAME</string>
  <key>CFBundleDisplayName</key><string>$NAME</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>3.2.6</string>
  <key>CFBundleVersion</key><string>3.2.6</string>
  <key>LSMinimumSystemVersion</key><string>14.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>LSApplicationCategoryType</key><string>public.app-category.strategy-games</string>
</dict>
</plist>
EOP
codesign --force --sign - "$APP" >/dev/null 2>&1 && echo "ad-hoc signed $APP" || echo "codesign failed (continuing)"
plutil -lint "$APP/Contents/Info.plist"
echo "$APP"
