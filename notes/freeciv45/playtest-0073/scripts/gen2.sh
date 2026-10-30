#!/bin/bash
# gen2.sh <turns>: human-seat play script. Turn 1 founds the capital(s) with key b; later cities come from Lua (edit.create_city) every few turns.
N=$1
NM=(x Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lambda Mu Nu Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega Aleph Bet Gimel Dalet He Vav Zayin Chet Tet Yod Kaf Lamed Mem Nun Samekh Ayin Pe Tsade Qof Resh Shin Tav Argos Thebes Sparta Delphi Corinth Megara Elis Pylos Tiryns Mycenae Knossos Rhodes Samos Chios Lesbos Naxos Paros Delos Kos Thera Ios Syros Tinos Andros Kea Milos Sifnos Serifos Kimolos Folegandros Sikinos Anafi Amorgos Donousa Koufonisi Iraklia Schinoussa Kythnos Gyaros Skyros Euboea Aegina Salamis Hydra Poros Spetses Kythira Antikythera Zakynthos Kefalonia Ithaca Lefkada Paxos Corfu)
MORE='local function more(p, name) for c in p:cities_iterate() do for tt in c.tile:square_iterate(8) do if tt:city() == nil and tt.terrain:class_name() == "Land" then local ok = true; for c2 in p:cities_iterate() do if c2.tile:sq_distance(tt) < 16 then ok = false end end; for c3 in tt:square_iterate(3) do if c3:city() ~= nil and c3:city().owner ~= p then ok = false end end; if ok then edit.create_city(p, tt, name); if tt:city() ~= nil then edit.create_unit(p, tt, find.unit_type("Warriors"), 0, nil, -1); return end end end end end end; for p in players_iterate() do if p:is_human() then more(p, "NAME") end end'
cat <<'H'
pace 300
option gui_qt_freeciv45_edges on
dismiss
wait 8000
key Escape
dismiss
chat /lua cmd for p in players_iterate() do if p:is_human() then local t = nil; for u in p:units_iterate() do if u.utype:has_flag("Cities") then t = u.tile; break end end; if t then edit.create_city(p, t, "Alpha"); for u in t:units_iterate() do if u.utype:has_flag("Cities") then edit.unit_kill(u, "disbanded", nil) end end end end end
wait 3000
H
for t in $(seq 1 $N); do
echo "wait 1500"; echo dismiss; echo activate; echo "click button Return to map"; echo "wait 1200"
if [ $t -ge 3 ] && { [ $((t % 3)) -eq 0 ] || [ $t -gt 40 -a $((t % 5)) -eq 0 ]; }; then
  echo "chat /lua cmd ${MORE//NAME/${NM[$t]}}"; echo "wait 2500"; echo "city ${NM[$t]}"
fi
for k in 1 2 3 4; do echo "chooser $((2 + (t+k) % 4)) 0"; echo "wait 1000"; echo "click button Return to map"; done
echo "state t$t"
for k in 1 2 3; do echo "click tip for orders; shows the next one"; echo "wait 600"; echo center; echo "key f"; echo "wait 400"; done
if [ $((t % 20)) -eq 0 ] || [ $t -eq 15 ]; then echo "shot t$t"; fi
echo endturn
echo "wait $((6000 + t*60))"
done
echo "state final"; echo "shot final"; echo quit
