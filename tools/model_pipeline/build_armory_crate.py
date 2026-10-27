# Builds the HomesteadHF Armory Crate in Blender (run inside Blender).
# Real construction: individual bevelled planks mapped onto single painted planks of wood_jasik,
# battens, riveted corner plates, strap hinges, hasps, rope handles, an open lid with the rifle
# cradles inside, and vanilla accents (AK-74, 5.45 packs, F-1 grenades). Material name = vanilla
# texture path; previews load PAT's HD copies and unpack the X-Ray _bump maps.
import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix, Euler

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
exec(open(os.path.join(SCR, r"models\accent_lib.py")).read())
NAME = "armory_crate"
BLEND = os.path.join(SCR, r"models\armory_crate.blend")
random.seed(57280)

# ---------------------------------------------------------------- clean up
for o in list(bpy.data.objects):
    if o.name.startswith(NAME) or o.name.startswith("_preview") or o.name == "Cube":
        bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    if c.name in (NAME, "accent_candidates"):
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
COL = bpy.data.collections.new(NAME)
bpy.context.scene.collection.children.link(COL)

# ---------------------------------------------------------------- materials


def make_mat(tex, eshader="models\\model"):
    m = bpy.data.materials.get(tex) or bpy.data.materials.new(tex)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = bpy.data.images.load(find_tex(tex), check_existing=True)
    nt.links.new(ti.outputs['Color'], bs.inputs['Base Color'])
    nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    bs.inputs['Roughness'].default_value = 0.8
    if eshader == "models\\model_aref":
        nt.links.new(ti.outputs['Alpha'], bs.inputs['Alpha'])
        m.blend_method = 'CLIP' if hasattr(m, "blend_method") else None
    bump = find_tex(tex + "_bump")
    if bump:
        # X-Ray bump: normal xyz packed as (A, B, G), gloss in R
        bi = nt.nodes.new('ShaderNodeTexImage')
        bi.image = bpy.data.images.load(bump, check_existing=True)
        bi.image.colorspace_settings.name = 'Non-Color'
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        comb = nt.nodes.new('ShaderNodeCombineColor')
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = 1.0
        nt.links.new(bi.outputs['Color'], sep.inputs['Color'])
        nt.links.new(bi.outputs['Alpha'], comb.inputs['Red'])
        nt.links.new(sep.outputs['Blue'], comb.inputs['Green'])
        nt.links.new(sep.outputs['Green'], comb.inputs['Blue'])
        nt.links.new(comb.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])
        gl = nt.nodes.new('ShaderNodeMath'); gl.operation = 'SUBTRACT'; gl.inputs[0].default_value = 1.0
        nt.links.new(sep.outputs['Red'], gl.inputs[1])
        nt.links.new(gl.outputs[0], bs.inputs['Roughness'])
    m.xray.eshader = eshader
    m.xray.cshader = "default"
    m.xray.gamemtl = "default_object"
    return m


MAT = {}
for key, tex, sh in [("wood", "wood\\wood_jasik", "models\\model"), ("wood2", "wood\\wood_jasik2", "models\\model"),
                     ("metal", "mtl\\mtl_rust_dark", "models\\model"), ("rope", "mtl\\mtl_rope2-1", "models\\model"),
                     ("stencil", "decal\\decal_ro50210", "models\\model_aref"), ("star", "decal\\decal_star", "models\\model_aref")]:
    MAT[key] = make_mat(tex, sh)

PARTS = []  # objects to join into the crate

# ---------------------------------------------------------------- geometry helpers
# painted planks of wood_jasik (u ranges) and the clean v range (the texture has a band at the bottom)
STRIPS = [(0.342, 0.572), (0.666, 0.814), (0.03, 0.245)]
V_MAX = 0.90


def finish(bm, name, mat_keys, matrix=None, smooth_angle=35):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for k in mat_keys:
        me.materials.append(MAT[k])
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    if matrix is not None:
        o.matrix_world = matrix
    for p in me.polygons:
        p.use_smooth = True
    # sharp edges above the angle: flat chamfers that still catch the light
    bm2 = bmesh.new(); bm2.from_mesh(me)
    for e in bm2.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(smooth_angle):
            e.smooth = False
    bm2.to_mesh(me); bm2.free()
    PARTS.append(o)
    return o


def beveled_box(size, bevel, segments=1):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, offset_type='OFFSET', segments=segments,
                        profile=0.5, affect='EDGES', clamp_overlap=True)
    return bm


def plank(name, length, width, thick, matrix, key="wood", bevel=0.004, along="x", wide="z"):
    """A plank along local X (length), Z (width), Y (thickness), mapped onto one painted plank."""
    sz = Vector((length, thick, width))
    bm = beveled_box(sz, bevel)
    uvl = bm.loops.layers.uv.new("Texture")
    s0, s1 = random.choice(STRIPS)
    vscale = 0.75                                    # texture V per metre along the plank
    v0 = random.uniform(0.0, max(0.0, V_MAX - length * vscale))
    # the plank's width takes a slice of the painted plank at the same texel density as its length
    uw = min(s1 - s0, width * vscale)
    u0 = random.uniform(s0, s1 - uw)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = l.vert.co
            if ax == 1:      # broad face
                u = u0 + (p.z / width + 0.5) * uw
                v = v0 + (p.x + length / 2) * vscale
            elif ax == 2:    # edge along the length
                u = u0 + (p.y / thick + 0.5) * uw * (thick / width)
                v = v0 + (p.x + length / 2) * vscale
            else:            # end grain
                u = u0 + (p.z / width + 0.5) * uw
                v = v0 + (p.y / thick + 0.5) * thick * vscale
            l[uvl].uv = (u, v)
    for f in bm.faces:
        f.material_index = 0
    jitter = Matrix.Rotation(math.radians(random.uniform(-0.35, 0.35)), 4, 'Y') @ Matrix.Rotation(math.radians(random.uniform(-0.25, 0.25)), 4, 'Z')
    return finish(bm, name, [key], matrix @ jitter)


def metal_box(name, size, matrix, bevel=0.0015, tile=0.35, key="metal"):
    bm = beveled_box(Vector(size), bevel)
    uvl = bm.loops.layers.uv.new("Texture")
    ou, ov = random.random(), random.random()
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        a, b = [i for i in range(3) if i != ax]
        for l in f.loops:
            p = l.vert.co
            l[uvl].uv = (p[a] / tile + ou, p[b] / tile + ov)
    return finish(bm, name, [key], matrix)


def rivet(matrix):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.0055, radius2=0.0035, depth=0.004)
    bmesh.ops.translate(bm, vec=Vector((0, 0, 0.002)), verts=bm.verts)
    uvl = bm.loops.layers.uv.new("Texture")
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (l.vert.co.x * 3 + 0.5, l.vert.co.y * 3 + 0.5)
    return finish(bm, "rivet", ["metal"], matrix, smooth_angle=60)


def tube(name, points, radius, key="rope", sides=7, vscale=6.0):
    """A tube swept along points (rope)."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("Texture")
    rings = []
    for i, p in enumerate(points):
        t = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        a = t.cross(up).normalized(); b = t.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * k / sides) + b * math.sin(2 * math.pi * k / sides)) * radius) for k in range(sides)])
    dist = [0.0]
    for i in range(1, len(points)):
        dist.append(dist[-1] + (points[i] - points[i - 1]).length)
    for i in range(len(points) - 1):
        for k in range(sides):
            k2 = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]])
            for l, (uu, vv) in zip(f.loops, [(k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1)]):
                l[uvl].uv = (uu / sides, dist[vv] * vscale)
    return finish(bm, name, [key], None, smooth_angle=80)


def decal(name, w, h, matrix, key="stencil"):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("Texture")
    vs = [bm.verts.new((x, 0, z)) for x, z in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]]
    f = bm.faces.new(vs)
    for l, uv in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        l[uvl].uv = uv
    return finish(bm, name, [key], matrix)


def T(x, y, z, rx=0, ry=0, rz=0):
    return Matrix.Translation((x, y, z)) @ Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_matrix().to_4x4()


# ---------------------------------------------------------------- the crate
L, D = 1.20, 0.52          # outer length / depth
TH = 0.022                 # board thickness
SK = 0.05                  # skid height
PW, GAP = 0.122, 0.004     # wall plank width / gap
NROWS = 3
HB = NROWS * PW + (NROWS - 1) * GAP     # wall height
Z0 = SK + TH                            # top of the floor boards

# skids (brown, runners across the depth)
for x in (-0.44, 0.44):
    plank("skid", D + 0.04, SK, 0.09, T(x, 0, SK / 2, 0, 0, 90), key="wood2", bevel=0.006)
# floor: planks along X
nf = 4
fw = (D - 2 * TH - (nf - 1) * GAP) / nf
for i in range(nf):
    y = -D / 2 + TH + fw / 2 + i * (fw + GAP)
    plank("floor", L - 2 * TH, fw, TH, T(0, y, SK + TH / 2, 90, 0, 0))
# long walls: horizontal planks, front (-Y) and back (+Y)
for side in (-1, 1):
    for r in range(NROWS):
        z = SK + PW / 2 + r * (PW + GAP)
        plank("wall", L, PW, TH, T(0, side * (D / 2 - TH / 2), z))
# end walls: vertical planks between the long walls
ne = 4
ew = (D - 2 * TH - (ne - 1) * GAP) / ne
for side in (-1, 1):
    for i in range(ne):
        y = -D / 2 + TH + ew / 2 + i * (ew + GAP)
        plank("end", HB, ew, TH, T(side * (L / 2 - TH / 2), y, SK + HB / 2, 0, 90, 90))
# battens: vertical on the long sides near the ends, horizontal cleats on the ends
BW = 0.075
for side in (-1, 1):
    for sx in (-1, 1):
        plank("batten", HB, BW, 0.026, T(sx * (L / 2 - 0.145), side * (D / 2 + 0.013), SK + HB / 2, 0, 90, 0), bevel=0.005)
CL = D - 0.20     # end cleats stop short of the corners, which carry the corner plates
for sx in (-1, 1):
    for z in (SK + 0.075, SK + HB - 0.075):
        plank("cleat", CL, 0.07, 0.028, T(sx * (L / 2 + 0.014), 0, z, 0, 0, 90), bevel=0.005)

# corner plates: thin sheet bent around each corner of the box, flush with the boards, riveted
CP, CT = 0.09, 0.0025
for sx in (-1, 1):
    for sy in (-1, 1):
        xo, yo = sx * L / 2, sy * D / 2
        for zc, zs in ((SK, 1), (SK + HB, -1)):
            zm = zc + zs * CP / 2
            metal_box("corner", (CT, CP, CP), T(xo + sx * CT / 2, yo - sy * CP / 2, zm))      # on the end
            metal_box("corner", (CP, CT, CP), T(xo - sx * CP / 2, yo + sy * CT / 2, zm))      # on the long side
            if zs < 0:                                                                       # over the top edge
                metal_box("corner", (CP, CP, CT), T(xo - sx * CP / 2, yo - sy * CP / 2, zc + CT / 2))
            for a, b in ((0.028, 0.03), (0.062, 0.062), (0.028, 0.062)):
                rivet(T(xo + sx * CT, yo - sy * a, zc + zs * b, 0, sx * 90, 0))
                rivet(T(xo - sx * a, yo + sy * CT, zc + zs * b, -sy * 90, 0, 0))

# rope handles: through two holes in each end's upper cleat
for sx in (-1, 1):
    x = sx * (L / 2 + 0.03)
    zc = SK + HB - 0.075
    pts = []
    for k in range(13):
        t = k / 12
        y = -0.10 + 0.20 * t
        sag = math.sin(math.pi * t) * 0.07
        pts.append(Vector((x + sx * (0.012 + math.sin(math.pi * t) * 0.025), y, zc - 0.015 - sag)))
    tube("rope", [Vector((sx * (L / 2 - 0.005), -0.10, zc))] + pts + [Vector((sx * (L / 2 - 0.005), 0.10, zc))], 0.009)
    for y in (-0.10, 0.10):     # knots inside the crate
        tube("knot", [Vector((sx * (L / 2 - 0.03), y, zc - 0.012)), Vector((sx * (L / 2 - 0.03), y, zc + 0.012))], 0.016, sides=7)

# front hasps (staple on the body) and back strap hinges
for x in (-0.33, 0.33):
    metal_box("hasp_plate", (0.05, 0.004, 0.075), T(x, -(D / 2 + 0.002), SK + HB - 0.05))
    for dz in (-0.02, 0.0, 0.02):
        rivet(T(x + 0.016 * (1 if dz else 0), -(D / 2 + 0.004), SK + HB - 0.05 + dz, 90, 0, 0)) if dz else None
    tube("staple", [Vector((x - 0.012, -(D / 2 + 0.004), SK + HB - 0.035)), Vector((x - 0.012, -(D / 2 + 0.03), SK + HB - 0.035)),
                    Vector((x + 0.012, -(D / 2 + 0.03), SK + HB - 0.035)), Vector((x + 0.012, -(D / 2 + 0.004), SK + HB - 0.035))], 0.0035, key="metal", vscale=3)
HINGE_Z = SK + HB + 0.005
for x in (-0.38, 0.38):
    metal_box("hinge_body", (0.045, 0.004, 0.11), T(x, D / 2 + 0.002, HINGE_Z - 0.06))
    rivet(T(x, D / 2 + 0.004, HINGE_Z - 0.09, -90, 0, 0)); rivet(T(x, D / 2 + 0.004, HINGE_Z - 0.04, -90, 0, 0))
    tube("knuckle", [Vector((x - 0.03, D / 2 + 0.008, HINGE_Z)), Vector((x + 0.03, D / 2 + 0.008, HINGE_Z))], 0.008, key="metal", sides=8, vscale=3)

# the lid, opened back past upright and resting on its hinges
LID_ANGLE = 112
lid_pivot = Matrix.Translation((0, D / 2 + 0.008, HINGE_Z)) @ Matrix.Rotation(math.radians(-LID_ANGLE), 4, 'X') @ Matrix.Translation((0, -(D / 2 + 0.008), -HINGE_Z))
nl = 4
lw = (D + 0.02 - (nl - 1) * GAP) / nl
LZ = HINGE_Z + TH / 2
for i in range(nl):
    y = -(D + 0.02) / 2 + lw / 2 + i * (lw + GAP)
    plank("lid", L + 0.02, lw, TH, lid_pivot @ T(0, y, LZ, 90, 0, 0))
for sx in (-1, 1):   # battens under the lid (they face up now the lid is open)
    plank("lid_batten", D - 0.06, 0.07, 0.024, lid_pivot @ T(sx * (L / 2 - 0.13), 0, LZ - TH / 2 - 0.012, 0, 0, 90), bevel=0.004)
plank("lid_batten", L - 0.36, 0.06, 0.02, lid_pivot @ T(0, 0, LZ - TH / 2 - 0.01, 0, 0, 0), bevel=0.004)
for x in (-0.38, 0.38):
    metal_box("hinge_lid", (0.045, 0.11, 0.004), lid_pivot @ T(x, D / 2 - 0.05, LZ + TH / 2 + 0.002))
for x in (-0.33, 0.33):
    metal_box("hasp_strap", (0.04, 0.004, 0.10), lid_pivot @ T(x, -(D / 2 + 0.012), LZ - 0.035))

# rifle cradles inside: boards across the crate with two notches each
CR_H = 0.10
for x in (-0.30, 0.30):
    bm = bmesh.new()
    prof = [(-D / 2 + TH, 0), (D / 2 - TH, 0), (D / 2 - TH, CR_H), (0.20, CR_H), (0.16, CR_H - 0.045), (0.08, CR_H - 0.045), (0.04, CR_H),
            (-0.04, CR_H), (-0.08, CR_H - 0.045), (-0.16, CR_H - 0.045), (-0.20, CR_H), (-D / 2 + TH, CR_H)]
    front = [bm.verts.new((-0.011, y, z)) for y, z in prof]
    back = [bm.verts.new((0.011, y, z)) for y, z in prof]
    bm.faces.new(front[::-1]); bm.faces.new(back)
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        bm.faces.new([front[i], front[j], back[j], back[i]])
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.003, segments=1, affect='EDGES', clamp_overlap=True)
    uvl = bm.loops.layers.uv.new("Texture")
    u0, u1 = STRIPS[0]
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co
            l[uvl].uv = (u0 + (p.z / CR_H) * (u1 - u0), 0.3 + p.y * 0.75)
    finish(bm, "cradle", ["wood2"], T(x, 0, Z0))

# stencils: serial on the front, a weathered star on the end
decal("stencil", 0.30, 0.15, T(-0.16, -(D / 2 + 0.0012), SK + HB * 0.48, 0, 0, 0))
decal("star", 0.16, 0.16, T(L / 2 + 0.0292, 0, SK + HB * 0.5, 0, 0, 90), key="star")

# ---------------------------------------------------------------- vanilla accents


def accent(rel, matrix, ratio=None):
    """Import a vanilla .ogf and place it: matrix is applied about the mesh's bottom centre."""
    new, missing = import_ogf(rel, NAME + "_accents")
    meshes = []
    for o in new:
        if o.type == 'MESH' and not any("addon" in (m.name if m else "") for m in o.data.materials):
            meshes.append(o)
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(c[i] for c in corners) for i in range(3)])
    hi = Vector([max(c[i] for c in corners) for i in range(3)])
    base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    keep = []
    for o in meshes:
        for mod in list(o.modifiers):
            o.modifiers.remove(mod)
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = matrix @ Matrix.Translation(-base) @ mw
        if ratio:
            mod = o.modifiers.new("dec", 'DECIMATE'); mod.ratio = ratio
            bpy.context.view_layer.objects.active = o
            with bpy.context.temp_override(object=o):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
        keep.append(o)
    for o in new:
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    PARTS.extend(keep)
    return keep


# AK-74 resting in the back notches, lying on its side along the crate (the front notches are empty: one rifle is out)
# (the ogf stands upright along Y: turn it lengthwise along X, then lay it on its side)
NOTCH_Z = Z0 + CR_H - 0.045
# lying on its side (7 cm thick), resting in the notches
ak_m = Matrix.Translation((0.035, 0.215, NOTCH_Z + 0.034)) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Rotation(math.radians(-90), 4, 'Z')
ak = accent(r"dynamics\weapons\wpn_ak74\wpn_ak74", ak_m, ratio=0.55)
# 5.45 ammo packs stacked at the left end, F-1 grenades at the right
for x, y, z, rz in [(-0.49, -0.118, 0, 2), (-0.49, 0.118, 0, -3), (-0.485, 0.0, 0.086, 7)]:
    accent(r"dynamics\weapons\wpn_ammo\ammo_545x39_fmj", T(x, y, Z0 + z, 0, 0, 90 + rz), ratio=0.4)
accent(r"dynamics\weapons\wpn_grenades\wpn_f1", T(0.49, -0.14, Z0, 0, 0, 25), ratio=0.5)
accent(r"dynamics\weapons\wpn_grenades\wpn_f1", T(0.49, -0.045, Z0 + 0.036, 0, 90, -30) @ Matrix.Translation((0, 0, -0.036)), ratio=0.5)

# ---------------------------------------------------------------- join into one mesh
bpy.ops.object.select_all(action='DESELECT')
for o in PARTS:
    o.select_set(True)
bpy.context.view_layer.objects.active = PARTS[0]
bpy.ops.object.join()
crate = bpy.context.view_layer.objects.active
crate.name = NAME + "_visual"
crate.data.name = NAME + "_visual"
# the join keeps the first part's transform: bake it so the origin is the crate's bottom centre
with bpy.context.temp_override(object=crate, selected_editable_objects=[crate]):
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# drop duplicate materials (joined parts each brought a slot; re-imports add ".001" copies, whose
# name would be exported as the texture path)
for i, m in enumerate(crate.data.materials):
    base_name = m.name.split(".0")[0] if "." in m.name[-4:] else m.name
    if base_name != m.name:
        keep_m = bpy.data.materials.get(base_name)
        if keep_m is None:
            m.name = base_name
        else:
            crate.data.materials[i] = keep_m
seen = {}
for i, m in enumerate(crate.data.materials):
    seen.setdefault(m.name, i)
remap = {i: seen[m.name] for i, m in enumerate(crate.data.materials)}
for p in crate.data.polygons:
    p.material_index = remap[p.material_index]
bpy.context.view_layer.objects.active = crate
with bpy.context.temp_override(object=crate):
    bpy.ops.object.material_slot_remove_unused()
acc = bpy.data.collections.get(NAME + "_accents")
if acc:
    bpy.data.collections.remove(acc)

tris = sum(len(p.vertices) - 2 for p in crate.data.polygons)
bpy.ops.wm.save_as_mainfile(filepath=BLEND, copy=True)
print("tris", tris, "materials", [m.name for m in crate.data.materials], "dims", tuple(round(d, 3) for d in crate.dimensions))
