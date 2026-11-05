-- Standalone tests for the furniture lock's cheap paths in homestead_lock.script: the rotation
-- pre-check must give the same answer as the full check, the sweep / heal schedule must keep the old
-- rate (20 spot checks a second) without doing both in one frame, and the per-section caches must
-- read the configs once per section without changing which pieces are locked.
-- Run: lua tools/tests/test_furniture_perf.lua   (Lua 5.1, from the repo root)

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

local server = {}              -- id -> fake server object
local next_se_id = 5000
local released = {}
function alife_object(id) return server[id] end
function alife_release(se) released[se.id] = true; server[se.id] = nil end
function alife_create(sec, pos, lv, gv)
    next_se_id = next_se_id + 1
    local se = { id = next_se_id, sec = sec, position = pos, lv = lv, gv = gv }
    function se:section_name() return self.sec end
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
    wrappers[id] = { is_frozen = false, set_frozen = function(self, f) self.is_frozen = f end }
    return o
end

dofile("HomesteadHF/gamedata/scripts/homestead_lock.script")
on_game_start()
local tick = callbacks.actor_on_update
ok(type(tick) == "function", "actor_on_update registered")
ok(type(spot_turned) == "function", "spot_turned exposed")

---------------------------------------------------------------------------
-- 1. rotation pre-check == full check (the full check is the pre-change code)
---------------------------------------------------------------------------
local TURN_TOL = 0.0005
local function ref_axes(h, p, b)
    local sh, ch, sp, cp, sb, cb = math.sin(h), math.cos(h), math.sin(p), math.cos(p), math.sin(b), math.cos(b)
    local cc, cs, sc, ss = ch * cb, ch * sb, sh * cb, sh * sb
    return cc - sp * ss, -cp * sb, sp * cs + sc, sp * sc + cs, cp * cb, ss - sp * cc, -cp * sh, sp, cp * ch
end
local function ref_turn(h1, p1, b1, h2, p2, b2)
    local u1, u2, u3, u4, u5, u6, u7, u8, u9 = ref_axes(h1, p1, b1)
    local v1, v2, v3, v4, v5, v6, v7, v8, v9 = ref_axes(h2, p2, b2)
    local trace = u1 * v1 + u2 * v2 + u3 * v3 + u4 * v4 + u5 * v5 + u6 * v6 + u7 * v7 + u8 * v8 + u9 * v9
    return math.acos(math.max(-1, math.min(1, (trace - 1) / 2)))
end

math.randomseed(12345)
local function rnd(a, b) return a + (b - a) * math.random() end
local mismatch, bound_broken, near = 0, 0, 0
for i = 1, 200000 do
    local h, p, b = rnd(-math.pi, math.pi), rnd(-1.56, 1.56), rnd(-math.pi, math.pi)
    local scale = 10 ^ rnd(-7, -2)     -- 1e-7 .. 1e-2 rad, straddling the 5e-4 tolerance
    local dh, dp, db = rnd(-1, 1) * scale, rnd(-1, 1) * scale, rnd(-1, 1) * scale
    if i % 3 == 0 then dp, db = 0, 0 end
    local spot = { 0, 0, 0, h, p, b }
    local want = ref_turn(h + dh, p + dp, b + db, h, p, b) > TURN_TOL
    if spot_turned(h + dh, p + dp, b + db, spot) ~= want then mismatch = mismatch + 1 end
    if ref_turn(h + dh, p + dp, b + db, h, p, b) > math.abs(dh) + math.abs(dp) + math.abs(db) + 1e-7 then
        bound_broken = bound_broken + 1
    end
    if math.abs(dh) + math.abs(dp) + math.abs(db) <= TURN_TOL / 2 then near = near + 1 end
end
ok(mismatch == 0, "pre-check agrees with the full check (" .. mismatch .. " mismatches)")
ok(bound_broken == 0, "turn <= |dh|+|dp|+|db| (" .. bound_broken .. " broken)")
ok(near > 10000, "the sample exercises the cheap path (" .. near .. ")")

if BENCH then
    -- steady-state check: a pieces' worth of "has it turned?" tests, pieces that sit still
    local N = 200000
    local spots, ds = {}, {}
    for i = 1, 1000 do
        local h, p, b = rnd(-math.pi, math.pi), rnd(-1.5, 1.5), rnd(-math.pi, math.pi)
        spots[i] = { 0, 0, 0, h, p, b }
        ds[i] = { h + rnd(-1, 1) * 1e-5, p, b }
    end
    local t0 = os.clock()
    for i = 1, N do
        local d, s = ds[i % 1000 + 1], spots[i % 1000 + 1]
        ref_turn(d[1], d[2], d[3], s[4], s[5], s[6])
    end
    local old_ms = (os.clock() - t0) * 1000
    t0 = os.clock()
    for i = 1, N do
        local d, s = ds[i % 1000 + 1], spots[i % 1000 + 1]
        spot_turned(d[1], d[2], d[3], s)
    end
    local new_ms = (os.clock() - t0) * 1000
    BENCH_RESULTS = BENCH_RESULTS or {}
    BENCH_RESULTS[#BENCH_RESULTS + 1] = string.format(
        "lock rotation check x%d (settled pieces): old %.0f ms, new %.0f ms (%.1fx)", N, old_ms, new_ms, old_ms / math.max(new_ms, 0.001))
    -- heal slice size per frame-job: old 40 pieces / 2 s, new 10 pieces / 0.5 s
    BENCH_RESULTS[#BENCH_RESULTS + 1] = "lock heal: old 40 pieces per 2000 ms job, new 10 per 500 ms job (same 20 pieces/s, 4x smaller worst frame)"
end


ok(spot_turned(1, 0.2, 0.3, { 0, 0, 0, 1, 0.2, 0.3 }) == false, "same angles: not turned")
ok(spot_turned(-math.pi, 0, 0, { 0, 0, 0, math.pi, 0, 0 }) == false, "heading -pi == +pi: not turned")
ok(spot_turned(1.001, 0.2, 0.3, { 0, 0, 0, 1, 0.2, 0.3 }) == true, "1 mrad heading: turned")
ok(spot_turned(1.0003, 0.2, 0.3, { 0, 0, 0, 1, 0.2, 0.3 }) == false, "0.3 mrad heading: within tolerance")

---------------------------------------------------------------------------
-- 2. a placed piece comes online: spot taken, door mode set, solid floors stay solid
---------------------------------------------------------------------------
ini_data.hs_wall = { script_binding = "bind_hf_base.init", homestead_snap = "wall" }
ini_data.hs_floor = { script_binding = "bind_hf_base.init", homestead_snap = "floor" }
ini_data.junk = { script_binding = "bind_something_else.init" }

local wall = make_obj(1, "hs_wall", 10, 0, 10, 0.5, 0, 0)
local floor_ = make_obj(2, "hs_floor", 14, 0, 10, 0, 0, 0)
bind_hf_base.freeze_obj(1)
bind_hf_base.freeze_obj(2)
ok(se_vars[1] and se_vars[1].hs_spot and se_vars[1].hs_spot[1] == 10, "spot saved at first freeze")
ok(wall.door == 1, "wall in door mode")
ok(floor_.door == 0, "floor stays solid")
make_obj(3, "hs_wall", 0, 0, 0)
bind_hf_base.freeze_obj(3)
ok(ini_reads.homestead_snap == 2, "homestead_snap read once per section (" .. tostring(ini_reads.homestead_snap) .. ")")

---------------------------------------------------------------------------
-- 3. put back: drift past tolerance is undone, drift within it is left
---------------------------------------------------------------------------
-- reload: the piece comes online again turned 0.3 mrad and 0.5 mm off (within tolerance)
wall.ang.x = 0.5003; wall.pos.x = 10.0005
bind_hf_base.freeze_obj(1)
ok(wall.set_pos == 0 and wall.set_ang == 0, "within tolerance: not touched")
-- 2 mm off and 2 mrad turned: both put back
wall.ang.x = 0.502; wall.pos.x = 10.002
bind_hf_base.freeze_obj(1)
ok(wall.set_pos == 1 and wall.set_ang == 1, "drifted: put back")
ok(wall.pos.x == 10 and wall.ang.x == 0.5, "back on its spot")
-- moved only: position put back, rotation left
wall.pos.y = 0.01
bind_hf_base.freeze_obj(1)
ok(wall.set_pos == 2 and wall.set_ang == 1, "moved only: position put back")

---------------------------------------------------------------------------
-- 4. sweep: HF pieces HF's hook missed are locked, configs read once per section
---------------------------------------------------------------------------
nearby = {}
for i = 100, 149 do nearby[#nearby + 1] = make_obj(i, "junk", 0, 0, 0) end
local missed = make_obj(200, "hs_wall", 5, 0, 5)             -- HF never reported its freeze
wrappers[200].is_frozen = nil
local unfrozen = make_obj(201, "hs_wall", 6, 0, 6)           -- the player unfroze it
wrappers[201].is_frozen = false
nearby[#nearby + 1] = missed
nearby[#nearby + 1] = unfrozen
nearby[#nearby + 1] = wall

local reads_before = ini_reads.script_binding or 0
now = 1000; tick()                                          -- first sweep
ok(missed.shell_freezes == 1 and missed.door == 1, "missed piece frozen and locked")
ok(unfrozen.shell_freezes == 0 and unfrozen.door == 0, "unfrozen piece left alone")
now = 3100; tick()                                          -- second sweep
ok(missed.shell_freezes == 1, "locked piece is not frozen again")
ok((ini_reads.script_binding or 0) - reads_before == 2, "script_binding read once per section ("
    .. tostring((ini_reads.script_binding or 0) - reads_before) .. ")")

---------------------------------------------------------------------------
-- 5. schedule: one sweep per 2 s, heal slices never on a sweep frame, 20 checks a second
---------------------------------------------------------------------------
for i = 300, 399 do
    make_obj(i, "hs_wall", i, 0, 0)
    bind_hf_base.freeze_obj(i)
end
wrappers[201].is_frozen = false
-- count heal checks: every heal check reads the piece's spot through se_load_var(.., "hs_spot")
local heal_reads, last_check, max_gap = 0, {}, 0
local real_load = se_load_var
function se_load_var(id, n, name)
    local d = objects[id] and ini_data[objects[id]._sec]
    local solid_piece = d and (d.homestead_snap == "foundation" or d.homestead_snap == "floor")   -- checked by its own 100 ms pass
    if name == "hs_spot" and not solid_piece then
        heal_reads = heal_reads + 1
        if last_check[id] then max_gap = math.max(max_gap, now - last_check[id]) end
        last_check[id] = now
    end
    return real_load(id, n, name)
end
-- one piece drifts: a heal pass must put it back
objects[350].pos.y = 0.05

local online_count = 104       -- ids 1-3, 200 and 300-399
-- the old schedule checked 40 pieces per 2 s sweep (a sweep that empties the queue stops there),
-- so a piece waited up to ceil(n / 40) sweeps; the slices must never be slower than that
local old_cycle = math.ceil(online_count / 40) * 2000
local start, both = 20000, 0
now = start; tick()   -- settle the timers
stats.iterate = 0; heal_reads = 0; last_check = {}; max_gap = 0
for t = start + 16, start + 60000, 16 do
    now = t
    local it, hr = stats.iterate, heal_reads
    tick()
    if stats.iterate > it and heal_reads > hr then both = both + 1 end
end
ok(both == 0, "no frame sweeps and heals (" .. both .. ")")
ok(stats.iterate == 30, "one sweep per 2 s (" .. stats.iterate .. " in 60 s)")
ok(heal_reads >= 1100 and heal_reads <= 1200, "about 20 heal checks a second (" .. heal_reads .. " in 60 s)")
ok(max_gap > 0 and max_gap <= old_cycle, "every piece re-checked at least as often as before (" .. max_gap
    .. " ms, old " .. old_cycle .. " ms)")
local checked = 0
for _ in pairs(last_check) do checked = checked + 1 end
local solid_count = 0       -- solid pieces have their own 100 ms pass, not counted here
for id = 1, 399 do
    local d = objects[id] and ini_data[objects[id]._sec]
    if d and (d.homestead_snap == "foundation" or d.homestead_snap == "floor") and last_check[id] == nil and wrappers[id].is_frozen then
        solid_count = solid_count + 1
    end
end
ok(checked + solid_count == online_count, "every locked piece checked (" .. checked .. " + " .. solid_count .. " solid)")
ok(objects[350].pos.y == 0 and objects[350].set_pos == 1, "drifted piece put back by the heal pass")

-- after a pause (a load, a long frame) both are overdue: that frame only sweeps, the next one heals
do
    local it, hr = stats.iterate, heal_reads
    now = now + 10000; tick()
    ok(stats.iterate == it + 1 and heal_reads == hr, "both overdue: this frame only sweeps")
    now = now + 16; tick()
    ok(stats.iterate == it + 1 and heal_reads > hr, "both overdue: the next frame heals")
end
start = now - 60000

-- a piece the player unfroze after it was locked is not healed
wrappers[300].is_frozen = false
objects[300].pos.y = 1
for t = start + 60016, start + 120000, 16 do now = t; tick() end
ok(objects[300].pos.y == 1, "unfrozen piece not put back")
-- an offline piece drops out of the heal set
objects[301] = nil
last_check[301] = nil
for t = start + 120016, start + 180000, 16 do now = t; tick() end
ok(last_check[301] == nil, "offline piece no longer checked")
ok(errors == 0, "no lock errors printed (" .. errors .. ")")

-- a death speeds the heal up for a while: a drifted piece is back on its spot within a second, then
-- the normal rate returns
ok(type(callbacks.npc_on_death_callback) == "function" and type(callbacks.monster_on_death_callback) == "function",
    "death callbacks registered")
do
    local t0 = now + 30000
    for t = now + 16, t0, 16 do now = t; tick() end      -- settle
    objects[350].pos.y = 0.2
    callbacks.npc_on_death_callback({}, {})
    local back
    for t = t0 + 16, t0 + 2000, 16 do
        now = t; tick()
        if objects[350].pos.y == 0 then back = t - t0; break end
    end
    ok(back and back <= 1000, "piece put back within 1 s of a death (" .. tostring(back) .. " ms)")
    for t = now + 16, t0 + 30000, 16 do now = t; tick() end
    local reads = heal_reads
    for t = now + 16, now + 10000, 16 do now = t; tick() end
    ok(heal_reads - reads <= 220, "normal heal rate after the burst (" .. (heal_reads - reads) .. " in 10 s)")
end
-- a solid piece (foundation / floor) shoved off its spot is put back within 150 ms and stopped
do
    ini_data.hs_slab = { homestead_snap = "foundation", script_binding = "bind_hf_base.bind" }
    local o = make_obj(900, "hs_slab", 5, 0, 5, 0.3)
    bind_hf_base.freeze_obj(900)
    ok(o.door == 0, "solid piece stays out of door mode")
    now = now + 1000; tick()
    local frozen_before = o.shell_freezes
    o.pos.y = 0.04                       -- shoved up
    local back
    local t1 = now
    for t = t1 + 16, t1 + 400, 16 do
        now = t; tick()
        if o.pos.y == 0 then back = t - t1; break end
    end
    ok(back and back <= 150, "solid piece put back within 150 ms (" .. tostring(back) .. " ms)")
    ok(o.shell_freezes > frozen_before, "put-back re-freezes the piece, which zeroes its speed")

    -- a slab that keeps being pushed back (it overlaps a neighbour) stops being fought at 10 Hz
    local puts = o.set_pos
    for t = now + 16, now + 1600, 16 do
        now = t
        o.pos.y = 0.04
        tick()
    end
    -- 16 frames of 100 would be put back at 10 Hz; at most 5 count before it leaves (the shove above counts too)
    ok(o.set_pos - puts <= 5, "fighting piece leaves the fast pass after 5 put-backs (" .. (o.set_pos - puts) .. ")")
    errors = errors - 1       -- that report is expected
end

-- square foundations: door mode on top of a static collider
do
    ini_data.hs_square = { homestead_snap = "foundation", script_binding = "bind_hf_base.bind",
        homestead_collider = "hs_collider_foundation", homestead_collider_y = -0.3 }
    local o = make_obj(910, "hs_square", 7, 2, 9, 1.2)
    bind_hf_base.freeze_obj(910)
    local cid = se_vars[910] and se_vars[910].hs_collider
    local se = cid and server[cid]
    ok(se and se.sec == "hs_collider_foundation", "collider spawned with the piece")
    ok(o.in_door == true, "square foundation goes in door mode once it has a collider")
    ok(se and math.abs(se.position.y - 1.7) < 1e-6 and se.position.x == 7 and se.position.z == 9,
        "collider sits at the box centre under the piece")
    ok(se and se.angle.y == 1.2 and se.angle.x == 0, "spawn angle is x = pitch, y = heading")
    ok(se_vars[cid] and se_vars[cid].hs_collider_of == 910, "collider knows its piece")

    -- already has one: the heal pass keeps it
    for t = now + 16, now + 15000, 16 do now = t; tick() end
    ok(se_vars[910].hs_collider == cid and server[cid] ~= nil, "working collider kept by the heal pass")

    -- broken by an explosion: replaced
    objects[cid] = { get_physics_shell = function() return {} end, id = function() return cid end,
        section = function() return "hs_collider_foundation" end }
    for t = now + 16, now + 15000, 16 do now = t; tick() end
    local new_cid = se_vars[910].hs_collider
    ok(released[cid] and new_cid ~= cid and server[new_cid] ~= nil, "broken collider replaced")
    objects[cid] = nil

    -- picked up: the collider goes too, after the engine has finished with the piece
    callbacks.server_object_on_unregister({ id = 910 })
    ok(server[new_cid] ~= nil, "collider not released during unregister")
    for _, fn in ipairs(pending) do fn() end
    pending = {}
    ok(released[new_cid] and se_vars[910].hs_collider == nil, "collider released with its piece")
    objects[910] = nil

    -- a collider whose piece is gone is cleaned up by the sweep
    local stray = alife_create("hs_collider_floor", { x = 0, y = 0, z = 0 }, 1, 1)
    se_vars[stray.id] = { hs_collider_of = 910 }
    nearby[#nearby + 1] = { id = function() return stray.id end, section = function() return "hs_collider_floor" end }
    now = now + 3000; tick()
    ok(released[stray.id], "orphan collider released by the sweep")
    nearby[#nearby] = nil

    -- a piece with no collider section stays solid
    ini_data.hs_tri = { homestead_snap = "foundation_tri", script_binding = "bind_hf_base.bind" }
    local tri = make_obj(911, "hs_tri", 1, 0, 1)
    bind_hf_base.freeze_obj(911)
    ok(tri.door == 0 and not (se_vars[911] and se_vars[911].hs_collider), "triangle stays solid, no collider")
end

ok(errors == 0, "no lock errors after the death burst (" .. errors .. ")")

print(fails == 0 and ("all furniture perf tests passed (" .. checks .. " checks)") or (fails .. " FAILED"))
if not BENCH or fails > 0 then os.exit(fails == 0 and 0 or 1) end
