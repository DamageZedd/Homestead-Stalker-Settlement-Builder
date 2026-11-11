-- Regression: the Settlements page built two buttons (btn_companion_loan, btn_sworn_toggle) that only
-- the core XML had. Every FOMOD install replaces that XML with a theme's, and Init3tButton on a
-- missing node is an engine assert, so opening the page crashed the game. Every job_content button
-- the PDA script builds by a fixed path must exist in the core XML and in all three theme XMLs.
-- Run: lua tools/tests/test_pda_xml_nodes.lua   (Lua 5.1, from the repo root)
local function slurp(p) local f = assert(io.open(p, "rb")); local s = f:read("*a"); f:close(); return s end
local src = slurp("00_Core/gamedata/scripts/ui_stalker_camp_builder_pda.script")
local xmls = {
    "00_Core/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml",
    "01_Theme_Modern/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml",
    "01_Theme_ModernVanilla/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml",
    "01_Theme_Vanilla/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml",
}

-- the job_content buttons the script builds by a fixed path
local paths, seen = {}, {}
-- (a path closed by `",` is whole; one joined with `..` is built at run time and is skipped)
for path in src:gmatch('xml:Init3tButton%("(job_content:[%w_]+)",') do
    if not seen[path] then seen[path] = true; paths[#paths + 1] = path end
end
assert(#paths > 0, "no job_content buttons found")

local fails = 0
for _, xp in ipairs(xmls) do
    local x = slurp(xp)
    for _, path in ipairs(paths) do
        local leaf = path:match(":([%w_]+)$")
        if not x:find("<" .. leaf .. "[%s>]") then
            fails = fails + 1
            print("FAIL " .. xp .. " lacks <" .. leaf .. ">")
        end
    end
end
if fails == 0 then print("OK (" .. #paths .. " buttons in " .. #xmls .. " XMLs)") end
os.exit(fails == 0 and 0 or 1)
