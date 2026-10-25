-- SPDX-License-Identifier: GPL-2.0-or-later
-- Research observer for a Freeciv45 (civ45) autogame. Load it before the game starts, for example
--   scripts/test.sh ~/freeciv-builds/qt --ruleset civ45 --no-client --lua scripts/civ45-tech-log.lua
-- It changes nothing. It prints one server-log line per tech a player learns, so the pace of the tree can be
-- read afterwards with scripts/civ45-tech-summary.py (which knows each tech's era from the design note):
--   FC45TECH turn T <player> learned <tech> by <source>
-- The source is "researched", "learned" (traded, conquered, stolen), "lost" or whatever the server passes.

function fc45_tech_learned(tech, player, source)
  log.normal("FC45TECH turn %d %s learned %s by %s", game.turn(), player.name, tech:rule_name(), tostring(source))
end

signal.connect("tech_researched", "fc45_tech_learned")
log.normal("FC45TECH observer loaded at turn %d", game.turn())
-- SPDX-License-Identifier: GPL-2.0-or-later
-- Combat observer for a Freeciv45 (civ45) autogame. Load it before the game starts, for example
--   scripts/test.sh ~/freeciv-builds/qt --ruleset civ45 --no-client --lua scripts/civ45-combat-log.lua
-- It changes nothing. It prints one server-log line per attack-type action, per unit lost and per city that
-- changes hands, so the log can be counted afterwards (grep FC45COMBAT / FC45LOST / FC45CITY):
--   FC45COMBAT turn T <action> ok|failed <actor type> of <player> -> (x,y) units <n left> city <name>|-
--   FC45LOST turn T <unit type> of <player> reason <reason>
--   FC45CITY turn T <city> from <player> to <player> reason <reason>
-- The actor is "dead" when it did not survive its own action.

local watched = { ["Attack"] = true, ["Suicide Attack"] = true, ["Bombard"] = true, ["Bombard 2"] = true,
                  ["Bombard 3"] = true, ["Bombard Lethal"] = true, ["Capture Units"] = true,
                  ["Collect Ransom"] = true, ["Wipe Units"] = true }

function fc45_combat_action(action, success, actor, tile)
  local name = action:rule_name()
  if not watched[name] then return end
  local who = "dead"
  if actor ~= nil then who = actor.utype:rule_name() .. " of " .. actor.owner.name end
  local city = tile:city()
  log.normal("FC45COMBAT turn %d %s %s %s -> (%d,%d) units %d city %s", game.turn(), name,
             success and "ok" or "failed", who, tile.x, tile.y, tile:num_units(),
             city and city.name or "-")
end

function fc45_combat_lost(unit, player, reason)
  log.normal("FC45LOST turn %d %s of %s reason %s", game.turn(), unit.utype:rule_name(), player.name, reason)
end

function fc45_combat_city(city, old_owner, new_owner, reason)
  log.normal("FC45CITY turn %d %s from %s to %s reason %s", game.turn(), city.name,
             old_owner and old_owner.name or "-", new_owner and new_owner.name or "-", reason)
end

signal.connect("action_finished_unit_units", "fc45_combat_action")
signal.connect("unit_lost", "fc45_combat_lost")
signal.connect("city_transferred", "fc45_combat_city")
log.normal("FC45COMBAT observer loaded")

-- Night 5 (balance report 5): who starts where, and who gets the wonders. It changes nothing in the game, except
-- that FC45_NO_DOMINATION = true (set by the runner before this file) moves the domination check past the game's end.
if FC45_NO_DOMINATION then FC45_DOM_FROM_TURN = 100000 end

local function fc45_is_land(t) return t.terrain:class_name() == "Land" end

function fc45_bias_starts()
  -- Land components, 8-connected, by flood fill from each player's first unit.
  local comp, size, nextid = {}, {}, 0
  local function fill(t0)
    nextid = nextid + 1; local todo, n = {t0}, 0; comp[t0.id] = nextid
    while #todo > 0 do
      local t = table.remove(todo); n = n + 1
      for nb in t:square_iterate(1) do
        if comp[nb.id] == nil and fc45_is_land(nb) then comp[nb.id] = nextid; table.insert(todo, nb) end
      end
    end
    size[nextid] = n
  end
  local land, conts = 0, 0
  for t in whole_map_iterate() do
    if fc45_is_land(t) then
      land = land + 1
      if comp[t.id] == nil then fill(t); conts = conts + 1 end
    end
  end
  local per = {}
  for p in players_iterate() do
    if fc45_is_civ(p) then
      for u in p:units_iterate() do
        local c = comp[u.tile.id] or 0; per[c] = (per[c] or 0) + 1
        log.normal("FC45START %s | %s | continent %d of %d tiles", p.name, p.nation:rule_name(), c, size[c] or 0)
        break
      end
    end
  end
  local shared = 0
  for c, n in pairs(per) do shared = shared + 1 end
  log.normal("FC45MAP land %d tiles, %d land masses, players on %d of them", land, conts, shared)
end

local fc45_bias_done = false
function fc45_bias_turn(turn, year)
  if not fc45_bias_done then fc45_bias_done = true; fc45_bias_starts() end
end

function fc45_bias_building(building, city)
  if building:is_great_wonder() then
    log.normal("FC45WONDER turn %d %s by %s in %s", game.turn(), building:rule_name(), city.owner.name, city.name)
  end
end

signal.connect("turn_begin", "fc45_bias_turn")
signal.connect("building_built", "fc45_bias_building")
