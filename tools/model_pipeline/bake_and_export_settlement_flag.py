# Automated bake, atlas generation, rigging, and OGF export for HomesteadHF Settlement Flag.
# Runs headless in Blender: blender.exe -b -P bake_and_export_settlement_flag.py
import bpy, os, sys, time
from mathutils import Matrix, Vector

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
REPO = r"C:\Users\hocke\.gemini\git repo homestead\Homestead"
TEX_OUT = os.path.join(REPO, r"HomesteadHF\gamedata\textures\homestead_hf")
MESH_OUT = os.path.join(REPO, r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF")

os.makedirs(TEX_OUT, exist_ok=True)
os.makedirs(MESH_OUT, exist_ok=True)

# 1. Build the approved Settlement Flag visual
print("\n--- 1. Building Settlement Flag Visual ---")
exec(open(os.path.join(SCR, r"models\build_settlement_flag.py")).read())
print(f"Visual: {visual.name}, {len(visual.data.vertices)} verts, {len(visual.data.polygons)} faces")

# 2. Bake base atlas (stalker)
print("\n--- 2. Baking Base Atlas (Stalker / Loners) ---")
exec(open(os.path.join(SCR, r"models\bake_atlas.py")).read())

t0 = time.time()
ob, base_png = bake_atlas("settlement_flag_visual", "atlas_settlement_flag", 4096)
print(f"Base atlas baked in {time.time() - t0:.1f}s -> {base_png}")

# 3. Batch bake remaining 11 factions
FACTIONS = [
    "stalker", "dolg", "freedom", "csky", "ecolog", "killer",
    "army", "bandit", "monolith", "renegade", "greh", "isg"
]

print("\n--- 3. Baking Faction Atlas Variants ---")
ob.hide_render = False
ob.hide_viewport = False
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
bpy.context.view_layer.objects.active = ob

flag_mat = next(m for m in ob.data.materials if "flag" in m.name)
tex_node = next(n for n in flag_mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.name != '_bake_target')

sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 4
sc.render.bake.use_pass_direct = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.use_pass_color = True
sc.render.bake.margin = 8
sc.render.bake.target = 'IMAGE_TEXTURES'

png_paths = {"stalker": base_png}

for fid in FACTIONS[1:]:
    t1 = time.time()
    flag_tex_path = os.path.join(SCR, f"vanilla_tex\\textures\\prop\\flag_{fid}.dds")
    tex_node.image = bpy.data.images.load(flag_tex_path, check_existing=True)
    
    img_name = f"atlas_settlement_flag_{fid}"
    img = bpy.data.images.new(img_name, 4096, 4096, alpha=False)
    
    for m in ob.data.materials:
        if m:
            tn = m.node_tree.nodes.get("_bake_target")
            if tn:
                tn.image = img
                tn.select = True
                m.node_tree.nodes.active = tn
                
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=8, use_clear=True)
    
    out_png = os.path.join(SCR, "models", f"{img_name}.png")
    img.filepath_raw = out_png
    img.file_format = 'PNG'
    img.save()
    png_paths[fid] = out_png
    print(f"Baked {fid:10s} in {time.time() - t1:.1f}s -> {out_png}")
    
    # Free image from RAM immediately to prevent memory buildup
    bpy.data.images.remove(img, do_unlink=True)

ob.hide_render = True
ob.hide_viewport = True

# 4. Rigging and exporting OGF meshes
print("\n--- 4. Rigging Collision and Exporting OGFs ---")
exec(open(os.path.join(SCR, r"models\export_lib.py")).read())

mesh = make_export("settlement_flag_visual_bake", "settlement_flag", base_png)

# Compute final mesh bounding box for LTX
me = mesh.data
corners = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
lo = Vector([min(c[i] for c in corners) for i in range(3)])
hi = Vector([max(c[i] for c in corners) for i in range(3)])
dim = hi - lo
origin = (lo + hi) / 2
print(f"Mesh bounds: X=[{lo.x:.3f}, {hi.x:.3f}], Y=[{lo.y:.3f}, {hi.y:.3f}], Z=[{lo.z:.3f}, {hi.z:.3f}]")
print(f"Dimensions (width, depth, height): {dim.x:.3f}, {dim.y:.3f}, {dim.z:.3f}")
print(f"Origin: {origin.x:.3f}, {origin.y:.3f}, {origin.z:.3f}")

# Collision boxes:
# 1. Root link: base pedestal, radial outriggers, and storage chest
# 2. shape_1: vertical mast column
boxes = [
    ((0.0, -0.05, 0.16), (0.44, 0.44, 0.16), Matrix.Identity(3)),
    ((0.0, 0.0, 1.40), (0.06, 0.06, 1.08), Matrix.Identity(3)),
]

arm = rig(mesh, "settlement_flag", boxes, 12.0)

# Export base model (.object and default .ogf)
r1, r2, obj_path, ogf_path = export(arm, MESH_OUT, "settlement_flag")
print(f"Exported base settlement_flag: obj={os.path.exists(obj_path)}, ogf={os.path.exists(ogf_path)}")

# Export all 12 faction variants with their respective texture paths
for fid in FACTIONS:
    tex_key = f"homestead_hf\\atlas_settlement_flag_{fid}"
    for c in arm.children:
        for m in c.data.materials:
            m.name = tex_key
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE':
                    n.name = tex_key
                    n.label = tex_key
                    n.image = bpy.data.images.load(png_paths[fid], check_existing=True)
            m.xray.eshader = "models\\model"
            m.xray.cshader = "default"
            m.xray.gamemtl = "default_object"
            
    r1, r2, _, ogf_v = export(arm, MESH_OUT, f"settlement_flag_{fid}")
    print(f"Exported settlement_flag_{fid}.ogf: {os.path.exists(ogf_v)} ({os.path.getsize(ogf_v)} bytes)")

print("\n--- Pipeline Completed Successfully! ---")
