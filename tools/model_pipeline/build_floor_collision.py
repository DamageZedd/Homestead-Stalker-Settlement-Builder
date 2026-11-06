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
   The standing box comes from the bone's obb only. The bone shape and mass are used only by the loose shell
   of a collider that broke, so they are a small light box: at the source's 2000 kg (x10 when broken) with
   the box's size, a broken foundation was a 20 t slab half inside the ground, thrown out by depenetration.
3. Triangles need several boxes: a collider is one box, so each triangle gets TRI_STRIPS colliders, stepped
   strips parallel to one leg (see triangle_strips). Strip k is as wide as the triangle at its top edge, so
   no box leaves the visible piece; the strips cover TRI_STRIPS / (TRI_STRIPS + 1) of its area (8: 88.9 %).
   The ltx lines that place them are printed (homestead_collider_1..N in items_homestead_building.ltx).
"""
import struct
from pathlib import Path

DIR = Path("HomesteadHF/gamedata/meshes/dynamics/HomesteadHF/building")
OGF_HEADER, OGF_TEXTURE, OGF_VERTICES, OGF_INDICES, OGF_CHILDREN = 1, 2, 3, 4, 9
OGF_BONE_NAMES, OGF_IKDATA, OGF_USERDATA = 13, 16, 17
USERDATA = b"[collide]\r\nignore_ragdoll = true\r\n\0"
SOLID = ["hs_foundation", "hs_floor", "hs_foundation_triangle", "hs_floor_triangle", "hs_stairs_spiral_end"]
# Square pieces: name -> (source .ogf, explicit collider centre, explicit collider half sizes).
# hs_foundation's own dynamic bone shape is restricted to the 0.40 m deck above ground (y = 0.005..0.395, matching
# hs_foundation_triangle) so its dynamic ODE body never overlaps terrain below y = 0, while hs_collider_foundation
# (the static breakable_object collider with no physics body) covers the full -0.995..0.395 height including the skirt.
COLLIDERS = {
    "hs_collider_foundation": ("hs_foundation", (0.0, -0.3, 0.0), (2.349, 0.695, 2.349)),
    "hs_collider_floor": ("hs_floor", None, None),
}
FOUNDATION_DECK_SHAPE = ((0.0, 0.20, 0.0), (2.349, 2.349, 0.195))
# triangle pieces: legs along +x and +z of the model from the right-angle corner at (-LEG, -LEG), hypotenuse x + z = 0
# name -> (section of the placed piece, lowest y, highest y of its boxes: the square colliders' heights)
TRIANGLES = {"hs_collider_floor_tri": ("placeable_hs_floor_triangle", 0.005, 0.095),
             "hs_collider_foundation_tri": ("placeable_hs_foundation_triangle", -0.995, 0.395)}
# Walls, doorways and posts (door mode lets NPCs and mutants through a piece, so it gets static boxes too).
# model -> half sizes; thickness is padded to 0.10 each side (the walls are 0.10 to 0.114 m thick) so a charging
# mutant can't skip over the box in one physics step.
WALL_MODELS = {
    "hs_collider_wall": (2.349, 1.288, 0.06),         # 4.7 m wall: hs window / loophole, Hideout Furniture wall(_metal)
    "hs_collider_wall_low": (2.349, 0.625, 0.06),
    "hs_collider_wall_half": (1.172, 1.289, 0.06),    # Hideout Furniture wall02(_metal)
    "hs_collider_post": (0.195, 1.288, 0.195),
    "hs_collider_dd_post": (0.372, 1.288, 0.06),      # double doorway: two posts and a lintel, opening 3.2 x 2.25 m
    "hs_collider_dd_lintel": (1.600, 0.163, 0.06),
    "hs_collider_hfd_left": (1.2295, 0.995, 0.06),    # Hideout Furniture doorway: opening x 0.12..1.12, up to 2.0 m
    "hs_collider_hfd_right": (0.6095, 0.995, 0.06),
    "hs_collider_hfd_lintel": (2.349, 0.29, 0.06),
    "hs_collider_spiral_end": (2.349, 0.045, 0.072),  # spiral stair landing: 5 mm inset from hs_stairs_spiral_end
}
# piece section -> boxes (model, centre x, y, z in the piece's frame)
WALLS = {
    "placeable_hs_wall_window": [("hs_collider_wall", 0.0, 1.293, -0.008)],
    "placeable_hs_wall_loophole": [("hs_collider_wall", 0.0, 1.293, 0.0)],
    "placeable_hs_wall_low": [("hs_collider_wall_low", 0.0, 0.63, 0.0)],
    "placeable_hs_support_frame": [("hs_collider_post", 0.0, 1.293, 0.0)],
    "placeable_hs_doorway_double": [("hs_collider_dd_post", -1.977, 1.293, 0.0), ("hs_collider_dd_post", 1.977, 1.293, 0.0),
                                    ("hs_collider_dd_lintel", 0.0, 2.418, 0.0)],
    "placeable_hs_stairs_spiral_end": [("hs_collider_spiral_end", 0.0, 0.05, -2.277237)],
}
for _s in ("placeable_wall", "placeable_wall_metal"):
    WALLS[_s] = [("hs_collider_wall", 0.005, 1.293, -0.008)]
for _s in ("placeable_wall02", "placeable_wall02_metal"):
    WALLS[_s] = [("hs_collider_wall_half", -0.022, 1.294, -0.008)]
for _s in ("placeable_wall_doorway", "placeable_wall_doorway_metal"):
    WALLS[_s] = [("hs_collider_hfd_left", -1.1195, 1.0, -0.006), ("hs_collider_hfd_right", 1.7395, 1.0, -0.006),
                 ("hs_collider_hfd_lintel", 0.0, 2.2905, -0.006)]
TRI_STRIPS = 8
LEG = 2.349                    # the square pieces' collider half size
INSET = 0.005                  # as the square colliders: 5 mm inside the model, so snapped neighbours don't overlap
FMT_1L = 0x12071980
VERT_1L = 60
SFNOPICKABLE = 1
BROKEN_HALF = (0.05, 0.05, 0.05)   # bone shape: only what is left of a collider that broke
BROKEN_MASS = 1.0                  # bone mass, last field but the centre of mass (x10 when broken)
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


def triangle_strips(y0, y1, n=TRI_STRIPS):
    """Boxes (centre x, y, z, half x, y, z) in the model's frame that stack up a right isosceles triangle.
    The usable triangle has legs from -LEG and its hypotenuse INSET inside the model's (x + z = -d). N strips
    of height H / (N + 1), each as wide as the triangle is at its top edge, leave only the notches along the
    hypotenuse and the apex."""
    d = INSET * 2 ** 0.5
    height = LEG + (LEG - d)
    h = height / (n + 1)
    out = []
    for k in range(n):
        z0, z1 = -LEG + k * h, -LEG + (k + 1) * h
        x1 = -d - z1
        out.append(((-LEG + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, (x1 + LEG) / 2, (y1 - y0) / 2, h / 2))
    return out


def make_collider(source=None, half=None, centre_override=None):
    """The collider model of a square piece (box read from `source`), or of a box of these half sizes."""
    chunks = read_chunks((DIR / ((source or "hs_floor") + ".ogf")).read_bytes())
    ik = get(chunks, OGF_IKDATA)
    o, centre, source_half = bone_shape(ik)
    half = half or source_half
    if centre_override is not None:
        centre = centre_override

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
    new_ik[o + 4:o + 64] = obb(BROKEN_HALF)
    struct.pack_into("<f", new_ik, len(new_ik) - 16, BROKEN_MASS)
    return write_chunks([
        (OGF_HEADER, header(get(chunks, OGF_HEADER), half)),
        (OGF_CHILDREN, write_chunks([(0, new_child)])),
        (OGF_BONE_NAMES, names[:-60] + obb(half)),
        (OGF_IKDATA, bytes(new_ik)),
    ]), centre


def main():
    for name, (source, col_centre, col_half) in COLLIDERS.items():
        data, centre = make_collider(source, half=col_half, centre_override=col_centre)
        (DIR / (name + ".ogf")).write_bytes(data)
        print(f"{name}: {len(data)} bytes, homestead_collider_y = {centre[1]:.6f}")
    for name, (section, y0, y1) in TRIANGLES.items():
        strips = triangle_strips(y0, y1)
        area = sum(4 * s[3] * s[5] for s in strips)
        print(f"{name}: {len(strips)} strips cover {area / (LEG * LEG * 2):.1%} of the triangle")
        for k, (cx, cy, cz, hx, hy, hz) in enumerate(strips):
            data, _ = make_collider(half=(hx, hy, hz))
            (DIR / f"{name}_{k + 1}.ogf").write_bytes(data)
            print(f"  [{section}] homestead_collider_{k + 1} = {name}_{k + 1}, {cx:.6f}, {cy:.6f}, {cz:.6f}")
    for name, half in WALL_MODELS.items():
        data, _ = make_collider(half=half)
        (DIR / (name + ".ogf")).write_bytes(data)
        print(f"{name}: {len(data)} bytes, half {half}")
    print("; --- hs_colliders_<piece section> blocks for items_homestead_building.ltx")
    for sec, boxes in WALLS.items():
        print(f"[hs_colliders_{sec}]")
        for k, (model, x, y, z) in enumerate(boxes):
            print(f"homestead_collider_{k + 1} = {model}, {x:.6f}, {y:.6f}, {z:.6f}")
    for name in SOLID:
        path = DIR / (name + ".ogf")
        chunks = [c for c in read_chunks(path.read_bytes()) if c[0] != OGF_USERDATA]
        if name == "hs_foundation":
            new_chunks = []
            for cid, d in chunks:
                if cid == OGF_IKDATA:
                    o, _, _ = bone_shape(d)
                    ik_b = bytearray(d)
                    trn, hsz = FOUNDATION_DECK_SHAPE
                    struct.pack_into("<3f3f", ik_b, o + 4 + 36, *trn, *hsz)
                    d = bytes(ik_b)
                new_chunks.append((cid, d))
            chunks = new_chunks
        chunks.append((OGF_USERDATA, USERDATA))
        path.write_bytes(write_chunks(chunks))
        print(f"{name}: ignore_ragdoll")


if __name__ == "__main__":
    main()
