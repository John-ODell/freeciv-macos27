-- SPDX-License-Identifier: GPL-2.0-or-later
-- Draft observer for a Freeciv45 (civ45) autogame. Load it before the game starts, for example
--   scripts/test.sh ~/freeciv-builds/qt --ruleset civ45 --no-client --lua scripts/civ45-draft-log.lua
-- It changes nothing. It prints one server-log line per draft unit built, per city that shrinks because a
-- unit was built, and per unit disbanded into a city's build, so the log can be counted afterwards
-- (grep FC45DRAFT / FC45SHRINK / FC45WHIP):
--   FC45DRAFT turn T <unit type> of <player> in <city> size <size after>
--   FC45SHRINK turn T <city> of <player> by <change> to <size> reason <reason>
--   FC45WHIP turn T <unit type> of <player> into <city> (draft|other)

function fc45_draft_built(unit, city)
  if unit.utype:has_flag("Draft") then
    log.normal("FC45DRAFT turn %d %s of %s in %s size %d", game.turn(), unit.utype:rule_name(),
               unit.owner.name, city and city.name or "-", city and city.size or 0)
  end
end

function fc45_draft_shrink(city, change, reason)
  if reason == "unit_built" then
    log.normal("FC45SHRINK turn %d %s of %s by %d to %d reason %s", game.turn(), city.name,
               city.owner.name, change, city.size, reason)
  end
end

function fc45_draft_city_action(action, actor, city)
  if action:rule_name() == "Disband Unit Recover" and actor ~= nil then
    log.normal("FC45WHIP turn %d %s of %s into %s %s", game.turn(), actor.utype:rule_name(),
               actor.owner.name, city.name, actor.utype:has_flag("Draft") and "draft" or "other")
  end
end

signal.connect("unit_built", "fc45_draft_built")
signal.connect("city_size_change", "fc45_draft_shrink")
signal.connect("action_started_unit_city", "fc45_draft_city_action")
log.normal("FC45DRAFT observer loaded at turn %d", game.turn())
