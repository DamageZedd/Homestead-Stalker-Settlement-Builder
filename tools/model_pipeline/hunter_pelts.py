# Hunter Station: the pelts/hides keep their custom art, carved out of the old atlas into one small texture
# (textures\homestead_hf\hunter_pelts.dds). Everything else stays on vanilla textures (run inside Blender).
#   1. dump_tris(shipped_dir, pre_blend, out_json)  - matches the shipped (atlas-UV) triangles to the pre-atlas pelt polygons
#   2. python pack_pelts.py atlas.dds tris.json pelts.png map.json
#   3. apply_pelts(ob, tris_json, map_json, png) - after retarget(): UVs of the pelt faces from the packed sheet
import bpy, json, os
import numpy as np

PELT_MATS = {"act\\act_plot", "mat_hunter_raw_flesh_hide", "mat_hunter_pseudodog_pelt",
             "mat_hunter_pseudodog_pelt_back", "mat_hunter_leather_pelt"}
PELT_TEX = "homestead_hf\\hunter_pelts"
# retarget() overrides: every pelt material ends on the one dedicated texture
OVERRIDES = {m: PELT_TEX for m in PELT_MATS}


def dump_tris(ship, pre, out_json):
    """ship = imported shipped mesh object (atlas UVs), pre = pre-atlas mesh object (before retarget())."""
    me = pre.data; sm = ship.data
    names = [m.name for m in me.materials]
    pp = [p for p in me.polygons if names[p.material_index] in PELT_MATS]
    tri_c = np.array([np.mean([sm.vertices[v].co[:] for v in p.vertices], axis=0) for p in sm.polygons])
    tri_n = np.array([p.normal[:] for p in sm.polygons])
    uvl = sm.uv_layers[0].data
    tris = []
    for k, p in enumerate(pp):
        vs = np.array([me.vertices[v].co[:] for v in p.vertices]); lo = vs.min(0) - 1e-3; hi = vs.max(0) + 1e-3
        n = np.array(p.normal[:]); d = np.abs((tri_c - vs[0]) @ n)
        m = (tri_c >= lo).all(1) & (tri_c <= hi).all(1) & (d < 2e-3) & ((tri_n @ n) > 0.9)
        for i in np.where(m)[0]:
            sp = sm.polygons[i]
            tris.append(dict(owner=k, pos=[list(sm.vertices[sm.loops[li].vertex_index].co) for li in sp.loop_indices],
                             uv=[list(uvl[li].uv) for li in sp.loop_indices]))
    json.dump(dict(tris=tris), open(out_json, "w"))
    return len(tris), len(pp)


def apply_pelts(ob, tris_json, map_json, png):
    me = ob.data
    names = [m.name for m in me.materials]
    mi = names.index(PELT_TEX)
    mp = json.load(open(map_json))["uv"]
    tris = json.load(open(tris_json))["tris"]
    by_owner = {}
    for i, t in enumerate(tris):
        by_owner.setdefault(t["owner"], []).append(i)
    pp = [p for p in me.polygons if p.material_index == mi]
    uvl = me.uv_layers[0].data
    miss = 0
    for k, p in enumerate(pp):
        cand = []
        for ti in by_owner.get(k, []):
            for pos, uv in zip(tris[ti]["pos"], mp[str(ti)]):
                cand.append((np.array(pos), uv))
        for li in p.loop_indices:
            co = np.array(me.vertices[me.loops[li].vertex_index].co[:])
            best = min(cand, key=lambda c: np.abs(c[0] - co).sum()) if cand else None
            if best is None or np.abs(best[0] - co).sum() > 2e-3:
                miss += 1
                if best is None:
                    continue
            uvl[li].uv = best[1]
    mat = me.materials[mi]
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            n.image = bpy.data.images.load(png, check_existing=True)
    return miss
