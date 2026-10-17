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
