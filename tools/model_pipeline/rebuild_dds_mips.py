"""Rebuild the mip levels (1 and up) of a DXT5 .dds from its level 0, keeping level 0 byte for byte.
For sheets whose PNG renders are gone: the art is not touched, only the smaller levels are made again with
dxt5_encode (box filter on premultiplied alpha, edge colour bleed, fitted endpoints).
usage: python -I rebuild_dds_mips.py in.dds out.dds"""
import os, struct, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dxt5_encode


def main(src, dst):
    d = open(src, "rb").read()
    assert d[:4] == b"DDS " and d[84:88] == b"DXT5", "DXT5 .dds expected"
    h, w = struct.unpack_from("<2I", d, 12)
    size0 = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 16
    level0 = d[128:128 + size0]
    chain = dxt5_encode.build_chain(dxt5_encode.decode_level(w, h, level0))
    out = bytearray(d[:128])
    struct.pack_into("<I", out, 28, len(chain))                  # mip count
    out += level0
    for lv in chain[1:]:
        out += dxt5_encode.encode_level(lv)
    with open(dst, "wb") as f:
        f.write(out)
    print(dst, w, h, "mips", len(chain))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
