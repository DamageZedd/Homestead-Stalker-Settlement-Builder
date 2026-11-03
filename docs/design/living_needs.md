# Living Needs and Shortage Consequences: design (not implemented)

Status: DRAFT for user approval. No feature code exists. Internal doc, not README content.
Line numbers are from `main` at ff04d24 (v1.3.5) and will drift; `docs/CODEMAP.md` is stale (it puts `get_camp_stats` at 4887, it is at 5075), so these cites come from the live files.
Paths: `00_Core/gamedata/scripts/`, abbreviated `sb.script` (stalker_camp_builder), `jobs`, `inv`, `events`, `prosper`, `pda`, `mcm`.

Goal (from the roadmap suggestion, treated as ideas): settlers need and consume resources over time; shortages have consequences beyond "job pauses"; a lean camp and a fat camp play differently.

## 1. What exists today

The foundation is bigger than the roadmap assumes. The design extends it; it does not start from nothing.

| Area | Today | Where |
|---|---|---|
| Food | Every `food_consumption_interval` (86400 game s, MCM `food_consumption_interval_hr` 1-72h) each settler eats exactly 1 item from camp storage. Missing food sets `camp.hungry_until` / `hungry_count` and shows a hard-coded English toast. | `jobs` `process_settler_eating` 3162; interval at `sb.script` 694, MCM map 1025, `mcm` 95; ticked from `process_all_settler_eating` (`sb.script` ~2328), `actor_on_update` slot 8 (~2380) |
| What counts as food | `FOOD_SECTIONS` includes vodka, beer, water_drink, mineral_water, tea, flask, energy_drink, and any `meat_*` (raw meat too, which cooks need as input). | `jobs` 3139-3160 |
| Morale | `camp.happiness` (0-100) is scored in `get_camp_stats` from beds vs population, defense vs 3/settler, pumps, food/water in chests (+-5 each), pianos, radios, decor, and hunger (-5 per hungry settler, cap -30). The PDA and desertion read this value. | `sb.script` 5075-5240 (hunger 5222-5228), PDA 1429-1434 |
| A second "morale" | `get_camp_morale` computes `camp.morale` from a different formula (pump, guard, radio, drugkit, toolkits). It is not what the PDA or desertion use. | `sb.script` 6650 |
| Desertion | Below `happiness < 20`, with 2+ settlers: each settler rolls 3%, at most one leaves per check, then a 7200 game-s cooldown. Runs from `process_camp_morale` (~every 10 real s, slot 6, `sb.script` 2375). Leaving uses the banish-style purge and a red toast (`st_survivor_abandoned`). | `sb.script` 5242-5300 |
| "Moved on" | A separate, positive exit: tier-3 settler with savings >= 5000 and a bought weapon may leave as a veteran, +goodwill. MCM default OFF. | `prosper` 294-322; MCM `settler_move_on_*` |
| Prosperity / savings | Settlers earn a "cut" per work cycle (`settler_cut_per_cycle` 2 x tier mult, cap `settler_savings_cap` 20000), spend it on a better weapon once per promotion, queue rank/reputation. Guards earn nothing. | `prosper` 94-125, 150-215 |
| Production inputs | Cook uses raw meat + fuel/water, brewer uses potatoes/water/wood, electrician uses fuel/batteries, woodcutter, farmer (grain), scrapper, ammo craft uses powder+scrap. All via `find_and_consume_item`; a cycle with no input is paused. Water pumps and fridges are on timers (`water_interval` 6h, `fridge_interval` 12h). | `jobs` 1189 (consume), 1784+ cook, 2212+ electrician, 2424+ woodcutter, 2602+ brewer, 2732+ farmer, 3721/3784 water/fridge |
| Job pause | `_calc_job_paused_status` decides if a job is waiting for inputs or storage room; `shortfall_reason` is shown on the PDA survivors tab. | `jobs` 1246-1297; PDA 1708-1710 |
| Storage | Buckets: fridge, stove, crafter, tech, medic, weapon, armor, chest, other, pantry, station. Personal boxes are excluded by `is_settlement_storage`. Inventory snapshot is cached. | `storage` 185-366, 349-361; `sb.script` 514; `inv` 434 `get_camp_inventory_snapshot` |
| Item draw | `camp_consume_item` -> `camp_find_item` over camp boxes; invalidates the snapshot. | `inv` 743-790 |
| Guards | Guard = defense x5 in `stats.defense`; defense deficit feeds `raid_chance`. Guard ammo is not consumed. Turrets are fed ammo by a separate job. | `sb.script` 5180; `events` 400-460 (`raid_base_chance` 15, `raid_deficit_mult` 3, `raid_cooldown` 129600); `jobs` 3199-3274 turrets |
| Medic | The medic job produces medical supplies from a medstation. Settlers never consume medicine. | `jobs` 1984-2003 |
| Offline time | Jobs are real-time driven (`job_start_realtime`); on load `rebase_one_survivor_job` caps credit at one interval. Eating uses game time and resets after ONE round, so a long sleep costs one meal. | `sb.script` ~4500 rebase; `jobs` 3162-3172 |
| Save | `save_state` / `load_state` pack `active_camps` wholesale (per-field pcall), `SAVE_STATE_VERSION = 2`; `normalize_camps` fills defaults on load. New camp/survivor fields need no migration if code treats nil as "not started". | `sb.script` 272, 3755, 3802, 3987 |

Key fact: food, hunger toast, morale penalty and desertion all exist. What is missing is variety, water as a separate need, medicine, ammo, fuel upkeep, graded tiers, job refusal, and a view of it all in the PDA.

## 2. Design principles

1. Extend `camp.happiness` only. Do not touch `camp.morale` (the other formula); it would create a third meaning.
2. One capped "needs penalty" on happiness. Every shortage tier is budgeted against the desertion line (20), so turning the feature on cannot, by itself, empty a camp.
3. Change numbers, not AI. Guard effectiveness is a multiplier on the guard's defense contribution. NPC combat behavior is not changed (cannot be verified from here).
4. Draw only from settlement storage (the existing `is_settlement_storage` rule); never personal boxes.
5. Use the cached inventory snapshot for stock levels; no per-tick box scans.
6. Master toggle defaults OFF. Existing behavior (1 food/day, -5 per hungry, desertion) stays byte-for-byte when the toggle is off.
7. Shortage math is a pure function, testable with the Lua 5.1 on this machine.

## 3. Proposed needs model

Rates are per settler per in-game day (86400 game s). "Ration" below means one item.

| Need | Rate / settler / day | Drawn from | Notes |
|---|---|---|---|
| Food | 1.0 (today's rate) | pantry/fridge/stove/chest buckets | Split into 3 classes for variety: staple (bread, conserva, tushonka, cooked meat), protein/fresh (cooked meat, sausage, kolbasa), comfort (chocolate, vodka, tea). Variety = number of classes eaten in the last 3 days, 0-3. |
| Water | 1.0 | any bucket (clean water, mineral, flask, tea) | A camp with a working pump counts as water-supplied: pump output `flask` is the supply, so pumps become the lean camp's answer. |
| Medical | 0.1 on a normal day; +1 per wounded settler after a raid/death event | medic bucket | Bandage / medkit / antibiotic classes. Medic job lowers use (x0.5). |
| Ammo | 0 at rest; per raid, 1 box per active guard | weapon/crafter buckets | Only consumed when a raid happens (not a daily drip). |
| Fuel | 0.25 per bed-occupied night in winter-style "cold" (optional, phase 4) | stove/crafter, wood/charcoal | Deferred; see open questions. |

Consumption timing: one "needs round" per `needs_interval` (default 24h, reusing the existing food interval value). A round runs once per due interval.

### Offline / sleep catch-up (the core rule)

Current behavior is a de facto cap: eating resets `last_food_consumption_time = now` after one round, so a 3-day sleep costs one meal. Production catch-up is also capped at one interval, because sleep advances game time with almost no real time. Any naive "consume N days of food" would wipe a camp the player did not even play.

Rule: `rounds_due = min(floor(elapsed / interval), catchup_cap)`, with `catchup_cap` default **1** (= today's behavior), configurable 1-3. Shortage tiers are evaluated on the round that actually ran; nothing accumulates "hunger debt" for unplayed time. When the toggle is first enabled or the mod loads an old save, timers start at "now" and a grace period (default 3 game days) suppresses penalties.

Camps on other levels: stock is read through `camp_iterate_inventory`, which has an offline (server object) path as well as the online one (`inv` ~170-195). Phase 0 must confirm `camp_consume_item` works on offline boxes; if it does not, off-level camps simply do not run needs rounds (documented limitation, same as production today).

## 4. Shortage tiers and consequences

Evaluated per round per camp. `cover` = stocked days of need / required days, per need. A camp state is the worst tier across food, water, medical.

| Tier | Trigger | Happiness penalty (total capped -35) | Other consequence |
|---|---|---|---|
| 0 Fed | all covered, variety >= 2 | +0 (variety 3: +5) | none |
| 1 Thin | covered but variety 0-1 or a stock below 2 days | -5 | PDA warning only |
| 2 Short | a need unmet for 1 round (some settlers unserved) | -5 per unserved settler (cap -20), the existing hunger rule generalised | Unserved settlers pause demanding jobs ("too hungry to work": goes through `_calc_job_paused_status`, reason string reuses the PDA path). Idle/guard unaffected. |
| 3 Starving | a need unmet for 2+ consecutive rounds | -25 flat plus unserved penalty, total cap -35 | Guard defense contribution x0.6; production cycles x0.5 rate; desertion allowed (existing roll, see below) |
| Medical gap | wounded/raid casualties and no medicine | -10 | Medic job paused if no input; "wounded" settlers (raid survivors) work at x0.5 until treated |
| Ammo gap | raid starts and guards have no ammo in storage | no happiness change | Each unarmed guard counts x0.5 in that raid's defense for `raid_chance` and outcome |

Desertion: reuse the existing 3% / one-per-check / 7200 s cooldown block unchanged. New rule only adds an MCM toggle to disable needs-driven desertion and a pre-warning: when `happiness < 30` with needs penalty active, a toast "settlers are close to leaving" once per 2 game days. A needs penalty alone never pushes a well-built camp (beds, defense, pump, radio = ~100) below 20: base 100 - 35 = 65 still above the line. Camps already at 40-50 (no beds or defense) can reach desertion, which is intended.

Budget check (worst case, 6 settlers, no variety, starving): score 50 + 20 (beds) + 20 (defense) + 10 (pumps) + 10 (stocks) = 110 -> 100; needs penalty -35 = 65. A bare camp (beds short, defense short, no pump): 50-20-20-10-10 = -10 -> 0 already today; the new penalty changes nothing there. Mid camps (score ~50) drop to ~15: this is the band where shortage becomes real, by design.

## 5. Lean vs prosperous camp

Same systems, different outcomes:

- Lean (few settlers, a pump, a farmer + cook, staples only): needs met with variety 1-2, no bonus, no penalty. Cheap, stable, low savings (savings come from work cycles regardless).
- Prosperous (many settlers, medic, trader, comfort goods stocked): variety 3 gives +5 happiness and raises the settler's cut per cycle by +25% (applied in `prosper_on_work`), which speeds up savings toward weapon purchases and moving on. It also costs more stock per day, so it needs a farmer, hunter, cook, brewer and a trader to keep the pantry full.
- Interaction with trader income: no new currency. A trader's takings stay as is. Optional (phase 4): comfort goods (vodka, chocolate) can be sold by the trader at a higher price, so a surplus is spendable.
- Interaction with savings: a Starving camp pays no cut (`prosper_credit` returns 0 at tier 3), so shortage also slows progression and moving on.

## 6. PDA additions

- Overview tab: one line under "Settlement Morale" in `pda` ~1434: "Needs: Food 3.2d / Water 4.0d / Meds 1.5d, Variety 2/3" with color by tier.
- New "Stores" panel (phase 3) as a sub-view on the overview tab (not a new top tab, to avoid the left-container layout work): stocked days per need, daily draw, and which settlers are unserved.
- Survivors tab: the existing "Waiting: <reason>" line (`pda` 1708) gets the new reason strings; no layout change.
- Toasts: replace the hard-coded English hunger toast (`jobs` ~3188) with `translate_string` entries (ASCII only; see the text rule). Radio feed gets one line per tier change.

## 7. MCM options (all under a new "Needs" group in `mcm`)

| Key | Type | Default | Purpose |
|---|---|---|---|
| `needs_enabled` | check | **false** | Master toggle. Off = today's behavior exactly. |
| `needs_consumption_mult` | track 0.25-2.0 | 1.0 | Scales all rates |
| `needs_grace_days` | track 0-10 | 3 | No penalties after enabling / loading an old save |
| `needs_catchup_cap` | track 1-3 | 1 | Max rounds per due interval |
| `needs_desertion` | check | true (only effective when master on) | Allow needs-driven desertion |
| `needs_job_refusal` | check | true | Hungry settlers pause demanding jobs |
| `needs_guard_penalty` | check | true | Guard defense x0.6 when starving |
| `needs_variety_bonus` | check | true | +5 happiness / +25% cut at variety 3 |

Each needs: defaults table (~`sb.script` 690), key -> path map (~870), `mcm` group, and localization strings (3 places plus XML; the English text XML stays ASCII).

## 8. Save compatibility

- New fields live on the camp record only (`camp.needs = { last_round_sec, hunger_rounds, water_rounds, med_rounds, variety = {...}, grace_until }`); old saves have none. `normalize_camps` (3987) creates it with `last_round_sec = now` and `grace_until = now + grace`.
- No `SAVE_STATE_VERSION` bump needed; a bump to 3 only if a migration step is added (not planned).
- Turning the toggle off must also clear the tier penalty immediately (compute from the toggle, not from stored state).
- Uninstalling the mod leaves unknown camp fields; they are plain numbers/strings, no engine objects.

## 9. Performance budget

- One needs round per camp per `needs_interval` game time, run from the existing slot 8 (`process_all_settler_eating`), so no new timer slot.
- Stock levels from `get_camp_inventory_snapshot` (cached, 10 s TTL); at most one extra snapshot read per round. No per-tick scans.
- Per-round work: O(settlers + classes). With 4 camps x 12 settlers this is a few hundred table ops per game day.
- PDA reads precomputed `camp.needs` values; computed only when a round runs.

## 10. Risks and failure modes

| Risk | Mitigation |
|---|---|
| Existing saves lose settlers after enabling | Toggle OFF by default, grace period, timers start at now, penalty cap -35 |
| Long sleep wipes stock | Catch-up cap = 1 round (current behavior) |
| Food and water both count the same items today (vodka, water in `FOOD_SECTIONS`) | Open question 2; keep the current pool for the "food" need when the new split is off |
| Raw meat eaten before the cook can use it | Open question 3; default: needs rounds prefer cooked/non-raw items, falling back to raw |
| Off-level camps cannot consume | Phase 0 verifies; otherwise documented limitation |
| Two morale values confuse the PDA | Extend `camp.happiness` only |
| Job refusal deadlocks a camp (nobody works -> no food -> nobody works) | Farmer, hunter, cook, and scavenger jobs are exempt from "too hungry"; they are the way out |
| Guard multiplier causes a raid spiral | Raid chance already rises with deficit; capped by `raid_base_chance` + deficit; add a floor of x0.6 |
| Lua 200-local / 60-upvalue limits in `sb.script` (7026 lines) | Put the new logic in a new file `stalker_camp_builder_needs.script`; `tools/check_lua.ps1` guards the limits |

## 11. Phased implementation plan

Each phase is small, shippable behind the master toggle, and verifiable without running the game. Tooling: Lua 5.1 is installed (`C:\Program Files (x86)\Lua\5.1\lua.exe`, `luac.exe`); `tools/check_lua.ps1` does the syntax and locals/upvalue check; pure functions get a standalone Lua test in `tools/tests/`.

0. **Audit (no behavior change).** Confirm `camp_consume_item` on offline boxes, list which item sections fall in each class (food/water/medical/ammo) from the game LTX, record in this doc. Verify: read-only; findings appended to this file.
1. **Pure needs engine.** New `stalker_camp_builder_needs.script` with `needs_round(stock, settlers, elapsed, cfg) -> consumed, deficits, tier, happiness_delta` and class tables; not yet wired. Verify: `check_lua.ps1` + standalone tests (sleep catch-up, grace, caps, variety, tier boundaries, 35-point cap).
2. **Wire food + water + tiers behind the toggle.** Replace the body of `process_settler_eating` when `needs_enabled`; feed `camp.needs` penalty into `get_camp_stats` (replaces the hunger block, `sb.script` 5222-5228); add MCM entries + strings. Toggle off = untouched path. Verify: diff shows the old path unchanged when off; unit tests; luac; grep of every new `cfg.*` key against the three registration sites.
3. **PDA surfacing.** Overview needs line, Stores sub-panel, reason strings, toasts via `translate_string`. Verify: XML well-formed, ASCII check, every new string id exists, `check_lua.ps1`.
4. **Consequences.** Job refusal via `_calc_job_paused_status` (with exemptions), guard multiplier in `stats.defense`, savings slowdown at tier 3, desertion pre-warning and toggle. Verify: unit tests for the multiplier and exemptions; static read-through of the single call sites.
5. **Medical and ammo.** Medicine draw after raids/death events (`events` `check_completed_raids` 546), ammo draw at `spawn_camp_raid` 210; wounded work penalty. Verify: unit tests; call-site review.
6. **Optional:** fuel/cold, comfort goods price at the trader.

Nothing can be play-tested here; every phase ends with a short in-game checklist for the user.

## 12. Open questions for the user

1. Scope: ship phases 1-4 (food/water, tiers, PDA, consequences) first, or include medical/ammo?
2. Should water be a separate need from food? (Today vodka/beer/water all count as "food"; splitting changes shipped behavior.)
3. Should settlers stop eating raw meat that cooks need as input (needs rounds prefer cooked, fall back to raw)?
4. Is -35 total happiness penalty and the "Starving" tier consequences (guards x0.6, production x0.5, desertion allowed) the right severity, or gentler?
5. Default: master toggle OFF forever, or ON for new games and OFF for loaded saves?
6. Catch-up cap default of 1 (today's behavior): confirm. Should sleeping count as "rest" and skip rounds entirely?
7. Do you want job refusal at all, or only morale/desertion consequences?
8. Fuel/cold: in or out?
9. New file `stalker_camp_builder_needs.script` (recommended) vs extending `jobs`/`sb.script`?
10. This feature adds an English-only text surface; add translations at the same time, or later?

## 13. Implementation status (phases 0-2 done, not play-tested)

- Phase 0 audit: `camp_consume_item` works on offline boxes (server-object path with `pending_item_cond`, `inv` ~170-260), so off-level camps do run needs rounds. Item classes are fixed tables in `stalker_camp_builder_needs.script`; the vanilla LTX was not consulted.
- Phase 1: pure rules (`needs_class_of`, `needs_rounds_due`, `needs_tier`, `needs_penalty`, `needs_round`) in `stalker_camp_builder_needs.script`; tests in `tools/tests/test_needs.lua` (run with Lua 5.1 from the repo root).
- Phase 2: `process_settler_eating` hands over to `needs_process` when `needs_enabled` is on; `get_camp_stats` adds `needs_happiness_delta` (and the old hunger penalty is cleared while needs are on); MCM options `needs_enabled`, `needs_consumption_mult`, `needs_grace_days`, `needs_catchup_cap`, `needs_variety_bonus`; eng/rus strings (English text in both).
- Decisions taken for the open questions (change them if you disagree): water is its own need and a camp with a water pump counts as supplied; vodka/beer/treats are "comfort" food, raw meat is eaten last; cap -35; catch-up cap 1.
- Differences from the sketch above: the "Thin" tier was dropped (a lean camp eating one class would be penalised every day, against section 5); the penalty only comes from unserved settlers, plus the variety bonus. Job refusal, guard multiplier, desertion toggle, savings slowdown and the PDA panel are still phases 3-4.
- Known gap: if the toggle is switched off for a long time and on again, the stored clock is stale; the catch-up cap limits the cost to `needs_catchup_cap` rounds, and the grace period is not renewed.

## 14. Implementation status (phases 3-4 done, not play-tested)

- PDA: while Living Needs is on, the overview "Provisions" line shows `Needs: <tier>, Variety n/3` before the storage figure (`ui_stalker_camp_builder_pda.script`, `needs_summary_text`). No new widgets, so the layout is unchanged. The separate Stores sub-panel (stocked days, daily draw) is not built.
- Job refusal: `needs_job_refused` is checked in `_calc_job_paused_status`, so the existing pause path and the PDA reason ("Too Hungry") apply. Only the settlers who went without are marked (first N by id, N = unserved), farmers, hunters, cooks and scavengers are exempt, guards and idle settlers are not marked, and the mark lapses after one round.
- Guards: `get_camp_stats` multiplies the guard term of `stats.defense` by 0.6 while the camp is Starving (tier 3), so the raid chance rises. No NPC combat change.
- Savings: `prosper_credit` pays nothing to settlers of a Starving camp.
- Desertion: new MCM `needs_desertion`; when off, a shortage-driven penalty blocks the below-20 desertion roll. A warning toast (once per 2 game days) appears when happiness is under 30 with an active penalty.
- New MCM options: `needs_job_refusal`, `needs_guard_penalty`, `needs_desertion` (all default on, effective only with the master toggle).
- Not done: production at half rate while starving (listed in section 4), the Stores sub-panel, medical/ammo (phase 5). The unused string `st_homestead_needs_tier_1` is kept for a future "Thin" tier.
