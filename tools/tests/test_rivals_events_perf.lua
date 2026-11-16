-- Standalone tests for the perf changes in the rivals / expeditions / events scripts: each cached or
-- skipped lookup must give the same results as before.
-- Run: lua tools/tests/test_rivals_events_perf.lua   (Lua 5.1, from the repo root)
stalker_camp_builder = { cfg = {}, defaults = {} }
local sb = stalker_camp_builder
-- the rivals script keeps a probe vector at file scope
vector = vector or function()
    return setmetatable({ x = 0, y = 0, z = 0 }, { __index = { set = function(v, x, y, z) v.x, v.y, v.z = x, y, z; return v end } })
end
dofile("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_expeditions.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_events.script")

local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end
local function near(a, b, msg)
    if type(a) ~= "number" or math.abs(a - b) > 1e-6 then
        fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b))
    end
end

-- ---------------------------------------------------------------- switch distance (rivals)
-- the formula before the cache: max(150, switch_distance) * (1 + switch_factor), factor 0.1 without an ini
local function old_formula(sd, factor) return math.max(150, sd or 150) * (1 + (factor or 0.1)) end
do
    local sd = 450
    alife = function() return { switch_distance = function() return sd end } end

    -- no system ini yet (too early in the load): the fallback, and nothing remembered
    ini_sys = nil
    near(sb.get_safe_switch_distance(), old_formula(450, 0.1), "fallback factor without ini")

    local reads, factor = 0, 0.25
    ini_sys = { r_float_ex = function(_, sec, key)
        reads = reads + 1
        eq(sec, "alife", "ini section"); eq(key, "switch_factor", "ini key")
        return factor
    end }
    near(sb.get_safe_switch_distance(), old_formula(450, 0.25), "factor from the ini")
    near(sb.get_safe_switch_distance_sqr(), old_formula(450, 0.25) ^ 2, "squared")
    for _ = 1, 50 do sb.get_safe_switch_distance() end
    eq(reads, 1, "ini read once")

    -- the switch distance stays live (scripts may change it)
    sd = 750
    near(sb.get_safe_switch_distance(), old_formula(750, 0.25), "live switch distance")
    sd = 100
    near(sb.get_safe_switch_distance(), old_formula(150, 0.25), "floor of 150 m")
    eq(reads, 1, "still one ini read")

    -- is_player_near: same level within the safe distance, as before
    sd = 450
    local lvl = "l01_escape"
    level = { name = function() return lvl end }
    db = { actor = { position = function() return { x = 0, y = 0, z = 0 } end } }
    local r = old_formula(450, 0.25)
    eq(sb.is_player_near(lvl, { x = r - 1, y = 0, z = 0 }), true, "near inside the radius")
    eq(sb.is_player_near(lvl, { x = r + 1, y = 0, z = 0 }), false, "not near outside the radius")
    eq(sb.is_player_near("l02_garbage", { x = 0, y = 0, z = 0 }), false, "other level")
    eq(reads, 1, "is_player_near uses the cached factor")
end

-- ---------------------------------------------------------------- expedition chatter (expeditions)
-- reference: the three checks emit_expedition_chatter makes, any one of which sends a line
local function would_send(chatter, p)
    return (p >= 0.25 and not chatter[25]) or (p >= 0.50 and not chatter[50]) or (p >= 0.75 and not chatter[75]) or false
end
do
    local states = {
        {}, { [25] = true }, { [25] = true, [50] = true }, { [25] = true, [50] = true, [75] = true },
        { [50] = true }, { [75] = true }, { [25] = true, [75] = true },
    }
    for _, ch in ipairs(states) do
        for i = 0, 120 do
            local p = i / 100
            eq(sb.expedition_chatter_due(ch, p), would_send(ch, p), "chatter due at " .. p)
        end
    end
    eq(sb.expedition_chatter_due({}, -1), false, "negative progress")
end

-- the 1-second tick: names are looked up only on a tick that sends a line, and every line still goes out
do
    local now = 0
    local translations, labels, tips = 0, 0, {}
    sb.game_sec = function() return now end
    game = { translate_string = function(id) translations = translations + 1; return id end }
    sb.get_camp_label = function(camp) labels = labels + 1; return camp.name end
    sb.camp_send_tip = function(_, msg) tips[#tips + 1] = msg end
    sb.active_camps = { [7] = { name = "Home" } }
    db = { actor = {} }
    local exp = { start_sec = 0, duration = 1000, hub_id = 7, target_level = "l01_escape", survivor_name = "Bob",
        looted_stashes = { [101] = true } }   -- already looted: the tick does not loot in this test
    sb.active_stash_expeditions = { [101] = exp }

    local function tick(t) now = t; sb.process_stash_expeditions() end
    tick(100)
    eq(#tips, 0, "no line at 10%"); eq(translations, 0, "no lookups at 10%"); eq(labels, 0, "no label at 10%")
    tick(300)
    eq(#tips, 1, "25% line"); eq(labels, 1, "label looked up for the line")
    local t_after = translations
    tick(400)
    eq(#tips, 1, "no repeat"); eq(translations, t_after, "no lookups between lines"); eq(labels, 1, "no label between lines")
    tick(600)
    eq(#tips, 2, "50% line")
    tick(990)
    eq(#tips, 3, "75% line")
    eq(exp.chatter[25] and exp.chatter[50] and exp.chatter[75], true, "all three flagged")
    -- a camp that is gone: the fallback name is still used for the line
    exp.chatter = {}
    sb.active_camps = {}
    tick(300)
    eq(#tips, 4, "line with the camp gone")
end

-- ---------------------------------------------------------------- raid check gating (events)
-- only camps with a survivor are checked: has_survivor (next) must match the old count > 0
do
    local cfg = sb.cfg
    cfg.raid_cooldown = 10
    cfg.raid_check_interval = 100
    cfg.event_player_dist = 100
    sb.game_sec = function() return 1000 end
    db = { actor = { position = function() return {} end } }
    level = { name = function() return "l01_escape" end }
    alife_object = function() return nil end
    sb.set_event_timers(0, nil)
    local empty = { level = "l01_escape", survivors = {} }
    local none = { level = "l01_escape" }
    local one = { level = "l01_escape", survivors = { [5] = { name = "a" } } }
    local many = { level = "l01_escape", survivors = { [5] = {}, [6] = {}, ["7"] = {} } }
    local other = { level = "l02_garbage", survivors = { [8] = {} } }
    sb.active_camps = { [1] = empty, [2] = none, [3] = one, [4] = many, [5] = other }
    sb.process_camp_raids()
    eq(empty.last_raid_check_time, nil, "empty camp not checked")
    eq(none.last_raid_check_time, nil, "camp without a list not checked")
    eq(one.last_raid_check_time, 1000, "camp with one survivor checked")
    eq(many.last_raid_check_time, 1000, "camp with survivors checked")
    eq(other.last_raid_check_time, nil, "camp on another level not checked")
end

-- ---------------------------------------------------------------- rescale_rival_timers (BUG 6)
do
    sb.game_sec = function() return 10000 end
    sb.rival_camps = {
        r1 = { ruins_decay_time = 10000, unoccupied_time = 9000, takeover_at = 13600 },
        r2 = { ruins_decay_time = 8000 },
    }
    sb.dismantled_levels = { l01_escape = 17200, l02_garbage = 9000 }
    sb.faction_retaliation_timers = { dolg = 15000 }

    -- 1 -> 2 doubles durations, elapsed age (1000 -> 2000, unoccupied_time 9000 -> 8000), and future stamps
    sb.rescale_rival_timers(1, 2)
    near(sb.rival_camps.r1.ruins_decay_time, 20000, "ruins_decay_time doubled")
    near(sb.rival_camps.r1.unoccupied_time, 8000, "unoccupied_time age doubled")
    near(sb.rival_camps.r1.takeover_at, 17200, "takeover_at remaining doubled")
    near(sb.rival_camps.r2.ruins_decay_time, 16000, "r2 ruins_decay_time doubled")
    near(sb.dismantled_levels.l01_escape, 24400, "future dismantled_levels doubled")
    near(sb.dismantled_levels.l02_garbage, 9000, "past dismantled_levels untouched")
    near(sb.faction_retaliation_timers.dolg, 20000, "faction_retaliation_timers remaining doubled")

    -- invalid or equal factors are no-ops
    sb.rescale_rival_timers(nil, 2)
    sb.rescale_rival_timers(0, 2)
    sb.rescale_rival_timers(2, 2)
    near(sb.rival_camps.r1.ruins_decay_time, 20000, "no-op rescale preserves value")
end

-- ---------------------------------------------------------------- missing chest stash release (BUG 4)
do
    local released_stash = nil
    local m_state = { player_created_stashes = { [777] = "blue_box_item", [888] = "keep" } }
    alife_storage_manager = { get_state = function() return m_state end }
    treasure_manager = {
        caches = { [777] = "medkit_army" },
        release_stash_by_id = function(id) released_stash = id end,
    }
    sb.game_sec = function() return 20000 end
    sb.game_timer_scale = function() return 2 end
    sb.sync_timer_scale = function() end
    sb.remove_all_rival_map_spots = function() end
    sb.release_camp_decorations = function() end
    sb.camp_send_tip = function() end
    sb.cfg.max_rival_camps = 0
    sb.dismantled_levels = {}
    sb.faction_retaliation_timers = {}
    sb.faction_retaliation_targets = {}
    sb.active_convoys = {}
    sb.rival_camps = {
        gone = { chest_id = 777, level = "l01_escape", name = "MissingCamp" },
    }
    alife = function() return {} end
    alife_object = function() return nil end
    db = { actor = nil }
    level = { name = function() return "l01_escape" end, object_by_id = function() return nil end }
    time_global = function() return 100000 end
    game = { translate_string = function(s) return s end }

    sb.update_rival_camps()
    eq(released_stash, 777, "missing se_chest teardown calls treasure_manager.release_stash_by_id")
    eq(treasure_manager.caches[777], nil, "missing se_chest teardown clears treasure_manager.caches")
    eq(m_state.player_created_stashes[777], nil, "missing se_chest teardown clears player_created_stashes")
    eq(m_state.player_created_stashes[888], "keep", "unrelated stash untouched")
    eq(sb.rival_camps.gone, nil, "missing se_chest rival camp removed")
    eq(sb.dismantled_levels["l01_escape"] >= 20000 + 2 * 3600 * 2, true, "dismantled_levels respects game_timer_scale")
end

-- ---------------------------------------------------------------- radio log clear scoping (BUG 11b)
do
    dofile("00_Core/gamedata/scripts/stalker_camp_builder_radio.script")
    sb.radio_logs = {}
    sb.add_camp_radio_log("hub_a", "combat", "Raid A")
    sb.add_camp_radio_log("hub_b", "combat", "Raid B")
    eq(#(sb.radio_logs["all"] or {}), 2, "two logs recorded under all")

    sb.clear_camp_radio_logs("hub_a")
    eq(#(sb.radio_logs["hub_a"] or {}), 0, "hub_a logs cleared")
    eq(#(sb.radio_logs["hub_b"] or {}), 1, "hub_b logs preserved")
    eq(#(sb.radio_logs["all"] or {}), 2, "clearing specific hub preserves 'all' feed")

    sb.clear_camp_radio_logs("all")
    eq(#(sb.radio_logs["hub_b"] or {}), 0, "clearing 'all' clears hub logs")
    eq(#(sb.radio_logs["all"] or {}), 0, "clearing 'all' empties 'all' feed")
end

-- ---------------------------------------------------------------- gadgets: channel bus, fire_cd, caching, alarm delegation (BUG 10, 11a, PERF 12-13)
do
    local vec_allocs = 0
    local function mkvec(x, y, z)
        vec_allocs = vec_allocs + 1
        local v = { x = x or 0, y = y or 0, z = z or 0 }
        function v:set(a, b, c)
            if type(a) == "table" then self.x, self.y, self.z = a.x, a.y, a.z
            else self.x, self.y, self.z = a or 0, b or 0, c or 0 end
            return self
        end
        function v:sub(o) self.x, self.y, self.z = self.x - o.x, self.y - o.y, self.z - o.z; return self end
        function v:add(o) self.x, self.y, self.z = self.x + o.x, self.y + o.y, self.z + o.z; return self end
        function v:mul(s) self.x, self.y, self.z = self.x * s, self.y * s, self.z * s; return self end
        function v:magnitude() return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z) end
        function v:normalize() local m = self:magnitude(); if m > 0 then self:mul(1/m) end; return self end
        function v:dotproduct(o) return self.x*o.x + self.y*o.y + self.z*o.z end
        function v:crossproduct(a, b)
            self.x = a.y*b.z - a.z*b.y
            self.y = a.z*b.x - a.x*b.z
            self.z = a.x*b.y - a.y*b.x
            return self
        end
        function v:distance_to(o)
            local dx, dy, dz = self.x - o.x, self.y - o.y, self.z - o.z
            return math.sqrt(dx*dx + dy*dy + dz*dz)
        end
        return v
    end
    vector = function() return mkvec(0, 0, 0) end
    vector2 = function() return { set = function(s, a, b) s.x, s.y = a, b; return s end } end
    Frect = function() return { set = function(s) return s end } end

    local active_mod_env = _G
    local active_super_cls = nil
    local active_self = nil
    class = function(name)
        local target_env = active_mod_env
        return function(base)
            local cls = setmetatable({}, { __index = base })
            cls.__index = cls
            cls.__base = base
            setmetatable(cls, {
                __index = base,
                __call = function(c, ...)
                    local inst = setmetatable({ binder = {} }, c)
                    local prev_cls, prev_self = active_super_cls, active_self
                    active_super_cls, active_self = c.__base, inst
                    if c.__init then c.__init(inst, ...) end
                    active_super_cls, active_self = prev_cls, prev_self
                    return inst
                end,
            })
            target_env[name] = cls
            _G[name] = cls
            return cls
        end
    end
    super = function(...)
        if active_super_cls and active_super_cls.__init then
            active_super_cls.__init(active_self, ...)
        end
    end
    local function load_mod(modname, path)
        local env = setmetatable({}, { __index = _G })
        _G[modname] = env
        local prev_env = active_mod_env
        active_mod_env = env
        local chunk = assert(loadfile(path))
        setfenv(chunk, env)
        chunk()
        active_mod_env = prev_env
        return env
    end

    bind_hf_base = {
        wrappers = {},
        hf_binder_wrapper = {
            __init = function(self, obj) self.object = obj end,
            update = function() end,
            net_destroy = function() end,
            pickup = function() end,
        },
        get_wrapper = function(id) return bind_hf_base.wrappers[id] end,
    }
    clsid = {
        actor = 1, script_stalker = 2,
        bloodsucker_s = 10, boar_s = 11, dog_s = 12, flesh_s = 13, pseudodog_s = 14,
        burer_s = 15, cat_s = 16, chimera_s = 17, controller_s = 18, fracture_s = 19,
        poltergeist_s = 20, gigant_s = 21, zombie_s = 22, snork_s = 23, tushkano_s = 24,
        psy_dog_s = 25, psy_dog_phantom_s = 26,
    }
    rq_target = { rqtObject = 1, rqtStatic = 2, rqtObstacle = 4 }
    hit = { fire_wound = 1 }
    game_object = { enemy = 2, friend = 0 }
    sound_object = setmetatable({ s3d = 1, looped = 2 }, {
        __call = function()
            return {
                playing = function() return false end,
                play_at_pos = function() end,
                play_no_feedback = function() end,
                stop = function() end,
            }
        end
    })
    particles_object = function() return { move_to = function() end, play = function() end } end
    ray_pick = function()
        return {
            set_position = function() end, set_direction = function() end,
            set_range = function() end, set_flags = function() end,
            set_ignore_object = function() end, query = function() end,
            get_object = function() return nil end, get_distance = function() return 0 end,
        }
    end
    random_float = function(a, _) return a end
    utils_xml = { screen_ratio = function() return 1.777 end }
    device = function() return { width = 1920, height = 1080 } end
    ui_events = { BUTTON_CLICKED = 1, WINDOW_KEY_PRESSED = 2 }
    DIK_keys = { DIK_ESCAPE = 1 }
    Register_UI = function() end
    Unregister_UI = function() end
    CScriptXmlInit = function()
        local wnd = {
            SetWndSize = function() end, GetWidth = function() return 100 end,
            InitTexture = function() end, SetText = function() end,
        }
        return {
            ParseFile = function() end, InitFrame = function() return wnd end,
            InitTextWnd = function() return wnd end, InitStatic = function() return wnd end,
            Init3tButton = function() return wnd end,
        }
    end
    CUIScriptWnd = {
        __init = function() end, Update = function() end, OnKeyboard = function() return false end,
        SetWndRect = function() end, SetAutoDelete = function() end,
        Register = function() end, AddCallback = function() end,
        ShowDialog = function() end, HideDialog = function() end, IsShown = function() return false end,
    }
    news_manager = { send_tip = function() end }
    ini_sys = { r_string_ex = function() return nil end, section_exist = function() return false end }
    alife_object = function() return nil end
    game = { translate_string = function(s) return s end }

    local get_data_calls = 0
    local hf_store = {}
    hf_obj_manager = {
        get_data = function(id)
            get_data_calls = get_data_calls + 1
            return hf_store[id]
        end,
        update_data = function(id, patch)
            hf_store[id] = hf_store[id] or {}
            for k, v in pairs(patch) do hf_store[id][k] = v end
        end,
    }

    local bone_calls = 0
    local nearest_list = {}
    level = {
        name = function() return "l01_escape" end,
        add_bullet = function() end,
        object_by_id = function() return nil end,
        iterate_nearest = function(_, _, fn)
            for _, o in ipairs(nearest_list) do
                if fn(o) then break end
            end
        end,
    }
    db = { actor = { id = function() return 1 end, position = function() return mkvec(0, 0, 0) end } }

    local mod_alarm = load_mod("bind_alarm_system", "00_Core/gamedata/scripts/bind_alarm_system.script")
    local mod_alarm_pda = load_mod("bind_alarm_system_pda", "00_Core/gamedata/scripts/bind_alarm_system_pda.script")
    local mod_dc = load_mod("bind_display_counter", "00_Core/gamedata/scripts/bind_display_counter.script")
    local mod_turret = load_mod("bind_pistol_turret", "00_Core/gamedata/scripts/bind_pistol_turret.script")
    local mod_ui = load_mod("ui_pistol_turret", "00_Core/gamedata/scripts/ui_pistol_turret.script")

    local function make_obj(id)
        local p = mkvec(0, 0, 0)
        return {
            id = function() return id end,
            position = function() return p end,
            set_bone_visible = function() bone_calls = bone_calls + 1 end,
            play_cycle = function() end,
            set_shader = function() end,
            bone_id = function() return 1 end,
            bone_transform = function()
                return { c = mkvec(0, 0, 0), i = mkvec(1, 0, 0), j = mkvec(0, 0, 1), k = mkvec(0, 0, 1) }
            end,
        }
    end

    -- 1. Alarm PERF 12/13 & BUG 11a delegation + fallback safety
    hf_store[1001] = { is_on = false }
    local alarm_wrp = mod_alarm.alarm_system_wrapper(make_obj(1001))
    get_data_calls, bone_calls, vec_allocs = 0, 0, 0
    alarm_wrp:update(100) -- first_update
    for _ = 1, 20 do alarm_wrp:update(50) end -- 1.0s < 2.0s STATE_SYNC_INTERVAL
    eq(get_data_calls, 0, "alarm skips repeated hf_obj_manager.get_data within sync interval")
    eq(bone_calls, 1, "alarm dirty-checks set_bone_visible (1 set across 20 steady frames)")

    mod_alarm.toggle_alarm_system(1001) -- sets cache directly
    alarm_wrp:update(50)
    eq(alarm_wrp.is_on, true, "toggle_alarm_system updates wrapper cache immediately")
    eq(bone_calls, 2, "bone_led updates once when toggled ON")
    alarm_wrp:net_destroy()

    -- BUG 11a: PDA alarm delegates to bind_alarm_system.alarm_has_targets, plus safe pcall fallback
    local delegated = 0
    local orig_canon = mod_alarm.alarm_has_targets
    mod_alarm.alarm_has_targets = function(o, r, rp) delegated = delegated + 1; return orig_canon(o, r, rp) end
    local rp = ray_pick()
    local bad_stalker = {
        clsid = function() return clsid.script_stalker end,
        position = function() return mkvec(0, 0, 2) end,
        alive = function() return true end,
        id = function() error("dead proxy") end,
        relation = function() return game_object.enemy end,
    }
    nearest_list = { bad_stalker }
    mod_alarm_pda.alarm_has_targets(make_obj(1002), 5, rp)
    eq(delegated, 1, "PDA alarm delegates to bind_alarm_system.alarm_has_targets")
    mod_alarm.alarm_has_targets = nil
    local ok_fb, res_fb = pcall(mod_alarm_pda.alarm_has_targets, make_obj(1002), 5, rp)
    eq(ok_fb, true, "PDA fallback handles throwing o:id() safely via pcall")
    eq(res_fb, false, "throwing proxy safely skipped in PDA fallback")
    mod_alarm.alarm_has_targets = orig_canon
    nearest_list = {}

    -- 2. Display counter PERF 12
    hf_store[2001] = { channel = 1 }
    local dc_wrp = mod_dc.display_counter_wrapper(make_obj(2001))
    get_data_calls = 0
    for _ = 1, 20 do dc_wrp:update(50) end -- 1.0s < 2.0s CHANNEL_SYNC_INTERVAL
    eq(get_data_calls, 0, "display counter skips repeated get_data between 2s sync ticks")
    mod_dc.cycle_display_counter_channel(2001)
    eq(dc_wrp.channel, 2, "cycle_display_counter_channel updates cached channel immediately")
    dc_wrp:net_destroy()

    -- 3. Multi-turret channel bus (BUG 10) + fire_once boolean + UIPistolTurret dirty-check (PERF 12)
    _G.hf_turret_channels = {}
    hf_store[3001] = { mag = { "ammo_9x19_fmj", "ammo_9x19_fmj" }, channel = 4 }
    hf_store[3002] = { mag = { "ammo_9x19_fmj" }, channel = 4 }
    local t1 = mod_turret.pistol_turret_wrapper(make_obj(3001))
    local t2 = mod_turret.pistol_turret_wrapper(make_obj(3002))
    bind_hf_base.wrappers[3001], bind_hf_base.wrappers[3002] = t1, t2

    t1:update(50); t1:update(300)
    t2:update(50); t2:update(300)
    eq(_G.hf_turret_channels[4].ammo, 1, "shared channel reports lowest active turret ammo (1)")
    eq(_G.hf_turret_channels[4].turret_id, 3002, "shared channel tracks lowest-ammo turret 3002")

    t2:set_channel(5)
    eq(_G.hf_turret_channels[4] ~= nil, true, "t2 switching away does NOT wipe channel 4 for t1")
    eq(_G.hf_turret_channels[4].turret_id, 3001, "channel 4 reverts cleanly to t1")
    eq(_G.hf_turret_channels[4].ammo, 2, "channel 4 shows t1 ammo")
    eq(_G.hf_turret_channels[5].turret_id, 3002, "t2 immediately publishes on channel 5")

    t1:net_destroy()
    eq(_G.hf_turret_channels[4], nil, "destroying last turret on channel 4 clears channel entry")
    t2:net_destroy()
    eq(_G.hf_turret_channels[5], nil, "destroying last turret on channel 5 clears channel entry")

    -- fire_once returns false on steer limit (> 12 deg) without popping ammo
    hf_store[3003] = { mag = { "ammo_9x19_fmj", "ammo_9x19_fmj" }, channel = 0 }
    local t3 = mod_turret.pistol_turret_wrapper(make_obj(3003))
    t3.pitch_idx = 3 -- valid MUZZLE_BONES index; barrel_dir is +Z (0,0,1)
    eq(t3:fire_once(mkvec(10, 0, 0)), false, "fire_once returns false when exceeding MAX_STEER_DEG")
    eq(t3:get_mag_count(), 2, "aborted fire_once consumes no ammo")
    eq(t3:fire_once(mkvec(0, 0, 10)), true, "fire_once returns true on valid aligned target")
    eq(t3:get_mag_count(), 1, "successful fire_once consumes 1 round")
    t3:net_destroy()

    -- UIPistolTurret SetText dirty check & cached get_channel
    local ui_set_text_calls = 0
    local orig_xml = CScriptXmlInit
    CScriptXmlInit = function()
        local wnd = {
            SetWndSize = function() end, GetWidth = function() return 100 end,
            InitTexture = function() end,
            SetText = function() ui_set_text_calls = ui_set_text_calls + 1 end,
        }
        return {
            ParseFile = function() end, InitFrame = function() return wnd end,
            InitTextWnd = function() return wnd end, InitStatic = function() return wnd end,
            Init3tButton = function() return wnd end,
        }
    end
    hf_store[3004] = { mag = { "ammo_9x19_fmj" }, channel = 2 }
    local t4 = mod_turret.pistol_turret_wrapper(make_obj(3004))
    bind_hf_base.wrappers[3004] = t4
    local gui = mod_ui.UIPistolTurret()
    gui:TestAndShow(3004)
    get_data_calls, ui_set_text_calls = 0, 0
    for _ = 1, 10 do gui:Update() end
    eq(get_data_calls, 0, "UI Update avoids get_data via cached turret channel")
    eq(ui_set_text_calls, 1, "UI SetText called once across 10 unchanged frames")
    t4:set_channel(3)
    gui:Update()
    eq(ui_set_text_calls, 2, "UI SetText updates immediately when channel changes")
    CScriptXmlInit = orig_xml
    t4:net_destroy()
end

if fails > 0 then print("test_rivals_events_perf: " .. fails .. " FAILED"); os.exit(1) end
print("test_rivals_events_perf: all passed")
