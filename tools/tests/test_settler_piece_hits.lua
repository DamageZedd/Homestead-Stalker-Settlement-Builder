-- Settlers take no damage from placed base pieces: npc_on_before_hit in stalker_camp_builder.script
-- cancels a hit whose source is a Hideout Furniture / Homestead piece, and only for settlers.
-- The function is cut out of the (huge) script by its markers and run against stubs.
-- Run: lua tools/tests/test_settler_piece_hits.lua   (Lua 5.1, from the repo root)

local fails = 0
local function ok(c, m) if not c then fails = fails + 1; print("FAIL " .. m) end end

local f = assert(io.open("00_Core/gamedata/scripts/stalker_camp_builder.script", "rb"))
local src = f:read("*a"):gsub("\r\n", "\n"); f:close()
local a = src:find("local hf_piece_sections = {}", 1, true)
local b = src:find("-- safe_register_callback is defined at top of file", a, true)
assert(a and b, "markers not found")

local reads = 0
ini_sys = { r_string_ex = function(_, sec, key)
    reads = reads + 1
    if key == "script_binding" then
        if sec == "placeable_wall" then return "bind_hf_base.bind" end
        if sec == "wpn_ak74" then return "bind_item.bind" end
    end
end }
stalker_camp_builder = { settler_lookup = { [10] = { is_rival = false }, [11] = { is_rival = true } } }
local chunk = assert(loadstring(src:sub(a, b - 1)))
chunk()

local function obj(id, sec) return { id = function() return id end, section = function() return sec end } end
local function hit(npc, sec)
    local flags = { ret_value = true }
    stalker_camp_builder.npc_on_before_hit(npc, { draftsman = obj(99, sec) }, 0, flags)
    return flags.ret_value
end

ok(hit(obj(10, "stalker"), "placeable_wall") == false, "settler: hit from a base piece cancelled")
ok(hit(obj(10, "stalker"), "wpn_ak74") == true, "settler: hit from anything else kept")
ok(hit(obj(11, "stalker"), "placeable_wall") == true, "rival settler: kept")
ok(hit(obj(12, "stalker"), "placeable_wall") == true, "non-settler: kept")
local pf = { ret_value = true }
stalker_camp_builder.actor_on_before_hit({ draftsman = obj(99, "placeable_wall") }, 0, pf)
ok(pf.ret_value == false, "player: hit from a base piece cancelled")
pf = { ret_value = true }
stalker_camp_builder.actor_on_before_hit({ draftsman = obj(99, "wpn_ak74") }, 0, pf)
ok(pf.ret_value == true, "player: hit from anything else kept")
pf = { ret_value = true }
stalker_camp_builder.actor_on_before_hit({}, 0, pf)
ok(pf.ret_value == true, "player: no source kept")
local flags = { ret_value = true }
stalker_camp_builder.npc_on_before_hit(obj(10, "stalker"), { }, 0, flags)
ok(flags.ret_value == true, "no source: kept")
stalker_camp_builder.npc_on_before_hit(obj(10, "stalker"), nil, 0, flags)
local before = reads
hit(obj(10, "stalker"), "placeable_wall"); hit(obj(10, "stalker"), "placeable_wall")
ok(reads == before, "section read once, then cached")

print(fails == 0 and "settler piece hit tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
