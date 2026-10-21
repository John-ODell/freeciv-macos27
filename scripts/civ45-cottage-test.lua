-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) cottage test (issue 275, notes/freeciv45/design/cottages.md section 5).
-- Load it into a civ45 server before the game starts with
--   lua file scripts/civ45-cottage-test.lua
-- (scripts/civ45-cottage-test.sh does that). From turn 2 it gives the human-controlled "Tester" Pottery and a city
-- whose only good tile is a grassland cottage, so the city works it; puts a second cottage far from every city;
-- and sets Workers to the mine job on grassland and on hills. It then checks that the grassland job builds a
-- Cottage and the hills job a Mine, that the worked cottage grows into a Hamlet and the unworked one doesn't, and
-- that pillage takes the top stage only.
-- Prints "FC45TEST PASS|FAIL <case>" and a final "FC45TEST DONE <n>/<total>".

fc45_cott = { passed = 0, total = 0, step = 0 }

-- Turns the worked cottage gets to grow (10 % a turn: 99.8 % within 60).
FC45_COTT_GROW_TURNS = 60

local function check(name, ok)
  fc45_cott.total = fc45_cott.total + 1
  if ok then fc45_cott.passed = fc45_cott.passed + 1 end
  log.normal("FC45TEST %s %s", ok and "PASS" or "FAIL", name)
end

local function done()
  fc45_cott.step = -1
  log.normal("FC45TEST DONE %d/%d", fc45_cott.passed, fc45_cott.total)
end

local CLEAR = { "River", "Irrigation", "Farmland", "Mine", "Road", "Cottage", "Hamlet", "Village", "Town",
                "Iron", "Horses", "Coal", "Oil", "Peat", "Resources" }

-- Make a tile bare terrain: no river, improvement or resource.
local function bare(t, terrain)
  edit.change_terrain(t, find.terrain(terrain))
  for _, e in ipairs(CLEAR) do pcall(function() edit.remove_extra(t, e) end) end
  for _, r in ipairs(fc45_res_all or {}) do pcall(function() edit.remove_extra(t, r) end) end
end

local function land_far_from_cities(t, d)
  if t.terrain:class_name() ~= "Land" or t:city() ~= nil or t:num_units() > 0 then return false end
  for p in players_iterate() do
    for c in p:cities_iterate() do
      if c.tile:sq_distance(t) <= d then return false end
    end
  end
  return true
end

local function setup()
  local tester
  for p in players_iterate() do if p.name == "Tester" then tester = p end end
  local home
  for u in tester:units_iterate() do home = u.tile end
  if home == nil then check("the Tester has a unit to found on", false); return done() end
  edit.give_tech(tester, find.tech_type("Pottery"), 0, false, "hut")
  fc45_cott.tester = tester

  -- Every tile the city could work becomes bare desert except one grassland cottage, so the city works it.
  local cot
  for t in home:square_iterate(3) do
    local d = home:sq_distance(t)
    if d > 0 and d <= 8 then
      bare(t, "Desert")
      if cot == nil and d == 1 then cot = t end
    end
  end
  bare(home, "Grassland")
  bare(cot, "Grassland")
  edit.create_extra(cot, "Cottage")
  if not edit.create_city(tester, home, "Cottageton") or home:city() == nil then
    check("a city for the Tester", false); return done()
  end
  fc45_cott.city, fc45_cott.cot = home:city(), cot

  -- An unworked cottage, a grassland tile and a hills tile for the Workers, all far from every city.
  local spots = {}
  for t in whole_map_iterate() do
    if #spots < 3 and land_far_from_cities(t, 50) then
      local ok = true
      for _, s in ipairs(spots) do if s:sq_distance(t) <= 50 then ok = false end end
      if ok then spots[#spots + 1] = t end
    end
  end
  if #spots < 3 then check("three tiles far from every city", false); return done() end
  bare(spots[1], "Grassland"); edit.create_extra(spots[1], "Cottage")
  bare(spots[2], "Grassland"); bare(spots[3], "Hills")
  fc45_cott.idle, fc45_cott.grass, fc45_cott.hills = spots[1], spots[2], spots[3]

  local workers = find.unit_type("Workers")
  local mine = find.action("Build Mine")
  local w1 = edit.create_unit(tester, spots[2], workers, 0, nil, -1)
  local w2 = edit.create_unit(tester, spots[3], workers, 0, nil, -1)
  check("a Workers on grassland can't build a Mine", not w1:perform_action(mine, spots[2], "Mine"))
  check("a Workers on grassland starts a Cottage", w1:perform_action(mine, spots[2], "Cottage"))
  check("a Workers on hills can't build a Cottage", not w2:perform_action(mine, spots[3], "Cottage"))
  check("a Workers on hills starts a Mine", w2:perform_action(mine, spots[3], "Mine"))
  fc45_cott.start = game.current_turn()
  fc45_cott.step = 1
end

local function pillage_start()
  local t = fc45_cott.cot
  -- Village and Town by edit, which skips their growth chance; then a Warriors pillages.
  edit.create_extra(t, "Village")
  edit.create_extra(t, "Town")
  check("Village and Town placed on the hamlet", t:has_extra("Village") and t:has_extra("Town"))
  local u = edit.create_unit(fc45_cott.tester, t, find.unit_type("Warriors"), 0, nil, -1)
  local pillage = find.action("Pillage")
  check("pillage can't take the Village while the Town stands", not u:perform_action(pillage, t, "Village"))
  check("pillage can take the Town", u:perform_action(pillage, t, "Town"))
  fc45_cott.step = 2
end

local function grow_turn()
  local turn = game.current_turn() - fc45_cott.start
  if fc45_cott.built == nil and turn >= 12 then
    fc45_cott.built = true
    local g, h = fc45_cott.grass, fc45_cott.hills
    check("the grassland job built a Cottage", g:has_extra("Cottage") and not g:has_extra("Mine"))
    check("the hills job built a Mine", h:has_extra("Mine") and not h:has_extra("Cottage"))
    check("the Workers' fresh cottage, unworked, has not grown", not g:has_extra("Hamlet"))
  end
  if fc45_cott.cot:has_extra("Hamlet") then
    check(string.format("the worked cottage grew into a Hamlet (after %d turns)", turn), true)
    check("the unworked cottage has not grown", not fc45_cott.idle:has_extra("Hamlet"))
    check("the Hamlet keeps the Cottage under it", fc45_cott.cot:has_extra("Cottage"))
    return pillage_start()
  end
  if turn >= FC45_COTT_GROW_TURNS then
    check(string.format("the worked cottage grew into a Hamlet within %d turns", FC45_COTT_GROW_TURNS), false)
    return done()
  end
end

local function pillaged_turn()
  local t = fc45_cott.cot
  check("the pillage took the Town", not t:has_extra("Town"))
  check("the Village, Hamlet and Cottage are still there",
        t:has_extra("Village") and t:has_extra("Hamlet") and t:has_extra("Cottage"))
  done()
end

function fc45_cott_turn(turn, year)
  if turn < 2 or fc45_cott.step < 0 then return false end
  if fc45_cott.step == 0 then setup()
  elseif fc45_cott.step == 1 then grow_turn()
  else pillaged_turn() end
  return false
end
signal.connect("turn_begin", "fc45_cott_turn")
