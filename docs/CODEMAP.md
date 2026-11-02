# CODEMAP: Homestead (Stalker Settlement Builder)

Index of Lua `.script` files: every `function` with start and end line, its leading comment (purpose), engine callbacks/timers/binder hooks registered inside it, and MCM/ini keys read inside it.

- **Line ranges**: `start`-`end`, where `end` is the line before the next `function` in the same file (approximate for nested defs).
- **Purpose**: the `-- name -- purpose` or `-- purpose` comment directly above the function. `(no comment)` means read the source.
- **Hooks**: `RegisterScriptCallback`, `AddScriptCallback`, `CreateTimeEvent`/`RemoveTimeEvent`, binder registration, with the line they appear on.
- **Coverage**: 1087 function rows; 775 have no leading comment and show `(no comment)`. Those purposes need a follow-up pass that reads the body. Hook and cfg columns are regex-based, so they can miss indirect or dynamically built keys.
- **Cfg**: keys read via `ui_mcm.get`, `mcm_get`, `ini_sys:r_*_ex` and `r_*` helpers.


## Core / state

### `00_Core/gamedata/scripts/stalker_camp_builder.script` (6832 lines, 299 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `_obj_id` | 18-18 | (no comment) | - | - |
| `_obj_section` | 19-19 | (no comment) | - | - |
| `_se_sec_name` | 20-20 | (no comment) | - | - |
| `_client_pos` | 21-21 | (no comment) | - | - |
| `_se_pos` | 22-24 | (no comment) | - | - |
| `patch_alife_storage_manager` | 25-76 | Monolith / Anomaly Engine Crash Guard: alife_storage_manager | - | - |
| `safe_register_callback` | 77-89 | (no comment) | - | - |
| `patch_item_artefact_binder_save` | 90-121 | Prevents fatal crash in zz_item_artefact.script line 255: attempt to index field 'object' (a userdata value) | - | - |
| `patch_watchdog_lag_protection` | 122-122 | during heavy asset loading / synchronous decompression (e.g. 3.8MB OGFs, textures) | - | - |
| `grant_watchdog_immunity` | 123-141 | (no comment) | - | - |
| `hook_debug_spawner` | 142-189 | Hook Debug Spawner directly | - | - |
| `patch_detec_bone_hide_guard` | 190-192 | generate unnecessary garbage. | - | - |
| `patch_ledge_grabbing_guard` | 193-198 | (no comment) | - | - |
| `homestead_guard_log` | 199-207 | (no comment) | - | - |
| `guarded_call` | 208-216 | pcall that reports a failure through homestead_guard_log (once per 30s per tag) instead of dropping it | - | - |
| `patch_task_manager_guard` | 217-231 | instead of replacing CRandomTask.update or allocating closures per task on every frame. | - | - |
| `patch_actor_binder_guard` | 232-234 | (no comment) | - | - |
| `patch_meat_spoiling_fridges` | 235-274 | (no comment) | - | - |
| `is_level_vertex` | 275-282 | `level` has no valid_vertex_id (that is a game graph method); u32(-1) means no vertex | - | - |
| `game_sec` | 283-341 | (no comment) | - | - |
| `safe_squad_members` | 342-349 | (no comment) | - | - |
| `pack_vector` | 350-362 | Vector pack/unpack -- prevents save corruption. | - | - |
| `unpack_vector` | 363-372 | (no comment) | - | - |
| `pack_table_vectors` | 373-401 | (no comment) | - | - |
| `unpack_table_vectors` | 402-421 | (no comment) | - | - |
| `safe_alife_object` | 422-428 | (no comment) | - | - |
| `safe_level_object` | 429-435 | (no comment) | - | - |
| `safe_position` | 436-448 | (no comment) | - | - |
| `safe_distance` | 449-457 | (no comment) | - | - |
| `safe_distance_sqr` | 458-466 | (no comment) | - | - |
| `safe_alife_release` | 467-472 | (no comment) | - | - |
| `safe_deferred_release` | 473-492 | (no comment) | CreateTimeEvent("homestead_release") L475 | - |
| `outpost_piece_ids` | 493-513 | (no comment) | - | - |
| `is_settlement_storage` | 514-524 | Furniture or level box is the player's own: no job, sorter or supply count touches it. | - | homestead_storage |
| `is_valid_camp_box` | 525-631 | furniture box (not shipped with Homestead) inside the camp? | - | - |
| `get_camp_containers` | 632-632 | so the rest of this file can keep using the short names. | - | - |
| `consume_one_use` | 633-633 | (no comment) | - | - |
| `camp_iterate_inventory` | 634-634 | (no comment) | - | - |
| `invalidate_camp_inventory_cache` | 635-635 | (no comment) | - | - |
| `get_camp_inventory_snapshot` | 636-636 | (no comment) | - | - |
| `camp_find_item` | 637-637 | (no comment) | - | - |
| `camp_consume_item` | 638-638 | (no comment) | - | - |
| `camp_count_item` | 639-660 | (no comment) | - | - |
| `camp_send_tip` | 661-670 | holds back a routine report's toast; an alert (always) shows either way. | - | - |
| `play_job_complete_sound` | 671-673 | (no comment) | - | - |
| `get_time_of_day_mult` | 674-921 | (no comment) | - | - |
| `ensure_mcm_paths` | 922-940 | (no comment) | - | - |
| `on_mcm_load` | 941-949 | (no comment) | - | - |
| `stalker_camp_builder.invalidate_mcm_cache` | 950-954 | (no comment) | - | - |
| `get_mcm_setting` | 955-1094 | (no comment) | - | - |
| `get_active_camp_near` | 1095-1133 | (no comment) | - | - |
| `stalker_camp_builder.get_nearby_smart_terrain_hazard` | 1134-1188 | (no comment) | - | - |
| `stalker_camp_builder.is_smart_respawn_blocked_in_camp` | 1189-1234 | (no comment) | - | - |
| `get_camp_bed_capacity` | 1235-1370 | (no comment) | - | - |
| `resolve_structure_type` | 1371-1397 | (no comment) | - | - |
| `is_station_stash` | 1398-1402 | a work station's hidden stash is that station's storage, never the main chest | - | - |
| `stalker_camp_builder.sanitize_primary_chest` | 1403-1410 | (no comment) | - | - |
| `find_best_container` | 1411-1524 | (no comment) | - | - |
| `get_camp_label` | 1525-1546 | (no comment) | - | - |
| `get_recruitable_camps` | 1547-1581 | (no comment) | - | - |
| `get_camp_info` | 1582-1614 | (no comment) | - | - |
| `anchor_settler_to_smart` | 1615-1619 | (no comment) | - | - |
| `stalker_camp_builder.get_furniture_front_vertex_and_pos` | 1620-1679 | returns valid level vertex and pos offset | - | - |
| `teleport_npc_to_camp_hub` | 1680-1683 | (no comment) | - | - |
| `is_companion` | 1684-1690 | (no comment) | - | - |
| `get_recruitment_roll` | 1691-1694 | (no comment) | - | - |
| `no_camps_exist` | 1695-1698 | (no comment) | - | - |
| `camps_are_full` | 1699-1702 | (no comment) | - | - |
| `recruitment_roll_success` | 1703-1706 | (no comment) | - | - |
| `recruitment_roll_fail` | 1707-1710 | (no comment) | - | - |
| `can_recruit` | 1711-1714 | (no comment) | - | - |
| `release_npc_from_squad_and_smart` | 1715-1718 | (no comment) | - | - |
| `set_camp_settler_relations` | 1719-1723 | (no comment) | - | - |
| `get_settler_job_target` | 1724-1727 | Cross-Level Settler Teleport | - | - |
| `teleport_settler_to_camp_level` | 1728-1731 | (no comment) | - | - |
| `recall_all_settlers` | 1732-1735 | (no comment) | - | - |
| `recruit_npc_to_camp` | 1736-1739 | (no comment) | - | - |
| `recruit_npc` | 1740-1743 | (no comment) | - | - |
| `transfer_survivor_to_camp` | 1744-1747 | (no comment) | - | - |
| `camp_slot_1_exists` | 1748-1750 | (no comment) | - | - |
| `camp_slot_2_exists` | 1751-1753 | (no comment) | - | - |
| `camp_slot_3_exists` | 1754-1756 | (no comment) | - | - |
| `camp_slot_4_exists` | 1757-1760 | (no comment) | - | - |
| `recruit_to_camp_slot_1` | 1761-1763 | (no comment) | - | - |
| `recruit_to_camp_slot_2` | 1764-1766 | (no comment) | - | - |
| `recruit_to_camp_slot_3` | 1767-1769 | (no comment) | - | - |
| `recruit_to_camp_slot_4` | 1770-1773 | (no comment) | - | - |
| `is_camp_survivor` | 1774-1777 | (no comment) | - | - |
| `set_survivor_job` | 1778-1781 | (no comment) | - | - |
| `set_survivor_position` | 1782-1785 | (no comment) | - | - |
| `clear_survivor_position` | 1786-1789 | (no comment) | - | - |
| `set_survivor_position_to_actor` | 1790-1793 | (no comment) | - | - |
| `can_recruit_back` | 1794-1797 | (no comment) | - | - |
| `recruit_back` | 1798-1801 | (no comment) | - | - |
| `can_return_to_settlement` | 1802-1805 | (no comment) | - | - |
| `get_return_to_settlement_text` | 1806-1809 | (no comment) | - | - |
| `return_to_settlement` | 1810-1813 | (no comment) | - | - |
| `get_settler_display_name` | 1814-1817 | (no comment) | - | - |
| `dismiss_survivor` | 1818-1821 | (no comment) | - | - |
| `is_camp_settler` | 1822-1825 | (no comment) | - | - |
| `spawn_scavenged_loot` | 1826-1829 | (no comment) | - | - |
| `spawn_hunted_meat` | 1830-1833 | (no comment) | - | - |
| `process_ammo_crafting` | 1834-1837 | (no comment) | - | - |
| `process_gear_repair` | 1838-1854 | (no comment) | - | - |
| `process_cook_job` | 1855-1858 | (no comment) | - | - |
| `process_medic_job` | 1859-1862 | (no comment) | - | - |
| `process_turret_maintenance` | 1863-1866 | (no comment) | - | - |
| `update_camp_jobs` | 1867-1870 | (no comment) | - | - |
| `restrain_rival_squads` | 1871-1874 | (no comment) | - | - |
| `create_squad_at_pos` | 1875-1878 | (no comment) | - | - |
| `release_camp_decorations` | 1879-1882 | (no comment) | - | - |
| `find_nearby_squad_for_repopulation` | 1883-1886 | (no comment) | - | - |
| `get_smart_terrains_on_level` | 1887-1890 | (no comment) | - | - |
| `get_all_levels_with_smarts` | 1891-1894 | (no comment) | - | - |
| `get_enemy_faction_for` | 1895-1898 | (no comment) | - | - |
| `find_wiping_squad` | 1899-1902 | (no comment) | - | - |
| `squad_has_story_npc` | 1903-1907 | (no comment) | - | - |
| `update_rival_camps` | 1908-1911 | update_rival_camps() -- Master rival-camp lifecycle manager. | - | - |
| `update_active_convoys` | 1912-1915 | (no comment) | - | - |
| `cleanup_camp_convoys` | 1916-1919 | (no comment) | - | - |
| `enforce_rival_camp_survivor_cap` | 1920-1940 | (no comment) | - | - |
| `run_expedition_tick` | 1941-1947 | actor_on_update helpers | - | - |
| `run_weapon_watchdog` | 1948-1972 | (no comment) | - | - |
| `process_debug_respawn` | 1973-1983 | (no comment) | - | stalker_camp_builder/qol_debug/respawn_rival_camps |
| `process_uninstall_prep` | 1984-2029 | (no comment) | - | stalker_camp_builder/qol_debug/uninstall_purge_rival_furniture |
| `stalker_camp_builder.purge_all_rival_furniture` | 2030-2033 | (no comment) | - | - |
| `process_boundary_rescan` | 2034-2054 | (no comment) | - | - |
| `process_proximity_structure_rescan` | 2055-2068 | (no comment) | - | - |
| `forget_looted_outpost_chest` | 2069-2075 | task's item put there would go with the outpost's decay. | - | - |
| `populate_gamma_rival_chests` | 2076-2118 | (no comment) | - | - |
| `run_periodic_actor_tasks` | 2119-2128 | (no comment) | - | - |
| `process_surge_reaction` | 2129-2141 | (no comment) | - | - |
| `process_hospitality_buff` | 2142-2183 | (no comment) | - | - |
| `process_all_settler_eating` | 2184-2192 | (no comment) | - | - |
| `actor_on_update` | 2193-2258 | per-tick orchestrator | - | - |
| `stalker_camp_builder.in_player_range` | 2259-2266 | distance (stalker_camp_builder_rivals' is_player_near) | - | - |
| `process_refugee_despawns` | 2267-2305 | (no comment) | - | - |
| `camp_npc_move_to` | 2306-2309 | (no comment) | - | - |
| `camp_npc_arrive` | 2310-2337 | (no comment) | - | - |
| `run_rival_npc_patrol` | 2338-2553 | (no comment) | - | - |
| `refresh_settler_goodwill` | 2554-2571 | (no comment) | - | - |
| `handle_refugee_ai` | 2572-2590 | (no comment) | - | - |
| `enforce_settler_leash` | 2591-2618 | (no comment) | - | - |
| `npc_on_update` | 2619-2789 | settler per-tick AI orchestrator | - | - |
| `find_struct_lvid` | 2790-2893 | Nested helpers used by the job-dispatch block below. | - | - |
| `get_job_target_lvid` | 2894-2934 | (no comment) | - | - |
| `move_to_job_furniture` | 2935-3248 | (no comment) | - | - |
| `hf_on_furniture_place` | 3249-3429 | (no comment) | CreateTimeEvent("homestead_smart_warn_" .. tostring(obj_id) L3382 | homestead_hub, item_section |
| `stalker_camp_builder.release_camp_trader` | 3430-3439 | that still exist | - | - |
| `hf_on_before_furniture_release` | 3440-3497 | (no comment) | - | - |
| `init_hf_pickup_hook` | 3498-3523 | (no comment) | - | - |
| `server_object_on_unregister` | 3524-3563 | init_hf_pickup_hook skip hf_on_before_furniture_release: drop such a piece here. | - | - |
| `get_time_sec` | 3564-3575 | (no comment) | - | - |
| `can_banish` | 3576-3580 | (no comment) | - | - |
| `banish_npc` | 3581-3586 | (no comment) | - | - |
| `get_job_progress` | 3587-3590 | (no comment) | - | - |
| `get_job_time_remaining` | 3591-3594 | (no comment) | - | - |
| `get_job_paused_status` | 3595-3598 | (no comment) | - | - |
| `camp_has_item` | 3599-3602 | (no comment) | - | - |
| `camp_has_repairable_gear` | 3603-3606 | (no comment) | - | - |
| `save_state` | 3607-3627 | (no comment) | - | - |
| `keys_to_numbers` | 3628-3642 | (no comment) | - | - |
| `load_state` | 3643-3803 | (no comment) | - | - |
| `normalize_camps` | 3804-3870 | State Normalization / Migration | - | - |
| `stalker_camp_builder.get_surface_y` | 3871-3920 | (no comment) | - | - |
| `stalker_camp_builder.get_ground_vertex_and_pos` | 3921-4005 | (no comment) | - | - |
| `snap_rival_camps_to_ground` | 4006-4009 | (no comment) | - | - |
| `force_respawn_all_rival_camps` | 4010-4045 | (no comment) | - | - |
| `has_paw_pins` | 4046-4056 | (no comment) | - | - |
| `get_settlement_map_spot_type` | 4057-4074 | (no comment) | - | - |
| `refresh_settlement_map_spot` | 4075-4090 | when it is missing; otherwise only its text changes. | - | - |
| `get_outpost_map_spot_type` | 4091-4146 | (no comment) | - | - |
| `remove_all_rival_map_spots` | 4147-4156 | (no comment) | - | - |
| `remove_all_camp_map_spots` | 4157-4166 | (no comment) | - | - |
| `sync_rival_camp_map_spot` | 4167-4203 | (no comment) | - | - |
| `sync_all_camp_map_spots` | 4204-4266 | (no comment) | - | - |
| `show_camp_summary_toast` | 4267-4289 | actor_on_first_update helpers | CreateTimeEvent("homestead_camp_summary") L4281 | - |
| `get_job_realtime_interval` | 4290-4306 | (no comment) | - | - |
| `rebase_one_survivor_job` | 4307-4325 | (no comment) | - | - |
| `rebase_all_survivor_jobs` | 4326-4335 | (no comment) | - | - |
| `clean_orphaned_camps` | 4336-4354 | (no comment) | - | - |
| `migrate_ctime_fields` | 4355-4355 | (no comment) | - | - |
| `convert_if_needed` | 4356-4388 | (no comment) | - | - |
| `check_hf_requirements` | 4389-4401 | (no comment) | - | - |
| `validate_loaded_structures` | 4402-4413 | (no comment) | - | - |
| `populate_gamma_rival_chests_on_load` | 4414-4442 | (no comment) | - | - |
| `run_settler_self_heals` | 4443-4457 | (no comment) | - | - |
| `stalker_camp_builder.survivor_se` | 4458-4464 | and its id may be free or taken by another object; the engine's switch and squad calls crash on those. | - | - |
| `verify_and_heal_settlers` | 4465-4521 | (no comment) | - | - |
| `survivor_is_companion` | 4522-4529 | (no comment) | - | - |
| `restore_dismissed_companion_jobs` | 4530-4542 | (no comment) | - | - |
| `teleport_camp_settlers_home` | 4543-4562 | (no comment) | - | - |
| `separation_sweep` | 4563-4589 | (no comment) | - | - |
| `cross_level_recall_and_health_check` | 4590-4608 | (no comment) | - | - |
| `stalker_camp_builder.sanitize_orphan_container_children` | 4609-4707 | ============================================================================ | - | - |
| `actor_on_first_update` | 4708-4784 | level-entry orchestrator | CreateTimeEvent("homestead_level_entry") L4753, CreateTimeEvent("homestead_level_entry") L4760 | - |
| `set_scavenge_job` | 4785-4788 | (no comment) | - | - |
| `set_hunter_job` | 4789-4792 | (no comment) | - | - |
| `set_craft_job` | 4793-4796 | (no comment) | - | - |
| `set_repair_job` | 4797-4800 | (no comment) | - | - |
| `set_idle_job` | 4801-4804 | (no comment) | - | - |
| `set_guard_job` | 4805-4808 | (no comment) | - | - |
| `set_cook_job` | 4809-4812 | (no comment) | - | - |
| `set_medic_job` | 4813-4816 | (no comment) | - | - |
| `set_electrician_job` | 4817-4820 | (no comment) | - | - |
| `set_woodcutter_job` | 4821-4824 | (no comment) | - | - |
| `set_brewer_job` | 4825-4828 | (no comment) | - | - |
| `set_scrapper_job` | 4829-4832 | (no comment) | - | - |
| `set_farmer_job` | 4833-4836 | (no comment) | - | - |
| `set_trader_job` | 4837-4840 | (no comment) | - | - |
| `check_camp_chest_supplies` | 4841-4856 | (no comment) | - | - |
| `check_sec` | 4857-4886 | (no comment) | - | - |
| `get_camp_stats` | 4887-5053 | (no comment) | - | - |
| `process_camp_morale` | 5054-5122 | (no comment) | - | - |
| `get_camp_status_text` | 5123-5161 | phrase id (PhraseDialog.cpp 211-219). The status is that of the camp the player stands in. | - | - |
| `check_camp_sleep_bonus` | 5162-5193 | (no comment) | - | - |
| `award_survivor_xp` | 5194-5226 | Survivor XP / Skill System | - | - |
| `get_survivor_tier_mult` | 5227-5237 | (no comment) | - | - |
| `add_camp_log_entry` | 5238-5254 | (no comment) | - | - |
| `transfer_supplies` | 5255-5328 | Returns: number of items actually transferred. | - | - |
| `get_camp_inventory_summary` | 5329-5353 | Returns a table of {section = count, ...}. | - | - |
| `establish_trade_route` | 5354-5369 | Establish a trade route between two camps. | - | - |
| `remove_trade_route` | 5370-5382 | Remove all trade routes from a camp (or a specific one by index). | - | - |
| `process_trade_routes` | 5383-5400 | actor_on_update task table (slot 9, teardown-grace gated). | - | - |
| `server_entity_on_unregister` | 5401-5539 | (no comment) | - | - |
| `stalker_camp_builder.respawn_settler` | 5540-5572 | re-creates an Invincible settler who died (npc_on_death_callback) at the camp's hub | - | - |
| `npc_on_death_callback` | 5573-5616 | (no comment) | CreateTimeEvent("homestead_respawn_settler") L5598 | - |
| `npc_on_hit_callback` | 5617-5639 | combat defense reaction and damage recovery for settlers | - | - |
| `homestead_luabind_fatal_diag` | 5640-5649 | Writes the offender and a traceback to the log so crashes can be traced. | - | - |
| `camp_holds_squad` | 5650-5661 | True when a camp holds the squad as its garrison, a reinforcement, or a heat-mutant. | - | - |
| `stalker_camp_builder.is_held_squad` | 5662-5683 | AlifePlus ownership predicate: owned while Homestead tracks the squad in its own registries. | - | - |
| `on_game_start` | 5684-5710 | (no comment) | - | - |
| `get_weapon_repair_tier` | 5711-5733 | (no comment) | - | parent_section, repair_type, cost, ammo_class |
| `stalker_camp_builder.restore_wpo_weapon_parts` | 5734-5784 | (no comment) | - | con_parts_list |
| `calc_wpo_repair_cost` | 5785-5858 | (no comment) | - | class, parent_section, con_parts_list, cost |
| `stalker_camp_builder.is_settler` | 5859-5888 | (no comment) | - | - |
| `get_cached_level_name` | 5889-5898 | (no comment) | - | - |
| `stalker_camp_builder.is_pos_in_active_camp` | 5899-5939 | max_dist: how near a hub counts (45 m when left out, as the emission cover asks) | - | - |
| `stalker_camp_builder.invalidate_roof_cover_cache` | 5940-5947 | (no comment) | - | - |
| `find_roof_ids` | 5948-5969 | (no comment) | - | - |
| `stalker_camp_builder.note_roof_piece` | 5970-5976 | a server object registered (placed) or released: a roof or floor piece updates the list | - | - |
| `rebuild_roof_cover_cache` | 5977-6068 | (no comment) | - | - |
| `stalker_camp_builder.is_pos_under_homestead_roof` | 6069-6101 | Tile footprint is 4.70895m x 4.70895m (half-tile = 2.3545m; 2.65m includes eaves/snap tolerance). | - | - |
| `stalker_camp_builder.is_settler_at_pos` | 6102-6124 | (no comment) | - | - |
| `stalker_camp_builder.is_rival_camp_object` | 6125-6177 | (no comment) | - | - |
| `on_dotmarks_manual_interact_release` | 6178-6454 | (no comment) | - | homestead_hub |
| `stalker_camp_builder.get_camp_morale` | 6455-6495 | compute dynamic 0-100% morale based on living conditions | - | - |
| `stalker_camp_builder.apply_hospitality_buff` | 6496-6509 | slowly restores health and stamina (same rate as friendly rival camps). | - | - |
| `stalker_camp_builder.tick_hospitality_buff` | 6510-6518 | (no comment) | - | - |
| `stalker_camp_builder.check_hospitality_on_item_use` | 6519-6535 | (no comment) | - | - |
| `stalker_camp_builder.check_hospitality_on_sleep` | 6536-6547 | (no comment) | - | - |
| `get_tech_overhaul_ask_text` | 6548-6551 | (no comment) | - | - |
| `repair_equipped_weapon_and_parts` | 6552-6556 | (no comment) | - | - |
| `is_actor_healthy` | 6557-6565 | Public Dialogue and Medic Forwarders (Direct Resolution) | - | - |
| `is_actor_not_healthy` | 6566-6574 | (no comment) | - | - |
| `is_actor_injured` | 6575-6582 | (no comment) | - | - |
| `is_actor_irradiated` | 6583-6589 | (no comment) | - | - |
| `is_actor_injured_irradiated` | 6590-6598 | (no comment) | - | - |
| `medic_heal_wounds` | 6599-6602 | (no comment) | - | - |
| `medic_cure_rad` | 6603-6606 | (no comment) | - | - |
| `medic_full_treat` | 6607-6610 | (no comment) | - | - |
| `open_technician_upgrade_ui` | 6611-6614 | (no comment) | - | - |
| `start_camp_tech_trade` | 6615-6618 | (no comment) | - | - |
| `start_camp_medic_trade` | 6619-6622 | (no comment) | - | - |
| `is_camp_medic` | 6623-6626 | (no comment) | - | - |
| `is_camp_repairer` | 6627-6630 | (no comment) | - | - |
| `is_camp_trader` | 6631-6634 | (no comment) | - | - |
| `actor_has_drugkit` | 6635-6638 | (no comment) | - | - |
| `actor_has_toolkit1` | 6639-6642 | (no comment) | - | - |
| `actor_has_toolkit2` | 6643-6646 | (no comment) | - | - |
| `actor_has_toolkit3` | 6647-6650 | (no comment) | - | - |
| `give_medic_drugkit` | 6651-6654 | (no comment) | - | - |
| `give_tech_toolkit1` | 6655-6658 | (no comment) | - | - |
| `give_tech_toolkit2` | 6659-6662 | (no comment) | - | - |
| `give_tech_toolkit3` | 6663-6666 | (no comment) | - | - |
| `survivor_has_custom_position` | 6667-6670 | (no comment) | - | - |
| `dialog_set_survivor_position_to_actor` | 6671-6674 | (no comment) | - | - |
| `dialog_clear_survivor_position` | 6675-6678 | (no comment) | - | - |
| `start_camp_trader_trade` | 6679-6682 | (no comment) | - | - |
| `is_camp_woodcutter` | 6683-6686 | (no comment) | - | - |
| `is_camp_brewer` | 6687-6690 | (no comment) | - | - |
| `is_camp_scrapper` | 6691-6694 | (no comment) | - | - |
| `is_camp_farmer` | 6695-6698 | (no comment) | - | - |
| `is_camp_trader` | 6699-6702 | (no comment) | - | - |
| `actor_has_woodcutter_axe` | 6703-6706 | (no comment) | - | - |
| `give_woodcutter_axe` | 6707-6710 | (no comment) | - | - |
| `actor_has_brewer_drugkit` | 6711-6714 | (no comment) | - | - |
| `give_brewer_drugkit` | 6715-6718 | (no comment) | - | - |
| `actor_has_scrapper_tools` | 6719-6722 | (no comment) | - | - |
| `give_scrapper_tools` | 6723-6726 | (no comment) | - | - |
| `is_not_woodcutter_mode_auto` | 6727-6730 | (no comment) | - | - |
| `is_not_woodcutter_mode_timber` | 6731-6734 | (no comment) | - | - |
| `is_not_woodcutter_mode_charcoal` | 6735-6738 | (no comment) | - | - |
| `set_woodcutter_mode_auto` | 6739-6742 | (no comment) | - | - |
| `set_woodcutter_mode_timber` | 6743-6746 | (no comment) | - | - |
| `set_woodcutter_mode_charcoal` | 6747-6763 | (no comment) | - | - |
| `setup_settler_beh_logic` | 6764-6767 | (no comment) | - | - |
| `restore_settler_logic` | 6768-6772 | (no comment) | - | - |
| `get_camp_storage_metrics` | 6773-6832 | EXPEDITION SALVAGE STARS & CAMP STORAGE METRICS | - | inv_weight |

### `00_Core/gamedata/scripts/stalker_camp_builder_mcm.script` (183 lines, 2 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `prepare_group` | 11-19 | real module. The main stalker_camp_builder.script creates the table. | - | - |
| `on_mcm_load` | 20-183 | (no comment) | - | - |

### `00_Core/gamedata/scripts/modxml_stalker_camp_builder.script` (961 lines, 7 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `has_catspaw_skull` | 751-760 | (no comment) | - | - |
| `get_homestead_mapspots` | 761-801 | (no comment) | - | - |
| `build_paw_spot_xml` | 802-811 | (no comment) | - | - |
| `build_paw_mapspots` | 812-826 | (no comment) | - | - |
| `get_paw_mapspots` | 827-833 | (no comment) | - | - |
| `on_xml_read` | 834-934 | (no comment) | RegisterScriptCallback("on_xml_read") L837 | - |
| `on_game_start` | 935-961 | (no comment) | RegisterScriptCallback("on_specific_character_dialog_list") L936 | - |


## Jobs

### `00_Core/gamedata/scripts/stalker_camp_builder_jobs.script` (4301 lines, 66 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `consume_one_use` | 15-72 | decrement one use from a multi-use item, or release it | - | - |
| `is_wood_part` | 73-73 | (no comment) | - | - |
| `is_clean_water` | 74-74 | (no comment) | - | - |
| `is_lamp_battery` | 75-75 | (no comment) | - | - |
| `is_generator_fuel` | 76-76 | (no comment) | - | - |
| `is_gunpowder` | 77-77 | (no comment) | - | - |
| `is_scrap` | 78-78 | (no comment) | - | - |
| `is_cloth` | 79-80 | (no comment) | - | - |
| `is_potato` | 81-81 | the farmer's crops: potatoes go to the still, grain is milled and baked into bread | - | - |
| `is_grain` | 82-82 | (no comment) | - | - |
| `is_bread` | 83-85 | (no comment) | - | - |
| `is_fermentable` | 86-106 | product (and the camp's food), so only stale bread goes in the still | - | - |
| `output_box` | 107-115 | its inputs, so that they aren't spent on output there is no room for | - | inv_weight |
| `stalker_camp_builder.set_survivor_job` | 116-218 | assigns a job to a settler and re-syncs their | - | - |
| `stalker_camp_builder.spawn_scavenged_loot` | 219-319 | scavenger finds a stash in the wilderness and uses | - | - |
| `format_deposited_items_summary` | 320-345 | (no comment) | - | - |
| `stalker_camp_builder.spawn_hunted_meat` | 346-436 | drop N random raw mutant meats into box_id | - | - |
| `stalker_camp_builder.is_camp_supply_capped` | 437-653 | checks if camp already has an abundant stockpile | - | - |
| `stalker_camp_builder.process_ammo_crafting` | 654-674 | consume gunpowder + scrap, produce ammo box | - | - |
| `check_sec` | 675-857 | (no comment) | - | - |
| `is_repair_fee` | 858-863 | (no comment) | - | - |
| `gun_parts_worn` | 864-882 | repair round raises. | - | parent_section, con_parts_list |
| `gun_condition_pinned` | 883-890 | wear, and only its parts count. Knives keep a real condition. | - | - |
| `stalker_camp_builder.process_gear_repair` | 891-898 | repair one or more damaged items in exchange for food | - | - |
| `is_valid_box` | 899-908 | (no comment) | - | - |
| `add_box` | 909-958 | (no comment) | - | - |
| `check_item_repair_and_fee` | 959-1132 | (no comment) | - | parent_section, con_parts_list |
| `stalker_camp_builder.get_cooked_version` | 1133-1189 | convert raw meat section to its cooked equivalent | - | - |
| `stalker_camp_builder.find_and_consume_item` | 1190-1196 | search camp containers, consume first match | - | - |
| `stalker_camp_builder.camp_has_item` | 1197-1204 | (no comment) | - | - |
| `stalker_camp_builder.camp_has_repairable_gear` | 1205-1212 | non-destructive check for damaged gear and fee | - | - |
| `check_item` | 1213-1246 | (no comment) | - | - |
| `stalker_camp_builder._calc_job_paused_status` | 1247-1297 | authoritative check for paused settlement jobs | - | - |
| `check_container` | 1298-1754 | (no comment) | - | inv_weight |
| `stalker_camp_builder.get_job_paused_status` | 1755-1783 | (no comment) | - | - |
| `stalker_camp_builder.process_cook_job` | 1784-1842 | consume raw meat + fuel, produce cooked meals | - | - |
| `is_raw_meat` | 1843-1983 | meal that can't be cooked would be lost | - | - |
| `stalker_camp_builder.process_medic_job` | 1984-2003 | produce medical supplies from the medstation | - | - |
| `is_medic_ethanol` | 2004-2211 | (no comment) | - | - |
| `stalker_camp_builder.process_electrician_job` | 2212-2241 | Electrician job: recharge lamp conditions using batteries/mechanical waste, or run generator station | - | - |
| `run_generator` | 2242-2423 | (no comment) | - | - |
| `stalker_camp_builder.process_woodcutter_job` | 2424-2601 | Woodcutter job: harvest timber (prt_i_wood) or burn charcoal (charcoal) | - | - |
| `stalker_camp_builder.process_brewer_job` | 2602-2725 | Brewer job: distill clean water + wood into Nemiroff Vodka | - | - |
| `farmer_text` | 2726-2731 | (no comment) | - | - |
| `stalker_camp_builder.process_farmer_job` | 2732-2898 | (no comment) | - | - |
| `trader_text` | 2899-2907 | (no comment) | - | - |
| `trader_item_state` | 2908-2922 | item is online, its server packet (read with utils_stpk) otherwise | - | - |
| `trader_item_price` | 2923-2951 | in an ammo box, and by condition for anything else. 0 means he will not buy it. | - | cost, quest_item, max_uses, box_size |
| `stalker_camp_builder.process_trader_job` | 2952-3026 | (no comment) | - | - |
| `stalker_camp_builder.collect_trader_takings` | 3027-3039 | hand the player the stall's takings through GAMMA's normal money | - | - |
| `stalker_camp_builder.process_scrapper_job` | 3040-3151 | Scrapper job: salvage metal scrap and hardware from Zone ruins | - | - |
| `is_food_section` | 3152-3162 | (no comment) | - | - |
| `stalker_camp_builder.process_settler_eating` | 3163-3198 | (no comment) | - | - |
| `stalker_camp_builder.get_turret_ammo_count` | 3199-3211 | Turret maintenance: get count + feed ammo | - | - |
| `stalker_camp_builder.feed_turret` | 3212-3239 | (no comment) | - | - |
| `stalker_camp_builder.process_turret_maintenance` | 3240-3274 | (no comment) | - | - |
| `is_valid_box` | 3275-3281 | (no comment) | - | - |
| `add_box` | 3282-3363 | (no comment) | - | - |
| `is_camp_trader` | 3364-3379 | trader's id goes back into use once the body is released. | - | - |
| `stalker_camp_builder.process_settler_equipment` | 3380-3393 | survivors inspect Armory Crate and Quartermaster Locker for weapon and armor upgrades | - | - |
| `is_firearm` | 3394-3508 | a firearm takes ammo: knives, binoculars and grenades have no ammo_class | - | ammo_class, cost, inv_name |
| `vis_key` | 3509-3532 | the suit being worn goes back to the locker (DNPCAV keeps it in the NPC's inventory) | - | - |
| `stalker_camp_builder.update_camp_jobs` | 3533-3664 | (no comment) | CreateTimeEvent("homestead_trader_stock") L3604 | - |
| `is_valid_box` | 3665-4163 | (no comment) | - | - |
| `stalker_camp_builder.get_job_progress` | 4164-4244 | get_job_progress / get_job_time_remaining -- UI helpers used by the PDA | - | - |
| `stalker_camp_builder.get_job_time_remaining` | 4245-4301 | (no comment) | - | - |


## Settlers / recruit

### `00_Core/gamedata/scripts/stalker_camp_builder_npc.script` (796 lines, 15 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `is_valid_level_vertex` | 31-41 | (no comment) | - | - |
| `stalker_camp_builder.camp_npc_move_to` | 42-115 | ============================================================================ | - | - |
| `stalker_camp_builder.camp_npc_arrive` | 116-176 | Clear released destination cache so movement can re-trigger when destination changes | - | - |
| `stalker_camp_builder.anchor_settler_to_smart` | 177-276 | ============================================================================ | - | - |
| `stalker_camp_builder.home_squad_target` | 277-286 | player. | - | - |
| `stalker_camp_builder.pin_settler_home_squad` | 287-302 | load. Companion squads stay with the companion system. | - | - |
| `stalker_camp_builder.forget_binder_squad` | 303-319 | squad, or the binder goes on calling that squad after it is released. | - | - |
| `stalker_camp_builder.release_settler_home_squad` | 320-365 | ============================================================================ | - | - |
| `stalker_camp_builder.convert_settler_to_companion_squad` | 366-426 | ============================================================================ | - | - |
| `stalker_camp_builder.get_settler_job_target` | 427-529 | ============================================================================ | - | - |
| `stalker_camp_builder.teleport_npc_to_camp_hub` | 530-539 | ============================================================================ | - | - |
| `stalker_camp_builder.is_companion` | 540-592 | ============================================================================ | - | - |
| `stalker_camp_builder.get_settler_display_name` | 593-634 | ============================================================================ | - | - |
| `stalker_camp_builder.setup_settler_beh_logic` | 635-767 | ============================================================================ | - | - |
| `stalker_camp_builder.restore_settler_logic` | 768-796 | (no comment) | - | - |

### `00_Core/gamedata/scripts/stalker_camp_builder_recruit.script` (4348 lines, 150 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `stalker_camp_builder.get_territory_ruling_faction` | 19-22 | (no comment) | - | - |
| `stalker_camp_builder.can_settler_safely_live_in_camp` | 23-80 | (no comment) | - | - |
| `resolve_speakers` | 81-84 | (no comment) | - | - |
| `safe_id` | 85-160 | (no comment) | - | - |
| `get_npc_rank_name` | 161-178 | (no comment) | - | - |
| `stalker_camp_builder.get_recruitment_fee` | 179-196 | (no comment) | - | - |
| `stalker_camp_builder.check_recruitment_requirements` | 197-246 | (no comment) | - | - |
| `stalker_camp_builder.get_recruitment_roll` | 247-313 | ============================================================================ | - | - |
| `stalker_camp_builder.no_camps_exist` | 314-321 | (no comment) | - | - |
| `stalker_camp_builder.camps_are_full` | 322-329 | no camp has a free bed (get_recruitable_camps with no stalker skips the faction checks) | - | - |
| `stalker_camp_builder.camps_refuse_recruit` | 330-336 | or its enemies among the settlers (can_settler_safely_live_in_camp) | - | - |
| `stalker_camp_builder.recruitment_roll_success` | 337-347 | (no comment) | - | - |
| `stalker_camp_builder.recruitment_roll_fail` | 348-357 | (no comment) | - | - |
| `stalker_camp_builder.can_recruit` | 358-436 | (no comment) | - | - |
| `stalker_camp_builder.release_npc_from_squad_and_smart` | 437-476 | ============================================================================ | - | - |
| `stalker_camp_builder.set_camp_settler_relations` | 477-529 | ============================================================================ | - | - |
| `stalker_camp_builder.teleport_settler_to_camp_level` | 530-675 | ============================================================================ | CreateTimeEvent("homestead_xteleport_" .. npc_id) L623 | - |
| `stalker_camp_builder.heal_settler_squad_membership` | 676-770 | ============================================================================ | - | - |
| `stalker_camp_builder.heal_corrupted_scripted_targets` | 771-776 | ============================================================================ | - | - |
| `is_settler_squad` | 777-856 | only a squad whose member is one of our settlers is ours to clear | - | - |
| `stalker_camp_builder.heal_orphaned_settler_squads` | 857-876 | (no comment) | - | - |
| `stalker_camp_builder.recall_all_settlers` | 877-915 | (no comment) | - | - |
| `stalker_camp_builder.recruit_npc_to_camp` | 916-1150 | ============================================================================ | - | - |
| `stalker_camp_builder.recruit_npc` | 1151-1163 | (no comment) | - | - |
| `stalker_camp_builder.transfer_survivor_to_camp` | 1164-1255 | (no comment) | - | - |
| `camp_slot_exists` | 1256-1262 | ============================================================================ | - | - |
| `recruit_to_camp_slot` | 1263-1292 | (no comment) | - | - |
| `stalker_camp_builder.camp_slot_1_exists` | 1293-1293 | (no comment) | - | - |
| `stalker_camp_builder.camp_slot_2_exists` | 1294-1294 | (no comment) | - | - |
| `stalker_camp_builder.camp_slot_3_exists` | 1295-1295 | (no comment) | - | - |
| `stalker_camp_builder.camp_slot_4_exists` | 1296-1297 | (no comment) | - | - |
| `stalker_camp_builder.recruit_to_camp_slot_1` | 1298-1298 | (no comment) | - | - |
| `stalker_camp_builder.recruit_to_camp_slot_2` | 1299-1299 | (no comment) | - | - |
| `stalker_camp_builder.recruit_to_camp_slot_3` | 1300-1300 | (no comment) | - | - |
| `stalker_camp_builder.recruit_to_camp_slot_4` | 1301-1305 | (no comment) | - | - |
| `get_camp_slot_text` | 1306-1328 | error or a nil there is fatal. | - | - |
| `stalker_camp_builder.get_camp_slot_1_text` | 1329-1329 | (no comment) | - | - |
| `stalker_camp_builder.get_camp_slot_2_text` | 1330-1330 | (no comment) | - | - |
| `stalker_camp_builder.get_camp_slot_3_text` | 1331-1331 | (no comment) | - | - |
| `stalker_camp_builder.get_camp_slot_4_text` | 1332-1333 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_survivor` | 1334-1366 | (no comment) | - | - |
| `stalker_camp_builder.set_survivor_position` | 1367-1455 | ============================================================================ | - | - |
| `stalker_camp_builder.clear_survivor_position` | 1456-1466 | (no comment) | - | - |
| `stalker_camp_builder.set_survivor_position_to_actor` | 1467-1472 | (no comment) | - | - |
| `stalker_camp_builder.can_recruit_back` | 1473-1493 | (no comment) | - | - |
| `stalker_camp_builder.recruit_back` | 1494-1598 | (no comment) | CreateTimeEvent("recruit_back_" .. npc_id) L1524 | - |
| `stalker_camp_builder.can_return_to_settlement` | 1599-1622 | ============================================================================ | - | - |
| `stalker_camp_builder.get_return_to_settlement_text` | 1623-1639 | listed as a topic), the dialog id and the phrase id (PhraseDialog.cpp 211-219) | - | - |
| `stalker_camp_builder.return_to_settlement` | 1640-1676 | (no comment) | - | - |
| `stalker_camp_builder.find_companion_settler` | 1677-1691 | The camp and entry of a settler away with the player as a companion, or nothing | - | - |
| `stalker_camp_builder.return_dismissed_settler` | 1692-1715 | remove_from_actor_squad wrap (on_game_start) runs it a tick after the dismissal. | - | - |
| `stalker_camp_builder.heal_stuck_companion_settlers` | 1716-1784 | ============================================================================ | - | - |
| `stalker_camp_builder.record_banished_companion` | 1785-1805 | ============================================================================ | - | - |
| `stalker_camp_builder.purge_settler_companion_and_squad_state` | 1806-1990 | ============================================================================ | - | - |
| `stalker_camp_builder.heal_ghost_companion_squads` | 1991-2221 | ============================================================================ | - | - |
| `stalker_camp_builder.dismiss_survivor` | 2222-2254 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_settler` | 2255-2271 | (no comment) | - | - |
| `stalker_camp_builder.survivor_record_matches` | 2272-2285 | hold it until the next load: the record only belongs to the id while the object there has its section | - | - |
| `stalker_camp_builder.can_banish` | 2286-2291 | ============================================================================ | - | - |
| `stalker_camp_builder.banish_npc` | 2292-2329 | (no comment) | - | - |
| `stalker_camp_builder.rename_camp` | 2330-2338 | ============================================================================ | - | - |
| `stalker_camp_builder.rename_survivor` | 2339-2403 | (no comment) | - | - |
| `stalker_camp_builder.reassign_freed_settler_to_smart` | 2404-2493 | ============================================================================ | - | faction |
| `stalker_camp_builder.queue_dismantle_structure_cleanup` | 2494-2525 | ============================================================================ | - | - |
| `is_camp_piece` | 2526-2576 | (no comment) | - | - |
| `is_safe_deletable_item` | 2577-2612 | Test if an ALife object qualifies as ground clutter / loose item to clean up | - | - |
| `evaluate_obj` | 2613-2695 | (no comment) | CreateTimeEvent(event_id) L2672 | - |
| `stalker_camp_builder.is_camp_hub_object` | 2696-2708 | that is gone can leave its id to another object, so the id alone doesn't show the hub is there. | - | - |
| `stalker_camp_builder.release_camp_residents` | 2709-2741 | whose hub is gone) both need it. | - | - |
| `stalker_camp_builder.dismantle_camp` | 2742-2818 | (no comment) | - | - |
| `stalker_camp_builder.cycle_specialization` | 2819-2840 | ============================================================================ | - | - |
| `stalker_camp_builder.get_specialization_mult` | 2841-2855 | (no comment) | - | - |
| `stalker_camp_builder.get_specialization_label` | 2856-2875 | (no comment) | - | - |
| `stalker_camp_builder.get_player_faction` | 2876-2884 | ============================================================================ | - | - |
| `stalker_camp_builder.save_safe_faction` | 2885-2898 | (no comment) | - | - |
| `stalker_camp_builder.get_camp_dominant_faction` | 2899-2934 | ============================================================================ | - | - |
| `stalker_camp_builder.fast_travel_to_camp` | 2935-3007 | ============================================================================ | - | - |
| `stalker_camp_builder.get_camp_trader_section` | 3008-3073 | ============================================================================ | - | - |
| `stalker_camp_builder.summon_caravan` | 3074-3126 | ============================================================================ | CreateTimeEvent("homestead_trader_init") L3104 | - |
| `stalker_camp_builder.start_camp_trader_trade` | 3127-3188 | ============================================================================ | CreateTimeEvent("homestead_trader_break_dialog") L3166, CreateTimeEvent("homestead_trader_break_dialog") L3178 | - |
| `stalker_camp_builder.is_camp_medic` | 3189-3209 | ============================================================================ | - | - |
| `stalker_camp_builder.is_camp_repairer` | 3210-3230 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_trader` | 3231-3256 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_woodcutter` | 3257-3277 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_brewer` | 3278-3298 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_scrapper` | 3299-3320 | (no comment) | - | - |
| `stalker_camp_builder.open_technician_workbench` | 3321-3372 | (no comment) | CreateTimeEvent("homestead_tech_wb") L3365 | - |
| `get_drugkit_camp` | 3373-3387 | the camp a drug kit goes to: the medic's own, else the one the player stands in | - | - |
| `stalker_camp_builder.actor_has_drugkit` | 3388-3394 | (no comment) | - | - |
| `get_upgrade_tier` | 3395-3416 | (no comment) | - | - |
| `get_technician_camp` | 3417-3446 | (no comment) | - | - |
| `hook_inventory_upgrades` | 3447-3498 | (no comment) | - | - |
| `stalker_camp_builder.actor_has_toolkit1` | 3499-3512 | Azot's jup_b217 dialog takes all three) | - | - |
| `stalker_camp_builder.actor_has_toolkit2` | 3513-3526 | (no comment) | - | - |
| `stalker_camp_builder.actor_has_toolkit3` | 3527-3540 | (no comment) | - | - |
| `stalker_camp_builder.medic_treat_actor` | 3541-3580 | (no comment) | - | - |
| `stalker_camp_builder.give_medic_drugkit` | 3581-3599 | NOTE: start_camp_medic_trade is defined later (with resolve_speakers) -- do not define here | - | - |
| `stalker_camp_builder.open_technician_upgrade_ui` | 3600-3627 | (no comment) | - | - |
| `stalker_camp_builder.start_camp_tech_trade` | 3628-3641 | (no comment) | - | - |
| `stalker_camp_builder.start_camp_medic_trade` | 3642-3657 | (no comment) | - | - |
| `deliver_toolkit` | 3658-3687 | NOTE: start_camp_trader_trade is defined earlier (with trading computer support) -- do not redefine here | - | - |
| `stalker_camp_builder.give_tech_toolkit1` | 3688-3688 | (no comment) | - | - |
| `stalker_camp_builder.give_tech_toolkit2` | 3689-3689 | (no comment) | - | - |
| `stalker_camp_builder.give_tech_toolkit3` | 3690-3691 | (no comment) | - | - |
| `stalker_camp_builder.dialog_auto_sort_supplies` | 3692-3695 | (no comment) | - | - |
| `get_speaker_survivor_and_camp` | 3696-3730 | (no comment) | - | - |
| `get_scrapper_tool` | 3731-3742 | the tool the scrapper's hand-in takes: the first one on the list the player carries | - | - |
| `stalker_camp_builder.get_scrapper_tools_text` | 3743-3751 | id and the phrase id (PhraseDialog.cpp 211-219); a Lua error or a nil there is fatal. | - | - |
| `stalker_camp_builder.actor_has_woodcutter_axe` | 3752-3761 | (no comment) | - | - |
| `stalker_camp_builder.give_woodcutter_axe` | 3762-3774 | (no comment) | - | - |
| `stalker_camp_builder.actor_has_brewer_drugkit` | 3775-3783 | (no comment) | - | - |
| `stalker_camp_builder.give_brewer_drugkit` | 3784-3800 | (no comment) | - | - |
| `stalker_camp_builder.actor_has_scrapper_tools` | 3801-3808 | (no comment) | - | - |
| `stalker_camp_builder.give_scrapper_tools` | 3809-3821 | (no comment) | - | - |
| `stalker_camp_builder.is_not_woodcutter_mode_auto` | 3822-3827 | (no comment) | - | - |
| `stalker_camp_builder.is_not_woodcutter_mode_timber` | 3828-3833 | (no comment) | - | - |
| `stalker_camp_builder.is_not_woodcutter_mode_charcoal` | 3834-3839 | (no comment) | - | - |
| `stalker_camp_builder.set_woodcutter_mode_auto` | 3840-3846 | (no comment) | - | - |
| `stalker_camp_builder.set_woodcutter_mode_timber` | 3847-3853 | (no comment) | - | - |
| `stalker_camp_builder.set_woodcutter_mode_charcoal` | 3854-3860 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_farmer` | 3861-3866 | (no comment) | - | - |
| `stalker_camp_builder.has_trader_takings` | 3867-3871 | the Trader has takings from the market stall waiting for the player | - | - |
| `stalker_camp_builder.collect_trader_takings_dialog` | 3872-3878 | (no comment) | - | - |
| `stalker_camp_builder.is_not_farmer_mode_auto` | 3879-3884 | (no comment) | - | - |
| `stalker_camp_builder.is_not_farmer_mode_potato` | 3885-3890 | (no comment) | - | - |
| `stalker_camp_builder.is_not_farmer_mode_grain` | 3891-3896 | (no comment) | - | - |
| `stalker_camp_builder.set_farmer_mode_auto` | 3897-3903 | (no comment) | - | - |
| `stalker_camp_builder.set_farmer_mode_potato` | 3904-3910 | (no comment) | - | - |
| `stalker_camp_builder.set_farmer_mode_grain` | 3911-3921 | (no comment) | - | - |
| `get_wpn_parts_table` | 3922-3944 | ============================================================================ | - | - |
| `get_weapon_repair_tier` | 3945-3971 | (no comment) | - | parent_section, repair_type, cost, ammo_class |
| `stalker_camp_builder.get_tech_overhaul_ask_text` | 3972-4012 | (no comment) | - | parent_section, con_parts_list |
| `stalker_camp_builder.repair_equipped_weapon_and_parts` | 4013-4111 | (no comment) | - | parent_section, con_parts_list |
| `stalker_camp_builder.is_actor_healthy` | 4112-4120 | ============================================================================ | - | - |
| `stalker_camp_builder.is_actor_not_healthy` | 4121-4129 | (no comment) | - | - |
| `stalker_camp_builder.is_actor_injured` | 4130-4137 | (no comment) | - | - |
| `stalker_camp_builder.is_actor_irradiated` | 4138-4144 | (no comment) | - | - |
| `stalker_camp_builder.is_actor_injured_irradiated` | 4145-4158 | (no comment) | - | - |
| `can_pay_medic` | 4159-4161 | (no comment) | - | - |
| `stalker_camp_builder.can_pay_medic_wounds` | 4162-4162 | (no comment) | - | - |
| `stalker_camp_builder.can_pay_medic_rad` | 4163-4163 | (no comment) | - | - |
| `stalker_camp_builder.can_pay_medic_full` | 4164-4165 | (no comment) | - | - |
| `stalker_camp_builder.medic_heal_wounds` | 4166-4184 | (no comment) | - | - |
| `stalker_camp_builder.medic_cure_rad` | 4185-4202 | (no comment) | - | - |
| `stalker_camp_builder.medic_full_treat` | 4203-4225 | (no comment) | - | - |
| `stalker_camp_builder.dialog_set_survivor_position_to_actor` | 4226-4240 | ============================================================================ | - | - |
| `stalker_camp_builder.dialog_clear_survivor_position` | 4241-4249 | (no comment) | - | - |
| `stalker_camp_builder.survivor_has_custom_position` | 4250-4264 | (no comment) | - | - |
| `stalker_camp_builder.mark_settler_companion` | 4265-4301 | npc_on_update kept sending them back to their station: pause the job as recruit_back does | - | - |
| `on_game_start` | 4302-4348 | (no comment) | CreateTimeEvent("homestead_dismissed_" .. npc_id) L4338 | - |


## Storage / inventory

### `00_Core/gamedata/scripts/stalker_camp_builder_storage.script` (1051 lines, 25 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `get_camp_containers` | 15-17 | (no comment) | - | - |
| `stalker_camp_builder.get_box_capacity` | 18-32 | STASH CAPACITY & WEIGHT QUERY UTILITIES (v1.2.4) | - | capacity |
| `stalker_camp_builder.get_box_current_weight` | 33-106 | (no comment) | - | inv_weight, use_condition, max_uses, empty_weight |
| `stalker_camp_builder.box_has_room_for` | 107-122 | (no comment) | - | - |
| `stalker_camp_builder.camp_has_storage_room` | 123-179 | (no comment) | - | - |
| `build_categorized_boxes` | 180-193 | personal = true sorts the player's own furniture boxes in the camp instead of its storage | - | - |
| `make_box_meta` | 194-367 | (no comment) | - | specialized_storage, homestead_storage_buckets |
| `get_camp_categorized_boxes` | 368-378 | (no comment) | - | - |
| `get_personal_categorized_boxes` | 379-422 | kept on the camp-storage cache so every rescan that clears that one clears this too | - | - |
| `route_by_name` | 423-465 | Purifier kit "water". tea and water_drink are kind i_drink, which route_by_kind sends to food. | - | ammo_class, burn_protection |
| `stalker_camp_builder.get_item_sort_route` | 466-485 | route name for an item section: food, fuel, medic, weapon, armor, ammo, parts, tech or misc | - | kind, class |
| `stalker_camp_builder.get_auto_sort_target_box` | 486-519 | AUTO-SORT TARGET ROUTING & CENTRALIZED DEPOSIT SYSTEM (v1.3.0) | - | - |
| `takes_item_meta` | 520-534 | (no comment) | - | kind |
| `pick_box` | 535-545 | (no comment) | - | - |
| `route_box` | 546-608 | (no comment) | - | - |
| `stalker_camp_builder.save_pending_cond` | 609-612 | real item as soon as it exists: every 2s while near it, on spawn, and on pickup. | - | - |
| `stalker_camp_builder.load_pending_cond` | 613-619 | (no comment) | - | - |
| `stalker_camp_builder.queue_item_cond` | 620-633 | (no comment) | - | - |
| `stalker_camp_builder.apply_pending_cond` | 634-668 | (no comment) | - | - |
| `stalker_camp_builder.pending_cond_tick` | 669-696 | (no comment) | - | - |
| `stalker_camp_builder.start_pending_cond_timer` | 697-703 | (no comment) | CreateTimeEvent("homestead_pend_cond") L701 | - |
| `stalker_camp_builder.deposit_item_to_camp` | 704-945 | (no comment) | - | inv_weight, ammo_class, burn_protection, kind, class, parent_section, con_parts_list, max_uses |
| `stalker_camp_builder.smart_dump_to_camp_storage` | 946-975 | (no comment) | - | - |
| `is_item_equipped` | 976-990 | (no comment) | - | - |
| `sort_inventory` | 991-1051 | (no comment) | - | quest_item |

### `00_Core/gamedata/scripts/stalker_camp_builder_containers.script` (411 lines, 12 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `_obj_id` | 9-9 | (no comment) | - | - |
| `_obj_clsid` | 10-13 | (no comment) | - | - |
| `stalker_camp_builder.linked_stash_id` | 14-23 | a Homestead work station's station_stash. nil for anything else. | - | - |
| `stalker_camp_builder.ensure_hub_stash` | 24-60 | (at pos.y - 50) created in alife_storage_manager state so a ground-level inventory_box is never needed. | - | homestead_hub, script_binding |
| `stalker_camp_builder.release_legacy_camp_stash` | 61-66 | and releases the invisible inventory_box so it never remains behind when picking up a workbench or flag. | - | - |
| `drain_and_release_box` | 67-127 | only while both are online, with transfer_item, which keeps each item as it is. | - | - |
| `check_orphan` | 128-163 | (no comment) | - | - |
| `stalker_camp_builder.invalidate_server_container_cache` | 164-170 | (no comment) | - | - |
| `stalker_camp_builder.get_server_container_items` | 171-215 | (no comment) | - | - |
| `stalker_camp_builder.iterate_server_container` | 216-295 | (no comment) | - | - |
| `stalker_camp_builder.safe_iterate_inventory_box` | 296-365 | (no comment) | - | - |
| `stalker_camp_builder.is_actual_container` | 366-411 | (no comment) | - | - |

### `00_Core/gamedata/scripts/stalker_camp_builder_inventory.script` (803 lines, 10 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `stalker_camp_builder.get_camp_containers` | 9-36 | gathers all valid container IDs belonging to a camp | - | - |
| `add_box` | 37-81 | (no comment) | - | - |
| `stalker_camp_builder.consume_one_use` | 82-149 | (no comment) | - | use_condition, max_uses, inv_weight, empty_weight |
| `stalker_camp_builder.camp_iterate_inventory` | 150-361 | UNIFIED SETTLEMENT INVENTORY SIMULATION CONTRACT | - | max_uses |
| `stalker_camp_builder.invalidate_camp_inventory_cache` | 362-382 | (no comment) | - | - |
| `stalker_camp_builder.on_actor_box_change` | 383-433 | (no comment) | - | max_uses |
| `stalker_camp_builder.get_camp_inventory_snapshot` | 434-742 | (no comment) | - | inv_weight |
| `stalker_camp_builder.camp_find_item` | 743-767 | (no comment) | - | - |
| `stalker_camp_builder.camp_consume_item` | 768-789 | (no comment) | - | - |
| `stalker_camp_builder.camp_count_item` | 790-803 | (no comment) | - | - |


## Rivals / raids

### `00_Core/gamedata/scripts/stalker_camp_builder_rivals.script` (3186 lines, 55 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `rival_decor_enabled` | 5-28 | at existing camps and stops new camps/tier upgrades from spawning more. | - | - |
| `get_safe_switch_distance` | 29-35 | despawn within that radius. The engine doesn't export the factor; it is in alife.ltx. | - | alife |
| `get_safe_switch_distance_sqr` | 36-41 | (no comment) | - | - |
| `is_player_near` | 42-54 | whether the player is on level lvl within online switch distance of pos, close enough to see a squad appear or vanish | - | - |
| `in_player_settlement` | 55-72 | outposts keep clear of them (spawn_single_rival_camp) | - | - |
| `is_companion_squad` | 73-78 | whether the player has taken this squad as companions (axr_companions keeps them by squad id) | - | - |
| `release_rival_hold` | 79-95 | stop holding a squad at an outpost: drop the pin and the members' rival lookups | - | - |
| `is_valid_camp_squad` | 96-112 | (no comment) | - | - |
| `is_squad_alive` | 113-132 | (no comment) | - | - |
| `enforce_rival_camp_survivor_cap` | 133-211 | trim garrison members exceeding max_survivors_rival_camp | - | - |
| `courier_id_reused` | 212-216 | squad's id goes to a later object) | - | - |
| `cleanup_camp_convoys` | 217-266 | (no comment) | - | - |
| `safe_teleport_object` | 267-322 | (no comment) | - | - |
| `stalker_camp_builder.setup_rival_squad_positions` | 323-419 | Spawns/teleports squad members to tactical guard posts away from the blue box | - | - |
| `stalker_camp_builder.restrain_rival_squads` | 420-469 | pin rival camp squads in place via script_target and dislodge anyone stuck on the blue box | - | - |
| `stalker_camp_builder.create_squad_at_pos` | 470-492 | spawn a squad at the given position | - | - |
| `stalker_camp_builder.release_camp_decorations` | 493-513 | alife_release all decoration ids on a camp | - | - |
| `stalker_camp_builder.find_nearby_squad_for_repopulation` | 514-570 | find a non-assigned squad near a camp | - | - |
| `stalker_camp_builder.is_underground_smart` | 571-595 | (no comment) | - | - |
| `stalker_camp_builder.is_underground_level` | 596-614 | (no comment) | - | - |
| `build_smart_cache` | 615-642 | (no comment) | - | - |
| `stalker_camp_builder.get_smart_terrains_on_level` | 643-663 | (no comment) | - | - |
| `stalker_camp_builder.get_all_levels_with_smarts` | 664-671 | list level names that have at least one smart (surface only) | - | - |
| `stalker_camp_builder.get_enemy_faction_for` | 672-705 | pick a random enemy faction for the given faction | - | - |
| `stalker_camp_builder.find_wiping_squad` | 706-730 | find a hostile squad within 45m of the camp | - | - |
| `stalker_camp_builder.squad_has_story_npc` | 731-742 | true if any squad member has a story_id (skip these | - | - |
| `stalker_camp_builder.get_level_factions` | 743-810 | returns the list of factions appropriate for a level | - | - |
| `stalker_camp_builder.get_dynamic_squad_section_for_faction` | 811-875 | (no comment) | - | - |
| `reinforce_stronghold` | 876-889 | its furniture, so its new owner gets this squad too; nothing is built. | - | - |
| `squad_has_living_member` | 890-904 | true when any member of the squad is still alive (online object first, server object otherwise) | - | - |
| `roll_occupancy` | 905-909 | Camp Occupancy Duration", scaled by the slider otherwise (cfg holds it in seconds) | - | - |
| `resolve_rival_camp_time_up` | 910-1020 | (no comment) | - | - |
| `roll_rival_heat_mutants` | 1021-1075 | (no comment) | - | - |
| `trigger_rival_skirmish_sos` | 1076-1108 | (no comment) | - | - |
| `resolve_pending_rival_skirmish` | 1109-1200 | (no comment) | - | - |
| `mark_rival_garrison_eliminated` | 1201-1232 | (no comment) | - | - |
| `process_single_rival_camp` | 1233-1451 | (no comment) | - | - |
| `check_empty` | 1452-1516 | (no comment) | - | - |
| `stalker_camp_builder.update_rival_camps` | 1517-1756 | master rival-camp lifecycle manager. | - | - |
| `stalker_camp_builder.snap_rival_camps_to_ground` | 1757-1995 | precision surface anchoring for chests, | - | - |
| `get_rival_camp_theme_sections` | 1996-2027 | and its tier upgrades (at file scope, so upgrade_rival_camp_tier can call it too) | - | - |
| `pick_existing` | 2028-2054 | (no comment) | - | - |
| `stalker_camp_builder.is_rival_decor` | 2055-2069 | (no comment) | - | - |
| `stalker_camp_builder.is_camp_decor` | 2070-2076 | recorded when it was placed, or any outpost section for pieces placed before sections were kept | - | - |
| `spawn_rival_camp_defenses_and_decor` | 2077-2175 | (no comment) | - | - |
| `stalker_camp_builder.spawn_single_rival_camp` | 2176-2488 | attempt to establish 1 rival camp on target_level | - | - |
| `stalker_camp_builder.force_respawn_all_rival_camps` | 2489-2592 | debug: dismantle all and re-spawn 1-4 camps | - | - |
| `stalker_camp_builder.upgrade_rival_camp_tier` | 2593-2787 | 1. CAMP PROGRESSION & TIER EVOLUTION (Tier 1 -> Tier 2 -> Tier 3) | - | bounding_box_size |
| `stalker_camp_builder.dispatch_rival_camp_convoy` | 2788-2877 | Note: is_player_near() is defined at top of file, dynamically respecting alife():switch_distance() | - | - |
| `stalker_camp_builder.update_active_convoys` | 2878-2955 | (no comment) | - | - |
| `stalker_camp_builder.process_rival_camp_surge` | 2956-2976 | 3. SURGE ZOMBIFICATION & MUTANT NEST SYSTEM | - | - |
| `stalker_camp_builder.zombify_rival_camp` | 2977-3030 | (no comment) | - | - |
| `stalker_camp_builder.transform_to_mutant_nest` | 3031-3095 | (no comment) | - | - |
| `stalker_camp_builder.trigger_allied_reinforcement` | 3096-3139 | 4. ALLIED REINFORCEMENTS & RETALIATION HIT SQUADS | - | - |
| `stalker_camp_builder.check_sos_rescue_reward` | 3140-3186 | 5. SOS RESCUE REWARD & GRATITUDE | - | - |


## Expeditions

### `00_Core/gamedata/scripts/stalker_camp_builder_expeditions.script` (1983 lines, 53 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `game_sec` | 14-14 | these stay in stalker_camp_builder.script; its module-level functions aren't globals here | - | - |
| `camp_send_tip` | 15-15 | (no comment) | - | - |
| `add_radio_feed_entry` | 16-17 | (no comment) | - | - |
| `is_level_vertex` | 18-24 | (no comment) | - | - |
| `stalker_camp_builder.get_expedition_for_stash` | 25-48 | (no comment) | - | - |
| `stalker_camp_builder.restore_missing_settler` | 49-116 | (no comment) | - | - |
| `stalker_camp_builder.recall_scavenger_expedition_by_npc` | 117-136 | (no comment) | - | - |
| `stalker_camp_builder.get_scavenger_expedition_for_survivor` | 137-151 | (no comment) | - | - |
| `stalker_camp_builder.recall_scavenger_expedition` | 152-205 | (no comment) | - | - |
| `stalker_camp_builder.get_available_scavengers` | 206-273 | (no comment) | - | - |
| `stalker_camp_builder.is_quest_or_task_stash` | 274-339 | (no comment) | - | quest_item |
| `is_player_stash` | 340-345 | a backpack stash the player dropped (item_backpack records each one) | - | - |
| `is_stash_box` | 346-351 | a stash is an inventory box; a marker on anything else (an NPC) doesn't make one | - | - |
| `has_marked_stash_spot` | 352-366 | (no comment) | - | - |
| `stalker_camp_builder.is_settlement_structure_or_hub` | 367-398 | (no comment) | - | - |
| `stalker_camp_builder.is_stash_spot` | 399-417 | (no comment) | - | - |
| `stalker_camp_builder.is_stash_yellow` | 418-465 | (no comment) | - | - |
| `stalker_camp_builder.get_level_marked_stashes` | 466-473 | (no comment) | - | - |
| `evaluate_stash_candidate` | 474-563 | (no comment) | - | - |
| `get_self_contained_obj_info` | 564-599 | (no comment) | - | - |
| `get_self_contained_global_pos` | 600-607 | (no comment) | - | - |
| `get_self_contained_distance` | 608-624 | (no comment) | - | - |
| `get_self_contained_duration_sec` | 625-700 | (no comment) | - | - |
| `roll_gamma_toolkit` | 701-754 | (no comment) | - | - |
| `generate_gamma_stash_loot` | 755-814 | (no comment) | - | - |
| `split_stash_entry` | 815-823 | Extract_Uses splits it the same way when the player opens the stash | - | - |
| `loot_and_clear_stash` | 824-1004 | (no comment) | - | ammo_class |
| `stalker_camp_builder.calculate_single_stash_duration` | 1005-1019 | (no comment) | - | - |
| `stalker_camp_builder.calculate_regional_sweep_duration` | 1020-1076 | (no comment) | - | - |
| `stalker_camp_builder.format_expedition_time` | 1077-1097 | (no comment) | - | - |
| `stalker_camp_builder.format_expedition_real_mins` | 1098-1110 | (no comment) | - | - |
| `stalker_camp_builder.map_spot_menu_add_property` | 1111-1202 | (no comment) | - | - |
| `stalker_camp_builder.map_spot_menu_property_clicked` | 1203-1224 | (no comment) | - | - |
| `stalker_camp_builder.allow_home_squad_online` | 1225-1237 | would go with him. Returns it. | - | - |
| `teleport_scavenger_on_departure` | 1238-1277 | (no comment) | - | - |
| `stalker_camp_builder.dispatch_scavenger_to_stash` | 1278-1385 | (no comment) | - | - |
| `stalker_camp_builder.dispatch_scavenger_regional_sweep` | 1386-1474 | (no comment) | - | - |
| `get_item_display_name` | 1475-1492 | (no comment) | - | inv_name |
| `get_expedition_progress` | 1493-1498 | game time alone: it counts sleep, and runs at the faster pace of emissions and psi storms | - | - |
| `emit_expedition_chatter` | 1499-1520 | (no comment) | - | - |
| `loot_due_stashes` | 1521-1534 | (no comment) | - | - |
| `find_expedition_camp` | 1535-1556 | (no comment) | - | - |
| `find_expedition_survivor` | 1557-1572 | (no comment) | - | - |
| `is_level_vertex` | 1573-1576 | `level` has no valid_vertex_id (that is a game graph method); u32(-1) means no vertex | - | - |
| `reposition_survivor_at_camp` | 1577-1690 | (no comment) | CreateTimeEvent("homestead_exp_return") L1673 | - |
| `roll_expedition_ambush` | 1691-1718 | (no comment) | - | - |
| `deposit_expedition_haul` | 1719-1724 | (no comment) | - | - |
| `record` | 1725-1773 | (no comment) | - | - |
| `award_expedition_xp` | 1774-1800 | (no comment) | - | - |
| `format_expedition_receipt` | 1801-1871 | (no comment) | - | - |
| `cleanup_expedition` | 1872-1901 | Per-expedition completion (was the ~180-line pcall'd body) | - | - |
| `complete_expedition` | 1902-1944 | (no comment) | - | - |
| `stalker_camp_builder.process_stash_expeditions` | 1945-1983 | orchestrator | - | - |

### `00_Core/gamedata/scripts/stalker_camp_builder_events.script` (562 lines, 12 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `stalker_camp_builder.get_event_timers` | 16-19 | (no comment) | - | - |
| `stalker_camp_builder.set_event_timers` | 20-26 | (no comment) | - | - |
| `process_camp_random_events` | 27-61 | (no comment) | - | - |
| `trigger_random_camp_event` | 62-209 | (no comment) | CreateTimeEvent("homestead_trader_init") L165 | inv_name |
| `spawn_camp_raid` | 210-308 | (no comment) | - | - |
| `enforce_raid_hostility` | 309-379 | (no comment) | CreateTimeEvent("homestead_raid_hostile_1_" .. squad.id) L329, CreateTimeEvent("homestead_raid_hostile_2_" .. squad.id) L333 | - |
| `has_active_alarm` | 380-394 | does this camp have a switched-on alarm siren | - | - |
| `process_camp_raids` | 395-456 | (no comment) | - | - |
| `stalker_camp_builder.end_camp_raid` | 457-468 | following the player to every level, as check_completed_raids sees only camps that still exist | - | - |
| `check_completed_raids` | 469-548 | (no comment) | - | - |
| `refugee_on_net_spawn` | 549-558 | first time it is online; the server object keeps the community from then on | - | - |
| `on_game_start` | 559-562 | (no comment) | RegisterScriptCallback("npc_on_net_spawn") L560 | - |

### `00_Core/gamedata/scripts/stalker_camp_builder_scan.script` (349 lines, 7 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `_se_sec_name` | 14-15 | (no comment) | - | - |
| `stalker_camp_builder.reset_scan_camp_structures_cache` | 16-24 | (no comment) | - | - |
| `stalker_camp_builder.scan_camp_structures` | 25-72 | (no comment) | - | - |
| `evaluate_furniture_candidate` | 73-152 | or allocating strings, filtering out 98%+ of world objects with zero garbage. | - | placeable_section |
| `stalker_camp_builder.scan_multiple_camp_structures` | 153-193 | (no comment) | - | - |
| `evaluate_multi` | 194-315 | (no comment) | - | placeable_section |
| `stalker_camp_builder.invalidate_scan_camp_structures_cache` | 316-349 | (no comment) | - | - |

### `00_Core/gamedata/scripts/stalker_camp_builder_radio.script` (301 lines, 7 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `trim_radio_log` | 19-30 | oldest reports. The next scan writes its lines again; a report pushed out is gone. | - | - |
| `stalker_camp_builder.intercept_pda_news_message` | 31-34 | (no comment) | - | - |
| `add_camp_radio_log` | 35-91 | (no comment) | - | - |
| `add_radio_feed_entry` | 92-95 | (no comment) | - | - |
| `clear_camp_radio_logs` | 96-103 | (no comment) | - | - |
| `hook_homestead_news_manager` | 104-107 | (no comment) | - | - |
| `stalker_camp_builder.seed_initial_settlement_telemetry` | 108-301 | (no comment) | - | - |


## PDA UI

### `00_Core/gamedata/scripts/ui_stalker_camp_builder_pda.script` (3246 lines, 87 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `make_gauge` | 7-14 | PDA AUTOMATED KEYWORD COLORIZER & GAUGES (iTheon Tactical Engine) | - | - |
| `escape_pda_pattern` | 15-18 | (no comment) | - | - |
| `colorize_pda_text_base` | 19-41 | (no comment) | - | - |
| `colorize_pda_text` | 42-45 | the same, in the theme's colors | - | - |
| `play_pda_ui_sound` | 46-50 | (no comment) | - | - |
| `close_pda` | 51-63 | by CUIPdaWnd::SetActiveSubdialog without a dialog holder, so its own HideDialog does nothing. | - | - |
| `get_singleton` | 64-65 | (no comment) | - | - |
| `homestead_pda_actor_on_update` | 66-83 | (no comment) | - | - |
| `get_ui` | 84-106 | (no comment) | RegisterScriptCallback("actor_on_update") L89 | - |
| `SettlementListItem:__init` | 107-135 | (no comment) | - | - |
| `SettlementListItem:SetSelected` | 136-152 | (no comment) | - | - |
| `SurvivorListItem:__init` | 153-204 | (no comment) | - | - |
| `SurvivorListItem:SetSelected` | 205-222 | (no comment) | - | - |
| `SurvivorListItem:UpdateStatus` | 223-234 | run over the rank line under it) | - | - |
| `TransferCampListItem:__init` | 235-247 | (no comment) | - | - |
| `RivalListItem:__init` | 248-303 | (no comment) | - | - |
| `RivalListItem:SetSelected` | 304-320 | (no comment) | - | - |
| `SettlementManagerPDA:__init` | 321-324 | (no comment) | - | - |
| `SettlementManagerPDA:__finalize` | 325-331 | (no comment) | - | - |
| `SettlementManagerPDA:OnKeyboard` | 332-345 | (no comment) | - | - |
| `SettlementManagerPDA:InitControls` | 346-537 | (no comment) | - | - |
| `init_safe_job_btn` | 538-744 | (no comment) | - | - |
| `SettlementManagerPDA:SetTab` | 745-869 | (no comment) | - | - |
| `SettlementManagerPDA:UpdateTopStatusBar` | 870-923 | (no comment) | - | - |
| `SettlementManagerPDA:Update` | 924-953 | (no comment) | - | - |
| `selected_value` | 954-958 | list rebuilds select the row that was selected before (by an item field), else the first | - | - |
| `row_of` | 959-970 | (no comment) | - | - |
| `SettlementManagerPDA:Reset` | 971-1109 | (no comment) | - | - |
| `SettlementManagerPDA:ClearDetails` | 1110-1131 | (no comment) | - | - |
| `SettlementManagerPDA:ClearRivalDetails` | 1132-1142 | (no comment) | - | - |
| `SettlementManagerPDA:OnRivalSelected` | 1143-1324 | (no comment) | - | - |
| `SettlementManagerPDA:OnRefreshClicked` | 1325-1330 | (no comment) | - | - |
| `SettlementManagerPDA:RenderOverviewStats` | 1331-1441 | (no comment) | - | - |
| `SettlementManagerPDA:OnSettlementSelected` | 1442-1530 | (no comment) | - | - |
| `SettlementManagerPDA:RefreshOverviewLive` | 1531-1540 | (no comment) | - | - |
| `SettlementManagerPDA:OnSurvivorSelected` | 1541-2068 | (no comment) | - | - |
| `SettlementManagerPDA:GetSurvivorInfo` | 2069-2078 | (no comment) | - | - |
| `SettlementManagerPDA:AssignJob` | 2079-2089 | (no comment) | - | - |
| `SettlementManagerPDA:OnPositionHereClicked` | 2090-2104 | (no comment) | - | - |
| `SettlementManagerPDA:OnPositionRecallClicked` | 2105-2140 | (no comment) | - | - |
| `SettlementManagerPDA:OnJobDirectiveClicked` | 2141-2204 | (no comment) | - | - |
| `SettlementManagerPDA:OnTransferClicked` | 2205-2223 | (no comment) | - | - |
| `SettlementManagerPDA:OnRenameClicked` | 2224-2235 | (no comment) | - | - |
| `SettlementManagerPDA:OnCycleSpecialization` | 2236-2243 | (no comment) | - | - |
| `SettlementManagerPDA:OnFastTravelClicked` | 2244-2268 | (no comment) | - | - |
| `SettlementManagerPDA:OnSummonCaravanClicked` | 2269-2288 | (no comment) | - | - |
| `SettlementManagerPDA:OnDismantleClicked` | 2289-2305 | (no comment) | - | - |
| `SettlementManagerPDA:OnRecallSettlersClicked` | 2306-2318 | (no comment) | - | - |
| `SettlementManagerPDA:OnBanishClicked` | 2319-2335 | (no comment) | - | - |
| `SettlementManagerPDA:OnRenameSurvivorClicked` | 2336-2347 | (no comment) | - | - |
| `SettlementManagerPDA:FormatSurvivorStatus` | 2348-2536 | (no comment) | - | - |
| `SettlementManagerPDA:UpdateSurvivorsProgress` | 2537-2597 | (no comment) | - | - |
| `SettlementManagerPDA:OnManualRefresh` | 2598-2618 | (no comment) | - | - |
| `SettlementManagerPDA:RefitSurvivorDetail` | 2619-2632 | moves by the difference. Positions only: the texts stay as the refresh wrote them. | - | - |
| `shift` | 2633-2640 | (no comment) | - | - |
| `grow` | 2641-2670 | (no comment) | - | - |
| `SettlementManagerPDA:RefreshJobProgress` | 2671-2842 | (no comment) | - | - |
| `UIRenameCamp:__init` | 2843-2850 | (no comment) | - | - |
| `UIRenameCamp:__finalize` | 2851-2853 | (no comment) | - | - |
| `UIRenameCamp:InitControls` | 2854-2881 | (no comment) | - | - |
| `UIRenameCamp:InitCallBacks` | 2882-2886 | (no comment) | - | - |
| `UIRenameCamp:OnAccept` | 2887-2900 | (no comment) | - | - |
| `UIRenameCamp:OnKeyboard` | 2901-2912 | (no comment) | - | - |
| `UIRenameCamp:Close` | 2913-2920 | (no comment) | - | - |
| `UIRenameSurvivor:__init` | 2921-2928 | (no comment) | - | - |
| `UIRenameSurvivor:__finalize` | 2929-2931 | (no comment) | - | - |
| `UIRenameSurvivor:InitControls` | 2932-2959 | (no comment) | - | - |
| `UIRenameSurvivor:InitCallBacks` | 2960-2964 | (no comment) | - | - |
| `UIRenameSurvivor:OnAccept` | 2965-2985 | (no comment) | - | - |
| `UIRenameSurvivor:OnKeyboard` | 2986-2997 | (no comment) | - | - |
| `UIRenameSurvivor:Close` | 2998-3003 | (no comment) | - | - |
| `SettlementManagerPDA:OnAutoSortClicked` | 3004-3016 | (no comment) | - | - |
| `SettlementManagerPDA:SetSurvivorFilter` | 3017-3055 | ROSTER FILTER & MAP LOCATE HANDLERS | - | - |
| `SettlementManagerPDA:OnFilterAllClicked` | 3056-3059 | (no comment) | - | - |
| `SettlementManagerPDA:OnFilterExpClicked` | 3060-3063 | (no comment) | - | - |
| `SettlementManagerPDA:OnFilterWorkClicked` | 3064-3067 | (no comment) | - | - |
| `SettlementManagerPDA:OnFilterIdleClicked` | 3068-3071 | (no comment) | - | - |
| `SettlementManagerPDA:OnLocateSettlementMapClicked` | 3072-3086 | (no comment) | - | - |
| `SettlementManagerPDA:OnLocateRivalMapClicked` | 3087-3110 | (no comment) | - | - |
| `SettlementManagerPDA:SetRadioFilter` | 3111-3140 | RADIO FEED HANDLERS (v1.0.3 Rebuild) | - | - |
| `SettlementManagerPDA:OnRadioFilterAllClicked` | 3141-3144 | (no comment) | - | - |
| `SettlementManagerPDA:OnRadioFilterExpClicked` | 3145-3148 | (no comment) | - | - |
| `SettlementManagerPDA:OnRadioFilterWorkClicked` | 3149-3152 | (no comment) | - | - |
| `SettlementManagerPDA:OnRadioFilterCombatClicked` | 3153-3156 | (no comment) | - | - |
| `SettlementManagerPDA:OnRadioScanClicked` | 3157-3163 | (no comment) | - | - |
| `SettlementManagerPDA:OnRadioClearClicked` | 3164-3173 | (no comment) | - | - |
| `SettlementManagerPDA:PopulateRadioFeed` | 3174-3246 | (no comment) | - | - |

### `00_Core/gamedata/scripts/z_stalker_camp_builder_pda_monkeypatch.script` (685 lines, 21 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `_se_community` | 5-5 | When clicked, it redirects to the standalone Settlements subdialog. | - | - |
| `_se_clsid` | 6-6 | (no comment) | - | - |
| `_se_profile_name` | 7-7 | (no comment) | - | - |
| `_se_set_profile_name` | 8-9 | (no comment) | - | - |
| `on_game_start` | 10-32 | (no comment) | - | - |
| `outpost_piece` | 33-36 | and the radio and lamp dialogs pick the piece up without asking. Outposts place both. | - | - |
| `keep_outpost_piece` | 37-46 | (no comment) | - | - |
| `keep_outpost_piece_in_dialog` | 47-226 | (no comment) | - | kind, species |
| `pda.set_active_subdialog` | 227-319 | (no comment) | CreateTimeEvent("homestead_pda") L233 | - |
| `pass_results` | 320-356 | (no comment) | - | - |
| `get_safe_profile_for_se` | 357-372 | ========================================================================= | - | - |
| `sanitize_se_profile` | 373-388 | (no comment) | - | - |
| `sanitize_all_stalker_profiles` | 389-451 | 1. Sweep all ALife stalkers on game load / level load to sanitize existing broken profiles | RegisterScriptCallback("actor_on_first_update") L412, RegisterScriptCallback("server_entity_on_register") L413 | - |
| `engage_homestead_disconnect_grace` | 452-473 | (no comment) | RegisterScriptCallback("on_level_changing") L458, RegisterScriptCallback("actor_on_net_destroy") L459 | - |
| `is_homestead_craft_sec` | 474-479 | (no comment) | - | - |
| `parse_craft_recipe_line` | 480-622 | (no comment) | - | - |
| `slot_count` | 623-635 | (no comment) | - | - |
| `GUI_CLASS:BuildMainMenu` | 636-648 | (no comment) | - | - |
| `GUI_CLASS:InitCallBacks` | 649-656 | (no comment) | - | - |
| `GUI_CLASS:RefreshTabVisibility` | 657-673 | (no comment) | - | - |
| `GUI_CLASS:OnClickMainMenu` | 674-685 | (no comment) | - | - |

### `00_Core/gamedata/scripts/z_stalker_camp_builder_pda_mac.script` (50 lines, 3 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `restore_tab_bar` | 5-11 | (no comment) | - | - |
| `safe_get_ui` | 12-21 | (no comment) | CreateTimeEvent("homestead_pda") L15 | - |
| `on_game_start` | 22-50 | (no comment) | CreateTimeEvent("homestead_pda") L41 | - |

### `00_Core/gamedata/scripts/ui_stalker_camp_builder_theme.script` (146 lines, 13 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `c` | 66-69 | (no comment) | - | - |
| `rgb` | 70-74 | (no comment) | - | - |
| `argb` | 75-82 | (no comment) | - | - |
| `markup` | 83-87 | keeps the element's default color (CUILines::GetColorFromText). | - | - |
| `recolor` | 88-91 | (no comment) | - | - |
| `swap` | 92-96 | (no comment) | - | - |
| `swap3` | 97-103 | three numbers are not a color to the engine: map them, or at least add the alpha | - | - |
| `texture` | 104-108 | (no comment) | - | - |
| `faction` | 109-114 | a faction's color for a rival camp, as ARGB; nil for an unknown faction | - | - |
| `faction_codes` | 115-123 | every faction's color as an "a,r,g,b" string, for inline markup in log text | - | - |
| `set_active` | 124-130 | mark a button selected or not, by texture (see the engine note above) | - | - |
| `banner` | 131-142 | the backing of a status line: kind is "secure", "neutral" or "threat" | - | - |
| `short` | 143-146 | label never wraps: what does not fit runs past both edges. | - | - |

### `01_Theme_Vanilla/gamedata/scripts/ui_stalker_camp_builder_theme.script` (146 lines, 13 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `c` | 66-69 | (no comment) | - | - |
| `rgb` | 70-74 | (no comment) | - | - |
| `argb` | 75-82 | (no comment) | - | - |
| `markup` | 83-87 | keeps the element's default color (CUILines::GetColorFromText). | - | - |
| `recolor` | 88-91 | (no comment) | - | - |
| `swap` | 92-96 | (no comment) | - | - |
| `swap3` | 97-103 | three numbers are not a color to the engine: map them, or at least add the alpha | - | - |
| `texture` | 104-108 | (no comment) | - | - |
| `faction` | 109-114 | a faction's color for a rival camp, as ARGB; nil for an unknown faction | - | - |
| `faction_codes` | 115-123 | every faction's color as an "a,r,g,b" string, for inline markup in log text | - | - |
| `set_active` | 124-130 | mark a button selected or not, by texture (see the engine note above) | - | - |
| `banner` | 131-142 | the backing of a status line: kind is "secure", "neutral" or "threat" | - | - |
| `short` | 143-146 | label never wraps: what does not fit runs past both edges. | - | - |


## Prosper

### `00_Core/gamedata/scripts/stalker_camp_builder_prosper.script` (324 lines, 24 functions)

Top-level (outside functions): hooks: AddScriptCallback(name) L49; cfg: none

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `sb.send_settler_callback` | 53-58 | send one of the callbacks; a failing listener must not break Homestead's own flow | - | - |
| `sb.settler_id_of_record` | 59-66 | the NPC id a settler record belongs to, for events that only carry the record | - | - |
| `prosper_move_on_on` | 67-70 | (no comment) | - | - |
| `prosper_cut_on` | 71-74 | (no comment) | - | - |
| `prosper_savings_cap` | 75-79 | (no comment) | - | - |
| `sb.prosper_credit` | 80-89 | credit a settler's cut, clamped so the real-time economy cannot run away | - | - |
| `sb.prosper_on_work` | 90-96 | a completed work cycle pays the settler's cut, scaled by tier | - | - |
| `sb.prosper_overflow_allowed` | 97-101 | a job with no room for its output keeps earning its cut, instead of pausing, until the savings cap | - | - |
| `sb.prosper_overflow_cycles` | 102-106 | how many whole cycles are due for a job that is saving instead of running; at most 2 per tick | - | - |
| `sb.prosper_overflow_credit` | 107-113 | (no comment) | - | - |
| `sb.prosper_queue_standing` | 114-119 | queue a rank and reputation change on the record; applied when the NPC is online | - | - |
| `sb.prosper_on_promotion` | 120-125 | (no comment) | - | - |
| `sb.prosper_apply_standing` | 126-142 | apply the queued standing to a game object that is online; a failed apply stays queued | - | - |
| `prosper_is_firearm` | 143-147 | (no comment) | - | ammo_class |
| `prosper_ammo_for` | 148-158 | (no comment) | - | ammo_class |
| `sb.prosper_try_buy` | 159-213 | the ammo for it comes with it, so the settler's own needs are met first | - | cost, inv_name |
| `sb.prosper_tick` | 214-229 | then apply it when the NPC is online, then a purchase | - | - |
| `prosper_clean_community` | 230-236 | the faction without the "actor_" prefix the player's own faction carries | - | - |
| `sb.set_settler_community` | 237-257 | net spawn otherwise (pending_community). Returns true when a settler record was found. | - | - |
| `sb.get_trader_community` | 258-266 | the camp's visiting trader faction, or nil when no trader is present | - | - |
| `sb.set_trader_community` | 267-280 | trader was present. | - | - |
| `sb.prosper_on_trader_arrived` | 281-286 | a trader came to the camp | - | - |
| `sb.prosper_on_trader_departed` | 287-293 | the trader left, or was lost; call before the camp forgets their id | - | - |
| `sb.prosper_try_move_on` | 294-324 | the faction's goodwill with the player rises, and the player gets word of it | - | - |


## HomesteadHF furniture

### `HomesteadHF/gamedata/scripts/homestead_snap.script` (612 lines, 34 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `mcm_get` | 62-68 | ------------------- | - | - |
| `load_settings` | 69-84 | (no comment) | - | snap_enabled, snap_key, rotate_key, snap_radius, furniture_grid, ground_fit |
| `get_info` | 85-115 | { class = , w = , t = , half = } for a world section; class "furniture" when not a building piece | - | homestead_snap |
| `get_corners` | 116-132 | the 8 local corners of the HF bbox of a section, as HF builds it | - | bounding_box_size, bounding_box_origin |
| `rot_y` | 133-138 | ------------------- | - | - |
| `dir_yaw` | 139-142 | yaw that turns local +Z onto the direction (dx, dz) | - | - |
| `wrap_angle` | 143-149 | (no comment) | - | - |
| `quad_yaw` | 150-154 | base + k*90 degrees, the one nearest to want | - | - |
| `quantise` | 155-159 | (no comment) | - | - |
| `clamp` | 160-164 | (no comment) | - | - |
| `to_world` | 165-169 | (no comment) | - | - |
| `to_local` | 170-178 | (no comment) | - | - |
| `get_frame` | 179-200 | position and yaw of a placed piece, from its server object | - | - |
| `find_target` | 201-242 | (no comment) | - | - |
| `roof_neighbours` | 243-276 | vertical shift). Two eaves meeting (a V gutter) do not count. | - | - |
| `sockets` | 277-278 | target the player aims at to pick it. quad = any of the 4 yaws, nearest to the preview wins. | - | - |
| `add` | 279-285 | (no comment) | - | - |
| `neighbours` | 286-292 | next tile over on each side | - | - |
| `wall_laterals` | 293-367 | lateral offsets of a tile centre along a wall: a half wall sits on either half of the edge | - | - |
| `solve_building` | 368-384 | best socket for a building piece: nearest anchor to the aim point within snap_radius | - | - |
| `solve_furniture` | 385-415 | (no comment) | - | - |
| `solve` | 416-432 | snapped { pos, yaw } for this frame, or nil to leave HF's own transform alone | - | - |
| `snapping` | 433-449 | (no comment) | - | - |
| `ground_height` | 450-457 | (no comment) | - | - |
| `fit_foundation` | 458-477 | fitted pivot height and whether the ground is too uneven for the skirt, or nil without ground | - | - |
| `install_hooks` | 478-481 | ------------------- | - | - |
| `placeable_furniture.start_placing_item` | 482-495 | (no comment) | - | - |
| `placeable_furniture.set_state` | 496-513 | (no comment) | - | - |
| `bbox_class:SetWorldOrigin` | 514-545 | (no comment) | - | - |
| `bbox_class:CheckForCollisions` | 546-565 | (no comment) | - | - |
| `placeable_furniture.create_object` | 566-581 | (no comment) | - | - |
| `on_before_key_press` | 582-594 | (R reloads). Swallowing them also keeps HF from cancelling placement. | - | - |
| `hf_present` | 595-601 | (no comment) | - | - |
| `on_game_start` | 602-612 | (no comment) | RegisterScriptCallback("on_option_change") L609, RegisterScriptCallback("on_before_key_press") L610 | - |

### `HomesteadHF/gamedata/scripts/homestead_hologram.script` (171 lines, 15 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `mcm_get` | 22-28 | (no comment) | - | - |
| `load_settings` | 29-38 | (no comment) | - | hologram |
| `model_path` | 39-44 | ------------------- | - | visual |
| `tint` | 45-59 | (no comment) | - | - |
| `remove_hologram` | 60-65 | (no comment) | - | - |
| `ensure_hologram` | 66-85 | (no comment) | - | - |
| `update` | 86-100 | (no comment) | - | - |
| `safe_update` | 101-112 | (no comment) | - | - |
| `install_hooks` | 113-114 | ------------------- | - | - |
| `placeable_furniture.start_placing_item` | 115-127 | (no comment) | - | - |
| `renderer:DrawBShapeCollider` | 128-132 | runs every frame after HF (and the snap hooks) have set the preview's final transform | - | - |
| `renderer:Stop` | 133-140 | (no comment) | - | - |
| `on_update` | 141-147 | placement can end without the renderer being stopped (e.g. a save is loaded) | - | - |
| `hf_present` | 148-154 | (no comment) | - | - |
| `on_game_start` | 155-171 | (no comment) | RegisterScriptCallback("on_option_change") L167, RegisterScriptCallback("actor_on_update") L168, RegisterScriptCallback("actor_on_net_destroy") L169 | - |

### `HomesteadHF/gamedata/scripts/homestead_lock.script` (217 lines, 16 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `mcm_get` | 37-43 | (no comment) | - | - |
| `report` | 44-47 | (no comment) | - | - |
| `set_static` | 48-58 | (no comment) | - | - |
| `save_spot` | 59-63 | (no comment) | - | - |
| `clear_spot` | 64-71 | (no comment) | - | - |
| `forget_piece` | 72-80 | objects, which have no Lua server class, so axr_main never clears their se vars. | - | - |
| `hpb_axes` | 81-89 | rotation can have a different heading/pitch/bank (heading +-pi, a piece tipped onto its side). | - | - |
| `turn_between` | 90-98 | Angle of the rotation from one heading/pitch/bank to the other: trace(A^T B) = 1 + 2 cos(angle). | - | - |
| `keeps_rotation` | 99-102 | lot for a tiny change of the rotation, so its rotation can't be rebuilt from it. | - | - |
| `report_put_back` | 103-109 | (no comment) | - | - |
| `put_back` | 110-131 | force_set_* move the physics shell without waking it. | CreateTimeEvent("homestead_lock") L125 | - |
| `hook_set_frozen` | 132-150 | when it was declared, before on_game_start could replace hf_binder_wrapper's. | - | - |
| `on_piece_frozen` | 151-171 | Runs after HF has frozen a piece that just came online. | - | - |
| `load_settings` | 172-192 | (no comment) | - | lock_furniture |
| `hook_freeze` | 193-205 | HF's net_spawn looks freeze_obj up when it runs, so replacing it here covers every piece. | - | - |
| `on_game_start` | 206-217 | (no comment) | RegisterScriptCallback("on_option_change") L214, RegisterScriptCallback("server_object_on_unregister") L215 | lock_furniture |

### `HomesteadHF/gamedata/scripts/homestead_market_stall.script` (100 lines, 8 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `state` | 7-13 | alife_storage_manager state: market_stashes[stall_id] = stash_id. | - | - |
| `get_stash` | 14-41 | id of the stall's stash, creating it when there is none yet | - | - |
| `find_stash` | 42-48 | the stash id if it already exists (no creation): what the Trader sells from | - | - |
| `open_stash` | 49-58 | (no comment) | - | - |
| `use_stall` | 59-64 | Hideout Furniture menu (with Pick Up) | CreateTimeEvent("homestead_market") L62 | - |
| `init` | 65-70 | (no comment) | bind_object(market_stall_wrapper(obj) L66 | - |
| `market_stall_wrapper:__init` | 71-75 | (no comment) | - | - |
| `market_stall_wrapper:pickup` | 76-100 | picking the stall up hands the goods back first | - | - |

### `HomesteadHF/gamedata/scripts/homestead_settlement_flag.script` (72 lines, 7 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `actor_faction` | 10-18 | (no comment) | - | - |
| `swap_flag` | 19-27 | swap a flag of another faction (or the crafted one) for the player's faction's flag | - | - |
| `actor_on_item_take` | 28-36 | (no comment) | CreateTimeEvent("homestead_flag") L34 | - |
| `on_game_start` | 37-40 | (no comment) | RegisterScriptCallback("actor_on_item_take") L38 | - |
| `init` | 41-46 | (no comment) | bind_object(flag_wrapper(obj) L42 | - |
| `flag_wrapper:__init` | 47-51 | (no comment) | - | - |
| `flag_wrapper:pickup` | 52-72 | picking the flag up takes the settlement down with it, like picking up a Workshop hub | - | - |

### `HomesteadHF/gamedata/scripts/homestead_station_storage.script` (131 lines, 12 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `state` | 8-14 | station_stashes[station_id] = stash_id. | - | - |
| `forget_camp_containers` | 15-25 | the camps cache their containers: a new or removed stash must show up at once | - | - |
| `get_stash` | 26-47 | id of the station's stash, creating it when there is none yet | - | - |
| `find_stash` | 48-54 | the stash id if it already exists (no creation) | - | - |
| `open_stash` | 55-64 | (no comment) | - | - |
| `use_station` | 65-73 | Hideout Furniture menu (with Pick Up) | CreateTimeEvent("homestead_station") L71 | - |
| `make_stash` | 74-78 | (no comment) | - | - |
| `init` | 79-84 | (no comment) | bind_object(station_wrapper(obj) L80 | - |
| `station_wrapper:__init` | 85-90 | (no comment) | - | - |
| `station_wrapper:net_spawn` | 91-96 | so settlers can store in it before the player ever opens it | CreateTimeEvent("homestead_station") L94 | - |
| `station_wrapper:net_destroy` | 97-104 | (no comment) | RemoveTimeEvent("homestead_station") L99 | - |
| `station_wrapper:pickup` | 105-131 | picking the station up hands its storage back first | - | - |

### `00_Core/gamedata/scripts/bind_workshop_furniture.script` (72 lines, 4 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `init` | 5-12 | Enables native engine use callback on placeable workbenches and stashes. | bind_object(hf_workshop_wrapper(obj) L6 | - |
| `hf_workshop_wrapper:__init` | 13-16 | workshop from its radial menu, which calls it with no arguments | - | - |
| `hf_workshop_wrapper:net_destroy` | 17-23 | (no comment) | - | - |
| `hf_workshop_wrapper:pickup` | 24-72 | (no comment) | - | - |

### `00_Core/gamedata/scripts/bind_display_counter.script` (193 lines, 15 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `get_data` | 11-14 | (no comment) | - | - |
| `set_data` | 15-18 | (no comment) | - | - |
| `get_turret_channel_bus` | 19-23 | (no comment) | - | - |
| `ensure_defaults` | 24-32 | (no comment) | - | - |
| `anim_name_for_channel` | 33-36 | (no comment) | - | - |
| `digit_texture` | 37-43 | (no comment) | - | - |
| `cycle_display_counter_channel` | 44-66 | (no comment) | - | - |
| `init` | 67-72 | (no comment) | bind_object(display_counter_wrapper(obj) L68 | - |
| `display_counter_wrapper:__init` | 73-84 | (no comment) | - | - |
| `display_counter_wrapper:apply_channel_animation` | 85-94 | (no comment) | - | - |
| `display_counter_wrapper:apply_display_number` | 95-130 | Generic 2-digit display path for future channel value mirroring (e.g. ammo). | - | - |
| `display_counter_wrapper:apply_display_for_channel` | 131-135 | (no comment) | - | - |
| `display_counter_wrapper:update` | 136-170 | (no comment) | - | - |
| `display_counter_wrapper:play_switch_sound` | 171-185 | (no comment) | - | - |
| `display_counter_wrapper:net_destroy` | 186-193 | (no comment) | - | - |

### `00_Core/gamedata/scripts/bind_alarm_system.script` (287 lines, 12 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `toggle_alarm_system` | 24-33 | (no comment) | - | - |
| `init` | 34-41 | ------------------------------------------------------------------------------ | bind_object(alarm_system_wrapper(obj) L35 | - |
| `get_bone_forward` | 42-59 | ------------------------------------------------------------------------------ | - | - |
| `get_target_center` | 60-72 | (no comment) | - | - |
| `is_in_front_of_bone` | 73-88 | (no comment) | - | - |
| `has_clear_los` | 89-124 | (no comment) | - | - |
| `is_enemy_stalker_to_actor` | 125-151 | (no comment) | - | - |
| `alarm_has_targets` | 152-192 | the alarm item itself behaves. | - | - |
| `alarm_sound_base` | 193-196 | Standard Anomaly installs rely on base Hideout Gadgets' alarm_system_sounds. | - | - |
| `alarm_system_wrapper:__init` | 197-212 | (no comment) | - | - |
| `alarm_system_wrapper:update` | 213-275 | ------------------------------------------------------------------------------ | - | - |
| `alarm_system_wrapper:net_destroy` | 276-287 | ------------------------------------------------------------------------------ | - | - |

### `00_Core/gamedata/scripts/bind_alarm_system_pda.script` (273 lines, 10 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `toggle_alarm_system_pda` | 24-40 | (no comment) | - | - |
| `init` | 41-48 | ------------------------------------------------------------------------------ | bind_object(alarm_system_pda_wrapper(obj) L42 | - |
| `get_bone_forward` | 49-66 | ------------------------------------------------------------------------------ | - | - |
| `get_target_center` | 67-79 | (no comment) | - | - |
| `is_in_front_of_bone` | 80-95 | (no comment) | - | - |
| `has_clear_los` | 96-137 | (no comment) | - | - |
| `alarm_has_targets` | 138-183 | loaded yet (X-Ray loads scripts lazily on first reference). | - | - |
| `alarm_system_pda_wrapper:__init` | 184-200 | (no comment) | - | - |
| `alarm_system_pda_wrapper:update` | 201-269 | ------------------------------------------------------------------------------ | - | - |
| `alarm_system_pda_wrapper:net_destroy` | 270-273 | (no comment) | - | - |


## Turrets

### `00_Core/gamedata/scripts/bind_pistol_turret.script` (1239 lines, 56 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `hf_get_data` | 88-91 | ------------------------------------------------------------------------------ | - | - |
| `hf_ensure_defaults` | 92-114 | (no comment) | - | - |
| `hf_set` | 115-118 | (no comment) | - | - |
| `get_turret_channel_bus` | 119-123 | (no comment) | - | - |
| `toggle_pistol_turret` | 124-131 | (no comment) | - | - |
| `get_obj_by_id_safe` | 132-138 | ------------------------------------------------------------------------------ | - | - |
| `can_check_relation` | 139-158 | (no comment) | - | - |
| `has_clear_shot` | 159-204 | (no comment) | - | - |
| `build_pitch_bones` | 205-223 | (no comment) | - | - |
| `get_muzzle_pos_dir` | 224-236 | (no comment) | - | - |
| `call_add_bullet` | 237-243 | (no comment) | - | - |
| `clamp` | 244-249 | (no comment) | - | - |
| `wrap_deg_180` | 250-255 | (no comment) | - | - |
| `snap_deg` | 256-259 | (no comment) | - | - |
| `fbox_get_min_max` | 260-271 | (no comment) | - | - |
| `step_towards_yaw` | 272-279 | (no comment) | - | - |
| `step_towards_pitch` | 280-287 | (no comment) | - | - |
| `apply_yaw_step_budget` | 288-301 | (no comment) | - | - |
| `apply_pitch_step_budget` | 302-315 | (no comment) | - | - |
| `yaw_idle_anim_name` | 316-324 | (no comment) | - | - |
| `pitch_deg_to_index` | 325-332 | (no comment) | - | - |
| `hide_all_pitch_bones` | 333-338 | (no comment) | - | - |
| `set_pitch_mesh` | 339-350 | (no comment) | - | - |
| `play_cycle_once` | 351-359 | (no comment) | - | - |
| `yaw_wrap_and_clamp` | 360-367 | (no comment) | - | - |
| `turret_sync_mag` | 368-374 | ------------------------------------------------------------------------------ | - | - |
| `turret_set_mag` | 375-381 | (no comment) | - | - |
| `turret_has_ammo` | 382-385 | (no comment) | - | - |
| `turret_mag_push` | 386-403 | (no comment) | - | - |
| `turret_mag_pop` | 404-417 | (no comment) | - | - |
| `update_motor_sound` | 418-456 | ------------------------------------------------------------------------------ | - | - |
| `idle_update` | 457-519 | ------------------------------------------------------------------------------ | - | - |
| `get_bbox_height` | 520-535 | ------------------------------------------------------------------------------ | - | - |
| `get_target_aim_pos` | 536-569 | (no comment) | - | - |
| `turret_target_visible` | 570-580 | (no comment) | - | - |
| `get_bone_axis` | 581-592 | (no comment) | - | - |
| `capture_yaw_basis` | 593-615 | (no comment) | - | - |
| `compute_desired_yaw_deg` | 616-639 | (no comment) | - | - |
| `compute_desired_pitch_deg` | 640-677 | (no comment) | - | - |
| `is_enemy_to_actor` | 678-689 | (no comment) | - | - |
| `is_valid_target` | 690-725 | (no comment) | - | - |
| `rebuild_hostile_cache` | 726-738 | (no comment) | - | - |
| `find_best_target_cached` | 739-791 | The cached hostiles within max_radius, best score (least turning, then nearest) first. | - | - |
| `pistol_turret_wrapper:__init` | 792-857 | (no comment) | - | - |
| `pistol_turret_wrapper:get_mag_count` | 858-861 | (no comment) | - | - |
| `pistol_turret_wrapper:mag_push` | 862-865 | (no comment) | - | - |
| `pistol_turret_wrapper:get_channel` | 866-874 | (no comment) | - | - |
| `pistol_turret_wrapper:set_channel` | 875-883 | (no comment) | - | - |
| `pistol_turret_wrapper:cycle_channel` | 884-892 | (no comment) | - | - |
| `turret_clear_channel` | 893-905 | (no comment) | - | - |
| `turret_publish_channel` | 906-937 | (no comment) | - | - |
| `pistol_turret_wrapper:update` | 938-1130 | ------------------------------------------------------------------------------ | - | - |
| `pistol_turret_wrapper:fire_once` | 1131-1192 | (no comment) | - | - |
| `pistol_turret_wrapper:pickup` | 1193-1218 | the turret switches offline (the player leaving switch range, a load, a sleep). | - | - |
| `pistol_turret_wrapper:net_destroy` | 1219-1235 | (no comment) | - | - |
| `init` | 1236-1239 | ------------------------------------------------------------------------------ | bind_object(pistol_turret_wrapper(obj) L1237 | - |

### `00_Core/gamedata/scripts/ui_pistol_turret.script` (290 lines, 17 functions)

| Function | Lines | Purpose | Hooks registered | Cfg/MCM keys |
|---|---|---|---|---|
| `UIPistolTurret:__init` | 18-23 | (no comment) | - | - |
| `UIPistolTurret:__finalize` | 24-27 | (no comment) | - | - |
| `UIPistolTurret:InitControls` | 28-61 | (no comment) | - | - |
| `UIPistolTurret:Pickup` | 62-76 | (no comment) | - | - |
| `actor_ammo_count_one` | 77-88 | Count all ammo in inventory for a single section | - | - |
| `actor_remove_ammo_rounds` | 89-128 | Returns the number of rounds actually removed. | - | - |
| `UIPistolTurret:Reload` | 129-203 | (no comment) | - | - |
| `channel_to_text` | 204-210 | (no comment) | - | - |
| `UIPistolTurret:CycleChannel` | 211-219 | (no comment) | - | - |
| `UIPistolTurret:InitCallbacks` | 220-226 | (no comment) | - | - |
| `UIPistolTurret:Initialize` | 227-238 | (no comment) | - | ui_texture |
| `UIPistolTurret:TestAndShow` | 239-245 | (no comment) | - | - |
| `UIPistolTurret:Update` | 246-261 | (no comment) | - | - |
| `UIPistolTurret:OnTrackButton` | 262-264 | (no comment) | - | - |
| `UIPistolTurret:OnKeyboard` | 265-276 | (no comment) | - | - |
| `UIPistolTurret:Close` | 277-283 | (no comment) | - | - |
| `start_dialog` | 284-290 | (no comment) | - | - |


## GAMMA compat

### `02_GAMMA/gamedata/scripts/stalker_camp_builder_gamma_mode.script` (6 lines, 0 functions)

_No `function` definitions; see top-level hooks/cfg above._


## Notes

- `04_HideoutGadgetsGammaPatch/` exists in the tree but contains no `.script` files, so it is not indexed.
- `01_Theme_Vanilla/.../ui_stalker_camp_builder_theme.script` is a near-duplicate of the `00_Core` copy (both 145 lines); both are indexed.
- `stalker_camp_builder.script` defines bare `function name()` helpers and `stalker_camp_builder.name()` methods; both forms are listed under the same file.
- Spot-checked against source: `process_medic_job` (jobs 1984), `hf_on_furniture_place` (core 3249), `save_state` (core 3607), `npc_on_death_callback` (core 5573) and its `homestead_respawn_settler` CreateTimeEvent (core 5598).
