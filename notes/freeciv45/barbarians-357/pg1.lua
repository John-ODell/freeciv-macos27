-- passive "human-like" player: never lets Oscar pass MAXC cities (kills Settlers), optionally caps garrison per city
-- logs FC45STATE turn cities defenders every 5 turns
local MAXC, MAXDEF, GARR = 3, 99, 1
function fc45_passive(turn, year)
  local p = nil
  for q in players_iterate() do if q.name == "Oscar" then p = q end end
  if p == nil then return end
  local nc = 0
  for c in p:cities_iterate() do nc = nc + 1 end
  local perc, mil = {}, 0
  for u in p:units_iterate() do
    local n = u.utype:rule_name()
    if n == "Settlers" and nc >= MAXC then edit.unit_kill(u, "disbanded", nil)
    elseif n == 'Warriors' or n == 'Phalanx' or n == 'Archers' or n == 'Horsemen' or n == 'Spearmen' or n == 'Legion' or n == 'Pikemen' then
      mil = mil + 1
      local c = u.tile:city()
      if c ~= nil then
        perc[c.id] = (perc[c.id] or 0) + 1
        if perc[c.id] > MAXDEF then edit.unit_kill(u, "disbanded", nil) end
      end
    end
  end
  if GARR > 0 then
    local ph = find.unit_type("Phalanx")
    for c in p:cities_iterate() do
      local have = 0
      for u in c.tile:units_iterate() do if u.owner == p and u.utype:rule_name() == "Phalanx" then have = have + 1 end end
      for i = have + 1, GARR do edit.create_unit(p, c.tile, ph, 0, c, -1) end
    end
  end
  if turn % 5 == 0 then log.normal("FC45STATE turn %d cities %d military %d", turn, nc, mil) end
end
signal.connect("turn_begin", "fc45_passive")
