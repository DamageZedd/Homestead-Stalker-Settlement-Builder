-- Standalone tests for settlement retaliation raids and offline resolution.
-- Run: lua tools/tests/test_retaliation.lua   (Lua 5.1, from the repo root)

stalker_camp_builder = {
    cfg = {
        rival_camp_retaliation_raids = true,
        needs_enabled = true,
        needs_ammo = true,
    },
    active_camps = {},
    faction_retaliation_timers = {},
    faction_retaliation_targets = {},
}

-- Mocks for standalone test
local now = 10000
stalker_camp_builder.game_sec = function() return now end
stalker_camp_builder.game_timer_scale = function() return 1 end

vector = function()
    local v = { x = 0, y = 0, z = 0 }
    function v:set(x, y, z) self.x = x or 0; self.y = y or 0; self.z = z or 0; return self end
    function v:distance_to(o)
        local dx, dy, dz = self.x - (o.x or 0), self.y - (o.y or 0), self.z - (o.z or 0)
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    end
    return v
end

level = {
    name = function() return "l01_escape" end,
}
game = {
    translate_string = function(str) return str or "" end,
}
db = { actor = {} }

dofile("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_events.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_needs.script")

local sb = stalker_camp_builder
local fails = 0
local function eq(a, b, msg)
    if a ~= b then
        fails = fails + 1
        print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b))
    end
end

-- 1. Target Camp Selection
eq(sb.find_retaliation_target_camp("dolg"), nil, "no camps returns nil")

sb.active_camps[101] = { level = "l02_garbage", survivors = { [1] = {} } }
sb.active_camps[102] = { level = "l01_escape", survivors = { [2] = {}, [3] = {} } }
eq(sb.find_retaliation_target_camp("dolg"), 102, "prefers camp on current level with survivors")

sb.active_camps[103] = { level = "l03_agroprom", survivors = { [4] = {} }, is_primary = true }
eq(sb.find_retaliation_target_camp("dolg"), 103, "prefers primary camp")

-- 2. Retaliation Queueing
sb.queue_faction_retaliation("monster", 102)
eq(sb.faction_retaliation_timers["monster"], nil, "monsters do not retaliate")

sb.queue_faction_retaliation("zombied", 102)
eq(sb.faction_retaliation_timers["zombied"], nil, "zombies do not retaliate")

sb.queue_faction_retaliation("dolg", 102)
local dolg_timer = sb.faction_retaliation_timers["dolg"]
eq(type(dolg_timer), "number", "dolg timer queued")
eq(dolg_timer >= now + 7200 and dolg_timer <= now + 14400, true, "timer within 2-4 hours")
eq(sb.faction_retaliation_targets["dolg"], 102, "target camp recorded")

-- Duplicate queue does not overwrite earlier timer
sb.queue_faction_retaliation("dolg", 103)
eq(sb.faction_retaliation_timers["dolg"], dolg_timer, "timer not overwritten")
eq(sb.faction_retaliation_targets["dolg"], 102, "target not overwritten")

-- 3. Offline Resolution
local camp_high_def = { name = "Fortress", happiness = 80, survivors = { [1] = {} } }
sb.get_camp_stats = function(c) return { defense = 35 } end
sb.resolve_offline_retaliation(102, camp_high_def, "dolg")
eq(camp_high_def.happiness, 80, "high defense repels raid without happiness loss")

local camp_low_def = { name = "Outpost", happiness = 70, survivors = { [1] = {}, [2] = {}, [3] = {} } }
sb.get_camp_stats = function(c) return { defense = 10 } end
sb.resolve_offline_retaliation(101, camp_low_def, "dolg")
eq(camp_low_def.happiness, 55, "low defense breached: loses 15 happiness")
eq(camp_low_def.survivors[1].needs_hungry_until ~= nil, true, "survivor 1 affected by breach")
eq(camp_low_def.survivors[2].needs_hungry_until ~= nil, true, "survivor 2 affected by breach (no early break)")
eq(camp_low_def.survivors[3].needs_hungry_until ~= nil, true, "survivor 3 affected by breach (no early break)")

-- 4. Guard Ammo Consumption
local ammo_boxes = 2
sb.find_and_consume_item = function(hub, c, check_fn)
    if ammo_boxes > 0 and check_fn("ammo_5.45x39_fmj") then
        ammo_boxes = ammo_boxes - 1
        return "ammo_5.45x39_fmj"
    end
    return nil
end

local camp_guards = { survivors = {} }
-- 2 guards, 2 ammo boxes available -> 1.0 full defense
local mult = sb.needs_process_guard_ammo(101, camp_guards, 2)
eq(mult, 1.0, "2 guards with 2 boxes: full 1.0 defense")
eq(ammo_boxes, 0, "ammo consumed")

-- 4 guards, 0 ammo boxes available -> 0.5 deficit defense
mult = sb.needs_process_guard_ammo(101, camp_guards, 4)
eq(mult, 0.5, "4 guards with 0 boxes: 0.5 defense mult")

-- 5. Retaliation Raid Cooldown Bypass, Failed Spawn Retry, and Untouched Alarm Auto-On
do
    local vpos = vector():set(10, 0, 10)
    db.actor = {
        position = function() return vpos end,
        character_community = function() return "actor_stalker" end,
        game_vertex_id = function() return 1 end,
    }
    ini_sys = { section_exist = function() return true end }
    game_object = { enemy = 2 }
    character_community = function() return "actor_stalker" end
    CreateTimeEvent = function() end
    sound_object = function() return { play_at_pos = function() end } end
    local allow_spawn_pos = false
    local toggled_alarms = {}
    local objs = {
        [201] = { position = vpos },
        [202] = { position = vpos },
        [501] = { position = vpos },
    }
    alife = function() return {} end
    alife_object = function(id) return objs[id] end
    level.vertex_id = function() return 1 end
    level.vertex_position = function() return vpos end
    level.object_by_id = function() return nil end
    sb.get_ground_vertex_and_pos = function()
        if not allow_spawn_pos then return nil, nil end
        return 1, vector():set(70, 0, 10)
    end
    local sq_id = 900
    sb.create_squad_at_pos = function()
        sq_id = sq_id + 1
        local sq = { id = sq_id }
        objs[sq_id] = sq
        return sq
    end
    sb.get_dynamic_squad_section_for_faction = function(fac) return fac .. "_sim_squad_veteran" end
    sb.safe_squad_members = function(sq)
        local sent = false
        return function()
            if sent or not sq then return nil end
            sent = true
            return { id = sq.id * 10, object = { alive = function() return true end } }
        end
    end
    sb.get_camp_label = function(c) return c.name or "Camp" end
    sb.camp_send_tip = function() end
    sb.add_camp_radio_log = function() end
    sb.camp_attackers = function() return {} end
    hf_obj_manager = { get_data = function() return nil end }
    bind_alarm_system = { toggle_alarm_system = function(id) toggled_alarms[id] = true end }

    sb.cfg.event_player_dist = 150
    sb.cfg.raid_cooldown = 1000
    sb.active_camps = {
        [201] = {
            name = "Alpha", level = "l01_escape",
            survivors = { [11] = { job = "guard" } },
            structures = { [501] = "alarm" },
            pending_retaliation = { faction = "dolg", due_sec = now },
        },
        [202] = {
            name = "Beta", level = "l01_escape",
            survivors = { [12] = { job = "guard" } },
            structures = {},
        },
    }

    -- Failed spawn preserves pending_retaliation and keeps nil bootstrap intact
    sb.set_event_timers(nil, nil)
    sb.process_camp_raids()
    eq(sb.active_camps[201].pending_retaliation ~= nil, true, "failed raid spawn keeps pending_retaliation")
    eq(sb.active_camps[201].active_raid, nil, "failed spawn sets no active_raid")

    -- Retry succeeds while global timer is still nil (bypasses nil bootstrap) and activates untouched alarm (data == nil)
    allow_spawn_pos = true
    sb.set_event_timers(nil, nil)
    sb.process_camp_raids()
    eq(sb.active_camps[201].pending_retaliation, nil, "successful retaliation spawn clears pending_retaliation")
    eq(sb.active_camps[201].active_raid ~= nil, true, "retaliation active_raid created")
    eq(sb.active_camps[201].active_raid.is_retaliation, true, "marked as retaliation")
    eq(toggled_alarms[501], true, "untouched alarm with nil data switched ON during raid")
    local raid_ts = sb.get_event_timers()
    eq(raid_ts, now, "last_raid_game_sec stamped on successful retaliation")

    -- Pending retaliation on camp 202 also bypasses active raid_cooldown
    now = now + 20 -- well under raid_cooldown = 1000
    sb.active_camps[202].pending_retaliation = { faction = "bandit", due_sec = now }
    sb.process_camp_raids()
    eq(sb.active_camps[202].pending_retaliation, nil, "second retaliation bypassed active raid_cooldown")
    eq(sb.active_camps[202].active_raid ~= nil, true, "second retaliation spawned under cooldown")
end

print(fails == 0 and "all retaliation tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
