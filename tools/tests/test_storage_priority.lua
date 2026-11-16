-- Standalone tests for storage weight caching, offline priority_box_id, multi-use counting,
-- scan invalidation, and ammo_elapsed / preserve_pristine deposits.
-- Run: lua tools/tests/test_storage_priority.lua   (Lua 5.1, from the repo root)

local fails = 0
local checks = 0
local function eq(a, b, msg)
    checks = checks + 1
    if a ~= b then
        fails = fails + 1
        print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b))
    end
end
local function ok(cond, msg)
    checks = checks + 1
    if not cond then
        fails = fails + 1
        print("FAIL " .. msg)
    end
end

local tg = 10000
function time_global() return tg end

local sim_objs = {}
local released_ids = {}
local next_id = 50000
local box_items = {}
local next_box_weights = {}

local sim_mt = {
    object = function(_, id) return sim_objs[id] end,
}
function alife() return sim_mt end
function alife_object(id) return sim_objs[id] end
function alife_release(se) if se and se.id then sim_objs[se.id] = nil; released_ids[se.id] = true end end
function alife_create(sec, pos, lvid, gvid, pid)
    next_id = next_id + 1
    local obj = { id = next_id, parent_id = pid or 65535, position = pos, m_level_vertex_id = lvid, m_game_vertex_id = gvid, section_name = function() return sec end }
    sim_objs[obj.id] = obj
    if pid and box_items[pid] then box_items[pid][#box_items[pid] + 1] = obj end
    return obj
end

local create_item_calls = {}
function alife_create_item(sec, owner, opt)
    create_item_calls[#create_item_calls + 1] = { sec = sec, owner = owner, opt = opt }
    local pid = (type(owner) == "table" and owner.id) or 65535
    local pos = (type(owner) == "table" and (owner.position or owner[1])) or { x = 0, y = 0, z = 0 }
    local lvid = (type(owner) == "table" and (owner.m_level_vertex_id or owner[2])) or 1
    local gvid = (type(owner) == "table" and (owner.m_game_vertex_id or owner[3])) or 1
    if opt and opt.ammo then
        local box_sz = 30
        local rem = opt.ammo
        local out = {}
        while rem > 0 do
            local chunk = math.min(rem, box_sz)
            next_id = next_id + 1
            local s = { id = next_id, parent_id = pid, position = pos, m_level_vertex_id = lvid, m_game_vertex_id = gvid, a_elapsed = chunk, section_name = function() return sec end }
            sim_objs[s.id] = s
            if pid ~= 65535 and box_items[pid] then box_items[pid][#box_items[pid] + 1] = s end
            out[#out + 1] = s
            rem = rem - chunk
        end
        return out
    end
    return alife_create(sec, pos, lvid, gvid, pid)
end

function se_save_var() end
function se_load_var() return nil end
function CreateTimeEvent() end
function RemoveTimeEvent() end
function dup_table(t)
    local copy = {}
    for k, v in pairs(t) do copy[k] = v end
    return copy
end

level = {
    object_by_id = function() return nil end,
}

local sec_props = {
    bread = { class = "II_FOOD", inv_weight = 0.3, max_uses = 1, kind = "i_food" },
    ration_ru = { class = "II_FOOD", inv_weight = 0.6, max_uses = 3, kind = "i_food" },
    ["ammo_5.45x39_fmj"] = { class = "AMMO", inv_weight = 0.3, box_size = 30 },
    wpn_ak74 = { class = "WP_AK74", inv_weight = 3.2, ammo_class = "ammo_5.45x39_fmj" },
    inventory_box = { class = "S_INVBOX", inv_weight = 1.0 },
    placeable_camp_box = { class = "S_INVBOX", inv_weight = 1.0 },
}
ini_sys = {
    section_exist = function(_, sec) return sec_props[sec] ~= nil end,
    line_exist = function(_, sec, k) return sec_props[sec] and sec_props[sec][k] ~= nil end,
    r_float_ex = function(_, sec, k) return sec_props[sec] and sec_props[sec][k] end,
    r_string_ex = function(_, sec, k) return sec_props[sec] and sec_props[sec][k] end,
    r_bool_ex = function(_, sec, k, def) local v = sec_props[sec] and sec_props[sec][k]; if v == nil then return def end; return v end,
}

IsItem = function(kind, sec)
    if kind == "ammo" and sec == "ammo_5.45x39_fmj" then return true end
    return nil
end

stalker_camp_builder = {
    active_camps = {},
    cfg = {},
    camp_box_id_cache = {},
    outpost_piece_ids = {},
    resolve_structure_type = function() return nil end,
    safe_alife_object = function(id) return sim_objs[id] end,
    linked_stash_id = function() return nil end,
    ensure_hub_stash = function() return nil end,
    sanitize_primary_chest = function() end,
    is_wood_part = function() return false end,
}
local sb = stalker_camp_builder

dofile("00_Core/gamedata/scripts/stalker_camp_builder_storage.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_inventory.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_scan.script")

local box_caps = {}
sb.get_box_capacity = function(bid) return box_caps[bid] end

local inv_cache_clears = {}
sb.invalidate_server_container_cache = function(bid) inv_cache_clears[#inv_cache_clears + 1] = bid end

local server_iter_calls = 0
sb.iterate_server_container = function(box_or_id, cb)
    server_iter_calls = server_iter_calls + 1
    local bid = (type(box_or_id) == "table") and box_or_id.id or box_or_id
    for _, s in ipairs(box_items[bid] or {}) do
        if cb(s.id, s) == true then return end
    end
end

-- World fixture: 1 hub, 2 boxes
local hub_id = 100
local box_1, box_2 = 201, 202
sim_objs[hub_id] = { id = hub_id, parent_id = 65535, position = { x = 1, y = 2, z = 3 }, m_level_vertex_id = 10, m_game_vertex_id = 20, section_name = function() return "placeable_camp_box" end }
sim_objs[box_1] = { id = box_1, parent_id = 65535, position = { x = 1, y = 2, z = 3 }, m_level_vertex_id = 10, m_game_vertex_id = 20, section_name = function() return "placeable_camp_box" end }
sim_objs[box_2] = { id = box_2, parent_id = 65535, position = { x = 2, y = 2, z = 3 }, m_level_vertex_id = 11, m_game_vertex_id = 20, section_name = function() return "placeable_camp_box" end }
box_items[box_1] = {}
box_items[box_2] = {}
box_caps[box_1] = 10.0
box_caps[box_2] = 10.0

local camp = {
    hub_id = hub_id,
    primary_chest_id = box_1,
    structures = { [box_1] = "chest", [box_2] = "chest" },
    stored_items = {},
}
sb.active_camps[hub_id] = camp

sb.get_camp_containers = function() return { box_1, box_2 } end
sb.is_valid_camp_box = function(bid) return bid == box_1 or bid == box_2 end
sb.get_item_sort_route = function(sec)
    if sec == "ammo_5.45x39_fmj" then return "ammo" end
    if sec == "wpn_ak74" then return "weapon" end
    return "misc"
end

-- 1. camp_count_item counts uses, not item entries
local r1 = alife_create("ration_ru", { x = 0, y = 0, z = 0 }, 1, 1, box_1)
local r2 = alife_create("ration_ru", { x = 0, y = 0, z = 0 }, 1, 1, box_2)
local b1 = alife_create("bread", { x = 0, y = 0, z = 0 }, 1, 1, box_2)
camp.stored_items = {
    [r1.id] = { sec = "ration_ru", cond = 1.0, uses = 3, max_uses = 3, box_id = box_1 },
    [r2.id] = { sec = "ration_ru", cond = 1.0, uses = 2, max_uses = 3, box_id = box_2 },
    [b1.id] = { sec = "bread", cond = 1.0, uses = 1, max_uses = 1, box_id = box_2 },
}
camp._stored_items_complete = true

eq(sb.camp_count_item(hub_id, camp, function(sec) return sec == "ration_ru" end), 5,
    "camp_count_item sums remaining uses (3 + 2 = 5)")
eq(sb.camp_count_item(hub_id, camp, function(sec) return sec == "ration_ru" end, 3), 3,
    "camp_count_item respects stop_at_cap across multi-use stack")

-- 2. offline camp_iterate_inventory respects priority_box_id
local visited = {}
sb.camp_iterate_inventory(hub_id, camp, function(iid, sec, cond, uses, se_o, cid)
    visited[#visited + 1] = cid
end, box_2)
ok(#visited == 3 and visited[1] == box_2 and visited[2] == box_2 and visited[3] == box_1,
    "offline camp_iterate_inventory visits priority_box_id first")

-- 3. camp_has_storage_room lazily builds and reuses camp._cached_box_weights
server_iter_calls = 0
box_caps[box_1] = 0.05 -- full, forces check of box_2
box_caps[box_2] = 50.0
eq(sb.camp_has_storage_room(camp, hub_id, 0.5), true, "camp_has_storage_room finds room in box_2")
local calls_first = server_iter_calls
ok(calls_first > 0 and camp._cached_box_weights and camp._cached_box_weights[box_1] ~= nil and camp._cached_box_weights[box_2] ~= nil,
    "camp_has_storage_room populates camp._cached_box_weights")

server_iter_calls = 0
eq(sb.camp_has_storage_room(camp, hub_id, 0.5), true, "camp_has_storage_room second call succeeds")
eq(server_iter_calls, 0, "camp_has_storage_room reuses cached box weights without rescanning")

-- 4. scan invalidation clears _stored_items_complete, _cached_box_weights, _stats_cache, _stats_cache_tick and bumps _inv_rev/_struct_rev
camp._stats_cache = { cached = true }
camp._stats_cache_tick = 12345
local prev_inv_rev = camp._inv_rev or 0
local prev_struct_rev = camp._struct_rev or 0
sb.invalidate_scan_camp_structures_cache(hub_id)
eq(camp._stored_items_complete, nil, "scan invalidation clears _stored_items_complete")
eq(camp._cached_box_weights, nil, "scan invalidation clears _cached_box_weights")
eq(camp._stats_cache, nil, "scan invalidation clears _stats_cache")
eq(camp._stats_cache_tick, nil, "scan invalidation clears _stats_cache_tick")
ok((camp._inv_rev or 0) > prev_inv_rev, "scan invalidation increments _inv_rev")
ok((camp._struct_rev or 0) > prev_struct_rev, "scan invalidation increments _struct_rev")

-- 5. deposit_item_to_camp handles ammo_elapsed (single/multi-box), invalidates box cache, and preserves _inv_snapshot
box_caps[box_1] = 50.0
camp._cached_box_weights = nil
tg = tg + 1
camp._inv_snapshot = { total_items = 0, total_weight = 0, max_weight = 100 }
create_item_calls = {}
inv_cache_clears = {}
local rev_before_ammo = camp._inv_rev or 0
local dep_box = sb.deposit_item_to_camp(hub_id, camp, "ammo_5.45x39_fmj", false, 0, 1.0, nil, nil, false, 45, true)
eq(dep_box, box_1, "ammo deposited into camp storage box")
eq(#create_item_calls, 1, "single alife_create_item call with ammo option")
eq(create_item_calls[1].opt and create_item_calls[1].opt.ammo, 45, "passes exact ammo count 45")
eq(camp._inv_snapshot.total_items, 2, "45 rounds (30+15) registers 2 ammo boxes in _inv_snapshot")
ok((camp._inv_rev or 0) > rev_before_ammo, "deposit_item_to_camp increments _inv_rev")
eq(inv_cache_clears[#inv_cache_clears], dep_box, "deposit_item_to_camp invalidates server container cache for target box")

-- 6. drop_at_hub = true (arg 9) drops ammo on ground WITHOUT owner.id when storage is full
box_caps[box_1] = 0.01
box_caps[box_2] = 0.01
camp._cached_box_weights = nil
create_item_calls = {}
local stored_before = camp._inv_snapshot.total_items
local dropped = sb.deposit_item_to_camp(hub_id, camp, "ammo_5.45x39_fmj", false, 0, 1.0, nil, nil, true, 45)
ok(dropped ~= nil, "drop_at_hub = true succeeds when boxes are full")
eq(create_item_calls[1].owner.id, nil, "ground drop passes position tuple without hub id")
eq(create_item_calls[1].opt and create_item_calls[1].opt.ammo, 45, "ground drop keeps ammo count")
eq(camp._inv_snapshot.total_items, stored_before, "ground drop does not inflate stored _inv_snapshot")

-- 7. preserve_pristine = true (arg 11) preserves 1.0 condition while default (< 0.99 rule) still degrades gear
box_caps[box_1] = 50.0
camp._cached_box_weights = nil
create_item_calls = {}
local w_dep_box = sb.deposit_item_to_camp(hub_id, camp, "wpn_ak74", false, 0, 1.0, nil, nil, false, nil, true)
ok(w_dep_box ~= nil and create_item_calls[#create_item_calls].opt.cond == 1.0, "preserve_pristine keeps 1.0 weapon condition")

create_item_calls = {}
sb.deposit_item_to_camp(hub_id, camp, "wpn_ak74", false, 0, 1.0, nil, nil, false)
ok(create_item_calls[#create_item_calls].opt.cond < 0.99, "standard deposit without preserve_pristine keeps <0.99 wear roll")

print(string.format("%d checks, %d failed", checks, fails))
if fails > 0 then os.exit(1) end
