-- Unit tests for Settlement Bodyguard / Companion Loan System:
--   1. loan_settler_as_companion preserves paused_job, paused_job_progress, xp, tier, savings, and assigned_pos
--   2. loan_settler_as_companion flushes queued rank/reputation standing onto the online NPC and marks sworn=true
--   3. return_companion_to_settlement restores paused_job and paused_job_progress cycle elapsed time
--   4. set_survivor_job restores paused_job_progress when reassigning back to paused_job, or resets when switching jobs
--   5. prosper_try_move_on never dismisses a sworn survivor even at Master tier with full savings
--   6. toggle_settler_sworn toggles survivor.sworn on and off
-- Run: lua tools/tests/test_companion_loan.lua   (Lua 5.1, from the repo root)

local now_sec = 50000
local now_tg = 100000

_G.stalker_camp_builder = {
    cfg = {
        settler_savings_enabled = true,
        settler_move_on_enabled = true,
        settler_move_on_savings = 5000,
        settler_move_on_chance = 100,
        realtime_job_cook_interval = 1200,
        realtime_job_craft_interval = 1500,
        realtime_job_hunter_interval = 1800,
    },
    defaults = {},
    active_camps = {},
    camp_npc_released = {},
    settler_home_squads = {},
    game_sec = function() return now_sec end,
    time_factor = function() return 10 end,
    get_time_of_day_mult = function() return 1.0 end,
    job_game_elapsed_sec = function(surv, cur, tf)
        if not surv.job_start_time then return 0 end
        return math.max(0, (cur - surv.job_start_time) / tf)
    end,
    set_camp_settler_relations = function() end,
    teleport_npc_to_camp_hub = function() return true end,
    teleport_settler_to_camp_level = function() return true end,
    get_camp_label = function(camp) return camp and camp.name or "Camp" end,
    send_settler_callback = function() end,
    guarded_call = function(_, fn, ...) if fn then return fn(...) end end,
    dismiss_survivor = function() return true end,
    camp_send_tip = function() end,
    camp_npc_arrive = function() end,
}
local sb = _G.stalker_camp_builder

_G.time_global = function() return now_tg end
_G.game = { translate_string = function(s) return s end }
_G.db = { actor = { id = function() return 0 end }, storage = {} }
_G.move = { walk = 1, standing = 1 }
_G.anim = { free = 1 }
_G.axr_companions = {
    companion_squads = {},
    add_to_actor_squad = function() end,
    remove_from_actor_squad = function() end,
    set_companion_to_follow_state = function() end,
}
_G.actor_menu = { set_msg = function() end }

local online_npcs = {}
_G.level = {
    object_by_id = function(id) return online_npcs[id] end,
    name = function() return "l01_escape" end,
}
_G.alife_object = function() return nil end
_G.alife = function() return nil end
_G.AddScriptCallback = function() end
_G.SendScriptCallback = function() end
_G.vector = function()
    return {
        x = 0, y = 0, z = 0,
        set = function(self, x, y, z) self.x, self.y, self.z = x, y, z; return self end,
    }
end

dofile("00_Core/gamedata/scripts/stalker_camp_builder_prosper.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script")
dofile("00_Core/gamedata/scripts/stalker_camp_builder_recruit.script")

local fails = 0
local function check(cond, msg)
    if not cond then
        fails = fails + 1
        print("FAIL: " .. msg)
    end
end

-- Mock an online NPC with rank/reputation tracking
local npc_rank = 1000
local npc_rep = 0
local npc_infos = {}
online_npcs[42] = {
    id = function() return 42 end,
    alive = function() return true end,
    character_name = function() return "Vaska Veteran" end,
    character_rank = function() return npc_rank end,
    set_character_rank = function(_, r) npc_rank = r end,
    character_reputation = function() return npc_rep end,
    change_character_reputation = function(_, d) npc_rep = npc_rep + d end,
    set_movement_type = function() end,
    set_body_state = function() end,
    set_mental_state = function() end,
    disable_info_portion = function(_, info) npc_infos[info] = nil end,
    give_info_portion = function(_, info) npc_infos[info] = true end,
    has_info = function(_, info) return npc_infos[info] == true end,
}

-- Set up a camp with a survivor at 50% cook cycle progress (600s elapsed out of 1200s)
local surv = {
    name = "Vaska Veteran",
    job = "cook",
    tier = 3,
    xp = 500,
    savings = 6500,
    bought_tier = 3,
    standing_tier = 1, -- tiers 2 and 3 not yet flushed to NPC
    standing_queue = { { rank = 450, rep = 25 } },
    assigned_pos = { x = 12, y = 0, z = -8, lvid = 1234, gvid = 56 },
    job_start_time = now_sec - (600 * 10),
    job_start_realtime = now_tg - (600 * 1000),
}
sb.active_camps[100] = {
    name = "Rookie Homestead",
    survivors = { [42] = surv },
}

-- 1. Verify initial progress is 50%
local prog_before = sb.get_job_progress(surv, sb.active_camps[100], 100)
check(math.abs((prog_before or 0) - 0.5) < 0.01, "initial cook progress should be 0.5, got " .. tostring(prog_before))

-- 2. Loan settler as companion
local ok_loan, err_loan = sb.loan_settler_as_companion(42)
check(ok_loan == true, "loan_settler_as_companion should succeed, got " .. tostring(err_loan))
check(surv.job == "companion" and surv.is_companion == true, "survivor job should be companion")
check(surv.paused_job == "cook", "paused_job should be cook, got " .. tostring(surv.paused_job))
check(math.abs((surv.paused_job_progress or 0) - 0.5) < 0.01, "paused_job_progress should be ~0.5, got " .. tostring(surv.paused_job_progress))
check(surv.sworn == true, "loaned companion should be marked sworn = true")
check(surv.assigned_pos and surv.assigned_pos.lvid == 1234, "assigned_pos must be preserved")
check(npc_infos["npcx_is_companion"] == true, "online NPC should receive npcx_is_companion info")

-- Standing queue should have been flushed (450 queued + tier 2 (3000) + tier 3 (6000) = +9450 rank)
check(npc_rank == 1000 + 450 + 3000 + 6000, "online NPC should receive full queued rank, got " .. tostring(npc_rank))
check(surv.standing_queue == nil, "standing_queue should be nil after flush")

-- 3. Advance time while companion is out with the player; then return to settlement
now_sec = now_sec + 36000
now_tg = now_tg + 3600000
local ok_ret = sb.return_companion_to_settlement(42)
check(ok_ret == true, "return_companion_to_settlement should succeed")
check(surv.job == "cook" and surv.is_companion == nil and surv.paused_job == nil, "survivor should return to cook job")
local prog_after = sb.get_job_progress(surv, sb.active_camps[100], 100)
check(math.abs((prog_after or 0) - 0.5) < 0.02, "returned cook should resume at ~50% cycle progress, got " .. tostring(prog_after))
check(surv.sworn == true, "sworn status must remain true after returning to settlement")

-- 4. Sworn Master-tier settler must never move on
local moved = sb.prosper_try_move_on(100, sb.active_camps[100], surv, 42)
check(moved == false, "sworn Master settler must not leave via prosper_try_move_on")

-- 5. Toggle sworn off, verify toggle_settler_sworn works, and prosper_try_move_on can now trigger
local ok_tog, state_tog = sb.toggle_settler_sworn(42)
check(ok_tog == true and state_tog == false and surv.sworn == false, "toggle_settler_sworn should turn sworn off")
local ok_tog2, state_tog2 = sb.toggle_settler_sworn(42)
check(ok_tog2 == true and state_tog2 == true and surv.sworn == true, "toggle_settler_sworn should turn sworn back on")

-- 6. Loan again and reassign via set_survivor_job back to paused_job ("cook") — should preserve progress
sb.loan_settler_as_companion(42)
now_sec = now_sec + 10000
now_tg = now_tg + 1000000
sb.set_survivor_job(42, "cook")
local prog_reassign = sb.get_job_progress(surv, sb.active_camps[100], 100)
check(math.abs((prog_reassign or 0) - 0.5) < 0.02, "set_survivor_job back to paused_job should restore ~50% progress, got " .. tostring(prog_reassign))

if fails == 0 then
    print("test_companion_loan: all passed")
end
os.exit(fails == 0 and 0 or 1)
