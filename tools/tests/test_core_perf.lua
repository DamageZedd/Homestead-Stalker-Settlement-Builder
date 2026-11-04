-- Standalone tests for the core perf pass (settler condlist cache, inventory scan sweep index).
-- Run: lua tools/tests/test_core_perf.lua   (Lua 5.1, from the repo root)
local fails, checks = 0, 0
local function ok(cond, msg)
    checks = checks + 1
    if not cond then fails = fails + 1; print("FAIL " .. msg) end
end

local function deep_eq(a, b, path, seen)
    path = path or "v"
    if type(a) ~= type(b) then return false, path .. ": type " .. type(a) .. " vs " .. type(b) end
    if type(a) ~= "table" then
        if a ~= b then return false, path .. ": " .. tostring(a) .. " vs " .. tostring(b) end
        return true
    end
    seen = seen or {}
    if seen[a] == b then return true end
    seen[a] = b
    for k, v in pairs(a) do
        local e, why = deep_eq(v, b[k], path .. "." .. tostring(k), seen)
        if not e then return false, why end
    end
    for k in pairs(b) do
        if a[k] == nil then return false, path .. "." .. tostring(k) .. ": missing on the left" end
    end
    return true
end

-- ---------------------------------------------------------------------------------------------
-- 1. setup_settler_beh_logic: condlists parsed once per NPC, fields still assigned every call
-- ---------------------------------------------------------------------------------------------
stalker_camp_builder = {}
db = { storage = {} }
modules = { stype_stalker = 0 }
schemes_by_stype = {}
schemes = { beh = "axr_beh" }
move = { stand = 1, standing = 2 }
anim = { free = 3 }
state_lib = { states = { guard = true, sit_knee = true, wait_na = true } }
local set_state_calls = 0
state_mgr = {
    get_state = function(npc) return npc._state end,
    set_state = function(npc, s) npc._state = s; set_state_calls = set_state_calls + 1 end,
}
local parses = 0
local parse_nil_for = nil
xr_logic = {
    parse_condlist = function(npc, section, field, src)
        parses = parses + 1
        if parse_nil_for and src == parse_nil_for then return nil end
        return { { section = src, infop_check = {}, infop_set = {} } }
    end,
    set_new_scheme_and_logic = function() end,
}

dofile("00_Core/gamedata/scripts/stalker_camp_builder_npc.script")
local sb = stalker_camp_builder

local function fake_npc(id)
    local npc = { _id = id, _info = {} }
    function npc:id() return self._id end
    function npc:alive() return true end
    function npc:give_info_portion(i) self._info[i] = true end
    function npc:disable_info_portion(i) self._info[i] = nil end
    function npc:set_dest_level_vertex_id(v) self._dest = v end
    function npc:set_movement_type() end
    function npc:set_body_state() end
    function npc:set_mental_state() end
    function npc:enable_talk() self._talk = true end
    db.storage[id] = { active_scheme = "beh", beh_homestead_active = true, beh = {}, meet = { meet_manager = {} } }
    return npc
end

local MEET_FIELDS = {
    use = "true", close_anim = "guard", close_snd_hello = "nil", close_snd_bye = "nil", snd_on_use = "nil",
    close_distance = "4", close_victim = "actor", far_anim = "nil", far_snd = "nil", far_distance = "6",
    far_victim = "actor", trade_enable = "true", abuse = "false", allow_break = "true", meet_on_talking = "true",
}

local a = fake_npc(101)
sb.setup_settler_beh_logic(a, 500, nil, "sit_knee")
ok(parses == 16, "first call parses 15 meet fields + beh wait_anim (got " .. parses .. ")")
local st = db.storage[101]
for field, src in pairs(MEET_FIELDS) do
    ok(type(st.meet[field]) == "table" and st.meet[field][1].section == src, "meet." .. field .. " parsed from '" .. src .. "'")
end
ok(st.meet.commander_threat == nil and st.meet.meet_manager.use == "true", "meet manager re-applied")
ok(st.beh.wait_cond and st.beh.wait_cond[1].section == "sit_knee", "beh wait_cond parsed from the anim")
ok(st.beh.wait_anim == "sit_knee" and st.beh.wait_animation == "sit_knee", "beh anim fields")
ok(st.beh.rally_lvid == 500 and st.beh.am_i_reached == true, "rally lvid set")
ok(a._info["npcx_beh_wait"] == true and a._dest == 500 and a._talk, "info portions, dest and talk applied")

-- the engine (or another scheme) overwrote a field: the next call puts it back without parsing
local use_tbl = st.meet.use
st.meet.use = "overwritten"
st.meet.commander_threat = true
sb.setup_settler_beh_logic(a, 500, nil, "sit_knee")
ok(parses == 16, "second call parses nothing (got " .. parses .. ")")
ok(st.meet.use == use_tbl, "meet.use re-assigned from the cache")
ok(st.meet.commander_threat == nil, "commander_threat cleared again")

-- a different anim parses that anim once
sb.setup_settler_beh_logic(a, 500, nil, "wait_na")
ok(parses == 17, "new anim parses once (got " .. parses .. ")")
ok(st.beh.wait_cond[1].section == "wait_na", "beh wait_cond follows the anim")
sb.setup_settler_beh_logic(a, 500, nil, "sit_knee")
ok(parses == 17, "back to a known anim: no parse")
ok(st.beh.wait_cond[1].section == "sit_knee", "beh wait_cond back to sit_knee")

-- each NPC has its own tables (nothing shared between settlers)
local b = fake_npc(102)
sb.setup_settler_beh_logic(b, 600, nil, "sit_knee")
ok(parses == 33, "second NPC parses its own (got " .. parses .. ")")
ok(db.storage[102].meet.use ~= db.storage[101].meet.use, "condlist tables not shared across NPCs")

-- a parse that gives no table is not cached
parse_nil_for = "actor"
local c = fake_npc(103)
sb.setup_settler_beh_logic(c, 700, nil, "sit_knee")
local p1 = parses
sb.setup_settler_beh_logic(c, 700, nil, "sit_knee")
ok(parses - p1 == 2, "nil parses retried each call (close_victim, far_victim; got " .. (parses - p1) .. ")")
parse_nil_for = nil

-- a fresh storage entry (NPC respawned) parses again
db.storage[101] = { active_scheme = "beh", beh_homestead_active = true, beh = {}, meet = {} }
local p2 = parses
sb.setup_settler_beh_logic(a, 500, nil, "sit_knee")
ok(parses - p2 == 16, "new storage entry parses again")

-- ---------------------------------------------------------------------------------------------
-- 2. camp_iterate_inventory: differential test against the pre-change function
-- ---------------------------------------------------------------------------------------------
-- the function as it was before the perf pass (copied verbatim from stalker_camp_builder_inventory.script)
function reference_camp_iterate_inventory(hub_id, camp, callback, priority_box_id)
    if not callback then return false end
    local sb = stalker_camp_builder
    local sim = alife()
    if not sim then return false end

    if not camp and hub_id and sb.active_camps then
        camp = sb.active_camps[hub_id]
    end
    if not hub_id and camp and camp.hub_id then
        hub_id = camp.hub_id
    end

    local containers = sb.get_camp_containers(hub_id, camp) or {}
    if #containers == 0 then return false end

    local box_order = {}
    local seen_boxes = {}
    if priority_box_id and sb.is_valid_camp_box(priority_box_id, hub_id, camp) then
        box_order[1] = priority_box_id
        seen_boxes[priority_box_id] = true
    end
    for _, bid in ipairs(containers) do
        if not seen_boxes[bid] then
            seen_boxes[bid] = true
            box_order[#box_order + 1] = bid
        end
    end

    local any_box_online = false
    for _, cid in ipairs(box_order) do
        local box_obj = level and level.object_by_id and level.object_by_id(cid)
        if box_obj and box_obj.iterate_inventory_box then
            any_box_online = true
            break
        end
    end

    if any_box_online then
        if camp then camp.stored_items = camp.stored_items or {} end
        local scan_stopped = false
        for _, cid in ipairs(box_order) do
            local box_obj = level and level.object_by_id and level.object_by_id(cid)
            if box_obj and box_obj.iterate_inventory_box then
                local stopped = false
                local seen_in_box = {}
                sb.safe_iterate_inventory_box(box_obj, function(temp, cl_item)
                    if not cl_item then return end
                    local iid = cl_item:id()
                    seen_in_box[iid] = true
                    -- An item released earlier in this update has no server object any more, but the
                    -- box lists it until the client handles the destroy event next frame: skip it, or
                    -- every later count and consume in this update finds it again
                    local se_obj = sim:object(iid)
                    if not se_obj then return end
                    -- uses owed from offline consumption come off before the uses are read
                    if type(cl_item) == "userdata" and sb.pending_item_cond and sb.pending_item_cond[iid] then
                        sb.apply_pending_cond(cl_item)
                    end
                    local sec = cl_item:section()
                    local cond = 1.0
                    local ok_c, c = pcall(function() return cl_item:condition() end)
                    if ok_c and c then cond = c end
                    local uses = 1
                    local ok_u, u = pcall(function() return cl_item:get_remaining_uses() end)
                    if ok_u and u then uses = u end
                    local item_w = (cl_item.weight and cl_item:weight()) or nil
                    local ini = ini_sys or sys_ini or system_ini()
                    local max_u = (cl_item.get_max_uses and cl_item:get_max_uses()) or (ini and ini:section_exist(sec) and ini:r_float_ex(sec, "max_uses")) or uses

                    if camp and camp.stored_items then
                        camp.stored_items[iid] = {
                            sec = sec,
                            cond = cond,
                            uses = uses,
                            max_uses = max_u,
                            box_id = cid,
                            weight = item_w,
                            verified = true
                        }
                    end

                    local stop = callback(iid, sec, cond, uses, se_obj, cid, cl_item)
                    if stop == true then
                        stopped = true
                        return true
                    end
                end)
                if camp and camp.stored_items then
                    for stored_iid, stored_it in pairs(camp.stored_items) do
                        if stored_it.box_id == cid and not seen_in_box[stored_iid] then
                            -- the listing misses what a stopped scan never reached, and what was spawned
                            -- into the box this update (the client lists it from the next frame)
                            local se_stored = sim:object(stored_iid)
                            if not (se_stored and se_stored.parent_id == cid) then
                                camp.stored_items[stored_iid] = nil
                            end
                        end
                    end
                end
                if stopped then
                    scan_stopped = true
                    return true
                end
            else
                local stopped = false
                sb.iterate_server_container(cid, function(child_id, se_item)
                    if not (child_id and se_item) then return end
                    local sec = se_item:section_name()
                    local seen = camp and camp.stored_items and camp.stored_items[child_id]
                    -- server items export no condition: keep the one recorded for this item
                    local cond = (seen and seen.sec == sec and seen.cond) or se_item.condition or 1.0
                    local ini = ini_sys or sys_ini or system_ini()
                    local max_u = (ini and ini:section_exist(sec) and ini:r_float_ex(sec, "max_uses")) or 1
                    -- server items export no uses: an item with no record counts as one use, not all of them
                    local uses = (seen and seen.sec == sec and seen.uses) or 1

                    if camp and camp.stored_items then
                        local same_sec = seen and seen.sec == sec
                        local max_u_entry = (same_sec and seen.max_uses) or max_u
                        camp.stored_items[child_id] = {
                            sec = sec,
                            cond = cond,
                            uses = uses,
                            max_uses = max_u_entry,
                            box_id = cid,
                            weight = (same_sec and seen.weight) or nil,
                            verified = (same_sec and seen.verified) or false
                        }
                    end

                    local stop = callback(child_id, sec, cond, uses, se_item, cid, nil)
                    if stop == true then
                        stopped = true
                        return true
                    end
                end)
                if stopped then
                    scan_stopped = true
                    return true
                end
            end
        end
        if camp and not scan_stopped then
            camp._stored_items_complete = true
        end
    else
        -- OFFLINE SETTLEMENT INVENTORY SIMULATION CONTRACT
        camp = camp or (hub_id and sb.active_camps and sb.active_camps[hub_id])
        if camp then
            camp.stored_items = camp.stored_items or {}
            if not camp._stored_items_complete then
                for _, cid in ipairs(box_order) do
                    sb.iterate_server_container(cid, function(child_id, se_item)
                        if child_id and se_item then
                            local sec = se_item:section_name()
                            local seen = camp.stored_items and camp.stored_items[child_id]
                            -- server items export no condition: keep the one recorded for this item
                            local cond = (seen and seen.sec == sec and seen.cond) or se_item.condition or 1.0
                            local ini = ini_sys or sys_ini or system_ini()
                            local max_u = (ini and ini:section_exist(sec) and ini:r_float_ex(sec, "max_uses")) or 1
                            -- server items export no uses: an item with no record counts as one use, not all of them
                            local uses = (seen and seen.sec == sec and seen.uses) or 1
                            camp.stored_items[child_id] = {
                                sec = sec,
                                cond = cond,
                                uses = uses,
                                max_uses = max_u,
                                box_id = cid,
                                weight = (seen and seen.sec == sec and seen.weight) or nil,
                                verified = (seen and seen.verified) or false
                            }
                        end
                    end)
                end
                camp._stored_items_complete = true
            end

            for iid, it in pairs(camp.stored_items) do
                local se_obj = sim:object(iid)
                -- only what is still in one of this camp's boxes, and still the same item
                if not se_obj or not seen_boxes[se_obj.parent_id] or se_obj:section_name() ~= it.sec then
                    camp.stored_items[iid] = nil
                else
                    local stop = callback(iid, it.sec, it.cond or 1.0, it.uses or 1, se_obj, it.box_id, nil)
                    if stop == true then return true end
                end
            end
        else
            for _, cid in ipairs(box_order) do
                local stopped = false
                sb.iterate_server_container(cid, function(child_id, se_item)
                    if not (child_id and se_item) then return end
                    local sec = se_item:section_name()
                    local cond = se_item.condition or 1.0
                    local ini = ini_sys or sys_ini or system_ini()
                    -- server items export no uses: an item with no record counts as one use, not all of them
                    local uses = 1
                    local stop = callback(child_id, sec, cond, uses, se_item, cid, nil)
                    if stop == true then
                        stopped = true
                        return true
                    end
                end)
                if stopped then return true end
            end
        end
    end

    return false
end

dofile("00_Core/gamedata/scripts/stalker_camp_builder_inventory.script")
local new_iterate = stalker_camp_builder.camp_iterate_inventory

-- deterministic PRNG so both runs build the same world
local function rng(seed)
    local s = seed
    return function(n)
        s = (s * 1103515245 + 12345) % 2147483648
        if n then return (s % n) + 1 end
        return s / 2147483648
    end
end

local SECS = { "bread", "kolbasa", "ammo_9x19_fmj", "bandage", "medkit", "flask", "wood_part" }

-- builds the engine stubs and a camp from a seed; returns camp, hub_id, priority, callback, trace
local function build_world(seed)
    local r = rng(seed)
    local sbt = stalker_camp_builder
    local se = {}          -- id -> server object
    local boxes = {}       -- cid -> { online, items = { cl or id } }
    local box_ids = {}
    local nboxes = r(4)
    for i = 1, nboxes do
        local cid = 1000 + i
        box_ids[i] = cid
        boxes[cid] = { online = r() < 0.6, items = {} }
        se[cid] = { parent_id = 65535, section_name = function() return "inventory_box" end }
    end
    local next_id = 2000
    local function new_item(cid, released)
        next_id = next_id + 1
        local iid = next_id
        local sec = SECS[r(#SECS)]
        local cond = math.floor(r() * 100) / 100
        local uses = r(3)
        local cl = { _id = iid, _sec = sec, _cond = cond, _uses = uses, _w = r(5) / 10 }
        function cl:id() return self._id end
        function cl:section() return self._sec end
        function cl:condition() return self._cond end
        function cl:get_remaining_uses() return self._uses end
        function cl:weight() return self._w end
        if r() < 0.5 then function cl:get_max_uses() return 3 end end
        if not released then
            se[iid] = { parent_id = cid, condition = cond, section_name = function() return sec end }
        end
        local list = boxes[cid].items
        list[#list + 1] = cl
        return iid, sec
    end
    for _, cid in ipairs(box_ids) do
        for _ = 1, r(6) - 1 do new_item(cid, r() < 0.1) end
    end

    local camp = { structures = {}, stored_items = {} }
    -- stale entries: in a camp box by record, gone or elsewhere now
    for _ = 1, r(5) do
        next_id = next_id + 1
        local bid = box_ids[r(#box_ids)]
        camp.stored_items[next_id] = { sec = "bread", cond = 0.5, uses = 1, box_id = bid, verified = true }
        local roll = r(3)
        if roll == 1 then
            se[next_id] = { parent_id = bid, section_name = function() return "bread" end }   -- just spawned
        elseif roll == 2 then
            se[next_id] = { parent_id = 9999, section_name = function() return "bread" end }  -- moved away
        end
    end
    -- records of real items, some pointing at the wrong box (moved between camp boxes)
    for _, cid in ipairs(box_ids) do
        for _, cl in ipairs(boxes[cid].items) do
            if r() < 0.5 then
                local rec_box = (r() < 0.3) and box_ids[r(#box_ids)] or cid
                camp.stored_items[cl._id] = { sec = cl._sec, cond = 0.9, uses = 2, max_uses = 3, box_id = rec_box, weight = 0.2, verified = false }
            end
        end
    end
    -- an entry with no box
    next_id = next_id + 1
    camp.stored_items[next_id] = { sec = "flask", cond = 1, uses = 1 }
    if r() < 0.3 then camp._stored_items_complete = true end

    local invalid = {}
    if r() < 0.2 then invalid[box_ids[r(#box_ids)]] = true end
    local priority = (r() < 0.5) and box_ids[r(#box_ids)] or nil

    local sim = { object = function(_, id) return se[id] end }
    alife = function() return sim end
    level = {
        object_by_id = function(id)
            local b = boxes[id]
            if b and b.online then return { _cid = id, iterate_inventory_box = true } end
            return nil
        end,
    }
    ini_sys = {
        section_exist = function() return true end,
        r_float_ex = function(_, sec, key) if key == "max_uses" and sec == "medkit" then return 2 end return nil end,
    }
    sbt.pending_item_cond = nil
    sbt.active_camps = { [500] = camp }
    sbt.get_camp_containers = function()
        local out = {}
        for i, cid in ipairs(box_ids) do out[i] = cid end
        return out
    end
    sbt.is_valid_camp_box = function(bid) return boxes[bid] ~= nil and not invalid[bid] end
    sbt.safe_iterate_inventory_box = function(box_obj, cb)
        for _, cl in ipairs(boxes[box_obj._cid].items) do
            if cb(box_obj, cl) == true then return end
        end
    end
    sbt.iterate_server_container = function(cid, cb)
        for _, cl in ipairs(boxes[cid].items) do
            local s = se[cl._id]
            if s and cb(cl._id, s) == true then return end
        end
    end

    local trace = {}
    local stop_after = (r() < 0.4) and r(8) or nil
    local function callback(iid, sec, cond, uses, se_obj, cid, cl_item)
        trace[#trace + 1] = { iid, sec, cond, uses, cid, cl_item ~= nil }
        if stop_after and #trace >= stop_after then return true end
    end
    return camp, 500, priority, callback, trace
end

local function run(fn, seed)
    local camp, hub_id, priority, cb, trace = build_world(seed)
    local ret = fn(hub_id, camp, cb, priority)
    return { ret = ret, trace = trace, stored = camp.stored_items, complete = camp._stored_items_complete }
end

local diffs = 0
for seed = 1, 400 do
    local old_r = run(reference_camp_iterate_inventory, seed)
    local new_r = run(new_iterate, seed)
    local same, why = deep_eq(old_r, new_r)
    if not same then
        diffs = diffs + 1
        if diffs <= 5 then print("seed " .. seed .. " differs: " .. tostring(why)) end
    end
end
ok(diffs == 0, "camp_iterate_inventory matches the pre-change function on 400 random camps (" .. diffs .. " differ)")

-- stored_ids_by_box groups ids and skips entries without a box
local idx = stalker_camp_builder.stored_ids_by_box({
    [1] = { box_id = 10 }, [2] = { box_id = 11 }, [3] = { box_id = 10 }, [4] = {},
})
table.sort(idx[10])
ok(#idx[10] == 2 and idx[10][1] == 1 and idx[10][2] == 3, "ids grouped by box")
ok(#idx[11] == 1 and idx[11][1] == 2, "single id box")
local n = 0
for _ in pairs(idx) do n = n + 1 end
ok(n == 2, "no list for an entry without box_id")

-- optional benchmark (tools/bench_perf.lua sets BENCH): camp_iterate_inventory before vs after
if BENCH then
    local function measure(fn)
        collectgarbage(); collectgarbage()
        local m0, t0 = collectgarbage("count"), os.clock()
        for rep = 1, 5 do
            for seed = 1, 400 do
                local camp, hub_id, priority, cb = build_world(seed)
                fn(hub_id, camp, cb, priority)
            end
        end
        return (os.clock() - t0) * 1000, collectgarbage("count") - m0
    end
    local base_t = measure(function() end)   -- world construction only
    local old_t = measure(reference_camp_iterate_inventory)
    local new_t = measure(new_iterate)
    BENCH_RESULTS = BENCH_RESULTS or {}
    BENCH_RESULTS[#BENCH_RESULTS + 1] = string.format(
        "camp_iterate_inventory x2000 camps: old %.0f ms, new %.0f ms (world build %.0f ms; net old %.0f, net new %.0f)",
        old_t, new_t, base_t, old_t - base_t, new_t - base_t)
end

print(string.format("%d checks, %d failed", checks, fails))
if fails > 0 then os.exit(1) end
