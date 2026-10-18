# Installed software log

Everything installed or changed on this machine for the Freeciv macOS 27 port.
Machine: Apple Silicon (arm64), macOS 27.0.1 (26A434), Xcode 27.0 (27A266a), Homebrew 7.0.9.

## Already present before this work (observed 2026-10-15, `brew list`, `xcode-select -p`)

- Xcode 27.0 at /Applications/Xcode.app, command line tools active.
- Homebrew 7.0.9 at /opt/homebrew with (relevant subset): cairo, cmake, fontconfig, freetype,
  fribidi, gettext 1.0, gh, git, glib, harfbuzz, icu4c@78 78.3, jpeg-turbo, libpng, ninja 1.13.2,
  node, openjdk, pixman, python@3.14, sqlite 3.54.0, xz, zstd.
- Hopper Disassembler at ~/Applications/Hopper Disassembler.app (used by REA as decompiler).
- REA (`rea-agents` 6.5.0 via npx), `reverse-engineer-anything` skill v42.
- Temurin 21 JDK (cask). Ghidra: NOT installed / not configured (GHIDRA_INSTALL_DIR unset).

## Installed on 2026-10-15 for this work (`brew install`)

Build tools:
| Formula | Version | Why |
| --- | --- | --- |
| meson | 1.12.1 | Freeciv's primary build system |
| pkgconf | 3.0.8 | pkg-config for meson dependency lookup |
| autoconf | 2.73 | autotools build (secondary) |
| automake | 1.19 | autotools build (secondary) |
| libtool | 2.6.2 | autotools build (secondary) |
| python@3.15 | 3.15.0 | pulled in as a dependency of meson |

Toolkits and libraries:
| Formula | Version | Why |
| --- | --- | --- |
| qt | 6.12.0 | Qt client (first choice). Pulls the whole Qt 6.12 module set (qtbase, qtsvg, qtdeclarative, qtwebengine 6.11.2, ...) |
| gtk+3 | 3.24.52_1 | GTK 3.22 client |
| gtk4 | 4.24.1 | GTK4 client |
| sdl2-compat | 2.32.74 | `sdl2` in Homebrew now resolves to sdl2-compat (SDL2 API on top of SDL3) |
| sdl3 | 3.4.18 | dependency of sdl2-compat |
| sdl2_image | 2.8.12_1 | SDL2 client |
| sdl2_ttf | 2.24.0 | SDL2 client |
| sdl2_mixer | 2.8.2 | SDL audio (all clients) |
| sdl2_gfx | 1.0.4_1 | SDL2 client |
| readline | 8.3.6 | server console (macOS libedit is not sufficient, see upstream INSTALL section 8) |
| curl | 8.23.0 | libcurl for modpack installer / metaserver (system curl would also work) |
| icu4c@78 | 78.3 | already present; keg-only, needs PKG_CONFIG_PATH |
| zstd | 1.5.7_1 | already present |
| sqlite | 3.54.0 | already present |

Dependencies pulled in automatically by the above (not chosen directly): at-spi2-core, dbus,
gdk-pixbuf 2.44.8, glib 2.90.1, graphene, gsettings-desktop-schemas, harfbuzz 14.6.0, hicolor-icon-theme,
libepoxy, librsvg, libxfixes, libxi, libxtst, pango 1.58.2, double-conversion, md4c, hunspell,
libb2, assimp, protobuf, and the SDL2_mixer codec stack (flac, fluid-synth, game-music-emu, lame,
libogg, libvorbis, libxmp, mpg123, opus, opusfile, portaudio, wavpack, libsndfile).

Note on collateral changes: `brew install` rebuilt/relinked a few unrelated formulae because a
shared dependency moved (awscli 2.38.1, node 26.12.0, ollama 0.40.4, openssl@4 4.0.3, curl, libevent,
libwebsockets, mosquitto, s2n, simdjson, simdutf, merve, mlx, aws-c-*). Their Cellar directories
carry today's date. No formula was upgraded by an explicit `brew upgrade`; this was Homebrew's
automatic dependency reconciliation. (observed: `ls -lt /opt/homebrew/Cellar/*/*`, brew log shows
0 "Upgrading" lines.)

## Downloaded (not installed) into ./downloads/ (git-ignored)

| File | Source | SHA-256 |
| --- | --- | --- |
| freeciv-3.1.0-beta1-MacOS.tar.gz (109 MB) | https://files.freeciv.org/packages/macos/ (official, 2023-03-20) | a53ec05aafdbbaddd6238a52ac9e2c6ab987d5ba3192a36d4a5fdea14e7c5db2 |
| freeciv-3.3.90.1-dev_arm64_gtk3.zip (195 MB) | https://github.com/sabinomaggi/freeciv-mac/releases/tag/3.3.90.1-dev-macos | 99c0cfdd70540bbd0fe6dab92579970637acda837ee5ed588c6c46dcf080c8fa |
| freeciv-3.3.90.1-dev_arm64_sdl2.zip (195 MB) | same | bfc679134125941449ff3e943a7986fadbbb0f57e79959c7a7837f438f39bccd |

No official DMG exists for 3.1/3.2; the official macOS artefact is a tar.gz of a Freeciv.app.

## Cloned into ./refs/ (git-ignored, read-only, `--depth 1`)

- freeciv (main, 3.3.90-dev, commit 3f0038d8), freeciv-S3_2 (3.2.6+, commit 44e6898c),
  freeciv-web, freeciv-environments, freeciv-website, all from https://github.com/freeciv/.
- github-cleanhub (John-ODell) cloned to /tmp/cleanhub-ref for the GitHub workflow rules.

## Not touched

/Applications, any installed app, system settings, SIP, Gatekeeper settings.

## Added 2026-10-16 00:00 (test installs outside git and outside TCC-protected folders)

- `~/freeciv-builds/{qt,gtk}` : `ninja install` of port/freeciv build-qt and build-gtk reconfigured with
  `-Dprefix=$HOME/freeciv-builds/<x>` because LaunchServices-launched apps block on TCC when their libraries live under ~/Desktop.
- `~/freeciv-builds/apps/{FreecivGTK4,FreecivQt}.app` : minimal ad-hoc-signed test bundles made by scripts/mk-min-app.sh (no dylib bundling).
- `~/Desktop/freeciv-port/builds/{qt,gtk,sdl2}` : first installs (git-ignored). `~/.freeciv/` : client option files written by the clients on first run (and by the community app's launcher).
- Safe to delete all of the above.

## Added 2026-10-16 morning (Step 5, nothing new from Homebrew)

- `scripts/build.sh qt` reconfigured `port/freeciv/build-qt` to release and reinstalled `~/freeciv-builds/qt` (no new formulae: the check found everything present).
- `~/freeciv-builds/apps/Freeciv.app` (159 MB, self-contained, ad-hoc signed) from `scripts/bundle.sh qt`;
  `~/freeciv-builds/apps/Freeciv-3.2.6-arm64.dmg` (85 MB) + `.sha256` from `scripts/dmg.sh`. Both git-ignored, safe to delete and regenerate.
- `~/.freeciv/freeciv-client-rc-3.2` etc. written by the clients during probes.
- `~/freeciv-builds/gtk` and `~/freeciv-builds/sdl2` reconfigured to release by `scripts/build.sh gtk|sdl2` (no new formulae);
  `~/freeciv-builds/apps/{Freeciv-GTK4,Freeciv-GTK3,Freeciv-SDL2}.app` from `scripts/bundle.sh`; the stale
  `FreecivGTK4.app`/`FreecivQt.app` test wrappers from last night were deleted. `~/Desktop/freeciv-port/builds/` (last
  night's debug installs) is now unused and can be deleted.

## 2026-10-17, test tileset (issue 74)

- `~/.freeciv/3.2/freeciv45test.tilespec` and `~/.freeciv/3.2/freeciv45test`: symlinks into this repo's
  `tilesets/` (first made to the `tileset-t0` worktree, re-pointed to the main checkout after the merge), so any
  client on this machine can load the test tileset by name. Delete the two links to uninstall; nothing else.
  Observed 2026-10-17 evening: the re-point had not happened and the links still went to the worktree's stale
  copy; re-pointed to `~/Desktop/freeciv-port/tilesets/` then (issue 149).
- `scripts/windows-of-pid` compiled again in the worktree (git-ignored).

## Added and removed 2026-10-17 midday (local terrain-texture generation trial; all deleted the same day)

- `~/freeciv-builds/art-venv/` (1.0 GB): Python 3.14 venv (`/opt/homebrew/bin/python3.14 -m venv`; the default python3 is
  3.15, for which PyTorch has no wheel) with pip packages torch 2.14.1, torchvision, diffusers 0.41.0, transformers,
  accelerate, safetensors, pillow. Used only by `~/freeciv-builds/art/tile_render.py`.
- `~/freeciv-builds/hf-cache/` (6.7 GB): Hugging Face cache (`HF_HOME`) holding the fp16 safetensors of
  `stabilityai/stable-diffusion-xl-base-1.0` at commit 462165984030d82259a11f4367a4eed129e94a7b, licence
  CreativeML Open RAIL++-M (outputs belong to the person who makes them; the weights themselves are not redistributed
  and are not part of any repo). No HF account or token was used.
- `~/freeciv-builds/art/` : the render scripts and their output tiles.
- **Removed 2026-10-17 afternoon.** The trial produced seamless but flat, wallpaper-like textures (SDXL base, 1024 px,
  circular padding), far from the painted-realism target, so John dropped it. `~/freeciv-builds/art-venv`,
  `~/freeciv-builds/hf-cache` and `~/freeciv-builds/art` were deleted (7.7 GB freed). Nothing remains installed from it;
  terrain art continues through the ChatGPT requests in ~/Desktop/asset_generator/freeciv45/.
