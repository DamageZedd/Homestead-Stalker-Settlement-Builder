-- Regression: outpost pieces floated on slopes. find_ground_anchor replaced the downward ray's
-- ground hit with the height of the nearest AI node whenever the two differed by more than 0.5 m,
-- and that node may stand up to 5 m away: 4 m up a slope it is well over 0.5 m higher, so the
-- piece took the node's height and floated. Only a hit above the walkable ground (a tree, rock
-- overhang or roof) may be replaced.
-- Run: lua tools/tests/test_rival_ground_anchor.lua   (Lua 5.1, from the repo root)
local src = io.open("00_Core/gamedata/scripts/stalker_camp_builder_rivals.script", "rb"):read("*a"):gsub("\r", "")
local body = src:match("\n(find_ground_anchor = function%(.-\nend)\n")
assert(body, "find_ground_anchor not found")

local fails = 0
local function eq(a, b, msg)
    if math.abs(a - b) > 1e-6 then fails = fails + 1; print(("FAIL %s: got %s, want %s"):format(msg, a, b)) end
end

local function vec(x, y, z) return { x = x or 0, y = y or 0, z = z or 0 } end
local vmt = { __index = { set = function(v, x, y, z) v.x, v.y, v.z = x, y, z; return v end } }
local function vector() return setmetatable(vec(), vmt) end

-- a world with a ground ray (static geometry) and one AI node
local world
local env = setmetatable({
    vector = vector,
    stalker_camp_builder = {
        -- a downward ray from ref_y + up over up + down metres: the highest static surface it meets
        get_surface_y = function(x, z, ref_y, up, down)
            local top = ref_y + up
            local best
            for _, s in ipairs(world.statics) do
                if s <= top and s >= top - (up + down) and (not best or s > best) then best = s end
            end
            return best
        end,
    },
    level = {
        vertex_id = function() return 7 end,
        vertex_position = function() return world.node end,
    },
}, { __index = _G })
local chunk = assert(loadstring("local find_ground_anchor\n" .. body .. "\nreturn find_ground_anchor"))
setfenv(chunk, env)
local find_ground_anchor = chunk()

-- 1. a slope: the ground here is 10.0, the nearest node is 4 m away uphill at 12.0
world = { statics = { 10.0 }, node = vec(4, 12.0, 0) }
local _, _, y = find_ground_anchor(0, 0, 10.0, 10.0)
eq(y, 10.0, "slope: the ray's ground is kept, not the uphill node's height")

-- 2. downhill: the node 4 m away is at 8.0, the ground here 10.0
world = { statics = { 10.0 }, node = vec(4, 8.0, 0) }
_, _, y = find_ground_anchor(0, 0, 10.0, 10.0)
eq(y, 10.0, "downhill: the ray's ground is kept")

-- 3. a canopy: the ray first meets a branch at 13.0, the ground (and the node under the spot) at 10.0
world = { statics = { 13.0, 10.0 }, node = vec(0.2, 10.0, 0) }
_, _, y = find_ground_anchor(0, 0, 10.0, 10.0)
eq(y, 10.0, "canopy: a hit above the walkable ground is not used")

-- 4. a canopy over a slope: branch at 15.0, ground here 11.0, node 3 m away at 10.0
world = { statics = { 15.0, 11.0 }, node = vec(3, 10.0, 0) }
_, _, y = find_ground_anchor(0, 0, 11.0, 11.0)
eq(y, 11.0, "canopy over a slope: the ground under the branch is found")

-- 5. flat ground with the node right under it: unchanged
world = { statics = { 10.0 }, node = vec(0.3, 10.05, 0) }
_, _, y = find_ground_anchor(0, 0, 10.0, 10.0)
eq(y, 10.0, "flat ground")

if fails == 0 then print("OK") end
os.exit(fails == 0 and 0 or 1)
