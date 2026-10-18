# Freeciv45 win conditions: implementation-ready design

Date: 2026-10-17. Status: design for the civ45-rules session to implement as one ruleset slice. Every decision
in "Open questions for John" is his. Labels as in the other notes: observed (read at the cited place), derived,
inferred, unverified.

Paths: `up/` is `refs/freeciv-S3_2/` (3.2.6+, commit 44e6898c), `civ45/` is `port/freeciv/data/civ45/` at fork
commit f55003f (the committed state; the fork's working tree carries uncommitted slice 2 edits that this note
does not cite). Spec: `notes/freeciv45/mechanics.md` section 2.17 (six victories, MUST for conquest, culture,
space and score, LATER for domination and diplomatic). Feasibility: `notes/freeciv45/in-freeciv.md` only notes
that `edit.player_victory` exists; this note fills in the rest. Roadmap: `notes/freeciv45-plan.md`.

## 1. Summary

Freeciv45 ships six ways to win. Four are stock Freeciv settings, one is a Lua turn-start check, one is the
stock "allied" rule standing in for a vote until a later slice.

| # | Win | Freeciv45 rule | Mechanism | Native? |
|---|---|---|---|---|
| 1 | Conquest | Every rival is dead or has surrendered | `check_for_game_over()` single-victor branch | Yes |
| 2 | Domination | Own 60% of the land tiles and 50% of the world's citizens for 3 turns running | Lua on `turn_begin`, then `edit.player_victory` | Lua |
| 3 | Cultural | National culture at or above a threshold and well ahead of the second player | `victories` CULTURE plus `[culture]` keys | Yes |
| 4 | Space | A spaceship launched and arrived | `victories` SPACERACE, `endspaceship` | Yes |
| 5 | Diplomatic | The last alliance standing wins together (a vote comes later) | `victories` ALLIED | Yes (vote: Lua, later) |
| 6 | Time | The game ends at a fixed turn and the highest score wins | `endturn`, score table, Lua names the winner | Yes (announcement: Lua) |

The engine checks them in a fixed order every turn end (`up/server/srv_main.c:363-680`, called from `:3007`):
scenario winners (Lua or a `Victory` effect, `:372-394`), team victory (`:426-460`), allied (`:469-521`), conquest
(`:524-546`), culture (`:550-572`), turn limit (`:575-584`), spaceship arrival (`:600-660`). All observed.

## 2. Each win, mapped

### 2.1 Conquest (native)

- Rule: when exactly one non-barbarian player is alive and not surrendered, and at least one other player is
  dead or surrendered, that player wins (`up/server/srv_main.c:396-416,524-546`, observed).
- With ALLIED on, a defeated player who was allied to the victor does not count as a defeated enemy
  (`:532-533`, observed): a conquest win needs at least one non-allied victim.
- Nothing to set. Barbarians and animals never count (`:405-407`).

### 2.2 Domination (Lua)

No engine rule reads land or population share, and no requirement type can express either (checked against
the requirement list in `up/doc/README.effects:58-119`, observed), so this is a Lua script on `turn_begin`
(`up/server/scripting/script_server.c:424`). The pieces it needs all exist (observed unless marked):

| Need | Lua | Where |
|---|---|---|
| All tiles | `whole_map_iterate()` | `up/common/scriptcore/tolua_game.pkg:815-817` |
| Tile owner and terrain | `tile.owner`, `tile.terrain` | `:70-71` |
| Land or water | `terrain:class_name()` returns `"Land"` or `"Oceanic"` | `:507`; `up/common/scriptcore/api_game_methods.c:981-987` |
| All players | `players_iterate()` | `:805-812` |
| Alive | `player.is_alive` | `:39` |
| Barbarian or animal | `player.nation:rule_name()` is `"Barbarian"` or `"Animal Kingdom"` | `:37,429`; `up/data/nation/singlebarbarian.ruleset:5`, `animals.ruleset:5`; civ45 includes no pirate nation (`civ45/nations.ruleset`) |
| Citizens | `player:cities_iterate()` and `city.size` | `:733-735,264-265` |
| Win | `edit.player_victory(player)` sets the winner status; the game ends at that turn's end as a "scenario victory" | `up/server/scripting/tolua_server.pkg:207-208`; `up/server/srv_main.c:372-394` |
| Memory across saves | scalar globals only, so one global per player id | `up/common/scriptcore/tolua_common_a.pkg:137-170` |

Sketch (the slice writes the real one in `civ45/script.lua`):

```lua
-- Domination: 60% of land tiles and 50% of citizens, three turns in a row.
FC45_DOM_LAND_PCT = 60
FC45_DOM_POP_PCT  = 50
FC45_DOM_TURNS    = 3
FC45_DOM_FROM_TURN = 100   -- no check before this turn: nobody can qualify and the map walk costs time

local function fc45_is_civ(p)
  local n = p.nation:rule_name()
  return p.is_alive and n ~= "Barbarian" and n ~= "Animal Kingdom"
end

function fc45_domination_check(turn, year)
  if turn < FC45_DOM_FROM_TURN then return end
  local land, owned = 0, {}
  for tile in whole_map_iterate() do
    if tile.terrain:class_name() == "Land" then
      land = land + 1
      if tile.owner then owned[tile.owner.id] = (owned[tile.owner.id] or 0) + 1 end
    end
  end
  local pop, pops = 0, {}
  for p in players_iterate() do
    if fc45_is_civ(p) then
      local s = 0
      for c in p:cities_iterate() do s = s + c.size end
      pops[p.id] = s; pop = pop + s
    end
  end
  for p in players_iterate() do
    if fc45_is_civ(p) then
      local key = "fc45_dom_run_" .. p.id          -- scalar global: survives save and load
      local ok = land > 0 and pop > 0
        and (owned[p.id] or 0) * 100 >= land * FC45_DOM_LAND_PCT
        and (pops[p.id] or 0) * 100 >= pop * FC45_DOM_POP_PCT
      _G[key] = ok and ((_G[key] or 0) + 1) or 0
      if _G[key] >= FC45_DOM_TURNS then
        notify.all(_("The %s rule the known world."), p.nation:plural_translation())
        edit.player_victory(p)
      end
    end
  end
end
signal.connect("turn_begin", "fc45_domination_check")
```

Notes, all derived unless marked:
- "Land" means owned land tiles, worked or not; ocean tiles are left out so coastal borders do not inflate the
  share. The score's `landarea` counts the same thing in C (`up/server/score.c:161-212`) but Lua cannot read
  it, hence the map walk.
- Population is the sum of city sizes, which is what the score calls citizens (`up/server/score.c:355`).
- Three turns in a row stops a one-turn spike from a captured city deciding the game.
- Cost: one pass over the map and all cities per turn. At `tilesperplayer` 100 and 12 players the map is about
  2,500 tiles (`civ45/game.ruleset:919,926`); unverified, measure in the autogame (section 4).
- `player_victory` makes the server announce "Scenario victory to the X" (`up/server/srv_main.c:391`); the
  notify line above gives the player the real reason first.
- Allies: with ALLIED on, an alliance that jointly passes the thresholds does not win here; the thresholds are
  per player. Open question 2.

### 2.3 Cultural (native)

- Rule: the player with the most culture wins when its culture is at least `victory_min_points` and more than
  `(100 + victory_lead_pct)%` of the second player's (`up/server/srv_main.c:550-572`, observed). Culture is the
  national history plus every city's culture (`up/server/score.c:278`, `player_culture()`).
- Keys: `civ45/game.ruleset:383-388` (`[culture] victory_min_points = 20000`, `victory_lead_pct = 100`), flag
  CULTURE in `victories` (`:920`). All observed.
- Pace today (observed in the Freeciv45 slice 1 autogame, `logs/test-qt-20261016-175736/freeciv-T0101-Y00001-final.sav.gz`):
  at turn 101 the twelve players' culture runs from 206 to 519, the best scores 43 to 117. In the older hex game
  at turn 201 (`logs/test-qt-20261016-144233/freeciv-T0201-Y01500-final.sav.gz`) the range is 577 to 3,244.
  Culture sources are the `History` effects, 1 to 6 per building or wonder, and 10 or 5 for celebrating cities
  (`civ45/effects.ruleset:2050-3845`, `produce_culture1/2`), with `history_interest_pml = 0` (`game.ruleset:393`).
- Derived: at that pace 20,000 is reached around turn 600 by the best AI, after the turn limit below, so today's
  key is a dead letter. The culture slice (roadmap row 8) will add a culture rate and more sources, so the number
  must be re-tuned then; until then the recommendation in section 3 makes it reachable by a builder who commits.

### 2.4 Space (native)

- Rule: SPACERACE in `victories` lets players build the ship; with `endspaceship` TRUE (default,
  `up/common/game.h:585`) the game ends when a ship arrives and its owner wins (`up/server/srv_main.c:600-660`,
  observed). The arrival year is set at launch from the ship's mass and `spaceship_travel_pct` (default 100,
  `up/server/spacerace.c:119`, `up/common/game.h:587`), so the ship must also complete its flight, as the spec
  asks (section 2.17).
- Parts are the three `Special` buildings behind Apollo Program's `Enable_Space` (`civ45/buildings.ruleset:1338-1347`
  for Space Structural; `civ45/effects.ruleset` `apollo_program_1`, observed). Their techs are Space Flight,
  Superconductors and Environmentalism; the tech-tree design keeps them in the last era.
- If a ship arrives, `rank_users()` marks every other player surrendered for the ranking (`up/server/score.c:445-461`).

### 2.5 Diplomatic: allied now, a vote later

- ALLIED semantics (`up/server/srv_main.c:469-521`, observed): when more than one candidate is left and every
  alive, non-barbarian, non-surrendered player is allied with every other (an alliance treaty or the same team,
  `pplayers_allied()`), all of them win together. It fires only after everyone outside the alliance is gone, so it
  is "the last alliance standing", not a vote. Keep it on: it is what lets a human and an AI partner finish a
  game together, and it changes conquest as 2.1 says.
- In AI-only games (issue 84, decided 2026-10-17 as plan decision 13): ten AIs can ally into a single alliance
  long before anyone is beaten, and then they all win at once: turn 142 on seeds 42/42 with no attack in the whole
  game, where on seeds 11/11 the AIs kept 10 to 20 pairs at war through turn 400. The rule stays as it is; it
  needs every living player in the alliance, so a human decides whether it can fire. Autogames that must run
  to their end turn ALLIED off with `--extra "set victories SPACERACE|CULTURE"`, and `scripts/test.sh` reports a
  game that ends by a victory as a pass that names the turn.
- Changed 2026-10-18 (issue 159): the single bloc came from the AI level. Every game before that day ran at the server's
  default, Easy, which adds handicaps Normal lacks, among them `H_CEASEFIRE` (a cease-fire offer at first contact),
  `H_DIPLOMACY` and `H_DEFENSIVE` (`ai/difficulty.c`); which of them builds the bloc was not isolated.
  civ45's game.ruleset now sets `ailevel` to Normal, and the fork's server gives a ruleset's level to the AIs that
  aifill made in pregame before the ruleset loaded (`server/settings.c`, `settings_ruleset`). On seeds 42/42, where
  every pair was allied from T200 to T350 at Easy (balance report 1, b1), 29 to 38 of 55 pairs are at war from T100
  to the end, with 1,730 attacks (`logs/test-qt-20261018-160612`, `notes/freeciv45/balance-2.md`).
- A real vote needs Lua, and Lua cannot read diplomatic states or the AI's attitude: `tolua_game.pkg` and
  `tolua_server.pkg` have no diplstate, alliance or "love" getter (grep for those words, 2026-10-17, observed
  absence). The one known door is an effect with a `DiplRel` requirement read through
  `effects.unit_bonus(unit, other_player, "User_Effect_3")`, which takes an "other player"
  (`up/common/scriptcore/tolua_game.pkg:646-648`; that a `DiplRel` req resolves there is inferred). The vote
  slice can decide; it waits for the religion and congress wonders (roadmap rows 11 and 12).

### 2.6 Time limit on score

- `endturn` ends the game at the end of that turn (`up/server/settings.c:2908-2913`; default 5000,
  `up/common/game.h:395`). The server announces "turn limit was exceeded" and marks nobody a winner
  (`up/server/srv_main.c:575-584`); `rank_users(TRUE)` then ranks by score, but only writes a file when the
  server was started with `--ranklog` (`up/server/score.c:417-429`). All observed. There is no `endvictory`
  setting in 3.2 (grep of `settings.c`, observed absence).
- Score (`up/server/score.c:351-362`, observed): citizens + 2 per tech + 5 per wonder + spaceship score +
  units built / 10 + units killed / 3 + culture / 50. Lua reads it with `server.civilization_score(player)`
  (`up/server/scripting/tolua_server.pkg:49-50`).
- Freeciv45 rule: at the start of the last turn, Lua names the highest-scoring living player the winner with
  `edit.player_victory`, so the game ends with a named victor instead of a bare turn-limit notice. The turn is
  read from `server.setting.get("endturn")` (`up/server/scripting/tolua_server.pkg:56-58`), so the rule follows
  whatever endturn the host sets.
- Calendar: `civ45/effects.ruleset:3985-4041` steps the year by 50, 25, 20, 10, 5, 2 and 1; from 4000 BC that
  reaches 1 AD at turn 101, 1000 at 151, 1500 at 201, 1750 at 251, 1900 at 326 and 2050 at turn 476 (derived
  by summing the steps; unverified against a long autogame).

## 3. Recommended settings

All go in `civ45/game.ruleset` `[settings]` (the `set` table from `:917`) unless marked. Locks stay FALSE,
as decision 5 of the plan keeps map and killstack unlocked.

| Key | Today | Recommended | Why |
|---|---|---|---|
| `victories` | `SPACERACE\|ALLIED\|CULTURE` | same | All three native wins stay on; see 2.1 to 2.5 |
| `endspaceship` | engine default TRUE | `"endspaceship", "ENABLED", FALSE` written out | The ship must arrive, as the spec says; writing it makes the rule visible |
| `spaceship_travel_pct` | 100 | 100 | No reason to change until the space era is tuned |
| `endturn` | engine default 5000 | 475 | The turn the calendar reaches 2050 (2.6); a game that reaches it ends on score |
| `[culture] victory_min_points` | 20000 | 8000 | Reachable near turn 350 to 400 by a player who builds for culture at today's pace, which is after space parts become possible, so the two races overlap (derived from 2.3; re-tune after roadmap row 8) |
| `[culture] victory_lead_pct` | 100 | 50 | Needing double the runner-up punishes a two-builder game; half again still demands a clear lead |
| Domination (Lua) | none | land 60%, citizens 50%, 3 turns, from turn 100 | A map share that needs real conquest on a 12-player map (the best AI holds about 15% of the land at turn 101: 185 of about 1,200 land tiles, `landarea` in the T101 save); citizens stop a land-rich, city-poor empire winning on borders alone |

`citymindist`, `tilesperplayer` and `aifill` stay as they are (`civ45/game.ruleset:919-929`).

## 4. Test plan

Rules test, new cases in `scripts/civ45-rules-test.lua` (runs at turn 12 of a 40-turn game with the human
"Tester", `scripts/civ45-rules-test.sh:17-40`):

| Case | How | Pass when |
|---|---|---|
| Settings | `server.setting.get("victories")`, `("endturn")`, `("endspaceship")` | `"SPACERACE\|ALLIED\|CULTURE"`, `"475"`, `"ENABLED"` (the string forms are `up/server/settings.c:4145-4154`; the bitwise form is unverified: print it once and fix the expected value) |
| Culture keys | `game.info` has no culture fields (`tolua_game.pkg:128-140`), so read `civ45/game.ruleset` with `luadata` is not possible either; check by grep in the shell script | `victory_min_points = 8000`, `victory_lead_pct = 50` |
| Domination unit test | Set `FC45_DOM_LAND_PCT = 0`, `FC45_DOM_POP_PCT = 0`, `FC45_DOM_TURNS = 1`, `FC45_DOM_FROM_TURN = 0`, call `fc45_domination_check(12, 0)` | Every living civ is marked winner: the server log ends the game with "Scenario victory" naming all of them |
| Domination negative | Thresholds back to 60/50/3, call again | No winner; the `fc45_dom_run_*` globals are 0 |
| Domination counts | A copy of the count loop in the test compares its land total with `whole_map_iterate` minus `"Oceanic"` tiles | Equal |
| Score winner | Set `endturn` to 13 through `--extra "set endturn 13"` in a second run | At turn 13 the log has "Scenario victory to" the player with the highest `server.civilization_score` |

Autogame, 10 AIs, seeds 42/42, data from the source tree:

```bash
FREECIV_DATA_PATH=port/freeciv/data scripts/test.sh ~/freeciv-builds/qt --ruleset civ45 --no-client --turns 480
```

Check in the final save: `culture=` and `landarea=` per `[scoreN]` block, the `Game ended` line in
`autogame.log` (turn limit, a scenario victory, or a culture win), and the wall time of the `turn_begin` walk
(compare with the slice 1 run's 38 s for 100 turns, `notes/civ45-planning.md:191`). If an AI wins by culture
before turn 400, raise `victory_min_points`; if none passes 4,000 by turn 475, lower it.

## 5. What the spec says that the ruleset does not

- Spec 2.17 rates domination and diplomatic LATER; this note ships domination now because it is one Lua
  function, and keeps diplomatic at the allied rule.
- `victory_min_points 20000` is unreachable at today's culture pace (2.3), so the CULTURE flag that
  `civ45/game.ruleset:920` enables has never been able to fire.

## Open questions for John

1. Domination thresholds: 60% land and 50% citizens for 3 turns, or the spec's "about 65% land plus a population
   lead" (section 2.17 of mechanics.md, which also says the reference game varies them)?
2. Should an alliance win domination jointly (sum the allies' land and citizens)? Lua cannot see alliances
   (2.5), so "yes" means the `DiplRel` trick or waiting for an engine getter.
3. `endturn` 475 (the year 2050) as the shipped default, or leave the engine's 5000 and let hosts set it?
4. Culture: 8000 and a 50% lead now, knowing row 8 of the roadmap will change the pace, or leave 20000 until
   that slice lands?
5. Should the score winner at `endturn` be announced through Lua (2.6), or is the plain turn-limit ending enough?

## Implementation order

1. `civ45/game.ruleset`: `[settings]` rows for `endspaceship` and `endturn`; `[culture]` keys.
2. `civ45/script.lua`: `fc45_domination_check` and the end-turn score winner, both on `turn_begin`; constants at
   the top of the file so the test can override them.
3. `scripts/civ45-rules-test.lua`: the six cases above; `scripts/civ45-rules-test.sh` unchanged.
4. `civ45/README.civ45` and the `game.ruleset` summary text (`:39-49`): one paragraph on the six wins.
5. Fork patch 0009 (0008 is slice 2's), the autogame, and the "Where it stands" row in `notes/freeciv45-plan.md`.
