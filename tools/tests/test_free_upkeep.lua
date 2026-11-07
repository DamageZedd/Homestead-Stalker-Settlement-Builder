-- Free weapon upkeep at a Repair Bench never lowers a gun's condition. Run: lua tools/tests/test_free_upkeep.lua (from the repo root)
-- Needs only the line the job uses to compute the new condition: a 0.90 gun with a worn part used to drop to 0.80.
local src = (io.open("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script", "rb"):read("*a"):gsub("\r", ""))
local expr = src:match("local target_c = (mmax%(cur_c, mmin%(0%.80, cur_c %+ 0%.15%)%))")
assert(expr, "free upkeep condition line not found (is it the mmax-guarded form?)")
local fails = 0
local function eq(a, b, m) if math.abs(a - b) > 1e-9 then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
local function target(cur_c)
    return setfenv(loadstring("return " .. expr), { mmin = math.min, mmax = math.max, cur_c = cur_c })()
end
eq(target(0.50), 0.65, "0.50 gains 0.15")
eq(target(0.70), 0.80, "0.70 capped at 0.80")
eq(target(0.80), 0.80, "0.80 stays")
eq(target(0.90), 0.90, "0.90 gun with a worn part is not lowered")
eq(target(1.00), 1.00, "1.00 gun is not lowered")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("free upkeep OK")
