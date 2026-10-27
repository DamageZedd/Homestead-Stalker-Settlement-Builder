# Presentation stage for HomesteadHF model approvals (run inside Blender after a build script).
# Ground, sun, sky and EEVEE settings; render_views() writes PNGs. Objects named _preview* are
# never exported.
import bpy, math, os
from mathutils import Vector

GROUND_TEX = r"C:\GAMMA\mods\PAT\gamedata\textures\grnd\grnd_dirt_dust_01.dds"


def stage():
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError as e:
        print(e)
    ee = sc.eevee
    for attr, val in (("use_raytracing", True), ("use_shadows", True), ("use_gtao", True), ("gtao_distance", 0.4),
                      ("shadow_ray_count", 3), ("shadow_step_count", 10), ("use_shadow_jitter_viewport", True)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception:
                pass
    sc.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else sc.view_settings.view_transform
    sc.view_settings.look = 'None'
    # sky
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (0.42, 0.47, 0.55, 1)
    bg.inputs['Strength'].default_value = 0.65
    # ground
    g = bpy.data.objects.get("_preview_ground")
    if not g:
        bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
        g = bpy.context.active_object
        g.name = "_preview_ground"
        m = bpy.data.materials.new("_preview_ground")
        m.use_nodes = True
        t = m.node_tree
        bs = next(n for n in t.nodes if n.type == 'BSDF_PRINCIPLED')
        ti = t.nodes.new('ShaderNodeTexImage')
        ti.image = bpy.data.images.load(GROUND_TEX, check_existing=True)
        mp = t.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (3, 3, 3)
        tc = t.nodes.new('ShaderNodeTexCoord')
        t.links.new(tc.outputs['UV'], mp.inputs['Vector']); t.links.new(mp.outputs['Vector'], ti.inputs['Vector'])
        t.links.new(ti.outputs['Color'], bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = 0.95
        g.data.materials.append(m)
    # low warm sun with soft shadows, cool fill from the sky
    sun = bpy.data.objects.get("_preview_sun")
    if not sun:
        sd = bpy.data.lights.new("_preview_sun", 'SUN')
        sun = bpy.data.objects.new("_preview_sun", sd)
        sc.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.data.color = (1.0, 0.93, 0.82)
    sun.data.angle = math.radians(4)
    sun.rotation_euler = (math.radians(52), 0, math.radians(35))
    for o in sc.objects:
        if o.type == 'LIGHT' and o.name != "_preview_sun":
            o.hide_render = True
            o.hide_viewport = True


def render_views(prefix, target, shots, res=(1000, 760), lens=55):
    """shots: {name: (camera position)}; returns PNG paths."""
    sc = bpy.context.scene
    cam = bpy.data.objects.get("_preview_cam")
    if not cam:
        cam = bpy.data.objects.new("_preview_cam", bpy.data.cameras.new("_preview_cam"))
        sc.collection.objects.link(cam)
    cam.data.lens = lens
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    paths = []
    for name, pos in shots.items():
        cam.location = pos
        cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = f"{prefix}_{name}.png"
        bpy.ops.render.render(write_still=True)
        paths.append(sc.render.filepath)
    return paths
