# Step 2: Reproduction on macOS 27.0.1 (arm64, Xcode 27, Homebrew 7.0.9)

All runs on 2026-10-15/16. Raw logs, screenshots, stack samples and crash-report diffs in `logs/`
(git-ignored; excerpts here). Label key: observed / derived / inferred / unknown.

## 2A. Prebuilt apps (details and evidence: notes/prebuilt-apps.md, written by the REA subagent, spot-checked)

| App | Result on macOS 27 | Root cause |
| --- | --- | --- |
| Official freeciv.org `Freeciv.app` 3.1.0-beta1 (2023, x86_64, Qt 5.15.8) | Does not launch via Finder/`open` (LaunchServices error -54, lsd: "Error -67062 validating the signing information"). Direct exec aborts in dyld: `@rpath/libfreeciv.dylib` with zero LC_RPATH, all other deps are absolute `/Applications/Freeciv.app/Contents/homebrew/...` paths. With a hand-built DYLD_LIBRARY_PATH the Qt5 main menu renders under Rosetta. | (d) bundle layout + (a) dylib graph, plus (c) completely unsigned. Not a toolkit/runtime problem. observed (REA trace_dylib_resolution, otool -l, codesign -dv, crash report .ips) |
| Community sabinomaggi `freeciv.app` 3.3.90.1-dev arm64 GTK3 (2025-04) | Launches via `open -W` and directly; GTK 3.22 main menu renders. Relocatable `@executable_path/../lib` graph, ad-hoc linker-signed, unsigned bundle, not notarized; launcher copies data into ~/.freeciv on every start. | Works, but Gatekeeper would block a browser-downloaded copy; no audio (no SDL2_mixer). observed |
| Community sabinomaggi `freeciv.app` 3.3.90.1-dev arm64 SDL2 | Launches, "SDL2 Client for Freeciv" window renders. Same bundle as above except the launcher's exec line. | Works, same caveats. observed |

Spot-checks I ran myself (observed): `lipo -archs` official freeciv-qt = x86_64; `vtool -show-build` minos 11.0 sdk 11.3; `otool -l | grep -c LC_RPATH` = 0; `codesign -dv` = "code object is not signed at all". Community freeciv-gtk3.22: arm64, minos 15.0 sdk 15.4, `Signature=adhoc`, flags `0x20002(adhoc,linker-signed)`.

## 2B. Build from source (Freeciv S3_2 = 3.2.6+, commit 44e6898c, meson 1.12.1, Homebrew deps)

Config (same env as upstream's `scripts/ci-build.sh mac-meson`):
```
export CPPFLAGS="-I$(brew --prefix gettext)/include -I$(brew --prefix readline)/include"
export LDFLAGS="-L$(brew --prefix gettext)/lib -L$(brew --prefix icu4c)/lib -L$(brew --prefix readline)/lib"
export PKG_CONFIG_PATH="$(brew --prefix icu4c)/lib/pkgconfig"
meson setup build-qt   -Dclients=qt          -Dfcmp=qt        -Dqtver=qt6 -Daudio=sdl2 -Dtools=ruledit,manual,ruleup -Ddebug=true
meson setup build-gtk  -Dclients=gtk3.22,gtk4 -Dfcmp=gtk3,gtk4            -Daudio=sdl2 -Dtools=manual,ruleup -Ddebug=true
meson setup build-sdl2 -Dclients=sdl2        -Dfcmp=cli                  -Daudio=sdl2 -Dtools=manual,ruleup -Ddebug=true
```

| Stage | Qt (6.12.0) | GTK 3.22 (3.24.52) | GTK4 (4.24.1) | SDL2 (sdl2-compat 2.32.74 on SDL3 3.4.18) | Server |
| --- | --- | --- | --- | --- | --- |
| meson setup | OK | OK | OK | OK | OK |
| compile (unpatched) | **FAIL** `client/gui-qt/gui_main.cpp:26 'SDL2/SDL.h' file not found` | **FAIL** `client/gui-gtk-3.22/gui_main.c:26` same | not reached (same target shape, derived) | OK | OK |
| compile (with patches/0001) | OK (40 warnings: -Wcast-align, -Wimplicit-fallthrough, -Wgnu-folding-constant) | OK | OK | OK | OK |
| link + install | OK | OK | OK | OK | OK |
| launch from shell, main menu | OK, "Freeciv (Qt6)" window, correct rendering (logs/qt-launch/shot.png) | OK (logs/gtk3-launch/window.png) | OK, one `Gdk-WARNING gdk_frame_timings_presented() called on skipped frame` | OK, 640x512 pt window, "Using Video Output: cocoa" (logs/sdl2-launch) | n/a |
| autoconnect to local server, pregame page | OK | OK | OK | OK | 4 AI + 1 human |
| server `start`, in-game map render | OK, hexemplio tiles, sidebar, minimap, unit panel (logs/qt-game/02-ingame.png) | OK, in-window menubar Game/Edit/View/... (logs/gtk3-game/02-ingame.png) | OK, no in-window menubar (native NSMenu, see 2C) (logs/gtk4-game/02-ingame.png) | OK, own widget toolkit renders (logs/sdl2-game/02-ingame.png) | 100-turn autogame with 10 AIs: 43 s, exit 0 |
| server `save` | OK probe1.sav.gz | OK | OK | OK | |
| server `load` + `start` again | OK, client follows back into the game | OK | OK | OK | |
| server `quit` | client shows "Lost connection: server disconnected" and returns to main menu | same | same | same | |
| client SIGTERM | **ignored**, needs SIGKILL | **ignored** | **ignored** | exits 0 | |
| crash reports (DiagnosticReports diff) | none | none | none | none | none |
| audio | not verified (no sound device check; SDL2_mixer linked) | | | | |
| menus, dialogs, keyboard, trackpad | see 2C | | | | |

Observed in `sample` stack traces: Qt runs `QCocoaEventDispatcher -> [NSApplication run]`; GTK3 `gtk_main -> g_main_loop_run -> poll_func (gdk quartz) -> nextEventMatchingMask`; GTK4 `g_application_run -> poll_func (libgtk-4) -> nextEventMatchingMask`; SDL2 `gui_event_loop -> SDL_SYS_DelayNS (libSDL3.0.dylib)` i.e. the "SDL2" client really runs on SDL3 through sdl2-compat.

Note on the first game-probe attempt: `set timeout -1` turned on the server's autogame test mode (debug builds only, per `help timeout`) and the game raced to turn 580 with the human idle. Not a port bug; the probe was rerun with `timeout 0`.

### Failure 1 (build): missing SDL include path for gtk3.22 / gtk4 / qt clients
- Error: `fatal error: 'SDL2/SDL.h' file not found` at `client/gui-qt/gui_main.cpp:26` and `client/gui-gtk-3.22/gui_main.c:26` (observed, logs/ninja-qt.log, logs/ninja-gtk.log).
- Cause: `meson.build` executables `freeciv-gtk3.22` (S3_2 line 3354), `freeciv-gtk4` (3447), `freeciv-qt` (3574) list `dependencies: [<toolkit>_dep, net_dep, gettext_dep, mw_extra_dep]` without `audio_dep`; `client_common` (line 2246) has it but meson does not propagate include dirs through `link_with` of a static library. `freeciv-sdl2`, `freeciv-sdl3`, `freeciv-stub` do list `audio_dep`. On Linux `/usr/include/SDL2/SDL.h` is on the default search path so nobody noticed. (derived from meson.build + compile command in logs/ninja-qt.log which has no `-I/opt/homebrew/include`.)
- Why upstream's own macOS CI passes: unknown. Their mac-meson job uses `-Daudio=sdl3` and `brew install lua@5.4 jpeg qt@6`; `pkg-config --cflags sdl3` here does contain `-I/opt/homebrew/include` but sdl3main_dep is also not attached to those targets. Possibly a transitively-included `-I/opt/homebrew/include` from another dependency on the runner. Not verified.
- Fix: patches/0001-build-add-audio-dependency-to-gtk3.22-gtk4-and-Qt-cl.patch (3 lines). Verified: all three clients compile, link, run.

### Failure 2 (launch): app bundle launched via LaunchServices hangs in dyld when the install prefix is under ~/Desktop
- Symptom: `open FreecivGTK4.app` (a minimal bundle wrapping the installed `freeciv-gtk4`, prefix `~/Desktop/freeciv-port/builds/gtk`) never shows a window; process sits in `dyld4::prepare -> loadDependents -> ... realpath -> __open` for minutes; `sample` and `lldb` attach hang on it too; `kill -9` works. The same binary executed from a shell starts in ~3 s. (observed, logs/gtk4-menu/dyld-stuck-sample.txt)
- `DYLD_PRINT_SEARCHING=1` via `LSEnvironment` shows the first and only path attempted: `find path "/Users/johnodell/Desktop/freeciv-port/builds/gtk/lib/libfreeciv.dylib"` (observed, logs/gtk4-menu/dbg-stderr.log).
- Cause (inferred, strong): macOS privacy protection (TCC) for the Desktop folder. A LaunchServices-launched app has no Desktop permission, so the kernel blocks the `open()` while tccd shows a consent dialog that nobody answered. Shell-launched processes inherit the terminal app's Desktop permission. tccd's log payload is private so the prompt itself was not captured (unknown).
- Consequence for the port: a redistributable `.app` must be self-contained (dylibs and data inside `Contents/`), and testing bundles must install to a non-protected prefix. Not a Freeciv or toolkit bug. Work-around used here: reinstall with `-Dprefix=$HOME/freeciv-builds/<client>`.

## 2C. Native menu bar and dialogs (the Tk-freeze failure class)


**Not verified tonight.** Driving the native menu bar needs either Accessibility permission for the automation host
(REA `observe_native_ui` returned `accessibility-denied`; `osascript` System Events returned -25211) or a human.
Changing Privacy & Security settings is outside this session's remit, so the following is left for a 5-minute manual pass.
What *was* observed: all four clients idle correctly in their Cocoa event loops (sample stacks above); Qt's menu
activation is queued by design (notes/macos27-toolkits.md section 4) and SDL has no app-level menu, so only GTK4 is
structurally exposed to the Tk-class freeze (native `gtk_application_set_menubar` + nested `g_main_loop_run` in
`client/gui-gtk-4.0/gui_stuff.c blocking_dialog()`; a June 2026 forum report of a "dead menubar on first launch" with
Homebrew gtk4 on macOS 26 exists, see notes/upstream-survey.md).

Morning checklist (each client, in-game):
1. Start: `~/freeciv-builds/<qt|gtk>/bin/freeciv-<qt|gtk4|gtk3.22>` from Terminal, or `open ~/freeciv-builds/apps/Freeciv<Qt|GTK4>.app`. Start a new game from the main menu.
2. Menu bar: open Game > Options > Local client options (GTK4: Game > Options; Qt: Game > Options) and Help > About. Expect a dialog; beach ball = the Tk class. While frozen: `sample $(pgrep -f freeciv-gtk4) 5 -file ~/Desktop/freeciv-port/logs/freeze.txt`.
3. Dialogs: open the City dialog (click a city), Research dialog (F6), Players (F3). Close each with its button and with ⌘W/Esc.
4. Keyboard: ⌘Q, ⌘N (Qt), Ctrl vs Cmd in the help texts (upstream RM #1293), arrow keys to move a unit, "+/-" zoom.
5. Trackpad: two-finger scroll over the map (should pan), pinch (Qt zooms? GTK no), right-click menu on a tile.
6. Retina: compare crispness of map text at 100% zoom; GTK3.22 is expected blurry on 26.5+/27 (GTK #8233, Homebrew 3.24.52_1 lacks fix d75c8720), SDL2 window is 1x (640x512 pt, upscaled; observed).
7. Audio: enable sound in options, found a city, listen.
8. Quit via menu Game > Quit, and via ⌘Q; confirm the process exits (SIGTERM is ignored by GTK/Qt clients, observed).

## 2D. HiDPI (observed from per-window `screencapture -l`)
- Qt: 1728x1030 pt window captured at 3680x2284 px, text and tiles crisp -> 2x backing store. GTK4: same, crisp UI text; chat console font tiny but sharp. GTK 3.22: window content crisp at the main menu; in-game not checked for the #8233 blur (needs eyes).
- SDL2: 640x512 pt window; the client never requests `SDL_WINDOW_ALLOW_HIGHDPI`, output is 1x and upscaled (blurry at 2x capture). Resolution is a client option; default is small.
