# Build script for the HomesteadHF Chemist Station (run inside Blender).
# Heavy industrial Zone chemistry & propellant/fuel synthesis workbench with fractional distillation
# column, copper Liebig condenser coil, multi-fuel retort burner, nitration & gunpowder drying tray,
# overhead reagent rack, and authentic vanilla S.T.A.L.K.E.R. Anomaly .ogf accents.
import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix, Euler

NAME = "chemist_station"
BLEND = "chemist_station.blend"

os.environ.setdefault("HSHF_SCRATCH", r"C:\Anomaly\tools\_test_unpack")
os.environ.setdefault("HSHF_VANILLA_MESHES", r"C:\Anomaly\tools\_test_unpack\meshes")
os.environ.setdefault("HSHF_VANILLA_TEX", r"C:\Anomaly\tools\_test_unpack\textures")

SCR = os.environ["HSHF_SCRATCH"]
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())

start({
    "wood": ("wood\\wood_jasik", "models\\model"),
    "wood_dark": ("wood\\wood_box", "models\\model"),
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "metal_green": ("mtl\\mtl_pod_green", "models\\model"),
    "metal_plate": ("mtl\\mtl_pod_02", "models\\model"),
    "pipe": ("mtl\\mtl_barrel_big_rust", "models\\model"),
    "copper": ("mtl\\mtl_red_paint_iov", "models\\model"),
    "red": ("mtl\\mtl_red_painted", "models\\model"),
    "glass": ("glas\\glas_dirt", "models\\model"),
    "charcoal_mat": ("grnd\\grnd_dirt_dark", "models\\model"),
    "white": ("wall\\wall_house_white_01", "models\\model"),
}, seed=4182)


def disc(name, radius, depth, matrix, key, seg=18, uv_scale=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = uv_scale or (1.0 / max(radius * 2.2, 0.02))
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)


def cone_part(name, r1, r2, depth, matrix, key, seg=18):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    rm = max(r1, r2, 0.02)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x / (rm * 2.2), 0.5 + l.vert.co.y / (rm * 2.2))
    return finish(bm, name, [key], matrix, smooth_angle=55)


# ---------------------------------------------------------------- 1. Workbench Structural Steel Frame
TL = 1.64   # Table length along X [-0.82, +0.82]
TD = 0.82   # Table depth along Y [-0.41, +0.41]
TABLE_TOP_Z = 0.860
LEG_H = TABLE_TOP_Z - 0.038  # 0.822m
LEG_S = 0.055

LX0, LX1 = -TL / 2 + 0.065, TL / 2 - 0.065  # -0.755, +0.755
LY0, LY1 = -TD / 2 + 0.055, TD / 2 - 0.055  # -0.355, +0.355

# 4 heavy painted steel angle/post legs with bolted foot pads and top flanges
for lx in (LX0, LX1):
    for ly in (LY0, LY1):
        metal_box("foot_pad", (0.085, 0.085, 0.008), T(lx, ly, 0.004), bevel=0.001, tile=0.3, key="metal")
        disc("anchor_bolt_1", 0.005, 0.006, T(lx - 0.03, ly - 0.03, 0.010), "metal", seg=8)
        disc("anchor_bolt_2", 0.005, 0.006, T(lx + 0.03, ly + 0.03, 0.010), "metal", seg=8)
        metal_box("table_leg", (LEG_S, LEG_S, LEG_H), T(lx, ly, LEG_H / 2 + 0.008), bevel=0.003, tile=0.4, key="metal_green")
        metal_box("leg_top_flange", (0.09, 0.09, 0.010), T(lx, ly, LEG_H + 0.003), bevel=0.001, tile=0.3, key="metal")

# Top apron frame connecting leg tops
APRON_H = 0.065
APRON_TH = 0.028
APRON_Z = TABLE_TOP_Z - 0.036 - APRON_H / 2
metal_box("apron_f", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_b", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY1, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_l", (APRON_TH, LY1 - LY0, APRON_H), T(LX0, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_r", (APRON_TH, LY1 - LY0, APRON_H), T(LX1, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")

# Welded diagonal corner gussets with rivets
for lx, sx in ((LX0, +1), (LX1, -1)):
    for ly, sy in ((LY0, +1), (LY1, -1)):
        metal_box("corner_gusset", (0.055, 0.055, 0.006), T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z), bevel=0.001, tile=0.2, key="metal")
        rivet(T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z + 0.005))

# ---------------------------------------------------------------- 2. Lower Stretcher Shelf (Z = 0.18m)
SHELF_Z = 0.180
metal_box("stretcher_f", (LX1 - LX0, 0.035, 0.035), T(0, LY0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_b", (LX1 - LX0, 0.035, 0.035), T(0, LY1, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_l", (0.035, LY1 - LY0, 0.035), T(LX0, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_r", (0.035, LY1 - LY0, 0.035), T(LX1, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")

# 4 heavy lower shelf planks laid flat (rx=90)
SHELF_W = (LY1 - LY0 - 0.01) / 4
for si in range(4):
    spy = (LY0 + 0.02) + SHELF_W / 2 + si * SHELF_W
    plank(f"shelf_plank_{si}", LX1 - LX0 + 0.04, SHELF_W - 0.004, 0.024, T(0, spy, SHELF_Z + 0.0295, 90, 0, 0), key="wood_dark", bevel=0.003)

# ---------------------------------------------------------------- 3. Main Workbench Tabletop & Chemical Spill Tray (Z = 0.860m)
TOP_PLANK_W = (TD - 0.012) / 5
for pi in range(5):
    py = -TD / 2 + TOP_PLANK_W / 2 + pi * (TOP_PLANK_W + 0.002)
    plank(f"top_plank_{pi}", TL, TOP_PLANK_W - 0.003, 0.036, T(0, py, TABLE_TOP_Z - 0.018, 90, 0, 0), key="wood", bevel=0.003)

# Galvanized / lead-lined chemical spill tray covering center & right reaction zone (X: -0.22 to +0.80)
PLATE_X0, PLATE_X1 = -0.22, TL / 2 - 0.02
PLATE_W = PLATE_X1 - PLATE_X0
PLATE_D = TD - 0.04
PLATE_CX = (PLATE_X0 + PLATE_X1) / 2
metal_box("chem_spill_plate", (PLATE_W, PLATE_D, 0.006), T(PLATE_CX, 0, TABLE_TOP_Z + 0.003), bevel=0.001, tile=0.5, key="metal_plate")

# Low raised spill-containment lip around the galvanized chemical plate
LIP_H = 0.014
for sy in (-1, 1):
    metal_box("spill_lip_x", (PLATE_W, 0.008, LIP_H), T(PLATE_CX, sy * (PLATE_D / 2 - 0.004), TABLE_TOP_Z + LIP_H / 2), bevel=0.001, key="metal")
for sx in (-1, 1):
    metal_box("spill_lip_y", (0.008, PLATE_D - 0.016, LIP_H), T(PLATE_CX + sx * (PLATE_W / 2 - 0.004), 0, TABLE_TOP_Z + LIP_H / 2), bevel=0.001, key="metal")

for bx in (PLATE_X0 + 0.04, PLATE_CX, PLATE_X1 - 0.04):
    for by in (-PLATE_D / 2 + 0.035, +PLATE_D / 2 - 0.035):
        disc("plate_bolt", 0.006, 0.003, T(bx, by, TABLE_TOP_Z + 0.006), "metal", seg=8)

# ---------------------------------------------------------------- 4. Rear Vertical Reagent Rack & Fume Baffle Hood
UPRIGHT_H = 0.640
UPRIGHT_Z = TABLE_TOP_Z + UPRIGHT_H / 2
for ux in (LX0, 0.0, LX1):
    metal_box("rack_post", (0.042, 0.042, UPRIGHT_H), T(ux, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")

# Lower slatted timber backboard (Z: 0.89m to 1.15m)
plank("backboard_low", LX1 - LX0, 0.12, 0.020, T(0, LY1 + 0.015, TABLE_TOP_Z + 0.09, 0, 0, 0), key="wood_dark", bevel=0.003)
plank("backboard_high", LX1 - LX0, 0.12, 0.020, T(0, LY1 + 0.015, TABLE_TOP_Z + 0.22, 0, 0, 0), key="wood_dark", bevel=0.003)

# Middle reagent shelf at Z = 1.18m with tubular steel retaining guard rail
MID_SHELF_Z = 1.180
MID_SHELF_D = 0.20
MID_SHELF_Y = LY1 - MID_SHELF_D / 2 + 0.02
plank("mid_shelf_plank", TL - 0.06, MID_SHELF_D, 0.022, T(0, MID_SHELF_Y, MID_SHELF_Z, 90, 0, 0), key="wood", bevel=0.003)
for sx in (-1, 0, 1):
    bx = sx * (LX1 - 0.02)
    metal_box("mid_shelf_bracket", (0.018, MID_SHELF_D, 0.028), T(bx, MID_SHELF_Y, MID_SHELF_Z - 0.022), bevel=0.002, key="metal")
# Retaining rod across front of middle shelf so reagent jars don't tip
GUARD_Y = MID_SHELF_Y - MID_SHELF_D / 2 + 0.012
GUARD_Z = MID_SHELF_Z + 0.042
tube("mid_shelf_guard", [Vector((-TL / 2 + 0.05, GUARD_Y, GUARD_Z)), Vector((TL / 2 - 0.05, GUARD_Y, GUARD_Z))], 0.005, key="metal", sides=8, vscale=3.0)
for gx in (-TL / 2 + 0.06, 0.0, TL / 2 - 0.06):
    tube("guard_post", [Vector((gx, GUARD_Y, MID_SHELF_Z + 0.01)), Vector((gx, GUARD_Y, GUARD_Z + 0.005))], 0.005, key="metal", sides=8)

# Upper overhead shelf & fume baffle canopy at Z = 1.48m
TOP_SHELF_Z = TABLE_TOP_Z + UPRIGHT_H - 0.02
TOP_SHELF_D = 0.22
TOP_SHELF_Y = LY1 - TOP_SHELF_D / 2 + 0.02
plank("top_shelf_plank", TL - 0.04, TOP_SHELF_D, 0.024, T(0, TOP_SHELF_Y, TOP_SHELF_Z, 90, 0, 0), key="wood", bevel=0.003)
# Front retaining curb & fume baffle visor along the top shelf
metal_box("top_shelf_curb", (TL - 0.04, 0.014, 0.032), T(0, TOP_SHELF_Y - TOP_SHELF_D / 2 + 0.007, TOP_SHELF_Z + 0.020), bevel=0.001, tile=0.3, key="metal")
metal_box("fume_hood_visor", (TL - 0.04, 0.010, 0.048), T(0, TOP_SHELF_Y - TOP_SHELF_D / 2 + 0.005, TOP_SHELF_Z - 0.016, 12, 0, 0), bevel=0.002, tile=0.4, key="metal_green")
for rx in (-0.65, -0.22, 0.22, 0.65):
    rivet(T(rx, TOP_SHELF_Y - TOP_SHELF_D / 2 - 0.002, TOP_SHELF_Z + 0.005, 90, 0, 0))

# ---------------------------------------------------------------- 5. Fractional Fuel Cracking & Condenser Column (Right Side)
# Distills raw alcohol + charcoal into high-grade Kerosene & Gasoline
COL_X, COL_Y = 0.44, 0.14
BZ = TABLE_TOP_Z + 0.006

# Flanged heavy steel boiler base & vertical fractionating column
disc("still_base_flange", 0.105, 0.016, T(COL_X, COL_Y, BZ + 0.008), "metal", seg=20)
for ang in range(0, 360, 60):
    rad = math.radians(ang)
    disc("flange_bolt", 0.006, 0.008, T(COL_X + math.cos(rad) * 0.088, COL_Y + math.sin(rad) * 0.088, BZ + 0.018), "metal", seg=8)

disc("still_boiler_drum", 0.082, 0.24, T(COL_X, COL_Y, BZ + 0.136), "pipe", seg=20, uv_scale=2.2)
cone_part("still_reducer", 0.082, 0.046, 0.055, T(COL_X, COL_Y, BZ + 0.283), "metal", seg=20)
# Upper fractionating column with 3 riveted reinforcing bands
disc("still_column", 0.044, 0.24, T(COL_X, COL_Y, BZ + 0.430), "pipe", seg=18, uv_scale=3.0)
for rz in (BZ + 0.34, BZ + 0.43, BZ + 0.52):
    disc("column_band", 0.049, 0.016, T(COL_X, COL_Y, rz), "metal", seg=18)
disc("column_top_cap", 0.054, 0.018, T(COL_X, COL_Y, BZ + 0.558), "metal_plate", seg=18)

# Analog pressure gauge mounted on front of column
tube("gauge_stem", [Vector((COL_X, COL_Y - 0.044, BZ + 0.38)), Vector((COL_X, COL_Y - 0.082, BZ + 0.38))], 0.007, key="copper", sides=8)
disc("gauge_body", 0.034, 0.016, T(COL_X, COL_Y - 0.090, BZ + 0.38, 90, 0, 0), "metal", seg=18)
disc("gauge_face", 0.028, 0.004, T(COL_X, COL_Y - 0.098, BZ + 0.38, 90, 0, 0), "white", seg=18)
metal_box("gauge_needle", (0.004, 0.003, 0.022), T(COL_X + 0.004, COL_Y - 0.101, BZ + 0.385, 0, 35, 0), bevel=0.0005, key="red")

# Vanilla cast-iron valve wheel on the boiler feed manifold (repainted with vanilla mtl_red_painted)
tube("valve_stem", [Vector((COL_X - 0.082, COL_Y - 0.02, BZ + 0.16)), Vector((COL_X - 0.115, COL_Y - 0.02, BZ + 0.16))], 0.009, key="metal", sides=10)
_wheel = accent(r"dynamics\workshop_room\ventil_01", T(COL_X - 0.120, COL_Y - 0.02, BZ + 0.16, 0, -90, 0), scale=0.26)
for _o in _wheel:
    _o.data.materials.clear()
    _o.data.materials.append(MAT["red"])

# Water-Jacketed Glass Liebig Condenser & Internal Copper Spiral Coil (X = +0.18, Y = +0.08)
COND_X, COND_Y, COND_Z = 0.18, 0.08, BZ + 0.25
# Heavy laboratory support stand behind the condenser
metal_box("cond_stand_base", (0.11, 0.13, 0.010), T(COND_X, COND_Y + 0.08, BZ + 0.005), bevel=0.002, key="metal")
tube("cond_stand_rod", [Vector((COND_X, COND_Y + 0.11, BZ + 0.01)), Vector((COND_X, COND_Y + 0.11, BZ + 0.44))], 0.007, key="metal", sides=10)
for cz in (COND_Z - 0.06, COND_Z + 0.06):
    metal_box("cond_bosshead", (0.022, 0.032, 0.022), T(COND_X, COND_Y + 0.10, cz), bevel=0.002, key="metal")
    tube("cond_clamp_arm", [Vector((COND_X, COND_Y + 0.09, cz)), Vector((COND_X, COND_Y + 0.03, cz))], 0.005, key="metal", sides=8)
    disc("cond_clamp_ring", 0.044, 0.012, T(COND_X, COND_Y, cz), "metal", seg=16)

# Glass condenser outer jacket & brass end caps
disc("cond_glass_jacket", 0.038, 0.20, T(COND_X, COND_Y, COND_Z), "glass", seg=18, uv_scale=2.5)
disc("cond_cap_top", 0.042, 0.016, T(COND_X, COND_Y, COND_Z + 0.104), "copper", seg=18)
disc("cond_cap_bot", 0.042, 0.016, T(COND_X, COND_Y, COND_Z - 0.104), "copper", seg=18)

# Internal helical copper cooling coil visible inside the glass jacket
coil_pts = []
for i in range(25):
    t_frac = i / 24.0
    ang = t_frac * 4.0 * 2.0 * math.pi
    coil_pts.append(Vector((COND_X + math.cos(ang) * 0.018, COND_Y + math.sin(ang) * 0.018, (COND_Z + 0.085) - t_frac * 0.17)))
tube("copper_condenser_coil", coil_pts, 0.0045, key="copper", sides=7, vscale=6.0)

# Overhead copper vapor lyne arm connecting column top to condenser top
vapor_pts = [
    Vector((COL_X, COL_Y, BZ + 0.565)),
    Vector((COL_X, COL_Y, BZ + 0.610)),
    Vector(((COL_X + COND_X) / 2, (COL_Y + COND_Y) / 2, BZ + 0.590)),
    Vector((COND_X, COND_Y, COND_Z + 0.155)),
    Vector((COND_X, COND_Y, COND_Z + 0.110)),
]
tube("copper_vapor_pipe", vapor_pts, 0.011, key="copper", sides=10, vscale=4.0)

# Distillate outlet spout curving from bottom of condenser into the 3L glass receiver carboy at (0.18, -0.10)
RCV_X, RCV_Y = 0.18, -0.10
spout_pts = [
    Vector((COND_X, COND_Y, COND_Z - 0.112)),
    Vector((COND_X, COND_Y - 0.03, BZ + 0.125)),
    Vector((RCV_X, RCV_Y, BZ + 0.155)),
    Vector((RCV_X, RCV_Y, BZ + 0.130)),
]
tube("distillate_spout", spout_pts, 0.006, key="copper", sides=8, vscale=5.0)

# ---------------------------------------------------------------- 6. Nitration Retort & Burner Assembly (Center-Left)
BURN_X, BURN_Y = -0.08, 0.04
# Vanilla portable multi-fuel stove sitting on the spill plate
accent(r"dynamics\cooking\multi_fuel_stove", T(BURN_X, BURN_Y, BZ, 0, 0, 15))

# Steel tripod Heating Stand straddling the stove burner
RING_Z = BZ + 0.165
disc("tripod_ring", 0.068, 0.010, T(BURN_X, BURN_Y, RING_Z), "metal", seg=18)
metal_box("wire_gauze_pad", (0.11, 0.11, 0.004), T(BURN_X, BURN_Y, RING_Z + 0.007), bevel=0.001, tile=0.2, key="metal_plate")
for ang in (35, 155, 275):
    rad = math.radians(ang)
    tx, ty = BURN_X + math.cos(rad) * 0.064, BURN_Y + math.sin(rad) * 0.064
    bx_foot, by_foot = BURN_X + math.cos(rad) * 0.095, BURN_Y + math.sin(rad) * 0.095
    tube("tripod_leg", [Vector((bx_foot, by_foot, BZ)), Vector((tx, ty, RING_Z))], 0.0055, key="metal", sides=8)

# Two-stage glass boiling retort flask sitting on the wire gauze pad
FLASK_Z = RING_Z + 0.009
cone_part("flask_lower", 0.036, 0.062, 0.055, T(BURN_X, BURN_Y, FLASK_Z + 0.0275), "glass", seg=18)
cone_part("flask_upper", 0.062, 0.020, 0.055, T(BURN_X, BURN_Y, FLASK_Z + 0.0825), "glass", seg=18)
disc("flask_neck", 0.019, 0.050, T(BURN_X, BURN_Y, FLASK_Z + 0.135), "glass", seg=16)
disc("flask_stopper", 0.021, 0.018, T(BURN_X, BURN_Y, FLASK_Z + 0.165), "red", seg=16)

# Glass vapor transfer tube from retort flask stopper into the condenser jacket
retort_tube_pts = [
    Vector((BURN_X, BURN_Y, FLASK_Z + 0.172)),
    Vector((BURN_X, BURN_Y, FLASK_Z + 0.225)),
    Vector(((BURN_X + COND_X) / 2, (BURN_Y + COND_Y) / 2, FLASK_Z + 0.230)),
    Vector((COND_X - 0.025, COND_Y, COND_Z + 0.095)),
]
tube("retort_transfer_tube", retort_tube_pts, 0.0055, key="glass", sides=8, vscale=4.0)

# ---------------------------------------------------------------- 7. Divided Charcoal & Gunpowder Drying Tray (Back-Left)
TRAY_W, TRAY_D, TRAY_H = 0.42, 0.20, 0.055
TRAY_CX, TRAY_CY = -0.50, 0.18
TRAY_Z = TABLE_TOP_Z + TRAY_H / 2
metal_box("powder_tray_bot", (TRAY_W, TRAY_D, 0.005), T(TRAY_CX, TRAY_CY, TABLE_TOP_Z + 0.003), bevel=0.001, tile=0.3, key="metal_plate")
for sy in (-1, 1):
    metal_box("powder_tray_wf", (TRAY_W, 0.006, TRAY_H), T(TRAY_CX, TRAY_CY + sy * (TRAY_D / 2), TRAY_Z), bevel=0.001, key="metal_plate")
for sx in (-1, 1):
    metal_box("powder_tray_ws", (0.006, TRAY_D, TRAY_H), T(TRAY_CX + sx * (TRAY_W / 2), TRAY_CY, TRAY_Z), bevel=0.001, key="metal_plate")
for di in (-1, 1):
    metal_box("powder_tray_div", (0.005, TRAY_D - 0.01, TRAY_H - 0.006), T(TRAY_CX + di * (TRAY_W / 6), TRAY_CY, TRAY_Z), bevel=0.001, key="metal_plate")

# Pulverized charcoal & smokeless gunpowder mounds inside the tray compartments + heavy steel pestle rod
for ci, cx_off in enumerate((-TRAY_W / 3, 0.0, TRAY_W / 3)):
    cone_part(f"powder_mound_{ci}", 0.052, 0.014, 0.028, T(TRAY_CX + cx_off, TRAY_CY, TABLE_TOP_Z + 0.019), "charcoal_mat", seg=14)
tube("grinding_pestle", [
    Vector((TRAY_CX - TRAY_W / 3 - 0.02, TRAY_CY - 0.03, TABLE_TOP_Z + 0.018)),
    Vector((TRAY_CX - TRAY_W / 3 + 0.05, TRAY_CY + 0.05, TABLE_TOP_Z + 0.078)),
], 0.011, key="metal", sides=10)

# ---------------------------------------------------------------- 8. Vanilla S.T.A.L.K.E.R. Anomaly Accents
DG = Matrix.Diagonal

# --- A. Main Tabletop Props (Z = TABLE_TOP_Z) ---
# Articulated gooseneck workshop inspection lamp on front-left corner
accent(r"dynamics\workshop_room\table_lamp_01", T(-0.68, -0.06, TABLE_TOP_Z + 0.004, 0, 0, 50))

# Chemist's drug & reagent synthesis kit on the left wooden worktop
accent(r"dynamics\equipments\trade\drugskit", T(-0.46, -0.18, TABLE_TOP_Z + 0.004, 0, 0, -14))

# Protective chemist safety goggles resting on front edge
accent(r"dynamics\equipments\trade\goggles", T(-0.18, -0.26, TABLE_TOP_Z + 0.006, 0, 0, 22))

# 3-liter glass distillate receiver carboy catching fuel from the copper condenser spout
accent(r"dynamics\kitchen_room\bottle_3l", T(RCV_X, RCV_Y, BZ, 0, 0, 35) @ DG((0.58, 0.58, 0.58, 1)))

# Chemical solvent bottle behind the burner
accent(r"dynamics\repair\solvent", T(-0.08, 0.24, BZ, 0, 0, -25))

# Small chemical reagent vials & bottles near the nitration tray
accent(r"dynamics\equipments\medical\antirad_kalium", T(-0.26, -0.08, BZ, 0, 0, 40))
accent(r"dynamics\equipments\medical\antibio_chlor", T(-0.25, 0.02, BZ, 0, 0, -18))
accent(r"dynamics\equipments\medical\drug_antidot", T(-0.20, -0.12, BZ, 0, 0, 65))

# Raw Zone vodka / alcohol feedstock bottles next to the fractional column
accent(r"dynamics\devices\dev_vodka\dev_vodka", T(0.62, -0.14, BZ, 0, 0, 28))
accent(r"dynamics\devices\dev_vodka\dev_vodka2", T(0.68, -0.02, BZ, 0, 0, -35))

# Sealed metal gunpowder / ammo tin on the front-right corner
accent(r"dynamics\equipments\trade\ammo", T(0.44, -0.22, BZ, 0, 0, -16))

# --- B. Middle Reagent Shelf Props (Z = MID_SHELF_Z + 0.011 = 1.191m) ---
MZ = MID_SHELF_Z + 0.011
for ji, jx in enumerate((-0.58, -0.44, -0.30)):
    accent(r"dynamics\equipments\trade\jar", T(jx, MID_SHELF_Y + 0.01, MZ, 0, 0, 25 + ji * 45))
accent(r"dynamics\workshop_room\banka_kraski_1", T(-0.10, MID_SHELF_Y + 0.01, MZ, 0, 0, 12), scale=0.62)
accent(r"dynamics\equipments\quest\box_kanifol", T(0.08, MID_SHELF_Y + 0.01, MZ, 0, 0, -18))
accent(r"dynamics\equipments\quest\box_resistors", T(0.24, MID_SHELF_Y + 0.01, MZ, 0, 0, 8))
accent(r"dynamics\drink\drink_flask", T(0.60, MID_SHELF_Y + 0.01, MZ, 0, 0, 22), ratio=0.5)

# --- C. Upper Canopy Shelf Props (Z = TOP_SHELF_Z + 0.012 = 1.492m) ---
UZ = TOP_SHELF_Z + 0.012
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_high", T(-0.52, TOP_SHELF_Y + 0.01, UZ, 0, 0, 14))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_mid", T(-0.52, TOP_SHELF_Y + 0.01, UZ + 0.039, 0, 0, -8))
accent(r"dynamics\kitchen_room\bottle_3l", T(-0.24, TOP_SHELF_Y + 0.01, UZ, 0, 0, -30) @ DG((0.52, 0.52, 0.52, 1)))
accent(r"dynamics\repair\glue_a", T(-0.04, TOP_SHELF_Y, UZ, 0, 0, 25))
accent(r"dynamics\repair\glue_b", T(0.06, TOP_SHELF_Y, UZ, 0, 0, -15))
accent(r"dynamics\workshop_room\banka_kraski_1", T(0.26, TOP_SHELF_Y + 0.01, UZ, 0, 0, 35), scale=0.58)
accent(r"dynamics\equipments\trade\jar", T(0.46, TOP_SHELF_Y + 0.01, UZ, 0, 0, -40))
accent(r"dynamics\equipments\trade\jar", T(0.58, TOP_SHELF_Y + 0.01, UZ, 0, 0, 15))

# --- D. Soviet GP-5 Gas Mask Hanging on Left Upright Post ---
disc("mask_peg", 0.005, 0.045, T(LX0 - 0.035, LY1, 1.25, 0, 90, 0), "metal", seg=8)
accent(r"dynamics\outfit\helm_respirator_gp5", T(LX0 - 0.055, LY1 - 0.02, 1.06, 90, 0, -90) @ DG((0.82, 0.82, 0.82, 1)))

# --- E. Lower Storage Shelf (Z = SHELF_Z + 0.026 = 0.206m) & Ground Accents ---
LZ = SHELF_Z + 0.026
# Left: Chemist's reserve drug/chemical toolkit & ammo/gunpowder toolkit boxes
accent(r"dynamics\equipments\quest\box_toolkit_drug", T(-0.50, 0.04, LZ, 0, 0, -6))
accent(r"dynamics\equipments\quest\box_toolkit_ammo", T(-0.48, -0.16, LZ, 0, 0, 8))

# Center: Refined Kerosene fuel tins
accent(r"dynamics\cooking\kerosene", T(-0.10, -0.02, LZ, 0, 0, 14))
accent(r"dynamics\cooking\kerosene", T(0.14, 0.06, LZ, 0, 0, -22))

# Right: 20L steel Gasoline jerrycans (scaled 0.84x to fit cleanly under the workbench apron)
accent(r"dynamics\balon\kanistra", T(0.46, 0.0, LZ, 0, 0, 78), scale=0.84)

# Ground beside right leg: Red propane gas cylinder standing upright and feeding the fractional still
BALON_X, BALON_Y = TL / 2 + 0.16, 0.10
accent(r"dynamics\balon\gaz_balon", T(BALON_X, BALON_Y, 0.0, 0, 0, -35), scale=0.88)
# Flexible rubber gas feed hose curving around the right tabletop edge up to the column boiler
hose_pts = [
    Vector((BALON_X, BALON_Y, 0.54)),
    Vector((BALON_X - 0.04, BALON_Y + 0.04, 0.72)),
    Vector((TL / 2 + 0.03, COL_Y + 0.06, TABLE_TOP_Z + 0.02)),
    Vector((TL / 2 - 0.04, COL_Y + 0.06, TABLE_TOP_Z + 0.03)),
    Vector((COL_X + 0.075, COL_Y + 0.03, BZ + 0.08)),
]
tube("gas_supply_hose", hose_pts, 0.007, key="metal", sides=8, vscale=5.0)

# Ground beside front-left leg: Burlap charcoal sack from the Woodcutter
accent(r"dynamics\cooking\charcoal", T(-TL / 2 - 0.14, -0.06, 0.0, 0, 0, 72))

# ---------------------------------------------------------------- Join all parts into chemist_station_visual
visual = join_parts()

try:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SCR, "models", BLEND))
    print(f'Info: Saved copy as "{BLEND}"')
except Exception as e:
    print(e)
