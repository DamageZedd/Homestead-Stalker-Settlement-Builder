"""HD inventory icon renders of the shipped HomesteadHF models (run inside Blender with the XRay addon).

    exec(open(path).read()); run(["hs_foundation", ...], out_dir, cell=200)

Each model is imported from its shipped .object, textured from the mod's own and the vanilla textures,
rendered in the Hideout Furniture icon style (transparent, elevated front-left 3/4, overcast light) at
cell px per inventory cell (50 px = vanilla, 200 px = 4x HD), and removed again. Output: <out_dir>/<model>.png.
These renders are for the optional HD Inventory Icons patch only.
"""
import os
import re
import sys

import bpy
from mathutils import Vector

REPO = os.environ.get("HSHF_REPO", r"C:\Users\hocke\.gemini\git repo homestead\Homestead")
MESHES = os.path.join(REPO, r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF")
TMP = os.environ.get("HSHF_TMP", r"C:\Users\hocke\AppData\Local\Temp\claude_sp")
TEX_DIRS = [
    os.path.join(REPO, r"HomesteadHF\gamedata\textures"),
    os.environ.get("HSHF_VTEX", os.path.join(TMP, r"vtex\textures")),
    os.path.join(TMP, r"actors_unpack\textures"),
    os.path.join(TMP, r"ui_unpack\textures"),
    r"C:\GAMMA\mods\385- Even More Hideout Furnitures - facelessez\gamedata\textures",
]


def find_texture(path):
    for d in TEX_DIRS:
        p = os.path.join(d, path + ".dds")
        if os.path.exists(p):
            return p
    return None


def link_textures(obj):
    missing = []
    for m in obj.data.materials:
        if not m or not m.use_nodes:
            continue
        base = re.sub(r"(\.(\d{3}|aref))+$", "", m.name)
        path = find_texture(base)
        nt = m.node_tree
        img = next((n for n in nt.nodes if n.type == 'TEX_IMAGE'), None)
        bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not (img and bsdf):
            continue
        if not path:
            missing.append(base)
            continue
        img.image = bpy.data.images.load(path, check_existing=True)
        if not bsdf.inputs["Base Color"].is_linked:
            nt.links.new(img.outputs['Color'], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.9
        if bsdf.inputs.get("Specular IOR Level"):
            bsdf.inputs["Specular IOR Level"].default_value = 0.1
        if "aref" in (m.xray.eshader or ""):
            nt.links.new(img.outputs['Alpha'], bsdf.inputs['Alpha'])
            try:
                m.surface_render_method = 'DITHERED'
            except Exception:
                pass
    return missing


def one(model, out_dir, cw, ch, cell, view=(-1.0, -1.25, 0.95)):
    sc = bpy.context.scene
    before = set(bpy.data.objects)
    folder = MESHES if any(os.path.exists(os.path.join(MESHES, model + e)) for e in (".object", ".ogf")) else os.path.join(MESHES, "building")
    if os.path.exists(os.path.join(folder, model + ".object")):
        bpy.ops.xray_import.object(directory=folder, files=[{'name': model + ".object"}])
    else:
        bpy.ops.xray_import.ogf(directory=folder, files=[{'name': model + ".ogf"}])
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == 'MESH']
    missing = []
    for o in meshes:
        missing += link_textures(o)
    for o in sc.objects:
        o.hide_render = o not in new
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    centre = (Vector([min(p[i] for p in pts) for i in range(3)]) + Vector([max(p[i] for p in pts) for i in range(3)])) / 2
    cam = bpy.data.objects.get("_icon_cam") or bpy.data.objects.new("_icon_cam", bpy.data.cameras.new("_icon_cam"))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.hide_render = False
    cam.data.type = 'ORTHO'
    d = Vector(view).normalized()
    cam.location = centre + d * 40
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cam.data.shift_x = cam.data.shift_y = 0.0
    cam.data.clip_end = 200
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    verts = [inv @ (o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
    x0, x1 = min(v.x for v in verts), max(v.x for v in verts)
    y0, y1 = min(v.y for v in verts), max(v.y for v in verts)
    px = (int(cw * cell), int(ch * cell))
    aspect = px[0] / px[1]
    wx, wy = (x1 - x0) * 1.06, (y1 - y0) * 1.06
    cam.data.ortho_scale = max(wx, wy * aspect) if aspect >= 1 else max(wy, wx / aspect)
    cam.data.shift_x = ((x0 + x1) / 2) / cam.data.ortho_scale
    cam.data.shift_y = ((y0 + y1) / 2) / cam.data.ortho_scale
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = px
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items:
        if e.identifier.startswith("BLENDER_EEVEE"):
            sc.render.engine = e.identifier
    w = sc.world or bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
    bg.inputs['Strength'].default_value = 1.15
    sun = bpy.data.objects.get("_icon_sun")
    if not sun:
        sun = bpy.data.objects.new("_icon_sun", bpy.data.lights.new("_icon_sun", 'SUN'))
        sc.collection.objects.link(sun)
    sun.hide_render = False
    sun.data.energy = 2.0
    sun.rotation_euler = (0.9, 0.1, -0.6)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, model + ".png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in sc.objects:
        o.hide_render = False
    return out, sorted(set(missing))


def run(jobs, out_dir, cell=200):
    """jobs: list of (model, cells_w, cells_h)."""
    for model, cw, ch in jobs:
        print(one(model, out_dir, cw, ch, cell))
