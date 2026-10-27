# Builds the HomesteadHF Field Kitchen (the Cook's station) in Blender (run inside Blender).
# A welded steel field range on a brick plinth: cast-iron top with ring burner lids, firebox door with
# vents, ash drawer, oven door with a thermometer, corner angles, a chimney with damper and rain cap; a
# stock pot and kettle on the burners; a weathered wooden prep shelf with plates, a bowl, a mug and a ladle;
# birch firewood, a charcoal sack and a kerosene can. Vanilla accents; material name = texture path.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "field_kitchen"
BLEND = os.path.join(SCR, r"models\field_kitchen.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
start({"brick": ("briks\\briks_br3", "models\\model"), "steel": ("mtl\\mtl_rja_01", "models\\model"),
       "iron": ("mtl\\mtl_rusted_01", "models\\model"), "pipe": ("mtl\\mtl_barrel_big_rust", "models\\model"),
       "metal": ("mtl\\mtl_rust_dark", "models\\model"), "table": ("wood\\wood_box", "models\\model"),
       "bark": ("lfo\\lfo_trees\\bark\\trees_atp_birch_bark", "models\\model"), "cut": ("wood\\wood_spil_1", "models\\model")}, seed=125)


def disc(name, radius, depth, matrix, key, seg=28, uv_scale=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = uv_scale or (0.48 / radius)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=50)


def log(length, radius, matrix):
    """A birch log along local X: bark around, sawn ends."""
    bm = bmesh.new()
    seg = 10
    ring = [[bm.verts.new((sx * length / 2, math.cos(2 * math.pi * k / seg) * radius * random.uniform(0.92, 1.05),
                           math.sin(2 * math.pi * k / seg) * radius * random.uniform(0.92, 1.05))) for k in range(seg)] for sx in (-1, 1)]
    uvl = bm.loops.layers.uv.new("Texture")
    ov = random.random()
    for k in range(seg):
        k2 = (k + 1) % seg
        f = bm.faces.new([ring[0][k], ring[0][k2], ring[1][k2], ring[1][k]])
        f.material_index = 0
        for l, (uu, vv) in zip(f.loops, [(k, 0), (k + 1, 0), (k + 1, 1), (k, 1)]):
            l[uvl].uv = (uu / seg, ov + vv * length * 0.9)
    for side, rv in ((0, ring[0][::-1]), (1, ring[1])):
        f = bm.faces.new(rv)
        f.material_index = 1
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.y / radius * 0.47, 0.5 + l.vert.co.z / radius * 0.47)
    me = bpy.data.meshes.new("log"); bm.to_mesh(me); bm.free()
    me.materials.append(MAT["bark"]); me.materials.append(MAT["cut"])
    o = bpy.data.objects.new("log", me); COL.objects.link(o); o.matrix_world = matrix
    for p in me.polygons:
        p.use_smooth = p.material_index == 0
    PARTS.append(o)
    return o


DG = Matrix.Diagonal  # shorthand for accent scales

# ---------------------------------------------------------------- plinth and range
PW, PD, PH = 1.05, 0.66, 0.22
metal_box("plinth", (PW, PD, PH), T(0, 0, PH / 2), bevel=0.01, tile=2.2, key="brick")
metal_box("plinth_cap", (PW + 0.02, PD + 0.02, 0.025), T(0, 0, PH + 0.0125), bevel=0.006, tile=1.6, key="brick")
SW, SD, SH = 0.95, 0.58, 0.54
Z0 = PH + 0.025
metal_box("body", (SW, SD, SH), T(0, 0, Z0 + SH / 2), bevel=0.008, tile=0.9, key="steel")
TOPZ = Z0 + SH
metal_box("top_plate", (SW + 0.04, SD + 0.04, 0.028), T(0, 0, TOPZ + 0.014), bevel=0.006, tile=0.7, key="iron")
TZ = TOPZ + 0.028
for bx, r in ((-0.22, 0.15), (0.21, 0.13)):
    for i, rr in enumerate((r, r * 0.68, r * 0.36)):
        disc("burner_ring", rr, 0.006, T(bx, -0.02, TZ + 0.003 + i * 0.0025), "iron", uv_scale=1.2)
    metal_box("ring_lifter_slot", (0.03, 0.008, 0.004), T(bx + r * 0.5, -0.02, TZ + 0.011), bevel=0.001, key="metal")
# corner angles up the body
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = sx * (SW / 2 + 0.002), sy * (SD / 2 + 0.002)
        metal_box("angle", (0.004, 0.045, SH), T(cx, cy - sy * 0.0225, Z0 + SH / 2), bevel=0.001)
        metal_box("angle", (0.045, 0.004, SH), T(cx - sx * 0.0225, cy, Z0 + SH / 2), bevel=0.001)
FY = -SD / 2
# firebox door (left) with vents, hinges and a latch handle
fd_c = Vector((-0.24, FY - 0.006, Z0 + 0.30))
metal_box("firebox_frame", (0.34, 0.006, 0.26), T(fd_c.x, FY - 0.003, fd_c.z), bevel=0.002, key="iron")
metal_box("firebox_door", (0.30, 0.012, 0.22), T(fd_c.x, FY - 0.011, fd_c.z), bevel=0.004, key="iron")
for i in range(4):
    metal_box("vent", (0.035, 0.004, 0.012), T(fd_c.x - 0.075 + i * 0.05, FY - 0.0175, fd_c.z - 0.06), bevel=0.0008, key="metal")
for z in (fd_c.z - 0.07, fd_c.z + 0.07):
    tube("door_hinge", [Vector((fd_c.x - 0.155, FY - 0.012, z - 0.025)), Vector((fd_c.x - 0.155, FY - 0.012, z + 0.025))], 0.007, key="metal", sides=8, vscale=3)
tube("door_handle", [Vector((fd_c.x + 0.10, FY - 0.017, fd_c.z + 0.02)), Vector((fd_c.x + 0.10, FY - 0.045, fd_c.z + 0.02)),
                     Vector((fd_c.x + 0.13, FY - 0.045, fd_c.z + 0.02))], 0.006, key="metal", sides=8, vscale=3)
# ash drawer under it
metal_box("ash_drawer", (0.30, 0.012, 0.075), T(fd_c.x, FY - 0.008, Z0 + 0.065), bevel=0.003, key="iron")
tube("ash_handle", [Vector((fd_c.x - 0.05, FY - 0.014, Z0 + 0.065)), Vector((fd_c.x - 0.05, FY - 0.035, Z0 + 0.065)),
                    Vector((fd_c.x + 0.05, FY - 0.035, Z0 + 0.065)), Vector((fd_c.x + 0.05, FY - 0.014, Z0 + 0.065))], 0.005, key="metal", sides=8, vscale=3)
# oven door (right) with a thermometer dial
od_c = Vector((0.22, FY, Z0 + 0.26))
metal_box("oven_door", (0.36, 0.012, 0.30), T(od_c.x, FY - 0.006, od_c.z), bevel=0.004, key="steel")
metal_box("oven_handle", (0.26, 0.022, 0.02), T(od_c.x, FY - 0.024, od_c.z + 0.12), bevel=0.004, key="metal")
disc("thermometer", 0.04, 0.012, T(od_c.x, FY - 0.016, od_c.z + 0.04, 90, 0, 0), "metal", uv_scale=2.0)
metal_box("needle", (0.004, 0.003, 0.032), T(od_c.x + 0.006, FY - 0.0235, od_c.z + 0.05, 0, 30, 0), bevel=0.0005, key="iron")
# towel bar along the front of the top
for x in (-SW / 2 + 0.05, SW / 2 - 0.05):
    metal_box("bar_post", (0.012, 0.04, 0.012), T(x, FY - 0.02, TOPZ - 0.03), bevel=0.002)
tube("towel_bar", [Vector((-SW / 2 + 0.05, FY - 0.04, TOPZ - 0.03)), Vector((SW / 2 - 0.05, FY - 0.04, TOPZ - 0.03))], 0.008, key="metal", sides=8, vscale=2)
# chimney from the back left: a collar, damper, two pipe sections and a rain cap
CHX, CHY = -0.36, SD / 2 - 0.10
tube("chimney", [Vector((CHX, CHY, TZ)), Vector((CHX, CHY, 1.20)), Vector((CHX, CHY, 1.95))], 0.065, key="pipe", sides=14, vscale=1.2)
for z in (TZ + 0.02, 1.20, 1.56):
    tube("pipe_band", [Vector((CHX, CHY, z - 0.012)), Vector((CHX, CHY, z + 0.012))], 0.071, key="metal", sides=14, vscale=2)
tube("damper_rod", [Vector((CHX - 0.10, CHY, 1.08)), Vector((CHX + 0.09, CHY, 1.08))], 0.005, key="metal", sides=6, vscale=3)
bm_ = bmesh.new()
bmesh.ops.create_cone(bm_, cap_ends=True, cap_tris=False, segments=14, radius1=0.12, radius2=0.012, depth=0.08)
uvl_ = bm_.loops.layers.uv.new("Texture")
for f in bm_.faces:
    for l in f.loops:
        l[uvl_].uv = (0.5 + l.vert.co.x * 2, 0.5 + l.vert.co.y * 2)
finish(bm_, "rain_cap", ["pipe"], T(CHX, CHY, 2.04), smooth_angle=60)
for a in (0, 120, 240):
    rr = math.radians(a)
    metal_box("cap_strut", (0.006, 0.006, 0.07), T(CHX + math.cos(rr) * 0.06, CHY + math.sin(rr) * 0.06, 1.975), bevel=0.001)

# ---------------------------------------------------------------- prep shelf on the right
SX0, SX1 = SW / 2 + 0.02, SW / 2 + 0.56
shelf_w = SX1 - SX0
metal_box("shelf_top", (shelf_w, SD, 0.035), T((SX0 + SX1) / 2, 0, TOPZ - 0.0175), bevel=0.005, tile=1.2, key="table")
for sy in (-1, 1):
    metal_box("shelf_leg", (0.045, 0.045, TOPZ - 0.035), T(SX1 - 0.04, sy * (SD / 2 - 0.04), (TOPZ - 0.035) / 2), bevel=0.004, tile=1.2, key="table")
metal_box("shelf_low", (shelf_w - 0.06, SD - 0.06, 0.025), T((SX0 + SX1) / 2 - 0.02, 0, 0.18), bevel=0.004, tile=1.2, key="table")
for sy in (-1, 1):
    metal_box("shelf_bracket", (0.03, 0.03, 0.18), T(SX0 + 0.02, sy * (SD / 2 - 0.05), TOPZ - 0.12, 0, 35, 0), bevel=0.003)

# ---------------------------------------------------------------- stock and accents
accent(r"dynamics\kitchen_room\kitchen_kastrula", T(-0.22, -0.02, TZ + 0.008, 0, 0, 20) @ DG((0.55, 0.55, 0.55, 1)))
accent(r"dynamics\kitchen_room\teapot_1", T(0.21, -0.02, TZ + 0.008, 0, 0, -35) @ DG((0.55, 0.55, 0.55, 1)))
TT = TOPZ
accent(r"dynamics\kitchen_room\kitchen_tarelka1", T(SX0 + 0.16, -0.12, TT, 0, 0, 0) @ DG((0.6, 0.6, 0.6, 1)))
accent(r"dynamics\kitchen_room\kitchen_tarelka1", T(SX0 + 0.16, -0.12, TT + 0.022, 0, 0, 40) @ DG((0.6, 0.6, 0.6, 1)))
accent(r"dynamics\kitchen_room\kitchen_miska", T(SX0 + 0.38, 0.06, TT, 0, 0, 10) @ DG((0.55, 0.55, 0.55, 1)))
accent(r"dynamics\kitchen_room\kitchen_krujka", T(SX0 + 0.40, -0.17, TT, 0, 0, 60) @ DG((0.8, 0.8, 0.8, 1)))
accent(r"dynamics\kitchen_room\kitchen_lojka", T(SX0 + 0.20, 0.13, TT + 0.004, 0, 0, 75) @ DG((0.85, 0.85, 0.85, 1)))
accent(r"dynamics\kitchen_room\kitchen_bludo", T(SX0 + 0.16, 0.12, TT, 0, 0, 0) @ DG((0.6, 0.6, 0.6, 1)))
# birch firewood stacked on the lower shelf
LZ = 0.18 + 0.0125
for row, n in enumerate((4, 3, 2)):
    for i in range(n):
        r = random.uniform(0.042, 0.055)
        y = (i - (n - 1) / 2) * 0.105
        log(random.uniform(0.38, 0.44), r, T((SX0 + SX1) / 2 - 0.02 + random.uniform(-0.02, 0.02), y, LZ + 0.05 + row * 0.088, random.uniform(-10, 10), 0, 0))
# charcoal sack and kerosene can on the ground
accent(r"dynamics\cooking\charcoal", T(-PW / 2 - 0.18, -0.12, 0.0, 0, 0, 75))
accent(r"dynamics\cooking\kerosene", T(-PW / 2 - 0.16, 0.20, 0.0, 0, 0, 100))

kitchen = join_parts()
