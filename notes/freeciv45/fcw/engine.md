# FCW (fcw.org-server): engine and client study for Freeciv45

Date: 2026-10-18. Read-only study. Path prefixes: **FCW** = `~/Desktop/freeciv-port/refs/fcw.org-server`,
**UP** = `~/Desktop/freeciv-port/refs/freeciv-web` (upstream, last commit 2025-05-02), **S32** =
`~/Desktop/freeciv-port/refs/freeciv-S3_2`. JS paths are under `FCW/freeciv-web/src/main/webapp/javascript/`
(written `js/`). Labels: **[SP]** = matters to a single-player desktop game. Line numbers are approximate.

## Most useful for us

1. **Stack-kill casualty reports, and escape from a stack kill** (`FCW/freeciv/freeciv/server/unittools.c` ~2500-3010).
   The server lists every unit lost per player, and a defender can escape to a free tile on a dice roll. This is
   close to Civ4's stack combat and should be written fresh as our own GPL-2.0+ C. [SP]
2. **Unit-type icons inline in message text.** The server tags unit names with a marker
   (`server/unittools.c` ~222, `get_web_unit_icon`). The client swaps each marker for a small picture
   (`js/emoji_list.js`, `webapp/images/e/`, 724 PNGs). Our badges and log could do the same with tileset sprites.
3. **Keys act on the hovered city.** Hover a city and press B to buy, R to set a rally point; shift-right-click
   copies a production target and pastes it into another city (`js/control.js` ~2661-2760, ~3600-3800). New for us,
   cheap to add in `mapctrl.cpp`.
4. **City-bar display modes cycled by one key.** The bar shows size, turns to finish, buy cost, growth, surplus,
   pollution or corruption (`js/2dcanvas/mapview.js:69`). Fits our city marker (panels.md 3.1).
5. **Stack drawing modes.** A ring plus a small "+" for stacks, with per-unit-type offsets so badges sit on each
   sprite (`js/2dcanvas/tilespec.js` ~780-870, `create_unit_offset_arrays`). Fits the stack chips and unit flags.
6. **Empire overview tables** (`js/empire.js`): units by type, by home city with upkeep, units in each city, a
   cities-by-buildings grid, an upkeep grid, and every city's worklist with cut and paste. Fits hud-layout.md
   section 4 (overview screens).
7. **The city list's mass actions** (`js/city.js` ~3260-4200). Clicking a building icon changes production in the
   selected cities; shift-click highlights the cities that have it; ctrl-click selects the cities building it;
   "buy all selected". Fits the economy overview.
8. **Battle odds calculator** (`js/warcalc.js`), a closed-form win chance and expected hit points. A natural
   companion to our unit card and hover tooltip (Q2).
9. **The tile popup built by the server** (`server/maphand.c` ~2690-2960): yields with a bonus or penalty arrow
   and the raw value, the bribe cost for your own units, and output limited to what the player can see. Ideas
   for our tile box (panels.md 8.4).
10. **For a browser build later:** S32 already builds a JSON server with `-Dserver=freeciv-web`
    (`S32/meson_options.txt:72`). FCW's thin proxy (`FCW/freeciv-proxy/civcom.py`) shows how little sits between a
    browser and that server.

## 1. Server base and C changes

**Base.** FCW vendors a full, heavily changed tree, not a patch set. `FCW/freeciv/freeciv/fc_version` says
3.0.92-dev (the 3.1 development line). `FCW/freeciv/advanced_backports.txt` gives the baseline as freeciv master
`2e2ce4b` "as of 12-Nov-21", plus a few cherry-picks. The patch step in `FCW/freeciv/prepare_freeciv.sh` is
commented out, and `freeciv/patches/` (29 files, listed in `apply_patches.sh`) is history that already lives in
the tree. Most of FCW's own work is edited straight into the tree with no patch file. The `//` comment style
marks it (upstream Freeciv uses `/* */`): 116 such lines in `server/unithand.c`, 93 in `unittools.c`, 55 in
`cityturn.c`, 40+ in `common/city.c` and `common/unittype.[ch]`. Upstream Freeciv-web instead patches freeciv
master 3.3-dev (`UP/freeciv/version.txt`, Aug 2024). A clean divergence diff would need commit 2e2ce4b, which
the local shallow clone at `refs/freeciv` lacks.

**Gameplay** (new server settings not in S32, from `server/settings.c`):
- Combat: extended bombard with max targets, max kills, move cost, attack modifier and retaliation rounds. The
  data is packed into bits of unused unit-type fields so savegames still load (`common/unittype.h` ~547-650,
  `unittype.c` ~2520-2650). Also iPillage, an instant pillage with odds (`unittype.h` ~622, `js/pillage_dialog.js`);
  stack-kill escape and reports (item 1); capturing units that carry cargo (`unithand.c` ~393). [SP]
- `fusion` H-bomb and reworked nuke damage (`unittools.c` ~3300-3380); `nukes_minor`/`nukes_major` switches. [SP]
- `autoattack_style` and a "vigil" order that limits auto-attack to units on watch (`unittools.c` ~3847-3950). [SP]
- Cities: `city_output_style` ("WYSIWYG" output when size changes, `cityturn.c` ~926); `hangry` (starving
  cities riot, `cityturn.c` ~1244); `fulldisorder`; `slot_control` for building several different units in one
  turn from the worklist (`common/city.c` ~770-950, `cityturn.c` ~2742); migrants with zero population cost; the
  default governor applied by the server (`cityturn.c` ~406-470, `cityhand.c` ~592). [SP]
- Movement: `zoc_purity`, `universal_unload`/`unload_override`, `move_bonus_in_frags`
  (`common/aicore/path_finding.c` ~650-780, `common/map.c` ~792-861). [SP]
- Diplomacy: `casusbelliturns`, `armisticelength`, `ceasefirelength`, plus a reworked pact table
  (`server/diplhand.c` ~600-735, `actiontools.c` ~125-161); investigate-city odds shown to the player, and a
  Siege Ram that skips diplomatic combat (`diplomats.c` ~349-392, ~2111). [SP, partly]
- Economy, map and misc: `blueprints` (tech theft gives bulb credit, `techtools.c` ~379, ~1350); `looting`;
  `killcitizen_pct`; `trademinforeign`; `airliftdestdivisor`; the "Pax Dei" wonder counter (`srv_main.c` ~1520);
  a climate-change rework with thaw safeguards (`srv_main.c` ~769-862, `map.c` ~713-754); map generator
  `polarstrip`, `singlepole`, `alltemperate`, more rivers, hills before mountains in the cold
  (`generator/mapgen.c` ~320, ~1497); small wonders count toward score (`score.c` ~319). [SP]

**AI.** No AI features. There are crash guards only: `patches/ai_traits_crash.patch`,
`patches/freeciv_segfauls_fix.patch` (diplomat with no goto tile), and a role fix in `ai/default/aiunit.c` ~2441.
S32 has none of these guards (`S32/ai/aitraits.c:71`), so check whether the crashes happen in 3.2 before taking
any of them. [SP]

**Protocol and web.** The server sends the client things a full client computes itself:
- Goto and rally paths: `PACKET_GOTO_PATH_REQ/GOTO_PATH` and `PACKET_RALLY_PATH_REQ`
  (`common/networking/packets.def` ~2366-2395, `unithand.c` ~3787).
- The tile popup text: `PACKET_INFO_TEXT_REQ/MESSAGE` (`patches/maphand_ch.patch`, `maphand.c` ~2961).
- City buildable lists and output strings (`patches/freeciv_web_packets_def_changes.patch`,
  `city_impr_fix2.patch`).
- Text markup uses angle brackets (`freeciv-svn-webclient-changes.patch`) and is escaped against script injection
  (`message_escape.patch`).
- Plus `server_password.patch`, `metachange.patch`, `load_command_confirmation.patch`, `savegame.patch`, and the
  ISO/HEX/WRAPY topologies blocked under `FREECIV_WEB` (`settings.c` ~1303).

None of this matters to our Qt client. Most of the web packets went into S32 itself (`S32/.../packets.def`
~2444-2476).

**Longturn.** `patches/longturn.patch`: pick a nation in a running game; latejoiners get techs and gold
(`connecthand.c` ~112-166, `latejoin_gold`); `unitwaittime_style`; delayed orders (`unittools.c` ~5454);
anonymous player names separate from account names (`connecthand.c` ~623, `handchat.c` ~447). Not for us.

**Bug fixes.** `activity_null_check.patch`; `mapimg_bugfix.patch` (a divide by zero); a resource-extra fix in
`common/tile.c` ~981; a fix for recursive continent renumbering in `maphand.c` ~1937; `navajo-remove-long-city-names`
and `pragma_pack_city_length` (city names longer than the limit). Only the tile.c and maphand.c fixes look worth
re-checking on 3.2. [SP]

## 2. Web client features

Compared with UP's `js/` folder, FCW adds about 310 functions and four new files: `empire.js`, `warcalc.js`,
`emoji_list.js`, `tracklist.js`.

- **City dialog** (`webclient/city.hbs`, `js/city.js`, 4548 lines against UP's smaller one).
  - Tabs: Overview, Production, Trade routes with revenue totals, Happiness broken down by cause
    (`show_city_happy_tab`), Governor (`js/cma.js`, sliders, copy and paste, apply to all), Settings.
  - A specialist picker in the title bar (`toggle_specialist_control_pane`).
  - Rally points, one-time or kept (`city_rally_row`).
  - Clicking a worked tile on the main map, with no dialog open, toggles it (`control.js:2748`).
  - Maps onto the **city overlay slice**. The happiness breakdown and the worked-tile toggle from the main map
    are the new parts.
- **Tech tree** (`js/tech.js`, `js/reqtree.js`): hand-placed layouts for each ruleset
  (`reqtree_multiplayer`, `_civ2civ3`, `_mpplus`, ...), drawn on a canvas. It highlights the prerequisites of
  the goal and research already possible, shows an info box and Wikipedia summaries, and pops up a dialog when a
  tech is gained. The Qt tree already does most of this. New for us: the goal path highlight and hiding units
  the server settings forbid.
- **Unit orders and goto** (`js/control.js`, 7715 lines; `webclient/orders.jsp`).
  - An icon panel with the hotkey in each tooltip, plus a "more orders" expander.
  - "Go and...": goto, then do the last chosen action (`key_unit_go_and` ~6667).
  - Rally goto, connect, vigil, board and deboard.
  - Select all units on a tile, the same type on a tile, the same type on a continent or everywhere
    (~4953-5035), and "only units waiting for orders" (`key_filter_for_units_in_queue`).
  - Focus lock and auto-centre.
  - The goto path comes from the server.
  - Maps onto the **unit bar** (panels.md 2.3-2.4). The selection filters are new and fit a Civ4-style stack UI.
- **Tooltips and help.** The server-built tile popup (item 9). Action buttons show success odds
  (`action_dialog.js:294`). The help manual has a facts pane with exact costs and strengths
  (`js/helpdata.js`), and city items carry tooltips (`city.js` ~577-900). Maps onto the **tile box** (8.4) and Q2.
- **Overview and minimap** (`js/overview.js`): a bitmap drawn from a palette, redrawn only when a hash of the
  grid changes (`generate_overview_hash`), and a mode with dull terrain that shows diplomatic colours. Maps onto
  the minimap. The hash skip is worth copying.
- **Notifications and messages** (`js/messages.js`, `packhand.js`).
  - Each event type has its own CSS class.
  - Tile and unit links are clickable and centre the map with a marker (`recenter_flare_tile`).
  - Governor messages are sent to the Governor tab (`handle_city_governor_event`).
  - Old event sounds are muted after a reconnect (`suppress_event_sound`).
  - Unit icons appear inline in the text.
  - Maps onto the **badges slice** and the log. The per-event routing and inline icons are new.
- **Hotkeys** (`control.js` ~3434-4090).
  - Shift plus a letter opens a tab.
  - Keys act on the hovered city (item 3).
  - Ctrl-shift-C cycles the city bar; shift-S cycles the stack mode.
  - Border modes: flags, a three-colour scheme, "moving borders" (`mapview.js` ~655-775).
  - A chalkboard mode (alt-X) for drawing notes on the map (`tilespec.js` ~488, `get_user_mark_sprite`).
  - Mostly new; map onto the unit bar keyboard and the edges.
- **Mobile and touch.** Small-screen and touch branches throughout `city.js`, minimise and maximise for the
  message box on mobile (`messages.js` ~199-215), and Hammer.js bundled (`js/libs/hammer.min.js`). `js/mobile.js`
  only handles rotation. Not relevant on macOS.
- **Rendering.** FCW is 2D canvas only; the WebGL folder has been removed (`index.jsp:50` keeps a dead debug hook).
  - Iso drawing is a port of the C painter's algorithm `gui_rect_iterate`, layer by layer
    (`js/2dcanvas/mapview_common.js` ~308-520).
  - Each sprite is cut from the atlas once into its own canvas (`mapview.js:236`).
  - The whole map is redrawn at most every 35 ms on `requestAnimationFrame` (`mapview_common.js` ~639-675).
  - Map scrolls slide using an oversized back buffer (`mapview.js` ~956-1030).
  - It draws an iso tileset (amplio2, `tileset_config_amplio2.js`) on a non-iso map, since ISO topology is
    blocked. Nothing here is faster than the C `mapview_common.c` we already have. The redraw throttle and the
    per-layer timing counters are the only takeaways.
  - Our **slide slice** (`slide/slide.md`) already covers unit animation.

## 3. The WebGL / 3D renderer

It exists only in UP (`UP/freeciv-web/src/main/webapp/javascript/webgl/`, about 3500 lines), not in FCW.
- three.js, MIT (`webgl/libs/three.min.js`), with its Water2, Reflector and GLTFLoader helpers.
- The terrain is one plane mesh. The heightmap is built at 4x4 vertices per tile from terrain height plus
  distance from coast or river, then smoothed (`heightmap.js`).
- A fragment shader picks the terrain texture per pixel from a small "tile-type" bitmap, one coloured pixel per
  tile (`map_tiletype_renderer.js`, `shaders/terrain_fragment_shader.glsl`). Borders and roads come from further
  lookup textures.
- Units and cities are glTF `.glb` models named after the ruleset unit (`webapp/gltf/`, 71 files, sources in
  `UP/blender/`). Labels are billboards; trees and jungle are sprites.
- Licences: the code is AGPL. For the models, `UP/blender/CREDITS` names opengameart "Blender models for Freeciv
  units", with some blendswap models it calls public domain. No licence file covers `gltf/` or `textures/`, so
  each source needs checking before reuse (unverified).
- For a native client: the shader trick (a tile-type lookup texture plus a texture atlas, blended in one pass)
  and the coast-distance heightmap are ideas we could rebuild in Metal or Qt RHI. The code itself can't be used.
  It is far from our iso sprite path; at most it is reference for a later 3D mode.

## 4. Packaging and runtime

- Browser, then nginx, then **freeciv-proxy** (Python and Tornado, one per server).
- The proxy reads the server's 2-byte length plus JSON frames and batches them into WebSocket arrays
  (`freeciv-proxy/civcom.py`).
- **Publite2** keeps a pool of `freeciv-web` server processes ready, per game type (`publite2/civlauncher.py`,
  `pubscript_singleplayer.serv`: `set topology WRAPX`, `aifill 8`).
- A Java/Tomcat webapp handles login, the metaserver, saves, hall of fame and PBEM, backed by MySQL
  (`freeciv-web/src/main/java/...`, `docker-compose.yml`, `Vagrantfile`).
- Even single-player runs one server process per game on the host.
- Assets and protocol are generated from Freeciv: `scripts/freeciv-img-extract/img-extract.py` builds sprite
  atlases and a JS tilespec, and `scripts/generate_js_hand/` builds JS packet handlers from `packets.def`.

For a later "Freeciv45 in the browser": rebuild our patched 3.2 server with `-Dserver=freeciv-web` and put a
small WebSocket bridge like civcom in front of it. The client would be the hard part. Options are FCW or UP's
AGPL client (all of it AGPL), or a WebAssembly build of our own Qt client, which would keep everything GPL.
Publite2, Tomcat and MySQL only matter for a public multiplayer site.

## 5. Licences

- The client JS is AGPL-3.0. Reuse ideas only; no code goes into our GPL-2.0+ C or Qt patches.
- The vendored server is GPL-2.0+. FCW's C edits could legally be adapted, but they are woven into a 3.1-dev
  tree and packed into savegame bitfields; rewriting is cleaner than porting.
- `freeciv-proxy` and the img-extract and generator scripts carry GPL-2.0+ headers, not AGPL
  (`civcom.py`, `img-extract.py`).
- **Art and music: be careful.** `js/tracklist.js` warns that the music and imagery may not be GPL and may be
  absent from the public repo. `FCW/music/` has named composers' tracks with no licence file. The emoji set
  (`images/e/`) and order icons have no stated source.
- The bundled libraries (jQuery, Hammer, SweetAlert, Morris, Raphael, three.js) are MIT or BSD.
- UP's 3D models and textures have no licence file.
- Our non-commercial status doesn't change any of this; copying art needs a licence either way.
