-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) hidden strategic resources test (issue 265). Load it into a civ45 server before the game starts with
--   lua file scripts/civ45-resources-test.lua
-- (scripts/civ45-resources-test.sh does that). At the first turn start from turn 2 on it counts the strategic
-- resources map generation placed, founds a city for the human-controlled "Tester" with one of each resource in
-- its radius, and checks that each gives no bonus before its tech and its full bonus after. It saves the game
-- before and after the techs ("res-before", "res-after") so the runner can check the Tester's own map.
-- Prints "FC45TEST PASS|FAIL <case>", "FC45TEST TILE <extra> <x> <y>" and a final "FC45TEST DONE <n>/<total>".

fc45_res = { passed = 0, total = 0 }

local function check(name, ok)
  fc45_res.total = fc45_res.total + 1
  if ok then fc45_res.passed = fc45_res.passed + 1 end
  log.normal("FC45TEST %s %s", ok and "PASS" or "FAIL", name)
end

-- Resource, revealing tech, a terrain it can sit on, and its bonus (terrain.ruleset [resource_*]).
local res = {
  { "Iron",   "Iron Working",     "Mountains", { Shield = 3 } },
  { "Horses", "Horseback Riding", "Grassland", { Shield = 1, Trade = 1 } },
  { "Coal",   "Steam Engine",     "Hills",     { Shield = 2 } },
  { "Oil",    "Electricity",      "Desert",    { Shield = 3 } },
}

local function run()
  for _, r in ipairs(res) do
    local n = 0
    for t in whole_map_iterate() do
      if t:has_extra(r[1]) then n = n + 1 end
    end
    check(string.format("map generation placed %d %s", n, r[1]), n > 0)
  end

  local tester
  for p in players_iterate() do
    if p.name == "Tester" then tester = p end
  end
  local home
  for u in tester:units_iterate() do home = u.tile end
  if home == nil or not edit.create_city(tester, home, "Prospect") then
    check("a city for the Tester", false)
    return
  end
  local city = home:city()

  -- One resource on each of four tiles two steps from the city, cleared of other resources.
  local spots = {}
  for t in home:square_iterate(2) do
    if #spots < #res and home:sq_distance(t) >= 4 and home:sq_distance(t) <= 5 and t.terrain:class_name() == "Land"
       and t:num_units() == 0 then
      table.insert(spots, t)
    end
  end
  for i, r in ipairs(res) do
    local t = spots[i]
    edit.change_terrain(t, find.terrain(r[3]))
    for _, o in ipairs(res) do edit.remove_extra(t, o[1]) end
    edit.create_extra(t, r[1])
    r.tile = t
    log.normal("FC45TEST TILE %s %d %d", r[1], t.nat_x, t.nat_y)
  end

  local function bonus(t, otype)
    return effects.tile_bonus(t, city, otype, "Output_Add_Tile")
  end
  local base = {}
  for _, r in ipairs(res) do
    check(string.format("Tester lacks %s at the start", r[2]), not tester:knows_tech(find.tech_type(r[2])))
    base[r[1]] = {}
    for o, v in pairs(r[4]) do
      base[r[1]][o] = bonus(r.tile, o)
      check(string.format("hidden %s gives no %s (tile add %d)", r[1], o, base[r[1]][o]), base[r[1]][o] == -v)
    end
  end
  server.save("res-before")

  for _, r in ipairs(res) do
    edit.give_tech(tester, find.tech_type(r[2]), 0, false, "hack")
  end
  for _, r in ipairs(res) do
    for o, v in pairs(r[4]) do
      local after = bonus(r.tile, o)
      check(string.format("%s gives its %d %s after %s (tile add %d)", r[1], v, o, r[2], after),
            after - base[r[1]][o] == v)
    end
  end
  server.save("res-after")
  log.normal("FC45TEST DONE %d/%d", fc45_res.passed, fc45_res.total)
end

function fc45_res_turn(turn, year)
  if turn >= 2 and not fc45_res.ran then
    fc45_res.ran = true
    run()
  end
  return false
end
signal.connect("turn_begin", "fc45_res_turn")
