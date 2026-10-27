"""PNG -> DXT1 .dds with a full mip chain, header laid out like the existing HomesteadHF atlases.
usage: python -I make_dds.py in.png out.dds"""
import io, struct, sys
from PIL import Image


def dxt1_blocks(img):
    """Pillow writes DXT1 without mips: encode one level and return its block data."""
    w, h = img.size
    pad = img
    if w < 4 or h < 4:   # a DXT block is 4x4: smaller mips are one padded block
        pad = img.resize((max(4, w), max(4, h)), Image.BOX)
    buf = io.BytesIO()
    pad.save(buf, format="DDS", pixel_format="DXT1")
    data = buf.getvalue()[128:]
    blocks = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 8
    return data[:blocks]


def main(src, dst):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    levels = []
    cur = im
    while True:
        levels.append(dxt1_blocks(cur))
        if cur.size == (1, 1):
            break
        cur = cur.resize((max(1, cur.size[0] // 2), max(1, cur.size[1] // 2)), Image.LANCZOS)
    hdr = bytearray(128)
    hdr[0:4] = b"DDS "
    struct.pack_into("<7I", hdr, 4, 124, 0xA1007, h, w, len(levels[0]), 0, len(levels))
    struct.pack_into("<2I4s", hdr, 76, 32, 0x4, b"DXT1")          # pixel format: FOURCC
    struct.pack_into("<I", hdr, 108, 0x401008)                    # caps: complex | texture | mipmap
    with open(dst, "wb") as f:
        f.write(hdr)
        for lv in levels:
            f.write(lv)
    print(dst, w, h, "mips", len(levels))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
