-- Standalone tests for the PDA live-refresh helpers (ui_stalker_camp_builder_pda_perf.script)
-- and the theme's cached colors (ui_stalker_camp_builder_theme.script).
-- Run: lua tools/tests/test_pda_perf.lua   (Lua 5.1, from the repo root)

local fails = 0
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end

-- engine stubs ---------------------------------------------------------------------------
local argb_calls = 0
function GetARGB(a, r, g, b)
    argb_calls = argb_calls + 1
    return ((a * 256 + r) * 256 + g) * 256 + b
end

local translations = {
    stalker = "Loner", loner = "Loner", dolg = "Duty", duty = "Duty",
    freedom = "Freedom", svoboda = "Freedom", killer = "Mercenary", mercenary = "Mercenary",
    csky = "Clear Sky", clear_sky = "Clear Sky", ecolog = "Eco(log)+%", monolith = "Monolith",
    bandit = "Bandit", renegade = "", army = "Military",
    -- military: no translation (the id comes back)
    st_pda_settlement_job_guard = "Guard",
    st_pda_sv_needs_fed = "Fed",
}
local tr_calls = 0
game = { translate_string = function(id)
    tr_calls = tr_calls + 1
    local v = translations[id]
    if v == nil then return id end
    return v
end }

-- each .script is its own namespace in the engine: load it into a table of its name
local function load_module(path, name)
    local env = setmetatable({}, { __index = _G })
    local chunk = assert(loadfile(path))
    setfenv(chunk, env)
    chunk()
    _G[name] = env
    return env
end
local theme = load_module("00_Core/gamedata/scripts/ui_stalker_camp_builder_theme.script", "ui_stalker_camp_builder_theme")
local perf = load_module("00_Core/gamedata/scripts/ui_stalker_camp_builder_pda_perf.script", "ui_stalker_camp_builder_pda_perf")

-- throttle_due ---------------------------------------------------------------------------
local due, keep = perf.throttle_due(nil, 5000, 1000)
eq(due, true, "nil last is due"); eq(keep, 5000, "nil last starts at now")
due, keep = perf.throttle_due(0, 300, 1000)
eq(due, true, "Reset (0) is due at once"); eq(keep, 300, "Reset (0) starts at now, not 0 + interval")
due, keep = perf.throttle_due(5000, 5999, 1000)
eq(due, false, "not yet due"); eq(keep, 5000, "not due keeps last")
due, keep = perf.throttle_due(5000, 6000, 1000)
eq(due, true, "due on the cadence"); eq(keep, 6000, "cadence 1")
due, keep = perf.throttle_due(5000, 6016, 1000)
eq(due, true, "a late frame is due"); eq(keep, 6000, "a late frame keeps the cadence (no drift)")
due, keep = perf.throttle_due(5000, 4000, 1000)
eq(due, true, "clock went back: due"); eq(keep, 4000, "clock went back: restart at now")
due, keep = perf.throttle_due(5000, 60000, 1000)
eq(due, true, "long gap: due once"); eq(keep, 60000, "long gap: restart at now, no burst")
-- a frame loop at ~60 fps for 10 s fires 10 times (500 ms cadence before: 20, + 10 from actor_on_update)
local last, fired = 0, 0
for t = 16, 10000, 16 do
    local d, k = perf.throttle_due(last, t, 1000)
    if d then fired = fired + 1; last = k end
end
eq(fired, 10, "10 refreshes in 10 s")
-- OnManualRefresh writes time_global() as the last tick: the next one is a cadence later
due = perf.throttle_due(7000, 7500, 1000)
eq(due, false, "manual refresh pushes the next tick")

-- theme: cached colors equal the uncached ones ----------------------------------------------
local function ref_argb(role, alpha)
    local v = ({ heading = {238, 196, 112}, body = {200, 200, 200}, dim = {160, 160, 160},
        danger = {238, 28, 36}, warn = {238, 155, 23}, good = {56, 209, 115}, bright = {255, 255, 255} })[role]
        or {200, 200, 200}
    return GetARGB(alpha or 255, v[1], v[2], v[3])
end
for _, role in ipairs({ "heading", "body", "dim", "danger", "warn", "good", "bright", "nonsense" }) do
    eq(theme.argb(role), ref_argb(role), "argb " .. role)
    eq(theme.argb(role), ref_argb(role), "argb cached " .. role)
    eq(theme.argb(role, 120), ref_argb(role, 120), "argb alpha " .. role)
end
argb_calls = 0
for _ = 1, 100 do theme.argb("danger"); theme.argb("body") end
eq(argb_calls, 0, "argb hits the cache (no GetARGB per row)")
eq(theme.argb(nil), ref_argb("body"), "argb nil role is body")
eq(theme.markup("heading"), "%c[255,238,196,112]", "markup heading")
eq(theme.markup("heading"), "%c[255,238,196,112]", "markup heading cached")
eq(theme.markup(nil), "%c[255,200,200,200]", "markup nil is body")

-- the original recolor and colorize, as reference ------------------------------------------
local legacy = {
    ["238,196,112"] = "heading", ["238,153,26"] = "heading", ["255,230,150"] = "heading",
    ["220,220,220"] = "body", ["200,200,200"] = "body",
    ["144,238,144"] = "bright", ["100,200,255"] = "bright", ["180,220,255"] = "bright",
    ["128,222,234"] = "bright",
    ["200,255,200"] = "good", ["100,255,100"] = "good",
    ["255,100,100"] = "danger", ["255,120,120"] = "danger",
    ["255,180,100"] = "warn", ["255,160,60"] = "warn",
}
local function ref_markup(role)
    local v = ({ heading = {238, 196, 112}, body = {200, 200, 200}, bright = {255, 255, 255},
        good = {56, 209, 115}, warn = {238, 155, 23}, danger = {238, 28, 36} })[role]
    return string.format("%%c[255,%d,%d,%d]", v[1], v[2], v[3])
end
local function ref_recolor(text)
    if type(text) ~= "string" or not text:find("%c[", 1, true) then
        return text
    end
    local function swap(r, g, b)
        local role = legacy[r .. "," .. g .. "," .. b]
        return role and ref_markup(role) or nil
    end
    local function swap3(r, g, b)
        return swap(r, g, b) or string.format("%%c[255,%s,%s,%s]", r, g, b)
    end
    text = text:gsub("%%c%[%d+,(%d+),(%d+),(%d+)%]", swap)
    return (text:gsub("%%c%[(%d+),(%d+),(%d+)%]", swap3))
end
local function ref_escape(str)
    return (str:gsub("([%(%)%.%%%+%-%*%?%[%]%^%$])", "%%%1"))
end
local function ref_colorize_base(text)
    if not text or text == "" then return "" end
    local faction_colors = theme.faction_codes()
    for comm, clr in pairs(faction_colors) do
        local comm_str = game.translate_string(comm)
        if comm_str and comm_str ~= comm and comm_str ~= "" then
            text = text:gsub(ref_escape(comm_str), function()
                return string.format("%%c[%s]%s%%c[200,200,200]", clr, comm_str)
            end)
        end
    end
    text = text:gsub("Ambushed", function() return "%c[255,100,100]Ambushed%c[200,200,200]" end)
    text = text:gsub("Defeated", function() return "%c[200,255,200]Defeated%c[200,200,200]" end)
    text = text:gsub("Recovered", function() return "%c[180,220,255]Recovered%c[200,200,200]" end)
    text = text:gsub("Deposited", function() return "%c[238,153,26]Deposited%c[200,200,200]" end)
    return text
end
local function ref_colorize(text) return ref_recolor(ref_colorize_base(text)) end

local samples = {
    "", "plain text, no names",
    "Duty patrol Ambushed near the Bar; Freedom Defeated them.",
    "Loner Recovered 3 stashes and Deposited them at camp (Loner, Loner).",
    "Eco(log)+% scientists: Clear Sky and Mercenary seen. Military pushed back.",
    "%c[255,100,100]Raid%c[200,200,200] on Monolith: %c[238,196,112]Bandit%c[200,200,200] lost",
    "%c[255,1,2,3]odd%c[9,9,9] codes and a 100% sign",
    "Renegade and military are not translated; Duty Duty",
    "Guard: Expedition to Zaton (45% - 3m 05s remaining)",
}
for i, s in ipairs(samples) do
    eq(perf.colorize(s), ref_colorize(s), "colorize sample " .. i)
    eq(perf.colorize(s), ref_colorize(s), "colorize sample " .. i .. " (memo)")
    eq(theme.recolor(s), ref_recolor(s), "recolor sample " .. i)
end
eq(perf.colorize(nil), ref_colorize(nil), "colorize nil")

-- the faction patterns are built once per open, not per text
perf.reset()
tr_calls = 0
for i = 1, 50 do perf.colorize("Duty report " .. i) end
local n_factions = 0
for _ in pairs(theme.faction_codes()) do n_factions = n_factions + 1 end
eq(tr_calls, n_factions, "translations once per open for 50 texts")

-- memo stays bounded and right after it is dropped
for i = 1, 400 do
    local s = "Freedom Recovered " .. i
    if perf.colorize(s) ~= ref_colorize(s) then eq(perf.colorize(s), ref_colorize(s), "memo overflow " .. i) end
end

-- job_label / tr ---------------------------------------------------------------------------
perf.reset()
tr_calls = 0
eq(perf.job_label("guard"), "Guard", "job label translated")
eq(perf.job_label("woodcutter"), "Woodcutter", "job label fallback capitalized")
eq(perf.job_label("guard"), "Guard", "job label cached")
eq(perf.job_label("woodcutter"), "Woodcutter", "job label fallback cached")
eq(tr_calls, 2, "job labels translated once each")
eq(perf.tr("st_pda_sv_needs_fed"), "Fed", "tr")
eq(perf.tr("st_pda_sv_needs_fed"), "Fed", "tr cached")
eq(perf.tr("st_missing"), "st_missing", "tr of a missing id")
eq(tr_calls, 4, "tr once per id")
perf.reset()
perf.job_label("guard")
eq(tr_calls, 5, "reset drops the cache")

if fails == 0 then print("test_pda_perf: all passed") else print("test_pda_perf: " .. fails .. " failed"); os.exit(1) end
