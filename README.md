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
| `scripts/` | `build.sh` (configure+build+install), `test.sh` (autogame + save/load probe), `bundle.sh` + `fix-dylibs.py` (self-contained .app with a compiled `launcher.c` and the `collect-licenses.py` notices), `sign-app.sh` (ad-hoc or Developer ID, hardened runtime), `dmg.sh` (DMG, optional notarization), and the probe helpers used for the evidence. | Yes |
| `notes/` | Findings: project map, reproduction logs, REA analysis of prebuilt apps, root cause, plan, backlog, install log, Civ4/5 planning menu (`civ45-planning.md`), the proposal for the port, civ45 and civ54 as two or three games (`game-directions.md`), and the Freeciv45 build plan (`freeciv45-plan.md`, research in `freeciv45/`). | Yes |
| `downloads/` | Prebuilt macOS apps and tarballs used for diagnosis. | No |
| `inbox/` | Notes between this desk and other Claude desks (rules in `inbox/README.md`). Local only. | No |

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
`test.sh ... --ruleset civ45` runs the autogame on civ45, the ruleset of Freeciv45 (patches 0003, 0004, 0006 and 0008 to 0010: sandbox
plus stacks of units on a square map, siege units that wound whole stacks, fights to the death, six ways to win, upgrades
that keep veterancy and draft units raised from a citizen, see
`port/freeciv/data/civ45/README.civ45` after applying the patches); `--lua FILE` loads a script before the game starts,
for example `scripts/civ45-combat-log.lua`, which logs every attack, bombardment, unit lost and city taken for counting
(`scripts/civ45-combat-summary.py`), or `scripts/civ45-draft-log.lua`, which logs draft units built, cities shrunk by a
build and units disbanded into a build (`scripts/civ45-draft-summary.py`, which also reads city sizes from a save);
`test.sh` reads the installed data unless given `--data port/freeciv/data`, and its result line names the directory
the ruleset came from. `--ruleset civ54` does the same for civ54, the copy of civ45's earlier one-unit-per-tile hex
rules kept for the later Civ5-style game (patch 0005, `data/civ54/README.civ54`). `scripts/check-stacking.py SAVE.gz`
counts units per tile in the saves an autogame leaves behind (add `--ruleset port/freeciv/data/civ54` to apply civ54's
exemptions for aircraft and ships in port, or `--report` for civ45, where stacks are the rule).
`scripts/civ45-rules-test.sh ~/freeciv-builds/qt` checks Freeciv45's rules in a game with one human-controlled
player: the map and stack settings, moving onto a friendly unit and into an occupied city, a three-unit stack that
keeps two units when its defender loses, a stack still together a turn later, and the combat rules: a siege unit's
bombardment wounds a three-unit stack without killing (a Warriors then beats its defender) and is refused against a lone
unit, a Bomber bombards at range 1 only, a duel of equals ends with one unit dead, and a Withdraws attacker breaks off;
and the ways to win: the victory settings, the domination script's counting and decision, and with
`--extra "set endturn 6"` the score winner the ruleset names at the last turn; and the draft: the draft units and their tech
gate, an upgrade in the Tester's own city that keeps the unit hardened and costs the computed price, and a Levy disbanded
into the build, whose 30 shields the runner reads from the next autosave.
`--extra "set killstack enabled"` is the control run, which must fail. `scripts/civ54-rules-test.sh ~/freeciv-builds/qt` checks civ54's rules
directly: it loads `scripts/civ54-rules-test.lua` into a civ54 game with one human-controlled player, moves a land
unit, a fighter and destroyers at a coastal city at turn 12, runs the turn-start sweep, and exits 0 only if every case
passes and the server log holds no Lua error.
`scripts/ruleset-look.sh CLIENT OUTDIR` plays a ruleset (civ45 unless `--ruleset`, read from the source tree) in a
real client and captures every client window at pregame and at turn 1; the client runs on an options file of its own
in OUTDIR (notes/freeciv45/client-look.md).
`scripts/harness-test.sh ~/freeciv-builds/qt` tests the harness hook of patch 0007, which hands named AI players'
build and research choices to a program outside the server, for play-testing (`notes/freeciv45/harness.md`). It
plays a 50-turn civ45 game in which `scripts/harness-chooser.py` answers at random (`--mode first`: always the AI's
own pick), checks the decisions against the saves with `scripts/harness-check.py`, and plays a control game on the
same seeds without the hook.
Install prefixes and bundles live outside `~/Desktop`, `~/Documents` and `~/Downloads` on purpose: macOS privacy
protection stalls Finder-launched apps whose libraries sit in those folders (notes/reproduction.md, Failure 2).
Without an Apple Developer ID the app is ad-hoc signed; Gatekeeper rejects a downloaded copy until the user chooses
Open Anyway. With a Developer ID certificate, `bundle.sh --sign` and `dmg.sh --sign ... --notarize-profile ...`
produce a notarized DMG; the one-time setup and the commands are in `notes/release.md`.
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

Everything in this repository (scripts, patches, notes) is free software under the GNU General Public
License, version 2 or (at your option) any later version: the same terms as Freeciv. The full text is in
`LICENSE`, and each script starts with an `SPDX-License-Identifier: GPL-2.0-or-later` line. Patches under
`patches/` modify Freeciv's GPL-2.0-or-later code and keep the upstream licence headers intact.
Until 2026-10-16 this section said scripts and notes were MIT; copies taken before then may still be used
under MIT.

The macOS app also contains libraries from Homebrew under their own licences (LGPL, GPL-3.0, MIT, BSD and
others). Each build lists them, with licence texts and source locations, in
`Freeciv.app/Contents/Resources/licenses/THIRD-PARTY-NOTICES.txt`, written by `scripts/collect-licenses.py`.
