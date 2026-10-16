# Releases

## How a release is cut

1. `scripts/build.sh qt` on a clean `port/freeciv` at the commit to ship (upstream S3_2 plus `patches/`).
2. `scripts/test.sh ~/freeciv-builds/qt` (100-turn autogame plus client save/load probe) must pass.
3. `scripts/bundle.sh qt` (for a notarized release add `--sign "Developer ID Application: <Name> (<TEAMID>)"`),
   then `scripts/game-probe.sh` against the bundle's `Contents/MacOS/Freeciv`. The bundle carries
   `Contents/Resources/COPYING`, `SOURCE.txt` (upstream commit, local patches) and `licenses/`: each bundled
   library's licence texts and source location, summed up in `licenses/THIRD-PARTY-NOTICES.txt`.
   `bundle.sh` stops if `scripts/collect-licenses.py` cannot trace a bundled library to its Homebrew formula
   or finds no licence text for it.
4. `scripts/dmg.sh ~/freeciv-builds/apps/Freeciv.app` writes the DMG and its sha256 (for a notarized release add
   `--sign "Developer ID Application: <Name> (<TEAMID>)" --notarize-profile freeciv-notary`, see below).
5. Source tarball of the exact tree: `git -C port/freeciv archive --format=tar.gz --prefix=freeciv-<ver>-mac<N>/ -o freeciv-<ver>-mac<N>-src.tar.gz <commit>`.
   GPL v2 section 3 requires the matching source to be available with the binary; the tarball on the release
   page is that source, and `SOURCE.txt` in the bundle points to it.
6. `gh release create v<ver>-mac<N>` on John-ODell/freeciv-macos27 with the DMG, both sha256 files and the tarball.
   Release assets are not commits, so the "no binaries in git" rule from the brief holds.

Nothing is notarized unless `dmg.sh --sign <Developer ID> --notarize-profile <profile>` is used, which needs an
Apple Developer Program membership (99 USD/year, observed on developer.apple.com pricing as of 2026, unverified
for the current year). Without it macOS 27 Gatekeeper refuses the first launch (observed, notes/step5-port.md)
and the user must choose Open Anyway or clear the quarantine attribute. No App Store is involved either way.

## Developer ID signing and notarization

Apple's notary service requires, for every executable: a Developer ID certificate (not ad hoc, not Apple
Development), hardened runtime, a secure timestamp, no `get-task-allow` entitlement, and the macOS 10.9 SDK or
later (observed, "Prepare your software for notarization" on
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution, read
2026-10-16). Given a Developer ID identity, `scripts/sign-app.sh` meets the first four for every Mach-O in
the bundle, the compiled launcher (`scripts/launcher.c`) included; the binaries are built with the current
macOS SDK, which covers the fifth (derived). Nothing in the bundle needs an entitlement (derived: no JIT, no
`DYLD_` variables, one signing identity for every library, so library validation passes; a copy signed with
hardened runtime by the Apple Development identity passed `scripts/game-probe.sh`, observed 2026-10-16).

State on 2026-10-16: the login keychain holds a Developer ID Application identity, issued that day by
Developer ID Certification Authority (G2) and valid until 2027-11-15, next to the Apple Development one
(observed, `security find-identity -v -p codesigning` and `openssl x509 -dates`). A throwaway binary signed
with it, hardened runtime and secure timestamp, passes `codesign --verify --strict` and carries the chain
Developer ID Application > Developer ID Certification Authority > Apple Root CA (observed). No notarytool
profile is stored yet, so nothing has been notarized. Software signed while the certificate is valid keeps
running after it expires, but new releases need a new certificate (the Developer ID page cited below; it
says so for apps without a Developer ID provisioning profile, and the bundle has none).

One-time setup, done by the account holder by hand (no script here touches the private key or the passwords):

1. Create a "Developer ID Application" certificate. Required role: Account Holder; a team can have up to five
   (observed, https://developer.apple.com/help/account/certificates/create-developer-id-certificates/, read 2026-10-16).
   Xcode can do the same from Settings > Accounts > Manage Certificates (unverified on Xcode for macOS 27).
   By hand on macOS 27 (observed 2026-10-16 unless marked otherwise):
   - Make the signing request in Keychain Access. `open -a "Keychain Access"` opens the Passwords app
     instead; open the real one (Keychain Access 11.0) by its path:

         open "/System/Library/CoreServices/Applications/Keychain Access.app"

     Click an empty spot in the item list, then choose Keychain Access > Certificate Assistant > Request a
     Certificate From a Certificate Authority…. With an item selected the menu item ends in "With “<item>”…"
     (its `Localizable.loctable`) and, inferred, uses that item's key instead of a new one. Enter the Apple ID
     email and a name, leave CA Email Address empty, choose Saved to disk. Do not open the saved
     `.certSigningRequest`: double-clicking it starts Certificate Assistant's flow for issuing a certificate
     as your own CA.
   - Web: Certificates, Identifiers & Profiles > Certificates > + > Developer ID > Developer ID Application,
     G2 Sub-CA, Choose File with the request, Continue, Download. Developer ID Installer sits next to it and
     signs Mac installer packages instead (Apple's page above); the download's name tells them apart:
     `developerID_application.cer` is the right one, `developerID_installer.cer` is not.
   - One request per certificate: the portal refuses a request that "has already been used to generate
     another certificate" and asks for a new one.
   - Double-click the `.cer` and choose the login keychain, not iCloud or System.
2. Check: `security find-identity -v -p codesigning` lists `Developer ID Application: <Name> (<TEAMID>)` with
   its 40-hex SHA-1 hash; `--sign` takes either, and the hash avoids retyping a name with punctuation in it.
   The first signatures with a key made this way most likely ask for the login keychain password: choose
   Always Allow, because `sign-app.sh` signs every Mach-O in the bundle separately. Observed: the first three
   test signatures with the new key took 10 to 12 s each, the next ones 0.03 s (the Apple Development key:
   0.04 s); that the password prompt was the delay is inferred.
3. Make an app-specific password for the Apple ID: account.apple.com > Sign-In and Security > App-Specific
   Passwords (observed, https://support.apple.com/en-us/102654, read 2026-10-16).
4. Store it for notarytool, which prompts for the password when `--password` is left out (observed,
   `xcrun notarytool store-credentials --help`, notarytool 1.1.3):

       xcrun notarytool store-credentials freeciv-notary --apple-id <apple-id> --team-id <TEAMID>

Each notarized release, after steps 1 and 2 of the checklist above:

    scripts/bundle.sh qt --sign "Developer ID Application: <Name> (<TEAMID>)"
    scripts/dmg.sh ~/freeciv-builds/apps/Freeciv.app --sign "Developer ID Application: <Name> (<TEAMID>)" \
        --notarize-profile freeciv-notary
    xcrun stapler validate ~/freeciv-builds/apps/Freeciv-<ver>-arm64.dmg
    spctl -a -t open --context context:primary-signature -vv ~/freeciv-builds/apps/Freeciv-<ver>-arm64.dmg

`dmg.sh` uploads the DMG to Apple, waits for the verdict and staples the ticket. If Apple rejects it,
`xcrun notarytool log <submission-id> --keychain-profile freeciv-notary` prints Apple's log as JSON
(observed, `xcrun notarytool log --help`, notarytool 1.1.3). The expected `spctl`
verdict is "accepted" with source "Notarized Developer ID" (inferred from Gatekeeper's usual output, to be
confirmed on the first run). Do not put the Apple ID, team ID or password in this repository: it is public.

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
