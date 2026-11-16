-- Regression test suite for Area 2 bugfixes & perf improvements:
--   BUG 1: _expeditions.script loot_and_clear_stash partial uses & partial ammo elapsed
--   BUG 2: _expeditions.script homonym survivor lookup/cleanup isolation by numeric npc_id
--   BUG 3: _expeditions.script / _jobs.script utils_obj.switch_online level guard
--   BUG 7: _npc.script convert_settler_to_companion_squad actual_sq vs home_sq cleanup & adoption
--   BUG 8: _recruit.script recruit_npc_to_camp backdated job_start_time on paused restore
--   PERF 1: _expeditions.script get_level_marked_stashes level-first candidate filter
--
-- Run: lua tools/tests/test_expeditions.lua

local fails = 0
local checks = 0
local function check(cond, msg)
    checks = checks + 1
    if not cond then
        fails = fails + 1
        print("FAIL: " .. tostring(msg))
    end
end
local function eq(a, b, msg)
    check(a == b, string.format("%s (got %s, want %s)", tostring(msg), tostring(a), tostring(b)))
end

local function slurp(path)
    local f = assert(io.open(path, "rb"))
    local s = f:read("*a")
    f:close()
    return (s:gsub("\r", ""))
end

local exp_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_expeditions.script")
local jobs_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
local npc_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_npc.script")
local recruit_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_recruit.script")

-- Shared minimal engine stubs
local CURRENT_LEVEL = "l01_escape"
local switch_online_calls = {}
local sim_online_calls = {}
local sim_offline_calls = {}
local released_ids = {}
local spot_checks = {}
local created_squads = {}
local mock_se_objs = {}
local mock_cl_objs = {}
local mock_children = {}
local mock_stpk_item = {}
local mock_stpk_ammo = {}
local mock_stpk_wpn = {}
local mock_parts = {}
local mock_sections = {}
local cur_tg = 100000
local cur_game_sec = 500000

_G.vector = function()
    return { x = 0, y = 0, z = 0, set = function(self) return self end, distance_to = function() return 10 end }
end
_G.time_global = function() return cur_tg end
_G.IsStalker = function() return true end
_G.IsItem = function(kind, sec)
    if kind == "ammo" then return sec and sec:find("^ammo_") ~= nil end
    return false
end
_G.game = { translate_string = function(s) return s end }
_G.ui_item = { get_sec_name = function(s) return s end }
_G.news_manager = { send_tip = function() end }
_G.db = { actor = {}, storage = {} }
_G.clsid = { inventory_box = 10, inventory_box_s = 11 }
_G.axr_companions = { companion_squads = {} }
_G.SIMBOARD = { squads = {}, assign_squad_to_smart = function() end }
_G.utils_obj = {
    switch_online = function(id)
        switch_online_calls[#switch_online_calls + 1] = id
    end,
}
_G.utils_stpk = {
    get_item_data = function(se) return mock_stpk_item[se.id] or { condition = 1.0 } end,
    get_ammo_data = function(se) return mock_stpk_ammo[se.id] or { condition = 1.0 } end,
    get_weapon_data = function(se) return mock_stpk_wpn[se.id] or { condition = 1.0 } end,
}
_G.item_parts = {
    get_parts_con = function(_, id) return mock_parts[id] end,
}
_G.ini_sys = {
    section_exist = function(_, sec) return mock_sections[sec] ~= nil end,
    r_float_ex = function(_, sec, key)
        local m = mock_sections[sec]
        return m and m[key] or nil
    end,
    r_string_ex = function(_, sec, key)
        local m = mock_sections[sec]
        return m and m[key] or nil
    end,
    r_bool_ex = function(_, sec, key)
        local m = mock_sections[sec]
        return m and m[key] or false
    end,
}
_G.alife_object = function(id) return mock_se_objs[id] end
_G.alife_release = function(se)
    if se then
        released_ids[se.id] = true
        mock_se_objs[se.id] = nil
    end
end
_G.game_graph = function()
    return {
        vertex = function(_, gvid)
            return { level_id = function() return (gvid == 200) and 2 or 1 end }
        end,
    }
end
_G.level = {
    name = function() return CURRENT_LEVEL end,
    object_by_id = function(id) return mock_cl_objs[id] end,
    map_has_object_spot = function(id, spot)
        spot_checks[id] = (spot_checks[id] or 0) + 1
        local se = mock_se_objs[id]
        return se and se.spot == spot and 1 or 0
    end,
    map_remove_object_spot = function() end,
    vertex_position = function() return _G.vector() end,
}

local sim_obj = {
    object = function(_, id) return mock_se_objs[id] end,
    level_name = function(_, lid) return (lid == 2) and "l02_garbage" or "l01_escape" end,
    get_children = function(_, se_parent)
        local list = mock_children[se_parent.id] or {}
        local idx = 0
        return function()
            idx = idx + 1
            return list[idx]
        end
    end,
    set_switch_online = function(_, id, val)
        sim_online_calls[#sim_online_calls + 1] = { id = id, val = val }
    end,
    set_switch_offline = function(_, id, val)
        sim_offline_calls[#sim_offline_calls + 1] = { id = id, val = val }
    end,
    create = function(_, sec, pos, lvid, gvid)
        local sq = {
            id = 9000 + #created_squads + 1,
            members = {},
            npc_count = function(self)
                local c = 0
                for _ in pairs(self.members) do c = c + 1 end
                return c
            end,
            register_member = function(self, id)
                self.members[id] = true
                if mock_se_objs[id] then mock_se_objs[id].group_id = self.id end
            end,
            unregister_member = function(self, id)
                self.members[id] = nil
                if mock_se_objs[id] then mock_se_objs[id].group_id = 65535 end
            end,
        }
        created_squads[#created_squads + 1] = sq
        return sq
    end,
}
_G.alife = function() return sim_obj end
_G.get_object_squad = function(se_npc)
    return se_npc and se_npc.group_id and mock_se_objs[se_npc.group_id] or nil
end

_G.stalker_camp_builder = {
    cfg = { max_survivors_player_camp = 15, max_survivors_per_camp = 15, enable_surplus_cap = true },
    defaults = {},
    active_camps = {},
    active_stash_expeditions = {},
    non_settler_cache = {},
    camp_box_id_cache = {},
    CAMP_BOX_ID_CACHE_TTL_MS = 10000,
    game_sec = function() return cur_game_sec end,
    time_factor = function() return 6 end,
    game_timer_scale = function() return 1 end,
    camp_send_tip = function() end,
    add_radio_feed_entry = function() end,
    get_camp_label = function() return "Camp" end,
    get_specialization_mult = function() return 1.0 end,
    safe_alife_object = function(id) return mock_se_objs[id] end,
    forget_binder_squad = function() end,
    is_settlement_structure_or_hub = function() return false end,
    is_quest_or_task_stash = function() return false end,
}

assert(loadstring(exp_src, "@stalker_camp_builder_expeditions.script"))()
assert(loadstring(jobs_src, "@stalker_camp_builder_jobs.script"))()
local sb = _G.stalker_camp_builder
sb.is_settlement_structure_or_hub = function() return false end
sb.is_quest_or_task_stash = function() return false end
sb.survivor_se = function(n_id) return mock_se_objs[tonumber(n_id) or n_id] end

-- 1. BUG 1: loot_and_clear_stash preserves partial uses + partial ammo elapsed without altering < 0.99 guard
do
    mock_sections = {
        medkit = { max_uses = 3 },
        ammo_5_45 = { box_size = 30 },
        wpn_ak74 = { ammo_class = "ammo_5_45" },
        wpn_pm = { ammo_class = "ammo_9x18" },
    }
    -- Note ammo section starts with ammo_ for IsItem("ammo", sec)
    mock_sections["ammo_5.45x39_fmj"] = { box_size = 30 }

    local deposits = {}
    sb.deposit_item_to_camp = function(hub_id, camp, sec, is_y, tier, cond, parts, uses, drop, ammo)
        deposits[#deposits + 1] = {
            sec = sec, cond = cond, parts = parts, uses = uses, drop = drop, ammo = ammo
        }
        return 1
    end

    local stash_id = 500
    mock_se_objs[stash_id] = { id = stash_id, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1 }
    mock_se_objs[1] = { id = 1, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1 }
    mock_children[stash_id] = { 501, 502, 503, 504 }

    -- 501: online multi-use medkit with 2/3 uses and condition ~0.66
    mock_se_objs[501] = { id = 501, parent_id = stash_id, section_name = function() return "medkit" end }
    mock_cl_objs[501] = { get_remaining_uses = function() return 2 end }
    mock_stpk_item[501] = { condition = 0.66 }

    -- 502: offline partial ammo box with 11 rounds out of 30
    mock_se_objs[502] = { id = 502, parent_id = stash_id, section_name = function() return "ammo_5.45x39_fmj" end }
    mock_stpk_ammo[502] = { ammo_left = 11 }
    mock_stpk_item[502] = { condition = 1.0 }

    -- 503: damaged weapon (< 0.99 cond) retains cond & parts
    mock_se_objs[503] = { id = 503, parent_id = stash_id, section_name = function() return "wpn_ak74" end }
    mock_stpk_wpn[503] = { condition = 0.42 }
    mock_parts[503] = { barrel = 40 }

    -- 504: pristine weapon (>= 0.99 cond) preserves DANZY EDIT < 0.99 guard (cond stays nil)
    mock_se_objs[504] = { id = 504, parent_id = stash_id, section_name = function() return "wpn_pm" end }
    mock_stpk_wpn[504] = { condition = 0.995 }
    mock_parts[504] = { barrel = 100 }

    local loot_fn = exp_src:match("(local function loot_and_clear_stash.-\nend)")
    -- Use public recall/complete via deposit_expedition_haul or test loot_and_clear_stash directly via complete/process
    -- Execute complete-like path by exposing loot_and_clear_stash helper via loadstring on file body slice
    local helper_extra = assert(exp_src:match("(local function extract_stash_child_extras.-\nend)"), "extract helper")
    local env_b1 = setmetatable({
        mfloor = math.floor, pairs_ = pairs, ipairs_ = ipairs, tostr = tostring,
        tonum = tonumber, sformat = string.format, alife = _G.alife,
        treasure_manager = { caches = {} },
        is_player_stash = function() return false end,
        is_stash_box = function() return true end,
        gamma_map_tiers = { l01_escape = 2 },
        generate_gamma_stash_loot = function() return {} end,
    }, { __index = _G })
    local f_extra = setfenv(loadstring(helper_extra .. "\n" .. loot_fn .. "\nreturn loot_and_clear_stash"), env_b1)()

    local exp_loot = { npc_id = 101, target_level = "l01_escape", haul = {} }
    f_extra(stash_id, exp_loot)
    local haul = exp_loot.haul
    eq(#haul, 4, "BUG 1: looted 4 stash items")
    eq(haul[1].sec, "medkit", "BUG 1: item 1 medkit")
    eq(haul[1].uses, 2, "BUG 1: medkit uses=2 preserved")
    eq(haul[2].sec, "ammo_5.45x39_fmj", "BUG 1: item 2 ammo")
    eq(haul[2].ammo, 11, "BUG 1: partial ammo=11 preserved")
    eq(haul[3].sec, "wpn_ak74", "BUG 1: item 3 damaged weapon")
    eq(haul[3].cond, 0.42, "BUG 1: damaged weapon cond preserved")
    check(haul[3].parts and haul[3].parts.barrel == 40, "BUG 1: damaged weapon parts preserved")
    eq(haul[4].cond, nil, "BUG 1: >= 0.99 condition guard kept intact")
    eq(haul[4].parts, nil, "BUG 1: pristine weapon carries no parts")

    -- Recall expedition passes uses + ammo_elapsed (param 10) to deposit_item_to_camp
    sb.active_camps = {
        [1] = {
            hub_id = 1,
            level = "l01_escape",
            survivors = { [101] = { name = "Vasya", job = "scavenge", on_expedition = true } },
        },
    }
    mock_se_objs[101] = { id = 101, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1, can_switch_online = function() return true end }
    sb.active_stash_expeditions = {
        [stash_id] = { stash_id = stash_id, hub_id = 1, npc_id = 101, survivor_name = "Vasya", haul = haul },
    }
    eq(sb.recall_scavenger_expedition(stash_id), true, "BUG 1: recall expedition succeeds")
    eq(#deposits, 4, "BUG 1: recall deposited all 4 items")
    eq(deposits[1].uses, 2, "BUG 1: deposit_item_to_camp got uses=2")
    eq(deposits[2].ammo, 11, "BUG 1: deposit_item_to_camp got ammo_elapsed=11")
    mock_cl_objs = {}
end

-- 2. BUG 2: homonym settlers ("Vasya") with distinct npc_ids must never alias or clear each other
do
    sb.active_camps = {
        [1] = {
            hub_id = 1,
            level = "l01_escape",
            survivors = {
                [101] = { name = "Vasya", job = "scavenge", on_expedition = true },
            },
        },
        [2] = {
            hub_id = 2,
            level = "l02_garbage",
            survivors = {
                [202] = { name = "Vasya", job = "scavenge", on_expedition = true },
            },
        },
    }
    sb.active_stash_expeditions = {
        [700] = { stash_id = 700, hub_id = 1, npc_id = 101, survivor_name = "Vasya" },
    }
    local e101 = sb.get_scavenger_expedition_for_survivor(sb.active_camps[1].survivors[101], 101)
    local e202 = sb.get_scavenger_expedition_for_survivor(sb.active_camps[2].survivors[202], 202)
    eq(e101 and e101.npc_id, 101, "BUG 2: npc 101 matches own expedition")
    eq(e202, nil, "BUG 2: homonym npc 202 does NOT match 101 expedition")

    -- cleanup_expedition (invoked when 700 completes/cancels) must only clear npc 101
    local clean_src = assert(exp_src:match("(local function cleanup_expedition.-\nend)"), "cleanup_expedition")
    local env_c = setmetatable({ pairs_ = pairs, tonum = tonumber, tostr = tostring }, { __index = _G })
    local f_clean = setfenv(loadstring(clean_src .. "\nreturn cleanup_expedition"), env_c)()
    f_clean(700)
    eq(sb.active_camps[1].survivors[101].on_expedition, nil, "BUG 2: npc 101 expedition flag cleared")
    eq(sb.active_camps[2].survivors[202].on_expedition, true, "BUG 2: homonym npc 202 on_expedition preserved")
end

-- 3. BUG 3: utils_obj.switch_online is guarded by same-level check across _expeditions and _jobs
do
    CURRENT_LEVEL = "l01_escape"
    switch_online_calls = {}
    sim_online_calls = {}
    sim_offline_calls = {}

    mock_se_objs[2] = { id = 2, position = _G.vector(), m_level_vertex_id = 2, m_game_vertex_id = 200 }
    mock_se_objs[301] = {
        id = 301, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1,
        can_switch_online = function() return false end,
    }
    sb.active_camps = {
        [2] = {
            hub_id = 2,
            level = "l02_garbage", -- off-level from actor ("l01_escape")
            survivors = {
                [301] = { name = "Stalker", job = "scavenge", on_expedition = true },
            },
        },
    }
    sb.active_stash_expeditions = {}
    -- Orphaned on_expedition cleanup in get_available_scavengers on off-level camp
    sb.get_available_scavengers()
    eq(#switch_online_calls, 0, "BUG 3: get_available_scavengers skips utils_obj.switch_online off-level")
    check(#sim_online_calls >= 1 and sim_online_calls[1].id == 301 and sim_online_calls[1].val == true,
        "BUG 3: get_available_scavengers sets set_switch_online(true) off-level")
    check(#sim_offline_calls >= 1 and sim_offline_calls[1].id == 301 and sim_offline_calls[1].val == true,
        "BUG 3: get_available_scavengers sets set_switch_offline(true) off-level")

    -- set_survivor_job on off-level camp must also avoid utils_obj.switch_online
    switch_online_calls = {}
    sim_online_calls = {}
    sb.set_survivor_job(301, "guard")
    eq(#switch_online_calls, 0, "BUG 3: set_survivor_job skips utils_obj.switch_online off-level")
    check(#sim_online_calls >= 1, "BUG 3: set_survivor_job uses set_switch_online off-level")

    -- Same-level camp MUST still call utils_obj.switch_online
    switch_online_calls = {}
    sb.active_camps[1] = {
        hub_id = 1,
        level = "l01_escape",
        survivors = { [302] = { name = "Local", job = "scavenge", on_expedition = true } },
    }
    mock_se_objs[302] = {
        id = 302, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1,
        can_switch_online = function() return false end,
    }
    sb.set_survivor_job(302, "guard")
    check(#switch_online_calls >= 1 and switch_online_calls[1] == 302, "BUG 3: same-level camp still calls switch_online")
end

-- 4. PERF 1: get_level_marked_stashes filters by target_level before spot/settlement/quest checks
do
    spot_checks = {}
    local clsid_checks = {}
    _G.server_objects_registry = {
        [801] = { id = 801, m_game_vertex_id = 1, spot = "treasure", clsid = function() clsid_checks[801] = (clsid_checks[801] or 0) + 1; return 10 end },
        [802] = { id = 802, m_game_vertex_id = 200, spot = "treasure", clsid = function() clsid_checks[802] = (clsid_checks[802] or 0) + 1; return 10 end },
    }
    mock_se_objs[801] = _G.server_objects_registry[801]
    mock_se_objs[802] = _G.server_objects_registry[802]
    local found = sb.get_level_marked_stashes("l01_escape")
    eq(#found, 1, "PERF 1: returned only target-level marked stash")
    eq(found[1], 801, "PERF 1: stash 801 matched")
    eq(spot_checks[801], 1, "PERF 1: target-level stash checked spot once")
    eq(spot_checks[802], nil, "PERF 1: off-level stash skipped before spot check")
    eq(clsid_checks[802], nil, "PERF 1: off-level stash skipped before clsid/box check")
    _G.server_objects_registry = nil
end

-- 5. BUG 7: convert_settler_to_companion_squad unregisters from actual_sq even when home_sq differs, and registers solo home_sq
do
    local conv_src = assert(npc_src:match("(function stalker_camp_builder%.convert_settler_to_companion_squad.-\nend)"), "convert fn")
    local settler_home_squads = {}
    local env_npc = setmetatable({ settler_home_squads = settler_home_squads }, { __index = _G })
    local f_conv = setfenv(loadstring(conv_src .. "\nreturn stalker_camp_builder.convert_settler_to_companion_squad"), env_npc)()

    -- Case A: settler in 2-member actual_sq (400), cached home_sq (401) is ALSO overloaded (2 members)
    local unreg_actual = false
    local sq_actual = {
        id = 400,
        members = { [101] = true, [102] = true },
        npc_count = function() return 2 end,
        unregister_member = function(self, id)
            unreg_actual = (id == 101)
            self.members[id] = nil
        end,
    }
    local sq_home = {
        id = 401,
        npc_count = function() return 2 end,
        unregister_member = function() end,
    }
    mock_se_objs[400] = sq_actual
    mock_se_objs[401] = sq_home
    mock_se_objs[101] = { id = 101, group_id = 400, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1 }
    settler_home_squads[101] = 401
    created_squads = {}
    local res_sq = f_conv(101, nil)
    eq(unreg_actual, true, "BUG 7a: unregistered from actual_sq despite mismatched home_sq")
    eq(#created_squads, 1, "BUG 7a: created dedicated companion squad")
    eq(res_sq.id, created_squads[1].id, "BUG 7a: returned dedicated squad")
    eq(mock_se_objs[101].group_id, created_squads[1].id, "BUG 7a: registered into dedicated squad")

    -- Case B: settler in actual_sq (402, solo or shared) while empty cached home_sq (403) exists -> unregister 402 & register into 403
    local unreg_402 = false
    local reg_403 = false
    mock_se_objs[402] = {
        id = 402, npc_count = function() return 1 end,
        unregister_member = function(_, id) unreg_402 = (id == 102) end,
    }
    mock_se_objs[403] = {
        id = 403, npc_count = function() return 0 end,
        register_member = function(_, id) reg_403 = (id == 102); mock_se_objs[id].group_id = 403 end,
    }
    mock_se_objs[102] = { id = 102, group_id = 402, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1 }
    settler_home_squads[102] = 403
    local res_b = f_conv(102, nil)
    eq(unreg_402, true, "BUG 7b: unregistered from stale actual_sq when adopting empty home_sq")
    eq(reg_403, true, "BUG 7b: registered settler into adopted empty home_sq")
    eq(res_b.id, 403, "BUG 7b: reused empty home_sq")
end

-- 6. BUG 8: recruit_npc_to_camp backdates job_start_time alongside job_start_realtime on restore
do
    local rec_src = assert(recruit_src:match("(function stalker_camp_builder%.recruit_npc_to_camp.-\nend)"), "recruit fn")
    local env_rec = setmetatable({
        pda_recruit_target = nil,
        settler_home_squads = {},
        sformat = string.format,
        npc_squad = nil,
        mfloor = math.floor,
    }, { __index = _G })
    -- Only check the restored timestamps in recruit_npc_to_camp
    cur_tg = 1000000
    cur_game_sec = 500000
    sb.get_job_rt_interval = function() return 300 end
    sb.get_time_of_day_mult = function() return 1.0 end
    sb.get_camp_max_survivors = function() return 15 end
    sb.register_settler_home_squad = function() end
    sb.apply_settler_npc_role = function() end
    sb.ensure_companion_dismissed = function() end
    sb.refugee_ids = {}
    sb.settler_lookup = {}
    sb.is_companion = function() return false end
    sb.can_settler_safely_live_in_camp = function() return true end
    sb.release_npc_from_squad_and_smart = function() end
    sb.set_camp_settler_relations = function() end
    sb.teleport_npc_to_camp_hub = function() end
    env_rec.alife_storage_manager = { get_state = function() return {} end }
    env_rec.actor_menu = { set_msg = function() end }
    sb.active_camps = {
        [1] = {
            hub_id = 1,
            level = "l01_escape",
            survivors = {
                [505] = {
                    name = "Returning",
                    job = "companion",
                    is_companion = true,
                    paused_job = "cook",
                    paused_xp = 12,
                    paused_tier = 1,
                    paused_job_progress = 0.5,
                },
            },
        },
    }
    local fake_npc = {
        id = function() return 505 end,
        character_name = function() return "Returning" end,
        character_community = function() return "stalker" end,
        section = function() return "sim_default_stalker_1" end,
        get_visual_name = function() return "actors\\stalker_neutral\\stalker_neutral_1" end,
        character_icon = function() return "ui_inGame2_Neutral_1" end,
        has_info = function() return false end,
        disable_info_portion = function() end,
    }
    mock_se_objs[1] = { id = 1, position = _G.vector(), m_level_vertex_id = 1, m_game_vertex_id = 1 }
    mock_se_objs[505] = { id = 505, group_id = nil }
    local f_rec = setfenv(loadstring(rec_src .. "\nreturn stalker_camp_builder.recruit_npc_to_camp"), env_rec)()
    f_rec(_G.db.actor, fake_npc, 1)
    local restored = sb.active_camps[1].survivors[505]
    eq(restored.job, "cook", "BUG 8: restored paused job")
    -- 0.5 * 300s = 150 real sec; tf = 6 -> 900 game sec backdated
    eq(restored.job_start_realtime, cur_tg - 150 * 1000, "BUG 8: job_start_realtime backdated by 150s")
    eq(restored.job_start_time, cur_game_sec - 150 * 6, "BUG 8: job_start_time backdated by 900 game sec")
end

if fails > 0 then
    print(string.format("%d/%d checks FAILED", fails, checks))
    os.exit(1)
end
print(string.format("All %d expedition, NPC squad & recruit checks passed!", checks))
