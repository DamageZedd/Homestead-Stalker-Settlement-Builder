-- Regression: a tester saw a merc outpost abandoned, reclaimed by mercs, abandoned again, and so on.
-- An outpost whose garrison is killed (by the player, raiders or offline combat) did not record the
-- faction that lost it or count the takeover, so the reclaim roll could bring the same faction back
-- every time. Both ways an outpost empties now record them, as the time-up path always did.
-- Run: lua tools/tests/test_rival_reclaim.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script", "rb"):read("*a"):gsub("\r", "")
local body = src:match("\n(local function mark_rival_garrison_eliminated.-\nend)\n")
assert(body, "mark_rival_garrison_eliminated not found")

local env = setmetatable({
    mrandom = function(a) return a end,
    sformat = string.format,
    game = { translate_string = function(s) return s end },
    stalker_camp_builder = { camp_send_tip = function() end },
    relation_registry = { community_relation = function() return 0 end },
}, { __index = _G })
local chunk = assert(loadstring(body .. "\nreturn mark_rival_garrison_eliminated"))
setfenv(chunk, env)
local f = chunk()

local sb = { cfg = {}, sync_rival_camp_map_spot = function() end }
local camp = { faction = "killer", squad_id = 5, takeover_count = 1 }
f(sb, camp, nil, 1000)

local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end
eq(camp.status, "unoccupied", "outpost empty")
eq(camp.last_faction, "killer", "the faction that lost it is recorded")
eq(camp.takeover_count, 2, "the takeover is counted")
eq(camp.faction, nil, "no faction holds it")
if fails == 0 then print("OK") end
os.exit(fails == 0 and 0 or 1)
