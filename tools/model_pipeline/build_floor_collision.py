#!/usr/bin/env python3
"""Physics data for the building kit's floors, written directly into the .ogf files.
Run from the repo root after any Blender re-export of these models:
    python tools/model_pipeline/build_floor_collision.py

1. Adds a [collide] ignore_ragdoll user data chunk to every piece that stays solid, so corpses never
   touch or wake it (engine: ApplySpawnIniToPhysicShell reads the visual's LL_UserData).
2. Writes the invisible collider models spawned under foundations and floors by homestead_lock.script.
   A breakable_object has no physics body, only a box (the bone's size, centred on the object), so
   nothing can move it. The model has one zero-area triangle, so it draws nothing, and its bone shape
   is flagged not pickable, so bullets and the player's aim pass through it. No new textures: the
   chunk keeps the foundation's vanilla texture name.
"""
import struct
from pathlib import Path

DIR = Path("HomesteadHF/gamedata/meshes/dynamics/HomesteadHF/building")
OGF_HEADER, OGF_TEXTURE, OGF_VERTICES, OGF_INDICES, OGF_CHILDREN = 1, 2, 3, 4, 9
OGF_BONE_NAMES, OGF_IKDATA, OGF_USERDATA = 13, 16, 17
USERDATA = b"[collide]\r\nignore_ragdoll = true\r\n\0"
SOLID = ["hs_foundation", "hs_floor", "hs_foundation_triangle", "hs_floor_triangle", "hs_stairs_spiral_end"]
COLLIDERS = {"hs_collider_foundation": "hs_foundation", "hs_collider_floor": "hs_floor"}
FMT_1L = 0x12071980
VERT_1L = 60
SFNOPICKABLE = 1
IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)


def read_chunks(data):
    out, o = [], 0
    while o < len(data):
        cid, size = struct.unpack_from("<II", data, o)
        out.append((cid, data[o + 8:o + 8 + size]))
        o += 8 + size
    return out


def write_chunks(chunks):
    return b"".join(struct.pack("<II", cid, len(d)) + d for cid, d in chunks)


def get(chunks, cid):
    return next(d for i, d in chunks if i == cid)


def bone_shape(ik):
    """(offset of the shape, centre, half sizes on the model's x, y, z)"""
    o = ik.index(b"\0", 4) + 1
    r = struct.unpack_from("<9f", ik, o + 4)
    t = struct.unpack_from("<3f", ik, o + 4 + 36)
    h = struct.unpack_from("<3f", ik, o + 4 + 48)
    half = tuple(sum(abs(r[a * 3 + axis]) * h[a] for a in range(3)) for axis in range(3))
    return o, t, half


def header(template, half):
    version, kind, shader = struct.unpack_from("<BBH", template)
    radius = (half[0] ** 2 + half[1] ** 2 + half[2] ** 2) ** 0.5
    return struct.pack("<BBH6f4f", version, kind, shader, -half[0], -half[1], -half[2],
                       half[0], half[1], half[2], 0, 0, 0, radius)


def obb(half):
    return struct.pack("<15f", *IDENTITY, 0, 0, 0, *half)


def make_collider(source):
    chunks = read_chunks((DIR / (source + ".ogf")).read_bytes())
    ik = get(chunks, OGF_IKDATA)
    o, centre, half = bone_shape(ik)

    # the triangle is copied from the foundation's first child, which has the plain 1-link vertex format
    template = read_chunks((DIR / "hs_foundation.ogf").read_bytes())
    child = read_chunks(get(template, OGF_CHILDREN))[0][1]
    sub = read_chunks(child)
    verts = get(sub, OGF_VERTICES)
    fmt, _ = struct.unpack_from("<II", verts)
    assert fmt == FMT_1L
    vert = struct.pack("<3f", 0, 0, 0) + verts[8 + 12:8 + VERT_1L]
    new_child = write_chunks([
        (OGF_HEADER, header(get(sub, OGF_HEADER), half)),
        (OGF_TEXTURE, get(sub, OGF_TEXTURE)),
        (OGF_VERTICES, struct.pack("<II", FMT_1L, 3) + vert * 3),
        (OGF_INDICES, struct.pack("<I3H", 3, 0, 1, 2)),
    ])

    names = get(chunks, OGF_BONE_NAMES)
    new_ik = bytearray(ik)
    flags = struct.unpack_from("<H", ik, o + 2)[0] | SFNOPICKABLE
    struct.pack_into("<H", new_ik, o + 2, flags)
    new_ik[o + 4:o + 64] = obb(half)
    return write_chunks([
        (OGF_HEADER, header(get(chunks, OGF_HEADER), half)),
        (OGF_CHILDREN, write_chunks([(0, new_child)])),
        (OGF_BONE_NAMES, names[:-60] + obb(half)),
        (OGF_IKDATA, bytes(new_ik)),
    ]), centre


def main():
    for name, source in COLLIDERS.items():
        data, centre = make_collider(source)
        (DIR / (name + ".ogf")).write_bytes(data)
        print(f"{name}: {len(data)} bytes, homestead_collider_y = {centre[1]:.6f}")
    for name in SOLID:
        path = DIR / (name + ".ogf")
        chunks = [c for c in read_chunks(path.read_bytes()) if c[0] != OGF_USERDATA]
        chunks.append((OGF_USERDATA, USERDATA))
        path.write_bytes(write_chunks(chunks))
        print(f"{name}: ignore_ragdoll")


if __name__ == "__main__":
    main()
