<div align="center">

<sub>S.T.A.L.K.E.R. ANOMALY / G.A.M.M.A.</sub>

# HOMESTEAD
### STALKER SETTLEMENT BUILDER

*Build camps. Recruit survivors. Automate production. Hold the line.*

![Version](https://img.shields.io/badge/version-v1.3.4-e0a43c?style=for-the-badge) ![Author](https://img.shields.io/badge/by-Damage__Zedd-8fae5a?style=for-the-badge) ![Game](https://img.shields.io/badge/S.T.A.L.K.E.R.-Anomaly%201.5.3-555555?style=for-the-badge)

**[GAMMA Discord Thread](https://discord.com/channels/912320241713958912/1515669053606334504/1542893750408315030)** · **[Full Changelog](CHANGELOG.md)** · **[ModDB](https://www.moddb.com/mods/stalker-anomaly/addons/homestead-stalker-settlement-builder)** · **[Latest Release](https://github.com/DamageZedd/Homestead-Stalker-Settlement-Builder/releases/latest)**

</div>

> ⚠️ **FULL RELEASE – PLEASE READ**
> Homestead is a very large project and bugs are expected. Please report any issues you encounter so they can be fixed in future updates. Back up your saves before updating.

Homestead is a comprehensive settlement management and tactical camp-building mod for S.T.A.L.K.E.R. Anomaly. Build functioning camps, recruit survivors, automate production, repel hostile raids, and watch the Zone come alive as rival factions fight over territory around you.

Plant a Settlement Flag to establish a 50-meter settlement boundary. Construct beds, stoves, stashes, defensive barricades, water pumps, alarm sirens, automated pistol turrets, power generators, and decorative furniture. Recruit stalkers or shelter refugees, assign them specialized jobs, manage morale and resources, and control everything remotely through a full 5-tab PDA interface and extensive MCM.

---

## 🆕 New in v1.3.4

### 💰 Settler Savings, Spending & Standing
Working settlers earn a cut that builds as savings, spend it on gear for their faction, and rise in rank and reputation. Overflow pays the cut instead of pausing jobs. Options are in MCM.

### 🚶 Settlers Who Move On (off by default)
A settler who has done well can move on and rejoin their faction as a veteran. Script callbacks and a faction provider hook let other mods, such as Factions of the Zone, plug in.

### 🏴 Rival Camps
The spawn-distance, interval and chance sliders now work as described.

### 🛠️ Fixes
A large bug-fix pass across jobs, settlers, expeditions, turrets, the lock, trader pricing and the PDA, plus a fix for a start-up crash on GAMMA. See the changelog.


---

## 🔧 The Workstations

Every job has its own placeable workstation. Settlers walk to it, work at it and get bonuses from it.

<p align="center"><img src="docs/images/collage_workstations.jpg?v=1" alt="Crafting workstations" width="100%"></p>

<p align="center"><img src="docs/images/collage_services.jpg?v=1" alt="Production, food and care stations" width="100%"></p>

- **Moonshine Distiller**: Brewer
- **Ammunition Crafting Bench**: Crafter
- **Woodcutter Station**: Woodcutter
- **Electrician Generator Bench**: Electrician
- **Gunsmith & Armor Repair Bench**: Repairer / Scrapper
- **Hunter Butchering Station**: Hunter
- **Farmer Station** 🆕: Farmer
- **Market Stall** 🆕: Trader
- **Field Kitchen**: Cook · counts as a stove · 300 kg of food & drink storage
- **Field Infirmary**: Medic · 300 kg of medicine storage
- **Guard Post**: Guard · 300 kg of weapon, ammo & grenade storage
- **Salvage Table**: Scavenger · 300 kg of tool, parts & salvage storage

### 💧 Water Purifier
A gravity-fed **water purifier** on a concrete pad: an intake pipe comes up out of the ground into a blue steel settling drum, a grey carbon canister and two filter cartridges, and clean water runs out of a valve spout into the vanilla bucket. Ground water is irradiated, so it needs cleaning. It counts as a settlement water pump, so with charcoal or paper filters in camp storage your settlers fill clean flasks of water every few hours. It is built from vanilla G.A.M.M.A. parts and textures (the valve wheel, the bucket, and metal, concrete and rust textures). Craft it at a workbench; it weighs 10 kg in your inventory.

### 🏴 Settlement Flag
A pole and banner that marks the ground as yours. Placing it founds a settlement and makes it the camp hub. Its banner shows your faction's patch and changes by itself if your faction does; a custom faction from Factions of the Zone shows its own emblem. It is also the camp's main storage (300 kg). Picking it up dismantles the settlement.

<p align="center"><img src="docs/images/hero_settlement_flag_factions.jpg?v=2" alt="Settlement Flag faction banners"><br><sub>Loners · Duty · Freedom · Clear Sky · Ecologists · Military<br>Bandits · Renegades · Mercenaries · Monolith · Sin · ISG</sub></p>

### 📦 Settlement Storage
Themed boxes for the settlement's own stock. Settlers and Auto-Sort put each kind of item in its own box first, and settlers take what they need from them.

<p align="center"><img src="docs/images/collage_storage.jpg?v=1" alt="Settlement storage, guard post and flag" width="100%"></p>

- **Armory Crate**: weapons, ammunition & grenades · 250 kg
- **Quartermaster Locker**: suits, armour, helmets & gas masks · 250 kg
- **Med Crate**: medkits, bandages, drugs & anti-rad · 100 kg
- **Pantry**: food & drink that keeps (after the fridges) · 200 kg
- **Supply Crate**: parts, tools, materials & everything else · 300 kg

---

## 📟 PDA Settlement Manager

Full 5-tab tactical interface accessible from anywhere in the Zone. The top status bar shows a live military clock, weather, RF signal strength, and the active settlement.

**Tab 1 — Settlements Overview.** Live population, defense rating, morale, food, water, and storage. 8-button operations grid: Fast Travel, Summon Caravan, Auto-Sort Stash, Set Specialization, Recall Settlers, Rename, Transfer Resources, Dismantle.

![Settlements Overview](https://media.moddb.com/images/members/5/4662/4661404/profile/ss_player_09-03-26_22-16-37_l03.png)

**Tab 2 — Settlers Roster & Dossier.** Scrollable survivor cards with portraits, rank, experience, and real-time job progress. Job assignment and per-job directives (Medic, Crafter, Woodcutter, Farmer). Field commands: Anchor Position, Recall, Rename, Transfer Between Settlements.

![Settlers Roster](https://media.moddb.com/images/members/5/4662/4661404/profile/ss_player_09-03-26_22-16-44_l03.png)

**Tab 3 — Rival Wilderness Camps.** Real landscape photos for 21 Zone levels. Dynamic threat banners (HOSTILE / ABANDONED / ALLIED / MUTANT NEST). Tactical recon: faction, garrison strength, tier, estimated loot.

![Rival Wilderness Camps](https://media.moddb.com/images/members/5/4662/4661404/profile/ss_player_09-03-26_22-16-47_l03.png)

**Tab 4 — Settlement Radio Transceiver.** Real-time event log for expeditions, combat alerts, craft cycles, harvests, sales, medical treatments, and raid summaries. Category filters + Live Zone Scanner.

![Settlement Radio](https://media.moddb.com/images/members/5/4662/4661404/profile/ss_player_09-03-26_22-16-50_l03.png)

**Tab 5 — Field Survival Guide.** Illustrated operational directives covering every mechanic, including every job. Full English & Russian localization.

![Field Survival Guide](https://media.moddb.com/images/members/5/4662/4661404/profile/ss_player_09-03-26_22-16-52_l03.png)

---

## 👷 Settlement Jobs

14 jobs, all intervals configurable in MCM. Job progress persists across levels, fast travel, and sleep. Settlers keep working while you're away.

| Job | What it does | Workstation |
|---|---|---|
| **Guard** | Patrols, boosts Defense Rating, mans sentry posts, radio callouts | Guard Post |
| **Scavenger** | Zone-wide stash expeditions with live tracking and loot receipts | Salvage Table |
| **Crafter** | Ammunition and turret supplies | Ammunition Crafting Bench |
| **Repairer** | Weapons, armor, and passive storage repairs | Gunsmith & Armor Repair Bench |
| **Cook** | Processes meat, produces food, grants 4-hour hospitality buffs | Field Kitchen |
| **Medic** | Medical supplies, field healing and radiation treatment | Field Infirmary |
| **Electrician** | Power grid, night lights, turret overcharge, battery charging | Electrician Generator Bench |
| **Woodcutter** | Firewood and charcoal | Woodcutter Station |
| **Brewer** | Distills vodka, uses potatoes first | Moonshine Distiller |
| **Scrapper** | Salvages scrap and hardware | — |
| **Hunter** | Butchers and tans mutant carcasses | Hunter Butchering Station |
| **Farmer** 🆕 | Potatoes, grain and bread | Farmer Station |
| **Trader** 🆕 | Sells your goods for RU | Market Stall |
| **Idle** | Available for reassignment or dispatch | — |

---

## 🏕️ Settlement Building

- Deployable Camp Hub: the Settlement Flag
- 50m territory boundary with visual placement feedback
- 100m minimum distance between settlements (failed placements refund items)
- Placeable structures: beds, stoves, stashes, fridges, sandbags, metal barricades, wooden walls, water pumps, generators, alarm sirens, automated pistol turrets, display counters, decorative furniture, and the HomesteadHF workstations
- Secondary workbenches can be placed inside existing settlements

### 🧱 Building Kit & Snapping
Build real houses, Fallout 4 style. The new HomesteadHF building pieces and the Hideout Furniture walls snap to each other on one grid, and furniture snaps onto floors and flush against walls.

- **Pieces** (crafted at a workbench): foundations, floors, walls, a doorway, a support post, stairs, a ramp and tin roofs, in square and triangular shapes (listed below). Walls, half walls and doorways come from *Even More Hideout Furnitures*.
- **Grid**: one tile is 4.71 m (the width of a Hideout Furniture wall); one storey is a wall plus a floor. Stairs climb exactly one storey over 3.2 m (head at the tile edge, foot inset so a wall can stand in front of it), and a sloped roof rises one storey over one tile.
- **Controls while placing**: aim at a placed piece and the preview snaps to it. **R** rotates 90° (to the next snap position when snapped), **G** turns snapping on or off. Both keys can be changed in MCM → Homestead → Building, along with the snap radius and the furniture grid.

<p align="center"><img src="docs/images/collage_walls.jpg?v=1" alt="Walls, doorways and support post" width="100%"></p>
<p align="center"><img src="docs/images/collage_floors.jpg?v=1" alt="Foundations and floors" width="100%"></p>
<p align="center"><img src="docs/images/collage_stairs.jpg?v=1" alt="Stairs and ramp" width="100%"></p>
<p align="center"><img src="docs/images/collage_roofs.jpg?v=1" alt="Tin roofs" width="100%"></p>

- **Concrete foundation**: sinks into slopes; levels itself to the ground. Plank floor: on a foundation or on top of walls.
- **Plank wall with window**: matches the Hideout Furniture wall. **Gable wall**: closes the open end under a sloped roof.
- **Wooden stairs**: one storey in 3.2 m. **Sloped tin roof**: 30°, one storey over one tile. Flat, outer-corner (hip), inner-corner (valley) and pyramid roofs complete the set.
- **Low plank wall**: a waist-high wall with a capping rail; nothing stacks on top of it.
- **Plank wall with loophole**: a full-height wall with a narrow firing slit.
- **Wide plank doorway**: a wall with a wide double-door opening and a lintel.
- **Wooden support post**: a square timber post that snaps to floor and foundation corners and holds up the storey above.
- **Triangular foundation / triangular plank floor / triangular tin roof**: half a tile cut along the diagonal; snap in any of four orientations or against a matching triangle to complete a full tile.
- **Plank entry steps**: three wide steps up to the height of a foundation, snapped to its outside edge.
- **Plank ramp**: a long ramp that climbs one storey across a tile, open underneath.
- **L-shaped stairs** (and a **mirrored** version) and **U-shaped stairs**: open underneath, one storey inside one tile; press R to turn.
- **Spiral stairs**: treads winding round a central column, one storey inside one tile. **Plank floor with spiral opening**: the matching floor with a round opening and railing for the top.

- **Placement hologram**: while placing any Hideout Furniture or Homestead item you see a translucent copy of the model, green where it fits and red where it is blocked. It can be turned off in MCM → Homestead → Building.

<table>
<tr>
<td width="50%" align="center"><img src="docs/images/hologram_valid.jpg?v=1" alt="Placement hologram, green"><br><b>GREEN: IT FITS</b><br><sub>press F to place it</sub></td>
<td width="50%" align="center"><img src="docs/images/hologram_blocked.jpg?v=1" alt="Placement hologram, red"><br><b>RED: BLOCKED</b><br><sub>something is in the way, move it</sub></td>
</tr>
</table>

## 🧑‍🤝‍🧑 Survivors & Recruitment

- Recruit any friendly/neutral stalker via dialogue
- Dynamic refugee arrival events (free to recruit)
- Rank-gated recruitment with sign-on fees (**2,500–35,000 RU**) and defense requirements, fully configurable in MCM
- Skill tiers: Novice → Skilled (**1.5x**) → Expert (**2x**) → Master (**3x** production)
- Rename settlers and settlements
- Territory-safe assignment (blocks hostile zones and incompatible factions)

## 🔍 Scavenger Expeditions

- Single-stash or full regional sweep from the PDA map
- Realistic 5 km/h travel time with terrain compensation + pre-dispatch ETA
- Live progress %, ETA, and location tracking
- Mid-mission radio chatter at 25% / 50% / 75%
- Detailed loot receipts with White vs Yellow stash breakdown (full GAMMA compatibility)
- Emergency radio recall

## 🔧 Camp Technician & WPO

- Opens native Anomaly/GAMMA Repair & Upgrade GUI at your base
- Full Weapon Parts Overhaul support (body + all internal parts to 100%)
- Dynamic pricing by weapon class and condition; clears engine misfire/jam states
- Toolkit progression (Basic → Advanced → Expert) and a technician barter shop for spare parts

## 🩺 Settlement Medic & Triage

- Patch Wounds & Stop Bleeding: **1,850 RU** (full health, stamina, bleed, BHS limbs)
- Cure Radiation: **1,480 RU** (0 mSv)
- Complete Medical Overhaul: **3,350 RU**
- Medical supply barter + Drug-Making Kit upgrades; full GAMMA Body Health System compatibility

## ⚔️ Combat & Defense

- Dynamic faction-aware raids and mutant packs
- 1.5-day grace period for new settlements; raiders spawn 65m+ outside boundaries
- Automated pistol turrets (**+15 Defense** each)
- Alarm sirens with 75m threat radar (**+15 Defense**)
- Cumulative Defense Rating system and post-raid radio combat reports
- Empty settlements (0 settlers) are immune to raids

## 🏷️ Settlement Specializations

| Outpost | Farm | Workshop | Hideout | Clinic |
|:---:|:---:|:---:|:---:|:---:|
| +50% Defense | +50% Food & Water | +50% Crafting & Repair | +50% Scavenging | +100% Medical |

## ⚙️ Settlement Systems

- Dynamic morale (food, water, sleep, furniture, power, events)
- Water pumps produce Clean Water Flasks every 6 hours; refrigerators restore +25% food freshness every 12 hours
- Power grid: night streetlights, +15 morale, turret overcharge
- Cook hospitality feasts (4-hour buffs)
- 1-Click Smart Auto-Sort; camp-to-camp resource transfer + automated trade routes
- Renown perks (Master of the Forge, Haven of the Zone, Warlord of the Wastes, Fortress Architect)

## 🌍 Dynamic Living Zone

Rival camps progress through three tiers and react to the world:

- Post-emission scrambles, retaliatory expeditions that set up new camps after a defeat, supply convoys
- Psy-zombification and mutant nest conversions
- Territorial turf wars and SOS distress signals
- Friendly camp hospitality buffs
- Story-aware Monolith boundaries + day/night circadian spawning

Loot or dismantle (**Shift+F**) rival camp chests. Dynamic HUD prompts show chest state.

## 🚀 Fast Travel & Caravans

Campfire fast travel between settlements (blocked during Blowouts, Psi-Storms, and combat). Summon trade caravans to your base. Automated recurring trade routes.

## 🤖 Settler AI

Native companion BEH scheme with 100% anti-wander guarantee. Settlers stay at workstations and only leave for combat. Instant "Send Here" teleport via PDA or dialogue. Job-specific animations.

## 🎛️ MCM — 30+ Options

Survivor capacity, production timers for every job, Trader price percentage, scavenger risk, raid frequency/grace period, rival camp density, recruitment fees, dynamic world toggles, and debug tools.

---

## 📦 Required Mods

**MODDED EXEs** — and the following base systems:

1. **[Hideout Furniture Mod (Base) [Version 2.3.2]](https://www.moddb.com/mods/stalker-anomaly/addons/hideout-furniture-hf)** — core placement engine, workbenches, and stashes
2. **[Hideout Gadgets for Hideout Furniture [Version 0.7.2]](https://www.moddb.com/mods/stalker-anomaly/addons/hideout-gadgets-for-hideout-furniture-version-07)** — alarm systems, turrets, and defense rating integrations
3. **[Hideout Furniture Expansion [Version 1.0.2]](https://www.moddb.com/mods/stalker-anomaly/addons/hideout-furniture-expansion)** — stoves, beds, and furniture varieties
4. **[Even More Hideout Furniture [Version 2.2]](https://www.moddb.com/mods/stalker-anomaly/addons/even-more-hideout-furniture)** — fridges, pianos, radios, and expanded decor props

**Not required but recommended:** [Mod App Creator [MAC] 0.9.9.4](https://www.moddb.com/mods/stalker-anomaly/addons/mod-app-creator-mac) — moves the Settlement PDA tab to an app screen with [3D Interactive PDA](https://www.moddb.com/mods/stalker-anomaly/addons/3d-interactive-pda-18-release), [iTheon's PDA Taskboard](https://www.moddb.com/mods/stalker-anomaly/addons/itheons-pda-taskboard), [Fatal Error by Ncenka](https://www.moddb.com/mods/stalker-anomaly/addons/fatal-error-by-ncenka), PANDA Private Messages (to be released) and [Player Group Command](https://www.moddb.com/mods/stalker-anomaly/addons/player-group-command).

## 📥 Installation

1. Install all required mods.
2. Install Homestead using the included **FOMOD** installer.
3. **Mod Organizer 2** is strongly recommended.
4. Launch the game.
5. Read the in-game PDA guide before starting your first settlement.

### Load Order

```
1. Hideout Gadgets for Hideout Furniture (Original)
2. 470 - Gadgets for Hideout Furniture DoktorDauerfeuer (G.A.M.M.A.)
3. Homestead (Stalker Settlement Builder)
   Place anywhere after the above mods.
```

![Homestead in game](https://media.moddb.com/images/members/5/4662/4661404/profile/Screenshot_2026-06-16_033647.png)

---

## 🎬 Featured In

- **Make STALKER GAMMA Fun Again** — [Cheeki Breeki](https://www.youtube.com/@CheekiBreekiTv) · [watch on YouTube](https://www.youtube.com/watch?v=wXc_kw3PRkM)

  [![Cheeki Breeki](https://media.moddb.com/images/downloads/1/311/310932/auto/h25yK6gS29eQNUtrQF7Q.jpg)](https://www.youtube.com/watch?v=wXc_kw3PRkM)

- **I Opened KFC in STALKER** — [Piwomage](https://www.youtube.com/@Piwomage) · [watch on YouTube](https://www.youtube.com/watch?v=14-ZuIWhvjA)

  [![Piwomage](https://media.moddb.com/images/downloads/1/311/310932/auto/gsOiISgjh89IGYL1JeKF.jpg)](https://www.youtube.com/watch?v=14-ZuIWhvjA)

---

## 🙏 Credits

- **Damage_Zedd** — Homestead, author and maintenance
- **[devinhorowitz](https://github.com/devinhorowitz)** — contributor: rival tier upgrades, same-level teleportation fixes, UI declarations, workstation mesh fixes and extensive bug fixes.
- **Queen Jadwiga** — community contributor: settlement lifecycle improvements, workshop dismantle handling, authentic map markers, natural walk-in settler recruitment, dialogue polish, and rival camp spawning diagnostics.
- **danzy** — community contributor: camp simulation fixes (storage lookup, hospitality buff, hunger/morale), major performance passes (time-sliced updates, NPC/think throttles, rescan intervals), and rival camp improvements (spawn stutter fix, off-map spawns).
- **damiansirbu** — community contributor.

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.
