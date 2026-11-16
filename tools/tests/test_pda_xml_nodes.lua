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

local required_top_bar = {
    "top_status_bar",
    "status_signal",
    "status_weather",
    "status_clock",
    "status_camp",
}

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
    for _, node in ipairs(required_top_bar) do
        if not x:find("<" .. node .. "[%s>]") then
            fails = fails + 1
            print("FAIL " .. xp .. " lacks <" .. node .. ">")
        end
    end
end

-- BUG 3 invariants on 01_Theme_Modern: CUI3tButton labels must use <text_color>, not r/g/b on <text>,
-- and <backpack><input> must carry a background texture so the filter box renders visibly.
local modern_xml = slurp("01_Theme_Modern/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml")
local modern_btns = 0
local pos = 1
while true do
    local s, _, tag = modern_xml:find("<(btn_[%w_]+)[%s>]", pos)
    if not s then break end
    local _, close_end = modern_xml:find("</" .. tag .. ">", s, true)
    assert(close_end, "unclosed <" .. tag .. "> in 01_Theme_Modern")
    local block = modern_xml:sub(s, close_end)
    if block:find("<text[%s>]") then
        modern_btns = modern_btns + 1
        if block:find("<text[^>]*%sr=") then
            fails = fails + 1
            print("FAIL 01_Theme_Modern <" .. tag .. "> uses legacy <text r=...> instead of <text_color>")
        end
        if not block:find("<text_color>", 1, true) then
            fails = fails + 1
            print("FAIL 01_Theme_Modern <" .. tag .. "> lacks <text_color>")
        end
    end
    pos = close_end + 1
end
assert(modern_btns > 0, "no <btn_*> with <text> found in 01_Theme_Modern")

local bp_block = modern_xml:match("<backpack[%s>].-</backpack>")
assert(bp_block, "missing <backpack> in 01_Theme_Modern")
local bp_input = bp_block:match("<input[%s>].-</input>")
assert(bp_input, "missing <backpack><input> in 01_Theme_Modern")
if not bp_input:find("<texture>[^<]+</texture>") then
    fails = fails + 1
    print("FAIL 01_Theme_Modern <backpack><input> lacks <texture>")
end

if fails == 0 then
    print("OK (" .. #paths .. " buttons + " .. #required_top_bar .. " status nodes in " .. #xmls .. " XMLs; " .. modern_btns .. " modern buttons verified)")
end
os.exit(fails == 0 and 0 or 1)
