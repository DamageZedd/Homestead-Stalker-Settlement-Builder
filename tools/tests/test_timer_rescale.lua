-- When game_timer_scale changes, stored timers keep their share of the interval (no early or late round).
-- Run: lua tools/tests/test_timer_rescale.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder.script", "rb"):read("*a")
local body = assert(src:match("(local ELAPSED_STAMPS.-\nfunction stalker_camp_builder%.sync_timer_scale.-\nend)"), "sync block")
local fails = 0
local function eq(a, b, m) if math.abs(a - b) > 1e-6 then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
local NOW, SCALE = 1000000, 1
stalker_camp_builder = { game_sec = function() return NOW end }
local raid, event = NOW - 6000, NOW - 600
stalker_camp_builder.get_event_timers = function() return raid, event end
stalker_camp_builder.set_event_timers = function(r, e) raid, event = r, e end
local env = setmetatable({ stalker_camp_builder = stalker_camp_builder, game_timer_scale = function() return SCALE end }, { __index = _G })
setfenv(loadstring(body), env)()
local sync = stalker_camp_builder.sync_timer_scale
local function camp()
    return { last_water_time = NOW - 3600, last_food_consumption_time = NOW - 43200, setup_sec = NOW - 7200, setup_duration = 36000,
        skirmish_cooldown_until = NOW + 12000, needs = { last_round_sec = NOW - 43200, grace_until = NOW + 86400, until_sec = NOW + 20000 },
        survivors = { [1] = { last_equip_check = NOW - 900, needs_hungry_until = NOW + 4000 } } }
end
-- an old save (no timer_scale) loaded under RTZ: scale 1 -> 1/6; half a meal round done stays half done
SCALE = 1 / 6
local c = camp(); sync(c)
eq(c.timer_scale, 1 / 6, "scale recorded")
eq(NOW - c.last_food_consumption_time, 43200 / 6, "elapsed meal time shrinks with the interval (half of 4 real hours)")
eq(NOW - c.last_water_time, 600, "pump elapsed")
eq(c.needs.until_sec - NOW, 20000 / 6, "needs window remaining")
eq(c.needs.grace_until - NOW, 86400 / 6, "grace remaining")
eq(c.setup_duration, 6000, "rolled garrison stay")
eq(NOW - c.setup_sec, 1200, "garrison age")
eq(c.skirmish_cooldown_until - NOW, 2000, "skirmish cooldown remaining")
eq(c.survivors[1].last_equip_check, NOW - 150, "equipment check elapsed")
eq(c.survivors[1].needs_hungry_until - NOW, 4000 / 6, "hungry window")
eq(NOW - raid, 1000, "global raid stamp")
eq(NOW - event, 100, "global event stamp")
-- the same scale again changes nothing
local before = c.last_food_consumption_time
sync(c); eq(c.last_food_consumption_time, before, "second sync is a no-op")
-- a save made under 1/6 loaded without RTZ: back to 1
SCALE = 1
sync(c)
eq(NOW - c.last_food_consumption_time, 43200, "back to the unscaled elapsed time")
eq(c.setup_duration, 36000, "garrison stay restored")
-- a camp that never had timers is left alone
local e = { survivors = {} }; SCALE = 0.5; sync(e); eq(e.timer_scale, 0.5, "empty camp records the scale")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("timer rescale OK")
