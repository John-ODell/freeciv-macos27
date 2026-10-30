#!/bin/bash
# gen3.sh: chooser break scenarios (test 2). Human seat + 2 AIs. No click outside a chooser while one is open (that closes it unpicked, which stops the chain for the turn).
MORE='local function more(p, name) for c in p:cities_iterate() do for tt in c.tile:square_iterate(8) do if tt:city() == nil and tt.terrain:class_name() == "Land" then local ok = true; for c2 in p:cities_iterate() do if c2.tile:sq_distance(tt) < 16 then ok = false end end; for c3 in tt:square_iterate(3) do if c3:city() ~= nil and c3:city().owner ~= p then ok = false end end; if ok then edit.create_city(p, tt, name); if tt:city() ~= nil then return end end end end end end; for p in players_iterate() do if p:is_human() then more(p, "NAME") end end'
found() { echo "chat /lua cmd ${MORE//NAME/$1}"; echo "wait 3500"; echo "city $1"; echo "state $2"; }
byname() { echo "local tc = nil; for p in players_iterate() do for c in p:cities_iterate() do if c.name == \"$1\" then tc = c end end end; if tc then $2 end"; }
pick() { echo "chooser 3 0"; echo "wait 2500"; echo "state $1"; echo "activate"; echo "click button Return to map"; echo "wait 800"; }
cat <<'H'
pace 400
option gui_qt_freeciv45_edges on
dismiss
wait 8000
key Escape
dismiss
chat /lua cmd for p in players_iterate() do if p:is_human() then local t = nil; for u in p:units_iterate() do if u.utype:has_flag("Cities") then t = u.tile; break end end; if t then edit.create_city(p, t, "Alpha"); edit.create_building(t:city(), find.building_type("Marco Polo's Embassy")); for u in t:units_iterate() do if u.utype:has_flag("Cities") then edit.unit_kill(u, "disbanded", nil) end end end end end
wait 3500
state s0open
chooser 3 0
wait 2500
state s0picked
click button Return to map
wait 800
chat /lua cmd local mx, my = 0, 0; for t in whole_map_iterate() do if t.nat_x > mx then mx = t.nat_x end; if t.nat_y > my then my = t.nat_y end end; local best, bd = nil, 1e9; for t in whole_map_iterate() do if t.terrain:class_name() == "Land" and t:city() == nil then local d = (t.nat_x - mx / 2) ^ 2 + (t.nat_y - my / 2) ^ 2; if d < bd then bd = d; best = t end end end; for p in players_iterate() do if p:is_human() then edit.create_unit(p, best, find.unit_type("Warriors"), 0, nil, -1); edit.create_unit(p, best, find.unit_type("Warriors"), 0, nil, -1) end end
wait 2000
state c0
center
click tip for orders; shows the next one
wait 1500
center
click tip for orders; shows the next one
wait 1500
center
shot c1
H
echo "state S1-city-removed-while-its-chooser-is-open"
found Beta s1open; echo "shot s1open"
echo "chat /lua cmd $(byname Beta 'tc:remove()')"; echo "wait 2000"; echo "state s1removed"
echo "wait 1500"; echo "state s1later"
pick s1picked; echo "city Alpha"
echo "state S2-city-captured-while-its-chooser-is-open"
found Gamma s2open
echo "chat /lua cmd local ai = nil; for q in players_iterate() do if not q:is_human() then ai = q; break end end; $(byname Gamma 'tc:transfer(ai)')"
echo "wait 2000"; echo "state s2captured"; echo "city Gamma"
pick s2picked
echo "state S3-turn-changes-with-a-chooser-open"
found Delta s3open
echo "endturn"; echo "wait 9000"; echo "dismiss"; echo "activate"; echo "wait 2500"; echo "state s3turn"; echo "shot s3turn"
pick s3picked
echo "state S4-diplomacy-meeting-while-a-chooser-is-open"
found Epsilon s4open
echo "meet 1"; echo "wait 3000"; echo "state s4meet"; echo "shot s4meet"
pick s4picked; echo "dismiss"
echo "state S5-city-dialog-opened-with-a-chooser-open"
found Zeta s5open
echo "opencity Alpha"; echo "wait 2000"; echo "state s5dialog"; echo "shot s5dialog"
pick s5picked
echo "state S6-city-removed-then-Cancel"
found Eta s6open
echo "chat /lua cmd $(byname Eta 'tc:remove()')"; echo "wait 1500"; echo "state s6removed"
echo "chooser last 0"; echo "wait 2500"; echo "state s6cancel"
echo "state S7-game-ends-with-a-chooser-open"
echo "endturn"; echo "wait 9000"; echo "dismiss"; echo "activate"; echo "wait 2500"
found Theta s7open
echo "chat /set endturn 4"; echo "wait 1500"
echo "endturn"; echo "wait 12000"; echo "state s7end"; echo "shot s7end"
echo "wait 3000"; echo "state s7after"
echo quit
