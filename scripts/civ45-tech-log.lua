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
