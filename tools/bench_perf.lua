-- Relative before/after benchmark for the large-settlement performance pass.
-- Run from the repo root with Lua 5.1:  lua tools/bench_perf.lua
-- Each pure test file runs its normal checks, then (BENCH set) times the old code (a frozen copy in the
-- test) against the shipped code. Numbers are plain Lua 5.1 on the dev machine: use them as ratios, not
-- as in-game milliseconds (the game runs LuaJIT, which is faster in absolute terms).
BENCH = true
for _, t in ipairs({ "tools/tests/test_core_perf.lua", "tools/tests/test_furniture_perf.lua" }) do
    dofile(t)
end
print("---- benchmark ----")
for _, line in ipairs(BENCH_RESULTS or {}) do print(line) end
