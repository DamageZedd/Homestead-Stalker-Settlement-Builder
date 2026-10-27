# Build script for HomesteadHF Settlement Flag (run inside Blender).
# Freestanding garrison flagpole hub: pedestal base with 4 radial outriggers, guy wires,
# heavy storage footlocker chest (the camp's 300 kg main storage), sectional mast with
# finial spear, hanging kerosene storm lantern, cross-spar, and draped faction banner.
import bpy, bmesh, os, math
from mathutils import Vector, Matrix, Euler

NAME = "settlement_flag"
BLEND = "settlement_flag.blend"

SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())

materials = {
    "metal": ("mtl\\mtl_rust_dark", "models\\model"),
    "metal_green": ("mtl\\mtl_pod_green", "models\\model"),
    "metal_plate": ("mtl\\mtl_pod_02", "models\\model"),
    "metal_tin": ("prop\\prop_iten4", "models\\model"),
    "brass": ("mtl\\mtl_ventil_pod_01", "models\\model"),
    "wood": ("wood\\wood_box", "models\\model"),
    "wood_dark": ("wood\\wood_jasik", "models\\model"),
    "canvas": ("prop\\prop_brezent", "models\\model"),
    "flag_stalker": ("prop\\flag_stalker", "models\\model"),
}

start(materials)

def disc(name, radius, depth, matrix, key, seg=16):
    """Planar disc for flat circular plates and washers."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    s = 1.0 / (radius * 2.2)
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
    return finish(bm, name, [key], matrix, smooth_angle=55)

def cylinder(name, radius, depth, matrix, key, seg=16, vscale=3.0, cap_ends=True):
    """Cylindrical unwrap for vertical pipes and poles: side walls map u around circumference, v along height."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("Texture")
    z_bot = -depth / 2.0
    z_top = +depth / 2.0
    ring_bot = []
    ring_top = []
    for k in range(seg):
        ang = 2.0 * math.pi * k / seg
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        ring_bot.append(bm.verts.new((x, y, z_bot)))
        ring_top.append(bm.verts.new((x, y, z_top)))
    
    # Side quad faces (wound outwards)
    for k in range(seg):
        k2 = (k + 1) % seg
        f = bm.faces.new([ring_bot[k], ring_bot[k2], ring_top[k2], ring_top[k]])
        for l, (uu, vv) in zip(f.loops, [(k, 0.0), (k + 1, 0.0), (k + 1, depth * vscale), (k, depth * vscale)]):
            l[uvl].uv = (uu / seg, vv)
            
    if cap_ends:
        # bottom cap (normal -Z): reversed order
        f_bot = bm.faces.new(list(reversed(ring_bot)))
        s = 1.0 / (radius * 2.2)
        for l in f_bot.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
        # top cap (normal +Z)
        f_top = bm.faces.new(ring_top)
        s = 1.0 / (radius * 2.2)
        for l in f_top.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * s, 0.5 + l.vert.co.y * s)
            
    return finish(bm, name, [key], matrix, smooth_angle=55)

# ---------------------------------------------------------------- Dynamic Cloth Wave & Banner Builder
def banner_wave_y(x, z, x0=0.05, x1=0.65, z0=1.55, z1=2.20):
    """Calculates organic 3D wind wave depth (peak-to-trough ~16.5cm) across banner surface."""
    u = (x - x0) / (x1 - x0)
    v = (z - z0) / (z1 - z0)
    billow = 0.20 + 0.80 * ((1.0 - v) ** 0.85)
    wave_h1 = 0.055 * math.sin(u * 5.2 + 0.3)
    wave_h2 = 0.024 * math.sin(u * 10.5 + 1.1)
    wave_diag = 0.020 * math.cos(u * 4.2 - v * 5.0 + 0.5)
    wave_v = 0.012 * math.sin((1.0 - v) * 7.5 + u * 2.0)
    return (wave_h1 + wave_h2 + wave_diag + wave_v) * billow

def create_draped_banner(name, x0, x1, z0, z1, mat_key, nx=24, nz=28):
    """Creates a draped cloth banner with realistic dynamic 3D wind billowing folds."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("Texture")
    
    verts_grid = []
    w = x1 - x0
    h = z1 - z0
    
    for j in range(nz):
        v = j / (nz - 1)
        row = []
        for i in range(nx):
            u = i / (nx - 1)
            x = x0 + u * w
            z = z0 + v * h
            y = banner_wave_y(x, z, x0, x1, z0, z1)
            vert = bm.verts.new((x, y, z))
            row.append((vert, u, v))
        verts_grid.append(row)
    
    bm.verts.ensure_lookup_table()
    
    # Front faces (normal pointing toward -Y, facing forward)
    for j in range(nz - 1):
        for i in range(nx - 1):
            v00, u00, v_00 = verts_grid[j][i]
            v10, u10, v_10 = verts_grid[j][i + 1]
            v11, u11, v_11 = verts_grid[j + 1][i + 1]
            v01, u01, v_01 = verts_grid[j + 1][i]
            
            f = bm.faces.new([v00, v10, v11, v01])
            for loop, (u, v) in zip(f.loops, [(u00, v_00), (u10, v_10), (u11, v_11), (u01, v_01)]):
                loop[uvl].uv = (u, v)
    
    # Back faces (normal pointing toward +Y, facing rear)
    verts_grid_back = []
    for j in range(nz):
        row_b = []
        for i in range(nx):
            orig, u, v = verts_grid[j][i]
            vb = bm.verts.new((orig.co.x, orig.co.y + 0.002, orig.co.z))
            row_b.append((vb, u, v))
        verts_grid_back.append(row_b)
        
    bm.verts.ensure_lookup_table()
    
    for j in range(nz - 1):
        for i in range(nx - 1):
            v00, u00, v_00 = verts_grid_back[j][i]
            v10, u10, v_10 = verts_grid_back[j][i + 1]
            v11, u11, v_11 = verts_grid_back[j + 1][i + 1]
            v01, u01, v_01 = verts_grid_back[j + 1][i]
            
            # Reversed winding for rear face
            f = bm.faces.new([v01, v11, v10, v00])
            for loop, (u, v) in zip(f.loops, [(1.0 - u01, v_01), (1.0 - u11, v_11), (1.0 - u10, v_10), (1.0 - u00, v_00)]):
                loop[uvl].uv = (u, v)
                
    return finish(bm, name, [mat_key], Matrix.Identity(4), smooth_angle=65)

# ---------------------------------------------------------------- 1. Base Pedestal & Radial Outriggers
# Central octagonal steel base plate on the ground
disc("base_plate", 0.20, 0.012, T(0, 0, 0.006), "metal", seg=8)

# Concrete / heavy steel ring ballast collar encircling mast base (R = 0.13m, H = 0.07m)
cylinder("ballast_collar", 0.13, 0.070, T(0, 0, 0.047), "metal_plate", seg=12, vscale=2.0)

# Central welded mast socket collar (R = 0.038m, H = 0.18m)
cylinder("socket_pipe", 0.038, 0.180, T(0, 0, 0.090), "metal_green", seg=12, vscale=3.0)

# 4 radial angle-iron outrigger stabilizer legs
# Front legs at 45 and 135 deg; rear legs angled outward at 210 and 330 deg to generously flank chest
OUTRIGGERS = [
    (45, 0.40),
    (135, 0.40),
    (210, 0.42),
    (330, 0.42),
]
for ang_deg, out_r in OUTRIGGERS:
    rad = math.radians(ang_deg)
    mid_x, mid_y = math.cos(rad) * (out_r / 2 + 0.04), math.sin(rad) * (out_r / 2 + 0.04)
    tip_x, tip_y = math.cos(rad) * out_r, math.sin(rad) * out_r
    
    # Diagonal angle-iron stabilizer leg
    ROT_M = T(mid_x, mid_y, 0.020, 0, 0, ang_deg)
    metal_box(f"outrigger_{ang_deg}", (out_r, 0.035, 0.035), ROT_M, bevel=0.002, tile=0.3, key="metal")
    
    # Outer foot pad with anchor ground spike
    metal_box(f"foot_pad_{ang_deg}", (0.075, 0.075, 0.008), T(tip_x, tip_y, 0.004), bevel=0.001, tile=0.2, key="metal_plate")
    disc(f"anchor_bolt_{ang_deg}", 0.006, 0.012, T(tip_x, tip_y, 0.010), "metal", seg=8)

# ---------------------------------------------------------------- 2. Settlement Main Storage Chest (Footlocker)
# Weathered military wooden field stash chest nestled behind the mast between rear outriggers
# Zero clipping: >3cm clearance from ballast collar, >9cm from guy wires, >3.9cm from legs
CHEST_X = 0.00
CHEST_Y = -0.29
CHEST_W = 0.38
CHEST_D = 0.24
CHEST_H = 0.22
CHEST_Z = 0.012 + CHEST_H / 2

# Main trunk body - authentic weathered dark crate wood
metal_box("chest_body", (CHEST_W, CHEST_D, CHEST_H), T(CHEST_X, CHEST_Y, CHEST_Z), bevel=0.003, tile=0.4, key="wood")

# Reinforced lid - authentic weathered dark crate wood with steel trim
LID_H = 0.035
LID_Z = 0.012 + CHEST_H + LID_H / 2
metal_box("chest_lid", (CHEST_W + 0.02, CHEST_D + 0.02, LID_H), T(CHEST_X, CHEST_Y, LID_Z), bevel=0.002, tile=0.3, key="wood")

# Steel corner reinforcing brackets on chest (8 corners)
for cx in (-CHEST_W / 2 + 0.015, +CHEST_W / 2 - 0.015):
    for cy in (CHEST_Y - CHEST_D / 2 + 0.015, CHEST_Y + CHEST_D / 2 - 0.015):
        for cz in (0.012 + 0.025, 0.012 + CHEST_H - 0.025):
            metal_box("corner_bracket", (0.035, 0.035, 0.050), T(cx, cy, cz), bevel=0.001, tile=0.1, key="metal")

# Horizontal strengthening iron bands on chest front and back
for rz in (0.07, 0.16):
    metal_box("chest_strap_f", (CHEST_W - 0.04, 0.006, 0.016), T(CHEST_X, CHEST_Y - CHEST_D / 2 - 0.003, rz), bevel=0.001, tile=0.2, key="metal")
    metal_box("chest_strap_b", (CHEST_W - 0.04, 0.006, 0.016), T(CHEST_X, CHEST_Y + CHEST_D / 2 + 0.003, rz), bevel=0.001, tile=0.2, key="metal")

# Front latch hasp and padlock
HASP_Y = CHEST_Y - CHEST_D / 2 - 0.006
metal_box("hasp_plate", (0.030, 0.008, 0.055), T(CHEST_X, HASP_Y, 0.012 + CHEST_H), bevel=0.001, tile=0.1, key="metal")
# Brass padlock
disc("padlock_body", 0.011, 0.018, T(CHEST_X, HASP_Y - 0.010, 0.012 + CHEST_H - 0.022), "brass", seg=10)
tube("padlock_shackle", [
    Vector((CHEST_X - 0.007, HASP_Y - 0.010, 0.012 + CHEST_H - 0.012)),
    Vector((CHEST_X - 0.007, HASP_Y - 0.010, 0.012 + CHEST_H + 0.002)),
    Vector((CHEST_X + 0.007, HASP_Y - 0.010, 0.012 + CHEST_H + 0.002)),
    Vector((CHEST_X + 0.007, HASP_Y - 0.010, 0.012 + CHEST_H - 0.012)),
], 0.0025, key="metal")

# Side drop carry handles
for sx in (-CHEST_W / 2 - 0.010, +CHEST_W / 2 + 0.010):
    tube(f"chest_handle_{sx}", [
        Vector((sx, CHEST_Y - 0.04, 0.14)),
        Vector((sx + (0.030 if sx > 0 else -0.030), CHEST_Y, 0.12)),
        Vector((sx, CHEST_Y + 0.04, 0.14)),
    ], 0.004, key="metal")

# Military stencil plate on chest lid
metal_box("stencil_plate", (0.14, 0.07, 0.002), T(CHEST_X, CHEST_Y, LID_Z + LID_H / 2 + 0.001), bevel=0.0005, tile=0.1, key="metal_tin")

# ---------------------------------------------------------------- 3. Vertical Mast & Top Finial (Z = 0.0 to 2.48m)
# Lower mast section (heavy pipe, OD ~ 52mm) with cylindrical unwrap
cylinder("mast_lower", 0.026, 1.15, T(0, 0, 1.15 / 2), "metal_green", seg=16, vscale=3.0)

# Mid-height flanged coupling sleeve at Z = 1.15m
cylinder("mast_coupler", 0.034, 0.060, T(0, 0, 1.150), "metal_plate", seg=14, vscale=2.0)
disc("coupler_bolt_1", 0.005, 0.012, T(0.032, 0, 1.150), "metal", seg=6)
disc("coupler_bolt_2", 0.005, 0.012, T(-0.032, 0, 1.150), "metal", seg=6)

# Upper mast section (OD ~ 44mm, Z = 1.15 to 2.38m) with cylindrical unwrap
UPPER_H = 2.38 - 1.15
cylinder("mast_upper", 0.022, UPPER_H, T(0, 0, 1.15 + UPPER_H / 2), "metal_green", seg=16, vscale=3.0)

# Masthead brass collar at Z = 2.38m
cylinder("masthead_collar", 0.028, 0.030, T(0, 0, 2.380), "brass", seg=14, vscale=2.0)

# Top decorative brass sphere finial base
disc("finial_sphere", 0.024, 0.036, T(0, 0, 2.405), "brass", seg=12)

# Spearhead spire finial (Z = 2.42 to 2.50m)
disc("finial_spire_base", 0.014, 0.030, T(0, 0, 2.435), "brass", seg=10)
disc("finial_spire_tip", 0.006, 0.045, T(0, 0, 2.470), "brass", seg=8)

# ---------------------------------------------------------------- 4. Guy Wires & Cleat
# Guy wire collar ring at Z = 1.40m
GUY_Z = 1.40
cylinder("guy_collar", 0.028, 0.025, T(0, 0, GUY_Z), "metal", seg=12, vscale=2.0)

# 4 braided steel guy wires anchored down to each outrigger foot pad (zero clipping to chest)
for gi, (ang_deg, out_r) in enumerate(OUTRIGGERS):
    rad = math.radians(ang_deg)
    tip_x, tip_y = math.cos(rad) * out_r, math.sin(rad) * out_r
    tube(f"guy_wire_{gi}", [
        Vector((0, 0, GUY_Z)),
        Vector((tip_x, tip_y, 0.015)),
    ], 0.0025, key="metal", sides=6)
    # Turnbuckle tensioner near base (t = 0.82)
    tb_pos = Vector((tip_x * 0.82, tip_y * 0.82, GUY_Z * 0.18 + 0.015 * 0.82))
    cylinder(f"turnbuckle_{gi}", 0.007, 0.035, T(tb_pos.x, tb_pos.y, tb_pos.z, 25, 0, ang_deg), "metal_plate", seg=8, vscale=2.0)

# Rope tie-off cleat at Z = 0.95m on front of mast (+Y)
CLEAT_Z = 0.95
metal_box("cleat_base", (0.015, 0.012, 0.055), T(0, 0.028, CLEAT_Z), bevel=0.001, tile=0.1, key="metal")
tube("cleat_horn", [
    Vector((0, 0.035, CLEAT_Z - 0.045)),
    Vector((0, 0.035, CLEAT_Z + 0.045)),
], 0.005, key="metal")

# Coiled hemp halyard rope around cleat
tube("rope_coil_1", [
    Vector((-0.018, 0.032, CLEAT_Z - 0.020)),
    Vector((+0.018, 0.032, CLEAT_Z + 0.020)),
    Vector((-0.018, 0.032, CLEAT_Z + 0.020)),
    Vector((+0.018, 0.032, CLEAT_Z - 0.020)),
], 0.004, key="wood_dark", sides=6)

# ---------------------------------------------------------------- 5. Horizontal Cross-Yard Spar (Z = 2.22m)
SPAR_Z = 2.22
SPAR_X0 = -0.05
SPAR_X1 = 0.68
# Welded cross-tee bracket on mast
metal_box("spar_tee", (0.055, 0.055, 0.040), T(0, 0, SPAR_Z), bevel=0.002, tile=0.2, key="metal")

# Horizontal spar tube extending toward +X
tube("cross_spar", [
    Vector((SPAR_X0, 0, SPAR_Z)),
    Vector((SPAR_X1, 0, SPAR_Z)),
], 0.011, key="metal_green", sides=10)

# Brass end caps on spar
disc("spar_cap_l", 0.015, 0.012, T(SPAR_X0, 0, SPAR_Z, 0, 90, 0), "brass", seg=10)
disc("spar_cap_r", 0.016, 0.015, T(SPAR_X1, 0, SPAR_Z, 0, 90, 0), "brass", seg=10)

# Diagonal brace strut under spar from mast to spar (Z=2.00 to Z=2.22, X=0.0 to X=0.22)
tube("spar_strut", [
    Vector((0.022, 0, 2.02)),
    Vector((0.24, 0, SPAR_Z - 0.010)),
], 0.006, key="metal", sides=8)

# ---------------------------------------------------------------- 6. Draped Faction Banner (Emblem is Entire Flag, Dynamic 3D Waves)
BANNER_X0 = 0.05
BANNER_X1 = 0.65  # width = 0.60m
BANNER_Z0 = 1.55  # height = 0.65m
BANNER_Z1 = 2.20

create_draped_banner("banner_cloth", BANNER_X0, BANNER_X1, BANNER_Z0, BANNER_Z1, "flag_stalker", nx=24, nz=28)

# Top edge reinforced hem strip swept along the top wave curve
top_curve = [Vector((BANNER_X0 + (i / 16) * (BANNER_X1 - BANNER_X0), banner_wave_y(BANNER_X0 + (i / 16) * (BANNER_X1 - BANNER_X0), BANNER_Z1), BANNER_Z1 + 0.003)) for i in range(17)]
tube("banner_hem_top", top_curve, 0.004, key="canvas", sides=6, vscale=4.0)

# Bottom edge reinforced hem strip swept along the bottom wave curve
bot_curve = [Vector((BANNER_X0 + (i / 16) * (BANNER_X1 - BANNER_X0), banner_wave_y(BANNER_X0 + (i / 16) * (BANNER_X1 - BANNER_X0), BANNER_Z0), BANNER_Z0 - 0.003)) for i in range(17)]
tube("banner_hem_bot", bot_curve, 0.004, key="canvas", sides=6, vscale=4.0)

# 5 brass grommet eyelets along top edge (precisely placed on the wavy cloth top)
for gi, gx in enumerate((0.10, 0.22, 0.35, 0.48, 0.60)):
    gy = banner_wave_y(gx, BANNER_Z1)
    disc(f"grommet_{gi}", 0.008, 0.004, T(gx, gy, BANNER_Z1, 90, 0, 0), "brass", seg=10)
    # Hemp rope loop wrapping around cross-spar
    tube(f"rope_loop_{gi}", [
        Vector((gx, gy - 0.012, BANNER_Z1)),
        Vector((gx, -0.012, SPAR_Z + 0.012)),
        Vector((gx, +0.012, SPAR_Z + 0.012)),
        Vector((gx, gy + 0.014, BANNER_Z1)),
    ], 0.0025, key="wood_dark", sides=6)

# 3 guide rings securing left edge of banner to the vertical mast
for ri, rz in enumerate((2.05, 1.85, 1.62)):
    ry = banner_wave_y(BANNER_X0, rz)
    tube(f"mast_ring_{ri}", [
        Vector((0.022, -0.012, rz)),
        Vector((BANNER_X0 + 0.005, ry - 0.006, rz)),
        Vector((BANNER_X0 + 0.005, ry + 0.006, rz)),
        Vector((0.022, +0.012, rz)),
    ], 0.0025, key="brass", sides=6)

# ---------------------------------------------------------------- 7. Mast Hanging Storm Lantern
# Iron hanger bracket on -X side of mast at Z = 1.72m
tube("lantern_bracket", [
    Vector((-0.022, 0, 1.72)),
    Vector((-0.16, 0, 1.74)),
    Vector((-0.16, 0, 1.68)),
], 0.005, key="metal", sides=8)

# Real in-game kerosene/gas lantern (dynamics\placeable\gas_lamp) hanging from bracket
accent(r"dynamics\placeable\gas_lamp", T(-0.16, 0.00, 1.512, 0, 0, 15))

# ---------------------------------------------------------------- 8. Join Parts into settlement_flag_visual
visual = join_parts()
