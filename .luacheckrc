-- luacheck config for Homestead (S.T.A.L.K.E.R. Anomaly 1.5.3 / GAMMA, LuaJIT-less X-Ray Lua 5.1).
-- Used by tools/check.ps1. Anomaly loads every .script as a global module, so any
-- base-game or other-mod module (utils_data, ui_options, ...) is an "undefined global" to luacheck.
-- Repo module names are added by check.ps1 on the command line; base-game ones are listed below
-- when seen. Everything not listed shows up as W113 and is tracked via tools/check_baseline.txt.

std = "lua51"
max_line_length = false
unused_args = false
self = false

ignore = {
    "211", "212", "213", -- unused local / argument / loop variable
    "231",               -- variable set but never accessed
    "311", "312", "314", -- value assigned is unused / overwritten
    "331", "341", "351", "431", "432", "421", "422", "423", -- unused/shadow noise common in X-Ray scripts
    "542",               -- empty if branch
    "6..",               -- whitespace / style
}

-- Engine and base-game globals that are read (never assigned) by this mod.
read_globals = {
    -- engine singletons / functions
    "db", "alife", "level", "game", "device", "get_console", "get_hud", "system_ini", "game_ini",
    "printf", "log", "log1", "abort", "flush", "get_time_global", "time_global", "get_unicode_char",
    "register_callback", "unregister_callback",
    -- Anomaly callback / time-event API
    "RegisterScriptCallback", "UnregisterScriptCallback", "AddScriptCallback", "SendScriptCallback",
    "CreateTimeEvent", "RemoveTimeEvent", "ResetTimeEvent", "AddUniqueCall", "RemoveUniqueCall",
    "ui_options",
    -- engine classes and helper types
    "vector", "vector2", "matrix", "rotation", "flags32", "CTime", "ini_file", "net_packet",
    "particles_object", "sound_object", "color", "fcolor", "Frect", "Fvector", "Fbox",
    "CUIStatic", "CUIScriptWnd", "CUIWindow", "CUIScrollView", "CUIListBox", "CUIProgressBar",
    "CScriptXmlInit", "CUITextWnd", "CUIFrameLineWnd", "CUIEditBox", "CUIListBoxItem",
    "get_hud", "bit_and", "bit_or", "bit_xor", "bit_not", "bit_shl", "bit_shr",
    "ClearCompletedTimeEvents", "dik_to_bind", "DIK_keys", "bind_to_dik",
    "patrol", "cond", "wait", "sound", "snd_type", "clsid", "danger_object", "anim", "move", "look",
    "action_base", "action_planner", "action_ptr", "world_property", "property_evaluator",
    "property_evaluator_const", "entity_action", "object", "hit", "cse_alife_item",
    "get_global", "get_script", "xrs_dyn_news", "demonized_time_events",
    -- common Anomaly modules referenced from the mod
    "utils_data", "utils_obj", "utils_ui", "utils_item", "utils_xml", "utils_stpk", "xr_logic", "xr_conditions",
    "xr_effects", "xr_gulag", "bind_stalker", "news_manager", "dialog_manager", "ui_mcm", "ui_inventory",
    "inventory_upgrades", "item_parts", "item_weapon", "ui_pda_npc_tab", "ui_pda_contacts_tab",
    "se_respawn", "sim_board", "simulation_objects", "sim_squad_scripted", "smart_terrain", "story_objects",
    "death_manager", "trade_manager", "treasure_manager", "tasks_fetch", "task_manager", "gameplay_disguise",
    "dynamic_news_manager", "axr_main", "axr_companions", "axr_trader", "axr_task_manager", "axr_utils",
    "ui_workshop", "ui_debug_launcher", "ui_main_menu", "ui_load_dialog", "ui_options_dialog", "game_statistics",
    "bind_item_container", "ui_stalker_camp_builder_pda",
}

-- Globals this mod itself writes. Add here only for true cross-file globals.
globals = {
    "stalker_camp_builder",
}

-- Never lint non-mod trees
exclude_files = { ".git/**", "docs/**", "tools/**", ".claude/**" }
