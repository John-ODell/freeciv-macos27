# Upstream survey: Freeciv on macOS (Apple Silicon, macOS 26/27)

Compiled 2026-10-15 from web (redmine, GitHub, Homebrew, MacPorts, forum) and the local read-only clones under
`/Users/johnodell/Desktop/freeciv-port/refs/` (`freeciv` = main 3.3.90-dev @ 3f0038d, `freeciv-S3_2` @ 44e6898,
`freeciv-environments`, `freeciv-web`, `freeciv-website`). Every claim carries a URL or a `file:line` citation.
Anything I could not open myself is marked **unverified**.

Sources that could NOT be reached (so their content is unverified below):
- `freeciv.fandom.com` (the "freeciv.org/wiki" host): `https://www.freeciv.org/wiki/Install-Mac` 302-redirects to
  `https://freeciv.fandom.com/wiki/Install-Mac`; fandom answers every scripted fetch (WebFetch, curl with a Chrome UA,
  `?action=raw`, `api.php?action=parse`) with a Cloudflare "Just a moment..." challenge (HTTP 403) or HTTP 402. The
  MediaWiki API additionally reports `missingtitle` for `Install-Mac`. Wayback has **no** snapshot of Install-Mac; it has
  snapshots of `How_to_Contribute` (2025-08-27), `NEWS-3.2.6`, `NEWS-3.2.2`, `NEWS-3.2.0`, `NEWS-3.1.4`, `NEWS-3.1.2`,
  `NEWS-3.1.1`, but web.archive.org rate-limited every retrieval (HTTP 429) and WebFetch refuses web.archive.org.
- `osdn.net` (the pre-2024 tracker, tickets `osdn#44549`, `#47589`, `#47604`, `#47767`): DNS no longer resolves
  (`getaddrinfo ENOTFOUND osdn.net`). Only web-search snippets of those tickets were available.
- Redmine has **no wiki module enabled** for the freeciv project: `/projects/freeciv/wiki`, `/wiki/index` and
  `/wiki.json` all return 404; the project JSON (`https://redmine.freeciv.org/projects/freeciv.json`) lists no modules,
  and the project page shows only the Activity / Issues / Roadmap / Search tabs. So there is no "Freeciv for macOS"
  redmine wiki page to cite.

---

## 1. Redmine tickets (https://redmine.freeciv.org/projects/freeciv)

Method: global search `/search?q=<term>&issues=1` for macos, "mac os x", darwin, apple, homebrew, macports, arm64,
"apple silicon", retina, hidpi, xcode; subject filters `issues.json?subject=~<term>` for mac/osx/brew/menu/hidpi/
retina/qt6/sdl3/scaling/dpi; and a full scan of all 2371 tickets' subject+description for mac-related words back to
2023-10-01. Terms with **zero** hits anywhere: darwin, apple, apple silicon, arm64, macports, retina, hidpi, dpi,
scaling, osx. There is no open ticket about HiDPI/Retina, Apple Silicon, or app-bundle packaging.

### 1a. Client behaviour on Mac (the substantive ones)

| # | Title | Tracker/Status | Fixed in | Gist | URL |
|---|---|---|---|---|---|
| 1292 | gtk clients on Mac - use meta key instead of ctrl key for menu accelerator keys | Feature, Closed | 3.1.6 | Dean Brown: Mac standard is Command for menu accelerators; Qt already did it. Added `ACCL_MOD_KEY "<Meta>"` under `#ifdef __APPLE__` for gtk3.22/gtk4/gtk5. Commit 140fbc88eb (2025-05-24). | https://redmine.freeciv.org/issues/1292 |
| 1489 | handle_edit_key_press() not directing Mac Meta -combinations to main key handler | Bug, Closed | 3.1.6 | Regression from #1292 (since 3.1.5/3.2.0-beta2); editor key handler must early-exit when Meta held. Macro moved to `gui_main.h`. Commit 4d5eb2bfd4. Maintainer asked for one patch per branch and standard commit messages (<70-char subject). | https://redmine.freeciv.org/issues/1489 |
| 1483 | gtk3.22 client - shortcut key for View menu item Show Stack Size doesn't work | Bug, Closed | 3.2.2 | "Ctrl/Meta +" shortcut broken on Mac only (US keyboard layout: '+' needs Shift). Marko could not reproduce (Finnish layout). Commit 8ef1ef5284 "Fix Show Stack Size shortcut in MacOS". | https://redmine.freeciv.org/issues/1483 |
| 1672 | Qt client - Help menu items disappear | Bug, Closed | 3.1.6 | On Mac, Qt auto-moves any action whose text starts with "About..." to the app menu, so Help items vanish after the help dialog is used once. Fix: `QAction::setMenuRole(QAction::NoRole)` under `#ifdef __APPLE__`. Commit 8bc2aebf6d "Fix disappearing About... menu items in MacOS" (2025-10-25). | https://redmine.freeciv.org/issues/1672 |
| 1630 | Qt: Add menu items to change sound volume | Feature, Closed | 3.2.2 | Spawned by Mac '+' key problems; Dean Brown notes "The sdl client is a problem on my Mac, I get no menus". | https://redmine.freeciv.org/issues/1630 |
| 1684 | gtk clients have a problem with GDK_KEY_plus key and sound volume | Bug, Closed | 3.3.0 | Same keyboard-layout issue family (Dean Brown, Mac). | https://redmine.freeciv.org/issues/1684 |
| 943 | gtk: Menu entries for zoom | Feature, Closed | 3.3.0 | Dean Brown found gtk3.22/gtk4 refuse bare '+'/'-' accelerators; waited on #1292 to avoid conflicts. | https://redmine.freeciv.org/issues/943 |
| 1708 | "Segmentation fault: 11" when viewing nations screen, OS X | Bug, Closed | 3.2.2 | Reporter on macOS 15.1.1, Homebrew 3.2.1 gtk3.22. Root cause not Mac-specific (`government_name_translation()` assert on dead nations). | https://redmine.freeciv.org/issues/1708 |
| 1658 | [Qt] Unable to choose nation for a new game | Bug, Closed | - | Duplicate of #1652; Dean Brown verified the fix on Mac. | https://redmine.freeciv.org/issues/1658 |
| 2339 | savecompat.c gnu-folding-constant warning on mac | Bug, In Review | 3.2.7 | Apple clang `-Wgnu-folding-constant` warnings found by running mac-meson CI with werror. | https://redmine.freeciv.org/issues/2339 |
| 2355 | stdinhand.c gnu-folding-constant warning on mac | Bug, New | - | same family (2026-10-10) | https://redmine.freeciv.org/issues/2355 |
| 2360 | unittools.c gnu-folding-constant warning on mac | Bug, New | - | same family (2026-10-11) | https://redmine.freeciv.org/issues/2360 |
| 1293 | Help -> Controls is wrong for qt client | Bug, New | - | Follow-on from #1292: help text says "Ctrl" everywhere, wrong on Mac. | https://redmine.freeciv.org/issues/1293 |

### 1b. Packaging / app bundle

| # | Title | Status | Fixed in | Gist | URL |
|---|---|---|---|---|---|
| 1731 | Drop homebrew-appbundle.sh | Feature, Closed | 3.3.0 | Full description: "homebrew-appbundle.sh was deemed dead end. Drop it." Commit 7f65299d40 (2025-11-10) removed `platforms/macos/homebrew-appbundle.sh` (118 lines) from main. **It still exists on S3_2.** | https://redmine.freeciv.org/issues/1731 |
| 1761 | ci-build.sh: Drop followtag from mac-meson | Feature, Closed | 3.3.0 | "mac-meson job configures 'macos' followtag to follow. There's no such tag." Commit a73f32d56f. | https://redmine.freeciv.org/issues/1761 |
| 2177 | Strings.txt listing nonexistent macos vertags | Bug, Closed | 3.3.0 | Dropped `?vertag:macos` translations on main (commit 6c9fe88bd4, 2026-08-29). S3_2 still has them: `refs/freeciv-S3_2/translations/Strings.txt:17,23`. | https://redmine.freeciv.org/issues/2177 |

### 1c. CI plumbing for the mac-meson job (all by Marko Lindqvist, all Closed unless noted)

| # | Title | Fixed in | Gist | URL |
|---|---|---|---|---|
| 216 | CI: Macos-14 | 3.1.2 | runner bump | https://redmine.freeciv.org/issues/216 |
| 352 | CI: Homebrew install/update fails on github actions | 3.1.1 | brew python symlink clash; workaround `rm /usr/local/bin/python3*` still in ci.yml | https://redmine.freeciv.org/issues/352 |
| 562 | CI: Don't install SDL2_gfx for mac-meson | 3.1.2 | use bundled SDL2_gfx | https://redmine.freeciv.org/issues/562 |
| 576 | CI: Drop autotools mac build | 3.3.0 | only meson is tested on mac now | https://redmine.freeciv.org/issues/576 |
| 895 | CI: mac-meson job warning about already installed pkg-config | 3.2.0 | | https://redmine.freeciv.org/issues/895 |
| 936 / 938 / 957 | CI: macos-15 ; S3_1 mac job to macos-14 ; S3_1 os_x runner to macos-15 | 3.1.4 | runner bumps | https://redmine.freeciv.org/issues/936 |
| 974 | CI: mac-meson failing because of missing icu | 3.1.4 | Homebrew icu4c became keg-only/versioned; needs `PKG_CONFIG_PATH` | https://redmine.freeciv.org/issues/974 |
| 975 | generate_packets.py failure on mac-meson CI job | 3.2.0 | Python 3.13 enum change broke generator (reported to CPython as python/cpython#125710) | https://redmine.freeciv.org/issues/975 |
| 977 | Work around mac-meson failure | Rejected | pin python 3.12 (not needed) | https://redmine.freeciv.org/issues/977 |
| 1156 | S3_1 CI: Mac jobs fail to install Qt | 3.1.4 | caused by installing pkg-config | https://redmine.freeciv.org/issues/1156 |
| 1158 | CI: mac-meson: icu4c already installed | 3.2.0-beta1 | | https://redmine.freeciv.org/issues/1158 |
| 1687 | S3_3 CI: mac-meson job tries to build removed gtk4x-client | 3.3.0 | | https://redmine.freeciv.org/issues/1687 |
| 1725 | CI: macos-26 runners | 3.2.2 | commit 6e539a0ec0 | https://redmine.freeciv.org/issues/1725 |
| 1760 | CI: mac-meson trying to use syslua, but lua-5.5 not found | 3.3.0 | | https://redmine.freeciv.org/issues/1760 |
| 2197 | CI: xcode-27 | 3.2.7 | commit d7b41044ea (2026-09-01): runner is now `xcode-27` | https://redmine.freeciv.org/issues/2197 |
| 2249 | CI: Build sdl3-client instead of sdl2-client on mac-meson job | 3.2.7 | commit 8f37c0bb69 | https://redmine.freeciv.org/issues/2249 |
| 2250 | CI: Install lua@5.5 for mac-meson job | 3.3.0-beta1 | | https://redmine.freeciv.org/issues/2250 |
| 2338 | CI: mac-meson job has sdl2 libraries include/lib paths in the commandline | 3.2.7 | log shows Homebrew now provides `/opt/homebrew/opt/sdl2-compat/`; commit 8d1ae8a482 (2026-10-06) | https://redmine.freeciv.org/issues/2338 |

Tickets referencing GitHub PRs: #2167 (PR #86, "Merged outside github UI", https://redmine.freeciv.org/issues/2167),
#2222 split from #2186 / PR #90 (https://redmine.freeciv.org/issues/2222).

### 1d. Redmine wiki / fandom wiki
- Redmine: no wiki module (see header). Nothing to cite.
- Fandom `Install-Mac`, `How_to_Contribute`, `NEWS-3.x.y`: **blocked / unverified** (see header). `doc/HACKING` still
  points at `https://www.freeciv.org/wiki/How_to_Contribute` (`refs/freeciv-S3_2/doc/HACKING:1168-1169`).

---

## 2. GitHub freeciv/freeciv

### 2a. Pull requests (issues are disabled; PRs are open but not the official channel)
`gh pr list --search macos|mac|darwin|apple|homebrew|xcode|osx --state all`: **no PR in the last 3 years mentions macOS.**
Only hits: #72 "meson: use `feature` option type" (OPEN, 2025-04-23, matched "mac" by substring) and #29 "Only include
sys/random.h for getentropy()" (CLOSED 2021). The repo has 95 PRs total; recent ones are translations or get re-filed as
redmine tickets, e.g. PR #86 -> RM #2167 ("Merged outside github UI. Also backported to stable branches",
https://github.com/freeciv/freeciv/pull/86) and PR #90 -> RM #2186/#2221/#2222 (https://github.com/freeciv/freeciv/pull/90).

### 2b. Commits touching `platforms/macos` (`gh api repos/freeciv/freeciv/commits?path=platforms/macos`)
| sha | date | subject |
|---|---|---|
| 5a4b947ada | 2022-12-04 | macos: Add homebrew-appbundle.sh build script (osdn#44549) https://github.com/freeciv/freeciv/commit/5a4b947ada15f3dd4b728258328ec43b205f3799 |
| 4bae424113 | 2023-02-28 | homebrew-appbundle.sh: Set version number dynamically (author "Dino") https://github.com/freeciv/freeciv/commit/4bae424113522ef9c04db519013539492e1b020f |
| 0f69a3b4c7 | 2023-04-10 | Set followtag for macos builds (osdn#47604) https://github.com/freeciv/freeciv/commit/0f69a3b4c73b43ed650514f25928f21e1209e79c |
| c4372c0e6d | 2023-04-22 | homebrew-appbundle.sh: Make libfreeciv static https://github.com/freeciv/freeciv/commit/c4372c0e6d922abc4114da451b9d003ecf81fa6a |
| 7e69fb3130 | 2023-09-24 | homebrew-appbundle.sh: Fix build https://github.com/freeciv/freeciv/commit/7e69fb3130e1799b072b5852d9d198653c30ceaf |
| 22c3d069a3 / 87ff1334f1 | 2023-09 | Meson: manual generator / ruleup optional (touch script args) |
| aaa3492427 | 2023-12-25 | Replace #!/bin/bash with posix shebang |
| 3fc3aeb690 | 2025-01-11 | Prepare main branch for 3.4 development |
| **7f65299d40** | **2025-11-10** | **Drop homebrew-appbundle.sh** ("See RM #1731"; removes 118 lines, also edits `fc_version`, `platforms/Makefile.am`) https://github.com/freeciv/freeciv/commit/7f65299d40b36b987e267765ed0071dfe8ac8dad |

On branch S3_2 the file is still present (`gh api ...commits?sha=S3_2&path=platforms/macos`: last touched 9f61d753b5
2025-07-04 "Set default followtag to 'stable'").

### 2c. Commits with "macOS"/"Mac" in the message since 2023 (`gh search commits`)
- 2026-10-06 8d1ae8a482 CI: Remove SDL2 include/lib path references from mac-meson job (RM #2338)
- 2026-09-16 8f37c0bb69 CI: Build sdl3-client at mac-meson job
- 2026-09-13 78db8b97fc CI: Install lua@5.5 for mac-meson job
- 2026-09-01 d7b41044ea CI: Update mac runner to xcode-27 (RM #2197)
- 2026-08-29 6c9fe88bd4 Strings.txt: Drop macos follow tag translations (RM #2177)
- 2025-12-19 a73f32d56f CI: Drop followtag setting from mac-meson job (RM #1761)
- 2025-11-23 1911be2ad4 ci-build.sh: Do not force syslua on mac-meson job (RM #1760)
- 2025-11-10 7f65299d40 Drop homebrew-appbundle.sh (RM #1731)
- 2025-11-09 8ef1ef5284 gtk3.22: Fix Show Stack Size shortcut in MacOS (RM #1483)
- 2025-11-03 6e539a0ec0 CI: Update mac runner to macos-26 (RM #1725)
- 2025-10-25 8bc2aebf6d Qt: Fix disappearing "About..." menu items in MacOS (RM #1672)
- 2025-06-07 4d5eb2bfd4 gtk: Fix handle_edit_key_press() to handle Mac modifier (RM #1489)
- 2025-05-24 140fbc88eb Mac: Use meta/command key as menu accelerator (RM #1292)
- 2024-11-25 70896b185f / 2024-10-17 c418a1ff20 CI: icu4c install dance for mac-meson
- 2024-10-07 f0c0822686 CI: Use macos-15 runner; 2024-05-09 30bc97f5c0 CI: Drop autotools mac build; 2024-05-07 ff77f12092 CI: Don't install external SDL2_gfx; 2024-05-04 df0b6dcf62 macos-14 runner; 2024-03-24 510698c658 CI: Workaround github mac build failure (RM #352)
- 2023-10-01 25041cbf0d CI: Do not build sdl3-client on mac-meson job; 2023-09-24 cd06f2af5d CI: Fix mac-meson build; 2023-07-13 c84dc400d3 CI: Update mac-meson job's client list; 2023-04-27 c7303d66d1 macos-13 runner; 2023-04-08 2fe7e4589f CI: Set custom followtag to mac builds (osdn#47767); 2023-03-18 4330e9903c Drop obsolete GENERATING_MAC code
- Searches for "Darwin", "Apple", "Apple Silicon", "arm64" in commit messages since 2023: **no hits**.

### 2d. What is in the tree today (main vs S3_2)
- CI job: `refs/freeciv/.github/workflows/ci.yml:53-77` — `mac-meson: runs-on: xcode-27`; removes stale python
  symlinks; `brew install meson lua@5.5 jpeg gtk+3 gtk4 sdl3_mixer sdl3_image sdl3_ttf qt@6`; runs
  `./scripts/ci-build.sh mac-meson`. S3_2 is identical except `lua@5.4` (`refs/freeciv-S3_2/.github/workflows/ci.yml:51-75`).
- Build script: `refs/freeciv/scripts/ci-build.sh:105-139` — sets `CPPFLAGS`/`LDFLAGS`/`PKG_CONFIG_PATH` from
  `brew --prefix gettext|readline|icu4c`, then `meson setup -Dqtver=qt6x -Ddebug=true -Daudio=sdl3
  -Dtools=ruledit,manual,ruleup -Dclients=gtk3.22,sdl3,gtk4,qt,stub,gtk4x -Dfcmp=gtk3,gtk4,qt,cli -Dprefix=$HOME/freeciv/mac-meson`,
  `ninja`, `ninja install`, then runs a server autogame. S3_2 variant (`refs/freeciv-S3_2/scripts/ci-build.sh:76-110`) still
  passes `-Dsyslua=true -Dfollowtag=macos` and no `gtk4x`. **CI never builds an .app, never runs a client, never codesigns.**
- Mac-specific code: `refs/freeciv-S3_2/client/gui-gtk-3.22/gui_main.h:23-30` and `client/gui-gtk-4.0/gui_main.h:24-30`
  (`#ifdef __APPLE__` -> `ACCL_MOD_KEY "<Meta>"`, `ACCL_MOD_MASK GDK_META_MASK`); `client/gui-qt/menu.cpp:972-981`
  (zero-width space prepended to the "Options" submenu title so Qt does not relocate it on Mac) and
  `menu.cpp:1726-1821` (`setMenuRole(QAction::NoRole)` on Help items). `meson.build` has no darwin branch at all
  (`refs/freeciv/meson.build:83` reads `host_machine.system()` but there is no `'darwin'` case; grep for rpath/install_name: none).
- Docs: `refs/freeciv-S3_2/INSTALL:568-590` "8. Mac OS X and Darwin notes" (icu4c pkg-config path; libedit is not a
  readline substitute, use Homebrew readline with CPPFLAGS/LDFLAGS). Main moved this to `refs/freeciv/doc/INSTALL.autotools:569`;
  main's meson `INSTALL` has no Mac section. `doc/README.packaging` has no Mac section.
- The dropped script (`refs/freeciv-S3_2/platforms/macos/homebrew-appbundle.sh`): hard-codes
  `CONTENTSDIR="/Applications/Freeciv.app/Contents/"` (line 22), writes an `Info.plist` with `plist version="0.9"`
  (line 48), an `LSEnvironment LD_LIBRARY_PATH` key (line 52, meaningless on macOS), `CFBundleExecutable
  ../bin/freeciv-gtk4` (lines 63-64, i.e. the binary lives outside `Contents/MacOS`), `CFBundleIdentifier freeciv`
  (no reverse-DNS), then `meson setup -Dsyslua=true -Dclients=gtk4,qt -Dfcmp=qt -Dfollowtag=macos
  -Ddefault_library=static -Dprefix=$CONTENTSDIR` (lines 104-112). It does **no** dylib bundling, no
  `install_name_tool`, no codesign. NEWS entry: `refs/freeciv-S3_2/NEWS:1210` "Support scripts added for building
  appbundle for macOS, using homebrew osdn#44549". `refs/freeciv-S3_2/fc_version:55` documents the `macos` followtag.

### 2e. Official binary
`https://files.freeciv.org/packages/macos/` contains exactly one file: `freeciv-3.1.0-beta1-MacOS.tar.gz`, 109 MB,
Last-Modified 2023-03-20 (HTTP HEAD: Content-Length 114547438). The website source
(`refs/freeciv-website/download.html:170-180`, last changed 2026-10-15) still says "MacOS binaries for MacOS 11.x or
later are available at: freeciv-3.1.0-beta1-MacOS.tar.gz" with a banner "MacOS packages for the latest beta are not
available yet." Web-search snippets of the dead osdn tracker say ticket #47589 (opened by cazfi 2023-03-18) was
answered by **ddeanbrown** two days later with the built package, and that #44549 "New process to build MacOS version"
was reported by ddeanbrown and modelled on the Longturn/freeciv21 bundle process
(https://osdn.net/projects/freeciv/ticket/47589, https://de.osdn.net/projects/freeciv/lists/archive/tickets/2022-December/009063.html
— **unverified**, host unreachable).

---

## 3. Homebrew

Formula: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/f/freeciv.rb (fetched raw 2026-10-15).
- Version 3.2.6 from the SourceForge tarball; `head` builds `main`. Two backport patches: upstream commits
  b427d038fab6 and 4718723428fc "Backport support for Lua 5.5" (annotated `type :backport`).
- Deps: build `meson ninja pkgconf`; runtime `adwaita-icon-theme (:no_linkage) cairo gdk-pixbuf glib gtk4 icu4c@78 lua
  pango readline sdl2-compat sdl2_mixer xz zstd`; `uses_from_macos bzip2 curl sqlite`; `on_macos depends_on "gettext"`.
  **No gtk+3, no qt, no sdl2_image/ttf** -> only the **gtk4 client** and the gtk4 modpack installer are built (meson
  default `clients=['gtk4']`, `fcmp=['gtk4']`, `audio='sdl2'`: `refs/freeciv-S3_2/meson_options.txt:1-11,48-52`).
- Install: `ENV.append "LDFLAGS", "-Wl,-rpath,#{rpath}"` on mac; deletes bundled `dependencies/lua-*`; meson args
  `-Dreadline=true -Dsyslua=true -Dtools=manual,ruleup` ("ruledit removed from tools as needs Qt").
- Bottles: `arm64_golden_gate`, `arm64_tahoe`, `arm64_sequoia`, `arm64_sonoma`, `arm64_linux`, `x86_64_linux`.
  `golden_gate` = macOS 27 and `tahoe` = 26 per
  https://github.com/Homebrew/brew/blob/HEAD/Library/Homebrew/macos_version.rb (lines 22-25). No Intel-mac bottles.
  formulae.brew.sh API: 41 installs in the last 30 days (https://formulae.brew.sh/api/formula/freeciv.json).
- Formula history (`gh api repos/Homebrew/homebrew-core/commits?path=Formula/f/freeciv.rb`): every upstream release
  landed within days (3.1.4 2025-01-03 ... 3.2.6 2026-09-03, bottle rebuilt 2026-09-12); `2026-06-01 freeciv: migrate
  to sdl2-compat` (432743aaf4, part of PR #285604); `2026-02-06 freeciv: update dependencies` (PR #266239);
  `2025-11-06 revision bump (icu4c@78 78.1)` (PR #253370); `2026-07-23 remove ENV.cxx11`; `2026-08-02 annotate patches`.
  PR list: https://github.com/Homebrew/homebrew-core/pulls?q=freeciv — all routine version bumps, all MERGED.
- homebrew-core issues mentioning freeciv in the last 2 years: **none** (last ones were #75993/#77343 "graphics bug"
  in 2021, https://github.com/Homebrew/homebrew-core/issues/77343).
- **sdl2 -> sdl2-compat:** `sdl2-compat` formula added 2026-05-09 (198f180df0, "sdl2-compat 2.32.68 (new formula)");
  `sdl2: replace with sdl2-compat` committed 2026-05-31 (ad4806814e) via PR #285604 (merged 2026-06-19,
  https://github.com/Homebrew/homebrew-core/pull/285604); `Formula/s/sdl2.rb` is now gone (raw URL 404). The
  sdl2-compat formula (https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/s/sdl2-compat.rb) is "SDL2
  compatibility layer that uses SDL3 behind the scenes", `depends_on "sdl3" => :no_linkage`, installs `sdl2.pc` as a
  symlink to `sdl2-compat.pc`; bottles for golden_gate/tahoe/sequoia (no sonoma). Upstream noticed this in RM #2338
  (`-L/opt/homebrew/opt/sdl2-compat/lib` in CI logs). `sdl2_mixer` is still real SDL2_mixer 2.8.2.
- Current Homebrew toolkit versions (formulae.brew.sh API): gtk4 4.24.1 (bottles golden_gate/tahoe/sequoia only),
  gtk+3 3.24.52, qt 6.12.0, sdl3 3.4.18.
- Field reports on the Homebrew gtk4 client: forum thread "freeciv-gtk4 on MacOS 26"
  (https://forum.freeciv.org/f/viewtopic.php?p=111294, t=95527, June-July 2026): after Homebrew switched from
  gtk3.22 to gtk4 the window loses mouse input "between every 2 or 3 mouse clicks" until minimised/re-opened; a second
  user (MacPorts, macOS 11.7) reports the menubar not responding on first launch until app-switching, plus many
  warnings, "gtk4 on the Mac is a problem"; no developer reply.

---

## 4. MacPorts

Portfile https://github.com/macports/macports-ports/blob/master/games/freeciv/Portfile (raw fetched):
- **version 2.6.4**, `maintainers nomaintainer`, autotools build, `--enable-fcdb=sqlite3 --with-readline
  --disable-sdl2framework`, client **sdl2** (`--enable-client=sdl2`, `app.executable freeciv-sdl2`, wrapped as an .app by
  `PortGroup app 1.0`) on `os.major > 10`, else SDL1; subport `freeciv-x11` builds the **gtk2** client; one patch
  `utility_randseed.c.patch`; variant `universal` only (ports.macports.org API: variants `["universal"]`).
- Last Portfile commits: 2021-10-16 (gtk2 path-style deps), 2021-05-30 "build fix for older systems", 2021-04-19
  "Update to 2.6.4" (`gh api repos/macports/macports-ports/commits?path=games/freeciv/Portfile`).
- Buildbot: builds succeed on `27_arm64` (2026-09-19), `26_x86_64` (2026-09-27), `26_arm64` (2025-09-22), `15_arm64`
  (https://ports.macports.org/api/v1/builds/?port_name=freeciv). Port page shows livecheck error ("regex didn't match"),
  7 installs/30 days (https://ports.macports.org/port/freeciv/). So MacPorts is five years and two major versions behind,
  but proves the old autotools tree compiles natively on arm64 macOS 27.
- MacPorts Trac search is behind an Anubis bot-check (`https://trac.macports.org/query?summary=~freeciv` returned the
  challenge page) — **ticket list unverified**.

---

## 5. Community packager: sabinomaggi/freeciv-mac

Repo: https://github.com/sabinomaggi/freeciv-mac (fork of freeciv/freeciv, 1 star, last push 2025-04-26, default branch
`main`). Branches: upstream mirrors (S2_x, S3_0, main, ...) plus `macos`.
- `main` is **0 commits ahead** of upstream (compare API: `ahead_by 0, behind_by 972, files []`).
- `macos` branch vs upstream main (`gh api repos/freeciv/freeciv/compare/main...sabinomaggi:freeciv-mac:macos`):
  15 commits ahead, merge base 2e41bf852e (2025-04-16); the only non-merge diffs are `.gitignore` (+19), `README.md`
  (+114), `README-original.md`, `autogen.sh` (+1/-1: `FC_RUN_CONFIGURE=no`) and an accidentally committed `config.log`
  (+661). `platforms/macos/` is untouched upstream (`homebrew-appbundle.sh`, 3260 bytes). **There are no bundle
  scripts, no Info.plist generation, no dylib relocation / install_name_tool scripts in the repo.**
- README (macos branch, https://github.com/sabinomaggi/freeciv-mac/blob/macos/README.md): recipe is autotools, not meson:
  `brew install autoconf automake icu4c sdl2 sdl2_image sdl2_ttf sdl2_gfx gtk+3 llvm libomp`; `PKG_CONFIG_PATH=
  /opt/homebrew/opt/icu4c@77/lib/pkgconfig` and `LDFLAGS/CPPFLAGS` for icu4c@77 "for an Apple Silicon Mac"; uses
  Homebrew llvm clang; `../configure --prefix=$HOME/Applications/freeciv-mac/freeciv-app --enable-client=auto
  --enable-freeciv-manual --enable-mapimg=auto --enable-debug=no --enable-static=no --enable-ack-legacy`; then
  "How to bundle Freeciv for macOS: 1. Copy the data directory ... TODO ..." (the bundling section is unfinished).
- Releases: `3.3.90.1-dev-macos` (2025-04-26, "Freeciv 3.3.90.1-dev for macOS packaged for arm64 (aka Apple Silicon)
  processors. GUI toolkits: GTK3 or SDL2."): `freeciv-3.3.90.1-dev_arm64_gtk3.zip` (195 MB, 39 downloads) and
  `..._sdl2.zip` (195 MB, 28 downloads); `v0.1.1-alpha-macos` (2018-04-18, "Fully tested only under macOS 10.11",
  `Freeciv.dmg` 387 MB). https://github.com/sabinomaggi/freeciv-mac/releases
- Upstreamable content: **none** — the README's Homebrew hints duplicate `INSTALL` section 8; the binaries were produced
  by hand from a stale dev snapshot. The one useful signal is that both the gtk3 and sdl2 clients were runnable on
  arm64 in April 2025. (I did not download the zips, so their internal layout is **unverified**.)

---

## 6. Freeciv21 (longturn/freeciv21) as a packaging reference

- Build: CMake + vcpkg manifest (`vcpkg.json`: qtbase, qtmultimedia, qtsvg, qttools, kf6archive, lua 5.4.8, openssl,
  sdl2-mixer, sqlite3, gettext) https://github.com/longturn/freeciv21/blob/master/vcpkg.json
- CI job `os_x_dyn` "macOS (x64-osx-custom)" in https://github.com/longturn/freeciv21/blob/master/.github/workflows/build.yaml
  (lines ~279-365): `runs-on: macos-15-intel`; `brew remove --force $(brew list)` then `brew install --overwrite autoconf
  autoconf-archive automake cmake create-dmg libtool nasm ninja pkgconf`; pinned python 3.11 (workaround for issue #2069);
  `lukka/run-vcpkg@v11` with a pinned vcpkg commit; `cmake --preset fullrelease-macos-dynamic`; build/test/install;
  `create-dmg --volname "Freeciv21 Game Installer" --volicon client.icns --app-drop-link ... Freeciv21-<tag>-x64-osx.dmg`
  + sha256; uploaded with `softprops/action-gh-release` on tags. A second job `os_x_static` (scheduled only) uses
  `fullrelease-macos-static`.
- Presets: `CMakePresets.json` `fullrelease-macos-dynamic` sets `FREECIV_USE_VCPKG=ON`, `FREECIV_MACOS_DYNAMIC=true`,
  `VCPKG_OVERLAY_TRIPLETS=cmake/`, `VCPKG_TARGET_TRIPLET=x64-osx-custom`
  https://github.com/longturn/freeciv21/blob/master/CMakePresets.json ; the triplet `cmake/x64-osx-custom.cmake`
  (`VCPKG_LIBRARY_LINKAGE dynamic`, `VCPKG_OSX_ARCHITECTURES x86_64`, gettext forced static).
- Bundle assembly: `cmake/FreecivInstall.cmake` `if(APPLE)` block (lines ~296-388): `configure_file(dist/Info.plist.in)`;
  `install(CODE ...)` creates `Freeciv21.app/Contents/{MacOS,Resources,Resources/doc,Resources/locale}`, copies
  `bin/freeciv21-*` into `Contents/MacOS`, `share/freeciv21` into `Resources`, builds `client.icns` with `iconutil
  --convert icns`; when `FREECIV_MACOS_DYNAMIC`, copies Qt `plugins/tls` and runs `macdeployqt6 Freeciv21.app
  -executable=<each exe>` to pull dylibs and fix install names.
  https://github.com/longturn/freeciv21/blob/master/cmake/FreecivInstall.cmake
- `dist/Info.plist.in` (https://github.com/longturn/freeciv21/blob/master/dist/Info.plist.in): PLIST 1.0,
  `CFBundleIdentifier net.longturn.freeciv21`, `CFBundleExecutable freeciv21-client`, `CFBundleIconFile client.icns`,
  `ATSApplicationFontsPath fonts`, **`NSHighResolutionCapable true`**, `CFBundleURLTypes` for `fc21://`.
- Signing/notarization: **none in CI** (grep of build.yaml/release.yaml for codesign/notar: no hits). Issue #2777
  "Support macOS ARM (arm64-osx)" (OPEN, 2025-08-20) states "Apple is now requiring a code sign with an Apple Developer
  ID to run binaries compiled on arm. Our CI produces a self-signed binary that won't run on another computer" and
  proposes ad-hoc `codesign --force --sign -` after bundling (https://github.com/longturn/freeciv21/issues/2777).
  Their install docs tell users to override Gatekeeper's "damaged and can't be opened" dialog
  (https://github.com/longturn/freeciv21/blob/master/docs/Getting/install.rst lines ~251-272).
- Architecture: releases ship **x64 only** (`Freeciv21-v3.2-dev.4-x64-osx.dmg`, 2026-09-12; v3.1.3 has no mac asset at
  all) https://github.com/longturn/freeciv21/releases . Issue #2647 "x86 macOS binaries" and #2777 discuss arm64: vcpkg
  cannot build universal binaries, Qt6 needs macOS 14 SDK, GitHub arm runners free / Intel runners paid
  (https://github.com/longturn/freeciv21/issues/2647). Relevant PRs: #2753 "Feature: Qt6 macos" (2025-08-09), #2763
  "update macos build and docs" (2025-08-20, "we can go all in on ARM support and allow Intel users to use Rosetta2" —
  later reversed), #2783 "macOS: Create App Bundle at Install" (2025-08-23), #2835 "Update macOS build to 15 with intel
  support" (2025-10-02), #2892 "macOS Qt6 linked Dynamically" (merged 2026-06-27, closes #2766 "installed size 500 MB
  because every exe statically links Qt") https://github.com/longturn/freeciv21/pull/2892 . Issue #2780 "CMake does all
  the macOS app bundle and dmg natively" closed won't-do: CPack DragNDrop "doesn't lend itself to our needs".
- Docs: `docs/Contributing/dev-env-macos.rst` ("Freeciv21 compiles and runs on Apple macOS Sonoma (v14) or higher";
  Homebrew + vcpkg; "at least 3 hours" first build) https://github.com/longturn/freeciv21/blob/master/docs/Contributing/dev-env-macos.rst ;
  `docs/Coding/packaging.rst` "macOS Package" section (bundle built by CMake at `--target install`, dmg by create-dmg)
  https://github.com/longturn/freeciv21/blob/master/docs/Coding/packaging.rst ; `docs/Contributing/workarounds.rst`
  ("The macOS CI installs a fixed Python version to work around a bug in Meson").

---

## 7. NEWS for 3.1.x / 3.2.x

- `refs/freeciv-S3_2/NEWS` (covers "MAJOR CHANGES FROM 3.1.x to 3.2.0" at line 10 and "3.0.x to 3.1.0" at line 528):
  the **only** macOS entry is line 1210 (in the 3.1.0 section): "Support scripts added for building appbundle for macOS,
  using homebrew osdn#44549". Same text at `refs/freeciv/NEWS:1222`. `grep -i "mac os|darwin|apple|homebrew|macports"`
  finds nothing else (the other "Darwin" hit is the Darwin's Voyage wonder).
- Point-release NEWS (NEWS-3.2.1 ... 3.2.6, 3.1.1 ... 3.1.6) live only on the fandom wiki, which is unreachable
  (see header) — **unverified**. From redmine `fixed_version` fields the Mac-relevant point-release fixes are: 3.1.6 /
  3.2.1-era: #1292 (Command-key accelerators), #1489, #1672 (Qt Help menu on Mac); 3.2.2: #1483 (Show Stack Size
  shortcut), #1708 (nations report crash reported from macOS), #1725 (CI macos-26); 3.2.7 (unreleased): #2197,
  #2249, #2338, #2339.

---

## 8. freeciv-environments

`refs/freeciv-environments` (HEAD 0fe2a63 "nightly-main.sh: Run ./update_po.sh"; dirs `buildsetup/`, `buildtest/`,
`dockers/{builders,server}`, `scheduled/`, `testing/`): `grep -rniE 'mac|macos|darwin|apple|homebrew|xcode|osx'`
returns **nothing**. The nightly/build-test infrastructure is Linux/Docker only; macOS exists upstream solely as the
GitHub-hosted `mac-meson` job. (`refs/freeciv-web` likewise has only two generic "macOS/OSX" mentions in README.md:90,111.)

---

## What this means for a macOS 27 arm64 port

**State of play.** Upstream compiles every client (gtk3.22, gtk4, gtk4x, qt6, sdl3, stub) plus ruledit/fcmp on an
`xcode-27` arm64 runner with Homebrew on every push (`refs/freeciv/.github/workflows/ci.yml:53-77`), and the
server autogame passes. Nobody upstream runs a GUI client in CI, packages an .app, codesigns, or ships a binary:
the only official artefact is a 3.1.0-beta1 tarball from March 2023 built by hand by ddeanbrown (section 2e), and the
upstream bundle script was declared a "dead end" and deleted from main on 2025-11-10 (RM #1731). Homebrew is the
de-facto macOS distribution (gtk4 client only, arm64 bottles for macOS 14-27, 41 installs/month); MacPorts is stuck
at 2.6.4.

**Known blockers / gaps (none is a compile blocker; all are packaging/UX).**
1. No app bundle, no dylib relocation, no Info.plist, no codesign/notarize anywhere upstream. The S3_2 script
   (`platforms/macos/homebrew-appbundle.sh`) installs straight into `/Applications/Freeciv.app/Contents/` with
   `CFBundleExecutable ../bin/freeciv-gtk4`, no `NSHighResolutionCapable`, no bundled libs — Homebrew must be present at
   runtime. Freeciv21 shows the working shape: Info.plist.in + CMake install(CODE) + `macdeployqt` + `create-dmg`
   (section 6), but even they have no Developer-ID signing and are x64-only (issue #2777).
2. gtk4 on macOS is reported broken in daily use (focus loss every few clicks, dead menubar on first launch; forum
   t=95527, June 2026, unanswered). gtk4 is exactly what Homebrew ships. Qt and gtk3.22 are the clients with actual
   Mac fixes in the tree (sections 1a, 2d); Dean Brown plays with the Qt client and says the SDL client "I get no menus".
3. SDL: Homebrew's `sdl2` is now `sdl2-compat` over SDL3 (since 2026-05-31); upstream reacted by building the sdl3
   client in CI (RM #2249) and stripping sdl2 paths (RM #2338). The `audio` default is still sdl2 (`meson_options.txt:48-52`);
   CI uses `-Daudio=sdl3`. Prefer sdl3 for anything new.
4. Keg-only Homebrew libs (icu4c@78, readline, gettext) need explicit `CPPFLAGS/LDFLAGS/PKG_CONFIG_PATH`
   (`ci-build.sh:107-112`, `INSTALL:568-590`); macOS libedit is not an acceptable readline.
5. Apple clang warnings (`-Wgnu-folding-constant`, RM #2339/#2355/#2360) are being fixed now; don't build with werror.
6. Mac keyboard semantics are only half done: Meta accelerators in gtk, Qt menu-role hacks, '+'/'-' layout issues
   (RM #1292, #1483, #1489, #1672, #1630, #1684), and help text still says "Ctrl" (RM #1293 open).
7. No HiDPI/Retina ticket exists at all; whether gtk4/Qt render crisply in a bundle is untested upstream.

**Known workarounds.** Use the exact `brew install` list and env from ci.yml/ci-build.sh; remove stale
`/usr/local/bin/python3*` symlinks on GitHub runners (RM #352); pin Python <3.13 if `generate_packets.py` misbehaves
(RM #975, fixed upstream); build with `-Dsyslua=true` + `lua@5.5` on main or `lua@5.4` on S3_2 (RM #1760/#2250);
don't pass `-Dfollowtag=macos` on main (tag dropped, RM #1761/#2177); for Gatekeeper, Freeciv21 documents the
"damaged" dialog override and ad-hoc `codesign --force --sign -`.

**People.** There is no designated macOS maintainer. Marko Lindqvist (cazfi, redmine user 5) owns CI and merges
everything. **Dean Brown** ("ddeanbrown"/"Dino", redmine user 21, 84 tickets) is the de-facto Mac tester/contributor:
built the 3.1.0-beta1 package (osdn#47589, unverified), fixed Command-key/menu bugs, builds via MacPorts on macOS 11.7
(forum). Sabino Maggi packages unofficial arm64 zips. Longturn's jwrober/lmoureaux own Freeciv21's mac pipeline.

**How upstream wants patches.** Open a ticket on https://redmine.freeciv.org/projects/freeciv (README.md:15 "Report bugs
& Submit patches: redmine.freeciv.org"; `doc/BUGS:6,24`) and attach a patch per active branch (S3_2, S3_3, main) with a
conventional commit message (<70-char subject + body) — see cazfi's review notes in RM #1489 and #1292 ("Can you provide
a single patch for S3_3/main?"). `doc/HACKING:1168-1176` still describes `diff -u` patches named descriptively. GitHub
PRs are tolerated but are re-filed as redmine tickets and "Merged outside github UI" (PR #86 -> RM #2167; PR #90 -> RM
#2186/#2222); GitHub issues are disabled. Given RM #1731 ("dead end"), a new bundle script would need to be pitched as a
feature ticket with a rationale (bundled dylibs + signing), probably against main first, with S3_2 backport patches.
