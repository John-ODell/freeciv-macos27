-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) stack and map rules test. Load it into a civ45 server before the game starts with
--   lua file scripts/civ45-rules-test.lua
-- (scripts/civ45-rules-test.sh does that; an autogame reads no console input once it runs). It runs at the
-- first turn start from turn 5 on, checks one more thing a turn later, and prints
-- "FC45TEST PASS|FAIL <case>" lines to the server log and a final "FC45TEST DONE <n>/<total>".
-- Moves and attacks go through the real "Unit Move" and "Attack" enablers via Unit:perform_action. The
-- human-controlled "Tester" (made by the runner) owns the test units: with no client attached, nothing
-- moves them between turns. The Animal Kingdom is at war with everyone, so it owns the stack that is attacked.

fc45_test = { passed = 0, total = 0 }

local function check(name, ok)
  fc45_test.total = fc45_test.total + 1
  if ok then fc45_test.passed = fc45_test.passed + 1 end
  log.normal("FC45TEST %s %s", ok and "PASS" or "FAIL", name)
end

local function find_player(pred)
  for p in players_iterate() do
    if p.is_alive and pred(p) then return p end
  end
  return nil
end

-- A land tile nobody holds: no unit, city, base, hut or border. The bases are civ45's (terrain.ruleset,
-- causes "Base"); a base with NoStackDeath would hide the stack rule in a control run with killstack on.
local bases = { "Fort", "Fortress", "Castle", "Airstrip", "Airbase", "Buoy" }
local function free(t)
  if t:num_units() > 0 or t:city() ~= nil or t.owner ~= nil
     or t:has_extra("Hut") or t:has_extra("Hermit") then return false end
  for _, b in ipairs(bases) do if t:has_extra(b) then return false end end
  return find.unit_type("Warriors"):can_exist_at_tile(t)
end

-- A free tile with n free neighbours; returns the tile and the neighbours.
local function free_spot(n, used)
  for t in whole_map_iterate() do
    if free(t) and not used[t.id] then
      local around = {}
      for a in t:circle_iterate(2) do
        if a.id ~= t.id and free(a) and not used[a.id] then around[#around + 1] = a end
      end
      if #around >= n then
        used[t.id] = true
        for i = 1, n do used[around[i].id] = true end
        return t, around
      end
    end
  end
  return nil
end

function fc45_rules_test_run()
  local function setting(name) return string.upper(server.setting.get(name) or "?") end
  local topo, wrap, ks = setting("topology"), setting("wrap"), setting("killstack")
  log.normal("FC45TEST settings: topology '%s', wrap '%s', killstack '%s'", topo, wrap, ks)
  check("square map seen from above (topology has neither ISO nor HEX)",
        topo ~= "?" and topo:find("ISO") == nil and topo:find("HEX") == nil)
  check("map wraps east to west only", wrap == "WRAPX")
  check("killstack is disabled", ks == "DISABLED")
  check("no one-unit-per-tile sweep is loaded",
        civ45_turn_begin_callback == nil and civ45_unit_built_callback == nil)

  local move, attack = find.action("Unit Move"), find.action("Attack")
  local tester = find_player(function(p) return p:is_human() end)
  local animals = find_player(function(p) return p.nation:rule_name() == "Animal Kingdom" end)
  local used = {}

  -- Moving onto a tile held by a friendly unit, then a third unit for the next turn's check.
  local home, around = free_spot(1, used)
  if tester == nil or home == nil then
    log.normal("FC45TEST SKIP no human-controlled player or no free land")
  else
    local function make(type_name, tile)
      return edit.create_unit(tester, tile, find.unit_type(type_name), 0, nil, -1)
    end
    make("Warriors", home)
    local walker = make("Phalanx", around[1])
    check("a unit moves onto a tile held by a friendly unit",
          walker:perform_action(move, home) and walker.tile.id == home.id and home:num_units() == 2)
    make("Archers", home)
    fc45_test.stack_tile, fc45_test.stack_turn = home.id, game.turn()
  end

  -- Moving into an AI city that already holds a unit (one is put there first if it is empty).
  local city, gate
  for p in players_iterate() do
    if p.is_alive and not p:is_human() then
      for c in p:cities_iterate() do
        for a in c.tile:circle_iterate(2) do
          if a.id ~= c.tile.id and a:num_units() == 0 and a:city() == nil
             and find.unit_type("Warriors"):can_exist_at_tile(a) then gate = a; break end
        end
        if gate ~= nil then city = c; break end
      end
    end
    if city ~= nil then break end
  end
  if city == nil then
    log.normal("FC45TEST SKIP no AI city with a free land neighbour")
  else
    if city.tile:num_units() == 0 then
      edit.create_unit(city.owner, city.tile, find.unit_type("Phalanx"), 0, city, -1)
    end
    local before = city.tile:num_units()
    local u = edit.create_unit(city.owner, gate, find.unit_type("Warriors"), 0, nil, -1)
    check("a unit moves into an occupied city",
          u:perform_action(move, city.tile) and u.tile.id == city.tile.id and city.tile:num_units() == before + 1)
  end

  -- An attack on a three-unit stack outside a city: one unit defends and dies, the other two live (with
  -- killstack all three would die). Freeciv picks the defender by its odds against this attacker, cheaper
  -- unit first on a tie (common/combat.c get_defender()), so against Armor a Warriors usually defends.
  -- Combat_Rounds can end a fight undecided, so a fresh stack and attacker get up to three tries.
  if tester == nil or animals == nil then
    log.normal("FC45TEST SKIP no human-controlled player or no Animal Kingdom")
  else
    local result = nil
    for try = 1, 3 do
      local spot, side = free_spot(1, used)
      if spot == nil then break end
      local phalanx = edit.create_unit(animals, spot, find.unit_type("Phalanx"), 0, nil, -1)
      local w1 = edit.create_unit(animals, spot, find.unit_type("Warriors"), 0, nil, -1)
      local w2 = edit.create_unit(animals, spot, find.unit_type("Warriors"), 0, nil, -1)
      local armor = edit.create_unit(tester, side[1], find.unit_type("Armor"), 0, nil, -1)
      local w1_id, w2_id, ph_id = w1.id, w2.id, phalanx.id
      local attacked = armor:perform_action(attack, spot)
      local left = {}
      for u in spot:units_iterate() do left[u.id] = true end
      log.normal("FC45TEST try %d: attack %s, units left %d (phalanx %s, warriors %s %s)", try,
                 tostring(attacked), spot:num_units(), tostring(left[ph_id] ~= nil),
                 tostring(left[w1_id] ~= nil), tostring(left[w2_id] ~= nil))
      if attacked and spot:num_units() < 3 then
        result = (spot:num_units() == 2)
        break
      end
      for u in spot:units_iterate() do u:kill("disbanded", nil) end
    end
    if result == nil then
      log.normal("FC45TEST SKIP no decisive attack in three tries")
    else
      check("only the defender dies when a stack outside a city loses (two of three left)", result)
    end
  end
end

function fc45_rules_test_turn(turn, year)
  if turn >= 5 and fc45_test.ran == nil then
    fc45_test.ran = true
    fc45_rules_test_run()
  elseif fc45_test.stack_turn ~= nil and turn > fc45_test.stack_turn and fc45_test.done == nil then
    fc45_test.done = true
    local tile = find.tile(fc45_test.stack_tile)
    check("a stack of three Tester units is still together a turn later", tile ~= nil and tile:num_units() == 3)
    log.normal("FC45TEST DONE %d/%d", fc45_test.passed, fc45_test.total)
  end
  return false
end
signal.connect("turn_begin", "fc45_rules_test_turn")
log.normal("FC45TEST loaded at turn %d", game.turn())
