# Prompt for the website builder: Freeciv for macOS 27 download page

Written 2026-10-18 for John to hand to the Claude session that builds northbridgelandmark.com
(repo John-ODell/website, clone ~/Desktop/website). Paste everything below the line.

---

Add a page for **Freeciv for macOS 27** to the site: a free download of John's macOS build of the open-source
strategy game Freeciv. The download itself stays on GitHub; our page explains it, gives one big button that
starts the download, and walks a non-technical player through installing it.

Read CLAUDE.md, LOCAL-SESSION.md and HANDOFF.md first, as always.

## The facts (checked 2026-10-18)

- **What it is:** Freeciv 3.2.6, the Qt client, packaged by John as a self-contained Mac app (no Homebrew or
  anything else to install). Source repo and releases: https://github.com/John-ODell/freeciv-macos27
- **Current release:** "Freeciv 3.2.6 for macOS 27 (Apple Silicon), build mac1", tag `v3.2.6-mac1`,
  https://github.com/John-ODell/freeciv-macos27/releases/tag/v3.2.6-mac1
- **Files on that release:** `Freeciv-3.2.6-arm64.dmg` (about 89 MB, the download), its `.sha256` checksum,
  and `freeciv-3.2.6-mac1-src.tar.gz` (the exact source, required by the GPL).
- **Requirements:** macOS 27.0 or later, Apple Silicon (M-series) Mac. Intel Macs are not supported by this
  build. Players on Windows, Linux, Intel Macs or older macOS should use the official downloads at
  https://www.freeciv.org.
- **Signing:** this build is not notarized yet, so macOS blocks the first launch (install step 3 below). John
  is setting up notarization; a later build will open with no extra step.
- **Licence:** Freeciv is free software under the GNU GPL v2 or later. It is not sold and the page carries no
  ads. It is an unofficial build by John, not a release of the Freeciv project.

## The page

- A new page at `/games/freeciv/` and an entry in `GAMES` in `site/js/data.js`, in the same style as the other
  games. Title "Freeciv for Mac", one-line description such as "The open-source civilization-building strategy
  game, packaged for macOS 27 on Apple Silicon. Free download." Do not call it "Civilization" or "Civ" and do
  not use any Civilization or Firaxis artwork, logos or screenshots.
- At the top: a short intro (what Freeciv is: build cities, research technologies, explore and conquer on a
  turn-based map, play against computer opponents or online), then **one large Download for Mac button**, with
  the version, file size and "macOS 27 or later, Apple Silicon" under it.
- Then "How to install", three numbered steps a non-technical player can follow, then a small "More" section.
- Screenshots: only ones John supplies from his own build; leave a placeholder if none are given.

## One-click download

- The button links straight to the DMG file, so one click starts the download.
- Do not hard-code the file name. On page load, fetch
  `https://api.github.com/repos/John-ODell/freeciv-macos27/releases/latest` (public, no key), pick the asset
  whose name ends in `-arm64.dmg`, and set the button's `href` to its `browser_download_url`; fill the version
  from `name` or `tag_name` and the size from `size`. Cache the answer in `sessionStorage`.
- Without JavaScript, or if the API call fails or is rate-limited, the button's default `href` is
  `https://github.com/John-ODell/freeciv-macos27/releases/latest`, which always shows the newest release.
- Below the button, small links: "All releases and source code" (the releases page) and "Other systems:
  freeciv.org" (https://www.freeciv.org).
- If the visitor is clearly not on a Mac (the user agent says Windows, Android, iPhone or Linux), show a gentle
  note under the button pointing to freeciv.org. Browsers cannot tell Apple Silicon from Intel reliably, so do
  not try; the requirement line covers it.
- Do not host or proxy the DMG on our site or Worker: GitHub serves it.

## How to install (text for the page)

1. **Download** with the button. The file `Freeciv-3.2.6-arm64.dmg` lands in Downloads.
2. **Open the DMG and drag Freeciv to Applications.** Double-click the downloaded file, then drag the Freeciv
   icon onto the Applications folder in the window that opens.
3. **Allow it the first time.** Open Freeciv from Applications. macOS shows a warning that it could not verify
   the app; click Done (not Move to Trash). The exact wording varies between macOS versions. Open System Settings, go to Privacy & Security, scroll down to the message about
   Freeciv, and click **Open Anyway**, then confirm. From then on Freeciv opens normally.

Make step 3 depend on one setting in `data.js`, for example `FREECIV.notarized = false`, so that when John
says a notarized build is out, flipping it to `true` removes step 3 and the note about it. Do not guess the
current state: it is `false` until John says otherwise.

In the "More" section, collapsed by default:
- **Check the download (optional):** in Terminal, in the Downloads folder:
  `shasum -a 256 -c Freeciv-3.2.6-arm64.dmg.sha256` after downloading the `.sha256` file from the release page.
  Use the file names from the API too, not hard-coded ones.
- **Terminal alternative to step 3:** `xattr -dr com.apple.quarantine /Applications/Freeciv.app`. Give every
  command a copy button.
- **Uninstall:** drag Freeciv from Applications to the Trash.
- **Source code and licence:** link the release's source archive and the repo; state the GPL v2 or later.
- **Credits:** Freeciv is developed by the Freeciv project (https://www.freeciv.org); this Mac build is by John.
  Add the same credit to the Links page, as the site's rules require for third-party content.

## Done looks like

- `/games/freeciv/` and its Games entry work in `npm run dev` at desktop and phone width, with no console
  errors and no sideways scroll, and the button downloads the DMG in one click (check the `href` it resolves
  to; don't commit a downloaded DMG).
- The fallback works with JavaScript off and with the API blocked.
- A Playwright test in `tests/` covers the page: the button exists, its fallback `href` is the releases page,
  and with a mocked API answer it points at the `-arm64.dmg` asset.
- Committed through the site's usual GitHub record: an issue, a branch, a PR with a review, a squash merge.
  Nothing goes live until John says so; pushing to `main` deploys.
- **No AI attribution anywhere:** follow https://github.com/John-ODell/github-cleanhub (the github-bullseye
  skill). No `Co-Authored-By` lines, no "Generated with" lines, nothing authored as Claude. This replaces the
  "Keep the Co-Authored-By line" sentence in the site's CLAUDE.md.
