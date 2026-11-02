# Ammo Bench on plain-Anomaly textures (run inside Blender; used by export_station.py).
# Pre-atlas mesh + hand-tuned vanilla materials; the custom vise and wrench are replaced by the vanilla vise and hammer;
# brass cartridges use the brass strip of wpn\wpn_bullet, bullet tips the lead tip of wpn\shell_545.
import os
WS = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws"
MD = os.path.join(WS, "models")

OVERRIDES = {"wpn_ammo_brass": "wpn\\wpn_bullet", "mtl_scale_brass": "wpn\\wpn_bullet", "wpn_copper_tip": "wpn\\shell_545",
             "prop_hopper_glass": "glas\\glas_dirt", "prop_m2a1_ammo_can": "mtl\\mtl_green_rja_iov",
             "mtl_rust_dark": "mtl\\mtl_rja_02", "mtl_bench_steel": "mtl\\mtl_barrel_big_rust"}
UV_SCALE = {"mtl\\mtl_rja_02": 0.4, "mtl\\mtl_barrel_big_rust": 0.5, "mtl\\mtl_bochka_01": 0.6, "mtl\\mtl_truba_ch_01": 0.6}
BOX = {"mtl\\mtl_green_rja_iov": 0.5, "wood\\wood_box": 0.45, "prop\\prop_dangerbox": 0.45}
BRASS = {"wpn\\wpn_bullet": (0.385, 0.43, 0.57, 0.86), "wpn\\shell_545": (0.75, 0.81, 0.88, 0.93)}   # pure-brass / lead-tip patches


def extra(ob):
    sp = {}; vs = {}; acc = {}
    exec(open(os.path.join(MD, "swap_part.py")).read(), sp)
    exec(open(os.path.join(MD, "ammo_bench_vise.py")).read(), vs)
    exec(open(os.path.join(MD, "accent_lib.py")).read(), acc)
    sp['box_project'](ob, BOX)
    me = ob.data; names = [m.name for m in me.materials]; uvl = me.uv_layers[0].data
    for mat, (u0, u1, v0, v1) in BRASS.items():
        mi = names.index(mat)
        for p in me.polygons:
            if p.material_index != mi:
                continue
            for li in p.loop_indices:
                c = me.vertices[me.loops[li].vertex_index].co
                uvl[li].uv = (u0 + (u1 - u0) * ((c.x * 53 + c.y * 31) % 1.0), v0 + (v1 - v0) * ((c.z * 17) % 1.0))
    ob = vs['swap_vise'](ob, acc)
    ob = sp['swap_part'](ob, acc, lambda lo, hi, m: abs(lo[0] + 0.26) < 0.01 and abs(hi[0] + 0.02) < 0.01 and abs(lo[1] - 0.035) < 0.01
                         and lo[2] > 0.9 and hi[2] < 0.94,
                         "dynamics\\workshop_room\\hammer", "prop\\prop_instrument_1", "link")
    sp['merge_dup_groups'](ob)
    return ob
