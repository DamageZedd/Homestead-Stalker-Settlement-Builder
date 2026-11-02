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
AXE_TILT = 18          # degrees, leaning toward +x
SINK = 0.012            # metres the blade is sunk into the stump top


def axe_post(placed):
    """Scale about the blade tip (lowest point), lean the handle, then sink the blade a little."""
    tip = placed[np.argmin(placed[:, 2])]
    T = Matrix.Translation(Vector(tip))
    return (Matrix.Translation((0, 0, -SINK)) @ T @ Matrix.Rotation(math.radians(AXE_TILT), 4, 'Y')
            @ Matrix.Diagonal((AXE_SCALE, AXE_SCALE, AXE_SCALE, 1.0)) @ T.inverted())


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
