# Swaps a custom-modelled accent for the vanilla Anomaly mesh that already exists (run inside Blender).
#   swap_part(ob, acc, pick, ogf, tex_path, bone, shader) -> joined object
#     pick(lo, hi, material_name) -> True for the loose parts of the custom accent (connected pieces of ob)
#     ogf       vanilla mesh path under meshes\ (e.g. dynamics\workshop_room\axe)
#     tex_path  the vanilla texture the mesh uses (matte models\model material is rebuilt for it)
#     bone      vertex group the new verts are weighted to (the old parts' bone)
# The vanilla mesh is scaled so its long axis matches the old part's long axis, rotated so its long and flat axes
# line up (head end = the heavier end), and centred on the old part.
import bpy, bmesh, os
import numpy as np
from mathutils import Matrix, Vector

TEX_ROOT = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures"


def _frame(vs):
    """(centre, long axis, flat axis, length) of a point set, long axis pointing toward the heavier end."""
    lo, hi = vs.min(0), vs.max(0)
    ext = hi - lo
    order = np.argsort(-ext)
    ctr = (lo + hi) / 2
    long_ax = np.zeros(3); long_ax[order[0]] = 1.0
    flat_ax = np.zeros(3); flat_ax[order[2]] = 1.0
    heavy = np.sign((vs.mean(0) - ctr)[order[0]]) or 1.0
    return ctr, long_ax * heavy, flat_ax, ext[order[0]]


def _basis(long_ax, flat_ax):
    third = np.cross(long_ax, flat_ax)
    return np.array([long_ax, flat_ax, third]).T      # columns


def swap_part(ob, acc, pick, ogf, tex_path, bone, shader="models\\model"):
    me = ob.data
    names = [m.name if m else None for m in me.materials]
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen = set(); drop = []; pts = []
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
        if pick(vs.min(0), vs.max(0), names[comp[0].material_index]):
            drop += comp; pts.append(vs)
    assert drop, "nothing picked"
    old = np.vstack(pts)
    bmesh.ops.delete(bm, geom=drop, context='FACES')
    bm.to_mesh(me); bm.free()

    new, _ = acc['import_ogf'](ogf, "tmp_swap")
    parts = [o for o in new if o.type == 'MESH']
    for o in new:
        if o.type == 'ARMATURE':
            bpy.data.objects.remove(o, do_unlink=True)
    for o in parts:
        o.parent = None
        o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
    van = np.array([v.co[:] for o in parts for v in o.data.vertices])
    c_old, l_old, f_old, len_old = _frame(old)
    c_van, l_van, f_van, len_van = _frame(van)
    R = _basis(l_old, f_old) @ _basis(l_van, f_van).T          # vanilla frame -> old frame
    M3 = np.eye(4); M3[:3, :3] = R * (len_old / len_van)
    M = Matrix.Translation(Vector(c_old)) @ Matrix(M3.tolist()) @ Matrix.Translation(Vector(-c_van))
    mat = bpy.data.materials.get(tex_path)
    if mat is not None and tex_path in names and mat.xray.eshader == shader:
        pass                                   # the model already carries this very material: reuse it
    else:
        if mat is not None and tex_path not in names:
            bpy.data.materials.remove(mat)     # the importer's glossy copy: rebuild it matte
        mat = bpy.data.materials.new(tex_path + (".swap" if tex_path in names else "")); mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); ti = nt.nodes.new('ShaderNodeTexImage')
        ti.image = bpy.data.images.load(os.path.join(TEX_ROOT, tex_path + ".dds"), check_existing=True)
        nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
        bs.inputs['Roughness'].default_value = 0.8
        mat.xray.eshader = shader; mat.xray.cshader = "default"; mat.xray.gamemtl = "default_object"
    for o in parts:
        o.data.transform(M)
        for mod in list(o.modifiers): o.modifiers.remove(mod)
        o.data.materials.clear(); o.data.materials.append(mat)
        o.data.uv_layers[0].name = me.uv_layers[0].name
        vg = o.vertex_groups.new(name=bone); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def box_project(ob, tiles):
    """Box-projects every face of the given materials in metres: tiles = {texture path: metres per texture repeat}."""
    me = ob.data
    names = [m.name for m in me.materials]
    uvl = me.uv_layers[0].data
    for tex, tile in tiles.items():
        if tex not in names:
            continue
        mi = names.index(tex)
        for p in me.polygons:
            if p.material_index != mi:
                continue
            a = int(np.argmax(np.abs(np.array(p.normal[:]))))
            for li in p.loop_indices:
                c = me.vertices[me.loops[li].vertex_index].co
                uvl[li].uv = [(c.y / tile, c.z / tile), (c.x / tile, c.z / tile), (c.x / tile, c.y / tile)][a]
