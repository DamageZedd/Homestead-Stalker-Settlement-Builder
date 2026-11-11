-- Regression test suite for v1.4.1 closed-loop production chains, Chemist role & default settler cap (15 roles)
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

-- 1. Verify settler population cap defaults & MCM range (0 to 30, default 15 = 1 per job role)
local main_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder.script")
local mcm_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_mcm.script")
local jobs_src = slurp("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
local pda_src = slurp("00_Core/gamedata/scripts/ui_stalker_camp_builder_pda.script")

local job_list_match = pda_src:match('local SV_JOB_ORDER = (%b{})')
assert(job_list_match, "SV_JOB_ORDER not found in PDA script")
local sv_jobs = assert(loadstring("return " .. job_list_match))()
-- SV_JOB_ORDER has "idle" + 15 active roles = 16 entries
eq(#sv_jobs - 1, 15, "active settlement job count")

local def_block = main_src:match("local defaults = (%b{})\nstalker_camp_builder%.defaults = defaults")
assert(def_block, "defaults table not found")
local D = assert(loadstring("return " .. def_block))()
eq(D.max_survivors_player_camp, 15, "defaults.max_survivors_player_camp")
eq(D.max_survivors_per_camp, 15, "defaults.max_survivors_per_camp")

local mcm_line = mcm_src:match('{ id = "max_survivors_player_camp"[^\n]+}')
assert(mcm_line, "max_survivors_player_camp MCM entry not found")
eq(tonumber(mcm_line:match("min = (%d+)")), 0, "MCM max_survivors_player_camp min")
eq(tonumber(mcm_line:match("max = (%d+)")), 30, "MCM max_survivors_player_camp max")
eq(tonumber(mcm_line:match("def = (%d+)")), 15, "MCM max_survivors_player_camp def")

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
    powder_1 = true, powder_2 = true, explo_jerrycan_fuel = true,
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
    find_stash = function(sid) return sid == 30 and 20 or nil end,
    get_stash = function(sid) return sid == 30 and 20 or nil end,
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

-- Test Chain 1c: Scrapper surplus metal refining ONLY draws Copper Wire (never refines scrap metal into cloth)
do
    local items = {}
    for _ = 1, 16 do items[#items + 1] = "prt_i_scrap" end
    for _ = 1, 6 do items[#items + 1] = "prt_i_fasteners" end
    reset_env(items)
    local camp = { hub_id = 1, structures = { [11] = "salvage_table" }, survivors = {} }
    local surv = { name = "Scrapper", job = "scrapper", tier = 2, has_tools = true }
    local ok = sb.process_scrapper_job(101, 1, camp, surv, 1)
    eq(ok, true, "Chain 1c: scrapper surplus copper refining succeeded")
    eq(count_sec("prt_i_copper"), 1, "Chain 1c: 1x prt_i_copper refined from surplus metal")
    eq(count_sec("prt_i_cloth"), 0, "Chain 1c: scrapper NEVER turns scrap metal into cloth")
end

-- Test Chain 2-lab: a Chemist with no lab structure at all is paused with "No Lab Station" and makes nothing
do
    reset_env({ "charcoal", "charcoal", "vodka" })
    local camp = { hub_id = 1, structures = { [20] = "water_pump" }, survivors = {} }
    local chem = { name = "Chemist", job = "chemist", tier = 0, chemist_mode = "powder" }
    local paused_l, reason_l = sb._calc_job_paused_status(chem, camp, 1, nil)
    eq(paused_l, true, "Chain 2-lab: chemist paused with no lab structure")
    eq(reason_l, "No Lab Station", "Chain 2-lab: pause reason")
    eq(sb.process_chemist_job(105, 1, camp, chem, 1), false, "Chain 2-lab: process_chemist_job refuses")
    eq(count_sec("powder_1"), 0, "Chain 2-lab: nothing synthesized")
end

-- Test Chain 2a: Chemist synthesizes Gunpowder (powder_1) from 2x Charcoal + 1x Alcohol/Vodka, then Crafter crafts ammo
do
    reset_env({ "charcoal", "charcoal", "vodka", "prt_i_scrap" })
    local camp = { hub_id = 1, structures = { [12] = "ammo_bench", [13] = "distiller" }, survivors = {} }
    local chem = { name = "Chemist", job = "chemist", tier = 0, chemist_mode = "powder" }
    local paused_c, reason_c = sb._calc_job_paused_status(chem, camp, 1, nil)
    eq(paused_c, false, "Chain 2a: chemist not paused when 2x charcoal + 1x vodka exist (reason=" .. tostring(reason_c) .. ")")
    local ok_chem = sb.process_chemist_job(105, 1, camp, chem, 1)
    eq(ok_chem, true, "Chain 2a: process_chemist_job synthesized gunpowder")
    eq(count_sec("charcoal"), 0, "Chain 2a: 2x charcoal consumed by chemist")
    eq(count_sec("vodka"), 0, "Chain 2a: 1x vodka consumed by chemist")
    check(count_sec("powder_1") >= 1, "Chain 2a: powder_1 synthesized by chemist")

    -- Now Ammo Crafter uses the Chemist's synthesized powder_1 + prt_i_scrap -> boxed ammo
    local crafter = { name = "Crafter", job = "craft", tier = 2, craft_order = "pistol" }
    local paused_a, reason_a = sb._calc_job_paused_status(crafter, camp, 1, nil)
    eq(paused_a, false, "Chain 2a: ammo crafter not paused after chemist synthesized gunpowder (reason=" .. tostring(reason_a) .. ")")
    local ok_craft = sb.process_ammo_crafting(102, 1, camp, crafter, 1)
    eq(ok_craft, true, "Chain 2a: process_ammo_crafting succeeded using chemist gunpowder")
    eq(count_sec("prt_i_scrap"), 0, "Chain 2a: 1x prt_i_scrap consumed by ammo crafter")
    check(count_sec("ammo_9x18_fmj") + count_sec("ammo_9x19_fmj") >= 1, "Chain 2a: pistol ammo crafted from chemist gunpowder")
end

-- Test Chain 2b: Chemist synthesizes Kerosene / Liquid Fuel from 2x Charcoal + 2x Alcohol/Vodka
do
    reset_env({ "charcoal", "charcoal", "vodka", "alcohol" })
    local camp = { hub_id = 1, structures = { [13] = "distiller" }, survivors = {} }
    local chem = { name = "Chemist", job = "chemist", tier = 0, chemist_mode = "fuel" }
    local paused_f, reason_f = sb._calc_job_paused_status(chem, camp, 1, nil)
    eq(paused_f, false, "Chain 2b: chemist not paused in fuel mode when 2x charcoal + 2x alcohol exist (reason=" .. tostring(reason_f) .. ")")
    local ok_fuel = sb.process_chemist_job(105, 1, camp, chem, 1)
    eq(ok_fuel, true, "Chain 2b: process_chemist_job synthesized liquid fuel")
    eq(count_sec("charcoal"), 0, "Chain 2b: 2x charcoal consumed for fuel")
    eq(count_sec("vodka") + count_sec("alcohol"), 0, "Chain 2b: 2x alcohol/vodka consumed for fuel")
    check(count_sec("kerosene") + count_sec("explo_jerrycan_fuel") >= 1, "Chain 2b: kerosene/liquid fuel synthesized")
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

-- Test Chain 6: Chemist Station (chemist_station) grants +1 yield bonus and X-Ray IReader::r_string (<4095 byte) line limit
do
    -- a batch of 3 (base 1 + lab 1 + chemist_station 1) takes 3 sets of inputs: 6 charcoal + 3 vodka
    reset_env({ "charcoal", "charcoal", "charcoal", "charcoal", "charcoal", "charcoal", "vodka", "vodka", "vodka" })
    local camp = { hub_id = 1, structures = { [16] = "chemist_station" }, survivors = {} }
    local chem = { name = "Chemist", job = "chemist", tier = 0, chemist_mode = "powder" }
    local paused_cs, reason_cs = sb._calc_job_paused_status(chem, camp, 1, nil)
    eq(paused_cs, false, "Chain 6: chemist not paused at chemist_station (reason=" .. tostring(reason_cs) .. ")")
    local ok_cs = sb.process_chemist_job(105, 1, camp, chem, 1)
    eq(ok_cs, true, "Chain 6: process_chemist_job succeeded at chemist_station")
    eq(count_sec("powder_1"), 3, "Chain 6: chemist_station grants +1 extra tin (base 1 + lab 1 + chemist_station 1 = 3)")
    eq(count_sec("charcoal") + count_sec("vodka"), 0, "Chain 6: each of the 3 tins paid its own charcoal and vodka")

    -- one set of inputs buys one tin, whatever the station
    reset_env({ "charcoal", "charcoal", "vodka" })
    eq(sb.process_chemist_job(105, 1, camp, chem, 1), true, "Chain 6: one set of inputs")
    eq(count_sec("powder_1"), 1, "Chain 6: one set of inputs makes one tin, not the whole batch")
    eq(count_sec("charcoal") + count_sec("vodka"), 0, "Chain 6: that set was used up")

    for _, xml_path in ipairs({
        "00_Core/gamedata/configs/text/eng/ui_st_stalker_camp_builder.xml",
        "00_Core/gamedata/configs/text/rus/ui_st_stalker_camp_builder.xml",
        "HomesteadHF/gamedata/configs/text/eng/st_homestead_stations.xml",
        "HomesteadHF/gamedata/configs/text/rus/st_homestead_stations.xml",
    }) do
        local raw = slurp(xml_path)
        local max_len = 0
        for line in raw:gmatch("[^\n]+") do
            if #line > max_len then max_len = #line end
        end
        check(max_len < 4000, xml_path .. " max line length < 4000 bytes for X-Ray IReader::r_string (got " .. max_len .. ")")
    end
end

-- Test Chain 7: Chemist fuel batch: at most 4 cans, every can pays 2 charcoal + 2 vodka uses
do
    local items = {}
    for _ = 1, 10 do items[#items + 1] = "charcoal" end
    for _ = 1, 10 do items[#items + 1] = "vodka" end
    reset_env(items)
    local camp = { hub_id = 1, structures = { [16] = "chemist_station" }, survivors = {} }
    local chem = { name = "Chemist", job = "chemist", tier = 3, chemist_mode = "fuel", has_drugkit = true }
    sb.get_survivor_tier_mult = function() return 3.0 end
    eq(sb.process_chemist_job(105, 1, camp, chem, 1), true, "Chain 7: fuel batch")
    eq(count_sec("kerosene"), 4, "Chain 7: a Master with a Station and a kit makes 4 cans, the batch cap")
    eq(count_sec("charcoal"), 2, "Chain 7: 4 cans took 8 charcoal uses")
    eq(count_sec("vodka"), 2, "Chain 7: 4 cans took 8 vodka uses")

    -- inputs for 2 cans only: the batch is cut to 2 (never 4 cans from 2 sets)
    reset_env({ "charcoal", "charcoal", "charcoal", "charcoal", "vodka", "vodka", "vodka", "vodka" })
    eq(sb.process_chemist_job(105, 1, camp, chem, 1), true, "Chain 7: short of inputs")
    eq(count_sec("kerosene"), 2, "Chain 7: inputs for 2 sets make 2 cans")
    eq(count_sec("charcoal") + count_sec("vodka"), 0, "Chain 7: all inputs used")
    sb.get_survivor_tier_mult = function(s) return (s and s.tier and s.tier >= 2) and 1.5 or 1.0 end

    -- every box full: the output would go to the Market Stall, so nothing is made and nothing is taken
    reset_env({ "charcoal", "charcoal", "vodka", "vodka" })
    local real_target = sb.get_auto_sort_target_box
    sb.get_auto_sort_target_box = function() return 20 end    -- the stall's stash
    local camp2 = { hub_id = 1, structures = { [16] = "chemist_station", [30] = "market_stall" }, survivors = {} }
    local chem2 = { name = "Chemist", job = "chemist", tier = 0, chemist_mode = "fuel" }
    eq(sb.process_chemist_job(105, 1, camp2, chem2, 1), false, "Chain 7: no batch when the output would overflow to the stall")
    eq(chem2.shortfall_reason, "Storage Full", "Chain 7: paused on Storage Full")
    eq(#stall_inv, 0, "Chain 7: nothing reached the Market Stall")
    eq(count_sec("charcoal") + count_sec("vodka"), 4, "Chain 7: inputs untouched")
    sb.get_auto_sort_target_box = real_target
end

-- Test Chain 8: wood and scrap metal stop at the 40 stock cap (a tester's camp filled ~200 kg of timber)
do
    eq(sb.get_stock_cap("wood"), 200, "Chain 8: default wood stock cap")
    eq(sb.get_stock_cap("scrap"), 200, "Chain 8: default scrap stock cap")
    -- the caps come from MCM; the rest of the chain runs at 40
    sb.cfg.wood_stock_cap, sb.cfg.scrap_stock_cap = 40, 40
    eq(sb.get_stock_cap("wood"), 40, "Chain 8: wood stock cap follows the setting")
    eq(sb.get_stock_cap("scrap"), 40, "Chain 8: scrap stock cap follows the setting")
    sb.cfg.yield_wood_min, sb.cfg.yield_wood_max = 8, 8

    -- a full woodpile: a Timber woodcutter cuts nothing and pauses
    local items = {}
    for _ = 1, 40 do items[#items + 1] = "prt_i_wood" end
    reset_env(items)
    local camp = { hub_id = 1, structures = {}, survivors = {} }
    local wc = { name = "Woodcutter", job = "woodcutter", tier = 0, woodcutter_mode = "timber" }
    eq(sb.process_woodcutter_job(106, 1, camp, wc, 1), false, "Chain 8: no timber past the cap")
    eq(wc.shortfall_reason, "Stockpile Full", "Chain 8: woodcutter shortfall")
    eq(count_sec("prt_i_wood"), 40, "Chain 8: woodpile unchanged")
    local p, r = sb._calc_job_paused_status(wc, camp, 1, nil)
    eq(p, true, "Chain 8: timber woodcutter paused at the cap")
    eq(r, "Stockpile Full", "Chain 8: timber pause reason")

    -- 37 stored: a cycle of 8 is cut to the 3 that fit under the cap
    items = {}
    for _ = 1, 37 do items[#items + 1] = "prt_i_wood" end
    reset_env(items)
    wc.shortfall_reason = nil
    eq(sb.process_woodcutter_job(106, 1, camp, wc, 1), true, "Chain 8: timber up to the cap")
    eq(count_sec("prt_i_wood"), 40, "Chain 8: woodpile filled to exactly 40")

    -- cap off: the woodpile grows as before
    sb.cfg.enable_surplus_cap = false
    items = {}
    for _ = 1, 40 do items[#items + 1] = "prt_i_wood" end
    reset_env(items)
    eq(sb.process_woodcutter_job(106, 1, camp, wc, 1), true, "Chain 8: cap off cuts timber")
    eq(count_sec("prt_i_wood"), 48, "Chain 8: cap off adds the full cycle")
    eq((sb._calc_job_paused_status(wc, camp, 1, nil)), false, "Chain 8: cap off never pauses timber")
    sb.cfg.enable_surplus_cap = true

    -- a full scrap pile: the scrapper salvages nothing and pauses
    items = {}
    for _ = 1, 40 do items[#items + 1] = "prt_i_scrap" end
    reset_env(items)
    local camp_s = { hub_id = 1, structures = { [11] = "workbench" }, survivors = {} }
    local sc = { name = "Scrapper", job = "scrapper", tier = 0 }
    eq(sb.process_scrapper_job(107, 1, camp_s, sc, 1), false, "Chain 8: no scrap past the cap")
    eq(sc.shortfall_reason, "Stockpile Full", "Chain 8: scrapper shortfall")
    eq(count_sec("prt_i_scrap"), 40, "Chain 8: scrap pile unchanged")
    eq(count_sec("prt_i_fasteners"), 0, "Chain 8: no fasteners while capped")
    p, r = sb._calc_job_paused_status(sc, camp_s, 1, nil)
    eq(p, true, "Chain 8: scrapper paused at the cap")
    eq(r, "Stockpile Full", "Chain 8: scrapper pause reason")

    -- 39 stored: a cycle of 3 scrap is cut to the 1 that fits
    items = {}
    for _ = 1, 39 do items[#items + 1] = "prt_i_scrap" end
    reset_env(items)
    sc.shortfall_reason = nil
    eq(sb.process_scrapper_job(107, 1, camp_s, sc, 1), true, "Chain 8: scrap up to the cap")
    eq(count_sec("prt_i_scrap"), 40, "Chain 8: scrap pile filled to exactly 40")

    -- a full scrap pile at a Salvage Table still refines copper wire, and salvages nothing new
    items = {}
    for _ = 1, 40 do items[#items + 1] = "prt_i_scrap" end
    for _ = 1, 6 do items[#items + 1] = "prt_i_fasteners" end
    reset_env(items)
    local camp_t = { hub_id = 1, structures = { [11] = "salvage_table" }, survivors = {} }
    local st = { name = "Scrapper", job = "scrapper", tier = 0, has_tools = true }
    eq((sb._calc_job_paused_status(st, camp_t, 1, nil)), false, "Chain 8: refining scrapper not paused at the cap")
    eq(sb.process_scrapper_job(107, 1, camp_t, st, 1), true, "Chain 8: capped scrapper refines")
    eq(count_sec("prt_i_copper"), 1, "Chain 8: copper wire from the full pile")
    eq(count_sec("prt_i_scrap"), 38, "Chain 8: refining draws the pile down")
    eq(count_sec("prt_i_fasteners"), 5, "Chain 8: no new fasteners while capped")

    -- an Auto woodcutter on its timber turn burns the full woodpile instead
    items = {}
    for _ = 1, 40 do items[#items + 1] = "prt_i_wood" end
    reset_env(items)
    local wa = { name = "Woodcutter", job = "woodcutter", tier = 0, woodcutter_mode = "auto", _woodcutter_alt = true }
    eq(sb.process_woodcutter_job(106, 1, camp, wa, 1), true, "Chain 8: auto woodcutter works at the cap")
    eq(count_sec("prt_i_wood"), 35, "Chain 8: auto burnt 5 wood")
    check(count_sec("charcoal") >= 3, "Chain 8: auto made charcoal")
end

-- Test Chain 9: Water pumps pay 1 filter per pump, Scavenge tier caps at 1.5, Hunter Station adds max_m + 1 without x1.5 meat multiplier
do
    -- 3 water pumps with only 1 filter: only 1 pump runs and produces 1 flask
    reset_env({ "water_filter" })
    local camp_w = { hub_id = 1, structures = { [21] = "water_pump", [22] = "water_pump", [23] = "water_pump" }, survivors = {} }
    local flasks1, fed1 = sb.process_water_pumps(1, camp_w, 3, 1, nil)
    eq(fed1, 1, "Chain 9: 3 pumps with 1 filter feeds 1 pump")
    eq(flasks1, 1, "Chain 9: 1 fed pump makes 1 flask")
    eq(count_sec("water_filter"), 0, "Chain 9: 1 filter consumed")
    eq(count_sec("flask"), 1, "Chain 9: 1 flask in storage")

    -- 3 water pumps with 3 filters: all 3 pumps run and produce 3 flasks
    reset_env({ "water_filter", "water_filter", "water_filter" })
    local flasks3, fed3 = sb.process_water_pumps(1, camp_w, 3, 1, nil)
    eq(fed3, 3, "Chain 9: 3 pumps with 3 filters feeds all 3 pumps")
    eq(flasks3, 3, "Chain 9: 3 fed pumps make 3 flasks")
    eq(count_sec("water_filter"), 0, "Chain 9: all 3 filters consumed")
    eq(count_sec("flask"), 3, "Chain 9: 3 flasks in storage")

    -- Scavenge tier multiplier caps at 1.5 inside spawn_scavenged_loot when multiplier is omitted
    reset_env({})
    sb.cfg.scavenge_min_items, sb.cfg.scavenge_max_items = 2, 2
    sb.scavenge_loot_table = { "conserva" }
    sb.get_survivor_tier_mult = function() return 3.0 end
    local camp_sc = { hub_id = 1, structures = {}, survivors = {} }
    local scav_surv = { name = "Scavenger", job = "scavenge", tier = 3 }
    local dep_sc = sb.spawn_scavenged_loot(1, nil, 1, camp_sc, scav_surv)
    eq(#dep_sc, 3, "Chain 9: Master scavenger tier_mult caps at 1.5 (base 2 * 1.5 = 3 items, not 6)")
    sb.get_survivor_tier_mult = function(s) return (s and s.tier and s.tier >= 2) and 1.5 or 1.0 end
end

if fails > 0 then
    print(string.format("%d/%d checks FAILED", fails, checks))
    os.exit(1)
end
print(string.format("All %d closed-loop production & settler cap checks passed!", checks))
