"""Hunter's Station: move ONLY the middle A-frame's beams from the pine-bark sub-mesh into a new wood_plank6_bar_b sub-mesh
(appended as the last child), with plank UVs (grain along each beam) and outward-facing triangles. Everything else in the file is copied byte for byte.

    python hunter_aframe_to_plank.py original_hunter_station.ogf out.ogf

The A-frame beams are the closed 12-triangle boxes of the bark sub-mesh that are either more than 0.85 m off the centre
line (legs, skids, cross rails) or reach above 1.5 m (top beam, diagonal braces). The small posts and slats on the
platform, the side racks and the pegs keep their bark.
The bark sub-mesh loses those triangles; its bounding header is recomputed. No other sub-mesh or chunk is touched.
"""
import struct
import sys

import numpy as np

STRIDE = 60
PLANK_S = 0.6


def chunks(b, off, end):
    out = []
    while off + 8 <= end:
        cid, sz = struct.unpack_from("<II", b, off)
        out.append([cid, b[off + 8:off + 8 + sz]])
        off += 8 + sz
    assert off == end
    return out


def pack(cs):
    return b"".join(struct.pack("<II", cid, len(d)) + d for cid, d in cs)


def mesh_of(sub):
    ch = {c: d for c, d in chunks(sub, 0, len(sub))}
    tex = ch[2].split(b"\0")[0].decode()
    fvf, cnt = struct.unpack_from("<II", ch[3])
    v = np.frombuffer(ch[3][8:], dtype="<f4").reshape(cnt, STRIDE // 4).astype(np.float64)
    n, = struct.unpack_from("<I", ch[4])
    idx = np.frombuffer(ch[4][4:4 + 2 * n], dtype="<u2").reshape(-1, 3).astype(np.int64)
    return tex, fvf, v, idx


def put_mesh(sub, fvf, v, idx):
    cs = chunks(sub, 0, len(sub))
    for c in cs:
        if c[0] == 3:
            c[1] = struct.pack("<II", fvf, len(v)) + v.astype("<f4").tobytes()
        elif c[0] == 4:
            c[1] = struct.pack("<I", idx.size) + idx.astype("<u2").tobytes()
    return pack(cs)


def header(sub, v):
    """Rewrites the sub-mesh's OGF_HEADER bounding box and sphere for vertices v (version, type and shader id kept)."""
    cs = chunks(sub, 0, len(sub))
    h = bytearray(cs[0][1])
    p = v[:, :3]
    lo, hi = p.min(0), p.max(0)
    c = (lo + hi) / 2
    r = np.linalg.norm(p - c, axis=1).max()
    struct.pack_into("<6f3ff", h, 4, *lo, *hi, *c, r)
    cs[0][1] = bytes(h)
    return pack(cs)


def header(sub, v):
    """Rewrites the sub-mesh's OGF_HEADER bounding box and sphere for vertices v (version, type and shader id kept)."""
    cs = chunks(sub, 0, len(sub))
    h = bytearray(cs[0][1])
    p = v[:, :3]
    lo, hi = p.min(0), p.max(0)
    c = (lo + hi) / 2
    r = np.linalg.norm(p - c, axis=1).max()
    struct.pack_into("<10f", h, 4, *lo, *hi, *c, r)
    cs[0][1] = bytes(h)
    return pack(cs)


def components(v, idx):
    key, vid = {}, np.array([0] * len(v))
    vid = np.array([key.setdefault(tuple(np.round(x, 4)), len(key)) for x in v[:, :3]])
    par = list(range(len(key)))

    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for t in idx:
        a, b, c = vid[t]
        par[f(a)] = f(b)
        par[f(b)] = f(c)
    comp = {}
    for i, t in enumerate(idx):
        comp.setdefault(f(vid[t[0]]), []).append(i)
    return list(comp.values()), vid


def is_aframe_box(v, idx, vid, tl):
    if len(tl) != 12:
        return False
    tt = idx[tl]
    edges = set()
    for t in tt:
        for j in range(3):
            edges.add((vid[t[j]], vid[t[(j + 1) % 3]]))
    if any((y, x) not in edges for (x, y) in edges):
        return False                                   # not a closed box
    p = v[np.unique(tt), :3]
    return abs(p[:, 0]).min() > 0.85 or p[:, 1].max() > 1.5


def plank_uv(p, nrm, long_axis):
    lp = long_axis - nrm * (nrm @ long_axis)
    if np.linalg.norm(lp) < 1e-4:
        lp = np.array([1.0, 0, 0]) - nrm * nrm[0]
        if np.linalg.norm(lp) < 1e-4:
            lp = np.array([0, 0, 1.0])
    lp /= np.linalg.norm(lp)
    return (p @ lp) * PLANK_S, (p @ np.cross(nrm, lp)) * PLANK_S


def main(src, dst):
    b = open(src, "rb").read()
    top = chunks(b, 0, len(b))
    kids_i = next(i for i, (cid, _) in enumerate(top) if cid & 0x7fffffff == 9)
    kids = chunks(top[kids_i][1], 0, len(top[kids_i][1]))          # (index, sub-mesh bytes)
    tex = [mesh_of(k[1])[0] for k in kids]
    bark = tex.index("lfo\\lfo_trees\\bark\\trees_atp_pine_bark")
    _, fvf_b, vb, ib = mesh_of(kids[bark][1])
    assert vb.shape[1] == STRIDE // 4
    vp, ip = np.zeros((0, STRIDE // 4)), np.zeros((0, 3), dtype=np.int64)

    comps, vid = components(vb, ib)
    move = [tl for tl in comps if is_aframe_box(vb, ib, vid, tl)]
    print("A-frame boxes moved to the plank sub-mesh:", len(move))
    moved_tris = sorted(t for tl in move for t in tl)
    keep_tris = np.array(sorted(set(range(len(ib))) - set(moved_tris)))

    # new plank vertices / indices (appended)
    add_v, add_i = [], []
    for tl in move:
        tt = ib[tl]
        pos = vb[:, :3]
        vol = np.einsum("ij,ij->i", pos[tt[:, 0]], np.cross(pos[tt[:, 1]], pos[tt[:, 2]])).sum()
        verts = np.unique(tt)
        remap = {int(o): len(vp) + len(add_v) + k for k, o in enumerate(verts)}
        pts = pos[verts] - pos[verts].mean(0)
        long_axis = np.linalg.svd(pts)[2][0]
        nv = vb[verts].copy()
        if vol < 0:                                       # inside out: flip normals and binormals, swap winding
            nv[:, 3:6] *= -1
            nv[:, 9:12] *= -1
        for r in nv:
            nrm = r[3:6] / np.linalg.norm(r[3:6])
            r[12], r[13] = plank_uv(r[:3], nrm, long_axis)
        add_v.extend(nv)
        for t in tt:
            tri = [remap[int(x)] for x in t]
            add_i.append(tri[::-1] if vol < 0 else tri)
        if vol < 0:
            print("  turned a box outward")
    new_vp = np.vstack([vp, np.array(add_v)])
    new_ip = np.vstack([ip, np.array(add_i)])
    assert new_vp.shape[0] < 65536

    # bark sub-mesh without the moved triangles (unused vertices dropped, order kept)
    used = np.unique(ib[keep_tris])
    remap = np.full(len(vb), -1)
    remap[used] = np.arange(len(used))
    new_vb = vb[used]
    new_ib = remap[ib[keep_tris]]

    kids[bark][1] = header(put_mesh(kids[bark][1], fvf_b, new_vb, new_ib), new_vb)
    new_sub = [[1, b""], [2, b"wood\\wood_plank6_bar_b\x00models\\model\x00"],
               [3, struct.pack("<II", fvf_b, len(new_vp)) + new_vp.astype("<f4").tobytes()],
               [4, struct.pack("<I", new_ip.size) + new_ip.astype("<u2").tobytes()]]
    new_sub[0][1] = chunks(kids[bark][1], 0, len(kids[bark][1]))[0][1]          # same header, bounds fixed below
    kids.append([kids[-1][0] + 1, header(pack(new_sub), new_vp)])
    top[kids_i][1] = pack(kids)
    open(dst, "wb").write(pack(top))
    print("bark sub-mesh %d: %d -> %d tris, %d -> %d verts; new plank sub-mesh %d: %d tris, %d verts" % (
        bark, len(ib), len(new_ib), len(vb), len(new_vb), kids[-1][0], len(new_ip), len(new_vp)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
