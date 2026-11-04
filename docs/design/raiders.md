# Raiders: design (not implemented)

Status: DRAFT for user approval. No feature code exists. Internal doc, not README content.
Origin: suggestion from Discord user Wx (raiders attack and capture/loot camps that are not the player's, and can be sent to reinforce the player's settlements under attack), plus the owner's Goodwill idea (losing or looting a chest friendly to a faction costs goodwill with that faction; bandit-style play).
Cites are from `main` at b385d08 and will drift. Paths: `00_Core/gamedata/scripts/`, abbreviated `sb` (stalker_camp_builder), `jobs`, `events`, `rivals`, `exp` (expeditions), `prosper`, `needs`, `pda`, `mcm`.
Nothing here was run in game; "feasible" below means "reads as feasible from the code", not "tested".

Goal: the player does not care which faction robs someone else's outpost, so hand that chore to a settler job. A Raider is a survivor job that takes a rival outpost (or hits one for loot), brings the haul home, and can be recalled to help defend the player's own camp. The Goodwill rules make "who you rob" a real choice, and give bandit-style players a path where robbing is the point.

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

Requirements to take the job (all checked when assigning and again before each dispatch):
- settler is not wounded, not on another expedition, has a weapon and ammo in inventory (reuses `survivor_se` checks used by scavengers);
- minimum rank (default: Experienced / rank 2 of the prosper ranks), so day-one settlers cannot raid;
- the camp keeps at least `raiders_min_guards` guards at home (default 1 per 3 settlers, floor 1).

A raider away from home does not count as a guard in `stats.defense`. A raider at home with no mission counts as a half guard (default; see open question 7).

Group size: one raider on a mission is a lone-wolf run (small loot, high risk). A band is formed when 2 to 4 raiders are free at once (default `raiders_band_size = 3`); odds and loot scale with the band. Phase 1 may ship lone-wolf only.

## 4. Target selection

Candidates are the rival camps in `sb.rival_camps` that are occupied (`camp.status == nil`, `camp.faction` set and not monster/zombied) and not currently targeted by another raid band. Never targeted:
- the player's own camps, and camps friendly to the player when `raiders_spare_friends` is on (default on, see section 7);
- camps inside the player's settlement boundary (`in_player_settlement`, `rivals` 55);
- camps with a story NPC in the garrison (`squad_has_story_npc`, `rivals` 731);
- mutant nests and zombified camps (these are a PvE job, maybe phase 4);
- camps whose level the player has barred through an MCM list (phase 3).

Ranking: score = expected loot (camp tier x chest content estimate) / (garrison strength x travel time), with a faction filter. The player chooses the filter per camp:

| Mode | Raiders go for | Default |
|---|---|---|
| Hostile only | factions at relation <= -500 (or `is_factions_enemies`) with the player | **yes** |
| Neutral and hostile | anything not friendly | no |
| Anyone | includes friends (bandit mode) | no, requires `raiders_bandit_mode` |
| Player pick | one rival camp chosen from the Outposts tab ("Raid this camp") | always available when the job is on |

The Outposts tab already lists rival camps (map spots, `show_rival_camp_map_spots`); a "Send raiders" button on the selected card is the player-directed path. Auto mode picks the best target on a timer.

## 5. Travel, combat, capture (three resolution levels)

### Level A: abstract timer (phase 1, the default)

Copy the expedition shape. A `raider_mission` record sits on the camp (not on the NPC, so it survives NPC re-creation, see `restore_missing_settler`):

```
camp.raider_missions[mission_id] = {
  target_key, target_level, faction, raider_ids = {...},
  start_sec, duration, state = "away" | "returning" | "done",
  odds_snapshot, loot_rolled = false
}
```

1. Dispatch: raiders are teleported off like `teleport_scavenger_on_departure` (`exp` 1238) so no NPC is left half-walking on a level the player is not on. They are marked `on_expedition`-like (`surv.on_mission = mission_id`) so the existing "not available" checks apply.
2. Duration: based on distance between camp and target (game-graph distance, as `get_self_contained_distance` already does in `exp` 608) and a flat 30 game-minute assault window. Capped, like expeditions.
3. Resolution at the end of the timer, in a pure function `raid_outcome(band, target, rng)`:
   - attacker strength = sum of per-raider strength (rank, weapon tier, armor tier), times a mission modifier (night, familiarity);
   - defender strength = garrison size x tier factor, plus the camp's defenses (turrets/decor are rival "defenses", `spawn_rival_camp_defenses_and_decor`);
   - win chance = a logistic of the ratio, clamped 5%-90%, shown to the player as odds before sending;
   - outcomes: **Success** (garrison beaten), **Repulsed** (raiders flee, some wounded), **Disaster** (raiders killed).
4. Casualties per raider on non-success: death probability `raiders_death_chance` (default 25% on Repulsed, 60% on Disaster for each member; a lone-wolf is not safer). Dead raiders are removed through the same path as a killed settler (so `settler_lookup`, relations and the "settler killed" bookkeeping stay consistent).
5. Real-world effect: on Success the rival camp's garrison is removed by calling the existing `mark_rival_garrison_eliminated` (`rivals` 1201) with `actor = nil`; this means the existing machinery handles map spots, ruins decay, "cleared" flag and, importantly, `faction_retaliation_timers`. Retaliation is therefore automatic if the faction hates the player. That coupling is intentional and has to be visible in the PDA (section 9).

Level A is level-independent and works offline (the same reason expeditions do). It is also the only level that cannot visibly "do" anything, which is why Level B exists.

### Level B: real assault when the player is on the level (phase 3, optional)

If the player is on the target's level and within about 300 m when a mission would resolve, the band is spawned as a real squad (reuse `create_squad_at_pos`, `rivals` 470) near the camp and pointed at it with `scripted_target`, the way raids point at the actor. The existing garrison logic (garrison alive checks, `resolve_pending_rival_skirmish`, `rivals` 1109) judges the result. This is the same code path that makes a player fight; no new combat rules, but also the highest risk of AI weirdness (squads that wander, companion-squad id collisions seen in `end_camp_raid`, the "only one raid at a time" rule). Treat as a stretch goal.

### Level C: capture and hold (phase 4, optional)

The rival camp becomes a Homestead "outpost" owned by the player: a small record in `camp.outposts` (position, level, faction theme, chest id, garrison = raiders left behind). It would need ownership, defense, upkeep, and a raid-back model. This is large. Phase 1-3 deliberately avoid it: "capture" means eliminating the garrison and taking the chest contents, leaving the camp in the existing "unoccupied/cleared" state. See open question 3.

## 6. Loot rules

- Loot comes from the target's chest (`camp.chest_id`) and what Level A rolls from its tier, not from the player's boxes. At resolution on Success: take a fraction of the chest, `raiders_loot_fraction` default 60% of items by count (a weighted pick favoring ammo, meds, food, then weapons), and the rest stays for the player to find. Rationale: the player can still do the outpost themselves and sees a believable leftover.
- If the chest is not loaded (other level), roll a synthetic haul from the tier loot tables already in `rivals` (~2487-2520 initial loot lists, 944 resupply list), the way `generate_gamma_stash_loot` (`exp` 755) synthesizes stash loot. No item is removed from an unloaded object (avoids server-object edits; Phase 0 must confirm `camp_consume_item` offline works, as needs did).
- Split: the camp keeps the haul (deposited like `deposit_expedition_haul`, `exp` 1719, into settlement storage only, never personal boxes, honoring `is_settlement_storage`). Raiders keep a cut in rubles into their savings via `prosper_credit` (default 15% of haul value, ties into the existing "cut per cycle" economy; a Starving camp pays none, matching `needs`).
- Money: rival chests do not hold cash today, so cash is a flat bounty by tier (default 500/1500/3000 for tiers 1-3, scaled by an MCM multiplier).
- Weight/space: if the settlement has no room (existing storage-full pause), the mission still resolves but the surplus is dropped to a "loot pile" (a stash at the camp) rather than lost; Phase 1 may simply pause dispatch when storage is nearly full.
- Cooldowns: a raider returns, rests `raiders_rest_hours` (default 6 game hours) before the next mission, and a given target camp cannot be raided again for `raiders_target_cooldown_hours` (default 24; on top, rival camps already respawn/decay on their own timers).
- Anti-exploit: loot value per mission is capped, per-day missions are capped (`raiders_max_per_day`, default 3 per camp), and a cleared camp yields nothing on a second visit.

## 7. Goodwill and the bandit option

All numbers are MCM-tunable. Goodwill uses `relation_registry.change_community_goodwill(faction, actor:id(), delta)` through one wrapper in the new script (the raid-reputation code, `events` 491, already shows the pattern including the faction filter and the "skip non-factions" list; the wrapper should reuse it, not copy it).

Who is hit when a raider (or the player) robs a camp:

| Event | Goodwill change |
|---|---|
| A raider band takes down a camp of faction F | F: `-raiders_goodwill_loot` (default -60 per camp). F's allies (friends of F, from `game_relations`): half. F's enemies: `+raiders_goodwill_enemy_bonus` (default +15, off by default; optional). |
| A raider loots a chest friendly to F (a camp where F has goodwill > 0 with the player) | F: -100 extra "betrayal" penalty. This is the owner's idea: robbing someone who likes you is worse than robbing an enemy. |
| The player loots a rival chest of a friendly faction manually | Same as above if `raiders_player_loot_goodwill` is on (default off, because the base game's own rules apply to that). |
| A raider dies in a mission | no goodwill effect; pure settler loss |
| Player recalls a mission before resolution | none |

Hard caps per faction per day (default 150) so one bad dispatch cannot burn a faction permanently. Goodwill in X-Ray is a bounded integer (communities range is roughly +-5000; kill-driven changes elsewhere use hundreds), so numbers here are intentionally of the same order as `raid_rep_per_settler = 25`; values are placeholders until playtest (open question 5).

The owner's wording "loses/loots a chest friendly to a faction" has two readings: (a) a *rival outpost chest* owned by a faction friendly to the player (covered above), (b) one of the player's own storage chests being looted by a raiding faction. (b) is already partly covered by raid reputation. Do not mix them. See open question 4.

### Bandit-style play option

`raiders_bandit_mode` (default off). When on:
- target filter "Anyone" is allowed, friendly camps included;
- goodwill loss with robbed factions is reduced (default x0.5) and a new self-sustaining stream appears: extra loot +25% and cash bounty x1.5 ("protection racket");
- gains reputation with bandit-aligned factions (bandit, renegade; list configurable in code, not MCM) per successful raid (default +20), so a player who plays a bandit grows a standing with them;
- raid reputation for lost settlers keeps working unchanged.
It does not change the player's own faction or relations; it only changes what raiders do and how it is priced. "Playing as a bandit" in the sense of changing the player's faction is already a base-game/GAMMA concern (`get_player_faction`, `sb` raid code reads it).

## 8. Reinforcement during attacks

The goal is: raiders away on a mission can be called back to help. Real teleport/return is where this gets difficult, so it is tiered.

1. Phase 2 (abstract): when the camp's `active_raid` starts (`spawn_camp_raid`), any raider with `state = "away"` for a Level A mission is offered a recall on the PDA ("Recall raiders", visible while the camp is under raid), and optionally `raiders_auto_recall` (default off) recalls them. Recall = the same path as `recall_scavenger_expedition` (`exp` 152): mission cancelled, raiders appear at camp after a short delay (default 20 s real time), mission loot lost (no haul, no goodwill change). They then spawn as ordinary guards for the rest of the raid. Because raids only exist while the player is on the camp's level, the band can be placed straight at the camp without simulating travel.
2. Reserve raiders: raiders at home count as half guards in `stats.defense` before the raid, so they lower raid chance as they do now for guards.
3. Phase 3 (real): while the player is on the level, raiders can run to the fight from a nearby field operation (Level B). Only worthwhile after Level B exists.
4. Reverse direction (very optional, phase 5): settler band joins a *rival* camp the player is helping (cf. `trigger_allied_reinforcement`, `rivals` 3164) so the player's raiders can be recruited to an SOS.

Edge cases to handle: the camp is on another level when the mission starts (raids never happen there, so no recall UI); the raider died during the mission (nothing to recall); the player leaves the level during recall (raid ends, `end_camp_raid` already cleans squad targets, the recalled raiders simply stay home).

## 9. PDA surface

- Survivors tab: Job page gets "Raider" (hidden when `raiders_enabled` is off). Summary banner line shows the mission state ("On mission: Rostok Outpost, back in 2h" / "Resting"); the existing "Waiting:" reason line gets new reasons (no weapon, no ammo, rank too low, camp needs guards). The Survivors tab uses a fixed layout (`docs/design/pda_survivors/`), so use the existing summary banner and reason line; no new widgets.
- Outposts tab: on a rival outpost card, a "Send raiders" button (visible when at least one raider is free) opening a small confirm: odds, estimated loot, expected goodwill cost, "retaliation likely". The card shows "Raid in progress" and the mission countdown, and reuses the existing map-spot flow. Needs a layout check with the Outposts redesign (`docs/design/pda_outposts/`), which is a sibling work item.
- Overview tab: one line "Raiders: 2 away, 1 resting; last haul 18 items" near the raid banner, hidden when none.
- Radio feed (`add_radio_feed_entry`) and tips: mission start, result, casualties, goodwill losses ("Wolf's band robbed Duty; Duty did not like that").
- All strings ASCII in eng XML, translated via `translate_string`; Russian entries can carry English text until translated (as the "move on" strings did).

## 10. MCM options (new "Raiders" group)

| Key | Type | Default | Purpose |
|---|---|---|---|
| `raiders_enabled` | check | **false** | Master toggle; off = job hidden, no missions, no goodwill code runs. |
| `raiders_auto_mode` | check | false | Auto-pick targets on a timer instead of only player-directed sends. |
| `raiders_target_filter` | list | hostile only | hostile / non-friendly / anyone. |
| `raiders_bandit_mode` | check | false | Section 7 bandit-style rules. |
| `raiders_spare_friends` | check | true | Never target factions friendly to the player (ignored in bandit mode). |
| `raiders_min_rank` | track 0-4 | 2 | Minimum prosper rank. |
| `raiders_band_size` | track 1-4 | 3 | Raiders per mission. |
| `raiders_min_guards` | track 0-4 | 1 | Guards that must stay home. |
| `raiders_death_chance` | track 0-100 | 25 | Per-raider death chance on Repulsed (x2.4 on Disaster). |
| `raiders_loot_fraction` | track 10-100 | 60 | Percent of the chest taken. |
| `raiders_cut_percent` | track 0-50 | 15 | Raiders' share into savings. |
| `raiders_goodwill_loot` | track 0-300 | 60 | Goodwill lost with the robbed faction. |
| `raiders_goodwill_betrayal` | track 0-300 | 100 | Extra loss for robbing a friendly faction's camp. |
| `raiders_goodwill_daily_cap` | track 0-1000 | 150 | Per-faction daily loss cap. |
| `raiders_auto_recall` | check | false | Recall raiders automatically when the camp is raided. |
| `raiders_max_per_day` | track 1-10 | 3 | Missions per camp per day. |

Each key needs: the defaults table (`sb` ~690), key -> path map (~870), `mcm` group, and localization in the usual places (see the Living Needs MCM list in `living_needs.md` for the exact pattern).

## 11. Save/load safety

- Camp-level only: `camp.raider_missions`, `camp.raider_state` (per-faction goodwill spent today, last mission day). Per-survivor: `survivor.raider = { rest_until, missions_done, kills }`. All plain numbers/strings/tables, no engine objects (ids only). nil = "never raided", so old saves load unchanged; `normalize_camps` (`sb` 3987) fills defaults.
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
| Abstract mission (Level A), odds, loot, goodwill | Easy-medium | Copies expeditions; pure functions are unit-testable. Risk is the number balance, not the code. |
| Goodwill via `change_community_goodwill` | Easy | Already used (`events` 520). |
| Calling `mark_rival_garrison_eliminated` from a raid | Medium | It assumes the rival squad and chest exist; need a nil `actor` path and care that the garrison squad is released from the sim (`rivals` 1233-1273 deletes camps whose chest is gone). Needs read-through before use. |
| Teleport raiders away / back | Medium | `teleport_scavenger_on_departure` and `restore_missing_settler` already do it; mission lifecycle after load is the risk. |
| Reinforce during a raid (abstract recall) | Medium | Spawn/appear at camp is fine; the raid only exists while the player is there. |
| Level B real assault with the player present | Hard | Squad AI control (`scripted_target`), companion-squad collisions, garrison judgment races; cannot be verified without play-testing. |
| Level C captured outposts | Hard | New ownership model, defense, upkeep, saving. A separate project. |
| Raid-back by rivals after capture | Hard | Depends on Level C. |
| Raiders tied to PDA Outposts redesign | Medium | Depends on the Outposts layout being final (sibling item). |

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

Each phase ships behind `raiders_enabled` (default off) and can be checked without launching the game via Lua 5.1 unit tests and `tools/check_lua.ps1`.

0. **Audit (no behavior change).** Confirm: (a) `camp_consume_item` / reading chest contents on an unloaded rival chest; (b) what `mark_rival_garrison_eliminated` needs when called without an actor and without a loaded squad; (c) how rival chest loot is generated, to choose a synthetic-haul table; (d) which survivor checks exist for "available" (on_expedition). Findings appended to this doc.
1. **Pure raider engine.** New `stalker_camp_builder_raiders.script`: `raid_odds`, `raid_outcome`, `loot_split`, `goodwill_plan` (pure), tests in `tools/tests/test_raiders.lua`; not wired. Verify: tests + `check_lua.ps1`.
2. **Job + abstract mission.** Job `raider`, mission dispatch/resolve (Level A), loot to storage, savings cut, goodwill wrapper, MCM group, radio/tips, no PDA beyond the job label and the existing reason line. Player-directed send only (a temporary "send" via the Job page). Verify: unit tests + in-game checklist (assign, send, wait, result, save/load mid-mission, toggle off).
3. **PDA Outposts "Send raiders" + Overview line**, odds/goodwill confirm, mission countdown on the card. Verify: XML well-formed, ASCII, every string id exists.
4. **Reinforcement (abstract recall)** + reserve raiders as half guards + `raiders_auto_recall`.
5. **Auto mode + bandit mode** (target ranking, filters, bandit reputation list).
6. **Stretch:** Level B real assault when the player is on the level.
7. **Separate project (not scheduled):** Level C captured outposts, raid-back, raiders garrisoning.

## 16. Open questions for the owner

1. Scope of "capture": is "eliminate the garrison and take the chest, camp becomes cleared" enough, or should a captured camp become a player-owned outpost (Level C, a separate large project)?
2. Who picks targets: player-directed only (send from the Outposts card), auto, or both? The doc proposes both, with auto off by default.
3. Should the Raider's mission be abstract (timer + odds, works anywhere, nothing visible) or visible (real fight when the player is nearby)? Doc proposes abstract first, visible as a stretch.
4. Goodwill: do you mean (a) robbing a rival outpost chest of a faction friendly to the player, (b) your own chest being looted by a faction, or both? The doc covers (a) and keeps (b) in the existing raid reputation.
5. Goodwill numbers: is -60 per robbed camp, -100 extra for a friendly faction, daily cap 150 right? Placeholder scale only (raid reputation uses 25 per settler, cap 100).
6. Bandit mode: just reduced penalties plus bandit/renegade reputation and richer loot, or should it also let the player change their own faction/relations?
7. Should an idle raider at home count as a half guard, a full guard, or nothing?
8. Rank gate: minimum rank 2 and at least one guard staying home. OK, or stricter/looser?
9. Death risk: 25% per raider on a failed raid (60% on a disaster). Too harsh for named settlers? Is a "wounded and back later" outcome preferred over death?
10. Loot: 60% of the chest, 15% cut to the raiders, flat cash bounty by tier. OK? Should the player be able to forbid weapons/armor loot?
11. Retaliation: a successful raid on a faction that hates the player uses the existing retaliation timers. Accept, or add a raider-only damper?
12. Reinforcement: recall button during a raid plus optional auto-recall (default off). Is that the reinforcement you meant, or do you want raiders to arrive from the field as real squads (hard)?
13. Should raiders ever target other settlements of the player (no), mutant nests (a PvE job, maybe later), or Zombified/story camps (no)?
14. Order versus the other designs: Raiders touches the PDA Outposts and Survivors work in flight. Land after that redesign, or design the UI hooks now?
15. Localization: English now with Russian carrying English text until translated (as for "move on")?

## 17. X-Ray Lua review (anomaly-modding checklist)

Added after loading the `anomaly-modding` skill. Labels: verified (read in this repo), inference (follows from the rules, untested), unknown (needs runtime proof).

- **Lifecycle** (verified pattern, inference for new code): register the new script's callbacks in `on_game_start` only; world-touching init (rival-camp lookup, mission resume) waits for `actor_on_first_update` or the existing `verify_and_heal_settlers` path. The mission tick hangs off an existing `actor_on_update` slot and is budgeted to one resolution per tick.
- **Save/load** (verified for `active_camps`, inference for the new fields): mission, cooldown and goodwill-cap fields hold plain numbers, strings and id lists only; no server objects or closures. Every stored object id (raider ids, target camp key, chest id) is revalidated on load and the mission is cancelled or finished deterministically if the target camp, chest or NPC is gone. Runtime caches (target ranking, odds) are rebuilt, not saved. Timers use game seconds, not `time_global()`, because `time_global()` and `CreateTimeEvent` do not survive load.
- **Delayed calls** (inference): the recall delay and any teleport-back must not rely on a `CreateTimeEvent` surviving a load; `respawn_settler` already handles this by keeping the record on the camp (`sb` ~5805). Raider recall copies that.
- **MCM** (verified pattern in `mcm`): options are read at runtime through the `cfg` map, never inside `on_mcm_load`; new keys need defaults, path map, MCM group and localization, as listed in section 10. `ui_mcm` stays optional.
- **Unknowns to resolve in Phase 0:** whether `mark_rival_garrison_eliminated` is safe with a nil actor and an unloaded squad; whether a rival chest can be read or edited while offline; whether `change_community_goodwill` is clamped by the engine (the existing raid reputation relies on it); whether teleporting a settler off-level and back leaves a stale `settler_lookup` entry (expeditions suggest not, not proven for a band).
- **Validation for the later code:** `luac -p`, `luac -l -l` to confirm every function stays under 200 locals (a reason for the separate file), unit tests in `tools/tests`, then the in-game checks: fresh start, first update, save and reload mid-mission, level transition during a mission, toggle off during a mission.
