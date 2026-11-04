"""Hunter's Station: the small log lying on the floor shared the pelt sheet (hunter_pelts). Move it into two new sub-meshes
appended as the last children: its body to the pine bark of the rest of the station (bark wrapped round the log, mirrored so
no seam), its two end caps to wood_spil_1 (end grain as a round cut). Everything else is copied byte for byte; the pelt
sub-mesh only loses these triangles and its unused vertices, its bounding header is recomputed.

    python hunter_roll_to_bark.py in.ogf out.ogf

Run after hunter_aframe_to_plank.py and fix_hunter_pelts.py (the log is the 44-triangle closed component of the pelt sub-mesh
at x 1.18..1.66, y 0..0.18).
"""
import struct
import sys

import numpy as np

from hunter_aframe_to_plank import STRIDE, chunks, components, header, mesh_of, pack, put_mesh

BARK = r"lfo\lfo_trees\bark\trees_atp_pine_bark"
SPIL = r"wood\wood_spil_1"
BARK_U, BARK_V = 1 / 0.8, 1 / 0.5      # tiles per metre along the log / round it


def sub(template, tex, v, idx, fvf):
    cs = [[1, chunks(template, 0, len(template))[0][1]], [2, tex.encode() + b"\0" + rb"models\model" + b"\0"],
          [3, struct.pack("<II", fvf, len(v)) + v.astype("<f4").tobytes()],
          [4, struct.pack("<I", idx.size) + idx.astype("<u2").tobytes()]]
    return header(pack(cs), v)


def main(src, dst):
    b = open(src, "rb").read()
    top = chunks(b, 0, len(b))
    ki = next(i for i, (cid, _) in enumerate(top) if cid & 0x7fffffff == 9)
    kids = chunks(top[ki][1], 0, len(top[ki][1]))
    k = next(i for i, c in enumerate(kids) if mesh_of(c[1])[0] == r"homestead_hf\hunter_pelts")
    _, fvf, v, idx = mesh_of(kids[k][1])
    comps, vid = components(v, idx)
    logs = [tl for tl in comps if len(tl) == 44 and 1.1 < v[idx[tl].ravel(), 0].min() < 1.3]
    assert len(logs) == 1, len(logs)
    tl = logs[0]
    pos = v[:, :3]
    tt = idx[tl]
    vol = np.einsum("ij,ij->i", pos[tt[:, 0]], np.cross(pos[tt[:, 1]], pos[tt[:, 2]])).sum()
    cap_t, body_t = [], []
    for t in tt:
        n = np.cross(pos[t[1]] - pos[t[0]], pos[t[2]] - pos[t[0]])
        n /= np.linalg.norm(n)
        (cap_t if abs(n[0]) > 0.9 else body_t).append(t)
    cap_t, body_t = np.array(cap_t), np.array(body_t)
    assert not set(cap_t.ravel()) & set(body_t.ravel()), "caps share vertices with the body"
    print("log: %d cap tris, %d body tris, volume sign %+.3g" % (len(cap_t), len(body_t), vol))
    allp = pos[tt.ravel()]
    centre = (allp.min(0) + allp.max(0)) / 2
    x0, x1 = allp[:, 0].min(), allp[:, 0].max()
    rad = max(allp[:, 1].max() - allp[:, 1].min(), allp[:, 2].max() - allp[:, 2].min()) / 2

    def build(tris, uvfn):
        verts = np.unique(tris)
        rm = {int(o): i for i, o in enumerate(verts)}
        nv = v[verts].copy()
        if vol < 0:
            nv[:, 3:6] *= -1
            nv[:, 9:12] *= -1
        for r in nv:
            r[12], r[13] = uvfn(r[:3])
        ni = np.array([[rm[int(x)] for x in t] for t in tris])
        return nv, (ni[:, ::-1] if vol < 0 else ni)

    def bark_uv(p):
        ang = np.arctan2(p[2] - centre[2], p[1] - centre[1])
        return (p[0] - x0) * BARK_U, abs(ang) * rad * BARK_V

    def cap_uv(p):
        return 0.5 + (p[1] - centre[1]) / (2 * rad), 0.5 + (p[2] - centre[2]) / (2 * rad)

    bv, bi = build(body_t, bark_uv)
    cv, ci = build(cap_t, cap_uv)

    keep = np.array(sorted(set(range(len(idx))) - set(tl)))
    used = np.unique(idx[keep])
    rm = np.full(len(v), -1)
    rm[used] = np.arange(len(used))
    nvp = v[used]
    kids[k][1] = header(put_mesh(kids[k][1], fvf, nvp, rm[idx[keep]]), nvp)
    tmpl = kids[k][1]
    n0 = kids[-1][0]
    kids.append([n0 + 1, sub(tmpl, BARK, bv, bi, fvf)])
    kids.append([n0 + 2, sub(tmpl, SPIL, cv, ci, fvf)])
    top[ki][1] = pack(kids)
    open(dst, "wb").write(pack(top))
    print("pelt sub-mesh: %d -> %d tris; new bark %d tris, cap %d tris" % (len(idx), len(keep), len(bi), len(ci)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
