# Re-textures the shipped Water Purifier body onto vanilla textures (run inside Blender after
# importing water_purifier.object): each connected part is classified by its colour in the old
# atlas, given one of five vanilla materials and a fresh box/cylinder UV in metres.
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
WS = __import__('os').environ.get('HSHF_WS', r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws")
ns = {"__name__": "b", "NAME": "water_purifier", "COL": None}
exec(open(os.path.join(WS, r"models\wp_analyze.py")).read(), ns)
exec(open(os.path.join(WS, r"models\accent_lib.py")).read(), ns)
exec(open(os.path.join(WS, r"models\build_lib.py")).read().split("# ---------------------------------------------------------------- geometry helpers")[0], ns)

# class -> (vanilla texture, tile size in metres)
CLASSES = {
    "slab":  ("wall\wall_stucco_07", 1.0),
    "tank":  ("mtl\mtl_sarcofag_t", 0.8),
    "pipe":  ("mtl\mtl_truba_pod_02", 0.6),
    "frame": ("mtl\mtl_rust_dark", 0.7),
    "dark":  ("mtl\mtl_barrel_big_rust", 0.7),
}
KEEP = {1: "mtl\mtl_red_painted", 2: "prop\prop_spade", 3: "water\water_pool1"}   # valve wheel, bucket, water


def classify(d):
    r, g, b = d["col"]
    z0, z1 = d["lo"][2], d["hi"][2]
    if z1 < 0.26 and (d["hi"][0] - d["lo"][0]) > 0.5:
        return "slab"
    if b - r > 0.03:
        return "tank"
    if r - b > 0.12:
        return "frame"
    if max(r, g, b) < 0.45:
        return "dark"
    return "pipe"


def retex(ob):
    me = ob.data
    info = ns["analyze"](ob)
    old_mats = {i: m for i, m in enumerate(me.materials)}
    keep_ex = {i: (m.xray.eshader) for i, m in old_mats.items() if i in KEEP}
    new = []
    for i in range(len(me.materials)):
        me.materials.pop(index=0)
    order = list(CLASSES) + [KEEP[1], KEEP[2], KEEP[3]]
    for key in order:
        tex = CLASSES[key][0] if key in CLASSES else key
        for m in list(bpy.data.materials):
            if m.name == tex:
                bpy.data.materials.remove(m)
        m = ns["make_mat"](tex, "models\model")
        me.materials.append(m)
    idx = {k: i for i, k in enumerate(order)}
    uvl = me.uv_layers[0]; uvl.name = "Texture"
    counts = {}
    for d in info:
        cls = classify(d) if d["mat"] == 0 else None
        if d["mat"] != 0:
            key = KEEP[d["mat"]]; tile = 0.4
        else:
            if cls == "pipe" and (d["hi"][0] - d["lo"][0]) > 1.0 and 0.9 < d["lo"][2] and d["hi"][2] < 1.2:
                cls = "frame"; key = CLASSES[cls][0]; tile = 1.4      # the table-top plate: dark rusted steel, larger tile
            else:
                key = CLASSES[cls][0]; tile = CLASSES[cls][1]
            counts[cls] = counts.get(cls, 0) + d["n"]
        mi = idx[cls] if d["mat"] == 0 else idx[key]
        faces = [me.polygons[i] for i in d["faces"]]
        if d["mat"] != 0:
            for p in faces:
                p.material_index = mi   # valve wheel, bucket, water keep their original UVs
            continue
        vs = np.array([me.vertices[v].co[:] for p in faces for v in p.vertices])
        lo, hi = vs.min(0), vs.max(0); ctr = (lo + hi) / 2; ext = hi - lo
        aligned = 0
        for p in faces:
            n = np.array(p.normal[:]); aligned += (np.abs(n).max() > 0.94) * p.area
        tot = sum(p.area for p in faces) or 1
        box = d["mat"] != 0 and False or (aligned / tot > 0.7)
        axis = int(np.argmax(ext)) if ext.max() > 2.0 * np.sort(ext)[1] else 2
        for p in faces:
            p.material_index = mi
            n = np.array(p.normal[:])
            for li in p.loop_indices:
                co = np.array(me.vertices[me.loops[li].vertex_index].co[:])
                if box:
                    a = int(np.argmax(np.abs(n)))
                    uu, vv = [c for c in range(3) if c != a]
                    uvl.data[li].uv = ((co[uu] - lo[uu]) / tile, (co[vv] - lo[vv]) / tile)
                else:
                    o = [c for c in range(3) if c != axis]
                    ang = math.atan2(co[o[1]] - ctr[o[1]], co[o[0]] - ctr[o[0]])
                    rad = max(ext[o[0]], ext[o[1]]) / 2
                    uvl.data[li].uv = (ang / (2 * math.pi) * 2 * math.pi * max(rad, 0.02) / tile, (co[axis] - lo[axis]) / tile)
        if not box:
            # keep each face's u continuous across the atan2 seam
            for p in faces:
                us = [uvl.data[li].uv[0] for li in p.loop_indices]
                per = 2 * math.pi * max(max(ext[c] for c in range(3) if c != axis) / 2, 0.02) / tile
                ref = us[0]
                for li in p.loop_indices:
                    u, v = uvl.data[li].uv
                    while u - ref > per / 2: u -= per
                    while u - ref < -per / 2: u += per
                    uvl.data[li].uv = (u, v)
    return counts
