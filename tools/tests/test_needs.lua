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
eq(sb.needs_class_of("meat_dog_raw"), "raw", "raw meat")
eq(sb.needs_class_of("bandage"), nil, "bandage is no food")
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

print(fails == 0 and "all needs tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
