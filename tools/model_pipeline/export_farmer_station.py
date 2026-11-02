# Exports the HomesteadHF Farmer Station on plain-Anomaly textures, no atlas (run inside Blender).
# Source: the pre-atlas farmer_station.blend (its materials are already one per vanilla texture, original UVs).
# The planter boxes (wood_board_01 / wood_collect) and their soil (grnd_dirt_dark) get fresh metre-scaled UVs
# (horizontal planks); the wheat/leaf sheet (amik\nature\list) uses the alpha-tested shader.
import bpy, os, re, numpy as np

WS = __import__('os').environ.get('HSHF_WS', r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws")          # workspace holding models\*.py (see README in this folder)
BLEND = r"C:\Users\hocke\Documents\Homestead_backups\pre_atlas_20261025\farmer_station.blend"
SHIPPED = r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF"    # absolute path of the repo folder
OUT = WS + r"\out"
NAME = "farmer_station"

lib = {}
exec(open(os.path.join(WS, r"models\export_lib.py")).read(), lib)
acc = {}
exec(open(os.path.join(WS, r"models\accent_lib.py")).read(), acc)

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
for i in list(bpy.data.images): bpy.data.images.remove(i)
with bpy.data.libraries.load(BLEND) as (src, dst):
    dst.objects = [NAME + "_visual"]
ob = dst.objects[0]
bpy.context.scene.collection.objects.link(ob)
me = ob.data
for m in me.materials:
    img = next(n.image for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image)
    rel = re.split(r"[\\/]textures[\\/]", img.filepath, 1)[1][:-4]          # the vanilla texture path
    p = acc['find_tex'](rel)
    if p:
        img.filepath = p
    m.name = rel
    m.xray.eshader = "models\\model_aref" if rel == "amik\\nature\\list" else "models\\model"
names = [m.name for m in me.materials]
uvl = me.uv_layers[0]


def remap(mname, tile, grain_h):
    mi = names.index(mname)
    for p in me.polygons:
        if p.material_index != mi:
            continue
        a = int(np.argmax(np.abs(np.array(p.normal[:]))))
        for li in p.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            if a == 2:
                uv = (c.y / tile, c.x / tile) if grain_h else (c.x / tile, c.y / tile)
            elif a == 0:
                uv = (c.z / tile, c.y / tile) if grain_h else (c.y / tile, c.z / tile)
            else:
                uv = (c.z / tile, c.x / tile) if grain_h else (c.x / tile, c.z / tile)
            uvl.data[li].uv = uv


remap("wood\\wood_board_01", 0.6, True)
remap("wood\\wood_collect", 0.5, True)
remap("grnd\\grnd_dirt_dark", 0.7, False)
uvl.name = "Texture"
ob = lib['make_export_vanilla'](NAME + "_visual", NAME) if False else ob
ob.name = NAME + "_visual"
exp = lib['make_export_vanilla'](NAME + "_visual", NAME)
arm = lib['reuse_rig'](exp, NAME, SHIPPED)
print(lib['export'](arm, OUT, NAME)[:2])
