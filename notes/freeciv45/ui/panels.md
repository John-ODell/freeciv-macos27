# Freeciv45 panels for the Qt client: the unit bar and the city panel (issue 91, 2026-10-17)

A design for two panels in `client/gui-qt`, a mockup drawn here (`panels-mockup.svg`), and the plan to build
them as a client patch. The survey `qt-today.md` (issue 85) is the source for every "today" claim and every
`file:line` below; the line numbers are for the fork at commit `6777c85`, where `client/gui-qt/` equals upstream
S3_2 `44e6898`. Labels: observed (in the survey or read at the line), inferred (my design reasoning), John's
(a decision for him, collected in section 6). Clean room: nothing here copies another studio's layout, icons,
text or names; the behaviour comes from John's two sentences, Freeciv's own data, and ordinary UI practice.

John's brief, in his words: the bottom bar "usually sits on a unit and is clicked into"; the left bar "is the
same but on a city, a small circle"; today's panels are "a very old and friction-full design". Read as: the
bottom of the screen belongs to the selected unit and is where its orders are clicked; the left of the screen
belongs to the city you clicked, opened from a small round marker on the map; both appear only when there is
something to show.

## 1. Principles

1. **A panel exists only while its subject is selected.** The unit bar shows when the focus list is non-empty
   and hides when it is empty (today's `hud_units` already does this, `hudwidget.cpp:598-601`). The city panel
   shows after a click on a city marker and closes on Escape, on its close button, on a click on another
   marker (which swaps the city), or when the city is lost.
2. **Everything on a panel is already in the client.** No new packets, no server changes. Each element below
   names its field or helper. The full city dialog stays as the long form behind one button (John's, section 6).
3. **Logical pixels, Retina-clean.** Sizes are given at 1x; at 2x the same logical sizes apply, QPainter draws
   text, bars and borders crisp by itself, and the only blurry parts are tileset sprites until the 2x art exists
   (plan rows Q1 and T0 to T2 in `notes/freeciv45-plan.md`). Panel pixmaps get `setDevicePixelRatio` so the
   OS does not double them a second time.
4. **One switch.** A Qt client option `gui_qt_freeciv45_panels` (default on in Freeciv45 builds, see 5.7)
   turns both panels off and brings back `hud_units` and the direct city dialog, so a before/after screenshot
   is one option flip apart.
5. **Keyboard first, mouse second.** Every action button shows its key, and the keys are the ones the Qt
   client already binds (`shortcuts.cpp:57-176`), so the bar teaches the shortcuts instead of competing with them.

## 2. The unit bar (bottom, centred on the map)

Mockup: `panels-mockup.svg`, group `unit_bar`. Class `unit_bar` (new file `unitbar.cpp/.h`, section 5.1).

### 2.1 Where and when

- A child of `map_view`, like `hud_units` (`pages.cpp:788`), centred horizontally, 12 px above the map's
  bottom edge, re-centred in `fc_game_tab_widget::resizeEvent` next to the existing calls (`fc_client.cpp:1094-1126`).
- Shown and refreshed from `update_unit_info_label()` (`mapview.cpp:1066-1071`), which common code calls on
  every focus change (`control.c:215-221`) and after orders; hidden when `head_of_units_in_focus()` is null.
  Unlike today's panel it is shown from that hook, not from `real_menus_update` (`menu.cpp:530-542`), so it
  never waits for a menu rebuild.
- Not draggable (the position is part of the design); the old panel's `unit_fx`/`unit_fy` settings
  (`fc_client.cpp:679-688`) are left alone for the off-switch case.

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
| **Portrait** | The head focus unit's sprite, cropped and scaled into the 80 px box, with a 6 px health bar below (green above 2/3, yellow to 1/3, red below). Click centres the map on the unit. Tooltip: `unit_description()`. | `put_unit()` into a canvas as today (`hudwidget.cpp:650-668`, `mapview_common.c:1399`); `punit->hp` and `unit_type_get(punit)->hp` (`common/unit.h:150`); `unit_description` (`client/text.c:482`) |
| **Name and veteran level** | "Warriors" bold; second line the veteran rank name and the home city in brackets, or "no home". | `unit_name_translation`, `utype_veteran_name_translation(ptype, punit->veteran)` (`common/unittype.c:2610`, `unit.h:151`), `player_city_by_number(owner, punit->homecity)` (`unit.h:145`) |
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

## 3. The city marker and the city panel (left, over the map)

Mockup: `panels-mockup.svg`, groups `city_marker`, `city_panel`, `odds_tooltip`. Classes `city_marker`
(painted in `map_view::paint`) and `city_panel` (new file `citypanel.cpp/.h`), section 5.1.

### 3.1 The marker

- A round badge, 28 px across at 1x, drawn over the city tile's centre after the map store is painted
  (`map_view::paint`, `mapview.cpp:291-296`), for every own city on screen and for foreign cities whose size
  the player can see. It shows the city size, uses the owner's nation colour as its fill (the map already has
  `get_player_color`, used for borders), a thin light ring, and a second ring while that city's panel is open.
  A city working under the governor gets a small dot.
- Clicking inside the circle opens the panel. The hit test runs in `map_view::shortcut_pressed` before the
  select button falls through to `action_button_pressed` (`mapctrl.cpp:453-461`): if the press is within 14 px
  of an own city's marker centre, open or swap the panel and return. A click elsewhere on the city tile keeps
  today's meaning (the stack chooser or the full dialog, per `do_map_click`, `control.c:2969-3001`).
- Shift+click on the marker opens the full dialog directly (John's, section 6). Ctrl+click and
  Ctrl+Shift+click keep their quick production and quick buy meaning (`mapctrl.cpp:325-333`, `:418-425`).
- The tileset's bar under the city (name, growth, production; `show_full_citybar`, `mapview_common.c:1907`)
  stays; it is common code and a tileset matter. Hiding it when the marker is on is a later option.

Data: `city_size_get`, `city_owner`, `tile_to_canvas_pos` (`mapview.cpp:105` shows the call), `cma_is_city_under_agent`.

### 3.2 The panel: where and when

- A child of `map_view` docked to its left edge (x = 0 of the map, which is right of `fc_sidebar`), full map
  height, 320 px wide at 1x; the same logical width at 2x. Its content scrolls when taller than the map.
- Opens on a marker click (3.1), on `popup_city_dialog` for the player's own city when the switch is on (so a
  newly founded city opens the panel, not the dialog: `qtg_real_city_dialog_popup`, `citydlg.cpp:3822`, routes
  there), and from the Cities report's "open" action.
- Refreshes from the same queue as the dialog: `qtg_real_city_dialog_refresh` (`citydlg.cpp:3870-3881`) calls
  the panel's `refresh()` when it shows that city; `qtg_city_dialog_is_open` (`:3925`) reports the panel too,
  which keeps `packhand.c:1100` from popping a second window.
- Closes on Escape, its close button, a marker click on another city (swap), `qtg_popdown_city_dialog`
  (`:3850`), and when the city is lost (`pcity` null in `refresh()`, as `citydlg.cpp:3011-3013` handles it).
- While open: the chat/messages widget (`info_tab`, default at x 0 of the map, `fc_client.cpp:660-677`) is
  moved right of the panel when it would overlap, and put back on close; the minimap, the unit bar and the
  combat log stay where they are. The old full dialog is not opened; if it is already open it is hidden.

### 3.3 Elements, top to bottom

| Element | Behaviour | Data source (observed) |
|---|---|---|
| **Header: size and growth** | The round marker repeated at 24 px with the size, the city name (click renames), "grows in N turns" or "starving in N turns" or "growth blocked", and "granary f/F". Previous/next city arrows and a close X on the right. | `city_size_get`, `city_name_get`, `city_turns_to_grow` (`common/city.c:1996`: positive, negative for famine, 0 blocked, `FC_INFINITY` never), `pcity->food_stock` and `city_granary_size` (`city.h:367`, `city.c:2146`); rename as `city_dialog::city_rename` (`citydlg.cpp:2383`); next/previous as `:3373-3441` |
| **Yields** | Five tiles: food, shields, trade, gold, bulbs, each the surplus (or the amount for gold and bulbs) with the full breakdown as tooltip. Luxury joins when non-zero. | `pcity->surplus[]`, `prod[]`, `waste[]` (`city.h:355-358`), formatted as `update_info_label` does (`citydlg.cpp:3160-3178`); tooltips `get_city_dialog_output_text` (`citydlg_common.c:748`) |
| **Production** | The current build with its sprite, "s/S shields, N turns", a thin progress bar, a Change button and a Buy button with the price (disabled when it cannot be bought, tooltip says why). Below, the queue as numbered rows with turns; a row's right-click menu moves or removes it; "+ add to queue" opens the chooser in queue mode. Change opens the existing chooser (`production_widget`) anchored to the panel; double-click there changes now, Shift+double-click adds last. | `pcity->production`, `shield_stock` (`city.h:368`), `city_production_build_shield_cost`, `get_city_dialog_production` (`citydlg_common.c:260`); `client.buy_cost` (`city.h:466`), `city_buy_production` (`citydlg_common.c:1552`); `city_get_queue` (`:1469`), `city_queue_insert` (`:1411`), `city_set_queue` (`:1486`), `city_change_production` (`:1287`); chooser `production_widget` (`citydlg.cpp:4521`) |
| **Citizens: happiness and health** | A row of small circles, one per citizen in the final feeling (green happy, grey content, red unhappy, blue specialists), with the count as text; below it "health: plague risk p%  pollution n", and when the city is disorderly or celebrating a one-line notice. Tooltip on the row: the six happiness causes. | `get_city_citizen_types(pcity, FEELING_FINAL, ...)` (`citydlg_common.c:1201`), `pcity->feel[][]` and `specialists[]` (`city.h:333-336`); `city_illness_calc` (`city.c:2884`, tenths of a percent, only when `game.info.illness_on`), `pcity->pollution`; `city_unhappy`, `city_celebrating` (`city.c:1626`, `:1645`); tooltips `text_happiness_*` (`client/text.c:1832-2104`) |
| **Buildings** | A plain list of the built improvements with the upkeep total in the heading; hover gives the help text; right-click offers sell (confirmation box). Wonders first. | `collect_already_built_targets` and `city_improvement_upkeep` as `update_improvements` uses them (`citydlg.cpp:3531-3546`); `impr_item`'s sell path (`citydlg.cpp:619`) |
| **Worked tiles on the map** | A "Show on map" toggle, on by default while the panel is open: the city's workable tiles are ringed on the main map, worked ones solid with their food/shield/trade numbers, free ones dashed. Clicking a ringed tile toggles its worker (specialist or worker). Off when the panel closes. | The map already does both halves: `toggle_city_color(pcity)` (`mapview_common.c:1501-1509`) makes the tileset draw `worked_tile_overlay` and `unworked_tile_overlay` for that city (`tilespec.c:5113-5121`), and `draw_city_output` adds the numbers (`:5122-5134`); the click is `adjust_workers_button_pressed` (`mapctrl_common.c:598-620`), today bound to Meta+Ctrl+click (`shortcuts.cpp:78-79`), which the panel re-routes from a plain click while it is open |
| **Units** | "Units here N, supported M": chips as in the unit bar; click focuses the unit and the unit bar takes over; the supported list is behind a disclosure. | `pcity->tile->units`, `pcity->units_supported`, as `update_units` (`citydlg.cpp:3297-3353`); upkeep overlay sprites `put_unit_city_overlays` (`mapview_common.c:1463`) |
| **Open full dialog** | A full-width button at the bottom, also Enter: hides the panel and calls today's `city_dialog` for the governor, the nationality table, counters, airlift and everything else. | `qtg_real_city_dialog_popup` with the switch bypassed (`citydlg.cpp:3822-3832`) |

### 3.4 Keyboard

- Escape closes the panel (then, as today, `key_cancel_action`, `mapctrl.cpp:191-195`). Enter opens the full
  dialog. Left/Right arrows with the panel focused go to the previous/next city (the dialog's buttons,
  `citydlg.cpp:3373`). `c` centres the map on the city (today's Center View key does this for the focus unit).
- Tab walks the Change, Buy, queue and toggle controls. The chooser keeps its own keys.

### 3.5 Theming

Class names: `city_panel`, `city_panel QLabel`, `city_section` (the small caps headings), `yield_tile`,
`prod_row`, `citizen_dots`, `city_marker` colours as four theme properties (fill, ring, open ring, text). The
panel's width and the marker's radius are not themed in the first slice (section 5.5 lists them as a later
option).

## 4. What is hidden, and the two panels together

| Situation | Unit bar | City panel | Today's widgets |
|---|---|---|---|
| Unit in focus, no city open | shown | hidden | `hud_units` hidden (switch on) |
| City panel open, unit still in focus | shown | shown | chat moved right of the panel |
| City panel open, nothing in focus | hidden | shown | |
| Switch off | hidden | hidden | `hud_units`, full dialog on click, as in `qt-today.md` |
| Full dialog open | shown | hidden | the dialog as today |

Both panels are map children, so reports in other game tabs (`add_game_tab`, `pages.cpp:811`) cover them as
they cover the minimap today.

## 5. Implementation plan (client patch on `client/gui-qt`)

### 5.1 New code

| File | Class | Role |
|---|---|---|
| `client/gui-qt/unitbar.h/.cpp` | `unit_bar : QFrame` | the bottom bar: `refresh(unit_list *)`, `show_for(unit *)`, hide when empty; owns `unit_chip` and `unit_action_button` |
| | `unit_chip : QAbstractButton` | one stack chip; paints the unit sprite from a canvas, ring when focused |
| | `unit_action_button : QAbstractButton` | icon + key hint; carries a test function and a handler |
| | `odds_tooltip` (free functions) | `odds_text_for(tile *)` building the tooltip from `combat_odds_to_astr`; `show_odds_tooltip(QPoint, tile *)` |
| `client/gui-qt/citypanel.h/.cpp` | `city_panel : QFrame` | the left panel: `open_for(city *)`, `refresh()`, `close_panel()`; sections as child widgets |
| | `city_marker` (free functions) | `paint_city_markers(QPainter *)` called from `map_view::paint`; `city_marker_at(QPoint) -> city *` for the hit test |
| `meson.build` | | add the four files to the Qt client's source and moc lists (`meson.build:3508-3570`) |

### 5.2 Hooks into existing code (small, named edits)

1. `client/options.h` and `options.c`: `gui_qt_freeciv45_panels` as a `GEN_BOOL_OPTION(..., COC_INTERFACE,
   GUI_QT, TRUE, panels_changed)` after `gui_qt_sidebar_left` (`options.c:3293`); the callback in
   `gui_main.cpp` next to `apply_sidebar` (`gui_main.cpp:263`) shows or hides the panels at once.
2. `pages.cpp:788`: create `unit_bar` and `city_panel` as map children next to `unitinfo_wdg`.
3. `mapview.cpp:1066` `update_unit_info_label`: when the switch is on, `unit_bar->refresh(punitlist)` and keep
   `hud_units` hidden; else today's code.
4. `hudwidget.cpp:598` `hud_units::update_actions`: return after `hide()` when the switch is on (so the old
   panel never pops from `real_menus_update`).
5. `mapview.cpp:291` `map_view::paint`: after the store, `paint_city_markers(painter)` when the switch is on.
6. `mapctrl.cpp:453` `shortcut_pressed`: before the select-button block, if the switch is on and
   `city_marker_at(pos)` is an own city, open the panel and return (Shift opens the dialog). While the panel is
   open and "show on map" is on, a plain click on a ringed tile of that city calls
   `adjust_workers_button_pressed(pos)` and returns.
7. `mapctrl.cpp:537` `mouseMoveEvent`: `show_odds_tooltip(event->globalPosition(), tile)` after `control_mouse_cursor`.
8. `citydlg.cpp:3822` `qtg_real_city_dialog_popup`: with the switch on, open the panel for own cities unless a
   "force full dialog" flag is set by the panel's button and the Shift+click path; `qtg_real_city_dialog_refresh`
   (`:3870`) and `qtg_city_dialog_is_open` (`:3925`) consult the panel too; `qtg_popdown_city_dialog` (`:3850`)
   closes it.
9. `fc_client.cpp:1094` `resizeEvent`: re-centre the bar and re-dock the panel; move the chat when it overlaps.
10. Theme files: a `unit_bar`/`city_panel` block appended to the three `resource.qss` files with the defaults.

No change to `common/` or `client/*.c`; everything is reachable from the Qt side (observed in the survey).

### 5.3 The minimum first slice (one PR, one patch `0008`)

Unit bar only, with the switch: portrait and health bar, name and veteran line, "str / moves / hp" line, stack
chips (click and Shift+click), and five actions: fortify (F), sentry (S), go to (G), skip (W), done (Space).
Hidden when nothing is in focus; `hud_units` hidden while the switch is on. No tooltip, no city work.
Acceptance: `scripts/ruleset-look.sh` with the civ45 ruleset shows the bar at turn 1 for the start stack; the
option off restores today's panel; both screenshots in the PR. Diff prepared in `first-slice.diff` (section 7).

### 5.4 What follows, in order

1. Build (B: found city / road / mine / irrigate), pillage, upgrade, disband and the second action row; key
   hints re-read from `fc_shortcuts`; `[` `]` chip cycling.
2. The combat odds tooltip (plan row Q2).
3. The city marker and the panel header, yields and production with Change, Buy and the queue (the common
   case the video notes call the build bar from the map).
4. Citizens, health, buildings, units here; the "open full dialog" button and the popup routing (5.2 item 8).
5. Worked tiles on the map with the click routing (5.2 item 6, second part).
6. Retina: `setDevicePixelRatio(2)` on the panel canvases and SVG icons (needs plan row Q1 for the map itself).
7. Theme blocks for Classic and Necrophos; later, the marker radius and panel width as theme properties.

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
- **Worked-tile clicks** change a plain click's meaning while the panel is open; the ring makes it visible,
  and the toggle turns it off. Rally points and trade routes keep their own hover modes.
- **Upstream drift.** `client/gui-qt/` is unchanged by patches 0001 to 0007; a rebase onto a later S3_2 may
  move the hook lines but not their functions.

### 5.6 How to test

- Option: `gui_qt_freeciv45_panels` in Game > Options > Interface; off reproduces `qt-today.md`.
- Screenshots before and after through `scripts/ruleset-look.sh <client> OUT --ruleset civ45 -- -t trident`,
  which captures turn 1 with the start stack in focus (the bar shows), and the same with the option off in a
  copied options file. City screenshots need either the Lua city trick from the survey or the input scripting
  in issue 87.
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

## 7. The prepared first slice

The unit bar of 5.3 is prepared under issue #95 as `first-slice.diff` in this folder: a diff against the
fork's `client/gui-qt`, unapplied, with build notes, what was tested and what was not in `first-slice.md`, and
screenshots `first-slice-on.png` (the bar), `first-slice-bar.png` (the bar alone) and `first-slice-off.png` (the
option off, today's panel back). It is not in `patches/` and the fork is untouched by this work.
