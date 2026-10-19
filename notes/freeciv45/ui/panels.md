# Freeciv45 panels for the Qt client: the unit bar, the city overlay and the map's edges (issue 91, 2026-10-17)

A design for two panels in `client/gui-qt`, a mockup drawn here (`panels-mockup.svg`), and the plan to build
them as a client patch. The survey `qt-today.md` (issue 85) is the source for every "today" claim and every
`file:line` below; the line numbers are for the fork at commit `6777c85`, where `client/gui-qt/` equals upstream
S3_2 `44e6898`. Labels: observed (in the survey or read at the line), inferred (my design reasoning), John's
(a decision for him, collected in section 6). Clean room: nothing here copies another studio's layout, icons,
text or names; the behaviour comes from John's two sentences, Freeciv's own data, and ordinary UI practice.

Revised 2026-10-17 (issue 118) to take in `hud-layout.md` section 8, which records in our own words which
information a player needs where: previous/next arrows on the unit bar (2.3), the city view as overlays on the
map's edges instead of one side panel (section 3), and a new section 8 for the top strip, the right-edge button
column with notification badges, the single "what next" button and a persistent tile box above the minimap.
Section 8 is appended, not inserted, so the section numbers other notes cite stay valid. Line numbers added in
this revision are for the fork at `49ba373` (patch 0016) and say so.

John's brief, in his words: the bottom bar "usually sits on a unit and is clicked into"; the left bar "is the
same but on a city, a small circle"; today's panels are "a very old and friction-full design". Read as: the
bottom of the screen belongs to the selected unit and is where its orders are clicked; the left of the screen
belongs to the city you clicked, opened from a small round marker on the map; both appear only when there is
something to show.

## 1. Principles

1. **A panel exists only while its subject is selected.** The unit bar shows when the focus list is non-empty
   and hides when it is empty (today's `hud_units` already does this, `hudwidget.cpp:598-601`). The city
   overlay shows after a click on a city marker and closes on Escape, on Return to map, on a click on another
   marker (which swaps the city), or when the city is lost.
3. **The map stays visible.** No panel covers the middle of the map: the unit bar sits on the bottom edge, the
   city overlay's parts sit on the four edges around a map centred on the city, the empire numbers on the top
   edge, buttons and badges on the right edge (`hud-layout.md` sections 1 and 3).
2. **Everything on a panel is already in the client.** No new packets, no server changes. Each element below
   names its field or helper. The full city dialog stays as the long form behind one button (John's, section 6).
4. **Logical pixels, Retina-clean.** Sizes are given at 1x; at 2x the same logical sizes apply, QPainter draws
   text, bars and borders crisp by itself, and the only blurry parts are tileset sprites until the 2x art exists
   (plan rows Q1 and T0 to T2 in `notes/freeciv45-plan.md`). Panel pixmaps get `setDevicePixelRatio` so the
   OS does not double them a second time.
5. **One switch.** A Qt client option `gui_qt_freeciv45_panels` (default on in Freeciv45 builds, see 5.7)
   turns everything in this note off and brings back `hud_units`, the left sidebar and the direct city dialog,
   so a before/after screenshot is one option flip apart.
6. **Keyboard first, mouse second.** Every action button shows its key, and the keys are the ones the Qt
   client already binds (`shortcuts.cpp:57-176`), so the bar teaches the shortcuts instead of competing with them.

## 2. The unit bar (bottom, centred on the map)

Mockup: `panels-mockup.svg`, frame "Map view", group `unit_bar` (drawn by `scripts/panels-mockup.py`). Class `unit_bar` (new file `unitbar.cpp/.h`, section 5.1).

### 2.1 Where and when

- A child of `map_view`, like `hud_units` (`pages.cpp:788`), centred horizontally, 12 px above the map's
  bottom edge, re-centred in `fc_game_tab_widget::resizeEvent` next to the existing calls (`fc_client.cpp:1094-1126`).
- Shown and refreshed from `update_unit_info_label()` (`mapview.cpp:1066-1071`), which common code calls on
  every focus change (`control.c:215-221`) and after orders; hidden when `head_of_units_in_focus()` is null.
  Unlike today's panel it is shown from that hook, not from `real_menus_update` (`menu.cpp:530-542`), so it
  never waits for a menu rebuild.
- Not draggable (the position is part of the design); the old panel's `unit_fx`/`unit_fy` settings
  (`fc_client.cpp:679-688`) are left alone for the off-switch case.
- Bottom centre, not bottom left as in `hud-layout.md` section 1 (inferred, decision 7): the bottom left
  belongs to the chat today and to the city overlay's production part when a city is open, and the first slice
  (patches 0015 and 0016) already sits centred.
- Hidden while the city overlay is open (section 4, decision 8).

### 2.2 Size

| | 1x | 2x (Retina) |
|---|---|---|
| Bar | 104 px tall, width = content, at least 560 px, at most map width minus 24 px | same logical px; backing pixmaps at DPR 2 |
| Portrait | 80 x 80 px box, sprite scaled to fit, 6 px health bar under it | same box; sprite stays the tileset's size scaled smooth until 2x art |
| Text block | name 15 px bold, lines 11 to 12 px, `fonts::notify_label` family (`client/options.h:411`) | same point sizes |
| Stack chips | 30 x 30 px, 6 px gap, at most 8 then a "+N" chip | same |
| Action buttons | 36 x 36 px, 6 px gap, icon 24 px, key hint 9 px bottom right | same |

Heights follow the font metrics the way `city_dialog` does (`citydlg.cpp:1529`), so a larger notify font grows
the bar instead of clipping it.

### 2.3 Elements

| Element | Behaviour | Data source (observed) |
|---|---|---|
| **Previous / next unit (title row)** | A "‹" left of the name and a "›" right of it step through the units that still need orders this turn, the main way through a turn (`hud-layout.md` section 2). "›" does what W does (the unit waits and the next candidate gets the focus), so its hint shows W. "‹" goes back through the units the bar has shown this turn, newest first, skipping ones that no longer need orders, and changes no unit's state. A small "3 need orders" count sits under the arrows; both arrows are dimmed when no other unit needs orders. | Next: `key_unit_wait` (`control.c:3554`), which ends in `unit_focus_advance` (`control.c:700`) and its candidate test `find_best_focus_candidate` (`control.c:661-700`: idle, moves left, not done, no orders). Previous: a list of unit ids kept in `unit_bar`, filled in `refresh()`, cleared on a new turn; `unit_focus_set` to step back. The count: the same candidate test over `client_player()->units` (inferred; Freeciv has no "previous unit" of its own) |
| **Portrait** | The head focus unit's sprite, cropped and scaled into the 80 px box, with a 6 px health bar below (green above 2/3, yellow to 1/3, red below). Click centres the map on the unit. Tooltip: `unit_description()`. | `put_unit()` into a canvas as today (`hudwidget.cpp:650-668`, `mapview_common.c:1399`); `punit->hp` and `unit_type_get(punit)->hp` (`common/unit.h:150`); `unit_description` (`client/text.c:482`) |
| **Name and veteran level** | "Warriors" bold; second line the home city in brackets, or "no home". The veteran level as small filled badges right of the portrait, one per level (`hud-layout.md` section 2), with the rank name in their tooltip; the first slice still prints the rank as text. | `unit_name_translation`, `utype_veteran_name_translation(ptype, punit->veteran)` (`common/unittype.c:2610`, `unit.h:151`), `player_city_by_number(owner, punit->homecity)` (`unit.h:145`) |
| **Strength, moves, health** | One line "str A / D   moves m of M   hp h/H": attack and defence from the type, moves left over move rate as fractions the way the client prints them, hit points. Fuel appended as today. | `ptype->attack_strength`, `defense_strength`, `move_rate`; `move_points_text(punit->moves_left)` (`movement.c:1047`); `punit->fuel` (`unit.h:152`) with the same fuel text as `hudwidget.cpp:622-633` |
| **State line** | Activity ("fortified", "sentried", "building road 3 turns", "going to (x,y)") and upkeep "upkeep 1 shield" or "free". | `unit_activity_astr` (`common/unit.c:1163`), `punit->activity` (`unit.h:156`), `punit->goto_tile` (`:154`), `punit->upkeep[]` (`:147`) |
| **Stack chips** | One chip per unit on the focus unit's tile that the player owns, in tile order, at most 8 then "+N" which opens today's stack chooser. The focused units are ringed. Click = focus that unit alone; Shift+click = add it to the focus; the chip tooltip is the unit's name, hp and activity. With several units in focus the text block says "Selected N units" and the action row offers only the actions all of them can do. | `punit->tile->units` (`unit.h`), `get_units_in_focus()`, `unit_focus_set` / `unit_focus_add` (`control.h:198-200`); the "+N" chip calls `unit_select_dialog_popup(tile)` (`dialogs.cpp:1299`) |
| **Actions** | Icon buttons with the key hint printed in the corner. First row, left to right, each shown only when its test passes: go to (G), fortify (F), sentry (S), build (B: found city for city founders, else the work action the unit can do here, road/mine/irrigate), pillage (Shift+P), found city when the build slot is taken by a work action, upgrade (Shift+U), disband (Shift+D), skip (W), done (Space). A second row appears only for units with more (explore X, patrol Q, board L, deboard U, set home H, auto worker A, clean P, paradrop, nuke), using today's tests. | Tests as in `unit_actions::update_actions` (`hudwidget.cpp:973-1170`: `unit_can_add_or_build_city`, `can_unit_do_activity_client`, `can_build_road`, `unit_upgrade_test`, `can_unit_paradrop`...). Pillage: `can_unit_do_activity_client(punit, ACTIVITY_PILLAGE)`. Click handlers call the control functions the menu slots call: `key_unit_goto` (`control.c:3483`), `key_unit_fortify` (`:3624`), `key_unit_sentry` (`:3768`), `key_unit_build_city` (`:3365`), `key_unit_pillage` (`:3720`), `key_unit_wait` (`:3554`), `key_unit_done` (`:3475`), `popup_upgrade_dialog` and `popup_disband_dialog` (`dialogs.h:297-298`), or `execute_shortcut` for the rest (`menu.cpp:1847`) |
| **Combat odds tooltip (plan row Q2)** | While a unit is in focus and the mouse rests on a tile with a unit of another player that the focus unit could attack, a tooltip next to the cursor shows: the target's name and state, a two-colour bar of attacker versus defender chance, "Chance to win: A:68% D:32%", and the A/D/FP/HP line for both. It hides when the mouse leaves the tile. It does not open on allied or own tiles. | `map_view::mouseMoveEvent` (`mapctrl.cpp:537-547`) with `canvas_pos_to_tile`; text from `combat_odds_to_astr` (`common/clientutils.c:310-345`), which already does the A/D percentages and the stats lines; defender choice via `get_defender` (`combat.c:836`); `can_unit_attack_tile` (`combat.h:58`); shown with `QToolTip::showText` as the city dialog does (`citydlg.cpp:3972`) |

### 2.4 Keyboard

- The keys in the hints are the client's defaults (`shortcuts.cpp:57-176`) and go on working whether or not the
  bar is shown; the bar re-reads them from `fc_shortcuts` so a remap changes the hint.
- `[` and `]` cycle the stack chips (previous/next unit on the tile), chosen because `map_view::keyPressEvent`
  (`mapctrl.cpp:119-212`) binds digits, arrows, Return, Escape and letters but not brackets (observed in that
  switch; the menu has no bracket shortcut, inferred from `menu.cpp:1001-1375`). To verify in the shortcuts
  dialog before the slice lands.
- Tab moves focus along the chips and buttons when the bar has keyboard focus (click on it); Escape gives
  focus back to the map (`mapview_wdg->setFocus()`, as `fc_client.cpp:1151-1153` does).

### 2.5 Theming

Class names for `resource.qss`: `unit_bar`, `unit_bar QLabel`, `unit_chip`, `unit_chip[focused="true"]`,
`unit_action`, `unit_action[hint]`. Colours, borders and the background come from the stylesheet with the
palette as fallback (the same way `hud_action` uses `QPalette::Text` and `Highlight`, `hudwidget.cpp:855-860`);
the health bar's three colours are theme properties with defaults. Icons: the theme's PNGs today
(`fc_icons::get_pixmap`, `fc_client.cpp:1046-1071`); SVG versions later so they stay sharp at 2x (the bundle
ships Qt's SVG plugin since PR 60).

## 3. The city marker and the city overlay (over the map's edges)

Mockup: `panels-mockup.svg`, frame "City view", groups `city_marker`, `city_overlay` (`city_yields`,
`city_header`, `city_sections`, `city_production`, `city_footer`). Classes `city_marker` (painted in
`map_view::paint`) and `city_overlay` (new file `cityoverlay.cpp/.h`), section 5.1.

The earlier version of this section had one 320 px panel down the left edge. `hud-layout.md` section 3 records
the other shape, the one this design now follows: clicking a city keeps the map on screen, centred on the city
with its worked tiles and their yields drawn on the map, and puts the city's information in small parts on the
map's edges. The round marker that opens it stays.

### 3.1 The marker

- A round badge, 28 px across at 1x, drawn over the city tile's centre after the map store is painted
  (`map_view::paint`, `mapview.cpp:291-296`), for every own city on screen and for foreign cities whose size
  the player can see. It shows the city size, uses the owner's nation colour as its fill (the map already has
  `get_player_color`, used for borders), a thin light ring, and a second ring while that city's overlay is open.
  A city working under the governor gets a small dot.
- Clicking inside the circle opens the overlay. The hit test runs in `map_view::shortcut_pressed` before the
  select button falls through to `action_button_pressed` (`mapctrl.cpp:453-461`): if the press is within 14 px
  of an own city's marker centre, open or swap the overlay and return. A click elsewhere on the city tile keeps
  today's meaning (the stack chooser or the full dialog, per `do_map_click`, `control.c:2969-3001`).
- Shift+click on the marker opens the full dialog directly (John's, section 6). Ctrl+click and
  Ctrl+Shift+click keep their quick production and quick buy meaning (`mapctrl.cpp:325-333`, `:418-425`).
- The tileset's bar under the city (name, growth, production; `show_full_citybar`, `mapview_common.c:1907`)
  stays; it is common code and a tileset matter. Hiding it when the marker is on is a later option.

Data: `city_size_get`, `city_owner`, `tile_to_canvas_pos` (`mapview.cpp:105` shows the call), `cma_is_city_under_agent`.

### 3.2 The overlay: where and when

- A mode of the map view, not a window. Opening it centres the map on the city (`center_tile_mapcanvas`,
  `mapview_common.c:1239`, fork `49ba373`), turns on the worked-tile drawing for that city (`toggle_city_color`,
  `:1501`), and shows five parts as children of `map_view`, each anchored to an edge (3.3). Between them the map
  is the map: it scrolls, its tooltips work, and a click on a ringed tile toggles a worker (3.3, last row).
- Opens on a marker click (3.1), on `popup_city_dialog` for the player's own city when the switch is on (so a
  newly founded city opens the overlay, not the dialog: `qtg_real_city_dialog_popup`, `citydlg.cpp:3822`,
  routes there), and from the Cities report's "open" action.
- Refreshes from the same queue as the dialog: `qtg_real_city_dialog_refresh` (`citydlg.cpp:3870-3881`) calls
  the overlay's `refresh()` when it shows that city; `qtg_city_dialog_is_open` (`:3925`) reports the overlay
  too, which keeps `packhand.c:1100` from popping a second window.
- Closes on Escape, Return to map, a marker click on another city (swap), `qtg_popdown_city_dialog` (`:3850`),
  and when the city is lost (`pcity` null in `refresh()`, as `citydlg.cpp:3011-3013` handles it). Closing turns
  the worked-tile drawing off and leaves the map where it is.
- While open, the bottom and right edges belong to the city: the unit bar, the chat (`info_tab`), the minimap,
  the tile box and the "what next" button (section 8) are hidden and come back on close; the top strip and the
  right-edge button column stay (section 4, decision 8). The old full dialog is not opened; if it is already
  open it is hidden.
- Sizes at 1x, the same logical sizes at 2x: yields 360 x 96 px, header 400 x 56 px, sections column 300 px wide
  and as tall as the map less the top strip, production 380 x 200 px, footer 340 x 40 px. Each part is
  translucent over the map like the unit bar, and none is draggable.

### 3.3 The parts

| Part | Where | Contents and behaviour | Data source (observed) |
|---|---|---|---|
| **Yields** (`city_yields`) | top left, under the top strip | The size, "grows in N turns" or "starving in N turns" or "growth blocked" and "granary f/F" on the first line; under it one tile per yield with its sign: food, shields, trade, gold, bulbs, luxury when non-zero, and the city's culture points. Each tile's tooltip is the full breakdown. | `city_size_get`, `city_turns_to_grow` (`common/city.c:1996`: positive, negative for famine, 0 blocked, `FC_INFINITY` never), `pcity->food_stock`, `city_granary_size` (`city.h:367`, `city.c:2146`); `pcity->surplus[]`, `prod[]`, `waste[]` (`city.h:355-358`) formatted as `update_info_label` does (`citydlg.cpp:3160-3178`); tooltips `get_city_dialog_output_text` (`citydlg_common.c:748`); `city_culture` (`common/culture.c:29`) |
| **Header** (`city_header`) | top centre | The round marker repeated at 24 px with the size, the city name (click renames), "‹" and "›" for the previous and next own city, and under the name small status icons: disorder, celebrating, under the governor, occupied. | `city_name_get`; rename as `city_dialog::city_rename` (`citydlg.cpp:2383`); next/previous as `:3373-3441`; `city_unhappy`, `city_celebrating` (`city.c:1626`, `:1645`), `cma_is_city_under_agent`, `pcity->client.occupied` |
| **Sections** (`city_sections`) | right, left of the right-edge button column | A column of sections, each folded or unfolded by a click on its heading, the state kept for the session: **Citizens** (one small circle per citizen in the final feeling: green happy, grey content, red unhappy, blue specialists; a click on a specialist changes its kind; "health: plague risk p%  pollution n"; tooltip on the row: the happiness causes), **Buildings** (built improvements, wonders first, upkeep total in the heading; hover gives the help text, right-click offers sell with a confirmation box), **Units** ("here N, supported M" as chips like the unit bar's; a click focuses the unit and closes the overlay so the unit bar takes over). Later sections: **Great people** (one progress bar per kind, once the client can read the ruleset's points, slice of patch 0013) and specialist buildings with their slots. | `get_city_citizen_types(pcity, FEELING_FINAL, ...)` (`citydlg_common.c:1201`), `pcity->feel[][]`, `specialists[]` (`city.h:333-336`), `city_change_specialist` (`citydlg_common.c:1560`); `city_illness_calc` (`city.c:2884`, tenths of a percent, only when `game.info.illness_on`), `pcity->pollution`; tooltips `text_happiness_*` (`client/text.c:1832-2104`); `collect_already_built_targets` and `city_improvement_upkeep` as `update_improvements` uses them (`citydlg.cpp:3531-3546`), `impr_item`'s sell path (`citydlg.cpp:619`); `pcity->tile->units`, `pcity->units_supported` as `update_units` (`citydlg.cpp:3297-3353`) |
| **Production** (`city_production`) | bottom left | The current build with its sprite, "s/S shields, N turns", a thin progress bar, the upkeep it will cost, and two buttons above it: Change and Buy with the price (disabled when it cannot be bought, the tooltip says why). A "Show queue" toggle unfolds the queue upwards as numbered rows with turns; a row's right-click menu moves or removes it; "+ add to queue" opens the chooser in queue mode. Change opens the existing chooser (`production_widget`) anchored to the part; double-click there changes now, Shift+double-click adds last. | `pcity->production`, `shield_stock` (`city.h:368`), `city_production_build_shield_cost`, `get_city_dialog_production` (`citydlg_common.c:260`); `client.buy_cost` (`city.h:466`), `city_can_buy` (`citydlg_common.c:1524`, fork `49ba373`), `city_buy_production` (`citydlg_common.c:1552`); `city_get_queue` (`:1469`), `city_queue_insert` (`:1411`), `city_set_queue` (`:1486`), `city_change_production` (`:1287`); chooser `production_widget` (`citydlg.cpp:4521`) |
| **Footer** (`city_footer`) | bottom centre | "Show worked tiles" toggle (on while the overlay is open), "Open full dialog" (also Enter: closes the overlay and calls today's `city_dialog` for the governor, nationality, counters, airlift and the rest), "Return to map" (also Escape). | `qtg_real_city_dialog_popup` with the switch bypassed (`citydlg.cpp:3822-3832`) |
| **Worked tiles on the map** | the map itself | The city's workable tiles are ringed, worked ones solid with their food/shield/trade numbers, free ones dashed. A plain click on a ringed tile toggles its worker. Hovering a tile shows the same tile tooltip as the main map (section 8.4). | `toggle_city_color(pcity)` (`mapview_common.c:1501-1509`) makes the tileset draw `worked_tile_overlay` and `unworked_tile_overlay` (`tilespec.c:5113-5121`), and `draw_city_output` adds the numbers (`:5122-5134`); the click is `adjust_workers_button_pressed` (`mapctrl_common.c:598-620`), today bound to Meta+Ctrl+click (`shortcuts.cpp:78-79`), which the overlay re-routes from a plain click while it is open |

### 3.4 Keyboard

- Escape closes the overlay (then, as today, `key_cancel_action`, `mapctrl.cpp:191-195`). Enter opens the full
  dialog. Left/Right arrows with the overlay focused go to the previous/next city (the dialog's buttons,
  `citydlg.cpp:3373`). `c` centres the map on the city again (today's Center View key does this for the focus
  unit).
- Tab walks Change, Buy, Show queue, the section headings and the footer buttons. The chooser keeps its own keys.

### 3.5 Theming

Class names: `city_overlay` (the shared look of the five parts), `city_yields`, `city_header`, `city_sections`,
`city_section` (one heading and its body), `city_production`, `city_footer`, `yield_tile`, `prod_row`,
`citizen_dots`; `city_marker` colours as four theme properties (fill, ring, open ring, text). The parts' sizes
and the marker's radius are not themed in the first slice (section 5.5 lists them as a later option).

## 4. What is hidden, and the panels together

| Situation | Unit bar | City overlay | Top strip, right edge | Minimap, tile box, what next | Today's widgets |
|---|---|---|---|---|---|
| Unit in focus, no city open | shown | hidden | shown | shown | `hud_units` and `fc_sidebar` hidden (switch on) |
| City overlay open, unit still in focus | hidden | shown | shown | hidden | chat hidden; the focus is kept and the bar comes back on close |
| City overlay open, nothing in focus | hidden | shown | shown | hidden | chat hidden |
| Nothing in focus, no city open | hidden | hidden | shown | shown | |
| Switch off | hidden | hidden | hidden | minimap only | `hud_units`, `fc_sidebar`, full dialog on click, as in `qt-today.md` |
| Full dialog open | as before it opened | hidden | shown | shown | the dialog as today |

All of these are map children (the top strip and the right-edge column are children of the game page next to
the map, section 8), so reports in other game tabs (`add_game_tab`, `pages.cpp:811`) cover them as they cover the
minimap today.

## 5. Implementation plan (client patch on `client/gui-qt`)

### 5.1 New code

| File | Class | Role |
|---|---|---|
| `client/gui-qt/unitbar.h/.cpp` | `unit_bar : QFrame` | the bottom bar: `refresh(unit_list *)`, `show_for(unit *)`, hide when empty; owns `unit_chip` and `unit_action_button` |
| | `unit_chip : QAbstractButton` | one stack chip; paints the unit sprite from a canvas, ring when focused |
| | `unit_action_button : QAbstractButton` | icon + key hint; carries a test function and a handler |
| | `odds_tooltip` (free functions) | `odds_text_for(tile *)` building the tooltip from `combat_odds_to_astr`; `show_odds_tooltip(QPoint, tile *)` |
| `client/gui-qt/cityoverlay.h/.cpp` | `city_overlay : QObject` | the mode: `open_for(city *)`, `refresh()`, `close_overlay()`, `place()`; owns the five parts and hides and restores the other map children |
| | `city_part : QFrame` | the shared base of the five parts (translucent box, theme class); `city_yields`, `city_header`, `city_sections`, `city_production`, `city_footer` derive from it |
| | `city_marker` (free functions) | `paint_city_markers(QPainter *)` called from `map_view::paint`; `city_marker_at(QPoint) -> city *` for the hit test |
| `client/gui-qt/mapedges.h/.cpp` | `top_strip : QFrame` | section 8.1 |
| | `edge_column : QFrame` | section 8.2: overview buttons, badges |
| | `what_next_button : QAbstractButton`, `tile_box : QFrame` | sections 8.3 and 8.4 |
| `meson.build` | | add the new files to the Qt client's source and moc lists (`meson.build:3508-3570`) |

### 5.2 Hooks into existing code (small, named edits)

1. `client/options.h` and `options.c`: `gui_qt_freeciv45_panels` as a `GEN_BOOL_OPTION(..., COC_INTERFACE,
   GUI_QT, TRUE, panels_changed)` after `gui_qt_sidebar_left` (`options.c:3293`); the callback in
   `gui_main.cpp` next to `apply_sidebar` (`gui_main.cpp:263`) shows or hides the panels at once.
2. `pages.cpp:788`: create `unit_bar`, `city_overlay`, `tile_box` and `what_next_button` as map children next to
   `unitinfo_wdg`; `top_strip` and `edge_column` in the page grid (section 8).
3. `mapview.cpp:1066` `update_unit_info_label`: when the switch is on, `unit_bar->refresh(punitlist)` and keep
   `hud_units` hidden; else today's code.
4. `hudwidget.cpp:598` `hud_units::update_actions`: return after `hide()` when the switch is on (so the old
   panel never pops from `real_menus_update`).
5. `mapview.cpp:291` `map_view::paint`: after the store, `paint_city_markers(painter)` when the switch is on.
6. `mapctrl.cpp:453` `shortcut_pressed`: before the select-button block, if the switch is on and
   `city_marker_at(pos)` is an own city, open the overlay and return (Shift opens the dialog). While the overlay
   is open and "Show worked tiles" is on, a plain click on a ringed tile of that city calls
   `adjust_workers_button_pressed(pos)` and returns.
7. `mapctrl.cpp:537` `mouseMoveEvent`: `show_odds_tooltip(event->globalPosition(), tile)` after
   `control_mouse_cursor`, and `tile_box->set_tile(tile)` when the hovered tile changes.
8. `citydlg.cpp:3822` `qtg_real_city_dialog_popup`: with the switch on, open the overlay for own cities unless a
   "force full dialog" flag is set by the footer's button and the Shift+click path; `qtg_real_city_dialog_refresh`
   (`:3870`) and `qtg_city_dialog_is_open` (`:3925`) consult the overlay too; `qtg_popdown_city_dialog` (`:3850`)
   closes it.
9. `fc_client.cpp:1094` `resizeEvent`: re-centre the bar, re-place the overlay's parts, the tile box and the
   "what next" button.
10. Theme files: `unit_bar`, `city_overlay`, `top_strip` and `edge_column` blocks appended to the three
    `resource.qss` files with the defaults.
11. `mapview.cpp:1000` `fc_client::update_info_label` (fork `49ba373`): also `top_strip->refresh()`, and the open
    city overlay's `refresh()` so the treasury and a new turn reach Buy and the worked tiles (the overlay slice
    does this part).
12. `messagewin.cpp:404` `real_meswin_dialog_update` (fork `49ba373`): also `edge_column->update_badges()`.
13. `update_unit_info_label`, `real_science_report_dialog_update` (`repodlgs.cpp:1157`) and
    `update_turn_done_button` (`mapview.cpp:1102`, fork `49ba373`): also `what_next_button->refresh()`.
14. `pages.cpp:800-805`: with the switch on, `fc_sidebar` is not added to the grid and `edge_column` takes column 2.

No change to `common/` or `client/*.c`; everything is reachable from the Qt side (observed in the survey).

### 5.3 The minimum first slice (one PR, one patch `0008`; built as patches 0015 and 0016)

Unit bar only, with the switch: portrait and health bar, name and veteran line, "str / moves / hp" line, stack
chips (click and Shift+click), and five actions: fortify (F), sentry (S), go to (G), skip (W), done (Space).
Hidden when nothing is in focus; `hud_units` hidden while the switch is on. No tooltip, no city work.
Acceptance: `scripts/ruleset-look.sh` with the civ45 ruleset shows the bar at turn 1 for the start stack; the
option off restores today's panel; both screenshots in the PR. Diff prepared in `first-slice.diff` (section 7).

### 5.4 What follows, in order

1. Build (B: found city / road / mine / irrigate), pillage, upgrade, disband and the second action row; key
   hints re-read from `fc_shortcuts`; `[` `]` chip cycling; the previous/next arrows and the veteran badges.
2. The combat odds tooltip (plan row Q2) and the tile box above the minimap (8.4), which share the tile text.
3. The overlay's first slice: the map centred on the city, yields top left, the sections column on the right,
   production bottom left with Change and Buy, the footer with Full dialog and Return to map. Prepared as
   `city-overlay-slice.md` and `city-overlay-slice.diff` (issue 135), unapplied. It opens through the popup
   routing (5.2 item 8) instead of the marker, and shows Citizens read-only.
4. The city marker (3.1, 5.2 items 5 and 6), the header with its arrows and status, the queue, the Units section
   and specialist clicks in Citizens.
5. Worked tiles on the map with the click routing (5.2 item 6, second part).
6. The top strip (8.1) and the right-edge column with the overview buttons (8.2); `fc_sidebar` leaves the grid.
7. Notification badges (8.2) and the "what next" button (8.3).
8. Retina: `setDevicePixelRatio(2)` on the panel canvases and SVG icons (needs plan row Q1 for the map itself).
9. Theme blocks for Classic and Necrophos; later, the marker radius and the parts' sizes as theme properties.

### 5.5 Risks

- **Qt 6.12 only.** The build uses Homebrew `qtbase` 6.12.0 (`qt-today.md` section 5). The new code uses Qt 6
  APIs (`QEnterEvent`, `globalPosition`) inside the `FC_QT5_MODE` guards upstream still carries
  (`hudwidget.h:166-170`), so a Qt 5 build keeps compiling even though it is not tested here.
- **Retina (plan row Q1).** Until the map store carries a pixel ratio, sprites in the bar are upscaled tileset
  art; the bar will look crisp in its text and bars and soft in its portraits. Not a blocker for the slice.
- **Hit test versus common code.** The marker click is intercepted in Qt before `action_button_pressed`; the
  goto, rally, trade and delayed-order states checked earlier in `shortcut_pressed` (`mapctrl.cpp:237-310`)
  must keep precedence, so the intercept sits after them and before the select button (`:453`).
- **Focus and menus.** `real_menus_update` is the thing that shows today's panel; leaving it to call
  `hud_units::update_actions` (which now returns early) keeps the menu sensitivity path untouched.
- **Worked-tile clicks** change a plain click's meaning while the overlay is open; the ring makes it visible,
  and the toggle turns it off. Rally points and trade routes keep their own hover modes.
- **Upstream drift.** `client/gui-qt/` is unchanged by patches 0001 to 0007; a rebase onto a later S3_2 may
  move the hook lines but not their functions.

### 5.6 How to test

- Option: `gui_qt_freeciv45_panels` in Game > Options > Interface; off reproduces `qt-today.md`.
- Screenshots before and after through `scripts/ruleset-look.sh <client> OUT --ruleset civ45 -- -t trident`,
  which captures turn 1 with the start stack in focus (the bar shows), and the same with the option off in a
  copied options file. Clicks, hovers and city screenshots through `scripts/ui-drive.sh` with a driver build
  (`bar-test/uidrive.diff`, issue 125); a city comes from a `/lua cmd edit.create_city(...)` line.
- A build from a scratch copy of the fork with the diff applied (section 7) and `meson compile -C build-qt`.
- Keyboard: every hint on the bar pressed once in a turn-1 game; `[` and `]` on a 3-unit stack.

### 5.7 Build and install

The patch becomes `patches/0008-...` applied to the fork, built with `scripts/build.sh qt`, installed to
`~/freeciv-builds/qt`; the default of the switch is on. Nothing is installed anywhere else.

## 6. Decisions for John

| # | Question | Proposal |
|---|---|---|
| 1 | Does the full city dialog stay reachable? | Yes: the panel's bottom button, Enter, and Shift+click on the marker. Removing it later is one line. |
| 2 | Which actions make the first row? | go to, fortify, sentry, build, pillage, upgrade, disband, skip, done (ten with found city when both apply); everything else in a second row that appears only for units that have them. |
| 3 | Plain click on a city tile outside the marker | keep today's meaning (stack chooser or full dialog) in the first slices; later make the whole tile open the panel. |
| 4 | The map's own city bar (name, growth, build) while markers are on | keep it; hide it as a later option. |
| 5 | Switch default | on for Freeciv45 builds; the same client plays other rulesets with the new panels unless turned off. |
| 6 | Chip cycling keys | `[` and `]`, pending a check in the shortcuts dialog. |
| 7 | Where the unit bar sits | bottom centre as built, not bottom left: the bottom left is the chat's, and the city overlay's production when a city is open. |
| 8 | What hides while the city overlay is open | the unit bar, the chat, the minimap, the tile box and "what next"; the top strip and the right-edge column stay. The focus unit is kept and its bar returns on close. |
| 9 | The left sidebar with the switch on | leaves the grid: its numbers move to the top strip (8.1), its buttons to the right-edge column (8.2), Turn Done becomes the "what next" button (8.3). Off brings it back as today. |
| 10 | What "what next" asks first | research unset, then a unit that needs orders, then a city whose queue ran out this turn, then End Turn. |
| 11 | The previous/next arrows | "›" is W (wait and go to the next unit), "‹" steps back through the units shown this turn without changing them; no new keys. |
| 12 | Does the strip's End turn stay now that "what next" ends the turn? | Pending. It stays in patch 0026, so End turn is always one click away even while "what next" asks for something else; removing it is one line in `top_strip`'s constructor. |

## 7. The prepared first slice

The unit bar of 5.3 was prepared under issue #95 as `first-slice.diff` in this folder, with build notes, what was
tested and what was not in `first-slice.md`, and screenshots `first-slice-on.png` (the bar), `first-slice-bar.png`
(the bar alone) and `first-slice-off.png` (the option off, today's panel back). It went onto the fork as patch
0015 (issue 123), and patch 0016 fixed what clicking it in a game turned up (issue 125, `first-slice.md`).

The city overlay's first slice (5.4 item 3) was prepared the same way under issue #135: `city-overlay-slice.diff`,
with what it does, how it was built and what a game showed in `city-overlay-slice.md`, and the shots and drive
script in `city-test/`. It went onto the fork unchanged as patch 0017 (issue #137).

The first slice of section 8, the top strip and the right-edge column with the overview buttons, went onto the fork
as patch 0018 (issue #140) behind its own option, `gui_qt_freeciv45_edges`; what it does and how it was checked is in
`edges-slice.md`, the shots in `edges-test/`. The notification badges (#143) followed as patches 0022 and 0023
(`badges-slice.md`, shots in `badges-test/`), and the "what next" button above the minimap (#144) as patch 0026
(`whatnext-slice.md`, shots in `whatnext-test/`). The sidebar's wheel and right-click extras and its indicators
(#146) followed as patch 0027 (`extras-slice.md`, shots in `extras-test/`). Dragging the map to pan it and two-finger
scrolling (#231) came as patch 0042 (`pan-slice.md`, shots in `pan-test/`).
The selected unit's movement range (#232) followed as patch 0044 (`range-slice.md`, shots in `range-test/`).
The unit bar was sized to its action boxes (#233) as patch 0046 (`barsize-slice.md`, shots in `barsize-test/`).

## 8. The map's edges: top strip, right-edge column, "what next" and the tile box

Mockup: `panels-mockup.svg`, frame "Map view", groups `top_strip`, `edge_column`, `what_next`, `tile_box`.
`hud-layout.md` sections 1, 5 and 6 say what goes here; this section says how the Qt client gets it. With the
switch on these replace the left sidebar (decision 9); with it off nothing here exists.

### 8.1 The top strip

- A `top_strip` frame in row 0 of the game page grid over the map and the right-edge column, 32 px tall at 1x,
  full width. Left to right: research (the tech and "+b bulbs, N turns"), gold and income ("123 (+5)"), the tax
  rates as three small numbers (click opens today's rates dialog), culture (the player's points), then, from the
  slice that adds them, strategic resources with counts; at the right end the year and turn and a menu button.
  Each number is a button that opens its report (research, economy, nations); deltas in brackets.
- Left of the year and turn, the sidebar's four indicators (research progress, global warming, nuclear winter,
  government) as one flat button at the strip's icon height, the game summary as its tooltip; a click or a
  right-click offers the government menu, as a right-click on the sidebar's indicators did (#146, patch 0027).
- Freeciv has no empire-wide happiness or faith number; those `hud-layout.md` entries have no Freeciv45 field and
  are left out until a ruleset slice adds one (inferred).
- Data: `research_get(client_player())`, `->researching`, `->bulbs_researched`, the per-turn bulbs as the sidebar's
  Research icon shows them (`repodlgs.cpp:1187`); `client.conn.playing->economic.gold`, `.tax`, `.lux`, `.sci`,
  `player_get_expected_income` (`common/player.c:1286`), as `fc_client::update_info_label` draws them today
  (`mapview.cpp:1035-1046`); `player_culture` (`common/culture.c:46`); `calendar_text()` (`common/calendar.c:141`)
  and `game.info.turn` (`mapview.cpp:1022-1027`).

### 8.2 The right-edge column and notification badges

- An `edge_column` frame in column 2 of the page grid, 64 px wide at 1x, full height under the top strip. From the
  top: round 44 px buttons for the screens used every few turns (research, nations and diplomacy, cities,
  units, economy), one "overviews" button that opens a short list of the rest (demographics, the message log,
  spaceship, score, help), and below a gap the notification badges.
- The sidebar's wheel and right-click extras sit on the matching buttons, with a tooltip line each (#146, patch
  0027): the wheel on Cities (up the other nations' cities, down your own), on Nations (up the other nations'
  capitals, down your capital) and on Units (up the other nations' units, down W); a right-click on Units centres
  on the focus unit, on Research offers the advances to research now, and on Nations opens the current diplomacy
  meeting (an observer gets the observe menu). The wheel first returns to the map and closes the city overlay. The
  sidebar's other right-click, back to the map from any button without its own, is dropped on purpose: the Map
  button does it.
- Each overview opens as today's report tab (`add_game_tab`, `pages.cpp:811-818`); a modal over the dimmed map as in
  `hud-layout.md` section 4 is a later step, since the reports are tabs of the game stack today (inferred).
- Badges: one round 36 px badge per unvisited message that has a place to go (a city or a tile), newest at the
  top, at most eight, then a "+N" badge that opens the messages log. The badge's icon is the event's kind (city,
  diplomacy, military, research, other), its tooltip the message text. A click jumps there (`meswin_goto`, or
  `meswin_popup_city` for city events, which opens the city overlay) and marks the message visited, which removes
  the badge. The chat and messages widget stays as the log.
- Data: the client's message list (`struct message` in `client/messagewin_common.h:29-39`: `descr`, `tile`,
  `event`, `location_ok`, `city_ok`, `visited`), refreshed through `real_meswin_dialog_update`
  (`messagewin.cpp:404`, fork `49ba373`); `meswin_goto` and `meswin_popup_city` (`client/messagewin_common.c:213`,
  `:185`); the kind from the event's section (`E_S_CITY`, `E_S_D_ME`, `E_S_ADVANCE`... in `common/events.c:31`),
  through a small accessor since the section table is file-local there (inferred).

### 8.3 The "what next" button

- One wide button, 224 x 40 px at 1x, directly above the minimap. Its text says what the turn needs next and a
  click does it: "Choose research" (opens the research report), "Unit needs orders" (focuses the next candidate
  as W does), "City needs production" (opens that city's overlay), and "End turn" when nothing blocks, which is
  today's Turn Done (`key_end_turn`, `control.c:3324`). A small "1 of 3" shows when more than one item waits.
- Order of the checks (decision 10): research unset, a unit that needs orders, a city whose queue ran out this turn,
  then End Turn. Shift+Return still ends the turn from the keyboard (`mapctrl.cpp:124-131`).
- Data: `research_get(client_player())->researching == A_UNSET`; the focus candidate test of 2.3; cities from this
  turn's "worklist is empty" and "production complete" messages in the message list (8.2), since the client has no
  flag of its own for it (inferred); `update_turn_done_button` (`mapview.cpp:1102`, fork `49ba373`) for the
  turn-done state.

### 8.4 The tile box above the minimap

- A `tile_box` frame, 224 px wide at 1x, above the "what next" button: the hovered tile's terrain and features,
  its improvements and roads, its owner, and its yield as three numbers, in four short lines. It keeps the last
  tile when the mouse leaves the map, so the cursor tooltip (Q2, 2.3) can stay short and the full text is one
  glance away.
- Data: `popup_info_text(ptile)` (`client/text.c:147`) is what the middle-click popup shows today
  (`fc_client::popup_tile_info`, `mapctrl.cpp:552`, fork `49ba373`); the box shows its terrain, owner and extras lines, plus
  food, shield and trade from `city_tile_output(nullptr, ptile, FALSE, o)` (`common/city.c:1283`, which takes a
  null city for a tile outside any city), refreshed from `map_view::mouseMoveEvent` when the hovered tile changes
  (5.2 item 7).

### 8.5 Sizes and placement at 1x (the same logical sizes at 2x)

| Part | Place | Size |
|---|---|---|
| `top_strip` | page grid row 0, columns 1 and 2 | full width x 32 |
| `edge_column` | page grid column 2, rows 1 and below | 64 x the rest |
| minimap | map child, bottom right as today (`fc_client.cpp:689-698`) | as today |
| `what_next_button` | map child, right-aligned with the minimap, 8 px above it | 224 x 40 |
| `tile_box` | map child, 8 px above `what_next_button` | 224 x 76 |
