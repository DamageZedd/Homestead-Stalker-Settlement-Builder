-- Settlers take no damage from placed base pieces: npc_on_before_hit in stalker_camp_builder.script
-- cancels a piece's physics strike, and only for settlers. The engine gives such a hit the VICTIM as its
-- source (a physics object is no IDamageSource), so a piece is found by being near the victim.
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
hit = { strike = 2, wound = 3, fire_wound = 8, explosion = 7 }
local near = {}   -- objects iterate_nearest reports around the victim
level = { iterate_nearest = function(pos, r, fn)
    assert(r == 2.5, "radius")
    for _, o in ipairs(near) do if fn(o) then return end end
end }
stalker_camp_builder = { settler_lookup = { [10] = { is_rival = false }, [11] = { is_rival = true } } }
local chunk = assert(loadstring(src:sub(a, b - 1)))
chunk()

local function obj(id, sec) return { id = function() return id end, section = function() return sec end, position = function() return {} end } end
local player = obj(1, "actor")
db = { actor = player }
-- the engine's piece strike: type strike, no weapon, source = the victim itself
local function strike(victim, extra)
    local h = { type = hit.strike, draftsman = victim, weapon_id = 0 }
    for k, v in pairs(extra or {}) do h[k] = v end
    return h
end
local function npc_hit(npc, h)
    local flags = { ret_value = true }
    stalker_camp_builder.npc_on_before_hit(npc, h, 0, flags)
    return flags.ret_value
end
local function actor_hit(h)
    local flags = { ret_value = true }
    stalker_camp_builder.actor_on_before_hit(h, 0, flags)
    return flags.ret_value
end
local settler = obj(10, "stalker")

near = { obj(99, "placeable_wall") }
ok(npc_hit(settler, strike(settler)) == false, "settler: piece strike (source = victim) cancelled")
ok(npc_hit(settler, { type = hit.strike }) == false, "settler: piece strike with no source cancelled")
ok(npc_hit(obj(11, "stalker"), strike(obj(11, "stalker"))) == true, "rival settler: kept")
ok(npc_hit(obj(12, "stalker"), strike(obj(12, "stalker"))) == true, "non-settler: kept")
ok(actor_hit(strike(player)) == false, "player: piece strike cancelled")
near = { obj(98, "hs_collider_wall") }
ok(actor_hit(strike(player)) == false, "player: strike beside a collider cancelled")
ok(npc_hit(settler, strike(settler)) == false, "settler: strike beside a collider cancelled")

-- what must go through
near = { obj(99, "placeable_wall") }
ok(npc_hit(settler, strike(settler, { weapon_id = 555 })) == true, "weapon hit kept")
ok(npc_hit(settler, strike(settler, { type = hit.fire_wound })) == true, "bullet kept")
ok(npc_hit(settler, strike(settler, { type = hit.explosion })) == true, "explosion kept")
ok(npc_hit(settler, strike(settler, { draftsman = obj(77, "bloodsucker_normal") })) == true, "creature melee kept")
ok(actor_hit(strike(player, { draftsman = obj(77, "bloodsucker_normal") })) == true, "player: creature melee kept")
ok(actor_hit(strike(player, { type = hit.fire_wound })) == true, "player: bullet kept")
near = { obj(50, "wpn_ak74"), obj(51, "stalker") }
ok(npc_hit(settler, strike(settler)) == true, "no piece nearby (fall in the open): kept")
near = {}
ok(actor_hit(strike(player)) == true, "player: nothing nearby kept")
near = { settler, obj(99, "placeable_wall") }
ok(npc_hit(settler, strike(settler)) == false, "the victim itself is skipped in the scan")
local flags = { ret_value = true }
stalker_camp_builder.npc_on_before_hit(settler, nil, 0, flags)
ok(flags.ret_value == true, "no hit table: kept")
ok(actor_hit(nil) == true, "player: no hit table kept")
near = { obj(99, "placeable_wall") }
npc_hit(settler, strike(settler))
local before = reads
npc_hit(settler, strike(settler)); npc_hit(settler, strike(settler))
ok(reads == before, "section read once, then cached")

print(fails == 0 and "settler piece hit tests passed" or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
