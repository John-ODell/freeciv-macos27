# The Qt client's panels today (survey for the Freeciv45 unit bar and city panel, 2026-10-17)

What the Qt client shows when a unit is selected and when a city is opened, which widget draws each element,
how it is triggered, what data the client already holds, and what a theme can change. Input for the design in
`panels.md` (same folder). Labels: observed (seen in this run or read in the source at the cited line),
inferred (my reading), unverified (not checked).

Setup (observed): `~/freeciv-builds/qt/bin/freeciv-server` reading the fork's `data/` with `rulesetdir civ45`,
`size 2`, `aifill 3`, `revealmap START`, `borders ENABLED`, seeds 7/7; `~/freeciv-builds/qt/bin/freeciv-qt -a
-t trident` on a fresh options file, default theme NightStalker (`client/options.h:404`), on a 2x display,
window 1728x1030 pt. Line numbers are for the fork `port/freeciv` at commit `6777c85`; none of patches 0001-0007
touches `client/gui-qt/`, so they equal upstream S3_2 `44e6898` (observed: `git log 44e6898..HEAD --
client/gui-qt` is empty). Keyboard and mouse automation was blocked by macOS accessibility (osascript "not
allowed to send keystrokes"), so the stack chooser and the middle-click tile popup are described from source,
not screenshots, and the city was founded with the server's Lua console
(`lua cmd edit.create_city(find.player(0), tile, "Lookton")`), which makes the client open the city dialog by
itself because `popup_new_cities` defaults to on (`client/options.c:138`, `client/packhand.c:924-927`).

Screenshots (PNG, quantized, 392 KB in all): `qt-today-map.png` (whole window, explorer in focus, Lookton
founded), `qt-today-unitbar.png` (the unit panel at 2x), `qt-today-sidebar.png` (the left bar at 2x),
`qt-today-citybar.png` (the map's city bar at 2x), `qt-today-city.png` (the city dialog at 1x).

## 1. The game page: who owns which pixels

`fc_client::create_game_page()` builds one grid (`client/gui-qt/pages.cpp:725-806`, observed):

| Element | Widget | Where it is put | Position and size |
|---|---|---|---|
| Left bar | `fc_sidebar` (`sidebar.h:111`, `sidebar.cpp:518`) holding nine `fc_sidewidget`s | column 0 of the page grid when `gui_qt_sidebar_left` (default on, `options.c:381`), else column 2 (`pages.cpp:801-805`) | width = max(80, screen width x 100 / 1920) px, standard widgets share the height (`sidebar.cpp:570-608`) |
| Map | `map_view` (`mapview.h:79`) inside `game_tab_widget` (a `QStackedWidget` of game tabs) | column 1 (`pages.cpp:798-806`) | fills the rest; the reports open as further tabs of the same stack (`add_game_tab`, `pages.cpp:811-818`) |
| Unit panel | `hud_units` (`hudwidget.h:205`) | child of the map (`pages.cpp:788`) | fraction of the map, default x 0.33, y 0.88, saved as `unit_fx`/`unit_fy` (`fc_client.cpp:679-688`); height = map height / 12 (`hudwidget.cpp:605`) |
| Chat and messages | `info_tab` (`messagewin.h:71`) | child of the map (`pages.cpp:791`) | bottom left, 20% x 40% of the map by default (`fc_client.cpp:660-677`) |
| Minimap | `minimap_view` (`mapview.h:218`) | child of the map (`pages.cpp:786`) | bottom right at (0.84, 0.79) (`fc_client.cpp:689-698`) |
| Combat log | `hud_battle_log` (`hudwidget.h:356`) | child of the map, hidden until a fight (`pages.cpp:789-790`) | |
| City dialog | `city_dialog` (`citydlg.h:437`), a `qfc_dialog` = `QDialog` with its own drawn title bar (`dialogs.h:73`) | parented to the map, built once, shown non-modal (`citydlg.cpp:3822-3832`) | saved geometry, else 4/5 x 5/6 of the screen (`citydlg.cpp:2318-2331`); 816x580 pt in this run |
| Stack chooser | `units_select` (`dialogs.h:202`) | child of the map at the cursor (`dialogs.cpp:4831-4860`) | |
| Tile popup | `info_tile` (`mapview.h:116`) | child of the map above the tile (`mapview.cpp:1356-1400`) | |

There is no bottom "game info" bar in the Qt client: the turn, date, gold and research live on the left bar
as text drawn onto the sidebar icons (`fc_client::update_info_label`, `mapview.cpp:999-1056`: calendar and
turn on the View icon at :1022-1027, gold and income on the Economy icon at :1035-1046; research name and
percent on the Research icon from `repodlgs.cpp:1187`). The tax bar and the four indicator sprites are two
non-standard sidewidgets painted in `fc_sidewidget::update_final_pixmap` (`sidebar.cpp:422-466`).

## 2. A selected unit

### 2.1 Trigger

The unit panel follows the focus list, not the mouse. `unit_focus_set()` (`client/control.c:518-569`) ends in
`focus_units_changed()` (`control.c:215-221`), which calls `update_unit_info_label()` and `menus_update()`.
The Qt side of the first only refreshes an already visible panel (`mapview.cpp:1066-1071`); the panel is
shown from `real_menus_update()`, which calls `unitinfo_wdg->update_actions(nullptr)` whenever menus are
rebuilt (`menu.cpp:530-542`, observed). `hud_units::update_actions` hides the frame when
`head_of_units_in_focus()` is null and shows it otherwise (`hudwidget.cpp:598-601`, `:792`). So the panel
appears on turn start (auto focus), on a map click that focuses a unit, and after every order, and vanishes
when no unit is in focus.

A left click on the map goes `map_view::mousePressEvent` (`mapctrl.cpp:521-527`) to `shortcut_pressed`
(`:214-480`): the select button (left, no modifier, `shortcuts.cpp:76`) calls
`action_button_pressed(SELECT_FOCUS)` on press (`:453-461`) and `SELECT_POPUP` on release (`:497-511`); both
reach `do_map_click()` (`control.c:2921-3005`), which focuses a lone own unit (`:2976-2989`) or pops the stack
chooser for several units (`:2996-3001`). The stack chooser is `units_select`: a pixmap grid of the tile's
units built in `create_pixmap()` (`dialogs.cpp:4876`), hover shows "activity HP:a/b" (`:5076-5100`), a left
click calls `unit_focus_set` on that unit (`:5042-5065`). Keys: `v` selects all on the tile, `Shift+V` the
same type (`menu.cpp:1158-1164`).

### 2.2 What is drawn (observed, `qt-today-unitbar.png`)

`hud_units` is a `QFrame` with an `QHBoxLayout` of three parts (`hudwidget.cpp:523-556`):

| Part | Source |
|---|---|
| Unit sprite with the move points painted on it ("1" bottom left, fractions drawn as a small stacked fraction) | `put_unit()` onto a canvas, cropped and scaled to the panel height (`hudwidget.cpp:650-668`); move text in white (`:681-737`) |
| Terrain sprite of the unit's tile | `put_terrain()` cropped and scaled (`:741-756`) |
| One text line "EXPLORER MP: 1 HP:10/10 +2 UNITS" (name, home city in brackets when it has one, moves, hit points, stack count or "Selected N units") | `:622-648`; `move_points_text()` (`common/movement.c:1047`), fuel appended for fuelled types |
| A row of square action buttons | `unit_actions` (`:938-1184`) |

Tooltips: the unit sprite shows `popup_info_text(tile)` (`:757`, text from `client/text.c:147`), the terrain
sprite `popup_terrain_info` (`:758`). Font: `fonts::notify_label`, forced uppercase bold at 90% of the label
height (`:603-604`, `:646-648`). The panel can be dragged by its `move_widget` corner handle (`:554`,
`mapview.cpp:407-430`) and remembers where it was (`hudwidget.cpp:565-571`).

### 2.3 The action buttons

`unit_actions::update_actions()` (`hudwidget.cpp:973-1184`) rebuilds the row for the head focus unit on every
refresh, in this fixed order, each only when its test passes: build city, mine, plant, irrigate, cultivate,
transform, road, goto (always), fortify, sentry, board, set home city, upgrade, auto worker, paradrop, clean,
deboard, nuke, wait (always), done (always). Each button is a `hud_action` (`:823-933`): a square of the
panel's height x 0.8 (`:1173-1175`), the theme PNG stretched to fill, a 1 px rectangle in the palette Text
colour, a Highlight fill on hover (`:843-866`). A click runs `gui()->menu_bar->execute_shortcut(id)`
(`:930-933`), which looks up the menu action by its key sequence (`menu.cpp:1847-1867`), so the bar can only
offer what the Unit/Work/Combat menus offer, and only shortcuts in `shortcut_id` (`shortcuts.h:33-96`). The
tooltip is the menu text (`:1172`). Not in the bar today: pillage (menu only, `Shift+P`, `menu.cpp:1299-1301`),
disband (`Shift+D`, `:1270-1271`), explore (`x`), patrol (`q`). Keys the bar's actions answer to
(`shortcuts.cpp:57-160`): B build city, M mine, I irrigate, R road, G goto, F fortify, S sentry, L board, U
deboard, H home, Shift+U upgrade, A auto worker, P clean, W wait, Space done.

### 2.4 Data the client already has for a unit

`struct unit` (`common/unit.h`): `moves_left` :149, `hp` :150, `veteran` :151, `fuel` :152, `activity` :156,
`homecity` :145, `upkeep[O_LAST]` :147, `goto_tile` :154, `done_moving` :180, `has_orders` :192 and the
`orders` block :198. The type gives attack, defence, firepower, move rate and max hp. Text helpers:
`move_points_text` (`movement.c:1047`), `utype_veteran_name_translation` (`common/unittype.c:2610`),
`unit_upkeep_astr` (`common/unit.c:1239`, "Food/Shield/Gold: f/s/g"), `unit_activity_astr` (`:1163`),
`unit_description` (`client/text.c:482`, name, veteran name, upkeep, activity, home, nearest city). Combat:
`unit_win_chance` (`common/combat.c:478`), `get_total_attack_power` (`:610`), `get_total_defense_power`
(`:767`), `get_defender` (`:836`); `combat_odds_to_astr` (`common/clientutils.c:310-345`) already writes
"Chance to win: A:95% D:46%" plus A/D/FP/HP lines, and the tile popup includes it when a focus unit could
attack there (`text.c:417`). This is the only place the odds appear today: the middle-click `info_tile` popup
(`mapctrl.cpp:464-468`, `:552-575`). Sprites: the tileset draws the hit point bar and veteran chevrons into
the unit sprite (`client/tilespec.c:4741-4747`), which is why the panel's unit image carries a green bar.

## 3. A clicked city

### 3.1 Trigger

A left click on an own city tile (release, `SELECT_POPUP`) reaches `do_map_click`, which calls
`popup_city_dialog(pcity)` when the player can see the city's internals (`control.c:2969-2972`). That queues
`CU_POPUP_DIALOG` (`client/update_queue.c:623-627`) and the queue runs `qtg_real_city_dialog_popup`
(`citydlg.cpp:3822-3832`): one `city_dialog` is built lazily and `setup_ui(pcity)` + `show()` + `raise()`.
Ctrl+click on a city opens the quick production chooser instead and Ctrl+Shift+click the quick buy
(`mapctrl.cpp:325-333`, `:418-425`; `shortcuts.cpp:72-75`). A city's units on the tile are reached by clicking
the tile when the city is foreign or when a unit is in focus and the tile holds one unit (`control.c:2990-2993`).
The dialog closes on its own only when the tileset changes (`mapview.cpp:1270-1271`); the X button hides it
(`citydlg.cpp:1711`).

### 3.2 What is drawn (observed, `qt-today-city.png`)

`city_dialog::city_dialog` (`citydlg.cpp:1506-2068`) is a splitter of two columns:

| Area | Widgets | Data |
|---|---|---|
| Title "Lookton - 10,000 citizens" | `update_title` (`:3789`) | `city_name_get`, `city_population` |
| Citizens row (top left) | `city_label` + pixmap (`:2908-2990`) | `get_city_citizen_types(FEELING_FINAL)` (`client/citydlg_common.c:1201`), citizen sprites |
| Previous / next / close / happiness / counters buttons | 64 px `QPushButton`s (`:1702-1746`) | |
| Info grid: Size, Food, Prod, Trade, Gold, Luxury, Science, Granary, Change in, Corruption, Waste, Culture, Pollution, Plague risk, Tech Stolen, Airlift | 16 label pairs from the `city_info` enum (`citydlg.h:50-86`), filled by `update_info_label` (`:3143-3261`) | `pcity->prod[]`, `surplus[]`, `waste[]` (`common/city.h:355-358`), `food_stock`/`shield_stock` (`:367-368`), `city_granary_size` (`common/city.c:2146`), `city_turns_to_grow` (`:1996`), `client.culture` (`city.h:465`), `city_illness_calc` (`city.c:2884`); tooltips from `get_city_dialog_output_text` (`citydlg_common.c:748`) |
| City map, worked tiles ringed, + and - zoom | `city_map` (`:1227-1354`) | `city_dialog_redraw_map` into a canvas; left click toggles a worker via `city_toggle_worker` (`citydlg_common.c:1571`); right click gives a worker-task menu (`:1356`) |
| City name button | `lcity_name` (`:1545`), click renames (`:2383`) | |
| Worklist group: filter checkboxes, Buy (with price), the production progress bar, add/up/down/remove, the queue table | `:1584-1586`, `:1788-1830`; progress `progress_bar` (`citydlg.h:111`) set by `update_building` (`:3443-3466`); queue filled by `update_improvements` (`:3552-3620`) | `get_city_dialog_production` (`citydlg_common.c:260`, "x/y N turns"), `city_production_build_shield_cost`, `client.buy_cost` (`city.h:466`), `city_get_queue`; clicking the bar opens `production_widget` (`show_targets`, `:3646`); Buy calls `city_buy_production` (`citydlg_common.c:1552`); change goes through `city_change_production` (`:1287`) |
| Present units, Supported units, Improvements (with total upkeep) | `unit_info`/`unit_item` rows (`:1056`, `:663-735`), `impr_info`/`impr_item` (`:472`, `:367`), filled by `update_units` (`:3297-3353`) and `update_improvements` (`:3511-3546`) | `pcity->tile->units`, `pcity->units_supported`, `collect_already_built_targets`, `city_improvement_upkeep`; a unit item's right-click menu activates, sentries, fortifies, disbands, upgrades (`:750-880`) |
| Happiness page (behind the switch button): six rows Cities, Luxuries, Buildings, Nationality, Units, Wonders, plus a nationality table | `:1842-1872`, `show_happiness` (`:2140`) | `get_city_citizen_types` per `citizen_feeling`, tooltips `text_happiness_*` (`client/text.c:1832-2104`), `pcity->feel[][]` (`city.h:333`) |
| Governor: presets, sliders, Enable, Save | `:1874-2000`, `update_cma_tab` (`:2612`) | `cmafec_*` |

Everything is sized by font metrics and fixed pixel counts (`int h = 2 * fm.height() + 2` at `:1529`, 64 px
buttons, 20 px zoom buttons at `:1600`), not by the display's pixel ratio.

## 4. What a theme can change, and what is code

`qtg_gui_load_theme` (`client/gui-qt/themes.cpp:46-102`) reads `themes/gui-qt/<name>/resource.qss`, sets the
Fusion style and installs the file as the application stylesheet. Icons come from
`themes/gui-qt/<name>/<id>.png`, falling back to `themes/gui-qt/icons/<id>.png` (`fc_client.cpp:1046-1071`);
the action icons are the files `home`, `mine`, `irrigation`, `buildroad`, `goto`, `fortify`, `sentry`,
`load`, `unload`, `set_homecity`, `upgrade`, `automate`, `paradrop`, `clean`, `nuke`, `wait`, `done`
(`data/themes/gui-qt/icons/`, 54 PNGs). Themeable through the stylesheet (NightStalker addresses these class
names): `hud_units` and `hud_units QLabel` (`resource.qss:858-865`), `hud_action` (`:853`), `fc_sidewidget`
(`:843`), `units_select` (`:761`), `info_tile` (`:359`), `info_tab` (`:629`), `minimap_view` (`:318`),
`city_dialog` and its push buttons, group boxes, tables and scroll areas (`:578-620`), `QToolTip` (`:517`).
Hard-coded in C++ (observed): the panel height (map / 12) and the square button size (`hudwidget.cpp:605-608`,
`:1173-1175`), the white move-points overlay (`:713`), the uppercase bold text (`:603-604`), the sidebar width
formula and the yellow label colour `QColor(232, 255, 0)` (`sidebar.cpp:576-578`, `:418`), the hover and
disabled overlays (`:480-503`), the city dialog's button sizes and layout, the stack chooser's drawing
(`dialogs.cpp:4876-5000`). Fonts are options (`gui_qt_font_notify_label` and friends, `client/options.h:410-417`),
picked at first run by `configure_fonts` (`fonts.cpp:150-175`).

## 5. Retina (plan row Q1) and the Qt version

Every canvas is a plain `QPixmap(width, height)` at logical size (`canvas.cpp:36-42`), and `map_view::paint`
copies the map store 1:1 (`mapview.cpp:291-296`), so on a 2x display the OS doubles every pixel: the map, the
unit and terrain images in the panel (`qt-today-unitbar.png`), the city map and the citizen sprites. The only
pixel-ratio read in the client is for font sizing (`fonts.cpp:164`). Zoom is a tileset re-read at a scale
(`menu.cpp:3325-3326`), not a pixel ratio. The build links Qt 6.12.0 from Homebrew's `qtbase`
(`build-qt/meson-logs/meson-log.txt:3504`; `otool -L` on `freeciv-qt`), while the source keeps `FC_QT5_MODE`
branches (for example `hudwidget.h:166-170`), so a client patch should compile under Qt 6 and leave the Qt 5
branches alone.

## 6. Switches the client already has

Qt-only booleans are declared with `GEN_BOOL_OPTION(..., COC_INTERFACE, GUI_QT, default, callback)` in the
options table (`client/options.c:3293-3296` for `gui_qt_sidebar_left`), stored in `gui_options`
(`client/options.h:405-423`), and may get a change callback in `qtg_options_extra_init`
(`client/gui-qt/gui_main.cpp:255-266`). The three `gui_qt_show_*_panel` flags are instead read and written by
hand in the options file code (`options.c:6023-6031`, `:6218-6223`). A "new panels" switch fits the first
pattern. Related player options: `popup_new_cities` (`options.c:138`), `center_when_popup_city` (`:132`),
`keyboardless_goto` (`:142`), `draw_full_citybar` (`:189`, the map's city bar in `qt-today-citybar.png` drawn by
`show_full_citybar`, `client/mapview_common.c:1907`).

## 7. What this means for the design

- The focus list is the right hook for a bottom bar: `focus_units_changed` already fans out to
  `update_unit_info_label` and `real_focus_units_changed` (`gui_main.cpp:352-363`, a Qt stub that only
  refreshes the stack chooser and goto dialog). A new bar can be fed from `update_unit_info_label`
  (`mapview.cpp:1066`) with no change to common code.
- The action row is a list of (test, shortcut id, icon) triples; a new bar can reuse the same tests and
  `execute_shortcut`, and add pillage and disband only by giving them shortcut ids (they are menu actions
  with hard-coded key sequences today, `menu.cpp:1270`, `:1299`).
- Everything a city panel needs is in `struct city` on the client and in `citydlg_common.c`; the full dialog
  computes it all in `refresh()` (`citydlg.cpp:2992-3022`), which a panel can mirror for its subset.
- The city bar on the map is drawn by common code into the map canvas (`mapview_common.c:1907-2210`), so a
  round city marker is either a tileset change (the `citybar` sprites in `data/misc/citybar.spec`) or a Qt
  overlay widget on the map; see `panels.md`.
- Sprites must be drawn at 2x for Retina before any of this looks modern (plan row Q1).
