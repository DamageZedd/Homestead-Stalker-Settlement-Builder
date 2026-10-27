# Turns a baked HomesteadHF model into its export rig and writes .object/.ogf (run inside Blender).
#   make_export(bake_name, name, atlas_png) -> mesh with one atlas material
#   rig(mesh, name, boxes, mass) -> armature: 'link' root bone (first box, mass, objects\large_furniture)
#        plus rigid 'shape_N' child bones for further boxes; boxes are (centre, half sizes, Blender rotation matrix)
#   export(arm, folder, name)
import bpy, os
from mathutils import Matrix, Vector

S_Z = Matrix.Scale(-1, 4, (0, 0, 1))


def make_export(bake_name, name, atlas_png):
    src = bpy.data.objects[bake_name]
    for o in list(bpy.data.objects):
        if o.name in (name + "_visual_export", name + ".object"):
            bpy.data.objects.remove(o, do_unlink=True)
    me = src.data.copy()
    for uv in [u.name for u in me.uv_layers if u.name != "atlas"]:
        me.uv_layers.remove(me.uv_layers[uv])
    me.uv_layers["atlas"].name = "Texture"
    me.uv_layers["Texture"].active_render = True
    tex = "homestead_hf\\atlas_" + name
    mat = bpy.data.materials.get(tex) or bpy.data.materials.new(tex)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.name = tex; ti.label = tex
    ti.image = bpy.data.images.load(atlas_png, check_existing=True)
    nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    bs.inputs['Roughness'].default_value = 0.8
    mat.xray.eshader = "models\\model"; mat.xray.cshader = "default"; mat.xray.gamemtl = "default_object"
    me.materials.clear(); me.materials.append(mat)
    for p in me.polygons:
        p.material_index = 0
    ob = bpy.data.objects.new(name + "_visual", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def rig(mesh, name, boxes, mass):
    arm_data = bpy.data.armatures.new(name + ".object")
    arm = bpy.data.objects.new(name + ".object", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    names = []
    for i, _ in enumerate(boxes):
        bn = "link" if i == 0 else f"shape_{i}"
        eb = arm_data.edit_bones.new(bn)
        eb.head = (0, 0, 0); eb.tail = (0, 0, 0.02); eb.roll = 0
        if i:
            eb.parent = arm_data.edit_bones["link"]
        names.append(bn)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    for bn, (centre, half, rot) in zip(names, boxes):
        b = arm_data.bones[bn]
        x = b.xray
        x.shape.type = '1'
        x.gamemtl = "objects\\large_furniture"
        x.mass.value = mass if bn == "link" else 1.0
        x.ikjoint.type = '4' if bn == "link" else '0'
        pose = arm.pose.bones[bn].matrix
        shape = Matrix.Translation(Vector(centre)) @ rot.to_4x4() @ Matrix.Diagonal((half[0], half[1], half[2], 1.0))
        # the addon's own apply_shape conversion (ops/edit_helpers/bone_shape.py)
        m = (pose @ S_Z).inverted() @ shape @ S_Z
        x.shape.box_trn = m.to_translation().to_tuple()
        sc = Vector([max(abs(a), 1e-6) for a in m.to_scale()])
        x.shape.box_hsz = sc.to_tuple()
        mrt = (m @ Matrix.Diagonal((sc[0], sc[1], sc[2], 1.0)).inverted()).to_3x3().transposed()
        for k in range(3):
            x.shape.box_rot[k * 3:k * 3 + 3] = mrt[k].to_tuple()
    arm.xray.flags = 1
    mesh.parent = arm
    vg = mesh.vertex_groups.get("link") or mesh.vertex_groups.new(name="link")
    vg.add(list(range(len(mesh.data.vertices))), 1.0, 'REPLACE')
    mod = mesh.modifiers.get("Armature") or mesh.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    return arm


def export(arm, folder, name):
    # the addon resets a brand-new material's shaders to 'default' once it first sees it: set them again
    for c in arm.children:
        for m in c.data.materials:
            m.xray.eshader = "models\\model"; m.xray.cshader = "default"; m.xray.gamemtl = "default_object"
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    for c in arm.children:
        c.select_set(True)
    bpy.context.view_layer.objects.active = arm
    obj_path = os.path.join(folder, name + ".object")
    ogf_path = os.path.join(folder, name + ".ogf")
    r1 = bpy.ops.xray_export.object_file(filepath=obj_path, object=arm.name, texture_name_from_image_path=False,
                                         fmt_version='soc', smoothing_out_of='SHARP_EDGES', export_motions=False)
    r2 = bpy.ops.xray_export.ogf_file(filepath=ogf_path, texture_name_from_image_path=False, fmt_version='soc',
                                      hq_export=True, export_motions=False)
    return r1, r2, obj_path, ogf_path
