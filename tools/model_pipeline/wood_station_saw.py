# Wood Station: replaces the custom bow saw with the vanilla Anomaly saw (meshes\dynamics\workshop_room\saw.ogf,
# texture prop\prop_instrument_1) at the same place on the sawhorse log (run inside Blender).
#   swap_saw(ob, accent_ns) - ob is the wood_station mesh after retarget(); accent_ns is accent_lib executed as a namespace.
import bpy, bmesh, math, os
import numpy as np
from mathutils import Matrix

PATH = "prop\\prop_instrument_1"
TEX_ROOT = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures"


def swap_saw(ob, acc):
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
        # the old saw: blade plane and the two arms, standing at x = -0.42, spanning y beyond +-0.6, z 0.78 .. 1.01
        if lo[0] > -0.5 and hi[0] < -0.35 and hi[1] - lo[1] > 0.0 and (hi[1] > 0.65 or lo[1] < -0.6) and lo[2] > 0.7:
            drop += comp
    bmesh.ops.delete(bm, geom=drop, context='FACES')
    bm.to_mesh(me); bm.free()

    new, _ = acc['import_ogf']("dynamics\\workshop_room\\saw", "tmp_saw")
    saws = [o for o in new if o.type == 'MESH']
    for o in new:
        if o.type == 'ARMATURE':
            bpy.data.objects.remove(o, do_unlink=True)
    # the vanilla saw lies flat along x: stand its blade upright and lay it along y, centred on the old saw
    # the extra 180 degrees about the long axis (Y) puts the teeth edge down toward the log and the handle side up
    M = Matrix.Translation((-0.42, 0.05, 0.84)) @ Matrix.Rotation(math.radians(180), 4, 'Y') @ Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
    mat = bpy.data.materials.get(PATH)
    if mat is not None:                      # the importer's own copy carries model_aref and a glossy default: rebuild it
        bpy.data.materials.remove(mat)
        mat = None
    if mat is None:
        mat = bpy.data.materials.new(PATH); mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); ti = nt.nodes.new('ShaderNodeTexImage')
        ti.image = bpy.data.images.load(os.path.join(TEX_ROOT, PATH + ".dds"), check_existing=True)
        nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
        bs.inputs['Roughness'].default_value = 0.8      # matte like the other parts (viewport only; the game uses models\model)
        mat.xray.eshader = "models\\model"; mat.xray.cshader = "default"; mat.xray.gamemtl = "default_object"
    # the blade's teeth are cut out by the texture's alpha (as in vanilla): it keeps models\model_aref, the frame models\model
    mat_aref = mat.copy(); mat_aref.name = PATH + ".aref"; mat_aref.xray.eshader = "models\model_aref"
    for o in saws:
        o.parent = None
        o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
        o.data.transform(M)
        for mod in list(o.modifiers): o.modifiers.remove(mod)
        o.data.materials.clear(); o.data.materials.append(mat_aref if o.name.startswith('saw.ogf 00') else mat)
        o.data.uv_layers[0].name = me.uv_layers[0].name
        vg = o.vertex_groups.new(name="part5"); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for o in saws: o.select_set(True)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active
