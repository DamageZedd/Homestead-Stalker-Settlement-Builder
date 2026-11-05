# HomesteadHF model pipeline

Blender + Python scripts that build the HomesteadHF furniture `.ogf` models on
plain-Anomaly game textures (no per-model atlases).

## Status of the scripts

These are the scripts the models were produced with. Their input locations
are environment variables; each defaults to the original author's scratch
workspace, so set them to run the scripts on another machine:

| Variable | Holds |
| --- | --- |
| `HSHF_WS` | workspace with the pipeline copies and pre-atlas backup `.blend` files |
| `HSHF_VTEX` | extracted vanilla `textures` tree |
| `HSHF_VANILLA_INDEX` | index of vanilla texture paths |
| `HSHF_VANILLA_MESHES`, `HSHF_VANILLA_TEX` | extracted vanilla meshes and textures used for accent parts |
| `HSHF_SCRATCH`, `HSHF_TMP` | scratch folders for intermediate files |

The shipped models themselves are the `.ogf` files under
`HomesteadHF/gamedata/meshes/dynamics/`. The scripts were only import-checked
in Blender after this change, not re-run end to end.

After a Blender re-export of a foundation or floor, run `python tools/model_pipeline/build_floor_collision.py`
from the repo root: it writes `[collide] ignore_ragdoll` back into those models and rebuilds the invisible
`hs_collider_*.ogf` models that `homestead_lock.script` spawns under them.

## README hero images

`render_hero.py` renders the `docs/images/hero_*.jpg` pictures from the shipped models, with their
real textures, in a headless Blender that has the XRay addon enabled:

```
blender -b -P tools/model_pipeline/render_hero.py -- jobs.json
```

`jobs.json` is a list of `{"model": "hunter_station", "out": "hero_hunter_station.png"}` (optionally
`"patch": "homestead_hf\\flag_patch_dolg"` to show another banner patch on the settlement flag, and
`"size"`). The renders are 1600x900 on the same flat background; convert them to JPG afterwards.

## Checking textures

```
python tools/model_pipeline/verify_textures.py <vanilla_textures_dir>
```

Lists every texture path used by every shipped `.ogf` and reports those that
are not in the extracted vanilla `textures` tree.

Expected exceptions (last run: 158 paths, 9 reported):

| Path | Why it is fine |
| --- | --- |
| `act/act_stalker_soldier_1`, `act_stalker_soldier_4`, `act_stalker_head_antigas_2` | Vanilla stalker textures from `textures_actors.db*`, which the extractor cannot unpack. Used by the quartermaster locker's stalker meshes. |
| `ui/ui_con_checker_interface` | Vanilla UI texture (in the UI db), used by the salvage table. |
| `homestead_hf/hunter_pelts` | Deliberate custom 2048x2048 pelt sheet (2.7 MB) kept at the author's request. |
| `homestead_hf/flag_patch_*` | The 13 faction patches the single settlement flag swaps between at run time (`build_flag_patches.py`). Only the loner one is baked into the model; the rest are applied by `homestead_settlement_flag.script`. |
| `dynamics/homestead_hf/farm_potato` | Existing custom potato texture. |
| `new_axe/axe_new_base` | Texture of the separate `wpn_axe.ogf` weapon model, not a furniture piece. |
| `wood/wood_plank6_bar_b` | Not in plain Anomaly; used by the building kit (`hs_*.ogf`) for Hideout Furniture-compatible wall planks. Requires that texture to be present in the install. |

## Not covered

The check is static. It does not verify how the models look or behave in game.
