# Build script for the HomesteadHF Raider Station / Tactical Planning Board (run inside Blender).
# Heavy raid command & tactical briefing table with topographic Zone war map, upright recon pinboard,
# field radio transceiver, binoculars, combat knife, sidearm, grenades, and under-table armory storage.
# Uses ONLY vanilla S.T.A.L.K.E.R. Anomaly textures and vanilla .ogf accents.
import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix, Euler

NAME = "raider_station"
BLEND = "raider_station.blend"

SCR = __import__('os').environ.get('HSHF_SCRATCH', r"C:\Anomaly\tools\_test_unpack")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())

start({
    "wood": ("wood\\wood_jasik", "models\\model"),
    "wood_dark": ("wood\\wood_box", "models\\model"),
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "metal_green": ("mtl\\mtl_pod_green", "models\\model"),
    "metal_plate": ("mtl\\mtl_pod_02", "models\\model"),
    "red_paint": ("mtl\\mtl_red_painted", "models\\model"),
    "map_war": ("prop\\prop_map_2", "models\\model"),
    "map_zone": ("prop\\prop_map", "models\\model"),
    "map_plan": ("prop\\prop_map_3", "models\\model"),
    "map_recon": ("prop\\prop_map_dolg", "models\\model"),
})


def disc(name, radius, depth, matrix, key, seg=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = 1.0 / max(radius * 2.2, 1e-4)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)


def map_sheet(name, w, d, thick, matrix, key, u0=0.0, u1=1.0, v0=0.0, v1=1.0):
    """Flat rectangular board/sheet with top face (+Z in local space) mapped to [u0..u1, v0..v1]."""
    bm = beveled_box(Vector((w, d, thick)), min(0.001, thick * 0.3))
    uvl = bm.loops.layers.uv.new("Texture")
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co
            tx = max(0.0, min(1.0, p.x / w + 0.5))
            ty = max(0.0, min(1.0, p.y / d + 0.5))
            l[uvl].uv = (u0 + tx * (u1 - u0), v0 + ty * (v1 - v0))
    return finish(bm, name, [key], matrix, smooth_angle=35)


def pushpin(name, x, y, z, key_head="red_paint"):
    """Tactical map pushpin with steel needle and coloured plastic/brass head."""
    disc(name + "_needle", 0.0018, 0.012, T(x, y, z + 0.006), "metal", seg=8)
    disc(name + "_base", 0.0065, 0.004, T(x, y, z + 0.012), key_head, seg=10)
    disc(name + "_top", 0.0085, 0.005, T(x, y, z + 0.018), key_head, seg=10)


def board_pin(name, x, y, z, key_head="red_paint"):
    """Horizontal pushpin pressed into the vertical recon backboard (-Y normal)."""
    disc(name + "_needle", 0.0018, 0.010, T(x, y - 0.005, z, 90, 0, 0), "metal", seg=8)
    disc(name + "_head", 0.0080, 0.006, T(x, y - 0.011, z, 90, 0, 0), key_head, seg=10)


def accent_flush(rel, x, y, target_z, rx=0, ry=0, rz=0, scale=None, ratio=None):
    """Import a vanilla .ogf, apply rotation & scale first, then snap its post-rotation bottom-centre to (x, y, target_z)."""
    new, _ = import_ogf(rel, NAME + "_accents")
    meshes = [o for o in new if o.type == 'MESH' and not any("addon" in (m.name if m else "") for m in o.data.materials)]
    rot_m = Euler((math.radians(rx), math.radians(ry), math.radians(rz))).to_matrix().to_4x4()
    s_m = Matrix.Diagonal((scale, scale, scale, 1.0)) if scale else Matrix.Identity(4)
    xf = rot_m @ s_m
    pts = [xf @ (o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    snap = Matrix.Translation((x - (lo.x + hi.x) / 2, y - (lo.y + hi.y) / 2, target_z - lo.z))
    keep = []
    for o in meshes:
        for mod in list(o.modifiers):
            o.modifiers.remove(mod)
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = snap @ xf @ mw
        if ratio:
            mod = o.modifiers.new("dec", 'DECIMATE'); mod.ratio = ratio
            bpy.context.view_layer.objects.active = o
            with bpy.context.temp_override(object=o):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        COL.objects.link(o)
        keep.append(o)
    for o in new:
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    PARTS.extend(keep)
    return keep, (hi - lo)


# ---------------------------------------------------------------- 1. Heavy Command Table Steel Frame
TL = 1.60   # Table length along X [-0.80, +0.80]
TD = 0.84   # Table depth along Y [-0.42, +0.42]
TABLE_TOP_Z = 0.850
LEG_H = TABLE_TOP_Z - 0.038  # 0.812m
LEG_S = 0.055

LX0, LX1 = -TL / 2 + 0.065, TL / 2 - 0.065  # -0.735, +0.735
LY0, LY1 = -TD / 2 + 0.055, TD / 2 - 0.055  # -0.365, +0.365

for lx in (LX0, LX1):
    for ly in (LY0, LY1):
        metal_box("foot_pad", (0.085, 0.085, 0.008), T(lx, ly, 0.004), bevel=0.001, tile=0.3, key="metal")
        disc("anchor_bolt_1", 0.005, 0.006, T(lx - 0.03, ly - 0.03, 0.010), "metal", seg=8)
        disc("anchor_bolt_2", 0.005, 0.006, T(lx + 0.03, ly + 0.03, 0.010), "metal", seg=8)
        metal_box("table_leg", (LEG_S, LEG_S, LEG_H), T(lx, ly, LEG_H / 2 + 0.008), bevel=0.003, tile=0.4, key="metal_green")
        metal_box("leg_top_flange", (0.09, 0.09, 0.010), T(lx, ly, LEG_H + 0.003), bevel=0.001, tile=0.3, key="metal")

# Top apron rails
APRON_H = 0.065
APRON_TH = 0.028
APRON_Z = TABLE_TOP_Z - 0.036 - APRON_H / 2
metal_box("apron_f", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_b", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY1, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_l", (APRON_TH, LY1 - LY0, APRON_H), T(LX0, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_r", (APRON_TH, LY1 - LY0, APRON_H), T(LX1, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")

for lx, sx in ((LX0, +1), (LX1, -1)):
    for ly, sy in ((LY0, +1), (LY1, -1)):
        metal_box("corner_gusset", (0.055, 0.055, 0.006), T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z), bevel=0.001, tile=0.2, key="metal")
        rivet(T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z + 0.005))

# ---------------------------------------------------------------- 2. Lower Armory & Comms Shelf (Z = 0.190m)
SHELF_Z = 0.190
metal_box("stretcher_f", (LX1 - LX0, 0.035, 0.035), T(0, LY0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_b", (LX1 - LX0, 0.035, 0.035), T(0, LY1, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_l", (0.035, LY1 - LY0, 0.035), T(LX0, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_r", (0.035, LY1 - LY0, 0.035), T(LX1, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")

SHELF_TOP_Z = SHELF_Z + 0.0175 + 0.024
SHELF_W = (LY1 - LY0 - 0.01) / 4
for si in range(4):
    spy = (LY0 + 0.02) + SHELF_W / 2 + si * SHELF_W
    plank(f"shelf_plank_{si}", LX1 - LX0 + 0.04, SHELF_W - 0.004, 0.024, T(0, spy, SHELF_Z + 0.0175 + 0.012, 90, 0, 0), key="wood_dark", bevel=0.003)

# ---------------------------------------------------------------- 3. Main Command Tabletop & Steel Map Bezel (Z = 0.850m)
TOP_PLANK_W = (TD - 0.012) / 5
for pi in range(5):
    py = -TD / 2 + TOP_PLANK_W / 2 + pi * (TOP_PLANK_W + 0.002)
    plank(f"top_plank_{pi}", TL, TOP_PLANK_W - 0.003, 0.036, T(0, py, TABLE_TOP_Z - 0.018, 90, 0, 0), key="wood", bevel=0.003)

# Riveted steel map-table perimeter rim (keeps maps & brass cartridges from rolling off)
RIM_H = 0.012
RIM_TH = 0.014
metal_box("rim_f", (TL + 0.008, RIM_TH, RIM_H), T(0, -TD / 2 + RIM_TH / 2, TABLE_TOP_Z + RIM_H / 2 - 0.002), bevel=0.001, tile=0.3, key="metal")
metal_box("rim_b", (TL + 0.008, RIM_TH, RIM_H), T(0, +TD / 2 - RIM_TH / 2, TABLE_TOP_Z + RIM_H / 2 - 0.002), bevel=0.001, tile=0.3, key="metal")
metal_box("rim_l", (RIM_TH, TD - 2 * RIM_TH, RIM_H), T(-TL / 2 + RIM_TH / 2, 0, TABLE_TOP_Z + RIM_H / 2 - 0.002), bevel=0.001, tile=0.3, key="metal")
metal_box("rim_r", (RIM_TH, TD - 2 * RIM_TH, RIM_H), T(+TL / 2 - RIM_TH / 2, 0, TABLE_TOP_Z + RIM_H / 2 - 0.002), bevel=0.001, tile=0.3, key="metal")

# ---------------------------------------------------------------- 4. Tabletop Tactical War Map & Breach Schematic
# Main Military Topographic Map with red target circles & attack arrows (prop_map_2)
MAP_CX, MAP_CY = -0.14, -0.02
MAP_W, MAP_D = 0.78, 0.62
MAP_Z = TABLE_TOP_Z + 0.002
MAP_TOP_Z = MAP_Z + 0.002
map_sheet("table_war_map", MAP_W, MAP_D, 0.004, T(MAP_CX, MAP_CY, MAP_Z, 0, 0, 1.5), "map_war",
          u0=0.04, u1=0.90, v0=0.03, v1=0.97)

# Steel corner hold-down weights on the main war map
for sx in (-1, 1):
    for sy in (-1, 1):
        wx = MAP_CX + sx * (MAP_W / 2 - 0.028)
        wy = MAP_CY + sy * (MAP_D / 2 - 0.028)
        metal_box("map_weight", (0.045, 0.018, 0.005), T(wx, wy, MAP_TOP_Z + 0.0025, 0, 0, sx * sy * 45), bevel=0.001, tile=0.2, key="metal_plate")

# Tactical Pushpins & Red Attack-Route Cord on the War Map
PIN_PTS = [
    (-0.34, +0.10),   # North-west staging point
    (-0.24, +0.04),   # Primary objective circle
    (-0.08, -0.06),   # Central crossroads stronghold
    (-0.20, -0.18),   # Southern approach
    (+0.10, -0.08),   # Eastern flank target
]
for idx, (px, py) in enumerate(PIN_PTS):
    pushpin(f"map_pin_{idx}", px, py, MAP_TOP_Z, key_head="red_paint" if idx in (1, 2, 4) else "metal_plate")

# Red tactical string linking staging point -> primary objective -> central stronghold -> eastern flank
tube("raid_route_cord_1", [
    Vector((PIN_PTS[0][0], PIN_PTS[0][1], MAP_TOP_Z + 0.004)),
    Vector((PIN_PTS[1][0], PIN_PTS[1][1], MAP_TOP_Z + 0.004)),
    Vector((PIN_PTS[2][0], PIN_PTS[2][1], MAP_TOP_Z + 0.004)),
    Vector((PIN_PTS[4][0], PIN_PTS[4][1], MAP_TOP_Z + 0.004)),
], 0.0022, key="red_paint", sides=6)

tube("raid_route_cord_2", [
    Vector((PIN_PTS[3][0], PIN_PTS[3][1], MAP_TOP_Z + 0.004)),
    Vector((PIN_PTS[2][0], PIN_PTS[2][1], MAP_TOP_Z + 0.004)),
], 0.0022, key="red_paint", sides=6)

# Secondary Outpost Facility Schematic / Breach Blueprint (prop_map_3) on right side of tabletop
PLAN_CX, PLAN_CY = +0.46, -0.06
PLAN_W, PLAN_D = 0.36, 0.34
map_sheet("table_breach_plan", PLAN_W, PLAN_D, 0.003, T(PLAN_CX, PLAN_CY, MAP_Z, 0, 0, -9), "map_plan",
          u0=0.02, u1=0.98, v0=0.02, v1=0.98)
pushpin("plan_pin_1", PLAN_CX - 0.06, PLAN_CY + 0.05, MAP_TOP_Z, key_head="red_paint")
pushpin("plan_pin_2", PLAN_CX + 0.07, PLAN_CY - 0.04, MAP_TOP_Z, key_head="red_paint")

# ---------------------------------------------------------------- 5. Upright Tactical Recon Backboard & Overhead Shelf
UPRIGHT_H = 0.640
UPRIGHT_Z = TABLE_TOP_Z + UPRIGHT_H / 2
metal_box("backboard_post_l", (0.045, 0.045, UPRIGHT_H), T(LX0, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")
metal_box("backboard_post_r", (0.045, 0.045, UPRIGHT_H), T(LX1, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")
metal_box("backboard_post_m", (0.038, 0.038, UPRIGHT_H), T(0.18, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")

BOARD_H = 0.500
BOARD_Z = TABLE_TOP_Z + BOARD_H / 2 + 0.030
BOARD_Y = LY1 + 0.014
plank("recon_backboard", LX1 - LX0, BOARD_H, 0.022, T(0, BOARD_Y, BOARD_Z, 0, 0, 0), key="wood_dark", bevel=0.003)

# Steel perimeter frame around the recon board
metal_box("board_frame_t", (LX1 - LX0 + 0.04, 0.028, 0.020), T(0, BOARD_Y - 0.004, BOARD_Z + BOARD_H / 2 + 0.005), bevel=0.001, tile=0.3, key="metal")
metal_box("board_frame_b", (LX1 - LX0 + 0.04, 0.028, 0.020), T(0, BOARD_Y - 0.004, BOARD_Z - BOARD_H / 2 - 0.005), bevel=0.001, tile=0.3, key="metal")

# Left/Center of Backboard: Two-Panel Soviet General Staff Zone Map (prop_map)
# Note: with rx=90, local +Y points down (-Z), so v0=0.97, v1=0.03 puts the map header upright at +Z!
BOARD_FRONT_Y = BOARD_Y - 0.013
map_sheet("board_zone_chart", 0.82, 0.42, 0.004, T(-0.24, BOARD_FRONT_Y, BOARD_Z, 90, 0, 0), "map_zone",
          u0=0.01, u1=0.99, v0=0.97, v1=0.03)

# Pushpins & red string on the upright Zone chart
for bx, bz in ((-0.60, BOARD_Z + 0.17), (+0.12, BOARD_Z + 0.17), (-0.60, BOARD_Z - 0.17), (+0.12, BOARD_Z - 0.17)):
    board_pin("chart_corner_pin", bx, BOARD_FRONT_Y, bz, key_head="metal_plate")
for bx, bz in ((-0.42, BOARD_Z + 0.06), (-0.18, BOARD_Z - 0.04), (+0.02, BOARD_Z + 0.08)):
    board_pin("chart_target_pin", bx, BOARD_FRONT_Y, bz, key_head="red_paint")
tube("board_route_cord", [
    Vector((-0.42, BOARD_FRONT_Y - 0.005, BOARD_Z + 0.06)),
    Vector((-0.18, BOARD_FRONT_Y - 0.005, BOARD_Z - 0.04)),
    Vector((+0.02, BOARD_FRONT_Y - 0.005, BOARD_Z + 0.08)),
], 0.0020, key="red_paint", sides=6)

# Right of Backboard: Annotated Aerial Recon Photo (prop_map_dolg, right-side-up with v0=0.98, v1=0.02)
map_sheet("board_recon_photo", 0.40, 0.40, 0.004, T(+0.46, BOARD_FRONT_Y, BOARD_Z, 90, 0, 0), "map_recon",
          u0=0.02, u1=0.98, v0=0.98, v1=0.02)
for bx, bz in ((+0.29, BOARD_Z + 0.16), (+0.63, BOARD_Z + 0.16), (+0.48, BOARD_Z - 0.02)):
    board_pin("recon_pin", bx, BOARD_FRONT_Y, bz, key_head="red_paint")

# Overhead Comms & Intel Shelf at Z = 1.490m
TOP_SHELF_Z = TABLE_TOP_Z + UPRIGHT_H
plank("top_shelf_plank", TL - 0.04, 0.24, 0.024, T(0, LY1 - 0.07, TOP_SHELF_Z + 0.012, 90, 0, 0), key="wood", bevel=0.003)
metal_box("top_shelf_curb", (TL - 0.04, 0.015, 0.032), T(0, LY1 - 0.19, TOP_SHELF_Z + 0.024), bevel=0.001, tile=0.3, key="metal")

# ---------------------------------------------------------------- 6. Vanilla .OGF Accents — Tabletop (100% Flush Snapped)
# Gooseneck command lamp clamped at back-left, illuminating the war map
accent_flush(r"dynamics\workshop_room\table_lamp_01", -0.66, +0.20, TABLE_TOP_Z, rz=45)

# Handheld walkie-talkie / FM radio standing at front-left of table
accent_flush(r"dynamics\devices\dev_fmradio\dev_fmradio", -0.67, -0.18, TABLE_TOP_Z, rz=28)

# Military field binoculars resting near upper-left of war map
accent_flush(r"dynamics\devices\dev_binoculars\dev_binoculars", -0.43, +0.21, MAP_TOP_Z, rz=-25)

# Stalker tactical PDA resting near front-left of war map
accent_flush(r"dynamics\devices\dev_pda\dev_pda", -0.46, -0.25, MAP_TOP_Z, rz=18)

# Combat knife resting flat across the bottom-left corner of the breach blueprint
accent_flush(r"dynamics\weapons\wpn_knife\wpn_knife_combat", +0.31, -0.24, MAP_TOP_Z, ry=90, rz=35)

# Stechkin APS sidearm resting flat at front-right of tabletop
accent_flush(r"dynamics\weapons\wpn_aps\wpn_aps", +0.56, -0.28, TABLE_TOP_Z, ry=90, rz=-15)

# 5.45x39 & 9x39 ammunition packs and F-1 / RGD-5 hand grenades at back-right of tabletop
accent_flush(r"dynamics\weapons\wpn_ammo\ammo_545x39_fmj", +0.42, +0.24, TABLE_TOP_Z, rz=-8)
accent_flush(r"dynamics\weapons\wpn_ammo\ammo_9x39_pab9", +0.61, +0.25, TABLE_TOP_Z, rz=12)
accent_flush(r"dynamics\weapons\wpn_grenades\wpn_f1", +0.66, +0.08, TABLE_TOP_Z, rz=20)
accent_flush(r"dynamics\weapons\wpn_grenades\wpn_rgd5", +0.69, -0.04, TABLE_TOP_Z, rz=-25)

# ---------------------------------------------------------------- 7. Vanilla .OGF Accents — Overhead Shelf (Z = TOP_SHELF_Z + 0.024)
SHELF_HI_Z = TOP_SHELF_Z + 0.024
# Classified recon dossier folders & raid logbook (scaled to fit wholly within the 0.24m shelf depth)
accent_flush(r"dynamics\equipments\documents_1", -0.46, LY1 - 0.06, SHELF_HI_Z, rz=88, scale=0.48)
accent_flush(r"dynamics\equipments\quest\notes_writing_book_1", -0.06, LY1 - 0.06, SHELF_HI_Z, rz=82, scale=0.56)
# Ammunition & ordnance toolkit box on right of overhead shelf
accent_flush(r"dynamics\equipments\quest\box_toolkit_ammo", +0.42, LY1 - 0.06, SHELF_HI_Z, rz=-4)

# ---------------------------------------------------------------- 8. Vanilla .OGF Accents — Lower Armory Shelf (300 kg Storage)
# Left: Soviet military field radio transceiver (scaled 0.56x to fit cleanly under tabletop apron)
accent_flush(r"dynamics\el_tehnika\transiver", -0.48, +0.02, SHELF_TOP_Z, rz=8, scale=0.56)

# Center: Heavy olive-drab military weapon/ordnance crate
_, crate_sz = accent_flush(r"dynamics\equipments\green_box", +0.06, +0.02, SHELF_TOP_Z, rz=2, scale=0.85)

# 9A-91 compact assault carbine resting flat directly on top of the military crate lid!
CRATE_TOP_Z = SHELF_TOP_Z + crate_sz.z - 0.008
accent_flush(r"dynamics\weapons\wpn_9a91\wpn_9a91", +0.06, +0.02, CRATE_TOP_Z, ry=-90, rz=82)

# Right: C4 demolition charge case and stacked 5.56x45 / 7.62x54R ammo boxes
accent_flush(r"dynamics\equipments\bomb_c4", +0.52, +0.04, SHELF_TOP_Z, rz=88, scale=0.62)
_, ammo1_sz = accent_flush(r"dynamics\weapons\wpn_ammo\ammo_556x45_ss190", +0.50, -0.22, SHELF_TOP_Z, rz=6)
accent_flush(r"dynamics\weapons\wpn_ammo\ammo_762x54_7h1", +0.50, -0.22, SHELF_TOP_Z + ammo1_sz.z, rz=-10)

# ---------------------------------------------------------------- Join all parts into raider_station_visual
visual = join_parts()

try:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SCR, "models", BLEND))
    print(f'Info: Saved copy as "{BLEND}"')
except Exception as e:
    print(e)
