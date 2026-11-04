-- Regression: the job tick must receive the paused reason (a `a, b, c = x and f()` keeps only the
-- first value, so reason_short was always nil and the "Storage Full" cut never applied).
-- Run: lua tools/tests/test_jobs_paused_status.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script", "rb"):read("*a")
local block = src:match("(local is_paused, reason_short, reason_detail.-)\n%s*%-%- the settler's cut")
assert(block, "paused-status block not found")
local env = setmetatable({
    survivor = {}, camp = {}, hub_id = 1, camp_snap = {},
    sb = { get_job_paused_status = function() return true, "Storage Full", "detail" end },
}, { __index = _G })
local chunk = assert(loadstring(block .. "\nreturn is_paused, reason_short, reason_detail"))
setfenv(chunk, env)
local p, s, d = chunk()
local fails = 0
if p ~= true or s ~= "Storage Full" or d ~= "detail" then
    fails = 1; print("FAIL paused status values lost: " .. tostring(p) .. ", " .. tostring(s) .. ", " .. tostring(d))
end
env.sb.get_job_paused_status = nil
p, s, d = chunk()
if p then fails = fails + 1; print("FAIL missing getter must leave job unpaused") end
if fails == 0 then print("OK") end
os.exit(fails == 0 and 0 or 1)
