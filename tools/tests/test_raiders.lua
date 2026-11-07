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

local info = { guards = 2, ready = 2, missions_today = 0 }
local target = { occupied = true, faction = "duty" }
eq(sb.raiders_can_send(info, target), true, "sendable")

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
refused(target, { guards = 0, ready = 2, missions_today = 0 }, "no_guard", "no guard at home")
refused(target, { guards = 2, ready = 0, missions_today = 0 }, "no_raider", "no raider")
refused(target, { guards = 2, ready = 1, missions_today = 3 }, "daily", "daily cap")
sb.cfg.raiders_bandit_mode = true
eq(sb.raiders_can_send(info, { occupied = true, faction = "duty", friendly = true }), true, "bandit may rob friends")
sb.cfg.raiders_bandit_mode = nil

-- survivor readiness
for rk = 0, 4 do eq(sb.raiders_survivor_ready({ tier = rk }, 100), true, "any rank may go: " .. rk) end
local o, r
-- odds rise with rank, smoothly, and stay inside the clamps
do
    local prev = -1
    for rk = 0, 4 do
        local p = sb.raid_odds(sb.raiders_band_strength({ { rank = rk }, { rank = rk }, { rank = rk } }), 4)
        eq(p > prev, true, "odds rise with rank " .. rk); eq(p >= 0.05 and p <= 0.9, true, "odds in bounds " .. rk)
        prev = p
    end
    local lo = sb.raid_odds(sb.raiders_band_strength({ { rank = 1 }, { rank = 1 }, { rank = 1 } }), 4)
    local hi = sb.raid_odds(sb.raiders_band_strength({ { rank = 4 }, { rank = 4 }, { rank = 4 } }), 4)
    eq(hi - lo > 0.25, true, "rank 4 clearly beats rank 1")
end
o, r = sb.raiders_survivor_ready({ tier = 3, raider = { wounded_until = 500 } }, 100); eq(r, "wounded", "wounded")
eq(sb.raiders_survivor_ready({ tier = 3, raider = { wounded_until = 50 } }, 100), true, "healed")
o, r = sb.raiders_survivor_ready({ tier = 3, on_expedition = true }, 100); eq(r, "busy", "on expedition")
o, r = sb.raiders_survivor_ready({ tier = 3, has_ammo = false }, 100); eq(r, "no_ammo", "no ammo")
o, r = sb.raiders_survivor_ready({ tier = 3, raider = { rest_until = 200 } }, 100); eq(r, "resting", "resting")

-- a dismantle cancels the raider missions once: release_camp_residents is the only caller
do
    local f = assert(io.open("00_Core/gamedata/scripts/stalker_camp_builder_recruit.script", "rb"))
    local recruit = f:read("*a"); f:close()
    local calls = select(2, recruit:gsub("raiders_on_camp_dismantled", ""))
    eq(calls, 2, "raiders_on_camp_dismantled: one call (the `if` guard and the pcall name it once each)")
    eq(recruit:find("pcall(sb.raiders_on_camp_dismantled, hub_id, camp)", 1, true) ~= nil, true, "called from release_camp_residents")
end

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
eq(sb.raiders_wounded_until(1000), 1000 + 40 * 60 * 10, "wounded 40 real minutes at tf 10")
eq(sb.raiders_rest_until(1000), 1000 + 20 * 60 * 10, "rest 20 real minutes at tf 10")
eq(sb.raiders_wounded_until(1000, nil, 1), 1000 + 40 * 60, "wounded 40 real minutes at tf 1")
eq(sb.raiders_rest_until(1000, nil, 0.1), 1000 + 20 * 60 * 0.1, "rest follows the factor given")
eq(sb.raiders_rest_until(1000, nil, 0), 1000 + 20 * 60 * 10, "bad factor falls back to 10")
eq(sb.raiders_rest_until(1000, { raiders_rest_minutes = 0 }), 1000, "rest 0 means no cooldown")
do  -- old records: waits above the setting are cut down, shorter ones stay, nothing is ever extended
    local r = { wounded_until = 1000 + 12 * 3600, rest_until = 1000 + 6 * 3600 }
    eq(sb.raiders_clamp_timers(r, 1000, nil, 10), true, "old hours-based record clamped")
    eq(r.wounded_until, 1000 + 40 * 600, "wounded clamped to 40 real minutes"); eq(r.rest_until, 1000 + 20 * 600, "rest clamped to 20 real minutes")
    local short = { wounded_until = 1500, rest_until = 1200 }
    eq(sb.raiders_clamp_timers(short, 1000, nil, 10), false, "short waits untouched")
    eq(short.wounded_until, 1500, "short wounded stays"); eq(sb.raiders_clamp_timers(nil, 1000), false, "nil record")
end
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
plan = sb.raiders_goodwill_plan({ faction = "duty", own = "stalker", allies = { "ecolog", "ecolog", "ecolog", "ecolog", "ecolog", "ecolog" } })
eq(find(plan, "ecolog"), -150, "repeated ally stays within the daily cap")
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
eq(m.arrive_sec, 4600, "arrive")
eq(sb.raiders_mission_due(m, 4599), false, "not due"); eq(sb.raiders_mission_due(m, 4600), true, "due")
eq(sb.raiders_mission_set_mode(m, "real"), true, "to real"); eq(m.state, "assault", "assault state")
eq(sb.raiders_mission_set_mode(m, "abstract"), true, "back to abstract"); eq(m.state, "away", "away state")
eq(sb.raiders_mission_set_mode(m, "bogus"), false, "bad mode")
eq(sb.raiders_mission_claim(m, "loot"), true, "loot once"); eq(sb.raiders_mission_claim(m, "loot"), false, "loot not twice")
eq(sb.raiders_mission_claim(m, "goodwill"), true, "goodwill once"); eq(sb.raiders_mission_claim(m, "goodwill"), false, "goodwill not twice")
eq(sb.raiders_mission_finish(m, "bogus"), false, "bad result"); eq(sb.raiders_mission_finish(m, "success"), true, "finish")
eq(sb.raiders_mission_finish(m, "disaster"), false, "finish twice"); eq(m.result, "success", "result kept")
eq(sb.raiders_mission_set_mode(m, "real"), false, "no mode change when done")

-- runtime layer with the engine stubbed: send, save/load, resolve
do
    local NOW = 1000000
    local released, goodwill, deposited, tips, moved = {}, {}, {}, {}, {}
    sb.game_sec = function() return NOW end
    time_global = function() return NOW * 1000 end
    game = { translate_string = function(id) return id end }
    level = { name = function() return "l01_escape" end }
    db = { actor = { id = function() return 1 end, give_money = function(_, n) moved.money = (moved.money or 0) + n end } }
    local objs = { [10] = { alive = true }, [11] = { alive = true }, [50] = {}, [51] = {}, [900] = {} }
    for id in pairs(objs) do objs[id].can_switch_online = function() return false end end
    local sim = { set_switch_online = function(_, id, v) moved["on" .. id] = v end, set_switch_offline = function() end }
    alife = function() return sim end
    alife_object = function(id) return objs[id] end
    alife_release = function(o) released[#released + 1] = o end
    utils_obj = { switch_online = function(id) moved["home" .. id] = true end }
    relation_registry = { community_relation = function() return 0 end, change_community_goodwill = function(f, _, d) goodwill[#goodwill + 1] = { f, d }; return true end,
                          community_goodwill = function() return 0 end }
    RegisterScriptCallback = function() end
    local forced_toasts = 0     -- reports sent with `always` (they would show with Verbose Notifications off)
    sb.camp_send_tip = function(_, t, _, _, _, _, _, always)
        tips[#tips + 1] = t
        if always then forced_toasts = forced_toasts + 1 end
    end
    sb.add_radio_feed_entry = function() end
    sb.allow_home_squad_online = function() end
    sb.prosper_credit = function(sv, n) sv.savings = (sv.savings or 0) + n end
    sb.safe_squad_members = function() local done; return function() if not done then done = true; return { id = 50, object = objs[50] } end end end
    sb.deposit_item_to_camp = function(_, _, sec) deposited[#deposited + 1] = sec; return true end
    sb.get_player_faction = function() return "actor_stalker" end
    sb.rival_camps = { k1 = { chest_id = 900, squad_id = 900, extra_squad_ids = { 51 }, faction = "bandit", tier = 1,
        position = { x = 100, z = 0 }, level = "l01_escape" } }
    local function fresh_camp()
        return { survivors = {
            [10] = { job = "raider", tier = 3 }, [11] = { job = "raider", tier = 2 },
            [12] = { job = "guard", tier = 1 },
        } }
    end
    local camp = fresh_camp()
    sb.active_camps = { [7] = camp }
    objs[7] = { position = { x = 0, z = 0 } }

    eq(sb.raiders_send_for(12), nil, "guard is not a raider (assign normally)")
    eq(sb.raiders_send_for(10), true, "send lead raider")
    eq(camp.raider_missions[1].state, "away", "mission recorded")
    eq(#camp.raider_missions[1].raider_ids, 2, "both raiders go")
    eq(camp.survivors[10].on_mission, 1, "flag on lead"); eq(camp.survivors[11].on_expedition, true, "expedition guard set")
    eq(camp.raider_state.missions_today, 1, "counted for today")
    eq(sb.raiders_send_for(10), false, "already away: no second send")
    local l1 = sb.raiders_pause_reason(camp.survivors[10]); eq(l1, "st_homestead_raider_on_mission", "pause reason")
    do   -- the time left shows like an expedition's (game seconds, formatted by the shared helper)
        local m1 = camp.raider_missions[camp.survivors[10].on_mission]
        eq(sb.raiders_mission_remaining(m1, m1.arrive_sec - 600), 600, "remaining game seconds")
        eq(sb.raiders_mission_remaining(m1, m1.arrive_sec + 5), 0, "never negative")
        eq(sb.raiders_mission_remaining({ state = "assault", arrive_sec = 50 }, 20), 30, "countdown continues in the field")
        eq(sb.raiders_mission_remaining({ state = "done" }, 0), nil, "none once finished")
        sb.format_expedition_time = function(sec) return "T" .. sec end
        game.translate_string = function(id) return id .. ":%s" end
        local l2, d2 = sb.raiders_pause_reason(camp.survivors[10], camp)
        eq(l2:find("^st_homestead_raider_on_mission_left:T") ~= nil, true, "label uses the left string")
        eq(l2:find("T%d+") ~= nil, true, "label has the formatted time"); eq(d2:find("T%d+") ~= nil, true, "detail has it too")
        NOW = NOW + 600
        local l3 = sb.raiders_pause_reason(camp.survivors[10], camp)
        eq(l3 ~= l2, true, "the text changes as the clock moves")
        NOW = NOW - 600
        sb.format_expedition_time = nil; game.translate_string = function(id) return id end
    end

    -- save/load: only plain data survives
    local function roundtrip(t)
        local function ser(v)
            if type(v) == "table" then
                local o = {}
                for k, x in pairs(v) do o[#o + 1] = "[" .. ser(k) .. "]=" .. ser(x) end
                return "{" .. table.concat(o, ",") .. "}"
            elseif type(v) == "string" then return string.format("%q", v)
            else return tostring(v) end
        end
        return loadstring("return " .. ser(t))()
    end
    sb.active_camps = { [7] = roundtrip(camp) }
    camp = sb.active_camps[7]
    eq(camp.raider_missions[1].faction, "bandit", "mission survives save/load")

    sb.raiders_process(); eq(camp.raider_missions[1] ~= nil, true, "not due yet")
    NOW = NOW + 6 * 3600
    local rnd = math.random; math.random = function(n) if n then return 1 end return 0.01 end
    sb.raiders_process(); math.random = rnd
    eq(camp.raider_missions[1], nil, "mission resolved and removed")
    eq(camp.survivors[10].on_mission, nil, "lead is home"); eq(camp.survivors[10].on_expedition, nil, "expedition flag cleared")
    eq(moved.home10, true, "lead switched back online")
    eq(#released, 2, "both garrison squads released"); eq(#deposited > 0, true, "loot deposited")
    eq(moved.money, 500, "bounty paid"); eq((camp.survivors[10].savings or 0) > 0, true, "savings cut paid")
    eq(goodwill[1][1], "bandit", "goodwill hit the robbed faction")
    eq(camp.survivors[10].raider.rest_until > NOW, true, "raiders rest after a mission")
    sb.rival_camps.k1 = nil

    -- cancel: a raider who changes job leaves the mission
    camp = fresh_camp(); sb.active_camps = { [7] = camp }
    sb.rival_camps.k2 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1, position = { x = 100, z = 0 } }
    NOW = NOW + 7 * 24 * 3600
    eq(sb.raiders_send_for(10), true, "second send")
    sb.raiders_cancel_for(7, 10)
    eq(camp.survivors[10].on_mission, nil, "cancelled raider is home")
    eq(#camp.raider_missions[1].raider_ids, 1, "mission keeps the other raider")
    -- an orphaned flag (mission record gone) is repaired
    camp.raider_missions = {}
    sb.raiders_process(); eq(camp.survivors[11].on_mission, nil, "orphaned mission flag repaired")
    -- failure paths: repulsed wounds everyone; disaster kills at the death chance and leaves the target alone
    local function run_loss(rolls)
        local c = fresh_camp(); sb.active_camps = { [7] = c }
        sb.rival_camps.k4 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1, position = { x = 100, z = 0 } }
        NOW = NOW + 2 * 24 * 3600
        eq(sb.raiders_send_for(10), true, "send for loss test")
        NOW = NOW + 6 * 3600
        local i = 0
        math.random = function(n) if n then return 1 end i = i + 1; return rolls[i] or rolls[#rolls] end
        local rel = #released
        sb.raiders_process(); math.random = rnd
        return c, #released - rel
    end
    local c = run_loss({ 0.99, 0.99 })
    eq(c.survivors[10].raider.wounded_until > NOW, true, "repulsed: wounded"); eq(c.survivors[11] ~= nil, true, "repulsed: nobody dies")
    local c2, rel2 = run_loss({ 0.99, 0.01, 0.01, 0.99 })
    eq(c2.survivors[10], nil, "disaster: low roll dies"); eq(c2.survivors[11] ~= nil, true, "disaster: high roll lives")
    eq(rel2 >= 1, true, "disaster: dead raider's record released"); eq(c2.survivors[11].raider.wounded_until > NOW, true, "disaster: survivor wounded")
    eq(sb.rival_camps.k4.raid_cooldown_until > NOW, true, "failed raid puts the target on cooldown")

    -- idle raider at home = half a guard; away or wounded = none
    near(sb.raiders_defense_share({ job = "raider" }, NOW), 0.5, "idle raider half a guard")
    near(sb.raiders_defense_share({ job = "raider", on_mission = 1 }, NOW), 0, "away raider adds none")
    near(sb.raiders_defense_share({ job = "raider", raider = { wounded_until = NOW + 5 } }, NOW), 0, "wounded raider adds none")
    -- the daily goodwill cap is shared by every camp
    goodwill = {}
    local c1, c2 = fresh_camp(), fresh_camp()
    sb.active_camps = { [7] = c1, [8] = c2 }
    sb.rival_camps.k3 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1, position = { x = 100, z = 0 } }
    local function lost() local t = 0; for _, g in ipairs(goodwill) do if g[1] == "bandit" and g[2] < 0 then t = t - g[2] end end; return t end
    local m1 = sb.raiders_new_mission(1, "k3", nil, "bandit", { 10 }, NOW, 60, 1)
    local m2 = sb.raiders_new_mission(1, "k3", nil, "bandit", { 10 }, NOW, 60, 1)
    c1.raider_missions = { [1] = m1 }; c2.raider_missions = { [1] = m2 }
    c1.raider_state = nil; c2.raider_state = nil
    NOW = NOW + 100
    math.random = function(n) if n then return 1 end return 0.01 end
    sb.cfg.raiders_goodwill_daily_cap = 70
    sb.raiders_process(); math.random = rnd
    eq(lost(), 70, "two camps share one daily cap")
    sb.cfg.raiders_goodwill_daily_cap = nil

    -- Outposts tab: button status, preview and the send to a chosen outpost
    NOW = NOW + 3 * 86400
    goodwill = {}
    local camp3 = fresh_camp()
    camp3.survivors[12].job = "guard"
    sb.active_camps = { [7] = camp3 }
    sb.rival_camps = { k1 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1,
            position = { x = 100, z = 0 }, level = "l01_escape" },
        k2 = { chest_id = 900, squad_id = 900, faction = "duty", tier = 2, position = { x = 50, z = 0 } },
        gone = { chest_id = 900, squad_id = 900, faction = "duty", status = "unoccupied" } }
    local s = sb.raiders_outpost_status("k1", 7)
    eq(s.state, "ready", "outpost ready"); eq(s.band, 2, "preview band"); eq(s.faction, "bandit", "preview faction")
    eq(s.loss, 60, "preview goodwill loss"); eq(s.friendly, false, "not friendly")
    eq(s.odds >= 0.05 and s.odds <= 0.9, true, "preview odds in range")
    eq(sb.raiders_outpost_status("gone", 7).reason, "empty", "cleared outpost is not a target")
    eq(sb.raiders_outpost_status("nokey", 7).reason, "empty", "unknown outpost")
    camp3.survivors[12].job = "idle"
    eq(sb.raiders_outpost_status("k1", 7).reason, "no_guard", "no guard home")
    camp3.survivors[12].job = "guard"
    camp3.raider_state = { day = math.floor(NOW / 86400), spent = {}, missions_today = 3 }
    eq(sb.raiders_outpost_status("k1", 7).reason, "daily", "daily cap")
    camp3.raider_state.missions_today = 0
    sb.rival_camps.k1.raid_cooldown_until = NOW + 100
    eq(sb.raiders_outpost_status("k1", 7).reason, "cooldown", "already hit")
    sb.rival_camps.k1.raid_cooldown_until = nil
    relation_registry.community_goodwill = function() return 800 end
    local fs = sb.raiders_outpost_status("k1", 7)
    eq(fs.state, "ready", "a friendly faction is a valid target"); eq(fs.friendly, true, "friendly flagged")
    eq(fs.loss, 150, "friendly loss: base plus betrayal, held to the daily cap")
    eq(sb.raiders_send(7, camp3, nil, "k1"), true, "a friendly outpost can be raided from the PDA")
    camp3.raider_missions = {}; camp3.raider_state = nil
    for _, sv in pairs(camp3.survivors) do sv.on_mission = nil; sv.on_expedition = nil end
    relation_registry.community_goodwill = function() return 0 end

    -- sending to a chosen outpost: the far one, not the nearest
    eq(sb.raiders_send(7, camp3, nil, "k1"), true, "send to the chosen outpost")
    eq(camp3.raider_missions[1].target_key, "k1", "mission targets the chosen outpost")
    eq(#camp3.raider_missions[1].raider_ids, 2, "free raiders go without a lead")
    local a = sb.raiders_outpost_status("k1", 7)
    eq(a.state, "away", "status away while the raid runs"); eq(a.band, 2, "away band"); eq(a.eta > 0, true, "eta counts down")
    eq(sb.raiders_mission_for("k1") ~= nil, true, "mission found for the card")
    eq(sb.raiders_mission_for("k2"), nil, "no mission on the other outpost")
    tips = {}
    eq(sb.raiders_send(7, camp3, nil, "k2"), false, "no raider left for a second send")
    eq(tips[1], "st_pda_raid_why_no_raider", "reason tip")
    eq(forced_toasts, 0, "raider toasts respect Verbose Notifications off")
    eq(sb.raiders_send(7, camp3, nil, "gone"), false, "cleared outpost refused")

    -- ---- phase 4: recall (manual, auto, defenders, save/load)
    sb.rival_camps.k9 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1, position = { x = 100, z = 0 }, level = "l01_escape" }
    sb.rival_camps.k8 = { chest_id = 900, squad_id = 900, faction = "bandit", tier = 1, position = { x = 100, z = 0 }, level = "l01_escape" }
    local function sent_camp()
        NOW = NOW + 5 * 86400
        local c = fresh_camp(); sb.active_camps = { [7] = c }
        eq(sb.raiders_send(7, c, nil, "k9"), true, "recall test: raiders out")
        return c
    end
    local function chk(away, ret, expect_ok, expect_why, msg)
        local o2, w2 = sb.raiders_recall_check(away, ret)
        eq(o2, expect_ok, msg .. " ok"); eq(w2, expect_why, msg .. " reason")
    end
    chk(2, 0, true, nil, "recall with a band away"); chk(0, 0, false, "none", "nobody away")
    chk(0, 2, false, "returning", "recall already in progress"); chk(1, 2, true, nil, "another band still away")
    near(sb.raiders_recall_delay(10), 200, "delay in game seconds"); near(sb.raiders_recall_delay(0), 200, "bad factor falls back")

    -- manual recall, no raid: no loot, no goodwill, no cooldown, band home after the delay
    do
        local c = sent_camp(); goodwill = {}; local dep = #deposited; local rel = #released
        local st = sb.raiders_recall_status(c); eq(st.ok, true, "status: can recall"); eq(st.away, 2, "status: two away")
        eq(sb.raiders_recall(7, c), 2, "two raiders recalled")
        eq(c.raider_missions[1].state, "returning", "mission is returning")
        eq(c.raider_missions[1].recalled, true, "recall flag on the record")
        st = sb.raiders_recall_status(c); eq(st.ok, false, "status: no second recall"); eq(st.reason, "returning", "status: already recalled")
        eq(st.returning, 2, "status: two returning"); eq(st.eta > 0, true, "status: eta")
        eq(sb.raiders_recall(7, c), 0, "a second recall does nothing")
        local rf = sb.raiders_recall_for(10); eq(rf.ok, false, "survivor button: recall in progress"); eq(rf.reason, "returning", "survivor button reason")
        eq(sb.raiders_recall_for(12), nil, "a guard has no recall")
        local l = sb.raiders_pause_reason(c.survivors[10], c); eq(l, "st_homestead_raider_recalling", "returning label")
        -- a mid-recall save/load keeps it; not due before the delay
        sb.active_camps = { [7] = roundtrip(c) }; c = sb.active_camps[7]
        eq(c.raider_missions[1].state, "returning", "recall survives save/load")
        sb.raiders_process(); eq(c.raider_missions[1] ~= nil, true, "still on the way")
        eq(sb.raiders_mission_due(c.raider_missions[1], NOW + 99999), false, "a returning mission is never resolved as a raid")
        NOW = NOW + 250
        sb.raiders_process()
        eq(c.raider_missions[1], nil, "band arrived, mission gone")
        eq(c.survivors[10].on_mission, nil, "flag cleared"); eq(moved.home10, true, "switched back online")
        eq(c.survivors[10].raider and c.survivors[10].raider.defending, nil, "no attack: not marked as defenders")
        eq(#deposited, dep, "no loot"); eq(#goodwill, 0, "no goodwill change"); eq(#released, rel, "garrison untouched")
        eq(sb.rival_camps.k9.raid_cooldown_until, nil, "no target cooldown")
        eq(sb.raiders_survivor_ready(c.survivors[10], NOW), true, "no rest or wounds after a recall")
        eq(sb.raiders_recall_status(c).reason, "none", "status: nobody away now")
    end

    -- recall during an attack: arrive as defenders (full guards) until the attack ends
    do
        local c = sent_camp(); c.active_raid = { squad_id = 1 }
        eq(sb.raiders_recall(7, c), 2, "recall during an attack")
        NOW = NOW + 250; sb.raiders_process()
        for _, id in ipairs({ 10, 11 }) do
            eq(c.survivors[id].raider.defending, true, "defender " .. id)
            near(sb.raiders_defense_share(c.survivors[id], NOW), 1, "a defender counts as a full guard")
        end
        local o3, w3 = sb.raiders_survivor_ready(c.survivors[10], NOW); eq(o3, false, "defender cannot be sent"); eq(w3, "defending", "defender reason")
        eq(sb.raiders_pause_reason(c.survivors[10], c), "st_homestead_raider_defending", "defender label")
        c.survivors[11].raider.wounded_until = NOW + 100
        near(sb.raiders_defense_share(c.survivors[11], NOW), 0, "a wounded defender adds none")
        -- no new raid during the attack, with the reason
        local o4, w4 = sb.raiders_can_send({ guards = 2, ready = 2, missions_today = 0, raid_active = true }, { occupied = true, faction = "duty" })
        eq(o4, false, "no raid while attacked"); eq(w4, "raid", "reason raid")
        sb.active_camps = { [7] = roundtrip(c) }; c = sb.active_camps[7]
        sb.raiders_process(); eq(c.survivors[10].raider.defending, true, "defenders stay while the attack lasts, also after a load")
        c.active_raid = nil
        sb.raiders_process()
        eq(c.survivors[10].raider.defending, nil, "attack over: stand down"); eq(c.survivors[11].raider.defending, nil, "all stand down")
        near(sb.raiders_defense_share(c.survivors[10], NOW), 0.5, "back to half a guard")
    end

    -- the player can recall a raider's whole mission from the Survivors tab, other missions stay
    do
        local c = sent_camp()
        c.survivors[13] = { job = "raider", tier = 2 }
        eq(sb.raiders_send(7, c, 13, "k8"), true, "second band out")
        local before = #c.raider_missions[1].raider_ids
        eq(sb.raiders_recall(7, c, nil, c.survivors[13].on_mission), 1, "only the one mission recalled")
        eq(c.raider_missions[1].state, "away", "the other mission keeps going"); eq(before, 2, "band size unchanged")
    end

    -- auto recall: option off does nothing; on, an attack recalls once, state in the saved record
    do
        local c = sent_camp(); c.active_raid = { squad_id = 1 }
        sb.raiders_process(); eq(c.raider_missions[1].state, "away", "auto recall off by default")
        sb.cfg.raiders_auto_recall = true
        sb.raiders_process(); eq(c.raider_missions[1].state, "returning", "auto recall fires when the camp is attacked")
        local arrive = c.raider_missions[1].arrive_sec
        sb.raiders_process(); eq(c.raider_missions[1].arrive_sec, arrive, "recalled only once")
        sb.active_camps = { [7] = roundtrip(c) }; c = sb.active_camps[7]
        NOW = NOW + 250; sb.raiders_process()
        eq(c.survivors[10].raider.defending, true, "arrived as defenders after a load")
        sb.cfg.raiders_auto_recall = nil
        -- a quiet camp is never recalled
        local c3 = sent_camp(); sb.cfg.raiders_auto_recall = true
        sb.raiders_process(); eq(c3.raider_missions[1].state, "away", "no attack, no auto recall")
        sb.cfg.raiders_auto_recall = nil
    end

    -- the outpost card: a recalled raid reads as returning, not as a fresh raid
    do
        local c = sent_camp()
        eq(sb.raiders_outpost_status("k9", 7).returning, false, "card: raid running")
        sb.raiders_recall(7, c)
        local o5 = sb.raiders_outpost_status("k9", 7); eq(o5.state, "away", "card: still held while returning"); eq(o5.returning, true, "card: returning")
    end
end

-- the freeze: game_sec lives in the stalker_camp_builder namespace, so a bare global game_sec is nil in
-- the raiders script. The clock must come from sb.game_sec and move the countdown and the due test.
do
    local gsec = 1000000
    game_sec = nil
    sb.game_sec = function() return gsec end
    level = { get_time_factor = function() return 10 end }
    local mm = sb.raiders_new_mission(1, "k", nil, "duty", {}, gsec, 3000, 0.5)
    gsec = gsec + 1200
    eq(sb.raiders_mission_due(mm, gsec), false, "not due yet")
    gsec = gsec + 1800
    eq(sb.raiders_mission_due(mm, gsec), true, "due once the clock reaches arrive_sec")
end

-- pure PDA helpers
do
    sb.cfg = {}
    eq(sb.raiders_faction_loss("duty", false, {}, "stalker"), 60, "plain loss")
    eq(sb.raiders_faction_loss("duty", true, {}, "stalker"), 150, "friendly loss capped at 150")
    eq(sb.raiders_faction_loss("duty", false, { duty = 120 }, "stalker"), 30, "loss left under the cap")
    eq(sb.raiders_faction_loss("duty", false, { duty = 150 }, "stalker"), 0, "cap used up")
    eq(sb.raiders_faction_loss("stalker", false, {}, "stalker"), 0, "never the player's own faction")
    eq(sb.raiders_faction_loss("monster", false, {}, "stalker"), 0, "not a faction")
    eq(sb.raiders_eta_text(3600 * 2 + 61), "2h 01m", "eta hours"); eq(sb.raiders_eta_text(725), "12m 05s", "eta minutes tick by the second")
    eq(sb.raiders_eta_text(0), "0s", "eta zero"); eq(sb.raiders_eta_text(-5), "0s", "eta negative"); eq(sb.raiders_eta_text(59.9), "59s", "eta seconds")
    eq(sb.raiders_eta_text(724) ~= sb.raiders_eta_text(725), true, "the text changes every second")
end

if fails > 0 then print(fails .. " FAILED"); os.exit(1) end

-- ---------------------------------------------------------------- phase 5: visible assault
do
    local function serialize(v)
        if type(v) ~= "table" then return type(v) == "string" and string.format("%q", v) or tostring(v) end
        local out = {}
        for k, x in pairs(v) do out[#out + 1] = "[" .. serialize(k) .. "]=" .. serialize(x) end
        return "{" .. table.concat(out, ",") .. "}"
    end
    local function roundtrip(v) return assert(loadstring("return " .. serialize(v)))() end
    local function fresh(now)
        local m = sb.raiders_new_mission(7, "k", "l01_escape", "bandit", { 11, 12, 13 }, now or 1000, 3000, 0.5)
        return m
    end
    local EP = 4242
    local function begin(m, now)
        eq(sb.raiders_assault_begin(m, now or 2000, 10, { squad_id = 99, section = "stalker_sim_squad_advanced",
            epoch = EP, proxy = 3, garrison = 4 }), true, "begin")
    end

    -- start window: travel over, before the deadline, option-independent pure check
    local m = fresh()                                    -- arrive_sec = 4000, travel over at 2200
    eq(sb.raiders_assault_start_due(m, 2199), false, "still travelling")
    eq(sb.raiders_assault_start_due(m, 2200), true, "arrived")
    eq(sb.raiders_assault_start_due(m, 4000), false, "deadline passed: abstract resolves")
    begin(m, 2300)
    eq(m.mode, "real", "real mode"); eq(m.state, "assault", "assault state")
    eq(sb.raiders_assault_start_due(m, 2400), false, "no second start")
    eq(sb.raiders_mission_due(m, 9999), false, "abstract timer is not enforced while fighting")
    eq(sb.raiders_mission_remaining(m, 2500), 1500, "countdown kept")

    local function step(obs, now)
        obs.epoch = obs.epoch == nil and EP or obs.epoch
        if obs.player_near == nil then obs.player_near = true end
        return sb.raiders_assault_step(m, obs, now)
    end
    eq(step({ proxy_alive = 3, garrison_alive = 4 }, 2310).act, "wait", "fight goes on")
    eq(step({ proxy_alive = 3, garrison_alive = 2 }, 2320).act, "wait", "progress")
    eq(m.real.progress_sec, 2320, "progress mark moves")
    -- win: the rival tick marked the outpost unoccupied
    local a = step({ proxy_alive = 2, garrison_alive = 0, target_status = "unoccupied" }, 2330)
    eq(a.act, "finish", "garrison eliminated"); eq(a.result, "success", "success")
    a = step({ proxy_alive = 0, garrison_alive = 0, target_status = "unoccupied" }, 2330)
    eq(a.result, "gone", "someone else cleared it")
    a = step({ proxy_alive = 2, garrison_alive = 2, target_status = "gone" }, 2330)
    eq(a.result, "gone", "target vanished")
    a = step({ proxy_alive = 0, garrison_alive = 3 }, 2330)
    eq(a.result, "disaster", "band wiped out")
    -- the player leaves: abstract fallback with the survivors' odds
    a = step({ proxy_alive = 3, garrison_alive = 2, player_near = false }, 2340)
    eq(a.act, "fallback", "player left")
    eq(a.odds > m.odds, true, "odds rise when the garrison is halved")
    near(a.odds, sb.raiders_fallback_odds(m), "odds match the helper")
    do
        local m2 = fresh()
        begin(m2, 2300); m2.real.proxy_alive, m2.real.garrison_alive = 3, 4
        near(sb.raiders_fallback_odds(m2), 0.5, "untouched sides keep the shown odds")
        m2.real.proxy_alive = 1
        eq(sb.raiders_fallback_odds(m2) < 0.5, true, "losses lower the odds")
        m2.real.proxy_alive = 0
        near(sb.raiders_fallback_odds(m2), 0.05, "no attackers: floor")
        m2.real.proxy_alive, m2.real.garrison_alive = 3, 0
        near(sb.raiders_fallback_odds(m2), 0.9, "no defenders: cap")
    end

    -- stalemate: no headcount change for 150 real s (1500 game s at tf 10) while the garrison stands
    m = fresh(); begin(m, 2300)
    step({ proxy_alive = 3, garrison_alive = 3 }, 2310)            -- first blood: the fight is on
    eq(step({ proxy_alive = 3, garrison_alive = 3 }, 2310 + 1499).act, "wait", "just under the stall limit")
    a = step({ proxy_alive = 3, garrison_alive = 3 }, 2310 + 1500)
    eq(a.act, "finish", "stalled"); eq(a.result, "repulsed", "stall with the garrison standing = repulsed")
    m = fresh(); begin(m, 2300)
    step({ proxy_alive = 3, garrison_alive = 0 }, 2310)
    a = step({ proxy_alive = 3, garrison_alive = 0 }, 2310 + 1500)
    eq(a.result, "success", "stall with an empty garrison = success")
    -- a fight where nobody ever fell never started: no punishment, no second try
    m = fresh(); begin(m, 2300)
    a = step({ proxy_alive = 3, garrison_alive = 4 }, 2300 + 1500)
    eq(a.act, "abstain", "never engaged")
    eq(sb.raiders_assault_reset(m, 3800, 300), true, "reset"); m.no_visible = true
    eq(sb.raiders_assault_start_due(m, 3900), false, "no second visible try")
    eq(sb.raiders_mission_due(m, 4100), true, "the abstract timer decides")
    m = fresh(); begin(m, 2300)
    local hard = m.real.hard_sec
    for t = 2300, hard, 1000 do step({ proxy_alive = 3 - (t / 1000) % 2, garrison_alive = 4 }, t) end
    a = step({ proxy_alive = 3, garrison_alive = 4 }, hard)
    eq(a.result, "repulsed", "hard cap ends the fight")

    -- save/load: the record survives a round trip; a different epoch (a load) resets it to a plain away mission
    m = fresh(); begin(m, 2300)
    m = roundtrip(m)
    eq(step({ proxy_alive = 3, garrison_alive = 4 }, 2400).act, "wait", "same session after a round trip")
    a = step({ proxy_alive = 3, garrison_alive = 4, epoch = 777 }, 2400)
    eq(a.act, "reset", "load detected")
    eq(sb.raiders_assault_reset(m, 2400, sb.raiders_assault_reset_delay(10)), true, "reset")
    eq(m.mode, "abstract", "abstract again"); eq(m.state, "away", "away again"); eq(m.real, nil, "no fight record")
    eq(m.arrive_sec, 2700, "30 real s left")
    eq(sb.raiders_assault_start_due(m, 2400), true, "may start over")
    eq(sb.raiders_mission_due(m, 2700), true, "or resolves abstractly")
    eq(sb.raiders_assault_step(fresh(), {}, 0).act, "reset", "a mission that never fought resets safely")

    -- once-only claims across a switch between abstract and real
    m = fresh(); begin(m, 2300)
    eq(sb.raiders_mission_claim(m, "loot"), true, "loot claimed")
    eq(sb.raiders_assault_reset(m, 2400, 0), true, "fell back")
    eq(sb.raiders_mission_claim(m, "loot"), false, "loot is not paid twice")
    eq(sb.raiders_mission_claim(m, "goodwill"), true, "goodwill claimed")
    eq(sb.raiders_mission_claim(m, "goodwill"), false, "goodwill is not paid twice")

    -- recall in the field: back to a returning abstract mission
    m = fresh(); begin(m, 2300)
    eq(sb.raiders_mission_recall(m, 2400, 200), true, "recall in assault")
    eq(m.state, "returning", "returning"); eq(m.mode, "abstract", "abstract"); eq(m.real, nil, "fight dropped")
    eq(sb.raiders_assault_step(m, {}, 0).act, "reset", "no step on a returning mission")
    eq(sb.raiders_recall_check(3, 0), true, "bands in the field count as away")
end

-- mission clock (Real Time Zones proof): clock = game_sec + off
do
    local adv = sb.raiders_clock_advance
    -- no RTZ: the offset never moves, the mission clock is the game clock
    near(adv(0, 100, 5000, 3, 10, false), 0, "no rtz: off unchanged")
    near(adv(nil, nil, 5000, 3, 10, false), 0, "no rtz: first use, nil off is 0")
    -- first step with RTZ (old save / just loaded): nothing to cancel yet
    near(adv(0, nil, 5000, 3, 10, true), 0, "rtz first step")
    -- one tick of 2 real seconds, nominal 10: clock must move 20 whatever the game clock did
    local function clock(off, last_g, g, dt, tf) return g + adv(off, last_g, g, dt, tf, true) end
    near(clock(0, 1000, 1020, 2, 10) - 1000, 20, "rtz clock at 10x game clock")
    near(clock(0, 1000, 1002, 2, 10) - 1000, 20, "rtz clock at 1x game clock (RTZ running real time)")
    near(clock(0, 1000, 1000.2, 2, 10) - 1000, 20, "rtz clock at 0.1x game clock (catch-up)")
    -- a forward game-clock jump (sync, +84 min) does not complete or skip anything
    near(clock(0, 1000, 1000 + 5040 * 60, 2, 10) - 1000, 20, "rtz clock ignores a clock jump")
    -- the first tick after a load has no real delta: the clock holds, even across a jump
    near(clock(37, 1000, 90000, 0, 10) - (1000 + 37), 0, "rtz load step holds the clock")
    -- a huge real delta (long pause) is clamped to one minute
    near(clock(0, 1000, 1001, 100000, 10) - 1000, 600, "rtz clamps a long real delta")
    -- bad factor falls back to 10, a negative delta counts as 0
    near(clock(0, 1000, 1001, 1, 0) - 1000, 10, "rtz zero factor")
    near(clock(0, 1000, 1001, -5, 10) - 1000, 0, "rtz negative delta")
    -- a ten real-minute countdown: 300 ticks of 2 s at game rates 0.1x and 1x both land on 6000 mission seconds
    for _, rate in ipairs({ 0.1, 1, 10 }) do
        local off, g, c0 = 0, 50000, 50000
        for _ = 1, 300 do
            local ng = g + 2 * rate
            off = adv(off, g, ng, 2, 10, true); g = ng
        end
        near(g + off - c0, 6000, "ten real minutes at game rate " .. rate)
    end
    -- an old record (arrive_sec in game seconds, off nil) stays valid: first step keeps clock == game_sec
    local m = sb.raiders_new_mission(1, "k", "l_x", "duty", { 1 }, 40000, 600, 0.5)
    near(sb.raiders_mission_remaining(m, 40000 + adv(nil, nil, 40000, 0, 10, true)), 600, "old record remaining")
end

-- wounded / cooldown feedback: reason keys, timers and the PDA lines
do
    local now = 1000
    local fit = { job = "raider", name = "Fit", raider = {} }
    local wnd = { job = "raider", name = "Hurt", raider = { wounded_until = now + 43200, rest_until = now + 21600 } }
    local rst = { job = "raider", name = "Tired", raider = { rest_until = now + 3600 } }
    local away = { job = "raider", name = "Gone", on_mission = 1 }
    local nw = { job = "raider", name = "Bare", has_weapon = false, raider = {} }
    local guard = { job = "guard", name = "Guard", raider = { wounded_until = now + 99 } }

    local k, l = sb.raiders_survivor_timer(wnd, now)
    eq(k, "wounded", "wounded timer wins over rest"); near(l, 43200, "wounded left")
    k, l = sb.raiders_survivor_timer(rst, now)
    eq(k, "resting", "rest timer"); near(l, 3600, "rest left")
    eq(sb.raiders_survivor_timer(fit, now), nil, "no timer when fit")
    eq(sb.raiders_survivor_timer(wnd, now + 43200), nil, "timer gone once both ended")
    eq(sb.raiders_survivor_timer(nil, now), nil, "nil survivor")

    -- real-time text: 12 game hours at factor 10 is 72 real minutes; rounded up, never 0s while running
    eq(sb.raiders_timer_text(43200, 10), "1h 12m", "wounded 12h at tf 10")
    eq(sb.raiders_timer_text(21600, 10), "36m 00s", "rest 6h at tf 10")
    eq(sb.raiders_timer_text(43200, 1), "12h 00m", "tf 1 (real time zones nominal 1)")
    eq(sb.raiders_timer_text(sb.raiders_wounded_until(0, nil, 10), 10), "40m 00s", "a fresh wound reads 40 real minutes")
    eq(sb.raiders_timer_text(sb.raiders_rest_until(0, nil, 10), 10), "20m 00s", "a fresh cooldown reads 20 real minutes")
    eq(sb.raiders_timer_text(5, 10), "1s", "rounds up")
    eq(sb.raiders_timer_text(0, 10), "0s", "zero")
    eq(sb.raiders_timer_text(100, 0), "10s", "bad factor falls back to 10")

    local list = sb.raiders_blockers({ a = fit, b = wnd, c = rst, d = away, e = nw, f = guard }, now)
    eq(#list, 4, "four raiders held back, the fit one and the guard are not")
    eq(list[1].key, "resting", "soonest first"); near(list[1].left, 3600, "rest left in list")
    eq(list[2].key, "wounded", "wounded second"); near(list[2].left, 43200, "wounded left in list")
    -- the two without a timer follow, by name
    eq(list[3].name, "Bare", "no weapon"); eq(list[3].key, "no_weapon", "no weapon key"); eq(list[3].left, nil, "no timer")
    eq(list[4].key, "busy", "on a mission"); eq(list[4].left, nil, "mission has its own timer")
    eq(#sb.raiders_blockers({}, now), 0, "no raiders no blockers")
    eq(#sb.raiders_blockers(nil, now), 0, "nil table")

    local fmt = { wounded = "%s W %s", resting = "%s R %s", busy = "%s B", no_weapon = "%s NW", more = "+%d", next = "next %s" }
    local lines = sb.raiders_blocker_lines(list, 10, fmt, 3)
    eq(#lines, 5, "three raiders, more, next")
    eq(lines[1], "Tired R 6m 00s", "rest line"); eq(lines[2], "Hurt W 1h 12m", "wounded line"); eq(lines[3], "Bare NW", "weapon line")
    eq(lines[4], "+1", "more line"); eq(lines[5], "next 6m 00s", "next line is the soonest timer")
    eq(#sb.raiders_blocker_lines({ list[3] }, 10, fmt, 3), 1, "no timer, no next line")
    eq(#sb.raiders_blocker_lines(nil, 10, fmt), 0, "nil list")
end

if fails > 0 then print("test_raiders: " .. fails .. " FAILED"); os.exit(1) end
print("test_raiders: all passed")
