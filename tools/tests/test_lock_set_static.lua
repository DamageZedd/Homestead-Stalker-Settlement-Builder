-- Regression: homestead_lock's set_static
--  * with colliders off, a slab whose physics shell is missing must not call unset_door_ignore_dynamics
--    (the engine asserts on a missing shell; the main path already checks for it).
-- Run: lua tools/tests/test_lock_set_static.lua   (Lua 5.1, from the repo root)

local fails, checks = 0, 0
local function ok(cond, msg)
    checks = checks + 1
    if not cond then fails = fails + 1; print("FAIL " .. msg) end
end

---------------------------------------------------------------------------
-- engine stubs
---------------------------------------------------------------------------
local now = 0
function time_global() return now end
local errors = 0
function printf(fmt, ...) errors = errors + 1; print("printf: " .. string.format(fmt, ...)) end

local ini_data = {}
ini_sys = {}
function ini_sys:r_float_ex(sec, key) local s = ini_data[sec]; return s and s[key] end
function ini_sys:r_string_ex(sec, key) local s = ini_data[sec]; return s and s[key] end

local se_vars = {}
function se_load_var(id, _, name) return se_vars[id] and se_vars[id][name] end
function se_save_var(id, _, name, val)
    se_vars[id] = se_vars[id] or {}
    se_vars[id][name] = val
end

function CreateTimeEvent() end
function net_packet() return {} end

local server = {}
function alife_object(id) return server[id] end
function alife_release(se) server[se.id] = nil end
function alife_create() return nil end

function vector()
    local v = { x = 0, y = 0, z = 0 }
    function v:set(x, y, z) self.x, self.y, self.z = x, y, z; return self end
    return v
end

local objects = {}
level = {}
function level.object_by_id(id) return objects[id] end
function level.iterate_nearest() end

db = { actor = { position = function() return { x = 0, y = 0, z = 0 } end } }

local callbacks = {}
function RegisterScriptCallback(name, fn) callbacks[name] = fn end
function getFS() return { exist = function() return true end } end

local wrappers = {}
bind_hf_base = {}
function bind_hf_base.get_wrapper(id) return wrappers[id] end
function bind_hf_base.freeze_obj(id)
    if not objects[id] then return end
    wrappers[id].is_frozen = true
    return true
end
bind_hf_static = { freeze_obj = function() return nil end }

local function make_obj(id, sec)
    local o = { _id = id, _sec = sec, pos = { x = 1, y = 2, z = 3 }, ang = { x = 0, y = 0, z = 0 },
        door_set = 0, unset_calls = 0, has_shell = true }
    function o:id() return self._id end
    function o:section() return self._sec end
    function o:level_vertex_id() return 11 end
    function o:game_vertex_id() return 22 end
    function o:position() return { x = self.pos.x, y = self.pos.y, z = self.pos.z } end
    function o:angle() return { x = self.ang.x, y = self.ang.y, z = self.ang.z } end
    function o:force_set_position() end
    function o:force_set_angle() end
    local po = {
        set_door_ignore_dynamics = function() o.door_set = o.door_set + 1; o.in_door = true end,
        unset_door_ignore_dynamics = function()
            o.unset_calls = o.unset_calls + 1
            assert(o.has_shell, "no physics shell")      -- what the engine does
            o.in_door = false
        end }
    function o:get_physics_object() return po end
    function o:get_physics_shell()
        if not o.has_shell then return nil end
        return { freeze = function() end }
    end
    objects[id] = o
    wrappers[id] = { is_frozen = false, set_frozen = function(self, f) self.is_frozen = f end }
    return o
end

MCM_ON = false                 -- colliders off
ui_mcm = { get = function() return MCM_ON end }

dofile("HomesteadHF/gamedata/scripts/homestead_lock.script")
on_game_start()

ini_data.hs_square = { homestead_snap = "foundation", script_binding = "bind_hf_base.bind",
    homestead_collider = "hs_collider_foundation", homestead_collider_y = -0.3 }

---------------------------------------------------------------------------
-- colliders off, slab with a shell: leaves door mode as before
---------------------------------------------------------------------------
local a = make_obj(100, "hs_square")
bind_hf_base.freeze_obj(100)
ok(a.unset_calls == 1 and a.in_door == false, "colliders off: a slab with a shell leaves door mode")
ok(errors == 0, "no lock errors with a shell (" .. errors .. ")")

---------------------------------------------------------------------------
-- colliders off, shell not ready: no engine call, no error
---------------------------------------------------------------------------
local b = make_obj(101, "hs_square")
b.has_shell = false
bind_hf_base.freeze_obj(101)
ok(b.unset_calls == 0, "colliders off: no unset_door_ignore_dynamics without a shell")
ok(errors == 0, "no lock errors without a shell (" .. errors .. ")")

print(fails == 0 and ("lock set_static tests passed (" .. checks .. " checks)") or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
