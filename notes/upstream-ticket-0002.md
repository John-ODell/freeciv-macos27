# Draft upstream ticket (NOT POSTED - for review)

Target: https://redmine.freeciv.org/projects/freeciv, tracker Feature, S3_2 / S3_3 / main.
Attach `patches/0002-Add-FREECIV_LOCALE_PATH-environment-variable.patch` (applies to S3_2 44e6898c; S3_3/main to regenerate).

## Subject
Add FREECIV_LOCALE_PATH environment variable for relocatable installations

## Description
`get_locale_dir()` (utility/fcintl.c) returns the compile-time LOCALEDIR, or cwd + LOCALEDIR when it is relative.
A relocatable installation such as a macOS .app bundle (or an unpacked tarball moved to another directory) cannot
know the locale directory at compile time, so translations are silently unavailable: `bindtextdomain()` points at a
directory that does not exist on the user's machine. Data files already have `FREECIV_DATA_PATH` for the same reason.

The patch adds `FREECIV_LOCALE_PATH`: when set and non-empty it is used as the locale directory, otherwise behaviour
is unchanged. Documented in the client and server man pages next to the other FREECIV_* variables.

Tested on macOS 27 (arm64): a bundle with `share/locale` under Contents/Resources and the variable exported by a
launcher script gets translated UI; without the variable it falls back to English as before.

## Commit message (as in the patch)
Add FREECIV_LOCALE_PATH environment variable

Relocatable installations such as a macOS .app bundle cannot know the
locale directory at compile time. Like FREECIV_DATA_PATH for data files,
FREECIV_LOCALE_PATH overrides the built-in LOCALEDIR in get_locale_dir().
Documented in the client and server man pages.
