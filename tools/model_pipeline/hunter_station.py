# Hunter Station on plain-Anomaly textures (run inside Blender; used by export_station.py).
# Everything is vanilla except the pelts/hides, which keep their custom art in textures\homestead_hf\hunter_pelts.dds
# (see hunter_pelts.py and pack_pelts.py; the carve data lives in hunter_pelts_data\).
import os
WS = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\ws"
REPO = r"C:\Users\hocke\OneDrive\Documents\GitHub\Homestead-Stalker-Settlement-Builder\.claude\worktrees\laughing-turing-46d9eb"
MD = os.path.join(WS, "models")
DATA = os.path.join(MD, "hunter_pelts_data")
PELT_DDS = os.path.join(REPO, "HomesteadHF", "gamedata", "textures", "homestead_hf", "hunter_pelts.dds")   # viewport preview only
_hp = {}
exec(open(os.path.join(MD, "hunter_pelts.py")).read(), _hp)
BARK = "lfo\\lfo_trees\\bark\\trees_atp_pine_bark"
OVERRIDES = {"mat_hunter_pine_bark": BARK, "mat_hunter_pine_bark.001": BARK}
OVERRIDES.update(_hp["OVERRIDES"])


def extra(ob):
    miss = _hp["apply_pelts"](ob, os.path.join(DATA, "tris.json"), os.path.join(DATA, "map.json"), PELT_DDS)
    assert miss == 0, miss
    return ob
