# Bakes a built HomesteadHF model into one atlas (run inside Blender after its build script).
# bake_atlas(src_name, atlas_name, size, decals) -> (bake object, atlas PNG path)
#   decals: [(decal material name, projection matrix (unit quad in local XZ, outward = local -Y), size (w, h),
#             world outward normal, target material name)] - each decal is projected into the target
#   material so it bakes into the boards, and the decal quads are dropped.
import bpy, bmesh, os
from mathutils import Matrix, Vector

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"


def _project_decal(mat, decal_mat, matrix, size, normal, tag):
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    base_link = bsdf.inputs['Base Color'].links[0]
    base_out = base_link.from_socket
    emp = bpy.data.objects.get("_bake_" + tag) or bpy.data.objects.new("_bake_" + tag, None)
    if emp.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(emp)
    emp.matrix_world = matrix @ Matrix.Diagonal((size[0], 1.0, size[1], 1.0))
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.object = emp
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    for axis, out in (('X', 'X'), ('Z', 'Y')):
        add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'; add.inputs[1].default_value = 0.5
        nt.links.new(sep.outputs[axis], add.inputs[0]); nt.links.new(add.outputs[0], comb.inputs[out])
    src_img = next(n.image for n in decal_mat.node_tree.nodes if n.type == 'TEX_IMAGE')
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = src_img; ti.extension = 'CLIP'
    nt.links.new(comb.outputs[0], ti.inputs['Vector'])
    # only on the outward faces right behind the decal
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    dot = nt.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = normal
    nt.links.new(geo.outputs['Normal'], dot.inputs[0])
    facing = nt.nodes.new('ShaderNodeMath'); facing.operation = 'GREATER_THAN'; facing.inputs[1].default_value = 0.5
    nt.links.new(dot.outputs['Value'], facing.inputs[0])
    absy = nt.nodes.new('ShaderNodeMath'); absy.operation = 'ABSOLUTE'; nt.links.new(sep.outputs['Y'], absy.inputs[0])
    near = nt.nodes.new('ShaderNodeMath'); near.operation = 'LESS_THAN'; near.inputs[1].default_value = 0.04
    nt.links.new(absy.outputs[0], near.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'
    nt.links.new(facing.outputs[0], m1.inputs[0]); nt.links.new(near.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
    nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(ti.outputs['Alpha'], m2.inputs[1])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    nt.links.new(m2.outputs[0], mix.inputs['Factor'])
    nt.links.new(base_out, mix.inputs[6]); nt.links.new(ti.outputs['Color'], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])


def bake_atlas(src_name, atlas_name, size=4096, decals=(), margin_px=8):
    sc = bpy.context.scene
    src = bpy.data.objects[src_name]
    for o in list(bpy.data.objects):
        if o.name == src_name + "_bake":
            bpy.data.objects.remove(o, do_unlink=True)
    ob = src.copy(); ob.data = src.data.copy(); ob.name = src_name + "_bake"
    sc.collection.objects.link(ob)
    # bake-only material copies
    for i, m in enumerate(ob.data.materials):
        ob.data.materials[i] = m.copy()
    names = [m.name.rsplit(".", 1)[0] for m in ob.data.materials]
    # decals: project into their target material, drop the quads
    decal_idx = set()
    for k, (dmat, matrix, dsize, normal, target) in enumerate(decals):
        di = names.index(dmat); ti = names.index(target)
        decal_idx.add(di)
        _project_decal(ob.data.materials[ti], ob.data.materials[di], matrix, dsize, normal, f"decal{k}")
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in decal_idx], context='FACES')
    bm.to_mesh(ob.data); bm.free()
    # unique unwrap at even density
    me = ob.data
    if "atlas" in me.uv_layers:
        me.uv_layers.remove(me.uv_layers["atlas"])
    src_uv = me.uv_layers["Texture"]
    atl = me.uv_layers.new(name="atlas")
    me.uv_layers.active = atl
    src_uv.active_render = True
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    margin = margin_px / size
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=margin, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # target image in every material
    img = bpy.data.images.get(atlas_name)
    if img and tuple(img.size) != (size, size):
        bpy.data.images.remove(img); img = None
    img = img or bpy.data.images.new(atlas_name, size, size, alpha=False)
    for m in me.materials:
        if m is None:
            continue
        nt = m.node_tree
        tn = nt.nodes.get("_bake_target") or nt.nodes.new('ShaderNodeTexImage')
        tn.name = "_bake_target"; tn.image = img
        uvn = nt.nodes.get("_bake_uv") or nt.nodes.new('ShaderNodeUVMap')
        uvn.name = "_bake_uv"; uvn.uv_map = "atlas"
        nt.links.new(uvn.outputs['UV'], tn.inputs['Vector'])
        for n in nt.nodes:
            n.select = False
        tn.select = True; nt.nodes.active = tn
    prev_engine = sc.render.engine
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = 4
    sc.render.bake.use_pass_direct = False
    sc.render.bake.use_pass_indirect = False
    sc.render.bake.use_pass_color = True
    sc.render.bake.margin = margin_px
    sc.render.bake.target = 'IMAGE_TEXTURES'
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=margin_px, use_clear=True)
    sc.render.engine = prev_engine
    out = os.path.join(SCR, "models", atlas_name + ".png")
    img.filepath_raw = out; img.file_format = 'PNG'; img.save()
    ob.hide_render = True; ob.hide_viewport = True
    return ob, out
