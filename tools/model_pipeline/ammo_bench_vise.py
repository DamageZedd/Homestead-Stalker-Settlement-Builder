# Ammo Bench: replaces the custom bench vise with the vanilla Anomaly vise (meshes\dynamics\workshop_room\tiski.ogf,
# texture prop\prop_iten4) on the same spot of the bench top (run inside Blender).
#   swap_vise(ob, accent_ns) - ob is the ammo_bench mesh after retarget(); accent_ns is accent_lib executed as a namespace.
import bpy, bmesh, math, os
import numpy as np
from mathutils import Matrix

PATH = "prop\\prop_iten4"
TEX_ROOT = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures"
CENTRE = (-0.50, -0.27, 0.91)      # bench-top spot of the old vise (x, y, bench-top z)
SCALE = 0.65
YAW = 180                          # degrees about z: the jaw faces the middle of the bench


def swap_vise(ob, acc):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen = set(); drop = []
    for f in bm.faces:
        if f.index in seen:
            continue
        st = [f]; seen.add(f.index); comp = []
        while st:
            x = st.pop(); comp.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); st.append(g)
        vs = np.array([v.co[:] for fc in comp for v in fc.verts])
        lo, hi = vs.min(0), vs.max(0)
        # the old vise: loose parts above the bench top at the left front corner
        if lo[2] > 0.84 and lo[0] > -0.7 and hi[0] < -0.35 and hi[1] < -0.15:
            drop += comp
    bmesh.ops.delete(bm, geom=drop, context='FACES')
    bm.to_mesh(me); bm.free()

    new, _ = acc['import_ogf']("dynamics\\workshop_room\\tiski", "tmp_vise")
    parts = [o for o in new if o.type == 'MESH']
    for o in new:
        if o.type == 'ARMATURE':
            bpy.data.objects.remove(o, do_unlink=True)
    mat = bpy.data.materials.get(PATH)
    if mat is not None:                      # the importer's copy: rebuild it matte, models\model
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(PATH); mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); ti = nt.nodes.new('ShaderNodeTexImage')
    ti.image = bpy.data.images.load(os.path.join(TEX_ROOT, PATH + ".dds"), check_existing=True)
    nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    bs.inputs['Roughness'].default_value = 0.8
    mat.xray.eshader = "models\\model"; mat.xray.cshader = "default"; mat.xray.gamemtl = "default_object"
    # sit the vanilla vise's base on the bench top
    allv = np.array([(o.matrix_world @ v.co)[:] for o in parts for v in o.data.vertices])
    base_z = allv[:, 2].min(); cx = (allv[:, 0].min() + allv[:, 0].max()) / 2; cy = (allv[:, 1].min() + allv[:, 1].max()) / 2
    M = (Matrix.Translation(CENTRE) @ Matrix.Rotation(math.radians(YAW), 4, 'Z') @ Matrix.Diagonal((SCALE, SCALE, SCALE, 1.0))
         @ Matrix.Translation((-cx, -cy, -base_z)))
    for o in parts:
        o.parent = None
        o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
        o.data.transform(M)
        for mod in list(o.modifiers): o.modifiers.remove(mod)
        o.data.materials.clear(); o.data.materials.append(mat)
        o.data.uv_layers[0].name = me.uv_layers[0].name
        vg = o.vertex_groups.new(name="link"); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active
