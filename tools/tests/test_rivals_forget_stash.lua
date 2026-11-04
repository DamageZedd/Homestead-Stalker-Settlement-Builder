-- Regression: releasing a rival camp must clear its chest from player_created_stashes. The old code
-- read a global `m_data` that does not exist in this script's namespace, so the entry leaked.
-- Run: lua tools/tests/test_rivals_forget_stash.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script", "rb"):read("*a")
local body = src:match("(local function forget_player_stash.-\nend)")
assert(body, "forget_player_stash not found")
assert(not src:find("m_data%.player_created_stashes%[camp"), "bare m_data use remains")
local state = { player_created_stashes = { [42] = "blue_box_item", [7] = "x" } }
local env = setmetatable({ alife_storage_manager = { get_state = function() return state end } }, { __index = _G })
local chunk = assert(loadstring(body .. "\nreturn forget_player_stash"))
setfenv(chunk, env)
local f = chunk()
f(42)
local fails = 0
if state.player_created_stashes[42] ~= nil then fails = fails + 1; print("FAIL chest 42 still registered") end
if state.player_created_stashes[7] ~= "x" then fails = fails + 1; print("FAIL other stash touched") end
env.alife_storage_manager = nil
f(7) -- no storage manager: must not error
if fails == 0 then print("OK") end
os.exit(fails == 0 and 0 or 1)
