-- Regression: an outpost snapped by the old ground probe (which took a far AI node's height on a
-- slope) floated for good, because the snap pass skipped every camp already marked snapped. Such a
-- camp is now checked once more (ground_fix_v5), its floating pieces go down to the ground, and a
-- piece standing on another (the radio on its table) moves with its base instead of being dropped
-- into the table by the ray, which passes through dynamic objects.
-- Run: lua tools/tests/test_rival_snap_existing.lua   (Lua 5.1, from the repo root)
stalker_camp_builder = { cfg = {}, defaults = {} }
local sb = stalker_camp_builder

local vmt = {}
vmt.__index = { set = function(v, x, y, z) v.x, v.y, v.z = x, y, z; return v end }
function vector() return setmetatable({ x = 0, y = 0, z = 0 }, vmt) end
local function V(x, y, z) return vector():set(x, y, z) end

dofile("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script")

local fails = 0
local function near(a, b, msg)
    if type(a) ~= "number" or math.abs(a - b) > 1e-3 then
        fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b))
    end
end
local function eq(a, b, msg)
    if a ~= b then fails = fails + 1; print("FAIL " .. msg .. ": got " .. tostring(a) .. ", want " .. tostring(b)) end
end

-- the ground falls 0.5 m per metre along x (y = 10 - 0.5 x); the only AI node is at x = 0
local function ground(x) return 10 - 0.5 * x end
sb.get_surface_y = function(x, z, ref_y, up, down)
    local g = ground(x)
    local top = ref_y + up
    if g <= top and g >= top - (up + down) then return g end
    return nil
end
local online = {}
level = {
    name = function() return "l01_escape" end,
    vertex_id = function() return 5 end,
    vertex_position = function() return V(0, ground(0), 0) end,
    object_by_id = function(id) return online[id] end,
}
ini_sys = { section_exist = function() return true end, r_string_ex = function() return nil end }

-- a server object: assigning its position copies the vector, as the engine's property does
local objs = {}
local function se(id, sec, x, y, z)
    local data = { position = V(x, y, z) }
    local o = setmetatable({ id = id, m_level_vertex_id = 5, m_game_vertex_id = 1 }, {
        __index = function(_, k) return data[k] end,
        __newindex = function(_, k, v)
            if k == "position" then data.position = V(v.x, v.y, v.z) else rawset(_, k, v) end
        end,
    })
    function o.section_name() return sec end
    objs[id] = o
    return o
end
alife = function() return { object = function(_, id) return objs[id] end } end

-- an old save: the chest sits right on the node; a crate 4 m down the slope floats at the node's
-- height (ground 8.0, stored 10.03); the table beside it floats too, and the radio stands on it
local chest = se(100, "inv_box", 0, 10.08, 0)
local crate = se(101, "placeable_box_wood", 4, 10.03, 0)
local tbl = se(102, "placeable_table1", 3, 10.03, 1)
local radio = se(103, "placeable_radio", 3, 10.83, 1)
sb.rival_camps = {
    [1] = {
        level = "l01_escape", chest_id = 100, position = { x = 0, y = 10.08, z = 0 },
        snapped = true, ground_snapped_v2 = true, ground_snapped_v4 = true,
        decorations = { 101, 102, 103 },
        decor_sections = { [101] = "placeable_box_wood", [102] = "placeable_table1", [103] = "placeable_radio" },
    },
}
local camp = sb.rival_camps[1]

sb.snap_rival_camps_to_ground()
near(crate.position.y, ground(4) + 0.03, "floating crate goes down to the ground")
near(tbl.position.y, ground(3) + 0.03, "floating table goes down to the ground")
near(radio.position.y, ground(3) + 0.03 + 0.8, "radio keeps its height above the table")
near(chest.position.y, 10.08, "chest on the node is left where it is")
eq(camp.ground_fix_v5, true, "camp marked checked")

-- checked once: a second pass does nothing
crate.position = V(4, 12.0, 0)
sb.snap_rival_camps_to_ground()
near(crate.position.y, 12.0, "a checked camp is not snapped again")

-- an online piece: its server position is not where it stands, so the camp is not marked
camp.ground_fix_v5 = nil
crate.position = V(4, 10.03, 0)
online[101] = {}
sb.snap_rival_camps_to_ground()
eq(camp.ground_fix_v5, nil, "not marked while a piece is online")
online[101] = nil

if fails == 0 then print("OK") end
os.exit(fails == 0 and 0 or 1)
