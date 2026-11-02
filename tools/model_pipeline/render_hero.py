"""Render README hero images of the shipped HomesteadHF models (run inside Blender with the XRay addon).

    blender -b -P render_hero.py -- jobs.json

jobs.json is a list of {"model": "hunter_station", "out": "C:/path/hero_hunter_station.png",
"patch": "homestead_hf\\flag_patch_dolg" (optional: swaps the settlement flag's banner patch),
"size": [1600, 900] (optional)}. The model is the shipped .object, its textures are looked up in the
mod's own textures, the extracted vanilla textures (HSHF_VTEX) and the other texture folders below.
The look matches the earlier heroes: flat grey-blue background, three-quarter view from the front
right and above, one sun plus ambient light.
"""
import json
import math
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
BG = (121 / 255.0, 132 / 255.0, 150 / 255.0)   # the flat colour of the earlier heroes


def find_texture(path):
    for d in TEX_DIRS:
        p = os.path.join(d, path + ".dds")
        if os.path.exists(p):
            return p
    return None


def engine():
    for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items:
        if e.identifier.startswith("BLENDER_EEVEE"):
            return e.identifier
    return "CYCLES"


def link_textures(mesh_obj, patch):
    missing = []
    for m in mesh_obj.data.materials:
        if not m or not m.use_nodes:
            continue
        base = re.sub(r"\.(\d{3}|aref)$", "", m.name)
        tex = patch if (patch and base.startswith("homestead_hf\\flag_patch_")) else base
        path = find_texture(tex)
        nt = m.node_tree
        img_node = next((n for n in nt.nodes if n.type == 'TEX_IMAGE'), None)
        bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not (img_node and bsdf):
            continue
        if not path:
            missing.append(tex)
            continue
        img_node.image = bpy.data.images.load(path, check_existing=True)
        for sock in ("Base Color",):
            if not bsdf.inputs[sock].is_linked:
                nt.links.new(img_node.outputs['Color'], bsdf.inputs[sock])
        bsdf.inputs["Roughness"].default_value = 0.9
        if bsdf.inputs.get("Specular IOR Level"):
            bsdf.inputs["Specular IOR Level"].default_value = 0.1
        if "aref" in (m.xray.eshader or ""):             # alpha-tested textures (flag patch, saw blade)
            nt.links.new(img_node.outputs['Alpha'], bsdf.inputs['Alpha'])
            try:
                m.surface_render_method = 'DITHERED'
            except Exception:
                pass
    return missing


def render(job):
    bpy.ops.wm.read_homefile(use_empty=True)
    sc = bpy.context.scene
    folder = MESHES if os.path.exists(os.path.join(MESHES, job["model"] + ".ogf")) else os.path.join(MESHES, "building")
    bpy.ops.xray_import.object(directory=folder, files=[{'name': job["model"] + ".object"}])
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    missing = []
    for o in meshes:
        missing += link_textures(o, job.get("patch"))
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centre, radius = (lo + hi) / 2, (hi - lo).length / 2

    w, h = job.get("size", [1600, 900])
    sc.render.engine = engine()
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.world = bpy.data.worlds.new("hero")
    sc.world.use_nodes = True
    bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs[0].default_value = (*[c ** 2.2 for c in BG], 1.0)   # the world colour is linear
    bg.inputs[1].default_value = 1.0

    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 50
    cam_d.sensor_fit = 'HORIZONTAL'      # the framing below works out the fit from the width
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    tan_h = (cam_d.sensor_width / 2) / cam_d.lens
    tan_v = tan_h * h / w
    direction = Vector((0.62, -1.0, 0.55)).normalized()
    cam.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    rot = cam.rotation_euler.to_matrix()
    verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    verts = verts[::max(1, len(verts) // 4000)]
    inv = rot.inverted()
    # frame the model itself: re-centre on the middle of its projected extent, then back the camera off
    # until every sampled vertex is inside the fill fraction of the frame
    fill_w, fill_h = job.get("fill", [0.80, 0.84])
    cam_pts = [inv @ (p - centre) for p in verts]
    cx = (min(c.x for c in cam_pts) + max(c.x for c in cam_pts)) / 2
    cy = (min(c.y for c in cam_pts) + max(c.y for c in cam_pts)) / 2
    shift = rot @ Vector((cx, cy, 0))
    centre = centre + shift
    dist = radius * 0.3
    while dist < radius * 40:
        pos = centre + direction * dist
        ok = True
        for p in verts:
            cc = inv @ (p - pos)
            depth = -cc.z
            if depth <= 0.01 or abs(cc.x / depth) > tan_h * fill_w or abs(cc.y / depth) > tan_v * fill_h:
                ok = False
                break
        if ok:
            break
        dist *= 1.015
    cam.location = centre + direction * dist
    sc.camera = cam

    sun_d = bpy.data.lights.new("sun", 'SUN')
    sun_d.energy = 3.2
    sun = bpy.data.objects.new("sun", sun_d)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(48), math.radians(8), math.radians(-35))

    sc.render.filepath = job["out"]
    bpy.ops.render.render(write_still=True)
    print("RENDERED", job["model"], "->", job["out"], "| missing:", sorted(set(missing)))


def main():
    jobs = json.load(open(sys.argv[sys.argv.index("--") + 1]))
    for job in jobs:
        render(job)


main()
