# PDA Radio Feed + How to Play: design concepts (phase 1)

Panel is 564x536 UI units (the area right of the left rail), drawn at 2x. Same colours and tab/section styling as the Overview concept C. Images: `comparison_radio.png`, `comparison_guide.png`, single panels `radio_A/B/C.png`, `guide_A/B/C.png`. Regenerate with `python make_mockups.py`.

## What exists today
- Radio: header, 4 filter buttons (All / Expeditions / Work / Combat), Scan, Clear, then a scroll list of cards (tag + time + text, newest first, max 50 kept). Categories: combat, expedition, work, general. Scan re-reads settlers and rivals into the log.
- Guide: one long scroll of 26 sections (11 main chapters + 14 job sub-sections) in gold/white colour-coded text. Nothing to jump to, about 40 screens of scrolling.

## Radio Feed
**A. Stripe cards** (smallest change). Same cards, colour stripe per category, counts on filter buttons, "TODAY" divider.
- Pro: easiest, no new data, matches Overview look. Con: still one long mixed list, no per-settlement view.
- XML: stripe = extra static per card colour (a few 1px-wide textures, or tinted `ui_homestead_card_bg`); counts are just button text.

**B. Channels**. Left list: All settlements or one settlement; tick boxes for type; compact one-line rows.
- Pro: with several settlements you can read just one; about 12 rows per screen. Con: needs `hub_id` kept per entry (logs already store per-hub lists, `radio_logs[hub_id]`), checkboxes need new XML buttons (could be toggle buttons).
- Tick boxes can be done with `check_mode` buttons; narrower text column (~380 wide) wraps more.

**C. Dispatch board**. Red alert banner for the latest raid, four summary tiles (last raid, expeditions out, last workshop, feed count), then the filtered list.
- Pro: shows state at a glance, feels like a radio operator desk. Con: tiles need new derived data (time since raid, count of scavengers out); less room for the list.

## How to Play
**A. Chapter pages**. Six tabs (Start, Build, Settlers, Defense, Economy, Setup) like Overview concept C, with Previous/Next page buttons.
- Pro: familiar tab look, text same size, chapters jump instantly. Con: needs the 26 sections regrouped into 6 chapters and page splitting by height (page count depends on text wrap); Next/Prev logic.

**B. Index + reader**. Left list of topics (jobs indented), right pane shows only the chosen topic, Start Here is first.
- Pro: any topic in one click, no scrolling through unrelated text, easiest to find "how do I do X". Con: narrower reading column (about 370 wide) so long sections still scroll; 15+ list buttons need a scroll list.

**C. Quick-start home**. Opens on an 8-step checklist and 12 topic tiles; a tile opens that topic full width with a Back button.
- Pro: best for new players, friendly, short. Con: two screens to build (home and reader), checklist is static (ticking would need saved state: not proposed), tile text is short.

## UI limits respected
- English XML stays ASCII (no arrows or fancy bullets): mockups use `>`, `-`, `x` only.
- X-Ray text: colour via `%c[a,r,g,b]` markup (already used), `complex_mode`, no images except existing textures (`ui_homestead_card_bg`, `ui_homestead_module_header`, `ui_homestead_btn_on`, `ui_button_ordinary`), no rounded corners or gradients, scroll view for long lists.
- Tab-style buttons toggle using the existing `hs_theme.set_active`.
