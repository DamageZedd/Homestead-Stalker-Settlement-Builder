# AUDIT: core (save/load, settler lifecycle, callbacks, module scope)

Static read of the code on main (30f31f1), by grep and line ranges. Nothing here was run in game; every
"in-game test" line is a suggested step, not something that was done. Line numbers are in
`00_Core/gamedata/scripts/` and are for 30f31f1.

Skipped as known or decided: #376-#380 and #388, #321 (task manager and actor binder guards),
`has_renown_perk` / `get_current_camp_id` dead guards, Demonized Ledge Grabbing.
`tools/check.ps1` result: 0 new findings (luac clean; module call resolution reports only the two known
guarded probes; luacheck not installed).

## Ranked findings

### F1 (Medium): an Invincible settler's record is lost if the respawn cannot run
- `stalker_camp_builder.script:5544` (`respawn_settler`), early returns at 5548 and 5551; called from the time event at 5598 and from `verify_and_heal_settlers` at 4516.
- `camp.respawning[dead_id] = nil` runs before the checks `hub_obj and sim and survivor` and before `sim:create` succeeds. If the hub is not found, `alife()` is nil, or `create` returns nil, the function returns with the only copy of the survivor record (job, tier, xp, savings, bought_tier) already dropped from `camp.respawning`; `npc_on_death_callback` removed it from `camp.survivors` at 5593.
- Scenario: Invincible settlers on; a settler dies, and the camp's hub is released or missing (or the create fails) when the 0.5 s event fires. The settler never comes back and the tip never shows.
- Fix: clear `camp.respawning[dead_id]` only after `camp.survivors[new_id] = survivor` is set (move line 5544 to just after the `new_se` check).
- Test: enable Invincible settlers, kill a settler, and remove the hub with a debug command before the event fires; confirm the record stays in `camp.respawning` and the respawn is retried at next level entry.

### F2 (Medium): `verify_and_heal_settlers` deletes settler records when the hub is not available
- `stalker_camp_builder.script:4465-4513`, with `stalker_camp_builder_expeditions.script:52-59`.
- `restore_missing_settler` returns nil when `sim:object(hub_id)` is nil or the camp is missing. The caller then adds the id to `stale` and removes `camp.survivors[npc_id]` and its lookup entry (4508-4511). Records are dropped with no log line and no way to recover.
- `server_entity_on_unregister` and `server_object_on_unregister` return early during teardown grace (5404-5409; `homestead_is_disconnecting` is set on level change and net destroy), so an `active_camps` entry whose hub was released in that window is not cleaned up either; the next `actor_on_first_update` then runs the heal against a camp with no hub.
- Scenario: a hub released during a level change by another mod; on the next level entry every settler of that camp is silently deleted.
- Fix: in `verify_and_heal_settlers`, skip the whole camp when `hub_obj` is nil (log once through `homestead_guard_log`), and only add to `stale` when the restore itself failed with a hub present.
- Test: load a save whose hub was removed with a debug command; confirm settlers stay in `camp.survivors` and a log line appears.

### F3 (Low-Medium): `set_survivor_job` leaves a string-keyed duplicate in `settler_lookup`
- `stalker_camp_builder_jobs.script:196-205`.
- It stores the same entry under `matched_id`, `id_num` and `id_str` (`tostring(npc_id)` is never nil). Every removal path clears only the numeric key: `game_object_on_net_destroy` (stalker_camp_builder.script:6382), `npc_on_death_callback` (5593, 5608), dismissal (recruit.script:1970), expeditions.script:91, verify_and_heal (4512). The string-key entry therefore keeps the old `camp` and `survivor` after the settler is dismissed, dead, or offline.
- It also breaks the "settler_lookup holds only online settlers" shape the rest of the code relies on: `sb.settler_id_of_record` (prosper.script:59) and the scan at jobs.script:1265 walk with `pairs` and can return the string key `"1234"` for a record, and `recruit.script:3430` falls back to `settler_lookup[tostring(v_id)]`, so a reused id can be read as a settler of a camp it was dismissed from.
- Fix: write only `sb.settler_lookup[id_num or matched_id] = entry` and drop the `id_str` write; the recruit.script:3430 string fallback can stay harmlessly.
- Test: assign a job to a settler, dismiss them, then check `settler_lookup["<id>"]` in the console (or have another NPC reuse the id).

### F4 (Low-Medium): `save_state` stops at the first failing field and says nothing; `load_state` then replaces the rest with empty tables
- `stalker_camp_builder.script:3607-3626` (one `pcall` around all assignments) and `3643-3711`.
- An error in `pack_table_vectors(active_camps)` or any later line skips every field after it, silently: no `homestead_guard_log`. The next load finds the keys missing and sets `active_camps`, `rival_camps`, `refugee_ids`, etc. to `{}`, so a single bad value drops later state, and the following save writes the empty state over it.
- Fix: one `pcall` per field with `homestead_guard_log("guard", "save_state:<field>", err)`; do not write a field that failed, and in `load_state` keep the existing value when the key is absent but `m_data.stalker_camp_builder_version` is present.
- Test: temporarily put a non-vector userdata in a camp table, save, check the log names the field and the other fields still saved.

### F5 (Low): `load_state` indexes records before `normalize_camps` has checked them
- `stalker_camp_builder.script:3671-3682` run before `normalize_camps()` at 3753; `load_state` is registered bare (6198), not wrapped in `pcall`.
- The cleanup loop does `camp._cached_storage_metrics_tg = nil` and `surv.job_start_realtime = nil` for every entry. A camp or survivor that is not a table (corrupt or hand-edited save, or another mod writing the key) raises there, although `normalize_camps` (3720-3745) already handles exactly that case. The error comes out of the engine's load callback.
- Fix: move the cleanup loop after `normalize_camps()`, or guard with `type(camp) == "table"` / `type(surv) == "table"`; wrap the registered handler in `guarded_call`.
- Test: edit a save so one survivor is a number; confirm the load completes and the entry is dropped.

### F6 (Info): the disconnect-grace callback is registered three times
- `stalker_camp_builder.script:6226-6235` (`actor_on_net_destroy`), `:6404-6409` (a second registration), and `z_stalker_camp_builder_pda_monkeypatch.script:451-459` (`actor_on_net_destroy` and `on_level_changing`). All set the same flags and the same 600000 ms deadline, and `actor_on_first_update` (4707-4716) clears them. Harmless; keep one registration to make the behaviour easier to follow.

## Checked, no finding
- Save content: `active_camps` (with all prosper fields: savings, bought_tier, standing_tier, standing_queue, tier, pending_community), `rival_camps`, refugees, convoys, expeditions, radio logs, timers are plain tables/numbers and go through `pack_table_vectors`/`keys_to_numbers`; missing prosper fields default with `or 0` / `or {}` where read. The only version gate is `save_version < 2` (3746-3750); older saves get their camp fields filled by `normalize_camps`.
- Direct field access on the result of `alife_object()`/`level.object_by_id()`: the grep for a call followed by `.` or `:` found one hit (jobs.script:258) and it is guarded by `and`. All `alife():create` / `sim:create` call sites check the result before use.
- Id collisions in re-creation: `restore_missing_settler` (expeditions.script:70-84) holds and releases objects that take another missing settler's id; `verify_and_heal_settlers` iterates over a snapshot.
- Callbacks: custom callbacks are added with `AddScriptCallback` at load (prosper.script:46-48); engine callbacks go through `safe_register_callback` in `on_game_start`; the PDA's `actor_on_update` is registered once behind a `_G` flag (ui_stalker_camp_builder_pda.script:86-90). Nothing is unregistered anywhere, which matches the lifetime of the mod's handlers.
- Module scope: `tools/check.ps1` reports no `sb`/`stalker_camp_builder` alias problem on main; spot-checked `sb.` uses in jobs.script `update_camp_jobs` and recruit.script `summon_caravan`, which declare `local sb` in scope.
