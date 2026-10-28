# usage: python -I make_flag_zombied.py flag_stalker.png flag_zombied.png  (flag_stalker: vanilla prop\flag_stalker.dds)
# Derive the zombified banner from the vanilla loner patch, the way the game's own
# ui_new_game_flair_zombied is the loner trefoil bleached and rotted.
import sys, numpy as np
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(1986)
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255.0
H, W, _ = im.shape

def noise(scale, octaves=4):
    acc = np.zeros((H, W), np.float32); amp = 1.0; tot = 0.0
    for o in range(octaves):
        s = max(2, int(scale / (2 ** o)))
        g = rng.random((H // s + 2, W // s + 2)).astype(np.float32)
        g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
        acc += g * amp; tot += amp; amp *= 0.5
    return acc / tot

lum = im @ np.array([0.299, 0.587, 0.114], np.float32)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
# thread mask: the yellow embroidery (warm, bright)
yellow = np.clip((r - b - 0.12) * 5.0, 0, 1) * np.clip((lum - 0.25) * 4, 0, 1)

blot = noise(220)
# bleached bone thread, unevenly: some patches sickly ochre, most chalky grey-white
bone = np.stack([0.80, 0.78, 0.70]) * (0.75 + 0.45 * lum[..., None])
ochre = np.stack([0.62, 0.55, 0.32]) * (0.75 + 0.45 * lum[..., None])
mixk = np.clip((blot - 0.45) * 3, 0, 1)[..., None]
thread = bone * (1 - mixk) + ochre * mixk
# cold blue-grey for the dark fabric
grey = lum[..., None] * np.array([0.92, 0.98, 1.12]) * 1.05
out_im = grey * (1 - yellow[..., None]) + thread * yellow[..., None]

# grime: dark blotches, rust-brown stains, greenish mould at the edges
grime = np.clip((noise(160) - 0.5) * 2.5, 0, 1)
out_im *= (1 - 0.45 * grime[..., None])
stain = np.clip((noise(300) - 0.58) * 4, 0, 1)[..., None]
out_im = out_im * (1 - 0.5 * stain) + np.array([0.24, 0.16, 0.10]) * 0.5 * stain
yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
edge = np.clip(1 - np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy)) * 6, 0, 1)
mould = np.clip((noise(90) - 0.5) * 3, 0, 1) * edge
out_im = out_im * (1 - 0.4 * mould[..., None]) + np.array([0.20, 0.24, 0.14]) * 0.4 * mould[..., None]


# blood: dried spatter, soaked into the cloth. A big splat with droplets thrown off it,
# a hand smear, and runs dripping down from the top of the banner.
blood = np.zeros((H, W), np.float32)
def splat(cx, cy, rad, n_drops, spread, rough=0.6):
    global blood
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad + (noise(18, 3) - 0.5) * rough
    blood = np.maximum(blood, np.clip((1.0 - d) * 6, 0, 1))
    for _ in range(n_drops):
        ang = rng.uniform(0, 2 * np.pi); dist = rad * rng.uniform(1.1, spread)
        dx, dy = cx + np.cos(ang) * dist, cy + np.sin(ang) * dist
        dr = rad * rng.uniform(0.04, 0.16) * (1.4 - (dist / (rad * spread)))
        dd = np.sqrt(((xx - dx) / 1.0) ** 2 + (yy - dy) ** 2) / max(dr, 0.002)
        blood = np.maximum(blood, np.clip((1.0 - dd) * 5, 0, 1))
splat(0.56, 0.28, 0.065, 80, 3.4, 0.9)
splat(0.27, 0.55, 0.045, 45, 3.0, 0.8)
splat(0.74, 0.62, 0.028, 25, 2.6)
# runs: thin drips falling from the big splat and the top hem
for x0, y0, length in [(0.54, 0.33, 0.14), (0.59, 0.33, 0.22), (0.51, 0.32, 0.08), (0.28, 0.59, 0.16), (0.20, 0.02, 0.18), (0.24, 0.02, 0.10)]:
    wob = (noise(60, 2) - 0.5) * 0.012
    w = 0.006 * (1 - np.clip((yy - y0) / length, 0, 1)) + 0.002
    run = np.clip(1 - np.abs(xx - x0 - wob) / w, 0, 1) * ((yy > y0) & (yy < y0 + length))
    tip = np.clip(1 - np.sqrt((xx - x0) ** 2 + (yy - y0 - length) ** 2) / 0.008, 0, 1)
    blood = np.maximum(blood, np.clip(np.maximum(run, tip) * 4, 0, 1))
# smear: a dragged hand print across the lower left of the trefoil
sm = np.clip(1 - np.abs((yy - 0.74) - (xx - 0.30) * 0.35) / 0.03, 0, 1) * np.clip(1 - np.abs(xx - 0.42) / 0.16, 0, 1)
blood = np.maximum(blood, sm * np.clip((noise(10, 3) - 0.15) * 3, 0, 1))
# soak-in: cloth texture breaks the stain up; dried brown at the edges, darker wine red inside
blood *= np.clip(0.55 + (noise(6, 2) - 0.5) * 1.2 + lum * 0.6, 0, 1)
inner = np.clip(blood * 1.3 - 0.3, 0, 1)[..., None]
col = np.array([0.20, 0.07, 0.04]) * (1 - inner) + np.array([0.26, 0.035, 0.03]) * inner
bl = blood[..., None] * 0.9
out_im = out_im * (1 - bl) + (col * (0.55 + 0.6 * lum[..., None])) * bl

# a few frayed burn holes: scorched rim, almost-black backing showing through
holes = np.zeros((H, W), np.float32)
for cx, cy, rad in [(0.80, 0.22, 0.045), (0.18, 0.80, 0.035), (0.62, 0.86, 0.025), (0.30, 0.27, 0.02)]:
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad + (noise(14, 3) - 0.5) * 1.1
    holes = np.maximum(holes, np.clip(1.6 - d, 0, 1))
burn = np.clip(holes * 2.2, 0, 1)[..., None]
core = np.clip((holes - 0.45) * 12, 0, 1)[..., None]
out_im = out_im * (1 - 0.7 * burn) + np.array([0.16, 0.09, 0.04]) * 0.7 * burn
out_im = out_im * (1 - core) + np.array([0.035, 0.035, 0.03]) * core

out_im = np.clip(out_im, 0, 1)
Image.fromarray((out_im * 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(1.2, 40, 2)).save(out)
