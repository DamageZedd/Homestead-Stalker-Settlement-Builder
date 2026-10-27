# Builds the HomesteadHF Guard Post (the Guards' station) in Blender (run inside Blender).
# Authentic S.T.A.L.K.E.R. Zone sentry watch post:
# - Spiked timber duckboard platform floor with flat horizontal transverse planks (rx=90).
# - Sturdy sentry watch desk / duty counter with heavy square timber legs, vertical apron frame,
#   steel corner brackets with rivets, flat horizontal tabletop planks (rx=90), and lower storage shelf.
# - Dedicated 3-gun timber weapon rack on the right flank: ladder side frames, base cradle trough,
#   rear barrel rest crossbar, and steel locking bar with brass padlock.
#   Holding two vanilla AK-74 rifles and a vanilla TOZ-34 shotgun standing upright without clipping.
# - Low 3-course fortified sandbag breastwork in front of the desk, keeping the sentry protected while
#   leaving the table, lower shelf equipment, and guns completely visible.
# - Octagonal steel checkpoint warning sign ("СТОП" with bullet holes) mounted on a wooden picket stake.
# - Tabletop duty station: green gooseneck table lamp with cord to lower shelf battery, open sentry ledger
#   with pencil, field binoculars, enamel mug, military FM radio, 5.45x39 and 12-ga ammo packs,
#   wooden tray with F-1 and RGD-5 grenades, and scattered spent brass casings.
import os, bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "guard_post"
BLEND = os.path.join(SCR, r"models\guard_post.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())

start({
    "wood": ("wood\\wood_jasik", "models\\model"),
    "wood_dark": ("wood\\wood_box", "models\\model"),
    "canvas": ("prop\\prop_brezent", "models\\model"),
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "metal_green": ("mtl\\mtl_pod_green", "models\\model"),
    "metal_tin": ("mtl\\mtl_barrel_big_rust", "models\\model"),
    "red": ("mtl\\mtl_red_paint_iov", "models\\model"),
    "white": ("wall\\wall_house_white_01", "models\\model"),
    "sign": ("sign\\sign_stop1", "models\\model"),
    "rope": ("item\\item_rope", "models\\model"),
}, seed=57280)

DG = Matrix.Diagonal

def disc(name, radius, depth, matrix, key, seg=20, uv_scale=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = uv_scale or (0.48 / max(radius, 0.02))
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)

def octagonal_sign(name, radius, depth, matrix):
    """8-sided stop sign with front face mapped 0..1 to sign_stop1."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(22.5), 3, 'Z'), verts=bm.verts)
    for f in bm.faces:
        is_front = f.normal.z > 0.5
        if is_front:
            f.material_index = 0
            for l in f.loops:
                l[uvl].uv = (0.5 + l.vert.co.x / (radius * 2.05), 0.5 + l.vert.co.y / (radius * 2.05))
        else:
            f.material_index = 1
            for l in f.loops:
                l[uvl].uv = (0.5 + l.vert.co.x * 2.0, 0.5 + l.vert.co.y * 2.0)
    return finish(bm, name, ["sign", "metal"], matrix, smooth_angle=25)

def sandbag(name, length=0.46, width=0.25, height=0.125, matrix=None, key="canvas", deform_seed=0):
    rng = random.Random(deform_seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((length, width, height)), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.036, segments=2, profile=0.5, affect='EDGES', clamp_overlap=True)
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)

    hl, hw, hh = length / 2, width / 2, height / 2
    for v in bm.verts:
        p = v.co
        nx = p.x / hl
        ny = p.y / hw
        nz = p.z / hh
        dist_xy = max(0.0, 1.0 - (nx * nx * 0.75 + ny * ny * 0.75))
        p.x += (1.0 - ny * ny) * (0.012 if p.x > 0 else -0.012)
        p.y += (1.0 - nx * nx) * (0.018 if p.y > 0 else -0.018)
        if p.z > 0:
            p.z += dist_xy * 0.016 - rng.uniform(0, 0.003)
        else:
            p.z -= dist_xy * 0.012

    uvl = bm.loops.layers.uv.new("Texture")
    u_off = rng.uniform(0.05, 0.8)
    v_off = rng.uniform(0.05, 0.8)
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        a, b = [i for i in range(3) if i != ax]
        for l in f.loops:
            p = l.vert.co
            l[uvl].uv = (p[a] * 1.8 + u_off, p[b] * 1.8 + v_off)
    return finish(bm, name, [key], matrix, smooth_angle=45)

def place_gun_upright(rel, butt_pos, lean_deg=9, yaw_deg=180, ratio=0.40):
    new_objs, _ = import_ogf(rel, NAME + "_accents")
    meshes = [o for o in new_objs if o.type == 'MESH' and not any("addon" in (m.name if m else "") for m in o.data.materials)]
    verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector([min(v[i] for v in verts) for i in range(3)])
    butt_vs = [v for v in verts if v.y < lo.y + 0.05]
    butt_center = Vector((sum(v.x for v in butt_vs) / len(butt_vs), lo.y, sum(v.z for v in butt_vs) / len(butt_vs)))

    m = (Matrix.Translation(butt_pos)
         @ Matrix.Rotation(math.radians(-lean_deg), 4, 'X')
         @ Matrix.Rotation(math.radians(yaw_deg), 4, 'Z')
         @ Matrix.Rotation(math.radians(90), 4, 'X')
         @ Matrix.Translation(-butt_center))

    keep = []
    for o in meshes:
        for mod in list(o.modifiers):
            o.modifiers.remove(mod)
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = m @ mw
        if ratio:
            mod = o.modifiers.new("dec", 'DECIMATE')
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = o
            with bpy.context.temp_override(object=o):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
        keep.append(o)
    for o in new_objs:
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    PARTS.extend(keep)
    return keep

# ---------------------------------------------------------------- 1. Duckboard Platform Floor
PLAT_L = 1.90   # width along X [-0.95, +0.95]
PLAT_W = 1.06   # depth along Y [-0.53, +0.53]
SLEEPER_H = 0.045
SLEEPER_W = 0.085
DECK_THICK = 0.024
DECK_Z = SLEEPER_H + DECK_THICK  # 0.069m

# 3 sleeper runner beams along Y
for sx in (-0.74, 0.0, +0.74):
    metal_box("sleeper", (SLEEPER_W, PLAT_W - 0.04, SLEEPER_H), T(sx, 0, SLEEPER_H / 2), bevel=0.003, tile=0.45, key="wood_dark")

# 12 flat horizontal decking planks along X (rx=90!)
PLANK_W = 0.082
GAP = 0.005
y_starts = [-PLAT_W / 2 + 0.045 + i * (PLANK_W + GAP) for i in range(12)]
for i, py in enumerate(y_starts):
    plank(f"deck_plank_{i}", PLAT_L, PLANK_W, DECK_THICK, T(0, py, SLEEPER_H + DECK_THICK / 2, 90, 0, 0), key="wood", bevel=0.003)
    # Iron nails at sleeper joints
    for sx in (-0.74, 0.0, +0.74):
        for ny_off in (-PLANK_W * 0.28, PLANK_W * 0.28):
            disc("nail", 0.004, 0.003, T(sx, py + ny_off, DECK_Z + 0.001), "metal", seg=8)

# ---------------------------------------------------------------- 2. Sentry Watch Desk (Center-Left)
DX0, DX1 = -0.52, 0.34
DY0, DY1 = -0.10, 0.44
DCX = (DX0 + DX1) / 2
DCY = (DY0 + DY1) / 2
DL = DX1 - DX0   # 0.86m
DW = DY1 - DY0   # 0.54m
TABLE_TOP_Z = 0.780
LEG_SIZE = 0.062
LEG_H = TABLE_TOP_Z - DECK_Z - 0.028

# 4 heavy timber legs with vertical wood grain
for lx in (DX0 + 0.03 + LEG_SIZE / 2, DX1 - 0.03 - LEG_SIZE / 2):
    for ly in (DY0 + 0.03 + LEG_SIZE / 2, DY1 - 0.03 - LEG_SIZE / 2):
        plank("table_leg", LEG_H, LEG_SIZE, LEG_SIZE, T(lx, ly, DECK_Z + LEG_H / 2, 0, 90, 0), key="wood_dark", bevel=0.004)
        # Steel corner bracket with rivets
        metal_box("leg_bracket", (LEG_SIZE + 0.012, LEG_SIZE + 0.012, 0.038), T(lx, ly, TABLE_TOP_Z - 0.046), bevel=0.002, tile=0.3, key="metal")
        for rot in (0, 90, 180, 270):
            rivet(T(lx, ly, TABLE_TOP_Z - 0.046) @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Translation((LEG_SIZE / 2 + 0.006, 0, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Y'))

# Vertical apron frame under tabletop
APRON_H = 0.075
APRON_TH = 0.024
APRON_Z = TABLE_TOP_Z - 0.028 - APRON_H / 2
plank("apron_f", DL - 0.08, APRON_H, APRON_TH, T(DCX, DY0 + 0.03 + LEG_SIZE / 2, APRON_Z, 0, 0, 0), key="wood_dark", bevel=0.003)
plank("apron_b", DL - 0.08, APRON_H, APRON_TH, T(DCX, DY1 - 0.03 - LEG_SIZE / 2, APRON_Z, 0, 0, 0), key="wood_dark", bevel=0.003)
plank("apron_l", DW - 0.08, APRON_H, APRON_TH, T(DX0 + 0.03 + LEG_SIZE / 2, DCY, APRON_Z, 0, 0, 90), key="wood_dark", bevel=0.003)
plank("apron_r", DW - 0.08, APRON_H, APRON_TH, T(DX1 - 0.03 - LEG_SIZE / 2, DCY, APRON_Z, 0, 0, 90), key="wood_dark", bevel=0.003)

# Lower shelf at Z = 0.25m
SHELF_Z = DECK_Z + 0.18
plank("stretcher_l", DW - 0.08, 0.045, 0.035, T(DX0 + 0.03 + LEG_SIZE / 2, DCY, SHELF_Z, 0, 0, 90), key="wood_dark", bevel=0.003)
plank("stretcher_r", DW - 0.08, 0.045, 0.035, T(DX1 - 0.03 - LEG_SIZE / 2, DCY, SHELF_Z, 0, 0, 90), key="wood_dark", bevel=0.003)
# 3 flat horizontal shelf planks (rx=90!)
for si, spy in enumerate([-0.04, 0.10, 0.24]):
    plank(f"shelf_plank_{si}", DL - 0.06, 0.135, 0.022, T(DCX, spy + 0.06, SHELF_Z + 0.022 + 0.011, 90, 0, 0), key="wood", bevel=0.003)

# Tabletop: 4 FLAT horizontal planks along X (rx=90!)
TOP_PLANK_W = (DW - 0.009) / 4
for pi in range(4):
    py = DY0 + TOP_PLANK_W / 2 + pi * (TOP_PLANK_W + 0.003)
    plank(f"table_top_plank_{pi}", DL, TOP_PLANK_W, 0.028, T(DCX, py, TABLE_TOP_Z - 0.014, 90, 0, 0), key="wood", bevel=0.003)

# Equipment on lower shelf:
# Military ammo crate with green metal strapping and rope handles
metal_box("shelf_ammo_box", (0.34, 0.22, 0.16), T(DCX - 0.08, DCY, SHELF_Z + 0.033 + 0.08), bevel=0.004, tile=0.5, key="wood_dark")
metal_box("ammo_strap_l", (0.025, 0.224, 0.164), T(DCX - 0.08 - 0.11, DCY, SHELF_Z + 0.033 + 0.08), bevel=0.001, tile=0.3, key="metal_green")
metal_box("ammo_strap_r", (0.025, 0.224, 0.164), T(DCX - 0.08 + 0.11, DCY, SHELF_Z + 0.033 + 0.08), bevel=0.001, tile=0.3, key="metal_green")
tube("ammo_handle_l", [Vector((DCX - 0.08 - 0.17, DCY - 0.04, SHELF_Z + 0.13)), Vector((DCX - 0.08 - 0.21, DCY, SHELF_Z + 0.11)), Vector((DCX - 0.08 - 0.17, DCY + 0.04, SHELF_Z + 0.13))], 0.007, key="rope")
tube("ammo_handle_r", [Vector((DCX - 0.08 + 0.17, DCY - 0.04, SHELF_Z + 0.13)), Vector((DCX - 0.08 + 0.21, DCY, SHELF_Z + 0.11)), Vector((DCX - 0.08 + 0.17, DCY + 0.04, SHELF_Z + 0.13))], 0.007, key="rope")

# Lead-acid battery for the sentry lamp
BAT_X, BAT_Y, BAT_Z = DCX + 0.22, DCY + 0.04, SHELF_Z + 0.033
metal_box("battery_body", (0.16, 0.12, 0.14), T(BAT_X, BAT_Y, BAT_Z + 0.07), bevel=0.004, tile=0.3, key="metal")
disc("bat_term_pos", 0.010, 0.018, T(BAT_X - 0.045, BAT_Y, BAT_Z + 0.149), "red", seg=12)
disc("bat_term_neg", 0.010, 0.018, T(BAT_X + 0.045, BAT_Y, BAT_Z + 0.149), "metal_tin", seg=12)

# Power cable running from battery to lamp
tube("lamp_power_cord", [
    Vector((BAT_X - 0.045, BAT_Y, BAT_Z + 0.158)),
    Vector((BAT_X - 0.045, DY1 - 0.02, BAT_Z + 0.18)),
    Vector((DX0 + 0.05, DY1 - 0.02, SHELF_Z + 0.25)),
    Vector((DX0 + 0.05, DY1 - 0.02, TABLE_TOP_Z - 0.02)),
    Vector((DX0 + 0.14, DY1 - 0.08, TABLE_TOP_Z + 0.005)),
], 0.005, key="rope", sides=8)

# ---------------------------------------------------------------- 3. Fortified Sandbag Breastwork (Low 3-Course)
# A rugged 3-course breastwork at Y = -0.32m that protects the post without blocking the table!
# Course 1 (on deck, Z = 0.131m):
sandbag("sb_f1_1", 0.46, 0.25, 0.125, T(-0.55, -0.32, DECK_Z + 0.062, 0, 0, 2), deform_seed=11)
sandbag("sb_f1_2", 0.46, 0.25, 0.125, T(-0.10, -0.32, DECK_Z + 0.062, 0, 0, -1), deform_seed=12)
sandbag("sb_f1_3", 0.46, 0.25, 0.125, T(+0.24, -0.32, DECK_Z + 0.062, 0, 0, 1), deform_seed=13)

# Course 2 (Z = 0.253m): staggered
sandbag("sb_f2_1", 0.46, 0.25, 0.125, T(-0.70, -0.32, DECK_Z + 0.184, 0, 0, -2), deform_seed=21)
sandbag("sb_f2_2", 0.46, 0.25, 0.125, T(-0.32, -0.32, DECK_Z + 0.184, 0, 0, 2), deform_seed=22)
sandbag("sb_f2_3", 0.46, 0.25, 0.125, T(+0.10, -0.32, DECK_Z + 0.184, 0, 0, 0), deform_seed=23)

# Course 3 (Top crest, Z = 0.375m, reaches Z ~ 0.44m):
sandbag("sb_f3_1", 0.46, 0.25, 0.125, T(-0.54, -0.31, DECK_Z + 0.306, 0, 0, 1), deform_seed=31)
sandbag("sb_f3_2", 0.46, 0.25, 0.125, T(-0.12, -0.31, DECK_Z + 0.306, 0, 0, -2), deform_seed=32)

# Left flank return wall (X = -0.74m, Y: [-0.20, +0.25])
sandbag("sb_side_1", 0.44, 0.24, 0.125, T(-0.74, -0.06, DECK_Z + 0.062, 0, 0, 88), deform_seed=41)
sandbag("sb_side_2", 0.44, 0.24, 0.125, T(-0.74, +0.16, DECK_Z + 0.062, 0, 0, 92), deform_seed=42)
sandbag("sb_side_3", 0.44, 0.24, 0.125, T(-0.74, +0.05, DECK_Z + 0.184, 0, 0, 89), deform_seed=43)
sandbag("sb_side_4", 0.44, 0.24, 0.125, T(-0.74, +0.05, DECK_Z + 0.306, 0, 0, 91), deform_seed=44)

# Octagonal "СТОП" Checkpoint Warning Sign
# Cleanly mounted on a wooden picket stake in front of the sandbags (Y = -0.47m, completely outside!)
metal_box("sign_stake", (0.045, 0.045, 0.58), T(-0.14, -0.47, DECK_Z + 0.29), bevel=0.003, tile=0.4, key="wood_dark")
# 8-sided octagonal sign with authentic bullet-holed STOP face
octagonal_sign("sign_plate", 0.165, 0.006, T(-0.14, -0.495, DECK_Z + 0.44, 86, 0, 0))
# Mounting bolts through the sign
disc("sign_bolt_t", 0.005, 0.010, T(-0.14, -0.50, DECK_Z + 0.53, 90, 0, 0), "metal", seg=8)
disc("sign_bolt_b", 0.005, 0.010, T(-0.14, -0.50, DECK_Z + 0.35, 90, 0, 0), "metal", seg=8)

# ---------------------------------------------------------------- 4. 3-Gun Timber Weapon Rack (Right Flank)
# Authentic open Soviet armory rack: two side ladder frames, base cradle trough, rear notched crossbar,
# and front security locking bar with padlock. Completely open with ZERO clipping!
RX0, RX1 = 0.38, 0.90
RCX = (RX0 + RX1) / 2   # 0.64m
RW = RX1 - RX0          # 0.52m
RY_F = 0.01
RY_B = 0.27
RCY = (RY_F + RY_B) / 2 # 0.14m
RD = RY_B - RY_F        # 0.26m
RACK_H = 0.74           # Height of side ladder frames

# Base floor board (rx=90!)
plank("rack_base", RW, RD, 0.024, T(RCX, RCY, DECK_Z + 0.012, 90, 0, 0), key="wood_dark", bevel=0.003)
# Low front retaining curb (height = 0.038m, holds buttstock toes securely while keeping receivers fully open)
plank("rack_curb_f", RW, 0.038, 0.022, T(RCX, RY_F + 0.011, DECK_Z + 0.019, 0, 0, 0), key="wood_dark", bevel=0.003)

# Two ladder-frame side cheeks at X = RX0 and X = RX1
for x in (RX0 + 0.012, RX1 - 0.012):
    # Front vertical post
    plank("rack_post_f", RACK_H, 0.045, 0.045, T(x, RY_F + 0.022, DECK_Z + RACK_H / 2, 0, 90, 0), key="wood_dark", bevel=0.004)
    # Rear vertical post
    plank("rack_post_b", RACK_H, 0.045, 0.045, T(x, RY_B - 0.022, DECK_Z + RACK_H / 2, 0, 90, 0), key="wood_dark", bevel=0.004)
    # Top horizontal cap
    plank("rack_top_cap", RD, 0.055, 0.030, T(x, RCY, DECK_Z + RACK_H - 0.015, 0, 0, 90), key="wood_dark", bevel=0.003)

# Rear barrel rest crossbar at Z = 0.68m, Y = 0.23m (behind the barrels)
plank("barrel_rest", RW - 0.03, 0.045, 0.025, T(RCX, RY_B - 0.040, 0.680, 0, 0, 0), key="wood_dark", bevel=0.003)

# Front steel locking rod across the front of the barrels at Z = 0.68m, Y = 0.16m
metal_box("lock_rod", (RW - 0.03, 0.010, 0.022), T(RCX, 0.160, 0.680), bevel=0.002, tile=0.3, key="metal")
disc("lock_hinge", 0.008, 0.035, T(RX0 + 0.022, 0.160, 0.680), "metal", seg=12)
metal_box("padlock_body", (0.018, 0.026, 0.032), T(RX1 - 0.022, 0.150, 0.668), bevel=0.002, tile=0.2, key="metal_tin")
tube("padlock_shackle", [
    Vector((RX1 - 0.022, 0.142, 0.686)),
    Vector((RX1 - 0.022, 0.150, 0.704)),
    Vector((RX1 - 0.022, 0.158, 0.686)),
], 0.003, key="metal")

# ---------------------------------------------------------------- 5. Place 3 Upright Weapons in Rack
# Standing upright with yaw=180 (faces forward), leaning back 9 deg against rear crossbar.
# Cleanly centered in their bays, magazines and profiles completely unobstructed!
# Slot 1: AK-74 #1 at X = 0.50
place_gun_upright(r"dynamics\weapons\wpn_ak74\wpn_ak74", Vector((0.50, 0.08, DECK_Z + 0.024)), lean_deg=9, yaw_deg=180, ratio=0.35)
# Slot 2: TOZ-34 Shotgun at X = 0.64
place_gun_upright(r"dynamics\weapons\wpn_toz34\wpn_toz34", Vector((0.64, 0.08, DECK_Z + 0.024)), lean_deg=9, yaw_deg=180, ratio=0.40)
# Slot 3: AK-74 #2 at X = 0.78
place_gun_upright(r"dynamics\weapons\wpn_ak74\wpn_ak74", Vector((0.78, 0.08, DECK_Z + 0.024)), lean_deg=9, yaw_deg=180, ratio=0.35)

# ---------------------------------------------------------------- 6. Tabletop Accents & Props (Z = TABLE_TOP_Z = 0.780m)
TT_Z = TABLE_TOP_Z

# Industrial gooseneck table lamp at back-left (illuminating logbook)
accent(r"dynamics\workshop_room\table_lamp_01", T(DX0 + 0.14, DY1 - 0.14, TT_Z, 0, 0, -35))

# Sentry Duty Logbook / Ledger (Center of desk, angled)
LOG_X, LOG_Y = DCX - 0.05, DCY - 0.01
LOG_M = T(LOG_X, LOG_Y, TT_Z + 0.004, 0, 0, -8)
# Leather binder cover
metal_box("log_cover", (0.32, 0.24, 0.006), LOG_M, bevel=0.002, tile=0.3, key="wood_dark")
# Left & right paper pages
metal_box("log_pages_l", (0.135, 0.21, 0.006), LOG_M @ T(-0.075, 0, 0.004), bevel=0.001, tile=1.0, key="white")
metal_box("log_pages_r", (0.135, 0.21, 0.006), LOG_M @ T(+0.075, 0, 0.004), bevel=0.001, tile=1.0, key="white")
# Ruled checklist lines
for gi in (-0.07, -0.035, 0.0, 0.035, 0.07):
    metal_box("grid_line_l", (0.11, 0.002, 0.001), LOG_M @ T(-0.075, gi, 0.008), bevel=0.0002, tile=0.1, key="red")
    metal_box("grid_line_r", (0.11, 0.002, 0.001), LOG_M @ T(+0.075, gi, 0.008), bevel=0.0002, tile=0.1, key="metal")
# Duty pencil resting in center fold
tube("duty_pencil", [LOG_M @ Vector((0, -0.08, 0.008)), LOG_M @ Vector((0, 0.08, 0.008))], 0.0035, key="red")

# Field binoculars sitting cleanly on the tabletop in clear view
accent(r"dynamics\devices\dev_binoculars\dev_binoculars", T(DCX - 0.18, DY0 + 0.09, TT_Z, 0, 0, 20), ratio=0.40)

# Enamel tin tea mug for sentry
MUG_X, MUG_Y = DX0 + 0.14, DY0 + 0.24
disc("tea_mug_body", 0.036, 0.072, T(MUG_X, MUG_Y, TT_Z + 0.036), "white", seg=16)
disc("tea_mug_rim", 0.037, 0.005, T(MUG_X, MUG_Y, TT_Z + 0.070), "metal_green", seg=16)
disc("tea_liquid", 0.033, 0.004, T(MUG_X, MUG_Y, TT_Z + 0.065), "wood_dark", seg=14)
tube("tea_mug_handle", [
    Vector((MUG_X + 0.036, MUG_Y, TT_Z + 0.060)),
    Vector((MUG_X + 0.062, MUG_Y, TT_Z + 0.045)),
    Vector((MUG_X + 0.036, MUG_Y, TT_Z + 0.020)),
], 0.004, key="white", sides=8)

# Military FM radio at back-right of desk
accent(r"dynamics\devices\dev_fmradio\dev_fmradio", T(DCX + 0.24, DY1 - 0.14, TT_Z, 0, 0, -25))

# Ammunition boxes on desk
accent(r"dynamics\weapons\wpn_ammo\ammo_545x39_fmj", T(DCX + 0.20, DY0 + 0.08, TT_Z, 0, 0, 15))
accent(r"dynamics\weapons\wpn_ammo\ammo_12x70_buck", T(DCX + 0.30, DY0 + 0.20, TT_Z, 0, 0, -20))

# Grenades ready on desk in a small wooden tray
metal_box("grenade_tray", (0.15, 0.11, 0.018), T(DCX + 0.06, DY1 - 0.14, TT_Z + 0.009), bevel=0.002, tile=0.2, key="wood_dark")
accent(r"dynamics\weapons\wpn_grenades\wpn_f1", T(DCX + 0.03, DY1 - 0.14, TT_Z + 0.018, 0, 0, 35), ratio=0.35)
accent(r"dynamics\weapons\wpn_grenades\wpn_rgd5", T(DCX + 0.09, DY1 - 0.14, TT_Z + 0.018, 90, 0, -40), ratio=0.35)

# Spent brass cartridge casings scattered near front edge
for ci, (cx, cy, crot) in enumerate([(DCX - 0.18, DY0 + 0.04, 38), (DCX - 0.24, DY0 + 0.06, -55), (DCX + 0.04, DY0 + 0.03, 14)]):
    disc(f"spent_casing_{ci}", 0.006, 0.036, T(cx, cy, TT_Z + 0.004, 0, 88, crot), "red", seg=8)

# ---------------------------------------------------------------- 7. Join and Save Mainfile
guard_post = join_parts()
