# Homestead (Stalker Settlement Builder) - Changelog

## v1.3.0 — Building Kit & Snapping

### 🧱 Building Kit (HomesteadHF):
- **Ten new placeable building pieces** (`items_homestead_building.ltx`, recipes `x_homestead_<piece>`): concrete foundation, plank floor, plank wall with window, plank gable wall, wooden stairs, and flat, sloped (30°), outer-corner (hip), inner-corner (valley) and pyramid tin roofs. Walls, half walls, doorways and doors still come from *Even More Hideout Furnitures*; the kit is sized to them.
- **One grid**: a tile is 4.70895 m (the Hideout Furniture wall width), a storey is a 2.58663 m wall plus a 0.1 m floor. Stairs rise exactly one storey over 3.2 m (about 40°), with their head flush with the tile edge and the foot inset 1.5 m so a wall can stand on the tile edge in front of them, and a sloped roof rises one storey over one tile, so a lean-to meets the walls of the floor above. Four outer corners over a 2×2 building make a pyramid roof; the gable wall closes the open ends under sloped, hip and valley roofs.
- **Models**: 56 to 2,500 triangles each, rigged like the HomesteadHF workstations (`link` root bone, all meshes skinned, `objects\large_furniture`). Vanilla textures plus the *Even More Hideout Furnitures* wall planks; the window wall uses the same plank texture, scale and offset as the 385 wall so plank lines carry across. Stairs and roofs have tilted collision boxes so they can be walked on; hip, valley, pyramid and gable pieces use several boxes on rigid child bones.
- **Inventory icons** on a new atlas (`ui\ui_icon_homestead_building.dds`, 512×1024), English and Russian names and descriptions (`st_homestead_building.xml`). The window wall counts as a barricade in the settlement scan, the other pieces as decor.

### 🧲 Snapping:
- **Fallout 4-style snapping for Hideout Furniture placement** (`homestead_snap.script`): aim at a placed piece and the preview snaps foundations beside foundations, walls onto floor and foundation edges and on top of walls, floors onto wall tops, stairs onto floors, roofs onto wall tops and beside each other. The Hideout Furniture walls snap the same way.
- **Furniture snaps too**: onto the top of floors, foundations and stairs (turned in 90° steps, on an optional grid) and flush against walls, standing on the floor.
- **Keys**: **R** rotates the held piece 90° (to the next snap position when snapped), **G** turns snapping on or off. Both are rebindable in the new MCM *Building* group, with *Snap Radius* and *Furniture Grid*. Snapped pieces skip Hideout Furniture's collision check, since flush pieces always touch.

### 👻 Placement Hologram:
- **A translucent copy of the real model while placing any Hideout Furniture or Homestead item** (`homestead_hologram.script`), green where it can be placed and red where it is blocked. Hideout Furniture alone only draws a wireframe box. It uses the engine's world script attachments (`level.add_attachment`), reads the preview's final position and rotation each frame (after snapping), and leaves the wireframe alone if the engine or the model can't do it. Toggle: MCM *Building* → *Placement Hologram*.
- New shader `homestead\hologram` (`shaders\r3\homestead_hologram.s/.vs/.ps`: alpha-blended forward pass with depth test, tint from `textures\homestead\homestead_holo_ok/bad.dds`, and a rim glow so the shape reads without lighting). It is deliberately not a "distort" shader: those write refraction offsets instead of colour, which made models with parts below their pivot (foundations) show the wrong thing.

### 🔒 Placed furniture stays put (`homestead_lock.script`):
- Furniture and the 385 walls crept, slid and tilted when the player or an NPC bumped into them. Hideout Furniture already freezes every piece when it comes online, and in the modded exes that fixes each physics element (what `fixed_bones` does), but a fixed piece is still a dynamic body: once a bump wakes it, the pieces it touches or overlaps (walls on foundations, wall corners, roofs on walls) push it away, and NPCs shove it.
- Every frozen piece except foundations, floors and stairs is now put in the engine's door mode (`set_door_ignore_dynamics`, what vanilla doors use) each time it comes online: it only collides with the player, grenades and the level, and none of them can move a frozen piece, so pieces no longer push each other and NPCs no longer shove them. **Trade-off:** NPCs, dropped items and bodies pass through walls, roofs and furniture. Scripts can't turn a piece into level geometry, so this is the closest to static the engine allows. Lamps and stash boxes are not physics objects and are left as they are.
- Foundations, floors and stairs (the Homestead pieces with `homestead_snap = foundation/floor/stairs`) stay solid for everyone, so NPCs, items and bodies land on them. Door mode on a wall or piece of furniture also stops its contacts with the floor under it, and every box of the ten building pieces' collision is inset 5 mm (in the `.ogf` and the `.object`), so snapped neighbours leave a 1 cm gap instead of overlapping and pushing each other.
- A piece unfrozen through Hideout Furniture's radial menu collides normally until it is frozen again. Pieces that already drifted stay where they are; pick them up and place them again. Toggle: MCM *Building* → *Lock Placed Furniture* (takes effect at once).
- **Pieces no longer move when a save is loaded.** The engine saves an online physics object's rotation with 8 bits per quaternion component, so every save and load turned each piece by about half a degree (up to ~0.9°, 1.5–2.3 cm at the end of a 3 m wall) and the error added up. The spot a piece is frozen at is now kept at full precision with the piece, and the piece is put back on it, without waking its physics, each time it comes online (the log says `homestead_lock: put N piece(s) back on their spots`). Freezing a piece again through the radial menu takes its new spot; wall-hung pieces (pitched 90°) only get their position back.
- Dropped along the way: setting `fixed_bones` at spawn (it changed nothing, and it read every piece as a physics object although HF has stash-box and lamp pieces with other packet layouts), and a put-back that moved drifted pieces back to their spot, which made overlapping walls fight their neighbours and move non-stop.

### ⛰ Foundation ground fit:
- HF's collision check counts any terrain poking into the preview box as a collision, so on a slope the first foundation could not be placed until collision was turned off. While you place a foundation, a 5×5 grid of probes now measures the ground under it and the pivot is set at the highest point: the preview box clears the terrain, the 1 m skirt sinks into the slope, and the spawned position matches the preview. Ground with more than 0.9 m of relief under one foundation is refused (red preview and a message), since the skirt could not cover it. Snapped neighbours keep the level of the foundation they snap to. Toggle: MCM *Building* → *Level Foundations to the Ground*.
- Ideas from the Sim Settlements source (spawn pieces static, align to the ground at a fixed height, keep one anchored grid) shaped both changes; no code was copied.

### 🛠 Building kit fixes:
- **Foundation collision matched to the grid**: its collision top was 2.5 cm above the 0.4 m the snap sockets use (small bolt details were included), and it was 1.2 cm wider than a tile on each side. Furniture and walls placed on it were buried 2.5 cm and got pushed up by physics after placing. The collision is now exactly 0.4 m high and exactly one tile wide.
- **Walls share one slab position**: the 385 walls have their collision centred 8 mm towards the front of the pivot; the Homestead window and gable walls now use the same offset, and the snap sockets (walls on floors and foundations, floors and roofs on wall tops, furniture against walls) measure from that slab.
- **Missing textures**: the foundation, roof tops and the metal fittings on the roofs and window wall were exported with the `default` engine shader instead of `models\model`, so they drew without their texture. All pieces now use `models\model`.
- **Roof collision**: the hip and pyramid roofs only had collision for part of each face (about a fifth of the surface was missing, mostly along the hips and near the peak). They now use full strips up to the peak plus a box along each hip line, and the gable wall's collision follows its whole slope. Checked against the meshes in Blender (no gap over 12 cm on any roof).

### 🧵 Rope texture:
- `textures\item\item_rope.dds` was an uncompressed 1024×1024 RGBA texture without mipmaps (4 MB); it is now DXT1 with a full mip chain (0.7 MB). Its alpha was unused, so nothing is lost. The `item_rope.thm` beside it was a copy of the fuel canister's and gave the rope a metal detail map and the canister's bump map; it is removed, so the rope uses the engine defaults.

### 📦 Settlement storage vs. personal storage:
- **Only the settlement's own storage is camp storage now.** Settlers, Auto-Sort, supply counts and job deposits use the HomesteadHF work stations' storage, the hub workbench's stash, fridges, and boxes marked `homestead_storage`. Every other Hideout Furniture box and level stash inside the camp boundary is the player's personal storage: no settler takes from it or fills it (`stalker_camp_builder.is_settlement_storage`, checked in `is_valid_camp_box`).
- **Every HomesteadHF work station holds 300 kg** (`homestead_station_storage.script`): the Distiller, Ammunition Bench, Woodcutter Station, Generator Station, Repair Bench, Hunter Station, Farmer Station and Water Purifier each get a hidden `station_stash` under them, made as soon as the station comes online. A quick use opens it; hold-use keeps the Hideout Furniture menu with Pick Up. Picking a station up hands its storage to the player (if the stash isn't loaded yet, the pickup waits and asks you to try again, so nothing is lost).
- The sorter sends each station what its `homestead_storage_buckets` name: food and drink to the Distiller, Farmer, Hunter and Water Purifier stations (after fridges), ammo, grenades and mutant parts to the Ammunition Bench and Hunter Station, tools and parts to the Repair Bench and Generator Station, fuel to the Woodcutter Station. What a job makes that fits nowhere else goes into any station with room. Stashes are looked up through `stalker_camp_builder.linked_stash_id` (workbench or station), which replaces the separate `workshop_stashes` lookups.
- **Five settlement boxes** (`items_homestead_storage.ltx`, recipes `x_homestead_<box>` at a workbench): the **Armory Crate** (weapons, ammo and grenades, 250 kg), **Quartermaster Locker** (armour and helmets, 250 kg), **Pantry** (food and drink after the fridge, 200 kg), **Supply Crate** (parts, tools and everything else, 300 kg; it can be the camp's main chest) and **Med Crate** (medicine, 100 kg). Each has its own structure type, so only the Supply Crate is ever picked as the main chest, and job overflow never lands in the Armory or Quartermaster boxes. Ammo and grenades now go to the Armory Crate before the ammo-crafting storage. The **Armory Crate** has its own model (`armory_crate.ogf`): an open Soviet rifle crate built plank by plank, with riveted corner plates, strap hinges, hasps, rope handles and a "57280" stencil, holding a vanilla AK-74 in notched cradles, three 5.45x39 packs and two F-1 grenades. About 15,000 triangles on one 4096 atlas (`homestead_hftlas_armory_crate`, DXT1 with mipmaps), a `link` collision box for the crate and a rigid box for the open lid, and a new icon on the workstation icon atlas. The **Quartermaster Locker** has its own model too (`quartermaster_locker.ogf`): a two-door Soviet steel locker with a riveted face frame, the left door padlocked and stencilled, the right door open on a vanilla steel helmet, a GP-5 hanging from the rail and boots, with a folded army outfit on top. About 5,300 triangles on one 4096 atlas (`homestead_hftlas_quartermaster_locker`), a `link` box for the body and a rigid box for the open door, and a 2x4 icon. The **Pantry** is an open plank rack stocked with sacks and spilled potatoes (from our own Farmer Station), tushonka, Smolenskaya conserva, Russian rations, vodka, flasks, jars and sausages hanging on strings (`pantry.ogf`, about 19,400 triangles on one 4096 atlas `homestead_hftlas_pantry`, one `link` box, a 3x4 icon). The Supply Crate and Med Crate still use Hideout Furniture stash meshes and icons as stand-ins until their own models are done.
- **Stations for the jobs that had none** (`items_homestead_stations.ltx`, recipes `x_homestead_<station>`), each with 300 kg of station storage: the **Field Kitchen** (Cook; it counts as a real stove, so full meals and the MCM fuel rule apply; food storage), **Field Infirmary** (Medic; counts as a medical station; medicine storage), **Guard Post** (new `guard_post` type that guards go to before barricades and turrets; weapon storage) and **Salvage Table** (new `salvage_table` type where scavengers wait between expeditions; tools and parts storage). Hideout Furniture meshes and icons stand in until their own models are done.
- A work station's hidden stash can no longer become the camp's main chest.
- **Settlement Flag hub** (`items_homestead_flag.ltx`, `homestead_settlement_flag.script`, recipe `x_homestead_settlement_flag`): plant it to found a settlement like the Hideout Furniture Workshop (pieces with `homestead_hub = true` count as hubs in `hf_on_furniture_place`). The crafted flag turns into your true faction's flag as soon as it is in your inventory (12 factions, one placed section each so each can get its own emblem; a disguise doesn't change it). The flag holds 300 kg as the camp's main storage, a quick use opens it, and picking it up dismantles the settlement (unless its storage isn't loaded yet). A flag planted inside an existing settlement goes back to your inventory. Workshop hubs keep working as before. Hideout Furniture Expansion's vertical poster stands in until the flag model is done.
- **Heads-up for existing saves:** supplies kept in Hideout Furniture boxes inside a camp stay where they are, but settlers no longer see them. Move them into a station's storage or a fridge.

## v1.2.9 — Water Purifier

### 💧 Water Purifier (HomesteadHF):
- **New placeable: Water Purifier** (`placeable_water_purifier`, item `homestead_water_purifier`, recipe `x_homestead_water_purifier`): a gravity-fed purifier on a concrete pad. An intake pipe rises out of the ground (through a bolted collar and a gate valve) into a blue steel settling drum with a funnel hopper, then through a grey carbon canister and two side filter cartridges, with a pressure gauge, a valve wheel and a spout over a bucket of water. Ground water carries radiation, so a purifier makes more sense than a hand pump. It weighs **10 kg** in the inventory (3x3 slot) and is crafted at a workbench from scrap, fasteners, copper and rope.
- **Model**: about 14,000 triangles on a single atlas material, smooth shaded, with a single `link` root bone and box collision. The valve wheel, bucket and water are vanilla G.A.M.M.A. parts (`workshop_room\\ventil_01`, `workshop_room\\vedro_01`, textures `mtl_ventil_pod_01`, `prop_spade`, `water_pool1`). The body uses one atlas (`homestead_hf\\atlas_water_purifier`, DXT1 with mipmaps) made only from vanilla textures.
- **Wired into the settlement**: `placeable_water_purifier` is mapped to the `water_pump` structure type, so it counts as a settlement water pump (the 6-hour flask production with charcoal or paper filters, camp stats, the PDA pump count and the Brewer's still check all see it). English and Russian names and descriptions, inventory icon on the workstation icon atlas, and a README entry.

## v1.2.8 — Farmer Job & Farmer Station, Trader Job & Market Stall, One Texture Atlas per Workstation

### 🥔 Farmer job (potatoes, grain & bread):
- **New Farmer job** for settlers: grows potatoes for the Brewer's still and grain that is milled and baked into bread. Works a plain plot anywhere; assign it from the PDA (new Farmer button in all three themes), from the settler dialogue, or by talking to the settler.
- **Pick the crop like Crafters and Medics**: a Farmer directive cycles *Auto-Rotate* (alternates), *Potato Focus* and *Grain Focus* — from the PDA directive button or in dialogue. A chosen crop pauses the job when its stockpile (40) is full; Auto-Rotate swaps crops first.
- **Farmer Station** (`placeable_farmer_station`, recipe `x_homestead_farmer_station`): raised potato and wheat beds, work crate with bucket and tools, sacks, a wooden fence and a brick field oven with a chimney, built from vanilla G.A.M.M.A. props and textures. Doubles the harvest and bakes bread right in the field (a Stove can bake as well). Multi-box collision, hold-Use pickup and a fitted placement outline like the other workstations.
- **New items**: Potatoes (`homestead_potato`) and Wheat Grain (`homestead_grain`), each with its own 3D model and inventory icon. The Brewer now uses potatoes first when distilling (a richer mash, +1 vodka per batch); fresh bread is no longer treated as a fermentable.
- **Settings**: MCM slider *Farmer Field Cycle (minutes)*; Farmer entry in the in-game guide, radio feed, stats and job labels. English and Russian strings.
### 🛒 Trader job & Market Stall:
- **New Trader job**: the Trader sells the goods you leave in the settlement's Market Stall and keeps the takings until you collect them. **Players can only sell**: the stall never sells anything back, and camp supplies are never touched.
- **Market Stall** (`placeable_market_stall`, recipe `x_homestead_market_stall`): a rustic roadside stall (plank counter on crates, patched tarp awning, sacks, a barrel, tins and bottles) built from vanilla G.A.M.M.A. props. A solid object with collision; use it to open its stash and drop goods in, hold-Use for the standard menu and Pick Up (goods are returned to you).
- **Prices follow the item's base price**: the Trader pays a share of each item's `cost` (default 60%, MCM *Trader Price*), reduced for worn gear and part-empty ammo boxes, and a little more for skilled traders. Up to 12 items are sold per cycle (MCM *Trader Sales Cycle*, default 15 min), most valuable first.
- **Takings go through G.A.M.M.A.'s normal money**: talk to the Trader and choose *Hand over the takings* to add the RU to your wallet. No new cash items.
- **Isolated storage**: the stall's stash is excluded from camp storage, the auto-sorter and every other job, so nothing eats the goods. Trader entry in the PDA (all themes), guide, radio feed and stats; English and Russian strings.

### 🖼️ Workstation textures:
- **One texture atlas per workstation** (`textures\homestead_hf\atlas_<station>.dds`, DXT1 with full mipmaps): each of the eight HomesteadHF workstations now uses a single material and texture, baked from the original vanilla / G.A.M.M.A. textures at full density on every face. Geometry, rigging and collision are unchanged. Ammo bench and generator glass is opaque (DXT1 has no alpha); lamp glow is kept.
- **Much smaller download**: the release no longer ships duplicate copies of vanilla / G.A.M.M.A. textures, uncompressed editor sources (`.object`) or byte-identical files that required mods already provide (Hideout Gadgets patch). The old per-material furniture textures (125 files, ~300 MB) were also removed from the repository, since no shipped model references them any more.
- **New inventory icons for every furniture item**: the eight workstations, Potatoes and Wheat Grain were re-rendered from the current models to match the Hideout Furniture icon style (transparent background, elevated front-left 3/4 view, muted overcast light, no outline or shadow). Same inventory cells as before, so no configuration changes; the icon atlas (`ui_icon_homestead_workstations.dds`) is now 512×1024 to fit the Market Stall icon.

### 🌐 Localisation:
- **Russian furniture strings fixed**: `st_homestead_hf.xml` (rus) declared windows-1251 but part of it was saved as UTF-8, so the older furniture names and descriptions were garbled in game. The whole file is now windows-1251, like the rest of the Russian localisation.

### 🔧 Fixes and refactoring added to v1.2.8 after the first build:
- **Core script split into modules**: `stalker_camp_builder.script` shed about 3,200 lines into four new files: `stalker_camp_builder_scan.script` (camp structure scanning and its cache), `stalker_camp_builder_containers.script` (server-container and inventory-box iteration), `stalker_camp_builder_inventory.script` (camp-level inventory helpers: containers, iterate, snapshot, find / consume / count) and `stalker_camp_builder_expeditions.script` (scavenger stash expeditions, the PDA map-spot dispatch menu and the travel-time engine). Behaviour is unchanged; every function is still reached through `stalker_camp_builder`.
- **Tick profiling**: with *Debug Logging* on, any actor-update slot that takes more than 4 ms logs `Slow tick slot N: X ms`, so the heavy slots (jobs, structure rescans, rival camps) can be profiled in large saves.
- **Task manager and actor binder guards no longer hide errors** (#321): both log a full traceback (once per key per 30 s). The task guard no longer clears `tsk.t` on an error, which dropped the task from saves while the PDA still listed it. The actor binder guard only swallows the luabind `[C] __index` crash and errors that pass through Homestead; any other mod's error is re-raised with its file and line.
- **Trader**: stall goods are priced by their real condition and rounds (#316). **Dismantle**: the player is paid the Market Stall's takings (#315).
- **Farmer**: with an oven, the grain and the bread stop at the 40 cap (#317). **Brewer**: the paused check counts the Moonshine Distiller and its 7 wood a batch (#318). **Woodcutter**: the wood count reaches the charcoal tip again (#311).
- **Generator Station**: the craft recipe has four components so the workshop lists it (#313), and drained batteries are recharged in place instead of deleted (#314).
- **Recruit**: the duplicate `is_camp_trader` that hid the caravan trader's dialog is removed (#312).
- **Icons and text**: potatoes and grain keep their inventory icons at full size (#319); the first workstation Russian strings are stored in windows-1251 (#320).
## v1.2.7 — HomesteadHF Modular Furniture Expansion, Settlement Distiller, Ammo Bench, Woodcutter Station, Generator Station, Gunsmith / Armor Repair Bench & Hunter Butchering / Tanning Station System

### 🛠️ HomesteadHF Workstation Fixes (spawn crash, collision, pickup, placement):
- **Electrician bench spawn crash fixed**: `generator_station.ogf` was exported with every part as a static mesh inside a skeleton model (its Armature modifier had no target), which crashed the game as soon as the item was created. All parts are now skinned to the `link` bone. Together with the dynamic bone game material fix (devinhorowitz), all six workstations now spawn.
- **Real collision on all six workstations**: the exported collision shapes had an all-zero rotation (zero size), so players walked through the furniture and Hideout Furniture's crosshair pickup could not hit it. Each model now has several collision boxes (tabletop, legs, backboard, large side items) that follow the furniture instead of one box around it.
- **Pickup works**: with real collision, hold-Use now finds the object and the Pickup option works. Added `fixed_bones = link` to every `[placeable_*]` section, like Hideout Furniture's own props.
- **Placement outline corrected**: `bounding_box_size` is read by Hideout Furniture as width, depth, height, with the origin as x, y (up), z. Boxes are now measured from each model's real bounds, inset 3 cm per side and lifted 10 cm, so the outline fits the furniture and no longer turns red on level ground.
- **Lower poly workstation models** re-exported from the fixed Blender sources.

### 🪵 HomesteadHF Modular Furniture & Custom Settlement Workstations:
- **Dedicated `HomesteadHF` Modular Furniture Architecture**: Established a dedicated `HomesteadHF` module housing custom placeable furniture definitions (`items_homestead_hf.ltx`), craft recipes (`mod_craft_homestead_hf.ltx`), string tables (`st_homestead_hf.xml`), and 3D meshes (`dynamics\HomesteadHF\distiller.ogf`). Registered `HomesteadHF` in FOMOD `ModuleConfig.xml` as a required base module for seamless installation.
- **Brewer Moonshine Distiller 3D Prop & Seamless Texture Architecture**: Created custom placeable Moonshine Distiller (*Самогонный Аппарат*) prop (`distiller.ogf` / `distiller.object` / `distiller.blend`) for settlement brewer workstations. Modeled to exact 1:1 scale for S.T.A.L.K.E.R. NPC brewer ergonomics (standing table height at 0.91m, boiler lid at 1.68m, pressure gauge at 1.72m eye level). Completely eliminated all texture seams and UV atlas stretching by utilizing canonical S.T.A.L.K.E.R. geometry (`prop_table_1`, `prop_stove1`, `bidon`, `barrel_metal`, `gaz_balon`, `box_wood`, `dev_vodka`, `prop_mug`) seamlessly integrated with custom copper distillation plumbing, a 3L glass thumper jar (*сухопарник*) wrapped in Soviet blue electrical tape (*синяя изолента*) with cloudy amber distillate, internal cooling worm coil, and brass drain spout positioned over a funnel and Cossacks vodka bottle. Re-engineered under-table prop spacing to provide clean floor clearance and air gaps between the wooden stash crate, desk cabinet pedestal, and propane gas cylinder. Fully rigged with X-Ray root bone `link`, box collision, and dynamic prop settings.
- **Settlement Brewer Workstation AI & Simulation Wiring**: Fully wired the Moonshine Distiller (`placeable_distiller`) into settlement simulation logic as the primary workstation for camp Brewers across `stalker_camp_builder.script` (`JOB_DISPATCH.brewer`, `structure_type_exact`, `structure_type_substrings`, `structure_type_check_order`), `stalker_camp_builder_npc.script` (`job_structs.brewer`), and `stalker_camp_builder_jobs.script` (`process_brewer_job`). Brewers now navigate directly to placed distillers as their top-priority workstation, receive an efficiency bonus reducing batch wood consumption from 10 to 7 parts, gain +1 bonus yield to vodka rations, and broadcast custom radio tips upon completing distillation runs. Added workbench recipe `x_homestead_distiller` under crafting category `[8]` using advanced tools and scavenged components (copper wire, scrap, fasteners, resistors).
- **Crafter Ammunition Crafting Bench 3D Prop & Ergonomic Reloading Architecture**: Created custom placeable Ammunition Crafting Bench (*Верстак для снаряжения патронов*) prop (`ammo_bench.ogf` / `ammo_bench.object` / `ammo_bench.blend`) for settlement crafter workstations. Modeled to exact 1:1 scale for S.T.A.L.K.E.R. NPC standing crafters (heavy welded steel diamond-plate tabletop at 0.91m, single-stage cast iron reloading press operating lever rising to 1.28m chest height to naturally align with the NPC `press` animation). Feature-complete with single-stage reloading press in dark RCBS green cast enamel with compound linkage arms, caliber die, smooth lathe-turned ram shaft, and seated active round; forged cast iron bench vise clamping a blued rifle barrel between soft jaw pads; mechanical balance-beam powder scale with graduated brass beam; upright powder measure dispenser hopper with drop tube; vintage powder canisters; stepped oiled pine reloading tray loaded with gleaming polished brass and copper-jacketed rounds; vernier caliper; hazardous materials component case; and lower heavy shelf storing an authentic US Military M2A1 .50 Cal Olive Drab Steel Ammunition Can (with exact yellow military stencil typography `100 CRTG .50 CAL / LINK M9 / 4 - BALL M33 / 1 - TRACER M17 / LC - 12H693S818`, folding wire handle with spot-welded mounting tabs, end toggle latch with circular punch hole, and stamped perimeter lid) and a weathered rope-handled pine supply crate. Completely eliminated floating components, calibrated PBR and X-Ray material properties (`mtl_floor_plate_02`, `mtl_rust_dark`, `mtl_bochka_01`, `mtl_truba_ch_01`, `wpn_ammo_762x51_diff`, `prop_m2a1_ammo_can_diff`, `wood_table_01`, `wood_box`, `prop_dangerbox`, `glas_dirt`), rigged with root bone `link`, box collision, and dynamic mass settings.
- **Settlement Crafter Workstation AI & Ammunition Yield Scaling**: Fully wired the Ammunition Crafting Bench (`placeable_ammo_bench`) into settlement simulation logic as the top-priority workstation for camp Crafters across `stalker_camp_builder.script` (`JOB_DISPATCH.craft`, `structure_type_exact`, `structure_type_substrings`, `structure_type_check_order`), `stalker_camp_builder_npc.script` (`job_structs.craft`), and `stalker_camp_builder_jobs.script` (`process_ammo_crafting`). Crafters now route directly to placed ammo benches as their primary workstation, receive a dedicated workbench efficiency bonus (+1 bonus box of ammunition per crafted batch), and broadcast custom PDA radio notifications celebrating freshly pressed and packed ammunition batches. Added workbench craft recipe `x_homestead_ammo_bench` under category `[8]` requiring basic tools, scrap metal, fasteners, copper wire, and electrical resistors.
- **Woodcutter Sawbuck, Chopping Block & Retort Kiln 3D Prop Architecture**: Created custom placeable Woodcutter's Station (*Козлы для распиловки, колода и углевыжигательная печь*) prop (`wood_station.ogf` / `wood_station.object` / `wood_station.blend`) for settlement woodcutter workstations. Designed as an authentic all-in-one frontier logging installation:
  - **Timber Sawbuck, Toothed Crosscut Saw & Longitudinal Pine Bark**: Heavy round-timber X-frame sawbuck with half-lap joinery and iron strapping, holding an authentic pine log cradle at `Z = 0.710m` with zero mesh clipping. Fixed cylinder normal detection (`abs(f.normal.z) > 0.8` for cut ends vs side faces) across all horizontal timber logs (`Sawbuck_Log`, `Ground_Timber_Log`, and skid rails), completely eliminating inverted tree-ring textures on the log bodies and applying authentic pine bark (`trees\trees_bark_sosna_01.dds` / `.thm`) running continuously along the longitudinal axis with end-grain growth rings (`wood_spil_1.dds`) on the cut ends. Modeled a full 1.44m vintage two-man logging crosscut saw with 48 distinct 22mm triangular peg teeth biting 3cm into the log kerf slot at `Z = 0.840m`, complete with upright carved wooden grip handles.
  - **Chopping Block with Tree Bark Outer Shell & BarryBogs Felling Axe Integration**: Authentic woodland chopping block (`Z = 0.580m`) featuring a realistic furrowed tree bark outer shell (`trees\trees_bark_a_02.dds` / `.thm` with bump maps) and end-grain growth ring top face (`wood_spil_1.dds`), embedded with an authentic forged carbon-steel felling axe (adapted from BarryBogs weapon suite). Fixed a multi-mesh join UV layer mismatch where imported OGF UVs (`'Texture'`) conflicted with procedural mesh UVs (`'UVMap'`), restoring full 1:1 UV mapping to the forged steel axe head and curved hickory handle (`new_axe\axe_new_base.dds` / `.thm`). Re-oriented the axe blade at a 45° angle biting 1.5cm into the stump top grain, prominently displaying the broad carbon-steel blade cheek, bevel, eye, poll, and hand-rubbed hickory handle with metal rivets, surrounded by scattered wood wedges, bark chips, and chopped firewood billets.
  - **Charcoal Retort Kiln, 2048 Upscaled Drum & Metallic Chimney**: Cylindrical steel charcoal retort drum mounted horizontally on a refractory clay firebrick hearth with arched combustion opening. Upscaled the drum texture (`mtl_bochka_05.dds` / `.thm`) to 2048×2048 resolution with high-fidelity metal micro-grit, flaking heat patina, deep seam weld lines, and crisp military stencil typography `2794`. Fitted with an authentic dark rolled sheet steel metallic chimney flue (`mtl\mtl_rust_dark.dds` with metallic=0.88, roughness=0.32), conical rain cowl with specular glint, pipe collar, and joint clamp band with tightening bracket and bolt.
  - **Grounded Cordwood Skid Pile**: Neat 10-log stacked cordwood pile (tiers of 4, 3, 2, and 1 crown log) resting squarely on dual pine timber skid rails directly on the ground plane (`Z = 0.000m`), completely eliminating all rear floating issues and preventing any stump collision.
  - **Lump Charcoal Supply Crate & Jet-Black Carbon Texture**: Sturdy wooden crate positioned with clean air gaps adjacent to the kiln and stump, filled with 18 individually faceted charcoal lumps textured with custom 1024×1024 jet-black porous carbon texture (`prop_charcoal_diff.dds` / `.thm`).
  - **Rigging & Materials**: Rigged with root bone `link`, box collision (`1.90m × 1.20m × 1.50m`), mass of 75kg, sound material `materials\wood`, and calibrated X-Ray engine shaders (`models\model`, `default`).
- **Electrician Field Electronics & Battery Charging Workbench 3D Prop Architecture (Full Asset Overhaul)**: Completely rebuilt and overhauled the custom placeable Electrician Electronics & Battery Charging Workbench (*Электротехнический верстак и станция зарядки аккумуляторов*) prop (`generator_station.ogf` / `generator_station.object` / `generator_station.blend`) for settlement electrician workstations, resolving all clipping and visual fidelity issues through authentic vanilla S.T.A.L.K.E.R. & G.A.M.M.A. asset kitbashing and high-fidelity texturing:
  - **Authentic S.T.A.L.K.E.R. & G.A.M.M.A. Workbench Foundation & Open Trestle Legs**: Integrated the official folding trestle steel workbench (`portable_workbench.ogf`) with heavy riveted steel diamond-plate tabletop (`mtl\mtl_sarcofag_t.dds` at `Z = 0.824m`) and tubular trestle X-legs (`mtl\mtl_truba_pod_02.dds`). Completely removed the lower blue storage chest (`prop\prop_dangerbox_2.dds` / mesh `07`) per user feedback to expose the authentic open folding trestle legs. Stripped all extraneous gunsmith meshes (Abakan receiver, cleaning rods, oil cans, and the clipping mechanical bench vise `01`) for a clean, spacious, trade-specific electrician presentation.
  - **Solid Industrial Backboard & Mounted Control Suite**: Erected a solid steel backboard panel (`prop\prop_el_shkaf_01.dds` at `Z = 0.84m` to `1.46m`) framed between upright square tube stanchions (`mtl\mtl_truba_ch_01.dds`) and a transverse top rail (`Z = 1.48m`). Flush-mounted the official Soviet electrical distribution switchboard (`el_control_unit_1.ogf` with analog gauges, ammeter dials, and rotary switches) and the heavy primary knife switch (`lab_primary_switcher.ogf` with `prop\prop_pribori_face_01.dds`), connected by horizontal backboard conduit.
  - **Cantilever Overhead Cage Worklight**: Cantilever tubular gooseneck arm extending forward from the top rail (`Z = 1.50m`) over the center of the workbench, holding an industrial metal bell shade (`mtl\mtl_lampa_pod_01.dds`), glowing incandescent bulb (`mat_bulb_glow` with emissive `models\light_planes`), and a protective four-rib steel wire cage.
  - **AAA Soviet Lead-Acid Accumulator Texture Atlas (`prop_accumulator_6st60`)**: Replaced procedural/amateur Arial text with a photorealistic, custom-crafted Soviet accumulator texture atlas (`prop\prop_accumulator_6st60.dds` + `.thm`). Accurately mapped to twin 12V 90Ah lead-acid accumulators with authentic Soviet GOST 959.0-71 and TU 16-529.020-75 Cyrillic typography (*АККУМУЛЯТОРНАЯ БАТАРЕЯ СТ-12В-90Ач*, *СДЕЛАНО В СССР ЗАВОД "ЗНАМЯ"*, Hammer and Sickle insignia), weathered paper label with ragged edges, black ribbed vulcanized casing, 6 yellow inspection cell caps, brass (+) terminal, and chrome (-) terminal. Calibrated battery casings to exact `200mm × 150mm × 185mm` proportions with a verified 20mm air gap between casings and 80mm spacing between central posts, eliminating all alligator clamp interpenetration.
  - **Zero-Clipping Catmull-Rom Smooth Organic Jumper Cabling with Anti-Penetration Bounds**: Replaced linear/handle-distorted curve tubes with smooth Catmull-Rom polygonal cylindrical cables. Heavy red positive lead drapes gracefully down from the control panel, rests on the wooden table, curves around the left side of Battery 1, and securely enters the red-insulated alligator clamp handle. Heavy black negative lead curves down, runs across the rear table, loops around the right side of Battery 2, and enters the black-insulated clamp handle. A dedicated series jumper bus neatly loops between the central terminals. Applied strict anti-penetration Z-clamping across all spline segments (`Z >= TABLETOP_Z + radius + 1mm`), mathematically eliminating any tabletop or ground surface penetration.
  - **Ground-Level Portable Generator & Front-Positioned Soviet 20L Jerry Can**: Positioned an official compact Soviet diesel generator (`disel_generator.ogf` scaled to 0.38x at `Z = 0.002m`) to the right of the bench with a 4.5cm air gap clear of the workbench trestle legs. Repositioned the authentic Soviet 20L stamped-steel fuel canister (`kanistra.ogf` with `prop\prop_kanistra.dds` at `Z = 0.002m`) prominently in front of the generator on the ground plane (`X = 0.90m, Y = -0.56m`, angled 15° toward the station center) with a clean 9cm clearance in front of the generator frame, ensuring 100% unobstructed visibility and zero clipping.
  - **Zero-Clipping Desktop Electronics Repair & Charging Suite**: Spatially partitioned the entire tabletop into non-overlapping work zones with verified air gaps: right table area accommodates an authentic handheld radio receiver (`radio.ogf` at `Z = 0.824m`) and an exoskeleton power supply unit (`psu_battery.ogf` with dedicated power lead); left table area features a heat-resistant ceramic soldering rest pad (`Z = 0.824m to 0.832m`) with chrome rest cradle supporting a horizontal pencil soldering iron with brass tip (`min Z = 0.828m`, zero table penetration) and coiled power lead, genuine printed circuit board (`materials_textolite.ogf`), roll of black PVC electrical tape, Leatherman multitool (`awr_leatherman.ogf`), rosin flux tin (`box_kanifol.ogf`), and copper wire spool (`materials_wire.ogf`).
  - **Rigging, Collision & Engine Shaders**: Rigged with root bone `link`, box collision (`1.93m × 1.02m × 1.51m`), 140kg mass, `materials\metal` sound material, canonical relative texture paths across all material slots, and calibrated X-Ray engine shaders (`models\model`, `models\light_planes`, `default`). Successfully exported to both `generator_station.ogf` and `generator_station.object` across HomesteadHF and active GAMMA mod directories, alongside an unjoined, fully editable master scene file (`generator_station.blend`) with 70 discrete named objects.
- **Settlement Electrician AI Workstation, Free Power Grid & Small Battery Pack Charging Logic**: Fully wired the Generator Station (`placeable_generator_station`) into settlement simulation logic as the top-priority workstation for camp Electricians across `stalker_camp_builder.script` (`JOB_DISPATCH.electrician`, `structure_type_exact`, `structure_type_substrings`, `structure_type_check_order`), `stalker_camp_builder_npc.script` (`job_structs.electrician`), and `stalker_camp_builder_jobs.script` (`process_electrician_job`):
  - **Small Battery Pack Rejuvenation & Upgrades**: When stationed at a generator station, electricians utilize the 4-slot dock to search camp storage for dead or drained small battery packs (`batteries_dead`, `battery_dead`, `ammo_battery_d`), recharging up to 3 to 4 units per cycle back into fresh, fully charged `batteries` ("Battery Pack"). High-tier or veteran electricians have a 25% chance per charged unit to upgrade cells to military-grade `batteries_ccell` ("Military Battery Unit"). If no dead batteries are available in storage, electricians can fabricate fresh battery packs using spare copper wire (`prt_i_copper`) and scrap metal (`prt_i_scrap`).
  - **Zero-Fuel Camp Lighting Grid**: If a generator station is present in camp, all perimeter spotlights and lamps are refueled to 100% condition directly from generator relay power with zero battery drain from settlement storage, eliminating fuel bottlenecks.
  - **Electronics Conditioning & Radio Feed**: Passthroughs restore degraded condition to 1.0 on camp electronics, detectors, torches, and heavy battery banks. Upon completing a station cycle, electricians broadcast an authentic radio dispatch to the player's PDA (`st_job_electrician_station_work`). Added workbench craft recipe `x_homestead_generator_station` under Category `[8]` requiring advanced tools, scrap metal, copper wire, capacitors, transistors, and resistors.
- **Technician Gunsmith & Armor Repair Bench 3D Prop Architecture (`placeable_repair_bench`)**: Created a custom placeable Gunsmith & Armor Repair Bench (*Оружейный и броневой ремонтный верстак*) prop (`repair_bench.ogf` / `repair_bench.object` / `repair_bench.blend`) for settlement technician workstations. Designed as an authentic, heavy-duty industrial workstation assembled by a veteran Zone mechanic, modeled to exact 1:1 scale with zero mesh clipping across 10 discrete Blender collections and 119 named objects:
  - **Heavy Welded Frame & Tabletop Architecture**: Welded 50mm square tubular steel frame (`1.80m × 0.85m × 0.95m` tabletop, `1.84m` overall height with backboard) finished in chipped Soviet industrial green enamel (`mtl\mtl_bochka_01.dds`), featuring a lower heavy channel steel storage shelf (`mtl\mtl_floor_plate_02.dds`), upright perforated backboard stanchions (`mtl\mtl_truba_ch_01.dds`), and a 4-drawer battered metal tool cabinet unit (`box_metall_01`). 5mm oil-blackened steel tabletop protected by corner gussets and an authentic vulcanized neoprene gunsmith work mat (`item_sewing_kit_b.dds`).
  - **Swivel Bench Vise with Dismantled AK-74 Receiver**: Heavy cast iron mechanical bench vise mounted on the left tabletop with Acme threaded lead screw, tommy bar, guide rails, and protective vulcanized rubber soft jaws (`prop_kanistra_black`). Securely clamps an authentic dismantled S.T.A.L.K.E.R. AK-74 stamped receiver (`wpn_ak74.ogf` / `wpn\wpn_ak74.dds`) at receiver balance point with zero mesh clipping.
  - **Disassembled Weapon Components & Parts Tray**: Laid out across the neoprene mat is an authentic dismantled AK parts kit (`gun_parts.ogf 01`) featuring stamped dust cover, bolt carrier and gas piston, rotary bolt, gas tube, selector lever, recoil spring assembly, and trigger group pins neatly arranged in an oiled metal parts tray. Includes an authentic Bakelite 30-round 5.45×39mm magazine (`ak74_orange_mag.ogf` / `wpn\wpn_magazines.dds`), TGP-A tactical muzzle brake/suppressor, unattached wooden buttstock, and lower handguard with heat shield.
  - **Gunsmith Cleaning Tools, Solvents & Lubricants**: Universal multi-section brass cleaning rod with swivel T-handle (`ramrod_tool.ogf`), open field cleaning kit tin (`cleaning_kit_s.ogf`), stainless steel Leatherman multi-tool pliers (`awr_leatherman.ogf`), double-ended nylon detailing brush, rolled shop rags, cylindrical steel solvent tin (`solvent.ogf`), Soviet green gun oil can (`gun_oil_ru.ogf`), grease tin (`grease.ogf`), and spray degreaser aerosol can with directional nozzle straw.
  - **Armor Repair Station & Ballistic Plate Servicing**: Spatially separated armor patching zone on the right tabletop fitted with a damaged GOST Level 5 composite strike plate featuring cracked ceramic and bullet spall crater, heavy fabric canvas patches (`textile_patch_m.ogf`), military field sewing kit with heavy-duty curved needles and nylon thread spools (`sewing_kit_b.ogf`), steel hand riveter, dual-grit sharpening stones (`sharpening_stones.ogf`), and heavy armor repair kit crate (`armor_repair_fa.ogf`).
  - **Perforated Tool Pegboard, Technical Blueprints & Articulated Task Lamp**: Heavy perforated steel tool pegboard backboard (`mtl\mtl_setka_01.dds`) holding Cyrillic AK-74 receiver technical schematics and armor composite cross-sections pinned with brass tacks, hanging stamped chrome vanadium double open-ended wrenches on steel hooks, compact metal upper shelf holding two 20-round military spam cans of 7.62×51mm AP ammo (`ammo_762x51_ap.ogf`), and an articulated adjustable green enamel task lamp with mounting bracket, knuckle joints, conical shade, incandescent bulb (`mat_bulb_glow` with emissive `models\light_planes`), casting focused warm light across the rifle vise.
  - **100% Authentic In-Game Texture Integration & Flawless UV Alignment across All Assets**: Completely eliminated generic fallback textures across all kitbashed S.T.A.L.K.E.R. props by extracting official base game DDS assets from `textures.db` and binding their authentic textures:
    - Receiver & Barrel: Corrected UV alignment by binding the authentic wood-furniture AK-74 diffuse texture (`wpn\wpn_ak74\wpn_ak74.dds`, 2048×2048), eliminating the UV mismatch caused by polymer AK-74M mapping and perfectly aligning all receiver stampings, rivets, selector notches, and buttstock grain.
    - PSO-1 Optical Scope: Bound the authentic 2048×2048 dark tactical steel diffuse map (`wpn\wpn_addons\wpn_addon_scope_pso\wpn_addon_scope_pso1.dds`) with Cyrillic dial markings, replacing an errant green bump map.
    - TGP-A Tactical Suppressor: `wpn\wpn_addon_sil_tgp-a.dds`
    - Disassembled Parts Kit: `item\part\wpn\wpn_ak74.dds`
    - 30-Round Bakelite Magazine: `aml_mags\ak545x39_mag\wpn_eft_ak74_mag_30rnd_diff.dds`
    - 5.45x39mm Cartridges: `aml_mags\cartridges\wpn_eft_ak74_ammo_545x39_diff.dds`
    - Cleaning Tools & Ramrod: `repair\repair_ramrod.dds` & `repair\repair_cleaning_kit.dds`
    - Leatherman Multi-tool: `awr\leatherman.dds`
    - Lubricants & Solvents: `repair\repair_gun_oil_ru.dds` & `repair\repair_grease_solvent.dds`
    - Armor Repair Kit & Sewing Kit: `repair\repair_armor_repair_fa.dds` & `repair\repair_sewing_kit.dds`
    - Textile Patches & Sharpening Stones: `repair\repair_textile_patch_m.dds` & `repair\repair_sharpening_stones.dds`
    - Ammunition Cans: `wpn\ammo\762x51_ap.dds`
    - Storage Crates: `prop\prop_dangerbox_2.dds` & `repair\repair_toolkit_wp.dds`
    - Technical Schematics & Blueprints: `item\item_document_01.dds` & `prop\prop_paper.dds`
  - **Unified UV Architecture, Dynamic Rigging & Engine Export**: Resolved multi-mesh UV layer divergence by unifying all 102 individual mesh UV layers to a single unified `Texture` channel prior to export joining, completely preventing dropped UVs on imported game assets during X-Ray export. Rigged with root bone `link`, box collision (`1.90m × 0.88m × 0.96m`), 110kg mass, `materials\metal` sound material, canonical relative texture paths, and calibrated X-Ray engine shaders (`models\model`, `models\light_planes`, `default`). Successfully exported to `repair_bench.ogf` (4.03 MB) and `repair_bench.object` (6.08 MB) across HomesteadHF and active GAMMA mod directories, while preserving the user's custom asset positioning in the unjoined master scene file (`repair_bench.blend`).
- **Settlement Technician AI Workstation, Repair Efficiency & Passive Weapon Maintenance**: Fully wired the Gunsmith & Armor Repair Bench (`placeable_repair_bench`) into settlement simulation logic as the top-priority workstation for camp Technicians across `stalker_camp_builder.script` (`JOB_DISPATCH.technician`, `structure_type_exact`, `structure_type_substrings`, `structure_type_check_order`), `stalker_camp_builder_npc.script` (`job_structs.technician`), and `stalker_camp_builder_jobs.script` (`process_gear_repair`, `check_job_idle`):
  - **Station Repair Efficiency (+50% Repair Increment)**: When stationed at a repair bench, technicians gain a +50% repair efficiency bonus per cycle (`repair_inc * 1.5`), accelerating gear reconditioning and broadcasting an authentic PDA radio dispatch (`st_job_technician_station_work`).
  - **Zero-Fee Passive Weapon Maintenance**: If a repair bench is present in camp, technicians passively inspect and service stored camp weapons below 80% condition for free (up to an 80% cap), cleaning actions, clearing bore fouling, and lubricating trigger groups, broadcasting `st_job_technician_passive_maintenance`. Satisfies technician workbench requirements even when no fee provisions are deposited in camp storage.
  - **Crafting & Localization**: Added workbench craft recipe `x_homestead_repair_bench` under Category `[8]` requiring heavy workshop tools, scrap metal, fasteners, steel pipe, and textile patches, with full English and Russian string tables (`st_homestead_hf.xml`).
- **Hunter Butchering & Tanning Station 3D Prop Architecture (`placeable_hunter_station`)**: Created a custom placeable Hunter Butchering & Tanning Station (*Охотничий разделочный стан и дубильня*) prop (`hunter_station.ogf` / `hunter_station.object` / `hunter_station.blend`) for settlement hunter workstations. Designed as an authentic frontier mutant game harvesting workstation, modeled to exact 1:1 scale with zero mesh clipping across 12 discrete Blender collections and 145 named mesh objects:
  - **Corrected Heavy Timber A-Frame Carcass Hanging Rack (`2.20m W × 1.50m D × 2.30m H`)**: Resolved inverted A-frame geometry by reconstructing the timber legs to form a true structural triangular "A" (wide ground skids at `Y = ±0.55m` tapering inward to meet at the top apex at `Y = 0.00m, Z = 2.18m`). Overlapping bolted lap joints, forged iron reinforcing brackets (`mtl\mtl_rust_dark.dds`), overhead crossbeam wrapped in weathered rope lashings (`item\item_rope.dds`), and a forged steel gambrel carcass hanger with downward spread hooks suspended via iron pulley wheel and braided rope.
  - **Ergonomic Skinning & Fleshing Beam**: Thick longitudinal halved timber log with smooth convex working face inclined at a 35° angle, supported by sturdy dual splayed log legs. Draped with an authentic partially fleshed mutant Flesh hide (`act\act_plot.dds` with cropped UV mapping to capture ribbed mutant skin). Fitted with a two-handed forged draw scraper tool resting across the beam crest, dual-grit sharpening whetstones (`sharpening_stones.ogf`), and folded oily shop rags.
  - **Complete Tanning Rack Overhaul, Custom Hide Textures & Zero-Floating Cordage**: Completely rebuilt both tanning stretch frames to eliminate all floating, detached, or misaligned meshes:
    - **Custom High-Fidelity Hide Textures**: Authored custom, photorealistic high-resolution hide textures with corresponding engine THM descriptors: `prop\prop_mutant_pelt_pseudodog.dds` (coarse grey/charcoal wolf fur along dorsal spine with authentic head, ear, paw, and tail contours on the front face, and `prop_mutant_pelt_pseudodog_back.dds` raw scraped parchment/flesh on the reverse) and `prop\prop_mutant_pelt_leather.dds` (warm golden amber buckskin suede with authentic scraper tool striations and radial pull wrinkles).
    - **Full 3D Structural Lap Joints & Corner Lashings**: Each rack is constructed from 4 peeled pine poles with overlapping corner lap joints, wooden through-pegs, and 3D rawhide rope cross-lashings (`mat_hunter_hemp_rope`), supported by an independent grounded rear kickstand pole (`Z = 0.00m`) fastened with a lashed collar.
    - **100% Physically Anchored Radial Cordage**: Replaced disconnected floating cylinders with 24 individual taut 3D cylindrical rope cords per frame. Every cord starts directly at a punched perimeter eyelet on the hide boundary and radiates outward under tension to securely wrap around the nearest frame rail (top, bottom, left, or right), completely eliminating floating elements.
    - **Flank Spatial Partitioning**: Positioned Frame 1 on the right flank with mallet and rolled hide bundle, and Frame 2 on the left flank with verified air gap clear of the hanging rope coil and gantry crossbeam. Preserved all custom user item placements and deletions across the station.
  - **Dynamic Rigging & Engine Export**: Single-bone dynamic armature `hunter_station` with root bone `link`, box collision (`4.56m × 2.60m × 2.40m`, half extents `2.28m × 1.30m × 1.20m`), 150kg mass, `materials\wood` sound material, and single unified UV layer `Texture` across 29 material slots. Exported to `hunter_station.ogf` (3.85 MB) and `hunter_station.object` (4.59 MB) across HomesteadHF and active GAMMA mod directories, preserving all master assets in `hunter_station.blend`.
- **Settlement Hunter AI Workstation, Meat Yield Scaling, Mutant Pelt Curing & Trophy Harvesting**: Fully wired the Hunter Butchering & Tanning Station (`placeable_hunter_station`) into settlement simulation logic as the top-priority workstation for camp Hunters across `stalker_camp_builder.script` (`JOB_DISPATCH.hunter`, `structure_type_exact`, `structure_type_substrings`, `structure_type_check_order`, `SPECIALIZED_CONTAINER_TYPES`), `stalker_camp_builder_npc.script` (`job_structs.hunter`), and `stalker_camp_builder_jobs.script` (`spawn_hunted_meat`):
  - **Meat Yield Scaling (+1 Base & 1.5x Multiplier)**: When stationed at a hunter station, hunters gain +1 to max meat drops and a 1.5x harvest multiplier to total meat yield deposited into camp storage.
  - **Mutant Pelt Preservation (75% Chance)**: Hunters utilizing the station have a 75% chance per cycle to harvest and preserve intact mutant pelts (`hide_pseudodog`, `hide_boar`, `hide_flesh`, `hide_dog`, `hide_chimera`, `hide_bloodsucker`, `hide_burer`).
  - **Rare Hunting Trophy Extraction (60% Chance)**: Hunters have a 60% chance per cycle to recover pristine mutant trophies (`mutant_part_boar_leg`, `mutant_part_flesh_eye`, `mutant_part_dog_tail`, `mutant_part_psevdodog_tail`, `mutant_part_snork_leg`, `mutant_part_bloodsucker_jaw`, `mutant_part_chimera_claw`).
  - **Dynamic Notification**: Emits a custom settlement radio dispatch (`st_job_hunter_station_work`) upon completing a butchering and tanning cycle.
- **Dedicated 3D Workstation Inventory Icon Atlas (`ui_icon_homestead_workstations`)**: Created a dedicated high-fidelity 512×512 inventory icon atlas (`ui_icon_homestead_workstations.dds`) replacing generic placeholder icons across all 6 custom settlement job furniture pieces in `items_homestead_hf.ltx`:
  - **1:1 Studio 3D Orthographic Renders**: Rendered each workstation directly from its master 3D model in Blender using high-resolution orthographic cameras, 3-point studio lighting (key sun, cool fill, and edge rim lights), and transparent RGBA alpha channels.
  - **Authentic S.T.A.L.K.E.R. Icon Styling**: Processed each icon with calibrated color contrast, Lanczos downsampling, unsharp masking, and subtle soft drop shadows so silhouettes stand out crisply against dark and bright inventory slots.
  - **Calibrated Grid Cell Registrations**:
    - `homestead_distiller` (Moonshine Distiller): Grid `(0, 0)`, Size `3 × 3` (150×150 px).
    - `homestead_ammo_bench` (Ammunition Crafting Bench): Grid `(3, 0)`, Size `3 × 3` (150×150 px).
    - `homestead_wood_station` (Woodcutter & Charcoal Station): Grid `(6, 0)`, Size `3 × 3` (150×150 px).
    - `homestead_generator_station` (Battery & Generator Station): Grid `(0, 3)`, Size `3 × 3` (150×150 px).
    - `homestead_repair_bench` (Gunsmith & Armor Repair Bench): Grid `(3, 3)`, Size `4 × 3` (200×150 px).
    - `homestead_hunter_station` (Hunter Butchering & Tanning Station): Grid `(0, 6)`, Size `4 × 3` (200×150 px).
  - **Fix Debug Item Spawner DX11 Render Freeze (Fatal UI THM Removal & DDS MipCount Patch)**: Diagnosed and resolved two fatal DirectX 11 render loop driver deadlocks that occurred immediately when clicking/spawning workstation items in the debug spawner (`UIDebugISpawner`) or viewing actor inventory:
    - **Fatal UI Texture THM Removal**: The workstation icon texture was previously accompanied by an errant 3D model `.thm` file referencing bump/detail material descriptors (`detail_metall_det3`, `prop_kanistra_bump`). In S.T.A.L.K.E.R. Anomaly, 2D UI quads (`icons_texture`) cannot bind 3D normal/detail shaders without tangent vertex attributes, causing an unhandled GPU driver deadlock. Permanently removed `ui_icon_homestead_workstations.thm`.
    - **DDS Header MipMap Count Correction (188 DDS Files Patched)**: Discovered that textures saved via Pillow default to `dwMipMapCount = 0` at offset 28 in the DDS header. In Direct3D 11 (`D3DX11CreateTextureFromMemory`), a mip count of 0 instructs the driver to allocate and stream a full 12-level mipmap pyramid; attempting to read non-existent subresources past EOF locked the DX11 device. Patched all 188 textures across `HomesteadHF` and the active mod directory so `dwMipMapCount = 1`, guaranteeing immediate, crash-free texture instantiation.
  - **Blender MCP Model Shader Correction & Hunter Station Re-Export (`hunter_station.ogf`)**: Audited all 6 workstation blend files in Blender using the Blender MCP bridge. Identified that `hunter_station_visual` had assigned `mat_hunter_sleepbag` with engine shader `default` instead of `models\model`. In X-Ray Engine D3D11, dynamic meshes rendered with `default` fail vertex shader input layout matching and crash/freeze the pipeline. Corrected `mat_hunter_sleepbag` to `models\model` and re-exported `hunter_station.ogf` (3.85 MB) and `hunter_station.object` (4.59 MB) with unified UV channels and valid X-Ray physics.
  - **100% Self-Contained Workstation Texture Suite (45 Textures Packaged)**: Converted and deployed 45 full-fidelity textures across `act/`, `aml_mags/`, `awr/`, `item/`, `mtl/`, `prop/`, `repair/`, `wood/`, and `wpn/` directly into `HomesteadHF/gamedata/textures/` (including mutant boar leg meat, skinning knives, axes, sleeping bag, AK-74 components, PSO-1 scope, gunsmith toolkits, oils, solvents, and sewing kits). Cleaned Blender `.001` material suffixes from `generator_station.ogf` texture chunk bindings. Verified with a comprehensive 128-mesh audit guaranteeing 0 missing textures across all 6 workstations.
  - **Standardized Placeable Physics Classification & Script Binding (`placeable_type = prop`, `script_binding = bind_hf_base.init`)**: Updated all 6 custom workstations in `items_homestead_hf.ltx` (`distiller`, `ammo_bench`, `wood_station`, `generator_station`, `repair_bench`, `hunter_station`) to use standard `placeable_type = prop` matching canonical Homestead placeable items (rather than raw engine class identifier `O_PHYSIC`), ensuring proper bounding box collision placement and physics interaction. Assigned `script_binding = bind_hf_base.init` across all workstation sections for proper client binder lifecycle management.
  - **Global ALife Create & Debug Spawner Watchdog Immunity**: Intercepted `_G.alife_create_item` and directly hooked `ui_debug_launcher.UIDebug_ItemSpawn.Action_SpawnItem` and `ui_debug_launcher.UIDebug_ItemSpawn.Spawn` to proactively grant lag protection (`a_rax_wd.save_state`) whenever spawning heavy settlement furniture, preventing false-positive Busy Hands watchdog timeouts and emergency save halts. Hoisted `safe_register_callback` with `_G` fallback to file scope in `stalker_camp_builder.script` so early startup patches have full callback access without nil global errors.
  - **Task Manager & Actor Binder Engine Crash Shields (`patch_task_manager_guard`, `patch_actor_binder_guard`)**: Safely wrapped `task_manager.CRandomTask.update` and `bind_stalker.actor_binder.update` in `pcall` with safe task validation, preventing fatal Luabind `[C] __index` crashes when game tasks iterate player inventory upon receiving newly spawned items.
  - **Detector Bone Hide Engine Crash Shield (`patch_detec_bone_hide_guard`)**: Safely wrapped BarryBogs detector bone hide update callback (`detec_bone_hide.actor_on_update`) in `pcall`, completely guarding against fatal `lua_pcall_failed` Luabind errors in `detec_bone_hide.script(20)` when active detector devices transition states or are queried during item spawning and inventory transactions.
  - **Bulletproof Fatal Lua Diagnostic Handler (`homestead_luabind_fatal_diag`)**: Protected the engine's Luabind fatal crash callback in `pcall` to ensure diagnostic logging never throws secondary exceptions inside `lua_pcall` or produces `error in error handling`.
  - **Universal Mod Compatibility**: Packaged standalone into `HomesteadHF` and mirrored to active G.A.M.M.A. directory, fully decoupling Homestead furniture from external third-party texture files (`placeable_devices.dds`).

## v1.2.6 — Core Simulation Stability, Raid Hourly Scheduling, XP Progression Normalization & Infrastructure Fixes

### 🛡️ Core Simulation Stability, Raid Scheduling & Inventory Integrity:
- **Engine Hardening — Universal CCharacterInfo [(null)] Profile Shield (fixes #306)**: Added proactive engine shielding in `z_stalker_camp_builder_pda_monkeypatch.script` intercepting `ui_inventory.start`, `death_manager.create_release_item`, `actor_on_first_update`, and `server_entity_on_register`. Prevents unguardable X-Ray engine crashes in `CXML_IdToIndex<CCharacterInfo>::GetById` (`xml_str_id_loader.h:115`, `item not found, id [(null)]`) caused when any stalker or corpse with an unassigned or stripped `character_profile` is queried by `CUICharacterInfo` during corpse looting, trade, or dialog. Missing profiles are automatically detected and repaired with faction-appropriate fallback profiles (`sim_default_<comm>_0` or `default`). Removed redundant `load_state` registration which executed prior to savegame entity deserialization, avoiding 65,534 empty ALife lookups, and added execution verification to `set_profile_name` before logging repairs.
- **Hourly Camp Raid Cooldown Check Interval Enforcement**: Fixed an issue in `process_camp_raids` where elapsed raid cooldowns ran in `actor_on_update` slot 5 without validating the check interval (`cfg.raid_check_interval`, default 3600 game seconds = 1 hour), causing raids to roll every 10 real seconds and trigger rapid settlement assaults. Added `(current_sec - camp.last_raid_check_time) >= check_interval` guard to ensure raids roll strictly on the configured in-game hourly schedule.
- **Dual-XP Progression Scale Normalization**: Unified survivor XP progression thresholds to standard 100 / 250 / 500 XP (Skilled / Expert / Master) across routine jobs (+10 XP) and expeditions (+15 / +25 / +45 XP). Level promotions now broadcast congratulations into the PDA settlement radio feed, and missing professions (`woodcutter`, `brewer`, `scrapper`) have been added to the job display resolver.
- **Container Scan Completeness & Offline Inventory Shielding**: Added `camp._stored_items_complete` tracking so early-terminating online container queries cannot poison offline inventory iterations or truncate stored-item lists.
- **ALife 65k Sweep Cache Optimization**: Resolved a critical ALife loop issue in `get_server_container_items` where empty containers stored `nil` instead of `{}`, triggering full 65,534-ID ALife registry sweeps on every check. Empty containers now cache properly within the 3.5s window, and duplicate item insertion between `camp.stored_items` and `server_objects_registry` has been eliminated.
- **Workshop Hub Script Zone Release & Resource Leak Fix**: Updated `hf_on_before_furniture_release` to invoke `safe_deferred_release(camp.zone_id)` before setting `active_camps[obj_id] = nil`, preventing abandoned `script_zone` objects from lingering in engine memory and corrupting savegame state upon hub deconstruction.
- **Offline Multi-Use Item Max Uses Query**: Updated offline container scans to query authentic `max_uses` from `ini_sys` (`r_float_ex` / `r_u32_ex`) rather than hardcoding `uses = 1`, preserving multi-use medical, cooking, and maintenance item values.
- **Scavenger Ambush MCM Config Guard**: Added fallback resolution `(sb.cfg.scavenge_ambush_chance or sb.cfg.scavenger_ambush_chance or 15)` in `stalker_camp_builder_jobs.script` and added `scavenger_ambush_chance = 15` alongside `scavenge_ambush_chance = 15` in MCM defaults to prevent nil comparison errors.
- **Radio Feed Deduplication & Missing Storage Warnings (fixes #306)**: Tagged all initial settlement telemetry entries with `scan = true` so `trim_radio_log` properly purges prior telemetry passes on rescans. Expanded telemetry reporting to include woodcutters, brewers, scrappers, and electricians, widened `load_state` deduplication window to 8 entries, suppressed redundant `camp_send_tip` logs on successful scavenger and hunter radio dispatches, and restored vital missing storage container warnings to the PDA radio feed under Expeditions and Work categories.
- **Fridge Preservation Expansion for Cooked Dishes**: Expanded refrigerator food preservation logic to protect all cooked meats (`meat_*`), sausage (`kolbasa`), bread, and opened rations against condition decay.
- **Cook Stockpile Capping & Job State Accuracy**: Updated `process_cook_job` when food stockpiles are capped to set `survivor.shortfall_reason = "Stockpile Full"` and cleanly return `false`, preventing unearned XP gains and misleading success chimes.
- **Electrician Grid Check & Ambush Work State Integrity**: Resolved hardcoded `did_work = true` flags during scavenger ambushes, missing container scenarios, and fully powered electrician grids (`survivor.shortfall_reason = "Grid Fully Powered"`).
- **Pending Condition & Vector Packing Fixes**: Fixed `deposit_item_to_camp` to preserve existing queued item condition and parts when updating uses (`pend.u`), and updated `pack_table_vectors` to count exact 3-key coordinate sets rather than relying on LuaJIT hash bucket ordering.

### 👥 AI Workstations, Companion Logic, Theme Architecture & Dialogues (Phase 2 Fixes):
- **Settler Animation Condlist Synchronization**: Resolved an issue in `setup_settler_beh_logic` where `axr_beh.script` and custom AI schemes continuously reset settlers to `"guard"` every C++ planner tick because `st.beh.delay_cond`, `st.beh.wait_anim`, and `st.beh.delay_anim` were not synchronized with `safe_anim`. Homestead now updates all condlist properties and animation state variables across `st.beh`, eliminating violent 1-second animation flickering and preserving custom look vectors.
- **Workstation AI for Woodcutters, Brewers & Scrappers**: Integrated `woodcutter`, `brewer`, and `scrapper` professions into `JOB_DISPATCH`, `get_settler_job_target`, and `get_settler_display_name`. Settlers assigned to these trades now receive authentic workstation routing (workbenches, stoves, medstations, repair benches), play trade-appropriate animations, and display proper job titles ("the Woodcutter", "the Brewer", "the Scrapper") rather than aimlessly wandering camp.
- **Companion State Retention on Reassignment**: Corrected `purge_settler_companion_and_squad_state` so `m_data.stalker_camp_builder_freed_settlers` is strictly set when a settler is banished (`is_banish ~= false`). Reassigning a companion settler back to routine camp duties now preserves their settler behavior logic across map transitions and game loads.
- **Cross-Level Companion Teleport Online Switch Restoration**: Fixed an issue in `return_to_settlement` where dismissing companions to a settlement on another map left their server object with `switch_online = false`, permanently preventing them from switching online. The routine now restores `set_switch_online(npc_id, true)` and `set_switch_offline(npc_id, true)` upon arrival.
- **Caravan Trader Faction Alignment & Recruitment Protection**: Expanded `get_camp_trader_section` to fall back to authentic faction-appropriate model sections (`sim_default_<faction>_1`) rather than defaulting to Loner (`"stalker_regular"`), and added a 0.1s initialization callback setting trader relations and community upon spawn. Added a guard to `can_recruit` blocking players from recruiting active caravan traders and losing them to automatic despawn sweeps.
- **WPO Weapon & Parts Overhaul Dialogue Reconnection**: Connected the missing WPO weapon overhaul dialogue node (`phrase 12`) to `camp_technician_dialog` in `modxml_stalker_camp_builder.script`. Fixed speaker resolution in `get_tech_overhaul_ask_text` and `repair_equipped_weapon_and_parts` to explicitly inspect `db.actor` rather than resolving to the technician NPC when called from `<script_text>` functors.
- **Guard Station Look Vector & Facing Direction**: Updated `set_survivor_position` to capture the player's view direction (`db.actor:direction()`) and store `look_x`, `look_y`, `look_z` in `assigned_pos`. Settlers ordered to "Hold this position" now turn to face outward toward chokepoints and perimeters instead of looking straight down at their feet.
- **Modern Theme Architecture Modernization**: Updated `01_Theme_Modern` scripts to conform to Homestead's modular theme architecture, eliminating the outdated 3,335-line monolithic script and establishing full compatibility with `ui_stalker_camp_builder_theme.script`.

### ⚔️ Production Chains, Specialization Scaling, Turret Ballistics & Dynamic Outposts (Phase 3 Fixes):
- **Timber Kiln Kiln Burn & Woodcutter Balance**: Rebalanced the timber kiln to consume a fixed batch of 5 wood scraps in exchange for 3 bags of charcoal (with an additional +2 bonus bags when equipped with a woodcutter axe), preventing the kiln from burning single scrap pieces for disproportionate charcoal yields. Wood harvest yields and charcoal batches now scale dynamically with survivor skill tiers (Novice 1.0x, Skilled 1.5x, Expert 2.0x, Master 3.0x) and receive agricultural bonuses from the Farm specialization (1.25x).
- **Brewery Distillation Expansion & Medical Precursor Scaling**: Expanded brewery distillation in `process_brewer_job` to utilize clean water or fermentable food items (bread, corn, beans, tomatoes, potatoes) to brew Nemiroff Vodka. When the brewer is equipped with a chemical drug kit or achieves higher survivor rank (tier >= 2), distillation yields pure Medical Alcohol (`alcohol` / `antiseptic`) alongside vodka rations. Output now scales with survivor tier and Farm specialization bonuses.
- **Scrapper Workshop & Damaged Gear Salvaging**: Enhanced the scrapper role to scale metal scrap and fastener salvaging with survivor skill tiers, Workshop specialization (1.25x), and Hideout specialization (1.25x). Scrappers equipped with basic tools now actively inspect settlement storage for ruined weapons and armor (<35% condition) to dismantle into extra scrap metal, fasteners, and spare components.
- **Crafting & Medical Tier Multiplier Integration**: Integrated survivor tier scaling (`get_survivor_tier_mult`) into ammunition crafting (`process_ammo_crafting`) and medical synthesis (`process_medic_job`), allowing higher-ranked survivors to yield larger production batches for camp armories and clinics.
- **Electrician Cycle Integrity, Battery Recharging & Status Accuracy**: Fixed `process_electrician_job` which previously returned `nil` and caused the job update loop to evaluate `did_work = false` even when lamps were successfully recharged. The routine now returns the exact count of serviced fixtures, clears `survivor.shortfall_reason`, awards survivor XP, and provides a battery maintenance service that recharges depleted battery cells (`batteries_dead` / degraded batteries) when camp lighting grids are already fully powered.
- **Technician Hub Workbench Recognition & Shortfall Clearing**: Fixed workbench detection in `process_gear_repair` to recognize the settlement Workshop hub (`hub_id`) directly in `wb_set` even if omitted from `workshop_stashes`. Added explicit clearing of `survivor.shortfall_reason = nil` when gear is successfully repaired so stale shortfall warnings do not linger on active technicians.
- **Turret Table Raycast Elevation Offset**: Elevated the visibility and tracking raycast origin in `bind_pistol_turret.script` by `+0.55m` (`turret_pos.y = turret_pos.y + 0.55`). When placed on elevated platforms, barricades, or `placeable_turret_table`, raycasts now originate from the turret optic and muzzle level rather than clipping against the table's own geometry, enabling turrets to reliably acquire and engage downhill and ground-level hostiles.
- **Startup Crash Fix — Duplicate `[alarm_system]` DLTX Section**: Reverted the un-commented `[alarm_system]` / `[placeable_alarm_system]` item sections, the `[alarm_system]` trade entry, and the `x_alarm_system` recipe in `04_HideoutGadgetsGammaPatch`. G.A.M.M.A.'s Gadgets for Hideout Furniture (`items_hf_gadgets_gamma.ltx` / `trade_gadgets_gamma.ltx` / `mod_craft_gadgets_gamma.ltx`) already defines all of these, so re-declaring them crashed the game while loading `system.ltx` (`[DLTX] Duplicate section 'alarm_system' wasn't marked as an override`).
- **Alarm Threat Filtering**: Expanded detection range in `bind_alarm_system_pda.script` to 15 meters and added threat filtering so alarms only trigger for hostile enemies and mutants, preventing false alarms on the player and friendly settlement stalkers.
- **Dynamic Outpost SOS Response Countdown Timer & Skirmish Cleanup (fixes #305)**: Fixed an issue in `stalker_camp_builder_rivals.script` where outpost skirmishes and SOS distress calls resolved instantaneously in the same millisecond the raid was triggered. Skirmishes now feature a full 3-minute (180s real-time, scaled by `level.get_time_factor()`) response countdown window allowing the player to rush in and defend allied garrisons for gratitude rewards. Additionally resolved an issue where quiet or hostile outposts kept stale `pending_skirmish` flags when garrisons moved on or were eliminated, ensuring new garrisons and faction takeovers start with clean skirmish states.
- **Skirmish Takeover Clean ALife Squad Member Release**: Resolved an issue during rival outpost faction takeovers where former garrison squads were disconnected via `release_rival_hold` without deleting their NPCs, creating phantom wandering stalkers. Defeated garrison squad members are now cleanly eliminated using `alife_release`.
- **Courier Delivery Smart Terrain Radius Expansion**: Widened courier supply convoy completion detection from 25m to 35m (`dist_sqr <= 1225.0`) and added distance checks to the destination smart terrain (`target_smart_id`), preventing couriers arriving at outpost perimeter smarts from getting stranded outside chest interaction bounds.

## v1.2.5 — Medical Synthesis Stockpile Capping, Scavenger Expedition Teleportation, Simulation Integrity & Multi-Camp Lifecycle Polish

### 💊 Medical Synthesis & Stockpile Capping (Community / Kruglov, devinhorowitz):
- **Medic Ibuprofen & Drug Booster Stockpile Capping**: Resolved a bug where medics accumulated excessive stockpiles of ibuprofen (24+ units in the medstation) by incorporating `drug_booster` and `ibuprofen` into `is_camp_supply_capped` (`auto` mode) and `snapshot.med_counts.auto`.
- **Per-Item Candidate Surplus Threshold in Auto-Balanced Mode**: Enforced per-item caps (8+ units) on individual medicine candidates in `process_medic_job` auto mode and prevented endless fallback production when surplus ethanol was available. Medics now properly recognize when medical stockpiles are full, set `shortfall_reason = "Stockpile Full"`, send the stocked notification tip, and transition to passive medical healing for wounded settlers.
- **Medic Synthesis Material Text Alignment (PR #269)**: Aligned PDA Guide texts, job shortfall tips, and paused status lines to accurately indicate that bandages require vodka/alcohol rather than non-existent standalone cloth items in base Anomaly/GAMMA (`MEDIC_CLOTH = { prt_i_cloth = true }`), preventing player confusion over uncraftable medical materials.
- **Medic Synthesis Stockpile Upper Bound Enforcement (PR #280)**: Updated `is_camp_supply_capped` and `process_medic_job` so synthesized batches cap at available stockpile space rather than producing excess surpluses beyond the target threshold.

### 🎒 Scavenger Expeditions & Offline ALife Simulation (Community / dynz, devinhorowitz):
- **Expedition Scavenger Offline Teleportation & Despawn**: Fixed an issue where scavengers dispatched on distant expeditions (e.g. from Rostok to Pripyat) remained physically standing idle at camp in front of the player. `teleport_scavenger_on_departure` now switches both the scavenger server object and their dedicated single-member `home_squad` offline and teleports both entities directly to the target stash coordinates/level via `sim:teleport_object`. When targeting a different map, the X-Ray engine immediately unregisters their client game object from the active level.
- **Recalled Scavenger Workstation Snapping & Home Squad Re-Pinning**: Updated `recall_scavenger_expedition` and natural expedition completion to invoke `teleport_settler_to_camp_level` and `pin_settler_home_squad`, cleanly snapping returning scavengers back to camp workstations and re-anchoring their home squads to the camp hub.
- **Expedition Squad ALife Online Switching (PR #281)**: Restored squad online simulation flags via `allow_home_squad_online` upon scavenger return, recall, or job reassignment, ensuring returning scavengers physically appear at camp.
- **Quest Stash Protection & Verification (PR #282)**: Extended quest item checks in `is_quest_or_task_stash` using `IsItem("quest", sec)` and repeated checks immediately prior to looting in `loot_and_clear_stash`, preventing scavengers from clearing New Tasks / Tasks QoL quest stashes.
- **Scavenger Perimeter Patrol UI & Radio Reports (PR #267)**: Resolved an issue where `RefreshJobProgress` in the PDA detail panel overwrote active perimeter patrol status with "Waiting for Orders" after 500ms across all four UI themes. Perimeter patrols now consistently display their countdown timer and distinct status in the detail view, and send dedicated perimeter patrol radio notifications rather than referencing non-existent stash tiers.

### 🛡️ Settlement Natural Spawn Point Sweep, Warnings & Defensive Readiness (Community / Seprious, WindWalker, Queen Jadwiga, dynz, devinhorowitz):
- **Proactive Natural Spawn Point Proximity Sweep on Camp Placement**: Added `get_nearby_smart_terrain_hazard` to sweep active Zone smart terrains within the settlement perimeter (~65m) whenever a workbench (`placeable_workshop`) is placed to establish a new camp. If a natural ALife spawn point is detected, the game issues an immediate high-visibility warning notification and audio alert naming the smart terrain and distance, warning players against building living quarters directly over hostile spawn nests (such as the Jupiter railway tunnel UNISG spawn).
- **Spawn Hazard Radio Log Routing (fixes #275)**: Routed the natural spawn point placement warning directly through `camp_send_tip` with `"combat"` category and persistent radio feed registration, ensuring workbench spawn point alerts appear in the settlement radio log alongside other security warnings.
- **PDA Settlement Overview Spawn Hazard Alert Badge**: Added persistent `camp.near_smart` and `camp.near_smart_dist` tracking. If a settlement contains a natural Zone smart terrain inside its borders, the PDA Settlement Manager Overview tab displays a prominent `[! SPAWN HAZARD: NATURAL SPAWN POINT IN PERIMETER !]` threat banner and updates the sector threat rating to `ELEVATED`.
- **PDA Overview Smart Terrain Check Camp Level Alignment (PR #284)**: Updated `get_nearby_smart_terrain_hazard` calls in the PDA Settlement Manager Overview tab across all UI themes to pass `camp.level`, preventing false-positive hazard warnings from other maps.
- **Settlement Natural Spawn Cancellation Hook (fixes #290)**: Added opt-in MCM toggle `block_respawn_in_settlements` ("Block Natural Spawns in Settlements", default off) and `stalker_camp_builder.is_smart_respawn_blocked_in_camp(smart)`. When enabled, natural ALife respawn attempts from Zone smart terrains located within active settlement perimeters are cleanly cancelled via the engine's `on_try_respawn` callback (`flags.disabled = true`) and `se_smart_terrain.try_respawn` wrapper.
- **Settler Defensive Readiness & Breakable Wait Lock**: Changed `combat_ignore_keep_when_attacked = false` in `beh_settler.ltx` and updated `npc_on_hit_callback` so settlers under fire by hostile NPCs or mutants immediately break their stationary `npcx_beh_wait` workstation lock and receive `npcx_beh_hide_in_cover`, allowing them to seek cover, draw weapons, and defend themselves rather than remaining helpless standing targets.
- **Hospitality Buff Description Alignment (fixes #275)**: Corrected `st_buff_hospitality_applied` across English and Russian localization to accurately reflect the buff's actual gradual health and stamina restoration rather than non-implemented carry capacity stats.

### ⚔️ Wilderness Outposts, Rival Skirmishes & Territory Warfare (fixes #289, PR #285):
- **Outpost Skirmish & Seizure Cooldown (fixes #289)**: Added a 6 in-game hour cooldown (`camp.skirmish_cooldown_until`) following camp establishment, hostile seizures, and unoccupied takeovers, preventing outposts from entering rapid, repeated takeover loops and spawning continuous hostile squads.
- **Localized Skirmish & Mayday Alerts (fixes #289)**: Restricted on-screen mayday distress calls and skirmish resolution tips to outposts located on the player's active level or near player settlements. Distant skirmishes across the Zone are now silently recorded to the PDA settlement radio log (`stalker_camp_builder.add_camp_radio_log`), eliminating constant immersion-breaking HUD notifications.
- **Faction Retaliation Raids Implementation (fixes #289)**: Wired the MCM toggle `rival_camp_retaliation_raids` ("Faction Retaliation Raids") and persistent `stalker_camp_builder.faction_retaliation_timers`. Eliminating hostile outposts now queues a counter-expedition timer (2–4 game hours) for the defeated hostile faction to establish a retaliatory outpost, preserved across saves.
- **Mutant Nest Conversion MCM Gating (PR #285)**: Ensured automated conversion of fallen rival camps into active mutant nests strictly honors the `rival_camp_surge_effects` ("Emission Effects & Mutant Nests") MCM setting.

### ⚙️ Multi-Settlement Job Scheduling & Production Pipelines (Community / devinhorowitz):
- **Multi-Settlement Round-Robin Job Loop & Turret Upkeep Scheduling (PR #256)**: Re-structured `update_camp_jobs` block nesting so the round-robin camp advance runs once per update tick rather than once per iteration (preventing even-numbered settlements from being skipped or starved of the global cycle budget). Relocated turret maintenance outside the settler loop so turret checks run once per settlement rather than per settler.
- **Technician WPO Part Repair Restoration (PR #261)**: Exported `gun_parts_worn` to `stalker_camp_builder`, restoring condition and WPO wear evaluation in inventory snapshots so camp technicians properly detect and repair damaged weapon parts in G.A.M.M.A. workbenches.
- **Exact Material Matching for Inventory Snapshots (PR #262)**: Replaced loose substring checks in `get_camp_inventory_snapshot` with the exact section evaluation functions (`is_wood_part`, `is_clean_water`, `is_lamp_battery`, `is_gunpowder`, `is_repair_fee`), preventing poltergeist powder, decorative items, and wooden gear from masquerading as craft materials.
- **Crafter Ammo Stock Cap Synchronization (PR #263)**: Aligned snapshot-based crafter paused checks with `is_camp_supply_capped` rules, respecting order-specific capacity limits (15 for Auto, turret shortfall exceptions) rather than prematurely stalling ammo production.
- **Cook Multi-Container Raw Meat Detection (PR #264)**: Updated `_calc_job_paused_status` for cooks to evaluate total stored raw meat across all settlement storage containers rather than stalling when meat is stored in secondary chests or additional refrigerators.
- **Woodcutter Auto Charcoal Reserve Balance (fixes #271)**: Solved a starvation deadlock where woodcutters on Auto mode never produced charcoal when paired with an active brewer. The job now maintains a 5-bag charcoal reserve for cooking stoves and water pump filters (burning 5-wood batches whenever charcoal < 5 and wood >= 5) before prioritizing wood conservation (10+ parts) for the brewery.
- **Container-Specific Capacity Checks for Producing Jobs (fixes #272)**: Replaced broad camp-wide capacity checks in `_calc_job_paused_status` with section-targeted container queries via `get_auto_sort_target_box`. Producing jobs (scrappers, woodcutters, crafters, cooks, brewers, medics) now pause with "Storage Full" when containers accepting their specific output are full, eliminating runaway item dumping on the ground at the hub.
- **Inventory Snapshot Caching & Zero-Hitch Paused Evaluations (fixes #273)**: Forwarded cached snapshot references directly into `get_job_paused_status` during job update passes, updated snapshot weights in-place during deposits, and integrated `camp._cached_box_weights` into `camp_has_storage_room`, eliminating redundant multi-thousand engine container iterations during active job updates.
- **Water Pump Filter Waiting & Accurate Infrastructure Status (PR #279, PR #288)**: Water pumps now wait for stored filters instead of burning a full cycle interval when filters are absent. Aligned PDA Guide texts, step checklists, and overview metrics to accurately identify valid pump props and display "No Filter in Storage" when filter supplies are depleted.
- **Settler Companion Dismissal Duty Return (PR #283)**: Wrapped `axr_companions.remove_from_actor_squad` to automatically resume paused camp jobs and return dismissed companion settlers to their assigned duties.
- **Hunter and Camp Scavenger Stationing Text Alignment (PR #287)**: Clarified across PDA detail panels, radio reports, and guides that hunters and perimeter patrol scavengers work directly from camp without departing on map-spanning expeditions.

### 📦 Storage Containers, Auto-Sort & Simulation Records (Community / devinhorowitz):
- **Role-Restricted Last-Resort Job Deposits (PR #260)**: Removed `fallback_chest` overrides that bypassed container role restrictions, preventing job deposits from placing unauthorized items (such as metal scrap or ammunition) into refrigerators, stoves, medical cases, or weapon displays.
- **Saved Inventory Snapshot Purge on Load (PR #265)**: Cleared `camp._inv_snapshot` and its `time_global()` timestamp during `load_state`, ensuring fresh inventory snapshots are generated from loaded containers rather than serving future-dated stale snapshots after game reloads.
- **Overview Storage Metrics Local Declarations (PR #266)**: Restored local declarations for `total_items`, `total_weight`, and `max_weight` in `get_camp_storage_metrics`, eliminating nil-arithmetic errors when calculating storage capacity on fallback code paths.
- **Offline Multi-Use Item Integrity & Stored Item Recycled ID Weight Fix (fixes #274)**: Unknown multi-use items found offline without prior verified records now credit 1 use rather than fabricating unrecorded uses; offline container weight calculations strictly verify section matching and restrict lookups to the specific camp's containers, preventing recycled ALife object IDs from skewing box weight calculations; items taken while containers are online are purged from stored item records.
- **Stored-Item Record Retention on Early Scan Termination (PR #276)**: Prevented `camp_iterate_inventory` from purging un-scanned or newly spawned item records when callers terminate inventory searches early.
- **Box Weight Cache Freshness & Invalidation (PR #277)**: Corrected local variable references in snapshot weight population, invalidated cached weights on job consumption, and purged weight caches on game load.
- **Container Child Entity Validation (PR #278)**: Verified `se_obj.parent_id == box_id` before processing container children in `iterate_server_container` and `loot_and_clear_stash`, preventing stale or recycled ALife IDs from affecting container stock.

### 💬 Dialogue, Quests & Settlement Hand-Ins (Community / devinhorowitz):
- **Dialogue Speaker Flow Alternation & Status Follow-up (PR #257)**: Introduced an intermediary player dialogue phrase (`st_camp_status_noted`: "Good to know.") between the camp status report and returning to the order menu, preventing engine speaker-flip glitches from causing settlers to randomly speak player dialogue lines.
- **Scrapper Tool Hand-In Quest Protection & Script Text (PR #258)**: Removed quest toolkits (`toolkit_1`, `toolkit_2`, `toolkit_3`) from `SCRAPPER_TOOL_SECTIONS` so players do not accidentally consume irreplaceable technician quest items. Implemented dynamic `<script_text>` (`st_camp_scrapper_tools_offer`) naming the exact demolition tool or hammer being surrendered.
- **Brewer Camp Drug Kit Deduplication (PR #259)**: Updated brewer drug kit hand-in dialogues and preconditions to check `camp.has_drugkit`, preventing players from inadvertently surrendering duplicate drug kits to brewers in settlements that already have a kit.
- **Electrician & PDA Guide Text Accuracy (PR #268, PR #270)**: Updated PDA settlement guide entries and string tables to clarify that electricians maintain power to existing fixtures rather than recharging loose batteries, and lamps do not provide passive defense rating bonuses. Corrected v1.2.4 changelog descriptions for settler leash behavior and radio logging.
- **FOMOD G.A.M.M.A. Pack Detection (PR #286)**: Added automatic file dependency detection for `items_hf_gadgets_gamma.ltx` in `ModuleConfig.xml`, recommending the G.A.M.M.A. Compatibility Pack when installed.

## v1.2.4 — Comprehensive Simulation Stability, Precision Game Clock, ALife Hardening & Full UI/PDA Polish

### ⏱️ Engine Simulation Clock, Save State Integrity & ALife Scheduling (Community / devinhorowitz):
- **Precision Game Clock to the Second (PR #127)**: Replaced floating-point `game.get_game_time():diffSec(game.CTime())` (which suffered 4,096-second precision quantization, freezing Homestead's clock for ~70 game minutes before leaping ahead) with `game_sec()`, calculating exact whole elapsed seconds from Year 1. Completely normalizes job cycle calculations, sleep bonus detection, and morale timers.
- **Legacy Camp Backup Purge on Load (PR #115)**: Dropped frozen pre-1.1.7 `m_data.homestead_backup` tables from older saves upon load instead of erroneously restoring them, eliminating phantom outpost respawns, duplicate furniture accumulation, and null-pointer crashes during member registration.
- **Primary Camp Chest Persistence (PR #140)**: Deferred container validation in `normalize_camps` until ALife server objects are fully loaded, ensuring player-designated main storage boxes (`camp.primary_chest_id`) are preserved across save loads and level transitions rather than being reset.
- **Modded Exes Physics Furniture Unregister Hook (PR #126)**: Added a listener for `server_object_on_unregister` (provided by xray-monolith modded exes) to immediately prune picked-up or destroyed physics objects (O_PHYSIC) from settlement structures, settler workstation claims, and outpost decor records.
- **Engine Squad Group ID Preservation (PR #87)**: Removed erroneous Lua assignments of `group_id = 65535` across settler transfer, dismissal, and recruitment routines, preventing script desynchronization from the underlying engine squad member hierarchy.
- **Settler Home Squad Simulation Pinning (PR #131)**: Fixed an issue where settler home squads drifted away from settlements across the Zone by having `get_script_target` return `self.id`, restoring squad anchor pins on game load, and synchronizing offline squad coordinates with settlers during teleports and recalls.
- **Individual Settlement Raid Cooldown Grace (PR #153)**: Made settlement founding grace periods local to the newly established camp rather than pushing global raid timers forward Zone-wide, ensuring existing established settlements remain subject to normal raid schedules.
- **Online Binder Squad Cache Invalidation on Member Removal (PR #199)**: Added `forget_binder_squad` to clear an online stalker's cached motivator squad (`self.squad`) when Homestead removes them from a squad (such as during solo recruitment, job changes from companion duties, companion sweeps, or dismantle). Prevents `xr_motivator.script` from calling `commander_id()` on released engine squad pointers and triggering unhandled memory faults.
- **Settler Entity Validation Guard for Dispatch & Anchoring (PR #200)**: Added `survivor_se(npc_id, survivor)` verifying that an ALife ID still holds an active stalker before dispatching scavengers to stashes or anchoring settlers to smart terrains. Prevents fatal crashes in `alife_update_manager.cpp` and `register_member` caused by stale IDs from NPCs that were despawned or released by external mods (e.g. G.A.M.M.A. Dynamic Despawner).
- **Invincible Settler Pending Respawn Persistence (PR #208)**: Recorded pending respawns in `camp.respawning` when an Invincible Settler dies rather than keeping them solely inside transient 0.5-second time event closures, ensuring settlers that die right before a save or level transition respawn reliably upon load via `verify_and_heal_settlers`.
- **Deferred Game Time Initialization for Job Clocks on Load (PR #211)**: Removed premature `game.get_game_time()` initialization from `load_state` (which previously evaluated against the uninitialized Year 2018 engine clock before ALife storage finished loading), allowing `rebase_one_survivor_job` on the first update to initialize missing clocks from the authentic loaded save time. Prevents returning scavengers from erroneously paying out decades of backlog cycles.
- **Behavior Scheme Action Binding for Fresh Settlers (PR #213)**: Allowed `xr_logic.assign_storage_and_bind` to initialize `st.beh` during `setup_settler_beh_logic` rather than pre-allocating an empty table, ensuring the engine action and evaluator are properly bound to the GOAP planner. Eliminates an ALife action lock that caused newly recruited settlers to freeze at their station in a neutral pose without playing idle/work animations until the next reload.
- **Home Squad Cache Validation on Member Group ID (PR #222)**: Ensured `anchor_settler_to_smart` only reuses cached home squads if the settler's `group_id` matches the squad ID, and cleared the cached squad reference in `mark_settler_companion`. Prevents recycled or empty squad IDs from erroneously capturing unrelated single-member simulation squads during settler recalls.

### 👥 Settler Management, AI Navigation, Dialogue & Companion Interop (Community / devinhorowitz):
- **Vanilla Companion Hire Dialogue Integration (PR #132)**: Intercepted `axr_companions.add_to_actor_squad` so settlers recruited through standard game companion dialogue cleanly pause their settlement duties (`job = "companion"`), preventing camp soft-leash logic from fighting companion following orders.
- **Vanilla-Hired Settler Companion Sweep Protection (PR #97)**: Extended ghost companion migration sweep protection (Protection B) to companion settlers recruited via vanilla dialogue, preventing them from being unlinked from the player party during level transitions.
- **Station Post Preservation for Companions (PR #134)**: Prevented the PDA "Position Here" command from forcing stationary `beh@settler` logic onto active companions, storing their assigned post for settlement return while allowing them to continue following the player freely.
- **Companion-Only Banishment Tracking (PR #133)**: Ensured `banish_npc` only places active companions on the banished companions list, preventing standard settlers who were dismissed or reassigned from being permanently blacklisted from future companion recruitment.
- **Settlement Dismantling Banishment Scope (PR #110)**: Limited banished list recording during `dismantle_camp` strictly to active companion settlers, allowing non-companion settlers to freely integrate into Zone simulation squads.
- **Low-Morale Deserter Simulation Reassignment (PR #105)**: Replaced restrictive offline switch locks on low-morale camp deserters with clean settler logic purges and smart terrain reassignments via `reassign_freed_settler_to_smart`.
- **Freed Settler Native Faction Squad Assignment (PR #107)**: Corrected `reassign_freed_settler_to_smart` to spawn simulation squads matching the freed settler's native faction rather than defaulting everyone to Loner stalkers.
- **Online Binder Squad Hand-off for Freed Settlers (PR #108)**: Updated the engine binder squad cache for settlers freed while online in front of the player, allowing them to depart immediately with their new simulation squads without waiting for a reload.
- **Freed Settler Behavior Logic Restoration on Net Spawn (PR #109)**: Purged persistent `beh@settler` logic and infoportions from freed stalkers during net spawn, ensuring they resume authentic ALife behaviors upon re-entering the simulation.
- **Banished Record Name Validation Guard (PR #98)**: Guarded ghost companion checks against legacy boolean `true` records in `banished_companions`, preventing recycled ALife IDs from inadvertently stripping companion status from unrelated stalkers.
- **Settler Name Restoration (PR #156)**: A settler re-created by `restore_missing_settler` keeps its name and faction; one respawned by Invincible Settlers keeps its name and joins the camp's dominant faction. The name is set on the server object, so saves and level changes keep it.
- **Survivor Cap Enforcement on Settlement Transfers (PR #157)**: Enforced the configured MCM "Max Survivors" population ceiling during cross-settlement transfers in the PDA, closing an exploit that bypassed recruitment limits.
- **Combat & Danger State Leash Suppression (PR #94)**: Prevented `enforce_settler_leash` from overriding combat pathing and danger reactions, stopping settlers from nonchalantly walking toward the hub while engaged in active firefights.
- **Assigned Guard Post Priority over Soft Leash (PR #95)**: Prevented soft-leash tethering from pulling settlers away from their custom guard and workstation posts, wherever the posts are inside the camp boundary.
- **Settler Idle Wander Stabilization (PR #96)**: Throttled idle activity destination rolls so settlers pick a camp activity (stove, radio, instrument, or relaxation spot) and remain there for the idle period rather than twitching between targets every second.
- **Refugee Navigation Endpoint Adjustment (PR #100)**: Routed incoming refugees to stand and wait in front of the settlement hub rather than walking directly into the collision boundary of the workshop table.
- **Refugee Lifecycle & Despawn Cleanup (PR #116)**: Properly despawned departing refugees via `safe_release_manager`, pruned dead refugees from tracking tables, and prevented recycled ALife IDs from triggering phantom releases or zero-cost recruitment.
- **Restored Settler Stationing Dialogue Commands (PR #161)**: Reconnected missing dialogue phrases in `manage_camp_dialog`, allowing players to command any settler to hold their current position as a permanent station or resume standard workstation duties directly through conversation.
- **Recruitment Roll Cache Purge Isolation (PR #201)**: Preserved the active NPC's recruitment roll when `get_recruitment_roll` purges the 100-entry roll cache, preventing race conditions where precondition checks evaluate conflicting roll results and cause fatal `PhraseDialog` assertion crashes ("No available phrase to say").
- **Vanilla Rehire Companion Banishment Clearing (PR #207)**: Updated the `axr_companions.add_to_actor_squad` dialogue wrapper to automatically remove rehired stalkers from `banished_companions`, preventing previously banished settlers recruited through standard companion dialogue from being stripped by ghost companion sweeps on the next save load.
- **Dialogue Functor Tag Migration to `<script_text>` (PR #210)**: Replaced unread `<text_functor>` tags with engine-supported `<script_text>` tags across recruitment and settlement dialogues. Restores dynamic camp selection phrases with sign-on fees ("Sure, send me to Cordon Camp (2500 RU)") and makes the "Return to your settlement duties" dialogue topic visible.
- **Separation Sweep Hub Clearance without Post Overwrites (PR #212)**: Prevented `separation_sweep` (which nudges settlers standing within 1.3m of the hub after teleports and loads) from overwriting `assigned_pos`. Settlers without dedicated job furniture are repositioned cleanly without being falsely locked into permanent "Position: Custom (assigned)" stations.
- **Camp Medic Integration with Body Health System (PR #217)**: Routed camp medic paid treatments through base game dialogue actions (`dialogs.heal_actor_injury*`), ensuring broken limbs and body part damage under G.A.M.M.A.'s Body Health System (`zzz_player_injuries`) are fully healed rather than attempting to call undefined `heal_all_limbs` functions.
- **Camp Trader Dialogue Speaker Resolution & Window Opening (PR #218)**: Resolved speaker arguments in `start_camp_trader_trade`, ensuring clicking "I want to trade supplies" reliably opens trading computer interfaces or vanilla trade menus instead of closing the dialog immediately without opening a trade window.
- **Free Camp Reassignment for Owned Settlers (PR #219)**: Waived recruitment rank fees and camp defense rating requirements when transferring or re-recruiting the player's own companion settlers via dialogue, and preserved custom settler names and job directives across dialogue recruitment.
- **Station Assignment Out-of-Bounds Dialogue Feedback (PR #220)**: Added explicit dialogue feedback (`st_pda_position_too_far`) when attempting to station a settler outside the camp boundary radius via "Hold this position as your station", preventing silent assignment failures.
- **Legacy Companion Job Suppression on Update (PR #221)**: Detected `npcx_is_companion` info portions in `npc_on_update` to pause settlement duties for companions hired before PR #132, preventing camp soft-leash code from repeatedly pulling them away from the player.
- **Server Entity Character Name Synchronization on Rename (PR #234)**: Updated `rename_survivor` to set the settler's character name directly on the server object (`set_character_name`), ensuring custom names chosen in the PDA appear on in-game crosshair target labels and dialogue windows upon subsequent spawns.
- **Unseen Despawn Guard for Refugees & Traveling Traders (PR #239)**: Added distance and offline checks before releasing departing refugees and caravan merchants, preventing NPCs from abruptly vanishing mid-conversation or in plain sight of the player.
- **Faction Safety Refusal Feedback in Recruitment Dialogue (PR #242)**: Added dedicated dialogue response `st_recruit_camps_refuse` ("None of your settlements with free beds is safe for me: my faction's enemies either control the area or already live there.") when available settlements refuse a stalker due to faction hostility, properly distinguishing faction conflicts from lack of beds.

### 🏕️ Outposts, Convoys, Dynamic Events & Raids (Community / devinhorowitz):
- **Allied Reinforcement Retention & Defense Stations (Fixes #102)**: Fixed a bug where allied reinforcements dispatched to an outpost in distress were instantly recalled back home within a second due to their home camp's 16m leash; allied squad members now rush in danger readiness to the defending camp, hold tactical defensive positions around the outpost for the 2-minute defense duration or until the threat is resolved, and cleanly return to their home camp once the mission concludes.
- **Zone-Wide Settlement Clearance for Outposts (PR #138)**: Enforced minimum distance checks against player settlements across all Zone levels when generating dynamic outposts, preventing rival camps from spawning on top of remote player bases.
- **Immediate Outpost Abandonment on Garrison Elimination (PR #91)**: Marked outposts as abandoned immediately when their last garrison squad unregisters in `server_entity_on_unregister`, eliminating delayed or ghost occupied states.
- **Outpost Fortification Tier Retention on Skirmish (PR #154)**: Preserved upgraded outpost tiers and existing barricade structures when an outpost changes faction ownership following a skirmish takeover.
- **Garrison Squad Spawn Alignment at Guard Posts (PR #155)**: Initialized new garrison squads directly at their designated guard stations rather than spawning them stacked on top of the blue chest container.
- **Zombified Outpost Progression & Convoy Freezes (PR #136)**: Suspended tier upgrades, resupply deliveries, courier dispatches, and PDA broadcast announcements for outposts overtaken by zombified stalkers, treating them consistently with mutant nests.
- **Outpost Heat Pack Smart Terrain Assault Targeting (PR #135)**: Routed mutant heat packs directly toward the outpost's smart terrain rather than the garrison squad ID, allowing the ALife simulation to actively march mutant packs into outposts to assault the defenders.
- **Teardown Cleanup for Dead Convoys & Heat Packs (PR #89)**: Cleaned up recycled squad IDs for destroyed couriers and heat packs in `server_entity_on_unregister`, preventing outpost dismantlement from releasing unrelated ALife objects.
- **Persistent Script Targets for Convoys & Heat Squads (PR #90)**: Stored `scripted_target` properties in saved squad state, ensuring supply couriers and mutant heat packs retain their destinations after saving and loading.
- **Recruited Courier Convoy Decoupling (PR #88)**: Unlinked friendly couriers from active convoy tracking upon recruitment as companions, preventing them from being automatically despawned upon arrival at their destination.
- **Proximity Distance Guards for Convoys & Heat Packs (PR #101)**: Prevented supply couriers and mutant heat packs from abruptly spawning or despawning within view of the player.
- **Dynamic Switch Distance Checks for Outposts & Convoys (Fixes #174)**: Replaced hardcoded 150m (22,500m²) distance checks across outpost events (zombification, mutant nest transformations, skirmish garrison takeovers, abandoned camp repopulation, mutant heat pack spawns, and supply convoys) with dynamic engine switch distance (`math.max(150, alife():switch_distance())`). In modpacks like G.A.M.M.A. with 450m ALife switch distance, squads between 150m and 450m are online; this change prevents NPCs from abruptly popping in, transforming, or vanishing in plain sight within the player's online sphere and scope view.
- **Safe Outpost Furniture Teardown Array Iteration (PR #92)**: Isolated decoration release loops from in-place unregister array modifications in `camp.decorations`, preventing skipped furniture pieces during outpost removal.
- **Exact Section Validation for Stored Outpost Decor (PR #99)**: Verified recorded section strings before acting on stored outpost furniture IDs during release and ground-snapping passes, protecting unrelated player objects from accidental deletion.
- **Rival Squad Script Hold Release on Companion Recruitment (PR #93)**: Properly invoked `release_rival_hold` before validating garrison squads, ensuring recruited outpost guards have their rival AI locks cleared cleanly.
- **Persistent Raid Targets & Abandonment Resolution (PR #139)**: Raiders keep heading for the player across a save and load. A raid ends when the player leaves the camp's level; the raiders stop following and stay where they are.
- **Mutant Migration Event Direct Actor Targeting (PR #85)**: Re-routed mutant migration hordes to target the player directly rather than the physical workshop hub object, resolving fatal nil-value engine crashes in `on_reach_target`.
- **AI Mesh Validation for Mutant Migration Spawns (PR #137)**: Validated candidate spawn coordinates against the level AI graph, preventing mutant migration hordes from defaulting to the settlement hub and spawning inside camp workbenches.
- **Authentic Trade Caravan Departure Lifecycle (PR #117)**: Routed departing caravan traders through `safe_release_manager`, ensuring traveling merchants actually pack up and leave when their stay concludes.
- **Automated Caravan Departure on Settlement Teardown (PR #118)**: Automatically dismissed active caravan traders when a settlement is dismantled or its hub workbench picked up.
- **Idle Settler Leash Slider & Rival Camp Survivor Cap Enforcement (Fixes #255)**:
  - **Idle Settler Leash Slider (MCM 27)**: Removed the artificial 25m floor in `enforce_settler_leash` (`math.max(25, ...)` -> `math.max(3, cfg.npc_leash_radius or 10)`), allowing the slider's full 3–50m range to take effect for idle wander soft-leashing. Updated English and Russian MCM tooltips to reflect that idle settlers are walked back when straying past the configured leash radius.
  - **Max Survivors for Rival Camps (MCM 88)**: Connected the previously unused `max_survivors_rival_camp` MCM setting (range 1–10, default 5) via `enforce_rival_camp_survivor_cap`, pruning excess squad members through `squad:remove_npc` and releasing empty extra squads across outpost generation, stronghold reinforcement, tier 3 upgrades, faction takeovers, and periodic outpost maintenance (safely deferred when the player is nearby).
- **Off-Level Mutant Heat Pack Incursions for Outposts (PR #183)**: Allowed outpost mutant heat packs to generate while the player is on another map, routing packs to the outpost's smart terrain to ensure dynamic outpost combat and attrition continue across the Zone.
- **Single-Courier Outpost Throttling & Offline Delivery (PR #184)**: Restricted tier 2 outposts to one active supply courier at a time and allowed couriers exceeding their 2-hour duration to complete deliveries offline, preventing courier squads from stacking up indefinitely while the player remains nearby.
- **Outpost Event Distance Guard Expansion to Offline Radius (PR #191)**: Extended `is_player_near` outpost event guards to the engine offline radius (`mmax(150, switch_distance) * (1 + switch_factor)`), preventing couriers and garrisons within 450-495m from transforming, zombifying, or despawning while visible in player scope view.
- **Out-of-Sight Teardown for Decayed Outposts (PR #192)**: Replaced the hardcoded 60m distance check on abandoned outpost decay with full engine switch distance verification, preventing cleared outpost ruins and containers from vanishing abruptly in the player's view.
- **Outpost Container & Decor Isolation from Neighboring Settlements (PR #202)**: Filtered out outpost chest and decoration IDs from settlement structure scans and storage auto-routing, preventing newly founded settlements near outposts from adopting outpost furniture and losing stored items during outpost decay.
- **Settlement Proximity Exclusion for Heat Packs & Couriers (PR #223)**: Prevented mutant heat packs and rival supply convoys from spawning within or targeting smart terrains located inside player settlements, and cleared scripted targets on any packs that wander into player camps.
- **Inhabited Base Blacklist for Dynamic Outposts (PR #224)**: Excluded smart terrains listed in `[populated_smarts]` (such as Rookie Village, the 100 Rads bar, Yanov, and Skadovsk) from candidate dynamic outpost locations, preventing hostile garrisons and mutant packs from overtaking major faction bases.
- **Camp Teardown Raid Termination & Single Raid Concurrency (PR #225)**: Added `end_camp_raid` to drop the "actor" scripted target from active raiders when a settlement is dismantled, and prevented multiple overlapping raids from triggering simultaneously on the same camp.
- **Immediate ALife Target Reset for Released Outpost Garrisons (PR #226)**: Cleared `assigned_target_id`, `current_target_id`, and `current_action` in `release_rival_hold`, allowing garrisons whose time has expired to resume authentic Zone ALife simulation immediately rather than lingering in abandoned camps for 2-8 hours.
- **Out-of-Sight Outpost Upgrades & Offline Loot Stocking (PR #227)**: Deferred visual outpost tier upgrades and reinforcement squad spawns until the player is beyond switch distance, and created tier upgrade loot directly in offline server chest objects so outposts upgrade and stock properly across the Zone.
- **Tier 3 Auxiliary Squad Spawns on Stronghold Capture (PR #240)**: Ensured faction takeovers and skirmish victories at Tier 3 strongholds spawn the second auxiliary garrison squad for the new owner, maintaining proper garrison strength after ownership changes.
- **Offline Ground-Snapping Pass for Outpost Containers (PR #241)**: Deferred outpost ground-snapping completion flags until containers are processed while offline, preventing outpost chests and barricades from freezing at unadjusted elevations above or below ground.

### 🛠️ Settlement Jobs, Workbenches & Resource Automation (Community / devinhorowitz):
- **Changelog Wording Audit & Documentation Alignment (Fixes #198)**: Audited v1.2.4 changelog entries against code implementations:
  - Aligned Water Pump (#175), Settler Name Restoration (#156), and Persistent Raid Targets (#139) descriptions with authentic runtime behavior and engine mechanics.
  - Removed duplicate entry for Primary Camp Chest Persistence (#140).
  - Synchronized release version tags in `fomod/info.xml` and Modern PDA theme script to v1.2.4.
  - Cleaned up obsolete non-existent placeable section keys in structure type exact table.
- **Settler Tool Donations & Woodcutter Directives Dialogue (Fixes #196)**: Added full dialogue interactions and job assignments for Woodcutters, Brewers, and Scrappers so tool multipliers promised in the PDA Guide can be unlocked in-game:
  - **Woodcutter Axe Donation & Directives**: Added dialogue options allowing players to hand a felling axe (`wpn_axe`, `wpn_axe2`, `wpn_axe3`) to the woodcutter, setting `survivor.has_axe` and unlocking the 2x timber yield / +2 charcoal production boost alongside the `[Axe: 2x Boost]` PDA badge. Added harvest directive dialogue trees (`camp_woodcutter_dialog` and `manage_camp_dialog`) so players can change woodcutter harvest directives (Balanced Auto, Raw Timber, or Kiln Charcoal) directly through conversation as well as via the PDA.
  - **Brewer Distillery Kit Delivery**: Added dialogue option allowing players to hand a chemical drug-making kit (`itm_drugkit`) to the settlement brewer, granting the 2x vodka distillation boost (`[Distillery Kit: 2x Boost]`). Updated `process_brewer_job` and PDA status badges across all themes to also recognize settlement-level drug kits (`camp.has_drugkit`), ensuring kits delivered to the camp or medic benefit distilling operations.
  - **Scrapper Demolition Tools Hand-in**: Added dialogue option allowing players to deliver heavy demolition tools (sledgehammer, crowbars, toolkits, or repair kits) to the scrapper, setting `survivor.has_tools` and activating the 2x scrap / +67% fastener salvage bonus and `[Demolition Tools: 2x Boost]` PDA badge.
  - **Job Assignment via Dialogue & Transfer Retention**: Added missing Woodcutter, Brewer, and Scrapper job assignment options to `manage_camp_dialog`, and preserved `has_axe`, `has_drugkit`, and `has_tools` status across settlement transfers in `recruit_npc_to_camp`.
- **Job Yield Rebalancing & PDA Guide Alignment (Fixes #103)**: Rebalanced MCM yield slider maximums (wood/scrap 15-20, fasteners 10-15, craft multiplier 3x) and clamped per-cycle deposits for Woodcutters, Brewers, and Scrappers to prevent runaway item generation; capped catch-up cycles to 2 per tick to eliminate engine hitches when returning from away levels while smoothly preserving accumulated time; and updated English and Russian PDA Guide entries (`st_guide_s3i_body`, `st_guide_s3j_body`, `st_guide_s3k_body`) to accurately reflect dynamic MCM sliders and tool multiplier mechanics.
- **Woodcutter Kiln Fuel Batching & Brewery Supply Priority (Fixes #249)**: Fixed an issue where the Woodcutter on the default Auto-Rotate directive perpetually starved the camp Brewer of wood parts by burning all stored wood (up to 15 pieces) for 3-5 bags of charcoal before the brewer could accumulate the 10 wood parts needed to distill vodka:
  - Capped kiln cycles to consume a fixed batch of up to 5 wood scraps (producing 3-5 bags of charcoal, +2 with an axe) rather than deleting all available wood scraps in storage.
  - When the Woodcutter is on the Auto directive in a settlement with an active Brewer, the kiln cycle prioritizes the brewery supply chain by harvesting timber instead of burning charcoal whenever storage holds fewer than 10 wood parts. Once 10+ wood parts are stored, kiln cycles resume burning 5-wood batches into charcoal, allowing both jobs to produce steadily without starvation.
- **Exact Material Matching for Crafter Scrap & Medic Cloth (Fixes #252)**: Replaced loose substring matching for ammunition crafting scrap and medical synthesis cloth with exact section matching:
  - **Crafter Scrap (`CRAFT_SCRAP = { prt_i_scrap = true }`)**: Confined Crafter metal scrap consumption (`process_ammo_crafting`, paused check, and inventory snapshot) strictly to `prt_i_scrap`, eliminating substring matches (`"scrap"`, `"casing"`, `"bullet"`) that erroneously burned player Ammo Maker casings (`casing_p`, `casing_s`, `casing_r5`, `casing_r7`), throwing bolts (`bolt_bullet`), and full 10-15 round boxes of AP ammunition (`bullet_pistol_ap`, `bullet_shotgun_ap`, `bullet_r5_ap`, etc.) as 1x scrap metal.
  - **Medic Cloth (`MEDIC_CLOTH = { prt_i_cloth = true }`)**: Confined Medic cloth consumption (`process_medic_job`, paused check, and inventory snapshot) strictly to `prt_i_cloth`, preventing substring matches (`"fabric"`, `"textile"`, `"prt_i_paper"`) from consuming valuable outfit/helmet repair materials (`prt_o_fabrics_1` through `_4`) or water pump filter paper (`prt_i_paper`) to synthesize cheap bandages instead of utilizing brewer-distilled vodka.
  - **Snapshot Powder Cleanup**: Removed erroneous `or s == "prt_i_scrap"` check from `snapshot.has_powder` in `get_camp_inventory_snapshot`, ensuring gunpowder presence evaluates only against authentic powder sections.
- **Camp Specialization Bonus Integration across Jobs & Logistics (Fixes #172)**: Integrated active settlement specializations into job handlers so choosing specialized camps grants their full promised bonuses alongside the -25% defense penalty:
  - **Agricultural Farmstead**: Cooks gain +50% food meal yield (`process_cook_job`), water pumps generate +50% flask deposits (`update_camp_jobs`), and Hunters scale smoothly without artificial caps (`spawn_hunted_meat`).
  - **Tech Workshop**: Crafters generate +50% ammunition output (`process_ammo_crafting`), technicians gain +50% repair condition restored per cycle, and novice-to-master repair rounds scale with probabilistic rounding (`process_gear_repair`).
  - **Medical Clinic**: Medics gain +100% (2x) medical supply synthesis yield, cleanly compounding with drug-making kits (`process_medic_job`).
  - **Scavenger Hideout**: Scavengers gain +50% loot items per wilderness stash and +50% items recovered from dispatched expeditions (`spawn_scavenged_loot`, `deposit_expedition_haul`).
- **Settler Work Clock Reset on Resumption (PR #129)**: Reset job start timestamps when settlers resume duties after expeditions or companion service, preventing massive backlogs of accumulated cycles from paying out instantly.
- **Functional Level-Based Night Shift Modifiers (PR #130)**: Corrected hour retrieval in `get_time_of_day_mult` to query `level.get_time_hours()`, activating intended night-shift modifiers (+20% scavenge/medic speed, -20% cook speed between 22:00 and 05:00).
- **Online-Only Gear Repairs for Settlement Technicians (PR #120)**: Restricted technician repair cycles to online weapons and armor with valid game objects, preventing away camps from draining repair fees without restoring gear condition.
- **Technician Repair Compatibility with Workshops (PR #121)**: Keyed technician repair checks to the linked `workshop_stash` container, allowing settlers to repair damaged equipment placed inside Hideout Furniture Workshop stations.
- **Workbench Upgrade Toolkit Turn-in Protection (PR #123)**: Restricted technician toolkit turn-ins strictly to workbench upgrade kits (`itm_basickit`, `itm_advancedkit`, `itm_expertkit`), protecting vanilla story and quest toolkits from accidental consumption.
- **Technician Toolkit Upgrade Gating & Morale Retention (Fixes #171)**: Hooked `inventory_upgrades.get_global_precondition_functor` and `inventory_upgrades.prereq_functor_a` to dynamically gate camp technician upgrades behind delivered toolkits (Basic -> Tier 1, Advanced -> Tier 2, Expert -> Tier 3) and display missing-toolkit requirements instead of leaving all upgrade tiers unlocked by default; updated `deliver_toolkit` to record `camp.toolkits[tier]` alongside `camp.tech_toolkit_tier`; updated `get_camp_morale` to recognize either format so the +10 morale bonus persists across hourly recalculations; and added camp-delivered checks to dialog preconditions to prevent accidental duplicate toolkit deliveries.
- **Workstation Claim Validation Against Settlement Structures (PR #125)**: Verified settler workstation assignments against active entries in `camp.structures`, clearing stale workstation claims when furniture is removed.
- **Conditional Battery Usage for Electricians (PR #142)**: Updated electrician maintenance logic to only consume batteries when camp lamps actually require refueling, eliminating battery waste on fully powered lighting.
- **Stockpile Surplus Cap for Master Cook Kolbasa (PR #158)**: Included `kolbasa` under food stockpile surplus caps, properly pausing Master-tier cooks once 15 prepared meals are stored.
- **Technician Dialogue Phrasing & Window Exit Polish (PR #150)**: Defined missing dialogue string `st_manage_camp_close` and ended conversations cleanly prior to opening technician crafting interfaces.
- **Medic Treatment Affordability Preconditions (PR #151)**: Added actor money preconditions to paid medical treatment options, preventing medics from confirming treatments when the player lacks sufficient funds.
- **Water Pump Prototype Cleanup & Mod Collisions (Fixes #175)**: Removed the unused `[itm_water_pump]` and `[placeable_water_pump]` definitions, their strings, and the `bind_water_pump_furniture.script` stub. The pump's model (`dynamics\placeable\kolonka.ogf`) never shipped, and until v1.2.2 stopped traders stocking the pump, a restock that created one crashed the game. The section names and the stub matched Fillable Canteens 2.0's water pumps: a section defined twice without `!` stops the game at startup, and the stub replaced Fillable Canteens' binder. Camp water comes from placed metal barrels, sinks and bidons (`placeable_barrel_metal`, `placeable_sink`, `placeable_bidon`).
- **Technician Camp Resolution on Toolkit Delivery (PR #176)**: Resolved the technician's home settlement directly via `get_technician_camp` during toolkit deliveries and verified active camp presence before consuming kits, preventing toolkits from being lost when speaking to technicians working at peripheral benches.
- **Accurate Camp Morale Rescoring on Kit Deliveries (PR #179)**: Rescored camp morale via `get_camp_morale` upon delivering toolkits or drug-making kits rather than adding arbitrary bonus points to stored morale variables, preventing temporary upgrade price discount exploits.
- **Single-Kit Consumption & Camp Matching for Medic Drug Kits (PR #180)**: Matched drug-making kit deliveries directly to the medic's assigned settlement via `get_drugkit_camp` and closed dialogue offers once delivered, protecting surplus kits in player inventory from being consumed.
- **G.A.M.M.A. Upgrade Rank Pricing Map Integration for Technicians (PR #181)**: Integrated G.A.M.M.A.'s upgrade tier mapping (columns a/b = Tier 0, d = Tier 1, c = Tier 2, e/f = Tier 3) when `upgrade_rank_pricing.script` is active, ensuring camp technicians do not lock basic tier modifications that require no toolkits at vanilla mechanics.
- **Water Structure Morale Bonus for Placed Barrels & Sinks (PR #182)**: Counted `water_pump` typed furniture (`placeable_barrel_metal`, `placeable_sink`, `placeable_bidon`) toward settlement water points in `get_camp_morale`, allowing camps with placed barrels and sinks to achieve the 50/60 morale required for hospitality eating and sleeping buffs.
- **Hunter Tier Scaling Ceiling Alignment (PR #186)**: Clamped the hunter settler tier multiplier to 1.5 before compounding with Farmstead specialization bonuses, preventing runaway meat harvests from master-tier hunters.
- **Single-Application Workshop Repair Specialization Bonus (PR #187)**: Applied the Tech Workshop +50% repair bonus strictly to condition restored per cycle rather than compounding across both repair rounds and condition increments.
- **Technician Toolkit Delivery Dialogue String Corrections (PR #188)**: Removed misleading claims of "faster repairs" from English and Russian toolkit delivery strings (`st_tech_toolkit_delivered`, `st_camp_tech_tools_done`), accurately reflecting that delivered kits unlock modification tiers and grant morale.
- **Wood Part Gating for Brewery Vodka Distillation (PR #193)**: Required at least 10 wood scraps before consuming clean water in `process_brewer_job`, setting status to "Need Wood" when timber is lacking and preventing water waste on stalled distillation runs.
- **MCM Craft Output Multiplier Strict Clamping (PR #194)**: Clamped the Craft Output Multiplier slider value to 3.0 within script configuration, enforcing intended yield ceilings on older save files and updating tooltips to accurately reflect affected production jobs.
- **Destroyed Entity Filtering in Online Container Job Iterations (PR #214)**: Skipped items whose server objects were destroyed earlier in the same update tick during online container walks, preventing single items from satisfying multiple material consumption requirements (such as timber burns or vodka syntheses).
- **WPO Internal Weapon Part Wear Gating for Technicians (PR #215)**: Integrated G.A.M.M.A. Weapon Parts Overhaul (`item_parts.get_parts_con`) into technician repair eligibility checks, allowing settlement technicians to service guns with worn internal parts even when overall weapon condition reads high.
- **Radio Morale Bonus for Settlement Guitars & Receivers (PR #232)**: Counted placed guitars (`placeable_dev_guitar`) and receiver furniture typed as `radio` toward camp morale in `get_camp_morale`, granting the intended +15 morale bonus for camp entertainment.
- **Stove Tier Retention when Cook Fuel is Disabled (PR #233)**: Allowed stoves to cook higher-tier meals when "Cook Requires Fuel" is disabled in MCM, skipping fuel requirements without demoting cooked recipes to basic campfire meals.

### 🎒 Scavenger Logistics, Stashes & Container Management (Community / devinhorowitz):
- **Pure Game-Clock Timing for Scavenger Expeditions (PR #128)**: Removed dual-clock real-time fudge factors from scavenger trips, preventing emission/psi-storm time acceleration from instantly completing active expeditions.
- **Camp Scavenger Perimeter Patrol Rebalance & PDA Status Timer (Fixes #250)**: Fixed an exploit and UI discrepancy where a scavenger waiting at camp generated an entire full G.A.M.M.A. rare stash (weapons, armor, and expert toolkits) every cycle while the PDA displayed them as idle with no progress or timer:
  - Rebalanced camp scavenger perimeter patrols (`spawn_scavenged_loot`) to gather minor camp debris and salvage (1-2 items per cycle as configured by `scavenge_min_items` and `scavenge_max_items`, scaled by rank and Hideout specialization) from common level loot tables or `scavenge_loot_table`, eliminating unearned world-tier stashes and toolkit drops while awaiting orders.
  - Enabled countdown timer and progress tracking in `get_job_progress` and `get_job_time_remaining` for scavengers on camp patrol, activating the live PDA status displays across all themes (`Scavenger: Patrolling Camp (x% - ym zs remaining)` / `Status: Local Area Scavenging & Perimeter Patrol`) while maintaining instant availability for wilderness expeditions.
- **Automatic Scavenger Recall on Camp Dismantle (PR #106)**: Automatically terminated and recalled active scavenger expeditions when a settlement is dismantled, preventing orphaned expedition loops.
- **Multi-Use Item Use Retention During Online Stash Scans (PR #119)**: Preserved tracked remaining uses for items stored in offline containers when scanning settlements with online workshop stashes, preventing multi-use rations and fuel from being deleted on single use.
- **Player Backpack Exclusion from Settlement Storage (PR #122)**: Excluded player-deployed backpacks (`inv_backpack`) from camp storage registration, protecting personal stash bags from settler consumption and auto-sorting.
- **Player-Created Stash Tracking Retention (PR #86)**: Preserved `m_data.player_created_stashes` entries during entity unregistration, allowing external stash pickup scripts to correctly return deployed backpacks.
- **Treasure Cache Deregistration on Outpost Chest Release (PR #124)**: Cleared G.A.M.M.A. `treasure_manager.caches` records when outpost chests are released or decayed, preventing recycled ALife IDs from generating invalid quest stash locations.
- **Stash Weight Capacity Enforcement & Multi-Container Overflow Routing (Fixes #173)**: Integrated Hideout Furniture and G.A.M.M.A. stash weight capacities (`capacity` in LTX) into Auto-Sort and job resource deposits:
  - Added `get_box_capacity`, `get_box_current_weight`, and `box_has_room_for` utilities that calculate online and offline container weight to evaluate capacity thresholds.
  - Refactored `get_auto_sort_target_box` to track all candidate settlement containers per category (multiple ammo sumkas, gun cases, medicine boxes, etc.) and route incoming items to the first container of that type with available capacity before spilling over to general chests.
  - Updated 1-click Auto-Sort (`smart_dump_to_camp_storage`) with an in-memory batch weight cache to stop transferring items once containers reach their capacity limits, notifying the player of skipped items rather than overfilling capped boxes.
  - Passed item weight during settler job deposits (`deposit_item_to_camp`) so automation cycles seamlessly spread production across available settlement containers.
- **Storage Capacity Full Job Gating & Hub Overflow Dropping (Fixes #195)**: Fixed an issue where settlement jobs and expeditions continued overfilling the main chest indefinitely once all containers in a settlement reached maximum weight capacity:
  - Added `camp_has_storage_room` checking container capacity thresholds across all valid settlement storage boxes.
  - Producing settlement jobs (Cooks, Crafters, Medics, Hunters, Scrappers, Woodcutters, Brewers, and waiting Scavengers) pause with status `[PAUSED - Storage Full]` when all containers reach capacity, preserving cycle timers until room is cleared.
  - In `get_auto_sort_target_box`, prevented unconditional fallback to `fallback_chest` when all containers are full.
  - In `deposit_item_to_camp`, if an expedition haul arrives when all containers are at capacity, items spawn neatly on the ground at the camp hub workbench rather than vanishing or overfilling stashes.
- **Accurate Offline Container Weight for Multi-Use Items, Ammo & Weapons (Fixes #197)**: Fixed an issue where offline containers were evaluated against capacity limits using static base section weights (`inv_weight`), causing partially consumed items (charcoal bags, vodka, water, medicine) to read at full weight, kitted weapons to omit attachment weights, and fresh multi-use items found offline to default to 1 use:
  - Stored verified real engine item weight (`cl_item:weight()`) and maximum uses into `camp.stored_items` whenever items are inspected online or deposited into settlement storage.
  - Updated `consume_one_use` to dynamically adjust tracked item weight using the engine's `CEatableItem::Weight` formula (`empty_weight + (inv_weight - empty_weight) * (uses / max_uses)`) as settlers consume portions offline.
  - Corrected offline item discovery in `camp_iterate_inventory` to initialize untracked multi-use consumables to `max_uses` rather than 1 use, preventing full items from prematurely vanishing after a single offline cycle.
  - Updated `get_box_current_weight` to evaluate offline containers using recorded weights and dynamic multi-use calculations, preventing boxes of partially used materials from falsely reading full and overflowing prematurely.
- **Fallback Stash & Outpost Loot Table Sanitization (PR #159)**: Replaced nonexistent item section entries (`prt_i_resistor`, `prt_i_transist`, `toolkit_r`, `elite_detector`, etc.) in fallback loot and outpost chest tables with authentic items.
- **Storage Walks, Sleep Catch-Up Hitch & Registry Scan Optimizations (Fixes #248)**: Eliminated single-frame freezes and periodic hitches across simulation updates, container deposits, PDA refreshes, and game loads:
  - **Round-Robin Camp Scheduling & Sleep Catch-Up Cycle Budget**: Introduced `MAX_GLOBAL_CYCLES_PER_TICK = 6` global cycle budget and fair round-robin camp scheduling across 10-second update ticks, and capped settler backlogs to 6 cycles (`effective_interval * 6`), smoothing out sleep catch-up spikes (previously firing up to 36-60 cycles and 460,000+ engine calls in a single frame after sleeping) into imperceptible background ticks.
  - **Unified Settlement Inventory Snapshot**: Replaced redundant per-settler and per-job storage walks (which previously re-iterated every stored item 12-15 times per camp every 10 seconds) with a unified single-pass `get_camp_inventory_snapshot` caching item counts, multi-use supplies, damaged gear in workbenches, and turret ammo; settlers' paused states evaluate purely in Lua memory with zero engine calls.
  - **Single-Pass Turret Maintenance**: Optimized `process_turret_maintenance` to check total ammunition deficit and return early if the settlement inventory snapshot contains no 9mm rounds, refilling all deficit turrets across a single pass over online ammunition rather than looping entire camp inventories once per turret.
  - **PDA Roster Paused Status Cache**: Standardized `get_job_paused_status` cache TTL to 10 seconds (`max_age_ms or 10000`), matching the job tick rate and preventing PDA 500ms roster refreshes from re-walking camp storage every 1.5 seconds.
  - **Categorized Storage & Fast Auto-Sort Box Matching**: Added `get_camp_categorized_boxes` caching container metadata, showcase flags, and specialized storage buckets until camp structures change or are rescanned, eliminating per-deposit structure loops (reducing container choice from 1,622 engine calls down to ~10 per item deposit).
  - **Level-Filtered Multi-Camp Registry Scan on Load**: Restricted startup structure scans in `actor_on_first_update` and boundary rescans strictly to camps on the player's current level, and added `scan_multiple_camp_structures` to scan `server_objects_registry` in a single pass across all local settlements instead of looping 33,000+ server objects once per camp.
- **Strict Inventory Box Validation & Hub Storage Fallback (PR #177)**: Confined settlement storage containers strictly to authentic inventory boxes (excluding non-inventory physics decor props like `placeable_box_wood`), and updated unequipped camps to spawn an authentic 70kg `inventory_box` at the hub to prevent dropped items from becoming unpickable.
- **Independent Parts Data for Duplicated Haul Items & Recall Parity (PR #178)**: Deep-copied `item_parts` tables when creating duplicate expedition haul items so weapon and armor wear remain independent, and granted extra haul copy rolls to recalled expeditions.
- **Frame-Level Storage Weight Caching for Job Deposits (PR #185)**: Shared an in-memory batch `weight_cache` across all item deposits within a single update tick, preventing production jobs from overfilling containers before client-side physics shells update.
- **Specialized Storage Overflow Protection (PR #189)**: Excluded single-category containers (such as Hideout Furniture Expansion canned tuna crates, ammo boxes, and med cases) and appliances (fridges, stoves) from general Auto-Sort and job overflow routing.
- **Localized Auto-Sort Capacity Feedback & Fast Skip Accounting (PR #190)**: Added localized notifications (`st_auto_sort_skipped`, `st_auto_sort_none_fit`) in English and Russian when items cannot fit into camp storage, eliminating costly per-item container re-weighing.
- **Quest NPC Exclusion from Scavenger Stash Targeting (PR #203)**: Removed `ui_pda2_special_location` markers from scavenger stash targeting and required target entities to be inventory boxes, preventing scavengers from targeting unique NPCs (such as Hip, Nimble, or Arnie) and stripping their gear.
- **Multi-Use Consumable Extraction from Stashes (PR #204)**: Parsed multi-use count suffixes (`(.*)__(%d)`) when looting stashes and depositing items, preserving remaining uses on scavenged cooking kits, kerosene, and medicines.
- **Looted Outpost Chest Deregistration from G.A.M.M.A. Stash Pool (PR #205)**: Dropped looted outpost containers from `treasure_manager.caches` once marked empty (`false`), preventing abandoned chests from being chosen as targets for corpse stash notes or fetch quests.
- **Deferred Expedition Recall on Failed Transfers (PR #206)**: Deferred scavenger expedition recalls during settler transfers until after target camp capacity and faction safety checks succeed, preventing expeditions from being prematurely cancelled when transfers are refused.
- **Quest Item Exclusion from Auto-Sort by Item Kind (PR #216)**: Expanded Auto-Sort protected item checks to recognize `kind = i_quest` (`IsItem("quest")`), preventing documents, quest devices, and toolkit quest materials from being deposited into camp storage.
- **Dynamic Per-Container Capacity Accounting in Overview (PR #230)**: Calculated total settlement storage capacity on the Overview tab by summing each container's authentic `capacity` property rather than assuming a flat 150kg per box.
- **Universal Container Filtering for Last-Resort Job Deposits (PR #236)**: Confined last-resort job deposit fallbacks strictly to general storage containers, preventing automated item deposits from spilling into fridges, stoves, med cases, or single-kind boxes when storage is full.
- **Weapon Showcase Pegboard & Shelf Auto-Sort Exclusion (PR #237)**: Excluded weapon display pegboards and pistol shelves (`weapon_showcase`) from receiving general items during Auto-Sort and automated job deposits.
- **Permanent Offline Condition Queue Retention for Stored Gear (PR #238)**: Removed the 7-day expiration timer on `pending_cond_tick` records for offline items, ensuring weapons and armor scavenged while away retain their rolled condition until the player visits the settlement.

### 🛡️ Defense Turrets, Audio & Gadgets Hardening (Community / devinhorowitz):
- **Universal Suppressed Firing & MP7 Reload Audio for Turrets (PR #112)**: Ensured defense turrets utilize authentic suppressed gunfire audio and MP7 reload sounds across all installations, including Standard Anomaly.
- **Online-Only Ammo Refilling for Turrets (PR #141)**: Restricted automated turret maintenance to ammunition boxes with online game objects, preventing infinite ammo loops and inaccurate round deductions.
- **Native Game Audio Fallbacks for Alarms & Consumables (PR #143)**: Replaced missing sound paths for sirens and drinks with authentic engine-shipped audio assets, restoring audible raid alarms and medic consumption sounds.
- **Universal Pickup Protection for Outpost Radios & Lamps (PR #144)**: Extended furniture pickup prevention monkeypatches to `placeable_radio_wrapper` and `placeable_light_wrapper`, preventing players from dismantling outpost lights and radios.
- **Core String Definitions for Turret Radio Channels (PR #160)**: Added missing turret channel status strings (`st_turret_channel`, `st_channel_off`) to core string tables, eliminating raw text IDs on Standard Anomaly installs.
- **Turret Interface Icon Rect Dimension Normalization (PR #170)**: Corrected the icon rect dimensions in `ui_placeable_pistol_turret.xml` from 300x300 to match the 256x256 texture, eliminating UV distortion and centering the turret display.
- **Active Alarm Siren Defense Bonus During Raid Rolls (Fixes #254)**: Fixed an issue where the MCM `alarm_defense_bonus` (+15 defense by default) never lowered camp raid chances because `has_active_alarm` previously checked whether an alarm currently saw an intruder within 5 meters with line of sight before raiders even spawned:
  - Simplified `has_active_alarm` to check whether any placed alarm system in the settlement is switched on (`data.is_on`), applying the defense bonus consistently across both online and offline raid checks.
  - Aligned English and Russian PDA Guide Section 5 descriptions to clarify that an active (switched-on) siren contributes the Alarm Defense Bonus (+15 by default) during raid rolls.
- **Offline Container Early-Exit for Turret Maintenance (PR #235)**: Skipped turret ammunition searches when all camp containers are offline, eliminating thousands of redundant engine object lookups every 10 seconds for remote settlements.

### 📱 PDA Interface, Theme Parity, Controls & Localization (Community / devinhorowitz):
- **Modern PDA Self-Contained Texture & Taskboard Decoupling (Fixes #114)**: Replaced external PDA Taskboard texture references (`ui\taskboard_icons`) on `list_header_bg` and `top_status_bar` in Modern theme with base Anomaly 9-slice frame `ui_inGame2_pda_buttons_background`, mapped `btn_refresh_survivors` to Homestead's native `ui_homestead_btn_primary` with localized label `st_pda_btn_refresh_survivors`, and removed unused legacy taskboard texture blocks across all themes to eliminate missing-texture placeholders and log warnings on standard Anomaly installs.
- **Modern Theme Guide Separator Crash Fix (PR #104)**: Removed `stretch="1"` from `guide_separator_line` in the Modern PDA theme, resolving fatal crashes when opening the Settlements page.
- **Modern Theme Overview Header Card Dimensions (PR #113)**: Increased header card height in the Modern theme to 52 units, cleanly accommodating the two-line region and specialization badge.
- **Rivals Tab Section Header Draw Order Parity (PR #111)**: Corrected draw layering for Rivals tab section headers ("FACTION ALIGNMENT", "STRATEGIC LOCATION", "TACTICAL INTEL"), rendering them visibly above background panels across all themes.
- **Non-Mutating Data Refresh for Rivals Tab (PR #145)**: Separated UI list reloading from ALife outpost update ticks on the Rivals tab, preventing manual list refreshes from artificially accelerating Zone events.
- **Remote Outpost Distance Metric Concealment (PR #164)**: Hid misleading distance numbers for outposts situated on other maps, displaying distances only when the outpost shares the player's current level.
- **Authentic Happiness-Driven Morale Display (PR #146)**: Switched Overview tab morale indicators and radio telemetry to display authentic settlement happiness (`stats.happiness`), matching desertion thresholds and map marker alerts.
- **Threat Level Gauge Defense Cap Scaling (PR #165)**: Scaled the Overview tab Threat Level assessment against the configured MCM defense cap rather than a hardcoded value.
- **Functional PDA Window Closure on Exit & Fast Travel (PR #147)**: Resolved an issue where clicking Close or initiating Fast Travel failed to dismiss the PDA by properly handling window closure through PDA menu controllers.
- **Localized Fallback Naming for Unnamed Settlements (PR #148)**: Assigned clean, localized level-based names (e.g. "Cordon Settlement") to unnamed camps and prevented save loading from blanking settlement names.
- **Hostile Filtering & Snapshot Replacement for Radio Scan (PR #149)**: Fixed Radio Scan to report only genuinely hostile outposts rather than labeling friendly camps as enemies, and replaced previous scans cleanly to prevent radio log overflow.
- **Thematic Log Filtering for Camp Radio Feeds (PR #168)**: Assigned proper category tags (`work`, `expedition`, `combat`) to camp radio announcements, ensuring logs appear under their respective filter tabs.
- **Radio Log & News Hook Decoupling (Fixes #253)**: Removed the global `news_manager.send_tip` monkeypatch (`hook_homestead_news_manager`) and its 38-keyword string interception routine (`intercept_pda_news_message`), completely resolving foreign mod text pollution, engine overhead, and multi-language feed omissions:
  - **Eliminated Third-Party Mod Ingestion**: Prevented unrelated base game and third-party mod tips (e.g., G.A.M.M.A. disassembly tool warnings, dead technician alerts, water/trader news) from being captured into settlement radio logs.
  - **Direct Categorized Dispatches via `camp_send_tip`**: Routed settlement reports and alerts directly through `camp_send_tip` with explicit category tags (`"work"`, `"combat"`, `"expedition"`, `"general"`), including scavenger single and regional sweep departures, settler desertion notices, camp raid/morale warnings, cook meat deficits, settler hunger alerts, water pump filter shortages, trade network offline notices, and siren alarm triggers. Replies to the player's own actions (Auto-Sort, scavenger dispatch and recall, hand-ins to settlers, fast travel, paid treatment) still go straight to `news_manager` and stay out of the radio log.
  - **Multi-Language Radio Feed Parity**: Ensured radio log entries for Russian and non-English localizations are logged reliably with proper filter categorization without relying on English keyword matching.
- **Dossier XP Threshold Scale Parity (PR #152)**: Aligned settler dossier progress bars with actual work-cycle promotion tiers (10/25/50 XP) rather than expedition thresholds.
- **Dynamic Vertical Refitting for Expanding Roster Cards (PR #162)**: Dynamically adjusted roster card heights when multi-line status or telemetry expands, preventing text overlap between adjacent settler cards.
- **Scroll Offset Retention Across Roster Refreshes (PR #163)**: Maintained scroll positions when rebuilding settlement roster lists, preventing the view from snapping back to the top during updates.
- **Single Percent Sign Normalization in PDA Guide (PR #166)**: Replaced unescaped double percent signs (`%%`) in PDA guide string tables with clean single percent signs.
- **PDA Guide Alignment with Settlement Jobs & Storage Mechanics (Fixes #251)**: Corrected outdated descriptions in English and Russian PDA Guide entries (`ui_st_stalker_camp_builder.xml`) to accurately describe underlying game mechanics:
  - **Electrician (`st_guide_s3h_body`)**: Replaced free-lamp and battery-recharge claims with actual lamp upkeep behavior (consumes 1 Battery Pack from storage when lamps fall below 50% fuel to refill all placed lamps; pauses if storage lacks batteries; no battery recharging service).
  - **Medic (`st_guide_s3g_body`)**: Corrected AI-2 Medkit recipe to 4x vodka + 1 bandage (or bandages from 1x vodka / 1 cloth), and clarified that each vodka represents 1 use from a 3-use Nemiroff bottle.
  - **Crafter (`st_guide_s3d_body`)**: Corrected default ammo synthesis cycle from 10 minutes to the MCM default of 20 minutes.
  - **Cook (`st_guide_s3f_body`)**: Clarified that cooks operate from any camp container (making campfire meals without a stove, and gourmet meals on a fueled stove burning charcoal/kerosene/gas plus clean water for tier 2 or vodka for tier 3); updated default cycle to 15 minutes; and corrected the Hospitality Buff to 0.5% health and 5% stamina every 10s (4 hours for eating cooked/canned food at Morale >= 50, 6 hours for sleeping 3+ hours at Morale >= 60).
  - **Technician (`st_guide_s3e_body`)**: Clarified that passive repair operates strictly on weapons and armor placed within a workbench (workshop hub, workbench, or repair bench) while the player is near camp, consuming 1 vodka, conserva, or tushonka per round.
  - **Recruitment (`st_guide_s2_body`)**: Updated contract fee and requirement tables (novice/trainee free; experienced 2,500 RU; professional 5,000; veteran 10,000 + 25 Def; expert 16,000 + 35 Def; master 25,000 + 50 Def; legend 35,000 + 60 Def), and noted that companions pay rank fees while refugees join free.
  - **Storage & Routing (`st_guide_s4_body`, `st_guide_s3i_body`, `st_guide_s3k_body`)**: Updated protected gear list (all weapons, armor, helmets, artifacts, devices, belt/slot items, and quest items are protected regardless of equipped status); updated container routing radius to Camp Boundary Radius (50m default); removed nonexistent safe/bookcase sorting rules; corrected fridge preservation cycle to 12 game hours (MCM) restoring 25% condition on meat, kolbasa, and bread across camp boxes; and updated Woodcutter and Scrapper storage routing lines to match actual stove and ammo/case container priorities.
- **MCM Tooltip Default Value Corrections (PR #167)**: Corrected inaccurate default values in English and Russian MCM tooltips for Medic Job Cycle (25 min), Electrician Interval (15 min), and Rival Spawn Distance (250m).
- **Russian Recall Button Label Fit (PR #169)**: Shortened the Russian text label for the cross-level recall button, fitting the text within the button frame and preventing overlap with adjacent controls.
- **Double-Click Throttle for Dismantle & Banish Buttons (PR #209)**: Throttled Dismantle Camp and Banish settler button actions to at most once per second across all PDA themes, preventing accidental double-clicks from dismissing adjacent settlements or settlers.
- **Active Raid PDA Status Banner & Threat Level Parity (PR #228)**: Hooked `camp.active_raid` across all PDA theme scripts to accurately display the critical threat banner and active raid status during settlement attacks.
- **Verbose Notification Decoupling for Expedition & Outpost News (PR #229)**: Routed scavenger progress updates, receipts, and outpost recon reports through `camp_send_tip`, ensuring routine announcements respect the MCM Verbose Notifications toggle and appear reliably in Russian Radio feeds.
- **PDA Guide Alignment with Engine Defense & Raid Mechanics (PR #231)**: Corrected defense values, raid mechanics, and camp boundary descriptions in English and Russian PDA Guide sections to match actual runtime formulas (guards +5, sirens +10, barricades +2, turrets +15; 50m radius).
- **Transient Scan Entry Trimming for Radio Logs (PR #243)**: Added `trim_radio_log` to prioritize pruning temporary Radio Scan lines before discarding permanent settlement event reports when the radio log reaches capacity.
- **Cross-Level Distance Guard for PDA Top Bar Signal Strength (PR #244)**: Displayed fixed relay signal status ("SIGNAL: 25% (RELAY)") for settlements on other levels, preventing misleading local signal readings derived from cross-level coordinate comparisons.
- **Distinct Numbering for Same-Level Unnamed Settlements (PR #245)**: Appended sequential numbers ("Cordon Settlement #1", "#2") to unnamed camps sharing the same level, preventing duplicate entries in transfer menus and notifications.
- **MCM Tooltip Accuracy for Idle Leash & Camp Rest (PR #246)**: Updated English and Russian MCM tooltips to describe how the idle soft leash works and clarify that camp sleep bonuses restore satiety and stamina.
- **Button Text Truncation Parity for Modern Theme Orders (PR #247)**: Stripped trailing parenthetical order details with `hs_theme.short` on Modern theme Survivors tab buttons, preventing long directive labels from overflowing button borders.

## v1.2.3 — Comprehensive Community Bugfixes, Settlement Automation, Outpost Lifecycles & Engine Hardening

### 🛠️ Settlement Systems & Job Automation Hardening (Community / devinhorowitz):
- **Exact Material Section Matching for Jobs (PR #31)**: Replaced loose substring section matching in job material consumption with exact item section lookups across `stalker_camp_builder_jobs.script`. Prevents jobs from consuming unintended items (e.g. woodcutters/brewers consuming wooden exoskeletons or weapon furniture, water pumps consuming gas mask filters, ammo crafters consuming poltergeist powder, and stove cooks consuming empty gas jerrycans or decor kits). Cleaned up food stockpile caps to only count `meat_` items.
- **Offline Multi-Use Item Consumption (PR #36)**: Fixed an engine limitation where offline containers had no access to remaining uses on multi-use consumables (rations, water flasks, alcohol, medical supplies). Homestead now tracks remaining uses via `camp.stored_items` and queues partial consumptions through `pending_item_cond`, deducting single uses rather than deleting whole multi-use items while the player is remote.
- **Job Pause Checks & Requirements Synchronization (PR #57)**: Aligned `get_job_paused_status` checks with actual job execution logic:
  - **Medic**: Correctly requires 4 ethanol uses and 1 bandage for medkit orders instead of checking for 2 ethanol uses and throwing repeated "needs materials" alerts.
  - **Technician**: Properly checks both damage status and repair fees (`camp_has_repairable_gear`), utilizing the exact repair fee item list rather than failing silently with "No Gear to Repair".
  - **Cook**: Checks for raw meat before consuming stove fuel or water/vodka, eliminating fuel loss on empty cycles.
  - **Job Selection Idempotency**: `set_survivor_job` now returns early when clicking a settler's current job in the PDA or dialog, preventing unnecessary timer resets and cycle restarts.
- **Electrician Lamp Maintenance & Switch Preservation (PR #54)**: Fixed camp lamp refueling so condition/fuel values are updated directly on the active binder wrapper (`binded_object().wrapper`). Stopped forcing `is_on = true`, ensuring lamps manually switched off by the player remain switched off.
- **Empty Container ALife Sweep Optimization (PR #65)**: Optimized `iterate_server_container` when querying empty camp storage boxes. Previously, an empty box fell through to `get_server_container_items` which scanned all 65,534 ALife IDs across the Zone every 10 seconds. Homestead now terminates iteration cleanly after the server object's child pass completes.
- **Hospitality Buff Duration Persistence (PR #63)**: Saved `hospitality_buff_end_sec` in game seconds within persistent camp state, ensuring the well-fed / well-rested hospitality buff carries across save loads and level transitions.
- **Camp Rest Bonus Restoration (PR #50)**: Fixed `check_camp_sleep_bonus` to properly restore satiety and stamina using the engine's `change_satiety` and `change_power` methods rather than nonexistent actor setters. Removed false promises of thirst restoration from English and Russian UI messages.
- **Configurable Woodcutter and Scrapper Yields in MCM (Issue #4)**: Fixed an issue where woodcutter and scrapper yield settings existed in config (`yield_wood_min/max`, `yield_scrap_min/max`, `yield_fasteners_min/max`) and MCM path mappings but lacked MCM menu entries and were ignored in favor of hard-coded yield quantities. Added interactive slider controls in `stalker_camp_builder_mcm.script`, corresponding English and Russian localization string definitions, and connected `process_woodcutter_job` and `process_scrapper_job` to dynamically read and scale yields from MCM while preserving axe and tool productivity bonuses.
- **Session Clock Stamp Normalization on Load (PR #64)**: Purged session-relative `time_global()` timestamps (`_cached_storage_metrics_tg`, `_last_periodic_scan`, `temp_target_time`) during `load_state`, preventing hours-long storage UI caching freezes and cook pathing stalls after loading saves created late in long sessions.

### 🎒 Scavenger Expeditions & Settlement Logistics (Community / devinhorowitz):
- **Same-Level Scavenger Expedition Return (PR #32)**: Replaced a nonexistent engine call `level.valid_vertex_id` with a graph-valid vertex ID check (`u32(-1)`) in `reposition_survivor_at_camp`. Scavengers returning from expeditions while the player is on the same map now finish properly, deposit their haul, receive bonus salvage/XP, and return to their camp wait schemes rather than remaining stranded offline.
- **Scavenger Recall Haul Preservation & Safety (PR #33)**: Recalling a scavenger via the PDA or map now secures whatever loot was scavenged up to that point and deposits it into camp storage. Furthermore, changing jobs, transferring, banishing, or repositioning an active scavenger automatically recalls them first, preventing orphaned expedition loops and duplicate deployments.
- **Player-Created Stash Protection (PR #34)**: Excluded player-created backpacks (`treasure_player`, `inv_backpack`, `itm_actor_backpack`) and custom markers from scavenger target lists and automated level sweeps. Scavengers will no longer loot or dismantle the player's personal stash stashes.
- **Caravan Trader Restocking & Despawn Validation (PR #44)**: Stored `trader_stock_pending` in session-level tables to ensure caravans summoned remotely restock reliably upon player arrival even after saving/loading. Hardened trader despawn logic to verify the entity is a living trader before releasing, preventing accidental release of recycled ALife IDs.
- **Overlapping Caravan Prevention (PR #45)**: Excluded random caravan events while a camp trader is actively stationed at the settlement, preventing duplicate merchant spawns and stranded NPCs.
- **Expedition Stash Reservation & Duplicate Loot Prevention (Issue #80)**: Fixed an exploit and logic bug where multiple scavenger expeditions could be sent to the same stashes, double-looting them and generating duplicated rewards:
  - Added `get_expedition_for_stash` helper checking both primary stash IDs and all constituent stashes in regional sweeps (`all_stashes`).
  - Marked stashes across an active expedition now show "Scavenger in Transit" and offer a working "Recall" option that properly recalls the expedition even when right-clicking non-primary stashes.
  - `get_level_marked_stashes` now excludes any stashes currently claimed by active expeditions, preventing subsequent regional sweeps on the same map from overlapping or double-dispatching.
  - `dispatch_scavenger_to_stash` and `dispatch_scavenger_regional_sweep` reject dispatches to claimed stashes and filter out already-claimed targets from regional sweep lists.
  - `loot_and_clear_stash` prevents cross-expedition duplicate payouts by checking if a stash was already looted by another active expedition before generating items.

### 👥 Settler Management, Recruitment & Companion Integrations (Community / devinhorowitz):
- **Task Escort & Story Companion Recruitment Protection (PR #48)**: Prevented task companions, hostages, rescue targets (`npcx_beh_cannot_dismiss`, `companion_cannot_dismiss`), and story NPCs from appearing in camp recruitment dialogs, eliminating broken quest states and orphaned task squads.
- **Dual-Camp Settler Assignment Prevention (PR #47)**: Automatically unregisters a companion settler from their previous settlement roster when they are recruited into a new camp, preventing dual-bed reservation and roster duplication.
- **Settler Transfer State & Workstation Re-anchoring (PR #46)**: Cleanly clears sticky workstation assignments (`assigned_furniture`), temporary navigation targets, and cached furniture bindings during settler transfers, correctly pointing `settler_lookup` to the new camp and preventing teleport leash snapping back to the old base.
- **Dismissed Companion Job Restoration (PR #49)**: Fixed `heal_stuck_companion_settlers` and load-time sweeps so settlers dismissed from the player party via standard companion dialogue cleanly resume their previous assigned settlement duties rather than being forcefully re-added to the party.
- **Invincible Settler Engine Healing (PR #51)**: Switched health replenishment from nonexistent `npc:set_health` to the authentic engine method `npc:set_health_ex(1.0)` in `npc_on_update` and hit callbacks, ensuring the Invincible Settlers MCM setting works reliably in combat.
- **Recruitment Fee Charge Ordering (PR #39)**: Deferred recruitment fee deduction until after `recruit_npc_to_camp` successfully admits the settler, ensuring players are not charged when recruitment is blocked by camp population caps or faction restrictions.
- **Refugee Behavior Activation (PR #53)**: Registered refugee event NPCs in `settler_lookup`, enabling `handle_refugee_ai` to route refugees to camp hubs rather than idling indefinitely without camp logic.
- **Companion Move Mode Wrapper Varargs (PR #73)**: Updated the `axr_companions.cycle_companions_move_mode` monkeypatch to forward all arguments and return values through `pcall`, maintaining compatibility with companion command scripts.
- **Simulator Info Portion Cleanup (PR #30)**: Restored `sim:disable_info` in `purge_settler_companion_and_squad_state` and `heal_ghost_companion_squads`, ensuring companion and behavior infoportions are properly stripped when settlers are banished offline.
- **Ghost Companion Migration Sweep & Job Transition Hardening (Issue #76)**: Completely overhauled `heal_ghost_companion_squads` to resolve issues where the sweep protected every squad due to unsigned 32-bit story ID sentinels (`m_story_id ~= 65535` vs `get_object_story_id`). Corrected task object fields to query `current_target`, ensured positive ghost evidence overrides lingering `non_task_companions` registrations, isolated member purges so only confirmed ghost members are unlinked rather than entire mixed squads, and bound entity names to banished IDs to guard against ID recycling. Hardened `set_survivor_job` to route all transitions away from companion duties through `purge_settler_companion_and_squad_state(..., false)` so offline settlers never spawn new ghost squads.
- **Camp Dismantling & Banish Settler State Purge, Offline Recovery & Simulation Reassignment (Issue #81)**: Resolved an issue where dismantling a settlement or banishing settlers left non-companion settlers frozen forever at their stations with persistent `beh@settler` logic, retained `npcx_beh_wait` infoportions, locked offline switches, and no simulation squads:
  - `dismantle_camp` now runs `purge_settler_companion_and_squad_state` across all settlers regardless of job, stripping settler behavior schemes, guard/patrol infoportions, and companion states cleanly.
  - Eliminated hazardous `utils_obj.switch_online` calls in `dismantle_camp`, `banish_npc`, and `dismiss_survivor` that permanently set `set_switch_offline(id, false)`, restoring authentic ALife `can_switch_offline = true` and `can_switch_online = true` defaults so freed stalkers can freely enter and exit offline simulation.
  - Added persistent `m_data.stalker_camp_builder_freed_settlers` tracking so settlers dismantled or banished while offline have their `beh@settler` logic restored, homestead infoportions stripped, and state reset to idle upon their next net spawn.
  - Added `reassign_freed_settler_to_smart`, creating an `online_offline_group` simulation squad and routing non-story stalkers to the nearest friendly/neutral smart terrain via `SIMBOARD:assign_squad_to_smart`, allowing freed settlers to pack up and walk to a base instead of freezing as unmanaged stationary NPCs.

### 🏕️ Outposts, Raids & Dynamic Zone Events (Community / devinhorowitz):
- **Outpost Cooldown Arithmetic Overflow Fix (PR #41)**: Resolved a major bug in `process_single_rival_camp` where `xrTime:set` with year/day 0 caused an unsigned integer underflow, locking cleared outpost levels out of respawns for 200 million years. Cooldowns are now calculated with plain second offsets, and legacy barred levels are automatically restored on load.
- **Single-Roll Outpost Takeovers & Spawn Distance Guard (PR #55)**: Outpost takeovers are now rolled exactly once upon abandonment and saved in `camp.takeover_at`. New hostile/friendly garrisons arrive after a realistic 1–3 hour delay and only when the player is at least 150m away, preventing enemy squads from spawning on top of looting players and allowing abandoned ruins to properly decay and despawn.
- **Surge & Psi-Storm Outpost Zombification (PR #52)**: Enabled outpost surge zombification to trigger at the onset of emissions and psi-storms (`surge_manager.is_started`, `psi_storm_manager.is_started`) rather than waiting for actor death, skipping outposts within 150m of the player.
- **Mutant Nest Lifespan & Fortification Sanity (PR #56)**: Prevented mutant-infested outposts from receiving human fortification upgrades, loner squad reinforcements, or loner theme crates when their lifespan expires. Mutants now naturally disperse and convert to abandoned outposts when their timer concludes.
- **Outpost SOS Distress Call Hardening (PR #61)**: Recorded the calling faction in `sos_faction` and enforced a strict 2-hour Zone-wide expiration. Prevents distress calls from paying rewards to rival factions or mutant packs that overtook the outpost.
- **Outpost Furniture Theft Protection (PR #43)**: Updated `is_rival_camp_object` to check `camp.decorations`, properly protecting outpost barricades, workbenches, and decor from being picked up and pocketed by the player.
- **Outpost Entity Release Safety (PR #42)**: Hardened `release_camp_decorations` and squad teardowns to verify object section and squad validity before calling `alife_release`, preventing accidental deletion of unrelated entities sharing recycled ALife IDs.
- **Raid Faction Resolution (PR #58)**: Stripped the `"actor_"` prefix from community names before evaluating enemy raid types, ensuring bandit, renegade, and military player camps are raided by their true faction adversaries rather than default bandits.
- **Accurate Raid Summary Statistics (PR #59)**: Corrected casualty calculations in raid summaries ("Raid repelled! Raiders killed: %d, guards lost: %d"), accurately tracking fallen raiders after squad deletion and settlers killed while on guard duty.
- **Rival Camp Spawn Chance Persistence (PR #62)**: Cached the rolled spawn probability alongside `next_rival_spawn_interval_sec`, ensuring dynamic outpost density chances are preserved across updates.
- **Level Vertex Validation & NPC Patrol/Movement Enablement (Issue #77)**: Fixed a major engine discrepancy where `camp_npc_move_to`, `setup_settler_beh_logic`, and `run_rival_npc_patrol` unconditionally aborted execution due to calls to the nonexistent engine method `level.valid_vertex_id`. Replaced with `is_valid_level_vertex` / `is_level_vertex` (verifying `u32(-1)` sentinel boundaries) and `npc:accessible(lvid)`, fully activating walking navigation for settler soft leashes, workstation approaches, refugee camp routing, and dynamic rival outpost guard patrols.
- **Rival Outpost ID & Object Lifecycle Pruning (Issue #78)**: Resolved multiple engine issues where rival outpost IDs outlived their underlying ALife objects, causing recycled ID collisions, lingering state leaks, and ghost outpost lookups. Added immediate unregister teardown hooks for rival chest containers in `server_entity_on_unregister` (cleaning up map spots, decorations, squad script holds, `m_data.player_created_stashes`, and the outpost entry), pruned unregistering squad IDs and decoration IDs from active outposts, fixed chest decay to perform full atomic teardown instead of leaving orphan entries until subsequent cycles, tracked spawned decoration sections (`decor_sections`) to protect unrelated objects from accidental release, hardened squad lookups across `npc_on_update` and `game_object_net_spawn` to properly track auxiliary squads (`extra_squad_ids`) without fragile proximity fallbacks, and added strict community/companion validation (`is_valid_camp_squad`) across `restrain_rival_squads`, `process_single_rival_camp`, `zombify_rival_camp`, and `transform_to_mutant_nest` so unrelated squads reusing recycled ALife IDs are never restrained or erroneously deleted.
- **Supply Courier Traversal, Outpost Delivery & Heat Mutant Lifecycle Management (Issue #79)**: Resolved an issue where supply couriers and outpost "heat" mutant squads spawned frozen in place, never travelled, and leaked indefinitely into the simulation:
  - Allowed `create_squad_at_pos` to spawn mobile squads via an optional `no_pin` flag, eliminating the unconditional `get_script_target = function(self) return self.id end` self-targeting pin that froze simulation squads upon spawn.
  - Couriers now select starting smart terrains at least 60m away, route towards the smart terrain closest to their destination outpost via `SIMBOARD:assign_squad_to_smart` and `get_script_target`, and deposit resupply goods into both online and offline outpost containers.
  - Courier squads and individual squad members are cleanly released via `alife_release` upon delivery or timeout, avoiding permanent accumulation of orphan squads. Convoys and script targets are persisted across saves in `stalker_camp_builder_active_convoys`.
  - Heat mutant spawns now verify player distance (> 150m) and outpost faction (skipping mutant nests and monster camps), target the garrison squad (`get_script_target = function(self) return camp.squad_id end`) so they actively assault the outpost rather than standing idle, throttle to at most one active heat mutant pack per outpost via `camp.heat_mutant_squad_id`, and are cleanly released alongside active convoys whenever an outpost is dismantled, decayed, or destroyed.

### 🛡️ Defense Turrets & Gadgets Stability (Community / devinhorowitz):
- **Turret Aim Vector Normalization & Ammo Waste Prevention (PR #60)**: Normalized target direction vectors before evaluating steer angle in `pistol_turret_wrapper:fire_once`. Prevents turrets from failing close-range shots against point-blank targets, corrects extreme off-barrel firing angles, and ensures ammunition is only deducted when a valid shot actually fires.
- **Turret Ammo Recovery on Deliberate Pickup (PR #35)**: Moved turret magazine recovery into a dedicated `pickup` override. Turrets no longer dump their magazines into player inventory and beep for ammo whenever they cycle offline due to distance or level transitions.
- **Standard Install Turret Dialog Crash Fix (PR #28)**: Added `NodeExist("btn_channel")` validation before initializing the channel button in `UIPistolTurret:InitControls`, eliminating fatal "XML node not found" crashes on standard installs lacking the Hideout Gadgets GAMMA patch.
- **Turret String Table & Bullet Encoding Fix (PR #75)**: Corrected double-encoded UTF-8 bullet points (`0x95` cp1251) across `st_gun_turret.xml`, resolving corrupt character display ("Гўв‚¬Вў") on turret descriptions. Deduplicated shared gadget strings across `st_gun_turret.xml` and `st_alarm_system.xml`.

### 📱 PDA Interface, Controls & Localization Polish (Community / devinhorowitz):
- **Interactive PDA Button Flags (PR #29)**: Respected `homestead_no_pda_tab_flag` and Mod App Creator (`z_stalker_camp_builder_pda_mac`) module flags in `z_stalker_camp_builder_pda_monkeypatch`, eliminating crashes and preventing duplicate rail buttons.
- **PDA List Selection Retention (PR #68)**: Preserved selected camp (`hub_id`), settler (`survivor_id`), and outpost (`smart`) across list rebuilds, preventing unwanted UI resets back to the first item after renaming, sorting, assigning jobs, or filtering.
- **Settlement Roster Polling Optimization (PR #66)**: Throttled `UpdateSurvivorsProgress` in `homestead_pda_actor_on_update` so roster and container scanning only runs while the PDA window is actively open and visible.
- **UI Callback Crash Protection (PR #67)**: Wrapped Rivals tab and Left Rail manual refresh button callbacks in `pcall`, preventing unhandled script errors from crashing the game.
- **Radio Feed Clear Log Fix (PR #71)**: Prevented `PopulateRadioFeed` from immediately re-seeding telemetry entries after clicking Clear Log, allowing the empty log status message to display properly.
- **Modern Theme Survivor Rename Dialog (PR #72)**: Corrected `OnRenameSurvivorClicked` in `01_Theme_Modern` to open `UIRenameSurvivor` via `ShowDialog(true)`, allowing survivors to be renamed in the Modern theme.
- **Overview Security Rating Defense Cap Scaling (PR #69)**: Scaled the Overview tab security rating gauge against the configured MCM `defense_cap` rather than a hardcoded value of 150.
- **Settlement Map Spot Morale & Text Updates (PR #70)**: Implemented `refresh_settlement_map_spot` to dynamically write settlement names and low morale warnings (`[LOW MORALE: <40%]`) directly to active hub map spots.
- **Save Game Map Spot Synchronization (PR #40)**: Forced map spot synchronization on first update after level load, ensuring legacy serialized map spots from earlier versions are purged and replaced with non-serialized runtime spots.
- **Fast Travel Fee Deduction (PR #38)**: Deducted fast travel fees using `db.actor:give_money(-cost)` instead of nonexistent `set_money`.
- **Mechanic Armor/Helmet Repair Pricing Chain Preservation (PR #37)**: Preserved `inventory_upgrades_mp.how_much_repair` calculation chains for outfits and helmets, ensuring Homestead's weapon repair pricing override does not unintentionally alter armor repair costs in G.A.M.M.A.
- **String Table & Localization Fixes (PR #74)**:
  - Fixed Russian `st_dismantle_camp_done` to correctly indicate that workbenches and storage containers remain in place.
  - Added missing `st_pda_settlement_job_hunter` translation for English and Russian.
  - Fixed Russian radio text `st_pda_radio_no_logs` ("no radio traffic recorded" instead of radioactivity).
  - Deduplicated `st_camp_medic_heal_done` string IDs and replaced broken 3-byte UTF-8 em dashes with standard hyphens in English MCM text.

### 📦 Standard Anomaly Installs, Asset Packaging & Mod Compatibility Hardening (Community / devinhorowitz - Issue #82):
- **G.A.M.M.A. Flag Isolation**: Removed `00_Core/gamedata/scripts/stalker_camp_builder_gamma_flag.script` which erroneously forced `_G.is_gamma = true` across all installs including Standard S.T.A.L.K.E.R. Anomaly. The flag now strictly ships only within the optional `02_GAMMA` component (with `grok_stashes_on_corpses` continuing to serve as dynamic engine fallback).
- **Hideout Gadgets Sound Paths Standardization**: Standardized alarm siren/switch sounds in `bind_alarm_system.script` and `bind_alarm_system_pda.script` to `alarm_system_sounds\` (shipped by both base Hideout Gadgets 0.7.2 and Homestead's `04_HideoutGadgetsGammaPatch`), eliminating silent alarms and inverted sound folder logic on Standard Anomaly installs.
- **Turret and Display Counter Sounds**: Re-routed turret motor and out-of-ammo sounds in `bind_pistol_turret.script`, as well as display counter switch sounds in `bind_display_counter.script`, from G.A.M.M.A.-patch-specific `gun_turret_sounds\` to `alarm_system_sounds\`, ensuring turrets and counters play authentic audio on Standard Anomaly without missing-sound errors.
- **Vanilla Theme Texture Descriptions**: Re-mapped `ui_homestead_card_bg`, `ui_homestead_module_bg`, `ui_homestead_module_header`, `ui_homestead_dialog_bg`, `ui_homestead_banner_secure`, `ui_homestead_banner_neutral`, and `ui_homestead_banner_threat` in `01_Theme_Vanilla` to Homestead's own `ui\homestead_pda\` textures rather than iTheon's PDA Taskboard (`ui\taskboard_icons`), resolving missing texture box rendering and log errors for users without the Taskboard addon.
- **Mutant-Nest Map Spot Fallback**: Added dynamic detection in `modxml_stalker_camp_builder.script` for Catspaw skull textures (`ui_catsy_milpda.xml`, `ui_catsy_paw_texd.xml`). On Standard Anomaly installs lacking Catspaw addons, mutant nests cleanly fall back to base-game tactical hazard markers (`ui_pda2_base` / `ui_mmap_base` with hazard orange tint `r="255" g="100" b="0"`), eliminating missing texture spots.
- **Seamless Mod App Creator (MAC) Integration**: Moved `ui_app_settlement.xml` (defining button texture states `app_settlement_e/h/t/d`) into `00_Core` and removed the redundant `03_ModAppCreator` optional component from the FOMOD installer. Homestead now automatically detects MAC and registers the app icon seamlessly whenever MAC is present in the player's modlist, avoiding blank tiles when selecting "No Mod App Creator Integration".
- **Orphaned 01_PDATab Removal**: Deleted the orphaned and uninstalled `01_PDATab` directory, eliminating confusing duplicate code and ensuring all theme maintenance targets the active FOMOD theme packages.

### 🎨 Modern PDA Theme Parity, Layout & Engine Text Rendering (Community / devinhorowitz - Issue #83):
- **Texture Paths & Frame Window Initializations**: Fixed invalid double-backslash path for `dossier_portrait` (`ui\\ui_noise` -> `ui\ui_noise`) in `ui_stalker_camp_builder_pda.xml`. Switched 9-slice frame textures (`background`, `list_header_bg`) from `InitStatic` to `InitFrame`, and frame-line textures (`vertical_line`, `guide_separator_line`) from `InitStatic` to `InitFrameLine`, ensuring correct window types and border rendering across the Modern PDA interface.
- **Missing Rivals & Guide Panel Headers**: Initialized missing section header statics and text labels on the Rivals tab (`rival_faction_lbl`, `rival_loc_gar_lbl`, `rival_intel_lbl`, `rival_faction_bg`, `rival_loc_gar_bg`, and header backgrounds) and Guide tab (`guide_header_bg`, `guide_header_lbl`), bringing them to full visual parity with `00_Core`.
- **Survivor Detail Dynamic Layout & Scroll Height Refit**: Ported `RefitSurvivorDetail` to `01_Theme_Modern`, dynamically shifting child widgets and resizing `job_content` when multi-line job telemetry or custom-position status text expands/contracts. Re-measured `job_scroll` bounds via `Update()` when `job_resized` is flagged so `CUIScrollView` properly recalculates scroll range. Added `st_extra` height adjustments to Field Station button positions (`btn_position_here`, `btn_position_recall`, `btn_job_directive`, `btn_rename_survivor`).
- **Telemetry Text Truncation & Colorization Format**: Removed redundant `"Assigned Job: "` string prefix across `RefreshJobProgress` to prevent awkward line breaks and clipping within the compact telemetry card. Standardized all `%c` color formatting codes in `colorize_pda_text` and `RefreshJobProgress` to authentic 4-component ARGB (`%c[255,r,g,b]`), resolving engine color parsing inconsistencies.
- **Overview Header Layout & Threat Banner Positioning**: Split the region and specialization badge into dedicated lines (`[ REGION: %s ]\n[ SPEC: %s ]`) to eliminate text overflow and name clipping. Dynamically positioned `raid_banner_bg` and `raid_banner_lbl` below the measured badge height and updated Overview module card coordinates in XML to ensure clean vertical spacing.

### ⚙️ Gadget Hardening, Furniture Lifecycle & Shader Optimization (Community / devinhorowitz - Issue #84):
- **Alarm System PDA Inventory Icon Restored**: Restored the missing 50x50 icon for `[alarm_system_pda]` in `04_HideoutGadgetsGammaPatch/gamedata/textures/ui/ui_icon_pistol_turret.dds` at grid cell (4, 1), resolving the blank item slot in inventory, trader stock, and crafting menus when installing the Hideout Gadgets G.A.M.M.A. patch.
- **Universal Furniture Pickup Lifecycle Hook**: Wrapped `bind_hf_base.hf_binder_wrapper.pickup` in `stalker_camp_builder.script` to invoke `hf_obj_manager.cleanup_data(obj_id)` before furniture is released by Hideout Furniture. This immediately triggers `hf_on_before_furniture_release` to prune picked-up furniture from `camp.structures`, invalidate the structures cache, clear workstation bindings, erase lingering `hf_data` (preventing persistent `is_on` states on picked-up alarms), and notify external mods (e.g. Interaction Dot Marks).
- **Structure Existence Verification & Defense Ghosting Prevention**: Updated `get_camp_stats` and `has_active_alarm` to verify that `alife_object(id)` exists before tallying settlement structures or granting alarm raid-defense bonuses. Automatically prunes unreferenced or released entity IDs from `camp.structures`.
- **Nixie Display Shader State Caching**: Cached `_last_tens`, `_last_ones`, and `_last_powered` in `display_counter_wrapper` (`bind_display_counter.script`) and skipped `self.object:set_shader` when digit values and power states remain unchanged. Eliminates redundant per-frame mesh shader swaps on every placed counter.

## v1.2.2.1 — Settler Recruitment Idle Animation Hotfix

### 🐛 Critical Bugfix:
- **Settler Idle Animation Crash Fix (`npc_on_update`)**: Fixed a fatal crash (`attempt to call global 'mrandom' (a nil value)`) occurring when recruiting a settler or when unstructured settlers arrive or idle near camp hubs. Promoted `mrandom`, `mcos`, `msin`, `msqrt`, and `tsort` to module scope and routed idle animation rolls to `math.random`.

## v1.2.2 — Dynamic Tactical Map Markers & PAW Crests, Outposts Variance, Water Pump Clarifications & Smart Storage Fixes

### 🧰 Smart Storage & Gun Case Scrap Fix (Community / OnariX):
- **Dedicated Weapon & Armor Storage Routing (`get_auto_sort_target_box`)**: Fixed a bug where Hideout Furniture gun cases (`placeable_gun_case`) were matched as general crafting cases, causing scavengers and 1-click Auto-Sort to dump junk metal scrap and hardware fasteners into weapon cases.
- **Strict Weapon/Armor & Hardware Separation**: Introduced dedicated `weapon_box` (rifles, shotguns, pistols, snipers) and `armor_box` (suits, helmets, tactical gear) routing targets while explicitly excluding weapon cases from `crafter_box`. Metal scrap and ammo parts now route exclusively to toolboxes, craft benches, or the main fallback chest.

### 💧 Water Pump Clarification & In-Game PDA Guide (Community / OnariX):
- **In-Game Guide & PDA Overhaul (`st_guide_s4_body`, `st_guide_s10_body`)**: Completely updated the in-game "How to Play" guide to clarify how water pumps actually function in Hideout Furniture. Clarified that placeable **Metal Barrels** (`placeable_barrel_metal`) and **Sinks** (`placeable_decor_sink`) act as water pumps.
- **Filter Requirements & Refrigerator Deposit**: Detailed the 6-hour production cycle, charcoal/paper filter consumption from camp storage, and clean water flasks automatically depositing directly into camp refrigerators or blue chests. Updated in both English and Russian.

### 🏕️ Dynamic Outpost Garrison Variance (Community / Queen Jadwiga):
- **Dynamic Garrison Sizing without Map Camp Bloat**: Maintained the strict camp density limit (`max_camps_per_map = 3`) while making garrison NPC headcounts vary dynamically across outposts:
  - **Scout Posts (~30%)**: Light garrison of 2–3 NPCs.
  - **Standard Outposts (~45%)**: Fortified garrison of 3–4 NPCs.
  - **Fortified Strongholds (~25%)**: Heavy double-squad garrison of 5–8 NPCs.
- **Dynamic Squad Tier Progression**: Outpost squad compositions now scale with player rank progression, rolling novice, advanced, and veteran squads.
- **Multi-Squad ALife Restraint & Release (`extra_squad_ids`)**: Full lifecycle tracking for multi-squad garrisons, ensuring all squads tether properly to camp stations, respond to alarms, and cleanly release when cleared or converted to mutant infestations.

### 🏷️ UI Polish: Outposts Terminology:
- **Renamed "Rival Camps" Tab to "Outposts" (`st_pda_tab_rivals`, `st_pda_rivals_title`)**: Updated tab labels, headers, and guide sections from "Rival Camps" to "Outposts", properly reflecting that neutral and allied factions (Loners, Clear Sky, Duty, Freedom, Ecologists) can also occupy wilderness outposts.

### 📍 Dynamic Map Spots & PAW Pin/Insignia Integration (Community / Queen Jadwiga):
- **Universal Base & Outpost Markers (`map_spots_homestead.xml`)**: Replaced generic plain dots with distinctive tactical markers. Dedicated `homestead_camp_hub` displays an authentic emerald base icon for settlements.
- **Dynamic Faction Crests & PAW Auto-Detection**: When running alongside PAW (Personal Adjustable Waypoint, standard in G.A.M.M.A.), outposts dynamically render high-res faction crests (Bandits, Monolith, Mercenaries, Loners, Duty, Freedom, Ecologists, Clear Sky, Military, Sin, etc.), red skulls for Mutant Nests, and neutral pins for Abandoned Outposts.
- **MCM Customization**: Added full MCM settings under General and Rivals allowing players to select their preferred icon style:
  - **Settlement Map Marker**: Tactical Base (Recommended) / PAW Stalker Pin / Classic Green Dot.
  - **Outpost Map Marker**: Faction Insignias (Recommended) / Tactical Status Outposts / PAW Pushpins / Classic Colored Dots.
- **DXML Engine Safety**: Mapspot definitions are dynamically injected at runtime via `modxml_stalker_camp_builder.script`, ensuring zero missing-texture crashes even if PAW is not installed.
- **2x Larger Map Markers**: Settlement and outpost markers were too small to read at a glance, so they are now twice the size on the PDA map (settlement hub 22→44px, outposts 20→40px, abandoned 18→36px, mutant nests 16×18→32×36px, faction crests 18→36px, PAW pins 20→40px, skull 12→24px) and 1.5x larger on the minimap. Because PAW's own spot definitions are third-party, Homestead now registers its own `homestead_paw_pin_*` / `homestead_paw_badge_*` spots that reuse PAW's textures at the larger size (only injected when PAW is installed). Old marker names are still cleaned up on existing saves, so markers resize automatically on the next sync.
- **Non-Serialized Map Spots & Save Game Immunity (Issue #26)**: Replaced `level.map_add_object_spot_ser` with runtime `level.map_add_object_spot` across settlement hubs, camp placement, and outpost synchronization. Prevents custom XML mapspot type strings (`homestead_camp_hub`, `homestead_outpost_*`, `homestead_paw_*`) from ever being serialized into save files, ensuring saves remain 100% loadable without "XML node not found in file map_spots.xml" crashes if Homestead or PAW is uninstalled or rolled back. Automated load-time cleanup (`remove_all_camp_map_spots`) purges any legacy serialized custom spots from prior saves and redraws them as runtime unsaved spots.

### 👥 Ghost Companion Self-Heal Squad & Quest Protection (Community / devinhorowitz - Issue #25):
- **Companion Squad Type & Placeholder Resolution**: Fixed `heal_ghost_companion_squads` which previously checked `type(squad) == "table"` and never executed because `axr_companions.companion_squads` holds squad userdata or `false` load placeholders.
- **Strict Story, Quest & Escort Squad Immunity**: Eliminated dangerous negative heuristics. Story companions (Rogue, Stitch, Strelok, Degtyarev), quest escorts (vanilla, New Tasks, Tasks QoL), hostages, and legitimate vanilla companions are completely protected (`companion_cannot_dismiss`, `task_squads`, `hostages_by_id`, active `task_manager` quests, story IDs, and `non_task_companions`) and will never be touched.
- **Persistent Banished Settler Tracking (`record_banished_companion`)**: Recorded banished and dismissed settler IDs in persistent storage (`m_data.stalker_camp_builder_banished_companions`), enabling safe, positive verification of former Homestead companions.
- **Accurate Ghost Squad Purge**: Safely targets and releases only confirmed banished Homestead settler companion squads, settlers reassigned away from companion duties, and legacy orphaned `online_offline_group` companion squads.

### 🛠️ Settlement & Outpost Bugfixes & Polish (Community / devinhorowitz):
- **Outpost Map Spot Churn Prevention (PR #24)**: Re-adds an outpost's tactical mapspot only when its status or faction marker actually changes, preventing redundant engine spot churn.
- **Multi-Squad Stronghold & Outpost Lifecycles (PR #21, #23)**: Extra outpost/stronghold garrison squads are now cleanly released whenever their primary squad is cleared or dismissed, or when individual squad members are recruited as player companions.
- **Settler Companion Hand-off (PR #8)**: Prevents Homestead from overriding the companion scheme when a settler is actively following the player as a companion.
- **Offline Banish in Custom UI Themes (PR #9)**: Extended v1.2.1's offline settler banishment cleanup across Vanilla and Modern PDA theme dialogs.
- **Map Spot Refresh before Locate (PR #18)**: Refreshes outpost markers before triggering "Locate on Map" navigation across all theme pages.
- **Container Sanitizer Optimization (PR #19)**: Stopped running the container sanitizer unconditionally on every routine level load.
- **Looted Stash Entity Release (PR #10)**: Correctly releases scavenged/looted items regardless of whether the target stash container is online.
- **System INI Lookups (PR #11, #12)**: Ensured `ini_sys` is properly read during quest stash verification and auto-sort weapon/armor type checks.
- **Settler Idle State & Animations (PR #14)**: Switched from undefined `"smoke"` state to authentic `"smoking_stand"`.
- **MCM Map Marker Labels (PR #15)**: Restored descriptive UI text strings for custom map marker styles in the MCM menu.
- **Math & Patrol Optimizations (PR #7, #17)**: Hoisted trigonometric math calls in `npc_on_update` and streamlined outpost patrol distance-to-chest calculations.

### ⚡ Performance Optimization & Engine Hardening (ALAO & Codex Audit):
- **Lua 5.1 Prototype Local Limit Resolution (`update_rival_camps`)**: Eliminated an engine prototype limit issue where `update_rival_camps` accumulated 236 locals (exceeding Lua 5.1's 200-local prototype ceiling). Modularized the lifecycle loop into `process_single_rival_camp` (dropping locals to 92) and hoisted `spawn_rival_camp_defenses_and_decor` to module scope (reducing `spawn_single_rival_camp` locals to 134).
- **Hot-Path Closure Allocation Elimination**: Replaced anonymous function heap allocations inside `pcall` (e.g. `pcall(function() return pos:distance_to(pos2) end)`) with direct method invocations `pcall(pos.distance_to, pos, pos2)` in `safe_distance` and `is_squad_alive`, eliminating garbage collection stutter during distance scans.
- **Fast Distance Sqr Calculations**: Converted repeated `distance_to()` distance checks to `distance_to_sqr()` across entity scans and radius checks.
- **Scratch Vector Pre-Allocation**: Pre-allocated scratch vectors outside loops across squad positioning routines (`setup_rival_squad_positions`, `update_rival_camps`), avoiding constant C++ vector allocations and deallocations.
- **Fast Literal String Matching**: Added `plain = true` to fixed string searches in monkeypatched PDA scripts.
- **Dead Code Pruning**: Stripped unused functions, legacy stubs, and dead variables across `bind_display_counter.script`, `ui_stalker_camp_builder_pda.script`, and `stalker_camp_builder.script`.

### 🛑 Outpost net_spawn Duplicate ID & m_crows Crash Fix (Community / Gabe):
- **Level Load `m_crows` Queue & Re-anchor Desync Elimination (`snap_rival_camps_to_ground`)**: Fixed a fatal engine assertion crash (`assertion !m_crows[1].empty() failed: 4` dumping `placeable_stove1`, `placeable_table1`, `placeable_bed_1`, `placeable_radio`) followed by `CGameObject:net_spawn() Object with ID already exists! ID=50439 self=sim_default_killer_050439 other=sim_default_killer_050439`. Previously, `snap_rival_camps_to_ground` released existing decorations with `alife_release` and immediately called `sim:create` while `CObjectList` was processing initial level spawns, corrupting the engine's internal update queue. Decorations now have their coordinates (`position`, `m_level_vertex_id`, `m_game_vertex_id`) updated in-place without releasing or re-creating entities.
- **Online Entity Teleport Safety (`safe_teleport_object`)**: Stopped `TeleportObject` / `alife():teleport_object` from being called on online creatures or entities sharing the same game vertex. When an NPC is online on the active level, Homestead now repositions them via `set_npc_position(pos)` and updates their server coordinates directly, preventing the engine from attempting duplicate client-side `net_spawn()` registrations.
- **Delayed Level-Entry Orchestration**: Deferred `snap_rival_camps_to_ground`, `restrain_rival_squads`, and `populate_gamma_rival_chests_on_load` from synchronous `actor_on_first_update` execution into a dedicated 2.5-second `CreateTimeEvent`. This guarantees level geometry, pathfinding graph, and ALife entity spawn queues are completely idle before any outpost adjustments occur.
- **Streamlined Ground Vertex Probing (`get_ground_vertex_and_pos`)**: Optimized the height offset table and spiral radius in `get_ground_vertex_and_pos` to eliminate excessive CLevelGraph `vertex_id` queries on off-mesh positions, eliminating dozens of lines of `Invalid position for CLevelGraph::vertex_id specified` log spam.

## v1.2.1 — Community Hotfix: Ghost Companions & Settler Idle Animations

### 👻 "Ghost Companion" Desync Elimination (Community / OnariX):
- **Full Companion Squad & ALife Purge on Banish (`purge_settler_companion_and_squad_state`)**: Fixed the critical bug where asking a free settler to become a companion and subsequently banishing them turned them into permanent "ghost companions" (lingering HUD health bars, slow foot-following behavior, and unmanageable squad state). Homestead now completely strips companion squad registration (`axr_companions.companion_squads`), unregisters ALife squad members, releases dedicated companion groups, clears saved persistent variables (`se_save_var`), and revokes companion/holding infoportions.
- **Universal Offline Banish Support (`SettlementManagerPDA:OnBanishClicked`)**: Fixed the PDA remote banishment handler which previously skipped all ALife/companion cleanup whenever the target settler was offline or on another level.
- **Save-Migration Self-Heal (`heal_ghost_companion_squads`)**: Added an automated sweep to `run_settler_self_heals` that scans on load and heals existing saves affected by ghost companion squads, instantly wiping orphaned HUD health bars and freeing stalkers to live independently.

### 🎭 Broken Settler Idle Animation Fix (Community / DaWeeDick):
- **Eliminated Broken `play_guitar` & Floor-Clipping `sit_ass`**: Removed broken `play_guitar` calls (which caused stalkers without guitars to strum empty air or contort into broken poses) and ground-clipping `sit_ass` states that caused settlers' lower bodies to sink into wooden platforms, building floors, and uneven terrain.
- **Authentic Zone Idle Animation Pool**: Settlers resting or idle in camp now utilize a curated, rock-solid engine animation pool: relaxed standing (`wait_na`), alert guard (`guard`), environmental scanning (`caution`), smoking a cigarette (`smoke`), resting on one knee (`sit_knee`), ready stance (`threat_na`), and hands-behind-back (`ward`).
- **`axr_beh` Scheme Animation Synchronization**: Resolved the root cause of violent animation flickering and twitching. In `setup_settler_beh_logic`, Homestead now dynamically updates `st.beh.wait_cond` and `st.beh.wait_animation` to match the assigned animation, permanently stopping `axr_beh:beh_wait()` from overwriting `state_mgr` back to `"guard"` every frame.
- **Dynamic 20–35s Idle Animation Cycling**: Idle camp settlers now naturally switch stances every 20–35 seconds, making settlement life feel active and authentic without freezing NPCs in place indefinitely.

## v1.2.0 — Settlement Stability, Engine Hardening & Rival Outpost Polish

### 📦 Cross-Map / Offline Stash Persistence & Remote Job Execution:
- **Persistent Settlement Inventory Cache (`camp.stored_items`)**: Implemented a self-contained cross-map inventory tracking system stored directly inside active camp data in `alife_storage_manager`. Settlements now maintain continuous awareness of all items across chests, workbenches, and fridges even when the player is on another map or far away.
- **Offline Settlement Job Execution**: Solved the mod-breaking bug where jobs (Cook, Craft, Repair, Brewer, Medic, Woodcutter, Settler Eating) would randomly pause and freeze timers when the actor travelled to another level due to offline containers returning 0 items. Jobs now seamlessly detect, consume, and produce items while offline without stalling.
- **Water Pump & Filter Automation**: Fixed water pump item generation while remote; pumps now reliably consume filters/charcoal/paper and produce bottled clean water in settlement storage every 24 hours, unblocking Brewer and settler hydration routines Zone-wide.
- **iTheon's PDA Inventory System Integration**: Added cross-reference integration with `tb_inv_cache` (`a_ui_pda_inventory_cache.script`), ensuring Homestead settlements read and respect multi-level stash caches when running alongside iTheon's PDA suite.

### ⏱️ Job Timer Skew & Pause Desync Fixes:
- **`get_job_progress` Camp Resolution Bug**: Fixed a severe engine bug in `stalker_camp_builder_jobs.script` where `get_job_progress` called `get_job_paused_status` without passing `camp` or `hub_id`. This previously caused every job requiring containers or furniture (stoves, bidons, lamps, workbenches) to evaluate as paused and freeze progress bars indefinitely.
- **Reload & Level Transition Time Skew Guard**: Guarded `tg_update`, `homestead_teardown_grace_until`, and `actor_update_slot` in `stalker_camp_builder.script`. When quickloading or switching levels where `time_global()` resets to 0, Homestead now immediately resets its scheduling timers, eliminating multi-minute background update freezes.
- **PDA UI Live Timer Loop Protection**: Added clock skew recovery to `SettlementManagerPDA:Update()` and `Reset()` across all UI themes so negative delta ticks (`tg < _last_survivors_tick`) never permanently lock the survivor progress and overview polling loops.

### 🎨 FOMOD Theme Selection & Visual Options:
- **Selectable PDA Themes**: Added a dedicated FOMOD installer step allowing users to choose their preferred Settlements interface style:
  - **Modern Vanilla (Default & Recommended)**: The polished v1.2.0 blend of clean vanilla layout, sharp typography, and restored tactical colored module borders, cards, headers, and alert banners.
  - **Vanilla**: The flat vanilla reskin using standard Anomaly UI frames, dark transparent modules, and vanilla button styling.
  - **Modern**: The legacy v1.1.8 theme featuring dark textured cards, neon accent borders, custom tactical buttons, and modern typography.
  - **No PDA Tab**: Completely disables the remote PDA tab, allowing players to manage settlements exclusively in-person at Camp Hub workbenches.
- **Standalone 00_Core Fallback**: Bundled default Modern Vanilla configs and textures directly into `00_Core` so manual non-FOMOD drag-and-drop installations work out of the box without missing UI elements.

### 🎨 PDA UI Restoration & Colored Borders:
- **Restored Authentic Colored Borders & Frames**: Brought back custom bordered styling (`ui_card_bg.dds`, `ui_module_bg.dds`, `ui_module_header.dds`) featuring cyan/slate frames around module containers and section headers across Overview, Survivors, Rivals, Radio, and Guide tabs.
- **Dynamic Colored Status & Alert Banners**: Restored `ui_banner_secure.dds` (green border), `ui_banner_threat.dds` (red border), and `ui_banner_neutral.dds` (gold border) for raid alerts and rival status notifications, complete with color-matched text.
- **Card Selection Highlights**: Restored glowing amber/orange borders (`ui_card_selected.dds`) when highlighting settlement and survivor cards.
- **Flawless Layout Alignment**: Preserved vanilla reskin typography and button styling while ensuring 20px header boxes and card containers sit flush without text clipping or overlaps.

### 💥 Critical Crash & Transition Fixes (Community / Swittens):
- **Level-Transition Crash Fix (`find_ground_anchor`)**: Diagnosed and resolved a critical crash occurring during level transitions (e.g. Dark Valley to Garbage) or when rival camps initialize. Fixed a Lua forward-reference bug in `stalker_camp_builder_rivals.script` where `setup_rival_squad_positions` attempted to invoke `find_ground_anchor` before its local function declaration, triggering `attempt to call global 'find_ground_anchor' (a nil value)`.
- **Safe Cross-Level Settler Dismantle**: Guarded `utils_obj.switch_online` during settlement dismantling in `stalker_camp_builder_recruit.script` so it only executes when `camp.level == level.name()`, eliminating forced online-switching crashes across remote levels.

### 🏕️ Settlement Lifecycle & Ghost Camp Elimination (Queen Jadwiga):
- **Workshop Pickup Camp Dismantle**: Fixed the persistent "ghost" settlement bug where physically picking up the camp workshop / workbench box in Hideout Furniture left orphaned settlement records in memory and active markers in the PDA. Hooked `stalker_camp_builder.dismantle_camp` directly into `hf_workshop_wrapper:pickup()`.
- **Authentic Settlement Map Markers**: Upgraded player settlement map icons from generic stash markers (`treasure_player`) to dedicated settlement icons (`green_location`), with automated cleanup of legacy stash spots upon loading.
- **Rival Camp Map Spot Refresh**: Fixed the "Show on Map" button in `ui_stalker_camp_builder_pda.script` (`OnLocateRivalMapClicked`), forcing an immediate map spot synchronization prior to navigating to the Area Map tab.

### 🚶 Settler Recruitment & Immersion (Queen Jadwiga):
- **Natural Walk-In Recruitment**: Same-level online recruits now realistically walk to camp (`set_dest_level_vertex_id`, `move.walk`) and dynamically anchor to the camp's local smart terrain (`anchor_settler_to_smart`), replacing jarring instant teleportation.
- **Dialogue Clutter & Speaker Flow Fix**: Cleaned up settler dialogue trees in `modxml_stalker_camp_builder.script` (phrase `100`), removing redundant and looping options (idle talk, workbench use queries, generic status reports).
- **Squad Reset Prevention**: Moved the "Return to my squad" dialogue option to the very bottom of the menu to prevent accidental clicks.
- **Hunter Job Localization**: Added missing Hunter job dialogue strings and responses (`st_job_hunter_ask`, `st_job_hunter_done`) in both English and Russian.
- **Missing Audio Reference Removal**: Removed nonexistent `interface\inv_money` sound reference that caused harmless log error spam during paid recruit hiring.

### 🏰 Rival Camp Spawning & Diagnostics (Queen Jadwiga):
- **Fresh-Game Spawn Guarantee**: Resolved an issue where rival camps failed to spawn on brand-new playthroughs if the initial spawn roll failed, leaving the rival camp system seemingly dormant. Guaranteed an immediate first-cycle spawn check when total rival camps equal 0.
- **Detailed Spawn Diagnostics**: Added verbose rival camp spawn diagnostic logging under debug logging mode (`sb.cfg.debug_logging`) for rapid troubleshooting.

### 🧹 Streamlined Uninstallation & World Object Cleanup:
- **Uninstall Prep (MCM Debug Option)**: Added `Uninstall Prep: Purge All Rival Camp Furniture` toggle under MCM Quality of Life & Debug. Instantly despawns and permanently releases all defensive walls, barricade plates, sandbags, stoves, beds, crates, and decorations spawned across every rival camp throughout the Zone via engine `alife_release`.
- **Zero-Footprint Uninstallation**: Safely prepares existing savegames for mod removal without leaving orphaned physics entities or static collision meshes embedded in level geometry.
- **In-Game Confirmation & Auto-Reset**: Sends a clear in-game notification upon completion and automatically resets the MCM toggle back to `false`. Full English and Russian localization included.

### 🛡️ Nil-Safety & Engine Hardening Pass:
- **BEH Scheme Engine Hardening (`scheme=beh stype=nil`)**: Resolved severe log error spam (`!ERROR: ... trying to use a scheme not intended for stype scheme=beh stype=nil`) in `stalker_camp_builder_npc.script` (`setup_settler_beh_logic`). Guaranteed proper stalker entity type initialization (`st.stype = modules.stype_stalker`), proactive evaluator registration (`schemes_by_stype[0]["beh"] = true`), and defensive fallback configuration via `xr_logic.configure_schemes`. Settlers now cleanly and reliably lock to workstation vertices without failing scheme checks or spamming engine logs.
- **MCM Bad Path Fix**: Eliminated invalid path queries (`purge_rival_furniture`) in `stalker_camp_builder.script`, completely silencing repeating `!MCM given bad path:stalker_camp_builder/qol_debug/purge_rival_furniture` log errors.
- **Offline Object Log Spam Elimination (`_G.get_object_by_id`)**: Safely wrapped `_G.get_object_by_id` in `z_stalker_camp_builder_pda_monkeypatch.script` so querying offline entities returns `nil` without triggering false alarm `!ERROR get_object_by_id | no game object recieved from id` console messages.
- **Turret & Workshop Stash Lookup Hardening**: Replaced raw `get_object_by_id` calls in `bind_workshop_furniture.script` and `ui_pistol_turret.script` with safe `level.object_by_id` and server object fallbacks.
- **"Busy Hands" Expedition Haul Deposit Elimination**: Diagnosed and eliminated a critical Lua runtime crash (`utils_stpk.script:432: get_item_data` -> `[BusyHandsDebug] Runtime Error`) during scavenger expedition returns. Removed a redundant, duplicate post-registration packet write call on already-registered container items, and safeguarded all `utils_stpk` packet manipulations in `deposit_item_to_camp` and `deposit_expedition_haul` under defensive `pcall` wrappers.
- **`se_save_var` C++ Engine Hardening (`se_obj:name()` Access Violation)**: Diagnosed and resolved the fatal engine crash (`original_alife_create_item` / `se_obj:name()` C++ exception) occurring during expedition loot deposits. Patched `_G.se_save_var` in `patch_alife_storage_manager()` to safely pre-populate storage entries without triggering uncatchable engine exceptions when querying `:name()` on freshly registered container items. Safely wrapped all item name resolutions in `deposit_item_to_camp`.

### 🛡️ Container Integrity & Engine Crash Prevention (`xrServer::Perform_destroy`):
- **Automated Orphan Container Child Sanitizer (`child registered but not found`)**: Implemented `stalker_camp_builder.sanitize_orphan_container_children()` running on level initialization (`actor_on_first_update`). Automatically detects any containers or stashes across the Zone whose internal engine `children` vector references deleted/nonexistent object IDs (the fatal engine assertion `xrServer::Perform_destroy -> child registered but not found [ID]`). Safely clones the container, cleanly migrates all valid items and story IDs, updates active cache registrations in `treasure_manager` and Homestead camp stashes, and safely releases the corrupted container entity, curing affected save games on load.
- **Expedition Scavenger Container Detach Safeguard**: Hardened expedition scavenging item releases in `stalker_camp_builder.script`. Scavenged items scheduled for release from stashes are now explicitly detached via `sim:teleport_object` before engine release, guaranteeing the engine's `Perform_reject` fires and prevents phantom child ID references from ever being left behind in stash containers.
- **Recruitment & Dialog Hardening**: Protected `character_rank()`, NPC goodwill, and recruit position setting in `stalker_camp_builder_recruit.script`, eliminating edge-case nil-pointer crashes when interacting with companions or survivors.
- **Fast-Travel Combat & Funds Validation**: Guarded `best_enemy()` combat locks and money deduction routines against nil actor instances during fast-travel execution.
- **Rival Outpost Actor Safety**: Hardened community relation lookups, rank checks, and distance calculations in `stalker_camp_builder_rivals.script`.

### ⏱️ Savegame Health & Pending Condition Auto-Purge:
- **Timestamp Tracking**: Item condition queues (`pending_item_cond`) now track in-game timestamps for all spawned, crafted, or scavenged equipment.
- **Automated Stale Entry Pruning**: Any queued item condition whose ALife object no longer exists is immediately discarded. Uncollected items pending for longer than 7 in-game days are automatically purged to prevent savegame bloating across long playthroughs.
- **Non-Intrusive Distant Outpost Alerts**: Preserved the 10-minute cooldown and subtle audio profile for rival camp distress calls, preventing radio spam while maintaining Zone immersion.

### 🔌 Third-Party Mod Compatibility Wrappers:
- **Catspaw PAW Waypoint Creature Recognition**: Added server object section fallback (`se_obj:section_name()`) to `tasks_placeable_waypoints.safename` so Personal Adjustable Waypoint markers accurately resolve and display creature names instead of returning "Unknown" when mutants are offline.
- **Surge & Psi-Storm Cover Protection**: Hardened `pos_in_cover` overrides in `z_stalker_camp_builder_pda_monkeypatch.script` with `pcall` execution, ensuring external weather or ambient mods passing irregular coordinate structures never interrupt engine blowout cycles.
- **Chained Subdialog Hooks**: Verified non-destructive chaining on `pda.set_active_subdialog` for seamless compatibility with custom UI frameworks.

### 🔧 Scavenger Gear Integrity & Engine Callback Sync:
- **Worn-Condition Stash Scavenging**: Fully verified and integrated WPO-compliant degradation for scavenged outfits, helmets, and weapons via `loot_due_stashes`, preventing items from resetting to 100% condition.
- **Pre-Registration Packet Writing**: Degradable equipment is created with packet condition written prior to simulation registration via `alife_create(..., false)`.
- **Engine Callback Synchronization**: Container open, hover, and item pickup events immediately enforce worn states and GAMMA parts damage tables before UI render.

## v1.1.9 — Worn-Condition Guarantee, Community Economy & PDA Theming Overhaul

### 🛡️ Worn-Condition Guarantee & Item Persistence (Danzy Fix):
- **Worn-condition persistence for scavenged/crafted gear**: Resolved the critical bug where scavenged outfits, helmets, and weapons returned to camp at 100% condition.
- **Stash scavenging parts integrity & untouched loot fix**: Fixed `loot_due_stashes` so default 100% parts from untouched world stashes are not passed into camp deposits. When loot is untouched, `deposit_item_to_camp` now cleanly rolls authentic worn condition and degraded parts matching WPO standards.
- **Pre-registration packet condition (engine standard)**: Degradable gear is now created via `alife_create(..., false)` with packet condition written prior to simulation registration, preventing the engine from spawning items with default 100% health packets.
- **Engine-compliant UI and container condition hooks**: Replaced non-existent `game_object_on_net_spawn` hook with native Anomaly engine callbacks (`ActorMenu_on_mode_changed`, `ActorMenu_on_item_focus_receive`, `actor_on_item_take`, `actor_on_item_take_from_box`), ensuring items in camp containers have their worn condition and degraded parts applied immediately before UI rendering.
- **Dual-keyed parts persistence**: Saved parts tables are now indexed under both `nil` and `obj:name()` so GAMMA's `evaluate_parts` and UI tooltips always read matching worn states without accidentally recalculating parts back to 100%.
- **"Busy Hands" expedition return crash fix**: Refactored the settler return sequence to defer online state switching safely via `CreateTimeEvent` instead of instantaneous teleportation, preventing uncatchable engine exceptions.
- **Map icon clutter elimination**: Replaced duplicate green map markers and boundary icons with a single clean settlement marker (`treasure_player`), including automated cleanup of obsolete markers from existing savegames.
- **MCM yield balancing**: Added configurable options for Scrapper and Woodcutter yields (`yield_wood_min/max`, `yield_scrap_min/max`, `yield_fasteners_min/max`).

### ⚙️ Technician & Economy Balancing (Danzy Balance Pass):
- **Workbench-only technician repairs**: Technicians now only repair damaged gear placed into designated workbenches (`workbench`, `repair_bench`) or the settlement hub workshop box. Loot and equipment stored in player personal stashes remain untouched at their found condition.
- **Damaged gear scan filter**: Restructured camp inventory iteration so damaged items outside of workbenches do not trigger unwanted repair cycles or false shortfall states.
- **Job pause cache fix**: Corrected survivor pause status caching so reloads or job changes immediately refresh status badges instead of being pinned to old reasons (e.g., scavengers getting stuck on "No Damaged Gear").
- **Basic ammo crafting restriction**: Settler ammo crafting is restricted to basic (non-AP) calibers, preserving high-tier ammo economy.
- **Medic crafting balance**: Balanced medical supplies recipe (`medkit` now requires 4x vodka + bandage rather than 2x vodka).
- **Yield scaling**: Balanced baseline outputs for Woodcutters (4-8 base, 8-12 with axe), Brewers (2 base, 4 with drug kit), and Scrappers (3-6 scrap, 1-3 fasteners; 6-10 / 2-5 with tools).

### 📱 Vanilla PDA Reskin & Dynamic Theming (dynz & Community):
- **Centralized UI role theming**: Integrated `ui_stalker_camp_builder_theme.script` providing structured role-based styling (`heading`, `body`, `good`, `warn`, `danger`, `button_on`) matching native Anomaly PDA design language.
- **Vanilla PDA aesthetics**: Deployed dynz's updated Vanilla Reskin layout (`ui_stalker_camp_builder_pda.xml`, `ui_pda_stalker_camp_builder.xml`) and complete texture set (`btn_*`, `tab_*`, `ui_banner_*`, `ui_card_*`, `ui_module_*`, `thumb_*`).
- **Texture description mappings**: Comprehensive coordinates for UI tabs, faction indicators, map thumbnails, and status rules.

### 🏰 Fortified Rival Camp Architecture & Sentry AI Overhaul:
- **Perimeter Defensive Walls & Barricades**: Completely overhauled rival camp generation with authentic defensive fortifications. Camps now spawn complete perimeter structures including rear defensive walls (`placeable_wall` / `placeable_wall_metal`), flank barrier dividers (`placeable_wall_divider`), front combat cover barrels (`placeable_barrel_metal`), and reinforced barricade plates with a designated entrance chokepoint.
- **Faction-Themed Architectural Aesthetics**: Defensive materials now adapt dynamically to the occupant faction (corrugated metal walls and scrap plating for Bandits/Renegades; reinforced military walls, ammo crates, and metal tables for Duty/Military/Mercenaries; wooden palisades, camp stoves, and benches for Loners/Clear Sky).
- **Eliminated Nonsensical Clutter**: Removed ungrounded documents, loose ashtrays, and random floor props. Every camp item now serves a cohesive survival, defense, or logistics purpose (sheltered cot, heating stove, ammo crate, supply crate, communications table with radio).
- **Fixed NPCs Stuck on Blue Box**: Resolved the physics collision bug where squad members spawned directly into the center coordinates of the blue stash box, trapping them atop the box lid. Squads now spawn distributed across dedicated exterior sentry stations 2.5m – 4.5m away.
- **Active Camp Movement & Dynamic Sentry Patrols**: Fixed `npc_on_update` lookup caching so rival NPCs are recognized by the AI orchestrator. Sentry NPCs now patrol smoothly between fortified posts, execute vigilant guard/resting animations (`guard`, `threat_na`, `caution`, `smoke`, `sit_knee`) looking outward towards threats, and instantly break into uninhibited vanilla combat if an enemy appears.
- **Automatic Savegame Dislodging**: Integrated an automated check that detects NPCs perched on top of stash boxes in existing saves and safely relocates them to ground guard stations on load.

### 📦 Streamlined Packaging & Default PDA Integration:
- **Default Vanilla PDA Reskin**: dynz's Vanilla Reskin layout and complete texture assets are now installed directly as part of the core mod experience.
- **Removed Developer Preview Mock**: `zz_homestead_ui_preview.script` removed from release distributions to prevent mock settlement injection into live saves.
- **Simplified FOMOD**: Removed legacy PDA/No-PDA and alternate UI theme toggles so all users receive the authentic vanilla settlement PDA tab out-of-the-box.

## v1.1.8 — Community Fixes by danzy (merged)

**Credit: [danzy] — camp simulation fixes, performance passes and rival camp improvements, shared as a community patch for v1.1.7.** Merged with two modifications at the author's request (see below). Thanks danzy!

### 🐛 Simulation Fixes (all by danzy):
- **The storage lookup bug** — a lot of the camp simulation (jobs, rival camps, raids, morale, turret top-ups) was silently not running: `invalidate_server_container_cache` cleared only one box's cache entry, making that box read as **empty** until the next registry rebuild — so cooks found no meat, medics no vodka, turret maintenance no ammo, and surplus/morale checks saw nothing. Invalidation now forces a full rebuild. *This one fix is why turrets "never got topped up from camp storage" — the topping-up code was always there; it just read an empty chest.*
- **Camp chest selection** — new `sanitize_primary_chest` (applied on load via `normalize_camps` and inside `find_best_container` / `get_auto_sort_target_box`): the camp's main chest can no longer be a fridge, medstation or workbench, so settlers stop dumping everything into the fridge/medstation. General output now goes to the nearest real stash, with the fridge as a last resort.
- **Scavengers standing around in camp fixed** — the `npc_on_update` job-movement system was rebuilt around a data-driven `JOB_DISPATCH` table, resting scavengers no longer return early regardless of expedition state, and `script_release` is applied once per spawn instead of fighting the movement every think.
- **Hospitality buff actually works now** — the old buff set a timer nothing read. Eating cooked food or sleeping at a settlement with good morale (≥60) now applies a buff that slowly restores health and stamina while it lasts.
- **Hunger matters** — settlers going hungry now drop camp morale (−5 per hungry settler, max −30) and you get a PDA news message about it, feeding the existing low-morale abandonment logic.
- **Turret top-up from camp storage** — fixed by the storage lookup bug above (the maintenance code was correct; it read an empty chest).

### ⚡ Performance (all by danzy):
- The big 10-second update is now **time-sliced**: one system group per second across a 10-slot rotation (`PERIODIC_ACTOR_TASKS`), so camps/jobs, rival camps, raids, events, morale, refugees, eating and map-spot sync no longer all hitch on the same frame.
- Random NPCs near you were being checked against your camps **every tick** — non-settlers are now remembered and only re-checked every 5 seconds.
- Settlers think about once a second (was ~6×/second), the meet-manager re-assert is throttled to 10s, and `script_release` is applied once per spawn.
- The near-camp furniture rescan dropped from every 60s to every 10 minutes, and the structure-scan cache TTL from 2 minutes to 10 — placing or picking up furniture still updates the camp immediately.

### 🏕️ Rival Camps (by danzy):
- Fixed the **stutter when a rival camp spawned**: smart terrains never change during a session, so they are now mapped to their levels **once** and cached (`build_smart_cache`), instead of re-scanning every smart in the game per spawn attempt.
- **New rival camps only spawn on other maps**, so you never get the NPC load-in hitch near you. (The MCM debug "respawn rival camps" button can still force one on your map.)
- Ground-anchor fix: when the walkable AI vertex and the visual ray disagree, the anchor now trusts the AI mesh — the actual root cause of camps sinking/floating.

### ⚖️ Balance tweaks from danzy's edit (included):
- Medic output nerf: `medkit_ai2` (Army Medical Package) → regular `medkit` — the army kit was too strong for 2 vodka.
- Drug-Making Kit now actually doubles medic output (was advertised but never implemented).

### 🔧 Modifications made while merging (author's request):
- **Rival camp furniture is NOT removed** — danzy stripped all rival-camp decorations (they ended up jumbled) via a hard-coded flag. In v1.1.8 that becomes the **"Rival Camp Furniture" MCM toggle (default ON)** in the Rivals group: OFF clears decor already placed at existing camps and stops new camps/tier upgrades from spawning furniture. His ground-anchor and smart-cache fixes are kept either way.
- **Trade routes are NOT cut** — danzy removed the dead trade-route system; it is fully restored in v1.1.8 (transfer_supplies, establish/remove route, process_trade_routes wired into the staggered update) ahead of a proper route-setup UI.

## v1.1.7 — Unified Offline Simulation Contract, Sleep Catch-Up Engine, Turret Crash Fix & Balance Overhaul

### 🚨 Hotfix — Jobs stuck at "(Ready)" with no badge (Brewer / Repairer):
- **Problem**: Jobs sat at gold "(Ready)" indefinitely — no countdown, no production, and no `[PAUSED]` or `[WAITING]` badge explaining why (observed on Brewer and Repairer; Medic/Cook correctly showed their `Stockpile Full` reasons).
- **Root Causes**:
  1. **Silent dispatch errors**: when a job's per-cycle dispatch threw a Lua error (e.g. from an engine call hitting a specific camp state), the error was swallowed by the outer `pcall(update_camp_jobs)` — the shortfall park was never reached, `shortfall_reason` was never set, and the survivor's elapsed clock stayed at ≥100% forever. A pcall-swallowed error also produces no log line, making it invisible.
  2. **Shortfall park did not pin the clocks**: the park only set `paused_elapsed`; the display could still read ≥100% ("Ready") during the backoff window.
  3. **Repair had no shortfall reasons at all** — "nothing to repair" parked silently.
- **Fix Applied**:
  - Each per-cycle dispatch now runs in its **own pcall**. A throwing job no longer vanishes: the survivor shows `[WAITING: Job Error]`, the park/backoff applies, and the real error is written to the log once (`[Homestead] job dispatch error (job=..., npc=...): ...`) so the underlying cause can be identified.
  - The shortfall park now **pins the job clocks** at the 30-second backoff mark — the PDA shows an honest `~30s → 0s` retry countdown instead of ever reading "(Ready)" while waiting.
  - `process_gear_repair` gained shortfall reasons: `No Storage Container` and `No Gear to Repair`.
  - The `[WAITING: reason]` badge now includes the live retry countdown (`[WAITING: No Clean Water] (27s)`).
- **Note on `[PAUSED: Stockpile Full]`** (Medic/Cook in the screenshot): that is the by-design surplus cap (`enable_surplus_cap` in MCM) — production halts so camp storage is not flooded with meals/meds. Disable the MCM option if you want those professions to keep producing past the cap.

### 🍺 Brewer `[WAITING: Job Error]` root cause fixed (nil `pairs_` in `process_brewer_job`):
- **The diagnostic hook paid off immediately**: the logged dispatch error was `stalker_camp_builder_jobs.script:2003: attempt to call global 'pairs_' (a nil value)`.
- **Root Cause**: the Unified Inventory refactor used the `pairs_` alias inside `process_brewer_job`, but that alias is a **function-scoped local** defined only in `update_camp_jobs`, `_calc_job_paused_status`, and `spawn_scavenged_loot` — so every brewer cycle threw before doing anything, permanently parking the job at `[WAITING: Job Error]`.
- **Fix Applied**: `process_brewer_job` is covered again, and as insurance against the same refactor class anywhere else, **file-level aliases** (`pairs_`, `ipairs_`, `tostr`, `type_`, `mmin`, `mmax`, `mfloor`, `mabs`, `sfind`) were added to the top of the jobs, main, and rivals scripts. Function-local defs shadow them harmlessly; any function using an alias without declaring it now resolves correctly instead of throwing mid-cycle.

### 🏛️ Unified Offline Simulation Contract & Sleep Catch-Up Engine:
- **Single Source of Truth for Settlement Inventory**:
  - Implemented the Unified Settlement Inventory Contract (`sb.camp_iterate_inventory`, `sb.camp_find_item`, `sb.camp_consume_item`, `sb.camp_count_item`, and `sb.camp_has_item`), completely eliminating the online/offline "split-brain" architecture.
  - Replaced over 600 lines of fragile, duplicate container loops across all 11 settler professions and settlement systems.
  - Seamlessly bridges online client container iteration (`safe_iterate_inventory_box`) and offline server registry iteration (`iterate_server_container` via `_G.server_objects_registry`) under a single contract. Settlement jobs, pantry counts, and chest operations run with identical deterministic precision whether the player is standing inside camp or on the other side of the Zone.
  - Fixed multi-use item handling across online and offline states via `sb.consume_one_use`, correctly decrementing uses on client items and server entities alike (`utils_item.set_uses` / `se_item:set_remaining_uses`) or releasing the item when depleted.
  - Refactored Water Pump filter consumption, Food Chilling (fridge freshness preservation), and Trade Route logistics to route through the unified contract.
  - Fixed a crash in `check_camp_chest_supplies`: defined local `check_sec` to properly evaluate food and drink rations across camp containers.
- **Sleep & Fast-Travel Multi-Cycle Catch-Up Time Dilation**:
  - Overhauled `update_camp_jobs` with full time-dilation catch-up. Previously, sleeping or fast-traveling discarded accumulated production cycles because `survivor.job_start_time` was reset after running a single cycle.
  - Settlement production now calculates accumulated elapsed cycles (`cycles_accum = math.floor(effective_elapsed / effective_interval)`) and processes up to 5 cycles per 10-second tick until caught up (`cycles_to_run = math.min(5, math.max(1, cycles_accum))`).
  - Timestamps advance by exact cycle increments (`sec_advanced = cycles_completed * effective_interval * tf`), maintaining accurate simulation time without spiking CPU frametimes.
  - If a production cycle encounters a resource shortfall mid-catchup (e.g. running out of raw meat for cooking or clean water for brewing), catch-up halts cleanly, records the specific `shortfall_reason`, and backs off by 30 seconds rather than thrashing or corrupting state.

### 🏕️ Rival Camp Grounding & Decor Pool Sanitization:
- **Underground Decoration Elimination**:
  - Increased rigid-body clearance for rival camp props from +0.20m to +0.38m above raycast terrain surface, preventing initial physics interpenetration with ground geometry.
  - Eliminated the aggressive 10-second respawn loop in `stalker_camp_builder_rivals.script`. Re-anchoring now triggers only if an object has truly clipped below the surface (`y < surface_y - 0.15m`) or drifted into the sky (`y > surface_y + 1.5m`), preserving settled props and freezing their physics shell to stop jitter and clipping.
- **Sanitized Decoration Pools**:
  - Replaced 10 nonexistent or invalid LTX sections in `decor_pool`, `t2_decor_list`, and `t3_decor_list` (`placeable_target_practice`, `placeable_sign_stop`, `placeable_table_wooden`, `placeable_stool`, `placeable_table_round`, `placeable_couch`, `placeable_counter`, `placeable_shelves`, `placeable_bed_military`, `placeable_bed_bunk`) with verified valid placeable props (`placeable_chair_office`, `placeable_guitar`, `placeable_chair_wood_01`, `placeable_stool_kitchen`, `placeable_chair_wood_02`, `placeable_workbench_small`, `placeable_bed_mattress`, etc.).

### 🪓 Job Execution, Supply Transparency & Shortfall Fixes (Brewer & Woodcutter):
- **Shortfall Freeze Elimination**:
  - Fixed an issue where settlers whose job could not produce due to missing ingredients (e.g. brewer lacking clean water or woodcutter lacking wood scraps for charcoal) had their timer clamped at `effective_interval`, leaving them permanently stuck displaying `(Ready)` in the PDA without ever explaining why nothing was being produced.
  - In `update_camp_jobs`, shortfall states now apply a 30-second backoff (`paused_elapsed = math.max(0, effective_interval - 30)`) so production is retried promptly as soon as supplies arrive.
- **Supply Transparency & Diagnostics in PDA**:
  - Both the survivor list item and detail panel now explicitly report the shortfall cause in gold text: `[WAITING: No Clean Water]`, `[WAITING: No Still]`, or `[WAITING: No Wood Scraps]`, replacing the confusing "Ready" label.
  - Cleared `shortfall_reason` immediately once materials are supplied and production succeeds.
- **Expanded Water Matching for Brewers**:
  - Clean water detection in `_calc_job_paused_status` and `process_brewer_job` now recognizes canteens (`canteen`), flasks, mineral water, and all clean water variants.
- **Distillery Requirements & Localization**:
  - Added still/stove validation before distillation starts. If neither a Milk Can (Bidon) nor Camp Stove is detected, the brewer reports `No Still`.
  - Added new localized string `st_job_brewer_need_still` to both English and Russian XML tables (`configs/text/eng` and `configs/text/rus`).

### 🎒 Scavenger Expedition Safety & Camp Patrol Restoration:
- **Expedition Desync Watchdog & Exception Isolation**:
  - Added a failsafe watchdog in `process_stash_expeditions` (`elapsed >= dur` or `game_elapsed > dur + 300`) to guarantee that completed expeditions finalize even if time dilation or sleep fast-forward causes a timing desync.
  - Post-expedition rewards and item transfers are now wrapped in `pcall` with a guaranteed cleanup block: `active_stash_expeditions[stash_id] = nil` and `survivor.on_expedition = nil` always execute, preventing scavengers from ever becoming permanently locked or unusable if an item spawn encounters an unexpected exception.
- **Passive Camp Scavenging Loop**:
  - Scavengers resting in camp (not on active stash expedition) now engage in local camp scavenging patrols every 15 minutes real-time (`rt_interval = 900s`), gathering minor Zone debris and camp salvage.
  - PDA status now displays the live patrol remaining timer (e.g. `Scavenger: Patrolling (12m 30s remaining)`) and indicates when they are available for dispatch.

### 🌐 Cross-Map Trade Routes, MCM Job Parity & Census Optimization:
- **Cross-Map Supply Transfers**:
  - Fixed supply transfers (`transfer_supplies`) between camps located on different game levels. When the source container is offline (`level.object_by_id(source_box_id) == nil`), the transfer engine seamlessly falls back to `iterate_server_container` via `_G.server_objects_registry`.
  - Updated `get_camp_inventory_summary` to also support offline stashes and containers, ensuring trade route inventories and PDA overview metrics function Zone-wide regardless of player location.
  - **Zone-Wide Storage Telemetry**: Upgraded `get_camp_storage_metrics` with `iterate_server_container` and system ini item weight evaluation so the PDA Overview tab displays accurate weight and storage capacity for all player settlements across the Zone, even when camps are on other maps.
- **MCM Configuration Parity for All Jobs**:
  - Added customizable real-time cycle interval sliders to MCM for Woodcutter, Brewer, and Scrapper jobs (`realtime_job_woodcutter_interval_min`, `realtime_job_brewer_interval_min`, `realtime_job_scrapper_interval_min`).
  - Wired `cfg` metatable lookups in `stalker_camp_builder.script` and added full English and Russian localization descriptions for all three sliders.
  - Guarded the MCM getter for `respawn_rival_camps` with `pcall` to ensure exception-safe reads.
- **Settlement Census & Morale Tracking Accuracy**:
  - Updated `get_camp_stats` to track all modern settlement roles (`hunters`, `medics`, `electricians`, `woodcutters`, `brewers`, `scrappers`). Previously, these roles fell through into the `idlers` bucket, distorting the settlement census.
- **Robust Offline Dominant Faction Resolution**:
  - In `get_camp_dominant_faction`, added fallback to `alife_object(npc_id):community()` when NPCs are outside the player's active level and cached `survivor.community` on the survivor state to eliminate redundant lookups.

### Critical Crash Fixes & Engine Stability:
- **Luabind Fatal Error & Save Crash Elimination**:
  - Eliminated the blind 1..65534 sim:object loop in get_server_container_items. On MT builds, calling sim:object on unallocated ID slots threw an uncatchable Luabind assertion exception, which caused callbacks_gameobject.script to trigger an emergency save (tempsave), crashing the engine during object serialization (CALifeStorageManager::save at 0x14077D027).
  - Switched all full-registry scans (get_server_container_items, scan_camp_structures, find_best_container, get_available_stashes) to iterate _G.server_objects_registry directly. Only real, registered ALife entities are traversed, eliminating scan stutters and avoiding invalid memory access.
  - Removed the 30-second homestead_teardown_grace_until lockout from save_state. Quicksaves no longer freeze settler job updates or falsely report zero food/water.
  - Removed duplicate state.homestead_backup table that doubled save file bloat in m_data.

### ALAO (Anomaly Lua Auto Optimizer) Pass:
- Applied full ALAO pass across all Homestead scripts using standard flags (--fix, --fix-yellow, --fix-nil, --fix-debug, --remove-dead-code, --cache-threshold 3, --workers 8).
- Applied 157 automated optimizations: cached globals, localized hot functions, dead-code removal, and safe nil guards.
- Verified 0 syntax errors across all 18 scripts with luac.exe -p.

### 🛡️ Anomaly Codex Database Quality Audit:
- **Comprehensive Static Quality Scan**: Audited all 39 mod files against the official Anomaly Codex manifests (169 rules covering Lua quality, hot-path performance, save/load safety, callback lifecycle, MCM contracts, and localization).
- **Zero Unpatched Vanilla Overrides**: Verified 100% modular file placement with 0 conflicting base files. All integrations use DLTX, DXML, and non-destructive wrappers.
- **Save/Load & Hot-Path Integrity**: Confirmed 0 hot-path full scans, 0 hot-path config reads, 0 missing save version migrations, and 0 non-serializable objects in persistent state.
- **Fixed Missing Localization Strings**: Added missing `st_hostiles` and `unknown` string entries to both English and Russian localization tables (`configs/text/eng` and `configs/text/rus`). Previously, raid notifications displayed the raw literal `"st_hostiles"` in the tip text.
- **XML Well-Formedness Verified**: All 6 string tables and 6 UI XML descriptors verified 100% well-formed with matching encodings (UTF-8 and Windows-1251 cp1251).
- **Global Variable Cleanup**: Cleaned up explicit global exports via `_G` for `is_gamma` and `stalker_camp_builder_mac_flag`.
- **Monkeypatch Hardening**: Added nil-safe guards around `ActorMenu` in `z_stalker_camp_builder_pda_monkeypatch.script`.

### ⚡ Hotfix #10 — Hot-Path Vector Allocation & GC Thrashing Elimination, Nil-Safety Hardening, and Engine Micro-Optimizations:
- **Hot-Path Vector Allocations & GC Thrashing Elimination**:
  - **The Problem**: In X-Ray Lua, `vector():set(...)` calls allocate temporary C++ userdata objects. In per-frame and per-tick callbacks (`actor_on_update`, `npc_on_update`, spatial raycast grids, and radial distance loops), hundreds of short-lived vector objects were allocated every second, triggering frequent Lua garbage collector sweeps and causing micro-stutters during heavy combat or in settlements with multiple NPCs.
  - **Fix Applied**:
    - **`actor_on_update()` Campfire Comfort Check**: Replaced per-frame `vector():set(...)` allocation with register-level Cartesian squared difference arithmetic `(dx*dx + dy*dy + dz*dz) <= 400.0`.
    - **`npc_on_update()` Wander Search**: Pre-allocated wander patrol candidate vector `test_p` before the 15-iteration attempt loop instead of instantiating 15 vectors per settler per tick.
    - **Furniture & Workstation Stand Position**: Replaced dynamic table instantiation of 8 vectors in `get_furniture_front_vertex_and_pos` and `find_workstation_stand_pos_and_lvid` with static normalized unit direction tables (`STATIC_UNIT_STAND_DIRS`) and a single reused scratch vector. Removed redundant duplicate definition of `get_furniture_front_vertex_and_pos` (lines 3845-3908).
    - **Spiral Scan & Flatness Checks**: Replaced dynamic direction tables with `STATIC_SPIRAL_SCAN_DIRS` in `find_valid_level_vertex_and_pos`. Pre-allocated sample vector in `is_position_flat_enough` before the 8-sample radial ring loop.
    - **Camp Raid Radial Spawn Grid**: Pre-allocated `test_p` vector before 16-angle * distance step nested loops in `spawn_camp_raid`, eliminating up to 80 transient vector allocations per raid spawn check.
    - **Rival Camp Logistics & SOS Distance Checks**: Replaced candidate vector instantiations in courier convoy distance check (`check_courier_convoys`), allied reinforcement check (`trigger_allied_reinforcement`), and player rescue check (`check_sos_rescue_reward`) with direct Cartesian squared distance arithmetic.
    - **Survivor Position Bounds**: In `set_survivor_position`, replaced vector allocation with direct Cartesian squared distance arithmetic against camp boundary.
- **Settler Relation Loop & Method Call Overhead Reduction**:
  - In `npc_on_update()`, cached `npc_id` across relation refresh logic, eliminating 5 redundant Lua-to-C++ method calls (`npc:id()`) per tick for every NPC.
  - Strengthened alive checks: verified `other_obj.alive` exists prior to calling `:alive()`.
- **String Concatenation in PDA Loop Elimination**:
  - In `ui_stalker_camp_builder_pda.script`, eliminated string accumulator concatenation in the settlement list population loop, constructing `badge_str` in single branch expressions.
- **Safe Fallback Vector in Resource Logistics**:
  - In `stalker_camp_builder_jobs.script`, pre-allocated module-level `STATIC_ZERO_VECTOR` to eliminate fallback vector instantiations during scavenged loot and hunted meat deposits.
- **Production Logging Sanitization**:
  - Commented out raw `printf` diagnostic statement in `homestead_luabind_fatal_diag`.
- **Validation Results**:
  - ALAO RED findings reduced from 53 down to 39 (14 hot-path issues eliminated).
  - ALAO vector allocations in loops reduced from 38 down to 24 (14 loop allocations eliminated).
  - 100% clean compilation: 18/18 Lua scripts checked with 0 syntax errors via Anomaly Codex `luac_tool.py`.

### 🚨 Hotfix #9 — Scavenger Return Crash Fix, Recruitment Settlement Proximity, Crafter Ammo Directives, and Settlement Raid Faction Alignment:
- **Scavenger Return & Save/Load Crash Fix**:
  - **The Problem**: Players reported that when a scavenger returned from an expedition, quicksaving or loading a save right before/after their return caused a hard crash back to desktop (*"when the scavenger gets back to the base the game crashes"*, *"the save right before the scavenger got back crashes my game as soon as i load into it"*).
  - **Root Cause Identified**:
    1. In `deposit_item_to_camp`, weapons, outfits, and degradable items were created with `sim:create(sec, ..., false)` passing `false` as the 6th argument to keep the entity unregistered for packet editing, followed by a call to `sim.register(se_item)`. In Anomaly / GAMMA, `sim.register` does NOT exist in Lua bindings! This left newly deposited weapons and armors permanently unregistered in the ALife simulator. Attempting to save or load immediately caused an unhandled X-Ray serialization crash.
    2. In `process_stash_expeditions`, returning scavengers were forcibly brought online via `utils_obj.switch_online(exp.npc_id)` and given `se_npc.can_switch_offline = false` even when the player was on a completely different level (e.g. player in Garbage while settlement is in Rostok), causing fatal engine exceptions.
    3. Scavenger departure set `se_npc.position = vector():set(0, -500, 0)` with unmapped level vertex coordinates, corrupting saved AI coordinates.
  - **Fix Applied**:
    - Rewrote `deposit_item_to_camp` to create fully registered server objects via `alife():create` and directly apply condition, ammo, and attachments via `utils_stpk.get_weapon_data`/`set_weapon_data` without invalid unregistration.
    - In `process_stash_expeditions`, cross-level returns are strictly guarded: `utils_obj.switch_online` and client BEH setups execute ONLY if the player is currently on the same level as the camp (`is_same_level`), and `can_switch_offline` remains permanently `true`.
    - In `dispatch_scavenger_expedition` and `dispatch_scavenger_regional_sweep`, removed the `(0, -500, 0)` coordinate hack, switching scavengers offline cleanly via `utils_obj.switch_offline`.
- **Recruitment Settlement Proximity & Current Map Priority**:
  - **The Problem**: Players recruiting NPCs in a settlement reported that the recruit was inexplicably sent to a different, faraway settlement rather than the local/closest one (*"when i recruit ppl they join but they are not in the camp or in survivor tab... hes taking them in different settlement mb but idk why not the closest one"*).
  - **Root Cause Identified**: `get_recruitable_camps` previously sorted settlements purely by numeric ALife ID (`table.sort(list, function(a,b) return a.hub_id < b.hub_id end)`). Whichever camp happened to have the lowest `hub_id` was always assigned to Slot 1 in the dialogue and picked by quick recruit, regardless of where the player was standing.
  - **Fix Applied**:
    - Overhauled `get_recruitable_camps` to prioritize proximity to `db.actor`: camps on the player's active level are prioritized first, sorted by distance from the player (closest first). Remote camps are sorted second.
    - Updated `recruit_npc` to pass `npc` into `get_recruitable_camps(npc)[1]`, guaranteeing that recruits join the nearest local camp with valid faction compatibility.
- **Crafter Ammo Directive & Caliber-Specific Surplus Caps**:
  - **The Problem**: Crafters produced the wrong ammo calibers or stopped crafting entirely despite having materials (*"crafters also seem to produce the wrong ammo when u chose specific ammo like the medics"*).
  - **Root Cause Identified**:
    - `is_camp_supply_capped(hub_id, camp, "ammo")` checked a global cap of 6 boxes of ANY `ammo_` in storage, ignoring `survivor.craft_order`. If the camp had 6 boxes of shotgun shells, crafters refused to produce NATO 5.56 rifle rounds (*"Stockpile Full"*).
    - Turret ammo priority (`prefer_turrets`) was overriding specific player directives when camp turrets had $< 40$ rounds.
    - Missing materials (gunpowder or scrap) failed silently without setting `shortfall_reason`, leaving the PDA displaying "Working" with no output.
  - **Fix Applied**:
    - **Directive-Specific Ammo Caps**: `is_camp_supply_capped` now evaluates caps against the specific caliber group chosen (`pistol`: 8, `shotgun`: 8, `rifle_soviet`: 6, `rifle_nato`: 6, `rifle_heavy`: 6, `sniper`: 6, `turret`: 10, `auto`: 15).
    - **Protected Directives**: `prefer_turrets` only triggers when directive is `"auto"` or `"turret"`, never overriding an explicit player directive.
    - **Live Diagnostics**: `process_ammo_crafting` and `_calc_job_paused_status` now record exact shortfalls (`Need Gunpowder`, `Need Scrap Metal`, `Need Powder & Scrap`, `Stockpile Full`), displayed in gold text on the PDA.
    - **PDA Detail Panel**: Added a dedicated `job == "craft"` branch displaying active caliber directive (`[NATO 5.56x45]`, `[Handgun Ammo]`, etc.) and waiting status.
- **Settlement Raid Invader Faction Alignment**:
  - **The Problem**: Players with Duty settlements at Rostok reported that "Settlement Under Attack" events spawned peaceful Loners who ran up to the player, refused to attack, and offered quests (*"theres just a loner that is running to me and isnt attacking anyone... accepted a quest from one too"*).
  - **Root Cause Identified**:
    - `get_enemy_faction_for(faction, level_name)` in `stalker_camp_builder_rivals.script` fell back to any non-same faction on the map if no hardcoded enemy was present in `get_level_factions(level)`. On Rostok (`l05_bar`), the allowed factions are only `dolg` and `stalker`, so Duty was assigned `stalker` (Loners) as the "enemy" faction!
    - Newly spawned raid squads were not yet online on the frame they were created, so `npc_cl:set_relation(enemy)` silently failed.
  - **Fix Applied**:
    - In `get_enemy_faction_for`, added Zone-wide enemy evaluation (`relation <= -500`) for maps lacking local hostile spawns. Loners (`stalker`) and Ecologists (`ecolog`) are strictly excluded from attacking Duty/allied settlements, ensuring raids spawn true hostile invaders (Bandits, Mercenaries, Monolith, Renegades, or Mutants).
    - Added asynchronous hostility timers (`CreateTimeEvent` at 0.5s and 2.0s) so that as raiders switch online, they and camp defenders are guaranteed to be mutually hostile (`game_object.enemy`).

### 🚨 Hotfix #8 — Medic Ibuprofen Synthesis & Medical Directive Overhaul:
- **Medic Directive & Ibuprofen Synthesis Fix**:
  - **The Problem**: Players reported that when assigning a Medic to craft Ibuprofen via the PDA directive button, the medic never crafted Ibuprofen and instead produced random medical items (Bandages, AI-2 Medkits, or Antirad).
  - **Root Cause Identified**:
    - `process_medic_job` in `stalker_camp_builder_jobs.script` was running legacy placeholder logic that completely ignored `survivor.medic_order`. When consuming vodka or antiseptic, output was hardcoded to randomly select from `{"antirad", "medkit_army", "medkit"}`—`akvatab` (Ibuprofen) was completely omitted from the script.
    - `is_camp_supply_capped` evaluated a global medical cap (`cap = 8`) that did not recognize `akvatab` and capped production if the settlement held 8 generic bandages, halting synthesis even when the camp had zero Ibuprofen.
    - `_calc_job_paused_status` did not validate directive ethanol requirements, and `update_camp_jobs` hardcoded `did_work = true` regardless of whether medicine was actually synthesized.
    - Container auto-sort (`get_auto_sort_target_box`) omitted `akvatab` from Category 3 (Medical & Pharma Supplies), routing produced Ibuprofen into generic fallback chests rather than Medstations.
  - **Fix Applied**:
    - **Directive-Driven Synthesis Engine**: Overhauled `process_medic_job` to strictly honor `survivor.medic_order`:
      - **Ibuprofen (`akvatab`)**: Synthesizes `akvatab` (5 charges) using 5 units of ethanol/vodka. If less than 5 units of vodka are present, sets shortfall reason `Need 5x Vodka`, returns `false`, and backs off until ingredients arrive.
      - **Potassium Iodide (`kalium`)**: Synthesizes `antirad_kalium` (3 charges) using 3 units of ethanol/vodka.
      - **AI-2 Medkits (`medkit`)**: Synthesizes `medkit_ai2` (2 charges) using 2 units of ethanol/vodka.
      - **Bandages (`bandage`)**: Synthesizes `bandage` using 1 cloth/textile scrap or 1 unit of ethanol.
      - **Auto-Balanced (`auto`)**: Dynamically evaluates settlement medical stockpiles and synthesizes the lowest-stock medicine the settlement has ingredients to produce, falling back to field-dressing injured settlers if materials are depleted.
    - **Directive-Specific Surplus Caps**: `is_camp_supply_capped` now evaluates caps against the specific medicine ordered (`cap = 8` for Ibuprofen, Potassium Iodide, and Medkits; `15` for Bandages). Having abundant bandages no longer blocks Ibuprofen synthesis.
    - **Live Supply Diagnostics in PDA**: `_calc_job_paused_status` and PDA status formatters now display exact material requirements (`[WAITING: Need 5x Vodka]`, `[WAITING: Need 3x Vodka]`, `[WAITING: Need 2x Vodka]`, `[WAITING: No Materials]`) on both survivor list rows and the detail panel.
    - **Auto-Sort Clinic Routing**: Added `akvatab` and `ibuprofen` to Category 3 in `get_auto_sort_target_box`, routing produced Ibuprofen directly into settlement Medstations and medical stashes.

### 🚨 Hotfix #7 — Companion ↔ Settler Bi-directional Transition & Squad Architecture Fix, Cook Leveling:
- **Companion ↔ Settler Bi-directional Transition Overhaul**:
  - **The Problem**: Players reported that converting a companion into a settler and subsequently recruiting them back (`recruit_back`) broke the NPC completely: the NPC stood completely frozen in place, was missing from the companion squad list and PDA, refused to travel across level transitions, and when spoken to directly replied with refusal sounds or became trapped in unperformable actions ("Talk to my squad leader"). Players were unable to order them or reassign them back to settlement duties.
  - **Root Cause Identified**:
    - The vanilla and G.A.M.M.A. companion system (`axr_companions`) tracks companions through *squads* registered in `axr_companions.companion_squads[squad.id] = squad`. Calling `axr_companions.add_to_actor_squad` without a registered companion squad leaves the NPC squad-less.
    - When `beh_companion.ltx` evaluated a squad-less NPC, `!is_squad_commander` evaluated to true, redirecting their AI target to a non-existent leader (`target = commander`), which caused the NPC to freeze in place and rerouted interactions to refusal phrases (`snd_on_use = meet_use_no_talk_leader`).
    - Workstation lock flags (`move.stand`, `st.beh_homestead_active`, `homestead_settler_guard`, and `npcx_beh_wait`) were also left armed on the NPC, keeping them frozen in their previous work posture.
  - **Fix Applied**:
    - **Dedicated Squad Conversion (`convert_settler_to_companion_squad`)**: Converts the settler's single-member home squad directly into an active companion squad (or instantiates a new `online_offline_group`), sets `scripted_target = "actor"`, clears any smart-anchoring `get_script_target` nil-override, and registers the squad in `axr_companions.companion_squads[squad.id]`.
    - **Clean AI Unfreeze & Behavior Restoration**: When recruited back, the NPC's settler scheme is released via `restore_settler_logic`, workstation stand locks and rally points are cleared, `npcx_beh_wait` is disabled, and `axr_companions.set_companion_to_follow_state(online_npc)` is called to immediately resume active following.
    - **Dedicated "Return to Settlement" Dialogue**: Added a dedicated dialogue option (`return_to_settlement_dialog`) for active companions, allowing players to order companions directly back to settlement work without confusing or hijacked dialogue states. Fully localized in English and Russian (`ui_st_stalker_camp_builder.xml`).
    - **Precondition & Menu Segregation**: Updated `is_camp_survivor` to exclude active companions (`is_companion` / `job == "companion"`), preventing the stationary `manage_camp_dialog` from hijacking companion dialogue. Updated `can_recruit` to seamlessly support reassigning a companion to a different settlement.
    - **Safe PDA Job Reassignment**: Reassigning a settler away from the "Companion" role via the PDA now cleanly detaches them from `axr_companions`, re-anchors their squad to the settlement, and restores settler behavior logic without leaving orphaned companion references.
    - **Auto-Heal Sweep for Existing Saves**: Added `heal_stuck_companion_settlers()` on game load (`actor_on_first_update`) to detect and rescue any settlers currently stuck in companion limbo from prior versions, safely restoring their squad registration and AI state.
- **Cook Leveling & Output Quality Scaling**:
  - **Quality Scales with Cook Rank**: `process_cook_job` now dynamically scales cooking output quality with the cook's survivor tier (`math.max(sb.cfg.cook_output_tier or 1, surv_tier)`). As cooks gain experience (Skilled → Expert → Master), they naturally unlock the ability to prepare higher tier rations (Tier 2 seasoned meals and Tier 3 gourmet survival rations) when stoves, fuel, water, and seasonings are available.
  - **Supply & Surplus Diagnostics**: Cooks pause production and show clear shortfall status (`[WAITING: No Raw Meat]` or `[WAITING: Surplus Capped]`) when raw meats are depleted or camp food stores are full, preventing ingredient waste and making it transparent why XP is not currently being earned.

### 🚨 Hotfix #6 — Turret Ammo Crafting & Auto-Restock Overhaul, Caravan Faction Alignment:
- **Turret Ammo Supply Cap Bypass**: Fixed an issue where Crafters abruptly stopped producing ammo while defensive turrets remained completely empty because camp storage held 6+ boxes of unrelated ammunition (e.g. shotgun shells or rifle ammo). When `enable_surplus_cap` is active, `is_camp_supply_capped` now checks if camp turrets have an ammo deficit and only caps if camp storage already contains enough 9x19/9x18 rounds to load them.
- **Dedicated Turret Ammo Recipe & Caliber Correction**: When crafting for turrets (or when turrets need ammo in Auto mode), the crafter now crafts exclusively compatible 9x19 calibers (`ammo_9x19_fmj`, `ammo_9x19_pbp`, and `ammo_9x19_ap`). Eliminated the flaw where tier 2/3 propellants produced 5.45x39 or 5.56x45 rifle rounds that turrets could never load. Also expanded propellant and casing recognition to cover all GAMMA propellants and casings.
- **Broadened Turret Maintenance Caliber Support**: `process_turret_maintenance` now accepts all 9x19 and 9x18 variants (AP, PBP, PMM, FMJ) rather than strictly hardcoded FMJ.
- **Passive & Guard Turret Top-Off**: Guards now maintain camp turrets during their update cycle, and camps automatically top off defensive turrets from settlement storage every 10 seconds even if no Crafter is present.
- **Faction-Aligned Caravan Traders ("Riddled with Boolets" Fix)**: Resolved an issue where summoned trade caravans and random settlement caravan events spawned generic Loner (`stalker_regular`) traders in Mercenary, Bandit, Military, Freedom, or Duty settlements, causing camp guards and turrets to immediately gun them down. Added `get_camp_trader_section(camp)` to spawn matching faction traders (`sim_default_killer_trader`, `sim_default_bandit_trader`, `sim_default_dolg_trader`, etc.) with instant friendly actor and settlement relations.

### 🚨 Hotfix #5 — check_sec Nil Crash Fix & Contract as Law Hardening:
- **Problem**: In camp chest supply evaluation (`check_camp_chest_supplies`), a call to undefined global `check_sec` triggered a fatal `lua_pcall_failed` crash on line 4563.
- **Root Cause & Fix Applied**:
  - Defined local `check_sec(sec)` in `check_camp_chest_supplies` with robust recognition of all consumable food and drink sections (canned meat, bread, sausages, stews, MRE rations, vodka, beer, canteens, mineral water, energy drinks).
  - **Contract as Law Enforcement**: Migrated remaining manual container iteration loops in `process_turret_maintenance` (`stalker_camp_builder_jobs.script`) and `transfer_supplies` (`stalker_camp_builder.script`) to use `sb.camp_iterate_inventory`. Zero raw inventory iteration loops remain across all settlement jobs and logistics.
  - **Camp Storage Performance**: Added 5-second TTL memoization to `get_camp_storage_metrics` with event-driven invalidation on auto-sort and deposits, eliminating repetitive ALife registry scans.
  - **Dynamic MCM Cache Invalidation**: Hooked `on_option_change` to immediately invalidate cached job interval timers when MCM sliders are moved.
  - **Settlement Directives Polish**: Added full Russian and English translations for Medic, Woodcutter, and Crafter directives. Active directive tags (`[AI-2]`, `[Charcoal]`, `[12ga]`, etc.) now render directly on survivor list rows with live countdowns and shortfall reasons.

### 🚨 Hotfix #4 — Save/Teardown-Window Container Iteration + Fatal-Error Diagnostics:
- **Problem**: A fatal `func_or_userdata → C++ exception` crash surfaced inside the camp-jobs tick (`update_camp_jobs`), with no Lua traceback in the log. The user's log also showed a third-party script profiler (`devtools_profiler.script`) throwing repeated nested C++ exceptions during the save sequence — on MT builds such exceptions are **not catchable by pcall** and surface at whatever Lua frame was executing (Homestead's tick was the victim frame, not the thrower).
- **Fix Applied**:
  - **Teardown-grace gating extended to the whole jobs tick**: the mod already arms a 30-second grace window around every save and level transition (added in v1.1.x for the documented `xrServer::Perform_destroy "child registered but not found"` crash), but only `check_camp_chest_supplies` respected it. Now `update_camp_jobs`, the rival-chest stash fill, settler eating, and trade-route transfers **skip the window entirely** — no client inventory boxes are iterated while the engine is concurrently destroying objects. Job cycles are real-time accrued and catch up automatically when the window closes.
  - **`on_luabind_fatal_error` diagnostics registered**: the modded-exes framework fires this callback with the offender string before its fatal-error UI. Homestead now dumps the offender, a full `debug.traceback`, and a camp/survivor state summary to the log — the next luabind fatal will name its true throwing mod and call site instead of leaving an untraceable C++ exception.

### 🚨 Hotfix #3 — Cross-Mod Dispatch Poisoning (func_or_userdata C++ exception, dead interaction key):
- **Problem**: On a heavily-modded MT install, Homestead's 10-second tick crashed with `stalker_camp_builder.script(2146): func_or_userdata → C++ exception`, and the shared `actor_on_update` callback dispatch died with it — breaking the interaction (F) key and every callback registered after Homestead's (wearable-device mods, canted irons per-frame code, etc.) until a level change.
- **Root Cause**: The per-tick calls (`update_camp_jobs`, `update_rival_camps`, raids, events, morale, trade routes, map-spot sync, settler eating) were invoked as **bare globals**, and most of the tick's subsystems were not pcall-isolated. In the affected install, the callback chain reached the modded-exes game-object dispatcher (`callbacks_gameobject`) and other mods' per-frame code — where a C++ exception (`scripted_canted_irons` processing a weapon with `owner=nil`) is **not catchable by pcall** and aborted the entire shared dispatch.
- **Fix Applied**:
  - All eight per-tick subsystem calls now use **namespace-direct invocation** (`stalker_camp_builder.update_camp_jobs` etc.) with existence guards — the real Homestead functions are called regardless of any global-table mutation by other mods or the unlocalizer system.
  - The entire tick core (subsystems, surge reaction, hospitality buff, settler eating, map-spot sync) is **pcall-isolated call-by-call**, so a Lua error in one subsystem can never abort the shared dispatch chain that other mods depend on.
  - Note for affected installs: the C++ exception itself originates in `scripted_canted_irons.script` (its own trace shows `owner=nil owner_id=nil` — it processes a weapon whose owner vanished mid-frame). With this hotfix Homestead no longer forms part of that chain, but the underlying canted-irons edge case is that mod's own code.

### 🚨 Hotfix #2 — Frozen PDA Job Timers (stuck until a map/level change):
- **Problem**: Job timers on the PDA froze at their current value (e.g. stuck at 8:37) right after jobs completed, and only a map/level change brought them back to life.
- **Root Cause**: The PDA's periodic refreshers (`SettlementManagerPDA:Update` and the 1-second `homestead_pda_actor_on_update` callback) were **gated to the Survivors tab only** — the Overview tab (the default landing tab) was a static snapshot drawn once when the settlement was selected. Additionally, `UpdateSurvivorsProgress` silently returned without refreshing whenever the settlement-list selection was lost, leaving the visible rows frozen at their last rendered values.
- **Fix Applied**:
  - The 500 ms row refresher now runs on **both the Survivors and Overview tabs**, and the 1-second background callback was extended the same way.
  - New `RenderOverviewStats` method (split out of `OnSettlementSelected`) re-renders the Overview stat panels (threat banner, population/defense gauges, supplies, morale) every 5 seconds via a lightweight `RefreshOverviewLive` pass — without rebuilding the survivor list, so selections are preserved.
  - `UpdateSurvivorsProgress` no longer silently freezes: when the settlement selection is lost, it resolves the camp that actually owns the visible survivor rows and keeps updating them.
  - The right-hand detail panel timer (`RefreshJobProgress`) follows the resolved camp instead of dying with the selection.

### 🚨 Hotfix — News Tip Crash (news_manager.script:82, "attempt to index local 'sender' (a number value)"):
- **Problem**: On level entry (or any first camp tip), the game crashed with a fatal `lua_pcall_failed` inside `news_manager.send_tip`.
- **Root Cause**: The v1.1.7 `camp_send_tip` signature repair corrected the helper's parameter order but kept its 4-argument call into `news_manager.send_tip(actor, text, snd_type, duration)` — placing the numeric duration (e.g. `10000`) into the `news_type` slot (4th argument). Vanilla/GAMMA's `news_manager` indexes that argument, producing `attempt to index local 'sender' (a number value)`. (In v1.1.6 the same slot accidentally received the category *string* due to the old parameter-order bug, which is why this never crashed before.)
- **Fix Applied**:
  - `camp_send_tip` now calls `send_tip` with the standard GAMMA shape: `send_tip(actor, text, snd_type, category, duration)` — string in the news_type slot, number in the timeout slot, identical to every other direct call in the mod.
  - `camp_send_tip` and `camp_send_alert` wrap the `send_tip` call in `pcall` — a news-tip failure can now never hard-crash the game.
  - Localized the last hardcoded alarm string ("Alarm triggered." → `st_alarm_pda_triggered`, eng + rus).

### 🔴 Critical Crash Fix (Turret Maintenance):
- **Problem**: Placing any Homestead turret and assigning a Crafter caused a hard Lua error that aborted the entire job tick for ALL camps: `attempt to call global 'is_valid_box' (a nil value)`.
- **Root Cause**: `process_turret_maintenance` in `stalker_camp_builder_jobs.script` called a local helper `is_valid_box(bid)` that was never defined (its four sibling job functions each define their own copy). The call site in `update_camp_jobs` was also not pcall-isolated, so one failure froze every camp's jobs.
- **Fix Applied**:
  - Added the missing `local function is_valid_box` (same `is_valid_camp_box` / `is_actual_container` fallback pattern used by the sibling jobs).
  - Wrapped the `process_turret_maintenance` dispatch in `update_camp_jobs` in a `pcall` as belt-and-braces: a turret-maintenance error can never again abort the whole job tick.
- **Related crash hardening in this release**:
  - `hf_on_furniture_place`: guarded the hub `position` dereference when warning about boundary distance (the hub could be released mid-frame between the camp lookup and the distance check → "attempt to index nil").
  - Invincible-settler respawn path now populates the FULL `settler_lookup` entry (`camp` + `survivor` fields, not just `hub_id`), so respawned settlers no longer run with a nil survivor state until the next rebuild.
  - Hunter meat yield: `math.random(min, max)` now swaps inverted MCM bounds instead of throwing "empty interval" when a user sets Hunter Min Meat above Hunter Max Meat.
  - Turret reload UI: `Reload()` no longer plays the reload sound through a nil `self.object` (a CUIScriptWnd has no game object); the sound now plays at the turret's world position with a nil guard.

### 📻 Silently-Broken Feature Restoration:
- **`camp_send_tip` parameter-order mismatch (36 call sites)**: The helper was declared `(actor, text, snd_type, duration, hub_id, category)` while every caller passed `(actor, text, snd_type, category, duration)`. Consequences: tip durations were lost, and radio log entries were filed under junk hub keys (duration numbers used as table keys). The definition now matches the call convention; radio logs and tip durations work as designed.
- **Settlement Radio Feed was permanently empty**: `add_camp_radio_log` only wrote per-camp logs, but the PDA Radio tab renders exclusively `radio_logs["all"]`, which only seeding code ever populated. Every radio entry now also lands in the global transceiver feed (capped at 50 entries, same as before).
- **Job radio chatter restored**: Scavenger returns, hunter ambushes, and hunter returns call the previously nonexistent `add_radio_feed_entry` — it now exists and feeds the PDA Radio tab live.
- **PDA storage metrics were always zero**: `get_camp_storage_metrics` passed `(camp, hub_obj, "placeable_blue_box")` into `scan_camp_structures(hub_id, force)` — signature mismatch, always returned `{}`. It now iterates the camp's real containers via `get_camp_containers` with the safe inventory iterator.
- **Settlement telemetry hardcoded**: the telemetry seeder called `calculate_camp_defense` / `calculate_camp_morale`, which never existed anywhere — it always reported Defense 20 / Morale 75%. It now uses the real `get_camp_stats` (defense rating) and `get_camp_morale` values.
- **Turret channel bus refresh**: feeding a turret now immediately refreshes `_G.hf_turret_channels` so nixie display counters mirror the new ammo count instead of waiting for the wrapper's next publish tick.
- **Duplicate work eliminated**:
  - `map_spot_menu_add_property` / `map_spot_menu_property_clicked` were registered TWICE in the same `on_game_start`, so PDA map-spot context-menu handlers could fire twice. Now registered once (pcall'd).
  - `process_stash_expeditions` ran twice per 10-second cycle (1 s pcall'd tick + an unconditional call at the end of `actor_on_update`), advancing every expedition twice. The duplicate call is removed.
  - `structure_type_exact` registry had silently-overridden duplicate keys: `placeable_artifact_harvester` ("gadget" then "harvester") and `placeable_weapon_rack` ("stash" then "weapon_rack"). The stale earlier entries are removed; the specific later types are canonical and consumed by the container/event systems.
- **Dead MCM toggle revived**: `show_unknown_furniture_warning` existed in MCM but its log line was commented out — it now actually logs unknown furniture sections.

### 📦 Packaging & Compatibility Correctness:
- **G.A.M.M.A. flag shipped to everyone**: `stalker_camp_builder_gamma_flag.script` (`is_gamma = true`) lived in the always-installed 00_Core, so GAMMA-only rival-chest stash logic ran on Standard Anomaly installs too. The flag now ships ONLY with the optional 02_GAMMA component (GAMMA is still auto-detected via `grok_stashes_on_corpses` as a fallback).
- **"No PDA Tab" installer option was broken**: Core shipped the PDA scripts + tab injection while the PDA UI XML/textures ship only with the PDA component — choosing "No PDA Tab" left a Settlement tab that errored on open. The option now installs a marker flag (`05_NoPDATab`); the tab-bar injector, the `set_active_subdialog` hook, and the Mod App Creator registration all respect it and leave the PDA untouched. NPC recruit/manage dialogs remain unaffected.
- **GAMMA sound-pack dependencies removed from Standard installs**:
  - The pistol turret's shoot/reload sounds used GAMMA-only paths (`weapons\silencers\no_clinks\silencer_9x19`, `weapons\mp7\mp7_reload`). Sound paths are now selected per environment: GAMMA keeps the original paths; Standard Anomaly falls back to base-game sounds (`weapons\pm\...`).
  - Homestead's alarm binders overrode the base Hideout Gadgets binder but played `alarm_system_sounds\*`, which only the GAMMA pack ships — alarms were silent on Standard installs. Paths now resolve to base Gadgets' `gadgets_gamma_sounds\*` on Standard and `alarm_system_sounds\*` under GAMMA.
- **Script duplication removed**: 9 byte-identical script copies existed across 00_Core / 01_PDATab / 03_ModAppCreator / 04_HideoutGadgetsGammaPatch and (being higher FOMOD priority) would have silently overridden any Core-side fix. Duplicates deleted — Core is the single source of truth; asset-only components (PDA XML/textures, GAMMA meshes/sounds) are unchanged.
- **`alarm_has_targets` divergence hazard**: `bind_alarm_system_pda` carried a full duplicate of the detection body. It now delegates to the canonical `bind_alarm_system` implementation at call time (with a local fallback if that module isn't loaded yet).

### 🌐 Localization & Documentation:
- **30+ hardcoded English strings localized (eng + rus, windows-1251)**: settlement hub establishment/removal messages, furniture join/boundary warnings, banish/dismiss/recall notifications, turret reload/recovered-rounds and alarm online/offline messages, medic/electrician/woodcutter/brewer/scrapper job toasts, turret-refill notice, survivor-cap recruitment message, camp specialization toast, PDA fast-travel/caravan/dismantle failure messages, rest-bonus tip, and auto-sort radio entry. (Note: PDA job-directive label tables remain English — scheduled for the next localization pass.)
- **README corrections**: MCM settings count (31 → 68), job interval defaults aligned with actual MCM/code values.
- **MCM read caching**: `cfg` metatable lookups now go through a 5-second TTL cache — hot paths (per-settler 150–250 ms ticks, job dispatch) no longer hit `ui_mcm.get` dozens of times per second. The `respawn_rival_camps` debug trigger is excluded from caching to stay instantly responsive.

## v1.1.6 — Rival Camp Grounding & Underground Spawn Fix, Cook Supply Capping, Auto-Sort Container Routing, UI Cleanup & Performance Optimization

### 🏔️ Comprehensive Rival Camp Grounding & Underground Spawn Elimination:
- **Problem**: Even after resetting rival camps via MCM debug, rival camp outposts, chests, and decorations continued spawning underground or deep inside geometry (notably Dead City Outpost at y = -6.95m inside cit_kanaliz2 sewer network).
- **Root Causes Discovered Through Deep Research**:
  1. *Subterranean Smart Terrains in Candidate Pool*: Smart terrain selection previously filtered out underground level names (e.g. jupiter_underground, labx8), but did NOT filter out underground or sewer smart terrains located inside surface levels. Smarts like cit_kanaliz1 and cit_kanaliz2 (Dead City sewer tunnels at y ~ -7.0m), bar_dolg_bunker, katacomb_smart_terrain, and pas_b400_tunnel were selected as camp centers, placing chests and props 7+ meters below street level.
  2. *Remote Map Elevation Disconnect*: When camps spawn on other levels (offline maps), visual terrain meshes and collision geometry are not loaded into memory. Prop spawn formulas assigned pos.y = smart.position.y with a 30m–120m horizontal offset. Across rolling terrain, slopes, or depressions, this blind elevation assignment caused props to spawn deep inside hillsides or rock faces.
  3. *Hollowed-Out Ground Snapping*: snap_rival_camps_to_ground() had been stripped down to a safety placeholder that merely flipped boolean flags (camp.snapped = true, ground_snapped_v3 = true) without actually repositioning the chest or decorations to visual ground level when the player arrived on that map.
  4. *Zero Prop Clearance*: Downward visual raycasting positioned props at surface_y + 0.00, causing static 3D boxes and sleeping mats to clip or sink below terrain textures and grass meshes.
- **Fix Applied**:
  - **Subterranean Smart Blacklist & Filtering**: Created a dedicated underground_smart_terrains registry and is_underground_smart(name) filter to block all underground, sewer, bunker, and basement smarts across all levels. Also blacklisted l11_hospital.
  - **Auto-Purge for Existing Underground Camps**: In update_rival_camps and snap_rival_camps_to_ground, any camp occupying a blacklisted underground smart or level is automatically purged cleanly (map spots removed, chest, decorations, and squads released from ALife registry).
  - **Multi-Tier Ground Anchor Probing (find_ground_anchor)**: Replaced single-pass vertical probes with a 3-tier raycast search (close 4m up/8m down, wide 15m up/25m down, and high-vantage up to 45m down) backed by AI level graph validation (level.vertex_id). If no valid surface geometry exists, candidate locations are safely rejected.
  - **Safe Offline Entity Snapping in snap_rival_camps_to_ground**: When the player enters a map with unsnapped rival camps, chests are snapped with +0.08m ground clearance and decorations with +0.04m to +0.08m elevation. For squads, ONLY server-side entity positions (se_npc.position = pos) are updated while offline. Runtime calls to set_npc_position on online mutants/stalkers are completely avoided, eliminating engine handler_base purecall crashes (xrDebugNew.cpp:1048).
  - **Candidate Search Upgraded in spawn_single_rival_camp**: On the active level, uses full visual raycasting with ground clearance. On remote levels, constrains spawn radius to 20m–35m around smart centers and marks ground_snapped_v3 = false so exact visual ground snapping triggers seamlessly the moment the player visits the map.
  - **Hardened Camp Reset (force_respawn_all_rival_camps)**: Completely releases all existing rival squads, chests, and decorations from ALife. Spawns 1 guaranteed surface outpost on the current level with instant visual raycasting, and 2-3 outposts on remote levels flagged for arrival ground snapping.

### 🛡️ Critical Engine Crash Resolution (Pure Virtual Function Call in xrDebugNew.cpp:1048):
- **Problem**: When loading saved games located in maps with rival camps (e.g., loading autosaves entering `l08_yantar`), the engine crashed to desktop with:
  ```
  Expression    : <no expression>
  Function      : handler_base
  File          : ...\xrCore\xrDebugNew.cpp
  Line          : 1048
  Description   : pure virtual function call
  ```
- **Root Cause Isolated**:
  - In `stalker_camp_builder_rivals.script`, `snap_rival_camps_to_ground` executed on level entry for all rival camps missing the v3 ground snap flag.
  - For camps occupied by mutant or monster squads (such as Yantar Outpost #50 / `rival_camp_49485` and `rival_camp_28196` containing Chimeras and zombie packs), the function attempted to reposition squad members and invoked `online_npc:set_npc_position(new_npc_pos)`. In the X-Ray Monolith / OpenXRay engine, `CScriptGameObject::SetNpcPosition` is strictly implemented for `CAI_Stalker`. On `CBaseMonster` (mutants/monsters), movement vtable dispatch invokes a pure virtual function (`_purecall`), instantly terminating the game through the CRT purecall handler (`handler_base` in `xrDebugNew.cpp:1048`). Lua `pcall` cannot catch C++ CRT purecall terminations.
  - `safe_teleport_squad` and `safe_teleport_object` were called redundantly on active mutant squads mid-transition, calling `alife():teleport_object` twice in a single frame with out-of-bounds coordinates derived from `find_ground_anchor` that spammed dozens of `Invalid position for CLevelGraph::vertex_id specified` engine warnings.
  - Across `stalker_camp_builder.script` and `stalker_camp_builder_recruit.script`, multiple repositioning calls checked `(IsStalker(online_npc) or IsMonster(online_npc))`, erroneously allowing mutant entities to be passed into `set_npc_position`.
  - `snap_rival_camps_to_ground` was also being redundantly invoked every frame in `actor_on_update()`.
- **Fix Applied**:
  - Completely eliminated runtime squad and mutant manipulation from `snap_rival_camps_to_ground()`. Autonomous simulation squads and mutants now manage their own AI pathfinding naturally without artificial teleportation or script-forced repositioning.
  - Defused `snap_rival_camps_to_ground()` to cleanly flag existing camps as snapped (`snapped = true`, `ground_snapped_v2 = true`, `ground_snapped_v3 = true`) without hazardous runtime object teleportation, out-of-bounds cross-table queries, or `switch_offline`/`switch_online` churn.
  - Guarded all calls to `set_npc_position` across all scripts (`stalker_camp_builder.script`, `stalker_camp_builder_rivals.script`, `stalker_camp_builder_recruit.script`) with `IsStalker(...) and (not IsMonster(...))`, guaranteeing `SetNpcPosition` is never called on mutant or monster entities.
  - Removed the redundant per-frame `snap_rival_camps_to_ground` call from `actor_on_update()`.
  - Wrapped rival camp stash population in protective `pcall` isolation during level initialization and update loops.

### 🔧 Script Scope Fix (Unresolved `sformat` & `same_level` Globals):
- **Problem**: When rival camps transformed into mutant dens or triggered dynamic broadcasts, the game threw a Lua crash: `attempt to call global 'sformat' (a nil value)` in `transform_to_mutant_nest`.
- **Root Cause**: `local sformat = string.format` was scoped inside `update_rival_camps()`, leaving subsequent event and notification handlers (`transform_to_mutant_nest`, `trigger_psy_storm_zombification`, `dispatch_retaliation_raid`, `spawn_single_rival_camp`, `upgrade_rival_camp`) without access. Additionally, `same_level` was checked prior to its loop declaration.
- **Fix Applied**: Defined `_G.sformat = string.format` and top-level `local sformat = string.format` across all Homestead scripts (`stalker_camp_builder.script`, `stalker_camp_builder_rivals.script`, `stalker_camp_builder_jobs.script`, `stalker_camp_builder_recruit.script`, `stalker_camp_builder_npc.script`, `ui_stalker_camp_builder_pda.script`). Properly scoped `same_level` inside `update_rival_camps()`.

### 🏹 Hunter Expedition String Format Fix:
- **Problem**: When a camp hunter returned from an expedition and deposited meat, the game crashed with:
  `LUA error: ...stalker_camp_builder_jobs.script:2597: bad argument #3 to 'format' (number expected, got string)`
- **Root Cause**: In `ui_st_stalker_camp_builder.xml`, string tables for `st_job_hunter_returned` and `st_job_hunter_radio_feed` defined `%d` (integer) for the harvest description argument, but `format_deposited_items_summary` passes a formatted summary string (`meat_desc`).
- **Fix Applied**: Updated English and Russian string tables to use `%s` for the item summary. Hardened `stalker_camp_builder_jobs.script` with protective `pcall` fallback handling to guarantee zero crashes even if legacy or third-party translated XMLs still specify `%d`.

### 🌐 Complete Script Localization & Text Externalization (TheHunter1986's Report):
- **Problem**: In-game radio transmissions, reconnaissance reports, settlement events, and worker job toast notifications were hardcoded in English string literals instead of referencing localization files.
- **Root Cause**: Scripts called `news_manager.send_tip` and `sb.camp_send_tip` with hardcoded English strings directly.
- **Fix Applied**:
  - Registered 71 localization strings in both English (`utf-8`) and Russian (`windows-1251`) string tables in `ui_st_stalker_camp_builder.xml`.
  - Replaced all hardcoded string literals across `stalker_camp_builder.script`, `stalker_camp_builder_jobs.script`, `stalker_camp_builder_rivals.script`, and `stalker_camp_builder_recruit.script` with `game.translate_string(...)`.
  - Localized cooking methods (`st_cooking_at_campfire`, `st_cooking_on_stove`), reconnaissance broadcasts, caravan/refugee events, and worker toasts.

### 🎒 Scavenger Expedition Stash Loot Condition Fix (Guest's Report):
- **Problem**: Companions returning from scavenging stashes brought back pristine 100% condition weapons (e.g. AK-105) and suits (e.g. SKAT-9), breaking early-game G.A.M.M.A. balance.
- **Root Cause**:
  - `deposit_item_to_camp` spawned items into settlement storage boxes via `alife_create` without the `false` (unregistered) parameter. The engine immediately registered entities with default 100% condition before packet modifications (`utils_stpk.set_weapon_data` / `utils_stpk.set_item_data`) could take effect.
  - Client game objects are not yet instantiated on the spawn frame (`level.object_by_id(se_item.id)` returns `nil`), so direct client condition setters never executed.
  - Stash child item extraction used `utils_stpk.get_item_data` instead of `utils_stpk.get_weapon_data` for weapons, and forwarded uninitialized 1.0 conditions as `custom_cond`.
- **Fix Applied**:
  - Weapons, armor, and degradable items are now spawned unregistered via `alife_create(..., false)` (or `alife():create(..., false)`).
  - Authentic G.A.M.M.A. condition brackets are applied via `utils_stpk`:
    - Weapons: 10%–35% (Rare/Yellow stashes: 20%–45%)
    - Outfits & Helmets: 8%–30% (Rare/Yellow stashes: 15%–40%)
    - Other Degradables: 25%–55%
  - Registered manually via `alife():register(se_item)` with the degraded packet condition intact.
  - Item degradation is baked directly into the net-spawn packet prior to server registration, guaranteeing authentic conditions without unsafe client-side polling.
  - Handled WPO wear and ensured uninitialized `>= 0.99` conditions on stash child items are properly degraded.

### 🍽️ Cook "Full Storage" Stockpile Cap Fix:
- **Root Cause**: `is_camp_supply_capped(hub_id, camp, "food")` previously used an overly broad filter that counted all food and rations—including bread, canned goods (`conserva`, `tushonka`, `kolbasa`), and emergency rations—across all settlement containers towards the 15-meal surplus limit. Scavengers and player hoards would quickly fill this cap, causing camp cooks to pause after preparing only 1-2 meals with the notification *"Stockpile Full: Food stockpile is full (15+ rations stored)"*, even with an empty kitchen fridge and abundant raw mutant meat.
- **Resolution**: Updated `check_func` in `is_camp_supply_capped` to strictly count prepared cooked meat meals (`_cooked`, `_b`, `_a`, and the 10 mutant steak varieties). Cooks now only pause when there is an actual surplus of cooked steaks (protecting mutant meats needed for artifact crafting per design intent), and will never be blocked by stored bread, canned goods, or raw meat.

### 📦 Container Auto-Sort Overhaul & Ammo Routing:
- **Root Cause**:
  - `get_auto_sort_target_box` routed all items beginning with `mutant_part_` to the kitchen fridge, causing scavengers to store inedible mutant trophies (chimera claws, bloodsucker tentacles, boars hooves, controllers brains) in food refrigerators.
  - Finished ammunition (`ammo_*`, `grenade_*`, `gl_*`, `vog_*`) was missing from Category 4 (which only checked raw components like powder and scrap). Finished ammo fell through to the generic fallback chest, which could resolve to a medical clinic or food fridge if no primary settlement chest was configured.
- **Resolution**:
  - Differentiated edible mutant meat (`_meat`, `boar_chop`, `snork_hand`) from crafting trophies in `get_auto_sort_target_box`. Only edible raw meats route to the fridge, while inedible trophies and body parts route to crafting/hunting containers.
  - Added explicit patterns for finished ammunition and explosives in Category 4, properly routing crafted ammo to ammunition boxes and workbench stashes.
  - Improved `fallback_chest` resolution to prioritize workshop and technician containers before medical kits or food coolers.

### 🖥️ Dedicated PDA Integration & Hotkey Cleanup:
- **Root Cause**: Direct hotkey (`DIK_K`) binding in `z_stalker_camp_builder_pda_monkeypatch.script` conflicted with skills/character sheet hotkeys and allowed opening the settlement interface outside of the PDA via `ShowDialog(true)`.
- **Resolution**: Per community request, completely removed the standalone popup dialog and direct `DIK_K` hotkey callback. The Homestead Settlement Manager is now cleanly accessed exclusively through the PDA Settlements tab. Removed the obsolete `hotkey_pda` option from MCM and configuration tables.

### ⚡ Camp Performance & Frame Hitch Elimination:
- **Root Cause**:
  - In `stalker_camp_builder.script`, a safety-net structure re-scan (`scan_camp_structures`) was invoked every 10 seconds whenever the player was near a settlement hub. Combined with a short 15-second cache TTL, this forced an unthrottled 65,534-entity ALife registry scan on the main Lua thread while walking around camps, resulting in severe 40 FPS drops and micro-stutters.
  - In `stalker_camp_builder_rivals.script`, `spawn_single_rival_camp` ran up to 35 raycasting candidate attempts synchronously on the main thread during rival camp placement.
- **Resolution**:
  - Increased `scan_camp_structures_cache` TTL from 15 seconds to 120 seconds, and added a 60-second cooldown timer to the near-camp update loop safety net. Placed furniture continues to update instantaneously via event callbacks (`hf_on_furniture_place`).
  - Reduced rival camp candidate raycasting iterations to 10 max per tick, smoothing out terrain search and eliminating frame hitching.

### 🎛️ MCM Full Localization Audit & Reset Relocation:
- **Missing Localization Strings Fixed**: Corrected 25 missing string identifiers across all MCM submenu tabs and tooltips in both English and Russian string tables (`ui_st_stalker_camp_builder.xml`). Resolved raw key displays for tab names (`General`, `Jobs & Production`, `Rival Settlements`, `Raids & Events`, `Quality of Life & Debug`), header summaries, hunter expedition yields, ambush chances, surplus cap toggles, and rival progression timers.
- **Relocated "Reset / Respawn Rival Camps" to Debug Tab**: Moved the `respawn_rival_camps` toggle from the `rivals` menu into the `qol_debug` tab to group all troubleshooting and reset utilities into one dedicated location, and updated internal MCM path reflection accordingly.

## v1.1.5 — TeleportObject Crash Fix & MCM Bad Path Resolution

### 🛡️ Critical Engine & Script Stability Fixes:
- **🛠️ Fixed "Unstable Game State / Busy Hands" Crash (`_g.script(519) : TeleportObject`)**:
  - **Root Cause**: In `stalker_camp_builder_rivals.script`, ground-snapping and relocation routines called `TeleportObject(id, gvid, lvid, pos)`. However, `TeleportObject` in Anomaly/GAMMA's `_g.script` is declared as `TeleportObject(id, pos, lvid, gvid)`. Passing `gvid` (a number) into the `pos` parameter and `pos` (an Fvector) into `gvid` caused line 519 of `_g.script` to invoke `alife():teleport_object()` with inverted types, triggering a fatal C++ script engine type-mismatch exception that crashed the script thread and triggered the engine's protective "Unstable Game State / Busy Hands" emergency popup and `tempsave`.
  - **Resolution**: Implemented `safe_teleport_object` and `safe_teleport_squad` helper routines in `stalker_camp_builder_rivals.script`. These correctly translate parameter positions (`id, pos, lvid, gvid` when delegating to `TeleportObject`/`TeleportSquad`, and `id, gvid, lvid, pos` when falling back to `sim:teleport_object`). All five call sites (chest snap, decoration anchoring, squad positioning, NPC ground adjustment, and initial squad spawn) are now strictly type-safe and wrapped in `pcall` nil-guards.

- **🧹 Eliminated `!MCM given bad path` Console & Log Spam**:
  - **Root Cause**: `get_mcm_setting()` in `stalker_camp_builder.script` attempted a brute-force search across five submenu categories (`general`, `jobs`, `rivals`, `raids_events`, `qol_debug`) using `ui_mcm.get()`. In MCM, calling `ui_mcm.get()` on any path that does not exist immediately writes `!MCM given bad path:<path>` to the console and game log. Checking any option registered in later categories (such as `rivals` or `qol_debug`) logged multiple red error lines on every check, while internal non-MCM fallback keys (such as `realtime_job_brewer_interval`, `realtime_job_woodcutter_interval`, etc.) flooded the console with 6 errors every single update tick.
  - **Resolution**:
    - Replaced the linear `ui_mcm.get()` category search with an explicit `mcm_option_path` lookup dictionary and dynamic schema reflection (`ensure_mcm_paths()`) that reads directly from `stalker_camp_builder_mcm.on_mcm_load()`. Non-MCM keys return `nil` immediately without querying `ui_mcm`, and registered options are queried directly through their exact full category path in a single clean call.
    - Formally registered missing options in `stalker_camp_builder_mcm.script`: `respawn_rival_camps` (in `rivals`) and `trader_despawn_time_hr` (in `raids_events`), wiring them cleanly to their pre-existing localization strings.
    - Updated `respawn_rival_camps` update-loop polling in `stalker_camp_builder.script` to query `get_mcm_setting("respawn_rival_camps")` and reset cleanly.
    - Cleaned up obsolete legacy flat-path fallback for `enable_pda_tab` in `z_stalker_camp_builder_pda_monkeypatch.script`.

- **⚡ Settlement Tab UI Performance Optimization**:
  - Eliminated high-frequency redundant scans and cache stalls when switching between settlement tabs in the Homestead PDA.

## v1.1.4 — Ground Snapping & Offline ALife Settlement Automation Engine

### 🥇 Ground Snapping & Anti-Floating Overhaul Complete:
- **🔍 Root Cause Analysis**:
  - **xrAI Navmesh vs. Visual Mesh Mismatch**: The engine's xrAI level navigation grid nodes (`level.vertex_position`) routinely float between 0.3m to 1.5m above physical visual terrain, rocks, and roads (or clip under mounds and slopes). Placing props directly onto level vertex coordinates caused items to hover in mid-air.
  - **Flat Y-Offset Propagation**: When camps were spawned offline (on other levels), all props received a flat Y-coordinate based on the parent smart terrain center or central chest. When the player entered the level, decorations either inherited this flat height or failed node-distance tests, leaving them hovering on sloped ground.
  - **Destructive Decoration Drops**: In earlier versions, if a decoration failed a strict 2.5m delta check relative to the chest during re-snapping, the code called `alife_release(se_decor)`, causing up to 25% of camp props to vanish or float.
- **🛠️ Key Architectural Changes**:
  - **1. Precision Physical Surface Raycasting (`get_surface_y`)**:
    - Added `stalker_camp_builder.get_surface_y(x, z, ref_y, probe_up, probe_down)` using the engine's native `ray_pick()` API.
    - Configured with static geometry flag 2 (`_ground_probe_ray:set_flags(2)`), targeting visual level geometry, terrain heightmaps, and indoor concrete floors while ignoring dynamic entities and ragdolls.
    - Fires vertical downward ray probes directly through each target coordinate: $\text{origin} = (X, Y_{\text{ref}} + 2.0, Z)$, $\vec{d} = (0, -1, 0)$.
    - Returns the exact visual contact height: $Y_{\text{surface}} = \text{origin}.y - \text{ray:get\_distance()}$.
    - Enhanced `get_ground_vertex_and_pos` and `get_close_ground_y` to query physical static geometry first, keeping exact $(X, Z)$ planar coordinates while matching the valid level vertex ID.
  - **2. Precision Surface Anchoring & Ground Snap Overhaul (`find_ground_anchor`)**:
    - **Removed Destructive Roof Clamp**: Discovered and eliminated a clamp in `stalker_camp_builder_rivals.script` that forcibly slammed `target_y` down to the smart terrain center if `target_y - smart.position.y > 4.0`. On sloped or hilly maps (Army Warehouses, Red Forest, Cordon, Garbage, etc.), this kept $(X, Z)$ on the hill while forcing $Y$ into the valley floor, burying chests and decorations 4–20 meters inside the hillside mesh.
    - **Multi-Altitude Navmesh Ground Probe (`find_ground_anchor`)**: Searches level vertices across a wide vertical span ($\pm 22\text{m}$) around candidate coordinates, locking to the exact walkable AI cell ($<0.7\text{m}$ 2D distance).
    - **Physical Geometry Surface Raycast**: Fires a static geometry probe downward from the AI vertex height to find the true visual terrain, rock, or floor mesh.
    - **Positive Elevation Clearance (+0.08m / +0.04m)**: Placed chests and props with a dedicated clearance offset (+8cm for chests and furniture, +4cm for sleeping mats) to prevent terrain clipping and sinking into grass.
    - **Decorations & Squad Anchoring**: Automatically grounds all camp decorations (chests, radios, lamps, sleeping bags, pallets) and squad members at their true $(X, Z)$ ground height.
  - **3. Automatic Savegame Rescue (`ground_snapped_v3`)**:
    - Introduced `camp.ground_snapped_v3` tracking and an automatic underground detection check (`pos.y < (ground_y - 0.04)`).
    - Any camps in existing savegames that were spawned underground or trapped by earlier versions are immediately detected, elevated to ground surface, and repositioned via `TeleportObject` upon loading or during the 10-second background watchdog loop.
    - Zero performance cost: exits in $<0.001\text{ms}$ once all camps on the level are verified grounded.

### 🌐 Homestead Settlement Jobs: Complete Offline Map & ALife Engine Overhaul:
- **🔍 Root Cause Analysis (Why Offline Jobs Froze & Paused)**:
  - In the X-Ray / Anomaly engine, when you travel to another map, that level goes offline.
  - **Engine API Mismatch (`alife():get_children(se_obj)` vs `se_box:children()`)**: The X-Ray Monolith engine exports `alife():get_children(se_obj)` as a generator iterator. It does **not** expose a `se_box.children` property (it is `nil`) or `se_box:children()`. Consequently, previous offline checks evaluated to `nil` and skipped scanning entirely, returning false for all required items. This caused Brewer (`PAUSED: No Water`), Crafter (`PAUSED: No Gunpowder`), Repairer (`PAUSED: No Damaged Gear`), and Cook (`PAUSED: No Raw Meat`) to immediately freeze and pause when away from camp.
  - **Hideout Furniture Workbench Stash Blacklist**: In Hideout Furniture, the workbench object is a physical structure whose actual inventory is held in an underground linked container (`workshop_stash`). `is_actual_container` had an explicit blacklist against `workshop_stash`, and `is_valid_camp_box` had a vertical distance clamp that rejected it. As a result, all items deposited into the workbench were completely invisible to settler jobs and the PDA.
  - **Client Object Bottlenecks**: Functions previously relied on `level.object_by_id(box_id)`, which returns `nil` for any object outside the current active level bubble.
- **🛠️ What Was Fixed & Overhauled**:
  - **1. Native Engine Server Container Iteration (`alife():get_children`)**:
    - Replaced all non-existent `:children()` loops across all job processors and status checkers with the engine's native iterator: `for child_id in sim:get_children(se_box) do`.
    - Implemented `stalker_camp_builder.iterate_server_container(box_id, callback)` providing fast, non-blocking iteration over all server-side inventory objects.
    - Updated `camp_has_item`, `camp_has_repairable_gear`, `find_and_consume_item`, `process_ammo_crafting`, `process_gear_repair`, `process_turret_maintenance`, `check_camp_chest_supplies`, and `get_camp_dashboard` to iterate server entities via `iterate_server_container`.
  - **2. Hideout Furniture Workbench Stash Support**:
    - Un-blacklisted `workshop_stash` in `is_actual_container`.
    - Updated `is_valid_camp_box` to recognize `workshop_stash` by checking horizontal 2D distance without falsely rejecting on vertical underground offsets.
    - Implemented `stalker_camp_builder.get_camp_containers(hub_id, camp)` to automatically resolve workbench stashes from `alife_storage_manager.get_state().workshop_stashes`.
    - Settlers now seamlessly detect, consume, and store items inside workbench storage.
  - **3. Offline Ammo Crafting & Directive Support**:
    - Crafters inspect server entity sections (`se_item:section_name()`), select the appropriate powder according to tier rules, consume 1 use via `consume_one_use(gunpowder_id)`, release scrap, and deposit crafted ammo boxes using `sb.deposit_item_to_camp`.
    - Player-set caliber directives (Pistol, Shotgun, Soviet Rifle, NATO Rifle, Sniper, Turret) are fully respected offline.
  - **4. Offline Defensive Turret Maintenance**:
    - Technicians scan offline settlement containers for `ammo_9x18_fmj` and `ammo_9x19_fmj`.
    - Offline ammo count is read and decremented directly via server packet data (`se_item.elapsed`), feeding the turret magazine through `hf_obj_manager`.
    - Empty boxes are released, and partially used boxes retain their exact bullet count.
  - **5. Offline Armor & Weapon Repair (Armorer / Technician)**:
    - Technicians scan offline containers for damaged gear (`cond < 0.95`) and fee provisions (vodka, conserva, tushonka).
    - Updates `se_rep.condition` directly on the server entity.
    - **GAMMA WPO (Weapon Part Overhaul) Compatibility**: Internal part wear values are calculated and saved to persistent storage via `item_parts` and `se_save_var` so all internal parts are properly maintained.
  - **6. Offline Fridge Food Preservation**:
    - Every 12 game hours, all camp fridges and stashes are scanned offline via `iterate_server_container`.
    - Perishable mutant meats, bread, and sausages have their condition restored via `se_item.condition = math.min(1.0, cond + fridge_cond_restore)`.
  - **7. Offline Water Pump Filtration**:
    - Water pumps now scan offline containers for charcoal and paper filters via `iterate_server_container`, pumping and filtering clean flasks into camp storage while offline.
  - **8. Multi-Use Item Safety**:
    - `find_and_consume_item` safely decrements single uses from multi-use items (water, vodka, fuel, filters) offline without deleting full stacks.

## v1.1.3 — Deep Job Automation, Closed-Loop Supply Chain & Infrastructure Overhaul

### 🎯 Crafter Caliber Selection & Production Directives:
- **Player-Controlled Ammunition Crafting**:
  - Addressed community feedback regarding randomized ammunition crafting.
  - Players can now instruct Crafters to focus on specific calibers via the PDA Tab 2 Directive Cycle button (`btn_job_directive`) or dialogue.
  - Supported crafting directives:
    - `Auto-Balanced (Default)`: Rotates through standard ammunition calibers.
    - `Pistol / SMG`: 9x18mm FMJ, 9x19mm FMJ, .45 ACP Hydro-Shock.
    - `Shotgun`: 12x70 Buckshot, 12x76 Dart.
    - `Soviet Assault`: 5.45x39mm FMJ, 7.62x39mm FMJ.
    - `NATO Assault`: 5.56x45mm SS109.
    - `Battle Rifle / Heavy`: 7.62x51mm FMJ, 7.62x54mm 7N1.
    - `Sniper / Magnum`: .338 Lapua Magnum, 9x39mm SP-5.
    - `Turret Ammo`: Standard 9x19mm magazines for automated defense turrets.
  - Telemetry badges on survivor cards display the active caliber focus (e.g. `[Caliber: Soviet 5.45/7.62]`).

### 📱 2D PDA Top Tab Optimization for Non-MAC Users:
- **Rescaled Top Navigation Bar & DXML Fix**:
  - Fixed DXML element attribute lookup in `modxml_stalker_camp_builder.script` (`xml_obj:getElement(child)`), ensuring the Settlements tab reliably injects on all standard 2D and Interactive 3D PDAs when Mod App Creator (MAC) is not installed.
  - Dynamically rescales and positions all tab buttons (width `64-69px`, step `53-59px`) to fit cleanly within the `548px` tab container header without clipping or overlapping the clock and battery indicators.
  - Added dedicated PDA hotkey toggle (`DIK_K` by default, configurable in MCM) and ESC key support to seamlessly exit the Settlement Manager.

### 🌪️ Environmental Storm Protection & Camp Coverage:
- **Blowout & Psi-Storm Immunity**:
  - Implemented dynamic engine hooks in `z_stalker_camp_builder_pda_monkeypatch.script` into `surge_manager.CSurgeManager.pos_in_cover` and `psi_storm_manager.CPsiStormManager.pos_in_cover`.
  - Settlers and companions located within active settlement boundaries are recognized by the Zone's environmental simulation as being inside safe cover, preventing catastrophic NPC fatalities during blowouts and psi-storms.

### 💾 ALife Serialization & Quicksave Crash Resolution:
- **Prevented Spawn Entity Table Corruption**:
  - Resolved a fatal engine crash occurring during quicksaves when settlers deposited crafted goods or scavenged loot into camp containers.
  - Eliminated illegal `spawned_unregistered = true` flags and duplicate `alife():register(se_item)` calls in `deposit_item_to_camp`, ensuring 100% stable ALife entity registration and savegame integrity.

### ⚔️ Rival Camp Faction Mapping & Decor Immersion:
- **Corrected Faction Squad Spawns**:
  - Fixed squad section names for Mercenaries (`merc_sim_squad_*`), Duty (`duty_sim_squad_*`), and Military in `stalker_camp_builder_rivals.script`.
  - Refined rival camp procedural prop generation pool: eliminated immersion-breaking, floating, or mismatched decorative props (chandeliers, wall mirrors, fragile ornaments).
  - Protected rival camp decorative structures from player pickup via `is_rival_camp_object`.

### ⚙️ Interconnected Settlement Supply Chain & Closed-Loop Economy:
- **Zero Free Resource Generation**:
  - Medics and production facilities no longer conjure free items out of thin air. Settlers now interact in a closed-loop economy where gathering feeds refining, refining feeds manufacturing, and manufacturing sustains the colony.
- **Woodcutter Profession (`woodcutter`)**:
  - Operates near tree clusters or settlements, harvesting **15–20 wood parts** (`prt_i_wood`) per cycle.
  - **Axe Multiplier**: Donating an axe (`wpn_axe`, `wpn_axe2`, `wpn_axe3`) grants a permanent **2x production multiplier** (**30–40 wood parts** per cycle).
  - **Charcoal Burning Cycle**: Alternating cycle converts **15 wood scraps** into **3–5 charcoal** (`charcoal`), directly fueling cooking stoves and crafting black powder.
  - **Work Directives**: Settlers can be instructed via dialogue or PDA Tab 2 to follow `Auto-Rotate (50/50)`, `Timber Focus`, or `Charcoal Focus`.
  - Production pauses when wood stockpiles reach 100 parts or charcoal reaches 20 units.
- **Brewer Profession (`brewer`)**:
  - Converts **15 wood scraps** and **1 clean water** into **5 Nemiroff Vodka** (`vodka`) per cycle.
  - **Drug-Making Kit Multiplier**: Donating an `itm_drugkit` equips the distillery with advanced glassware and condensers, permanently doubling output to **10 Nemiroff Vodka** per cycle.
  - **Workstation Support**: Stationed at Milk Cans / Bidons (`placeable_bidon`, `decor_bidon`, `bidon`), falling back to camp stoves or workbenches.
  - Production automatically pauses if wood, clean water, or storage capacity (cap: 20 vodka) is reached.
- **Medic Overhaul & Ethanol Synthesis**:
  - Medical production now strictly consumes Nemiroff Vodka (`vodka`) refined by camp brewers:
    - **Bandages** (`bandage`): Requires **1 Vodka** → 1 Bandage.
    - **AI-2 Medkit** (`medkit_ai2`): Requires **2 Vodka** → 1 Kit with **2 charges**.
    - **Potassium Iodide** (`antirad_kalium`): Requires **3 Vodka** → 1 Pack with **3 charges**.
    - **Ibuprofen** (`akvatab`): Requires **5 Vodka** → 1 Blister Pack with **5 charges**.
  - **Synthesis Directives**: Players can set production orders via dialogue or PDA Tab 2: `Auto-Balanced`, `Bandages Only`, `AI-2 Kits Only`, `Potassium Iodide Only`, or `Ibuprofen Only`.
  - Pauses production when medical stockpile reaches 15 units.
- **Scrapper Profession (`scrapper`)**:
  - Passively scours settlement ruins and debris for **10–15 metal scrap** (`prt_i_scrap`) and **5–10 fasteners** (`prt_i_fasteners`) per cycle.
  - **Demolition Tool Multiplier**: Donating demolition tools (`wpn_crowbar`, `wpn_sledgehammer`, `toolkit_p`) permanently doubles output to **20–30 scrap** and **10–20 fasteners**.
  - Directly feeds Crafter ammo presses and Technician armor/weapon repair tables.
- **Electrician & Free Power Infrastructure**:
  - Removed generator requirement: electricians maintain camp lighting networks for free with zero battery fuel drain.
  - **Battery Recharging Service**: Every cycle, electricians locate up to **3 drained or depleted batteries** (`batteries_dead`, `batteries_exo`, or condition < 0.95) in settlement storage and recharge them to **100% condition (1.0)**.
- **Self-Sustaining Water Pumps**:
  - Water pumps now tap deep groundwater aquifers naturally, producing clean drinking water flasks directly into camp storage without consuming filters or charcoal. Updated the in-game "How to Play" guide and item tooltips to reflect this.

### 📱 PDA Tab 2 & Dialogue Interface Enhancements:
- **Organized 2x6 Job Matrix Layout**:
  - Rebuilt the PDA job assignment selector into a clean, symmetric 2x6 grid accommodating all 12 settlement professions: Guard, Patrol, Scavenger, Hunter, Cook, Crafter, Repairer, Medic, Electrician, Woodcutter, Brewer, and Scrapper.
- **Remote Directive Cycle Button (`btn_job_directive`)**:
  - Added an interactive button in Module 4 of the survivor detail panel. Allows the player to cycle synthesis orders for Medics and harvest modes for Woodcutters remotely from anywhere in the Zone without having to return to camp.
- **Dynamic Tool Upgrade & Telemetry Badges**:
  - Settler cards display active equipment upgrades (`[Axe: 2x Boost]`, `[Distillery Kit: 2x Boost]`, `[Demolition Tools: 2x Boost]`) and current directive badges (`[Order: Auto-Balanced]`, `[Order: Charcoal Only]`).
- **Interactive Tool Hand-in & Order Dialogue Trees**:
  - Added comprehensive dialogue trees for Woodcutters, Brewers, and Scrappers to receive tool upgrades and set operational directives.
- **Localization**:
  - Full English and Russian text support with native `windows-1251` encoding.

### 📦 Universal Camp Hub & Placeable Workshop Container Integration:
- **Transparent Workbench Stash Resolution**:
  - Integrated Hideout Furniture workbenches (`placeable_workshop`, `settlement_camp_hub`) and companion underground stashes (`workshop_stash`, `CInventoryBox`).
  - Added dynamic resolution via `resolve_container_id` and auto-creation via `get_workshop_stash_id(id, true)`, guaranteeing that item spawns and searches target the valid physical inventory container rather than the parent physics object.
- **Settler Job Supply Awareness**:
  - Settlers performing all camp tasks now seamlessly search, consume, and deposit items across the Camp Hub workbench and any placed secondary workbenches.
  - Updated Cooks, Crafters, Technicians, Medics, Electricians, Turret maintenance, and Settler daily meal consumption to inspect all camp containers including the central Camp Hub workbench.
  - Rebuilt `find_best_container`, `find_and_consume_item`, `camp_has_item`, `camp_has_repairable_gear`, and `is_camp_supply_capped` to dynamically inspect online objects and offline ALife parent-child trees across all camp containers simultaneously.
- **Blacklist Poisoning Elimination**:
  - Fixed an issue where Hideout Furniture workbenches were permanently poisoned in `known_bad_inventory_boxes` upon early load before `m_data.workshop_stashes` was initialized. Workbenches and workshop stashes are now explicitly exempted from container blacklisting.
- **Storage Metrics & UI Synchronization**:
  - Overhauled `get_camp_storage_metrics` to query all camp storage units including the central Camp Hub workbench, accurately displaying settlement item counts, total weight, and inventory status in the Settlement PDA Tab and UI dashboards.
- **Eliminated Unwanted Basic Wooden Chest Spawning**:
  - Updated auto-sorting and deposit logic so that placing items into camp automatically targets the central Camp Hub workbench when no dedicated specialized chests exist, preventing redundant basic wooden chests from cluttering settlements.

## v1.1.2 — Settlement PDA Tab Restoration, MCM Bad Path Cleanup & Engine Stability

### 📱 Settlement PDA Top Tab Restoration:
- **Restored Visible Settlements Top Tab Across All Setups**:
  - Replaced the invisible dummy button (`x="1000" width="0" height="0"`) in `modxml_stalker_camp_builder.script` with a dynamically positioned, fully styled `<button id="eptSettlement">`.
  - Filters existing tabs to ignore off-screen dummy buttons (`x >= 800`), preventing previous offset calculation errors caused by Mod App Creator (MAC) dummy buttons.
  - Automatically adapts button width and step (`69px` / `58px` step on 3D PDA; `79px` / `68px` step on standard/Taskboard/GAMMA; `89px` / `78px` on widescreen).
  - Automatically expands `<tab>` container width (`tab_attr.width = math.max(cur_w, next_x + btn_width + 10)`) to eliminate tab clipping.
  - Dynamically updates any existing dummy `eptSettlement` nodes in-place with proper coordinates, textures (`ui_inGame2_pda_button`), and white text colors.
  - Preserves Mod App Creator (MAC) launcher app registration, allowing access from **both** the top tab bar and the MAC launcher.

### 🔇 MCM Bad Path Log Spam Elimination:
- **Direct Flat Option Routing**:
  - Fixed `get_mcm_setting()` in `stalker_camp_builder.script` to query `stalker_camp_builder/<opt_name>` directly at the flat root.
  - Removed iteration over non-existent submenus (`general/`, `jobs/`, `rivals/`, etc.), eliminating all `!MCM given bad path:stalker_camp_builder/jobs/verbose_notifications` console and log spam.

### 🛡️ Settler AI Scheme & Engine Type-Safety Safeguards:
- **Settler AI Stype Safeguard**:
  - In `setup_settler_beh_logic` (`stalker_camp_builder_npc.script`), guarantees `st.stype = modules.stype_stalker` (0) if unassigned before calling `xr_logic.set_new_scheme_and_logic`, preventing `!ERROR: ... trying to use a scheme not intended for stype scheme=beh stype=nil` during level transitions or load.
- **ALife Object Type-Safety Crash Fix (`_g.script:2062`)**:
  - Replaced fragile `alife_object` lookups with `safe_alife_object(id)` that strictly validates `tonumber(id)` within ALife ID bounds (`num > 0 and num < 65535`) and calls `alife():object(num)` directly.
  - Prevents fatal crashes when active task targets (`tsk.target`, `tsk.current_target`) contain string identifiers (e.g. story IDs or smart terrains).
- **Hunter Button XML Crash-Proof Failsafe**:
  - Added `<btn_job_hunter>` grid definition to `ui_stalker_camp_builder_pda.xml` (x=84, y=202).
  - Implemented `init_safe_job_btn` in `ui_stalker_camp_builder_pda.script` with `NavigateToNode` probe and programmatic `CUI3tButton()` fallback if XML tags are missing.

## v1.1.1 — Level Transition Auto-Save Crash Resolution & Settler Synchronization

### 💾 Level Transition Auto-Save Win32 Buffer Crash Fix:
- **Eliminated Bedrock Teleportation (`vector():set(0, -500, 0)`)**:
  - In `dispatch_scavenger_to_stash` and `dispatch_scavenger_regional_sweep`, removed underground coordinate placement that placed entities 500 meters beneath the terrain.
  - Positioning ALife entities off the level navigation graph poisoned `CLevelGraph::vertex_id` (`Invalid position for CLevelGraph::vertex_id specified`).
  - During map level transitions, the engine serializer executes `* Saving spawns... * Saving objects...`. When attempting to serialize ALife objects located outside graph navmesh bounds, Windows file buffer allocation failed with Win32 Error 8 (`[error][ 8 ] : Not enough memory resources are available to process this command at address 0x0000000140788257`).
- **Engine-Sanctioned Offline Transition**:
  - Settlers on active expeditions now maintain valid camp navmesh coordinates while being switched offline cleanly via engine method calls (`se_npc:can_switch_online(false)`, `se_npc:can_switch_offline(true)`, `alife():set_switch_online(npc_id, false)`, `alife():set_switch_offline(npc_id, true)`, and `utils_obj.switch_offline`).
  - Corrected method invocations to use `:` instead of property assignments (`=`), respecting X-Ray CScriptGameObject / cse_alife_human_stalker class interfaces.
- **Savegame Self-Healing on Level Load**:
  - Added self-healing verification in `normalize_camps`: any settler entity previously trapped at bedrock (`position.y < -50`) is automatically rescued and snapped back to `hub_obj.position` with valid `m_level_vertex_id` and `m_game_vertex_id`.
- **Save State Memory Optimization**:
  - Removed redundant `state.homestead_backup` table cloning which was duplicating the entire settlement and rival hierarchy into `m_data` on every save.
  - Added automatic pruning of `radio_logs` (max 20 per settlement, 30 global).
  - Sanitized `active_stash_expeditions` table serialization to primitive data fields only.
  - Stripped legacy `homestead_backup` payloads from older saves upon load to reclaim engine memory.

### 🎒 Scavenger Waiting-for-Orders Overhaul:
- **Camp Waiting State (No Countdown Timer)**:
  - Scavengers not currently dispatched on an expedition wait at camp for player orders with **no countdown timer**, displaying `%c[255,238,196,112]Scavenger (Waiting for Orders)%c[220,220,220]`.
  - Scavengers no longer run local passive cycles or display confusing resets while waiting at camp.
- **Active Expedition Progress**:
  - When dispatched on a single-stash or regional sweep expedition via PDA or dialogue, a live, smoothly ticking expedition timer is displayed: `Expedition: %d%% (%dm %02ds)`.
  - Expedition durations now use synchronized real-time seconds (`math.max(game_elapsed, real_elapsed * tf)`), preventing the countdown from ticking 10x too fast.
- **Expedition Lookup Numeric Fallback**:
  - Enhanced `get_scavenger_expedition_for_survivor` with multi-tier resolution (numeric ID -> name -> hub fallback -> single active expedition), ensuring expeditions are always correctly linked to the survivor.

### 🏹 Hunter Tracking Timer & UI Thread Protection:
- **Continuous 30-Minute Tracking Cycle**:
  - Restored a smooth, continuous 30-minute tracking countdown for Hunters (`Hunter: Tracking (%d%% - %s remaining)` in mint green `%c[255,144,238,144]`).
  - Upon cycle completion, automatically transitions to `Hunter (Ready)` in gold, delivering harvested meat into camp food storage or fridges before smoothly resetting for the next cycle.
  - Passed `camp` and `hub_id` context to `get_job_paused_status` inside `get_job_progress` and `get_job_time_remaining`, preventing container false-positive pauses from freezing the Hunter timer.
- **PDA UI Thread Protection**:
  - In `SettlementManagerPDA:UpdateSurvivorsProgress()`, wrapped each list item update iteration in `pcall`. An unhandled error or missing entity on one settler row will never crash the loop or freeze updates for subsequent settlers.
  - Wrapped `self:RefreshJobProgress(false, hub_id)` in `pcall`.
  - Fixed `colorize_pda_text` pattern substitution to use function replacements, preventing Lua `gsub` from eating `%` and corrupting `%c[...]` color codes.

## v1.0.7 - Fixes Applied

### 📱 Restored Top Bar Visibility in Mod App Creator (`mac_mcm.script`):
- **In `pda_laucher_tab:Reset()`**: Replaced `Show(false)` with `pda_menu:GetTabControl():Show(true)` so the top tab row remains visible and interactive while browsing apps.
- **In `pda_laucher_tab:OnAppClicked()`**: Added an explicit `pda_menu:GetTabControl():Show(true)` call whenever an app is opened.
- **In `mac_handle_tabs()`**: Added a guard in `pda.set_active_subdialog` ensuring `GetTabControl():Show(true)` runs when switching to any subdialog (except inspecting an NPC PDA).

### 🛡️ Universal Engine Fallback in `pda.script`:
- Added an automatic safeguard to `set_active_subdialog(section)` in both active `pda.script` mods (`Location_Discovery_Text_Disabler_v` and `G.A.M.M.A. ZCP 1.4 Balanced Spawns`):
  ```lua
  local pda_menu = ActorMenu.get_pda_menu()
  if pda_menu and pda_menu:GetTabControl() and (section ~= "eptNPC") then
      pda_menu:GetTabControl():Show(true)
  end
  ```
- Any time you switch to any tab (Map, Tasks, Statistics, Relations, Contacts, Guide, Radio, Messages), the top tab control is guaranteed to restore to visible.

### 🧹 Cleaned XML Handling in `modxml_stalker_camp_builder.script`:
- Removed the `pda.*%.xml` tampering logic in both mod and loose versions. Homestead cleanly operates as an app inside Mod App Creator (`app_settlement`), preserving the original `pda_16.xml` layout and button dimensions.

### 🔄 Updated `z_stalker_camp_builder_pda_monkeypatch.script`:
- Chained `pda_menu:GetTabControl():Show(true)` on subdialog routing.

### 💧 Water Pump Output:
- **Fix**: In `stalker_camp_builder_jobs.script`, updated `process_water()` to spawn `flask` (Clean Water Flask) instead of `mineral_water`.
- **Result**: Aligns with the in-game manual and enables tier 2 food crafting.

### 📦 Counter Item Traps & Pickup Engine Crash:
- **In `stalker_camp_builder.script`**:
  - Added `counter` to the strict blacklist in `is_actual_container()` and `find_available_camp_container()` to prevent crafters and scavengers from selecting counters as drop-off targets.
  - In `_G.alife_release`, unlinked (`parent_id = 65535`) and released any trapped children before releasing placeable props.
- **In `z_stalker_camp_builder_pda_monkeypatch.script`**:
  - Hooked `bind_hf_base.hf_binder_wrapper.pickup` to safely rescue any items trapped inside a picked-up prop directly into the player's inventory (`db.actor`), clearing child parent IDs before engine destruction to eliminate the `xrServer::Perform_destroy` crash.

### 🗺️ New Game / Zero Camps Initialization & PDA Stability (Loner, Great Swamp):
- **In `ui_stalker_camp_builder_pda.script`**:
  - Guarded `level_weathers.get_weather_manager()` before calling `:get_weather_cycle()` in `UpdateTopStatusBar()` to prevent nil call crashes on brand new games.
  - When no settlements exist (`count == 0`), default the PDA view to the `"guide"` tab (Settlement Field Manual) instead of an empty overview screen.
- **In `stalker_camp_builder_rivals.script`**:
  - Added nil-guards on `SIMBOARD`, `SIMBOARD.smarts_by_names`, and `SIMBOARD.squads` across squad scanning, smart terrain queries, physical migration, and camp terrain snapping to prevent early-tick nil errors.

### ✅ Verification:
- All modified scripts compiled cleanly with `luac.EXE -p` (0 errors).
- DXML parsing simulation confirmed all 8 buttons (`eptTasks`, `eptLauncher`, `eptRanking`, `eptRelations`, `eptContacts`, `eptEncyclopedia`, `eptRadio`, `eptLogs`) are intact in `<tab>` at standard width (550).

## v1.0.6b - Rival Camp Chest Dismantling & Interaction Hotfix

### 📦 Rival Camp Chest Dismantling & Interaction Stability:
- **Fixed `CScriptGameObject::ID` Destroyed Object Crash**: Resolved a severe engine crash and interaction lockup (`CGameObject : cannot access class member CScriptGameObject::ID!` / `you are trying to use a destroyed object [0]` repeating tens of thousands of times) when taking all items or picking up an emptied rival camp chest (`placeable_blue_box`).
- **Safe Deferred Stash Removal**: Hooked `actor_on_stash_remove` with `data.cancel = true` and deferred `alife_release` by 0.15s via `CreateTimeEvent`. This guarantees `UIInventory` and its `UICellContainer` instances have completely closed and deallocated before the server object is released, eliminating the engine callback race condition.
- **Direct Hotkey Dismantle (`Shift + F`)**: Players can now dismantle rival camp chests directly from the crosshair by holding `Shift + F` while looking at the chest. All contents inside the chest are automatically safely transferred to the player's inventory without loss, and the player is awarded the `blue_box_item`.
- **Empty Chest Quick Dismantle (`F`)**: Pressing `F` on an already-empty rival camp chest now directly dismantles it on the spot without forcing open an empty loot interface.
- **Dynamic Crosshair HUD Prompts**: The HUD interaction prompt dynamically reflects the chest state:
  - Non-empty chest: `Open Camp Chest (Shift+F to Dismantle)`
  - Empty chest: `Dismantle Camp Chest`
- **Hostile Occupant Guard**: Dismantling rival camp chests is safely restricted while active hostile garrison forces still occupy and defend the camp.
- **Save Game & Stash Registry Compatibility**: Automatically registers all active rival camp chests into `m_data.player_created_stashes` on spawn and during `sync_all_camp_map_spots`, ensuring complete compatibility with existing save games and Hideout Furniture stash handlers.
- **Global Inventory Antifreeze Crash Shield**: Wrapped `utils_ui.UICellContainer.game_object_on_net_destroy` with `pcall` in `stalker_camp_builder.script`, shielding the entire game loop from any online object destruction during open container menus.


## v1.0.6a - Russian Localization Restoration & Recruitment Progression Balance

### 🌐 Russian Localization Hotfix (Community Bug Report - Dyshegyb / Obi Wan Kenobi):
- **100% Windows-1251 Cyrillic Restoration**: Fixed a severe encoding corruption issue where all Russian dialogue lines, recruitment dialogues, job assignments, and UI strings were replaced by literal question marks (`??????`). Reconstructed all 477 string entries in authentic, pristine Windows-1251 Cyrillic with zero unmapped characters or question mark corruption.
- **Strict XML Spec Conformance**: Escaped all unescaped XML ampersands (`&` -> `&amp;`), verified well-formed ElementTree parsing across both English and Russian XML tables.

### ⚖️ Settlement Recruitment Ranking & Balance System (Community Feedback - Obi Wan Kenobi):
- **Rank-Gated Progression**: Stalkers are no longer all trivially recruited for free. Recruitment now authentically accounts for the stalker's experience, reputation, and rank (`ranks.get_obj_rank_name`):
  - **Novices & Trainees**: Free (0 RU) -- Rookies are eager for safety, shelter, and companionship.
  - **Experienced Stalkers**: 2,500 RU sign-on bonus.
  - **Professionals**: 5,000 RU sign-on bonus.
  - **Veterans**: 10,000 RU sign-on bonus + requires Settlement Defense >= 25.
  - **Experts**: 16,000 RU sign-on bonus + requires Settlement Defense >= 35.
  - **Masters**: 25,000 RU sign-on bonus + requires Settlement Defense >= 50.
  - **Legends**: 35,000 RU sign-on bonus + requires Settlement Defense >= 60.
- **PDA Hired Squad & Mercenary Exploit Fix**: Addressed the exploit where players hired an elite bodyguard squad via PDA interactive services and immediately recruited them into permanent free settlement workers. Hired companions must now meet rank requirements, pay the full sign-on fee to permanently leave freelance contracting, and ensure the destination camp meets minimum defense thresholds.
- **Refugee Exemption**: Refugees seeking shelter at camps via dynamic settlement events remain 100% free to recruit, preserving emergency narrative events.
- **Dynamic Dialogue Telemetry & Audio**: Dialogue choices now display the required sign-on fee (e.g. `Sure, send me to Cordon Camp (2500 RU)`), play currency exchange audio (`interface\inv_money`) upon agreement, and display clear notifications if funds or settlement defenses are insufficient.
- **MCM Customization**: Added MCM configuration toggles under General Settings:
  - `Recruitment Rank & Fee Requirements`: Toggle ON/OFF to enable rank gating or play in unrestricted sandbox mode (Default: ON).
  - `Recruitment Fee Multiplier`: Slider (0.0x to 3.0x, Default: 1.0x) to tune sign-on costs.


## v1.0.6 - Settlement Integrity, Companion Stability & Community Quality-of-Life Update

### 👥 Settler Companion Level-Transition & Rejoin Fixes:
- **Level-Transition Eviction Resolved**: Settlers taken into the player's squad as active companions are no longer stripped of companion status, evicted, or snapped back to the camp workbench when traveling into a level containing a settlement.
- **Companion Rejoin Deletion Fix (Happy's Bug)**: Asking a recruited companion who joined a settlement to rejoin the player's companion squad no longer permanently deletes the NPC. Fixed `release_settler_home_squad` to unregister the stalker first and only release the squad if it contains zero remaining members.
- **Companion Squad Membership Protection**: `actor_on_first_update`, `teleport_settler_to_camp_level`, and `heal_settler_squad_membership` now explicitly guard and preserve active companion settlers.

### 🏗️ Settlement Mechanics & World Integrity:
- **Zero Loot Loss on Camp Dismantling**: Dismantling a settlement via the PDA now exclusively removes the camp's administrative boundary zone and frees settler assignments. All player-placed storage containers, stashes, workbenches, and all contained player loot remain 100% safe in the world.
- **Secondary Workbenches Allowed in Settlements**: Placing additional workbenches inside an existing settlement boundary now correctly registers them as secondary workshop stations instead of refunding and deleting them as illegal hubs.
- **Empty Settlement Raid Immunity**: Settlements with 0 survivors (such as personal player crafting hideouts) are now completely immune to hostile raid rolls, allowing players to maintain quiet private workshops without unwanted attacks.
- **Underground Spawning & Floor Clipping Fix**: Rewrote `get_furniture_front_vertex_and_pos` with a 3D vertex scoring algorithm penalizing vertical offset (`y_delta * 4.0`), tightened height tolerances, and added +0.1m height clearance. Restored settlers, refugees, and trade caravans now spawn standing cleanly on the floor rather than clipping below workbenches.
- **Rival Camp Reinforcement Movement Crash Fix**: Fixed a fatal script error (`attempt to index local 'npc' (a number value)`) in `camp_npc_move_to` occurring during wilderness camp battles when an allied rival camp dispatched reinforcement stalkers. `camp_npc_move_to` and `camp_npc_arrive` now safely accept both NPC IDs and game objects, gracefully handle vector coordinates, and enforce vertex validation.

### ⚙️ MCM Options & Localization:
- **Split Survivor Capacity Sliders**: Replaced the single global survivor slider with two independent MCM sliders:
  - **Max Survivors (Player Settlement)**: Range 1–25 (Default: 12)
  - **Max Survivors (Rival Camp)**: Range 1–10 (Default: 5)
- **Complete Russian Localization Parity**: Added full Russian translations for all new MCM sliders and updated settlement dismantle confirmations in Windows-1251 encoding.

### 🛠️ Critical Community Feedback Fixes:
- **Scavenger Expedition Authentic GAMMA White vs. Yellow Stash Logic**:
  - Full replication of S.T.A.L.K.E.R. G.A.M.M.A.'s White vs. Yellow stash system for Scavenger Expeditions:
    - **Yellow (Rare) Stashes**: Authentic chance to loot level-appropriate toolkits (`itm_ammokit`, `itm_drugkit`, `itm_basickit`, `itm_advancedkit`, `itm_expertkit`) adhering to GAMMA's 33-zone `tools_map_tiers` lookup and milestone progression (`actor_find_basic_kit`, `actor_find_advanced_kit`, `actor_find_expert_kit`), degraded weapons (20%–37% condition, empty magazines), degraded armor/helmets (5%–35%), rare artifacts/containers, and high-tier repair components.
    - **White (Common) Stashes**: Loot pool strictly restricted to common ammunition, loose casings (`casing_p`, `casing_s`, `casing_r5`, `casing_r7`), gunpowders (`powder_1`, `powder_2`, `powder_3`), bullet tips, cleaning gear, medical supplies, and basic crafting materials. Strictly 0% chance of toolkits or weapons/armor.
    - **Existing Stash Cache Extraction**: Scavengers looting stashes with pre-generated GAMMA strings (`treasure_manager.caches[id]`) or physical container children extract the exact items rolled by the engine, preserving all existing degraded conditions and internal part wear.
    - **PDA Map Spot Classification & Expedition Receipt**: Right-click context menus on PDA stash markers display `[Yellow Stash]` vs `[White Stash]` badges, and the expedition return receipt dynamically itemizes loot with White vs. Yellow breakdown and individual item quantities.
    - **Unregistered Netpacket Condition Injection**: Weapons and armor are injected via unregistered netpackets before engine registration, ensuring GAMMA's Weapon Parts Overhaul (WPO) correctly rolls realistic matching internal part wear instead of 100% mint condition.
- **Camp Raid Faction Hostility, Placement & Grace Period**:
  - *Raid Grace Period*: Placing a new workbench now establishes a 1.5 in-game day raid grace period, preventing instant raids from triggering the moment a settlement is founded. Fixed startup checks to avoid uninitialized raid rolls.
  - *Faction-Aware Hostility*: Raids now dynamically evaluate player faction relations (`sb.get_enemy_faction_for`). Bandit and Renegade players will no longer encounter peaceful Bandit raiders lounging by the campfire; raids now deploy authentic enemy factions (Loners, Duty, Military, Monolith) or aggressive mutant packs (Snorks, Bloodsuckers, Psy-Dogs, Zombied Stalkers).
  - *Perimeter Spawning & Aggressive Rush*: Raiders now verify 3D ground geometry at `>= 65m` outside camp boundaries, completely resolving raiders spawning directly on top of the workbench. Squads are given direct attack orders (`squad.rush = true`, `get_script_target = AC_ID`, enemy relation enforcement) to aggressively assault the base.
- **Persistent Job Progress Across Level Transitions & Sleep**:
  - Survivor job progress (cooking, crafting, water pumping, repairs, scavenging, medical supplies, electrical work) no longer resets to 0% when transitioning between maps, fast-traveling, or sleeping.
  - Real-time and game-time progress clocks now rebase smoothly on level entry and game load using the engine's time factor. Settlers now realistically continue their work while the player is away exploring the Zone or resting.
  - Recruited companions transitioning between companion duty and settlement work retain their exact job progress percentages.
- **Furniture Placement Freeze Fix**:
  - Fixed a bug where waiting 2–3 seconds after initiating placement of any furniture (workbenches, beds, laptops, containers) caused the placement hotkey to stop responding, the placement message to disappear, and bounding box outlines to freeze unmovable in midair.
  - Removed an erroneous placement state interrupt in `actor_on_update` that was falsely overriding Hideout Furniture's active placement loop when the player had an active slot assigned.
  - Players can now take as much time as needed to position, rotate, and align furniture without interruption.

### 🔊 Audio & Feedback Polish:
- **Routine Job Completion Audio Silenced**: Silenced repetitive background inventory chime clicks (`interface\inv_slot`) during background survivor job cycles (cooking, crafting, water pumping, repairs, scavenging).
- **Interactive Audio Retained**: Auto-sorting supplies into storage (`interface\inv_drop`), hospitality consumption (`interface\inv_drink`), clinic and field medic treatments (`interface\inv_medkit`, `interface\inv_drink`), and automated turret ammo recovery remain active for clear tactile feedback.


## v1.0.5 - Master UI Overhaul: Tactical PDA Aesthetic, Dynamic Telemetry & Interactive Roster Matrix

### Complete 5-Tab Tactical PDA & Dialog Overhaul:
- **Universal Left-Rail Navigation & Top Military Status Bar**: Full aesthetic unity across all 5 tabs with dynamic color accents (Gold, Mint Green, Crimson, Sky Blue, Cyan), real-time RF signal strength calculation based on hub distance, atmospheric storm monitor, and military time clock.
- **Tab 1: Settlements Overview**: Full-width modular architecture with brushed-metal background panels (`ui_homestead_module_bg`) and header stripes (`ui_homestead_module_header`) across Personnel, Defense Grid, Logistics/Supplies, and the 8-button Operations grid.
- **Tab 2: Settlers Roster & Dossier**: Redesigned scrollable layout with high-resolution portraits, real-time telemetry, an 8-profession 2x4 assignment matrix with gold active glow, and uniform full-width (152x26px) stacked Field Station command buttons (`Anchor Position`, `Recall`, `Rename`).
- **Tab 3: Rival Wilderness Camps**: Real level landscape photos for 21 Zone levels, dynamic threat banners (`[! THREAT IDENTIFIED // HOSTILE !]`, `[ABANDONED]`, `[ALLIED]`), and tactical recon intel.
- **Tab 4: Settlement Radio Transceiver**: Full-width transmission cards with category badges (Combat Alert, Scavenger Expedition, Logistics, Transceiver), frequency filter chips, and log clearing.
- **Tab 5: Field Survival Guide**: 10 modular operational directives covering camp hubs, recruitment, jobs, logistics, base defense, rival camps, and MCM options.
- **Tactical Modal Popups**: Replaced vanilla grey backpack dialog with custom brushed-metal military terminal (`ui_homestead_dialog_bg`) for both Settlement and Survivor renaming.

### Engine Stability, Polish & Bug Fixes:
- **Luabind Userdata Comparison Crash Fix**: Replaced `it == item` userdata comparisons with primitive ID comparisons (`it.survivor_id == sel_surv_id`), resolving the `No such operator [__eq]` CTD in `OnSurvivorSelected`.
- **Radio Feed Crash Fix**: Switched `InitFrame` to `InitStatic` for 2D quad textures in `PopulateRadioFeed`, preventing hard C++ crashes in `AnomalyDX11AVX.exe`.
- **Field Station Button Stacking & Sizing**: Standardized `btn_position_here`, `btn_position_recall`, and `btn_rename_survivor` to uniform 152x26px stacked layout, eliminating horizontal text overlaps.
- **Overview Module Background Panels**: Initialized all module background statics and headers in Lua `InitControls()` so brushed-metal panels render properly in-engine.
- **Listbox Overlap & Selection Box Polish**: Dynamic card height calculation and synchronized bounds prevent card overlap and ensure selection outlines wrap multi-line cards cleanly.
- **Settler Dialogue & Dedicated AI Logic**: Created `beh_settler.ltx` scheme to eliminate companion dialogue lockouts (`meet_use_no_talk_leader`) and hardened recruitment preconditions against speaker argument swaps.
- **Workshop Stash Exclusion & Underground Container Guard**: Blacklisted Hideout Furniture subterranean `workshop_stash` (`y - 50`) from container scans, auto-sort, and scavenger returns, restoring player workshop access.
- **Animation States & Audio Validation**: Mapped settler job animations to valid engine states (eliminating `ILLEGAL SET STATE CALLED`) and fixed missing `inv_item_use.ogg` reference.

### Asset Pipeline & Localization:
- **50 Custom DDS Textures**: Bundled 21 level landscape photo thumbnails, selection frames, status banners, module headers, and 4-state 3tButtons registered in `ui_pda_stalker_camp_builder.xml`.
- **Pure ASCII & Font Safety**: 100% clean ASCII characters in scripts and English XMLs (no UTF-8 emojis/mojibake), eliminating 8-bit font rendering corruption.
- **Full Russian Localization**: 100% string parity across all 54 UI identifiers encoded in Windows-1251.

## v1.0.4 — Critical Hotfix Release: Russian CTD Fix, Harvester Stash Exclusion, Global Repair Fix, Scavenger Expedition Save Persistence & Turret DLTX Fix

### 🇷🇺 Russian Localization Launch Crash Fixed & Complete String Parity
- **Fixed CTD on Game Startup**: Removed duplicate closing `</string>` tag at line 401 of `configs/text/rus/ui_st_stalker_camp_builder.xml` that caused a fatal X-Ray engine XML parser failure (`mismatched tag: line 401`) when booting the game with Russian language selected.
- **100% Russian Localization Parity**: Translated and verified all 108 previously missing strings (457/457 total strings across both English and Russian), including full coverage for all MCM settings, Scavenger expedition radio chatter, Settlement Technician factory overhauls, Clinic Doctor treatments, and Settlement Specializations in Windows-1251 encoding.

### 📦 Artifact Harvester & Display Counter Stash Exclusion
- **Prevented Loot Dumping into Harvesters**: Added explicit exclusions for `placeable_artifact_harvester`, `artifact_harvester`, `placeable_display_counter`, and `placeable_weapon_rack` in `structure_type_exact` and `find_best_container()`.
- **Primary Deposit Chest Integrity**: Scavengers, crafters, and auto-sort routing now strictly deposit loot into actual storage chests and stashes (`camp.primary_chest_id`). Specialized artifact harvesters and display counters are completely exempted from acting as generic camp deposit boxes.

### ⚖️ Vanilla & GAMMA Repair Balance Restored (No More 100% Free Repairs)
- **Eliminated Global Repair Monkeypatch**: Removed intrusive global hooks into `inventory_upgrades.effect_repair_item` and `UIInventory.RMode_RepairYes`. Routine player inventory cleaning with gun oils, solvents, or repair kits now restores condition by their intended vanilla/GAMMA amounts (e.g. +5% or +10%) rather than instantly cheat-restoring all weapons, armors, and internal parts to 100% mint condition.
- **Encapsulated Settlement Technician Overhaul**: The comprehensive WPO factory restoration feature is now strictly confined to speaking with your camp technician via the dedicated dialogue option (`st_camp_tech_overhaul_ask`).

### 🗺️ Scavenger Expedition State Persistence & Reliability
- **Save/Load State Persistence**: Added `active_stash_expeditions` to `save_state()` and `load_state()`. Quicksaving, autosaving, sleeping, or changing levels during an expedition now properly preserves ongoing expeditions instead of resetting scavengers to idle mid-run.
- **Robust Type-Safe NPC Matching**: Updated `get_scavenger_expedition_for_survivor()` to compare numeric IDs (`tonumber(exp.npc_id) == tonumber(npc_id)`) with fallback to survivor name matching, preventing premature orphan-clearing of active scavengers when opening the PDA map.
- **Guaranteed Loot Deposit & Radio Feed Receipts**: Post-expedition return receipts and haul summaries are now automatically broadcasted to both the player's PDA tip feed and archived in the **Radio Feed** tab under `[ Expeditions ]`.

### 🛡️ Automated Pistol Turret DLTX Standalone Definitions
- **Self-Contained Base Sections**: Removed `!` DLTX override prefix from `[pistol_turret]`, `[placeable_pistol_turret]`, and `[turret_table]` in `items_hf_gun_turret.ltx`, allowing pistol turrets to be crafted and spawned via the debug menu without requiring third-party base mods.
- **Corrected PDA Defense Breakdown**: Removed `"hg_"` wildcard prefix from gadget substring checks so general Hideout Gadgets items (wiring, lights, switches) no longer misclassify as turrets in the settlement overview.

## v1.0.3 — Master Release: iTheon Tactical PDA Theme, Settlement Radio Feed, Dynamic Auto-Extending Cards, Calibrated Expeditions, Companion BEH AI Lock & WPO Repair Overhaul

### 🎨 Authentic iTheon Taskboard Modern PDA UI & Tactical Theme
- **Mod App Creator (MAC) De-duplication**: Resolved duplicate entry in `Launcher > Network > Settlements`. When Mod App Creator (MAC) is active, Homestead cleanly integrates as a standalone launcher app (`Launcher > Settlements`) and skips injecting duplicate subdialog buttons into the network tab bar.
- **Aesthetic Refresh Icon Buttons**: Removed textual labels from all PDA refresh buttons (`btn_refresh_survivors` and `btn_refresh`). Buttons now cleanly display the high-resolution circular refresh icon texture (`ui_inGame2_pda_taskboard_custom_refresh`) with zero text clutter.
- **Integrated Texture Sheet**: Embedded `taskboard_icons.dds` texture descriptor providing high-resolution 9-slice dark slate metallic card frames (`ui_inGame2_pda_taskboard_custom_background`) and glossy gradient action buttons (`ui_inGame2_pda_taskboard_custom_refresh`).
- **9-Slice CUIFrameWindow Geometry**: Converted all settlement stat cards, survivor dossiers, rival intelligence briefs, and list items to use 9-slice `InitFrame` rendering with zero-overlap layout geometry across all 5 navigation tabs.
- **Real NPC Face Portraits**: Integrated dynamic stalker face rendering (`npc:character_icon()`) inside individual survivor roster cards (40x40px) and inspector dossiers.
- **Top Environmental Military Status Bar**: Real-time physical RF signal strength indicator (`📶 SIGNAL: 100% (LOCAL)` vs `📶 SIGNAL: 64% (RELAY)`), dynamic weather cycle (`ATMOS: CLEAR`, `ATMOS: RAINSTORM`, `ATMOS: PSY-STORM`), live military clock (`TIME: 14:22`), and active settlement hub indicator (`HUB: ROSTOK OUTPOST`).
- **Multi-Segmented ASCII Graphic Gauges**: Real-time text-based visualization for Morale (`85% [||||||..]`), Base Defense (`78/100 [||||||..]`), Camp Storage Weight (`142 / 250 kg [||||....] 57%`), and Survivor XP (`XP: 840/1500 [|||||.....] 56%`).
- **Color-Coded Typography**: Distinct color palettes across tabs: `#EEC470` Gold for active selections, `#90EE90` Mint Green for active operations/promotions, `#64C8FF` Sky Blue for expeditions, `#FF6464` Crimson for combat alerts and dismissals.

### 📐 Universal Dynamic Card Auto-Extension & Text Wrapping (`complex_mode="1"`)
- **Universal Multi-Line Word-Wrapping**: Enabled `complex_mode="1"` and calculated inner text boundaries on every text label across the entire mod UI (`settlement_row_name`, `settlement_row_details`, `survivor_row_name`, `survivor_row_status`, `survivor_row_rank`, `survivor_job`, `camp_def_breakdown`, `rival_camp_intel`, `radio_row_text`, `guide_section_body_text`), completely eliminating horizontal text spillover.
- **Universal Height Measurement**: Every card across the mod dynamically measures its rendered content height with `AdjustHeightToText()` and auto-scales the 9-slice metallic card frame (`card_bg:SetWndSize`) with clean internal padding.
- **Dynamic Element Shifting**: Automatically calculates the bottom coordinate of expanding cards and dynamically slides all subsequent buttons and controls downward:
  - *Survivor Dossier*: Job buttons, positioning actions, and transfer controls slide dynamically below the expanding workstation telemetry card.
  - *Settlement Overview*: Camp specialization picker and 7 action buttons slide dynamically below the expanding defense breakdown card.
  - *Rival Intel*: Locate map and refresh buttons slide dynamically below the expanding recon report card.

### 🔲 Non-Overlapping Layout Geometry & Expanded Listbox Slots
- **Rival Camps Column Layout Synchronization**: Realigned `rival_list` coordinates from $Y=136$ to $Y=162$ ($W=180, H=510$), matching `settlement_list` pixel-for-pixel. The top header background and "Rival Outposts" title box render cleanly above the list without card overlap.
- **Guaranteed Listbox Item Separation**: Expanded listbox slot heights in XML and dynamically bounded row heights (`card_h + 8`):
  - `survivor_list`: Expanded to `item_height="88"` (`158px` card width), ensuring a clean `8px` vertical breathing margin between adjacent settler cards.
  - `settlement_list`: Expanded to `item_height="68"` (`162px` card width), ensuring zero collision.
  - `rival_list`: Expanded to `item_height="68"` (`162px` card width), ensuring zero collision.
- **Dynamic Sub-Label Repositioning**: In `SurvivorListItem`, `SettlementListItem`, and `RivalListItem`, sub-labels (job assignments and camp locations) are dynamically positioned below the measured height of the name (`status_y = 4 + name_height + 3`), preventing wrapped names from rendering on top of job descriptions.
- **Dedicated Lines for Level & Experience**:
  - *Survivor Dossier*: Stalker Name (Line 1), Level & Rank (Line 2: `Rank: Veteran (Tier 2)`), and Experience (Line 3: `XP: 450 / 700 (64%)`) each render on their own dedicated, dynamically measured lines.
  - *Settler Roster Cards*: Name (Line 1), Job Status (Line 2), and Rank Badge (Line 3: `Tier 2 (Veteran)`) render with clean separate lines.
- **Flush Column Alignment Beside Scrollbars**:
  - All cards expanded to fit flush against vertical scrollbars with 0 dead gap and 0 overlap (`162px` for 180px columns, `158px` for 175px columns, `350px` for 370px panels, `544px` for 564px scrollviews).

### 📻 Dedicated Settlement Radio Feed & Real-Time Event Log (5th Navigation Tab)
- **5th Navigation Tab**: Added a dedicated `[ 📻 Radio Feed ]` tab (`btn_tab_radio` / `radio_panel`) paired with the left-hand settlement selector for real-time base telemetry.
- **Seamless Full-Width Ribbon Header**: Rebuilt radio panel filter and action buttons to span edge-to-edge ($X=0$ to $X=564$) continuously without dead gaps:
  `[ All Signals ]` (100px) | `[ Expeditions ]` (100px) | `[ Logistics ]` (96px) | `[ Combat Alerts ]` (100px) | `[ Scan Zone ]` (90px) | `[ Clear Feed ]` (78px).
- **Auto-Extending Transmission Cards**: Each radio transmission card measures its text height with `AdjustHeightToText()` and auto-resizes the 9-slice frame (`544px` width) for 1-line pings or 10-line combat telemetry logs.
- **Real-Time Event Logging Engine**: Automatically captures and records:
  - Scavenger expedition departures, checkpoints, ambush victories, and haul summaries.
  - Crafter ammunition synthesis cycles and turret reloads.
  - Cook meal preparation and hospitality buffs.
  - Water pump filtration cycles and filter consumption.
  - Medic diagnostic treatments and drug deliveries.
  - Base defense alarms, turret engagements, and raid repulsion summaries.
  - Smart auto-sort dump reports.
- **Live Zone Scanner & Telemetry Seeder**: Added a live radio scanner (`btn_radio_scan`) that broadcasts live settlement diagnostics, generator health, defense status, and local RF telemetry.
- **Save Game Persistence**: Radio activity entries serialize directly into save game state (`m_data.stalker_camp_builder_radio_logs`) preserving radio intercept history across game saves and reloads.

### 🌐 Complete String Localization Synchronization (English & Russian)
- **100% Localized String Tables**: Fully synchronized all UI button identifiers and labels in both English (`configs\text\eng\ui_st_stalker_camp_builder.xml`) and Russian (`configs\text\rus\ui_st_stalker_camp_builder.xml` Windows-1251):
  - *8 Job Buttons*: `st_job_idle_btn`, `st_job_guard_btn`, `st_job_scavenge_btn`, `st_job_craft_btn`, `st_job_repair_btn`, `st_job_cook_btn`, `st_job_medic_btn`, `st_job_electrician_btn`.
  - *Survivor Management*: `st_pda_btn_position_here`, `st_pda_btn_position_recall`, `st_pda_btn_rename_survivor`, `st_pda_btn_transfer`, `st_pda_settlement_survivors_count`.
  - *Rival Intel*: `st_pda_rival_status_lbl`, `st_pda_rival_faction_lbl`, `st_pda_rival_location_lbl`, `st_pda_rival_garrison_lbl`.
  - *Dialogs & Navigation*: `st_rename_settlement_title`, `ui_st_ok`, `ui_st_cancel`, `st_dismantle_camp`, `st_pda_tab_*`.
- **Complete Russian In-Game Guide**: All 10 tactical guide chapters translated into Windows-1251 Russian.

### 📖 Comprehensive In-Game "How to Play" Guide Overhaul
- **10 Rich Tactical Chapters**: Completely restructured the in-game Guide tab into 10 structured sections with colorized typography (`#EEC470` Gold, `#90EE90` Mint, `#64C8FF` Sky Blue, `#FF6464` Crimson):
  1. *Establishing a Settlement (Hubs, Boundaries & Storage)*
  2. *Recruitment, Housing Capacity & Roster Management*
  3. *Settler Professions & Automation Work Cycles*
  4. *Smart Auto-Sort, Refrigerators & Water Filtration*
  5. *Base Defense, Turrets, Gadgets & Raid Defense*
  6. *Rival Wilderness Camps & Tactical Intel*
  7. *Settlement Radio Feed & Event Logging*
  8. *Specializations, Morale & Trade Caravans*
  9. *MCM Configuration & Customization*
  10. *Quick-Start Survival Checklist*
- **Full Dual-Language Localization**: 100% English and Russian (Windows-1251) translations.

### 💂 Native Companion 'BEH' Workstation Anchor & Anti-Wander System
- **Engine-Level Workstation Locking**: Integrated Anomaly's native companion behaviour scheme (`beh` via `scripts\beh_companion.ltx`) for all working and station-anchored settlers.
- **npcx_beh_wait + rally_lvid Activation**: When a settler arrives at their furniture or is ordered to hold position, Homestead activates the native `beh` wait state and locks `st.beh.rally_lvid` to their station vertex.
- **100% Anti-Wander Guarantee**: Because the C++ engine's native `beh` scheme controls the NPC's action planner, all ambient wandering, corpse looting, weapon scavenging, and smart terrain goal evaluators are fully blocked. Settlers hold position indefinitely at their furniture just like a companion told to "Wait here".
- **Instant 'Send Here' Teleportation**: Clicking "Send Here" in the PDA Survivors Tab or commanding a settler via dialogue ("I want you to stay and work right here") instantly teleports the settler to that coordinate and immediately locks them in place with the native `BEH` wait scheme.
- **Eliminated Smart Terrain Hijacking**: Completely detached settlers from vanilla smart terrain job trees (`m_smart_terrain_id = 65535`), preventing vanilla patrol/guard routines from pulling them away from camp.
- **Hysteresis Station Anchoring (2.0m entry / 3.2m break)**: Settlers who arrive at their workstation enter a firm station lock (`move.stand`, `standing`, locked animation) with expanded 1.25m furniture clearance offsets to prevent physics mesh collision overlap.
- **Defensive Combat & Dialogue Retained**: In the event of a camp raid, settlers seamlessly engage hostiles and defend the camp, immediately returning to their station vertex once combat concludes.

### 💉 Settlement Medic Dialogue & Full Diagnostic Triage
- **Unlocked All Medical Services**: Removed restrictive health preconditions that previously hid treatment options when the player had high raw health.
- **Full Service Menu Always Visible**: Speaking to a settlement medic immediately presents all available medical procedures (Patch wounds, Purge radiation, Full treatment, Trade medicines, Deliver Drug-Making Kit, Anchor station).
- **GAMMA Body Health System (BHS) Compatibility**: Full compatibility for repairing localized limb trauma and heavy bleed in GAMMA regardless of overall health percentage.

### 🔧 Dynamic WPO Weapon Repair Engine & Unjamming
- **Work-Scaled WPO Pricing**: Price dynamically scales by weapon condition deficit and individual damaged WPO internal parts (barrel, bolt, trigger, gas tube, receiver).
- **100% Factory Mint Restoration**: Paying for repair restores the weapon and all internal parts to 100% factory condition with C++ misfire clearance (`SetMisfire(false)`).
- **Toolkit Deliveries**: Deliver Basic, Advanced, and Expert Toolkits to unlock Tier 1-3 equipment upgrades.

### 🔇 Audio Removal & Interface Silence
- **Audio Removal**: Completely disabled interface sound triggers per user directive for a silent, clean PDA interface.

### 🐛 Critical Bug Fixes & XML Parser Hardening
- **Vanilla PDA Top Tabs Preservation**: Fixed an issue in DXML tab injection where setting the `<tab>` element width stripped existing `x`, `y`, and `height` attributes. All existing attributes are now fully preserved, ensuring vanilla top tabs (`Map`, `Tasks`, `Ranking`, `Relations`, `Contacts`, etc.) never vanish.
- **Auto-Sort Arithmetic Crash Fix**: Fixed `attempt to perform arithmetic on global 'count_transferred' (a nil value)`.
- **XML Node Schema Validation**: Verified all 129 XML node bindings with 0 missing tags.
- **Engine XML Parser Cleansing**: Purged `.metadata.json` sidecar files from `textures_descr\` and `gamedata\`.
- **Water Pump Offline Scanning & Multi-Use Item Fix**: Water pumps now scan offline container children and decrement uses without destroying multi-use containers.

## v1.1.4 — Realistic 5 km/h Dynamic Distance Calculation & Real-Time Timer Sync

### 🏃 Realistic 5 km/h Distance-Based Transit Calculation
- **Physical Walking Speed Model**: Replaced hardcoded random expedition timers with dynamic distance-based calculation calibrated to a realistic **5 km/h walking speed** ($1.39	ext{ m/s}$) with $1.35	imes$ terrain detour compensation and 3 minutes per stash searching/packing.
- **Dynamic Single Stash Distance**: Calculates exact 2D distance between settlement hub and target stash (plus inter-map transit distance for cross-level expeditions). Nearby stashes take ~1–3 real minutes; distant stashes scale proportionally.
- **Dynamic Regional Sweep TSP Routing**: Calculates exact nearest-neighbor path between all marked stashes on the map, plus round-trip travel to/from the settlement hub.

### ⏱️ Smooth Real-Time Timer Synchronization
- **Dual-Clock Tracking (`time_global` + Game Time)**: Expedition progress bars and remaining time trackers now update smoothly in real time every second while seamlessly advancing when sleeping or waiting in-game, matching the behavior of workshop job timers.

## v1.1.3 — Pre-Dispatch Duration Display in Stash Menu

### ⏱️ Estimated Duration Preview Before Dispatch
- **Context Menu Duration Preview**: Added real-time duration estimates directly to the PDA map right-click menu items before clicking dispatch:
  - Single Stash: `Dispatch Scavenger: [Name] ([Camp] [T#] - Est. X mins)`
  - Regional Sweep: `Sweep All [Level] Stashes ([Count] Stashes): [Name] (Est. Y mins)`
- **Dynamic Calculation**: Previews dynamically factor in map distance (same map vs cross-level transit), scavenger tier reductions, and regional multi-route efficiency.

## v1.1.2 — Strict Map-Marked Stash Filtering & Real-Time Formatting Hotfix

### 🗺️ Strict Map-Marked Stash Filtering (Fixed 62 Stashes Bug)
- **Strict Visual Marker Check**: `get_level_marked_stashes` now checks `has_marked_stash_spot(id)` to guarantee only stashes with an actual visible PDA map marker (`treasure`, `treasure_unsearched`, `treasure_player`, `treasure_epic`, `treasure_unique`) are counted for Regional Sweeps. All 60+ hidden/unmarked ambient world containers are completely excluded.
- **Defined `format_expedition_real_mins`**: Fixed the nil call exception during single-stash dispatch by defining and exporting `format_expedition_real_mins` on `stalker_camp_builder`.

## v1.1.0b — Map-Marked Stash Filtering & Real-Time Expedition Display

### 🗺️ Visible Map-Marked Stashes Only
- **Filtered Out Unmarked Stashes**: Overhauled `get_level_marked_stashes` so Regional Sweep sweeps **ONLY** stashes that have an actual visible map marker on the PDA map (`treasure`, `treasure_unsearched`, `treasure_player`, `treasure_epic`, `treasure_unique`, etc.), ignoring unmarked ambient world boxes.

### ⏱️ Real-Time Expedition Time Conversion
- **Real-World Minutes Display**: Expeditions operate on in-game time (1.5 to 6 in-game hours), which is now dynamically converted to real-world minutes using `level.get_time_factor()` (typically ~6 to 18 real-world minutes).
- **PDA & Context Menu Time Tracker**: The PDA status text and map-spot context menu now display clear, intuitive real-time estimates (e.g. `8m 30s left` or `~12 mins`) instead of raw in-game hours.

## v1.1.0 — Stash Context Menu Crash Fix

### 🛠️ PDA Stash Context Menu Hotfix
- **Fixed `get_level_marked_stashes` Missing Function**: Restored `stalker_camp_builder.get_level_marked_stashes` to resolve the CTD when right-clicking on stash map spots.
- **Defensive Guarding**: Added safe fallback table initialization for `all_stashes` to prevent any nil indexing errors across different PDA map views.

## v1.0.9 — Robust Scavenger Discovery & Self-Healing Hotfix

### 🔍 Scavenger Availability & Stash Dispatch Overhaul
- **Fuzzy Job Matching**: `get_available_scavengers` now uses case-insensitive substring matching (`j:find('scav')`), recognizing all variations of scavenger jobs (`scavenge`, `scavenger`, `Scavenger`, `st_job_scavenge`, `scavenging`) across all saves and languages.
- **Stale Expedition Flag Self-Healing**: Automatically detects and clears orphan `on_expedition` flags if no active expedition exists in the expedition registry, restoring stuck scavengers to immediate availability.
- **Idle Settler Dispatch Fallback**: If no dedicated scavenger is assigned yet, idle/unassigned settlers in camp are presented as available to dispatch, automatically assigning them to the scavenger role upon launch.

## v1.0.8 — Idle Scavenger 'BEH' Station Lock & Expedition Lifecycle Hotfix

### 🎒 Idle Scavenger Station Locking & Availability
- **Dedicated Scavenger Update Branch**: Added a dedicated `scavenge` / `scavenger` job handler in `npc_on_update` so idle scavengers resting at camp are no longer treated as unassigned wanderers.
- **Native Companion 'BEH' Wait Scheme**: Idle scavengers resting in camp now automatically lock to their station (camp stash, workbench, or custom assigned position) using the native `beh` wait scheme (`npcx_beh_wait`), comfortably sitting and resting by their supplies.
- **Full Expedition Availability**: Idle scavengers are guaranteed to be recognized by `get_available_scavengers()`, allowing players to dispatch them immediately to any marked stash or regional sweep from the PDA map.
- **Expedition Lifecycle Management**: When dispatched on an expedition, scavengers cleanly switch offline while traversing the Zone. Upon return or recall, they are instantly teleported back to camp, brought online, and locked into their resting station via `BEH` wait.

## v1.0.7 — Instant 'Send Here' Teleport & Scavenger Stash Dispatch Fix

### 📍 Instant 'Send Here' Teleportation & Station Locking
- **Instant Repositioning**: Clicking "Send Here" in the PDA Survivors Tab or commanding a settler via dialogue (*"I want you to stay and work right here"*) now instantly teleports the settler to that coordinate.
- **Immediate Companion 'BEH' Wait Activation**: Once teleported, the settler immediately activates the native `beh` wait scheme, locking them firmly to that exact position just like a companion told to wait.

### 🎒 Scavenger Stash Right-Click Dispatch Overhaul
- **Comprehensive Stash Spot Recognition**: Expanded `is_stash_spot` to support all Anomaly & GAMMA stash spot types (`treasure_unsearched`, `treasure_epic`, `ui_pda2_stash_location`, `ui_pda2_actor_box`, `treasure_unique`, etc.) and all inventory box classes.
- **Job Alias Compatibility**: Updated scavenger searches to recognize both `"scavenge"` and `"scavenger"` job definitions.
- **Informative Empty State**: If the player right-clicks a stash without any free scavengers available, the context menu now displays an informative hint (*"Dispatch Scavenger (No scavengers available)"*) instead of remaining silently blank.

## v1.0.6 — Native Companion 'BEH' Workstation Anchor Scheme

### 💂 Native Companion 'BEH' Scheme Integration
- **Engine-Level Workstation Locking**: Integrated Anomaly's native companion behaviour scheme (`beh` via `scripts\beh_companion.ltx`) for all working and station-anchored settlers.
- **`npcx_beh_wait` + `rally_lvid` Activation**: When a settler arrives at their furniture or is ordered to hold position, Homestead activates the native `beh` wait state and sets `st.beh.rally_lvid` to their station vertex.
- **100% Anti-Wander Guarantee**: Because the C++ engine's native `beh` scheme controls the NPC's action planner, all ambient wandering, corpse looting, weapon scavenging, and smart terrain goal evaluators are fully blocked. The settler will hold position indefinitely at their furniture just like a companion told to "Wait here".
- **Defensive Combat & Dialogue Retained**: In the event of a camp raid, settlers seamlessly engage hostiles and defend the camp, immediately returning to their station vertex once combat concludes.

## v1.0.5 — Medic Dialogue & Treatment Options Hotfix

### 💉 Settlement Medic Dialogue Options Restored
- **Unlocked All Medical Services**: Removed restrictive health preconditions (`is_actor_healthy` / `is_actor_not_healthy`) that were previously branching to an empty dialogue phrase whenever the player had high health, hiding all healing options.
- **Full Service Menu Always Visible**: Speaking to a settlement medic now immediately presents all available medical procedures:
  - Patch wounds & stop bleeding (1,850 RU)
  - Purge radiation poisoning (1,480 RU)
  - Full medical treatment & limb restoration (3,350 RU)
  - Trade medical supplies
  - Deliver Drug-Making Kit
  - Anchor / clear station positions
- **GAMMA Body Health System (BHS) Compatibility**: Restoring treatment options ensures players with damaged limbs in GAMMA can always receive limb healing from settlement medics regardless of raw overall health percentage.

## v1.0.4 — Permanent Workstation Lock & Anti-Wander Hotfix

### 🔒 Rock-Solid Workstation Lock
- **Eliminated Cyclic Furniture Rescan Wiping**: Fixed an issue where `scan_camp_structures` ran on every NPC update tick and emptied `camp.structures = {}` every 5 seconds, causing settlers to temporarily lose sight of their assigned furniture and walk towards the hub before walking back.
- **Hysteresis Station Anchoring (2.0m entry / 3.2m break)**: Settlers who arrive at their workstation enter a firm station lock (`move.stand`, `standing`, locked animation). They will never toggle into walk/patrol mode as long as they stay within 3.2m of their station vertex.
- **Physics Collision Clearance**: Expanded furniture stand-position offsets from 0.85m to 1.25m, preventing physics mesh collision overlap between the stalker model and wide furniture (stoves, workbenches, beds, barricades) that previously pushed settlers away.
- **Disabled Ambient Evaluator Hijacking**: Working settlers now automatically disable vanilla corpse looting (`corpse_detection`), weapon scavenger routines (`gather_items`), and wounded assistance (`help_wounded`) while assigned to a job, keeping them permanently at their station.
- **Hard Station Drift Clamp**: If a working settler drifts more than 6.0m from their workstation outside of combat, they are instantly clamped and realigned back to their station vertex.

## v1.0.3 — Settler Anti-Wander & Recall System Hotfix

### 🛡️ Settler Anti-Wander Overhaul
- **Eliminated Smart Terrain Hijacking**: Completely detached settlers from vanilla smart terrain job trees (`m_smart_terrain_id = 65535`). Previously, anchoring settlers to nearby smart terrains inadvertently enrolled them into vanilla smart terrain patrol/guard jobs, constantly pulling them away from the player's camp.
- **Continuous Script Movement Authority**: Ensured `xr_motivator.script_release` is continuously maintained on every movement frame for active settlers, preventing vanilla AI logic schemes from overriding settler workstation assignments.
- **Adaptive Camp Territory Leash**: Expanded the idle wandering leash from a restrictive 10m to the full camp boundary, allowing idle settlers to freely use stoves, campfires, and beds placed across the settlement without triggering hard boundary snaps.

### 📍 Guaranteed Settler Recall (Both Buttons Restored)
- **Individual "Recall to Camp" Fix**: Removed a false-positive `is_companion` check in `teleport_settler_to_camp_level` that was silently discarding recall orders for recruited companions.
- **"Recall All Settlers" Overhaul**: `recall_all_settlers` now directly targets the currently selected settlement (or all settlements) and forces immediate client/server repositioning, movement halt (`move.stand`), and animation reset (`state_mgr -> idle`).
- **Immediate State & Path Reset**: Teleporting an online settler now resets their destination vertex, cancels any in-progress walk paths, and firmly anchors them to their assigned workstation vertex.

## v1.0.2 — Hotfix & Community Bug Fixes

### 🔴 Critical Crash Fixes
- **Recruitment Dialog Slot 4 Crash Fix**: Resolved a fatal crash `attempt to call method 'id' (a nil value)` triggered when opening recruitment dialog while having 4+ settlements (`camp_slot_4_exists` was missing speaker arguments).
- **Technician Toolkit Delivery Crash Fix**: Fixed a fatal crash `attempt to call global 'deliver_toolkit' (a nil value)` when attempting to deliver Basic, Advanced, or Expert toolkits to a settlement technician. Implemented `deliver_toolkit` handling inventory release, technician toolkit tier advancement, and settlement morale increase.
- **Nil Community Guard**: Added safe string fallback guards in `can_recruit` to prevent `bad argument #1 to 'gsub'` crashes when interacting with certain special/arena NPCs with non-standard faction data.
- **Camp Slot Name Resolution**: Fixed `get_camp_slot_text` passing entry tables to `get_camp_label`, ensuring correct settlement names are displayed in recruitment choices instead of fallback strings.
- **Dialog Speaker Safety**: Enhanced `resolve_speakers` with defensive type guards and `pcall` checks to prevent crashes when non-userdata parameters are received from engine dialog handlers.
- **Function Overwrite Deduplication**: Resolved duplicate function declarations (`is_camp_trader`, `start_camp_trader_trade`, `start_camp_medic_trade`), merging caravan trader and settler trader logic into unified handlers.

### 🟡 Chest & Inventory System Fixes
- **Water Pump Offline Container Scanning**: Added offline server-entity children scanning (`alife():object():children()`) to the water pump filter check. Water pumps now properly detect charcoal and paper filters even when containers are outside the player's active client render bubble or when the player is sleeping on another level.
- **Expanded Water Filter Container Search**: Water pump filter search now checks all settlement container types (workbenches, display counters, and custom containers) instead of restricting solely to `stash` and `fridge`.
- **Primary Deposit Chest Persistence**: Added `camp.primary_chest_id` tracking so scavengers, crafters, water pumps, and repairers deposit goods into a consistent primary chest rather than scattering items across disparate containers.

### 🟠 Settler Wall-Teleport & Collision Trap Fix
- **Hub-Center Relative Workstation Positioning**: Overhauled the furniture stand-position algorithm in `move_to_job_furniture`. When workbenches or workstations are placed flush against walls, the search now selects the accessible vertex closest to the settlement hub center (the open room side) rather than closest to the NPC's current position, preventing settlers from teleporting behind benches and getting trapped in wall gaps.

### 🟣 Rival Outpost Underground Spawning Fix
- **Bounded Vertical Snapping**: `snap_rival_camps_to_ground` and `get_close_ground_y` now enforce strict vertical delta clamping (max 3.0m–3.5m) relative to surface smart terrains, preventing chests and structures from snapping to subterranean basement rooms or underground lab nodes.
- **Dynamic Tier Upgrade Snapping**: When rival outposts upgrade to Tier 2 or Tier 3 while the player is on a different level, `camp.snapped` is properly reset so new structures are realigned to the ground upon player entry.


### 🛡️ Settler Anti-Disappearance & Complete Recall Fix
- **Eliminated Engine Unregister Purge**: Fixed a critical issue where routine engine/level transition unregisters mistakenly purged living settlers from `camp.survivors`. Settlers are now permanently preserved.
- **Auto-Restoration of Missing Entities**: If the engine simulation garbage collector ever drops an offline settler's server entity, Homestead automatically detects and restores them using their persisted character profile (name, section, visual, community, job, XP) at their camp hub.
- **Fixed "Recall All Settlers"**: Resolved a bug where `recall_all_settlers` skipped all settlers with the scavenger job. Recall now works for all non-expedition settlers across every settlement.

### 📻 Scavenger System Overhaul: Radio Chatter, Loot Receipts & Regional Sweeps
- **Mid-Mission Atmospheric Radio Chatter (Feature 1)**: Scavengers broadcast milestone radio updates to the player's PDA at 25% (sector crossing), 50% (stash coordinates confirmed & packing haul), and 75% (inbound return leg with loot).
- **Post-Expedition Detailed Loot Receipts (Feature 2)**: Completing an expedition delivers a comprehensive PDA receipt detailing target stashes, items recovered, bonus salvage from ambushes, and XP gains with tier progression.
- **Autonomous Regional Sweep (Feature 5)**: Right-clicking any stash on a map with multiple marked stashes provides an option to order a `"Sweep All [Level] Stashes"`. The scavenger autonomously routes through and plunders every unvisited secret stash on that map in a single expedition!

### 📊 Real-Time Scavenger Expedition Progress Tracking
- **Live Roster Progress**: The PDA Survivors roster dynamically displays active expedition progress and target locations in real-time (e.g. `Vanya (Scavenging: Dark Valley 45%)`).
- **Comprehensive Expedition Details**: Selecting an on-mission scavenger in the PDA reveals detailed transit metrics: destination level, percent completed, and exact remaining travel time countdown (e.g. `Job: Scavenger: Expedition to Dark Valley (45% - 1h 20m remaining)`).
- **PDA Map Spot Live Tracking & Recall**: Right-clicking an active expedition stash on the PDA world map displays live transit progress and gives an instant `"Recall Scavenger"` option to abort the run and return to base.

### 🗺️ PDA Map Stash Right-Click Scavenger Dispatch Overhaul
- **Dedicated Specific Scavenger Selection**: Right-clicking any discovered secret stash on the PDA world map now displays distinct options for each available scavenger by name and base location (e.g. `"Dispatch Scavenger: Vanya (Cordon Farm [T2])"`).
- **Availability Guard**: The context menu option only appears when you actually have idle scavengers in your settlements (hiding clutter if no scavengers are assigned or available).
- **Direct Callback Hook**: Guaranteed execution of `map_spot_menu_add_property` and `map_spot_menu_property_clicked` callbacks for all stash marker types.

### 💥 Fatal Error `squad:alive()` Method Crash Fix
- **Error**: Resolved fatal crash `attempt to call method 'alive' (a nil value)` in `stalker_camp_builder_rivals.script:1796` (`update_active_convoys`) and line 1990 (`check_sos_rescue_reward`).
- **Fix**: Replaced invalid `:alive()` calls on `cse_alife_online_offline_group` squad objects with safe `is_squad_alive(squad)` helper validating `squad:npc_count() > 0` and member iterators wrapped in `pcall`.

### 🗺️ Story-Aware Regional Faction Spawning (Monolith & Scorcher Fix)
- **Regional Faction Boundaries**: Fixed rival camp spawning and offline territory captures disregarding geographical territories (e.g. Monolith spawning in Cordon).
- **Brain Scorcher Story Check**: Monolith forces are now strictly locked to Northern territories (`Radar`, `Red Forest`, `Limansk`, `Hospital`, `Pripyat`, `CNPP`, `Generators`). They can only push into central contested areas (`Army Warehouses`, `Jupiter`, `Zaton`) after the Brain Scorcher is deactivated (`bar_deactivate_radar_done`).
- **Level-Constrained Takeovers**: Offline camp capturing (`get_enemy_faction_for`) now strictly restricts victorious factions to those authentic to that specific level.

### 🛡️ Territory & Faction-Safe Settler Assignment System
- **Hostile Territory Assignment Blocker**: Settlers can no longer be recruited or transferred to camps located in territories controlled by factions hostile to them (e.g. assigning Freedom stalkers to a camp in Duty-controlled Rostok, or Duty stalkers to Freedom-controlled Army Warehouses) where local AI would execute them on sight.
- **Intra-Camp Faction Compatibility**: Validates faction relations between incoming settlers and existing residents before recruitment or transfer, preventing hostile factions from being housed together.
- **Dynamic Recruitment Dialog Filtering**: The dialogue options when recruiting NPCs now automatically filter out hostile territories and camps with incompatible residents.

## v1.0.0 — Official Full Release

### 🛠️ Weapon Parts Overhaul (WPO) & Native Vanilla Repair Screen Integration
- **100% Native Vanilla Repair UI Hook**: Hooked directly into `inventory_upgrades.how_much_repair` and `effect_repair_item`. Asking your settlement technician to repair gear opens the standard in-game Anomaly/GAMMA Repair GUI right at your base.
- **Two-Page Technician Dialogue (Dedicated Repair & Trade Sub-Screen)**: Speaking with your settlement technician opens a clean second service screen presenting dedicated choices:
    - **🔧 Modify & Repair Equipment**: Opens the native Anomaly/GAMMA Repair & Upgrade interface.
    - **📦 Spare Parts & Hardware Barter**: Opens the technician trading shop.
    - **🧰 Toolkit Deliveries (Tier 1-3)**: Hand in Basic, Advanced, or Expert toolkits for upgrade unlocks.
    - **🚪 Never Mind**: Closes dialogue cleanly.
- **Dynamic Work-Scaled WPO Pricing**:
  - Automatically calculates total condition deficit of the weapon body **plus every individual damaged internal WPO part** (barrel, bolt, trigger mechanism, gas tube, receiver).
  - Scaled across 4 weapon classes:
    - **Type A (Pistols / Small SMGs)**: 3–4 parts (~45 RU/pt, capped at ~25,000 RU).
    - **Type B (Shotguns / 5.45 & 5.56 Carbines)**: 4–5 parts (~95 RU/pt, capped at ~70,000 RU).
    - **Type C (Battle Rifles / 7.62 / 9x39 / SVD)**: 5–6 parts (~175 RU/pt, capped at ~135,000 RU).
    - **Type D (Heavy / Anti-Materiel / Gauss / PKM / .338)**: Scaled with a hard ceiling of **200,000 RU**.
- **Complete WPO Parts Minting & C++ Engine Unjamming**:
  - Paying for repair restores the weapon body AND all internal WPO parts to **100% factory mint condition**.
  - Explicitly clears C++ engine misfire states (`wpn:cast_Weapon():SetMisfire(false)`) and updates dual-key SE storage (`(id, nil, "parts")` & `(id, name, "parts")`), eliminating lingering jam animations and NPC interaction lockouts.
- **Active Weapon Watchdog**: Automatically monitors equipped weapons on draw and clears legacy misfire flags on any pristine (>= 99%) weapon (throttled to 500ms for zero CPU overhead).
- **Toolkit Progression**: Deliver Basic (`toolkit_1`), Advanced (`toolkit_2`), and Expert (`toolkit_3`) toolkits to unlock Tier 1–3 equipment upgrades and permanent repair speed buffs.
- **Firm Workstation & Furniture Anchoring (Station Lock System)**:
  - Tightened precision arrival threshold to **1.35m**, keeping settlers firmly in front of their assigned workstations.
  - Active workstation working animations:
    - **🔧 Technicians / Repair**: Active tool tinkering, repair, and workbench tuning (`repair`, `dynamo`, `bar_stand`).
    - **🍳 Cooks**: Pot and stove tending (`cooking`, `bar_stand`, `wait_na`).
    - **💉 Medics**: Medical kit preparation and supply diagnostics (`probe`, `dynamo`, `wait_na`).
    - **🔨 Crafters**: Workbench assembly (`dynamo`, `bar_stand`, `wait_na`).
    - **🛡️ Guards**: Perimeter watch (`guard`, `threat_na`, `wait_na`).
    - **⚡ Electricians**: Power grid inspection (`probe`, `dynamo`, `wait_na`).
  - **In-Game Position Commands**: Talk to any settler to command *"Hold this position as your station."* (anchors them to your exact coordinates) or *"Resume standard workstation duties."*
- **Passive Storage Repairs**: Technicians gradually repair damaged weapons and armor stored in camp chests over time.

### 🏥 Settlement Medic & Multi-Option Diagnostic Triage System
- **Direct Multi-Option Triage Architecture**: Rebuilt `camp_medic_dialog` matching vanilla Anomaly's `dm_medic_general` 1:1, presenting clear treatment and service choices:
  - **🩹 Patch Wounds & Bleeding (1,850 RU)**: Restores health, stamina, stops bleeding, heals Body Health System (BHS) limbs, and triggers medkit injection animations.
  - **☢️ Cure Radiation Poisoning (1,480 RU)**: Purges all radiation down to 0 mSv with anti-rad injection effects.
  - **💉 Complete Medical Overhaul (3,350 RU)**: Comprehensive physical and radiological restoration.
  - **📦 Medical Supply Barter**: Opens dedicated pharmaceutical trading shop.
  - **🧪 Drug-Making Kit Delivery**: Hand in pharmaceutical kits for base upgrades.
  - **🩺 Peak Condition Check**: Confirms peak physical health when 0 medical attention is needed.
- **Crash & Black Screen Resolution**: Resolved C++ call stack overflow crash / black screen hang when speaking with settlement medics by replacing recursive forwarders with standalone non-recursive evaluation routines.

### 🚀 Major Performance & FPS Optimization (Eliminated Lag)
- **Eliminated 65k Server Registry Scan Spams**: Removed forced `scan_camp_structures(my_hub_id, true)` calls from the settler AI pathfinding loop.
- **Strict 5,000ms Scan Cooldown**: Implemented a hard throttle on full structure registry scans per hub, preventing high-frequency alife object iterations.
- **One-Time AI Motivator Release**: Optimized `xr_motivator.script_release` to run only once upon settler registration (`if not camp_npc_released[npc_id]`), removing repetitive frame-by-frame `pcall` overhead.
- **Active Weapon Watchdog Throttling**: Throttled weapon misfire watchdog check in `actor_on_update` from running frame-by-frame to once every 500ms.
- **Settler Goodwill Throttle**: Enforced a 15,000ms cooldown on cross-faction camp goodwill refresh loops.

### ⚡ Synchronous GUI Transitions & Dialogue Overhaul
- **Native Synchronous Engine Transitions**: Replaced asynchronous timers with native engine GUI transitions (`dialogs.hide_hud_inventory()` followed by `n:start_upgrade(db.actor)` and `n:start_trade(db.actor)`), preventing dialogue from closing prematurely before windows open.
- **Universal Recruitment & Clean Dialogue**: Removed custom dialogue overhaul lines for a clean, immersive vanilla experience. Fixed bidirectional speaker resolution (`resolve_speakers`) so recruitment is universally available across all friendly/neutral stalkers in the Zone.

### 📦 Smart Utilities, Auto-Sort & Infrastructure
- **1-Click Smart Auto-Sort**: Automatically routes items from player inventory directly to their designated settlement stations:
  - Raw meats -> Cooking Stoves & Ovens
  - Gunpowder, lead & scrap -> Crafter Workbenches
  - Damaged weapons & armor -> Technician Repair Tables
  - Medical drugs & stims -> Clinic Storage
  - Clean water, rations & ammo boxes -> Settlement Main Vault!
- **Automated Water Pumps**: Place Water Pumps, Sinks, or Metal Barrels to generate clean mineral water every 6 in-game hours (consuming charcoal/paper filters).
- **Old Fridge Food Preservation**: Restores +25% freshness to all stored food and raw mutant meat every 12 hours, completely eliminating food spoilage.
- **Settlement Power Grid**: Placing a Generator establishes an active electrical grid, automatically powering night streetlights (20:00 to 06:00), granting +15 camp morale, and overcharging automated turrets (+25% acquisition speed, +15% fire rate).
- **Cook Hospitality Feasts**: Automated cooking (every 5 mins) and 4-hour settlement hospitality buffs (+10kg carry capacity, +15% stamina regen, passive bleed resistance).

### 🗺️ Scavenger Stash Expeditions & Remote Management
- **Zone-Wide Stash Expeditions**: Dispatch Scavengers from the PDA to plunder discovered secret stashes across any level of the Zone.
- **Live ETA & Distance Tracking**: Real-time transit countdown, geographical distance, and travel speed displayed in the PDA Survivors tab.
- **Loot Recovery & Ambush Combat**: Scavengers return to base and deposit all stash items + bonus scrap directly into camp storage, fighting off random enemy ambushes along the way.
- **Emergency Radio Recall**: Cancel active expeditions at any time to recall scavengers home immediately.
- **Remote Survivor Management**: View live health, equipped weapons, assigned jobs, and morale across all 8 bases from anywhere in the Zone. Reassign jobs, transfer settlers between bases, or dismiss residents remotely.

### 🛡️ Defenses, Automated Turrets & Alarm Siren System
- **Self-Contained DLTX Fortifications**: Standalone defense items including Sandbags, Wooden Walls, Metal Barricades, Automated Pistol Turrets (+15 Defense), and Alarm Siren Systems (+15 Defense).
- **Automated Pistol Turrets**: Placed defense turrets automatically engage hostile mutants and enemy squads. Crafters routinely inspect and reload turret ammo reserves.
- **75m Perimeter Threat Radar**: Guards continuously scan 75 meters around the camp, sounding Alarm Sirens and rallying all armed settlers into defensive firing lines upon detecting hostiles.

### ⚔️ Living Zone Ecology, Fast Travel & Renown
- **Dynamic Rival Outposts**: Living enemy faction encampments spawn throughout the Zone, evolving from Tier 1 (Scout Camp) -> Tier 2 (Fortified Outpost) -> Tier 3 (Regional Stronghold).
- **Post-Emission Expansion & Retaliation Raids**: Factions scramble to claim territory following Blowouts/Psi-Storms, and destroying enemy strongholds triggers revenge counter-attacks within 2-4 hours.
- **Campfire Fast Travel**: Teleport between established settlement campfires (safely disabled during Blowouts, Psi-Storms, and active combat).
- **Settlement Renown Perks**: Unlock permanent faction bonuses including Master of the Forge (-15% repair cost), Haven of the Zone (2x caravan frequency), Warlord of the Wastes (+20% settler combat resilience), and Fortress Architect (-40% raid frequency).

### 📖 Masterclass In-Game "How to Play" Encyclopedia
- **Exhaustive 10-Section PDA Field Guide**: Completely rewritten, comprehensive in-game documentation covering every mechanic, formula, job cycle, and configuration parameter.
- **High-Contrast Rich Text Formatting**: Structured with gold subheaders (`>> [Title]`), high-contrast colored bullet points (`-`), and distinct multi-color callouts (Gold, Green, Cyan, Red, Gray) with 100% clean rendering across UTF-8 (English) and Windows-1251 (Russian).
- **Full 100% English & Russian Localization Parity**: Complete translations across all 394 string table entries.

### 🧹 Engine Stability, ALAO Optimization & Bug Fixes
- **356 ALAO AST Optimizations**: Global function call caching, string search acceleration (`string_find_plain`), cached `db.actor` queries, and dead-code elimination across all 17 Lua scripts.
- **O(1) Negative Cache in `npc_on_update`**: Eliminates expensive loop scans for non-settler NPCs across the level.
- **Jittered AI Tick Throttling (150-250ms)**: Staggers non-combat settler updates, pathfinding, and animation states to eliminate frame-time stutter.
- **Distance Squared Math**: Replaced expensive square root distance math with distance squared across all proximity checks.
- **Crash Fixes & Log Hygiene**: Resolved `RefreshOverview` nil crash, fixed `pairs_`/`ipairs_` nil global errors, resolved MCM bad path warnings, fixed text input modal crash on rename, and eliminated all script errors.

## v0.9.97 — Dynamic Spawn Timing & Zone Ecology Overhaul (All 6 Timing Features)

- **1. Post-Emission / Psi-Storm Scramble**:
  - Automatically listens for Blowout and Psi-Storm completions.
  - Triggers an immediate bonus spawn roll (65% chance) when an emission ends, simulating factions rushing into the field to claim reshuffled anomalies and territory.
- **2. Fuzzy / Jittered Spawn Intervals**:
  - Randomizes spawn attempt intervals between 2.0 and 4.5 in-game hours per cycle, eliminating rigid metronome clockwork.
- **3. Day / Night Circadian Timing Bias**:
  - Factions follow realistic diurnal/nocturnal operational hours:
    - **Daylight (06:00 – 19:00)**: Duty, Military, Ecologists, and Clear Sky get boosted presence for daytime patrols and expeditions (+50%).
    - **Nighttime (21:00 – 04:00)**: Bandits, Mercenaries, and Monolith get boosted nocturnal presence for covert operations (+50%).
- **4. Dynamic Zone Density Curve (Vacuum & Crowding Flow)**:
  - When the Zone has \(\le 3\) total camps, intervals drop to 1.5–2.0 hours (50% chance) to rapidly populate the frontier.
  - When the Zone has \(\ge 8\) total camps, intervals relax to 4.0–6.0 hours (25% chance) to prevent map clutter.
- **5. Fast Retaliation Counter-Expeditions**:
  - Defeated factions queue a fast retaliation timer (2–4 hours) to deploy a counter-outpost after camp wipes.
- **6. Rank-Scaled Tension & Progression**:
  - Automatically paces spawn intervals and garrison veterancy from Rookie (slower start) to Legend (intense contested Zone).

## v0.9.96 — Dynamic Outpost Level Up Progression on Lifespan Expiry

- **Organic Level Up on Expiry (Reduced Despawn Probability)**:
  - When an outpost reaches the end of its 6–18 hour operational lifespan cycle, it rolls to **Level Up and Fortify** rather than automatically packing up:
    - **Tier 1 (Scout Camp)**: 70% chance to upgrade to **Tier 2 (Fortified Outpost)** (spawning sandbags, gas lamps, radios, pallets, and higher tier loot); 30% chance to pack up.
    - **Tier 2 (Fortified Outpost)**: 85% chance to upgrade to **Tier 3 (Regional Stronghold)** (spawning display counters, safes, weapon repair kits, and calling in master reinforcement squads); 15% chance to pack up.
    - **Tier 3 (Regional Stronghold)**: 90% chance to **Hold Position & Resupply** (receiving fresh ammo/medical supplies and extending garrison lifespan for another 8–24 in-game hours); only 10% chance to pack up.
- **Physical Migration Only on Failed Progression**:
  - The garrison squad only packs up and physically marches towards a friendly base if the outpost fails its progression/survival roll, ensuring established strongholds feel permanent and deeply rooted in the Zone.

## v0.9.95 — Precision Ground Snapping, Terrain Stability & Living Zone Ecology

- **Precision Outward Radial Ground Snapping (`get_ground_vertex_and_pos`)**:
  - Completely redesigned vertical height sampling from bottom-up (`-30 to +30`) to outward radial expansion (`0, 0.25, -0.25, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0, 3.0, -3.0...`).
  - Anchors candidate height strictly to the parent smart terrain's surface elevation (\(\pm 3.0\)m), permanently preventing camps from spawning inside subterranean cellars, sewers, or tunnels.
  - Enforced strict 8-neighbor AI-grid connectivity and maximum slope limit (\(\le 1.8^\circ\)) so camps only spawn on flat, walkable ground.
- **Faction Territorial Frontline Bias**:
  - Expanded regional faction weighting to include all Zone levels (e.g. Truck Cemetery, Darkscape, Meadow) matching authentic faction lore.
- **Physical Squad Migration on Camp Expiry**:
  - When an outpost lifespan expires (6–18 in-game hours), the resident squad releases camp restraint and physically walks across the level towards the nearest friendly base to debrief.
- **Dynamic Camp Activity & Heat Simulation**:
  - Outposts accumulate activity heat over time; high-heat strongholds have a chance to draw wandering mutant packs or trigger hostile skirmish scouts.

## v0.9.93 — MCM Debug Refresh 1–4 Random Camp Seed

- **Random 1–4 Camp Initial Seed on Debug Refresh**:
  - When refreshing rival camps via the MCM Debug action ("Respawn/Refresh Rival Camps"):
    - Cleans up and dismantles all existing rival outposts.
    - Rolls a random target count between **1 and 4** (`math.random(1, 4)`).
    - Immediately establishes that random number of camps across distinct surface levels in the Zone (1 per level).
    - Re-synchronizes all map markers immediately.
    - Sends an in-game tip: `"DEBUG: Refreshed rival camps. Spawned X dynamic outposts across the Zone (random 1-4)."`

## v0.9.92 — Underground Level Exclusion for Rival Camps

- **Complete Underground & Lab Exclusion**:
  - Implemented `is_underground_level()` filter to strictly prevent rival camps, couriers, or wilderness outposts from spawning in underground labs, bunkers, and dungeons (`l03u_agr_underground`, `l04u_labx18`, `l08u_brainlab`, `l10u_bunker`, `l12u_sarcofag`, `l12u_control_monolith`, `l13u_warlab`, `jupiter_underground`, `labx8`, etc.).
  - Underground levels are excluded from `get_all_levels_with_smarts()` and `get_smart_terrains_on_level()`.
- **Auto-Purge for Existing Underground Camps**:
  - Any legacy or existing rival camp situated on an underground map is cleanly and automatically purged and dismantled on load/tick, ensuring only authentic surface wilderness camps exist.

## v0.9.91 — Map Marker & PDA Spot Visibility Synchronization Fix

- **Continuous Map Marker Synchronization (`sync_all_camp_map_spots`)**:
  - Implemented continuous map spot verification on every loop update tick (10s) and during `actor_on_first_update` on level entry and save loads.
  - Ensures every active player settlement camp and rival/wilderness outpost always has an active, visible PDA map marker.
- **Player Settlement Camp Marker Fix**:
  - Upgraded player settlement camp markers from `ui_pda2_actor_sleep_location` (which was hidden by engine minimum zoom `scale_min="3"`) to `treasure_player` (green player base stash marker) and `green_location`, rendering player settlements immediately visible at all zoom levels.
- **Rival & Wilderness Outpost Marker Healing**:
  - Automatically re-asserts `red_location` (hostile rival outposts), `green_location` (friendly/occupied camps), `blue_location` (abandoned outposts), and mutant nest danger markers across all levels if engine transitions ever drop the serialized spot.

## v0.9.90 — Dynamic Living Zone Overhaul (All 6 Living Systems)

- **1. Camp Progression & Tier Evolution (Tiers 1 -> 2 -> 3)**:
  - Rival outposts now naturally evolve over time from basic scout camps (Tier 1) into **Fortified Outposts** (Tier 2 - 4+ hours) and **Regional Strongholds** (Tier 3 - 8+ hours).
  - Upgrading dynamically spawns sandbags, barricades, gas lamps, radios, display counters, safes, and workbenches, while stocking chests with higher tier military and scientific loot.
  - Tier 3 Strongholds call in dedicated veteran/master reinforcement squads.
- **2. Intercepted Radio Chatter & Distress Signals (SOS)**:
  - Friendly and neutral rival camps under attack broadcast emergency SOS distress calls to the player's PDA.
  - Responding to the distress call and saving the garrison awards cash rewards (3,000–5,500 RU), faction goodwill, and bonus stash supplies.
- **3. Dynamic Supply Convoys & Courier Runs**:
  - Tier 2 and Tier 3 outposts periodically dispatch 2-man supply courier squads from neighboring smart terrains on foot across the map.
  - Successfully arriving couriers deposit fresh ammo, rations, and medical kits into the camp chest; ambushed couriers drop rich supply pouches.
- **4. Surge Psy-Zombification & Mutant Nest System**:
  - Outdoor garrisons exposed to blowouts and psy-storms roll survival checks; failed checks turn the outpost into a hostile zombified base (`stalker_zombied`).
  - Outposts overrun by mutant attacks convert into active **Mutant Nests** guarded by lurking mutant packs with custom PDA map markers.
- **5. Territorial Turf Wars & Retaliation Raids**:
  - Friendly camps situated within 150m of each other dispatch mutual defense reinforcements during firefights.
  - Eliminating hostile outposts (Monolith, Mercenaries, Bandits, Military) triggers a 30% chance of a retaliatory hit squad deployed to hunt down the attackers.
- **6. Friendly Camp Hospitality & Safe Havens**:
  - Resting near campfires at friendly rival outposts grants health, stamina, and psy recovery buffs, plus safe resting zones and field trade dialogue.
- **Comprehensive MCM Integration**: Added individual toggles and sliders for all 6 dynamic systems in the MCM menu.

## v0.9.85 — 3-Hour Interval & 33% Probability Camp Spawning

- **In-Game Time Interval (Every 3 In-Game Hours)**:
  - Rival camp establishment attempts are now strictly evaluated once every **3 in-game hours** (10,800 game seconds) using game time `game.get_game_time()`.
  - Configurable in MCM under `Spawn Attempt Interval (Game Hours)` (range 1–24 hours, default: 3 hours).
- **33% Establishment Chance**:
  - Each 3-hour interval rolls a **33% probability** to establish a single new outpost somewhere in the Zone. If the roll fails (67% of the time), no camp spawns and the system waits another 3 in-game hours.
  - Over a full 24-hour in-game day, approximately 2 to 3 new camps will organically appear across the Zone while older outposts abandon or decay, creating an authentic, living rhythm.
  - Configurable in MCM under `Spawn Attempt Chance (%)` (range 5–100%, default: 33%).
- **Save State Persistence**: `last_rival_spawn_attempt_sec` is persisted across saves to maintain timer state seamlessly during save/load and sleep cycles.

## v0.9.84 — Dynamic Debug Lifecycle Reset (No Instant Mass Spawning)

- **Dynamic Debug Reset**: Refactored the MCM "Respawn/Refresh Rival Camps" debug action.
  - Instead of forcing an immediate synchronous loop that dumps all camps onto maps in a single frame, the debug action now cleanly purges and dismantles all existing rival camps and resets the dynamic lifecycle.
  - Camps now organically, dynamically, and gradually appear one by one across random Zone maps over time via the normal background simulation loop (60s intervals, 60% probability checks, 1 camp per map per scan).

## v0.9.83 — Zone-Wide Camp Distribution & Map Dispersion Fix

- **Zone-Wide Map Dispersion**: Fixed issue where rival camps were all spawned on the first 2 maps encountered in the array.
  - Enforced a hard limit of **at most 1 camp spawn per map per scan cycle** (`spawned_on_level = true -> break`), forcing the spawner to iterate and distribute camps across all 20+ maps in the Zone (Cordon, Garbage, Agroprom, Dark Valley, Darkscape, Rostok, Army Warehouses, Yantar, Dead City, Radar, Red Forest, Limansk, Zaton, Jupiter, Pripyat, Swamps, etc.).
  - Enforced a limit of **at most 1 camp per smart terrain territory**, preventing multiple rival outposts from clustering around the exact same base.
  - Adjusted default `rival_camps_per_level_max` from 8 down to **3** (MCM slider range: 1 to 8), ensuring realistic regional dispersion (0–3 outposts per map).

## v0.9.82 — Engine Net Export Crash Hotfix (`smart_terrain` intercept & `switch_offline` removal)

- **Engine Net Export Crash Fix (`CAI_Stalker::net_Export` assertion `!NET.empty()`)**:
  - Removed harmful `smart_terrain.setup_gulag_and_logic_on_spawn` monkeypatch that erroneously bypassed `xr_logic.setup_logic_on_spawn`. Bypassing this engine initialization left stalker entity network packet queues uninitialized on spawn/save load, resulting in `CAI_Stalker::net_Export` assertion failure `!NET.empty()` at `ai_stalker.cpp:862`.
  - Removed destructive `utils_obj.switch_offline` calls during `level_changing`, `actor_on_first_update`, and the scavenger completion loop. Natural engine online/offline distance culling now operates smoothly without packet invalidation.

## v0.9.81 — Living Zone Camp Lifecycle & 100% Autonomous Dynamic Garrisons

- **100% Dedicated Dynamic Squad Generation**: Rival camps never hijack or interfere with vanilla smart terrain simulation squads. Every single rival camp now dynamically generates a dedicated, authentic faction squad appropriate for the map level with its own persistent garrison duties.
- **Living Zone Ebb & Flow (No Static Maxing Out)**: Replaced instantaneous hard-cap filling with probabilistic spawn rolls (60% chance per cycle) and randomized soft capacities per map level (1 to 8 outposts). The number of active rival outposts now naturally ebbs and flows across the Zone rather than being permanently maxed out.
- **Dynamic Lifespans & Organic Abandonment**: Rival camps now have randomized lifespans (6 to 18 game hours). When time expires, garrisons naturally pack up and move on, leaving behind abandoned outposts / ruins.
- **Spontaneous Zone Skirmishes & Territory Seizures**: Active rival camps periodically experience simulated faction raids or mutant attacks. Victorious enemy factions can seize the camp, change its alignment, and station fresh defenders.
- **Abandoned Outpost Dynamics & Natural Decay**: Abandoned campsites can be discovered and claimed by fresh dynamic faction squads, or naturally decay and dismantle after 2 to 5 game hours if left unlooted, freeing up the territory for future expeditions.
- **Dismantle Cooldown Overhaul**: Reduced whole-level dismantle cooldowns from 12–24 hours down to 2–4 hours.
- **MCM Control**: Added "Spawn Attempt Chance (%)" slider (10%–100%, default: 60%).

## v0.9.80 — Dynamic & Unrestricted Rival Camps Overhaul

- **Dynamic Zone-Wide Rival Camps**: Completely removed artificial restrictions and tight 25–50m radius clamps on rival camps. Rival outposts now spawn dynamically anywhere across the map in a 25m to 250m+ radius across wilderness, hills, valleys, woods, and open terrain.
- **Dynamic Squad Generation**: If no resident squad is currently idling at a territory, the system dynamically creates an authentic faction squad appropriate for that map level (Loners, Bandits, Mercenaries, Clear Sky, Duty, Freedom, Monolith, Ecologs, Military) rather than aborting camp creation.
- **Expanded Capacity & Density**: Increased default Zone-wide rival camp cap from 10 to 25 (customizable in MCM up to 60). Raised max rival camps per map from 3 to 8 (customizable in MCM up to 15).
- **Faction Turf Skirmishes**: Reduced minimum distance between competing rival camps from 150m down to 35m, allowing rival factions to establish competing outposts in the same territory and spark dynamic wilderness battles.
- **New MCM Controls**: Added sliders for "Max Camps Per Map" (1–15) and "Min Camp Spacing" (15–200m).

## v0.9.79 — Engine Crash Hotfix (`CAI_Stalker::net_Export` / `!NET.empty()` assertion)

- **Engine Crash Fix (`CAI_Stalker::net_Export` assertion `!NET.empty()`)**: Fixed engine crash when teleporting or re-assigning online settlers and squads. Calling `switch_offline` followed immediately by `alife():teleport_object` and `switch_online` on the exact same frame cleared the client stalker's network packet queue while the entity was still bound in memory, causing an instant engine crash in `ai_stalker.cpp:862`.
- **Direct Online Repositioning**: Online stalkers on the active map are now smoothly repositioned using direct client positioning (`cl_npc:set_npc_position()`) and server entity coordinate updates, completely avoiding destructive offline/online network cycles. Offline stalkers and cross-level transfers use safe asynchronous timers.

## v0.9.78 — Stability & Pathing Hotfix (Save-Load Crash, Indoor Lag, Floating Camps, Fast Travel)

- **Save-Load Crash Fix (`teleport_settler_to_camp_level` / `actor_on_first_update`)**: Fixed game crash when loading a save with hired settlers. `actor_on_first_update` previously attempted to switch settlers on remote levels online, corrupting the X-Ray online entity queue. Remote-level settlers now safely stay offline until the player visits their map.
- **Indoor Pathing & Single-Digit FPS Fix**: Fixed extreme lag when assigning settlers to jobs inside complex structures (e.g. Skinflint's Freedom building at Military Warehouses). Throttled `camp_npc_move_to()` to set destination vertex only when changed, eliminating continuous per-frame A* path recalculations. Cached furniture stand offsets in `move_to_job_furniture` to remove per-frame vector allocations.
- **Floating Camps Anti-Roof Clamping**: Added height validation in `snap_rival_camps_to_ground` to clamp ground snapping relative to the parent smart terrain center, preventing rival camps from spawning on building roofs or floating 20ft in the air in Army Warehouses.
- **Fast Travel Safe Offset**: Fixed physics collision crashes during fast travel by teleporting the player with a safe 1.5m offset in front of the workbench via `db.actor:set_actor_position()`.

## v0.9.77 — Performance & Gameplay Overhaul (Animation Error, WPO Weapon Parts, Cooking Tiers, Raid Boundaries)

- **Performance Fix ("warm_hands" Console Error & Multi-NPC Lag)**: Eliminated massive 70–80% FPS drop when assigning multiple guards, cooks, or repairers. Removed invalid `state_mgr` animation states (`"warm_hands"`) that were failing 60 times/sec per settler, replacing them with standard engine idle states (`"sit_ass"`, `"wait_na"`).
- **GAMMA / WPO Weapon Parts Repair Fix**: Resolved weapon parts condition not updating in GAMMA. Upgraded `process_gear_repair()` to fetch the complete parts table via `item_parts.get_parts_con()`, increment all individual components (barrel, receiver, trigger, bolt) by the repair percentage, and save the updated table back via `item_parts.set_parts_con()`.
- **Mutant Meat Cooking & Tier 2/3 Overhaul**: Fixed cooking mutant meats always outputting generic "Doctor's Sausage" (`kolbasa`). Mutant meats now cook into their specific cooked meat at Tier 1 (`mutant_part_boar_chop` → `meat_boar`, `mutant_part_flesh_meat` → `meat_flesh`), seasoned/prepared meats at Tier 2 (consuming clean water/canteen), and gourmet survival rations at Tier 3 (consuming vodka). Added campfire fallback if a stove has no fuel.
- **Raid Spawn Boundary & Grace Period**: Fixed instant raid spawning on top of the workbench when establishing a camp. Added an initial 24-game-hour grace period on camp setup, and implemented a 16-ray radial search enforcing a minimum 50m spawn distance from the hub.
- **"Send Here" PDA Relocation Crash Fix**: Resolved save loading crashes caused by transferring settlers across levels. Cross-level transferred NPCs now remain safely offline until the player visits their destination level, preventing game graph corruption.
- **Recruitment Roll Cache Cooldown**: Replaced permanent recruitment refusal lockout with a 60-second cooldown, allowing players to re-attempt recruitment after improving rank or goodwill.
- **Container Stash Filtering**: Prevented scavengers, crafters, and repairers from depositing generic loot into stoves or fridges.

## v0.9.76 — Bug-Fix Mega-Patch (Offline Items, WPO Weapons, Cook FPS, Charcoal)

- **Weapon Repair Fix (GAMMA WPO)**: Resolved weapon condition 0% repair bug. Items in containers exist as server entities; `level.object_by_id()` returned `nil` for offline weapons, causing `item_parts.set_parts_con(cl_rep)` to fail. Updated repair logic to safely pass `se_rep` / item ID to `item_parts`, fully restoring weapon part conditions in GAMMA/WPO.
- **Cook & Temp-Target Animation FPS Drop Fix**: Fixed ~50% FPS drop during cooking/movement. Line 1894 in `npc_on_update()` was using the invalid animation state `"use_med"` during temp-target movement, causing state resets 60 times/sec per online settler. Replaced with valid engine state `"sit_ass"`.
- **Water Pump Charcoal Consumption Fix**: Fixed charcoal filters consuming all 3 charges in 1 water cycle. `consume_one_use()` now properly decrements offline server entity charges (`utils_item` / `se_item`), consuming exactly 1 use per 24h water generation cycle.
- **Water Pump Structure Restoration (`decor_barrel_metal`)**: Restored `decor_barrel_metal`, `placeable_barrel_metal`, and `decor_sink` as valid water pumps in `structure_type_exact`. The `parent_id == 65535` server-entity filter prevents unplaced container items from double-counting.
- **Crafter Powder Quality Sorting & Matching**: Upgraded `process_ammo_crafting()` to sort found gunpowders by tier (`powder_1` < `powder_2` < `powder_3`) and consume the lowest tier first. Offline gunpowder section names are now safely read from `se_item:section_name()`.
- **Cook Tier 2/3 Meal Production & Campfire Tip**: Upgraded `get_cooked_version()` to produce higher-tier food (`conserva`, `kolbasa`, `bread`) when `cook_output_tier` is set to Tier 2/3. Corrected PDA tips to state "at the campfire" when no metal stove is present.
- **Survivor XP Farming Fix**: Gated survivor XP awards behind job success return flags (`did_work == true`). Settlers assigned to repair, craft, or cook no longer gain XP or level up when no items are available to process.

## v0.9.75 — Russian XML Syntax Fix (xrXMLParser Crash)

- **Russian XML Syntax Fix**: Fixed game-launch / new-game crash `xrXMLParser.cpp:139 (CXml::Load errDescr:Error reading end tag)` in `text\rus\ui_st_stalker_camp_builder.xml`. Removed an orphan `</string>` closing tag at line 414 and escaped raw ampersands (`&amp;`). Both English and Russian XML text files now pass strict XML parser validation with 100% syntax compliance. Thanks to user3255 on ModDB for providing the exact stack trace.

## v0.9.74 — Gunpowder Matching & Turret Ammo Prioritization

- **Gunpowder-to-Ammo Category Matching**: Upgraded `process_ammo_crafting()` to match input gunpowder quality to ammo output caliber pools. Pistol/shotgun powders now craft handgun/shotgun rounds, rifle powders craft intermediate rifle rounds, and heavy powders craft sniper/AP rounds. Prevents early-game balance breaks where pistol powder could craft high-caliber rifle rounds or heavy powder was wasted on 9x18mm.
- **Turret Ammo Prioritization (MCM)**: Added `craft_prefer_turret_ammo` MCM toggle (default ON). When enabled and camp auto-turrets exist, crafters prioritize producing 9x19mm and 9x18mm ammunition to keep defensive turrets continuously supplied.

## v0.9.73 — Major Performance Overhaul & Repair/Scavenger Fixes

- **FPS Drop & Console Error Root-Cause Fix**: Resolved the severe FPS drop (80%+ for guards, 15%+ for medics/repairers/crafters) and console script error spam. `npc_on_update()` was passing invalid animation state strings (`"use_med"` and `"threat_na"`) to `state_mgr`, which failed evaluation every tick and re-invoked state resets 60 times per second per settler. Replaced with clean engine idle states (`"guard"`, `"wait_na"`, `"sit_ass"`, `"warm_hands"`).
- **Scavenger Loot Container Fix**: Fixed scavenged items spawning on the floor under workbenches. `is_actual_container()` previously returned `true` for non-container props like `placeable_workshop`, causing `find_best_container()` to target workbenches instead of stashes. `is_actual_container()` now strictly validates true inventory boxes (`clsid.inventory_box` / `_stash` / `chest`) and ignores decorative props.
- **Weapon Repair & WPO Compatibility**: Overhauled `process_gear_repair()`. Weapon condition changes now update server property `se_rep.condition`, client condition `cl_rep:set_condition()`, and restore individual part condition via `item_parts.set_parts_con()` when Weapon Parts Overhaul (WPO) is installed.
- **Configurable Repair Increment (MCM)**: Added `repair_percent_per_cycle` setting to MCM (default 25%, adjustable from 5% to 100%). Prevents 1 tushonka from instantly repairing a 15% durability exosuit to 100% in a single cycle.
- **Water Pump Double-Counting Fix**: `scan_camp_structures()` now enforces `se_obj.parent_id == 65535` so spare items inside inventory chests or NPC inventories are ignored and not counted as placed world structures. Also added exact exclusions for `placeable_decor_barrel_metal` and `placeable_decor_sink`.

## v0.9.72 — Russian Translation Repair & GAMMA Water Pump Compatibility

- **Russian Text Encoding Fix**: Completely rebuilt `configs/text/rus/ui_st_stalker_camp_builder.xml` from the ground up to fix encoding corruption ("каша" / "porridge" text). All 315 text strings are now fully localized into idiomatic Russian and cleanly encoded in Windows-1251 (no BOM) for 100% X-Ray engine compatibility. Thanks to Guest on ModDB for the report.
- **GAMMA Water Pump Script Binder Stub**: Added `bind_water_pump_furniture.script` compatibility stub. In certain GAMMA builds with updated Hideout Furniture versions, the engine expects `bind_water_pump_furniture.init` for water pump placement. The stub safely delegates `init()` calls to `bind_hf_base.init`, preventing `bind_hf_base.script:46: attempt to index a nil value` crashes. Thanks to XPD254 on ModDB for the report.

## v0.9.71 — safe_distance Nil-Return Fix (Rival Patrol Crash, Round 2)

- **safe_distance Root-Cause Fix**: Fixed the actual source of a recurring "attempt to compare number with nil" crash in the rival NPC patrol logic. `safe_distance` only fell back to `math.huge` when its internal `pcall` threw an error — but if the underlying native `:distance_to()` call completed without error while returning `nil` (a real possible edge case), the function handed back a genuine `nil` from a helper every caller in this codebase trusts to always return a number. Now explicitly requires a numeric result before returning it, protecting every one of `safe_distance`'s callers at once, not just the rival patrol block. Thanks to Solas B for the crash report and Sicks0o for the initial investigation pointing at `dist_to_chest`.
- **Rival Patrol: Added Defense-in-Depth**: `npc_pos` (from `npc:position()`) now has an explicit nil guard with early-return, and `dist_to_chest` has a redundant `or math.huge` fallback at the call site as a second layer on top of the `safe_distance` fix above.

## v0.9.70 — Food Ration Tooltip & Low-Morale Map Warning Tags

- **Food Ration Consumption Clarification**: Updated MCM tooltip `ui_mcm_stalker_camp_builder_food_consumption_interval_hr_desc` in `ui_st_stalker_camp_builder.xml` to explicitly clarify that settlers consume food rations continuously (1 item per settler per 24 hours) from camp stashes even when the player is away on other maps.
- **Low-Morale PDA Map Marker Warning**: Added dynamic PDA map pin hint updates during `update_camp_jobs()`. When a camp's morale drops below 40%, its map pin hint automatically appends `[LOW MORALE: X%]`, providing instant PDA map-level visibility for camps at risk of settler desertion.

## v0.9.69 — Comprehensive Bug Fix Pass (sdsOdin Report)

- **Multi-Use Item Consumption Fix**: New `consume_one_use()` helper prevents full item deletion of multi-use items (vodka, charcoal, kerosene, gunpowder). Now correctly decrements one use via `get_remaining_uses()`/`set_remaining_uses()` and only releases the item on its last use. Fixes: water pump charcoal (3 uses consumed for 1 water), cooking fuel (all uses consumed), repair fee vodka (all 3 uses consumed), ammo crafting gunpowder.
- **Repair System Overhaul**: Condition changes now persist via `utils_stpk.get_weapon_data()`/`set_weapon_data()` netpacket writes instead of non-functional `se_rep.condition = 1.0` field assignment. Added `IsHeadgear(item)` recognition so helmets and headgear are now valid repair targets alongside weapons and outfits. Wrapped item type checks in `pcall` for dummy_item safety.
- **Turret Table Double-Counting Fix**: Added `placeable_turret_table = "decor"` to `structure_type_exact` table so turret tables are no longer misclassified as gadgets via the `"turret"` substring match. Turret tables no longer contribute +15 defense points or inflate the turret count in the PDA. Also filtered turret tables from `process_turret_maintenance()` ammo refill targeting.
- **Cooking Fuel Recognition**: Added `explo_balon_gas`, `explo_jerrycan_fuel`, and `jerrycan_fuel` to the fuel items table and added `"balon_gas"` and `"jerrycan"` substring checks. Gas balloons and gasoline canisters are now recognized as valid cooking fuel.
- **FPS Drop Fix (RefreshJobProgress)**: Removed debug `printf` console spam from `homestead_pda_actor_on_update()`. Increased auto-refresh throttle from 2s to 5s. Replaced full UI rebuild (`OnSurvivorSelected()`) with lightweight text-only update of the job progress label on the right panel. Full rebuild only occurs on manual refresh button press.
- **Promotion Typo Fix**: Added `job_display` lookup table in `award_survivor_xp()` mapping internal job IDs to display names (e.g. `"scavenge"` → `"Scavenger"`). Promotion messages now read "promoted to Skilled Scavenger" instead of "promoted to Skilled scavenge".
- **Settler Invulnerability Hardening**: `npc_on_death_callback` now checks `cfg.settler_invincible` and respawns dead settlers at their camp hub via deferred `CreateTimeEvent`, preserving their name, job, and faction. When invulnerability is off, original death removal behavior is preserved.
- **Scavenging Deposit Reliability**: Deferred `spawn_scavenged_loot()` call by 1.5 seconds via `CreateTimeEvent` after `switch_online()` to ensure camp containers are fully streamed in before items are spawned. PDA tip is now sent only after deferred spawn completes.

## v0.9.68 — Defensive Coercion for Rival NPC Patrol Wait Timer

- **Rival Patrol Timer Nil Guard**: Added unconditional defensive coercion (`p_data.wait_until = p_data.wait_until or 0`) immediately after table lookup in rival-camp NPC patrol tracking ([stalker_camp_builder.script](file:///C:/Users/hocke/.gemini/antigravity/brain/5bf60968-c259-4132-8aa1-5bb65293e90c/scratch/homestead_extracted/00_Core/gamedata/scripts/stalker_camp_builder.script)). Prevents `attempt to compare number with nil` Lua runtime error during patrol timer checks.

## v0.9.65 — Settlement & Survivor Rename Dialog Use-After-Free Crash Fix

- **Rename Dialog C++ Memory Protection**: Fixed C++ Use-After-Free crash (`0x0000000140272E7B` in `CUIWindow::OnMouseAction`) when closing or accepting Settlement & Survivor Rename dialogs (`UIRenameCamp` / `UIRenameSurvivor`). Replaced synchronous `DetachChild` calls inside button event callbacks with `Show(false)` and deferred 0.05s `CreateTimeEvent` detachment, preventing child list mutation while mouse actions are in mid-dispatch. Added double-invocation guards (`_closing`).

## v0.9.64 — Live Time Remaining Countdown for Job Status

- **Live Time Remaining Countdown**: Added formatted time-till-completion countdown in brackets (e.g., `(45% - 4m 52s)` or `(100% - Ready)`) to the survivor's job status display on the right detail panel (`survivor_job_txt`). Time remaining updates live in real time while the PDA is open.

## v0.9.63 — Single-Line Survivor List & Right-Panel Progress Layout

- **Single-Line Survivor List**: Replaced two-line survivor rows in the middle panel list box with clean, elegant single-line entries displaying only the survivor's name in gold font (`letterica18`). Completely eliminated all risk of vertical text overlap in the survivor list.
- **Right-Panel Job & Live Progress Display**: Moved the survivor's job title and live job progress percentage (e.g. `Job: Crafter (45%)`) to the right-side detail panel (`survivor_job_txt`). Real-time progress updates live on the detail panel.

## v0.9.62 — PDA Survivor Row Vertical Spacing & Top Alignment Overhaul

- **PDA List Item Vertical Spacing & Alignment**: Overhauled `SurvivorListItem` and `SettlementListItem` row layout. Increased item height to 42px (`super(42)`), switched XML vertical text alignment from center (`vert_align="c"`) to top (`vert_align="t"`), and added a 20-pixel line height offset (`y=2..20` for name, `y=22..40` for job/details) with a 3px clear empty gap. This eliminates glyph overlap between survivor names and job labels.
- **Job Assignment Detail Panel Layout**: Adjusted `survivor_name` (`y=4`, `h=20`) and `survivor_job` (`y=26`, `h=38`) vertical bounds in the right-side job assignment panel for extra clearance above job action buttons.

## v0.9.61 — XML Font Crash Fix

- **XML Font Registry Crash Fix**: Resolved engine crash `CUIXmlInit::InitFont` / `unknown font: letterica14` when opening the PDA. Replaced non-existent `letterica14` font identifier in `settlement_row_details` and `survivor_row_job` templates ([ui_stalker_camp_builder_pda.xml](file:///C:/Users/hocke/.gemini/antigravity/brain/5bf60968-c259-4132-8aa1-5bb65293e90c/scratch/homestead_extracted/01_PDATab/gamedata/configs/ui/ui_stalker_camp_builder_pda.xml)) with standard engine font `letterica16`.

## v0.9.60 — Job Furniture Teleportation for Recall Buttons

- **Job Furniture Recall Teleportation**: Updated both the global "Recall Settlers" button (Overview tab) and individual survivor "Recall" button (Survivors tab) to teleport settlers directly to their assigned job workstations/furniture (cook -> stove, crafter -> workbench, repairer -> repair bench, medic -> medstation, guard -> barricade/gadget, etc.) instead of spawning at the center camp hub marker.
- **Smart Target Resolver (`get_settler_job_target`)**: Implemented intelligent workstation resolution that checks assigned custom spots, sticky furniture assignments, and matching camp structures before falling back to hub coordinates. Forced immediate snap-teleportation upon button click regardless of current proximity.

## v0.9.59 — PDA Survivors Tab Text Overlap Fix

- **PDA Survivor List Text Alignment**: Fixed vertical text collision and overlapping between survivor names (gold text) and job labels (gray text) in the PDA Survivors tab list view. Adjusted `survivor_row_name` and `survivor_row_job` bounding boxes with explicit `Frect` window rectangles (`y=2..18` for name, `y=19..34` for job) and matched font sizing (`letterica16` / `letterica14`).
- **Survivor Job Detail Panel Layout**: Enabled `complex_mode="1"` and expanded bounding dimensions for `survivor_job` text in the right-side job assignment panel, preventing long job descriptions from overlapping with survivor names or job action buttons.

## v0.9.58 — Post-Combat Settler Job Return & State Reset Fix

- **Post-Combat Settler Workstation Return**: Resolved issue where settlers remained standing idle in place after combat ended instead of returning to their assigned job furniture. Changed combat bail-out evaluation in `npc_on_update` from checking persistent `best_danger()` memory (which stays non-nil for minutes after enemies die) to checking active `best_enemy()`. As soon as all nearby hostiles are eliminated, settlers immediately resume job movement logic.
- **State Manager Post-Combat Fast-Set Reset**: Updated `camp_npc_move_to` in `stalker_camp_builder_npc.script` to force-set `state_mgr` to `"patrol"` with `{ fast_set = true }` whenever an NPC is redirected toward their workstation. This breaks residual combat posture animation locks (`"threat"`, `"threat_fire"`, `"walk"`) so NPCs walk smoothly back to their workstations and resume working animations.

## v0.9.57 — ALAO AST Performance Pass & Codex Audit

- **ALAO AST Performance Pass**: Executed Anomaly Lua Auto Optimizer (ALAO) across all codebase scripts. Applied green-tier AST bytecode optimizations including `t[#t+1]` array append performance conversions and localized `npc_id` caching. Verified 100% syntax compliance across all 16 modules via `luac_tool`.
- **Codex Quality Scan Audit**: Ran `anomaly-codex-main` workbench static analysis. Confirmed 0 critical and 0 high-severity errors across the codebase.

## v0.9.56 — CInventoryBox Engine Iteration & Safe Callback Registration Fix

- **Settlement & Survivor Rename Dialog Crash Fix**: Fixed a C++ use-after-free engine crash (`CUIWindow::OnMouseAction` / `0x0000000140272E7B`) when closing the settlement/survivor text input rename dialogs (`UIRenameCamp` / `UIRenameSurvivor`). Updated dialog initialization to use `self:SetAutoDelete(false)` instead of `SetAutoDelete(true)`, preventing C++ `DetachChild` from prematurely deleting `this` while Lua event handlers are still executing on the stack.
- **CInventoryBox Engine Iteration Fix**: Resolved `CScriptGameObject::IterateInventoryBox non-CInventoryBox object !!!` C++ engine log errors and stack trace spam in `safe_iterate_inventory_box` and `is_actual_container`. Updated container iteration to verify engine Class ID (`clsid.inventory_box` / `clsid.inventory_box_s`) before invoking C++ inventory iteration, and fall back to server-side child scanning (`alife_object(id).children`) for non-native placeable containers.
- **Safe Callback Registration Guard**: Updated `safe_register_callback` to check `axr_main.callbacks[name]` before registering optional engine callbacks (like `actor_on_level_changing`), suppressing engine stack trace warnings when callbacks are omitted in specific engine builds.

## v0.9.55 — Rival Camp NPC 10-Meter Patrol System Overhaul

- **Rival Camp NPC Dynamic 10-Meter Patrols**: Fixed issue where NPCs at rival camps stood motionless directly on top of the blue camp hub chest. Implemented a dynamic patrol loop for rival camp members that selects accessible AI grid vertices within a 2.5m–9.5m radius of the rival camp hub. NPCs now walk smoothly between patrol points using `camp_npc_move_to`, pause for 5–12 seconds at each point playing guard/idle animations facing camp center, tether back if they stray beyond 12m, and immediately engage in combat if enemies or threats appear.

## v0.9.54 — Settler Furniture Stand Vertex & Hideout Container / Filter Fixes

- **Settler & Rival NPC Furniture Stand Vertex Offset**: Fixed issue where NPCs got stuck standing on top of furniture, beds, workbenches, stoves, and barricades. Updated `move_to_job_furniture` in `stalker_camp_builder.script` to dynamically calculate an accessible floor vertex ~1.0m adjacent to the 3D furniture model. NPCs now walk to the floor in front of the furniture and turn to face it, rather than walking onto the center of the 3D object model.
- **Hideout Furniture & Placeable Chest Container Fix**: Fixed issue where scavenger loot failed to deposit in camp chests and stashes appeared unregistered. In `is_actual_container`, replaced engine `IsInventoryBox` (which only returns true for native `clsid.inventory_box` objects) with `box_obj.iterate_inventory_box ~= nil` and expanded section pattern matchers (`box`, `stash`, `fridge`, `safe`, `chest`, `stove`, `shkaf`, `cabinet`, `wardrobe`, `counter`, `workshop`, `container`, `bag`, `backpack`, `trus`, `crate`, `locker`, `inv_`, `hf_`). This prevents player-placed Hideout Furniture stashes from being incorrectly blacklisted in `known_bad_inventory_boxes`.
- **Water Filter & Scavenger Item Filter Recognition**: Fixed issue where paper sheets placed in camp chests were reported missing by the water pump. Corrected `find_filter` in `stalker_camp_builder_jobs.script` (removed restrictive `and sec:find("prt")` clause) and expanded `defaults.water_filters` in `stalker_camp_builder.script`. All paper items (`paper`, `sheets_paper`, `paper_sheets`, `sheet_paper`, `prt_i_paper`), charcoal, and filter variants are now correctly recognized and consumed as water pump filters.

## v0.9.53 — ALAO AST Performance Optimization Pass

- **AST Performance Optimizations (ALAO Pass)**: Ran the latest Anomaly Lua Auto Optimizer (ALAO) across all codebase scripts. Applied green-tier AST bytecode optimizations including `table.insert` array append bytecode conversions (`t[#t+1]`) and local `npc_id` caching to reduce LuaJIT execution cycles and memory allocation overhead.
- **Workstation Accessible Movement & AI Pathfinder Overhaul**: Ensured continuous per-frame destination vertex assignment in `camp_npc_move_to` without throttles, wrapped workstation destinations in `utils_obj.send_to_nearest_accessible_vertex`, and enforced workstation `look_position` facing vectors.

- **Safe Distance Vector Check & Log Spam Fix**: Resolved issue where `safe_position` returned function wrappers for online objects. This caused `safe_distance` to return `inf`, creating high-frequency log spam (`dist=inf`) 60 times a second and causing `npc_on_update` to return early before job movement loops ran. `safe_position` now verifies `type(pos) == "userdata"`, restoring accurate distance calculations and eliminating log spam.
- **Perform_destroy Engine Crash Fix**: Resolved native C++ `xrServer::Perform_destroy` engine crash (`child registered but not found [63232]`). `_G.alife_release` now explicitly sets `child.parent_id = 65535` before releasing items or container contents, unlinking child references from parent entities before server destruction.
- **Continuous Workstation Destination Setting**: Fixed issue where settlers wandered off. `camp_npc_move_to` now continuously sets the destination vertex every update tick. This prevents S.T.A.L.K.E.R. Anomaly's C++ engine stalker movement manager from dropping path goals and defaulting to wandering when logic release is active.
- **Accessible Vertex Resolution**: Wrapped all workstation target position calculations in `utils_obj.send_to_nearest_accessible_vertex`. This ensures that destination vertices are accessible on the level AI graph, preventing the C++ engine pathfinder from rejecting blocked furniture center vertices.
- **Workstation Facing Vectors**: Updated `move_to_job_furniture` to resolve assigned furniture IDs and pass target positions into `state_mgr.set_state` via `look_position`. Settlers now turn and directly face their assigned workstation when performing working animation loops.
- **Permanent Settler ALife Squad Pinning**: Settler home squads are assigned `get_script_target = function(self) return self.id end`, registered via `assign_smart`, and given an active `stay_time`. This pins squads at the settlement, preventing ALife simulation sweeps from reassigning or purging settler squads during offline ticks, level transitions, sleeping, or fast travel.
- **Expanded In-Game PDA Guide**: Added full documentation for the Electrician job, Camp Specializations (+50% bonuses), PDA Fast Travel, Bed Rest bonuses, and complete MCM settings to the in-game PDA How to Play tab.

## v0.9.49 — Companion Handoff Crash Fix & Electrician Job Corrections

- **Companion Handoff Orphaned-Squad Crash Fix**: `recruit_back_deferred` (the "bring a settler along as a companion" feature) was manually creating a dedicated squad, setting `scripted_target = "actor"` on it, and registering it into `axr_companions.companion_squads` *before* calling `axr_companions.add_to_actor_squad(online_npc)` — the real vanilla API, which moves the NPC into the actor's own squad. That left the manually-created squad behind as an empty, orphaned, still-`"actor"`-targeted squad still tracked by `SIMBOARD.squads`. When GAMMA's own simulation later processed that squad, it had no NPC left to resolve a target for, causing a confirmed native FATAL crash (`sim_squad_scripted.script`'s `PATCH_get_script_target`: `attempt to index global 'obj' (a nil value)`) every time a settler was sent back as a companion, independent of save state. Removed the redundant manual squad setup; `axr_companions.add_to_actor_squad` is now trusted to handle squad assignment on its own. The pre-handoff `unregister_member` step (to free the settler from their camp home squad) is retained.
- **Electrician Job Statue Animation Fix**: Removed `"wait_na"` (a neutral standing-idle animation) from the electrician job's animation pool. As with the identical fix previously applied to cook/craft/repair/medic, `move_to_job_furniture`'s "already idling" check locks a settler into whichever animation they first land on — a settler who rolled `wait_na` on arrival was stuck in a permanently frozen pose, never transitioning to the real working animation.
- **Electrician Job Missing Fallback Flag**: The electrician's `move_to_job_furniture` call was missing the `is_fallback` argument that every other job forwards from `get_job_target_lvid`, causing the hub-offset positioning math to always run even when the job had fallen back to a generic position where that offset doesn't apply.
- **Electrician Job Free Recharge Exploit Fix**: `process_electrician_job` was recharging every lamp in camp to full condition **unconditionally**, regardless of whether a battery was actually found and consumed — the `consumed` result only affected the wording of the success message, never whether the recharge itself happened. Electricians now require and consume a battery before any lamp condition is restored, matching the input-required-for-output pattern every other job enforces.

## v0.9.48 — Rival Camp Ground Snapping & Height Alignment

- **Rival Camp Terrain & Ground Snapping**: Resolved issue where rival camps and decorations (walls, beds, tables) would float in the air. Implemented `stalker_camp_builder.get_ground_vertex_and_pos(pos)` which performs vertical Y-height searches and horizontal spiral scans when candidate positions or offline smart terrains inherit floating height values (`smart.position.y`).
- **Slope & Ring Sampling Ground Alignment**: Updated `is_position_flat_enough` to resolve ground Y heights for all sample points independently. This prevents flat terrain candidate locations from false-failing slope checks when initial `pos.y` values are ungrounded.
- **Online Client Object Re-streaming**: Added `utils_obj.switch_offline` / `switch_online` refresh triggers during `snap_rival_camps_to_ground()`. When an online chest or decoration object has its position adjusted to ground level, the engine now immediately re-streams the 3D visual mesh at the new snapped coordinates instead of leaving the client object floating.

## v0.9.47 — Settler Leash & Immortality + Crafter Workshop Fixes

- **Settler Combat Leash Enforcement**: Moved camp boundary leash checks in `npc_on_update` to evaluate *before* the combat bail-out. Previously, when a settler detected an enemy or danger, the update function returned immediately, completely bypassing distance limits and allowing settlers to chase hostiles across the map. Settlers exceeding 2× boundary distance are now hard-teleported back to the camp hub, while settlers beyond boundary distance are redirected back to camp before re-engaging enemies.
- **True Settler Immortality & Hit Callback**: Registered a new `npc_on_hit_callback` in `on_game_start()` that heals invincible settlers (`settler_invincible` MCM option) to full health immediately upon taking damage, preventing single-frame lethal burst damage (e.g. snipers, grenades, point-blank shotguns) from killing them. Registered `npc_on_death_callback` for immediate survivor state cleanup on death.
- **Workshop Container Validation Fix**: Added `placeable_workshop` and substring `workshop` to `is_actual_container` in `stalker_camp_builder.script`. In v0.9.45, `placeable_workshop` was rejected by section name filtering, causing `is_actual_container` to blacklist the camp workbench and abort crafting jobs. Crafters now properly recognize and pull materials from the workshop.

## v0.9.46 — Caravan Trade Dialog Fix

- **Caravan Trade Instant-Close Fix**: Removed a redundant `dialogs.break_dialog` XML action from the `camp_trader_dialog` definition in `modxml_stalker_camp_builder.script`. The `start_camp_trader_trade` function already schedules `break_dialog` via a deferred `CreateTimeEvent` (0.1s delay) to allow the trade UI to open first. The XML-level action fired synchronously on the same frame, tearing down the dialog and trade window before it could render — causing the trade to appear to "close immediately" on click.

## v0.9.45 — Crafter & Settler Consumption Bug Fixes

- **Crafter Job & Workshop Container Fixes**: Added a robust `is_actual_container(box_id)` helper function to `stalker_camp_builder.script` that dynamically verifies container validity. Updated scavenger, crafter, gear repair, medical, and turret maintenance routines to check container validity and fallback to the camp chest (`camp_box_id`) when the preferred workbench or station resolves to a non-container structure (such as the camp hub). Material search loops now search both preferred and fallback chests, resolving the bug where craft jobs failed to find materials placed in the camp workbench.
- **Settler Consumption Improvements**: Expanded `FOOD_SECTIONS` and `is_food_section` in `stalker_camp_builder_jobs.script` to support drinking and eating of all canteens (`bottle_metal`), flasks (`flask`), mineral water, canned food, rations, and cooked mutant meat variants (including GAMMA quality tiers `_a` and `_b` using a wildcard `meat_` prefix).

## v0.9.44 — xr_effects `task_info` Indexing Crash Fix

- **xr_effects Safety Monkey-Patch**: Added dynamic runtime monkey-patches to `xr_effects.script` inside `on_game_start()`. This safely wraps 5 vanilla Anomaly/GAMMA storyline/faction relations functions (`drx_sl_store_task_giver`, `drx_sl_unregister_task_giver`, `drx_sl_unregister_hostage_giver`, `inc_goodwill_by_tasker_id`, `dec_goodwill_by_tasker_id`) to verify if the task's entry in `task_info` still exists before indexing it (e.g. `task_info[task_id].task_giver_id`). This completely resolves the fatal crash `attempt to index a nil value` in `xr_effects.script:1189` that occurs when a task is completed, failed, or cancelled, and its unregistration is subsequently triggered after it is already cleared from the active task manager list.

## v0.9.43 — Level Transition & Disconnect Crash Fix

- **Engine Unregister Safety Net**: Added an absolute safety net to the global `server_entity_on_unregister` callback in `stalker_camp_builder.script`. During level transitions, quickloads, or disconnecting/exiting to the main menu (when the game session is being torn down), any child items (items nested inside containers, NPCs, or corpses where `parent_id ~= 65535`) will have their `parent_id` cleared to `65535` right before unregistration. This prevents the native engine call `xrServer::Perform_destroy` from asserting on a parent-child mismatch (`child registered but not found`) during mass unregistration, resolving the exit-to-menu crash.
- **Teardown Tracking**: Registered for `actor_on_net_destroy` and `actor_on_first_update` to reliably track when the game session is disconnecting/unloading and reset it on level entry.

## v0.9.42 — ALAO Performance Optimizations

- **Auto-Optimizer Integration**: Ran the Anomaly Lua Auto Optimizer (ALAO) tool across the entire codebase to apply 424 safe green-tier AST-level optimizations, reducing CPU cycles and garbage collection overhead:
  - **Table Insertion**: Replaced all dynamic `table.insert(t, v)` append operations with direct index assignments `t[#t+1] = v`, which compiles to high-performance LuaJIT bytecodes (`TSET` and `LEN`) and avoids C-call overhead.
  - **Singleton Caching**: Cached frequently called singletons and global references (like `db.actor`, `alife()`, `device()`, `pairs`, `ipairs`, `string.format`, and `tostring`) into local variables at function entry points. This avoids repetitive hash-table lookups on the global table `_G` in hot loops and per-frame update cycles.
  - **Pow Optimization**: Transformed power operations (such as squaring) into direct multiplication (e.g. `x*x`) to use the single MUL instruction.

## v0.9.41 — Memory Leak & Global Variable Audit Fixes

- **Accidental Globals Fixed**: Cleaned up critical accidental global variables that leaked memory and corrupted logic:
  - Fixed `h` in `bind_pistol_turret.script`: It was accidentally assigning to a global `h` variable inside `get_target_aim_pos`, caching the first fallback height forever across all class types (mutants and stalkers).
  - Fixed `mpos` in `bind_pistol_turret.script`: Declared it as a local variable inside `turret_target_visible` to prevent creating persistent global references to the last turret's position vector.
  - Fixed `GUI` in `ui_pistol_turret.script`: Declared the singleton instance variable as local to prevent polluting the global `_G.GUI` namespace and causing clashes with other mods.
- **UI Singleton Leak Fix**: Modified `SettlementManagerPDA:__finalize()` in `ui_stalker_camp_builder_pda.script` to clear the `SINGLETON` reference (`SINGLETON = nil`) on close. This allows the Lua garbage collector to reclaim all resources allocated by the closed PDA Settlement Tab window.

## v0.9.40 — Safe Nest-Release & Double-Release Protection

- **Synchronous Child Release**: Changed the release of nested items (items inside containers, NPCs, or corpses where `parent_id ~= 65535`) from deferred/queued (`alife():release(se, true)`) to synchronous (`alife():release(se, false)`) in our global `alife_release` override. This ensures the server-side parent-child entity structure is updated immediately in the same frame, preventing client-server state desynchronization and the subsequent `xrServer::Perform_destroy: child registered but not found` crash.
- **Double-Release Guard**: Integrated a frame-based double-release guard using `device().frame` inside the global `alife_release` override. This checks and blocks duplicate releases of the same object ID in the same frame, preventing crash assertions triggered by concurrent background jobs (e.g. multiple settlers eating the same food item in the same tick).
- **Turret Ammo Iteration Refactor**: Refactored the turret ammo refilling loop in `stalker_camp_builder_jobs.script` to collect spent ammo box IDs and release them *after* the `safe_iterate_inventory_box` iteration loop completes, rather than during iteration, preventing runtime script iteration crashes.

## v0.9.39 — Container Release Crash Fix (`Perform_destroy`)

- **Empty Container Contents Before Release**: Fixed a fatal engine crash `xrServer::Perform_destroy: child registered but not found [ID]` that occurs when the engine attempts to release a player-placed container (like a camp chest or fridge) or a rival camp loot chest containing items.
  - **Global `alife_release` Interceptor**: Homestead now intercepts calls to `_G.alife_release` and checks if the targeted object is a container (by checking class IDs for `clsid.inventory_box` or name substrings like `stash`, `box`, `chest`, `fridge`, `safe`, `cabinet`).
  - **Safe Child Cleanup**: Before the container itself is released, the script automatically queries the alife registry to find all child items containing `parent_id == container.id` and releases them first. This prevents the engine's internal parent-child structures from getting out of sync during destruction and triggering a native crash.

## v0.9.38 — ZCP `obj` Crash Fix (Runtime Monkey-Patch)

- **ZCP `get_script_target` Crash Fix**: Fixed the fatal crash `sim_squad_scripted.script:139: attempt to index global 'obj' (a nil value)` caused by a typo in ZCP 1.4's `get_script_target()` method. The ZCP code references the undefined global variable `obj` instead of the local `se_target` when checking a numeric squad target's class ID. This crashes any squad whose `scripted_target` resolves to a valid alife object (squads, smart terrains, etc.).
  - **Runtime Monkey-Patch**: Rather than shipping a full override of ZCP's `sim_squad_scripted.script` (which would break on ZCP updates), Homestead now installs a monkey-patch on the `sim_squad_scripted` class prototype during `on_game_start()`. The patch wraps the original method in a `pcall`; on crash, it falls back to a corrected reimplementation that uses `se_target` instead of `obj`.
  - **Compatibility**: The patch is a no-op if ZCP is not installed or the bug has been fixed upstream. It preserves the full call chain including Useful Idiots' own wrapper.

## v0.9.37 — Companion Squad Orphan Hardening

- **Orphaned Companion Squad Cleanup**: Supplementary hardening to prevent and clean up empty companion squads that can accumulate after settlers are recruited back from camps.
  - **Camp Handoff Refactor**: Modified companion recruitment (`recruit_back_deferred` in `stalker_camp_builder_recruit.script`) to unregister the settler from the camp's home squad *before* creating a fresh, dedicated companion squad. This prevents vanilla/GAMMA companion-splitting scripts from evacuating the camp's home squad and leaving it empty and targeted at the actor.
  - **Extended Load-Time Sweep**: Extended `heal_corrupted_scripted_targets()` to safely identify, clean, and unregister zero-member (orphaned) actor-targeted companion squads from both the alife registry (`SIMBOARD`) and `companion_squads`, repairing existing affected saves automatically on load.

## v0.9.28 — PDA Guide Formatting Improvements

- **PDA How to Play / Guide Page Overhaul**: Improved guide readability by rewriting it from a monolithic text block into structured, visually distinct guide sections.
  - Added new XML layout templates for section headers (gold text on dark background bars), slightly indented body text boxes with bottom padding, and clean horizontal separator lines.
  - Refactored the UI script to build sections programmatically from individual translation keys instead of one giant string.
  - Split `st_pda_how_to_play_text` into 16 clean section pairs (`st_guide_s*` header/body) in both English and Russian translation tables, guaranteeing safe visual fallback for all language settings.

## v0.9.26 — PDA Tab Overlay Fix

- **PDA Pages Overlayed Bug Fixed**: All 4 Settlement tab pages (Overview / Survivors / Rivals / Guide) were rendering on top of each other simultaneously. Root cause: the v0.9.25 nil guards on `SetTab` and `Reset` bailed out entirely when `stalker_camp_builder` was nil, leaving all panels in their default visible state — and since all 4 panels sit at the same screen coordinates (406,108), the result was a jumbled overlay of every page at once. Fixed by:
  - **`InitControls` now hides 3 of 4 panels immediately after construction** — only `overview_panel` starts visible. This guarantees a clean first paint even before `SetTab` runs.
  - **`SetTab` no longer bails when `stalker_camp_builder` is nil** — instead it unconditionally hides ALL panels first (clean slate), then falls back to showing only the guide panel (which has no camp data dependency).
  - **`SetTab` now hides-all-then-shows** on every call, preventing any stale visibility from a previous interrupted call.
  - **`Reset` no longer bails when `stalker_camp_builder` is nil** — it clears the list boxes, calls `SetTab` (which handles the nil case safely), then returns. Previously it bailed before reaching `SetTab`, leaving panels unmanaged.

## v0.9.18 — Settler Routing & Workshop Crowding Fix

- **Workshop Hub Excluded from Structure Scan**: The camp hub IS the placed workshop (`placeable_workshop`), but `scan_camp_structures` explicitly skipped the hub ID. This meant the workshop was never registered in `camp.structures` as a workbench — settlers with workbench-based jobs could never find it through the primary lookup and always fell back to the hub center coordinates. The hub is now included in the structures table after the scan.
- **Workshop Section Name Not Recognized as Workbench**: Added `"workshop"` to the workbench substring list so `placeable_workshop` is correctly classified as a workbench (previously only `"workbench"`, `"anvil"`, and `"forge"` were recognized).
- **Job Furniture Fallback Chains**: Every job now tries multiple sensible furniture types before resorting to an offset fallback position:
  - **Guard**: barricade → gadget (turrets, alarm systems) → perimeter offset
  - **Cook**: stove/campfire → fridge → workbench (workshop) → offset
  - **Craft**: workbench → offset
  - **Repair**: repair bench → workbench (workshop) → offset
  - **Medic**: medstation → bed (tend patients) → fridge (medical supplies) → offset
- **Larger Fallback Offset Distances**: When no matching furniture exists at all, fallback positions are now 4–8m from the hub (previously 2–5m), making it visually clear that settlers are spread out rather than crowding the workshop.
- **Idle Settler Scatter**: Unassigned settlers without a campfire, piano, or radio to hang out near are now scattered to stable positions 3–5m around the hub based on their NPC ID, instead of all standing on the workshop center.

## v0.9.17 — Assets, Spawning, PDA, Localizations, and Safety Guards

- **Spawning Coordinates Correction**: Fixed a critical engine bug where spawning items into online containers with `vector(), 0, 0` coordinates would cause them to spawn at `(0, 0, 0)` of the level. Now, items are spawned using the container's actual coordinates, resolving the issue where generated loot (scavenged, cooked, filtered water, medicine, ammo) and transferred items never appeared.
- **PDA Renaming Dialog Crash**: Fixed a game crash when attempting to rename a settlement or settler. Dialogue popups now correctly attach as child windows within the PDA UI container (`AttachChild`) instead of trying to spawn a top-level modal dialog (`ShowDialog`), bypassing the engine window-manager input conflict.
- **Dialogue Localizations & Camp Slot Functors**: Fully localized the dynamic camp status dialogue into Russian. Additionally, replaced static "Settlement #1..#4" choices in the recruitment dialogue with dynamic text functors that show the actual, user-configured names of the camps (e.g. "Rookie Camp", "Merc Base").
- **NPC Recruitment Dialogue Precondition Safety Guard**: Fixed an instant crash when talking to NPCs by safely guarding the `actor` parameter in the `can_recruit` precondition.
- **Repeating Recruitment Dialog Option Bug Fixed**: Previously, even after an NPC was successfully recruited to a camp, the player could still select "Would you like to join one of my settlements?" and recruit them again over and over. Added an `is_camp_survivor` check to `can_recruit` to hide the recruitment dialog for already recruited settlers.
- **Missing Medic Job Option Added**: Fixed an omission where the "Medic" job assignment option was completely missing from the camp management dialogue tree, preventing players from assigning settlers to be medics via direct dialogue.
- **Settlers Ignoring Assigned Positions & Wandering Off Fix**: Fixed a bug where settlers would walk to their assigned position/furniture but then re-acquire vanilla smart terrain jobs and walk away. Keeping the settler script-released every tick in `npc_on_update` and avoiding clearing the script release state on arrival ensures they remain under Homestead control and play their animations stably at their assigned locations.
- **Movement Lock / Ignoring Custom Positions & Furniture Fix**: Fixed a bug where settlers completely ignored movement commands (set position or furniture pathing) because they were locked in state-manager idle/sitting states from their previous locations. Added a `state_mgr.set_state` call with `"patrol"` inside `camp_npc_move_to` to release animations and enable active engine-level pathfinding.
- **Self-Contained Alarm System Assets**: Merged missing meshes (`alarm_system.ogf`, `alarm_system_pda.ogf`), textures, sounds, and scripts from the base *Hideout Gadgets for Hideout Furniture* mod directly into the Homestead mod's `04_HideoutGadgetsGammaPatch` directory. This makes the PDA-enabled alarm system fully self-contained and prevents fatal client crashes due to missing model assets.
- **Safe Camp Registry Loading**: Modified `actor_on_first_update` to only delete orphaned camps if they are on the player's current level AND their hub object is confirmed missing from the alife registry. This prevents temporary engine level-load delays on other levels from deleting valid settlements.

## v0.9.10 — Invincible Settlers MCM Option

- **New MCM Option: Invincible Settlers** (default OFF). When enabled, settlers are healed to full health every update tick — they cannot die. Only applies to player settlers, not rival camp NPCs. Requested by viktormwirv for Anthology players who can't always defend their camp.

## v0.9.5 — Fast Travel Fix

- **Fast Travel Logic Bug Fixed**: `fast_travel_to_camp` always returned an error (either "same_level" or "cross_level_unsupported") and never actually teleported. The same-level early return at line 3310 made the teleport code unreachable. Fixed to properly teleport on same level and attempt cross-level via server entity vertex change.
- **MCM `event_check_interval` Slider Added**: cfg referenced this key but no MCM slider existed, causing "bad path" spam in logs.

## v0.9.3 — Loader Audit + Water Pump Trader Supply + CHANGELOG Split

- **Water Pump Trader Supply**: Created `trade_water_pump.ltx` registering `itm_water_pump` with Anomaly's trader supply system.
- **Loader Audit**: Confirmed no `stalker_camp_builder = stalker_camp_builder or {}` in sub-modules, `load_state` properly syncs table + local, all 63 `sb.X` references resolvable.
- **CHANGELOG.md**: Split from README.md.

## v0.9.0 — Settlement Not Showing in PDA Fix

- **`load_state` Local Variable Shadowing Bug Fixed**: `local active_camps = stalker_camp_builder.active_camps` created a local that shadowed the table field. When `load_state` reassigned `active_camps`, it went to the local, not `stalker_camp_builder.active_camps`. PDA saw empty table. Fixed by assigning to both.

## v0.8.9 — MCM Table Destruction Fix

- **Removed `stalker_camp_builder = stalker_camp_builder or {}`** from all sub-modules. This line created a self-reference in the sub-module's env table, not a global alias, destroying the main table.

## v0.8.6 — Module Split Fix (Remove zzzzzz_ Prefix)

- Reverted zzzzzz_ prefix approach, restored original filenames, fixed `is_position_flat_enough` and `CAMP_BOX_ID_CACHE_TTL_MS` to explicit `stalker_camp_builder.X` assignments, added safety bridge.

## v0.8.2 — Recruit Crash Fix + Inventory Box Log Spam

- **Recruit Companion Crash**: Wrapped `axr_companions.remove_from_actor_squad` in pcall, deferred `release_npc_from_squad_and_smart` to next frame.
- **Log Spam**: Added section-name fallback for `safe_iterate_inventory_box` when `IsInventoryBox` isn't available.

## v0.8.0 — Settler Wandering Fix + Caravan Trader Faction

- **Behavior Scheme Removed**: `beh@base` LTX scheme was overriding Lua-set destinations, causing settlers to wander. Removed the scheme entirely — Lua `npc_on_update` handles all movement.
- **Caravan Trader Faction**: Trader now spawns as camp's dominant faction via `set_character_community`.

## v0.7.9 — Spiral Search for Decoration Placement

- Decorations that would float/clip now get nudged to nearby valid ground via spiral search (5 rings × 8 directions). No radius reduction — 9 decorations at full radius.

## v0.7.7 — Rename Hotkey Fix (Correct Approach)

- `OnKeyboard` calls base class first (edit box gets keys), then returns `true` (blocks game hotkeys). No `level.disable_input()`, no `SetFocus()`.

## v0.7.4 — Repair Crash + Gas Balloon Fuel + Cook Tiers

- `set_condition` crash fix (server entity `condition` is a field, not method).
- Gas balloon recognized as fuel (exact + substring match).
- Cook output tier MCM slider (1-3).

## v0.7.0 — Cross-Level Settler Travel + Busy Hands + Rename World Name

- `teleport_settler_to_camp_level` + `recall_all_settlers` + PDA button.
- NPC state reset after recruit (busy hands fix).
- Rename updates NPC world name on both client and server entity.

## v0.6.6 — squad_members Nil Crash + Settler Lookup Leaks

- `safe_squad_members` helper for all 14 call sites.
- `settler_lookup` cleared in `banish_npc`, `npc_on_death_callback`, `process_camp_morale`.

## v0.6.7 — iterate_inventory_box Crash + Missing Behavior LTX

- `safe_iterate_inventory_box` helper for all 13 call sites.
- `homestead_settler_beh.ltx` restored (was dropped in v0.6.2 rebuild).
