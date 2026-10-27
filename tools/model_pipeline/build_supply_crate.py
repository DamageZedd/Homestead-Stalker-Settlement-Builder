# Builds the HomesteadHF Supply Crate in Blender (run inside Blender).
# A plywood shipping crate framed in grey battens with diagonal braces, on a pallet, its lid slid
# half off; inside, a raised tray of workshop supplies (kit boxes, component boxes, copper wire,
# gun oil, a spare barrel). Vanilla accents; material name = texture path.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "supply_crate"
BLEND = os.path.join(SCR, r"models\supply_crate.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
start({"ply": ("wood\\wood_chipboard1", "models\\model"), "batten": ("wood\\wood_box", "models\\model"),
       "pallet": ("wood\\wood_palitra", "models\\model"), "metal": ("mtl\\mtl_rust_dark", "models\\model"),
       "stencil": ("decal\\decal_ro50210", "models\\model_aref")}, seed=300)
V_MAX = 0.98
BATTEN_STRIPS = [(0.27, 0.37), (0.38, 0.51), (0.79, 0.93)]
PALLET_STRIPS = [(0.0, 0.15), (0.165, 0.28), (0.30, 0.405), (0.42, 0.555), (0.57, 0.725), (0.87, 1.0)]


def batten(name, length, width, thick, matrix, bevel=0.004):
    STRIPS[:] = BATTEN_STRIPS
    return plank(name, length, width, thick, matrix, key="batten", bevel=bevel)


def slat(name, length, width, thick, matrix, bevel=0.004):
    STRIPS[:] = PALLET_STRIPS
    return plank(name, length, width, thick, matrix, key="pallet", bevel=bevel)


def ply(name, size, matrix):
    return metal_box(name, size, matrix, bevel=0.002, tile=1.1, key="ply")


X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


def B(pos, length_axis, thick_axis, width_axis):
    """A plank's frame: its local X (length), Y (thickness) and Z (width) along these world axes."""
    m = Matrix((length_axis, thick_axis, width_axis)).transposed().to_4x4()
    m.translation = pos
    return m


# ---------------------------------------------------------------- pallet
PL, PW = 1.20, 1.00
BB, STR_H, DK = 0.022, 0.10, 0.022
PTOP = BB + STR_H + DK
for x in (-0.55, 0.0, 0.55):
    slat("pallet_bottom", PW, 0.10, BB, B((x, 0, BB / 2), Y, Z, X))
for y in (-0.45, 0.0, 0.45):
    slat("pallet_stringer", PL, STR_H, 0.09, B((0, y, BB + STR_H / 2), X, Y, Z))
for i in range(7):
    x = -PL / 2 + 0.05 + i * (PL - 0.10) / 6
    slat("pallet_deck", PW, 0.10, DK, B((x, 0, BB + STR_H + DK / 2), Y, Z, X))

# ---------------------------------------------------------------- crate
CL, CD, CH, PT = 0.92, 0.72, 0.62, 0.012
CX = -0.10
Z0 = PTOP
ply("ply_bottom", (CL, CD, PT), T(CX, 0, Z0 + PT / 2))
for sy in (-1, 1):
    ply("ply_side", (CL, PT, CH), T(CX, sy * (CD / 2 - PT / 2), Z0 + CH / 2))
for sx in (-1, 1):
    ply("ply_end", (PT, CD - 2 * PT, CH), T(CX + sx * (CL / 2 - PT / 2), 0, Z0 + CH / 2))
BW, BT = 0.07, 0.022
# long sides: frame and a diagonal brace
for sy in (-1, 1):
    y = sy * (CD / 2 + BT / 2)
    for z in (Z0 + BW / 2, Z0 + CH - BW / 2):
        batten("side_rail", CL, BW, BT, B((CX, y, z), X, Y, Z))
    for sx in (-1, 1):
        batten("side_post", CH - 2 * BW, BW, BT, B((CX + sx * (CL / 2 - BW / 2), y, Z0 + CH / 2), Z, Y, X))
    run, rise = CL - 3 * BW, CH - 2 * BW
    d = Vector((run, 0, sy * rise)).normalized()
    w = Vector((-d.z, 0, d.x))
    batten("side_brace", math.hypot(run, rise) - 0.04, BW, BT * 0.8, B((CX, y, Z0 + CH / 2), d, Y, w))
# ends: frame and a cleat across the middle
for sx in (-1, 1):
    x = CX + sx * (CL / 2 + BT / 2)
    for z in (Z0 + BW / 2, Z0 + CH / 2, Z0 + CH - BW / 2):
        batten("end_rail", CD + 2 * BT, BW, BT, B((x, 0, z), Y, X, Z))
    for sy in (-1, 1):
        batten("end_post", CH - 2 * BW, BW, BT, B((x, sy * (CD / 2 - BW / 2), Z0 + CH / 2), Z, X, Y))
# nails at the batten joints
for sy in (-1, 1):
    for sx in (-1, 1):
        for z in (Z0 + BW / 2, Z0 + CH - BW / 2):
            rivet(T(CX + sx * (CL / 2 - BW / 2), sy * (CD / 2 + BT + 0.001), z, sy * -90, 0, 0))
decal("stencil", 0.24, 0.12, T(CX + 0.19, -(CD / 2 + BT + 0.0015), Z0 + CH * 0.70))  # in the triangle above the brace

# inner tray at mid-height so the stock shows above the rim
TZ = Z0 + CH - 0.22
for sy in (-1, 1):
    batten("tray_ledger", CL - 2 * PT, 0.04, 0.03, B((CX, sy * (CD / 2 - PT - 0.015), TZ - 0.02), X, Y, Z))
for i in range(5):
    y = -CD / 2 + PT + 0.07 + i * (CD - 2 * PT - 0.14) / 4
    batten("tray_slat", CL - 2 * PT - 0.004, 0.12, 0.016, B((CX, y, TZ), X, Z, Y), bevel=0.003)

# the lid: plywood with a batten frame, slid half off toward +x and twisted
lid_m = T(CX + 0.34, -0.06, Z0 + CH + PT / 2 + 0.001, 0, 0, 13)
ply("lid", (CL + 0.02, CD + 0.02, PT), lid_m)
for sy in (-1, 1):
    batten("lid_rail", CL + 0.02, BW, BT, lid_m @ B((0, sy * (CD / 2 + 0.01 - BW / 2), PT / 2 + BT / 2), X, Z, Y))
for sx in (-1, 1):
    batten("lid_cleat", CD - 2 * BW + 0.02, BW, BT, lid_m @ B((sx * (CL / 2 + 0.01 - BW / 2), 0, PT / 2 + BT / 2), Y, Z, X))

# ---------------------------------------------------------------- stock on the tray (the open half, -x)
TT = TZ + 0.008
accent(r"dynamics\equipments\quest\box_toolkit_1", T(CX - 0.27, -0.18, TT, 0, 0, 4))
accent(r"dynamics\equipments\quest\box_toolkit_2", T(CX - 0.25, 0.05, TT, 0, 0, -6))
accent(r"dynamics\equipments\quest\box_toolkit_1", T(CX - 0.26, -0.17, TT + 0.062, 0, 0, -9))
accent(r"dynamics\equipments\quest\box_resistors", T(CX + 0.02, -0.20, TT, 0, 0, 92))
accent(r"dynamics\equipments\quest\box_condensers", T(CX + 0.02, 0.10, TT, 0, 0, 88))
accent(r"dynamics\equipments\quest\box_condensers", T(CX + 0.03, 0.09, TT + 0.071, 0, 0, 81))
for i, (x, y) in enumerate([(CX - 0.05, -0.02), (CX - 0.33, 0.24)]):
    accent(r"dynamics\equipments\quest\materials_wire", T(x, y, TT, 0, 0, random.uniform(0, 360)))
accent(r"dynamics\repair\gun_oil_ru", T(CX - 0.16, 0.26, TT, 0, 0, 30))
accent(r"dynamics\repair\gun_oil_ru", T(CX - 0.10, 0.27, TT, 0, 0, -10))
accent(r"dynamics\part\prt_w_barrel", T(CX - 0.20, -0.05, TT + 0.055, 0, 0, 70), ratio=0.5)
# a kit box and copper wire out on the pallet's free end
accent(r"dynamics\equipments\quest\box_toolkit_2", T(0.48, -0.25, PTOP, 0, 0, 85))
accent(r"dynamics\equipments\quest\materials_wire", T(0.49, 0.20, PTOP, 0, 0, 40))

supply = join_parts()
