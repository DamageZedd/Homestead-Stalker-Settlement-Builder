# Builds the HomesteadHF Med Crate in Blender (run inside Blender).
# A Soviet steel field medical chest: rolled edges, pressed ribs, corner caps, toggle latches, folding
# side handles, the lid open on hinges and a stay chain, painted red crosses on white discs (modelled),
# plywood dividers inside holding vanilla medkits, bandages, anti-rad, stims and a drugs kit, and a med bag
# beside it. Material name = texture path.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "med_crate"
BLEND = os.path.join(SCR, r"models\med_crate.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
start({"steel": ("mtl\\mtl_green_rja_iov", "models\\model"), "metal": ("mtl\\mtl_rust_dark", "models\\model"),
       "red": ("mtl\\mtl_red_paint_iov", "models\\model"), "white": ("wall\\wall_house_white_01", "models\\model"),
       "ply": ("wood\\wood_chipboard1", "models\\model")}, seed=103)
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


def steel(name, size, matrix, bevel=0.004):
    return metal_box(name, size, matrix, bevel=bevel, tile=0.8, key="steel")


def disc(name, radius, depth, matrix, key, seg=32):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=radius, radius2=radius, depth=depth)
    uvl = bm.loops.layers.uv.new("Texture")
    for f in bm.faces:
        for l in f.loops:
            l[uvl].uv = (0.5 + l.vert.co.x * 0.8, 0.5 + l.vert.co.y * 0.8)
    return finish(bm, name, [key], matrix, smooth_angle=60)


def red_cross(matrix, size):
    """A painted red cross on a white disc, in the local XY plane facing +Z."""
    disc("cross_disc", size * 0.62, 0.0016, matrix @ Matrix.Translation((0, 0, 0.0008)), "white")
    arm, thick = size * 0.78, size * 0.26
    for rot in (0, 90):
        metal_box("cross_bar", (arm, thick, 0.0012), matrix @ Matrix.Rotation(math.radians(rot), 4, 'Z') @ Matrix.Translation((0, 0, 0.0022)),
                  bevel=0.0002, tile=0.5, key="red")


# ---------------------------------------------------------------- body
L, D, H, T_ = 0.80, 0.45, 0.34, 0.010
FEET = 0.025
Z0 = FEET
steel("floor", (L, D, T_), T(0, 0, Z0 + T_ / 2))
for sy in (-1, 1):
    steel("wall", (L, T_, H), T(0, sy * (D / 2 - T_ / 2), Z0 + H / 2))
for sx in (-1, 1):
    steel("end", (T_, D - 2 * T_, H), T(sx * (L / 2 - T_ / 2), 0, Z0 + H / 2))
# rolled rim around the top edge
for sy in (-1, 1):
    tube("rim", [Vector((-L / 2, sy * (D / 2 - 0.004), Z0 + H)), Vector((L / 2, sy * (D / 2 - 0.004), Z0 + H))], 0.008, key="steel", sides=8, vscale=1)
for sx in (-1, 1):
    tube("rim", [Vector((sx * (L / 2 - 0.004), -D / 2, Z0 + H)), Vector((sx * (L / 2 - 0.004), D / 2, Z0 + H))], 0.008, key="steel", sides=8, vscale=1)
# pressed ribs: two horizontal on each long side, one on each end
for sy in (-1, 1):
    for z in (Z0 + 0.09, Z0 + H - 0.09):
        steel("rib", (L - 0.10, 0.008, 0.022), T(0, sy * (D / 2 + 0.003), z), bevel=0.003)
for sx in (-1, 1):
    steel("rib", (0.008, D - 0.10, 0.022), T(sx * (L / 2 + 0.003), 0, Z0 + H / 2), bevel=0.003)
# feet runners and corner caps
for sx in (-1, 1):
    metal_box("runner", (0.05, D - 0.02, FEET), T(sx * (L / 2 - 0.06), 0, FEET / 2))
# corner caps: thin plates wrapping each vertical corner outside, top and bottom
CP, CT = 0.055, 0.003
for sx in (-1, 1):
    for sy in (-1, 1):
        for zc in (Z0 + CP / 2, Z0 + H - CP / 2 - 0.01):
            metal_box("cap", (CT, CP, CP), T(sx * (L / 2 + CT / 2), sy * (D / 2 - CP / 2), zc), bevel=0.001)
            metal_box("cap", (CP, CT, CP), T(sx * (L / 2 - CP / 2), sy * (D / 2 + CT / 2), zc), bevel=0.001)
            rivet(T(sx * (L / 2 + CT), sy * (D / 2 - CP / 2), zc, 0, sx * 90, 0))
            rivet(T(sx * (L / 2 - CP / 2), sy * (D / 2 + CT), zc, -sy * 90, 0, 0))
# folding side handles: pivots and a U grip hanging down
for sx in (-1, 1):
    xo = sx * (L / 2 + 0.012)
    for y in (-0.07, 0.07):
        metal_box("handle_pivot", (0.014, 0.022, 0.03), T(xo, y, Z0 + H - 0.07))
    tube("handle", [Vector((xo + sx * 0.006, -0.07, Z0 + H - 0.075)), Vector((xo + sx * 0.012, -0.07, Z0 + H - 0.14)),
                    Vector((xo + sx * 0.012, 0.07, Z0 + H - 0.14)), Vector((xo + sx * 0.006, 0.07, Z0 + H - 0.075))], 0.0055, key="metal", sides=8, vscale=3)
# toggle latches on the front
for x in (-0.24, 0.24):
    metal_box("latch_base", (0.05, 0.008, 0.035), T(x, -(D / 2 + 0.004), Z0 + H - 0.05))
    metal_box("latch_lever", (0.03, 0.01, 0.06), T(x, -(D / 2 + 0.011), Z0 + H - 0.045, 12, 0, 0))
# red cross on the front
red_cross(B((0.0, -(D / 2 + 0.0005), Z0 + H * 0.5), X, Z, -Y) if False else
          Matrix.Translation((0.0, -(D / 2 + 0.0005), Z0 + H * 0.48)) @ Matrix.Rotation(math.radians(90), 4, 'X'), 0.16)

# ---------------------------------------------------------------- lid: open past upright on its back hinges
HZ = Z0 + H + 0.004
LID_T = 0.03
OPEN = 108
lid = Matrix.Translation((0, D / 2, HZ)) @ Matrix.Rotation(math.radians(-OPEN), 4, 'X') @ Matrix.Translation((0, -D / 2, -HZ))
steel("lid_top", (L + 0.01, D + 0.01, 0.008), lid @ T(0, 0, HZ + LID_T - 0.004))
for sy in (-1, 1):
    steel("lid_skirt", (L + 0.01, 0.008, LID_T), lid @ T(0, sy * (D / 2 + 0.001), HZ + LID_T / 2))
for sx in (-1, 1):
    steel("lid_skirt", (0.008, D + 0.01, LID_T), lid @ T(sx * (L / 2 + 0.001), 0, HZ + LID_T / 2))
red_cross(lid @ Matrix.Translation((0, 0, HZ + LID_T)), 0.20)
for x in (-0.22, 0.22):
    tube("hinge", [Vector((x - 0.04, D / 2 + 0.006, HZ)), Vector((x + 0.04, D / 2 + 0.006, HZ))], 0.008, key="metal", sides=8, vscale=3)
    metal_box("latch_keeper", (0.04, 0.012, 0.012), lid @ T(x, -(D / 2 + 0.007), HZ + 0.012))
# stay chain from the right end wall to the lid
p0 = Vector((L / 2 - 0.03, 0.10, Z0 + H - 0.04))
p1 = lid @ Vector((L / 2 - 0.03, -0.05, HZ + 0.01))
pts = [p0.lerp(p1, t) - Vector((0, 0, math.sin(math.pi * t) * 0.03)) for t in [i / 8 for i in range(9)]]
tube("stay", pts, 0.003, key="metal", sides=6, vscale=10)

# ---------------------------------------------------------------- inside: plywood dividers and stock
FZ = Z0 + T_
IL, ID = L - 2 * T_, D - 2 * T_
for x in (-0.12, 0.14):
    metal_box("divider", (0.008, ID, 0.17), T(x, 0, FZ + 0.085), bevel=0.0015, tile=0.9, key="ply")
metal_box("divider", (0.12 + 0.26 - 0.008, 0.008, 0.17), T(0.01, 0.02, FZ + 0.085), bevel=0.0015, tile=0.9, key="ply")
RAISE = FZ + 0.17      # a false floor so the stock shows above the rim
metal_box("false_floor", (IL - 0.004, ID - 0.004, 0.008), T(0, 0, RAISE - 0.004), bevel=0.001, tile=0.9, key="ply")
# left bay: medkits stacked by tier
for i, rel in enumerate([r"dynamics\devices\dev_aptechka\dev_aptechka_low", r"dynamics\devices\dev_aptechka\dev_aptechka_mid", r"dynamics\devices\dev_aptechka\dev_aptechka_high"]):
    accent(rel, T(-0.26, -0.07 + (i % 2) * 0.13, RAISE + (i // 2) * 0.04 + (i % 2) * 0.0, 0, 0, 90 + random.uniform(-6, 6)))
accent(r"dynamics\devices\dev_aptechka\dev_aptechka_low", T(-0.26, 0.06, RAISE + 0.038, 0, 0, 84))
# middle bay: bandages and anti-rad
for i in range(3):
    accent(r"dynamics\devices\dev_bandage\dev_bandage", T(0.0, -0.12 + i * 0.0, RAISE + i * 0.058, 0, 0, random.uniform(-8, 8)))
for i in range(3):
    accent(r"dynamics\devices\dev_antirad\dev_antirad", T(-0.05 + i * 0.05, 0.11, RAISE, 0, 0, random.uniform(-10, 10)))
# right bay: the drugs kit and stims
accent(r"dynamics\equipments\trade\drugskit", T(0.27, -0.05, RAISE, 0, 0, 90))
for i in range(3):
    accent(r"dynamics\equipments\medical\stim1", T(0.23 + i * 0.04, 0.15, RAISE, 0, 0, random.uniform(-10, 10)), ratio=0.3)
# a med bag on the ground against the left end
accent(r"dynamics\equipments\dev_med_bag", T(-L / 2 - 0.17, -0.06, 0.0, 0, 0, 80))

med = join_parts()
