# PDA Outposts tab: three layout concepts

Design only. Mockups are Pillow renders of the PDA window (764x603 UI units, drawn at 1.5x) with the real
panel geometry from `ui_stalker_camp_builder_pda.xml` (list 180 wide, detail 370 wide). Regenerate with
`python make_mockups.py`. Sample data is invented.

Current tab ("Outposts" = the `rivals` tab): a list of 162x84 cards (level photo + name only, 5 visible), and a 370 px
detail scroll with name, tier line, one banner (hostile / allied / abandoned), Faction, Location and Garrison
boxes, an Intel text box, and Locate on Map + Refresh buttons. The list never shows hostility, faction or tier,
although the script already builds a badge and a "location | tier" string for each row and then drops them.

Data actually available per outpost: name, level, tier 1-3, faction (or mutants), status (occupied / cleared /
unoccupied / mutant nest), garrison count (only while the squad is online), distance (only on the player's current
level), intel text. Mockups use only these.

| | A Compact list + dossier | B Hero picture + stat tiles | C Sub-tabs in the panel |
|---|---|---|---|
| List rows | 176x50 text rows, coloured side bar, faction/hostility line; about 9 visible | keeps the photo cards, adds status pill; about 5 visible | 176x46 rows plus All / Hostile / Allied / Empty filter chips |
| Detail | name, banner, Faction & Garrison, Location, Intel | big level photo header, 3 stat tiles, Intel | Intel / Garrison / Location sub-tabs, banner with faction and garrison, quick facts |
| Matches Overview concept C | partly (same banner, module style) | least (photo-led) | most (same tab strip + banner pattern) |

## A. Compact list + dossier
Pros: biggest gain for least change; every outpost's threat is readable without clicking; simplest XML (two static
rows, one coloured bar texture per state). Cons: loses the level photos (could stay as a small detail header).

## B. Hero picture + stat tiles
Pros: most atmospheric, reuses the existing `ui_homestead_thumb_<level>` art, big readable numbers. Cons: still only
about 5 outposts visible, the photo costs vertical space, status pill needs 3 small textures.

## C. Sub-tabs in the panel
Pros: consistent with the chosen Overview, room to grow (future outpost events or raid info get a tab), filters
help once there are many outposts. Cons: most work (sub-tab state, filter reload of the list, three panels);
Garrison and Location are thin today, so those tabs would feel empty until more data is shown.

Notes for implementation: a coloured side bar per row is one static texture tinted by `hs_theme` colour roles;
filters only re-run the list build in `Reset`. No dynamic layout is needed in any option; the Intel box already
resizes to its text in the current script.
