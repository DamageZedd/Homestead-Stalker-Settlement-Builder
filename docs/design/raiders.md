# Raiders: design (not implemented)

Status: DRAFT, owner decisions recorded (see Decisions). No feature code exists. Internal doc, not README content.
Origin: suggestion from Discord user Wx (raiders attack and capture/loot camps that are not the player's, and can be sent to reinforce the player's settlements under attack), plus the owner's Goodwill idea (losing or looting a chest friendly to a faction costs goodwill with that faction; bandit-style play).
Cites are from `main` at b385d08 and will drift. Paths: `00_Core/gamedata/scripts/`, abbreviated `sb` (stalker_camp_builder), `jobs`, `events`, `rivals`, `exp` (expeditions), `prosper`, `needs`, `pda`, `mcm`.
Nothing here was run in game; "feasible" below means "reads as feasible from the code", not "tested".

Goal: the player does not care which faction robs someone else's outpost, so hand that chore to a settler job. A Raider is a survivor job that takes a rival outpost (or hits one for loot), brings the haul home, and can be recalled to help defend the player's own camp. The Goodwill rules make "who you rob" a real choice, and give bandit-style players a path where robbing is the point.

## Decisions (owner answers, 2026-11-03)

These override anything below that disagrees. Question numbers refer to the original list (section 16).

| Q | Decision |
|---|---|
| 1 | **Clear and loot.** A raided camp becomes "cleared" (the existing unoccupied/ruins state). It is not player-owned. Captured outposts are dropped from the plan. |
| 2 | **Player-directed only.** The player picks the target and sends the band. No auto-targeting and no auto mode; `raiders_auto_mode` and timed ranking are removed. |
| 3 | **Both.** Abstract timer-and-odds missions AND visible real fights when the player is on the level. Real assault is a planned phase after the abstract one (section 5), and both share one mission record. |
| 4 | **Both goodwill cases.** Robbing a camp of a faction friendly to the player (new), plus the existing raid reputation for the player's own settlement being hit. |
| 5 | Keep the numbers: -60 goodwill per robbed camp, an extra -100 for a faction friendly to the player, daily cap 150 per faction. |
| 6 | **Bandit mode:** reduced penalties, bandit/renegade reputation, richer loot. It does not change the player's faction. |
| 7 | An idle raider at home counts as **half a guard**. |
| 8 | **Rank 2+**, and at least one guard stays home. |
| 9 | A failed raid: raiders **return wounded** and unavailable for a while. **Permanent death only on a disaster outcome.** The flat 25% death chance is dropped. |
| 10 | Keep 60% of the chest, 15% cut, cash bounty by tier. **Add an MCM toggle to forbid weapon/armor loot.** |
| 11 | Use the **existing retaliation timers**, no extra damper. |
| 12 | **Recall button plus optional auto-recall (default off).** Abstract teleport-back; no real arriving squads. |
| 13 | Not asked; default: no mutant nests, no story camps, no own settlements as targets. |
| 14 | **Design the PDA hooks now**: see section 9, based on the current `ui_stalker_camp_builder_pda.xml`. |
| 15 | Not asked; default: English now, Russian carries the English text until translated. |

## 1. What exists today

| Area | Today | Where |
|---|---|---|
| Jobs | A survivor has a free string `job`. Known jobs: idle, guard, scavenge/scavenger, craft, repair, cook, hunter, medic, electrician, brewer, farmer, woodcutter, scrapper, trader. Set via `set_<job>_job` -> `set_survivor_job`; counted by name in `get_camp_stats` (`stats.guards`, `stats.scavengers`, ...). | `sb` ~4986-5010 (setters), ~5120-5140 (counts); `jobs` dispatch ~3850-4100 |
| Job cadence | Real-time: `realtime_job_<job>_interval`, `job_start_realtime`, load rebase caps credit at one interval. | `jobs` 3850, 4208, 4292; `sb` 4486 |
| Pause logic | `_calc_job_paused_status` decides "waiting for inputs / storage room" and the PDA shows `shortfall_reason`. Idle and guard are exempt. | `jobs` 1246-1297 |
| Scavenger expeditions | The closest existing model. A scavenger is dispatched to a stash (or a regional sweep) on any level; the NPC is teleported away, a timer runs on game seconds, stashes are looted at progress points, an ambush is rolled, the haul is deposited in camp, the NPC returns and gets XP. State lives in `sb.active_stash_expeditions`, receipt text and radio chatter included. It is an abstraction: no real travel. | `exp` 1278-1470 (dispatch), 1691 (`roll_expedition_ambush`), 1719 (deposit), 1945 (`process_stash_expeditions`) |
| Rival camps | World outposts of other factions, tiers 1-3, a chest (`camp.chest_id`) holding loot, a garrison squad (`camp.squad_id`, `extra_squad_ids`), `camp.faction`, `camp.status` (nil / "unoccupied" / mutant nest). Spawn, upgrade, convoys, SOS calls, retaliation, ruins decay all exist. | `rivals` 2292 (spawn), 1233 (per-camp tick), 1517 (`update_rival_camps`), 2709 (upgrade), 2856 (convoys), 3164 (allied reinforcement), 3208 (SOS reward) |
| Capturing a rival camp | When the garrison dies, `mark_rival_garrison_eliminated` sets the camp "unoccupied" with a ruins timer and `cleared = true`; it does not turn the camp into anyone's property. Retaliation squads may follow if the faction hates the player. | `rivals` 1201-1232 |
| Rival-vs-rival | Only "allied reinforcement": same-faction rival camps within 175 m (`30625` = 175^2) and on the same level send their squad for two minutes to a defending rival camp. | `rivals` 3164-3206 |
| Raids on the player | `process_camp_raids` rolls per camp every `raid_check_interval` while the player is within `event_player_dist`; chance = `raid_base_chance` + deficit x `raid_deficit_mult`; one raid per camp at a time (`camp.active_raid`); cooldown `raid_cooldown`. `spawn_camp_raid` places a raider squad 60+ m out. Raids exist only while the player is on the camp's level. | `events` 400-460, 210-385; defaults `sb` ~800 |
| Raid bookkeeping | `camp.active_raid = { squad_id, faction, original_squad_size, remaining_count, guards_lost, settlers_lost, raiders_killed }`. Raid ends when the squad is gone, or when the player leaves the level (then the squad is released). | `events` 546-625; death hook `sb` ~5810 |
| Raid reputation (shipped) | `raid_apply_reputation` pays goodwill loss to the raiders' enemies (`relation_registry.change_community_goodwill(faction, actor:id(), -pts)`), skipping the raiders, the player's own faction and non-factions; MCM `raid_rep_enabled`, `raid_rep_per_settler`, `raid_rep_cap`. | `events` 460-532; `sb` 806-808 |
| Other goodwill | `settler_move_on_goodwill` (+100 to the settler's faction), `refresh_settler_goodwill` / `force_set_goodwill` keep settlers friendly with each other and the player (per-NPC, not faction). | `prosper` 294-322; `sb` 2707, 6519 |
| Defenders | Defense is a number (`stats.defense`); guards count x5, turrets and alarm add. No settler is ever "sent" anywhere except scavengers. Settlers fight in place as ordinary NPCs. | `sb` 5180; `events` 400-460 |
| Needs | Living Needs (`needs`) is an opt-in layer on the same camp record; a Starving camp already halves guards and blocks savings. A Raider job should respect it. | `docs/design/living_needs.md`, `needs` |
| Save | `save_state` packs `active_camps` wholesale (per-field pcall); `normalize_camps` fills defaults; new fields on survivor or camp records need no migration if nil means "not started". Rival camps save separately in `sb.rival_camps`. | `sb` 3755-3987 |
| MCM | Defaults table (`sb` ~690-810), key -> path map (~870), `mcm` group definitions, localization in 3 places plus XML (English XML stays ASCII). | as listed |

Two facts shape the whole design:

1. There is no ownership model for rival camps. A rival camp has a faction, a garrison and a chest, and nothing else. "Capture" has to be invented (section 5).
2. The scavenger expedition is an abstract, timer-driven, level-independent job that already survives save/load and sleeping. Anything that must work while the player is elsewhere should copy that shape, not try to simulate real NPC travel across levels.

## 2. Design principles

1. Default OFF. Master toggle `raiders_enabled = false`; with it off nothing changes, and a settler can never be given the job.
2. Abstract first, real combat later. Phase 1 resolves a raid on a timer with odds (like expeditions). Real fights are only used where the player is already present.
3. Never block the player. A Raider is always recallable, and the camp always keeps its guards (a camp needs a guard minimum before it may send raiders).
4. Add fields, not formulas. `camp.defense` / `camp.happiness` math stays as is; a raider away simply is not counted as a guard.
5. Goodwill is paid through the same helper the raid reputation already uses (one function, one clamp).
6. One new file `stalker_camp_builder_raiders.script` (recommended, same reason as `needs`: `sb` is 7000+ lines and near Lua's local/upvalue limits; `tools/check_lua.ps1` guards that).
7. Pure functions for odds, loot split and goodwill math, unit-testable with the Lua 5.1 on this machine (`tools/tests/`).

## 3. What a Raider is

A new survivor job `raider`, assigned like the others (PDA Survivors tab, Job page), counted in `get_camp_stats` as `stats.raiders`.

Requirements to take the job (checked when assigning and again before each dispatch):
- not wounded, not on another expedition or mission, has a weapon and ammo in inventory (the `survivor_se` checks scavengers use);
- **rank 2 or higher** (default; MCM `raiders_min_rank`);
- the camp keeps **at least one guard** at home (`raiders_min_guards`, default 1).

Guard accounting: a raider away or wounded counts as no guard in `stats.defense`; an **idle raider at home counts as half a guard**.

Band: 1 to 4 raiders sent together (default size 3). Odds and loot scale with the band. Phase 2 may ship lone-wolf only.

Wounded state: a raider back from a failed raid has `survivor.raider.wounded_until` (game seconds). While wounded they cannot be sent and count as no guard. Default 12 game hours (MCM `raiders_wounded_hours`).

## 4. Target selection (player-directed only)

There is no auto-targeting. The player picks a rival outpost on the Outposts tab (section 9) and sends the band. Invalid targets get a disabled button with a reason.

Valid target: an occupied rival camp in `sb.rival_camps` (`camp.status == nil`, `camp.faction` set, not monster or zombied), not already under a raid mission, not on cooldown. Never valid (not configurable, per Q13):
- the player's own settlements and anything inside the settlement boundary (`in_player_settlement`, `rivals` 55);
- camps whose garrison holds a story NPC (`squad_has_story_npc`, `rivals` 731);
- mutant nests and zombified camps.

Friendly factions: a camp of a faction friendly to the player is **allowed**, because the goodwill system prices it (section 7). The confirm panel warns in red and shows the cost. With `raiders_spare_friends` on (default) the button is disabled for friendly camps unless bandit mode is on.

## 5. Travel, combat, capture: one mission record, two resolvers

Both abstract missions and visible real fights are wanted. They share **one mission record**, so a mission can start abstract and become real (or fall back) without a second code path for loot, casualties, goodwill or cooldowns.

### 5.1 The mission record

```
camp.raider_missions[mission_id] = {
  id, state,            -- "away" | "assault" | "returning" | "done"
  mode,                 -- "abstract" | "real"   (abstract -> real once; real -> abstract on fallback)
  target_key, target_level, faction,
  raider_ids = {...},   -- settler npc ids (plain numbers)
  start_sec, duration, arrive_sec,
  odds,                 -- snapshot shown at dispatch, recomputed at resolve
  real = { squad_id, spawn_lvid, spawn_gvid, started_sec },   -- only when mode = "real"
  result,               -- nil | "success" | "repulsed" | "disaster"
  loot_rolled = false, goodwill_paid = false
}
```

The record lives on the camp (not the NPC), so it survives NPC re-creation (`restore_missing_settler`) and save/load. Result, loot and goodwill are applied by one function `finish_mission(camp, mission, result)`; both resolvers only decide the `result` and the casualty list. `loot_rolled` and `goodwill_paid` make it idempotent.

### 5.2 Resolver A: abstract (phase 2)

1. Dispatch: raiders are teleported off like `teleport_scavenger_on_departure` (`exp` 1238) and flagged `surv.on_mission = id`.
2. Duration: game-graph distance (as `get_self_contained_distance`, `exp` 608) plus a 30 game-minute assault window; capped like expeditions.
3. At the end, `raid_outcome(band, target, rng)` (pure function) returns `success | repulsed | disaster` from attacker strength (rank, weapon and armor tier) against garrison size x tier factor plus the camp's defenses. Win chance is a logistic of the ratio, clamped 5%-90%, shown before sending.
4. Casualties (Q9): on **success** none. On **repulsed**, every raider returns **wounded** and unavailable for `raiders_wounded_hours`, no loot. On **disaster**, each raider has `raiders_disaster_death_chance` (default 50%) to be lost permanently; survivors return wounded. Lost raiders leave through the same path as a killed settler (`settler_lookup`, relations, "settler killed" bookkeeping).
5. On success: remove the garrison through `mark_rival_garrison_eliminated` (`rivals` 1201) with a nil actor, so map spot, ruins decay, `cleared` and the faction retaliation timers (Q11) follow the existing code, undamped.

### 5.3 Resolver B: real assault (phase 4)

If when the band arrives the player is on the target's level (and within about 300 m, so the camp is online), the mission switches to `mode = "real"`, `state = "assault"`:
1. The band is spawned as a real squad near the camp (`create_squad_at_pos`, `rivals` 470), pointed at the camp with `scripted_target`, and tagged with the mission id.
2. The existing garrison logic judges the fight; the mission polls the squad every few seconds (the alive-count pattern of `check_completed_raids`, `events` 546).
3. Result: garrison gone and some raiders alive = `success`; band gone = `disaster` (those deaths are real, no extra roll); a stalemate timeout (default 6 game minutes without progress) or the player leaving the level = fall back to Resolver A's roll using the raiders still alive, so a half-finished fight never leaves a mission hanging.
4. The player can join the fight. Loot comes from the live chest (section 6).
5. This is the highest-risk piece: squad AI control, companion-squad id collisions (see `end_camp_raid`), and the mission/level-leave race. It ships behind `raiders_real_assault` (default off), and Resolver A stays the fallback for every failure.

A `real` mission found on load has no live squad: it is converted to `abstract` and re-rolled from the raiders still alive, never resumed mid-fight.

### 5.4 Capture

Cleared only (Q1): garrison gone, chest looted, the camp left in the existing unoccupied state with its ruins timer. No ownership model, no hold, no raid-back.

## 6. Loot rules

- Loot comes from the target's chest (`camp.chest_id`) and what the abstract resolver rolls from its tier, not from the player's boxes. At resolution on Success: take a fraction of the chest, `raiders_loot_fraction` default 60% of items by count (a weighted pick favoring ammo, meds, food, then weapons), and the rest stays for the player to find. Rationale: the player can still do the outpost themselves and sees a believable leftover.
- If the chest is not loaded (other level), roll a synthetic haul from the tier loot tables already in `rivals` (~2487-2520 initial loot lists, 944 resupply list), the way `generate_gamma_stash_loot` (`exp` 755) synthesizes stash loot. No item is removed from an unloaded object (avoids server-object edits; Phase 0 must confirm `camp_consume_item` offline works, as needs did).
- Split: the camp keeps the haul (deposited like `deposit_expedition_haul`, `exp` 1719, into settlement storage only, never personal boxes, honoring `is_settlement_storage`). Raiders keep a cut in rubles into their savings via `prosper_credit` (default 15% of haul value, ties into the existing "cut per cycle" economy; a Starving camp pays none, matching `needs`).
- Money: rival chests do not hold cash today, so cash is a flat bounty by tier (default 500/1500/3000 for tiers 1-3, scaled by an MCM multiplier).
- Weight/space: if the settlement has no room (existing storage-full pause), the mission still resolves but the surplus is dropped to a "loot pile" (a stash at the camp) rather than lost; Phase 1 may simply pause dispatch when storage is nearly full.
- **Weapon and armor toggle (Q10):** MCM `raiders_forbid_weapon_armor` (default off). When on, weapon and armor items are excluded from both the live chest pick and the synthetic haul; they stay in the rival chest for the player.
- Cooldowns: a raider returns, rests (`raiders_rest_hours`, default 6 game hours; wounded raiders use `raiders_wounded_hours` instead) before the next mission, and a given target camp cannot be raided again for `raiders_target_cooldown_hours` (default 24; on top, rival camps already respawn/decay on their own timers).
- Anti-exploit: loot value per mission is capped, per-day missions are capped (`raiders_max_per_day`, default 3 per camp), and a cleared camp yields nothing on a second visit.

## 7. Goodwill and the bandit option

All numbers are MCM-tunable. Goodwill uses `relation_registry.change_community_goodwill(faction, actor:id(), delta)` through one wrapper in the new script (the raid-reputation code, `events` 491, already shows the pattern including the faction filter and the "skip non-factions" list; the wrapper should reuse it, not copy it).

Who is hit when a raider (or the player) robs a camp:

| Event | Goodwill change |
|---|---|
| A raider band takes down a camp of faction F | F: `-raiders_goodwill_loot` (default -60 per camp, Q5). F's allies (friends of F, from `game_relations`): half. F's enemies: `+raiders_goodwill_enemy_bonus` (default +15, off by default; optional). |
| A raider loots a chest friendly to F (a camp where F has goodwill > 0 with the player) | F: -100 extra "betrayal" penalty (Q5). Robbing someone who likes you is worse than robbing an enemy. |
| The player loots a rival chest of a friendly faction manually | Same as above if `raiders_player_loot_goodwill` is on (default off, because the base game's own rules apply to that). |
| A raider dies in a mission | no goodwill effect; pure settler loss |
| Player recalls a mission before resolution | none |

Hard caps per faction per day (default 150) so one bad dispatch cannot burn a faction permanently. Goodwill in X-Ray is a bounded integer (communities range is roughly +-5000; kill-driven changes elsewhere use hundreds), so numbers here are intentionally of the same order as `raid_rep_per_settler = 25`; values are placeholders until playtest (open question 5).

Q4: both cases apply. (a) Robbing a rival outpost of a faction friendly to the player is the new rule above. (b) The player's own settlement chests hit by a raiding faction stay under the existing raid reputation (`events` 491), unchanged. They are separate code paths and must not double-count.

### Bandit-style play option

`raiders_bandit_mode` (default off). When on:
- target filter "Anyone" is allowed, friendly camps included;
- goodwill loss with robbed factions is reduced (default x0.5) and a new self-sustaining stream appears: extra loot +25% and cash bounty x1.5 ("protection racket");
- gains reputation with bandit-aligned factions (bandit, renegade; list configurable in code, not MCM) per successful raid (default +20), so a player who plays a bandit grows a standing with them;
- raid reputation for lost settlers keeps working unchanged.
It does not change the player's own faction or relations; it only changes what raiders do and how it is priced. "Playing as a bandit" in the sense of changing the player's faction is already a base-game/GAMMA concern (`get_player_faction`, `sb` raid code reads it).

## 8. Reinforcement during attacks (Q12)

Recall button plus optional auto-recall; no real arriving squads.

1. While the camp has an `active_raid` (`spawn_camp_raid`), the PDA shows **Recall raiders** (section 9). A recall cancels every mission of that camp that is `away` or `returning`, via the same path as `recall_scavenger_expedition` (`exp` 152): no haul, no goodwill change; wounded raiders are unaffected. The raiders reappear at the camp after a short delay (default 20 s real time) and fight as ordinary guards for the rest of the raid. This is an **abstract teleport-back**: no travel is simulated, and a raid only exists while the player is on the camp's level, so the band is placed beside the hub.
2. `raiders_auto_recall` (default **off**): the same recall fires when the raid starts.
3. A mission in real mode (5.3) on the same level is recalled the same way: its squad is released and the members are teleported to the hub.
4. Raiders at home already count as half guards, so they lower raid chance without any recall.
5. Edge cases: camp on another level (raids never happen there, no button); a dead raider (nothing to recall); a wounded raider (stays home, does not fight); the player leaves the level mid-recall (`end_camp_raid` cleans the raid; raiders simply stay home).

## 9. PDA surface: exactly where Raiders hooks in

Based on `00_Core/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml` and `ui_stalker_camp_builder_pda.script`. Four copies of the XML exist (`00_Core`, `01_Theme_Modern`, `01_Theme_ModernVanilla`, `01_Theme_Vanilla`); every XML change below is made in all four. Everything is hidden when `raiders_enabled` is off.

### 9.1 Survivors tab: job list and roster
- **Job button.** The Job page lays the job buttons in a 4-column grid (83x24 buttons, 89 px column pitch, 28 px row pitch; `LayoutSurvivorPages`, `SV_JOB_ORDER`). That is 16 slots for 14 jobs, so **`btn_job_raider` takes slot 15 (column 3, last row) with no layout change**. Add:
  - XML: a `btn_job_raider` block copied from `btn_job_trader` (xml ~515) using `st_job_raider_btn`;
  - script: `init_safe_job_btn("btn_job_raider", "raider", self.btn_job_guard)` next to the others (script ~735), an entry in the `job_btns` table (~2160) and in `SV_JOB_ORDER`;
  - when the toggle is off the button is not initialised and the grid looks as today.
- **Roster rows** (`survivor_list`; columns Name / Job / Rank / Needs): the Job column prints the localized job label; add `st_job_raider` ("Raider") and, on a mission, a short state suffix ("Raider (away)", "Raider (wounded)"), kept under about 16 characters for the 130 px column.
- **Summary banner** (`sv_sum_bg` / `sv_sum_lbl`, filled in `UpdateSurvivorHeader`, script ~2275): reuse the existing banner kinds: dim while resting, `secure`/good while away ("Raiding: <outpost>, back ~2h"), `threat`/warn while wounded ("Wounded, back in 8h"). No new widget.
- **Waiting reason** (the "Waiting:" line, `_calc_job_paused_status`, `jobs` 1246): new reasons: no weapon, no ammo, rank too low, wounded, camp needs a guard.
- **Stats page** (`sv_stat_lbl_1..4`): all four rows are used; while the job is `raider` the least useful row is replaced by mission count and last haul. No fifth row.
- **Orders page**: unchanged.

### 9.2 Outposts tab (`rivals`): the Send raiders button
The detail panel `rival_content` is a fixed 350 px stack: hero 0-118, banner 124, faction/garrison/distance tiles 154-212, status line 216, Intel box 240-392, buttons `btn_rival_locate` (x 0, w 170) and `btn_refresh` (x 180, w 170) at y 400, content height 490.
- **Add one full-width button `btn_rival_raid`** (350 x 28) at **y 432**, under the existing two, inside the 490 px content so nothing is resized. Shown only when the toggle is on and the selected card is an occupied rival camp. Init in the same block as `btn_rival_locate` (script ~481).
- **States** (set where `OnRivalSelected` fills the panel): enabled "Send raiders" when a raider is free and the camp is valid; disabled with the reason in `rival_banner_lbl` for: no free raider, cooldown, story camp, nest, friendly faction while `raiders_spare_friends` is on, mission in progress.
- **Confirm.** The click opens a confirm in the style of the banish and rename confirms, listing band, win chance, estimated loot and goodwill cost, plus "retaliation likely" when the faction hates the player. A friendly faction gets a red line with the -60 and -100.
- **Banner and Intel.** While a mission targets the camp, `rival_banner_lbl` shows "Raid in progress, back in Xh" (role warn) and `rival_camp_intel` appends one line with band size and odds.
- **Recall.** With a mission active the same button becomes "Recall raiders" (no loot, no goodwill).
- **List cards** (`RivalListItem`, `pill_text`): the pill shows "RAID" while a mission targets the camp. No new widget.

### 9.3 Overview tab
- **Status page:** the raid banner (`raid_banner_bg` / `raid_banner_lbl`, y 68, filled ~script 1714) gets one more segment only when relevant: "Raiders: 2 away, 1 wounded".
- **Defense page:** the Perimeter text shows "guards (+ N raiders away)", so the cost of sending raiders is visible.
- **Orders page:** a **Recall raiders** button, `btn_ov_recall_raiders`, as one full-width row, shown only while `camp.active_raid` exists and a raider is away. The raid banner is not used as a click target; a real button is more discoverable.

### 9.4 Radio and tips
Mission start, result, wounded, disaster and goodwill losses go to `add_radio_feed_entry` and `camp_send_tip`; ASCII text via `translate_string`.

### 9.5 What is not changed
No new top tab, no new panel, no change to list widths or the left container. Raiders add one job button, one Outposts button, one Overview button, and text in existing labels. The Survivors and Outposts redesign sessions (`docs/design/pda_survivors/`, `docs/design/pda_outposts/`) should be told about the reserved places (job grid slot 15, Outposts y=432, the Overview Orders row) before they add layout.

## 10. MCM options (new "Raiders" group)

| Key | Type | Default | Purpose |
|---|---|---|---|
| `raiders_enabled` | check | **false** | Master toggle; off = job hidden, no missions, no goodwill code runs. |
| `raiders_bandit_mode` | check | false | Section 7 bandit-style rules. |
| `raiders_spare_friends` | check | true | Disable Send raiders for factions friendly to the player (ignored in bandit mode). |
| `raiders_min_rank` | track 0-4 | 2 | Minimum prosper rank. |
| `raiders_band_size` | track 1-4 | 3 | Raiders per mission. |
| `raiders_min_guards` | track 0-4 | 1 | Guards that must stay home. |
| `raiders_idle_guard_weight` | track 0-100 | 50 | Percent of a guard an idle raider at home counts for. |
| `raiders_disaster_death_chance` | track 0-100 | 50 | Per-raider permanent-death chance on a disaster (a failed raid only wounds). |
| `raiders_wounded_hours` | track 1-72 | 12 | Game hours a wounded raider is unavailable. |
| `raiders_forbid_weapon_armor` | check | false | Raiders never take weapons or armor from a chest. |
| `raiders_real_assault` | check | false | Phase 4: visible fight when the player is on the level. |
| `raiders_loot_fraction` | track 10-100 | 60 | Percent of the chest taken. |
| `raiders_cut_percent` | track 0-50 | 15 | Raiders' share into savings. |
| `raiders_goodwill_loot` | track 0-300 | 60 | Goodwill lost with the robbed faction. |
| `raiders_goodwill_betrayal` | track 0-300 | 100 | Extra loss for robbing a friendly faction's camp. |
| `raiders_goodwill_daily_cap` | track 0-1000 | 150 | Per-faction daily loss cap. |
| `raiders_auto_recall` | check | false | Recall raiders automatically when the camp is raided. |
| `raiders_max_per_day` | track 1-10 | 3 | Missions per camp per day. |

Each key needs: the defaults table (`sb` ~690), key -> path map (~870), `mcm` group, and localization in the usual places (see the Living Needs MCM list in `living_needs.md` for the exact pattern).

## 11. Save/load safety

- Camp-level only: `camp.raider_missions` (the shared record of 5.1), `camp.raider_state` (per-faction goodwill spent today, last mission day). Per-survivor: `survivor.raider = { rest_until, missions_done, kills }`. All plain numbers/strings/tables, no engine objects (ids only). nil = "never raided", so old saves load unchanged; `normalize_camps` (`sb` 3987) fills defaults.
- No `SAVE_STATE_VERSION` bump unless a migration step is added.
- Mission state is derived from game seconds, not `time_global()`, so a sleep/load keeps it; resolution on load runs at most one mission per camp per tick (avoid a pile-up like the sleep catch-up problem in Living Needs).
- Raider NPCs that are teleported away during a mission can be lost across a save/load (the same hazard `restore_missing_settler` handles for expeditions). The mission record is the source of truth, and `verify_and_heal_settlers` (`sb` ~5800) must finish a mission or a recall after a load.
- Turning `raiders_enabled` off: missions in flight are cancelled and raiders recalled at the next tick; no data is deleted.
- The rival camp mutation (`mark_rival_garrison_eliminated`) is already save-safe; the new code only calls it.
- Uninstalling the mod leaves unknown fields as inert tables.

## 12. Performance

- One `process_raider_missions` tick per camp, a few table ops per active mission; hung off an existing slot of `actor_on_update` (no new timer), at most one resolution per tick.
- Target ranking is computed on demand (button press) or at most once per game hour in auto mode, over `sb.rival_camps` (tens, not thousands); distance uses precomputed positions.
- No per-frame scans, no `level.object_by_id` loops on unloaded levels (uses `alife_object` / the cached snapshot like the other jobs).
- Goodwill math is O(factions) once per resolved mission.

## 13. Feasibility (X-Ray Lua)

| Piece | Verdict | Why |
|---|---|---|
| New job + MCM + PDA label | Easy | Jobs are strings; counted in `get_camp_stats`; the pattern is copied from other jobs. |
| Abstract mission (Resolver A), odds, loot, goodwill | Easy-medium | Copies expeditions; pure functions are unit-testable. Risk is the number balance, not the code. |
| Goodwill via `change_community_goodwill` | Easy | Already used (`events` 520). |
| Calling `mark_rival_garrison_eliminated` from a raid | Medium | It assumes the rival squad and chest exist; need a nil `actor` path and care that the garrison squad is released from the sim (`rivals` 1233-1273 deletes camps whose chest is gone). Needs read-through before use. |
| Teleport raiders away / back | Medium | `teleport_scavenger_on_departure` and `restore_missing_settler` already do it; mission lifecycle after load is the risk. |
| Reinforce during a raid (abstract recall) | Medium | Spawn/appear at camp is fine; the raid only exists while the player is there. |
| Real assault with the player present (phase 4, shared record) | Hard | Squad AI control (`scripted_target`), companion-squad collisions, garrison judgment races; cannot be verified without play-testing. |
| PDA hooks (section 9) | Easy-medium | One button per tab and text in existing labels; the four theme XML copies must stay in sync. |

## 14. Risks

| Risk | Mitigation |
|---|---|
| Raiders strip every rival camp, killing the "there's something to find" loop | Per-day and per-target cooldowns, loot fraction, default OFF |
| Retaliation squads flood the player after a successful raid | Show it in the confirm panel; `rival_camp_retaliation_raids` already has its own MCM switch; add a raider-specific damper (retaliation delay x2) |
| Goodwill spiral to hostile factions | Daily cap, "spare friends" default on, bandit mode opt-in |
| Settlers die for nothing | Odds shown first, rank gate, `raiders_death_chance` tunable, recall always available |
| Camp left defenceless when raiders leave | `raiders_min_guards`, no mission starts while a raid is active, away raiders do not count as guards |
| Balance wrong without playtest | Phase 1 numbers conservative; each phase ends with an in-game checklist |
| Lua 200-local / 60-upvalue limits | Own script file; `tools/check_lua.ps1` |
| Mission lost across load | Mission record on camp; `verify_and_heal_settlers` completes/recalls |
| Raiding a story/quest camp | Filtered by `squad_has_story_npc` |

## 15. Phased plan

Each phase ships behind `raiders_enabled` (default off) and can be checked without launching the game via Lua 5.1 unit tests and `tools/check_lua.ps1`. Player-directed sends only throughout.

0. **Audit (no behavior change).** Confirm: (a) reading chest contents on an unloaded rival chest; (b) what `mark_rival_garrison_eliminated` needs with a nil actor and an unloaded squad; (c) how rival chest loot is generated, to pick a synthetic-haul table; (d) the survivor "available" checks (`on_expedition`); (e) teleporting a band away and back. Findings appended here.
1. **Pure raider engine.** New `stalker_camp_builder_raiders.script`: `raid_odds`, `raid_outcome`, `loot_split`, `goodwill_plan`, mission-record helpers (pure); tests in `tools/tests/test_raiders.lua`; not wired.
2. **Job + abstract mission (Resolver A).** Job `raider`, dispatch and resolve, wounded state, loot to storage, savings cut, weapon/armor toggle, goodwill wrapper, MCM group, tips and radio. Dispatch by a temporary Job-page action until phase 3.
3. **PDA hooks (section 9).** Job button, roster state, summary banner, Outposts "Send raiders" with confirm, Overview line and Recall button, in all four theme XML copies. Abstract recall and optional auto-recall come with it.
4. **Real assault (Resolver B).** The shared mission record switches to real when the player is on the level; behind `raiders_real_assault` (default off); abstract fallback on level leave or timeout.
5. **Bandit mode** (reduced penalties, bandit/renegade reputation, richer loot) and a balance pass from play-test numbers.

Nothing can be play-tested from here; every phase ends with a short in-game checklist for the owner.

## 16. Open questions (answered by the owner, see Decisions)

1. Capture scope: answered, clear and loot only.
2. Target picking: answered, player-directed only.
3. Abstract vs visible: answered, both, one shared mission record.
4. Goodwill cases: answered, both.
5. Goodwill numbers: answered, keep -60 / -100 / 150.
6. Bandit mode: answered, no faction change.
7. Idle raider at home: answered, half a guard.
8. Rank gate: answered, rank 2+, one guard stays.
9. Death risk: answered, wounded on failure, death only on disaster.
10. Loot: answered, keep 60/15/bounty; weapon/armor toggle added.
11. Retaliation: answered, existing timers.
12. Reinforcement: answered, recall button and optional auto-recall, abstract teleport-back.
13. Other targets: defaulted, no nests, story camps or own settlements.
14. PDA order: answered, hooks designed now (section 9).
15. Localization: defaulted, English now, Russian carries English.

New questions raised by the answers:
- N1. Wounded duration: is 12 game hours right?
- N2. Disaster outcome: 50% permanent death per raider, survivors wounded. OK?
- N3. Real assault: only when the player is within about 300 m of the camp, or whenever the player is on the level?
- N4. Should the Survivors and Outposts redesign sessions be told now about the reserved PDA places?

## 17. X-Ray Lua review (anomaly-modding checklist)

Added after loading the `anomaly-modding` skill. Labels: verified (read in this repo), inference (follows from the rules, untested), unknown (needs runtime proof).

- **Lifecycle** (verified pattern, inference for new code): register the new script's callbacks in `on_game_start` only; world-touching init (rival-camp lookup, mission resume) waits for `actor_on_first_update` or the existing `verify_and_heal_settlers` path. The mission tick hangs off an existing `actor_on_update` slot and is budgeted to one resolution per tick.
- **Save/load** (verified for `active_camps`, inference for the new fields): mission, cooldown and goodwill-cap fields hold plain numbers, strings and id lists only; no server objects or closures. Every stored object id (raider ids, target camp key, chest id) is revalidated on load and the mission is cancelled or finished deterministically if the target camp, chest or NPC is gone. Runtime caches (target ranking, odds) are rebuilt, not saved. Timers use game seconds, not `time_global()`, because `time_global()` and `CreateTimeEvent` do not survive load.
- **Delayed calls** (inference): the recall delay and any teleport-back must not rely on a `CreateTimeEvent` surviving a load; `respawn_settler` already handles this by keeping the record on the camp (`sb` ~5805). Raider recall copies that.
- **MCM** (verified pattern in `mcm`): options are read at runtime through the `cfg` map, never inside `on_mcm_load`; new keys need defaults, path map, MCM group and localization, as listed in section 10. `ui_mcm` stays optional.
- **Unknowns to resolve in Phase 0 (and for the real-assault phase: squad control via `scripted_target` and the mission/level-leave race are unknown until play-tested):** whether `mark_rival_garrison_eliminated` is safe with a nil actor and an unloaded squad; whether a rival chest can be read or edited while offline; whether `change_community_goodwill` is clamped by the engine (the existing raid reputation relies on it); whether teleporting a settler off-level and back leaves a stale `settler_lookup` entry (expeditions suggest not, not proven for a band).
- **Validation for the later code:** `luac -p`, `luac -l -l` to confirm every function stays under 200 locals (a reason for the separate file), unit tests in `tools/tests`, then the in-game checks: fresh start, first update, save and reload mid-mission, level transition during a mission, toggle off during a mission.
