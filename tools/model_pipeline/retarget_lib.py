# Re-points a pre-atlas station's materials at plain-Anomaly textures (run inside Blender).
#   retarget(ob, overrides) -> {material name: vanilla path}; merges materials that end on the same path,
#   loads the vanilla dds for the viewport and names each material after its texture path.
import bpy, os, re
IDX = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vanilla_index.txt"
INDEX = set(l.strip() for l in open(IDX, encoding="utf8") if l.strip())
BYBASE = {}
for p in INDEX:
    BYBASE.setdefault(p.split("\\")[-1].lower(), []).append(p)


def vanilla_path(m, overrides):
    if m.name in overrides:
        return overrides[m.name]
    img = next((n.image.filepath for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None) if m.node_tree else None
    cands = []
    if img:
        mm = re.split(r"[\/]textures[\/]", img, 1)
        if len(mm) == 2:
            cands.append(os.path.splitext(mm[1].replace("/", "\\"))[0])
        cands.append(os.path.splitext(os.path.basename(img))[0])
    cands.append(m.name.split(".0")[0])
    for c in cands:
        if c in INDEX:
            return c
        hit = BYBASE.get(c.split("\\")[-1].lower())
        if hit and len(hit) == 1:
            return hit[0]
    return None


def retarget(ob, overrides=None, tex_root=r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures"):
    overrides = overrides or {}
    me = ob.data
    mapping = {}; unresolved = []
    for m in me.materials:
        if m is None:
            continue
        p = vanilla_path(m, overrides)
        if p is None:
            unresolved.append(m.name)
        mapping[m.name] = p
    if unresolved:
        return mapping, unresolved
    order = []
    for m in me.materials:
        if m is not None and mapping[m.name] not in order:
            order.append(mapping[m.name])
    remap = {i: order.index(mapping[m.name]) for i, m in enumerate(me.materials) if m is not None}
    newidx = [remap.get(p.material_index, 0) for p in me.polygons]   # clearing the slots would reset the face indices
    olds = list(me.materials)
    me.materials.clear()
    for path in order:
        mat = bpy.data.materials.get(path)
        if mat is not None:
            bpy.data.materials.remove(mat)      # a same-named material from the source blend has broken image paths
            mat = None
        if mat is None:
            mat = bpy.data.materials.new(path); mat.use_nodes = True
            nt = mat.node_tree
            for n in list(nt.nodes): nt.nodes.remove(n)
            out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled'); ti = nt.nodes.new('ShaderNodeTexImage')
            f = os.path.join(tex_root, path + ".dds")
            if os.path.exists(f): ti.image = bpy.data.images.load(f, check_existing=True)
            nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'], out.inputs['Surface'])
            mat.xray.eshader = "models\model"; mat.xray.cshader = "default"; mat.xray.gamemtl = "default_object"
        me.materials.append(mat)
    for p, i in zip(me.polygons, newidx):
        p.material_index = i
    return mapping, []


def scale_uv(ob, factors):
    """factors: {vanilla texture path: uv multiplier} - <1 enlarges the texture on the surface."""
    me = ob.data
    names = [m.name for m in me.materials]
    uvl = me.uv_layers[0].data
    for p in me.polygons:
        f = factors.get(names[p.material_index])
        if f:
            for li in p.loop_indices:
                u, v = uvl[li].uv
                uvl[li].uv = (u * f, v * f)
