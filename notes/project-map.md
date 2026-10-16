# Step 1: Project map (Freeciv 3.2.6+, branch S3_2; main is 3.3.90-dev)

Sources: refs/freeciv-S3_2 (commit 44e6898c, 2026-10-16) and refs/freeciv (main, 3f0038d8).
File counts from `find <dir> -type f | wc -l` on S3_2.

## Components

| Component | Directory | Notes |
| --- | --- | --- |
| Shared library `libfreeciv` | utility/ (77 files), common/ (183) | Everything both server and client need: network packets (common/networking/packets.def, 2480 lines, generated into packets_gen.c by gen_headers/ python), rulesets, map, units, cities, scripting core (common/scriptcore, Lua). |
| Server `freeciv-server` | server/ (162) + server/{advisors,generator,savegame,scripting} | Game logic, map generator, save/load (gzip/bzip2/xz/zstd), Lua scripting, fcdb (sqlite3 by default) for player auth. Console via readline. |
| AI | ai/ (68): ai/default, ai/classic, ai/tex (threaded), ai/stub | Selected at runtime with `-A`/`aitype`. |
| Client common | client/ (663 incl. gui dirs) | Toolkit-independent client: options, tilespec, mapview, audio (client/audio_sdl.c = SDL2_mixer / SDL3_mixer), Lua console. |
| Client GUI: GTK 3.22 | client/gui-gtk-3.22 | C. Menus from data/gtk3.22_menus.xml. One `#ifdef __APPLE__` (gui_main.h:23). |
| Client GUI: GTK 4 | client/gui-gtk-4.0 | C. Upstream default client (`meson_options.txt` clients default = gtk4). One `#ifdef __APPLE__` (gui_main.h:24). |
| Client GUI: Qt | client/gui-qt | C++17, Qt 5 or 6 (`-Dqtver`). macOS-specific menu code in client/gui-qt/menu.cpp:972-981 and :1726-1804 (`#ifdef __APPLE__`). Uses QMainWindow/QMenuBar, QPainter 2D. |
| Client GUI: SDL2 | client/gui-sdl2 | C, own widget toolkit drawn on SDL surfaces; needs SDL2, SDL2_image, SDL2_ttf, SDL2_gfx (bundled copy in dependencies/SDL2_gfx if not found). No `__APPLE__` code. |
| Client GUI: SDL3 | client/gui-sdl3 | Same as sdl2 ported to SDL3 (3.2+ only). Upstream macOS CI builds this, not sdl2. |
| Client GUI: stub | client/gui-stub | Headless/no-op GUI, for testing. |
| Web client | refs/freeciv-web (separate repo) | HTML5/WebGL; needs the server built with `-Dserver=freeciv-web` and `-Djson-protocol=true`. Out of scope for a native macOS port but noted. |
| Modpack installer `freeciv-mp-{gtk3,gtk4,qt,cli}` | tools/fcmp | Downloads modpacks with libcurl. |
| Ruleset editor `freeciv-ruledit` | tools/ruledit | Qt only. |
| `freeciv-ruleup`, `freeciv-manual` | tools/ | CLI tools. |
| Game data | data/ (4841) | Rulesets (civ1, civ2, civ2civ3 default, classic, alien, multiplayer, sandbox, ...), tilesets (amplio2, hexemplio, trident, ...), sounds (stdsounds), music (stdmusic), themes per GUI, nations, scenarios, icons. |
| Bundled third-party | dependencies/ (158) | lua-5.4, tolua-5.2, luasql, tinycthread, cvercmp, SDL2_gfx. Used when `-Dsyslua=false/try` fails to find system Lua. |
| Translations | translations/ (146 .po) | gettext; `-Dnls`. |
| Tests | tests/ (18) | Ruleset sanity, autogame (scripts/test-autogame.serv: 10 AI, 100 turns). |

## Build systems

- **Meson** (`meson.build`, `meson_options.txt`, min 0.60.0): the primary one; used by upstream CI for macOS (`.github/workflows/ci.yml` job `mac-meson`, `runs-on: xcode-27`; `scripts/ci-build.sh` case `mac-meson`). Options that matter: `clients` (gtk3.22, sdl2, qt, gtk4, stub, sdl3), `fcmp`, `audio` (none/sdl2/sdl3), `qtver` (qt5/qt6), `syslua`, `readline`, `nls`, `tools`, `followtag`, `appimage`.
- **Autotools** (`configure.ac`, AC_PREREQ 2.65, `autogen.sh`, m4/): still maintained and used by the `autotools`, `clang-debug`, `dist` CI jobs. The autotools macros define `SDL2_PLAIN_INCLUDE` when SDL headers are found without the `SDL2/` prefix (m4/sound.m4:25, m4/sdl2-client.m4:100); meson never defines it, so meson builds always `#include <SDL2/SDL.h>`.

## Platform-specific code and packaging

| Path | What |
| --- | --- |
| platforms/macos/homebrew-appbundle.sh | The only macOS packaging script upstream. Builds gtk4+qt clients with meson against Homebrew, `-Dprefix=/Applications/Freeciv.app/Contents/` (installs straight into /Applications), writes a minimal Info.plist with `CFBundleExecutable` = `../bin/freeciv-gtk4` and `LSEnvironment LD_LIBRARY_PATH` (ignored by macOS; dyld uses DYLD_*). No dylib bundling, no signing. This is the recipe the official 3.1.0-beta1 Freeciv.app was made with (its Info.plist is byte-for-byte this template with freeciv-qt). |
| platforms/windows/ (installer_msys2, installer_cross) | Windows NSIS installers, the reference for "self-contained package" logic. |
| platforms/appimage/, platforms/flatpak/, platforms/emscripten/ | Linux and web packaging. |
| bootstrap/ | .desktop and metainfo files, `generate_metainfo.sh`. |
| data/freeciv-client.icns, data/freeciv-server.icns | macOS icons already exist. |
| INSTALL section 8 "Mac OS X and Darwin notes" | Only two notes: icu4c pkg-config path, and readline (libedit is not enough). |
| doc/README.packaging | General packaging notes. |

## Dependencies and their macOS 27 (Homebrew 7.0.9, arm64) status

| Dependency | Needed by | Homebrew formula / version here | Status on macOS 27 |
| --- | --- | --- | --- |
| C11 compiler, C++17 (Qt, ruledit) | all | Xcode 27 clang | works (build log: no errors after one meson fix) |
| meson >= 0.60, ninja, python3 | build | meson 1.12.1, ninja 1.13.2, python 3.15 | works |
| gettext (libintl) | all (`-Dnls`) | gettext 1.0, keg-only paths via CPPFLAGS/LDFLAGS | works with upstream's CPPFLAGS recipe |
| zlib, bzip2, xz (lzma), zstd | savegames | system zlib/bzip2, xz 5.x, zstd 1.5.7 | works |
| libcurl | fcmp, metaserver | curl 8.23.0 (keg-only) or system libcurl | works |
| SQLite3 | fcdb, fcmp | sqlite 3.54.0 (keg-only; system sqlite also present) | works |
| ICU (icu-uc) | utility (collation) | icu4c@78 78.3, keg-only: needs PKG_CONFIG_PATH | works with upstream's PKG_CONFIG_PATH recipe |
| Lua 5.4 | scripting | bundled dependencies/lua-5.4 used (syslua=try found no system lua) | works |
| readline | server console | readline 8.3.6 keg-only | works with CPPFLAGS/LDFLAGS recipe |
| SDL2 (+_mixer) | audio for every client | **sdl2-compat 2.32.74** (Homebrew's `sdl2` is now a compat layer over sdl3 3.4.18), sdl2_mixer 2.8.2 | builds and links; runtime goes through libSDL3.0.dylib (observed in `sample` of freeciv-sdl2: SDL_SYS_DelayNS in libSDL3.0.dylib) |
| SDL2_image, SDL2_ttf, SDL2_gfx | sdl2 client | 2.8.12_1, 2.24.0, 1.0.4_1 | builds and launches |
| GTK 3 >= 3.22 | gtk3.22 client, mp-gtk3 | gtk+3 3.24.52_1 (quartz backend) | builds and launches |
| GTK 4 | gtk4 client, mp-gtk4 | gtk4 4.24.1 (macOS backend) | builds and launches; one Gdk-WARNING `gdk_frame_timings_presented() called on skipped frame` at startup |
| Qt 6 Core/Gui/Widgets (+Svg for svgflags) | qt client, mp-qt, ruledit | qt 6.12.0 (pulls all Qt modules, ~2 GB) | builds and launches; warning about missing "Sans Serif" font alias |
| MagickWand (optional) | mapimg | not installed | skipped (optional) |
| MySQL/MariaDB/ODBC (optional) | fcdb backends | not installed | skipped (optional) |

## Observations that matter for the port (all observed in this session, see logs/)

1. Meson build on Homebrew needs the upstream CI env: `CPPFLAGS=-I$(brew --prefix gettext)/include -I$(brew --prefix readline)/include`, `LDFLAGS=-L.../gettext/lib -L.../icu4c/lib -L.../readline/lib`, `PKG_CONFIG_PATH=$(brew --prefix icu4c)/lib/pkgconfig`.
2. With `-Daudio=sdl2` the gtk3.22, gtk4 and qt executables fail to compile (`'SDL2/SDL.h' file not found`) because their meson targets lack `audio_dep` (meson.build:3354, :3447, :3574 on S3_2). The sdl2/sdl3/stub targets have it. Fixed in port/freeciv commit e57d3ed; upstreamable.
3. Default Homebrew `sdl2` is sdl2-compat; SDL2_gfx/image/ttf/mixer all link against it. No build problem, but it means the "SDL2 client" on macOS actually runs on SDL3.
4. All built binaries are plain arm64 Mach-O executables linked against absolute /opt/homebrew/opt/... dylib paths (otool -L). A redistributable .app needs dylib bundling and install_name rewriting; upstream has no script for that.
