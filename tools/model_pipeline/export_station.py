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

WS = __import__('os').environ.get('HSHF_WS', r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws")          # workspace holding models\*.py
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
    if cfg.get("saw"):                       # wood station: vanilla saw instead of the custom one
        sw = {}; acc = {}
        exec(open(os.path.join(WS, r"models\wood_station_saw.py")).read(), sw)
        exec(open(os.path.join(WS, r"models\accent_lib.py")).read(), acc)
        ob = sw['swap_saw'](ob, acc)
    if cfg.get("extra"):
        ob = cfg["extra"](ob) or ob
    ob.data.uv_layers[0].name = "Texture"
    ob.name = cfg["name"] + "_visual"
    exp = lib['make_export_vanilla'](cfg["name"] + "_visual", cfg["name"])
    arm = lib['reuse_rig'](exp, cfg["name"], shipped)
    os.makedirs(out, exist_ok=True)
    return lib['export'](arm, out, cfg["name"])[:2]


PRE = r"C:\Users\hocke\Documents\Homestead_backups\pre_atlas_20261025"
STATIONS = {
    "distiller": dict(name="distiller", blend=PRE + r"\distiller_multibone.blend", mesh="wpn_homestead_distiller_visual"),
    "wood_station": dict(name="wood_station", blend=PRE + r"\wood_station_multibone.blend", mesh="wood_station"),
    "market_stall": dict(name="market_stall", blend=PRE + r"\market_stall.blend", mesh="market_stall_visual"),
}

_BARK = "lfo\\lfo_trees\\bark\\trees_atp_pine_bark"
STATIONS["generator_station"] = dict(
    name="generator_station", blend=PRE + r"\generator_station_multibone.blend", mesh="generator_station_mesh",
    overrides={"prop_accumulator_6st60": "item\\item_battery", "mat_cable_red": "prop\\prop_provod_01", "mat_cable_black": "prop\\prop_provod_02",
               "act\\psu\\psu_battery_screen.009": "item\\item_battery", "act\\psu\\psu_battery_overall.009": "item\\item_battery"})
STATIONS["hunter_station"] = dict(
    name="hunter_station", blend=PRE + r"\hunter_station_multibone.blend", mesh="hunter_station_visual",
    overrides={"mat_hunter_pine_bark": _BARK, "mat_hunter_pine_bark.001": _BARK, "act\\act_plot": "act\\act_dogs_brown_soc",
               "mat_hunter_raw_flesh_hide": "food\\food_raw_flesh", "mat_hunter_pseudodog_pelt": "act\\act_dogs_black",
               "mat_hunter_pseudodog_pelt_back": "act\\act_dogs_black", "mat_hunter_leather_pelt": "act\\act_dogs_brown"})
STATIONS["repair_bench"] = dict(
    name="repair_bench", blend=PRE + r"\repair_bench_multibone.blend", mesh="repair_bench.001",
    overrides={"aml_mags\\cartridges\\wpn_eft_ak74_ammo_545x39_diff.002": "wpn\\wpn_bullet",
               "aml_mags\\ak545x39_mag\\wpn_eft_ak74_mag_30rnd_diff.002": "wpn\\wpn_addons\\wpn_addon_mag_ar_30rd"})

_am = {}
exec(open(os.path.join(WS, "models" + chr(92) + "ammo_bench.py")).read(), _am)
STATIONS["ammo_bench"] = dict(name="ammo_bench", blend=PRE + chr(92) + "ammo_bench_multibone.blend", mesh="ammo_bench",
                              overrides=_am["OVERRIDES"], uv_scale=_am["UV_SCALE"], extra=_am["extra"])

_wsn = {}
exec(open(os.path.join(WS, "models" + chr(92) + "wood_station.py")).read(), _wsn)
STATIONS["wood_station"].update(overrides=_wsn["OVERRIDES"], extra=_wsn["extra"])

_hs = {}
exec(open(os.path.join(WS, "models" + chr(92) + "hunter_station.py")).read(), _hs)
STATIONS["hunter_station"].update(overrides=_hs["OVERRIDES"], extra=_hs["extra"])
