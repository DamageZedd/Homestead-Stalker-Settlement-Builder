r"""Points texture references in the given .ogf files at wood\wood_plank6_bar_b (the texture the Hideout Furniture walls
use for their big faces). By default it replaces wood\wood_board_01: GAMMA texture packs (Project I.N.V.E.R.N.O) repaint
that texture as high-contrast white peeling paint, so big board surfaces looked blotchy. With --bark it replaces the pine
bark of the Hunter's Station A-frame instead. Rewrites the OGF_TEXTURE chunk and fixes the sizes of the chunks around it.

    python retex_board_to_plank.py [--bark] model.ogf [...]
"""
import struct
import sys

OLD, NEW = b"wood\\wood_board_01\0", b"wood\\wood_plank6_bar_b\0"
BARK = b"lfo\\lfo_trees\\bark\\trees_atp_pine_bark\0"


def rewrite(b, old, off, end):
    """Returns the bytes of the chunk run b[off:end] with the texture string replaced."""
    out = bytearray()
    while off + 8 <= end:
        cid, sz = struct.unpack_from("<II", b, off)
        d = off + 8
        data = b[d:d + sz]
        if cid & 0x7fffffff == 2 and data.startswith(old):
            data = NEW + data[len(old):]
        elif cid & 0x7fffffff == 9:
            data = bytes(children(b, old, d, d + sz))
        out += struct.pack("<II", cid, len(data)) + data
        off = d + sz
    return out


def children(b, old, off, end):
    """OGF_CHILDREN: numbered wrappers (index, size), each holding the sub-mesh's own chunks. The index is not a chunk id."""
    out = bytearray()
    while off + 8 <= end:
        idx, sz = struct.unpack_from("<II", b, off)
        data = bytes(rewrite(b, old, off + 8, off + 8 + sz))
        out += struct.pack("<II", idx, len(data)) + data
        off += 8 + sz
    return out


args = sys.argv[1:]
old = OLD
if args and args[0] == "--bark":
    old = BARK
    args = args[1:]
for p in args:
    b = open(p, "rb").read()
    n = b.count(old)
    r = bytes(rewrite(b, old, 0, len(b)))
    open(p, "wb").write(r)
    print(p, n, "reference(s) switched")
