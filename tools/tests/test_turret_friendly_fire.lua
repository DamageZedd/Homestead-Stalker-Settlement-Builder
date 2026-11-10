-- A turret never shoots the player's own settlers, refugees or companions, even when their relation to
-- the player reads "enemy" (raid reputation losses, a player faction change); rival camp members and
-- plain hostiles stay targets. is_enemy_to_actor .. is_valid_target are cut out of the script by their
-- markers and run against stubs.
-- Run: lua tools/tests/test_turret_friendly_fire.lua   (Lua 5.1, from the repo root)

local fails = 0
local function ok(c, m) if not c then fails = fails + 1; print("FAIL " .. m) end end

local f = assert(io.open("00_Core/gamedata/scripts/bind_pistol_turret.script", "rb"))
local src = f:read("*a"):gsub("\r\n", "\n"); f:close()
local a = src:find("local function is_enemy_to_actor", 1, true)
local b = src:find("local function rebuild_hostile_cache", a, true)
assert(a and b, "markers not found")

clsid = { actor = 1, script_stalker = 2 }
game_object = { enemy = 2, friend = 0 }
local function can_check_relation() return true end
local function relation_class() return true end
IsMonster = function() return false end
local player = { id = function() return 1 end }
db = { actor = player }
local companions = {}
stalker_camp_builder = {
    settler_lookup = { [10] = { survivor = {} }, [11] = { is_rival = true }, [12] = { is_refugee = true } },
    is_companion = function(npc) return companions[npc:id()] == true end,
}

local chunk = assert(loadstring("local can_check_relation, relation_class = ...\n" .. src:sub(a, b - 1) .. "\nreturn is_valid_target"))
local is_valid_target = chunk(can_check_relation, relation_class)

local function npc(id, rel, alive)
    return {
        id = function() return id end, clsid = function() return clsid.script_stalker end,
        alive = function() return alive ~= false end, wounded = function() return false end,
        relation = function() return rel end,
    }
end

ok(is_valid_target(npc(50, game_object.enemy)) == true, "plain hostile stalker: target")
ok(is_valid_target(npc(50, game_object.friend)) == false, "friendly stalker: not a target")
ok(is_valid_target(npc(10, game_object.enemy)) == false, "settler with enemy relation: not a target")
ok(is_valid_target(npc(12, game_object.enemy)) == false, "refugee with enemy relation: not a target")
ok(is_valid_target(npc(11, game_object.enemy)) == true, "rival camp member: still a target")
companions[60] = true
ok(is_valid_target(npc(60, game_object.enemy)) == false, "companion with enemy relation: not a target")
stalker_camp_builder.is_companion = function() error("boom") end
ok(is_valid_target(npc(50, game_object.enemy)) == true, "failing companion check does not drop real hostiles")
stalker_camp_builder = nil
ok(is_valid_target(npc(50, game_object.enemy)) == true, "no camp builder: relation only")

if fails > 0 then os.exit(1) end
print("turret friendly fire: ok")
