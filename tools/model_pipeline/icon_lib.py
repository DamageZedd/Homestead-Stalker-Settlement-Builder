# Inventory icon renders in the Hideout Furniture style (run inside Blender): transparent background,
# elevated front-left 3/4 view, muted overcast light, no ground or shadow.
import bpy, math
from mathutils import Vector


def render_icon(target_obj, path, px=(300, 200), view=(-1.0, -1.25, 0.95)):
    sc = bpy.context.scene
    hidden = []
    for o in sc.objects:
        if o is target_obj or o.type in ('CAMERA',):
            continue
        if not o.hide_render:
            o.hide_render = True
            hidden.append(o)
    w = sc.world
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    old = (tuple(bg.inputs['Color'].default_value), bg.inputs['Strength'].default_value)
    bg.inputs['Color'].default_value = (0.8, 0.8, 0.8, 1); bg.inputs['Strength'].default_value = 1.15
    cam = bpy.data.objects.get("_icon_cam") or bpy.data.objects.new("_icon_cam", bpy.data.cameras.new("_icon_cam"))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    corners = [target_obj.matrix_world @ Vector(c) for c in target_obj.bound_box]
    centre = sum(corners, Vector()) / 8
    d = Vector(view).normalized()
    cam.location = centre + d * 5
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cam.data.shift_x = cam.data.shift_y = 0.0
    bpy.context.view_layer.update()
    # fit the ortho scale to the projected bounds
    inv = cam.matrix_world.inverted()
    pts = [inv @ c for c in corners]
    wx = max(p.x for p in pts) - min(p.x for p in pts)
    wy = max(p.y for p in pts) - min(p.y for p in pts)
    aspect = px[0] / px[1]
    # ortho_scale spans the longer side of the render
    if aspect >= 1:
        cam.data.ortho_scale = max(wx, wy * aspect) * 1.06
    else:
        cam.data.ortho_scale = max(wy, wx / aspect) * 1.06
    cx = (max(p.x for p in pts) + min(p.x for p in pts)) / 2
    cy = (max(p.y for p in pts) + min(p.y for p in pts)) / 2
    cam.data.shift_x = cx / cam.data.ortho_scale
    cam.data.shift_y = cy / cam.data.ortho_scale
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = px
    sc.render.film_transparent = True
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    sc.render.film_transparent = False
    bg.inputs['Color'].default_value = old[0]; bg.inputs['Strength'].default_value = old[1]
    for o in hidden:
        o.hide_render = False
    return path
