# Draft upstream ticket (NOT POSTED - for review)

Target: https://redmine.freeciv.org/projects/freeciv, tracker Bug, affects S3_2 (3.2.6+), S3_3, main.
Attach `patches/0001-build-add-audio-dependency-to-gtk3.22-gtk4-and-Qt-cl.patch` (S3_2); S3_3/main need re-generation
against their meson.build line numbers (not yet done).

## Subject
meson: gtk3.22, gtk4 and qt clients fail to compile when SDL headers are not on the default include path

## Description
On macOS 27 with Homebrew (`-Daudio=sdl2`, sdl2-compat 2.32.74), `freeciv-gtk3.22`, `freeciv-gtk4` and `freeciv-qt`
fail to compile:

    client/gui-gtk-3.22/gui_main.c:26:10: fatal error: 'SDL2/SDL.h' file not found
    client/gui-qt/gui_main.cpp:26:10: fatal error: 'SDL2/SDL.h' file not found

The executable targets for those three clients list `dependencies: [<gui>_dep, net_dep, gettext_dep, mw_extra_dep]`
without `audio_dep` (meson.build lines 3354, 3447, 3574 on S3_2). `client_common` has `audio_dep`, but meson does not
propagate a static library's include directories through `link_with`, so the gui_main sources that include
`SDL2/SDL.h` directly (for `SDL_Init`/`audio_init`) get no `-I/opt/homebrew/include`. The sdl2, sdl3 and stub
executables already list `audio_dep`. On Linux the problem is hidden because `/usr/include/SDL2` is reachable from the
default include path.

The attached patch adds `audio_dep` to the three targets. Verified on macOS 27.0.1 arm64 (Xcode 27, meson 1.12.1):
all clients compile, link and run; no change on Linux expected (the dependency was already present via client_common
for linking).

I have not understood why the mac-meson CI job (`-Daudio=sdl3`) does not hit this; possibly another dependency on the
runner drags in `-I/opt/homebrew/include`.

## Commit message (as in the patch)
build: add audio dependency to gtk3.22, gtk4 and Qt client targets

The gui_main sources of these clients include SDL headers directly, but
their executable targets did not list audio_dep, so the SDL include path
was missing when SDL is not on the default include path (Homebrew on macOS).
