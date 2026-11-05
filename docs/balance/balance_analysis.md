# Balance analysis

Companion to `balance_inventory.md`. Prices are the installed GAMMA `cost` values (base cost in RU, read from
`C:\GAMMA\mods` and the unpacked vanilla configs on 2026-11-05). Pool averages: raw meat 736, pelt 1551, trophy 1023,
scavenged item about 1000 (map tier 2), ammo box about 1100. Unverified: the cost of `prt_i_cloth` and the powders (not found in the
installed configs), so the bandage and crafting input costs are estimates.

## 1. The two prices that matter

Base cost is not cash. GAMMA vendors buy at a fraction of it (`presets/trade_discounts.ltx`): generic 0.10, trasher and
supplier 0.20, barman, mechanic, medic and scientist 0.35, then times the economy `buy` factor (0.75 / 1.0 / 1.25 by
difficulty). The settler Trader (`jobs:2974`) pays `trader_price_percent` x min(1.5, tier mult) of base cost, so it is the
one lever that turns every producer's output, and the player's own loot, into RU.

| Trader rate | Novice | Skilled+ | A 26950 RU rifle sold | An exo outfit (129680) |
|---|---|---|---|---|
| before: 60 % | 60 % | 90 % | 24250 | 116700 |
| after: 25 % | 25 % | 37.5 % | 10100 | 48600 |
| best vendor (barman) | 35 % | - | 9400 | 45400 |

## 2. Best-case output per settler-hour (base cost RU, 100 % uptime)

Model in `tools/tests/test_balance_numbers.lua`, which asserts the ceilings. "Best case" stacks tier x3, the best
specialization, morale x1.1, Drug-Making Kit, stations, benches and night speed-up. Novice figures are the same
formulas at tier 1 and no specialization.

| Job | Novice RU/h | Best case RU/h | Input at best case RU/h | Limiter |
|---|---|---|---|---|
| scavenge | 2100 | 12200 | none | 20 % ambush; the loot pool (about 1/5 of it is powder) |
| hunter, no station | 1800 | 4400 | none | tier capped at 1.5 |
| hunter, station | 6400 | 11600 | none | station bonus is max+1 and x1.5 and pelts and trophies |
| craft | 3300 | 16500 | about 500 | powder from scavenging, stock cap 8 |
| medic bandage | 2400 | 31200 | 360 | stock cap 15 |
| medic akvatab | 10900 | 86900 | 3800 | stock cap 8 per batch, 5 vodka uses |
| medic medkit | 6000 | 48000 | 5400 | stock cap 8 |
| woodcutter | 2400 | 15800 | none | 40 per cycle |
| brewer | 8500 | 45400 | 3000-4100 | 16 per cycle, 7-10 wood |
| scrapper | 1100 | 8100 | none | 35 / 25 per cycle |
| farmer bread | 3600 | 25200 | 400-800 | stock cap 40, 8 per batch |
| trader | n/a | 12 items per 15 min | player goods | now 25 % of base |

Reading it: every producer returns more than its input, which is the design. The checks that keep this from running away
are the stock caps (medic 8 / 15, cook 15, ammo 8, farmer 40), the per-cycle caps and input scarcity (powder, wood,
vodka). Cash needs the Trader or a vendor, and a vendor pays 0.10-0.35.

Outliers, left as they are (they are tuned behaviours, or need a code change):

* Medic akvatab, kalium, medkit with a Clinic and a Drug-Making Kit: the batch is bounded by the stock cap (8), but a
  player who empties the box gets 8 akvatab (36000 base) for 5 vodka uses (1600) every 25 minutes. Clinic medic x2.0 is
  the only specialization above 1.5, and Drug-Making Kit doubles on top. Recommended (code): scale the vodka input with
  the batch, or cap the batch at 4 for the rare types.
* Repair: the fee is one use of vodka, conserva or tushonka (about 315 RU) whatever the gear is worth. A Master with a
  Workshop and a repair bench restores 56 % of a rifle (26950) per item, three items per cycle. A scaled fee would fix it (code).
* Hunter Station: max+1 and x1.5 together, plus pelts and trophies, is 3.5x a station-less novice. Probably intended
  as the reward for building it.
* Scavenge has no cap on the tier multiplier (hunters are capped at 1.5): a Master in a Hideout makes 12 items an hour for no input.

## 3. Units: real time against game time

Job cycles, raider rest and wounded, the Trader and expedition search are real time and use `time_factor()`, which
floors at the RTZ factor. `raiders:game_time_factor` calls `sb.time_factor()`, so it has the same floor: consistent.
Everything below is game time and so runs 6-10 times slower in real time under Real Time Zones (tf 1) than at
GAMMA's own factor:

| Timer | Game time | Real time at tf 10 | at tf 6 | at tf 1 (RTZ) |
|---|---|---|---|---|
| water pump interval | 6 h | 36 min | 60 min | 6 h |
| fridge interval | 12 h | 72 min | 2 h | 12 h |
| food and needs round | 24 h | 2.4 h | 4 h | 24 h |
| raid cooldown | 36 h | 3.6 h | 6 h | 36 h |
| random event cooldown | 48 h | 4.8 h | 8 h | 48 h |
| caravan despawn | 12 h | 72 min | 2 h | 12 h |
| rival convoys | 6 h | 36 min | 60 min | 6 h |
| equipment check | 30 min | 3 min | 5 min | 30 min |
| expedition walk (400 m out and back, 1.2 km/h) | 40 min | 4 min (3 min floor) | 6.7 min | 40 min |

Sources and sinks over the same span: 12 settlers eat 12 food items a game day. A novice farmer with a stove makes 6 bread
an hour, so at tf 10 (5 food items an hour needed) one farmer covers the camp, and at tf 1 (0.5 an hour needed) the camp
has 10 times what it eats. Water is the same: a pump gives the camp free water (`water_free`) and makes 4 flasks a game day.
So under RTZ sinks shrink 6-10x against the real-time sources, the food stock caps (cook 15, farmer 40) are what stops the
pile, and nothing starves. This is the living-needs tuning, so it is flagged, not changed. The one real mismatch is the
expedition walk: its duration is in game seconds (1.2 km/h), so a stash 400 m away takes 4 minutes at tf 10 and 40 under RTZ,
while the search time next to it is real time. Flagged.

Sleep and waiting: a job's backlog is at most 6 cycles, so a long sleep pays at most 6 cycles per settler. Under RTZ clock
sync a load pays none.

## 4. Sinks and sources

| Source | Sink |
|---|---|
| jobs (section 2) | stock caps, settlers' meals, fuel, batteries, filters, repair fees, medic vodka, brewer wood |
| expedition stashes | the world's finite stash list (looted stashes are marked) |
| raid bounty 500-3000 RU, up to 3 a day | goodwill losses (60 per outpost, 150 daily cap per faction) |
| SOS rescue 3000-5500 RU | needs a real rescue |
| settler cut (virtual savings, 60 x tier per cycle, cap 20000) | the settler's own weapon from their faction (spawned, not bought from the player) |
| Trader (player goods to RU) | the player's stock; now 25 % |

The settler cut is a source with no matching cost to the player; it is capped (20000 per settler, one weapon purchase per
tier) and only equips the settler. Left.

## 5. Changes made

| # | Change | Before | After | Reason |
|---|---|---|---|---|
| 1 | `trader_price_percent` default (code, MCM, fallback) | 60 | 25 | Vendors pay 10-35 %; the Trader paid 60-90 % |
| 2 | Farm: woodcutter, brewer; Workshop and Hideout: scrapper in `camp_specializations` | not listed (happy camp x1.1, unhappy x1.25) | 1.25 (happy 1.375, unhappy 1.25) | The jobs' x1.25 fallback fires only at exactly 1.0, so happy camps made less |

## 6. Flagged, left alone

* Medic output of rare meds at the Clinic and Drug-Making Kit ceiling (section 2). Needs a code decision on batch size or input.
* Repair fee does not scale with gear value (section 2).
* Expedition walk time is game time (section 3). A fix is a code change to the duration formula.
* Hunter Station double bonus, uncapped scavenge tier multiplier, three pumps for the price of one filter.
* Game-time timers under RTZ (section 3); the needs defaults are tuned.
* Raid cooldown (20 real minutes rest, 40 wounded, 3 a day), build kit, furniture lock, performance work: untouched.
* Players with a saved MCM profile keep their old Trader price of 60 until they press Default.

## 7. Playtest

* Hire a Trader with a market stall, stock a rifle and an outfit, and check the till after one visit: expect 25 % of the
  base price (37.5 % for a Skilled trader).
* A Farm settlement with a woodcutter, a brewer and morale over 80: wood and vodka per cycle should rise by about 25 %.
* A Workshop or Hideout scrapper in the same state.
