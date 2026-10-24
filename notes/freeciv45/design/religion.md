# Freeciv45 religion, first version

Roadmap slice 12 of [freeciv45-plan.md](../../freeciv45-plan.md) and part 4, first slice, of
[standalone.md](../standalone.md) (issue 273), made concrete. It builds on [mechanics.md](../mechanics.md) 2.10 (the
reference behaviour, rated MUST simplified: Lua founds a faith when its tech is first learned, spreads it to cities
with none, and marker buildings drive temple and state-faith happiness and shrine gold; missionaries, a religious
council and AI attitudes come later) and copies the patterns of [great-people.md](great-people.md): marker
buildings that nobody can build, a Lua record that is the source of truth, and native effects so the AI values
what it can see. Engine paths are the patched tree at patch 0050 (`series-0050`, 5dec93d); `civ45/...` is
`data/civ45/...` there.

## 1. What it does in play

- **Seven faiths, founded by tech.** The first civ to learn a founding tech founds that faith in one of its
  cities, which becomes the faith's **holy city**. A later discoverer gets nothing.
- **Faiths spread on their own** into cities that follow none yet, faster near many cities of that faith, faster
  still near the holy city or inside the same nation. Borders don't stop it: a neighbour's faith seeps into your
  frontier towns.
- **Each nation has a state faith,** picked for it: the faith most of its cities follow. Cities of the state faith
  get one more content citizen, and their Temples and Cathedrals one more each. Cities of other faiths get
  nothing extra, so a nation split between faiths is harder to keep happy.
- **A holy city adds 2 history (culture) a turn.** A first version also gave every city 1 history a turn for each
  faith it followed; in the balance games that nearly doubled the world's culture and brought seed 13's culture
  victory about 100 turns early (section 6), so it was dropped.
- **The Shrine,** which only a holy city can build, makes 2 citizens content, adds 25% gold, and pays its owner
  1 gold a turn for every city in the world that follows its faith, whoever owns them.

What that changes: the early race for Mysticism, Polytheism and Philosophy matters for more than wonders; a
holy city is a prize worth a war; and where a nation expands (towards its own faith or into a rival's) decides
how happy its cities are.

## 2. The faiths

The names are Freeciv45's own; no real religion is named or drawn. The founding techs are the seven
religious and philosophical techs of the tree, eras I to III ([tech-tree.md](tech-tree.md) rows 82-114).

| # | Faith | Founded by | Era | Tech row |
|---|---|---|---|---|
| 1 | The Hearth | Mysticism | I | tech-tree.md:82 |
| 2 | The Many Hands | Polytheism | II | tech-tree.md:97 |
| 3 | The Sun Throne | Ruler Apotheosis | II | tech-tree.md:98 |
| 4 | The Quiet Way | Philosophy | II | tech-tree.md:99 |
| 5 | The Star Path | Astronomy | III | tech-tree.md:112 |
| 6 | The One Flame | Monotheism | III | tech-tree.md:113 |
| 7 | The Deep Well | Theology | III | tech-tree.md:114 |

All seven work the same; only the names differ (as in the reference, mechanics.md 2.10).

## 3. What the engine gives and what Lua must do

| Need | How | Evidence |
|---|---|---|
| Know a tech was learned first | `tech_researched(tech, player, reason)`; a `fc45_rel_founded_<n>` global marks the faith as taken | signal at `server/scripting/script_server.c:483`; the great people use it the same way (`civ45/script.lua:944-953`) |
| A faith in a city | A marker improvement `<Faith> Faith` per faith, created by `edit.create_building` | `tolua_server.pkg:149-150`; it refuses only the Special genus (`api_server_edit.c:727-731`), so markers are `Improvement`, like the Residents (`civ45/buildings.ruleset`, `[building_resident_sage]`) |
| Markers can be sold or razed | They are improvements, so a player can sell one (`common/improvement.c:1104-1116`) and conquest may raze it (`server/citytools.c:930-942`). The Lua record `fc45_rel_<city id>` is the truth: `building_lost` re-creates a sold or razed marker at once and `city_transferred` after conquest, as the draft-unrest markers do (`civ45/script.lua:1122-1128`) | |
| A state faith | A hidden small wonder `<Faith> State Faith` per faith, kept by Lua in the capital, so effects can use `Building ... Player`, as the Golden Age does (great-people.md section 5) | `Player:primary_capital()` at `tolua_game.pkg:233-234` |
| Distance for spread | `Tile:sq_distance(other)` | `tolua_game.pkg:383-384` |
| The AI values the effects | `Make_Content`, `Output_Bonus` and `History` are all weighed by the default AI's building wants | `ai/default/daieffects.c:184, 238, 626` |
| Shrine gold | `edit.change_gold(owner, n)` each `turn_begin` | `tolua_server.pkg:176-177` |
| Persistence | Only scalar globals survive a save, so the record is one string per city (`"1;4;"`) and one number per faith or player | great-people.md section 1, last row |

## 4. Rules

### 4.1 Founding

On `tech_researched` with a founding tech, if `fc45_rel_founded_<n>` is unset and the player is a civ (not
barbarian) with at least one city:

1. the holy city is the player's largest city that follows no faith, else its largest city;
2. the faith is added to that city (record plus marker), `fc45_rel_holy_<n>` is set to its id, and the city gets
   the `Holy City` marker;
3. everyone is told: "The Hearth has been founded in Ur."

Any reason counts (research, a hut, a treaty, theft), as in the reference. A player with no city founds nothing,
and the faith stays open for the next.

### 4.2 Spread

Each `turn_begin`, for every civ city that follows no faith:

- every city within 10 tiles (`sq_distance <= 100`) that follows faith *f* adds weight to *f*: 1, doubled if it has
  the same owner, tripled if it is *f*'s holy city;
- the chance this turn is `min(10, total weight)` percent; on success the faith is drawn in proportion to the
  weights and added.

So a frontier town beside two foreign cities of one faith converts in about 50 turns; one beside its own holy city
and two more of its own cities in about 12. Cities already following a faith never gain a second by spreading in
this version (the reference does the same; only missionaries add a second, section 7).

A city can still hold more than one faith: a holy city founded in a city that already follows one keeps both.

### 4.3 State faith

Each `turn_begin`, for each civ:

- if it has no state faith, or none of its cities follows its state faith any more, the state faith becomes the
  faith most of its cities follow (ties: the older faith); none if no city follows any;
- the matching `<Faith> State Faith` small wonder sits in the capital (moved when the capital moves); every other
  state-faith wonder the player holds is removed;
- a change is announced to that player.

The player cannot pick yet. Picking, and the anarchy of changing, belong to the civics column of slice 2 (#274).

### 4.4 Effects (native, so the AI sees them)

| Effect | Value | Requirements | Rows |
|---|---|---|---|
| `Make_Content` | 1 | `Building <F> Faith City`, `Building <F> State Faith Player` | 7 |
| `Make_Content` | 1 | `Building Temple City`, `Building <F> Faith City`, `Building <F> State Faith Player` | 7 |
| `Make_Content` | 1 | `Building Cathedral City`, `Building <F> Faith City`, `Building <F> State Faith Player` | 7 |
| `History` | 2 | `Building Holy City City` | 1 |
| `Make_Content` | 2 | `Building Shrine City` | 1 |
| `Output_Bonus` | 25 | `Building Shrine City`, `OutputType Gold Local` | 1 |

A content citizen from a faith counts only when the city's faith is the owner's state faith, so a conquered city
of another faith stays restless until the faith changes or spreads.

### 4.5 Buildings

| Building | Genus | Can be built | Cost, upkeep | Notes |
|---|---|---|---|---|
| `<F> Faith` (7) | Improvement | no (`MinYear 9999 World`, the Residents' rule) | 1, 0 | city marker; graphic `b.faith_<n>`, alt `b.temple` |
| `<F> State Faith` (7) | SmallWonder | no (same) | 1, 0 | player marker in the capital; graphic alt `b.temple` |
| `Holy City` | Improvement | no (same) | 1, 0 | graphic alt `b.temple` |
| `Shrine` | Improvement | yes, with `Building Holy City City` and `Tech Philosophy Player` | 120, 2 | graphic `b.shrine`, alt `b.temple` |

Sixteen buildings: civ45 has 104 and the limit is 200 (`common/fc_types.h:43`).

### 4.6 Shrine gold

Each `turn_begin`, for each faith with a holy city that holds a Shrine: the city's owner gains 1 gold for every
city in the world following that faith. A holy city of two faiths with a Shrine pays for both.

### 4.7 Conquest and loss

- A captured city keeps its faiths and its holy status; the record restores any marker the capture razed.
- A destroyed city's record is dropped; a destroyed holy city leaves its faith without one (no Shrine possible
  again), as in the reference.

## 5. The AI

Nothing in the AI chooses faiths, so the rules above apply to it exactly as to a human: founding, spread and
state faith are automatic. The AI sees the content, gold and history effects and builds the Shrine for them
(daieffects.c rows in section 3). What it can't do: weigh founding techs for their faith, or like nations that
share its faith (the reference's main diplomatic effect). AI attitude is computed in C
(`ai/default/daidiplomacy.c`); no ruleset or Lua input to it was found (unverified beyond a read of that file), so that waits for engine work (plan, "Engine" section).

## 6. Test plan

A rules test like the strategic resources one (`scripts/civ45-resources-test.sh`), driven by a Lua script in an
autogame:

| # | Case | Expect |
|---|---|---|
| 1 | Give player A Mysticism | The Hearth founded in A's largest faithless city: record, marker and Holy City present; `fc45_rel_holy_1` is that city |
| 2 | Give player B Mysticism after | nothing founded for B |
| 3 | Sell the Hearth marker | re-created the same turn |
| 4 | A's second city beside the holy city, 20 turns | follows the Hearth (weight 6, own holy city: 6 percent a turn, so 71 percent within 20 turns; run until it does, at most 80 turns, 99 percent) |
| 5 | State faith | A holds `Hearth State Faith` in its capital; a city of the Hearth with a Temple has 3 more content citizens than the same city without the faith (1 faith, 1 temple, plus the Temple's own) |
| 6 | Shrine | buildable in the holy city only; owner's gold rises by the number of Hearth cities each turn |
| 7 | Save and load | records, holy city and state faith survive |

Results (2026-10-21, `scripts/civ45-religion-test.sh` on fork patch 0051): 18 of 18 cases pass, case 4 after 3
turns.

### 6.1 Balance games

Seeds 7 and 13, 10 Normal AIs, up to 475 turns, with religion, resources and cottages together (patches 0051 to
0053), against the same seeds on patch 0050. The full table is in
[cottages.md](cottages.md), section 6. For religion:

- All seven faiths are founded, the first at turns 69 to 74 and the last (the Deep Well) at turns 167 to 172.
- By turn 150 nearly every city follows a faith. Cities then keep the faith they have, since spreading only fills
  cities with none.
- Seed 7 at turn 300: 47 cities follow the Quiet Way, 42 the Hearth, 23 the Many Hands and one each the other four.
- Unhappy citizens fell (seed 7 at turn 300: 83 before, 21 after), the state faith and the luxuries together.
- The first version's 1 history a turn per faith per city raised seed 7's world culture at turn 300 from 52,585
  to 92,827. With only holy cities adding history it is 65,594; the rest comes from the faster economy.

## 7. Later

- Missionaries: a unit built in a city with a faith, carrying it to any city ("User Action" slots 1 and 2 are the
  sandbox leftovers, `civ45/actions.ruleset:481-492`). The AI scores such actions 0 (great-people.md section 1),
  so it needs a Lua rule like the great people's first.
- Picking the state faith, through the civics of slice 2.
- A religious council like the reference's, and AI attitudes by faith: engine work.
- Art: seven faith symbols for the city dialog (sheet 07 follow-up); until then markers fall back to the Temple.
