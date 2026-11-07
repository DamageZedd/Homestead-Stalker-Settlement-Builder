-- Regression: the radial menu's Freeze must hand a slab to heal_solid (solid_online) like the spawn path
-- does, so its new collider is found within SOLID_MS (100 ms) instead of waiting for the slower heal cycle.
-- Run: lua tools/tests/test_lock_refreeze.lua   (Lua 5.1, from the repo root)

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
local errors = 0               -- the lock only prints errors here (its put-back count goes through a time event)
function printf(fmt, ...) errors = errors + 1; print("printf: " .. string.format(fmt, ...)) end

local ini_reads = {}           -- key -> count
local ini_data = {}            -- section -> { key = value }
ini_sys = {}
function ini_sys:r_float_ex(sec, key)
    local s = ini_data[sec]
    return s and s[key]
end
function ini_sys:r_string_ex(sec, key)
    ini_reads[key] = (ini_reads[key] or 0) + 1
    local s = ini_data[sec]
    return s and s[key]
end

local se_vars = {}             -- id -> { name = value }
function se_load_var(id, _, name) return se_vars[id] and se_vars[id][name] end
function se_save_var(id, _, name, val)
    se_vars[id] = se_vars[id] or {}
    se_vars[id][name] = val
end

local events = 0
local pending = {}             -- time events of the colliders, run by the test
function CreateTimeEvent(ev, _, _, fn)
    events = events + 1
    if ev == "homestead_lock_collider" then pending[#pending + 1] = fn end
end

-- net_packet: one entry per byte; a float is its value and three empty bytes
function net_packet()
    local p = { data = {}, pos = 1 }
    function p:w_begin() self.data[#self.data + 1] = 0; self.data[#self.data + 1] = 0 end
    function p:w_u8(v) self.data[#self.data + 1] = v end
    function p:w_float(v)
        self.data[#self.data + 1] = v
        for _ = 1, 3 do self.data[#self.data + 1] = 0 end
    end
    function p:w_tell() return #self.data end
    function p:r_seek(n) self.pos = n + 1 end
    function p:r_u8() local v = self.data[self.pos]; self.pos = self.pos + 1; return v end
    function p:r_float() local v = self.data[self.pos]; self.pos = self.pos + 4; return v end
    return p
end

local server = {}              -- id -> fake server object
local next_se_id = 5000
local released = {}
function alife_object(id) return server[id] end
function alife_release(se) released[se.id] = true; server[se.id] = nil end
function alife_create(sec, pos, lv, gv)
    next_se_id = next_se_id + 1
    local se = { id = next_se_id, sec = sec, position = pos, lv = lv, gv = gv, health = 1 }
    function se:section_name() return self.sec end
    function se:STATE_Write(p)                 -- 8 bytes of other state, then health
        for i = 1, 8 do p:w_u8(i) end
        p:w_float(self.health)
    end
    function se:STATE_Read(p, size)
        self.read_size = size
        self.state_bytes = {}
        for i = 1, 8 do self.state_bytes[i] = p:r_u8() end
        self.health = p:r_float()
    end
    server[se.id] = se
    return se
end

function vector()
    local v = { x = 0, y = 0, z = 0 }
    function v:set(x, y, z) self.x, self.y, self.z = x, y, z; return self end
    return v
end

local objects = {}             -- id -> fake game object
local nearby = {}              -- what iterate_nearest hands out
local stats = { iterate = 0, lookups = 0 }
level = {}
function level.object_by_id(id) stats.lookups = stats.lookups + 1; return objects[id] end
function level.iterate_nearest(_, _, fn)
    stats.iterate = stats.iterate + 1
    for _, o in ipairs(nearby) do
        if fn(o) then break end
    end
end

db = { actor = { position = function() return { x = 0, y = 0, z = 0 } end } }

local callbacks = {}
function RegisterScriptCallback(name, fn) callbacks[name] = fn end
function getFS() return { exist = function() return true end } end

local wrappers = {}            -- id -> HF wrapper
bind_hf_base = {}
function bind_hf_base.get_wrapper(id) return wrappers[id] end
function bind_hf_base.freeze_obj(id)
    local o = objects[id]
    if not o then return end
    o.shell_freezes = o.shell_freezes + 1
    if wrappers[id] then wrappers[id].is_frozen = true end
    return true
end
bind_hf_static = { freeze_obj = function() return nil end }

local function make_obj(id, sec, x, y, z, h, p, b)
    local o = { _id = id, _sec = sec, pos = { x = x, y = y, z = z }, ang = { x = h or 0, y = p or 0, z = b or 0 },
        shell_freezes = 0, door = 0, set_pos = 0, set_ang = 0 }
    function o:id() return self._id end
    function o:section() return self._sec end
    function o:level_vertex_id() return 11 end
    function o:game_vertex_id() return 22 end
    function o:position() return { x = self.pos.x, y = self.pos.y, z = self.pos.z } end
    function o:angle() return { x = self.ang.x, y = self.ang.y, z = self.ang.z } end
    function o:force_set_position(v) self.pos = { x = v.x, y = v.y, z = v.z }; self.set_pos = self.set_pos + 1 end
    function o:force_set_angle(v) self.ang = { x = v.x, y = v.y, z = v.z }; self.set_ang = self.set_ang + 1 end
    local po = { set_door_ignore_dynamics = function() o.door = o.door + 1; o.in_door = true end,
        unset_door_ignore_dynamics = function() o.in_door = false end }
    function o:get_physics_object() return po end
    function o:get_physics_shell()
        return { freeze = function() o.shell_freezes = o.shell_freezes + 1 end }
    end
    objects[id] = o
    wrappers[id] = { is_frozen = false, object = o, set_frozen = function(self, f) self.is_frozen = f end }
    return o
end

MCM_ON = true
ui_mcm = { get = function() return MCM_ON end }

dofile("HomesteadHF/gamedata/scripts/homestead_lock.script")
on_game_start()
local tick = callbacks.actor_on_update

ini_data.hs_square = { homestead_snap = "foundation", script_binding = "bind_hf_base.bind",
    homestead_collider = "hs_collider_foundation", homestead_collider_y = -0.3 }

local function online_collider(cid, sec)
    objects[cid] = { get_physics_shell = function() return nil end, id = function() return cid end,
        section = function() return sec end }
end
local function step(n) for _ = 1, n do now = now + 100; tick() end end

local ID = 960
local o = make_obj(ID, "hs_square", 8, 2, 3, 0)
bind_hf_base.freeze_obj(ID)
online_collider(se_vars[ID].hs_collider, "hs_collider_foundation")
step(10)
ok(o.in_door == true, "spawn path: the slab is in door mode once its collider is online")

-- radial menu: Unfreeze, then Freeze again
local w = wrappers[ID]
w:set_frozen(false)
ok(o.in_door == false, "unfrozen: not in door mode")
step(7)                            -- a heal slice has just run
w:set_frozen(true)
ok(o.in_door == false, "refrozen: its new collider is not online yet")
local c = se_vars[ID].hs_collider
ok(c ~= nil and server[c] ~= nil, "refrozen: a new collider was made")
online_collider(c, "hs_collider_foundation")
step(2)                            -- 200 ms: heal_solid has run, the 500 ms heal has not
ok(o.in_door == true, "refrozen: door mode within 200 ms of the collider coming online")
ok(errors == 0, "no lock errors printed (" .. errors .. ")")

print(fails == 0 and ("lock refreeze tests passed (" .. checks .. " checks)") or (fails .. " FAILED"))
os.exit(fails == 0 and 0 or 1)
