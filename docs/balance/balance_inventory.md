# Balance inventory: item production and timers

Branch `claude/balance-pass-291ba0`, based on main `0fb606b`. Values are the shipped defaults (the `defaults` table
in `stalker_camp_builder.script`, repeated as `def =` in the MCM). A player's saved MCM value overrides both; the
MCM default only applies to a fresh profile.

Clock column: **R** = real seconds (`time_global`), **G** = game seconds (`game_sec()`), **R x tf** = a real-time
quantity stored as game seconds by multiplying with `time_factor()`. `time_factor()` floors at the RTZ configured
factor, and under RTZ clock sync `job_game_elapsed_sec` returns 0, so only the real clock counts for job cycles there.
Game-time timers (pump, fridge, meals, needs, raid and event cooldowns and checks, caravan, convoy, rival setup/tier/skirmish, equipment check, expedition walk) are multiplied by `game_timer_scale()` (tf/6 while RTZ locks the factor below 6, else 1); the values below are the unscaled ones.
File references are in `00_Core/gamedata/scripts/`; `main` = `stalker_camp_builder.script`.

## 1. Settler job cycles

A cycle runs when `max(real elapsed, game elapsed / tf) >= interval / time-of-day mult`
(`jobs:3860-3960`). Backlog is capped at 6 cycles (`jobs:3905`), 2 cycles per settler per tick (`jobs:3957`) and 6 per
tick overall (`jobs:3402`). Night = game hour 22-05 (`main:701`): scavenge and medic run x1.2 faster, cook x0.8
(slower), the rest x1.0. A job lacking inputs or storage room retries after 30 s, or 120 s after a full-storage
pause (`jobs:4170`).

| Job | Interval default | Clock | Source | Feeds |
|---|---|---|---|---|
| cook | 900 s | R | main:730 | meals from raw meat |
| craft (ammo) | 1200 s | R | main:731 | ammo boxes, turret ammo |
| repair | 900 s | R | main:732 | gear condition |
| scavenge (job) | 2100 s | R | main:733 | loot items |
| hunter | 1800 s | R | main:734 | meat, pelts, trophies |
| woodcutter | 1200 s | R | main:735 | wood parts, charcoal |
| brewer | 1200 s | R | main:736 | vodka, alcohol |
| scrapper | 1200 s | R | main:737 | scrap, fasteners |
| farmer | 1200 s | R | main:738 | potatoes, grain, bread |
| trader | 900 s | R | main:739 | RU into the stall till |
| medic | 1500 s | R | main:808 | medical items |
| electrician | 900 s | R | main:809 | lamp, battery, detector charge |
| guard | cycle pays XP and cut only | R | jobs:4108 | defence, turret upkeep |
| equipment check, prosper tick | 1800 s | G (not divided by tf) | jobs:3848 | weapon purchase, standing |
| legacy `job_*_interval`, `job_update_interval` | 7200-43200 s | G | main:723-728 | unused by the live loop |

## 2. Yields and conversions (per cycle, before multipliers)

Multipliers: tier x1.0 / 1.5 / 2.0 / 3.0 (novice / skilled / expert / master; XP 100 / 250 / 500 at 10 XP per
completed cycle, `main:5470-5500`), specialization (`defaults.camp_specializations`, `main:873`), morale above 80 gives
x1.10 (`recruit:2841`), `craft_output_multiplier` (MCM 1-3, default 1), ambush 20 % on scavenge and hunter.
`consume_one_use` takes one use of a multi-use item, so "1 vodka use" is one third of a bottle.

| Job | Input | Output | Caps | Source |
|---|---|---|---|---|
| scavenge | none | 1-2 items (main:789) x tier x spec, drawn from `generate_gamma_stash_loot` for the map tier | none | jobs:223 |
| hunter | none | 1-2 raw meat (main:744) x min(1.5, tier) x spec; with a Hunter Station max+1, x1.5, 75 % pelt, 60 % trophy | none | jobs:350 |
| craft | 1 powder use + 1 scrap | 1 ammo box x tier x spec, +1 with an ammo bench; basic ammo only | stock 8 per class, 15 auto | jobs:658 |
| repair | 1 use of vodka, conserva or tushonka per item | +25 % condition (MCM) x spec x bench 1.5; items per cycle = tier mult | none | jobs:895 |
| cook | 1 raw meat, fuel use on a stove, water (tier 2) or vodka (tier 3) | 1 meal x spec(food) | food stock 15 | jobs:1806 |
| medic bandage | 1 cloth, or 1 vodka use | bandage x tier x spec(medic) x drugkit 2 | stock 15, batch limited to room | jobs:2006 |
| medic medkit | 4 vodka uses + 1 bandage | medkit, same multiplier | stock 8 | jobs:2074 |
| medic kalium | 3 vodka uses | antirad_kalium | stock 8 | jobs:2065 |
| medic akvatab | 5 vodka uses | akvatab | stock 8 | jobs:2054 |
| electrician | battery or generator fuel use | recharges up to 3 x tier x spec batteries (max 4); fabricates a dead battery from copper + scrap | n/a | jobs:2234, :2336 |
| woodcutter, wood | none | 4-8 wood (main:746), axe or station 8-12, station +2; x tier x spec | 40 | jobs:2446 |
| woodcutter, charcoal | 5 wood | 3 (+2 axe, +1 station) charcoal x tier x spec | 25 | jobs:2534 |
| brewer | 7 wood (distiller) or 10, plus potato, water or ferment | 2 (3 distiller, +1 potato, +2 drugkit) vodka x tier x spec; alcohol from tier 2 | 16 | jobs:2624 |
| scrapper | none | 3-6 scrap, 1-3 fasteners (main:748-751), tools 6-10 / 2-5, x tier x spec | 35 / 25 | jobs:3062 |
| farmer, potato | none | 3-6 (+3 station) x tier x spec(food) | 30, stock 40 | jobs:2817 |
| farmer, bread | 3 grain per batch | 2 (3 station, +1 at tier 2) bread per batch, 1-2 batches | 8, stock 40 | jobs:2849 |
| trader | goods in the stall stash | RU = base cost x condition x `trader_price_percent` x min(1.5, tier mult); top 12 items | 12 items | jobs:2974 |
| water pump | 1 filter per interval | pumps x spec flasks (3 uses each) | needs room | jobs:3749 |
| fridge | none | +0.25 condition on food | n/a | jobs:3812 |

## 3. Expeditions, raids, events, rivals

| System | Value | Clock | Source |
|---|---|---|---|
| scavenger walk speed | 1.2 km/h, x game_timer_scale() | G (real under RTZ) | MCM `scavenger_walk_speed_kmh`, expeditions:630 |
| expedition search time | 60 s per stash, 45 s per sweep stash | R x tf | expeditions:640, :1070 |
| expedition minimum | 180 s same level, 360 s cross level | R x tf | expeditions:646 |
| tier walk reduction | 10 % per tier | - | expeditions:637 |
| expedition ambush | 20 %; a win bonus of 5 items | - | expeditions:1704 |
| expedition stash loot | white 3-6 items + 50 % powder, 46 % casing, 35 % bullet; yellow adds 1-2 weapon/outfit/artefact rolls and a toolkit | - | expeditions:754 |
| raid cooldown (attacks on the settlement) | 129600 s = 36 h | G | main:715 |
| raid check | 3600 s | G | main:716 |
| random event cooldown, check | 48 h, 2 h | G | main:717-718 |
| caravan trader despawn | 12 h | G | main:719 |
| water pump interval | 6 h | **G** | main:721 |
| fridge interval | 12 h | **G** | main:720 |
| food ration interval | 24 h | **G** | main:722 |
| raider mission | distance / 3 m/s + 1800 s, clamped 1800-14400 s | G | raiders:280, :42-43 |
| raider rest, wounded | 20, 40 real minutes | R x tf | main:839-840, raiders:253 |
| raiders per day, goodwill cap | 3, 150 per faction | G day | main:848, :847 |
| target cooldown after a mission | 24 h | G | raiders:1207 |
| raid bounty | 500 / 1500 / 3000 RU by camp tier, plus 60 % of the chest by count | - | raiders:39, :299 |
| raider cut | 15 % of haul value as savings | - | main:843 |
| assault stall, hard limit, linger | 150, 900, 90 real seconds | R x tf | raiders:547-550 |
| rival spawn scan, interval, chance | 60 s real, 3 h, 33 % | R, G, - | rivals:333, main:761 |
| rival tier 2, tier 3 | 4 h, 8 h | G | main:768-769 |
| rival convoy interval | 6 h | G | main:772 |
| rival setup duration | 24 h | G | main:803 |
| skirmish cooldown | 6 h | G | rivals:1154 |
| skirmish response countdown | 180 s | R x tf | rivals:1096 |
| SOS rescue reward | 3000-5500 RU | - | rivals:3244 |
| SOS memory | 2 h | G | rivals:3224 |
| abandon cooldown | 2 h | G | main:5336 |
| hospitality sleep check | 3 h | G | main:5448 |

## 4. Needs, savings, fees, sinks

| System | Value | Clock | Source |
|---|---|---|---|
| needs round (`needs_enabled`, default on) | 24 h, consumption x1.0, grace 3 days, catch-up cap 1 | G | needs:40, main:851-854 |
| needs penalties | 5 per unserved settler (cap 20), +25 starving, cap 35, variety +5 | - | needs:19-24 |
| guard strength when starving | x0.6 | - | needs:210 |
| settler cut | 60 RU per cycle x tier mult (guard: none), cap 20000 | per cycle | main:826-827, prosper:62 |
| settler weapon purchase | weapon cost + 2 ammo boxes, once per tier | per equipment check | prosper:125 |
| move on (off by default) | 10 % per check, savings >= 5000 | G | main:830-833 |
| recruitment fee | 0 / 0 / 2500 / 5000 / 10000 / 16000 / 25000 / 35000 by rank | - | recruit:151-158 |
| fast travel | 2000 RU | - | main:807 |
| medic service | wounds 1850, rad 1480, full 3350 RU | - | recruit:4158 |
| weapon overhaul | cost capped by tier, minimum 150 RU | - | recruit:4006 |
| settler repair fee | one use of vodka, conserva or tushonka per repaired item | - | jobs:861 |
| generator fuel | one kerosene use (or jerrycan) per shift | per cycle | jobs:68 |
| lamp battery | one battery per electrician cycle | per cycle | jobs:63 |
| stove fuel | one use per cook cycle | per cycle | jobs:1886 |
| water filter | one per pump interval | G | jobs:3749 |

## 5. Caches and UI timers (no balance effect)

structure scan cache 30 s (main:679), camp box cache 30 s (main:680), MCM read cache 5 s (main:1001), dashboard cache
15 s (main:5513), refugee despawn check 60 s (main:2451), scan expiry 10 min (scan:149, :308), trader stock retry
0.5 s (jobs:3631), reinforcement mission 120 s (rivals:3184), raid tick 3 s (raiders:646), expedition tick 1 s
(main:2138), alarm scan 0.15 s (bind_alarm_system:21). All real time.

## 6. Where the analysis lives

`docs/balance/balance_analysis.md`: value-per-hour model, comparison with vendor prices, units audit, changes made and
left alone. `tools/tests/test_balance_numbers.lua` pins the defaults and the ceilings.
