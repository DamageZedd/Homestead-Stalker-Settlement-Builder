"""Regression: the HD icon mips (tools/model_pipeline/dxt5_encode.py) leave no saturated specks along alpha edges.
Pillow's LANCZOS + DXT5 writer does (the reason for the encoder); the box filter + fitted endpoints do not.
Run: python -I tools/tests/test_dxt5_encode.py   (from the repo root; needs Pillow and numpy)"""
import io, os, struct, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_pipeline"))
import dxt5_encode as E

fails = 0


def ok(cond, msg):
    global fails
    if not cond:
        fails += 1
        print("FAIL " + msg)


def specks(im, thresh=100):
    """alpha > 0 pixels with a saturated channel that differ by > thresh from the mean of their visible neighbours"""
    a = im[..., 3] > 0
    rgb = im[..., :3].astype(np.float32)
    h, w = a.shape
    pa, pr = np.pad(a, 1), np.pad(rgb, ((1, 1), (1, 1), (0, 0)))
    s, n = np.zeros_like(rgb), np.zeros((h, w), np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                m = pa[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
                s += pr[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] * m[..., None]
                n += m
    dev = np.abs(rgb - s / np.maximum(n, 1)[..., None]).max(-1)
    sat = ((im[..., :3] <= 10) | (im[..., :3] >= 245)).any(-1)
    return int((a & (n >= 3) & sat & (dev > thresh)).sum())


def pillow_chain(img, levels=2):
    """what make_dds.py did: LANCZOS mips, Pillow's DXT5 writer, read back"""
    out, cur = [], Image.fromarray(img)
    for _ in range(levels):
        cur = cur.resize((cur.size[0] // 2, cur.size[1] // 2), Image.LANCZOS)
        buf = io.BytesIO()
        cur.save(buf, format="DDS", pixel_format="DXT5")
        out.append(np.array(Image.open(io.BytesIO(buf.getvalue())).convert("RGBA")))
    return out


# an icon like the real ones: smooth shaded shapes with hard alpha edges on transparent black
img = np.zeros((256, 256, 4), np.uint8)
yy, xx = np.mgrid[0:256, 0:256]
shade = (60 + 140 * (xx / 255.0)).astype(np.uint8)
for (x0, y0, x1, y1, col) in ((20, 20, 120, 70, (1.0, 0.1, 0.1)), (30, 90, 200, 140, (0.1, 0.9, 0.2)),
                              (60, 160, 90, 240, (0.3, 0.3, 1.0)), (110, 150, 230, 235, (0.9, 0.8, 0.1))):
    for c in range(3):
        img[y0:y1, x0:x1, c] = (shade[y0:y1, x0:x1] * col[c]).astype(np.uint8)
    img[y0:y1, x0:x1, 3] = 255
disc = np.hypot(xx - 190, yy - 60) < 40
img[disc, :3] = (240, 240, 240)
img[disc, 3] = 255

mine = E.build_chain(img)
pil = pillow_chain(img)
for i in (1, 2):
    data = E.encode_level(mine[i])
    dec = E.decode_level(mine[i].shape[1], mine[i].shape[0], data)
    n_mine, n_pil = specks(dec), specks(pil[i - 1])
    ok(n_mine <= 2, "level %d: %d specks with the new pipeline (want <= 2)" % (i, n_mine))
    ok(n_pil > n_mine, "level %d: Pillow's chain has %d specks, the new one %d" % (i, n_pil, n_mine))
    vis = mine[i][..., 3] > 0
    err = np.abs(dec[..., :3].astype(int) - mine[i][..., :3].astype(int))[vis].mean()
    ok(err < 6.0, "level %d: mean abs error %.2f" % (i, err))

# the file is a valid DXT5 DDS for Pillow, and its decode agrees with ours
data = E.encode_level(img)
hdr = bytearray(128)
hdr[0:4] = b"DDS "
struct.pack_into("<7I", hdr, 4, 124, 0xA1007, 256, 256, len(data), 0, 1)
struct.pack_into("<2I4s", hdr, 76, 32, 0x4, b"DXT5")
struct.pack_into("<I", hdr, 108, 0x1000)
pil_dec = np.array(Image.open(io.BytesIO(bytes(hdr) + data)).convert("RGBA"))
ok(np.abs(pil_dec.astype(int) - E.decode_level(256, 256, data).astype(int)).max() <= 1, "Pillow decodes the data as the reference decoder does")

# mip chain shape and premultiplied box filter on a half transparent texel: colour is not darkened by the transparent half
chain = E.build_chain(np.array([[[200, 100, 50, 255], [0, 0, 0, 0]], [[200, 100, 50, 255], [0, 0, 0, 0]]], np.uint8))
ok(len(chain) == 2 and chain[1].shape == (1, 1, 4), "1x1 last level")
ok(tuple(chain[1][0, 0]) == (200, 100, 50, 128), "premultiplied box keeps the visible colour: %s" % (tuple(chain[1][0, 0]),))

print("dxt5 encode tests passed" if fails == 0 else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
