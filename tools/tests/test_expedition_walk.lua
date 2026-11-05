-- Expedition walk time follows real time under Real Time Zones. Run: lua tools/tests/test_expedition_walk.lua
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_expeditions.script", "rb"):read("*a")
local walk = assert(src:match("(local function get_self_contained_duration_sec.-\nend)"), "duration fn")
local resc = assert(src:match("(function stalker_camp_builder%.rescale_expedition.-\nend)"), "rescale fn")
local fails = 0
local function eq(a, b, m) if math.abs(a - b) > 1e-6 then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
local TF, SCALE = 6, 1
stalker_camp_builder = { time_factor = function() return TF end, game_timer_scale = function() return SCALE end, cfg = {} }
mfloor = math.floor
local env = setmetatable({ stalker_camp_builder = stalker_camp_builder, mfloor = math.floor }, { __index = _G })
local f = setfenv(loadstring(walk .. "\nreturn get_self_contained_duration_sec"), env)()
setfenv(loadstring(resc), env)()
-- 800 m out and back at 1.2 km/h = 2400 game seconds; plus 60 real seconds of search
local function real_min(tf, scale) TF, SCALE = tf, scale; return f(800, true, nil, 60 * tf) / tf / 60 end
eq(real_min(6, 1), 2400 / 6 / 60 + 1, "GAMMA factor 6, unchanged: 6.7 min walk + 1 min search")
eq(real_min(10, 1), 2400 / 10 / 60 + 1, "factor 10 without RTZ unchanged")
eq(real_min(1, 1 / 6), 2400 / 6 / 60 + 1, "RTZ factor 1: the same 6.7 min walk + 1 min search as factor 6 (was 41)")
-- minimum stays 3 real minutes on the same level
eq(f(30, true, nil, 0) / 1 / 60 >= 3 and 1 or 0, 1, "minimum still 3 real minutes at factor 1")
-- an expedition under way keeps its share of the trip when the scale drops
SCALE = 1 / 6
local exp = { start_sec = 1000, duration = 3000 }          -- 2000 s done of 3000, saved under scale 1
stalker_camp_builder.rescale_expedition(exp, 3000 - 1000 + 1000 - 1000 + 1000)
eq(exp.timer_scale, 1 / 6, "scale recorded")
eq(exp.duration, 2000 + (3000 - 2000) / 6, "remaining time shrinks")
local done = { start_sec = 0, duration = 100, timer_scale = 1 }
stalker_camp_builder.rescale_expedition(done, 500); eq(done.duration, 100, "a finished trip is left alone")
local fresh = { start_sec = 0, duration = 600, timer_scale = 1 / 6 }
stalker_camp_builder.rescale_expedition(fresh, 100); eq(fresh.duration, 600, "same scale: no change")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("expedition walk OK")
