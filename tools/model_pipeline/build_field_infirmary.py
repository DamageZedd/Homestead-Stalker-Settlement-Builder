# Builds the HomesteadHF Field Infirmary (the Medic's station) in Blender (run inside Blender).
# A Soviet field examination couch and surgical station: tubular steel frame with corner gussets,
# ratcheting hinged headrest, three-piece stitched olive oilcloth mattress cushions with a quilted
# bolster pillow and straps, fold-down steel side rail, wooden duckboard under-rack, and patient
# step-stool; a wheeled telescoping IV stand with hanging glass infusion bottles and drip tubing;
# and an enamel hospital instrument cabinet with a painted red cross, articulated surgical lamp,
# kidney basin, bone saw, stims, tourniquet, medkits, bandages and field medic bag.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "field_infirmary"
BLEND = os.path.join(SCR, r"models\field_infirmary.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
start({
    "enamel": ("mtl\\mtl_pod_01", "models\\model"),
    "green": ("mtl\\mtl_pod_green", "models\\model"),
    "canvas": ("prop\\prop_brezent", "models\\model"),
    "linen": ("prop\\prop_mattress2", "models\\model"),
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "pipe": ("mtl\\mtl_barrel_big_rust", "models\\model"),
    "red": ("mtl\\mtl_red_paint_iov", "models\\model"),
    "white": ("wall\\wall_house_white_01", "models\\model"),
    "glass": ("glas\\glas_dirt", "models\\model"),
    "wood": ("wood\\wood_box", "models\\model"),
}, seed=409)

DG = Matrix.Diagonal


def disc(name, radius, depth, matrix, key, seg=24, uv_scale=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = uv_scale or (0.48 / max(radius, 0.02))
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)


def cone_part(name, r1, r2, depth, matrix, key, seg=20):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = 0.45 / max(r1, r2, 0.02)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)


def linen_box(name, size, matrix, bevel=0.010):
    """Box mapped onto the quilted grey-white linen side of prop_mattress2 (u in 0.05..0.34)."""
    bm = beveled_box(Vector(size), bevel)
    uvl = bm.loops.layers.uv.new("Texture")
    u0, u1 = 0.06, 0.33
    v0, v1 = 0.12, 0.88
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        a, b = [i for i in range(3) if i != ax]
        for l in f.loops:
            p = l.vert.co
            fa = p[a] / max(size[a], 0.01) + 0.5
            fb = p[b] / max(size[b], 0.01) + 0.5
            l[uvl].uv = (u0 + fa * (u1 - u0), v0 + fb * (v1 - v0))
    return finish(bm, name, ["linen"], matrix)


def red_cross(matrix, size):
    """Painted red cross on a white disc, in local XY plane facing +Z."""
    disc("cross_disc", size * 0.62, 0.0018, matrix @ Matrix.Translation((0, 0, 0.0009)), "white", seg=28, uv_scale=1.2)
    arm, thick = size * 0.78, size * 0.26
    for rot in (0, 90):
        metal_box("cross_bar", (arm, thick, 0.0014),
                  matrix @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Translation((0, 0, 0.0024)),
                  bevel=0.0003, tile=0.5, key="red")


# ---------------------------------------------------------------- 1. Examination Couch (Left / Centre)
# Couch spans X: [-0.82, +0.46] (length 1.28m), Y: [-0.32, +0.32] (width 0.64m), frame top Z = 0.50m
CX0, CX1 = -0.82, 0.46
CL = CX1 - CX0
CCX = (CX0 + CX1) / 2
CW = 0.64
FZ = 0.50
LEG_R = 0.019

# Four tubular steel legs with rubber/steel foot pads and joint collars
LX_L, LX_R = CX0 + 0.04, CX1 - 0.04
LY_F, LY_B = -(CW / 2 - 0.04), (CW / 2 - 0.04)
for lx in (LX_L, LX_R):
    for ly in (LY_F, LY_B):
        disc("couch_foot", 0.030, 0.014, T(lx, ly, 0.007), "metal", seg=16, uv_scale=4.0)
        tube("couch_leg", [Vector((lx, ly, 0.014)), Vector((lx, ly, FZ))], LEG_R, key="green", sides=12, vscale=2.0)
        for zc in (0.16, FZ - 0.025):
            disc("leg_collar", 0.023, 0.024, T(lx, ly, zc), "metal", seg=14, uv_scale=4.0)

# Upper rectangular frame rails (green hospital enamel) + corner gussets with rivets
FT = 0.032
for ly in (LY_F, LY_B):
    metal_box("couch_side_rail", (CL, FT, FT), T(CCX, ly, FZ - FT / 2), bevel=0.004, tile=0.9, key="green")
for lx in (LX_L, LX_R):
    metal_box("couch_end_rail", (FT, CW - 2 * FT, FT), T(lx, 0, FZ - FT / 2), bevel=0.004, tile=0.9, key="green")
for xm in (-0.38, 0.04):
    metal_box("couch_crossbar", (0.026, CW - 2 * FT, 0.024), T(xm, 0, FZ - FT / 2), bevel=0.003, tile=0.8, key="enamel")

# Corner gusset plates and rivets on the front & back faces of the leg joints
for lx, sx in ((LX_L, -1), (LX_R, 1)):
    for ly, sy in ((LY_F, -1), (LY_B, 1)):
        metal_box("gusset", (0.08, 0.005, 0.07), T(lx - sx * 0.02, ly + sy * (FT / 2 + 0.0025), FZ - 0.045), bevel=0.001, key="metal")
        rivet(T(lx - sx * 0.045, ly + sy * (FT / 2 + 0.005), FZ - 0.022, -sy * 90, 0, 0))
        rivet(T(lx, ly + sy * (FT / 2 + 0.005), FZ - 0.068, -sy * 90, 0, 0))

# Lower H-stretcher frame at Z = 0.16 with wooden duckboard slats
UZ = 0.16
for ly in (LY_F, LY_B):
    tube("low_rail", [Vector((LX_L, ly, UZ)), Vector((LX_R, ly, UZ))], 0.014, key="enamel", sides=10, vscale=2.0)
for lx in (LX_L + 0.06, LX_R - 0.06):
    tube("low_cross", [Vector((lx, LY_F, UZ)), Vector((lx, LY_B, UZ))], 0.013, key="enamel", sides=10, vscale=2.0)
for i in range(6):
    sx = LX_L + 0.12 + i * (CL - 0.32) / 5
    metal_box("duckboard_slat", (0.11, CW - 0.12, 0.014), T(sx, 0, UZ + 0.016), bevel=0.002, tile=0.8, key="wood")

# Hinged backrest frame on the left (-X) head end, inclined at 24 degrees
HX_PIVOT = -0.40
HEAD_LEN = 0.42
HEAD_ANG = 24
head_piv = Matrix.Translation((HX_PIVOT, 0, FZ)) @ Matrix.Rotation(math.radians(HEAD_ANG), 4, 'Y')
for ly in (LY_F + 0.01, LY_B - 0.01):
    metal_box("head_arm", (HEAD_LEN, 0.022, 0.022), head_piv @ T(-HEAD_LEN / 2, ly, 0.012), bevel=0.003, key="enamel")
    tube("head_hinge", [Vector((HX_PIVOT - 0.015, ly, FZ + 0.004)), Vector((HX_PIVOT + 0.015, ly, FZ + 0.004))], 0.009, key="metal", sides=8, vscale=3)
    p_top = head_piv @ Vector((-HEAD_LEN * 0.68, ly, 0.006))
    p_bot = Vector((LX_L + 0.06, ly, FZ - 0.01))
    tube("ratchet_strut", [p_bot, p_top], 0.007, key="metal", sides=8, vscale=3.0)
metal_box("head_cross", (0.022, CW - 0.10, 0.022), head_piv @ T(-HEAD_LEN + 0.03, 0, 0.012), bevel=0.003, key="enamel")
tube("ratchet_rod", [Vector((LX_L + 0.06, LY_F - 0.02, FZ - 0.01)), Vector((LX_L + 0.06, LY_B + 0.02, FZ - 0.01))], 0.006, key="metal", sides=8, vscale=3)

# Three-section upholstered olive oilcloth mattress cushions (headrest + middle seat + foot section)
PAD_H = 0.068
MID_X0, MID_X1 = -0.385, 0.035
FOOT_X0, FOOT_X1 = 0.048, 0.455
metal_box("mattress_mid", (MID_X1 - MID_X0, CW - 0.02, PAD_H), T((MID_X0 + MID_X1) / 2, 0, FZ + PAD_H / 2), bevel=0.015, tile=1.0, key="canvas")
metal_box("mattress_foot", (FOOT_X1 - FOOT_X0, CW - 0.02, PAD_H), T((FOOT_X0 + FOOT_X1) / 2, 0, FZ + PAD_H / 2), bevel=0.015, tile=1.0, key="canvas")
# Stitched seam welts on the cushions
for sx in (-0.175, 0.25):
    metal_box("mattress_welt", (0.010, CW - 0.016, PAD_H + 0.002), T(sx, 0, FZ + PAD_H / 2), bevel=0.002, tile=0.6, key="canvas")

# Angled headrest mattress pad + quilted linen bolster pillow strapped to the headrest
metal_box("mattress_head", (HEAD_LEN, CW - 0.02, PAD_H), head_piv @ T(-HEAD_LEN / 2, 0, 0.022 + PAD_H / 2), bevel=0.015, tile=1.0, key="canvas")
linen_box("bolster_pillow", (0.14, CW - 0.12, 0.065), head_piv @ T(-HEAD_LEN * 0.64, 0, 0.022 + PAD_H + 0.030), bevel=0.022)
for sy in (-0.17, 0.17):
    metal_box("pillow_strap", (0.15, 0.018, 0.070), head_piv @ T(-HEAD_LEN * 0.64, sy, 0.022 + PAD_H + 0.030), bevel=0.002, key="metal")

# Folded quilted hospital blanket at the foot end of the couch
linen_box("folded_blanket", (0.24, CW - 0.08, 0.034), T(0.31, 0.0, FZ + PAD_H + 0.016, 0, 0, 4), bevel=0.010)

# Back safety rail (+Y side) with clamp brackets
RY = CW / 2 + 0.018
for rx in (-0.26, 0.30):
    metal_box("rail_clamp", (0.036, 0.032, 0.048), T(rx, RY - 0.012, FZ - 0.012), bevel=0.002, key="metal")
    tube("rail_post", [Vector((rx, RY, FZ - 0.01)), Vector((rx, RY, FZ + 0.20))], 0.010, key="pipe", sides=10, vscale=2.5)
tube("rail_top", [Vector((-0.30, RY, FZ + 0.20)), Vector((0.34, RY, FZ + 0.20))], 0.011, key="pipe", sides=10, vscale=2.0)

# Patient Step-Stool (Приступок) in front of the couch (-Y)
ST_X, ST_Y = 0.02, -CW / 2 - 0.19
ST_W, ST_D, ST_H = 0.44, 0.25, 0.21
for sx in (-1, 1):
    for sy in (-1, 1):
        lx, ly = ST_X + sx * (ST_W / 2 - 0.025), ST_Y + sy * (ST_D / 2 - 0.025)
        disc("stool_foot", 0.018, 0.008, T(lx, ly, 0.004), "metal", seg=12)
        tube("stool_leg", [Vector((lx, ly, 0.008)), Vector((lx, ly, ST_H - 0.018))], 0.011, key="enamel", sides=10, vscale=2.5)
metal_box("stool_frame", (ST_W, ST_D, 0.020), T(ST_X, ST_Y, ST_H - 0.022), bevel=0.003, tile=0.7, key="green")
for i in range(3):
    sy = ST_Y - ST_D / 2 + 0.042 + i * (ST_D - 0.084) / 2
    metal_box("stool_slat", (ST_W - 0.02, 0.065, 0.014), T(ST_X, sy, ST_H - 0.005), bevel=0.002, tile=0.7, key="wood")
    for sx in (-1, 1):
        rivet(T(ST_X + sx * (ST_W / 2 - 0.035), sy, ST_H + 0.002))


# ---------------------------------------------------------------- 2. Telescoping IV Drip Stand (Back-Left)
IV_X, IV_Y = -0.78, 0.25
IV_TOP = 1.56
# 3-legged spider base with caster wheels
disc("iv_hub", 0.038, 0.045, T(IV_X, IV_Y, 0.065), "metal", seg=16)
for ang in (30, 150, 270):
    rad = math.radians(ang)
    ex, ey = IV_X + math.cos(rad) * 0.19, IV_Y + math.sin(rad) * 0.19
    tube("iv_leg", [Vector((IV_X, IV_Y, 0.065)), Vector((ex, ey, 0.038))], 0.012, key="enamel", sides=10, vscale=2.5)
    metal_box("iv_yoke", (0.024, 0.024, 0.024), T(ex, ey, 0.028), bevel=0.002, key="metal")
    disc("iv_wheel", 0.022, 0.012, T(ex, ey, 0.022, 90, 0, ang), "metal", seg=14, uv_scale=4.0)

# Lower enamel pole + locking collar + upper steel rod
tube("iv_pole_low", [Vector((IV_X, IV_Y, 0.08)), Vector((IV_X, IV_Y, 0.98))], 0.015, key="enamel", sides=12, vscale=1.5)
disc("iv_collar", 0.022, 0.036, T(IV_X, IV_Y, 0.98), "metal", seg=14)
tube("iv_thumbscrew", [Vector((IV_X, IV_Y, 0.98)), Vector((IV_X - 0.045, IV_Y, 0.98))], 0.005, key="metal", sides=8, vscale=3)
metal_box("iv_knob", (0.006, 0.028, 0.012), T(IV_X - 0.048, IV_Y, 0.98), bevel=0.001, key="red")
tube("iv_pole_high", [Vector((IV_X, IV_Y, 0.98)), Vector((IV_X, IV_Y, IV_TOP))], 0.010, key="pipe", sides=12, vscale=1.8)

# Double S-hook crown at top of IV pole
for sx in (-1, 1):
    hx = IV_X + sx * 0.105
    pts = [
        Vector((IV_X, IV_Y, IV_TOP - 0.02)),
        Vector((IV_X + sx * 0.05, IV_Y, IV_TOP + 0.01)),
        Vector((hx, IV_Y, IV_TOP)),
        Vector((hx, IV_Y, IV_TOP - 0.05)),
        Vector((hx + sx * 0.018, IV_Y, IV_TOP - 0.035)),
    ]
    tube("iv_hook", pts, 0.0045, key="metal", sides=8, vscale=4.0)

# Two inverted glass IV infusion bottles hanging from the hooks
for sx, b_scale in ((-1, 1.0), (1, 0.86)):
    bx = IV_X + sx * 0.105
    bz = IV_TOP - 0.155
    tube("iv_bail", [Vector((bx - 0.032, IV_Y, bz + 0.05)), Vector((bx, IV_Y, IV_TOP - 0.045)), Vector((bx + 0.032, IV_Y, bz + 0.05))], 0.0025, key="metal", sides=6, vscale=5)
    disc("iv_bottle", 0.036 * b_scale, 0.12 * b_scale, T(bx, IV_Y, bz), "glass", seg=18, uv_scale=2.5)
    disc("iv_band", 0.038 * b_scale, 0.014, T(bx, IV_Y, bz + 0.04), "metal", seg=18)
    metal_box("iv_label", (0.042 * b_scale, 0.003, 0.055 * b_scale), T(bx, IV_Y - 0.036 * b_scale, bz), bevel=0.0005, key="white")
    cone_part("iv_neck", 0.014 * b_scale, 0.035 * b_scale, 0.035, T(bx, IV_Y, bz - 0.075 * b_scale), "glass", seg=16)
    disc("iv_stopper", 0.016 * b_scale, 0.014, T(bx, IV_Y, bz - 0.095 * b_scale), "red", seg=14)
    disc("iv_chamber", 0.008, 0.036, T(bx, IV_Y, bz - 0.12 * b_scale), "glass", seg=12)

# Flexible IV line draping from the right bottle down to the couch headrest
iv_line_pts = [
    Vector((IV_X + 0.105, IV_Y, IV_TOP - 0.28)),
    Vector((IV_X + 0.12, IV_Y - 0.04, 1.10)),
    Vector((IV_X + 0.14, IV_Y - 0.10, 0.90)),
    Vector((-0.64, 0.16, 0.76)),
    Vector((-0.58, 0.22, 0.68)),
]
tube("iv_line", iv_line_pts, 0.0035, key="enamel", sides=7, vscale=8.0)


# ---------------------------------------------------------------- 3. Hospital Instrument Table & Cabinet (Right)
# Spans X: [+0.52, +1.04] (width 0.52m), Y: [-0.29, +0.29] (depth 0.58m), top tray Z = 0.80m
TX0, TX1 = 0.52, 1.04
TW = TX1 - TX0
TCX = (TX0 + TX1) / 2
TD = 0.58
TH = 0.80
WH_Z = 0.055

# Four caster wheels & tubular steel legs
for sx in (-1, 1):
    for sy in (-1, 1):
        lx, ly = TCX + sx * (TW / 2 - 0.03), sy * (TD / 2 - 0.03)
        disc("cart_wheel", 0.026, 0.014, T(lx, ly, 0.026, 90, 0, 20 * sx), "metal", seg=14, uv_scale=4.0)
        metal_box("cart_yoke", (0.028, 0.028, 0.030), T(lx, ly, 0.042), bevel=0.002, key="metal")
        tube("cart_leg", [Vector((lx, ly, WH_Z)), Vector((lx, ly, TH + 0.035))], 0.015, key="enamel", sides=12, vscale=2.0)

# Lower supply shelf at Z = 0.16 with perimeter guard rails
SZ_LOW = 0.16
metal_box("cart_shelf_low", (TW - 0.02, TD - 0.02, 0.018), T(TCX, 0, SZ_LOW), bevel=0.003, tile=0.8, key="enamel")
for sy in (-1, 1):
    tube("low_guard_x", [Vector((TX0 + 0.03, sy * (TD / 2 - 0.03), SZ_LOW + 0.038)),
                         Vector((TX1 - 0.03, sy * (TD / 2 - 0.03), SZ_LOW + 0.038))], 0.005, key="metal", sides=8, vscale=3)
for sx in (-1, 1):
    tube("low_guard_y", [Vector((TCX + sx * (TW / 2 - 0.03), -(TD / 2 - 0.03), SZ_LOW + 0.038)),
                         Vector((TCX + sx * (TW / 2 - 0.03), (TD / 2 - 0.03), SZ_LOW + 0.038))], 0.005, key="metal", sides=8, vscale=3)

# Middle enclosed medical locker (Z = 0.44 to 0.73) with front door, handle and Red Cross
CAB_Z0, CAB_Z1 = 0.44, 0.73
CAB_H = CAB_Z1 - CAB_Z0
CAB_ZC = (CAB_Z0 + CAB_Z1) / 2
metal_box("cab_body", (TW - 0.03, TD - 0.04, CAB_H), T(TCX, 0.005, CAB_ZC), bevel=0.004, tile=0.8, key="enamel")
DY_DOOR = -(TD / 2 - 0.02)
metal_box("cab_door", (TW - 0.09, 0.014, CAB_H - 0.04), T(TCX, DY_DOOR - 0.005, CAB_ZC), bevel=0.003, tile=0.7, key="green")
for hz in (CAB_ZC - 0.08, CAB_ZC + 0.08):
    tube("cab_hinge", [Vector((TCX + (TW - 0.09) / 2 + 0.004, DY_DOOR - 0.010, hz - 0.018)),
                       Vector((TCX + (TW - 0.09) / 2 + 0.004, DY_DOOR - 0.010, hz + 0.018))], 0.005, key="metal", sides=8, vscale=3)
HX_HND = TCX - (TW - 0.09) / 2 + 0.035
tube("cab_handle", [Vector((HX_HND, DY_DOOR - 0.010, CAB_ZC - 0.035)),
                    Vector((HX_HND, DY_DOOR - 0.032, CAB_ZC - 0.035)),
                    Vector((HX_HND, DY_DOOR - 0.032, CAB_ZC + 0.035)),
                    Vector((HX_HND, DY_DOOR - 0.010, CAB_ZC + 0.035))], 0.0045, key="metal", sides=8, vscale=3)
red_cross(Matrix.Translation((TCX + 0.01, DY_DOOR - 0.013, CAB_ZC)) @ Matrix.Rotation(math.radians(90), 4, 'X'), 0.14)

# Upper surgical instrument tray at Z = 0.80 with raised rim and push-handle
metal_box("cart_top_tray", (TW, TD, 0.020), T(TCX, 0, TH), bevel=0.004, tile=0.8, key="enamel")
for sy in (-1, 1):
    metal_box("tray_lip_x", (TW, 0.010, 0.024), T(TCX, sy * (TD / 2 - 0.005), TH + 0.016), bevel=0.002, key="enamel")
for sx in (-1, 1):
    metal_box("tray_lip_y", (0.010, TD - 0.02, 0.024), T(TCX + sx * (TW / 2 - 0.005), 0, TH + 0.016), bevel=0.002, key="enamel")
tube("cart_push_bar", [
    Vector((TX1, -0.18, TH - 0.005)),
    Vector((TX1 + 0.055, -0.18, TH - 0.005)),
    Vector((TX1 + 0.055, 0.18, TH - 0.005)),
    Vector((TX1, 0.18, TH - 0.005)),
], 0.008, key="pipe", sides=10, vscale=2.5)

# Articulated surgical examination lamp mounted at back-left of the cart (x=0.56, y=0.25)
LX_LAMP, LY_LAMP = TX0 + 0.04, TD / 2 - 0.04
disc("lamp_base", 0.036, 0.030, T(LX_LAMP, LY_LAMP, TH + 0.022), "metal", seg=16)
lamp_arm_pts = [
    Vector((LX_LAMP, LY_LAMP, TH + 0.035)),
    Vector((LX_LAMP - 0.02, LY_LAMP, TH + 0.28)),
    Vector((LX_LAMP - 0.10, LY_LAMP - 0.05, TH + 0.45)),
    Vector((LX_LAMP - 0.22, LY_LAMP - 0.11, TH + 0.52)),
    Vector((LX_LAMP - 0.30, LY_LAMP - 0.14, TH + 0.46)),
]
tube("lamp_arm", lamp_arm_pts, 0.010, key="pipe", sides=10, vscale=2.5)
for pt in lamp_arm_pts[1:4]:
    disc("lamp_joint", 0.016, 0.020, T(pt.x, pt.y, pt.z, 90, 0, 0), "metal", seg=12)
lamp_head_m = T(LX_LAMP - 0.32, LY_LAMP - 0.15, TH + 0.43, 25, -40, 15)
cone_part("lamp_shade", 0.090, 0.028, 0.080, lamp_head_m, "enamel", seg=20)
disc("lamp_cap", 0.028, 0.030, lamp_head_m @ T(0, 0, 0.048), "metal", seg=14)
disc("lamp_bulb", 0.034, 0.016, lamp_head_m @ T(0, 0, -0.010), "white", seg=16)


# ---------------------------------------------------------------- 4. Vanilla Anomaly Medical Accents
TT = TH + 0.010  # Top surface of surgical tray (Z = 0.81)
# Kidney basin & surgical tray with bone saw, stims, pills, coagulant, tourniquet, antiseptic
accent(r"dynamics\kitchen_room\kitchen_miska", T(TCX - 0.10, -0.12, TT, 0, 0, 20) @ DG((0.45, 0.45, 0.45, 1)))
accent(r"dynamics\kitchen_room\kitchen_bludo", T(TCX + 0.10, -0.11, TT, 0, 0, -15) @ DG((0.46, 0.46, 0.46, 1)))
accent(r"dynamics\workshop_room\saw", T(TCX + 0.02, 0.04, TT + 0.003, 0, 0, 18) @ DG((0.32, 0.32, 0.32, 1)))
accent(r"dynamics\equipments\medical\stim3", T(TCX + 0.10, -0.11, TT + 0.006, 0, 0, 35), ratio=0.4)
accent(r"dynamics\equipments\medical\stim1", T(TCX - 0.14, 0.02, TT, 0, 0, 75), ratio=0.4)
accent(r"dynamics\equipments\medical\stim2", T(TCX - 0.14, -0.03, TT, 0, 0, 82), ratio=0.4)
accent(r"dynamics\equipments\medical\drug_coagulant", T(TCX + 0.11, 0.11, TT, 0, 0, 80))
accent(r"dynamics\equipments\medical\drug_sleeping_pills", T(TCX + 0.11, 0.11, TT + 0.013, 0, 0, 65))
accent(r"dynamics\devices\dev_vodka\dev_vodka", T(TCX + 0.15, 0.19, TT, 0, 0, 30))
accent(r"dynamics\devices\dev_antirad\dev_antirad", T(TCX - 0.13, 0.17, TT, 0, 0, -20))

# Lower cart shelf (Z = 0.169): stacked medkits (scientific, army, standard), bandages, 3L glass jar
SL = SZ_LOW + 0.009
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_high", T(TCX - 0.10, -0.08, SL, 0, 0, 88))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_mid", T(TCX - 0.10, -0.07, SL + 0.039, 0, 0, 95))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_low", T(TCX - 0.09, 0.12, SL, 0, 0, 12))
accent(r"dynamics\devices\dev_bandage\dev_bandage", T(TCX + 0.10, -0.11, SL, 0, 0, 8))
accent(r"dynamics\devices\dev_bandage\dev_bandage", T(TCX + 0.10, -0.11, SL + 0.058, 0, 0, -14))
accent(r"dynamics\kitchen_room\bottle_3l", T(TCX + 0.11, 0.11, SL, 0, 0, 40) @ DG((0.68, 0.68, 0.68, 1)))

# On the examination couch: drugs kit case on the folded blanket + scientific medkit & bandage ready on the middle cushion
accent(r"dynamics\equipments\trade\drugskit", T(0.31, 0.02, FZ + PAD_H + 0.033, 0, 0, -75))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_high", T(-0.15, 0.10, FZ + PAD_H, 0, 0, 25))
accent(r"dynamics\devices\dev_bandage\dev_bandage", T(-0.18, -0.12, FZ + PAD_H, 0, 0, -30))

# On the wooden duckboard rack under the couch (Z = UZ + 0.023 = 0.183): medic bag and spare medkits
UR = UZ + 0.023
accent(r"dynamics\equipments\dev_med_bag", T(-0.22, -0.04, UR, 0, 0, 12))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_low", T(0.16, -0.06, UR, 0, 0, 75))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_mid", T(0.17, 0.12, UR, 0, 0, -15))

infirmary = join_parts()
