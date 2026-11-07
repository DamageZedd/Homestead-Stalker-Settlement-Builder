"""DXT5 (BC3) mip chain for RGBA icons, without external tools (numpy only).

Why not Pillow: Pillow's DXT5 writer picks block endpoints from the block's min/max, so the colour of the
transparent (0, 0, 0) pixels drags the endpoints and leaves saturated single-pixel specks along alpha edges,
and its LANCZOS mips overshoot (negative lobes, clamped to 0 / 255) at the same edges. Here:
  * mips are a 2x2 box filter on premultiplied alpha (no overshoot, no dark halo),
  * the colour of fully transparent pixels is bled in from the visible ones (a few pixels), so a block that
    straddles an edge is fitted to visible colour only and bilinear sampling does not pull in black,
  * block endpoints come from a weighted principal axis fit, then two least-squares refinements.
Public: build_chain(rgba_u8) -> list of RGBA levels, encode_level(rgba_u8) -> bytes, decode_level(w, h, bytes)."""
import numpy as np

BLEED = 4          # pixels the colour of the visible ones is carried into transparent ones


def _premul_box(rgba):
    """2x2 box filter on premultiplied alpha (sizes are powers of two; a 1 pixel side is repeated)."""
    h, w = rgba.shape[:2]
    if h == 1 and w == 1:
        return rgba.copy()
    nh, nw = max(1, h // 2), max(1, w // 2)
    f = rgba.astype(np.float64)
    a = f[..., 3:4]
    pm = np.concatenate([f[..., :3] * a / 255.0, a], -1)
    if h == 1:
        pm = np.repeat(pm, 2, 0)
    if w == 1:
        pm = np.repeat(pm, 2, 1)
    q = (pm[0:2 * nh:2, 0:2 * nw:2] + pm[1:2 * nh:2, 0:2 * nw:2] + pm[0:2 * nh:2, 1:2 * nw:2] + pm[1:2 * nh:2, 1:2 * nw:2]) / 4.0
    a2 = q[..., 3:4]
    rgb = np.where(a2 > 0, q[..., :3] * 255.0 / np.maximum(a2, 1e-9), 0.0)
    return np.clip(np.rint(np.concatenate([rgb, a2], -1)), 0, 255).astype(np.uint8)


def build_chain(rgba):
    levels = [rgba]
    while levels[-1].shape[0] > 1 or levels[-1].shape[1] > 1:
        levels.append(_premul_box(levels[-1]))
    return levels


def _bleed(rgba):
    """Colour of alpha == 0 pixels = average of the visible pixels near them (up to BLEED steps)."""
    rgb = rgba[..., :3].astype(np.float32)
    known = rgba[..., 3] > 0
    if known.all() or not known.any():
        return rgb, known
    rgb = rgb * known[..., None]
    k = known.astype(np.float32)
    h, w = k.shape
    for _ in range(BLEED):
        pr = np.pad(rgb * k[..., None], ((1, 1), (1, 1), (0, 0)))
        pk = np.pad(k, 1)
        s = np.zeros_like(rgb)
        n = np.zeros_like(k)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                s += pr[dy:dy + h, dx:dx + w]
                n += pk[dy:dy + h, dx:dx + w]
        fill = (k == 0) & (n > 0)
        rgb = np.where(fill[..., None], s / np.maximum(n, 1)[..., None], rgb)
        k = np.where(fill, 1.0, k)
    return rgb, known


def _expand565(c):
    r, g, b = (c >> 11) & 31, (c >> 5) & 63, c & 31
    return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)], -1).astype(np.float32)


def _quant565(rgb):
    r = np.clip(np.rint(rgb[..., 0] * 31 / 255), 0, 31).astype(np.int32)
    g = np.clip(np.rint(rgb[..., 1] * 63 / 255), 0, 63).astype(np.int32)
    b = np.clip(np.rint(rgb[..., 2] * 31 / 255), 0, 31).astype(np.int32)
    return (r << 11) | (g << 5) | b


def _palette(c0, c1):
    e0, e1 = _expand565(c0), _expand565(c1)
    return np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], -2)       # (..., 4, 3): c0, c1, 2/3 c0, 1/3 c0


_POS = np.array([0.0, 1.0, 1 / 3.0, 2 / 3.0], np.float32)   # weight of c1 in each palette index


def _fit_block_colours(px, w):
    """px (nb, 16, 3), w (nb, 16) -> 565 endpoints from a weighted principal axis."""
    ws = w.sum(-1, keepdims=True)
    mean = (px * w[..., None]).sum(1) / np.maximum(ws, 1e-6)
    d = px - mean[:, None, :]
    cov = np.einsum('bpi,bpj,bp->bij', d, d, w)
    v = np.tile(np.array([1.0, 1.1, 1.2], np.float32), (px.shape[0], 1))
    for _ in range(8):
        v = np.einsum('bij,bj->bi', cov, v)
        v /= np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)
    t = np.einsum('bpi,bi->bp', d, v)
    big = np.float32(1e9)
    tmin = np.where(w > 0, t, big).min(-1)
    tmax = np.where(w > 0, t, -big).max(-1)
    inset = (tmax - tmin) / 16.0                                              # pull the endpoints in a little
    lo = mean + v * (tmin + inset)[:, None]
    hi = mean + v * (tmax - inset)[:, None]
    return _quant565(hi), _quant565(lo)


def _refine(px, w, idx, c0, c1):
    """Least squares endpoints for the current indices (per channel, weighted)."""
    b = _POS[idx]
    a = 1 - b
    aa = (w * a * a).sum(-1)
    bb = (w * b * b).sum(-1)
    ab = (w * a * b).sum(-1)
    det = aa * bb - ab * ab
    ok = det > 1e-6
    ax = (w[..., None] * a[..., None] * px).sum(1)
    bx = (w[..., None] * b[..., None] * px).sum(1)
    d = np.where(ok, det, 1.0)[:, None]
    e0 = (bb[:, None] * ax - ab[:, None] * bx) / d
    e1 = (aa[:, None] * bx - ab[:, None] * ax) / d
    return (_quant565(np.where(ok[:, None], e0, _expand565(c0))),
            _quant565(np.where(ok[:, None], e1, _expand565(c1))))


def _assign(px, w, c0, c1):
    pal = _palette(c0, c1)
    d = ((px[:, :, None, :] - pal[:, None, :, :]) ** 2).sum(-1)               # (nb, 16, 4)
    idx = np.argmin(d, -1)
    err = (w * np.take_along_axis(d, idx[..., None], -1)[..., 0]).sum(-1)
    return idx, err


def encode_level(rgba):
    h, w = rgba.shape[:2]
    bw, bh = max(1, (w + 3) // 4), max(1, (h + 3) // 4)
    ph, pw = bh * 4, bw * 4
    if (ph, pw) != (h, w):
        rgba = np.pad(rgba, ((0, ph - h), (0, pw - w), (0, 0)), mode='edge')
    rgb, known = _bleed(rgba)
    wt = np.where(known, 1.0, 0.1).astype(np.float32)

    def blocks(a):
        return a.reshape(bh, 4, bw, 4, *a.shape[2:]).swapaxes(1, 2).reshape(bh * bw, 16, *a.shape[2:])
    px, wb, al = blocks(rgb), blocks(wt), blocks(rgba[..., 3]).astype(np.int32)

    c0, c1 = _fit_block_colours(px, wb)
    best = None
    for it in range(3):
        c0, c1 = np.maximum(c0, c1), np.minimum(c0, c1)
        idx, err = _assign(px, wb, c0, c1)
        if best is None:
            best = [c0, c1, idx, err]
        else:
            better = err < best[3]
            best = [np.where(better, c0, best[0]), np.where(better, c1, best[1]),
                    np.where(better[:, None], idx, best[2]), np.where(better, err, best[3])]
        if it < 2:
            c0, c1 = _refine(px, wb, idx, c0, c1)
    c0, c1, idx = best[0], best[1], best[2]
    # c0 > c1 selects the four colour mode; equal endpoints are nudged apart (and the indices follow)
    same = c0 == c1
    if same.any():
        c0 = np.where(same & (c0 < 0xFFFF), c0 + 1, c0)
        c1 = np.where(same & (c0 == c1), c1 - 1, c1)
        idx, _ = _assign(px, wb, c0, c1)

    # alpha: a0 > a1 selects the 8 value mode; a flat block (a0 == a1) is read as the 6 value mode, and
    # index 0 gives a0 in both
    a0, a1 = al.max(-1), al.min(-1)
    apal = np.zeros((a0.shape[0], 8), np.int32)
    apal[:, 0], apal[:, 1] = a0, a1
    for i in range(1, 7):
        apal[:, i + 1] = ((7 - i) * a0 + i * a1) // 7
    aidx = np.argmin(np.abs(al[..., None] - apal[:, None, :]), -1)

    out = np.zeros((bh * bw, 16), np.uint8)
    out[:, 0], out[:, 1] = a0, a1
    abits = np.zeros(a0.shape[0], np.uint64)
    for i in range(16):
        abits |= aidx[:, i].astype(np.uint64) << np.uint64(3 * i)
    for i in range(6):
        out[:, 2 + i] = ((abits >> np.uint64(8 * i)) & np.uint64(0xFF)).astype(np.uint8)
    out[:, 8], out[:, 9] = c0 & 0xFF, c0 >> 8
    out[:, 10], out[:, 11] = c1 & 0xFF, c1 >> 8
    cbits = np.zeros(a0.shape[0], np.uint32)
    for i in range(16):
        cbits |= idx[:, i].astype(np.uint32) << np.uint32(2 * i)
    for i in range(4):
        out[:, 12 + i] = ((cbits >> np.uint32(8 * i)) & np.uint32(0xFF)).astype(np.uint8)
    return out.tobytes()


def decode_level(w, h, data):
    """Reference decoder (four colour mode, bit replicated 565) used by the tests."""
    bw, bh = max(1, (w + 3) // 4), max(1, (h + 3) // 4)
    b = np.frombuffer(data, dtype=np.uint8).reshape(bh * bw, 16).astype(np.int32)
    a0, a1 = b[:, 0], b[:, 1]
    abits = np.zeros(bh * bw, np.uint64)
    for i in range(6):
        abits |= b[:, 2 + i].astype(np.uint64) << np.uint64(8 * i)
    aidx = np.stack([(abits >> np.uint64(3 * i)) & np.uint64(7) for i in range(16)], -1).astype(np.int32)
    pal = np.zeros((bh * bw, 8), np.int32)
    pal[:, 0], pal[:, 1] = a0, a1
    big = a0 > a1
    for i in range(1, 7):
        pal[:, i + 1] = np.where(big, ((7 - i) * a0 + i * a1) // 7, ((6 - i) * a0 + i * a1) // 5 if i <= 4 else 0)
    pal[:, 7] = np.where(big, pal[:, 7], 255)
    alpha = np.take_along_axis(pal, aidx, 1)
    c0 = b[:, 8] | (b[:, 9] << 8)
    c1 = b[:, 10] | (b[:, 11] << 8)
    cp = _palette(c0, c1)
    cbits = b[:, 12] | (b[:, 13] << 8) | (b[:, 14] << 16) | (b[:, 15] << 24)
    cidx = np.stack([(cbits >> (2 * i)) & 3 for i in range(16)], -1)
    col = np.take_along_axis(cp, cidx[..., None].repeat(3, -1), 1)
    img = np.zeros((bh * bw, 16, 4), np.uint8)
    img[..., :3] = np.clip(np.rint(col), 0, 255)
    img[..., 3] = alpha
    img = img.reshape(bh, bw, 4, 4, 4).transpose(0, 2, 1, 3, 4).reshape(bh * 4, bw * 4, 4)
    return img[:h, :w]
