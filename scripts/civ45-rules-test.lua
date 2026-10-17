-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) stack, map and combat rules test. Load it into a civ45 server before the game starts with
--   lua file scripts/civ45-rules-test.lua
-- (scripts/civ45-rules-test.sh does that; an autogame reads no console input once it runs). It runs at the
-- first turn start from turn 5 on, checks one more thing a turn later, and prints
-- "FC45TEST PASS|FAIL <case>" lines to the server log and a final "FC45TEST DONE <n>/<total>".
-- Moves and attacks go through the real "Unit Move" and "Attack" enablers via Unit:perform_action. The
-- human-controlled "Tester" (made by the runner) owns the test units: with no client attached, nothing
-- moves them between turns. The Animal Kingdom is at war with everyone, so it owns the units that are attacked.
-- The combat cases (slice 2) use "Bombard 2", the siege bombardment, and "Bombard", the aircraft one.

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

-- A free tile with n free neighbours; returns the tile and the neighbours. With big, the tile and the
-- neighbours must also carry a Big Land unit (siege units need a road in rough terrain).
local function free_spot(n, used, big)
  local ok = free
  if big then
    ok = function(t) return free(t) and find.unit_type("Howitzer"):can_exist_at_tile(t) end
  end
  for t in whole_map_iterate() do
    if ok(t) and not used[t.id] then
      local around = {}
      for a in t:circle_iterate(2) do
        if a.id ~= t.id and ok(a) and not used[a.id] then around[#around + 1] = a end
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

  if tester ~= nil and animals ~= nil then fc45_combat_test_run(tester, animals, used) end
end

-- Slice 2, combat. Units of the Tester and of the Animal Kingdom are created next to each other on free land
-- and act at once through the real enablers; what is checked is what is left on the tiles afterwards.
function fc45_combat_test_run(tester, animals, used)
  local attack, bombard, bombard_stack = find.action("Attack"), find.action("Bombard"), find.action("Bombard 2")
  local function mk(owner, type_name, tile)
    return edit.create_unit(owner, tile, find.unit_type(type_name), 0, nil, -1)
  end
  local function alive(owner, id) return find.unit(owner, id) ~= nil end
  local function owned_by(tile, owner)
    local n = 0
    for u in tile:units_iterate() do if u.owner.id == owner.id then n = n + 1 end end
    return n
  end

  -- Siege against a stack of three: all three live, and the bombardment wounded them (a Warriors then
  -- beats the stack's defender, which is at 1 hit point: a Howitzer's 20 shots at attack 12 against defence
  -- 1 leave a 10-hit-point Warriors at the 1-point floor almost surely, and a Warriors wins a round
  -- against a 1-point defender before losing ten in about 99.9% of fights).
  local spot, side = free_spot(2, used, true)
  if spot == nil then
    log.normal("FC45TEST SKIP no free land for the siege case")
  else
    mk(animals, "Warriors", spot); mk(animals, "Warriors", spot); mk(animals, "Warriors", spot)
    local howitzer = mk(tester, "Howitzer", side[1])
    local shot = howitzer:perform_action(bombard_stack, spot)
    log.normal("FC45TEST siege: bombard %s, units left %d", tostring(shot), spot:num_units())
    check("a siege unit bombards a three-unit stack and all three live", shot and spot:num_units() == 3)
    local warriors = mk(tester, "Warriors", side[2])
    local wid = warriors.id
    local hit = warriors:perform_action(attack, spot)
    log.normal("FC45TEST siege: warriors attack %s, units left %d, warriors alive %s", tostring(hit),
               spot:num_units(), tostring(alive(tester, wid)))
    check("a Warriors then beats the bombarded stack's defender (the stack was wounded)",
          hit and owned_by(spot, animals) == 2 and alive(tester, wid))
  end

  -- Siege against a lone unit is refused (the enabler wants two or more units on the tile).
  spot, side = free_spot(1, used, true)
  if spot == nil then
    log.normal("FC45TEST SKIP no free land for the lone-unit case")
  else
    mk(animals, "Warriors", spot)
    local catapult = mk(tester, "Catapult", side[1])
    local shot = catapult:perform_action(bombard_stack, spot)
    check("a siege unit may not bombard a lone unit", shot == false and spot:num_units() == 1)

    -- Aircraft bombard reaches one tile: a Bomber two tiles away is refused, an adjacent one is not,
    -- and its bombardment does not kill the lone unit either.
    local far = nil
    for a in spot:circle_iterate(4) do
      if spot:sq_distance(a) == 4 and free(a) and not used[a.id] then far = a; break end
    end
    if far == nil then
      log.normal("FC45TEST SKIP no free tile two steps from the lone unit")
    else
      used[far.id] = true
      local bomber = mk(tester, "Bomber", far)
      check("a Bomber two tiles away may not bombard (range 1)",
            bomber:perform_action(bombard, spot) == false and spot:num_units() == 1)
    end
    local near = mk(tester, "Bomber", side[1])
    check("an adjacent Bomber bombards the lone unit, which lives",
          near:perform_action(bombard, spot) == true and spot:num_units() == 1)
  end

  -- To the death: two Musketeers (20 hit points, firepower 1) need 20 lost rounds to die, so sandbox's
  -- 15-round cap always left both alive; with no cap exactly one of them dies.
  spot, side = free_spot(1, used)
  if spot == nil then
    log.normal("FC45TEST SKIP no free land for the duel")
  else
    mk(animals, "Musketeers", spot)
    local m = mk(tester, "Musketeers", side[1])
    local mid = m.id
    check("Combat_Rounds is 0 for a Musketeers (fights to the death)",
          effects.unit_bonus(m, nil, "Combat_Rounds") == 0)
    local hit = m:perform_action(attack, spot)
    local att_alive, def_alive = alive(tester, mid), owned_by(spot, animals) == 1
    log.normal("FC45TEST duel: attack %s, attacker alive %s, defender alive %s", tostring(hit),
               tostring(att_alive), tostring(def_alive))
    check("an even fight is to the death: Musketeers against Musketeers leaves exactly one dead",
          hit and att_alive ~= def_alive)
  end

  -- Withdraws: a Knights (10 hit points, cap 12 rounds) attacking a Musketeers (20 hit points) can never
  -- kill it, and dies only if it loses 10 of at most 12 rounds (about 1 fight in 200 at attack 4 against
  -- defence 3), so both are alive afterwards; two tries make a false failure negligible. Without the cap
  -- (or with Combat_Rounds 0 for everyone) one of the two always dies.
  local both = nil
  for try = 1, 2 do
    spot, side = free_spot(1, used)
    if spot == nil then break end
    mk(animals, "Musketeers", spot)
    local k = mk(tester, "Knights", side[1])
    local kid = k.id
    if try == 1 then
      check("Combat_Rounds is 12 for a Knights (Withdraws, 10 hit points)",
            effects.unit_bonus(k, nil, "Combat_Rounds") == 12)
      local d = mk(tester, "Dragoons", side[1])
      check("Combat_Rounds is 24 for a Dragoons (Withdraws, 20 hit points)",
            effects.unit_bonus(d, nil, "Combat_Rounds") == 24)
      d:kill("disbanded", nil)
    end
    local hit = k:perform_action(attack, spot)
    local att_alive, def_alive = alive(tester, kid), owned_by(spot, animals) == 1
    log.normal("FC45TEST withdraw try %d: attack %s, knights alive %s, musketeers alive %s", try,
               tostring(hit), tostring(att_alive), tostring(def_alive))
    if hit and att_alive and def_alive then both = true; break end
    both = false
  end
  if both == nil then
    log.normal("FC45TEST SKIP no free land for the withdraw case")
  else
    check("a Withdraws attacker that cannot win breaks off: Knights and Musketeers both alive", both)
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
