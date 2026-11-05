-- Repair fee scales with the value restored. Run: lua tools/tests/test_repair_fee.lua (from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script", "rb"):read("*a")
local consts = src:match("(local REPAIR_FEE_RU_PER_USE.-\nend)\n")
assert(consts, "repair_fee_uses not found")
stalker_camp_builder = {}
mmin, mmax = math.min, math.max
setfenv(loadstring(consts), setmetatable({ stalker_camp_builder = stalker_camp_builder, mmin = mmin, mmax = mmax, math = math, tonumber = tonumber }, { __index = _G }))()
local f = stalker_camp_builder.repair_fee_uses
local fails = 0
local function eq(a, b, m) if a ~= b then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
eq(f(4890, 0.25), 1, "pistol 25%")
eq(f(26950, 0.25), 3, "AK 25%")
eq(f(26950, 0.5625), 6, "AK Master workshop+bench (capped)")
eq(f(129680, 0.56), 6, "exo outfit capped")
eq(f(100, 0.25), 1, "floor")
eq(f(nil, nil), 1, "nil safe")
eq(f(50000, 0), 1, "nothing restored still costs one")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("repair fee OK")
