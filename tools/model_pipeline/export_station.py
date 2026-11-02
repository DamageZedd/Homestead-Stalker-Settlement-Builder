# Exports a pre-atlas HomesteadHF station on plain-Anomaly textures, no atlas (run inside Blender).
#   export_station(cfg) with cfg = dict(name, blend, mesh, overrides, uv_scale, extra)
#     blend     the pre-atlas .blend holding the station's mesh (geometry identical to the shipped model)
#     mesh      object name in that blend
#     overrides {source material name: vanilla texture path} for materials retarget_lib cannot resolve
#     uv_scale  {vanilla texture path: uv multiplier} (<1 enlarges the texture on the surface)
#     extra     optional callable(ob) for per-model UV fixes
# The shipped <name>.object is imported only for its rig (bones, collision boxes, vertex-group names) and is kept
# exactly; the mesh keeps its own bone vertex groups. Material names are the texture paths (models\model).
import bpy, os

WS = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws"          # workspace holding models\*.py
REPO = r"C:\Users\hocke\OneDrive\Documents\GitHub\Homestead-Stalker-Settlement-Builder"
SHIPPED = os.path.join(REPO, r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF")
OUT = os.path.join(WS, "out")


def export_station(cfg, shipped=SHIPPED, out=OUT):
    lib = {}; rt = {}
    exec(open(os.path.join(WS, r"models\export_lib.py")).read(), lib)
    exec(open(os.path.join(WS, r"models\retarget_lib.py")).read(), rt)
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)
    for i in list(bpy.data.images): bpy.data.images.remove(i)
    with bpy.data.libraries.load(cfg["blend"]) as (src, dst):
        dst.objects = [cfg["mesh"]]
    ob = dst.objects[0]
    bpy.context.scene.collection.objects.link(ob)
    mp, unresolved = rt['retarget'](ob, cfg.get("overrides", {}))
    assert not unresolved, unresolved
    if cfg.get("uv_scale"):
        rt['scale_uv'](ob, cfg["uv_scale"])
    if cfg.get("extra"):
        cfg["extra"](ob)
    ob.data.uv_layers[0].name = "Texture"
    ob.name = cfg["name"] + "_visual"
    exp = lib['make_export_vanilla'](cfg["name"] + "_visual", cfg["name"])
    arm = lib['reuse_rig'](exp, cfg["name"], shipped)
    os.makedirs(out, exist_ok=True)
    return lib['export'](arm, out, cfg["name"])[:2]


PRE = r"C:\Users\hocke\Documents\Homestead_backups\pre_atlas_20261025"
STATIONS = {
    "distiller": dict(name="distiller", blend=PRE + r"\distiller_multibone.blend", mesh="wpn_homestead_distiller_visual"),
    "wood_station": dict(name="wood_station", blend=PRE + r"\wood_station_multibone.blend", mesh="wood_station",
                         overrides={"trees_bark_sosna_01": "lfo\\lfo_trees\\bark\\trees_atp_pine_bark", "axe_new_base": "prop\\prop_spade",
                                    "ston_brick": "briks\\briks_br3", "mat_charcoal": "mtl\\mtl_barrel_big_rust"}),
    "market_stall": dict(name="market_stall", blend=PRE + r"\market_stall.blend", mesh="market_stall_visual"),
}
