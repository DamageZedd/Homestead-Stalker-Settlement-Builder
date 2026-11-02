# Re-textures and exports the HomesteadHF Water Purifier on plain-Anomaly textures, no atlas (run inside Blender).
# The purifier has no build script: its geometry is the shipped water_purifier.object (kept exactly, rig and collision
# included). retex_water_purifier.py classifies each connected part by its colour in the old atlas, gives it one
# of five vanilla materials and a fresh box/cylinder UV in metres; the valve wheel, bucket and water keep their UVs.
import bpy, os

WS = __import__('os').environ.get('HSHF_WS', r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws")          # workspace holding models\*.py
REPO = r"C:\Users\hocke\OneDrive\Documents\GitHub\Homestead-Stalker-Settlement-Builder"
SHIPPED = os.path.join(REPO, r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF")
OUT = WS + r"\out"
NAME = "water_purifier"

lib = {}
exec(open(os.path.join(WS, r"models\export_lib.py")).read(), lib)
rt = {}
exec(open(os.path.join(WS, r"models\retex_water_purifier.py")).read(), rt)

for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
for i in list(bpy.data.images): bpy.data.images.remove(i)
bpy.ops.xray_import.object(directory=SHIPPED, files=[{'name': NAME + ".object"}])
src = bpy.data.objects["WaterPurifier_visual"]
rt['retex'](src)
src.name = NAME + "_visual"
exp = lib['make_export_vanilla'](NAME + "_visual", NAME)
arm = lib['reuse_rig'](exp, NAME, SHIPPED)
os.makedirs(OUT, exist_ok=True)
print(lib['export'](arm, OUT, NAME)[:2])
