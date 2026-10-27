# Handoff: settlement storage, work stations and models

Written for Gemini (or any agent) picking up where Claude stopped. Read this whole file first.

## Ground rules from the owner

- **The owner approves every Blender model before export.** Build it, render a 4-view approval sheet, show it, wait for "Approved". Never bake, export or wire a model that has not been approved.
- **AAA quality.** Plank-by-plank / part-by-part, bevels, hardware, wear. A box with a texture is rejected. Pull in vanilla Anomaly `.ogf` meshes as accents (kettle, helmets, medkits, weapons...).
- **One texture atlas per model**: `HomesteadHF/gamedata/textures/homestead_hf/atlas_<name>.dds`, 4096, DXT1, 13 mips. Baked in Cycles from the source materials (PAT / vanilla / GAMMA textures), so the model has one material.
- Models should look different from Hideout Furniture but use Anomaly/GAMMA/PAT textures.
- Test in the GAMMA install before anything else ships: `C:\GAMMA\mods\Homestead (Stalker Settlement Builder)\gamedata` is a flattened copy of `00_Core`, `HomesteadHF`, `01_Theme_ModernVanilla`, `02_GAMMA`, `04_HideoutGadgetsGammaPatch` (skip `.object` files).
- English XML must stay ASCII; Russian is cp1251. Line endings LF in the repo.
- Shell scripts mangle backslashes in heredocs: write files with an editor tool, or use `chr(92)`.

## What is done (all on main)

Storage rules (`00_Core/gamedata/scripts/stalker_camp_builder*.script`):
- Only *settlement storage* counts as camp storage: workshop stash, fridges, anything with a `homestead_storage` key, plus station stashes. Hideout Furniture boxes are personal.
- Each work station owns a hidden 300 kg `station_stash` (`HomesteadHF/.../homestead_station_storage.script`), opened by using the station. `homestead_storage_buckets` on a section says what the sorter sends it.
- Five settlement boxes (`items_homestead_storage.ltx`): Armory Crate (weapons, ammo, grenades), Quartermaster Locker (armour), Pantry (food after the fridge), Supply Crate (parts/everything else, may be main chest), Med Crate (medicine).
- Four new job stations (`items_homestead_stations.ltx`): Field Kitchen (counts as a stove, so the cook makes full meals), Field Infirmary (medstation), Guard Post (`guard_post`), Salvage Table (`salvage_table`).
- Settlement Flag hub (`homestead_settlement_flag.script`, `items_homestead_flag.ltx`): swaps to the player's faction emblem; one per camp.
- Own models (own ogf, atlas, icon, collision): Armory Crate, Quartermaster Locker, Pantry, Supply Crate, Med Crate, Field Kitchen.

## What is left

1. **Models still on stand-in visuals** (build, show for approval, then bake/export/wire):
   - **Field Infirmary** (`homestead_field_infirmary` / `placeable_field_infirmary`; stand-in `clinic_equipments`; Medic station). Idea: steel field medical bed or couch with IV stand, instrument tray, lamp, vanilla medkits.
   - **Guard Post** (`placeable_guard_post`; stand-in `metal_table1`). Idea: sandbag/plank watch post with rifle rack, ammo box, lamp.
   - **Salvage Table** (`placeable_salvage_table`; stand-in `prop_table_2`). Idea: heavy workbench with vice, scrap bins, tools, parts.
   - **Settlement Flag** (`items_homestead_flag.ltx`; 12 factions, stand-in `prop_poster_vertical`). One pole/flag model with 12 faction emblems (one atlas can hold all 12 as separate UV cells, or one atlas per faction if the engine needs it; ask the owner).
2. **Gameplay items from the original Discord report (not started):**
   - Settlers should equip weapons and armour from the Armory / Quartermaster boxes (settlement crates).
   - The cook should prepare tier 3 food.
   - The fridge should freeze food that NPCs deposit.
   - The craftsman should get recipes for grenades and underbarrel (VOG) grenades.
3. In-game testing is still owed on everything above. The owner reported being happy with the storage deploy; the six models and the flag have not been confirmed in game yet.

## Per-model pipeline (what Claude did for each)

Scripts are in `tools/model_pipeline/` and run **inside Blender** through the Blender MCP (`execute_blender_code`). They contain hard-coded absolute paths (`SCR`, `S`, `WT`) from the original machine and session: change them to your checkout and a scratch folder first.

1. `build_<name>.py`: `exec` `build_lib.py`, call `start({material: (texture path, shader)}, seed)`, then build parts with `metal_box`, `plank`, `tube`, `rivet`, `decal`, `accent(vanilla_ogf_rel, matrix)` and finish with `join_parts()`. Vanilla meshes are unpacked with `C:\anomaly\tools\converter.exe -unpack` into a folder that `accent_lib.py` searches (`TEX_DIRS`); textures come from PAT (`C:\GAMMA\mods\PAT\gamedata\textures`), the vanilla unpack, and `C:\anomaly\tools\_test_unpack`.
2. Render four views (`preview_stage.py`: `stage()`, `render_views()`), assemble an approval sheet, show it to the owner. Iterate until approved.
3. Bake: `bake_atlas("<name>_visual", "atlas_<name>", 4096, ())` (Cycles diffuse colour; it returns `(object, png_path)`, so take the path from the tuple), then `make_export(bake_obj_name, name, png_path)`.
4. Rig and export: `rig(mesh, name, boxes, mass)` makes the `link` root bone plus `shape_N` boxes (collision; bone shape boxes, gamemtl `objects\large_furniture`), then `export(arm, folder, name)` writes `.object` and `.ogf` into `HomesteadHF/gamedata/meshes/dynamics/HomesteadHF/`. Check the ogf references `homestead_hf\atlas_<name>` with shader `models\model`.
5. DDS: `python -I tools/model_pipeline/make_dds.py atlas.png out.dds` (DXT1 with full mips; needs Pillow).
6. Icon: `icon_lib.render_icon(obj, png, px, view)`, then paste (resized to 50 px per grid cell) into `textures/ui/ui_icon_homestead_workstations.dds` (512x1024, uncompressed A8R8G8B8, no mips) at a free cell. Cells used so far include (4,9 3x2), (7,9 2x4), (4,11 3x4), (7,13 3x2), (0,15 3x2), (3,15 3x3). Check the alpha of the target region is empty before pasting.
7. Wire the config: `visual`, `icons_texture = ui\ui_icon_homestead_workstations`, `inv_grid_x/y/width/height`, remove stand-in `fixed_bones`, set `base_rotation`, and `bounding_box_size` (width x, depth, height) / `bounding_box_origin` (x, y up, z) from the mesh bounds: 3 cm inset per side, 10 cm lift. For a physic_object station keep `script_binding`, `ui_on_simple_interaction`, `homestead_storage_buckets`, `item_section` and the section names (job code matches names such as "stove").
8. Update `CHANGELOG.md` and the description strings (eng ASCII, rus cp1251), commit, deploy to the GAMMA install (copy changed files, verify with `cmp`).

Known Blender traps: the X-Ray addon resets a new material's `eshader` to `default` on first sight (`export()` re-sets it); each part's UV layer must be renamed to `Texture` (`join_parts()` does it); do not name a variable `S` if the script also uses `S` as a path; reset the scene with `read_homefile(use_empty=True)` in its own call before importing meshes.

## Where things are

- Plan and decisions: this file, `CHANGELOG.md` (top section), the commit log.
- The Blender source files (`.blend`) were not committed (large); rebuild from `tools/model_pipeline/build_*.py`.
- Nothing from this work has been released; do not make a release zip without the owner (release zip must exclude `.object` files and Hideout Gadgets duplicates, never a raw `git archive`).
