# Build script for the HomesteadHF Salvage Table (run inside Blender).
# Heavy industrial scavenger workbench with bench vise, tool backboard, scrap bins, and salvage parts.
import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix, Euler

NAME = "salvage_table"
BLEND = "salvage_table.blend"

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())

start({
    "wood": ("wood\\wood_jasik", "models\\model"),
    "wood_dark": ("wood\\wood_box", "models\\model"),
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "metal_green": ("mtl\\mtl_pod_green", "models\\model"),
    "metal_plate": ("mtl\\mtl_pod_02", "models\\model"),
    "metal_tin": ("mtl\\mtl_barrel_big_rust", "models\\model"),
    "copper": ("mtl\\mtl_red_paint_iov", "models\\model"),
    "rope": ("item\\item_rope", "models\\model"),
    "white": ("wall\\wall_house_white_01", "models\\model"),
})

def disc(name, radius, depth, matrix, key, seg=16):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = 1.0 / (radius * 2.2)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)

# ---------------------------------------------------------------- 1. Workbench Structural Steel Frame
TL = 1.60   # Table length along X [-0.80, +0.80]
TD = 0.82   # Table depth along Y [-0.41, +0.41]
TABLE_TOP_Z = 0.860
LEG_H = TABLE_TOP_Z - 0.038  # 0.822m
LEG_S = 0.055

LX0, LX1 = -TL / 2 + 0.065, TL / 2 - 0.065  # -0.735, +0.735
LY0, LY1 = -TD / 2 + 0.055, TD / 2 - 0.055  # -0.355, +0.355

# 4 heavy tubular/angle legs
for lx in (LX0, LX1):
    for ly in (LY0, LY1):
        # Foot pad with mounting holes
        metal_box("foot_pad", (0.085, 0.085, 0.008), T(lx, ly, 0.004), bevel=0.001, tile=0.3, key="metal")
        disc("anchor_bolt_1", 0.005, 0.006, T(lx - 0.03, ly - 0.03, 0.010), "metal", seg=8)
        disc("anchor_bolt_2", 0.005, 0.006, T(lx + 0.03, ly + 0.03, 0.010), "metal", seg=8)
        # Main leg post
        metal_box("table_leg", (LEG_S, LEG_S, LEG_H), T(lx, ly, LEG_H / 2 + 0.008), bevel=0.003, tile=0.4, key="metal_green")
        # Welded top mounting flange
        metal_box("leg_top_flange", (0.09, 0.09, 0.010), T(lx, ly, LEG_H + 0.003), bevel=0.001, tile=0.3, key="metal")

# Top apron frame connecting leg tops
APRON_H = 0.065
APRON_TH = 0.028
APRON_Z = TABLE_TOP_Z - 0.036 - APRON_H / 2
# Front & Back perimeter rails
metal_box("apron_f", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_b", (LX1 - LX0, APRON_TH, APRON_H), T(0, LY1, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
# Left & Right side rails
metal_box("apron_l", (APRON_TH, LY1 - LY0, APRON_H), T(LX0, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")
metal_box("apron_r", (APRON_TH, LY1 - LY0, APRON_H), T(LX1, 0, APRON_Z), bevel=0.002, tile=0.4, key="metal_green")

# Welded diagonal corner gussets on aprons
for lx, sx in ((LX0, +1), (LX1, -1)):
    for ly, sy in ((LY0, +1), (LY1, -1)):
        metal_box("corner_gusset", (0.055, 0.055, 0.006), T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z), bevel=0.001, tile=0.2, key="metal")
        rivet(T(lx + sx * 0.045, ly + sy * 0.045, APRON_Z + 0.005))

# ---------------------------------------------------------------- 2. Lower Stretcher Shelf (Z = 0.22m)
SHELF_Z = 0.220
# Lower cross rails
metal_box("stretcher_f", (LX1 - LX0, 0.035, 0.035), T(0, LY0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_b", (LX1 - LX0, 0.035, 0.035), T(0, LY1, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_l", (0.035, LY1 - LY0, 0.035), T(LX0, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")
metal_box("stretcher_r", (0.035, LY1 - LY0, 0.035), T(LX1, 0, SHELF_Z), bevel=0.002, tile=0.3, key="metal")

# 4 heavy lower shelf planks laid completely flat (rx=90!)
SHELF_W = (LY1 - LY0 - 0.01) / 4
for si in range(4):
    spy = (LY0 + 0.02) + SHELF_W / 2 + si * SHELF_W
    plank(f"shelf_plank_{si}", LX1 - LX0 + 0.04, SHELF_W - 0.004, 0.024, T(0, spy, SHELF_Z + 0.0175 + 0.012, 90, 0, 0), key="wood_dark", bevel=0.003)

# ---------------------------------------------------------------- 3. Main Workbench Tabletop (Z = TABLE_TOP_Z = 0.860m)
# 5 broad, heavy-duty scarred timber planks along X (rx=90!)
TOP_PLANK_W = (TD - 0.012) / 5
for pi in range(5):
    py = -TD / 2 + TOP_PLANK_W / 2 + pi * (TOP_PLANK_W + 0.002)
    plank(f"top_plank_{pi}", TL, TOP_PLANK_W - 0.003, 0.036, T(0, py, TABLE_TOP_Z - 0.018, 90, 0, 0), key="wood", bevel=0.003)

# Heavy zinc / sheet-metal cladding plate on the right half of the bench for heavy mechanical work
PLATE_X0 = -0.05
PLATE_X1 = TL / 2
PLATE_W = PLATE_X1 - PLATE_X0  # 0.85m
PLATE_D = TD - 0.02            # 0.80m
PLATE_CX = (PLATE_X0 + PLATE_X1) / 2
metal_box("zinc_plate", (PLATE_W, PLATE_D, 0.006), T(PLATE_CX, 0, TABLE_TOP_Z + 0.003), bevel=0.001, tile=0.5, key="metal_plate")

# Perimeter countersunk bolts securing the plate
for bx in (PLATE_X0 + 0.04, PLATE_CX, PLATE_X1 - 0.04):
    for by in (-PLATE_D / 2 + 0.04, +PLATE_D / 2 - 0.04):
        disc("plate_bolt", 0.006, 0.003, T(bx, by, TABLE_TOP_Z + 0.006), "metal", seg=8)

# ---------------------------------------------------------------- 4. Rear Vertical Tool Backboard & Overhead Riser
# Upright steel angle posts at X = LX0 and X = LX1 extending upward from the bench
UPRIGHT_H = 0.620
UPRIGHT_Z = TABLE_TOP_Z + UPRIGHT_H / 2
metal_box("backboard_post_l", (0.045, 0.045, UPRIGHT_H), T(LX0, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")
metal_box("backboard_post_r", (0.045, 0.045, UPRIGHT_H), T(LX1, LY1, UPRIGHT_Z), bevel=0.002, tile=0.3, key="metal_green")

# Heavy timber backboard for hanging tools (Z: 0.88m to 1.38m, height = 0.50m)
BOARD_H = 0.480
BOARD_Z = TABLE_TOP_Z + BOARD_H / 2 + 0.02
plank("tool_backboard", LX1 - LX0, BOARD_H, 0.022, T(0, LY1 + 0.015, BOARD_Z, 0, 0, 0), key="wood_dark", bevel=0.003)

# Top overhead shelf at Z = 1.48m (rx=90!)
TOP_SHELF_Z = TABLE_TOP_Z + UPRIGHT_H
plank("top_shelf_plank", TL - 0.04, 0.20, 0.024, T(0, LY1 - 0.06, TOP_SHELF_Z + 0.012, 90, 0, 0), key="wood", bevel=0.003)
# Front steel retaining curb so bottles/cans don't slide off
metal_box("top_shelf_curb", (TL - 0.04, 0.015, 0.035), T(0, LY1 - 0.16, TOP_SHELF_Z + 0.025), bevel=0.001, tile=0.3, key="metal")

# ---------------------------------------------------------------- 5. Bench Vise (Mounted at Front-Right Corner)
# Authentic Soviet cast-iron workshop bench vise bolted to the zinc plate
# Base flange at Z=0 sits flush on zinc plate at TABLE_TOP_Z + 0.004
VISE_X = 0.58
VISE_Y = -0.28
VISE_Z = TABLE_TOP_Z + 0.004
VISE_RZ = -15
VISE_M = T(VISE_X, VISE_Y, VISE_Z, 0, 0, VISE_RZ)

accent(r"dynamics\workshop_room\tiski", VISE_M, base_z=0.0)

# Mounting flange anchor bolts passing through the 3 cast lugs into tabletop
for lx, ly in ((-0.125, 0.029), (0.125, 0.029), (0.040, 0.117)):
    disc("vise_bolt", 0.008, 0.016, VISE_M @ T(lx, ly, 0.008), "metal", seg=10)

# Workpiece clamped solidly in vise jaws:
# High-pressure steel hydraulic pipe gripped firmly between the jaws (jaw center is at local Y = -0.089, Z = 0.2694)
JAW_Y = -0.0890
JAW_Z = 0.2694
tube("clamped_pipe", [
    VISE_M @ Vector((-0.16, JAW_Y, JAW_Z)),
    VISE_M @ Vector((+0.12, JAW_Y, JAW_Z)),
], 0.016, key="metal", sides=12)

# Hexagonal coupling collar / packing nut on pipe end
disc("pipe_collar", 0.022, 0.018, VISE_M @ T(0.12, JAW_Y, JAW_Z, 0, 90, 0), "metal_plate", seg=12)

# Brass valve handwheel assembly mounted onto the end of the pipe stem (0.32x scale)
accent(r"dynamics\workshop_room\ventil_01", VISE_M @ T(0.135, JAW_Y, JAW_Z, 0, 90, 0), scale=0.32)

# ---------------------------------------------------------------- 6. Tools Hanging on the Backboard
# Tool 1: Machinist hammer hanging horizontally on two pegs at upper center (flat against backboard)
HAMMER_Z = TABLE_TOP_Z + 0.36
accent(r"dynamics\workshop_room\hammer", T(0.00, LY1 - 0.015, HAMMER_Z, 90, 90, 0), scale=0.55)
disc("peg_hammer_1", 0.004, 0.040, T(-0.08, LY1 + 0.005, HAMMER_Z - 0.03, 90, 0, 0), "metal", seg=8)
disc("peg_hammer_2", 0.004, 0.040, T(+0.08, LY1 + 0.005, HAMMER_Z - 0.03, 90, 0, 0), "metal", seg=8)

# Tool 2: Steel wrench / keyga hanging vertically on left peg (flat against backboard)
KEYGA_X = -0.32
KEYGA_Z = TABLE_TOP_Z + 0.24
accent(r"dynamics\workshop_room\keyga", T(KEYGA_X, LY1 - 0.010, KEYGA_Z, 90, 0, 0))
disc("peg_wrench", 0.004, 0.035, T(KEYGA_X, LY1 + 0.005, KEYGA_Z + 0.17, 90, 0, 0), "metal", seg=8)

# Tool 3: Metal file / riffler hanging vertically on right peg (flat against backboard, scaled 0.42x)
RIFFLER_X = +0.28
RIFFLER_Z = TABLE_TOP_Z + 0.24
accent(r"dynamics\workshop_room\riffler", T(RIFFLER_X, LY1 - 0.015, RIFFLER_Z, 90, 0, 0), scale=0.42)
disc("peg_riffler", 0.004, 0.035, T(RIFFLER_X, LY1 + 0.005, RIFFLER_Z + 0.14, 90, 0, 0), "metal", seg=8)

# Tool 4: Hacksaw hanging on far-left of backboard
# Red tubular frame with tension screw and silver blade
HACK_X, HACK_Z = -0.58, TABLE_TOP_Z + 0.32
tube("hacksaw_frame", [
    Vector((HACK_X - 0.16, LY1 - 0.015, HACK_Z - 0.05)),
    Vector((HACK_X - 0.16, LY1 - 0.015, HACK_Z + 0.07)),
    Vector((HACK_X + 0.16, LY1 - 0.015, HACK_Z + 0.07)),
    Vector((HACK_X + 0.16, LY1 - 0.015, HACK_Z - 0.05)),
], 0.006, key="copper", sides=8)
metal_box("hacksaw_blade", (0.32, 0.002, 0.015), T(HACK_X, LY1 - 0.015, HACK_Z - 0.04), bevel=0.0005, tile=0.2, key="metal_plate")
metal_box("hacksaw_handle", (0.025, 0.025, 0.09), T(HACK_X - 0.17, LY1 - 0.015, HACK_Z - 0.02), bevel=0.002, tile=0.3, key="metal_green")
disc("peg_hacksaw", 0.004, 0.040, T(HACK_X, LY1 - 0.01, HACK_Z + 0.08, 90, 0, 0), "metal", seg=8)

# ---------------------------------------------------------------- 7. Overhead Riser Shelf Props (Z = TOP_SHELF_Z)
# Solvent bottle
accent(r"dynamics\repair\solvent", T(-0.45, LY1 - 0.06, TOP_SHELF_Z + 0.024))
# Tub of grease
accent(r"dynamics\repair\grease", T(-0.30, LY1 - 0.06, TOP_SHELF_Z + 0.024))
# Whetstone sharpening stone
accent(r"dynamics\repair\sharpening_stones", T(+0.15, LY1 - 0.06, TOP_SHELF_Z + 0.024))
# Steel wool scouring pad
accent(r"dynamics\repair\steel_wool", T(+0.35, LY1 - 0.06, TOP_SHELF_Z + 0.024))

# ---------------------------------------------------------------- 8. Divided Sheet Metal Scrap Bins (Back-Left of Table)
# 4-compartment divided sheet-metal sorting organizer (centered at X = -0.32, leaving left side open for lamp)
BIN_W = 0.44   # width along X
BIN_D = 0.20   # depth along Y
BIN_H = 0.080  # height
BIN_CX = -0.32
BIN_CY = 0.22
BIN_Z = TABLE_TOP_Z + BIN_H / 2

# Outer sheet metal tray
metal_box("bin_bottom", (BIN_W, BIN_D, 0.005), T(BIN_CX, BIN_CY, TABLE_TOP_Z + 0.003), bevel=0.001, tile=0.3, key="metal_plate")
metal_box("bin_wall_f", (BIN_W, 0.006, BIN_H), T(BIN_CX, BIN_CY - BIN_D / 2, BIN_Z), bevel=0.001, tile=0.3, key="metal_plate")
metal_box("bin_wall_b", (BIN_W, 0.006, BIN_H), T(BIN_CX, BIN_CY + BIN_D / 2, BIN_Z), bevel=0.001, tile=0.3, key="metal_plate")
metal_box("bin_wall_l", (0.006, BIN_D, BIN_H), T(BIN_CX - BIN_W / 2, BIN_CY, BIN_Z), bevel=0.001, tile=0.3, key="metal_plate")
metal_box("bin_wall_r", (0.006, BIN_D, BIN_H), T(BIN_CX + BIN_W / 2, BIN_CY, BIN_Z), bevel=0.001, tile=0.3, key="metal_plate")

# 3 internal dividers
CW = BIN_W / 4  # 0.11m per compartment
for di in (1, 2, 3):
    dx = BIN_CX - BIN_W / 2 + di * CW
    metal_box(f"bin_div_{di}", (0.005, BIN_D - 0.01, BIN_H - 0.005), T(dx, BIN_CY, BIN_Z), bevel=0.001, tile=0.3, key="metal_plate")

# Contents of Bin 1 (Far-Left): Coiled copper salvage wire
tube("copper_coil_1", [
    Vector((BIN_CX - BIN_W / 2 + 0.03, BIN_CY - 0.05, TABLE_TOP_Z + 0.02)),
    Vector((BIN_CX - BIN_W / 2 + 0.08, BIN_CY - 0.03, TABLE_TOP_Z + 0.05)),
    Vector((BIN_CX - BIN_W / 2 + 0.04, BIN_CY + 0.05, TABLE_TOP_Z + 0.04)),
    Vector((BIN_CX - BIN_W / 2 + 0.02, BIN_CY + 0.02, TABLE_TOP_Z + 0.06)),
    Vector((BIN_CX - BIN_W / 2 + 0.07, BIN_CY - 0.01, TABLE_TOP_Z + 0.03)),
], 0.005, key="copper", sides=7)

# Contents of Bin 2: Loose hardware (washers, nuts, bolts)
for hi in range(6):
    hx = BIN_CX - BIN_W / 2 + CW + 0.020 + (hi % 3) * 0.030
    hy = BIN_CY - 0.04 + (hi // 3) * 0.06
    disc(f"hardw_nut_{hi}", 0.012, 0.010, T(hx, hy, TABLE_TOP_Z + 0.012), "metal", seg=6)

# Contents of Bin 3: Radio parts / resistors box
accent(r"dynamics\equipments\quest\box_resistors", T(BIN_CX - BIN_W / 2 + 2.5 * CW, BIN_CY, TABLE_TOP_Z + 0.006, 0, 0, 10))

# Contents of Bin 4 (Far-Right): Rosin / soldering flux tin
accent(r"dynamics\equipments\quest\box_kanifol", T(BIN_CX - BIN_W / 2 + 3.5 * CW, BIN_CY, TABLE_TOP_Z + 0.006, 0, 0, -15))

# ---------------------------------------------------------------- 9. Tabletop Disassembly & Salvage Props (Z = TABLE_TOP_Z)
# Industrial gooseneck inspection lamp clamped to left table edge (clear of bin and hacksaw)
LAMP_X = -0.66
LAMP_Y = 0.02
LAMP_Z = TABLE_TOP_Z + 0.004
accent(r"dynamics\workshop_room\table_lamp_01", T(LAMP_X, LAMP_Y, LAMP_Z, 0, 0, 65))

# Electrical diagnostic continuity checker / multimeter (Center-left)
accent(r"dynamics\equipments\con_checker", T(-0.05, -0.05, TABLE_TOP_Z + 0.006, 0, 0, -12))
# Coiled black and red multimeter probe wires
tube("probe_wire_black", [
    Vector((-0.03, -0.08, TABLE_TOP_Z + 0.010)),
    Vector((-0.08, -0.16, TABLE_TOP_Z + 0.006)),
    Vector((-0.14, -0.12, TABLE_TOP_Z + 0.006)),
    Vector((-0.18, -0.22, TABLE_TOP_Z + 0.010)),
], 0.003, key="metal", sides=6)

tube("probe_wire_red", [
    Vector((-0.01, -0.08, TABLE_TOP_Z + 0.010)),
    Vector((+0.05, -0.15, TABLE_TOP_Z + 0.006)),
    Vector((+0.02, -0.22, TABLE_TOP_Z + 0.006)),
    Vector((+0.08, -0.26, TABLE_TOP_Z + 0.010)),
], 0.003, key="copper", sides=6)

# Metal solvent / paint tin with handle (center of table)
accent(r"dynamics\workshop_room\banka_kraski_1", T(0.18, 0.15, TABLE_TOP_Z + 0.006))

# Roll of black electrical friction tape (izolenta) on the zinc plate
disc("izolenta_tape", 0.036, 0.022, T(0.25, -0.18, TABLE_TOP_Z + 0.017), "metal", seg=16)
disc("izolenta_hole", 0.016, 0.023, T(0.25, -0.18, TABLE_TOP_Z + 0.017), "metal_plate", seg=12)

# Solder wire coil spool
disc("solder_spool_core", 0.026, 0.030, T(0.36, -0.10, TABLE_TOP_Z + 0.020), "metal_tin", seg=14)
disc("solder_spool_rim_t", 0.034, 0.003, T(0.36, -0.10, TABLE_TOP_Z + 0.035), "metal_green", seg=14)
disc("solder_spool_rim_b", 0.034, 0.003, T(0.36, -0.10, TABLE_TOP_Z + 0.005), "metal_green", seg=14)
# Unwound strand of shiny solder wire extending toward the vise
tube("solder_strand", [
    Vector((0.36, -0.07, TABLE_TOP_Z + 0.020)),
    Vector((0.42, -0.05, TABLE_TOP_Z + 0.008)),
    Vector((0.48, -0.12, TABLE_TOP_Z + 0.008)),
], 0.002, key="metal_tin", sides=6)

# Screwdriver resting on zinc plate
SCREW_M = T(0.12, -0.28, TABLE_TOP_Z + 0.012, 0, 0, 35)
metal_box("screwdriver_blade", (0.13, 0.005, 0.005), SCREW_M @ T(0.04, 0, 0), bevel=0.001, tile=0.1, key="metal_plate")
disc("screwdriver_handle", 0.014, 0.09, SCREW_M @ T(-0.06, 0, 0, 0, 90, 0), "copper", seg=10)

# Disassembled salvage electronics: circuit board / PCB resting on bench
PCB_M = T(-0.25, -0.16, TABLE_TOP_Z + 0.005, 0, 0, 8)
metal_box("salvage_pcb", (0.16, 0.11, 0.004), PCB_M, bevel=0.001, tile=0.2, key="metal_green")
# IC chips and capacitor cylinders on the PCB
metal_box("pcb_chip_1", (0.035, 0.025, 0.006), PCB_M @ T(-0.04, 0.02, 0.005), bevel=0.0005, tile=0.1, key="metal")
metal_box("pcb_chip_2", (0.045, 0.018, 0.006), PCB_M @ T(+0.03, -0.02, 0.005), bevel=0.0005, tile=0.1, key="metal")
disc("pcb_cap_1", 0.006, 0.016, PCB_M @ T(-0.03, -0.03, 0.010), "metal_tin", seg=8)
disc("pcb_cap_2", 0.005, 0.012, PCB_M @ T(+0.05, +0.03, 0.008), "copper", seg=8)

# ---------------------------------------------------------------- 10. Lower Storage Shelf Props (Z = SHELF_Z = 0.22m)
# Left side: Heavy steel mechanic toolkit case
accent(r"dynamics\equipments\quest\box_toolkit_1", T(-0.45, 0.05, SHELF_Z + 0.026, 0, 0, 6))

# Center: Galvanized steel scrap bucket filled with metal cutoffs and scrap rods
accent(r"dynamics\workshop_room\vedro_01", T(0.02, 0.02, SHELF_Z + 0.026))
# Scrap steel pipes and angle irons sticking out of the bucket
tube("scrap_rod_1", [
    Vector((0.02, 0.02, SHELF_Z + 0.20)),
    Vector((-0.04, 0.06, SHELF_Z + 0.62)),
], 0.012, key="metal", sides=8)

tube("scrap_pipe_2", [
    Vector((0.04, 0.01, SHELF_Z + 0.20)),
    Vector((0.08, -0.03, SHELF_Z + 0.58)),
], 0.016, key="copper", sides=8)

metal_box("scrap_angle_3", (0.028, 0.028, 0.44), T(0.00, -0.04, SHELF_Z + 0.40, 15, 8, 25), bevel=0.002, tile=0.3, key="metal_plate")

# Right side: Propane blowtorch gas cylinder standing upright
accent(r"dynamics\balon\gaz_balon", T(0.48, 0.04, SHELF_Z + 0.026))

# Heavy lead-acid battery next to the gas cylinder
BAT_X, BAT_Y = 0.28, -0.10
BAT_Z = SHELF_Z + 0.026
metal_box("battery_body", (0.20, 0.14, 0.16), T(BAT_X, BAT_Y, BAT_Z + 0.08), bevel=0.004, tile=0.3, key="metal")
disc("bat_cap_1", 0.012, 0.014, T(BAT_X - 0.05, BAT_Y, BAT_Z + 0.165), "copper", seg=10)
disc("bat_cap_2", 0.012, 0.014, T(BAT_X + 0.05, BAT_Y, BAT_Z + 0.165), "metal_tin", seg=10)

# ---------------------------------------------------------------- Join all parts into salvage_table_visual
visual = join_parts()

# Save a reference .blend
try:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SCR, "models", BLEND))
    print(f'Info: Saved copy as "{BLEND}"')
except Exception as e:
    print(e)
