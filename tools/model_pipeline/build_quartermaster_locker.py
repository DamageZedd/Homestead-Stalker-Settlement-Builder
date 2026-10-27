# Builds the HomesteadHF Quartermaster Locker in Blender (run inside Blender).
# A two-door Soviet steel locker built from sheet panels with rolled edges, a riveted face frame and
# a divider; each door maps onto one painted door of mtl_shkaf (vents, wear, handle hole). Left door
# padlocked, right door open on a hat shelf (steel helmet, GP-5), a hanging rail and boots; a folded
# army outfit on top. Vanilla accents; material name = texture path.
import os
SCR = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad"
NAME = "quartermaster_locker"
BLEND = os.path.join(SCR, r"models\quartermaster_locker.blend")
exec(open(os.path.join(SCR, r"models\build_lib.py")).read())
start({"shkaf": ("mtl\\mtl_shkaf", "models\\model"), "metal": ("mtl\\mtl_rust_dark", "models\\model"),
       "stencil": ("decal\\decal_ro50210", "models\\model_aref")}, seed=1972)

# mtl_shkaf: painted door columns (u ranges), their v range, the plain door for sides/interior, the riveted strip
DOOR_COLS = [(0.016, 0.246), (0.266, 0.500), (0.516, 0.746)]
DOOR_V = (0.035, 0.996)
# plain sheet: the lower halves of the painted doors (the fourth door has big X scratches that repeat)
PLAINS = [(0.03, 0.23, 0.10, 0.44), (0.28, 0.485, 0.10, 0.44), (0.53, 0.73, 0.10, 0.44)]
STRIP = (0.247, 0.265)
DENS = 0.45            # texture units per metre on plain sheet


def sheet(name, size, matrix, front=None, mirror=False, bevel=0.003, key="shkaf"):
    """A steel panel/box; its local -Y face shows `front` (u0, u1, v0, v1) stretched over it, the
    other faces plain sheet at an even density."""
    bm = beveled_box(Vector(size), bevel)
    uvl = bm.loops.layers.uv.new("Texture")
    pu0, pu1, pv0, pv1 = random.choice(PLAINS)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        if front and ax == 1 and n.y < 0:
            u0, u1, v0, v1 = front
            for l in f.loops:
                p = l.vert.co
                fx = p.x / size[0] + 0.5
                if mirror:
                    fx = 1.0 - fx
                l[uvl].uv = (u0 + fx * (u1 - u0), v0 + (p.z / size[2] + 0.5) * (v1 - v0))
            continue
        a, b = [i for i in range(3) if i != ax]
        if b != 2 and a == 2:
            a, b = b, a            # keep v vertical where the face has a vertical side
        fw, fh = size[a], size[b]
        uw, vh = min(fw * DENS, pu1 - pu0), min(fh * DENS, pv1 - pv0)
        ou = random.uniform(pu0, pu1 - uw); ov = random.uniform(pv0, pv1 - vh)
        for l in f.loops:
            p = l.vert.co
            l[uvl].uv = (ou + (p[a] / fw + 0.5) * uw, ov + (p[b] / fh + 0.5) * vh)
    for f in bm.faces:
        f.material_index = 0
    return finish(bm, name, [key], matrix)


# ---------------------------------------------------------------- the carcass
W, D, LEG, HB, TS = 0.82, 0.50, 0.06, 1.78, 0.012
Z0, ZT = LEG, LEG + HB
for sx in (-1, 1):
    sheet("side", (TS, D, HB), T(sx * (W / 2 - TS / 2), 0, Z0 + HB / 2))
sheet("top", (W, D, TS), T(0, 0, ZT - TS / 2), bevel=0.004)
sheet("bottom", (W - 2 * TS, D - 0.02, TS), T(0, 0.01, Z0 + TS / 2))
sheet("back", (W - 2 * TS, TS, HB - 2 * TS), T(0, D / 2 - TS / 2, Z0 + HB / 2))
sheet("divider", (TS, D - 0.04, HB - 2 * TS), T(0, 0.02, Z0 + HB / 2))
# face frame: riveted stiles, plain rails
FD = 0.02
YF = -D / 2 + FD / 2
STW, CTW, TRH, BRH = 0.025, 0.03, 0.05, 0.07
for sx in (-1, 1):
    sheet("stile", (STW, FD, HB), T(sx * (W / 2 - STW / 2), YF, Z0 + HB / 2), front=(STRIP[0], STRIP[1], DOOR_V[0], DOOR_V[1]))
sheet("stile", (CTW, FD, HB), T(0, YF, Z0 + HB / 2), front=(STRIP[0], STRIP[1], DOOR_V[0], DOOR_V[1]))
sheet("rail", (W, FD, TRH), T(0, YF, ZT - TRH / 2))
sheet("rail", (W, FD, BRH), T(0, YF, Z0 + BRH / 2))
# feet: short angle irons
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = sx * (W / 2 - 0.03), sy * (D / 2 - 0.03)
        metal_box("foot", (0.045, 0.004, LEG), T(cx, cy + sy * 0.02, LEG / 2))
        metal_box("foot", (0.004, 0.045, LEG), T(cx + sx * 0.02, cy, LEG / 2))

# ---------------------------------------------------------------- doors
GAP = 0.004
DW = (W - 2 * STW - CTW) / 2 - 2 * GAP
DH = HB - TRH - BRH - 2 * GAP
DT = 0.022
DZ = Z0 + BRH + GAP + DH / 2
DY = -D / 2 + DT / 2
HX = W / 2 - STW            # right door hinge line (inner edge of the right stile)
OPEN = 100                  # degrees the right door swings out


def door(cx, col, mirror, matrix_extra=Matrix.Identity(4), meeting_side=1):
    m = matrix_extra @ T(cx, DY, DZ)
    sheet("door", (DW, DT, DH), m, front=(col[0], col[1], DOOR_V[0], DOOR_V[1]), mirror=mirror, bevel=0.005)
    # lever handle at the texture's handle hole, 3.5 cm from the meeting edge, mid-height
    hx = meeting_side * (DW / 2 - 0.035)
    metal_box("handle_plate", (0.032, 0.006, 0.10), m @ T(hx, -DT / 2 - 0.003, 0.0))
    metal_box("handle_lever", (0.018, 0.03, 0.022), m @ T(hx, -DT / 2 - 0.018, 0.02))
    metal_box("handle_lever", (0.018, 0.012, 0.09), m @ T(hx, -DT / 2 - 0.031, -0.02))
    return m


# left door: closed, hinged on the left, its painted handle hole mirrored to the meeting edge
LX = -(CTW / 2 + GAP + DW / 2)
lm = door(LX, DOOR_COLS[0], True, meeting_side=1)
# right door: open on its hinge line
RX = CTW / 2 + GAP + DW / 2
hinge = Matrix.Translation((HX, -D / 2, 0)) @ Matrix.Rotation(math.radians(OPEN), 4, 'Z') @ Matrix.Translation((-HX, D / 2, 0))
rm = door(RX, DOOR_COLS[1], False, hinge, meeting_side=-1)
# hinge knuckles on both outer hinge lines
for x in (-HX, HX):
    for z in (DZ - DH * 0.4, DZ, DZ + DH * 0.4):
        tube("knuckle", [Vector((x, -D / 2 - 0.006, z - 0.035)), Vector((x, -D / 2 - 0.006, z + 0.035))], 0.007, key="metal", sides=8, vscale=3)
# hasp from the centre stile over the left door, with the vanilla padlock hanging from it
HZ = DZ + 0.16
metal_box("hasp_plate", (0.07, 0.005, 0.03), T(-0.03, -D / 2 - 0.0035, HZ))
for z in (HZ - 0.008, HZ + 0.008):
    rivet(T(-0.055, -D / 2 - 0.006, z, 90, 0, 0))
tube("staple", [Vector((0.006, -D / 2 - 0.001, HZ - 0.012)), Vector((0.006, -D / 2 - 0.022, HZ - 0.012)),
                Vector((0.006, -D / 2 - 0.022, HZ + 0.012)), Vector((0.006, -D / 2 - 0.001, HZ + 0.012))], 0.0035, key="metal", vscale=3)
decal("stencil", 0.17, 0.085, lm @ T(-0.01, -DT / 2 - 0.0012, 0.30))

# ---------------------------------------------------------------- inside the open compartment
CX0, CX1 = TS / 2, W / 2 - TS
SH = 1.45
sheet("shelf", (CX1 - CX0, D - 0.04, TS), T((CX0 + CX1) / 2, 0.01, SH))
sheet("shelf_lip", (CX1 - CX0, TS, 0.03), T((CX0 + CX1) / 2, -D / 2 + 0.03, SH - 0.012))
tube("rail", [Vector((CX0 + 0.01, 0.02, SH - 0.08)), Vector((CX1 - 0.01, 0.02, SH - 0.08))], 0.008, key="metal", sides=8, vscale=3)
for x in (CX0 + 0.012, CX1 - 0.012):
    metal_box("rail_bracket", (0.004, 0.03, 0.05), T(x, 0.02, SH - 0.07))
accent(r"dynamics\outfit\helm_battle", T(0.2, 0.02, SH + TS / 2, 0, 0, 160))
# the GP-5 hangs from the rail under the shelf (helmet and mask side by side are wider than the compartment)
accent(r"dynamics\outfit\helm_respirator_gp5", T(0.207, 0.0, SH - 0.33, 90, 0, 0) @ Matrix.Diagonal((0.8, 0.8, 0.8, 1)))
accent(r"dynamics\equipments\trade\boots", T(0.2, 0.04, Z0 + TS, 0, 0, 95) @ Matrix.Diagonal((0.95, 0.95, 0.95, 1)))
# a folded army outfit on top of the locker
accent(r"dynamics\outfit\army_outfit", T(0.0, 0.0, ZT, 0, 0, 90) @ Matrix.Diagonal((0.9, 0.82, 0.9, 1)))
# padlock hanging from the staple (the vanilla lock is 24 cm tall: scale it to a real padlock)
accent(r"dynamics\door\door_locker", T(0.006, -D / 2 - 0.03, HZ - 0.075, 0, 0, 8) @ Matrix.Diagonal((0.42, 0.42, 0.42, 1)))

locker = join_parts()
