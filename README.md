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
| `scripts/` | One-command build, bundle and sign scripts for macOS. | Yes |
| `notes/` | Findings: project map, reproduction logs, REA analysis of prebuilt apps, root cause, plan, backlog, install log. | Yes |
| `downloads/` | Prebuilt macOS apps and tarballs used for diagnosis. | No |

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
