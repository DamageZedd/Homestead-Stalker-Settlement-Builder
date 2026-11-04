"""Hunter's Station pelt sub-mesh (homestead_hf\\hunter_pelts): two UV repairs, in place (only UV floats change).

    python fix_hunter_pelts.py hunter_station.ogf

1. The wolf pelt's back: the tail-tip vertex of 12 back triangles pointed at the tail strip far away on the pelt sheet
   (UV 0.891, 0.422), smearing the sheet across the middle of the flesh side. Its UV is re-derived from the neighbouring
   vertices of the same side (least-squares map from position to UV), so it joins the pale hide area like the rest.
2. The small roll lying on the floor: its body was five thin quads mapped to fur strips with black margins. The body is
   re-mapped round the roll (mirrored, so no seam) onto the orange hide area of the sheet, which matches its two orange
   end caps (the caps keep their UVs).
"""
import struct
import sys

import numpy as np

TAIL_STRIP_UV = (0.891, 0.422)
ORANGE = (0.045, 0.225, 0.255, 0.370)          # u0, u1, v0, v1 inside the big orange hide of the sheet


def sub_meshes(b):
    out = {}
    off = 0
    while off + 8 <= len(b):
        cid, sz = struct.unpack_from("<II", b, off)
        if cid & 0x7fffffff == 9:
            p, k = off + 8, 0
            while p + 8 <= off + 8 + sz:
                _, s2 = struct.unpack_from("<II", b, p)
                q, sub = p + 8, {}
                while q + 8 <= p + 8 + s2:
                    c, s3 = struct.unpack_from("<II", b, q)
                    sub[c & 0x7fffffff] = (q + 8, s3)
                    q += 8 + s3
                out[k] = sub
                p += 8 + s2
                k += 1
        off += 8 + sz
    return out


def main(path):
    b = bytearray(open(path, "rb").read())
    subs = sub_meshes(b)
    k = next(i for i, s in subs.items() if b[s[2][0]:s[2][0] + s[2][1]].split(b"\0")[0] == b"homestead_hf\\hunter_pelts")
    sub = subs[k]
    d, _ = sub[3]
    fvf, cnt = struct.unpack_from("<II", b, d)
    v = np.array(struct.unpack_from("<" + "f" * 15 * cnt, b, d + 8)).reshape(cnt, 15)
    d4, _ = sub[4]
    n, = struct.unpack_from("<I", b, d4)
    idx = np.array(struct.unpack_from("<%dH" % n, b, d4 + 4)).reshape(-1, 3)
    pos, uv = v[:, :3], v[:, 12:14]

    # 1. wolf pelt back
    bad = [i for i in range(cnt) if abs(uv[i, 0] - TAIL_STRIP_UV[0]) < 0.003 and abs(uv[i, 1] - TAIL_STRIP_UV[1]) < 0.003
           and 1.4 < pos[i, 0] < 2.3]
    fan = [t for t in idx if any(i in bad for i in t)]
    neigh = sorted({int(i) for t in fan for i in t if i not in bad})
    A = np.c_[pos[neigh], np.ones(len(neigh))]
    sol = np.linalg.lstsq(A, uv[neigh], rcond=None)[0]
    for i in bad:
        uv[i] = np.r_[pos[i], 1.0] @ sol
    print("pelt back: %d vertices re-derived (%d triangles), now at UV %s" % (len(bad), len(fan), np.round(uv[bad], 3).tolist()))

    # 2. roll
    roll = [t for t in idx if 1.17 < pos[t][:, 0].min() and pos[t][:, 0].max() < 1.67 and pos[t][:, 1].max() < 0.19 and pos[t][:, 2].min() > 0.18]
    cap_v, body_v = set(), set()
    for t in roll:
        nrm = np.cross(pos[t[1]] - pos[t[0]], pos[t[2]] - pos[t[0]])
        nrm /= np.linalg.norm(nrm)
        (cap_v if abs(nrm[0]) > 0.9 else body_v).update(int(i) for i in t)
    assert not cap_v & body_v, "caps and body share vertices"
    body = sorted(body_v)
    p = pos[body]
    centre = (p.min(0) + p.max(0)) / 2
    x0, x1 = p[:, 0].min(), p[:, 0].max()
    u0, u1, v0, v1 = ORANGE
    for i in body:
        ang = np.arctan2(pos[i, 2] - centre[2], pos[i, 1] - centre[1])
        uv[i, 0] = u0 + abs(ang) / np.pi * (u1 - u0)
        uv[i, 1] = v0 + (pos[i, 0] - x0) / (x1 - x0) * (v1 - v0)
    print("roll: %d body vertices re-mapped, %d cap vertices untouched" % (len(body), len(cap_v)))

    v[:, 12:14] = uv
    struct.pack_into("<" + "f" * v.size, b, d + 8, *v.ravel())
    open(path, "wb").write(bytes(b))


if __name__ == "__main__":
    main(sys.argv[1])
