#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# One-command Freeciv build for macOS (Apple Silicon, Homebrew).
#
# Usage: scripts/build.sh <qt|gtk|sdl2|all> [--debug] [--audio sdl2|sdl3] [--jobs N] [--no-install-deps]
#
#   qt    : freeciv-qt client (Qt 6), fcmp-qt, ruledit, server, manual, ruleup
#   gtk   : freeciv-gtk4 and freeciv-gtk3.22 clients, fcmp-gtk4/gtk3, server, manual, ruleup
#   sdl2  : freeciv-sdl2 client, fcmp-cli, server, manual, ruleup
#
# Source tree : $FREECIV_SRC   (default: <repo>/port/freeciv, our patched S3_2 checkout); a git tree must have every
#               patch in patches/ as a commit, or the build stops (FREECIV_ALLOW_MISSING_PATCHES=1 builds anyway)
# Build dir   : $FREECIV_SRC/build-<client>[-debug]
# Install to  : $FREECIV_PREFIX_ROOT/<client>[-debug]   (default: ~/freeciv-builds; NOT under ~/Desktop,
#               ~/Documents or ~/Downloads: macOS privacy protection blocks LaunchServices-launched apps there,
#               see notes/reproduction.md Failure 2)
# Logs        : <repo>/logs/build-<client>[-debug].log
#
# Release is the default (-Dbuildtype=release -Ddebug=false). --debug gives -Ddebug=true -Dbuildtype=debug.
# The environment matches upstream's mac-meson CI job (scripts/ci-build.sh in the Freeciv tree): keg-only
# gettext, readline and icu4c need explicit CPPFLAGS/LDFLAGS/PKG_CONFIG_PATH. Homebrew packages are installed only
# when missing (brew install <missing>), never upgraded here; what was installed is printed at the end so it can
# be copied into notes/installed.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${FREECIV_SRC:-$ROOT/port/freeciv}"
PREFIX_ROOT="${FREECIV_PREFIX_ROOT:-$HOME/freeciv-builds}"
LOGDIR="$ROOT/logs"; mkdir -p "$LOGDIR"

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
[ $# -ge 1 ] || usage
TARGET="$1"; shift
DEBUG=0; AUDIO=sdl2; JOBS=""; INSTALL_DEPS=1
while [ $# -gt 0 ]; do
  case "$1" in
    --debug) DEBUG=1 ;;
    --audio) AUDIO="$2"; shift ;;
    --jobs) JOBS="-j $2"; shift ;;
    --no-install-deps) INSTALL_DEPS=0 ;;
    *) echo "unknown option $1"; usage ;;
  esac
  shift
done

case "$TARGET" in
  all) for t in qt gtk sdl2; do "$0" "$t" $([ $DEBUG = 1 ] && echo --debug) --audio "$AUDIO" ${JOBS:+--jobs ${JOBS#-j }}; done; exit 0 ;;
  qt|gtk|sdl2) ;;
  *) usage ;;
esac

# ---- the patch series ------------------------------------------------------------------------------------------
# A git source tree must carry every patch in patches/ as a commit; git am keeps a patch's subject, so the check
# looks for each subject in the tree's log (issue 269: macos27-port once lacked 0035-0043, 0045, 0047 and 0048, and a
# build from it quietly lost balance 2). A plain directory, such as a driver build's copy, can't be checked.
if git -C "$SRC" rev-parse --git-dir >/dev/null 2>&1; then
  SUBJECTS="$(git -C "$SRC" log --format=%s -n 5000)"
  LACKING=""
  for p in "$ROOT"/patches/*.patch; do
    s="$(git -C "$ROOT" mailinfo /dev/null /dev/null < "$p" | sed -n 's/^Subject: //p')"
    printf '%s\n' "$SUBJECTS" | grep -Fxq -- "$s" || LACKING="$LACKING $(basename "$p" | cut -c1-4)"
  done
  if [ -n "$LACKING" ]; then
    echo "$SRC lacks patches:$LACKING"
    echo "build from a tree with the whole series (44e6898 plus git am patches/*.patch), or set FREECIV_ALLOW_MISSING_PATCHES=1"
    [ "${FREECIV_ALLOW_MISSING_PATCHES:-0}" = 1 ] || exit 1
  fi
else
  echo "note: $SRC is not a git checkout, so it is not checked against patches/"
fi

# ---- Homebrew dependencies -------------------------------------------------------------------------------------
command -v brew >/dev/null || { echo "Homebrew is required (https://brew.sh)"; exit 1; }
COMMON="meson ninja pkgconf gettext readline icu4c@78 curl sqlite zstd"
case "$AUDIO" in
  sdl2) AUDIO_PKGS="sdl2-compat sdl2_mixer" ;;
  sdl3) AUDIO_PKGS="sdl3 sdl3_mixer" ;;
  none) AUDIO_PKGS="" ;;
  *) echo "--audio must be sdl2, sdl3 or none"; exit 1 ;;
esac
case "$TARGET" in
  qt)   PKGS="$COMMON $AUDIO_PKGS qt" ;;
  gtk)  PKGS="$COMMON $AUDIO_PKGS gtk4 gtk+3" ;;
  sdl2) PKGS="$COMMON sdl2-compat sdl2_image sdl2_ttf sdl2_mixer sdl2_gfx" ;;
esac
INSTALLED_NOW=""
MISSING=""
for p in $PKGS; do brew list --formula --versions "$p" >/dev/null 2>&1 || MISSING="$MISSING $p"; done
if [ -n "$MISSING" ]; then
  if [ $INSTALL_DEPS = 1 ]; then
    echo "installing missing Homebrew formulae:$MISSING"
    # shellcheck disable=SC2086
    brew install $MISSING
    INSTALLED_NOW="$MISSING"
  else
    echo "missing Homebrew formulae:$MISSING (rerun without --no-install-deps or brew install them)"; exit 1
  fi
fi
command -v swiftc >/dev/null || echo "note: Xcode command line tools not found (needed only for scripts/windows-of-pid)"

# ---- environment (upstream ci-build.sh mac-meson shape) --------------------------------------------------------
export CPPFLAGS="-I$(brew --prefix gettext)/include -I$(brew --prefix readline)/include${CPPFLAGS:+ $CPPFLAGS}"
export LDFLAGS="-L$(brew --prefix gettext)/lib -L$(brew --prefix icu4c@78)/lib -L$(brew --prefix readline)/lib${LDFLAGS:+ $LDFLAGS}"
PKGP="$(brew --prefix icu4c@78)/lib/pkgconfig:$(brew --prefix curl)/lib/pkgconfig:$(brew --prefix readline)/lib/pkgconfig"
[ "$TARGET" = qt ] && PKGP="$PKGP:$(brew --prefix qt)/lib/pkgconfig"
export PKG_CONFIG_PATH="$PKGP${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

# ---- meson options ---------------------------------------------------------------------------------------------
SUFFIX=""; [ $DEBUG = 1 ] && SUFFIX="-debug"
BUILD="$SRC/build-$TARGET$SUFFIX"
PREFIX="$PREFIX_ROOT/$TARGET$SUFFIX"
LOG="$LOGDIR/build-$TARGET$SUFFIX.log"
OPTS=(-Dprefix="$PREFIX" -Daudio="$AUDIO" -Dnls=true -Dsyslua=try)
if [ $DEBUG = 1 ]; then OPTS+=(-Ddebug=true -Dbuildtype=debug); else OPTS+=(-Ddebug=false -Dbuildtype=release); fi
case "$TARGET" in
  qt)   OPTS+=(-Dclients=qt -Dfcmp=qt -Dqtver=qt6 -Dtools=ruledit,manual,ruleup) ;;
  gtk)  OPTS+=(-Dclients=gtk3.22,gtk4 -Dfcmp=gtk3,gtk4 -Dtools=manual,ruleup) ;;
  sdl2) OPTS+=(-Dclients=sdl2 -Dfcmp=cli -Dtools=manual,ruleup) ;;
esac

[ -f "$SRC/meson.build" ] || { echo "no Freeciv source at $SRC (set FREECIV_SRC)"; exit 1; }
echo "== build $TARGET$SUFFIX: src=$SRC build=$BUILD prefix=$PREFIX log=$LOG"
{
  echo "# $(date) $0 $TARGET ${OPTS[*]}"
  echo "# CPPFLAGS=$CPPFLAGS"; echo "# LDFLAGS=$LDFLAGS"; echo "# PKG_CONFIG_PATH=$PKG_CONFIG_PATH"
  git -C "$SRC" log -1 --format='# source: %h %s' 2>/dev/null || true
} > "$LOG"
if [ -f "$BUILD/meson-private/coredata.dat" ]; then
  meson setup --reconfigure "$BUILD" "$SRC" "${OPTS[@]}" >> "$LOG" 2>&1 || { tail -30 "$LOG"; exit 1; }
else
  meson setup "$BUILD" "$SRC" "${OPTS[@]}" >> "$LOG" 2>&1 || { tail -30 "$LOG"; exit 1; }
fi
# shellcheck disable=SC2086
ninja -C "$BUILD" $JOBS >> "$LOG" 2>&1 || { grep -nE "error:|FAILED" "$LOG" | head -20; echo "see $LOG"; exit 1; }
ninja -C "$BUILD" install >> "$LOG" 2>&1 || { tail -30 "$LOG"; exit 1; }

echo "== installed:"
ls "$PREFIX/bin"
"$PREFIX/bin/freeciv-server" --version 2>/dev/null | head -1 || true
WARN=$(grep -c "warning:" "$LOG" || true); echo "== compiler warnings: $WARN (see $LOG)"
if [ -n "$INSTALLED_NOW" ]; then
  echo "== Homebrew formulae installed by this run (record in notes/installed.md):"
  for p in $INSTALLED_NOW; do brew list --formula --versions "$p"; done
fi
