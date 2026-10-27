# Shared building helpers for HomesteadHF models (run inside Blender).
# A build script sets NAME and BLEND, calls start(materials) with {key: (texture, eshader)}, builds parts
# with the helpers (each lands in PARTS), adds vanilla accents with accent(), then join_parts().

import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix, Euler

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
exec(open(os.path.join(SCR, r"models\accent_lib.py")).read())

MAT = {}
PARTS = []
COL = None


def start(materials, seed=57280):
    """Clears the previous build of NAME and makes its materials."""
    global COL
    random.seed(seed)
    PARTS.clear()
    for c in list(bpy.data.collections):
        for o in list(c.objects):
            if not o.name.startswith("_preview"):
                bpy.data.objects.remove(o, do_unlink=True)
        try:
            bpy.data.collections.remove(c)
        except Exception:
            pass
    for o in list(bpy.data.objects):
        if not o.name.startswith("_preview"):
            bpy.data.objects.remove(o, do_unlink=True)
    COL = bpy.data.collections.new(NAME)
    bpy.context.scene.collection.children.link(COL)
    for key, (tex, sh) in materials.items():
        MAT[key] = make_mat(tex, sh)


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



def accent(rel, matrix, ratio=None, scale=None, base_z=None):
    """Import a vanilla .ogf and place it: matrix is applied about the mesh's bottom centre."""
    new, missing = import_ogf(rel, NAME + "_accents")
    meshes = []
    for o in new:
        if o.type == 'MESH' and not any("addon" in (m.name if m else "") for m in o.data.materials):
            meshes.append(o)
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(c[i] for c in corners) for i in range(3)])
    hi = Vector([max(c[i] for c in corners) for i in range(3)])
    bz = base_z if base_z is not None else lo.z
    base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, bz))
    keep = []
    for o in meshes:
        for mod in list(o.modifiers):
            o.modifiers.remove(mod)
        mw = o.matrix_world.copy()
        o.parent = None
        if scale:
            s_mat = Matrix.Diagonal((scale, scale, scale, 1.0))
            o.matrix_world = matrix @ s_mat @ Matrix.Translation(-base) @ mw
        else:
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


def join_parts():
    """Joins PARTS into NAME_visual (origin = world origin), merges duplicate materials, saves BLEND."""
    # parts imported from .object/.ogf may name their UV layer differently: one layer called Texture,
    # or the join leaves their coordinates in a layer the rest of the mesh doesn't use
    for o in PARTS:
        uvs = o.data.uv_layers
        if len(uvs) == 1 and uvs[0].name != 'Texture':
            uvs[0].name = 'Texture'
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
    return crate
