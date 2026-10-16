# Releases

## How a release is cut

1. `scripts/build.sh qt` on a clean `port/freeciv` at the commit to ship (upstream S3_2 plus `patches/`).
2. `scripts/test.sh ~/freeciv-builds/qt` (100-turn autogame plus client save/load probe) must pass.
3. `scripts/bundle.sh qt`, then `scripts/game-probe.sh` against the bundle's `Contents/MacOS/Freeciv`.
   The bundle carries `Contents/Resources/COPYING` and `SOURCE.txt` (upstream commit, local patches).
4. `scripts/dmg.sh ~/freeciv-builds/apps/Freeciv.app` writes the DMG and its sha256.
5. Source tarball of the exact tree: `git -C port/freeciv archive --format=tar.gz --prefix=freeciv-<ver>-mac<N>/ -o freeciv-<ver>-mac<N>-src.tar.gz <commit>`.
   GPL v2 section 3 requires the matching source to be available with the binary; the tarball on the release
   page is that source, and `SOURCE.txt` in the bundle points to it.
6. `gh release create v<ver>-mac<N>` on John-ODell/freeciv-macos27 with the DMG, both sha256 files and the tarball.
   Release assets are not commits, so the "no binaries in git" rule from the brief holds.

Nothing is notarized unless `dmg.sh --sign <Developer ID> --notarize-profile <profile>` is used, which needs an
Apple Developer Program membership (99 USD/year, observed on developer.apple.com pricing as of 2026, unverified
for the current year). Without it macOS 27 Gatekeeper refuses the first launch (observed, notes/step5-port.md)
and the user must choose Open Anyway or clear the quarantine attribute. No App Store is involved either way.

## v3.2.6-mac1 (2026-10-16)

| Item | Value |
|---|---|
| Upstream | freeciv S3_2 commit 44e6898c |
| Local patches | 0001 audio dependency for client targets, 0002 FREECIV_LOCALE_PATH |
| Tree | port/freeciv 5e65e6b |
| Client | Qt 6.12.0 (Homebrew), arm64, minimum macOS 27.0 |
| Signing | ad-hoc, not notarized |
| Checks | build, 100-turn autogame, bundle save/load probe, DMG verify (logs/ of 2026-10-16) |
| Known issues | #3 manual UI pass not done, #4 SIGTERM, #15 SDL2 intermittent exit (not in this DMG) |
