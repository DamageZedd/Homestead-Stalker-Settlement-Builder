"""In-place UV / face-orientation fixes on shipped .ogf files (sizes never change, so no chunk rewrite is needed).

    python fix_uv_orient.py floor  model.ogf [submesh_index ...]   # plank grain along the floor's Z axis, continuous across the tile
    python fix_uv_orient.py aframe hunter_station.ogf              # Hunter's Station A-frame: outward faces + unstretched bark UVs

floor : every vertex whose normal points up or down gets u = z * S, v = x * S (planks run along Z like the Hideout floors and
        the plank panels of hs_floor), one continuous mapping over the whole tile so there is no seam. With submesh
        indices only those submeshes are touched (hs_floor: submesh 0 was the wood_board_01 part, whose UVs ran across).
aframe: in the bark submesh, every closed 12-triangle box (the frame's legs, posts, braces and cross-beams) that is wound
        inside out gets its triangles and normals flipped, and all of them get box-mapped UVs (u along the beam, v around it)
        at BARK_S repeats per metre; the old UVs were stretched up to 16:1 along the legs.
"""
import struct
import sys

import numpy as np

HALF = 2.354475
FLOOR_S = 0.6
BARK_S = 1.5


def submeshes(b):
    """{index: (verts_offset, count, idx_offset, n_idx, texture)} for the OGF_CHILDREN submeshes."""
    out = {}

    def walk(off, end, parent9=False, i=None):
        while off + 8 <= end:
            cid, sz = struct.unpack_from("<II", b, off)
            c = cid & 0x7fffffff
            d = off + 8
            if c == 9:
                o, k = d, 0
                while o + 8 <= d + sz:
                    _, s2 = struct.unpack_from("<II", b, o)
                    walk(o + 8, o + 8 + s2, True, k)
                    o += 8 + s2
                    k += 1
            elif parent9:
                if c == 2:
                    out.setdefault(i, {})["tex"] = b[d:d + sz].split(b"\0")[0].decode()
                elif c == 3:
                    out.setdefault(i, {})["v"] = d
                elif c == 4:
                    out.setdefault(i, {})["i"] = d
            off = d + sz

    walk(0, len(b))
    return out


def load(b, sm):
    d = sm["v"]
    fvf, cnt = struct.unpack_from("<II", b, d)
    v = np.array(struct.unpack_from("<" + "f" * 15 * cnt, b, d + 8)).reshape(cnt, 15)
    n, = struct.unpack_from("<I", b, sm["i"])
    idx = np.array(struct.unpack_from("<%dH" % n, b, sm["i"] + 4)).reshape(-1, 3)
    return v, idx


def store(b, sm, v, idx):
    d = sm["v"]
    struct.pack_into("<" + "f" * v.size, b, d + 8, *v.ravel())
    struct.pack_into("<%dH" % idx.size, b, sm["i"] + 4, *idx.ravel())


def planar(p, nrm, long_axis, s):
    """u along long_axis projected into the face plane, v across it."""
    lp = long_axis - nrm * (nrm @ long_axis)
    if np.linalg.norm(lp) < 1e-4:
        lp = np.array([1.0, 0, 0]) - nrm * nrm[0]
        if np.linalg.norm(lp) < 1e-4:
            lp = np.array([0, 0, 1.0])
    lp /= np.linalg.norm(lp)
    return (p @ lp) * s, (p @ np.cross(nrm, lp)) * s


def fix_floor(b, only):
    for i, sm in submeshes(b).items():
        if only and i not in only:
            continue
        v, idx = load(b, sm)
        k = 0
        for r in v:
            if abs(r[4]) > 0.9:                       # normal Y: up or down
                r[12], r[13] = (r[2] + HALF) * FLOOR_S, (r[0] + HALF) * FLOOR_S
                k += 1
        store(b, sm, v, idx)
        print("  submesh", i, sm["tex"], k, "vertices re-mapped")


def components(v, idx):
    key = {}
    vid = np.array([key.setdefault(tuple(np.round(x, 4)), len(key)) for x in v[:, :3]])
    par = list(range(len(key)))

    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for t in idx:
        a, b_, c = vid[t]
        par[f(a)] = f(b_)
        par[f(b_)] = f(c)
    comp = {}
    for i, t in enumerate(idx):
        comp.setdefault(f(vid[t[0]]), []).append(i)
    return list(comp.values()), vid


def fix_aframe(b):
    for i, sm in submeshes(b).items():
        if not sm["tex"].endswith("trees_atp_pine_bark"):
            continue
        v, idx = load(b, sm)
        comps, vid = components(v, idx)
        flipped = mapped = 0
        for tl in comps:
            if len(tl) != 12:
                continue
            tt = idx[tl]
            edges = {}
            for t in tt:
                for j in range(3):
                    e = (vid[t[j]], vid[t[(j + 1) % 3]])
                    edges[e] = edges.get(e, 0) + 1
            if any((y, x) not in edges for (x, y) in edges):
                continue                                   # not a closed box
            pos = v[:, :3]
            a, b1, c = pos[tt[:, 0]], pos[tt[:, 1]], pos[tt[:, 2]]
            if np.einsum("ij,ij->i", a, np.cross(b1, c)).sum() < 0:
                idx[tl] = tt[:, [0, 2, 1]]
                verts = np.unique(tt)
                v[verts, 3:6] *= -1
                v[verts, 9:12] *= -1
                flipped += 1
            verts = np.unique(idx[tl])
            ext = pos[verts].max(0) - pos[verts].min(0)
            pts = pos[verts] - pos[verts].mean(0)
            long_axis = np.linalg.svd(pts)[2][0]
            for vi in verts:
                nrm = v[vi, 3:6] / np.linalg.norm(v[vi, 3:6])
                v[vi, 12], v[vi, 13] = planar(pos[vi], nrm, long_axis, BARK_S)
            mapped += 1
        store(b, sm, v, idx)
        print("  submesh", i, sm["tex"], mapped, "boxes mapped,", flipped, "turned outward")


if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    data = bytearray(open(path, "rb").read())
    print(path)
    if mode == "floor":
        fix_floor(data, {int(x) for x in sys.argv[3:]})
    elif mode == "aframe":
        fix_aframe(data)
    else:
        sys.exit(__doc__)
    open(path, "wb").write(bytes(data))
