-- The invisible colliders must not break in a collision, and one that breaks anyway must be harmless.
-- Engine: a body's m v^2 / 2 above collision_break_threthhold is a strike hit, which breaks a breakable
-- whatever its health, and a frozen piece counts as 1e8 kg. The class keeps the threshold in a static
-- that every breakable's Load overwrites, so vanilla [breakable_object] must have the same value.
-- Run: lua tools/tests/test_collider_unbreakable.lua   (Lua 5.1, from the repo root)

local fails, checks = 0, 0
local function ok(cond, msg)
    checks = checks + 1
    if not cond then fails = fails + 1; print("FAIL " .. msg) end
end

local function read_all(path)
    local f = assert(io.open(path, "rb"))
    local s = f:read("*a")
    f:close()
    return s
end

local function float_at(s, o)   -- little-endian float at 1-based offset o
    local b1, b2, b3, b4 = s:byte(o, o + 3)
    local sign = b4 >= 128 and -1 or 1
    local exp = (b4 % 128) * 2 + math.floor(b3 / 128)
    local frac = (b3 % 128) * 65536 + b2 * 256 + b1
    if exp == 0 then return 0 end
    return sign * (1 + frac / 8388608) * 2 ^ (exp - 127)
end

local function u32_at(s, o)
    local a, b, c, d = s:byte(o, o + 3)
    return a + b * 256 + c * 65536 + d * 16777216
end

local function chunk(s, id)
    local o = 1
    while o <= #s do
        local cid, size = u32_at(s, o), u32_at(s, o + 4)
        if cid == id then return s:sub(o + 8, o + 7 + size) end
        o = o + 8 + size
    end
end

local MIN_THRESHOLD = 1e20      -- 1e8 kg at 1 km/s is 5e13
local BUILDING = "HomesteadHF/gamedata/configs/items/items/items_homestead_building.ltx"
local MESHES = "HomesteadHF/gamedata/meshes/"

-- sections of the colliders
local sections, sec = {}, nil
for line in (read_all(BUILDING) .. "\n"):gmatch("(.-)\r?\n") do
    local name = line:match("^%[([%w_]+)%]")
    if name then
        sec = name:find("^hs_collider_") and { name = name } or nil
        if sec then sections[#sections + 1] = sec end
    elseif sec then
        local k, v = line:match("^([%w_]+)%s*=%s*([^;%s]+)")
        if k then sec[k] = v end
    end
end
ok(#sections == 27, "27 collider sections (" .. #sections .. ")")

for _, s in ipairs(sections) do
    ok(s.class == "O_BRKBL", s.name .. " is a breakable")
    ok((tonumber(s.collision_break_threthhold) or 0) >= MIN_THRESHOLD, s.name .. ": a collision can't break it")

    local ogf = read_all(MESHES .. s.visual:gsub("\\", "/"))
    local names, ik = chunk(ogf, 13), chunk(ogf, 16)
    -- the standing box: bone obb, last 60 bytes of the names chunk (half sizes are its last 12)
    local box_x = float_at(names, #names - 11)
    local box_z = float_at(names, #names - 3)
    ok(box_x > 0.05 and box_z > 0.05, s.name .. ": the standing box keeps its size")
    -- what is left when broken: bone shape after the material name, mass 16 bytes from the end
    local o = ik:find("\0", 5, true) + 1
    ok(math.abs(float_at(ik, o + 4 + 48) - 0.05) < 1e-4, s.name .. ": a broken one is a small box")
    ok(float_at(ik, #ik - 15) <= 1, s.name .. ": a broken one is light (" .. float_at(ik, #ik - 15) .. ")")
end

-- the static is shared: vanilla breakables carry the same threshold
local patch = read_all("HomesteadHF/gamedata/configs/mod_system_homestead_breakable.ltx")
ok(patch:find("![breakable_object]", 1, true), "patches vanilla [breakable_object]")
local value = patch:match("collision_break_threthhold%s*=%s*(%S+)")
ok((tonumber(value) or 0) >= MIN_THRESHOLD, "vanilla breakables get the same threshold")
for _, s in ipairs(sections) do
    ok(s.collision_break_threthhold == value, s.name .. " has the patch's value")
end

print(fails == 0 and ("collider unbreakable tests passed (" .. checks .. " checks)") or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
