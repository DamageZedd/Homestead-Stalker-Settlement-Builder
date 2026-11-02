"""PNG -> DXT1 .dds with a full mip chain, header laid out like the existing HomesteadHF atlases.
usage: python -I make_dds.py in.png out.dds"""
import io, struct, sys
from PIL import Image


def dxt_blocks(img, fmt="DXT1"):
    """Pillow writes DXT without mips: encode one level and return its block data."""
    w, h = img.size
    pad = img
    if w < 4 or h < 4:   # a DXT block is 4x4: smaller mips are one padded block
        pad = img.resize((max(4, w), max(4, h)), Image.BOX)
    buf = io.BytesIO()
    pad.save(buf, format="DDS", pixel_format=fmt)
    data = buf.getvalue()[128:]
    blocks = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * (8 if fmt == "DXT1" else 16)
    return data[:blocks]


def main(src, dst, fmt="DXT1"):
    """fmt DXT1 for opaque textures, DXT5 when the PNG carries an alpha channel."""
    im = Image.open(src).convert("RGB" if fmt == "DXT1" else "RGBA")
    w, h = im.size
    levels = []
    cur = im
    while True:
        levels.append(dxt_blocks(cur, fmt))
        if cur.size == (1, 1):
            break
        cur = cur.resize((max(1, cur.size[0] // 2), max(1, cur.size[1] // 2)), Image.LANCZOS)
    hdr = bytearray(128)
    hdr[0:4] = b"DDS "
    struct.pack_into("<7I", hdr, 4, 124, 0xA1007, h, w, len(levels[0]), 0, len(levels))
    struct.pack_into("<2I4s", hdr, 76, 32, 0x4, fmt.encode())     # pixel format: FOURCC
    struct.pack_into("<I", hdr, 108, 0x401008)                    # caps: complex | texture | mipmap
    with open(dst, "wb") as f:
        f.write(hdr)
        for lv in levels:
            f.write(lv)
    print(dst, w, h, "mips", len(levels))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "DXT1")
