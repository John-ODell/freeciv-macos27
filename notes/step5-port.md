# Step 5: the port (build, run, package) - results

Date: 2026-10-16. Approved plan: notes/root-cause-and-plan.md section 3 (P1 build script, P2 self-contained Qt
.app, P3 ad-hoc signed DMG, then the other clients). Label key: observed / derived / inferred / unknown.
Evidence lives in `logs/` (git-ignored); GitHub: issues 5, 7, 8, 14 and PRs 9, 11, 12 in John-ODell/freeciv-macos27.

## What exists now

| Piece | Command | Output | Verified by |
| --- | --- | --- | --- |
| Reproducible build | `scripts/build.sh qt\|gtk\|sdl2\|all` | `~/freeciv-builds/<client>/` release install (`buildtype=release`, `debug=false`, patches 0001+0002) | 477-step rebuild 21 s wall (qt); gtk and sdl2 built the same way (logs/build-*.log) |
| Smoke test | `scripts/test.sh <prefix>` | autogame 100 turns / 10 AIs over a held-open FIFO, then save/load/restart probe per client | qt PASS (autogame 20 s), gtk PASS (gtk4 + gtk3.22 probes), sdl2: autogame ok, probe see below |
| Bundle | `scripts/bundle.sh qt\|gtk4\|gtk3.22\|sdl2` | `~/freeciv-builds/apps/{Freeciv,Freeciv-GTK4,Freeciv-GTK3,Freeciv-SDL2}.app`, 136-159 MB, ad-hoc signed, `LSMinimumSystemVersion` 27.0 (computed) | `codesign --verify --strict --deep` ok; `open` + `lsof`: only bundle, /System, /usr/lib images (44/63/56/50 bundled images loaded) |
| DMG | `scripts/dmg.sh <App.app> [--sign ID --notarize-profile P]` | `Freeciv-3.2.6-arm64.dmg` 85 MB + sha256 | `hdiutil verify` VALID; mounted app signature ok; signing/notarization path untested (no credentials) |
| Upstream patches | `patches/0001`, `patches/0002` + `notes/upstream-ticket-000{1,2}.md` | audio_dep on gtk/qt targets; `FREECIV_LOCALE_PATH` | both `git am` cleanly on upstream S3_2 44e6898c; not posted |

## Bundle anatomy (all four, observed)
- `Contents/MacOS/<Launcher>`: bash launcher exporting `FREECIV_DATA_PATH`, `FREECIV_SCENARIO_PATH`, `FREECIV_LOCALE_PATH`
  (GTK: also `GSETTINGS_SCHEMA_DIR`, `XDG_DATA_DIRS`, `FONTCONFIG_PATH`, `GDK_PIXBUF_MODULE_FILE`), `cd` to MacOS so the
  client's `./freeciv-server` lookup (client/connectdlg_common.c:424) hits the bundled server, then `exec` the client.
  Launcher is named `<App>-launcher` where `<App>` would collide case-insensitively with the client binary (APFS).
- `Contents/MacOS/freeciv-<client>, freeciv-server, freeciv-mp-<x>[, freeciv-ruledit]`.
- `Contents/Frameworks/`: closure of Homebrew dylibs (+ Qt frameworks minus Headers), ids/loads `@rpath/...`,
  rpaths `@executable_path/../Frameworks` + `@loader_path/../Frameworks` and none that lead out of the bundle
  (issue 61: Homebrew left the Qt plugins `@loader_path/../../../../lib`, /Applications/lib for an app in
  /Applications, and libSDL2 `@loader_path/../../../../opt/sdl3/lib`, /opt/sdl3/lib there; fix-dylibs.py deletes
  them and fails on any left); `libSDL3.0.dylib` + `libSDL3.dylib` symlink for sdl2-compat's dlopen.
  `Contents/PlugIns/` (Qt): platforms/qcocoa, styles/qmacstyle, imageformats gif/ico/jpeg.
- `Contents/Resources/share/freeciv` (46 MB data), `share/locale` (25 MB), GTK: `share/glib-2.0/schemas/gschemas.compiled`,
  `etc/fonts` (dereferenced conf.d, Homebrew cache dir removed), empty `etc/gdk-pixbuf-loaders.cache`.
- Info.plist: version from fc_version, `NSHighResolutionCapable`, `.sav*` document types, category strategy-games.

## Per-client results (bundles, launched both with `open` and through the launcher-driven game probe)

| Client | `open` main menu | self-contained (`lsof`) | game probe (start, save, load, restart, quit) | Notes |
| --- | --- | --- | --- | --- |
| Qt | ok (logs/bundle-qt-open) | yes, 44 images, incl. libSDL3 + qcocoa | pass: start, autosave + explicit save, load, restart, server quit -> "Lost connection" (logs/bundle-qt-game, 6 shots, no crash reports); in-game render checked by eye | |
| GTK4 | ok (logs/bundle-Freeciv-GTK4-open) | yes, 63 images; gtk40.mo still read from /opt/homebrew (GTK's own translations use its compiled-in localedir; falls back to English elsewhere) | pass: start, autosave + explicit save, load, restart, server quit -> "Lost connection" (logs/bundle-gtk4-game, 6 shots, no crash reports) | |
| GTK 3.22 | ok (window 1728x1030 on first launch) | yes, 56 images | pass, same sequence (logs/bundle-gtk3-game); in-game window goes 1728x1030 and is crisp at 2x in the capture, so GTK #8233 blur is not visible here (needs eyes) | Gtk-WARNING: cannot load Adwaita `bullet-symbolic.svg` (no SVG pixbuf loader; same on the Homebrew install, derived) |
| SDL2 | ok, 601x480 pt window | yes, 50 images | pass, same sequence (logs/bundle-sdl2-game); client exits 0 on SIGTERM. One earlier install-probe run disconnected at game start (issue 15) | |

## Gatekeeper (observed)
`spctl -a -t exec` rejects the ad-hoc bundle with and without `com.apple.quarantine`; Gatekeeper assessments are
enabled on this machine. A downloaded copy needs Open Anyway or `xattr -dr com.apple.quarantine`; the DMG README says
so. Only `dmg.sh --sign <Developer ID> --notarize-profile <p>` removes that, which needs John's Apple Developer account.

## Not verified / open
- Menus, dialogs, keyboard, trackpad, audio by hand (issue 3). Non-English UI (locale path is set and exists).
- Second machine without Homebrew (none available); `lsof` is the proxy.
- `dmg.sh --sign/--notarize-profile` (no credentials).
- Probe scripts were fixed twice today (release server rejects `-F`; relative `--saves` path doubled the save path), so
  the earliest bundle probe runs did not actually exercise save/load; the reruns in this note did.
- GTK clients and Qt still ignore SIGTERM (issue 4).
