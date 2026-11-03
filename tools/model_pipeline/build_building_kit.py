"""Builds the extra HomesteadHF building-kit pieces (SCUM-style wooden modular elements) from the shipped
hs_floor / hs_foundation meshes' materials. Run inside Blender (live MCP or headless with the XRay addon):

    exec(open(r".../build_building_kit.py").read())      # builds every piece into the scene as hsk_<name>_visual
    build_all()                                         # returns {name: object}

Pieces are plain boxes/prisms with world-metre UVs on the two vanilla wood textures already used by the kit
(wood\\wood_plank6_bar_b panels, wood\\wood_board_01 trim/treads) and grnd\\grnd_concrete_2 for the foundation.
Conventions match the shipped pieces: Z up, pivot at the bottom centre of the tile, wall spans X, front is -Y.
"""
import bmesh
import bpy
import math
from mathutils import Matrix, Vector

TILE = 4.70895
H = 2.58663          # wall height
T = 0.114076         # wall thickness
STOREY = 2.68663
HALF = TILE / 2
UV_SCALE = 1.0       # texture repeats per metre


def mat(name):
    for src in ("hs_floor_visual", "hs_foundation_visual_export", "hs_wall_window_visual"):
        o = bpy.data.objects.get(src)
        if o:
            for m in o.data.materials:
                if m.name == name:
                    return m
    raise KeyError(name)


def reproject(f, uv):
    """Texture axes in the face plane: u along the horizontal tangent (grain runs along walls, treads, ramp
    width), v up the face / along the slope, both in metres, so no face is stretched or sheared."""
    f.normal_update()
    n = f.normal
    up = Vector((0, 0, 1))
    u = n.cross(up)
    if u.length < 1e-4:
        u = Vector((1, 0, 0))
    u.normalize()
    v = n.cross(u).normalized()
    if v.z < 0 and abs(n.z) < 0.99:
        v = -v
    for l in f.loops:
        c = l.vert.co
        l[uv].uv = (c.dot(u) * UV_SCALE, c.dot(v) * UV_SCALE)


class Mesh:
    def __init__(self, name, mats):
        self.name, self.mats = name, mats
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("Texture")

    def _face(self, pts, mi):
        vs = [self.bm.verts.new(p) for p in pts]
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return
        f.material_index = mi
        reproject(f, self.uv)

    def poly(self, pts, mi=0, flip=False):
        """Single face from points (counter-clockwise seen from outside unless flip)."""
        self._face(list(reversed(pts)) if flip else pts, mi)

    def prism(self, base, z0, z1, mi=0, side=None):
        """Extruded polygon: base = [(x,y)...] counter-clockwise from above."""
        side = mi if side is None else side
        n = len(base)
        self._face([(x, y, z1) for x, y in base], mi)
        self._face([(x, y, z0) for x, y in reversed(base)], side)
        for i in range(n):
            a, b = base[i], base[(i + 1) % n]
            self._face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], side)

    def box(self, x0, x1, y0, y1, z0, z1, mi=0, top=None):
        top = mi if top is None else top
        self._face([(x0, y1, z1), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1)][::-1], top)
        self._face([(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)][::-1], mi)
        self._face([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], mi)
        self._face([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], mi)
        self._face([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], mi)
        self._face([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], mi)

    def wedge(self, x0, x1, ya, za, yb, zb, z_base=0.0, mi=0):
        """Slab between x0..x1 whose side profile runs from (ya, za) up to (yb, zb), solid down to z_base."""
        prof = [(ya, z_base), (yb, z_base), (yb, zb), (ya, za)]
        # side faces (x0 side facing -X, x1 side facing +X)
        self._face([(x1, y, z) for y, z in prof], mi)
        self._face([(x0, y, z) for y, z in reversed(prof)], mi)
        n = len(prof)
        for i in range(n):
            (y0_, z0_), (y1_, z1_) = prof[i], prof[(i + 1) % n]
            self._face([(x0, y0_, z0_), (x1, y0_, z0_), (x1, y1_, z1_), (x0, y1_, z1_)], mi)

    def finish(self, pivot_to_origin=True):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        me = bpy.data.meshes.new(self.name + "_visual")
        self.bm.to_mesh(me)
        self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(self.name + "_visual", me)
        bpy.context.scene.collection.objects.link(ob)
        for p in me.polygons:
            p.use_smooth = False
        return ob


def kit_mats():
    return mat("wood\\wood_plank6_bar_b"), mat("wood\\wood_board_01")


PLANK, BOARD = 0, 1


def new(name):
    return Mesh(name, list(kit_mats()))


# ---------------------------------------------------------------- walls
def wall_frame(m, x0, x1, z0, z1, trim=0.12, out=0.03):
    """Planked panel with a board-trim border (both faces, trim sticks out 3 cm)."""
    m.box(x0, x1, -T / 2, T / 2, z0, z1, PLANK, top=BOARD)
    for (a, b, c, d) in ((x0, x0 + trim, z0, z1), (x1 - trim, x1, z0, z1),
                         (x0 + trim, x1 - trim, z0, z0 + trim), (x0 + trim, x1 - trim, z1 - trim, z1)):
        m.box(a, b, -T / 2 - out, T / 2 + out, c, d, BOARD)


def wall_low():
    m = new("hsk_wall_low")
    h = 1.2
    wall_frame(m, -HALF, HALF, 0, h)
    m.box(-HALF, HALF, -T / 2 - 0.05, T / 2 + 0.05, h, h + 0.06, BOARD)   # cap rail
    return m.finish()


def wall_loophole():
    m = new("hsk_wall_loophole")
    x0, x1 = -HALF, HALF
    sx, sz0, sz1 = 0.55, 1.35, 1.65                                    # slit half width, bottom, top
    m.box(x0, x1, -T / 2, T / 2, 0, sz0, PLANK, top=BOARD)
    m.box(x0, x1, -T / 2, T / 2, sz1, H, PLANK, top=BOARD)
    m.box(x0, -sx, -T / 2, T / 2, sz0, sz1, PLANK)
    m.box(sx, x1, -T / 2, T / 2, sz0, sz1, PLANK)
    for (a, b, c, d) in ((x0, x0 + 0.12, 0, H), (x1 - 0.12, x1, 0, H), (x0, x1, 0, 0.12), (x0, x1, H - 0.12, H),
                         (-sx - 0.08, sx + 0.08, sz0 - 0.08, sz0), (-sx - 0.08, sx + 0.08, sz1, sz1 + 0.08)):
        m.box(a, b, -T / 2 - 0.03, T / 2 + 0.03, c, d, BOARD)
    for sgn in (-1, 1):
        m.box(sgn * (sx + 0.08) - 0.04 + (0.04 if sgn < 0 else 0), sgn * (sx + 0.08) + 0.04 - (0.04 if sgn > 0 else 0),
              -T / 2 - 0.03, T / 2 + 0.03, sz0 - 0.08, sz1 + 0.08, BOARD)
    return m.finish()


def doorway_double():
    m = new("hsk_doorway_double")
    d, dh = 1.6, 2.25                                                 # half opening width, opening height
    m.box(-HALF, -d, -T / 2, T / 2, 0, H, PLANK, top=BOARD)
    m.box(d, HALF, -T / 2, T / 2, 0, H, PLANK, top=BOARD)
    m.box(-d, d, -T / 2, T / 2, dh, H, PLANK)
    for (a, b, c, e) in ((-HALF, -HALF + 0.12, 0, H), (HALF - 0.12, HALF, 0, H), (-HALF, HALF, H - 0.12, H),
                         (-d - 0.12, -d, 0, dh + 0.12), (d, d + 0.12, 0, dh + 0.12), (-d - 0.12, d + 0.12, dh, dh + 0.12)):
        m.box(a, b, -T / 2 - 0.03, T / 2 + 0.03, c, e, BOARD)
    return m.finish()


def support_frame():
    m = new("hsk_support_frame")
    p = 0.14
    m.box(-p, p, -p, p, 0, H, BOARD)                                  # post
    m.box(-p - 0.06, p + 0.06, -p - 0.06, p + 0.06, 0, 0.22, PLANK, top=BOARD)   # base block
    m.box(-p - 0.06, p + 0.06, -p - 0.06, p + 0.06, H - 0.14, H, PLANK, top=BOARD)  # capital
    return m.finish()


# ---------------------------------------------------------------- floor / foundation triangles
def triangle_of(src_name, name):
    """Half a tile: the shipped slab cut along the diagonal (right angle at -X,-Y), same pivot as the full tile."""
    src = bpy.data.objects[src_name]
    bm = bmesh.new()
    bm.from_mesh(src.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(1, 1, 0), clear_outer=True, clear_inner=False)
    cut = [e for e in bm.edges if e.is_boundary]
    if cut:
        res = bmesh.ops.edgeloop_fill(bm, edges=cut) if hasattr(bmesh.ops, "edgeloop_fill") else None
        for f in (res or {}).get("faces", []):
            f.material_index = 0
    bm.normal_update()
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        reproject(f, uvl)
    me = bpy.data.meshes.new(name + "_visual")
    bm.to_mesh(me)
    bm.free()
    for mm in src.data.materials:
        me.materials.append(mm)
    ob = bpy.data.objects.new(name + "_visual", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def floor_triangle():
    """Half a floor tile (right angle at -X,-Y): plank underside, board top, same 10 cm slab as the floor."""
    m = new("hsk_floor_triangle")
    tri = [(-HALF, -HALF), (HALF, -HALF), (-HALF, HALF)]
    m.prism(tri, 0, 0.06, PLANK)
    m.prism([(-HALF + 0.02, -HALF + 0.02), (HALF - 0.04, -HALF + 0.02), (-HALF + 0.02, HALF - 0.04)], 0.06, 0.1, BOARD, side=BOARD)
    return m.finish()


# ---------------------------------------------------------------- stairs and ramp
RISE_STEPS = 16
STEP_H = STOREY / RISE_STEPS
TREAD = 0.07         # tread / landing board thickness: the underside stays open so you can walk under


def strip(m, c0, c1, ta, za, tb, zb, th, mi, axis_y=True):
    """Sloped board between c0..c1 across, running from (ta, za) to (tb, zb) with top on that line, th thick."""
    prof = [(ta, za - th), (tb, zb - th), (tb, zb), (ta, za)]
    pt = (lambda c, t, z: (c, t, z)) if axis_y else (lambda c, t, z: (t, c, z))
    m._face([pt(c1, t, z) for t, z in prof], mi)
    m._face([pt(c0, t, z) for t, z in reversed(prof)], mi)
    for i in range(4):
        (t0, z0), (t1, z1) = prof[i], prof[(i + 1) % 4]
        m._face([pt(c0, t0, z0), pt(c1, t0, z0), pt(c1, t1, z1), pt(c0, t1, z1)], mi)


def posts(m, x0, x1, y0, y1, z, p=0.14):
    for x in (x0 + p / 2, x1 - p / 2):
        for y in (y0 + p / 2, y1 - p / 2):
            m.box(x - p / 2, x + p / 2, y - p / 2, y + p / 2, 0, z, BOARD)


def landing(m, x0, x1, y0, y1, z):
    m.box(x0, x1, y0, y1, z - 0.12, z, PLANK, top=BOARD)
    posts(m, x0, x1, y0, y1, z - 0.12)


def flight(m, x0, x1, ya, yb, za, zb, n, axis_y=True):
    """Open flight from (ya, za) to (yb, zb): board treads, thin risers, side stringers; nothing under the steps."""
    d = 1 if yb > ya else -1
    dz = (zb - za) / n
    for i in range(n):
        t0, t1 = ya + (yb - ya) * i / n, ya + (yb - ya) * (i + 1) / n
        z = za + dz * (i + 1)
        lo, hi = min(t0, t1), max(t0, t1)
        if axis_y:
            m.box(x0, x1, lo, hi, z - TREAD, z, BOARD)
            m.box(x0, x1, t0 if d > 0 else t0 - 0.03, t0 + 0.03 if d > 0 else t0, z - dz, z - TREAD, PLANK)
        else:
            m.box(lo, hi, x0, x1, z - TREAD, z, BOARD)
            m.box(t0 if d > 0 else t0 - 0.03, t0 + 0.03 if d > 0 else t0, x0, x1, z - dz, z - TREAD, PLANK)
    for c0, c1 in ((x0, x0 + 0.07), (x1 - 0.07, x1)):
        strip(m, c0, c1, ya, za, yb, zb, 0.32, BOARD, axis_y)


def stairs_small():
    m = new("hsk_stairs_small")
    flight(m, -0.755, 0.755, -0.6, 0.6, 0, 0.4, 3)
    return m.finish()


def ramp():
    m = new("hsk_ramp")
    w = 1.25
    strip(m, -w, w, -HALF, 0.14, HALF, STOREY, 0.14, PLANK)                       # deck
    for c0, c1 in ((-w, -w + 0.12), (w - 0.12, w)):                               # side beams and curbs
        strip(m, c0, c1, -HALF, 0.14 + 0.1, HALF, STOREY + 0.1, 0.42, BOARD)
    for t in (-1.2, 1.2):                                                         # supports under the deck
        z = 0.14 + (STOREY - 0.14) * (t + HALF) / TILE
        posts(m, -w, w, t - 0.1, t + 0.1, z - 0.14)
    return m.finish()


def stairs_l(mirror=False):
    m = new("hsk_stairs_l_mirrored" if mirror else "hsk_stairs_l")
    xa0, xa1 = -HALF, -HALF + 1.51
    yl0, yl1 = HALF - 1.51, HALF
    half = STOREY / 2
    n = RISE_STEPS // 2
    flight(m, xa0, xa1, -HALF, yl0, 0, half, n)
    landing(m, xa0, xa1, yl0, yl1, half)
    flight(m, yl0, yl1, xa1, HALF, half, STOREY, n, axis_y=False)
    ob = m.finish()
    if mirror:
        ob.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        ob.data.flip_normals()
        ob.name = "hsk_stairs_l_mirrored_visual"
    return ob


def stairs_u():
    m = new("hsk_stairs_u")
    w = 1.51
    n = RISE_STEPS // 2
    yl0 = HALF - 1.51
    flight(m, -HALF, -HALF + w, -HALF, yl0, 0, STOREY / 2, n)
    landing(m, -HALF, HALF, yl0, HALF, STOREY / 2)
    flight(m, HALF - w, HALF, yl0, -HALF, STOREY / 2, STOREY, n)
    return m.finish()


def stairs_spiral():
    m = new("hsk_stairs_spiral")
    n = RISE_STEPS
    r0, r1 = 0.3, 2.15
    da = math.radians(315) / n
    a_start = math.radians(-45)
    for i in range(n):
        a0, a1 = a_start + i * da, a_start + (i + 1) * da
        z = STEP_H * (i + 1)
        base = [(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)),
                (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))]
        m.prism(base, z - 0.08, z, BOARD, side=PLANK)
    seg = 12
    col = [(0.3 * math.cos(2 * math.pi * k / seg), 0.3 * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    m.prism(col, 0, STOREY, BOARD)
    return m.finish()


BUILDERS = {
    "hsk_wall_low": wall_low,
    "hsk_wall_loophole": wall_loophole,
    "hsk_doorway_double": doorway_double,
    "hsk_support_frame": support_frame,
    "hsk_floor_triangle": floor_triangle,
    "hsk_foundation_triangle": lambda: triangle_of("hs_foundation_visual_export", "hsk_foundation_triangle"),
    "hsk_stairs_small": stairs_small,
    "hsk_ramp": ramp,
    "hsk_stairs_l": stairs_l,
    "hsk_stairs_l_mirrored": lambda: stairs_l(True),
    "hsk_stairs_u": stairs_u,
    "hsk_stairs_spiral": stairs_spiral,
}


def build_all():
    out = {}
    for name, fn in BUILDERS.items():
        old = bpy.data.objects.get(name + "_visual")
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        out[name] = fn()
    return out
