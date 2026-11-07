-- Chemist batches pay for their own inputs. Run: lua tools/tests/test_chemist_batch.lua (from the repo root)
local src = (io.open("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script", "rb"):read("*a"):gsub("\r", ""))
local body = src:match("(stalker_camp_builder%.CHEMIST_FUEL_BATCH_MAX = 4.-\nend)\n")
assert(body, "chemist_batch_size not found")
stalker_camp_builder = {}
setfenv(loadstring(body), setmetatable({ stalker_camp_builder = stalker_camp_builder }, { __index = _G }))()
local f = stalker_camp_builder.chemist_batch_size
local fails = 0
local function eq(a, b, m) if a ~= b then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
eq(stalker_camp_builder.CHEMIST_FUEL_BATCH_MAX, 4, "fuel batch cap")
eq(stalker_camp_builder.CHEMIST_POWDER_BATCH_MAX, 6, "powder batch cap")
eq(f(4, 8, 8, 2, 2), 4, "8 charcoal + 8 vodka uses pay for 4 cans")
eq(f(4, 8, 4, 2, 2), 2, "4 vodka uses pay for 2 cans")
eq(f(4, 5, 8, 2, 2), 2, "5 charcoal uses pay for 2 cans")
eq(f(4, 2, 2, 2, 2), 1, "exactly one set")
eq(f(4, 1, 1, 2, 2), 1, "never below 1 (the caller checked the first set)")
eq(f(6, 8, 4, 2, 1), 4, "powder: 4 vodka limits 6 tins to 4")
eq(f(nil, 8, 8, 2, 2), 1, "nil want")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("chemist batch OK")
