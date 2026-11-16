-- Standalone tests for the pure rules in stalker_camp_builder_needs.script.
-- Run: lua tools/tests/test_needs.lua   (Lua 5.1, from the repo root)
stalker_camp_builder = { cfg = {} }
dofile("00_Core/gamedata/scripts/stalker_camp_builder_needs.script")
local sb = stalker_camp_builder
local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end

-- classes
eq(sb.needs_class_of("bread"), "staple", "bread")
eq(sb.needs_class_of("kolbasa"), "protein", "kolbasa")
eq(sb.needs_class_of("vodka"), "comfort", "vodka is comfort food")
eq(sb.needs_class_of("water_drink"), "water", "water")
eq(sb.needs_class_of("meat_dog"), "protein", "cooked meat is protein")
eq(sb.needs_class_of("bandage"), nil, "bandage is no food")
eq(sb.needs_class_of("mutant_part_dog_meat"), "raw", "raw meat is the raw class")
eq(sb.needs_class_of("mutant_part_dog_tail"), nil, "a tail is no food")
eq(sb.needs_class_of(nil), nil, "nil")

-- catch-up: a long sleep costs at most the cap
eq(sb.needs_rounds_due(86399, 86400, 1), 0, "not yet due")
eq(sb.needs_rounds_due(86400, 86400, 1), 1, "due")
eq(sb.needs_rounds_due(86400 * 5, 86400, 1), 1, "5 days asleep, cap 1")
eq(sb.needs_rounds_due(86400 * 5, 86400, 3), 3, "5 days asleep, cap 3")
eq(sb.needs_rounds_due(86400 * 2, 86400, 3), 2, "2 days asleep, cap 3")
eq(sb.needs_rounds_due(nil, 86400, 1), 0, "nil elapsed")

-- tiers and penalties
eq(sb.needs_tier(0, 0), 0, "fed")
eq(sb.needs_tier(2, 1), 2, "short")
eq(sb.needs_tier(1, 2), 3, "starving")
eq(sb.needs_penalty(0, 0, 3, true), 5, "variety bonus")
eq(sb.needs_penalty(0, 0, 3, false), 0, "variety bonus off")
eq(sb.needs_penalty(0, 0, 1, true), 0, "lean camp no penalty")
eq(sb.needs_penalty(2, 2, 0, true), -10, "2 unserved")
eq(sb.needs_penalty(2, 9, 0, true), -20, "unserved cap")
eq(sb.needs_penalty(3, 9, 0, true), -35, "total cap")
eq(sb.needs_penalty(3, 1, 0, true), -30, "starving + 1")

-- a stocked pantry: counts per class, drawing like the engine does
local function pantry(t)
    local io = { eaten = {}, drinks = t.water or 0 }
    io.eat = function(order)
        for _, c in ipairs(order) do
            if (t[c] or 0) > 0 then t[c] = t[c] - 1; io.eaten[#io.eaten + 1] = c; return c end
        end
    end
    io.drink = function() if io.drinks > 0 then io.drinks = io.drinks - 1; return true end return false end
    return io
end

-- fed and watered
local st = {}
local r = sb.needs_round(st, 3, {}, pantry({ staple = 9, water = 9 }))
eq(r.tier, 0, "fed tier"); eq(r.fed, 3, "fed 3"); eq(r.penalty, 0, "no penalty fed")

-- no water, no pump: everyone unserved
st = {}
r = sb.needs_round(st, 3, {}, pantry({ staple = 9 }))
eq(r.no_water, 3, "no water"); eq(r.unserved, 3, "3 unserved"); eq(r.tier, 2, "short"); eq(r.penalty, -15, "-15")
-- same, a second round in a row: starving
r = sb.needs_round(st, 3, {}, pantry({ staple = 9 }))
eq(r.tier, 3, "starving"); eq(r.penalty, -35, "starving penalty capped")

-- a pump supplies the water
st = {}
r = sb.needs_round(st, 3, { water_free = true }, pantry({ staple = 9 }))
eq(r.tier, 0, "pump means water"); eq(r.no_water, 0, "pump no_water")

-- no food at all
st = {}
r = sb.needs_round(st, 2, { water_free = true }, pantry({}))
eq(r.no_food, 2, "no food"); eq(r.tier, 2, "hungry tier")
-- recovery resets the streak
r = sb.needs_round(st, 2, { water_free = true }, pantry({ staple = 5 }))
eq(r.tier, 0, "recovered"); eq(st.short_rounds, 0, "streak reset")

-- grace: eats, but no penalty and the streak does not start
st = {}
r = sb.needs_round(st, 2, { water_free = true, grace = true }, pantry({}))
eq(r.penalty, 0, "grace penalty"); eq(r.tier, 0, "grace tier"); eq(st.short_rounds or 0, 0, "grace streak")

-- variety: three days of three classes earns the bonus; raw meat is last
st = {}
local io = pantry({ staple = 3, protein = 3, comfort = 3, raw = 3 })
local got = {}
for i = 1, 3 do r = sb.needs_round(st, 1, { water_free = true, variety_bonus = true }, io) end
eq(r.variety, 3, "variety 3"); eq(r.penalty, 5, "bonus earned")
for _, c in ipairs(io.eaten) do eq(c ~= "raw", true, "raw meat left alone") end

-- raw meat is the fallback
st = {}
r = sb.needs_round(st, 1, { water_free = true }, pantry({ raw = 1 }))
eq(r.fed, 1, "raw is eaten when nothing else is there")

-- consumption multiplier: 0.5 x 2 settlers = 1 ration, fractions carry over
st = {}
io = pantry({ staple = 9 })
sb.needs_round(st, 3, { water_free = true, mult = 0.5 }, io)
eq(#io.eaten, 1, "1.5 -> 1 ration"); sb.needs_round(st, 3, { water_free = true, mult = 0.5 }, io)
eq(#io.eaten, 3, "carry makes 3 over two rounds")

-- consequences (phase 4), with a stubbed clock and config
local now = 1000
sb.game_sec = function() return now end
sb.cfg = { needs_enabled = true }
local camp = { survivors = {
    [1] = { job = "craft" }, [2] = { job = "repair" }, [3] = { job = "farmer" }, [4] = { job = "guard" }, [5] = { job = "medic" },
} }
sb.needs_mark_settlers(camp, { tier = 2, unserved = 2 }, now, 86400)
eq(camp.survivors[1].needs_hungry_until ~= nil, true, "first worker hungry")
eq(camp.survivors[2].needs_hungry_until ~= nil, true, "second worker hungry")
eq(camp.survivors[5].needs_hungry_until, nil, "only two marked")
eq(camp.survivors[3].needs_hungry_until, nil, "farmer never refuses")
eq(camp.survivors[4].needs_hungry_until, nil, "guard not marked")
eq(sb.needs_job_refused(camp.survivors[1]), true, "hungry craft refuses")
eq(sb.needs_job_refused(camp.survivors[3]), false, "farmer works")
eq(sb.needs_starving(camp.survivors[1]), false, "tier 2 still pays")
now = 1000 + 86400
eq(sb.needs_job_refused(camp.survivors[1]), false, "refusal lapses")
now = 1000
sb.cfg.needs_job_refusal = false
eq(sb.needs_job_refused(camp.survivors[1]), false, "refusal option off")
sb.cfg.needs_job_refusal = nil
sb.cfg.needs_enabled = false
eq(sb.needs_job_refused(camp.survivors[1]), false, "master off")
sb.cfg.needs_enabled = true

sb.needs_mark_settlers(camp, { tier = 3, unserved = 1 }, now, 86400)
eq(sb.needs_starving(camp.survivors[4]), true, "starving camp pays no cut, guard too")
eq(camp.survivors[2].needs_hungry_until, nil, "marks are rebuilt each round")

camp.needs = { tier = 3, until_sec = now + 100, penalty = -30 }
eq(sb.needs_guard_mult(camp), 0.6, "starving guards x0.6")
sb.cfg.needs_guard_penalty = false
eq(sb.needs_guard_mult(camp), 1, "guard option off")
sb.cfg.needs_guard_penalty = nil
camp.needs.tier = 2
eq(sb.needs_guard_mult(camp), 1, "short is not starving")
camp.needs.tier = 3; now = now + 200
eq(sb.needs_guard_mult(camp), 1, "lapsed round")
now = 1000
eq(sb.needs_blocks_desertion(camp), false, "desertion allowed by default")
sb.cfg.needs_desertion = false
eq(sb.needs_blocks_desertion(camp), true, "shortage morale cannot drive settlers away")
camp.needs.penalty = 5
eq(sb.needs_blocks_desertion(camp), false, "no shortage, no block")

-- Phase 5: medical supplies & guard ammo
eq(sb.needs_is_med("bandage"), true, "bandage is med")
eq(sb.needs_is_med("medkit_army"), true, "medkit_army is med")
eq(sb.needs_is_med("stimpack"), true, "stimpack is med")
eq(sb.needs_is_med("bread"), false, "bread is not med")

eq(sb.needs_is_ammo("ammo_5.45x39_fmj"), true, "ammo 5.45 is ammo")
eq(sb.needs_is_ammo("ammo_12x70_buck"), true, "buckshot is ammo")
eq(sb.needs_is_ammo("ammo_battery"), false, "battery is not ammo")
eq(sb.needs_is_ammo("vodka"), false, "vodka is not ammo")

-- medical gap penalty
eq(sb.needs_penalty(0, 0, 0, false, true), -10, "medical gap penalty on fed camp")
eq(sb.needs_penalty(2, 2, 0, false, true), -20, "tier 2 (-10) + med gap (-10) = -20")
eq(sb.needs_penalty(3, 2, 0, false, true), -35, "penalty capped at -35")

-- wounded treatment in needs_round
st = {}
local med_stock = 2
local io_med = pantry({ staple = 5 })
io_med.med = function()
    if med_stock > 0 then med_stock = med_stock - 1; return true end
    return false
end
r = sb.needs_round(st, 2, { water_free = true, wounded_count = 2 }, io_med)
eq(r.treated, 2, "2 wounded treated")
eq(r.medical_gap, false, "no medical gap when treated")
eq(med_stock, 0, "all 2 med used")

-- medical gap when shortage
st = {}
r = sb.needs_round(st, 2, { water_free = true, wounded_count = 2 }, io_med)
eq(r.treated, 0, "0 treated, med empty")
eq(r.medical_gap, true, "medical gap triggered")
eq(r.penalty, -10, "penalty reflects med gap")

-- wounded check
local surv_w = { wounded_until = 2000 }
local surv_rw = { raider = { wounded_until = 2000 } }
local surv_ok = {}
now = 1500
eq(sb.needs_is_wounded(surv_w), true, "settler wounded")
eq(sb.needs_is_wounded(surv_rw), true, "raider wounded")
eq(sb.needs_is_wounded(surv_ok), false, "healthy settler")
now = 2500
eq(sb.needs_is_wounded(surv_w), false, "wound healed after time")

-- guard ammo consumption
local ammo_in_box = 3
sb.find_and_consume_item = function(hub, c, check_fn)
    if ammo_in_box > 0 and check_fn("ammo_9x18_fmj") then
        ammo_in_box = ammo_in_box - 1
        return "ammo_9x18_fmj"
    end
    return nil
end
local test_c = { survivors = {} }
local def_mult = sb.needs_process_guard_ammo(1, test_c, 3)
eq(def_mult, 1.0, "3 guards fed 3 ammo boxes: full defense")
eq(ammo_in_box, 0, "ammo box empty now")
def_mult = sb.needs_process_guard_ammo(1, test_c, 4)
eq(def_mult, 0.5, "4 guards with 0 ammo boxes: 0.5 defense mult")

-- starving check
now = 1000
local surv_starving = { needs_starving_until = 1500 }
local surv_normal = {}
local camp_starving = { needs = { tier = 3, until_sec = 2000 } }
local camp_short = { needs = { tier = 2, until_sec = 2000 } }
eq(sb.needs_is_starving(surv_starving, nil), true, "survivor starving until")
eq(sb.needs_is_starving(surv_normal, camp_starving), true, "camp starving tier 3")
eq(sb.needs_is_starving(surv_normal, camp_short), false, "camp tier 2 not starving")

sb.cfg.needs_production_penalty = false
eq(sb.needs_is_starving(surv_starving, camp_starving), false, "penalty off in mcm")
sb.cfg.needs_production_penalty = true

-- test get_job_rt_interval scaling
sb.cfg.realtime_job_cook_interval = 900
vector = vector or function() return { x = 0, y = 0, z = 0 } end
dofile("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
eq(sb.get_job_rt_interval("cook", surv_normal, camp_short), 900, "cook normal interval")
eq(sb.get_job_rt_interval("cook", surv_w, camp_short), 1800, "cook wounded interval x2")
eq(sb.get_job_rt_interval("cook", surv_normal, camp_starving), 1800, "cook starving interval x2")
eq(sb.get_job_rt_interval("cook", surv_w, camp_starving), 3600, "cook wounded + starving interval x4")

-- regression: needs_process called flag_on before its local was declared (a nil global), so the
-- needs round errored for every camp with settlers
db = db or {}
local np_ok, np_err = pcall(sb.needs_process, 1, { hub_id = 1, needs = { last_round_sec = now - 86400 * 10, round = 0, short_rounds = 0 }, survivors = { [7] = { name = "A", job = "cook", wounded_until = 2000 } } })
eq(np_ok, true, "needs_process runs for a camp with settlers (" .. tostring(np_err) .. ")")

-- regression: multi-round catch-up in needs_process must accumulate treated and decrement wounded_count
local prev_find = sb.find_and_consume_item
local prev_tip = sb.camp_send_tip
local prev_actor = db.actor
game = game or {}
game.translate_string = game.translate_string or function(k) return k end

local stock = { bread = 6, medkit = 1 }
sb.find_and_consume_item = function(_, _, check_fn)
    if stock.bread > 0 and check_fn("bread") then stock.bread = stock.bread - 1; return "bread" end
    if stock.medkit > 0 and check_fn("medkit") then stock.medkit = stock.medkit - 1; return "medkit" end
    return nil
end
local tips = {}
db.actor = {}
sb.camp_send_tip = function(_, text) tips[#tips + 1] = text end

now = 1000 + 86400 * 10
local catch_camp1 = {
    hub_id = 1,
    structures = { [10] = "water_pump" },
    needs = { last_round_sec = now - 86400 * 3, round = 0, short_rounds = 0 },
    survivors = {
        [1] = { name = "W1", job = "cook", wounded_until = now + 5000 },
    },
}
sb.needs_process(1, catch_camp1)
eq(catch_camp1.survivors[1].wounded_until, nil, "catch-up clears wounded_until when treated in round 1 of 3")
eq(catch_camp1.needs.penalty, 0, "no false medical_gap penalty on subsequent catch-up rounds after healing")
eq(catch_camp1.needs.last_med_warn, nil, "no medical gap warning sent after settler already treated")

-- partial catch-up treatment: 2 wounded, 1 medkit, due=3 -> 1 healed, 1 still wounded, unserved=1
stock = { bread = 6, medkit = 1 }
tips = {}
local catch_camp2 = {
    hub_id = 2,
    structures = { [11] = "water_pump" },
    needs = { last_round_sec = now - 86400 * 3, round = 0, short_rounds = 0 },
    survivors = {
        [1] = { name = "W1", job = "cook", wounded_until = now + 5000 },
        [2] = { name = "W2", job = "medic", wounded_until = now + 5000 },
    },
}
sb.needs_process(2, catch_camp2)
local healed_count, still_wounded = 0, 0
for _, sv in pairs(catch_camp2.survivors) do
    if sv.wounded_until == nil then healed_count = healed_count + 1 else still_wounded = still_wounded + 1 end
end
eq(healed_count, 1, "catch-up heals 1 of 2 wounded even when last round had 0 medkits")
eq(still_wounded, 1, "remaining wounded stays wounded")
eq(catch_camp2.needs.penalty, -10, "medical gap penalty still applies for remaining unserved wounded")
eq(catch_camp2.needs.last_med_warn, now, "medical gap warning recorded")

sb.find_and_consume_item = prev_find
sb.camp_send_tip = prev_tip
db.actor = prev_actor

print(fails == 0 and "all needs tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
