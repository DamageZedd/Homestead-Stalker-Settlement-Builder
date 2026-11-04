-- Standalone test for stalker_camp_builder.time_factor (the game-seconds-per-real-second used to
-- convert game spans to real ones), with a stubbed engine and Real Time Zones.
-- Run: lua tools/tests/test_time_factor.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder.script", "rb"):read("*a")
local body = src:match("(function time_factor%(%).-\nend)")
assert(body, "time_factor not found")
local jbody = src:match("(function job_game_elapsed_sec%(.-\nend)")
assert(jbody, "job_game_elapsed_sec not found")
local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end
local function run(engine_tf, rtz)
    level = engine_tf and { get_time_factor = function() return engine_tf end } or nil
    rtz_mcm = rtz and { get_config = function(k) return rtz[k] end } or nil
    local env = setmetatable({}, { __index = _G })
    setfenv(loadstring(body), env)()
    return env.time_factor()
end
local on = { enabled = true, lock_time_factor = true, time_factor_val = 1.0 }

eq(run(10, nil), 10, "vanilla keeps the engine factor")
eq(run(0.1, nil), 0.1, "no RTZ: engine factor untouched")
eq(run(nil, nil), 10, "no level: default")
eq(run(0, nil), 10, "zero factor: default")
eq(run(1, on), 1, "RTZ normal")
eq(run(0.1, on), 1, "RTZ catch-up 0.1 floors at the configured factor")
eq(run(10, on), 10, "RTZ emission factor passes")
eq(run(0.1, { enabled = false, lock_time_factor = true, time_factor_val = 1.0 }), 0.1, "RTZ disabled")
eq(run(0.1, { enabled = true, lock_time_factor = false, time_factor_val = 1.0 }), 0.1, "RTZ factor not locked")

local function elapsed(rtz)
    rtz_mcm = rtz and { get_config = function(k) return rtz[k] end } or nil
    local env = setmetatable({}, { __index = _G })
    setfenv(loadstring(jbody), env)()
    return env.job_game_elapsed_sec({ job_start_time = 1000 }, 1600, 2)
end
eq(elapsed(nil), 300, "no RTZ: game span / factor")
eq(elapsed({ enabled = true, sync_clock = true }), 0, "RTZ clock sync: game span ignored")
eq(elapsed({ enabled = true, sync_clock = false }), 300, "RTZ without sync")
eq(elapsed({ enabled = false, sync_clock = true }), 300, "RTZ disabled")
-- No Real Time Zones installed: rtz_mcm is an undefined global (nil, as for any absent optional mod,
-- the same guard axr_main / ap_api / mac_mcm use). Output must equal the pre-RTZ formulas exactly.
local function old_tf(engine_tf)
    local lv = engine_tf ~= nil and { get_time_factor = function() return engine_tf end } or nil
    local tf = (lv and lv.get_time_factor and lv.get_time_factor()) or 10
    if tf <= 0 then tf = 10 end
    return tf
end
local function old_raider_tf(engine_tf)
    local lv = engine_tf ~= nil and { get_time_factor = function() return engine_tf end } or nil
    local tf = lv and lv.get_time_factor and lv.get_time_factor() or 10
    return tf > 0 and tf or 10
end
for _, f in ipairs({ 0, 0.1, 0.5, 1, 2, 6, 10, 60, -5 }) do
    eq(run(f, nil), old_tf(f), "no RTZ identical to old formula, factor " .. f)
    eq(run(f, nil), old_raider_tf(f), "no RTZ identical to old raider formula, factor " .. f)
    rtz_mcm = nil
    local env = setmetatable({}, { __index = _G })
    setfenv(loadstring(jbody), env)()
    local tf = run(f, nil)
    eq(env.job_game_elapsed_sec({ job_start_time = 1000 }, 1600, tf), math.max(0, (1600 - 1000) / old_tf(f)), "no RTZ elapsed, factor " .. f)
    eq(env.job_game_elapsed_sec({ job_start_time = 1000 }, 400, tf), 0, "no RTZ elapsed clamps at 0, factor " .. f)
    eq(env.job_game_elapsed_sec({}, 1600, tf), 0, "no RTZ elapsed without start, factor " .. f)
end
eq(run(nil, nil), old_tf(nil), "no RTZ, no level")
-- RTZ present and locked: floored at the configured factor, never below the engine's
for _, f in ipairs({ 0, 0.1, 1, 6, 10, 60 }) do
    eq(run(f, { enabled = true, lock_time_factor = true, time_factor_val = 6 }), math.max(f, 6), "RTZ floor, factor " .. f)
end
if fails > 0 then print(fails .. " failure(s)"); os.exit(1) end
print("test_time_factor: ok")
