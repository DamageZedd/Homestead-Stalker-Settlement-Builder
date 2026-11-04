r"""Points every wood\wood_board_01 texture reference in the given .ogf files at wood\wood_plank6_bar_b (the texture the
Hideout Furniture walls use for their big faces). GAMMA texture packs (Project I.N.V.E.R.N.O) repaint wood_board_01 as
high-contrast white peeling paint, so big board surfaces looked blotchy. Rewrites the OGF_TEXTURE chunk and fixes the
sizes of the chunks around it.

    python retex_board_to_plank.py model.ogf [...]
"""
import struct
import sys

OLD, NEW = b"wood\\wood_board_01\0", b"wood\\wood_plank6_bar_b\0"


def rewrite(b, off, end, children=False):
    """Returns the bytes of the chunk run b[off:end] with the texture string replaced."""
    out = bytearray()
    while off + 8 <= end:
        cid, sz = struct.unpack_from("<II", b, off)
        c = cid & 0x7fffffff
        d = off + 8
        data = b[d:d + sz]
        if c == 2 and data.startswith(OLD):
            data = NEW + data[len(OLD):]
        elif c == 9 and not children:        # OGF_CHILDREN; inside it, 9 is just the tenth sub-mesh
            data = bytes(rewrite(b, d, d + sz, True))
        elif children:                       # the numbered sub-meshes inside OGF_CHILDREN
            data = bytes(rewrite(b, d, d + sz))
        out += struct.pack("<II", cid, len(data)) + data
        off = d + sz
    return out


for p in sys.argv[1:]:
    b = open(p, "rb").read()
    n = b.count(OLD)
    r = bytes(rewrite(b, 0, len(b)))
    open(p, "wb").write(r)
    print(p, n, "reference(s) switched")
