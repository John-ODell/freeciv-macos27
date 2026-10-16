#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Make an .app bundle's Mach-O files self-contained.

Walks every Mach-O under Contents/MacOS, Contents/Frameworks and Contents/PlugIns. Any dependency that lives
outside the bundle and outside /usr/lib and /System (Homebrew, the install prefix, ...) is copied into
Contents/Frameworks (whole .framework directories for frameworks, minus Headers), its LC_ID_DYLIB is set to
@rpath/<leaf>, the referencing LC_LOAD_DYLIB is rewritten to @rpath/<leaf>, and every executable and library gets
LC_RPATH entries for @executable_path/../Frameworks and @loader_path/../Frameworks. Dependencies that Homebrew
already expresses relatively (@loader_path/libfoo.dylib, @rpath/QtX.framework/...) are resolved against the
library's original location, copied under the referenced name, and left as they are. At the end every
reference must resolve inside the bundle or the script exits non-zero.

Usage: fix-dylibs.py <App.app> [--extra /path/to/lib.dylib ...]
--extra copies libraries nothing links against directly (dlopen'ed ones such as libSDL3).
"""
import os, shutil, subprocess, sys, stat, glob

def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(a)}\n{r.stderr}")
    return r.stdout

def is_macho(p):
    try:
        with open(p, 'rb') as f:
            m = f.read(4)
    except (IsADirectoryError, FileNotFoundError):
        return False
    return m in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xfe\xed\xfa\xcf')

def loads(p):
    out = sh('otool', '-L', p).splitlines()[1:]
    return [l.split()[0] for l in out if l.strip()]

def dylib_id(p):
    out = sh('otool', '-D', p).splitlines()
    return out[1].strip() if len(out) > 1 else None

def rpaths(p):
    out = sh('otool', '-l', p).splitlines()
    return [out[i + 2].split()[1] for i, l in enumerate(out) if l.strip() == 'cmd LC_RPATH']

def external(dep):
    return dep.startswith('/') and not dep.startswith('/usr/lib') and not dep.startswith('/System')

def split_framework(path):
    """'/x/Qt.framework/Versions/A/Qt' -> ('/x/Qt.framework', 'Versions/A/Qt') or None"""
    if '.framework/' not in path:
        return None
    i = path.index('.framework/') + len('.framework')
    return path[:i], path[i + 1:]

class Bundler:
    def __init__(self, app):
        self.app = app
        self.fw = os.path.join(app, 'Contents', 'Frameworks')
        os.makedirs(self.fw, exist_ok=True)
        self.src_of = {}      # bundle file (realpath) -> original file (realpath)
        self.copied = []
        self.work = []
        self.seen = set()

    def copy_dylib(self, src, name):
        """copy a plain dylib into Frameworks as <name>; add a symlink for its real basename if different"""
        real = os.path.realpath(src)
        dst = os.path.join(self.fw, name)
        if not os.path.exists(dst):
            shutil.copy2(real, dst)
            os.chmod(dst, 0o755)
            self.src_of[dst] = real
            self.copied.append(name)
            print(f"copied {real} -> Frameworks/{name}")
        rb = os.path.basename(real)
        if rb != name and not os.path.exists(os.path.join(self.fw, rb)):
            os.symlink(name, os.path.join(self.fw, rb))
        self.work.append(dst)
        return dst

    def copy_framework(self, fdir_src, rel):
        fname = os.path.basename(fdir_src)
        fdir_dst = os.path.join(self.fw, fname)
        if not os.path.isdir(fdir_dst):
            shutil.copytree(os.path.realpath(fdir_src), fdir_dst, symlinks=True)
            for root, dirs, _ in os.walk(fdir_dst):
                for d in list(dirs):
                    if d == 'Headers':
                        hp = os.path.join(root, d)
                        os.remove(hp) if os.path.islink(hp) else shutil.rmtree(hp)
                        dirs.remove(d)
            self.copied.append(fname)
            print(f"copied {os.path.realpath(fdir_src)} -> Frameworks/{fname}")
            for root, _, files in os.walk(fdir_dst):
                for f in files:
                    p = os.path.join(root, f)
                    if not os.path.islink(p) and is_macho(p):
                        rp = os.path.realpath(p)
                        self.src_of[rp] = os.path.realpath(os.path.join(os.path.realpath(fdir_src), os.path.relpath(p, fdir_dst)))
                        self.work.append(rp)
        return os.path.realpath(os.path.join(fdir_dst, rel))

    def resolve_relative(self, dep, p):
        """find the original file behind an @rpath/ or @loader_path/ reference made by bundle file p"""
        src = self.src_of.get(p, p)
        srcdir = os.path.dirname(src)
        if dep.startswith('@loader_path/'):
            cands = [os.path.join(srcdir, dep[len('@loader_path/'):])]
        else:
            leaf = dep[len('@rpath/'):]
            dirs = []
            for rp in rpaths(src):
                rp = rp.replace('@loader_path', srcdir).replace('@executable_path', srcdir)
                dirs.append(rp)
            # Homebrew frameworks/dylibs refer to siblings; walk up out of X.framework/Versions/A
            d = srcdir
            for _ in range(4):
                dirs.append(d); d = os.path.dirname(d)
            dirs += ['/opt/homebrew/lib'] + glob.glob('/opt/homebrew/opt/qt*/lib')
            cands = [os.path.join(x, leaf) for x in dirs]
        for c in cands:
            if os.path.exists(c):
                return os.path.normpath(c)   # no '..' left, or split_framework() picks the wrong .framework
        return None

    def run(self, extra):
        for sub in ('MacOS', 'Frameworks', 'PlugIns'):
            for root, _, files in os.walk(os.path.join(self.app, 'Contents', sub)):
                for f in files:
                    p = os.path.join(root, f)
                    if not os.path.islink(p) and is_macho(p):
                        self.work.append(os.path.realpath(p))
        for e in extra:
            self.copy_dylib(e, os.path.basename(os.path.realpath(e)))

        while self.work:
            p = self.work.pop()
            if p in self.seen:
                continue
            self.seen.add(p)
            os.chmod(p, os.stat(p).st_mode | stat.S_IWUSR)
            myid = dylib_id(p)
            changes = []
            for dep in loads(p):
                if dep == myid:
                    continue
                if external(dep):
                    fwk = split_framework(dep)
                    if fwk:
                        self.copy_framework(*fwk)
                        changes += ['-change', dep, f'@rpath/{os.path.basename(fwk[0])}/{fwk[1]}']
                    else:
                        name = os.path.basename(dep)
                        self.copy_dylib(dep, name)
                        changes += ['-change', dep, f'@rpath/{name}']
                elif dep.startswith('@rpath/') or dep.startswith('@loader_path/'):
                    leaf = dep.split('/', 1)[1]
                    inside = os.path.join(self.fw, leaf) if dep.startswith('@rpath/') else os.path.normpath(os.path.join(os.path.dirname(p), leaf))
                    if os.path.exists(inside):
                        self.work.append(os.path.realpath(inside))
                        continue
                    orig = self.resolve_relative(dep, p)
                    if orig is None:
                        continue  # reported by the final check
                    fwk = split_framework(orig)
                    if fwk:
                        self.copy_framework(*fwk)
                    else:
                        self.copy_dylib(orig, os.path.basename(leaf))
            if p.startswith(self.fw + os.sep):
                fwk = split_framework(p)
                want = f'@rpath/{os.path.basename(fwk[0])}/{fwk[1]}' if fwk else f'@rpath/{os.path.basename(p)}'
                if myid and myid != want:
                    changes += ['-id', want]
            have = rpaths(p)
            for rp in ('@executable_path/../Frameworks', '@loader_path/../Frameworks'):
                if rp not in have:
                    changes += ['-add_rpath', rp]
            for rp in have:
                if rp.startswith('/opt/homebrew') or rp.startswith('/Users/') or rp.startswith('/usr/local'):
                    changes += ['-delete_rpath', rp]
            if changes:
                sh('install_name_tool', *changes, p)

        bad = []
        for p in sorted(self.seen):
            myid = dylib_id(p)
            for dep in loads(p):
                if dep == myid:
                    continue
                if external(dep):
                    bad.append((p, dep))
                elif dep.startswith('@rpath/'):
                    if not os.path.exists(os.path.join(self.fw, dep[len('@rpath/'):])):
                        bad.append((p, dep + '  [unresolved]'))
                elif dep.startswith('@loader_path/'):
                    if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(p), dep[len('@loader_path/'):]))):
                        bad.append((p, dep + '  [unresolved]'))
        if bad:
            for p, d in bad:
                print(f"STILL EXTERNAL: {d}  (from {os.path.relpath(p, self.app)})")
            raise SystemExit(1)
        print(f"ok: {len(self.seen)} Mach-O files checked, {len(self.copied)} libraries/frameworks copied into Contents/Frameworks")

def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    extra = args[args.index('--extra') + 1:] if '--extra' in args else []
    Bundler(os.path.abspath(args[0])).run(extra)

if __name__ == '__main__':
    main()
