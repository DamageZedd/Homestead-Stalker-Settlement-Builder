"""List every texture path referenced by the shipped HomesteadHF .ogf models and
report the ones that are not in the plain-Anomaly texture extract.

Usage (from the repo root):
    python verify_textures.py <vanilla_textures_dir> [model.ogf ...]

<vanilla_textures_dir> is the folder holding the extracted vanilla `textures`
tree (the one that contains `wood/`, `mtl/`, `act/`, ...). With no model
arguments it checks every .ogf under HomesteadHF/gamedata/meshes/dynamics.
Paths that exist in the mod's own gamedata are reported as 'own-mod'.
"""
import glob
import os
import struct
import sys

BS = chr(92)


def walk(b, off, end, out):
    while off + 8 <= end:
        cid, sz = struct.unpack_from('<II', b, off)
        cid &= 0x7fffffff
        d = off + 8
        if cid == 2:
            s = b[d:d + sz].split(b'\0')
            out.add((s[0].decode('latin1'), s[1].decode('latin1')))
        elif cid == 9:
            o = d
            while o + 8 <= d + sz:
                _, s2 = struct.unpack_from('<II', b, o)
                walk(b, o + 8, o + 8 + s2, out)
                o += 8 + s2
        off = d + sz


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vanilla = sys.argv[1].rstrip('/\\') + '/'
    files = sys.argv[2:] or glob.glob(
        'HomesteadHF/gamedata/meshes/dynamics/**/*.ogf', recursive=True)
    rows = {}
    for p in files:
        b = open(p, 'rb').read()
        s = set()
        walk(b, 0, len(b), s)
        for t, _shader in s:
            rows.setdefault(t.replace(BS, '/'), set()).add(os.path.basename(p))
    bad = []
    for t, models in sorted(rows.items()):
        if os.path.exists(vanilla + t + '.dds'):
            continue
        own = os.path.exists('HomesteadHF/gamedata/textures/' + t + '.dds')
        bad.append((t, 'own-mod' if own else 'NOT-IN-VANILLA', sorted(models)[:5]))
    print(len(rows), 'texture paths;', len(bad), 'not in the vanilla extract:')
    for row in bad:
        print(row)


if __name__ == '__main__':
    main()
