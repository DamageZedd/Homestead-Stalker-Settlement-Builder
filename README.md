# Homestead (Stalker Settlement Builder)

***IMPORTANT NOTICE***  
**PLEASE READ BEFORE INSTALLING**

Homestead is a comprehensive, deep settlement simulation overhaul. While v1.2.8 is a tested, architecturally unified release featuring full offline ALife simulation, always back up your saved games before updating or modifying large modlists.

**Author:** Damage_Zedd  
**Version:** v1.2.8  

---

## Description

**Homestead (Stalker Settlement Builder)** is a comprehensive, immersive settlement management and tactical camp-building mod for **S.T.A.L.K.E.R. Anomaly 1.5.3**.

Homestead transforms the lonely, hostile wilderness of the Zone into a canvas for building a living, breathing community. By deploying a base **Hideout Furniture workbench** (which acts as the **Settlement Camp Hub**), players establish a 50-meter territory boundary where they can place beds, stoves, stashes, defensive barricades, water pumps, alarms, and morale boosters.

Recruit companion stalkers or shelter arriving refugees to populate your settlement. Assign survivors to active job cycles—from standing guard at barricades and cooking mutant meat to repairing damaged gear, crafting ammunition, distilling ethanol, harvesting timber, and scavenging the wasteland. Balance your camp's happiness and water supplies; keep defenses high to prevent deadly raids; and customize every parameter directly in-game via a full **Mod Configuration Menu (MCM)**.

With the **PDA Settlement Manager**, you can remotely monitor all of your active settlements from anywhere in the Zone—checking happiness, population, defenses, and chest supplies, reassigning survivor jobs in real-time, cycling production directives, fast-traveling to camps, summoning trade caravans, establishing trade routes between settlements, and keeping tabs on dynamic wilderness outposts. Homestead features dynamic wild spawning (outposts appear 25–50 meters away from smart terrains pointing towards the level's centroid) populated by actual, hijacked simulation ALife squads. Occupying NPCs patrol naturally within a 15-meter radius of the central chest and naturally leave the camp after 24 in-game hours to return to standard ALife simulation duties. Fully integrated into the *Hideout Furniture* ecosystem, Homestead delivers a polished, premium life-sim survival experience in the heart of the Zone.

---

## Key Features

- **Deployable Camp Hub**: Place a Hideout Furniture workbench to establish your camp zone with visual smoke/dust placement feedback, boundary alerts, and automatic 100m overlap placement blocks with item refunds.
- **PDA Settlement Manager**: A fully integrated, interactive PDA tab allowing you to remotely track active camp statistics, reassign survivor jobs across an organized 2x6 grid, toggle remote directives, cycle camp specializations, fast-travel to camps, summon trade caravans, dismantle camps, rename camps and survivors, and monitor wilderness outposts from anywhere in the Zone.
- **Companion & Refugee Recruitment**: Recruit companion stalkers or talk to arriving refugees to have them join your camp (subject to bed capacity and a configurable survivor cap).
- **Settlement Jobs & Closed-Loop Economy**: Assign survivors to real-time work cycles (all configurable via MCM):
  - **Guard**: Patrols placed barricades and stands watch, raising camp Defense Rating.
  - **Patrol**: Roams the settlement boundary to detect threats and defend perimeter structures.
  - **Woodcutter**: Gathers 15–20 wood parts per cycle (doubled with an axe), or burns 15 wood scraps into 3–5 charcoal. Supports Auto-Rotate, Timber Focus, and Charcoal Focus directives.
  - **Brewer**: Distills 15 wood scraps and 1 clean water into 5 bottles of Nemiroff Vodka per cycle (doubled to 10 with a drug-making kit) at milk cans/bidons.
  - **Scrapper**: Salvages 10–15 scrap metal and 5–10 fasteners from ruins per cycle (doubled with crowbars, sledgehammers, or toolkits).
  - **Crafter**: Crafts workbench ammunition from gunpowder + metal scrap, and maintains automated turret ammunition using 9x18/9x19 ammo boxes.
  - **Repairer**: Restores damaged weapons and armor to 100% in exchange for food or vodka payment.
  - **Cook**: Stays near stoves to cook raw mutant meat into hot meals (tushonka, conserva, kolbasa, bread) using charcoal or fire fuel.
  - **Medic**: Synthesizes foundational medicines (Bandages, AI-2 kits, Potassium Iodide, Ibuprofen) strictly utilizing refined Nemiroff Vodka. Configurable production directives.
  - **Electrician**: Maintains camp lighting networks for free (no generator required) and passively recharges up to 3 drained batteries back to 100% condition per cycle.
  - **Scavenger**: Dispatched on targeted stash expeditions or regional sweeps across the Zone, returning with valuable artifacts, parts, and munitions.
  - **Hunter**: Tracks mutant game in a continuous 30-minute wilderness cycle, harvesting meat directly into camp food chests.
- **Real-Time Job Progression**: Jobs advance in real-time (not game-time), so progress is visible while you play. Default intervals: Cook 15 min, Craft 20 min, Repair 15 min, Scavenge 35 min, Hunter 30 min, Medic 25 min, Electrician 15 min, Woodcutter/Brewer/Scrapper 20 min — all MCM-adjustable where exposed.
- **Survivor XP & Skill System**: Survivors gain XP per completed job cycle. Tiers: Novice → Skilled (1.5× output) → Expert (2× output) → Master (3× output). Tier displayed next to survivor name in the PDA.
- **Tool Hand-in Upgrades**: Provide settlers with tools (Axes for Woodcutters, Drug Kits for Brewers, Demolition Tools for Scrappers) for permanent 2× efficiency bonuses.
- **Camp Specialization**: Each camp can be assigned a type via the PDA:
  - **Outpost** (+50% defense), **Farm** (+50% food/water), **Workshop** (+50% craft/repair), **Hideout** (+50% scavenge), **Clinic** (+100% medic output).
- **Camp Morale System**: Happiness is dynamic — low morale (<20%) risks survivors abandoning the camp; high morale (>80%) grants +10% production bonus and player hospitality buffs.
- **Camp-to-Camp Resource Transfer**: Transfer supplies between camp chests without physically traveling.
- **Trade Routes**: Establish automatic item-transfer routes between camps on a timer.
- **Fast-Travel to Camps**: Teleport to any camp from the PDA for an RU cost (MCM-adjustable). Blocked during combat.
- **Summon Trade Caravan**: Call a trader to any camp from the PDA (4-game-hour cooldown, free).
- **Dismantle Camp**: Cleanly remove a camp hub, furniture, and dismiss survivors from the PDA.
- **Survivor Rename**: Give your settlers custom names via the PDA.
- **Resource Dashboard**: Aggregate food/water/medical/ammo totals across all camps, displayed in the PDA Overview.
- **Automated Water Pumps & Sinks**: In Hideout Furniture, placeable Metal Barrels (`placeable_barrel_metal`), Sinks (`placeable_sink`), or Milk Cans (`placeable_bidon`) function as water pumps. They produce clean drinking water flasks directly into camp refrigerators (or storage chests) every 6 in-game hours, consuming one charcoal or paper filter per batch from camp storage.
- **Fridge Preservation**: Chills raw meat and food every 12 hours, restoring condition incrementally by +0.25 to simulate decay prevention.
- **Morale Boosters**: Radios and pianos boost camp happiness/morale (+10% each) and attract idle survivors who play guitars or relax nearby.
- **Camp Raids & Alarm Sirens**: Defensive gaps trigger raids by hostile squads (including advanced/veteran Bandits and Zombied). Placed alarms play subway sirens to warn of attacks. Post-raid summary shows raiders killed and guards lost.
- **Dynamic Wilderness Outposts**: Assault or trade with dynamic outposts across the Zone (populated by hostile Bandits, Monolith, Mercenaries or friendly/allied Loners, Clear Sky, Duty, Freedom, Ecologists). Garrisons scale dynamically with player rank from light 2-man scout posts up to 8-man reinforced strongholds, with patrolling ALife squads. Occupants patrol within camp boundaries and clearings yield tactical loot caches.
- **Tactical Map Markers & Faction Crests**: Distinctive PDA map icons for player settlements (tactical emerald base or PAW stalker pin) and wilderness outposts (dynamic faction badges for Bandits, Monolith, Loners, Duty, Freedom, Mercs, etc., red skulls for Mutant Nests, and white pins for Abandoned Outposts), with selectable styles in MCM.
- **Random Settlement Events**: Campfire trade caravans visit to sell supplies, refugees arrive seeking work (despawn after 2 game days if not recruited), and mutant migrations require defense.
- **Sleep Bonus**: Sleeping in a camp boundary restores satiety, power, and thirst to full (MCM toggle).
- **Time-of-Day Modifiers**: Scavenge +20% at night (stealth), Cook -20% at night, Medic +20% at night.
- **Startup Dependency Warnings**: Alerts the player via red PDA warnings if any required mod is missing.
- **Mod Configuration Menu (MCM)**: 71 adjustable settings across 5 groups (General, Jobs, Rivals, Raids & Events, QoL/Debug) covering camp boundary, hub overlap, idle NPC leash radius, spawn distances and cadence, rival camp tiers/convoy/retaliation systems, all job intervals (including Woodcutter, Brewer, and Scrapper), craft output multiplier, alarm defense bonus, decor happiness bonus, fast-travel cost, raid deficit multiplier, verbose notifications toggle, and more.

---

## Required Mods

**MODDED EXEs** required.

This mod requires the following base systems to be installed:

1. **Hideout Furniture Mod (Base) [Version 2.3.2]** — Provides core placement engine, workbenches, and stashes
2. **Hideout Gadgets for Hideout Furniture [Version 0.7.2]** — Provides alarm systems, turrets, and defense rating integrations
3. **Hideout Furniture Expansion [Version 1.0.2]** — Provides stoves, beds, and furniture varieties
4. **Even More Hideout Furniture [Version 2.2]** — Provides fridges, pianos, radios, and expanded decor props

### Not required but recommended

- **Mod App Creator [MAC] - 0.9.9.4** — Moves Settlement PDA tab to an app screen with:
  - 3D INTERACTIVE PDA
  - iTheon's PDA Taskboard
  - Fatal Error by Ncenka
  - PANDA Private Messages (to be released)
  - Player Group Command

---

## How to Play

1. Install all required mods (listed above) in the correct load order.
2. Install Homestead (Stalker Settlement Builder) via the included FOMOD installer.
3. (Recommended) Use a mod manager like Mod Organizer 2.
4. Look at the in-game guide on the PDA (Settlements tab → Guide).

---

## Load Order

```
[ ] Hideout Gadgets for Hideout Furniture (Original)
[ ] 470- Gadgets for Hideout Furniture - DoktorDauerfeuer (G.A.M.M.A. version)
[ ] Homestead (Stalker Settlement Builder)    {anywhere after these mods}
```

---

## Credits

- **Damage_Zedd** — Homestead, author and maintenance
- **[devinhorowitz](https://github.com/devinhorowitz)** — contributor: rival tier upgrades, same-level teleportation fixes, UI declarations, and extensive bug fixes across v1.2.0.
- **Queen Jadwiga** — community contributor: settlement lifecycle improvements, workshop dismantle handling, authentic map markers, natural walk-in settler recruitment, dialogue polish, and rival camp spawning diagnostics.
- **danzy** — community contributor: camp simulation fixes (storage lookup, hospitality buff, hunger/morale), major performance passes (time-sliced updates, NPC/think throttles, rescan intervals), and rival camp improvements (spawn stutter fix, off-map spawns). Merged in v1.1.8 with modifications — see the changelog.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.
