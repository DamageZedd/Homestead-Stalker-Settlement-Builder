-- Regression test suite for v1.4.1 closed-loop production chains & default settler cap (14 roles)
-- Run: lua tools/tests/test_production_chains.lua

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

-- 1. Verify settler population cap defaults & MCM range (0 to 28, default 14 = 1 per job role)
local main_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder.script")
local mcm_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_mcm.script")
local jobs_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
local pda_src = slurp("00_Core/gamedata/scripts/ui_stalker_camp_builder_pda.script")

local job_list_match = pda_src:match('local SV_JOB_ORDER = (%b{})')
assert(job_list_match, "SV_JOB_ORDER not found in PDA script")
local sv_jobs = assert(loadstring("return " .. job_list_match))()
-- SV_JOB_ORDER has "idle" + 14 active roles = 15 entries
eq(#sv_jobs - 1, 14, "active settlement job count")

local def_block = main_src:match("local defaults = (%b{})\nstalker_camp_builder%.defaults = defaults")
assert(def_block, "defaults table not found")
local D = assert(loadstring("return " .. def_block))()
eq(D.max_survivors_player_camp, 14, "defaults.max_survivors_player_camp")
eq(D.max_survivors_per_camp, 14, "defaults.max_survivors_per_camp")

local mcm_line = mcm_src:match('{ id = "max_survivors_player_camp"[^\n]+}')
assert(mcm_line, "max_survivors_player_camp MCM entry not found")
eq(tonumber(mcm_line:match("min = (%d+)")), 0, "MCM max_survivors_player_camp min")
eq(tonumber(mcm_line:match("max = (%d+)")), 28, "MCM max_survivors_player_camp max")
eq(tonumber(mcm_line:match("def = (%d+)")), 14, "MCM max_survivors_player_camp def")

-- 2. Set up lightweight X-Ray environment to execute closed-loop production chains in stalker_camp_builder_jobs.script
_G.vector = function()
    return { x = 0, y = 0, z = 0, set = function(self) return self end, distance_to = function() return 5 end }
end
_G.time_global = function() return 100000 end
_G.game = { translate_string = function(s) return s end }
_G.ui_item = { get_sec_name = function(s) return s end }
_G.db = { actor = {} }

local existing_sections = {
    prt_i_wood = true, prt_i_scrap = true, prt_i_fasteners = true, prt_i_cloth = true, prt_i_copper = true,
    charcoal = true, kerosene = true, vodka = true, alcohol = true, flask = true, water_drink = true,
    bandage = true, medkit = true, medkit_army = true, stimpack = true, akvatab = true, antirad_kalium = true,
    tushonka = true, conserva = true, bread = true, homestead_potato = true, homestead_grain = true,
    mutant_part_boar_chop = true, meat_boar = true, meat_boar_b = true, meat_boar_a = true,
    hide_boar = true, hide_pseudodog = true, hide_flesh = true, hide_dog = true, hide_chimera = true, hide_bloodsucker = true, hide_burer = true,
    mutant_part_boar_leg = true, mutant_part_flesh_eye = true, mutant_part_dog_tail = true,
    mutant_part_psevdodog_tail = true, mutant_part_krovosos_jaw = true, mutant_part_snork_leg = true,
    mutant_part_chimera_claw = true, mutant_part_cat_tail = true, mutant_part_burer_hand = true,
    ammo_9x18_fmj = true, ammo_9x19_fmj = true,
}

_G.ini_sys = {
    section_exist = function(_, sec) return existing_sections[sec] == true end,
    line_exist = function(_, sec, _) return existing_sections[sec] == true end,
    r_float_ex = function(_, _, k)
        if k == "inv_weight" then return 0.2 end
        return 1
    end,
    r_string_ex = function(_, sec, _) return sec end,
    r_bool_ex = function() return false end,
}

local next_id = 500
local server_objects = {}
local camp_inv = {}
local stall_inv = {}

local function reset_env(items)
    server_objects = {
        [1] = { id = 1, position = vector(), m_level_vertex_id = 1, m_game_vertex_id = 1, section_name = function() return "camp_hub" end },
        [10] = { id = 10, position = vector(), m_level_vertex_id = 1, m_game_vertex_id = 1, section_name = function() return "homestead_field_kitchen" end },
        [20] = { id = 20, position = vector(), m_level_vertex_id = 1, m_game_vertex_id = 1, section_name = function() return "market_stash" end },
    }
    camp_inv = {}
    stall_inv = {}
    for _, sec in ipairs(items or {}) do
        next_id = next_id + 1
        local id = next_id
        local obj = { id = id, parent_id = 1, position = vector(), m_level_vertex_id = 1, m_game_vertex_id = 1, section_name = function() return sec end }
        server_objects[id] = obj
        camp_inv[#camp_inv + 1] = { id = id, sec = sec, uses = 1, cond = 1.0 }
    end
end

_G.alife_object = function(id) return server_objects[id] end
_G.alife_release = function(se_obj)
    if not se_obj then return end
    server_objects[se_obj.id] = nil
    for i = #camp_inv, 1, -1 do
        if camp_inv[i].id == se_obj.id then
            table.remove(camp_inv, i)
            break
        end
    end
end
_G.alife = function()
    return {
        object = function(_, id) return server_objects[id] end,
        create = function(_, sec, pos, lvid, gvi, parent_id)
            next_id = next_id + 1
            local obj = { id = next_id, parent_id = parent_id, position = pos or vector(), m_level_vertex_id = lvid or 0, m_game_vertex_id = gvi or 0, section_name = function() return sec end }
            server_objects[next_id] = obj
            if parent_id == 20 then
                stall_inv[#stall_inv + 1] = sec
            else
                camp_inv[#camp_inv + 1] = { id = next_id, sec = sec, uses = 1, cond = 1.0 }
            end
            return obj
        end,
    }
end
_G.level = {
    object_by_id = function(_)
        return { character_name = function() return "Tester" end, alive = function() return true end }
    end
}
_G.homestead_market_stall = {
    find_stash = function(sid) return sid == 30 and 20 or nil end
}

_G.stalker_camp_builder = {
    cfg = {
        enable_surplus_cap = true,
        craft_output_multiplier = 1,
        cook_requires_fuel = true,
        cook_output_tier = 2,
        yield_scrap_min = 3,
        yield_scrap_max = 3,
        yield_fasteners_min = 1,
        yield_fasteners_max = 1,
        hunter_min_meat = 1,
        hunter_max_meat = 1,
        water_filters = { water_filter = true },
    },
    defaults = {},
    camp_box_id_cache = {},
    CAMP_BOX_ID_CACHE_TTL_MS = 10000,
    camp_send_tip = function() end,
    game_sec = function() return 100000 end,
    time_factor = function() return 6 end,
    game_timer_scale = function() return 1 end,
    is_actual_container = function() return true end,
    linked_stash_id = function(id) return id end,
    MEDIC_RARE_BATCH_MAX = 4,
    medic_batch_size = function(want, eth, per)
        local n = math.max(1, math.floor(tonumber(want) or 1))
        if eth and per and per > 0 then
            n = math.min(n, math.max(1, math.floor(eth / per)))
        end
        return n
    end,
    get_auto_sort_target_box = function() return 1 end,
    box_has_room_for = function() return true end,
    get_survivor_tier_mult = function(s) return (s and s.tier and s.tier >= 2) and 1.5 or 1.0 end,
    get_specialization_mult = function() return 1.0 end,
    deposit_item_to_camp = function(_, _, sec)
        _G.alife():create(sec, vector(), 1, 1, 1)
        return 1
    end,
    camp_iterate_inventory = function(_, _, fn)
        for i = 1, #camp_inv do
            local e = camp_inv[i]
            if e and server_objects[e.id] then
                if fn(e.id, e.sec, e.cond, e.uses, server_objects[e.id], 1, nil) then break end
            end
        end
    end,
    camp_count_item = function(_, _, pred, cap)
        local n = 0
        for _, e in ipairs(camp_inv) do
            if pred(e.sec) then
                n = n + (e.uses or 1)
                if cap and n >= cap then return n end
            end
        end
        return n
    end,
    camp_has_item = function(h, c, pred)
        return _G.stalker_camp_builder.camp_count_item(h, c, pred, 1) > 0
    end,
    camp_find_item = function(_, _, pred)
        for _, e in ipairs(camp_inv) do
            if pred(e.sec) then return e.id end
        end
        return nil
    end,
    camp_consume_item = function(_, _, pred)
        for i, e in ipairs(camp_inv) do
            if pred(e.sec) then
                local sec = e.sec
                server_objects[e.id] = nil
                table.remove(camp_inv, i)
                return sec
            end
        end
        return nil
    end,
}

assert(loadstring(jobs_src, "@stalker_camp_builder_jobs.script"))()
local sb = _G.stalker_camp_builder

local function count_sec(sec)
    local n = 0
    for _, e in ipairs(camp_inv) do
        if e.sec == sec then n = n + 1 end
    end
    return n
end

-- Test Chain 1a: Scrapper pelt curing (hide_boar + charcoal -> 2x prt_i_cloth)
do
    reset_env({ "hide_boar", "charcoal" })
    local camp = { hub_id = 1, structures = { [11] = "salvage_table" }, survivors = {} }
    local surv = { name = "Scrapper", job = "scrapper", tier = 2, has_tools = true }
    local ok = sb.process_scrapper_job(101, 1, camp, surv, 1)
    eq(ok, true, "Chain 1a: scrapper job succeeded")
    eq(count_sec("hide_boar"), 0, "Chain 1a: hide_boar consumed")
    eq(count_sec("charcoal"), 0, "Chain 1a: charcoal consumed")
    eq(count_sec("prt_i_cloth"), 2, "Chain 1a: 2x prt_i_cloth produced from pelt curing")
end

-- Test Chain 1b: Scrapper Vanilla fallback (when prt_i_cloth does not exist -> produces bandage)
do
    existing_sections.prt_i_cloth = false
    reset_env({ "hide_boar", "charcoal" })
    local camp = { hub_id = 1, structures = { [11] = "salvage_table" }, survivors = {} }
    local surv = { name = "Scrapper", job = "scrapper", tier = 2 }
    local ok = sb.process_scrapper_job(101, 1, camp, surv, 1)
    eq(ok, true, "Chain 1b: scrapper vanilla fallback succeeded")
    eq(count_sec("bandage"), 2, "Chain 1b: 2x bandage produced when prt_i_cloth is absent")
    existing_sections.prt_i_cloth = true
end

-- Test Chain 2b: Ammo Crafter improvised black powder at ammo_bench (3 charcoal + 1 scrap + 1 vodka -> ammo)
do
    reset_env({ "charcoal", "charcoal", "charcoal", "prt_i_scrap", "vodka" })
    local camp = { hub_id = 1, structures = { [12] = "ammo_bench" }, survivors = {} }
    local surv = { name = "Crafter", job = "craft", tier = 2, craft_order = "pistol" }
    local paused, reason = sb._calc_job_paused_status(surv, camp, 1, nil)
    eq(paused, false, "Chain 2b: ammo crafter not paused when improvised propellant inputs exist (reason=" .. tostring(reason) .. ")")
    local ok = sb.process_ammo_crafting(102, 1, camp, surv, 1)
    eq(ok, true, "Chain 2b: process_ammo_crafting succeeded with improvised black powder")
    eq(count_sec("charcoal"), 0, "Chain 2b: 3x charcoal consumed")
    eq(count_sec("prt_i_scrap"), 0, "Chain 2b: 1x prt_i_scrap consumed")
    eq(count_sec("vodka"), 0, "Chain 2b: 1x vodka consumed")
    check(count_sec("ammo_9x18_fmj") + count_sec("ammo_9x19_fmj") >= 1, "Chain 2b: pistol ammo crafted")
end

-- Test Chain 3: Cook burns charcoal before kerosene, recognizes Field Kitchen, and cans surplus potatoes into tushonka
do
    reset_env({
        "mutant_part_boar_chop", "charcoal", "kerosene", "flask",
        "homestead_potato", "homestead_potato", "homestead_potato", "homestead_potato",
        "homestead_potato", "homestead_potato", "homestead_potato", "homestead_potato"
    })
    local camp = { hub_id = 1, structures = { [10] = "stove", [1] = "fridge" }, survivors = {} }
    local surv = { name = "Cook", job = "cook", tier = 2, cook_mode = "tier2" }
    local ok = sb.process_cook_job(103, 1, camp, surv, 1)
    eq(ok, true, "Chain 3: cook job succeeded at Field Kitchen")
    eq(count_sec("charcoal"), 0, "Chain 3: charcoal burned first")
    eq(count_sec("kerosene"), 1, "Chain 3: kerosene preserved for generator")
    eq(count_sec("homestead_potato"), 6, "Chain 3: 2 surplus potatoes consumed for canning")
    eq(count_sec("tushonka"), 1, "Chain 3: bonus canned tushonka produced")
end

-- Test Chain 4: Medic at Field Infirmary (medstation) upgrades medkit to stimpack using mutant trophy
do
    reset_env({ "vodka", "vodka", "vodka", "vodka", "bandage", "mutant_part_boar_leg" })
    local camp = { hub_id = 1, structures = { [14] = "medstation" }, survivors = {} }
    local surv = { name = "Medic", job = "medic", tier = 2, medic_order = "medkit" }
    local ok = sb.process_medic_job(104, 1, camp, surv)
    eq(ok, true, "Chain 4: medic job succeeded at Field Infirmary")
    eq(count_sec("mutant_part_boar_leg"), 0, "Chain 4: mutant trophy consumed")
    eq(count_sec("stimpack"), 1, "Chain 4: first unit upgraded to stimpack")
end

-- Test Chain 5: Hunter routes surplus pelts/trophies (>= 4 in camp storage) into Market Stall stash
do
    reset_env({
        "hide_boar", "hide_boar", "hide_boar", "hide_boar",
        "mutant_part_boar_leg", "mutant_part_boar_leg", "mutant_part_boar_leg", "mutant_part_boar_leg"
    })
    local camp = { hub_id = 1, structures = { [15] = "hunter_station", [30] = "market_stall" }, survivors = {} }
    math.randomseed(1)
    for _ = 1, 5 do
        sb.spawn_hunted_meat(1, 1.0, 1, camp)
    end
    check(#stall_inv > 0, "Chain 5: surplus pelts/trophies routed into Market Stall stash")
end

if fails > 0 then
    print(string.format("%d/%d checks FAILED", fails, checks))
    os.exit(1)
end
print(string.format("All %d closed-loop production & settler cap checks passed!", checks))
