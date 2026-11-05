-- Game-time timers follow real time under Real Time Zones (factor locked at 1): scale = tf / 6, never above 1.
-- Run: lua tools/tests/test_game_timer_scale.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder.script", "rb"):read("*a")
local tf_body = assert(src:match("(function time_factor%(%).-\nend)"), "time_factor")
local sc_body = assert(src:match("(local TIMER_REFERENCE_TF = 6.-\nstalker_camp_builder%.game_timer_scale = game_timer_scale)"), "game_timer_scale")
local keys_body = assert(src:match("(local GAME_TIMER_KEYS = %b{})"), "GAME_TIMER_KEYS")
local fails = 0
local function eq(a, b, m) if math.abs(a - b) > 1e-9 then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
local function scale(engine_tf, rtz)
    level = engine_tf and { get_time_factor = function() return engine_tf end } or nil
    rtz_mcm = rtz and { get_config = function(k) return rtz[k] end } or nil
    stalker_camp_builder = {}
    local env = setmetatable({ stalker_camp_builder = stalker_camp_builder }, { __index = _G })
    setfenv(loadstring(tf_body .. "\n" .. sc_body .. "\nreturn game_timer_scale()"), env)
    return setfenv(loadstring(tf_body .. "\n" .. sc_body .. "\nreturn game_timer_scale()"), env)()
end
local on = { enabled = true, lock_time_factor = true, time_factor_val = 1.0 }
eq(scale(1, on), 1 / 6, "RTZ locked at 1: a 24 h round takes 4 real hours")
eq(scale(0.1, on), 1 / 6, "RTZ catch-up 0.1 floors at the configured factor")
eq(scale(10, on), 1, "RTZ emission factor: unchanged")
eq(scale(6, nil), 1, "no RTZ, factor 6")
eq(scale(1, nil), 1, "no RTZ: the player's own factor is left alone")
eq(scale(10, nil), 1, "no RTZ, factor 10")
eq(scale(1, { enabled = false, lock_time_factor = true, time_factor_val = 1.0 }), 1, "RTZ disabled")
eq(scale(1, { enabled = true, lock_time_factor = false, time_factor_val = 1.0 }), 1, "RTZ factor not locked")
eq(scale(1, { enabled = true, lock_time_factor = true, time_factor_val = 3.0 }), 0.5, "RTZ locked at 3")
-- the shortened keys are the game-time ones, and none is a real-time job interval
local keys = loadstring("local " .. keys_body:gsub("^local ", "") .. " return GAME_TIMER_KEYS")
local K = setfenv(loadstring("local GAME_TIMER_KEYS = " .. keys_body:match("%b{}") .. " return GAME_TIMER_KEYS"), {})()
for _, k in ipairs({ "water_interval", "fridge_interval", "food_consumption_interval", "raid_cooldown", "event_cooldown", "trader_despawn_time" }) do
    eq(K[k] and 1 or 0, 1, k .. " is scaled")
end
for _, k in ipairs({ "realtime_job_cook_interval", "raiders_rest_minutes", "raiders_wounded_minutes" }) do
    eq(K[k] and 1 or 0, 0, k .. " is not scaled")
end
-- rival tier hours, the skirmish cooldown and the equipment check use the same scale
local function rd(n) return io.open("00_Core/gamedata/scripts/" .. n, "rb"):read("*a") end
local rivals, jobs = rd("stalker_camp_builder_rivals.script"), rd("stalker_camp_builder_jobs.script")
local function count(s, pat) local n = 0; for _ in s:gmatch(pat) do n = n + 1 end; return n end
eq(count(rivals, "21600 %* sb%.game_timer_scale%(%)"), 4, "skirmish cooldown sites scaled")
eq(rivals:find("/ 3600 / sb.game_timer_scale()", 1, true) and 1 or 0, 1, "tier age scaled")
eq(jobs:find("1800 * sb.game_timer_scale()", 1, true) and 1 or 0, 1, "equipment check scaled")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("game timer scale OK")
