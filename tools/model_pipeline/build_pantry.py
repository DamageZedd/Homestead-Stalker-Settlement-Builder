# Builds the HomesteadHF Pantry in Blender (run inside Blender).
# An open plank rack (posts, slatted shelves on rails, X-brace on the back) stocked with vanilla food:
# sacks (lifted from our own Farmer Station), tushonka and conserva tins, Russian rations, vodka,
# flasks, jars and sausages hanging on strings. Material name = texture path.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "pantry"
BLEND = os.path.join(SCR, r"models\pantry.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
TEX_DIRS.insert(0, os.path.join(SCR, r"wt\HomesteadHF\gamedata\textures"))
start({"wood": ("wood\\wood_jasik2", "models\\model"), "metal": ("mtl\\mtl_rust_dark", "models\\model"),
       "rope": ("mtl\\mtl_rope2-1", "models\\model")}, seed=2024)
# painted planks of wood_jasik2 (u ranges)
STRIPS[:] = [(0.03, 0.56), (0.665, 0.785), (0.83, 0.975)]

W, D, H = 1.30, 0.50, 1.75
P = 0.06                      # post section
SHELVES = [0.10, 0.62, 1.12, 1.62]
ST = 0.025                    # shelf board thickness

# posts
for sx in (-1, 1):
    for sy in (-1, 1):
        plank("post", H, P, P, T(sx * (W / 2 - P / 2), sy * (D / 2 - P / 2), H / 2, 0, 90, 0), bevel=0.006)
# shelves: slats along X on front/back rails, side rails between the posts
ns, sgap = 4, 0.006
sw = (D - 0.01 - (ns - 1) * sgap) / ns
for z in SHELVES:
    for i in range(ns):
        y = -(D - 0.01) / 2 + sw / 2 + i * (sw + sgap)
        plank("slat", W - 0.01, sw, ST, T(0, y, z + ST / 2, 90, 0, 0), bevel=0.003)
    for sy in (-1, 1):
        plank("rail", W - 2 * P, 0.06, 0.022, T(0, sy * (D / 2 - P - 0.011), z - 0.03), bevel=0.004)
    for sx in (-1, 1):
        plank("side_rail", D - 2 * P, 0.06, 0.022, T(sx * (W / 2 - P / 2), 0, z - 0.03, 0, 0, 90), bevel=0.004)
# X-brace across the back
bz0, bz1 = SHELVES[0] + 0.05, SHELVES[-1] - 0.05
ang = math.degrees(math.atan2(bz1 - bz0, W - 2 * P))
blen = math.hypot(bz1 - bz0, W - 2 * P)
for sgn in (-1, 1):
    plank("brace", blen, 0.07, 0.02, T(0, D / 2 + 0.01 * (1 if sgn > 0 else 2), (bz0 + bz1) / 2, 0, sgn * ang, 0), bevel=0.004)
# nails where the brace crosses the posts
for sx in (-1, 1):
    for z in (bz0 + 0.02, bz1 - 0.02):
        rivet(T(sx * (W / 2 - P / 2), D / 2 + 0.031, z, -90, 0, 0))

# ---------------------------------------------------------------- stock
TOP = [z + ST for z in SHELVES]


def farmer_sacks():
    """The three produce sacks of our Farmer Station, as separate objects (bottom centre at origin)."""
    p = os.path.join(SCR, r"wt\HomesteadHF\gamedata\meshes\dynamics\HomesteadHF\farmer_station.object")
    d, f = os.path.split(p)
    before = set(bpy.data.objects)
    bpy.ops.xray_import.object(directory=d, files=[{'name': f}])
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == 'MESH'][0]
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    mesh.modifiers.clear()
    mesh.parent = None
    atlas = os.path.join(SCR, r"wt\HomesteadHF\gamedata\textures\homestead_hf\atlas_farmer_station.dds")
    for m in mesh.data.materials:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = bpy.data.images.load(atlas, check_existing=True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    parts = [o for o in bpy.data.objects if o.type == 'MESH' and o.data.materials
             and o.data.materials[0] and o.data.materials[0].name.startswith("hf_atlas_farmer_station")]
    sacks = sorted([o for o in parts if len(o.data.vertices) == 1432], key=lambda o: o.dimensions.z, reverse=True)
    for o in parts:
        if o not in sacks:
            bpy.data.objects.remove(o, do_unlink=True)
    for o in sacks:
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        base = Vector(((min(c.x for c in cs) + max(c.x for c in cs)) / 2, (min(c.y for c in cs) + max(c.y for c in cs)) / 2, min(c.z for c in cs)))
        o.data.transform(Matrix.Translation(-base) @ o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
    return sacks


def place_part(o, matrix, ratio=None):
    o.matrix_world = matrix
    if ratio:
        mod = o.modifiers.new("dec", 'DECIMATE'); mod.ratio = ratio
        bpy.context.view_layer.objects.active = o
        with bpy.context.temp_override(object=o):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    PARTS.append(o)


sacks = farmer_sacks()      # tallest first: two standing, one lying
place_part(sacks[0], T(-0.38, 0.0, TOP[0], 0, 0, 20) @ Matrix.Diagonal((0.72, 0.72, 0.72, 1)), ratio=0.45)
place_part(sacks[2], T(0.30, 0.0, TOP[0], 0, 0, -8) @ Matrix.Diagonal((0.85, 0.85, 0.85, 1)), ratio=0.45)
place_part(sacks[1], T(-0.02, 0.06, TOP[0], 0, 0, -35) @ Matrix.Diagonal((0.74, 0.74, 0.74, 1)), ratio=0.45)
# loose potatoes (our own farm_potato) spilling in front of the sacks
pot_path = os.path.join(SCR, r"wt\HomesteadHF\gamedata\meshes\dynamics\HomesteadHF\farm_potato.ogf")
for i, (x, y) in enumerate([(-0.16, -0.17), (-0.10, -0.2), (0.12, -0.18), (0.55, -0.15), (0.50, -0.19)]):
    d_, f_ = os.path.split(pot_path)
    before = set(bpy.data.objects)
    bpy.ops.xray_import.ogf(directory=d_, files=[{'name': f_}])
    newp = [o for o in bpy.data.objects if o not in before]
    for o in newp:
        if o.type != 'MESH':
            continue
        for m in o.data.materials:
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE':
                    n.image = bpy.data.images.load(os.path.join(SCR, r"wt\HomesteadHF\gamedata\textures\dynamics\homestead_hf\farm_potato.dds"), check_existing=True)
        o.modifiers.clear(); mw = o.matrix_world.copy(); o.parent = None
        cs = [mw @ Vector(c) for c in o.bound_box]
        base = Vector(((min(c.x for c in cs) + max(c.x for c in cs)) / 2, (min(c.y for c in cs) + max(c.y for c in cs)) / 2, min(c.z for c in cs)))
        o.matrix_world = T(x, y, TOP[0], random.uniform(0, 40), 0, random.uniform(0, 360)) @ Matrix.Translation(-base) @ mw
        dec = o.modifiers.new("dec", 'DECIMATE'); dec.ratio = 0.22
        with bpy.context.temp_override(object=o):
            bpy.ops.object.modifier_apply(modifier=dec.name)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
        PARTS.append(o)
    for o in newp:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)

# middle shelf: a pyramid of tushonka, conserva tins, rations
cz = TOP[1]
for row, n in enumerate((5, 4, 3)):
    for i in range(n):
        x = -0.48 + (i + row * 0.5) * 0.078
        accent(r"dynamics\devices\dev_tushonka\dev_tushonka", T(x, -0.12, cz + row * 0.095, 0, 0, random.uniform(0, 360)))
for i in range(4):
    accent(r"dynamics\devices\dev_conserv\dev_conserv", T(-0.02, -0.10, cz + i * 0.06, 0, 0, random.uniform(-15, 15)))
for i in range(2):
    accent(r"dynamics\devices\rations\ration_ru", T(0.36, 0.0, cz + i * 0.076, 0, 0, 90 + random.uniform(-6, 6)))
for i in range(3):
    accent(r"dynamics\devices\dev_tushonka\dev_tushonka", T(-0.46 + i * 0.08, 0.08, cz, 0, 0, random.uniform(0, 360)))
for i in range(3):
    accent(r"dynamics\devices\dev_conserv\dev_conserv", T(0.13, 0.10, cz + i * 0.06, 0, 0, random.uniform(-20, 20)))
accent(r"dynamics\devices\rations\ration_ru", T(0.40, 0.02, cz + 0.152, 0, 0, 97))

# upper shelf: vodka, flasks, jars
uz = TOP[2]
for i in range(4):
    accent(r"dynamics\devices\dev_vodka\dev_vodka", T(-0.52 + i * 0.075, 0.05 - (i % 2) * 0.06, uz, 0, 0, random.uniform(0, 360)))
accent(r"dynamics\drink\drink_water", T(-0.15, -0.05, uz, 0, 0, 15))
accent(r"dynamics\drink\drink_water", T(-0.04, 0.02, uz, 0, 0, -25))
accent(r"dynamics\drink\drink_flask", T(0.10, -0.06, uz, 0, 0, 30), ratio=0.5)
for i, (x, y) in enumerate([(0.33, -0.08), (0.43, -0.06), (0.38, 0.05), (0.50, 0.06), (0.53, -0.08), (0.28, 0.08)]):
    accent(r"dynamics\equipments\trade\jar", T(x, y, uz, 0, 0, random.uniform(0, 360)))
for i, (x, y) in enumerate([(-0.49, 0.13), (-0.41, 0.15)]):
    accent(r"dynamics\devices\dev_vodka\dev_vodka", T(x, y, uz, 0, 0, random.uniform(0, 360)))
accent(r"dynamics\devices\dev_conserv\dev_conserv", T(0.43, 0.0, uz + 0.095, 0, 0, 10))

# top shelf: rations; sausages hanging on strings from the top shelf's front rail
tz = TOP[3]
accent(r"dynamics\devices\rations\ration_ru", T(-0.35, 0.0, tz, 0, 0, 92))
accent(r"dynamics\devices\rations\ration_ru", T(-0.33, 0.0, tz + 0.076, 0, 0, 84))
accent(r"dynamics\devices\dev_vodka\dev_vodka", T(0.02, 0.05, tz, 0, 0, 40))
for row, n in enumerate((3, 2)):
    for i in range(n):
        accent(r"dynamics\devices\dev_tushonka\dev_tushonka", T(0.36 + (i + row * 0.5) * 0.078, 0.02, tz + row * 0.095, 0, 0, random.uniform(0, 360)))
rail_y, rail_z = -(D / 2 - P - 0.011) - 0.012, SHELVES[3] - 0.06
for i, x in enumerate((0.10, 0.19, 0.30)):
    drop = 0.05 + i * 0.025
    tube("string", [Vector((x, rail_y, rail_z + 0.035)), Vector((x, rail_y - 0.004, rail_z - 0.01)), Vector((x, rail_y - 0.006, rail_z - drop))], 0.002, sides=5, vscale=20)
    rel = r"dynamics\devices\dev_kolbasa\dev_kolbasa" if i != 1 else r"dynamics\devices\dev_sausage\dev_sausage"
    # the sausage lies along Y: stand it on end, hanging from the string
    accent(rel, T(x, rail_y - 0.006, rail_z - drop, 90, 0, 0) @ Matrix.Translation((0, -0.0, 0)) @ Matrix.Rotation(math.radians(180), 4, 'X'))

pantry = join_parts()
