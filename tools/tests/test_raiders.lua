-- Standalone tests for the pure rules in stalker_camp_builder_raiders.script.
-- Run: lua tools/tests/test_raiders.lua   (Lua 5.1, from the repo root)
stalker_camp_builder = { cfg = {} }
dofile("00_Core/gamedata/scripts/stalker_camp_builder_raiders.script")
local sb = stalker_camp_builder
local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end
local function near(a, b, msg)
    if type(a) ~= "number" or math.abs(a - b) > 1e-6 then
        fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b))
    end
end

-- off by default
eq(sb.raiders_enabled(), false, "default off")
local info = { guards = 2, ready = 2, missions_today = 0 }
local target = { occupied = true, faction = "duty" }
local ok, why = sb.raiders_can_send(info, target)
eq(ok, false, "refused while off"); eq(why, "disabled", "reason disabled")
sb.cfg.raiders_enabled = true
eq(sb.raiders_can_send(info, target), true, "sendable when on")

-- target refusals
local function refused(t, i, reason, msg)
    local o, r = sb.raiders_can_send(i or info, t)
    eq(o, false, msg .. " refused"); eq(r, reason, msg .. " reason")
end
refused({ occupied = true, faction = "duty", story = true }, nil, "story", "story camp")
refused({ occupied = true, faction = "monster" }, nil, "empty", "monster")
refused({ occupied = true, faction = "duty", nest = true }, nil, "nest", "nest")
refused({ occupied = true, faction = "duty", own = true }, nil, "own", "own settlement")
refused({ occupied = false, faction = "duty" }, nil, "empty", "unoccupied")
refused({ occupied = true, faction = "duty", on_cooldown = true }, nil, "cooldown", "cooldown")
refused({ occupied = true, faction = "duty", friendly = true }, nil, "friendly", "friendly spared")
refused(target, { guards = 0, ready = 2, missions_today = 0 }, "no_guard", "no guard at home")
refused(target, { guards = 2, ready = 0, missions_today = 0 }, "no_raider", "no raider")
refused(target, { guards = 2, ready = 1, missions_today = 3 }, "daily", "daily cap")
sb.cfg.raiders_bandit_mode = true
eq(sb.raiders_can_send(info, { occupied = true, faction = "duty", friendly = true }), true, "bandit may rob friends")
sb.cfg.raiders_bandit_mode = nil

-- survivor readiness
eq(sb.raiders_survivor_ready({ rank_tier = 2 }, 100), true, "rank 2 ok")
local o, r = sb.raiders_survivor_ready({ rank_tier = 1 }, 100); eq(r, "rank", "rank 1 too low")
o, r = sb.raiders_survivor_ready({ rank_tier = 3, raider = { wounded_until = 500 } }, 100); eq(r, "wounded", "wounded")
eq(sb.raiders_survivor_ready({ rank_tier = 3, raider = { wounded_until = 50 } }, 100), true, "healed")
o, r = sb.raiders_survivor_ready({ rank_tier = 3, on_expedition = true }, 100); eq(r, "busy", "on expedition")
o, r = sb.raiders_survivor_ready({ rank_tier = 3, has_ammo = false }, 100); eq(r, "no_ammo", "no ammo")
o, r = sb.raiders_survivor_ready({ rank_tier = 3, raider = { rest_until = 200 } }, 100); eq(r, "resting", "resting")

-- guards: idle raider is half a guard
near(sb.raiders_effective_guards(2, 3), 3.5, "2 guards + 3 idle raiders")
near(sb.raiders_effective_guards(nil, nil), 0, "nil guards")

-- odds
near(sb.raid_odds(10, 10), 0.5, "even odds")
near(sb.raid_odds(100, 1), 0.90, "clamped high")
near(sb.raid_odds(1, 100), 0.05, "clamped low")
near(sb.raid_odds(0, 5), 0.05, "no attacker")
near(sb.raid_odds(5, 0), 0.90, "no defender")
local band = { { rank = 2, weapon_tier = 1, armor_tier = 1 }, { rank = 0 } }
near(sb.raiders_member_strength({ rank = 2, weapon_tier = 1, armor_tier = 1 }), 2 * 1.15 * 1.1, "member strength")
near(sb.raiders_band_strength(band), 2 * 1.15 * 1.1 + 1, "band strength")
near(sb.raiders_defender_strength(4, 2, 2), 4 * 1.4 + 1, "defender strength")
near(sb.raiders_defender_strength(4, 9, 0), 8, "tier clamps to 3")

-- outcome and casualties
eq(sb.raid_outcome(0.5, 0.4, 0.9), "success", "roll under odds wins")
eq(sb.raid_outcome(0.5, 0.6, 0.9), "repulsed", "loss, low disaster roll fails")
eq(sb.raid_outcome(0.5, 0.6, 0.1), "disaster", "loss, disaster roll")
eq(sb.raid_outcome(0.9, 0.95, 0.2), "repulsed", "good odds rarely disaster (15%)")
local c = sb.raid_casualties("success", 3, { 0, 0, 0 })
eq(#c.ok, 3, "success: all ok"); eq(#c.dead, 0, "success: none dead")
c = sb.raid_casualties("repulsed", 3, { 0, 0, 0 })
eq(#c.wounded, 3, "repulsed: all wounded"); eq(#c.dead, 0, "repulsed: nobody dies")
c = sb.raid_casualties("disaster", 3, { 0.1, 0.9, 0.49 })
eq(#c.dead, 2, "disaster: two die at 50%"); eq(c.wounded[1], 2, "disaster: the survivor is wounded")
c = sb.raid_casualties("disaster", 0, nil); eq(#c.dead + #c.wounded + #c.ok, 0, "empty band")
eq(sb.raiders_wounded_until(1000), 1000 + 12 * 3600, "wounded 12h default")
eq(sb.raiders_mission_duration(0), 1800, "min duration")
eq(sb.raiders_mission_duration(1e9), 4 * 3600, "max duration")

-- loot
local items = {
    { sec = "wpn_ak74", kind = "weapon", value = 3000 },
    { sec = "ammo_545", kind = "ammo", value = 100 },
    { sec = "bandage", kind = "med", value = 50 },
    { sec = "bread", kind = "food", value = 20 },
    { sec = "outfit_bandit", kind = "armor", value = 2000 },
}
local l = sb.raiders_loot_split(items)
eq(#l.taken, 3, "60% of 5 = 3 items"); eq(l.taken[1].sec, "ammo_545", "ammo first")
eq(l.taken[2].sec, "bandage", "meds second"); eq(l.taken[3].sec, "bread", "food third")
eq(#l.left, 2, "weapon and armor left"); eq(l.taken_value, 170, "taken value")
sb.cfg.raiders_forbid_weapon_armor = true
l = sb.raiders_loot_split(items)
eq(#l.taken, 2, "forbid: 60% of 3 = 2"); eq(#l.left, 3, "forbid: weapons and armor stay with the rest")
for _, it in ipairs(l.taken) do eq(it.kind == "weapon" or it.kind == "armor", false, "forbid: no weapon/armor taken") end
sb.cfg.raiders_forbid_weapon_armor = nil
eq(#sb.raiders_loot_split({}).taken, 0, "empty chest"); eq(#sb.raiders_loot_split(nil).taken, 0, "nil chest")
eq(sb.raiders_cut(1000, false), 150, "15% cut"); eq(sb.raiders_cut(1000, true), 0, "starving camp pays no cut")
eq(sb.raiders_bounty(1), 500, "tier 1 bounty"); eq(sb.raiders_bounty(3), 3000, "tier 3 bounty")
sb.cfg.raiders_bandit_mode = true
eq(sb.raiders_bounty(1), 625, "bandit +25% bounty")
sb.cfg.raiders_bandit_mode = nil

-- goodwill
local function find(plan, f) for _, p in ipairs(plan) do if p.faction == f then return p.delta end end end
local plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", friendly = false, allies = { "ecolog" } })
eq(find(plan, "duty"), -60, "robbed faction -60"); eq(find(plan, "ecolog"), -30, "ally -30")
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", friendly = true })
eq(find(plan, "duty"), -150, "friendly faction -60 - 100 capped to 150 daily")
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", friendly = true, spent = { duty = 100 } })
eq(find(plan, "duty"), -50, "daily cap leaves 50")
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", spent = { duty = 150 } })
eq(find(plan, "duty"), nil, "capped faction not charged")
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "ecolog", allies = { "ecolog", "monster" } })
eq(find(plan, "ecolog"), nil, "own faction never charged"); eq(find(plan, "monster"), nil, "non-faction skipped")
eq(#sb.raiders_goodwill_plan(nil), 0, "nil args"); eq(#sb.raiders_goodwill_plan({ faction = "monster" }), 0, "monster")
sb.cfg.raiders_bandit_mode = true
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", friendly = true })
eq(find(plan, "duty"), -80, "bandit: (60+100)*50%")
eq(find(plan, "bandit"), 20, "bandit rep"); eq(find(plan, "renegade"), 20, "renegade rep")
plan = sb.raiders_goodwill_plan({ faction = "bandit", own = "stalker" })
eq(find(plan, "bandit"), -30, "bandit mode: robbed bandit still loses, half"); eq(find(plan, "renegade"), 20, "renegade still gains")
sb.cfg.raiders_bandit_mode = nil
eq(sb.raiders_is_friendly(500), true, "friendly at 500"); eq(sb.raiders_is_friendly(499), false, "not at 499")

-- mission record
local m = sb.raiders_new_mission(1, "k", "l01_escape", "duty", { 10, 11 }, 1000, 3600, 0.6)
eq(m.arrive_sec, 4600, "arrive"); eq(sb.raiders_mission_due(m, 4599), false, "not due"); eq(sb.raiders_mission_due(m, 4600), true, "due")
eq(sb.raiders_mission_set_mode(m, "real"), true, "to real"); eq(m.state, "assault", "assault state")
eq(sb.raiders_mission_set_mode(m, "abstract"), true, "back to abstract"); eq(m.state, "away", "away state")
eq(sb.raiders_mission_set_mode(m, "bogus"), false, "bad mode")
eq(sb.raiders_mission_claim(m, "loot"), true, "loot once"); eq(sb.raiders_mission_claim(m, "loot"), false, "loot not twice")
eq(sb.raiders_mission_claim(m, "goodwill"), true, "goodwill once"); eq(sb.raiders_mission_claim(m, "goodwill"), false, "goodwill not twice")
eq(sb.raiders_mission_finish(m, "bogus"), false, "bad result"); eq(sb.raiders_mission_finish(m, "success"), true, "finish")
eq(sb.raiders_mission_finish(m, "disaster"), false, "finish twice"); eq(m.result, "success", "result kept")
eq(sb.raiders_mission_set_mode(m, "real"), false, "no mode change when done")

if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("test_raiders: all passed")
