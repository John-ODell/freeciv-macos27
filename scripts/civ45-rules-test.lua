-- SPDX-License-Identifier: GPL-2.0-or-later
-- Freeciv45 (civ45) stack, map, combat, victory, draft, tech, roster and great people rules test. Load it into a civ45 server before the game starts with
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
  check("square tiles seen at an angle (topology ISO, not HEX)",
        topo ~= "?" and topo:find("ISO") ~= nil and topo:find("HEX") == nil)
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
  fc45_victory_test_run()
  if tester ~= nil then fc45_draft_test_run(tester, used) end
  if tester ~= nil then fc45_tech_test_run(tester) end
  if tester ~= nil and animals ~= nil then fc45_roster_test_run(tester, animals, used) end
  if tester ~= nil then fc45_gp_test_run(tester, used) end
  if tester ~= nil then fc45_decisions_test_run(tester) end
end

-- Great people (slice 11, notes/freeciv45/design/great-people.md): points, deeds, the golden age and the
-- settling enabler, in Testerburg; the birth, the settling and the age's end are checked a turn later.
function fc45_gp_test_run(tester, used)
  local city = fc45_test.city
  if city == nil then
    log.normal("FC45TEST SKIP no Testerburg for the great people cases")
    return
  end
  local deed, pledge = find.action("User Action 3"), find.action("User Action 4")
  local function known_techs(p)
    local n = 0
    for i = 0, 300 do
      local t = find.tech_type(i)
      if t ~= nil and p:knows_tech(t) then n = n + 1 end
    end
    return n
  end
  local function gp(kind) return edit.create_unit(tester, city.tile, find.unit_type("Great " .. kind), 0, city, -1) end

  -- Points: a Library gives 1 a turn, a University 2 more.
  city:create_building(find.building_type("Library"))
  local r1 = effects.city_bonus(city, "User_Effect_3")
  city:create_building(find.building_type("University"))
  local r2 = effects.city_bonus(city, "User_Effect_3")
  check("great-person points: 1 a turn with a Library, 3 with a University too", r1 == 1 and r2 == 3)

  -- Deeds, each by a fresh great person standing in the city.
  local techs = known_techs(tester)
  local sage = gp("Sage")
  local did = sage:perform_action(deed)
  check("a Great Sage's deed gives one tech", did and known_techs(tester) == techs + 1)
  local gold = tester:gold()
  local magnate = gp("Magnate")
  did = magnate:perform_action(deed)
  check("a Great Magnate's trade mission in its own city brings 100 gold plus 30 per citizen",
        did and tester:gold() == gold + 100 + 30 * city.size)
  local culture = city:culture()
  local virtuoso = gp("Virtuoso")
  did = virtuoso:perform_action(deed)
  check("a Great Virtuoso's masterwork adds 400 to the city's culture", did and city:culture() == culture + 400)
  local content = effects.city_bonus(city, "Make_Content")
  local oracle = gp("Oracle")
  did = oracle:perform_action(deed)
  check("a Great Oracle founds the Sanctum, which makes one more citizen content",
        did and city:has_building(find.building_type("Sanctum")) and effects.city_bonus(city, "Make_Content") == content + 1)

  -- The Commander drills the stack on a free tile.
  local spot = free_spot(0, used)
  if spot == nil then
    log.normal("FC45TEST SKIP no free land for the Commander case")
  else
    local w1 = edit.create_unit(tester, spot, find.unit_type("Warriors"), 0, nil, -1)
    local w2 = edit.create_unit(tester, spot, find.unit_type("Warriors"), 0, nil, -1)
    local commander = edit.create_unit(tester, spot, find.unit_type("Great Commander"), 0, nil, -1)
    did = commander:perform_action(deed)
    local v1, v2 = -1, -1
    for u in spot:units_iterate() do
      if u.id == w1.id then v1 = u.veteran end
      if u.id == w2.id then v2 = u.veteran end
    end
    log.normal("FC45TEST commander: deed %s, veteran levels %d and %d", tostring(did), v1, v2)
    check("a Great Commander's drill raises two green Warriors one veteran level", did and v1 == 1 and v2 == 1)
  end

  -- A golden age: one pledge starts the first, the second then needs two.
  local pid = tester.id
  local pledger = gp("Sage")
  did = pledger:perform_action(pledge)
  local golden = find.building_type("Golden Age")
  local until_turn = rawget(_G, fc45_gp_key("fc45_golden_until_", pid))
  log.normal("FC45TEST golden age: pledge %s, building %s, until %s, points percent %d", tostring(did),
             tostring(city:has_building(golden)), tostring(until_turn), effects.city_bonus(city, "User_Effect_4"))
  check("one pledge starts a golden age in the capital for ten turns, doubling great-person points",
        did and city:has_building(golden) and until_turn == game.turn() + 10
        and effects.city_bonus(city, "User_Effect_4") == 100)
  local again = gp("Sage")
  did = again:perform_action(pledge)
  local marker = find.building_type("Pledge of the Sage")
  check("the second golden age needs two pledges: one counts, marks the Sage's pledge and starts nothing",
        did and rawget(_G, fc45_gp_key("fc45_golden_pledges_", pid)) == 1 and rawget(_G, fc45_gp_key("fc45_golden_count_", pid)) == 1
        and city:has_building(marker))
  local third = gp("Sage")
  local refused = not third:perform_action(pledge)
  check("a second Sage cannot pledge the same age: the pledge needs great people of different kinds",
        refused and rawget(_G, fc45_gp_key("fc45_golden_pledges_", pid)) == 1)
  if not refused then third = nil end
  if third ~= nil then third:kill("disbanded", nil) end
  -- Residents stay with a city that changes hands (John's decision of 2026-10-17): a second city of the
  -- Tester's settles a Great Oracle and is handed to another player with edit.transfer_city, which emits no
  -- city_transferred signal (only unit_conquer_city does, server/citytools.c:2145), so the turn_begin sweep
  -- is what keeps the Resident; a turn later the city is checked for it. The restore itself is checked then
  -- too, by removing Testerburg's Resident Sage and calling it.
  local victim = nil
  for p in players_iterate() do
    if p.id ~= tester.id and fc45_is_civ(p) and victim == nil then victim = p end
  end
  local spot = nil
  for t in city.tile:square_iterate(6) do
    if spot == nil and t:sq_distance(city.tile) >= 16 and t:city() == nil and t:num_units() == 0
       and (t.terrain:rule_name() == "Grassland" or t.terrain:rule_name() == "Plains") then spot = t end
  end
  if victim ~= nil and spot ~= nil and edit.create_city(tester, spot, "Residentia") then
    local c2 = spot:city()
    local oracle = edit.create_unit(tester, c2.tile, find.unit_type("Great Oracle"), 0, c2, -1)
    local settled = oracle:perform_action(find.action("Join City"), c2)
    local handed = edit.transfer_city(c2, victim)
    log.normal("FC45TEST handover: Residentia settled an Oracle %s, handed to %s %s, owner now %s",
               tostring(settled), victim.name, tostring(handed), c2.owner.name)
    check("a second city settles a Great Oracle and is handed to another player", settled and handed and c2.owner.id == victim.id)
    fc45_test.gp_city2 = c2.id
  else
    log.normal("FC45TEST SKIP no second player or no site for Residentia (victim %s, spot %s)", tostring(victim ~= nil), tostring(spot ~= nil))
  end
  -- End the age next turn, and put the city one turn short of a birth: both are checked then.
  fc45_gp_set(fc45_gp_key("fc45_golden_until_", pid), game.turn() + 2)
  fc45_gp_set(fc45_gp_key("fc45_gp_pool_", city.id), 148)
  fc45_test.gp_city, fc45_test.gp_born = city.id, fc45_gp_get(fc45_gp_key("fc45_gp_born_", pid))
end

-- A turn later: the birth from the pool, the settling, and the age's end.
function fc45_gp_test_later()
  local city = find.city(nil, fc45_test.gp_city)
  if city == nil then
    log.normal("FC45TEST SKIP Testerburg is gone")
    return
  end
  local tester, pid = city.owner, city.owner.id
  local born = nil
  for u in city.tile:units_iterate() do
    if u.utype:rule_name() == "Great Sage" and u.owner.id == pid then born = u end
  end
  log.normal("FC45TEST birth: pool %s, born %s, sage %s", tostring(rawget(_G, fc45_gp_key("fc45_gp_pool_", city.id))),
             tostring(rawget(_G, fc45_gp_key("fc45_gp_born_", pid))), tostring(born ~= nil))
  check("a city one turn short of 150 points bears a Great Sage (its sources are a Library and a University), and the pool resets",
        born ~= nil and fc45_gp_get(fc45_gp_key("fc45_gp_pool_", city.id)) == 0
        and fc45_gp_get(fc45_gp_key("fc45_gp_born_", pid)) == fc45_test.gp_born + 1)
  check("the golden age has ended a turn later", not city:has_building(find.building_type("Golden Age"))
        and rawget(_G, fc45_gp_key("fc45_golden_until_", pid)) == nil)
  if fc45_test.gp_city2 ~= nil then
    local c2 = find.city(nil, fc45_test.gp_city2)
    local res = find.building_type("Resident Oracle")
    local owner_rec = c2 and rawget(_G, fc45_gp_key("fc45_gp_res_owner_", c2.id))
    log.normal("FC45TEST handover a turn later: city %s, owner %s, Resident Oracle %s, record owner %s",
               tostring(c2 ~= nil), c2 and c2.owner.name or "-", tostring(c2 and c2:has_building(res)), tostring(owner_rec))
    check("the handed-over city still has its Resident Oracle a turn later, under its new owner",
          c2 ~= nil and c2.owner.id ~= pid and c2:has_building(res) and owner_rec == c2.owner.id)
  end
  if born ~= nil then
    local join = find.action("Join City")
    local size = city.size
    local did = born:perform_action(join, city)
    local resident = find.building_type("Resident Sage")
    check("the Sage settles: the city grows by one and has a Resident Sage",
          did and city.size == size + 1 and city:has_building(resident))
    local second = edit.create_unit(tester, city.tile, find.unit_type("Great Sage"), 0, city, -1)
    local joined = second:perform_action(join, city)
    local deed = second:perform_action(find.action("User Action 3"))
    check("a second Sage cannot settle where a Resident Sage is, but can do its deed", not joined and deed)
    -- Residents stay with a captured city: the record names the kind, and the restore re-creates the building.
    local record = rawget(_G, fc45_gp_key("fc45_gp_res_", city.id))
    edit.remove_building(city, resident)
    fc45_gp_residents_restore(city, "test")
    log.normal("FC45TEST residents: record %s, Resident Sage back %s", tostring(record), tostring(city:has_building(resident)))
    check("a settled Sage is recorded for the city and re-created after the city changes hands",
          record == "Sage;" and city:has_building(resident))
  end
  -- The AI's rule (issue 121): the Sage's pledge from a turn ago still waits, no age runs, and a Great Magnate
  -- is born now; the rule pledges it at once, which makes the two kinds the second age needs.
  if rawget(_G, fc45_gp_key("fc45_golden_until_", pid)) == nil and fc45_gp_get(fc45_gp_key("fc45_golden_pledges_", pid)) == 1 then
    local magnate = edit.create_unit(tester, city.tile, find.unit_type("Great Magnate"), 0, city, -1)
    local mid = magnate.id
    fc45_gp_ai(tester, game.turn())
    local still = false
    for u in city.tile:units_iterate() do if u.id == mid then still = true end end
    log.normal("FC45TEST ai pledge: count %s, until %s, magnate left %s", tostring(rawget(_G, fc45_gp_key("fc45_golden_count_", pid))),
               tostring(rawget(_G, fc45_gp_key("fc45_golden_until_", pid))), tostring(still))
    check("the AI rule pledges a Great Magnate born a turn after the Sage's pledge, which starts the second golden age",
          not still and fc45_gp_get(fc45_gp_key("fc45_golden_count_", pid)) == 2
          and rawget(_G, fc45_gp_key("fc45_golden_until_", pid)) == game.turn() + 10)
  else
    log.normal("FC45TEST SKIP the AI pledge case: an age runs or no pledge waits")
  end
end

-- The tech tree: the six new techs and the three restored ones (John's decision of 2026-10-17) exist, and the
-- cost of a tech is what the Linear style gives: base_tech_cost 10 times the number of techs it needs counted
-- with itself (common/tech.c, num_reqs starts at 1), times the era's cost_pct (common/tech.c:273),
-- times Tech_Cost_Factor 3. Gunpowder needs 17 techs in the Renaissance (200%): 10 x 18 x 2 x 3 = 1080; Fusion
-- Power needs 70 in the Information era (275%): 710 x 2.75 = 1952.5 (the cost is a double), x 3 = 5857; a root tech such as Alphabet
-- is 30. Player:tech_cost reads research_total_bulbs_required for the Tester, who has no embassy, so no leakage
-- lowers it; under this style the cost does not depend on what the player already knows.
function fc45_tech_test_run(tester)
  local have = find.tech_type("Agriculture") ~= nil and find.tech_type("Hunting") ~= nil
    and find.tech_type("Archery") ~= nil and find.tech_type("Machinery") ~= nil
    and find.tech_type("Compass") ~= nil and find.tech_type("Printing") ~= nil
  local back = find.tech_type("Ruler Apotheosis") ~= nil and find.tech_type("Nanomaterials") ~= nil
    and find.tech_type("Labor Union") ~= nil
  check("the six new techs and the three restored ones exist", have and back)
  if not have then return end
  local al = tester:tech_cost(find.tech_type("Alphabet"))
  local gp, fp = tester:tech_cost(find.tech_type("Gunpowder")), tester:tech_cost(find.tech_type("Fusion Power"))
  log.normal("FC45TEST tech costs for the Tester: Alphabet %d, Gunpowder %d, Fusion Power %d (sciencebox %s)",
             al, gp, fp, tostring(server.setting.get("sciencebox")))
  check("a root tech (Alphabet) costs 30 bulbs", al == 30)
  check("Gunpowder costs 1080 bulbs (17 techs needed plus itself, Renaissance 200%)", gp == 1080)
  check("Fusion Power costs 5857 bulbs (70 techs needed plus itself, Information era 275%)", fp == 5857)
end

-- John's decisions of 2026-10-17 (plan decisions 10 and 11): the Horses gate, the two units that came back, the
-- restored techs' unlocks and the three themed buildings. Lua has no cargo getter and no city-level build check, so
-- the Transport's 4 and the Horses gate are shell checks; the Residents-on-capture and distinct-kind pledge cases sit with the great people cases.
function fc45_decisions_test_run(tester)
  local city = fc45_test.city
  if city == nil then
    log.normal("FC45TEST SKIP no Testerburg for the decisions cases")
    return
  end
  -- The Horses gate is a city-range Extra requirement, which Lua cannot test: Player:can_build_direct is
  -- can_player_build_unit_direct (common/unittype.c), which treats city-range requirements as possible, so it
  -- said true with no Horses anywhere near Testerburg. The runner greps the seven requirements instead.
  local alpine, zealots = find.unit_type("Alpine Troops"), find.unit_type("Zealots")
  check("Alpine Troops are back as a Gun unit that ignores terrain, Zealots as a mounted unit that withdraws",
        alpine ~= nil and alpine:has_flag("Gun") and alpine:has_flag("IgTer")
        and zealots ~= nil and zealots:has_flag("Mounted") and zealots:has_flag("Withdraws"))
  local altar, suffrage = find.building_type("Altar to The Divine Ruler"), find.building_type("Women's Suffrage")
  local no_altar, no_suffrage = tester:can_build_direct(altar), tester:can_build_direct(suffrage)
  edit.give_tech(tester, find.tech_type("Ruler Apotheosis"), 0, false, "test")
  edit.give_tech(tester, find.tech_type("Labor Union"), 0, false, "test")
  check("the Altar needs Ruler Apotheosis and Women's Suffrage needs Labor Union again",
        not no_altar and not no_suffrage and tester:can_build_direct(altar) and tester:can_build_direct(suffrage))
  local catapult = edit.create_unit(tester, city.tile, find.unit_type("Catapult"), 0, city, -1)
  local vet0, health0, routes0 = effects.unit_bonus(catapult, nil, "Veteran_Build"), effects.city_bonus(city, "Health_Pct"),
                                 effects.city_bonus(city, "Max_Trade_Routes")
  city:create_building(find.building_type("Siege Workshop"))
  city:create_building(find.building_type("Apothecary"))
  city:create_building(find.building_type("Telegraph Office"))
  local vet1, health1, routes1 = effects.unit_bonus(catapult, nil, "Veteran_Build"), effects.city_bonus(city, "Health_Pct"),
                                 effects.city_bonus(city, "Max_Trade_Routes")
  log.normal("FC45TEST themed buildings: Veteran_Build %d to %d, Health_Pct %d to %d, Max_Trade_Routes %d to %d",
             vet0, vet1, health0, health1, routes0, routes1)
  check("a Siege Workshop gives siege units a veteran level, an Apothecary 30 health, a Telegraph Office a trade route",
        vet1 == vet0 + 1 and health1 == health0 + 30 and routes1 == routes0 + 1)
  catapult:kill("disbanded", nil)
end

-- Slice 3, upgrades and the draft. The Tester gets a city of its own (it has none: nothing moved its
-- Settlers), the techs and the gold, and acts through the real "Upgrade Unit" and "Disband Unit Recover"
-- enablers. Lua cannot read a city's shield stock or build a unit, so the 30 shields of a disbanded draft unit
-- are read by the runner from the next autosave (the city is named for that), and a draft unit's citizen
-- cost is seen in the autogame's city_size_change signal, not here.
function fc45_draft_test_run(tester, used)
  local levy, militia, conscripts = find.unit_type("Levy"), find.unit_type("Militia"), find.unit_type("Conscripts")
  if levy == nil or militia == nil or conscripts == nil then
    check("the ruleset has the Levy, Militia and Conscripts draft units", false)
    return
  end
  check("the three draft units carry the Draft flag",
        levy:has_flag("Draft") and militia:has_flag("Draft") and conscripts:has_flag("Draft"))
  local before = tester:can_build_direct(militia)
  edit.give_tech(tester, find.tech_type("Bronze Working"), 0, false, "test")
  edit.give_tech(tester, find.tech_type("Gunpowder"), 0, false, "test")
  check("a Levy can be raised with Bronze Working and a Militia only once Gunpowder is known",
        tester:can_build_direct(levy) and not before and tester:can_build_direct(militia))

  -- A free tile that takes a city: grassland or plains (the map's free rows are glacier, which refuses
  -- cities), and no city within citymindist (3: none in the 5-by-5 square around it).
  local spot, city
  for t in whole_map_iterate() do
    local terrain = t.terrain:rule_name()
    if (terrain == "Grassland" or terrain == "Plains") and free(t) and not used[t.id] then
      local near = false
      for a in t:circle_iterate(8) do if a:city() ~= nil then near = true end end
      if not near then
        used[t.id] = true
        spot = t
        if edit.create_city(tester, t, "Testerburg") then city = t:city() end
        break
      end
    end
  end
  if spot == nil then
    log.normal("FC45TEST SKIP no free grassland or plains for the Tester's city")
    return
  end
  if city == nil then
    check("the Tester founds Testerburg on free land", false)
    return
  end
  log.normal("FC45TEST Testerburg is city %d at tile %d on turn %d", city.id, spot.id, game.turn())

  -- A hardened (level 2) Spearmen (rule name Phalanx) upgraded in its city keeps its level. "Upgrade Unit"
  -- goes to the newest type the chain reaches, Musketeers here since Gunpowder is known (Spearmen, Pikemen,
  -- Musketeers), and costs 2 * missing + missing^2 / 20 gold, where missing is the Musketeers' 60 shields
  -- less half the Spearmen's 20 (Unit_Shield_Value_Pct -50 for the price): 50, so 225 gold.
  edit.give_tech(tester, find.tech_type("Feudalism"), 0, false, "test")
  edit.change_gold(tester, 1000)
  local gold = tester:gold()
  local ph = edit.create_unit(tester, spot, find.unit_type("Phalanx"), 2, city, -1)
  local upgraded = ph:perform_action(find.action("Upgrade Unit"), city)
  local after = nil
  for u in spot:units_iterate() do if u.id == ph.id then after = u end end
  log.normal("FC45TEST upgrade: performed %s, now %s, veteran %s, gold %d -> %d", tostring(upgraded),
             after and after.utype:rule_name() or "gone", after and tostring(after.veteran) or "-", gold, tester:gold())
  check("a hardened Spearmen upgraded in its city is a Musketeers that is still hardened, for 225 gold",
        upgraded and after ~= nil and after.utype:rule_name() == "Musketeers" and after.veteran == 2
        and tester:gold() == gold - 225)

  -- A Levy disbanded into the city's build is gone; the runner checks the 30 shields in the autosave.
  local lv = edit.create_unit(tester, spot, levy, 0, city, -1)
  local n = spot:num_units()
  local whipped = lv:perform_action(find.action("Disband Unit Recover"), city)
  check("a Levy disbands into Testerburg's build and is gone", whipped and spot:num_units() == n - 1)
  log.normal("FC45TEST expect disbanded shields 30 in Testerburg")
  fc45_test.city = city
  fc45_unrest_test_run(tester, city, spot, levy, militia)
end

-- Draft and whip unrest (issue 107). Lua cannot build a unit, so the ruleset's unit_built handler is called
-- the way the signal calls it; the faces, the quota, a sold unrest building and the expiry are then read back.
function fc45_unrest_test_run(tester, city, spot, levy, militia)
  if fc45_draft_unit_built == nil then
    check("the ruleset has the draft unrest rule (fc45_draft_unit_built)", false)
    return
  end
  local key = fc45_gp_key("fc45_unrest_", city.id)
  local u1, u2, u4 = find.building_type("Draft Unrest 1"), find.building_type("Draft Unrest 2"), find.building_type("Draft Unrest 4")
  local mc0 = effects.city_bonus(city, "City_Unrest")
  local lv = edit.create_unit(tester, spot, levy, 0, city, -1)
  fc45_draft_unit_built(lv, city)
  local mc1, rec1 = effects.city_bonus(city, "City_Unrest"), rawget(_G, key)
  log.normal("FC45TEST unrest after a Levy: City_Unrest %d to %d, record %s", mc0, mc1, tostring(rec1))
  check("a Levy built in Testerburg makes one content citizen unhappy for ten turns (Draft Unrest 1, City_Unrest 1)",
        city:has_building(u1) and not city:has_building(u2) and mc0 == 0 and mc1 == 1
        and rec1 == string.format("%d:1;", game.turn() + 10))
  local ml = edit.create_unit(tester, spot, militia, 0, city, -1)
  fc45_draft_unit_built(ml, city)
  local mc2 = effects.city_bonus(city, "City_Unrest")
  check("a Militia drafted there too adds three faces, four in all (Draft Unrest 4 alone, City_Unrest 4)",
        city:has_building(u4) and not city:has_building(u2) and not city:has_building(u1) and mc2 == 4)
  edit.remove_building(city, u4)
  fc45_unrest_lost(city, u4, "sold", nil)
  check("an unrest building sold away comes straight back", city:has_building(u4))
  local limit = fc45_draft_limit()
  for i = 2, limit do fc45_draft_counted(tester, "Militia") end
  local quota = find.building_type("Draft Quota")
  log.normal("FC45TEST draft quota: limit %d, drafts %d, quota %s", limit,
             fc45_gp_get(fc45_gp_key("fc45_drafts_n_", tester.id)), tostring(tester:has_wonder(quota)))
  check("after the turn's draft limit no Militia can be raised, while a Levy (the whip) still can",
        limit >= 1 and limit <= 5 and not tester:can_build_direct(militia) and tester:can_build_direct(levy))
  lv:kill("disbanded", nil)
  ml:kill("disbanded", nil)
  -- The Levy's face ends next turn and the Militia's three stay.
  fc45_gp_set(key, string.format("%d:1;%d:3;", game.turn() + 1, game.turn() + 10))
  fc45_test.unrest_city = city.id
  -- City_Unrest reaches the base content citizens (issue 157): a new size-1 city with no buildings has one
  -- content citizen; one face of unrest makes it unhappy, so the city falls into disorder.
  local site = nil
  for t in city.tile:square_iterate(8) do
    if site == nil and t:sq_distance(city.tile) >= 49 and t:city() == nil and t:num_units() == 0
       and (t.terrain:rule_name() == "Grassland" or t.terrain:rule_name() == "Plains") then site = t end
  end
  if site ~= nil and edit.create_city(tester, site, "Unrestia") then
    local c3 = site:city()
    local calm = not c3:is_unhappy()
    edit.create_building(c3, u1)
    local riot = c3:is_unhappy()
    edit.remove_building(c3, u1)
    -- edit.remove_building does not refresh the city; adding a building with no mood effect does.
    edit.create_building(c3, find.building_type("Barracks"))
    local calm_again = not c3:is_unhappy()
    log.normal("FC45TEST City_Unrest in a new size %d city: calm %s, in disorder with one face %s, calm again %s",
               c3.size, tostring(calm), tostring(riot), tostring(calm_again))
    check("one face of unrest makes the only (base content) citizen of a city with no buildings unhappy",
          calm and riot and calm_again)
    edit.remove_city(c3)
  else
    log.normal("FC45TEST SKIP no site for Unrestia")
  end
end

function fc45_unrest_test_later()
  local city = find.city(nil, fc45_test.unrest_city)
  if city == nil then
    log.normal("FC45TEST SKIP Testerburg is gone for the unrest case")
    return
  end
  local has = function(n) return city:has_building(find.building_type("Draft Unrest " .. n)) end
  log.normal("FC45TEST unrest a turn later: record %s, buildings 1 %s, 2 %s, 4 %s",
             tostring(rawget(_G, fc45_gp_key("fc45_unrest_", city.id))), tostring(has(1)), tostring(has(2)), tostring(has(4)))
  check("a turn later the expired face is gone and the three left are Draft Unrest 2 and 1",
        has(1) and has(2) and not has(4))
  check("the draft quota is lifted at the next turn: Militia can be raised again",
        city.owner:can_build_direct(find.unit_type("Militia")))
end

-- The roster (slice 10, notes/freeciv45/design/units-and-upgrades.md): the renamed units keep their rule
-- names, the dropped ones are gone, the new ones exist, the counters work through the bonuses rows, and
-- City Walls are keyed on the attacker's class flag.
function fc45_roster_test_run(tester, animals, used)
  local renamed = { Phalanx = "Spearmen", Legion = "Swordsmen", Elephants = "War Elephants", Armor = "Tank",
                    Nuclear = "Atom Bomb", ["Mech. Inf."] = "Mechanized Infantry", Helicopter = "Gunship",
                    AWACS = "Radar Plane", ["AEGIS Cruiser"] = "Missile Cruiser", SSBN = "Missile Submarine",
                    ICBM = "Nuclear Missile" }
  local ok = true
  for rule, shown in pairs(renamed) do
    local ut = find.unit_type(rule)
    if ut == nil or ut:name_translation() ~= shown then
      ok = false
      log.normal("FC45TEST rename: %s shows as %s", rule, ut and ut:name_translation() or "nil")
    end
  end
  check("the eleven renamed units keep their rule names and show the new ones", ok)
  ok = true
  for _, name in ipairs({ "Jaguar Warrior", "Immortal", "Crusaders", "Mechanic" }) do
    if find.unit_type(name) ~= nil then ok = false end
  end
  check("Jaguar Warrior, Immortal, Crusaders and Mechanic are gone (Alpine Troops came back, Crusaders as Zealots)", ok)
  ok = true
  for _, name in ipairs({ "Scout", "Axemen", "Horse Bowmen", "War Galley", "Macebearers", "Longbowmen",
                          "Crossbowmen", "Trebuchet", "Grenadiers", "Ship of the Line", "Infantry",
                          "Machine Gunners", "Armoured Cars", "Main Battle Tank", "Air Defence Infantry",
                          "Jet Fighter" }) do
    if find.unit_type(name) == nil then ok = false; log.normal("FC45TEST missing unit %s", name) end
  end
  check("the sixteen new units exist", ok)
  check("Spearmen and Pikemen carry Melee, Horsemen Mounted, Musketeers Gun, Catapult Siege, Tank Armour",
        find.unit_type("Phalanx"):has_flag("Melee") and find.unit_type("Pikemen"):has_flag("Melee")
        and find.unit_type("Horsemen"):has_flag("Mounted") and find.unit_type("Musketeers"):has_flag("Gun")
        and find.unit_type("Catapult"):has_flag("Siege") and find.unit_type("Armor"):has_flag("Armour"))

  -- The Spear counter: War Elephants (strength 8, Mounted, no Withdraws, so the fight is to the death)
  -- attack Pikemen (strength 6, doubled against Mounted to 12) on open grassland or plains twenty times.
  -- The Pikemen win a round with 12/20 and the fight (ten rounds before losing ten, 10 hit points each,
  -- firepower 1) with 0.81, so they win 11 or more of 20 with 0.998; without the counter (8 against 6)
  -- they win a fight with 0.26 and 11 of 20 with 0.006. A river on the spot would raise both.
  local attack = find.action("Attack")
  local spot, side
  for t in whole_map_iterate() do
    local terrain = t.terrain:rule_name()
    if (terrain == "Grassland" or terrain == "Plains") and free(t) and not used[t.id] and not t:has_extra("River") then
      for a in t:circle_iterate(2) do
        if a.id ~= t.id and free(a) and not used[a.id] and find.unit_type("Elephants"):can_exist_at_tile(a) then
          spot, side = t, a; break
        end
      end
      if spot ~= nil then used[spot.id] = true; used[side.id] = true; break end
    end
  end
  if spot == nil then
    log.normal("FC45TEST SKIP no open grassland or plains for the counter case")
  else
    local wins, fights = 0, 0
    for _ = 1, 20 do
      local pk = edit.create_unit(animals, spot, find.unit_type("Pikemen"), 0, nil, -1)
      local el = edit.create_unit(tester, side, find.unit_type("Elephants"), 0, nil, -1)
      local pid = pk.id
      if el:perform_action(attack, spot) then
        fights = fights + 1
        if find.unit(animals, pid) ~= nil then wins = wins + 1 end
      end
      for u in spot:units_iterate() do u:kill("disbanded", nil) end
      for u in side:units_iterate() do u:kill("disbanded", nil) end
    end
    log.normal("FC45TEST counter: Pikemen won %d of %d fights against War Elephants on %s", wins, fights,
               spot.terrain:rule_name())
    check("Pikemen beat attacking War Elephants in at least 11 of 20 fights (the Spear counter doubles them)",
          fights == 20 and wins >= 11)
  end

  -- City Walls (Defend_Bonus 100) apply to a Melee or Siege attacker and not to a Gun one or the Howitzer.
  -- effects.unit_bonus evaluates the effect with the unit's type and the city on its tile, so a unit standing
  -- in Testerburg stands in for an attacker of its type; the walls' share is the rise when they are built
  -- (every city already gives 50 against Ground attackers, effect_city_defense_0).
  local city = fc45_test.city
  if city == nil then
    log.normal("FC45TEST SKIP no Testerburg for the walls case")
  else
    local units, before, after = {}, {}, {}
    for i, name in ipairs({ "Warriors", "Musketeers", "Catapult", "Howitzer" }) do
      units[i] = edit.create_unit(tester, city.tile, find.unit_type(name), 0, city, -1)
      before[i] = effects.unit_bonus(units[i], nil, "Defend_Bonus")
    end
    city:create_building(find.building_type("City Walls"))
    for i = 1, 4 do after[i] = effects.unit_bonus(units[i], nil, "Defend_Bonus") end
    log.normal("FC45TEST walls: Defend_Bonus without and with City Walls: Warriors %d %d, Musketeers %d %d, Catapult %d %d, Howitzer %d %d",
               before[1], after[1], before[2], after[2], before[3], after[3], before[4], after[4])
    check("City Walls add Defend_Bonus 100 against Melee and Siege attackers and nothing against Gun and the Howitzer",
          after[1] - before[1] == 100 and after[3] - before[3] == 100 and after[2] == before[2] and after[4] == before[4])
    for _, u in ipairs(units) do u:kill("disbanded", nil) end
  end
end

-- Victory rules: the settings the server exposes, and the domination script's counting and decision with
-- the thresholds overridden (the real ones cannot be met at turn 5, when the test runs). The keys Lua cannot read
-- (victory_min_points, victory_lead_pct, endturn, endspaceship in game.ruleset) are checked by the runner.
function fc45_victory_test_run()
  local function setting(name) return string.upper(server.setting.get(name) or "?") end
  check("victories are the space race, the last alliance standing and culture",
        setting("victories") == "SPACERACE|ALLIED|CULTURE")
  check("the game ends when a spaceship arrives (endspaceship enabled)", setting("endspaceship") == "ENABLED")
  if fc45_domination_qualifiers == nil then
    log.normal("FC45TEST SKIP no domination script loaded")
    return
  end
  local civs = 0
  for p in players_iterate() do if fc45_is_civ(p) then civs = civs + 1 end end
  local q, land, pop = fc45_domination_qualifiers(0, 0)
  check("every living civ qualifies for domination at thresholds of 0", #q == civs and civs > 0 and pop > 0)
  local q2 = fc45_domination_qualifiers(60, 50)
  check("no civ qualifies at 60% of the land and 50% of the citizens at turn 5", #q2 == 0)
  local mine = 0
  for t in whole_map_iterate() do if t.terrain:class_name() ~= "Oceanic" then mine = mine + 1 end end
  check("the domination land count equals the map's non-oceanic tiles", land == mine)
  local from = FC45_DOM_FROM_TURN
  FC45_DOM_FROM_TURN = 0
  fc45_domination_check(game.turn(), 0)
  FC45_DOM_FROM_TURN = from
  local zero, seen = true, 0
  for p in players_iterate() do
    if fc45_is_civ(p) then
      seen = seen + 1
      if _G[string.format("fc45_dom_run_%d", p.id)] ~= 0 then zero = false end
    end
  end
  check("a domination check at 60/50 leaves every civ's run counter at 0", zero and seen == civs)
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
  -- kill it, and dies only if it loses 10 of at most 12 rounds (about 1 fight in 90 at strength 10 against
  -- 9), so both are alive afterwards; two tries make a false failure negligible. Without the cap
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
    if fc45_test.gp_city ~= nil then fc45_gp_test_later() end
    if fc45_test.unrest_city ~= nil then fc45_unrest_test_later() end
    -- Run with --extra "set endturn <this turn>": the ruleset names the best score the winner at the
    -- start of the last turn, and the runner checks the server's victory line against this one.
    if fc45_best_score ~= nil and tonumber(server.setting.get("endturn")) == turn then
      local best, score = fc45_best_score()
      if best ~= nil then
        log.normal("FC45TEST expect victory to the %s (score %d)", best.nation:plural_translation(), score)
      end
    end
    local tile = find.tile(fc45_test.stack_tile)
    check("a stack of three Tester units is still together a turn later", tile ~= nil and tile:num_units() == 3)
    log.normal("FC45TEST DONE %d/%d", fc45_test.passed, fc45_test.total)
  end
  return false
end
signal.connect("turn_begin", "fc45_rules_test_turn")
log.normal("FC45TEST loaded at turn %d", game.turn())
