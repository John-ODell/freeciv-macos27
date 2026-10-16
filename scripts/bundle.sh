#!/bin/bash
# Assemble a self-contained, ad-hoc signed macOS .app from a Freeciv install made by scripts/build.sh.
#
# Usage: scripts/bundle.sh <qt|gtk4|gtk3.22|sdl2> [--prefix DIR] [--out DIR] [--name NAME] [--sign IDENTITY]
#
#   --prefix  install prefix to bundle              (default: ~/freeciv-builds/<qt|gtk|sdl2>)
#   --out     directory to write the .app into      (default: ~/freeciv-builds/apps)
#   --name    app name                              (default: Freeciv for qt, "Freeciv <Client>" otherwise)
#   --sign    codesign identity                     (default: "-" = ad-hoc; see scripts/dmg.sh for notarization)
#
# Layout:  <Name>.app/Contents/MacOS/<Name>        launcher: sets FREECIV_DATA_PATH / FREECIV_LOCALE_PATH, cd's
#                                                   next to the binaries (so the client's spawned ./freeciv-server
#                                                   is the bundled one), exec's the client
#          Contents/MacOS/freeciv-<client>, freeciv-server, freeciv-mp-<x>, freeciv-ruledit (qt)
#          Contents/Frameworks/                     every non-system dylib and Qt framework, install names @rpath
#          Contents/PlugIns/                        Qt plugins (macdeployqt)
#          Contents/Resources/share/freeciv, share/locale, freeciv-client.icns
# The bundle depends on nothing outside itself and /System; Homebrew is not needed at run time.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -ge 1 ] || { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
CLIENT="$1"; shift
case "$CLIENT" in qt) SUB=qt;; gtk4|gtk3.22) SUB=gtk;; sdl2) SUB=sdl2;; *) echo "client must be qt, gtk4, gtk3.22 or sdl2"; exit 1;; esac
PREFIX="$HOME/freeciv-builds/$SUB"; OUT="$HOME/freeciv-builds/apps"; NAME=""; SIGN="-"
while [ $# -gt 0 ]; do case "$1" in
  --prefix) PREFIX="$2"; shift;; --out) OUT="$2"; shift;; --name) NAME="$2"; shift;; --sign) SIGN="$2"; shift;;
  *) echo "unknown option $1"; exit 1;; esac; shift; done
case "$CLIENT" in qt) : "${NAME:=Freeciv}"; BID=org.freeciv.qt;; gtk4) : "${NAME:=Freeciv GTK4}"; BID=org.freeciv.gtk4;;
  gtk3.22) : "${NAME:=Freeciv GTK3}"; BID=org.freeciv.gtk3;; sdl2) : "${NAME:=Freeciv SDL2}"; BID=org.freeciv.sdl2;; esac
SRC="${FREECIV_SRC:-$ROOT/port/freeciv}"
BIN="$PREFIX/bin/freeciv-$CLIENT"
[ -x "$BIN" ] || { echo "no $BIN; run scripts/build.sh $SUB first"; exit 1; }
case "$OUT" in "$HOME/Desktop"*|"$HOME/Documents"*|"$HOME/Downloads"*) echo "warning: $OUT is privacy-protected; Finder launches may stall on a consent prompt (notes/reproduction.md F2)";; esac

# version from fc_version
eval "$(grep -E '^(MAJOR|MINOR|PATCH|EMERGENCY)_VERSION=|^VERSION_LABEL=' "$SRC/fc_version")"
VER="$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION${EMERGENCY_VERSION:+.$EMERGENCY_VERSION}"
VERLABEL="$VER$VERSION_LABEL"
DATASUBDIR="$MAJOR_VERSION.$MINOR_VERSION"

APP="$OUT/$NAME.app"; C="$APP/Contents"
echo "== bundling $BIN ($VERLABEL) -> $APP"
rm -rf "$APP"; mkdir -p "$C/MacOS" "$C/Resources/share" "$C/Frameworks"

# binaries
cp "$BIN" "$C/MacOS/"
cp "$PREFIX/bin/freeciv-server" "$C/MacOS/"
for t in freeciv-mp-$CLIENT freeciv-mp-gtk3 freeciv-mp-gtk4 freeciv-mp-cli freeciv-ruledit; do
  case "$CLIENT:$t" in qt:freeciv-mp-qt|qt:freeciv-ruledit|gtk4:freeciv-mp-gtk4|gtk3.22:freeciv-mp-gtk3|sdl2:freeciv-mp-cli)
    [ -x "$PREFIX/bin/$t" ] && cp "$PREFIX/bin/$t" "$C/MacOS/";; esac
done
# data + locale
cp -R "$PREFIX/share/freeciv" "$C/Resources/share/freeciv"
[ -d "$PREFIX/share/locale" ] && cp -R "$PREFIX/share/locale" "$C/Resources/share/locale"
cp "$SRC/data/freeciv-client.icns" "$C/Resources/freeciv-client.icns"

# launcher
cat > "$C/MacOS/$NAME" <<'EOL'
#!/bin/bash
# Freeciv.app launcher: make the bundle relocatable, then exec the client.
DIR="$(cd "$(dirname "$0")" && pwd)"
RES="$(cd "$DIR/../Resources" && pwd)"
export FREECIV_DATA_PATH="${FREECIV_DATA_PATH:-$RES/share/freeciv:$HOME/.freeciv/@DATASUBDIR@}"
export FREECIV_SCENARIO_PATH="${FREECIV_SCENARIO_PATH:-$RES/share/freeciv/scenarios:$HOME/.freeciv/@DATASUBDIR@/scenarios:$HOME/.freeciv/scenarios}"
export FREECIV_LOCALE_PATH="${FREECIV_LOCALE_PATH:-$RES/share/locale}"
export PATH="$DIR:$PATH"
cd "$DIR"   # the client starts a local game with ./freeciv-server (client/connectdlg_common.c)
exec "$DIR/@CLIENTBIN@" "$@"
EOL
sed -i '' -e "s|@DATASUBDIR@|$DATASUBDIR|g" -e "s|@CLIENTBIN@|freeciv-$CLIENT|g" "$C/MacOS/$NAME"
chmod +x "$C/MacOS/$NAME"

# Info.plist
cat > "$C/Info.plist" <<EOP
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key><string>en</string>
  <key>CFBundleExecutable</key><string>$NAME</string>
  <key>CFBundleIconFile</key><string>freeciv-client</string>
  <key>CFBundleIdentifier</key><string>$BID</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>CFBundleName</key><string>$NAME</string>
  <key>CFBundleDisplayName</key><string>$NAME</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>$VER</string>
  <key>CFBundleVersion</key><string>$VERLABEL</string>
  <key>CFBundleGetInfoString</key><string>Freeciv $VERLABEL ($CLIENT client), GPL-2.0-or-later, https://www.freeciv.org</string>
  <key>NSHumanReadableCopyright</key><string>Copyright (C) 1996-2026 The Freeciv Project. GNU GPL v2 or later.</string>
  <key>LSMinimumSystemVersion</key><string>@MINOS@</string>
  <key>LSApplicationCategoryType</key><string>public.app-category.strategy-games</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSSupportsAutomaticGraphicsSwitching</key><true/>
  <key>NSPrincipalClass</key><string>NSApplication</string>
  <key>CFBundleDocumentTypes</key>
  <array><dict>
    <key>CFBundleTypeName</key><string>Freeciv saved game</string>
    <key>CFBundleTypeRole</key><string>Viewer</string>
    <key>CFBundleTypeExtensions</key><array><string>sav</string><string>sav.gz</string><string>sav.xz</string><string>sav.zst</string></array>
  </dict></array>
</dict>
</plist>
EOP

# Qt plugins (the frameworks themselves are copied by fix-dylibs.py below). A bundle's Contents/PlugIns is on
# QCoreApplication::libraryPaths() by default, so no qt.conf is needed (Qt 6.12 is relocatable as well).
if [ "$CLIENT" = qt ]; then
  QP="$(brew --prefix qtbase)/share/qt/plugins"
  mkdir -p "$C/PlugIns/platforms" "$C/PlugIns/styles" "$C/PlugIns/imageformats"
  cp "$QP/platforms/libqcocoa.dylib" "$C/PlugIns/platforms/"
  cp "$QP/styles/libqmacstyle.dylib" "$C/PlugIns/styles/"
  for f in libqgif libqico libqjpeg; do cp "$QP/imageformats/$f.dylib" "$C/PlugIns/imageformats/"; done
fi

# every remaining Homebrew / prefix dylib -> Contents/Frameworks, install names -> @rpath
EXTRA=()
SDL3="$(brew --prefix sdl3 2>/dev/null)/lib/libSDL3.0.dylib"
if otool -L "$BIN" | grep -q libSDL2 && [ -f "$SDL3" ]; then EXTRA=(--extra "$SDL3"); fi   # sdl2-compat dlopens @loader_path/libSDL3.dylib
python3 "$ROOT/scripts/fix-dylibs.py" "$APP" "${EXTRA[@]}"
[ -f "$C/Frameworks/libSDL3.0.dylib" ] && ln -sf libSDL3.0.dylib "$C/Frameworks/libSDL3.dylib"

# LSMinimumSystemVersion = highest minos of anything in the bundle
MINOS=$(find "$C/MacOS" "$C/Frameworks" "$C/PlugIns" -type f 2>/dev/null | while read -r f; do
  otool -l "$f" 2>/dev/null | awk '/LC_BUILD_VERSION/{b=1} b&&/minos/{print $2; exit}'; done | sort -t. -k1,1n -k2,2n | tail -1)
sed -i '' "s|@MINOS@|${MINOS:-14.0}|" "$C/Info.plist"
plutil -lint "$C/Info.plist" >/dev/null

# sign inside-out: libraries and plugins, then helper executables, then the bundle
find "$C/Frameworks" "$C/PlugIns" -type f \( -name "*.dylib" -o -perm +111 \) 2>/dev/null | while read -r f; do
  file -b "$f" | grep -q Mach-O && codesign --force --sign "$SIGN" --timestamp=none "$f" 2>/dev/null; done
find "$C/Frameworks" -maxdepth 1 -name "*.framework" -exec codesign --force --sign "$SIGN" --timestamp=none {} \; 2>/dev/null
for f in "$C"/MacOS/freeciv-*; do codesign --force --sign "$SIGN" --timestamp=none "$f"; done
codesign --force --sign "$SIGN" --timestamp=none "$APP"
codesign --verify --strict --deep "$APP" && echo "codesign verify: ok ($SIGN)"

echo "== $APP"; du -sh "$APP" | cut -f1 | sed 's/^/size: /'
echo "minos: ${MINOS:-?}   signed: $(codesign -dv "$APP" 2>&1 | grep -E '^Signature|^Authority' | head -1)"
echo "launch:  open \"$APP\"     or     \"$C/MacOS/$NAME\" -a -s localhost -p 5556"
