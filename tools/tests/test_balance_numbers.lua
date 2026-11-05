-- Numbers check for the balance pass (docs/balance/). Reads the shipped defaults and MCM defaults straight from the
-- scripts, then asserts: MCM defaults equal the code defaults in the getter's units, job cycle times and the
-- Trader rate stay in range, every job's best-case output per real hour (all multipliers stacked) stays under a
-- ceiling, and the specialization table lists every stat a job reads.
-- Run: lua tools/tests/test_balance_numbers.lua   (Lua 5.1, from the repo root)
local SCRIPTS = "00_Core/gamedata/scripts/"
local function slurp(name) local f = assert(io.open(SCRIPTS .. name, "rb")); local s = f:read("*a"); f:close(); return s end
local main = slurp("stalker_camp_builder.script")
local mcm = slurp("stalker_camp_builder_mcm.script")
local jobs = slurp("stalker_camp_builder_jobs.script")

local fails = 0
local function check(cond, msg) if not cond then fails = fails + 1; print("FAIL " .. msg) end end
local function eq(a, b, msg) check(a == b, msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end

-- the code defaults ------------------------------------------------------------------------------------------
local block = main:match("local defaults = (%b{})\nstalker_camp_builder%.defaults = defaults")
assert(block, "defaults table not found")
local D = assert(loadstring("return " .. block))()

-- the MCM defaults: id -> def ---------------------------------------------------------------------------------
local M = {}
for line in mcm:gmatch("[^\n]+") do
    local id = line:match('id = "([%w_]+)"')
    local def = line:match("def = ([%w%.%-]+)")
    if id and def and def ~= "nil" then
        if def == "true" then M[id] = true elseif def == "false" then M[id] = false else M[id] = tonumber(def) end
    end
end

-- 1. MCM default == code default, in the units the getter converts to ---------------------------------------
local converted = {}
for id, v in pairs(M) do
    if type(v) == "number" then
        local base, unit = id:match("^(.*)_(min)$")
        if not base then base, unit = id:match("^(.*)_(hr)$") end
        local key, want
        if unit == "min" then key = base; want = v * 60 elseif unit == "hr" then key = base; want = v * 3600 end
        if key and D[key] ~= nil then
            converted[id] = true
            eq(D[key], want, "MCM " .. id .. " vs defaults." .. key)
        end
    end
end
local seen = 0
for id, v in pairs(M) do
    if not converted[id] and D[id] ~= nil and type(D[id]) == type(v) then
        seen = seen + 1
        eq(D[id], v, "MCM " .. id .. " vs defaults." .. id)
    end
end
check(seen > 40, "expected to compare many plain MCM defaults, compared " .. seen)
check(M.trader_price_percent == D.trader_price_percent, "trader price percent MCM vs code")

-- 2. cycle times: real seconds, sane range -------------------------------------------------------------------
for _, k in ipairs({ "realtime_job_cook_interval", "realtime_job_craft_interval", "realtime_job_repair_interval",
        "realtime_job_scavenge_interval", "realtime_job_hunter_interval", "realtime_job_woodcutter_interval",
        "realtime_job_brewer_interval", "realtime_job_scrapper_interval", "realtime_job_farmer_interval",
        "realtime_job_trader_interval", "medic_job_interval", "electrician_job_interval" }) do
    local v = D[k]
    check(type(v) == "number" and v >= 600 and v <= 2400, k .. " should be 10-40 real minutes, got " .. tostring(v))
end
-- the raid cooldown / wounded / rest settings are the user-facing tuned values: pin them
eq(D.raiders_rest_minutes, 20, "raiders rest minutes")
eq(D.raiders_wounded_minutes, 40, "raiders wounded minutes")
eq(D.raiders_max_per_day, 3, "raiders per day")
eq(D.raid_cooldown, 36 * 3600, "raid cooldown")

-- 3. Trader: must not pay more than the best GAMMA vendors (barman, mechanic, medic buy at 0.35) -----------------
local best_rate = D.trader_price_percent / 100 * 1.5   -- Skilled and above
check(D.trader_price_percent >= 10 and best_rate <= 0.40, "Trader best-case rate " .. best_rate .. " exceeds 40% of base cost")

-- 4. output ceilings -----------------------------------------------------------------------------------------
-- Base costs in RU from the installed GAMMA configs (average of the pools the jobs draw from; see
-- docs/balance/balance_analysis.md). Everything is stacked to the maximum: tier 3.0, best specialization, morale 1.1,
-- Drug-Making Kit x2, ammo bench +1, station bonuses, night speed-up.
local COST = {
    scav_item = 1000, meat = 736, hide = 1551, trophy = 1023, ammo_box = 1100, bandage = 1000, medkit = 2500,
    kalium = 3080, akvatab = 4524, wood = 132, vodka = 946, scrap = 50, fasteners = 73, bread = 600, charcoal = 1262,
}
local TIER, MORALE = 3.0, 1.1
local spec_max = {}
for _, spec in pairs(D.camp_specializations) do
    for stat, v in pairs(spec) do
        if type(v) == "number" and stat ~= "defense" and (not spec_max[stat] or v > spec_max[stat]) then spec_max[stat] = v end
    end
end
local function per_hour(batch_value, interval, night)
    return batch_value * 3600 / (interval / (night or 1))
end
local function randomized(lo, hi) return (lo + hi) / 2 end
local ceil = {}
local out = {}
local function job(name, ru_per_hour, limit, items_per_hour)
    out[#out + 1] = string.format("%-34s %9.0f RU/h  (ceiling %6d)%s", name, ru_per_hour, limit,
        items_per_hour and string.format("  %5.1f items/h", items_per_hour) or "")
    check(ru_per_hour <= limit, name .. " best case " .. math.floor(ru_per_hour) .. " RU/h exceeds ceiling " .. limit)
end

-- scavenge: no input, 20% ambush, night x1.2
do
    local mult = TIER * spec_max.scavenge * MORALE
    local items = randomized(D.scavenge_min_items, D.scavenge_max_items) * mult * (1 - D.scavenge_ambush_chance / 100)
    job("scavenge (master, hideout)", per_hour(items * COST.scav_item, D.realtime_job_scavenge_interval, 1.2), 14000,
        per_hour(items, D.realtime_job_scavenge_interval, 1.2))
end
-- hunter: tier capped at 1.5, station max+1 and x1.5, 75% pelt, 60% trophy
do
    local mult = math.min(1.5, TIER) * spec_max.hunter * MORALE * 1.5
    local meat = randomized(D.hunter_min_meat, D.hunter_max_meat + 1) * mult
    local value = (meat * COST.meat + 0.75 * COST.hide + 0.6 * COST.trophy) * (1 - D.hunter_ambush_chance / 100)
    job("hunter (master, hideout, station)", per_hour(value, D.realtime_job_hunter_interval), 16000)
end
-- craft: one box per cycle x tier x spec + bench; input-limited by powder from scavenging
do
    local boxes = math.floor(TIER * spec_max.craft * MORALE + 1)
    job("craft (master, workshop, bench)", per_hour(boxes * COST.ammo_box, D.realtime_job_craft_interval), 24000)
end
-- medic: rare types come 4 at a time and every unit pays its own inputs; bandages are room-limited (15)
do
    local mult = TIER * spec_max.medic * 2 * MORALE
    local akva = math.min(4, math.floor(mult + 0.5))   -- MEDIC_RARE_BATCH_MAX
    job("medic akvatab (clinic, drugkit)", per_hour(akva * COST.akvatab, D.medic_job_interval), 46000)
    local band = math.min(15, math.floor(mult + 0.5))
    job("medic bandage (clinic, drugkit)", per_hour(band * COST.bandage, D.medic_job_interval), 40000)
end
-- woodcutter: 40 cap
do
    local count = (math.max(D.yield_wood_min * 2, 1) + math.floor(D.yield_wood_max * 1.5 + 0.5)) / 2 + 2
    local n = math.min(40, count * TIER * 1.25 * MORALE)
    job("woodcutter (master, farm, station)", per_hour(n * COST.wood, D.realtime_job_woodcutter_interval), 18000)
end
-- brewer: 16 cap
do
    local n = math.min(16, (3 + 1 + 2) * TIER * 1.25 * MORALE)
    job("brewer (master, farm, distiller)", per_hour(n * COST.vodka, D.realtime_job_brewer_interval), 50000)
end
-- scrapper: 35 / 25 caps
do
    local s = (D.yield_scrap_min * 2 + math.floor(D.yield_scrap_max * 5 / 3 + 0.5)) / 2
    local f = (D.yield_fasteners_min * 2 + math.floor(D.yield_fasteners_max * 5 / 3 + 0.5)) / 2
    local m = TIER * 1.25 * MORALE
    local value = math.min(35, s * m) * COST.scrap + math.min(25, f * m) * COST.fasteners
    job("scrapper (master, workshop, tools)", per_hour(value, D.realtime_job_scrapper_interval), 10000)
end
-- farmer: bread, 8 cap per batch, two batches with a station
do
    local bread = math.min(8, math.floor(4 * 1.5 * MORALE + 0.5)) * 2
    job("farmer bread (farm, station)", per_hour(bread * COST.bread, D.realtime_job_farmer_interval), 32000)
end
-- food source against sink under Real Time Zones (timers scaled to factor 6 by game_timer_scale): 12 settlers eat 12 items
-- per meal round; a novice farmer with a stove makes 2 bread per 20 minutes per batch
do
    local round_real_h = D.food_consumption_interval / 3600 / 6         -- real hours per round at the scaled interval
    local need_per_h = 12 / round_real_h
    local farmer_per_h = 2 * 3600 / D.realtime_job_farmer_interval      -- one batch of 2 bread per cycle
    out[#out + 1] = string.format("RTZ food: 12 settlers need %.1f/h, one novice farmer makes %.1f/h", need_per_h, farmer_per_h)
    check(farmer_per_h / need_per_h <= 3, "one novice farmer oversupplies a camp of 12 more than 3x under RTZ")
end
-- hard caps in the code that the ceilings above rely on
check(jobs:find("math.min(math.floor(count * tier_mult * spec_mult * mult + 0.5), 40)", 1, true), "woodcutter 40 cap changed")
check(jobs:find("MEDIC_RARE_BATCH_MAX = 4", 1, true), "medic rare batch cap changed")
check(jobs:find("math.min(math.floor(count * total_mult + 0.5), 16)", 1, true), "brewer 16 cap changed")

-- 5. specialization table lists the stats the jobs read -------------------------------------------------------
local function spec_has(spec, stat) return type(D.camp_specializations[spec][stat]) == "number" end
for _, st in ipairs({ "woodcutter", "brewer" }) do check(spec_has("farm", st), "farm lacks " .. st) end
for _, st in ipairs({ "scrapper" }) do
    check(spec_has("workshop", st), "workshop lacks " .. st)
    check(spec_has("hideout", st), "hideout lacks " .. st)
end
for name, spec in pairs(D.camp_specializations) do
    for stat, v in pairs(spec) do
        if type(v) == "number" then check(v >= 0.5 and v <= 2.0, "specialization " .. name .. "." .. stat .. " out of range: " .. v) end
    end
end

for _, l in ipairs(out) do print(l) end
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("balance numbers OK")
