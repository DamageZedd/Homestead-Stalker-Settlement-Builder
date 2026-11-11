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

if fails > 0 then print("test_rivals_events_perf: " .. fails .. " FAILED"); os.exit(1) end
print("test_rivals_events_perf: all passed")
