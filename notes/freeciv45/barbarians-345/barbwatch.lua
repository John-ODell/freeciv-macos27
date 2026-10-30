-- logs each barbarian unit the first turn it is seen: FC45BARB turn T <type> of <player> land|sea|boat
local seen = {}
function fc45_barb_watch(turn, year)
  for p in players_iterate() do
    if p.nation:rule_name() == "Barbarian" then
      for u in p:units_iterate() do
        if not seen[u.id] then
          seen[u.id] = true
          local where = u.tile.terrain:class_name() == "Oceanic" and "sea" or "land"
          if u:transporter() ~= nil then where = "boat" end
          log.normal("FC45BARB turn %d %s of %s %s", game.turn(), u.utype:rule_name(), p.name, where)
        end
      end
    end
  end
end
signal.connect("turn_begin", "fc45_barb_watch")
