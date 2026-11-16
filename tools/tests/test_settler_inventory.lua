-- Unit tests for Settler Inventory Access, Filtering, State Sync, and Equipment Lock:
--   1. is_settler_inventory_item_visible & ParseInventory filtering (dense array vs id_list map)
--   2. ParseInventory isolation (never matches db.actor, non-loot mode, companions, or untracked NPCs)
--   3. can_open_settler_inventory & can_open_settler_inventory_by_id checks
--   4. open_settler_inventory & open_settler_inventory_by_id (LMode_Init FDDA bypass, npcx_is_companion untouched,
--      companion delegation, mag_field_load block, error cleanup of _settler_inv_id)
--   5. ActorMenu_on_item_after_move, GUI_on_hide, Close, npc_on_death_callback, actor_on_net_destroy sync
--   6. toggle_settler_equipment_lock & process_settler_equipment skip when equipment_locked
--   7. modxml_stalker_camp_builder manage_camp_dialog phrase 24/241 contract
-- Run: lua tools/tests/test_settler_inventory.lua   (Lua 5.1, from the repo root)

local fails = 0
local checks = 0
local function check(cond, msg)
    checks = checks + 1
    if not cond then
        fails = fails + 1
        print("FAIL: " .. tostring(msg))
    end
end

-- Mock environment state
local callbacks = {}
local function fire_callback(name, ...)
    local list = callbacks[name]
    if not list then return end
    for i = 1, #list do
        list[i](...)
    end
end

_G.RegisterScriptCallback = function(name, fn)
    callbacks[name] = callbacks[name] or {}
    callbacks[name][#callbacks[name] + 1] = fn
end

local registered_uis = {}
_G.Register_UI = function(name, path)
    registered_uis[#registered_uis + 1] = { name = name, path = path }
end

_G._GUIs_keyfree = {}
_G.printf = function() end
_G.game = { translate_string = function(s) return s end }
_G.time_global = function() return 100000 end
_G.str_explode = function(str, sep)
    local out = {}
    for part in string.gmatch(str, "([^" .. sep .. "]+)") do
        out[#out + 1] = part
    end
    return out
end

local item_cfg = {
    wpn_ak74       = { kind = "w_rifle", cost = 20000, ammo_class = "ammo_5.45x39_fmj", inv_name = "AK-74" },
    wpn_pm         = { kind = "w_pistol", cost = 2000, ammo_class = "ammo_9x18_fmj", inv_name = "PM" },
    novice_outfit  = { kind = "o_light", npc_visual = "actors/stalker_novice" },
    exo_outfit     = { kind = "o_heavy", npc_visual = "actors/stalker_exo" },
    medkit         = { kind = "i_medical", can_trade = true },
    ammo_545       = { kind = "w_ammo" },
    ammo_5_45x39_fmj = { kind = "w_ammo" },
    ["ammo_5.45x39_fmj"] = { kind = "w_ammo" },
    device_pda_1   = { kind = "i_device" },
    quest_pda      = { kind = "i_quest", quest_item = true },
    untradeable_x  = { kind = "i_misc", can_trade = false },
    anim_medkit    = { kind = "i_medical", anim = true },
    custom_bolt    = { kind = "i_misc", is_bolt = true },
    hand_radio     = { kind = "i_misc" },
    hand_radio_r   = { kind = "i_misc" },
    anim_knife     = { kind = "i_misc" },
    anim_binoc     = { kind = "i_misc" },
    device_torch   = { kind = "i_device" },
    bolt           = { kind = "i_misc" },
    wpn_binoc_inv  = { kind = "i_device" },
    guitar_a       = { kind = "i_misc" },
    harmonica_a    = { kind = "i_misc" },
}

_G.ini_sys = {
    section_exist = function(_, sec) return item_cfg[sec] ~= nil end,
    r_bool_ex = function(_, sec, key, def)
        local c = item_cfg[sec]
        if c and c[key] ~= nil then return c[key] end
        return def
    end,
    r_float_ex = function(_, sec, key)
        local c = item_cfg[sec]
        return c and c[key] or nil
    end,
    r_string_ex = function(_, sec, key)
        local c = item_cfg[sec]
        return c and c[key] or nil
    end,
}

_G.IsBolt = function(obj)
    local sec = obj and obj:section()
    return sec ~= nil and item_cfg[sec] ~= nil and item_cfg[sec].is_bolt == true
end
_G.IsItem = function(kind, sec)
    if kind == "anim" and sec and item_cfg[sec] then
        return item_cfg[sec].anim == true
    end
    return false
end
_G.IsWeapon = function(obj)
    local sec = obj and obj:section() or ""
    return string.sub(sec, 1, 4) == "wpn_"
end
_G.IsOutfit = function(obj)
    local sec = obj and obj:section() or ""
    return string.find(sec, "_outfit", 1, true) ~= nil
end
_G.IsStalker = function(obj)
    return obj ~= nil and not obj.is_item
end

local online_objs = {}
local se_objs = {}
_G.level = {
    object_by_id = function(id) return online_objs[id] end,
    name = function() return "l01_escape" end,
}
_G.alife_object = function(id) return se_objs[id] end

local actor_obj = {
    id = function() return 0 end,
    alive = function() return true end,
    iterate_inventory = function() end,
    iterate_ruck = function() end,
}
_G.db = {
    actor = actor_obj,
    storage = {},
}

_G.pda = { set_active_subdialog = function() end }

local start_calls = 0
local last_mode_val = nil
local gui_events = {}
local gui_shown = false
local gui_throw_on_lmode = false

local mock_gui = {
    IsShown = function() return gui_shown end,
    LMode_Init = function(_, npc)
        if gui_throw_on_lmode then error("simulated LMode_Init failure") end
        gui_events[#gui_events + 1] = { fn = "LMode_Init", id = npc:id() }
    end,
    ShowDialog = function(_, flag)
        gui_shown = flag
        gui_events[#gui_events + 1] = { fn = "ShowDialog", flag = flag }
    end,
}
_G.GetActorMenu = function() return mock_gui end

local companion_trade_calls = {}
_G.axr_companions = {
    start_trade = function(a, npc)
        companion_trade_calls[#companion_trade_calls + 1] = { actor = a, npc = npc }
    end,
    add_to_actor_squad = function() end,
    remove_from_actor_squad = function() end,
}

local parse_calls = {}
local close_calls = 0
_G.ui_inventory = {
    GUI = mock_gui,
    start = function(mode, obj)
        start_calls = start_calls + 1
    end,
    change_last_mode = function(m)
        last_mode_val = m
    end,
    UIInventory = {
        ParseInventory = function(self, npc, all, id_list, ignore_kind)
            parse_calls[#parse_calls + 1] = {
                id = npc and npc:id(),
                all = all,
                id_list = id_list,
                ignore_kind = ignore_kind,
            }
            local items = npc and npc._items or {}
            if id_list then
                local map = {}
                for _, itm in ipairs(items) do
                    if all or not itm.slotted then
                        map[itm:id()] = itm
                    end
                end
                return map
            end
            local arr = {}
            for _, itm in ipairs(items) do
                if all or not itm.slotted then
                    arr[#arr + 1] = itm
                end
            end
            return arr
        end,
        Close = function()
            close_calls = close_calls + 1
            gui_shown = false
        end,
    },
}

_G.stalker_camp_builder = {
    cfg = {},
    defaults = {},
    active_camps = {},
    camp_npc_released = {},
    settler_home_squads = {},
    game_sec = function() return 50000 end,
    time_factor = function() return 10 end,
    game_timer_scale = function() return 1.0 end,
    get_time_of_day_mult = function() return 1.0 end,
    get_camp_label = function(camp) return camp and camp.name or "Camp" end,
    guarded_call = function(_, fn, ...) if fn then return fn(...) end end,
    camp_send_tip = function() end,
    safe_iterate_inventory_box = function(box, fn)
        for _, item in ipairs(box._items or {}) do
            fn(box, item)
        end
    end,
}
local sb = _G.stalker_camp_builder

_G.vector = function()
    return {
        x = 0, y = 0, z = 0,
        set = function(self, x, y, z) self.x, self.y, self.z = x, y, z; return self end,
    }
end
_G.AddScriptCallback = function() end
_G.SendScriptCallback = function() end

dofile("00_Core/gamedata/scripts/z_stalker_camp_builder_pda_monkeypatch.script")
local monkeypatch_on_game_start = _G.on_game_start
-- Call monkeypatch on_game_start before later dofile() scripts overwrite global on_game_start
monkeypatch_on_game_start()
monkeypatch_on_game_start()

dofile("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_recruit.script")

check(#(callbacks["GUI_on_hide"] or {}) == 1, "GUI_on_hide should register exactly once")
check(#(callbacks["ActorMenu_on_item_after_move"] or {}) == 1, "ActorMenu_on_item_after_move should register exactly once")
check(#(callbacks["npc_on_death_callback"] or {}) == 1, "npc_on_death_callback should register exactly once")
check(#(callbacks["actor_on_net_destroy"] or {}) == 1, "actor_on_net_destroy should register exactly once")
check(type(sb.is_settler_inventory_item_visible) == "function", "is_settler_inventory_item_visible exported")

local function make_item(id, sec, slotted, cond)
    return {
        id = function() return id end,
        section = function() return sec end,
        condition = function() return cond or 1.0 end,
        slotted = slotted or false,
    }
end

-- 1. Visibility filter checks
do
    local visible_secs = { "wpn_ak74", "novice_outfit", "medkit", "ammo_545", "device_pda_1" }
    for _, sec in ipairs(visible_secs) do
        check(sb.is_settler_inventory_item_visible(make_item(1, sec)) == true, sec .. " should be visible")
    end

    local hidden_secs = {
        "hand_radio", "hand_radio_r", "anim_knife", "anim_binoc",
        "device_torch", "bolt", "wpn_binoc_inv", "guitar_a", "harmonica_a",
        "quest_pda", "untradeable_x", "anim_medkit", "custom_bolt",
    }
    for _, sec in ipairs(hidden_secs) do
        check(sb.is_settler_inventory_item_visible(make_item(2, sec)) == false, sec .. " should be hidden")
    end
    check(sb.is_settler_inventory_item_visible(nil) == false, "nil item should be hidden")
    check(sb.is_settler_inventory_item_visible({ section = function() return "" end }) == false, "empty section hidden")
end

-- Helper to create a mock settler NPC
local function make_npc(id, opts)
    opts = opts or {}
    local infos = opts.infos or {}
    local info_mutations = 0
    local active_wpn = nil
    local best_wpn = opts.best_wpn
    local transfers = {}
    return {
        id = function() return id end,
        alive = function() return opts.alive ~= false end,
        character_name = function() return opts.name or ("Settler " .. id) end,
        has_info = function(_, k) return infos[k] == true end,
        give_info_portion = function(_, k) info_mutations = info_mutations + 1; infos[k] = true end,
        disable_info_portion = function(_, k) info_mutations = info_mutations + 1; infos[k] = nil end,
        best_weapon = function() return best_wpn end,
        set_best_weapon = function(_, w) best_wpn = w end,
        make_item_active = function(_, w) active_wpn = w end,
        get_active_weapon = function() return active_wpn end,
        get_info_mutations = function() return info_mutations end,
        get_visual_name = function() return opts.visual or "actors/stalker_novice" end,
        inventory_for_each = function(_, fn)
            for _, itm in ipairs(opts.items or {}) do
                fn(itm)
            end
        end,
        transfer_item = function(_, itm, target)
            transfers[#transfers + 1] = { item = itm, target = target }
        end,
        get_transfers = function() return transfers end,
        _items = opts.items or {},
    }
end

-- Set up camp + settler 42
local ak74 = make_item(1001, "wpn_ak74", true, 0.9)
local outfit = make_item(1002, "novice_outfit", false, 0.9)
local medkit = make_item(1003, "medkit", false, 1.0)
local mixed_items = {
    make_item(1004, "hand_radio_r", false),
    ak74,
    make_item(1005, "device_torch", false),
    outfit,
    make_item(1006, "bolt", false),
    medkit,
    make_item(1007, "wpn_binoc_inv", true),
    make_item(1008, "quest_pda", false),
    make_item(1009, "untradeable_x", false),
    make_item(1010, "anim_medkit", false),
    make_item(1011, "custom_bolt", false),
}
local npc42 = make_npc(42, { items = mixed_items, best_wpn = ak74 })
online_objs[42] = npc42
local sanitized_ids = {}
se_objs[42] = {
    id = 42,
    clsid = function() return 1 end,
    community = function() return "stalker" end,
    profile_name = function() return "(null)" end,
    set_profile_name = function(_, p) sanitized_ids[42] = p end,
    section_name = function() return "sim_default_stalker_0" end,
}
_G.clsid = { stalker = 1, script_stalker = 2 }

local surv42 = { name = "Vaska", job = "guard", has_weapon = true }
sb.active_camps[100] = {
    name = "Rookie Camp",
    survivors = { [42] = surv42 },
}

-- 2. ParseInventory wrapping & isolation
do
    sb._settler_inv_id = 42
    parse_calls = {}

    -- Array mode (id_list nil): must force all=true, preserve ignore_kind, return dense array with NO holes
    local fake_inv_ui = { mode = "loot", npc_is_companion = false }
    local arr = ui_inventory.UIInventory.ParseInventory(fake_inv_ui, npc42, false, nil, true)
    check(#parse_calls == 1 and parse_calls[1].all == true and parse_calls[1].ignore_kind == true,
        "ParseInventory should forward all=true and ignore_kind=true")
    check(#arr == 3, "dense filtered array should have 3 items, got " .. tostring(#arr))
    check(arr[1] == ak74 and arr[2] == outfit and arr[3] == medkit and arr[4] == nil,
        "dense array must preserve order with zero holes")
    local ip_count = 0
    for _ in ipairs(arr) do ip_count = ip_count + 1 end
    check(ip_count == 3, "ipairs count must equal 3 (no holes)")

    -- Map mode (id_list true): must delete filtered keys and keep visible ids
    local map = ui_inventory.UIInventory.ParseInventory(fake_inv_ui, npc42, false, true, false)
    check(map[1001] == ak74 and map[1002] == outfit and map[1003] == medkit, "map mode keeps visible items")
    check(map[1004] == nil and map[1005] == nil and map[1006] == nil and map[1007] == nil
        and map[1008] == nil and map[1009] == nil and map[1010] == nil and map[1011] == nil,
        "map mode deletes all filtered internal items")

    -- Isolation: db.actor must NEVER be overridden
    parse_calls = {}
    actor_obj._items = { make_item(9001, "bolt", false) }
    local a_res = ui_inventory.UIInventory.ParseInventory(fake_inv_ui, actor_obj, false, nil, false)
    check(parse_calls[1].all == false and #a_res == 1, "db.actor ParseInventory must never be overridden or filtered")

    -- Isolation: mode != "loot" must pass through untouched
    parse_calls = {}
    local inv_res = ui_inventory.UIInventory.ParseInventory({ mode = "trade" }, npc42, false, nil, false)
    check(parse_calls[1].all == false, "non-loot mode must not force all=true")
    check(#inv_res == 9, "non-loot mode must not apply settler loot filter")

    -- Isolation: companion flag must pass through untouched
    parse_calls = {}
    ui_inventory.UIInventory.ParseInventory({ mode = "loot", npc_is_companion = true }, npc42, false, nil, false)
    check(parse_calls[1].all == false, "companion mode must not force all=true")

    sb._settler_inv_id = nil
end

-- 3. Preconditions (dialog + PDA by_id)
do
    check(sb.can_open_settler_inventory(actor_obj, npc42) == true, "can_open true for online alive settler")
    check(sb.can_open_settler_inventory(npc42, actor_obj) == true, "can_open true with reversed speaker args")
    check(sb.can_open_settler_inventory(npc42) == true, "can_open true with single npc arg")
    check(sb.can_open_settler_inventory(actor_obj, nil) == false, "can_open false for actor alone")

    local ok_id, err_id = sb.can_open_settler_inventory_by_id(100, 42)
    check(ok_id == true and err_id == nil, "can_open_by_id returns true, nil when online & alive")

    -- On expedition
    surv42.on_expedition = true
    check(sb.can_open_settler_inventory(actor_obj, npc42) == false, "can_open false when on expedition")
    local ok_exp, err_exp = sb.can_open_settler_inventory_by_id(100, 42)
    check(ok_exp == false and err_exp == "st_pda_open_inv_expedition", "expedition error key mismatch")
    surv42.on_expedition = nil

    -- Offline
    online_objs[42] = nil
    check(sb.can_open_settler_inventory(actor_obj, npc42) == false, "can_open false when offline")
    local ok_off, err_off = sb.can_open_settler_inventory_by_id(100, 42)
    check(ok_off == false and err_off == "st_pda_open_inv_offline", "offline error key mismatch")
    online_objs[42] = npc42

    -- Reused item ID
    online_objs[77] = { id = function() return 77 end, is_item = true, alive = function() error("cannot access class member Alive") end }
    sb.active_camps[100].survivors[77] = { name = "BadId" }
    local ok_p, res_p = pcall(sb.can_open_settler_inventory_by_id, 100, 77)
    check(ok_p and res_p == false, "can_open_by_id must not call alive() on item object")
    sb.active_camps[100].survivors[77] = nil
    online_objs[77] = nil
end

-- 4. open_settler_inventory + FDDA bypass + companion delegation + mag_field_load + error reset
do
    start_calls = 0
    gui_events = {}
    registered_uis = {}
    gui_shown = false
    sanitized_ids[42] = nil

    -- mag_field_load blocking check
    _G.mag_field_load = { loading_in_progress = true }
    check(sb.open_settler_inventory(actor_obj, npc42) == false, "open_settler_inventory aborts during mag_field_load")
    check(sb._settler_inv_id == nil and #gui_events == 0, "aborted mag_field_load leaves _settler_inv_id nil")
    _G.mag_field_load.loading_in_progress = false

    -- Error inside LMode_Init must reset sb._settler_inv_id to nil
    gui_throw_on_lmode = true
    check(sb.open_settler_inventory(actor_obj, npc42) == false, "error in LMode_Init returns false")
    check(sb._settler_inv_id == nil, "sb._settler_inv_id must reset to nil on LMode_Init failure")
    gui_throw_on_lmode = false

    -- Normal stationary settler open via open_settler_inventory_by_id
    local opened = sb.open_settler_inventory_by_id(42)
    check(opened == true, "open_settler_inventory_by_id succeeds")
    check(start_calls == 0, "ui_inventory.start must NOT be called (bypasses FDDA corpse crouch)")
    check(sb._settler_inv_id == 42, "sb._settler_inv_id set to 42")
    check(sanitized_ids[42] ~= nil, "sanitize_se_profile ran before opening")
    check(last_mode_val == 4, "change_last_mode(4) called")
    check(gui_events[1] and gui_events[1].fn == "LMode_Init" and gui_events[1].id == 42, "LMode_Init called with npc 42")
    check(gui_events[2] and gui_events[2].fn == "ShowDialog" and gui_events[2].flag == true, "ShowDialog(true) called")
    check(_G._GUIs_keyfree["UIInventory"] == false, "_GUIs_keyfree['UIInventory'] set to false")
    check(#registered_uis == 1 and registered_uis[1].name == "UIInventory", "Register_UI called")
    check(npc42.get_info_mutations() == 0, "npcx_is_companion must NEVER be mutated")

    -- Re-open blocked while GUI is already shown
    check(sb.open_settler_inventory(npc42) == false, "must not open when GUI:IsShown() is true")

    -- Companion delegation
    gui_shown = false
    sb._settler_inv_id = nil
    local comp_npc = make_npc(43, { infos = { npcx_is_companion = true } })
    online_objs[43] = comp_npc
    sb.active_camps[100].survivors[43] = { name = "Comp" }
    companion_trade_calls = {}
    check(sb.open_settler_inventory(actor_obj, comp_npc) == true, "companion open returns true")
    check(#companion_trade_calls == 1 and companion_trade_calls[1].npc == comp_npc, "companion delegates to axr_companions.start_trade")
    check(sb._settler_inv_id == nil, "companion delegation must not set _settler_inv_id")
    online_objs[43] = nil
    sb.active_camps[100].survivors[43] = nil
end

-- 5. Post-transfer & hide/close/death/destroy state sync
do
    -- Unarmed state clears old_aim_time and updates has_weapon=false
    sb._settler_inv_id = 42
    _G.db.storage[42] = { old_aim_time = 950 }
    npc42.set_best_weapon(nil, nil)
    npc42.make_item_active(nil, nil)
    fire_callback("ActorMenu_on_item_after_move", 42, ak74, "loot", 2)
    check(surv42.has_weapon == false, "has_weapon refreshed to false after removing last weapon")
    check(_G.db.storage[42].old_aim_time == nil, "old_aim_time cleared when unarmed to prevent state_mgr_weapon crash")

    -- Unrelated UI hide must NOT clear _settler_inv_id
    fire_callback("GUI_on_hide", "OtherDialog", "other")
    check(sb._settler_inv_id == 42, "GUI_on_hide for non-UIInventory must not clear _settler_inv_id")

    -- Armed on UIInventory hide refreshes has_weapon=true, clears _settler_inv_id, activates best_weapon
    npc42.set_best_weapon(nil, ak74)
    fire_callback("GUI_on_hide", "UIInventory", "ui_inventory")
    check(sb._settler_inv_id == nil, "GUI_on_hide('UIInventory') clears _settler_inv_id")
    check(surv42.has_weapon == true, "has_weapon refreshed to true on hide")
    check(npc42.get_active_weapon() == ak74, "make_item_active called with best_weapon on hide")

    -- Close() fallback path clears _settler_inv_id and clears old_aim_time if unarmed
    sb._settler_inv_id = 42
    _G.db.storage[42] = { old_aim_time = 777 }
    npc42.set_best_weapon(nil, nil)
    ui_inventory.UIInventory.Close(mock_gui)
    check(close_calls == 1 and sb._settler_inv_id == nil, "UIInventory:Close clears _settler_inv_id")
    check(_G.db.storage[42].old_aim_time == nil and surv42.has_weapon == false, "UIInventory:Close syncs unarmed state")

    -- npc_on_death_callback only clears when tracked npc dies
    sb._settler_inv_id = 42
    _G.db.storage[42] = { old_aim_time = 321 }
    fire_callback("npc_on_death_callback", make_npc(999), actor_obj)
    check(sb._settler_inv_id == 42, "unrelated NPC death must not clear _settler_inv_id")
    fire_callback("npc_on_death_callback", npc42, actor_obj)
    check(sb._settler_inv_id == nil and _G.db.storage[42].old_aim_time == nil, "tracked NPC death clears _settler_inv_id & old_aim_time")

    -- actor_on_net_destroy clears _settler_inv_id
    sb._settler_inv_id = 42
    fire_callback("actor_on_net_destroy")
    check(sb._settler_inv_id == nil, "actor_on_net_destroy clears _settler_inv_id")
end

-- 6. Equipment Lock & process_settler_equipment
do
    local armory_wpn = make_item(2001, "wpn_ak74", false, 1.0)
    local armory_ammo = make_item(2002, "ammo_5.45x39_fmj", false, 1.0)
    local armory_box = {
        _items = { armory_wpn, armory_ammo },
        transfer_item = function(self, itm, target)
            self._transferred = self._transferred or {}
            self._transferred[#self._transferred + 1] = itm
        end,
    }
    local locker_suit = make_item(2003, "exo_outfit", false, 1.0)
    local armor_box = {
        _items = { locker_suit },
        transfer_item = function(self, itm, target)
            self._transferred = self._transferred or {}
            self._transferred[#self._transferred + 1] = itm
        end,
    }
    online_objs[501] = armory_box
    online_objs[502] = armor_box

    _G.dynamic_npc_armor_visuals = {
        is_allowed_comm = function() return true end,
        get_visual_prot = function(vis)
            if vis == "actors/stalker_exo" then return 0.9 end
            return 0.1
        end,
    }
    sb.get_camp_categorized_boxes = function()
        return {
            boxes_by_bucket = {
                weapon = { { id = 501 } },
                armor = { { id = 502 } },
            },
        }
    end

    local pm = make_item(2004, "wpn_pm", true, 1.0)
    local worn_suit = make_item(2005, "novice_outfit", false, 1.0)
    local eq_npc = make_npc(44, {
        best_wpn = pm,
        visual = "actors/stalker_novice",
        items = { pm, worn_suit },
    })
    online_objs[44] = eq_npc
    local eq_surv = { name = "Lockable", job = "guard" }
    sb.active_camps[100].survivors[44] = eq_surv

    -- Toggle equipment lock ON
    local st1 = sb.toggle_settler_equipment_lock(100, 44)
    check(st1 == true and eq_surv.equipment_locked == true, "toggle_settler_equipment_lock enables lock and returns true")

    -- process_settler_equipment must skip BOTH weapon and armor swaps while locked
    sb.process_settler_equipment(100, sb.active_camps[100], eq_surv, 44)
    check(armory_box._transferred == nil, "locked settler must not pull weapon/ammo from Armory")
    check(armor_box._transferred == nil, "locked settler must not pull outfit from Quartermaster")
    check(#eq_npc.get_transfers() == 0, "locked settler must not transfer worn gear back")

    -- Toggle equipment lock OFF
    local st2 = sb.toggle_settler_equipment_lock(100, 44)
    check(st2 == false and eq_surv.equipment_locked == false, "toggle_settler_equipment_lock disables lock and returns false")

    -- process_settler_equipment upgrades weapon & armor when unlocked
    sb.process_settler_equipment(100, sb.active_camps[100], eq_surv, 44)
    check(armory_box._transferred and #armory_box._transferred == 2, "unlocked settler pulls weapon + ammo from Armory")
    check(armor_box._transferred and #armor_box._transferred == 1, "unlocked settler pulls armor from Quartermaster")
    check(#eq_npc.get_transfers() == 2, "unlocked settler returns old weapon + old suit")
    check(eq_npc.get_active_weapon() == armory_wpn, "unlocked settler activates upgraded weapon")

    -- Unknown survivor returns nil
    check(sb.toggle_settler_equipment_lock(100, 99999) == nil, "unknown survivor toggle returns nil")
end

-- 7. modxml_stalker_camp_builder manage_camp_dialog phrase 24/241 contract
do
    local f = assert(io.open("00_Core/gamedata/scripts/modxml_stalker_camp_builder.script", "r"))
    local src = f:read("*a")
    f:close()
    local manage_block = src:match('<dialog id="manage_camp_dialog">(.-)</dialog>')
    check(manage_block ~= nil, "manage_camp_dialog block present in modxml")
    if manage_block then
        local p100 = manage_block:match('<phrase id="100">(.-)</phrase>')
        check(p100 and p100:find("<next>24</next>", 1, true) ~= nil, "phrase 100 links to <next>24</next>")
        local p24 = manage_block:match('<phrase id="24">(.-)</phrase>')
        check(p24 and p24:find("<precondition>stalker_camp_builder.can_open_settler_inventory</precondition>", 1, true) ~= nil,
            "phrase 24 checks can_open_settler_inventory")
        check(p24 and p24:find("<text>st_camp_open_inv_ask</text>", 1, true) ~= nil, "phrase 24 uses st_camp_open_inv_ask")
        check(p24 and p24:find("<next>241</next>", 1, true) ~= nil, "phrase 24 links to <next>241</next>")
        local p241 = manage_block:match('<phrase id="241">(.-)</phrase>')
        check(p241 and p241:find("<text>st_camp_open_inv_reply</text>", 1, true) ~= nil, "phrase 241 uses st_camp_open_inv_reply")
        check(p241 and p241:find("<action>stalker_camp_builder.open_settler_inventory</action>", 1, true) ~= nil,
            "phrase 241 calls open_settler_inventory")
    end
end

if fails == 0 then
    print(string.format("test_settler_inventory: all %d checks passed", checks))
end
os.exit(fails == 0 and 0 or 1)
