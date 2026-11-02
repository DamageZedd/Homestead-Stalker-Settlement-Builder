# Wood Station on plain-Anomaly textures (run inside Blender; used by export_station.py).
# Custom saw -> vanilla saw (wood_station_saw.py); custom axe -> vanilla axe, enlarged and leaning, blade sunk in the stump.
import math, os
import numpy as np
from mathutils import Matrix, Vector

WS = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws"
MD = os.path.join(WS, "models")
BARK = "lfo\\lfo_trees\\bark\\trees_atp_pine_bark"
OVERRIDES = {"trees_bark_sosna_01": BARK, "axe_new_base": "prop\\prop_spade", "ston_brick": "briks\\briks_br3",
             "mat_charcoal": "mtl\\mtl_barrel_big_rust"}
AXE_SCALE = 1.7        # on top of matching the old axe's length
AXE_LEAN = 40          # degrees the handle leans from vertical; the bit (blade edge) swings down toward the stump
SINK = 0.025           # metres the lowest point of the blade edge is sunk into the stump top
STUMP_TOP = 0.60       # z of the stump top (wood_spil_1 top face)
AXE_XY = (0.15, -0.311)  # where the blade edge lands on the stump top


def axe_post(placed):
    """Scale 1.7x, then rotate about the thickness axis (y) so the bit points down and the handle leans, and plant
    the cutting edge (the line of bit vertices, parallel to the handle) into the stump top."""
    edge = placed[placed[:, 0] < placed[:, 0].min() + 0.004]       # the bit's edge line
    pivot = edge.mean(0)
    P = Matrix.Translation(Vector(pivot))
    M = P @ Matrix.Rotation(-math.radians(AXE_LEAN), 4, 'Y') @ Matrix.Diagonal((AXE_SCALE, AXE_SCALE, AXE_SCALE, 1.0)) @ P.inverted()
    new = np.array([(M @ Vector(v))[:] for v in placed])
    zmin = new[:, 2].min()
    e_new = np.array([(M @ Vector(v))[:] for v in edge]).mean(0)
    shift = Vector((AXE_XY[0] - e_new[0], AXE_XY[1] - e_new[1], STUMP_TOP - SINK - zmin))
    return Matrix.Translation(shift) @ M

def extra(ob):
    sp = {}; sw = {}; acc = {}
    exec(open(os.path.join(MD, "swap_part.py")).read(), sp)
    exec(open(os.path.join(MD, "wood_station_saw.py")).read(), sw)
    exec(open(os.path.join(MD, "accent_lib.py")).read(), acc)
    ob = sw['swap_saw'](ob, acc)
    ob = sp['swap_part'](ob, acc, lambda lo, hi, m: m == "prop\\prop_spade", "dynamics\\workshop_room\\axe",
                         "prop\\prop_instrument_1", "link", post=axe_post)
    sp['merge_dup_groups'](ob)
    return ob
