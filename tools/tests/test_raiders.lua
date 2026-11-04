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
    sb.camp_send_tip = function(_, t) tips[#tips + 1] = t end
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
    eq(sb.raiders_send(7, camp3, nil, "gone"), false, "cleared outpost refused")
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
    near(sb.raiders_eta_parts and (mm.arrive_sec - gsec) / 10, 180, "eta ticks with the game clock")
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
    local h, m = sb.raiders_eta_parts(3600 * 2 + 61); eq(h, 2, "eta hours"); eq(m, 2, "eta minutes round up")
    h, m = sb.raiders_eta_parts(0); eq(h + m, 0, "eta zero")
    h, m = sb.raiders_eta_parts(-5); eq(h + m, 0, "eta negative")
    h, m = sb.raiders_eta_parts(59); eq(m, 1, "under a minute counts as one")
end

if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("test_raiders: all passed")
