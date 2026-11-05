# Pre-release checklist

Run before every release, after `tools/RELEASE_CHECKLIST.md` step 1 (README) is done. Nothing here
runs the game; it is static checking plus packaging checks.

1. **Repo checks**: `powershell -File tools/check.ps1` must print `0 new`.
2. **Lua syntax**: `luac -p` on every tracked script (Lua 5.1, e.g. `C:\Program Files (x86)\Lua\5.1\luac.exe`):
   `for f in $(git ls-files '*.script'); do luac -p "$f" || echo FAIL $f; done`
3. **Lua tests** (from the repo root, Lua 5.1): `lua tools/tests/test_needs.lua`,
   `lua tools/tests/test_raiders.lua`, `lua tools/tests/test_time_factor.lua`; each must end with a pass line.
4. **anomaly-modding validator** (workbench outside the repo):
   - `export STALKER_WORKBENCH=C:/Users/<you>/Documents/Homestead_Release/qa_workbench`
   - `python ~/.claude/skills/anomaly-modding/scripts/init_project.py --name homestead` (once)
   - copy the shipped gamedata of `HEAD` into `projects/homestead/gamedata`: overlay `00_Core`, `HomesteadHF`,
     `01_Theme_ModernVanilla`, `02_GAMMA` (their `gamedata/` folders, no `.object` files), clearing the folder first
   - `python ~/.claude/skills/anomaly-modding/scripts/validate_project.py --project homestead` must say `project: valid`
   - `python ~/.claude/skills/anomaly-modding/scripts/quality_scan.py scan projects/homestead`: triage only NEW
     findings. Known false positives / baseline: LUA_UNSAFE_DB_ACTOR, LUA_UNSAFE_LEVEL, LUA_UNSAFE_ALIFE,
     MONKEY_PATCH, LUA_HIDDEN_GLOBAL, LOCALIZATION_LEGACY_ENCODING (the scan reads ASCII as cp1251),
     LOCALIZATION_MISSING_ID for ids built from a prefix (check the suffixes exist in eng and rus),
     SAVE_MISSING_VERSION in modules that keep no save state of their own, the guarded `ui_mcm` uses and the
     feature-detecting `on_game_start` in `homestead_hologram.script`.
5. **English text stays ASCII**: no byte above 127 in `configs/text/eng/*.xml`.
6. **Zip layout** (see the packaging notes; never a raw `git archive`): top-level folders `00_Core`,
   `01_Theme_*`, `02_GAMMA`, `04_HideoutGadgetsGammaPatch`, `05_HDIcons_Patch`, `HomesteadHF`, `fomod`, plus `CHANGELOG.md` and
   `README.md`. Leave out every `.object` file and every 04 file that is byte-identical in GAMMA's
   `470- Gadgets for Hideout Furniture`. Compare the file list with the previous zip (only intended additions),
   check the size is near the previous release, `hunter_station.ogf` is about 2.0 MB, no `.object`, and
   `fomod/info.xml` carries the new version.
7. **Byte-compare with the install** `C:\GAMMA\mods\Homestead (Stalker Settlement Builder)\gamedata`: the
   install is flattened with the `01_Theme_ModernVanilla` theme, so compare the `00_Core`, `HomesteadHF`,
   `02_GAMMA` and `01_Theme_ModernVanilla` files only (the other themes always differ). Differences must be
   line endings only; for a real difference decide which side is newer and never overwrite the install blindly.
8. **Docs match the zip**: CHANGELOG section for the new version, README "New in" and feature sections,
   `python tools/make_moddb_description.py`, release notes and Discord text in `Homestead_Release`.
