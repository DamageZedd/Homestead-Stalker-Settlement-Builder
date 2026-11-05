-- Medic batches pay for their own inputs. Run: lua tools/tests/test_medic_batch.lua (from the repo root)
local src = (io.open("00_Core/gamedata/scripts/stalker_camp_builder_jobs.script", "rb"):read("*a"):gsub("\r", ""))
local body = src:match("(stalker_camp_builder%.MEDIC_RARE_BATCH_MAX = 4.-\nend)\n")
assert(body, "medic_batch_size not found")
stalker_camp_builder = {}
setfenv(loadstring(body), setmetatable({ stalker_camp_builder = stalker_camp_builder, mmin = math.min, mmax = math.max }, { __index = _G }))()
local f = stalker_camp_builder.medic_batch_size
local fails = 0
local function eq(a, b, m) if a ~= b then fails = fails + 1; print("FAIL " .. m .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end end
eq(stalker_camp_builder.MEDIC_RARE_BATCH_MAX, 4, "rare batch cap")
eq(f(8, 40, 5), 8, "40 vodka uses pay for 8 akvatab")
eq(f(8, 12, 5), 2, "12 uses pay for 2 akvatab")
eq(f(8, 5, 5), 1, "exactly one set")
eq(f(8, 3, 5), 1, "never below 1 (the caller checked the first set)")
eq(f(4, nil, 0), 4, "cloth batch: no vodka limit")
eq(f(nil, nil, 0), 1, "nil want")
-- the code applies the cap and the batch size
check = src:find('if target_sec ~= "bandage" then mult = math.min(mult, stalker_camp_builder.MEDIC_RARE_BATCH_MAX) end', 1, true)
eq(check ~= nil, true, "rare cap applied in process_medic_job")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("medic batch OK")
