"""Exports the building-kit pieces built by build_building_kit.py as hs_<name>.object/.ogf (run inside Blender, after
build_all()). Collision is a few thin boxes per piece so the space under stairs and ramps stays walkable.

    exec(open(r".../export_building_kit.py").read())
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else r"C:\Users\hocke\.gemini\git repo homestead\Homestead\tools\model_pipeline")
import export_lib as xl  # noqa: E402

OUT = r"C:\Users\hocke\.gemini\git repo homestead\Homestead\HomesteadHF\gamedata\meshes\dynamics\HomesteadHF\building"
TILE = 4.70895
HALF = TILE / 2
H = 2.58663
T = 0.114076
STOREY = 2.68663
I3 = Matrix.Identity(3)


def slab(a, b, z0, z1):
    return ((((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (z0 + z1) / 2)), ((b[0] - a[0]) / 2, (b[1] - a[1]) / 2, (z1 - z0) / 2), I3)


def ramp_box(across, p0, p1, w, th=0.1):
    """Thin box along the line p0 -> p1 (3D points), `across` is the horizontal width axis, w its half width."""
    d = Vector(p1) - Vector(p0)
    length = d.length
    d.normalize()
    a = Vector(across)
    n = a.cross(d).normalized()
    rot = Matrix((a, d, n)).transposed()
    c = (Vector(p0) + Vector(p1)) / 2 - n * th * (1 if n.z > 0 else -1)
    return ((c.x, c.y, c.z), (w, length / 2, th), rot)


def flight_box(x0, x1, ya, yb, za, zb, axis_y=True):
    if axis_y:
        return ramp_box((1, 0, 0), ((x0 + x1) / 2, ya, za), ((x0 + x1) / 2, yb, zb), (x1 - x0) / 2)
    return ramp_box((0, 1, 0), (ya, (x0 + x1) / 2, za), (yb, (x0 + x1) / 2, zb), (x1 - x0) / 2)


def tri_boxes(top):
    """Staircase of boxes inside the triangle (right angle at -X,-Y)."""
    h = HALF
    rows = [(-h, -h / 2, -h, h / 2), (-h / 2, 0, -h, 0), (0, h / 2, -h, -h / 2)]
    return [slab((x0, y0), (x1, y1), 0, top) for (y0, y1, x0, x1) in rows]


def stairs_l_boxes(mirror):
    xa0, xa1 = -HALF, -HALF + 1.51
    yl0 = HALF - 1.51
    b = [flight_box(xa0, xa1, -HALF, yl0, 0.0, STOREY / 2), slab((xa0, yl0), (xa1, HALF), STOREY / 2 - 0.12, STOREY / 2),
         flight_box(yl0, HALF, xa1, HALF, STOREY / 2, STOREY, axis_y=False)]
    if mirror:
        b = [((-c[0], c[1], c[2]), h, Matrix.Scale(-1, 3, (1, 0, 0)) @ r @ Matrix.Scale(-1, 3, (1, 0, 0))) for c, h, r in b]
    return b


def stairs_u_boxes():
    w = 1.51
    yl0 = HALF - 1.51
    return [flight_box(-HALF, -HALF + w, -HALF, yl0, 0.0, STOREY / 2), slab((-HALF, yl0), (HALF, HALF), STOREY / 2 - 0.12, STOREY / 2),
            flight_box(HALF - w, HALF, yl0, -HALF, STOREY / 2, STOREY)]


def spiral_boxes():
    r0, r1 = 0.3, 2.15
    n = 16
    da = math.radians(315) / n
    out = [((0, 0, STOREY / 2), (0.3, 0.3, STOREY / 2), I3)]
    for i in range(n):
        a = math.radians(-45) + (i + 0.5) * da
        z = STOREY / 16 * (i + 1)
        rm = (r0 + r1) / 2
        rot = Matrix.Rotation(a, 3, 'Z')          # local X = radial, local Y = tangential
        out.append(((rm * math.cos(a), rm * math.sin(a), z - 0.04), ((r1 - r0) / 2, rm * da / 2 + 0.05, 0.06), rot))
    return out


def boxes_for(name):
    w = 1.25
    if name == "hsk_wall_low":
        return [slab((-HALF, -T / 2), (HALF, T / 2), 0, 1.26)]
    if name == "hsk_wall_loophole":
        return [slab((-HALF, -T / 2), (HALF, T / 2), 0, H)]
    if name == "hsk_doorway_double":
        return [slab((-HALF, -T / 2), (-1.6, T / 2), 0, H), slab((1.6, -T / 2), (HALF, T / 2), 0, H), slab((-1.6, -T / 2), (1.6, T / 2), 2.25, H)]
    if name == "hsk_support_frame":
        return [slab((-0.2, -0.2), (0.2, 0.2), 0, H)]
    if name == "hsk_floor_triangle":
        return tri_boxes(0.1)
    if name == "hsk_foundation_triangle":
        return tri_boxes(0.4)
    if name == "hsk_stairs_small":
        return [flight_box(-0.755, 0.755, -0.6, 0.6, 0.0, 0.4)]
    if name == "hsk_ramp":
        return [ramp_box((1, 0, 0), (0, -HALF, 0.14), (0, HALF, STOREY), w, 0.12)]
    if name == "hsk_stairs_l":
        return stairs_l_boxes(False)
    if name == "hsk_stairs_l_mirrored":
        return stairs_l_boxes(True)
    if name == "hsk_stairs_u":
        return stairs_u_boxes()
    if name == "hsk_stairs_spiral":
        return spiral_boxes()
    raise KeyError(name)


def export_all(names=None):
    res = {}
    for key in names or [o.name[:-len("_visual")] for o in bpy.data.objects if o.name.startswith("hsk_") and o.name.endswith("_visual")]:
        src = bpy.data.objects[key + "_visual"]
        src.location = (0, 0, 0)
        out_name = "hs_" + key[len("hsk_"):]
        for n in (out_name + ".object",):
            if n in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
        mesh = xl.make_export_vanilla(src.name, out_name)
        arm = xl.rig(mesh, out_name, boxes_for(key), 100.0)
        res[out_name] = xl.export(arm, OUT, out_name)[:2]
    return res
