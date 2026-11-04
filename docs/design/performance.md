# Performance pass (v1.4.0): large settlements

Goal: a settlement with many survivors, outposts, pieces and hubs should cost less per frame, with identical
gameplay. Nothing here changes balance, timings (the game clock and real-time helpers are untouched), saved
data, or MCM options.

The tick structure was already staggered by earlier passes (`actor_on_update` runs one slot per second,
settlers think about once a second, rivals and raids are sliced). This pass removed what was left: per-tick
allocations, repeated lookups, work done while the PDA is closed, and big single-frame jobs.

## Findings and changes

| Area | Cost scaling | Change | Measured / estimated |
|---|---|---|---|
| Settler think (`npc_on_update`) built 3 closures and literal anim tables every think | O(survivors) allocs per second | closures became file-level helpers, anim tables constant | removes ~4 closures and several tables per settler-second (estimated) |
| `setup_settler_beh_logic` re-parsed 16 constant condlists every think | O(survivors) parses per second | parsed once per NPC, cached in `db.storage[id].homestead_condlists` (not saved) | 16 parses per settler-second removed (estimated) |
| `camp_iterate_inventory` stale-entry sweep | O(boxes x items) per scan | indexed by box, O(boxes + items); pcall closures removed; per-snapshot reads hoisted | same output on 400 random camps; small random worlds time the same (25 vs 24 ms net), gain grows with box count |
| Furniture lock rotation check (`homestead_lock`) | O(pieces) per sweep, trig per piece | cheap angle-sum early-out, exact check only when needed | **6.1x faster** on settled pieces (213 ms vs 35 ms per 200k checks) |
| Furniture lock drift heal | 40 pieces in one frame every 2 s | 10 pieces every 0.5 s (same 20 pieces/s), never in the 80 m sweep's frame | worst frame 4x smaller |
| Lock: `script_binding` / `homestead_snap` ini reads | per sweep / per load | cached per section | removes ini reads from the sweep |
| PDA refresh while closed | O(survivors) per second during normal play | `actor_on_update` stops when the PDA is closed | whole roster refresh removed from normal play |
| PDA refresh while open | ~3 roster refreshes a second | one shared 1 s timer | about 3x fewer refreshes |
| PDA roster rows | widget calls per row every refresh | rows with unchanged text and color make no calls; per-row closures and label tables removed; translations, job labels, role colors cached | scales with unchanged rows (most of them) |
| Alarm binders (`bind_alarm_system*`) | per-frame scan of nearby objects | class check before position read; no closures; position read only when a sound starts | per frame, per alarm |
| Pistol turret hostile cache and frame path | per rebuild / per frame | relation class prefilter; closure-free pcalls; yaw animation names cached | per frame, per turret |
| Rivals `get_safe_switch_distance` | ini read per call | `switch_factor` read once (switch distance still live) | 52 ini reads down to 1 in the test |
| Expedition tick (every 1 s) | per-tick table and level/camp lookups | lookups only on ticks where a radio line is due | removes a table and 2 lookups per second |
| Events / raiders | survivor count by full walk; game time factor per survivor | `next()`; once per camp | small |

Benchmark: `lua tools/bench_perf.lua` (Lua 5.1, repo root). It runs the old code (frozen in the tests)
against the shipped code. Numbers are ratios from plain Lua 5.1 on the dev machine, not in-game
milliseconds.

## Still expensive (not changed, and why)

- **Job pause status**: `_calc_job_paused_status` does full inventory scans for every settler on each 10 s
  jobs tick, in one frame: O(survivors x items x checks). Probably the biggest remaining spike. A safe fix
  needs an inventory generation counter bumped on every deposit and consume path; a missed bump would show a
  stale pause reason. Alternative: spread the settler loop of `update_camp_jobs` over slots, which shifts
  cycle timing by a few seconds.
- **Settler goodwill refresh**: every 10 s each settler sets goodwill with every other settler, O(S^2) cheap
  engine calls. Caching game objects across frames risks dangling objects.
- **Idle wander and missing-station scan**: walk `camp.structures` per settler-second, O(S x P). Caching
  would delay noticing a new or removed piece (behavior change).
- **PDA list rebuilds**: `Reset` and `OnSettlementSelected` still tear down and rebuild every list; reuse
  needs a rework of the list item classes. The page also asks core for per-row job status every second, and
  `pos_in_cover` is called 15k+ times in a refresh.
- **Eating / needs rounds**: one inventory scan per settler per food interval (rare, once per game day).
- **Offline box sweeps** (old exes without `alife():get_children`): a 65k-id sweep per consume. Not reached
  with Modded Exes.
- **Hideout Furniture's own per-piece binder update** is likely the largest cost that grows with piece count
  (inference, not measured, external mod).

Per-area detail notes from the audits are in the session notes (perf-core, perf-pda, perf-furniture,
perf-rivals-events).

## How to measure in game

Nothing is added for players. With the MCM debug logging option on, `actor_on_update` already logs
`[Homestead] Slow tick slot N: X ms` for any slot over 4 ms. Compare it before and after on a large save:

1. Load a big settlement (many survivors, many pieces), enable debug logging, play 5 minutes near the hub.
2. Count `Slow tick slot` lines in the xray log and note which slot and how many ms (slot 1 = camp jobs,
   3 = rivals, 8 = eating).
3. Check the frame time (`rs_stat on`/FPS counter) while idle near the camp, with the PDA closed and open.

## Verify in game

Settlers at stations face furniture and can be talked to (also after save/load and level change); job
movement (hunter, scavenger, assigned posts, cook); storage counts after moving items between boxes; pieces
stay put after loading, a shoved wall comes back within seconds, an unfrozen piece moves freely, floors stay
solid; PDA countdowns tick, status and needs changes show, the PDA works with the 3D PDA option and its radio
colors look the same; alarms still fire and tip; turrets shoot hostiles and ignore settlers, the player and
furniture.
