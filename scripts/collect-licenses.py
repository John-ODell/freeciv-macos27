#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Collect licence texts and source locations for everything bundled in a Freeciv .app.

Usage: scripts/collect-licenses.py APP [--freeciv-src DIR] [--brew-prefix DIR]

Writes APP/Contents/Resources/licenses/<component>/... and
APP/Contents/Resources/licenses/THIRD-PARTY-NOTICES.txt.

Every Mach-O file under Contents/Frameworks and Contents/PlugIns is traced to the Homebrew formula
that installed it (through <brew-prefix>/opt/<formula>). Licence, homepage and the formula's source URL
come from `brew info --json=v2`; the exact source URL of the installed version comes from the keg's
sbom.spdx.json when present. Licence files are copied from the keg. When a keg ships none, the
standard text for each GPL-family licence in its SPDX expression is copied from another installed keg.
Libraries Freeciv compiles into libfreeciv (Lua, tolua, cvercmp) are covered from the Freeciv source.
Exit status 1 if a bundled file cannot be traced or a needed licence text is missing.
"""
import glob, json, os, re, shutil, subprocess, sys

LICENCE_FILE = re.compile(r"^(LICEN[CS]E|COPYING|COPYRIGHT|NOTICE)", re.I)
# Title lines that identify standard licence texts, for kegs that ship none of their own.
STANDARD_TEXTS = {
    "GPL-2.0": ("GNU GENERAL PUBLIC LICENSE", "Version 2, June 1991"),
    "GPL-3.0": ("GNU GENERAL PUBLIC LICENSE", "Version 3, 29 June 2007"),
    "LGPL-2.1": ("GNU LESSER GENERAL PUBLIC LICENSE", "Version 2.1, February 1999"),
    "LGPL-3.0": ("GNU LESSER GENERAL PUBLIC LICENSE", "Version 3, 29 June 2007"),
}


def die(msg):
    print("collect-licenses: " + msg, file=sys.stderr)
    sys.exit(1)


def is_macho(path):
    try:
        with open(path, "rb") as f:
            magic = f.read(4)
    except OSError:
        return False
    return magic in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca")


def bundled_items(contents):
    """Yield (display name, lookup key) for bundled libraries, frameworks and plugins."""
    fw = os.path.join(contents, "Frameworks")
    for name in sorted(os.listdir(fw)) if os.path.isdir(fw) else []:
        path = os.path.join(fw, name)
        if name.endswith(".framework"):
            yield name, name
        elif os.path.isfile(path) and not os.path.islink(path) and is_macho(path):
            yield name, name
    pl = os.path.join(contents, "PlugIns")
    for root, _, files in os.walk(pl):
        for name in sorted(files):
            path = os.path.join(root, name)
            if is_macho(path):
                yield os.path.relpath(path, pl), name


def opt_index(brew):
    """Map library basename / framework name -> formula that owns the real file.

    Files are found through <brew>/opt/*, then resolved: the owner is the keg under
    <brew>/Cellar/<formula>/<version> that holds the real file, so umbrella formulas
    (qt) and symlink-only kegs never claim another formula's library."""
    cellar = os.path.realpath(os.path.join(brew, "Cellar")) + os.sep
    index = {}
    def owner(path):
        real = os.path.realpath(path)
        return real[len(cellar):].split(os.sep)[0] if real.startswith(cellar) else None
    for opt in sorted(glob.glob(os.path.join(brew, "opt", "*"))):
        for sub in ("lib", os.path.join("share", "qt", "plugins")):
            base = os.path.join(opt, sub)
            if not os.path.isdir(base):
                continue
            for root, dirs, files in os.walk(base, followlinks=True):
                for d in dirs:
                    if d.endswith(".framework"):
                        f = owner(os.path.join(root, d))
                        if f:
                            index.setdefault(d, f)
                dirs[:] = [d for d in dirs if not d.endswith(".framework")]
                for name in files:
                    f = owner(os.path.join(root, name))
                    if f:
                        index.setdefault(name, f)
    return index


def spdx_ids(expr):
    return sorted(set(re.findall(r"[A-Za-z0-9.+-]+(?=\s|\)|$)", expr or ""))
                  - {"AND", "OR", "WITH"})


def find_standard_text(brew, key, cache={}):
    if key in cache:
        return cache[key]
    title, version = STANDARD_TEXTS[key]
    found = None
    for path in sorted(glob.glob(os.path.join(brew, "Cellar", "*", "*", "*"))):
        if not os.path.isfile(path) or not LICENCE_FILE.match(os.path.basename(path)):
            continue
        try:
            head = open(path, encoding="utf-8", errors="replace").read(400)
        except OSError:
            continue
        if title in head and version in head and (key.startswith("L") or "LESSER" not in head):
            found = path
            break
    cache[key] = found
    return found


def main(argv):
    args = list(argv)
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    app = os.path.abspath(args.pop(0))
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "port", "freeciv")
    brew = "/opt/homebrew"
    while args:
        opt = args.pop(0)
        if opt == "--freeciv-src" and args:
            src = args.pop(0)
        elif opt == "--brew-prefix" and args:
            brew = args.pop(0)
        else:
            die("unknown argument " + opt)
    contents = os.path.join(app, "Contents")
    out = os.path.join(contents, "Resources", "licenses")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    index = opt_index(brew)
    used = {}           # formula -> [bundled names]
    untraced = []
    for shown, key in bundled_items(contents):
        if key == "libfreeciv.dylib":
            continue  # Freeciv itself, covered by ../COPYING and ../SOURCE.txt
        formula = index.get(key)
        if formula is None:
            untraced.append(shown)
        else:
            used.setdefault(formula, []).append(shown)

    info = {}
    if used:
        raw = subprocess.run(["brew", "info", "--json=v2"] + sorted(used), capture_output=True, text=True, check=True).stdout
        for f in json.loads(raw)["formulae"]:
            info[f["name"]] = f
            for alias in f.get("aliases", []) + f.get("oldnames", []):
                info.setdefault(alias, f)

    problems = []
    rows = []
    for formula in sorted(used):
        f = info.get(formula, {})
        keg = os.path.realpath(os.path.join(brew, "opt", formula))
        version = os.path.basename(keg)
        licence = f.get("license") or "unknown"
        url = ((f.get("urls") or {}).get("stable") or {}).get("url", "")
        sbom = os.path.join(keg, "sbom.spdx.json")
        if os.path.isfile(sbom):
            try:
                pkgs = json.load(open(sbom)).get("packages", [])
                loc = [p.get("downloadLocation") for p in pkgs if p.get("name") == formula and p.get("downloadLocation")]
                if loc and loc[0] != "NOASSERTION":
                    url = loc[0]
            except (OSError, ValueError):
                pass
        dest = os.path.join(out, formula)
        os.makedirs(dest)
        copied = []
        for name in sorted(os.listdir(keg)):
            path = os.path.join(keg, name)
            if os.path.isfile(path) and LICENCE_FILE.match(name):
                shutil.copy2(path, os.path.join(dest, name))
                copied.append(name)
        if not copied:
            wanted = set()
            for sid in spdx_ids(licence):
                for key in STANDARD_TEXTS:
                    if sid.startswith(key + "-") or sid == key:
                        wanted.add(key)
            if "LGPL-3.0" in wanted:
                wanted.add("GPL-3.0")  # LGPLv3 is additional permissions on top of GPLv3
            for key in sorted(wanted):
                text = find_standard_text(brew, key)
                if text:
                    shutil.copy2(text, os.path.join(dest, key + ".txt"))
                    copied.append(key + ".txt")
                else:
                    problems.append(f"{formula}: no local copy of the {key} text")
            if not wanted:
                problems.append(f"{formula}: keg has no licence file and {licence!r} has no standard text here")
        rows.append((formula, version, licence, url, f.get("homepage", ""), used[formula], copied))

    # Libraries Freeciv compiles into libfreeciv.dylib.
    vendored = []
    lua_h = os.path.join(src, "dependencies", "lua-5.4", "src", "lua.h")
    if os.path.isfile(lua_h):
        text = open(lua_h, encoding="utf-8", errors="replace").read()
        m = re.search(r"/\*{5,}.*?Copyright \(C\).*?\*{5,}/", text, re.S)
        if m:
            os.makedirs(os.path.join(out, "lua"))
            open(os.path.join(out, "lua", "LICENSE.txt"), "w").write(m.group(0) + "\n")
            vendored.append(("lua", "5.4 (in Freeciv's dependencies/lua-5.4)", "MIT", "lua/LICENSE.txt"))
        else:
            problems.append("lua: copyright block not found at the end of lua.h")
    for name, rel, licence in (("tolua", "tolua-5.2/README", "tolua licence (permissive, see file)"),
                               ("cvercmp", "cvercmp/README.cvercmp", "GPL-2.0-or-later (granted to Freeciv, see file)")):
        path = os.path.join(src, "dependencies", rel)
        if os.path.isfile(path):
            os.makedirs(os.path.join(out, name))
            shutil.copy2(path, os.path.join(out, name, os.path.basename(path)))
            vendored.append((name, "in Freeciv's dependencies/" + os.path.dirname(rel), licence,
                             name + "/" + os.path.basename(path)))
        else:
            problems.append(f"{name}: {path} missing")

    app_name = os.path.basename(app)
    lines = [
        f"{app_name}: third-party components",
        "=" * (len(app_name) + 24),
        "",
        "Freeciv itself is free software under the GNU GPL, version 2 or any later version: see ../COPYING.",
        "../SOURCE.txt names the exact Freeciv source and patches this app was built from.",
        "",
        "The libraries below were copied into the app from Homebrew and keep their own licences. Where a",
        "component offers a choice (\"A OR B\"), you may use it under any of the offered licences; Qt is",
        "used here under the LGPL-3.0. The GNU GPL v3 terms apply to freeciv-server and freeciv-ruledit as",
        "distributed here, because they link GNU readline (GPL-3.0-or-later); Freeciv's \"version 2 or",
        "later\" grant allows that.",
        "",
        "Source code: each Source line is where that exact version is published. If a link stops working,",
        "open an issue at https://github.com/John-ODell/freeciv-macos27/issues and the source will be provided.",
        "Libraries under the LGPL are dynamically linked (Contents/Frameworks) and can be replaced: put the",
        "modified library in its place, then re-sign the app for use on your Mac with",
        f"  codesign --force --deep --sign - {app_name}",
        "(a Developer ID signature with hardened runtime refuses to load a changed library until then).",
        "",
    ]
    for formula, version, licence, url, home, names, copied in rows:
        lines += [
            f"{formula} {version}",
            f"  Licence:  {licence}",
            f"  Source:   {url or 'unknown'}",
            f"  Homepage: {home or 'unknown'}",
            f"  Bundled:  {', '.join(names)}",
            f"  Texts:    {', '.join(formula + '/' + c for c in copied) or 'none found'}",
            "",
        ]
    lines += ["Compiled into libfreeciv.dylib from Freeciv's own source tree:", ""]
    for name, where, licence, text in vendored:
        lines += [f"{name}", f"  Version:  {where}", f"  Licence:  {licence}", f"  Texts:    {text}", ""]
    open(os.path.join(out, "THIRD-PARTY-NOTICES.txt"), "w").write("\n".join(lines))

    print(f"collect-licenses: {len(rows)} Homebrew components, {len(vendored)} vendored, -> {out}")
    for u in untraced:
        print(f"  UNTRACED: {u}")
    for p in problems:
        print(f"  MISSING: {p}")
    return 1 if (untraced or problems) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
