-- Standalone test for stalker_camp_builder.time_factor (the game-seconds-per-real-second used to
-- convert game spans to real ones), with a stubbed engine and Real Time Zones.
-- Run: lua tools/tests/test_time_factor.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder.script", "rb"):read("*a")
local body = src:match("(function time_factor%(%).-\nend)")
assert(body, "time_factor not found")
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
if fails > 0 then print(fails .. " failure(s)"); os.exit(1) end
print("test_time_factor: ok")
