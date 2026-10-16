-- SPDX-License-Identifier: GPL-2.0-or-later
-- civ45 one-unit-per-tile rules test. Load it into a civ45 server before the game starts with the command
--   lua file scripts/civ45-rules-test.lua
-- (scripts/civ45-rules-test.sh does that; an autogame reads no console input once it runs). It runs once,
-- at the first turn start from turn 12 on, and
-- prints "CIV45TEST PASS|FAIL <case>" lines to the server log and a final "CIV45TEST DONE <n>/<total>".
-- Uses a coastal city: moves through the real "Unit Move" enablers via Unit:perform_action, and calls
-- the global sweep callback from data/civ45/script.lua directly.

function civ45_rules_test_run()
  local passed, total = 0, 0
  local function check(name, ok)
    total = total + 1
    if ok then passed = passed + 1 end
    log.normal("CIV45TEST %s %s", ok and "PASS" or "FAIL", name)
  end

  local move = find.action("Unit Move")
  local function free(t)
    return t:num_units() == 0 and t:city() == nil and not t:has_extra("Hut") and not t:has_extra("Hermit")
  end
  local function oceanic(t) return t.terrain:class_name() == "Oceanic" end
  local function count_on(tile, pred)
    local n = 0
    for u in tile:units_iterate() do if pred(u) then n = n + 1 end end
    return n
  end

  -- Find a city with one free land neighbour and an ocean neighbour that has a free ocean neighbour.
  local city, land, sea1, sea2
  for p in players_iterate() do
    for c in p:cities_iterate() do
      local l, s1, s2
      for t in c.tile:circle_iterate(1) do
        if t.id ~= c.tile.id and free(t) then
          if oceanic(t) then
            if s1 == nil then
              for t2 in t:circle_iterate(1) do
                if t2.id ~= t.id and t2.id ~= c.tile.id and free(t2) and oceanic(t2) then s1, s2 = t, t2; break end
              end
            end
          elseif l == nil and find.unit_type("Phalanx"):can_exist_at_tile(t) then
            l = t
          end
        end
      end
      if l and s1 and s2 then city, land, sea1, sea2 = c, l, s1, s2; break end
    end
    if city then break end
  end

  if city == nil then
    log.normal("CIV45TEST SKIP no coastal city with free land and sea neighbours yet")
  else
    local owner = city.owner
    local function make(type_name, tile)
      return edit.create_unit(owner, tile, find.unit_type(type_name), 0, city, -1)
    end
    -- garrison: make sure the city tile holds exactly one land unit
    if count_on(city.tile, function(u) return u:transporter() == nil end) == 0 then
      make("Phalanx", city.tile)
    end
    log.normal("CIV45TEST city %s (%s), land %d, sea %d/%d", city.name, owner.name, land.id, sea1.id, sea2.id)

    local walker = make("Phalanx", land)
    check("land unit cannot move into an occupied city",
          not walker:perform_action(move, city.tile) and walker.tile.id == land.id)

    local fighter = make("Fighter", land)  -- shares land with walker only for the moment
    check("fighter (StacksAnywhere) can move into an occupied city",
          fighter:perform_action(move, city.tile) and fighter.tile.id == city.tile.id)

    local ship = make("Destroyer", sea1)
    check("ship (StacksInPort) can move into an occupied city",
          ship:perform_action(move, city.tile) and ship.tile.id == city.tile.id)

    local ship_a = make("Destroyer", sea1)
    local ship_b = make("Destroyer", sea2)
    check("ship cannot move onto an occupied ocean tile",
          not ship_b:perform_action(move, sea1) and ship_b.tile.id == sea2.id)

    -- sweep: garrison + fighter + ship in the city must stay put; an extra land unit must leave
    local extra = make("Musketeers", city.tile)
    civ45_turn_begin_callback(game.turn(), 0)
    local land_left = count_on(city.tile, function(u)
      return u:transporter() == nil and not u.utype:has_flag("StacksAnywhere") and not u.utype:has_flag("StacksInPort")
    end)
    check("sweep leaves one land unit in the city", land_left == 1)
    check("sweep keeps the fighter in the city", fighter.tile.id == city.tile.id)
    check("sweep keeps the ship in port", ship.tile.id == city.tile.id)
    check("sweep keeps the better defender (Musketeers) in the city", extra.tile.id == city.tile.id)
    check("sweep never leaves two land units on one tile nearby",
          (function()
            for t in city.tile:circle_iterate(50) do
              if count_on(t, function(u) return u:transporter() == nil and not u.utype:has_flag("StacksAnywhere")
                            and not (u.utype:has_flag("StacksInPort") and t:city() ~= nil) end) > 1 then return false end
            end
            return true
          end)())
  end
  log.normal("CIV45TEST DONE %d/%d", passed, total)
end

function civ45_rules_test_turn(turn, year)
  if turn >= 12 and civ45_rules_test_ran == nil then
    civ45_rules_test_ran = true
    civ45_rules_test_run()
  end
  return false
end
signal.connect("turn_begin", "civ45_rules_test_turn")
log.normal("CIV45TEST loaded at turn %d", game.turn())
