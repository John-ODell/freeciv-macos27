# Step 4: Root causes, fix plan, and "make it better" backlog

Written 2026-10-16 after Steps 0-3. Label key: observed / derived / inferred / unknown. Every claim points at a file,
log, ticket or URL; the long-form evidence is in the other notes (reproduction.md, prebuilt-apps.md, upstream-survey.md,
macos27-toolkits.md, project-map.md). **Nothing below Step 4 has been started; this document is the approval gate.**

## 1. Headline

Freeciv 3.2.6+ (S3_2) builds and runs on macOS 27.0.1 arm64 with Homebrew after a 3-line meson fix. All four clients
(Qt 6, GTK 3.22, GTK4, SDL2) and the server render, connect, play, save and load; no crash reports (reproduction.md 2B).
The problems are not "Freeciv is broken on macOS 27". They are: (1) one upstream build bug, (2) there is no usable
redistributable macOS build anywhere, and (3) a short list of toolkit-level macOS 26/27 regressions that affect polish.
The Tk-class menu freeze was *not* reproduced and could not be tested headlessly (reproduction.md 2C): Qt and SDL are
structurally immune; GTK4 needs a 5-minute manual check.

## 2. Root causes per failure

| # | Failure | Root cause | Label | Evidence |
|---|---|---|---|---|
| F1 | gtk3.22 / gtk4 / qt clients fail to compile: `'SDL2/SDL.h' file not found` | `meson.build` executable targets `freeciv-gtk3.22` (S3_2:3354), `freeciv-gtk4` (:3447), `freeciv-qt` (:3574) omit `audio_dep`; meson does not propagate a static library's include dirs through `link_with`. Linux hides it because `/usr/include/SDL2` is on the default path. | derived | logs/ninja-qt.log compile line has no `-I/opt/homebrew/include`; `client_common` at meson.build:2246 has `audio_dep`; sdl2/sdl3/stub targets have it. Fix verified: patches/0001, all clients build and run. Why upstream mac-meson CI passes: unknown (it uses `-Daudio=sdl3`). |
| F2 | App bundle launched with `open` hangs in dyld forever; same binary from a shell starts in 3 s | macOS privacy protection (TCC) for ~/Desktop: a LaunchServices-launched process has no Desktop grant, so `open()` on `~/Desktop/.../lib/libfreeciv.dylib` blocks in the kernel waiting for a consent dialog. Shell processes inherit Terminal's grant. | inferred (strong) | logs/gtk4-menu/dyld-stuck-sample.txt (`dyld4::prepare -> loadDependents -> realpath -> __open`), logs/gtk4-menu/dbg-stderr.log (`DYLD_PRINT_SEARCHING` shows that exact path as the first open), reinstall to `~/freeciv-builds` fixed it. The tccd prompt itself was not captured (log payload private): unknown. |
| F3 | Official freeciv.org `Freeciv.app` 3.1.0-beta1 does not launch | Four independent defects: x86_64-only (Rosetta needed); `@rpath/libfreeciv.dylib` with zero `LC_RPATH`; every other dependency is an absolute `/Applications/Freeciv.app/Contents/homebrew/...` path (works only when installed at that exact location); completely unsigned, so LaunchServices refuses it (-54 / -67062) before dyld even runs. Toolkit (Qt 5.15.8) is fine: with a hand-built `DYLD_LIBRARY_PATH` the menu renders under Rosetta. | observed | prebuilt-apps.md 1.2-1.7: `lipo -archs`, `otool -l` (0 LC_RPATH), `codesign -dv` ("not signed at all"), REA `trace_dylib_resolution`, logs/prebuilt/official-*.log and .ips. Recipe that produced it: `refs/freeciv-S3_2/platforms/macos/homebrew-appbundle.sh` (same Info.plist template; project-map.md). |
| F4 | Community sabinomaggi arm64 bundles run here but would not for a normal download | Ad-hoc linker-signed, not Developer-ID signed, not notarized; a quarantined copy hits Gatekeeper "damaged / can't be opened". Launcher script copies data into `~/.freeciv` on every start. No SDL2_mixer so no audio. | observed (launch) / derived (Gatekeeper, from codesign flags; not exercised because no quarantine attr was present) | prebuilt-apps.md 2.4, 2.6, 3.1; Freeciv21 issue #2777 describes the identical failure mode for their CI output. |
| F5 | Server probe raced to turn 580 | Not a bug. `set timeout -1` is the debug-build autogame mode (`help timeout`). | observed | reproduction.md 2B note. |
| F6 | GTK and Qt clients ignore SIGTERM | Clients install no SIGTERM handler (grep of `client/*.c` for `signal(`/`SIGTERM` finds only the `kill(server_pid, SIGTERM)` in `client/connectdlg_common.c:160,202`); the server does handle it in `server/srv_signal.c:86`. Needs `kill -9`; Dock quit path untested. | observed / cause derived from grep | reproduction.md 2B "client SIGTERM" row. |
| F7 | SDL2 client renders at 1x on Retina (640x512 pt, upscaled, blurry) | Client never requests `SDL_WINDOW_ALLOW_HIGHDPI`; under sdl2-compat/SDL3 that means a 1x backing store. Default resolution option is small. | observed (shot) / cause derived (grep of client/gui-sdl2, no ALLOW_HIGHDPI) | reproduction.md 2D; macos27-toolkits.md section 3. |

Toolkit-level issues that are *expected* on this machine but not yet seen with eyes (all from macos27-toolkits.md):
- GTK 3.22 blurry HiDPI content on macOS 26.5+/27: GTK #8233, fixed by d75c8720 on gtk-3-24 (2026-06-17) but in no tagged
  release; Homebrew `gtk+3` 3.24.52_1 lacks it. (expected, unverified on 27.0.1)
- GTK4 native menubar shows shortcuts without ⌘ glyph on macOS 27: GTK #8435, open. (expected)
- GTK4 focus loss / dead menubar on first launch: forum t=95527 (June 2026, macOS 26, Homebrew gtk4), unanswered. (unknown)
- Qt 6.12.0: invisible item-view check indicators with the macos style (QTBUG-150017, fixed 6.12.1), hidden native menu
  icons (QTBUG-151046, open), dark-mode line-edit borders (QTBUG-149290, fixed 6.12.1), tooltip placement (QTBUG-141541).
  Homebrew has 6.12.0 as of 2026-10-15. (expected)
- sdl2-compat: held key opens the accent popup and stops key repeat (sdl2-compat #620); `SDL_MAC_PRESS_AND_HOLD=0` works
  around it. (expected)

## 3. Fix plan, in priority order (port first)

Principle: upstream-shaped changes go into `port/freeciv` as small commits with matching `patches/NNNN-*.patch`; macOS
packaging that upstream declared a dead end (RM #1731) lives in this repo under `scripts/` and `packaging/` so it needs
no upstream buy-in to be useful, but is written so it *could* be offered as a `platforms/macos/` replacement later.

### P1. Build reproducibly on macOS 27 (one command)
1. `scripts/build.sh <qt|gtk|sdl2|all> [--debug]`: pins the brew formula list (`qt gtk+3 gtk4 sdl2-compat sdl2_{image,ttf,mixer,gfx} meson ninja pkgconf gettext readline icu4c@78 curl lua@5.4`), exports the CI env (ci-build.sh:107-112 shape), runs `meson setup` with the exact options used in reproduction.md 2B, `ninja`, `ninja install` into `~/freeciv-builds/<client>` (outside TCC-protected folders, F2). Idempotent; logs to logs/.
2. Carry patch 0001 (F1) in the port branch; add `-Daudio=sdl3` as an option so the default matches upstream CI
   (upstream-survey.md "Known blockers" 3) and fall back to sdl2 only if the sdl3 mixer stack is missing.
3. `scripts/test.sh`: server autogame smoke (100 turns, 10 AIs; 43 s observed) plus the FIFO-driven save/load/restart probe
   from scripts/game-probe.sh for whichever client was built. Effort: S. Risk: low. Value: high (everything else depends on it).

### P2. Make it run as a Mac app (self-contained, unsigned-but-valid)
4. `scripts/bundle.sh <client>`: assemble `Freeciv-<client>.app` with `Contents/{MacOS,Frameworks,Resources}`; copy the
   installed `share/freeciv` data and locale into Resources; copy the transitive dylib closure (6 direct Homebrew deps for
   Qt, 11 for gtk; closure ~60-120 dylibs, size to be measured) into Frameworks; rewrite `LC_ID_DYLIB`/`LC_LOAD_DYLIB` to
   `@rpath/...` with `install_name_tool` and add `LC_RPATH @executable_path/../Frameworks`; for Qt also copy the
   `plugins/platforms/libqcocoa.dylib` (+ imageformats, tls) and write `qt.conf` or rely on 6.12's relocatable defaults
   (macos27-toolkits.md section 1, release note c596e7af244); for the SDL stack explicitly copy `libSDL3.0.dylib` because
   sdl2-compat dlopens it (sdl2-compat #611). GTK additionally needs `lib/gdk-pixbuf-2.0/loaders` + `loaders.cache`,
   glib schemas (`glib-compile-schemas`), and `GTK_PATH`/`GDK_PIXBUF_MODULE_FILE` set from a tiny launcher or via
   `LSEnvironment` in Info.plist. Freeciv must find its data: `FREECIV_DATA_PATH` via `LSEnvironment`, or a thin
   `Contents/MacOS/launcher` shell that computes it from `$0` (the sabinomaggi approach, but without copying to ~/.freeciv).
5. Info.plist: `CFBundleIdentifier org.freeciv.<client>`, `CFBundleExecutable`, `CFBundleIconFile` from
   `data/freeciv-client.icns` (exists, project-map.md), **`NSHighResolutionCapable true`**, `LSMinimumSystemVersion`
   = the minos of the slowest dylib in the closure (Homebrew golden_gate bottles are built for 27; report it honestly),
   `CFBundleShortVersionString` from `fc_version`, `NSSupportsAutomaticGraphicsSwitching`.
6. Ad-hoc sign the whole bundle inside-out (`codesign --force --sign - --deep` is deprecated; sign Frameworks first, then
   the executable, then the bundle) and verify with `codesign --verify --deep --strict` and `spctl -a -t exec` (expect
   "rejected" without Developer ID, documented). Test: `open` from a non-protected folder, from Finder, and a copy that has
   been given `com.apple.quarantine` by hand to observe the exact Gatekeeper behaviour on 27 (currently derived only, F4).
7. Verification loop per client: launch via `open`, main menu, new game vs 4 AIs, play 5 turns by keyboard, save, quit via
   menu, relaunch, load, quit via ⌘Q; `sample` if anything beachballs. Effort: M (Qt), L (GTK: pixbuf/schemas/
   immodules), S (SDL2). Risk: medium (dylib closure drift when brew upgrades; mitigated by bundling). Value: high.

### P3. Package: signed arm64 .app and DMG
8. `scripts/dmg.sh`: `hdiutil create` (or `create-dmg` as Freeciv21 does, upstream-survey.md section 6) with an
   `/Applications` drop link, `.icns` volume icon, sha256 sidecar. Never committed (gitignore already excludes *.dmg).
9. Signing: if a Developer ID certificate is available, `codesign --timestamp --options runtime` with an entitlements
   file (`com.apple.security.cs.disable-library-validation` is *not* needed if every dylib is signed with the same
   identity; `allow-unsigned-executable-memory` is not needed for Lua 5.4 without JIT), then `xcrun notarytool submit`
   + `stapler`. Without one, ship ad-hoc-signed with the documented right-click > Open path and say so in the README.
   This is the only step that needs something from you (an Apple Developer account). Effort: S-M. Risk: low. Value: high
   for distribution, zero for your own use.
10. Optional GitHub Actions workflow on this repo (not upstream): macOS arm64 runner, build + bundle + dmg, artefact upload;
    signing only on tags with secrets. Effort: M. Risk: low. Value: medium.

### P4. Upstream what belongs upstream (draft only, never posted without your review)
11. RM ticket + patch for F1 (text drafted in notes/upstream-ticket-0001.md), one patch per branch (S3_2, S3_3, main) per
    cazfi's convention (upstream-survey.md "How upstream wants patches").
12. Later, if P2 works well: a feature ticket proposing `platforms/macos/` bundle tooling with a rationale (bundled dylibs,
    `NSHighResolutionCapable`, signing), pitched against main with S3_2 backports; expect pushback given RM #1731.

## 4. "Make it better" backlog (after the port is done; each item is one issue in this repo)

Effort S/M/L = under a day / a few days / a week+. Risk = chance of breaking something or being unupstreamable.

| # | Item | Client | Effort | Risk | Value | Notes / evidence |
|---|---|---|---|---|---|---|
| B1 | Retina for SDL2 client: request `SDL_WINDOW_ALLOW_HIGHDPI`, scale UI by `SDL_GetRendererOutputSize / window size`, bigger default resolution | sdl2 | M | M (the SDL client draws with its own pixel-based widget toolkit; every blit assumes 1x) | M | F7; macos27-toolkits.md 3. Upstream is moving to sdl3 client, so do it there if at all (RM #2249). |
| B2 | GTK3 HiDPI blur fix: build `gtk+3` from gtk-3-24 or add d75c8720 + 87d0980c as patches in our bundle recipe (not a Freeciv change) | gtk3.22 | S | L | H if you use gtk3.22 | GTK #8233 (expected, verify first with eyes). |
| B3 | Native macOS menu bar polish: Qt menu roles already handled (RM #1672); add `QAction::setMenuRole` for Preferences/Quit so they sit in the app menu; GTK4 ⌘ glyph bug is GTK #8435 (not ours; document) | qt, gtk4 | S | L | M | upstream-survey.md 1a. |
| B4 | Help > Controls text says Ctrl on Mac (RM #1293 open) : substitute Cmd under `__APPLE__` in `client/helpdata.c` or per-client help | all | S | L | M | Upstream-untaken, upstreamable. |
| B5 | Clean quit: handle SIGTERM in clients (`client/client_main.c`), and verify Dock "Quit" / ⌘Q path saves client options | all | S | L | M | F6; upstreamable. |
| B6 | Trackpad: two-finger scroll pans, pinch zooms (Qt: `QNativeGestureEvent` in `mapview`; GTK4: `GtkGestureZoom`; GTK3: `GDK_TOUCHPAD_PINCH` via `gdk-quartz`?) | qt first | M | M | H for feel | Not verified what exists today (2C checklist item 5). |
| B7 | Dark mode: Qt follows the system appearance automatically; Freeciv's hard-coded colours in `data/themes` / `client/gui-qt/fc_client.cpp` style sheets may clash; GTK3 needs `gtk-application-prefer-dark-theme` | qt, gtk | M | L | M | Check first; QTBUG-149290 cosmetic fix arrives with Qt 6.12.1. |
| B8 | Audio: default `-Daudio=sdl3` (matches upstream CI), bundle libSDL3 explicitly, verify sound plays; add `SDL_MAC_PRESS_AND_HOLD=0` for the sdl2 client | all | S | L | M | sdl2-compat #620, #611. Audio not verified yet. |
| B9 | Performance: profile turn-done and map redraw with Instruments on a large map; check `-Ddebug=true` vs release build first (all tonight's binaries are debug) | all | M | L | unknown until measured | Nothing observed; do not guess. |
| B10 | UI polish / QoL: remember window geometry per display, open the last save from the main menu, Cmd-based shortcuts table in Help, retina icons in the .app | qt | M | L | M | |
| B11 | AI behaviour improvements | server | L | H (gameplay balance, hard to upstream) | M | Only with a concrete complaint; the AI is shared with every platform. |
| B12 | Upstream-untaken bug fixes: Apple clang `-Wgnu-folding-constant` family (RM #2339/#2355/#2360, in progress upstream), `Strings.txt` stale macos vertags on S3_2 (RM #2177, fixed on main only) | all | S | L | L-M | Cheap goodwill patches. |
| B13 | Qt 6.12.1 bump when Homebrew ships it (fixes QTBUG-150017 invisible checkboxes, QTBUG-149290) | qt | S | L | H | Just rebuild/rebundle; nothing to code. |

## 5. Recommendation

Do P1 then P2 for the **Qt client only** first (Qt has the most Mac fixes in-tree, a queued menu dispatch that is immune
to the Tk-class freeze, crisp HiDPI already, and the smallest dylib closure), then P3 with ad-hoc signing. GTK4 is what
Homebrew ships but has the open macOS 26/27 reports (focus loss, dead menubar, GTK #8435); GTK 3.22 has the blur
regression; SDL2 is 1x and runs on a compat shim. Build and bundle those three afterwards as "also available". Then from
the backlog: B13 (free), B5 and B4 (small, upstreamable), B6 (biggest felt improvement), B2 only if you actually want
gtk3.22.

Before any of that, the 5-minute manual check in reproduction.md 2C would tell us whether GTK4's native menubar freezes
on 27; if it does, that becomes a P2 blocker for GTK4 and an upstream bug report, and the diagnostic is already written.

## 6. What is still unverified (carried forward)
- Menus, dialogs, keyboard shortcuts, trackpad and audio on all clients (reproduction.md 2C checklist).
- GTK 3.22 blur on 27.0.1 (expected from GTK #8233).
- Gatekeeper behaviour of a quarantined ad-hoc-signed bundle on 27 (derived from Freeciv21 #2777).
- Why upstream mac-meson CI compiles without `audio_dep` (F1).
- The exact TCC prompt behind F2 (payload private).
