# freeciv-macos27

Getting [Freeciv](https://www.freeciv.org/) running well on macOS 27 (Apple Silicon), then improving it.

Freeciv is the GPL empire-building game inspired by Civilization I/II. This repo holds
the macOS 27 port work: notes, build scripts, exported patches against upstream, and
packaging. It does not contain Freeciv itself, Civ2 code, or any Civ2 assets.

## Layout

| Path | What it is | In git? |
| --- | --- | --- |
| `refs/` | Shallow clones of the upstream repos (`freeciv`, `freeciv-S3_2`, `freeciv-web`, `freeciv-environments`, `freeciv-website`). Read-only reference. | No |
| `port/` | Working fork of Freeciv where fixes are made and built. Its own git repo. | No |
| `patches/` | Patches exported from `port/` with `git format-patch`, one per concern, upstreamable. | Yes |
| `scripts/` | `build.sh` (configure+build+install), `test.sh` (autogame + save/load probe), `bundle.sh` + `fix-dylibs.py` (self-contained .app), `dmg.sh` (DMG, optional Developer ID signing/notarization), and the probe helpers used for the evidence. | Yes |
| `notes/` | Findings: project map, reproduction logs, REA analysis of prebuilt apps, root cause, plan, backlog, install log, Civ4/5 planning menu (`civ45-planning.md`). | Yes |
| `downloads/` | Prebuilt macOS apps and tarballs used for diagnosis. | No |

## Download (macOS 27, Apple Silicon)

Releases: https://github.com/John-ODell/freeciv-macos27/releases. Each release has `Freeciv-<version>-arm64.dmg`,
its `.sha256`, and `freeciv-<version>-src.tar.gz`, the exact source the DMG was built from (upstream S3_2 plus
`patches/`). The app is ad-hoc signed, not notarized, so the first launch of a downloaded copy is refused by
Gatekeeper. Either open System Settings > Privacy & Security and choose Open Anyway after the refusal, or run:

```bash
xattr -dr com.apple.quarantine /Applications/Freeciv.app
```

Check the download first:

```bash
shasum -a 256 -c Freeciv-3.2.6-arm64.dmg.sha256
```

## Quick start (macOS 27, Apple Silicon, Homebrew)

```bash
git clone --depth 50 --branch S3_2 https://github.com/freeciv/freeciv.git port/freeciv
git -C port/freeciv am ../../patches/*.patch
scripts/build.sh qt                       # installs to ~/freeciv-builds/qt (Homebrew deps installed if missing)
scripts/test.sh ~/freeciv-builds/qt       # 100-turn autogame + client save/load probe
scripts/bundle.sh qt                      # ~/freeciv-builds/apps/Freeciv.app, self-contained, ad-hoc signed
scripts/dmg.sh ~/freeciv-builds/apps/Freeciv.app   # Freeciv-<version>-arm64.dmg + sha256
```

`build.sh gtk` / `build.sh sdl2` and `bundle.sh gtk4|gtk3.22|sdl2` do the same for the other clients.
`test.sh ... --ruleset civ45` runs the autogame on the civ45 ruleset (patch 0003: sandbox plus Civ4/5-style rules,
see `port/freeciv/data/civ45/README.civ45` after applying the patches), and `scripts/check-stacking.py SAVE.gz`
counts units per tile in the saves it leaves behind.
Install prefixes and bundles live outside `~/Desktop`, `~/Documents` and `~/Downloads` on purpose: macOS privacy
protection stalls Finder-launched apps whose libraries sit in those folders (notes/reproduction.md, Failure 2).
Without an Apple Developer ID the app is ad-hoc signed; Gatekeeper rejects a downloaded copy until the user chooses
Open Anyway (`dmg.sh --sign ... --notarize-profile ...` does the real thing when credentials exist).
The bundle's minimum system version is computed from its libraries; with today's Homebrew bottles that is
macOS 27.0, because `arm64_golden_gate` bottles are built for 27. A build on macOS 26 would produce a 26.x bundle.

## Plan

1. Tooling check, map the project, reproduce on macOS 27 (prebuilt app and source build).
2. Analyse the prebuilt app with REA (Mach-O slices, min OS, dylibs, signing).
3. Root cause and fix plan, then a "make it better" backlog.
4. Implement: build reproducibly, run, package as a signed arm64 `.app` and DMG.

Clients are tried in order Qt, GTK (3.22 then 4), SDL2. The server is always built.

## Workflow

GitHub work follows [github-cleanhub](https://github.com/John-ODell/github-cleanhub):
every unit of work is one issue, one branch, one pull request, one comment review and
one squash merge. Commits use Conventional Commit messages. No binaries, DMGs or
credentials are committed. Upstream clones and installed apps are never modified.

## License

Scripts and notes here are MIT unless stated otherwise. Patches under `patches/` modify
GPL-2.0-or-later code from Freeciv and are themselves GPL-2.0-or-later, with upstream
license headers kept intact.
