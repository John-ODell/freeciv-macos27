-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) religion test (issue 273, notes/freeciv45/design/religion.md section 6). Load it into a civ45
-- server before the game starts with
--   lua file scripts/civ45-religion-test.lua
-- (scripts/civ45-religion-test.sh does that). From turn 2 it gives the human-controlled "Tester" two cities and
-- Mysticism, then checks founding, the markers, the state faith and its content citizens, the Shrine's gold,
-- the record putting back a lost marker, and spread into the second city. It saves the game ("rel") once the
-- faith has spread, so the runner can check the record survives in the save.
-- Prints "FC45TEST PASS|FAIL <case>" and a final "FC45TEST DONE <n>/<total>".

fc45_relt = { passed = 0, total = 0, step = 0 }
FC45_RELT_SPREAD_TURNS = 80

local function check(name, ok)
  fc45_relt.total = fc45_relt.total + 1
  if ok then fc45_relt.passed = fc45_relt.passed + 1 end
  log.normal("FC45TEST %s %s", ok and "PASS" or "FAIL", name)
end

local function done()
  fc45_relt.step = -1
  log.normal("FC45TEST DONE %d/%d", fc45_relt.passed, fc45_relt.total)
end

local function content(c) return effects.city_bonus(c, "Make_Content") end

local function setup()
  local tester, ai
  for p in players_iterate() do
    if p.name == "Tester" then tester = p elseif ai == nil and fc45_is_civ(p) then ai = p end
  end
  local home
  for u in tester:units_iterate() do home = u.tile end
  if home == nil or not edit.create_city(tester, home, "Hearthstead") then
    check("a first city for the Tester", false); return done()
  end
  local second
  for t in home:square_iterate(4) do
    local d = home:sq_distance(t)
    if second == nil and d >= 9 and d <= 16 and t.terrain:class_name() == "Land" and t:city() == nil
       and (t.owner == nil or t.owner == tester) then
      if edit.create_city(tester, t, "Farhold") and t:city() ~= nil then second = t end
    end
  end
  if second == nil then check("a second city for the Tester", false); return done() end
  fc45_relt.a, fc45_relt.b = home:city().id, second:city().id

  check("no faith founded before the test", rawget(_G, "fc45_rel_founded_1") == nil)
  edit.give_tech(tester, find.tech_type("Mysticism"), 0, false, "hack")
  local holy_id = rawget(_G, "fc45_rel_holy_1")
  check("the Hearth is founded by the Tester", rawget(_G, "fc45_rel_founded_1") == tester.id)
  check("its holy city is one of the Tester's two", holy_id == fc45_relt.a or holy_id == fc45_relt.b)
  if holy_id ~= fc45_relt.a and holy_id ~= fc45_relt.b then return done() end
  local holy = find.city(nil, holy_id)
  fc45_relt.holy = holy_id
  fc45_relt.other = (holy_id == fc45_relt.a) and fc45_relt.b or fc45_relt.a
  check("the holy city has the Hearth Faith marker", holy:has_building(find.building_type("Hearth Faith")))
  check("the holy city has the Holy City marker", holy:has_building(find.building_type("Holy City")))
  check("the record says the Hearth", fc45_rel_has(holy, 1))
  local other = find.city(nil, fc45_relt.other)
  check("the other city follows no faith yet", #fc45_rel_list(other) == 0)

  edit.give_tech(ai, find.tech_type("Mysticism"), 0, false, "hack")
  check("a later discoverer founds nothing", rawget(_G, "fc45_rel_founded_1") == tester.id)

  -- Content before the state faith exists (it is placed at the next turn start), with a Temple.
  edit.create_building(holy, find.building_type("Temple"))
  fc45_relt.content = content(holy)
  fc45_relt.step = 1
end

local function state_turn()
  local holy = find.city(nil, fc45_relt.holy)
  local tester = holy.owner
  local cap = tester:primary_capital()
  check("the Tester's state faith is the Hearth", rawget(_G, fc45_gp_key("fc45_rel_state_", tester.id)) == 1)
  check("the Hearth State Faith sits in the capital",
        cap ~= nil and cap:has_building(find.building_type("Hearth State Faith")))
  local now = content(holy)
  check(string.format("state faith and its Temple make 2 more content (%d -> %d)", fc45_relt.content, now),
        now - fc45_relt.content == 2)

  -- Shrine gold: one a turn for every city of the faith.
  edit.create_building(holy, find.building_type("Shrine"))
  local g0 = tester:gold()
  local counts = { [1] = 0 }
  for p in players_iterate() do
    if fc45_is_civ(p) then
      for c in p:cities_iterate() do if fc45_rel_has(c, 1) then counts[1] = counts[1] + 1 end end
    end
  end
  fc45_rel_shrine_gold(counts)
  check(string.format("the Shrine pays %d gold for %d Hearth cities", tester:gold() - g0, counts[1]),
        tester:gold() - g0 == counts[1])

  -- A lost marker comes back from the record at the next turn start.
  edit.remove_building(holy, find.building_type("Hearth Faith"))
  check("the marker is gone after removal", not holy:has_building(find.building_type("Hearth Faith")))
  fc45_relt.step = 2
end

local function restore_turn()
  local holy = find.city(nil, fc45_relt.holy)
  check("the record put the marker back", holy:has_building(find.building_type("Hearth Faith")))
  fc45_relt.step = 3
  fc45_relt.from = game.turn()
end

local function spread_turn()
  local other = find.city(nil, fc45_relt.other)
  if other ~= nil and fc45_rel_has(other, 1) then
    check(string.format("the Hearth spread to the other city after %d turns", game.turn() - fc45_relt.from),
          other:has_building(find.building_type("Hearth Faith")))
    server.save("rel")
    return done()
  end
  if other == nil or game.turn() - fc45_relt.from > FC45_RELT_SPREAD_TURNS then
    check(string.format("the Hearth spread to the other city within %d turns", FC45_RELT_SPREAD_TURNS), false)
    return done()
  end
end

function fc45_relt_turn(turn, year)
  if turn < 2 or fc45_relt.step < 0 then return false end
  if fc45_relt.step == 0 then setup()
  elseif fc45_relt.step == 1 then state_turn()
  elseif fc45_relt.step == 2 then restore_turn()
  else spread_turn() end
  return false
end
signal.connect("turn_begin", "fc45_relt_turn")
