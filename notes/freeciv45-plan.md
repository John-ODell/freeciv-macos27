# Freeciv45 build plan

Date: 2026-10-16. Status: proposal; every decision in it is John's.
Labels as in the brief: observed, derived, inferred, unknown. Effort: S about a day, M two to four days,
L a week or more (inferred, each with its test).

Freeciv45 is the game civ45 became on 2026-10-16: an empire game in the style of the fourth game in the series.
Units travel in stacks on a square map, there are many unit types, and the look is modern, with our own art. It
is built on Freeciv 3.2 and is GPL. No Firaxis or 2K code, data, art, text or names are used. Mechanics come from
public descriptions, written in our own words.

Sources: four research reports, written by separate agents from public sources and the Freeciv tree.
- `notes/freeciv45/in-freeciv.md`: how each system maps onto Freeciv 3.2, and a slice plan.
- `notes/freeciv45/video-notes.md`: what a player does and looks at in a mid-game session (a public video).
- The graphics report, which proposes the tileset, the asset list, the art pipeline and the licence rules. It
  quotes John's private art repo, so it is kept with the art, not here; its conclusions are in "Look" below.
- `notes/freeciv45/mechanics.md`: the clean-room mechanics spec. It describes 18 systems from 101 public sources,
  rates each MUST, LATER or SKIP for a first playable, and ends with open questions. Its header records what
  changed after it was written and which of its engine claims were checked against the source.

## Where it stands

| Done | Evidence |
|---|---|
| The one-unit-per-tile hex rules kept as `civ54` for the later engine game | PR 45; `scripts/civ54-rules-test.sh` 11/11 |
| Slice 1: stacks, a square map seen from above that wraps east to west, only the defender dies (`killstack` off), cities work the 21-tile fat cross | PR 47; `scripts/civ45-rules-test.sh` 8/8, control run with killstack on fails; 100-turn autogame, `notes/civ45-planning.md` |
| A first look in the bundled Qt client: trident is offered at pregame; declined, amplio2 draws the square map as diamonds | PR 56; `notes/freeciv45/client-look.md` |

Open from slice 1: `test.sh` reads the installed ruleset unless told otherwise (#48), and the AI's stack use in
later eras (#49). The client look (#50) found a stale line in the tileset dialog (#53) and a missing SVG plugin in
the bundle (#54, and #55 upstream).

## Decisions for John

| # | Question | Recommendation |
|---|---|---|
| 1 | Does Freeciv45 stay "rules and Lua on the stock Freeciv server", so it runs on any Freeciv 3.2 and its servers take stock clients, with our own work allowed in the Mac client? | Yes. Client patches don't change the rules or the network protocol (derived: the server sends the rules to each client, `notes/game-directions.md`). Engine-only systems go to civ54 or upstream. |
| 2 | Combat: fights to the death, with a break-off for fast units; siege units damage whole stacks; bombard range back to 1 (2 was for fifth-game ranged units) | Yes, as the next slice. Stacks with no counter invite one huge stack (inferred). |
| 3 | Map look until our art exists: trident (square, 30 px, dated) as now; amplio2 drawn on the square map (a diamond look, seen in #50); or the `ISO` topology (same rules, amplio2's look) | Keep square with trident for now. The client offers trident at pregame, and a player who declines gets amplio2's diamonds (`notes/freeciv45/client-look.md`). The target is our own 96 px square tileset. |
| 4 | Art: 96 px tiles from 192 px masters; units with one facing in v1 (8 facings later); the proposed "gouache atlas" style; which image tool (OpenAI API, ChatGPT app, Gemini) | Yes to sizes and one facing. Style and tool are John's taste. |
| 5 | Lock `killstack` and `topology` in the ruleset, or leave them as pregame choices? | Leave unlocked, as Freeciv's own webperimental does with killstack (`refs/freeciv-S3_2/data/webperimental/game.ruleset:724`). |
| 6 | Public name "Freeciv45" | Fine as a working name. It follows the "Freeciv21" fork's pattern and avoids "Civilization"/"Civ" (inferred; Freeciv's naming guidance not checked). |
| 7 | One strength number per unit, for attack and defence alike, as in the reference game (spec 2.5, rated MUST), or Freeciv's separate attack and defence values? | One strength, brought in with slice 2 and the roster (slice 10), with an autogame before and after. Freeciv already decides each round by strength share; only the damage per round stays fixed (spec 2.5). |

## Roadmap

Each row is one issue, branch, PR and fork patch, with a rules-test case and an autogame, as slice 1 was.
Slice names use the reference game's terms as working labels only; what ships in the ruleset gets names of its
own, as the clean-room rule asks.

### Rules (ruleset and Lua, runs on stock Freeciv)

| # | Slice | Main change | Effort | Main risk |
|---|---|---|---|---|
| 2 | Combat | Siege "Bombard 2" allowed only against two or more units, so it wounds a stack without killing it; `Combat_Rounds` 0 (to the death) plus a capped break-off for a new `Withdraws` flag; bombard range 1 | S-M | The AI bombards instead of taking cities; tuning |
| 3 | Upgrades, drafting and whipping | Upgrades keep veteran levels; one draft unit per era that costs a citizen, behind a government; whipping as the spec's levy unit, which costs a citizen and is recycled into the build, because Lua cannot shrink a city | S-M | The AI drafts its cities small |
| 4 | Happiness and health from resources | +1 content per luxury and +health per food resource the nation can reach, through a marker building per resource that Lua keeps (an Extra requirement stops at TradeRoute range); the missing resources (horses, copper, stone, marble, aluminium, uranium) | M | Lua decides what counts as connected; its turn-start cost on big maps |
| 5 | Cottages | Four tile improvements that grow while worked and give more trade | M | Growth is random, not a fixed count of turns |
| 6 | Great Generals | Lua counts combat; a General joins a stack to promote it or settles as a military academy | M | The AI never uses it |
| 7 | Leader traits | Trait bonuses per nation, as hidden small wonders at first | M | Picking traits per nation |
| 8 | Culture and civics | A culture rate as a Freeciv "multiplier" slider; culture levels that add city defence (`MinCulture`); civics as governments plus, as the spec proposes, one policy building per column that Lua swaps | M | Five columns of exclusive choices are not native; the AI won't pick policies |
| 9 | Economy | Linear food box, content and health caps at the reference values, national gold upkeep for buildings and units, seven specialists (spec 2.4) | M | Freeciv riots where the reference game idles unhappy citizens (spec question 9) |
| 10 | Roster | The reference game's breadth, about 85 units over seven eras, with class counters, resource gating from slice 4 and a unique unit per nation (spec 2.8) | L | Every unit needs art (T2); balance |
| 11 | Great People and golden ages | Points from buildings and wonders through the blank `User_Effect` slots (Lua finds no specialist count), the seven kinds with their one-off uses, a golden age as a timed national building (spec 2.9) | M | The AI ignores Lua-only systems (spec question 10) |
| 12 | Religion, simplified | Seven Lua-founded religions as city marker buildings with passive spread, temples, state-religion happiness and shrine gold (spec 2.10) | L | The same AI gap; no missionaries at first |

Slice 2 moves first because slice 1 brought stacks back with no counter to them (mapping study, risk column of its slice 1).
Measure the AI (#49) after slice 2. Slices 9 to 12 complete the spec's first playable (its section 3). What it
defers (flanking, first strikes, ratio damage, automatic trade routes, espionage points, corporations, vassals and
votes, random events, AI personalities) waits for civ54 or a later pass.

### Look (tileset and Mac client)

| # | Step | What | Effort |
|---|---|---|---|
| T0 | Test tileset | Two terrains drawn by script, to prove the overhead corner cells and tall layers nobody has tried yet | S |
| T1 | Tileset v0 | Every tag the ruleset needs at 96 px, with scripted placeholders where no art exists yet, so the game loads complete | M |
| T2 | Painted art | About 430 kept cells from 7 sheets made with John's sheet workflow (ground, features, resources, units, cities, tech and building icons), plus about 630 sprites made by script (edges, fog, roads, rivers, overlays) | L, John and Claude |
| Q1 | Smooth Qt map | Non-blocking move animation (GTK has it, Qt doesn't; S) and Retina rendering (the Qt map ignores the display's pixel ratio; M) | M |
| Q2 | Numbers on hover | Tile, unit and city hover summaries and a combat odds tooltip before attacking (the video's top takeaway; Freeciv already computes the odds) | M |
| Q3 | Fast paths | Tech-learned popup (an empty stub in Qt), a chooser when a build completes, the build queue from the map | S-M |

Licence rules for the art: Freeciv45 art ships as GPL-2.0-or-later. Allowed inputs are only CC0, public domain,
CC BY 4.0 and GPL. No CC BY-SA, NonCommercial or NoDerivatives. There is one provenance record per image, and
no game screenshots or other studios' art as references. The OpenAI terms could not be read (HTTP 403 on
2026-10-16), so John records the version he agreed to.

### Engine (civ54 or upstream, not Freeciv45)

True collateral damage and first strikes, a full religion system, a real Great People system, the fourth game's
unhappiness (idle citizens instead of disorder), culture-driven border rings, ratio-based combat damage, Lua calls
that read a unit's hit points or change a city's size (neither exists: `common/scriptcore/tolua_game.pkg:58-66`,
`server/scripting/tolua_server.pkg:118-250`), Extra requirements at Player range, and a 3D client (a Godot front
end on Freeciv's C client core, XL). Lua can already cut hit points after an attack
(`server/scripting/api_server_edit.c:592-598`, signal `action_finished_unit_units`), but without reading them it
cannot keep the cut non-lethal. Some are small and general enough to offer upstream: a border-radius effect, Lua
hit point and city size calls, collateral fields.

## Shipping

Each finished slice goes into the next macOS release (notarized once the Apple ID password is reset) and,
because it is data, into a modpack that stock Windows and Linux Freeciv can load. Client patches ship only in our
Mac app.
