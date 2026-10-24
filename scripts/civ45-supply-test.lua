-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) resource happiness and health test (issue 276, notes/freeciv45/design/resources.md section 7).
-- Load it into a civ45 server before the game starts with
--   lua file scripts/civ45-supply-test.lua
-- (scripts/civ45-supply-test.sh does that). From turn 2 it gives the human-controlled "Tester" two cities, clears
-- every luxury and food resource inside its borders, puts two Wine, one Silk, one Wheat and one Buffalo inside them
-- and Gems outside every border, then checks the Supply markers in the capital and the content, size and health
-- they give the second city, and that removing the Silk takes its marker away.
-- Prints "FC45TEST PASS|FAIL <case>" and a final "FC45TEST DONE <n>/<total>".

fc45_supt = { passed = 0, total = 0, step = 0 }

local function check(name, ok)
  fc45_supt.total = fc45_supt.total + 1
  if ok then fc45_supt.passed = fc45_supt.passed + 1 end
  log.normal("FC45TEST %s %s", ok and "PASS" or "FAIL", name)
end

local function done()
  fc45_supt.step = -1
  log.normal("FC45TEST DONE %d/%d", fc45_supt.passed, fc45_supt.total)
end

local function bonus(c)
  return effects.city_bonus(c, "Make_Content"), effects.city_bonus(c, "Size_Adj"), effects.city_bonus(c, "Health_Pct")
end

local function put(t, terrain, res)
  edit.change_terrain(t, find.terrain(terrain))
  for _, r in ipairs(fc45_res_all) do pcall(function() edit.remove_extra(t, r) end) end
  pcall(function() edit.create_extra(t, res) end)
  return t:has_extra(res)
end

local function setup()
  local tester
  for p in players_iterate() do if p.name == "Tester" then tester = p end end
  local home
  for u in tester:units_iterate() do home = u.tile end
  if home == nil or not edit.create_city(tester, home, "Capitol") then
    check("a first city for the Tester", false); return done()
  end
  local second
  for t in home:square_iterate(4) do
    local d = home:sq_distance(t)
    if second == nil and d >= 9 and d <= 16 and t.terrain:class_name() == "Land" and t:city() == nil then
      if edit.create_city(tester, t, "Second") and t:city() ~= nil then second = t end
    end
  end
  if second == nil then check("a second city for the Tester", false); return done() end
  fc45_supt.tester, fc45_supt.b = tester, second:city().id

  -- Clear every luxury and food resource inside the Tester's borders; pick five owned land tiles that are not
  -- city centres, and one unowned land tile far from them.
  local spots, outside = {}, nil
  for t in whole_map_iterate() do
    if t.owner == tester then
      for _, r in ipairs(fc45_res_all) do pcall(function() edit.remove_extra(t, r) end) end
      if #spots < 5 and t:city() == nil and t.terrain:class_name() == "Land" and t:num_units() == 0 then
        spots[#spots + 1] = t
      end
    elseif outside == nil and t.owner == nil and t.terrain:class_name() == "Land" and t:sq_distance(home) > 400 then
      outside = t
    end
  end
  check("five tiles inside the Tester's borders", #spots == 5)
  if #spots < 5 then return done() end
  check("Wine placed twice", put(spots[1], "Hills", "Wine") and put(spots[2], "Hills", "Wine"))
  check("Silk placed", put(spots[3], "Forest", "Silk"))
  check("Wheat and Buffalo placed", put(spots[4], "Plains", "Wheat") and put(spots[5], "Plains", "Buffalo"))
  fc45_supt.silk = spots[3]
  if outside ~= nil then check("Gems placed outside every border", put(outside, "Jungle", "Gems")) end
  local mc, sz, hp = bonus(second:city())
  fc45_supt.base = { mc, sz, hp }
  fc45_supt.step = 1
end

local function supplies(p)
  local have = {}
  local cap = p:primary_capital()
  if cap == nil then return have, nil end
  for _, r in ipairs(fc45_res_all) do
    if cap:has_building(find.building_type(r .. " Supply")) then have[#have + 1] = r end
  end
  return have, cap
end

local function placed_turn()
  local p = fc45_supt.tester
  local have, cap = supplies(p)
  check("the Tester has a capital", cap ~= nil)
  table.sort(have)
  local list = table.concat(have, ",")
  check(string.format("the capital holds exactly Buffalo, Silk, Wheat and Wine Supply (%s)", list),
        list == "Buffalo,Silk,Wheat,Wine")
  local b = find.city(nil, fc45_supt.b)
  local mc, sz, hp = bonus(b)
  local base = fc45_supt.base
  check(string.format("two luxury kinds make 2 more content in the second city (%d -> %d)", base[1], mc), mc - base[1] == 2)
  check(string.format("two food kinds raise the size cap by 2 (%d -> %d)", base[2], sz), sz - base[2] == 2)
  check(string.format("two food kinds add 10%% health (%d -> %d)", base[3], hp), hp - base[3] == 10)
  edit.remove_extra(fc45_supt.silk, "Silk")
  fc45_supt.step = 2
end

local function removed_turn()
  local p = fc45_supt.tester
  local cap = p:primary_capital()
  check("Silk Supply is gone once the Silk is", cap ~= nil and not cap:has_building(find.building_type("Silk Supply")))
  local mc = bonus(find.city(nil, fc45_supt.b))
  check(string.format("one luxury kind left: 1 more content than at the start (%d -> %d)", fc45_supt.base[1], mc),
        mc - fc45_supt.base[1] == 1)
  done()
end

function fc45_supt_turn(turn, year)
  if turn < 2 or fc45_supt.step < 0 then return false end
  if fc45_supt.step == 0 then setup()
  elseif fc45_supt.step == 1 then placed_turn()
  else removed_turn() end
  return false
end
signal.connect("turn_begin", "fc45_supt_turn")
