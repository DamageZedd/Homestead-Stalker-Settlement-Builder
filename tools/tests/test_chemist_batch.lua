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

-- the PDA's Drug-Making Kit line for a Chemist matches process_chemist_job: +1 only when no lab-bonus structure stands
local pda = (io.open("00_Core/gamedata/scripts/ui_stalker_camp_builder_pda.script", "rb"):read("*a"):gsub(string.char(13), ""))
local NL = string.char(10)
local label_src = pda:match("(local function drugkit_boost_label.-" .. NL .. "end)" .. NL)
assert(label_src, "drugkit_boost_label not found")
local label = loadstring(label_src .. NL .. "return drugkit_boost_label")()
eq(label("chemist", { structures = { [1] = "stove" } }), " [Distillery Kit: +1 Output]", "kit + stove: +1")
eq(label("chemist", { structures = {} }), " [Distillery Kit: +1 Output]", "kit alone: +1")
eq(label("chemist", { structures = { [1] = "distiller" } }), "", "kit + distiller: nothing")
eq(label("chemist", { structures = { [1] = "medstation" } }), "", "kit + infirmary: nothing")
eq(label("chemist", { structures = { [1] = "stove", [2] = "chemist_station" } }), "", "kit + station: nothing")
eq(label("chemist", nil), " [Distillery Kit: +1 Output]", "no camp record")
eq(label("brewer", { structures = { [1] = "distiller" } }), " [Distillery Kit: 2x Boost]", "brewer line unchanged")
local _, n2x = pda:gsub("Distillery Kit: 2x Boost", "")
eq(n2x, 1, "one 2x text left, in the brewer branch")
if fails > 0 then print(fails .. " FAILED"); os.exit(1) end
print("chemist batch OK")
