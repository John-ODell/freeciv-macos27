// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * Main executable of the Freeciv .app bundles made by scripts/bundle.sh.
 *
 * Points Freeciv's data, scenario and locale search paths into the bundle (unless the user set
 * them), sets the GTK runtime variables when the bundle carries GTK data, puts the bundle's
 * Contents/MacOS first on PATH, changes into that directory (the client starts a local game
 * with ./freeciv-server, see client/connectdlg_common.c) and execs the real client.
 *
 * A compiled launcher instead of a shell script, so that the bundle's main executable is Mach-O:
 * hardened runtime and notarization apply to it like to every other binary in the app.
 *
 * A game built on Freeciv (bundle.sh --game) also defines GAME_NAME (set as FREECIV_GAME_NAME for the
 * client's window title), GAME_RULESET (set as FREECIV_GAME_RULESET: "Start new game" plays it on a tileset that
 * names no ruleset), GAME_OPT (its own options file in ~/.freeciv, as FREECIV_OPT, so its settings stay
 * apart from Freeciv's) and GAME_TILESET (passed as -t until that options file names a tileset, unless the player
 * gives -t or --tiles: the client saves the tileset it loads as the default, so a tileset the player picks later in
 * the options is kept).
 *
 * Build: clang -O2 -DCLIENT_BIN='"freeciv-qt"' -DDATASUBDIR='"3.2"' -o Freeciv launcher.c
 */
#include <errno.h>
#include <limits.h>
#include <mach-o/dyld.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef CLIENT_BIN
#error "define CLIENT_BIN, e.g. -DCLIENT_BIN='\"freeciv-qt\"'"
#endif
#ifndef DATASUBDIR
#error "define DATASUBDIR, e.g. -DDATASUBDIR='\"3.2\"'"
#endif

static void fail(const char *what)
{
  fprintf(stderr, "Freeciv launcher: %s: %s\n", what, strerror(errno));
  exit(127);
}

static void join(char *out, size_t size, const char *fmt, const char *a, const char *b, const char *c)
{
  int n = snprintf(out, size, fmt, a, b, c);
  if (n < 0 || (size_t) n >= size) {
    errno = ENAMETOOLONG;
    fail("path too long");
  }
}

/* Like the shell's ${NAME:-value}: set only when unset or empty. */
static void set_default(const char *name, const char *value)
{
  const char *cur = getenv(name);
  if ((cur == NULL || cur[0] == '\0') && setenv(name, value, 1) != 0) {
    fail(name);
  }
}

static void set_always(const char *name, const char *value)
{
  if (setenv(name, value, 1) != 0) {
    fail(name);
  }
}

#ifdef GAME_TILESET
/* Whether the game's tileset should be passed: the player chose none on the command line, and the options file
 * names no tileset for square maps (civ45's iso view is of square tiles). The client writes the tileset it loaded
 * there, so a missing file or an empty value means a first start, or one that ended before a tileset loaded. */
static int pass_game_tileset(int argc, char **argv)
{
  static const char key[] = "default_tileset_square_name=\"";
  const char *opt = getenv("FREECIV_OPT");
  char line[1024];
  int named = 0;
  FILE *f;

  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "-t") == 0 || strncmp(argv[i], "--tiles", 7) == 0) {
      return 0;
    }
  }
  if (opt == NULL || opt[0] == '\0' || (f = fopen(opt, "r")) == NULL) {
    return 1;
  }
  while (!named && fgets(line, sizeof(line), f) != NULL) {
    named = strncmp(line, key, sizeof(key) - 1) == 0 && line[sizeof(key) - 1] != '"';
  }
  fclose(f);
  return !named;
}
#endif

static int is_dir(const char *path)
{
  struct stat st;
  return stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}

int main(int argc, char **argv)
{
  char exe[PATH_MAX], real[PATH_MAX], dir[PATH_MAX], res[PATH_MAX], tmp[PATH_MAX];
  char buf[4 * PATH_MAX], scen[6 * PATH_MAX], client[PATH_MAX];
  uint32_t size = sizeof(exe);
  const char *home, *cur;
  char *slash;

#ifndef GAME_TILESET
  (void) argc;
#endif
  if (_NSGetExecutablePath(exe, &size) != 0 || realpath(exe, real) == NULL) {
    fail("cannot locate the launcher");
  }
  strlcpy(dir, real, sizeof(dir));
  slash = strrchr(dir, '/');
  if (slash == NULL) {
    errno = ENOENT;
    fail("cannot locate the launcher directory");
  }
  *slash = '\0';
  join(tmp, sizeof(tmp), "%s/../Resources%s%s", dir, "", "");
  if (realpath(tmp, res) == NULL) {
    fail("cannot find Contents/Resources");
  }

  home = getenv("HOME");
  if (home == NULL || home[0] == '\0') {
    struct passwd *pw = getpwuid(getuid());
    home = (pw != NULL && pw->pw_dir != NULL) ? pw->pw_dir : "";
  }

  join(buf, sizeof(buf), "%s/share/freeciv:%s/.freeciv/%s", res, home, DATASUBDIR);
  set_default("FREECIV_DATA_PATH", buf);
  join(buf, sizeof(buf), "%s/share/freeciv/scenarios:%s/.freeciv/%s/scenarios", res, home, DATASUBDIR);
  join(scen, sizeof(scen), "%s:%s/.freeciv/scenarios%s", buf, home, "");
  set_default("FREECIV_SCENARIO_PATH", scen);
  join(buf, sizeof(buf), "%s/share/locale%s%s", res, "", "");
  set_default("FREECIV_LOCALE_PATH", buf);
#ifdef GAME_NAME
  set_default("FREECIV_GAME_NAME", GAME_NAME);
#endif
#ifdef GAME_RULESET
  set_default("FREECIV_GAME_RULESET", GAME_RULESET);
#endif
#ifdef GAME_OPT
  join(buf, sizeof(buf), "%s/.freeciv/%s%s", home, GAME_OPT, "");
  set_default("FREECIV_OPT", buf);
#endif

  /* GTK clients: settings schemas, icon lookup, fontconfig, no pixbuf loader cache. */
  join(buf, sizeof(buf), "%s/share/glib-2.0/schemas%s%s", res, "", "");
  if (is_dir(buf)) {
    set_always("GSETTINGS_SCHEMA_DIR", buf);
    cur = getenv("XDG_DATA_DIRS");
    if (cur != NULL && cur[0] != '\0') {
      join(buf, sizeof(buf), "%s/share:%s%s", res, cur, "");
    } else {
      join(buf, sizeof(buf), "%s/share%s%s", res, "", "");
    }
    set_always("XDG_DATA_DIRS", buf);
    join(buf, sizeof(buf), "%s/etc/gdk-pixbuf-loaders.cache%s%s", res, "", "");
    set_always("GDK_PIXBUF_MODULE_FILE", buf);
    join(buf, sizeof(buf), "%s/etc/fonts%s%s", res, "", "");
    if (is_dir(buf)) {
      set_always("FONTCONFIG_PATH", buf);
    }
  }

  cur = getenv("PATH");
  join(buf, sizeof(buf), "%s%s%s", dir, (cur != NULL && cur[0] != '\0') ? ":" : "", cur != NULL ? cur : "");
  set_always("PATH", buf);

  if (chdir(dir) != 0) {
    fail(dir);
  }
  join(client, sizeof(client), "%s/%s%s", dir, CLIENT_BIN, "");
  argv[0] = client;
#ifdef GAME_TILESET
  if (pass_game_tileset(argc, argv)) {
    char **args = calloc((size_t) argc + 3, sizeof(char *));

    if (args == NULL) {
      fail("out of memory");
    }
    args[0] = client;
    args[1] = "-t";
    args[2] = GAME_TILESET;
    for (int i = 1; i < argc; i++) {
      args[i + 2] = argv[i];
    }
    execv(client, args);
    fail(client);
  }
#endif
  execv(client, argv);
  fail(client);
  return 127;
}
