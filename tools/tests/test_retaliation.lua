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
    function v:distance_to(o) return 0 end
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

local camp_low_def = { name = "Outpost", happiness = 70, survivors = { [1] = {} } }
sb.get_camp_stats = function(c) return { defense = 10 } end
sb.resolve_offline_retaliation(101, camp_low_def, "dolg")
eq(camp_low_def.happiness, 55, "low defense breached: loses 15 happiness")
eq(camp_low_def.survivors[1].needs_hungry_until ~= nil, true, "survivor affected by breach")

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

print(fails == 0 and "all retaliation tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
